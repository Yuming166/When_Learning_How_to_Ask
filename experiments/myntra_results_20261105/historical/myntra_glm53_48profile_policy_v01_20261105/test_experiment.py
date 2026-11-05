import ast
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

import experiment as ex


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = ex.load_context()
        cls.jobs = ex.rows(ex.INPUT/'private/jobs.jsonl')

    def test_exact_input_and_function_reuse(self):
        original=Path(ex.CFG['source_luna_experiment'])
        self.assertEqual(len(self.context['profiles']),48)
        self.assertEqual(len(self.context['cases']),280)
        self.assertEqual(len(self.context['menus']),35)
        self.assertEqual(len(self.jobs),288)
        for p in (ex.INPUT).rglob('*'):
            if p.is_file() and p.name!='http_requests.jsonl':
                self.assertEqual(ex.digest(p),ex.digest(original/'artifacts/input'/p.relative_to(ex.INPUT)))
        source=(ex.REFERENCE/'luna_replay_source.py').read_text()
        copied=(ex.BASE/'replay.py').read_text()
        names=('_reject_duplicate_keys','parse_field_answer','_case_trace')
        def functions(text):
            return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body
                    if isinstance(n,ast.FunctionDef) and n.name in names}
        self.assertEqual(functions(source),functions(copied))

    def test_response_model_truncation_and_schema_fail_closed(self):
        job=self.jobs[0]
        answer=ex.ref.ReferenceUser(self.context['profiles'][job['profile_id']]).answer(job['query_action'])
        payload={'model':ex.CFG['requested_model'],'choices':[{'finish_reason':'stop','message':{'content':json.dumps(answer)}}]}
        self.assertTrue(ex.validate_response(payload,job,self.context)['valid'])
        payload['model']='another-model'
        self.assertEqual(ex.validate_response(payload,job,self.context)['error_class'],'reported_model_mismatch')
        payload['model']=ex.CFG['requested_model']
        payload['choices'][0]['finish_reason']='length'
        result=ex.validate_response(payload,job,self.context)
        self.assertFalse(result['valid'])
        self.assertTrue(result['transport_ok'])
        payload['choices'][0]['finish_reason']='stop'
        payload['choices'][0]['message']['content']='{"field":"neckline","scores":{}}'
        self.assertFalse(ex.validate_response(payload,job,self.context)['valid'])

    def test_error_no_retry_no_credential_in_artifacts(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fake=unittest.mock.Mock()
            fake.call.side_effect=urllib.error.URLError('offline_mock TEST-CREDENTIAL-DO-NOT-PERSIST')
            # All six smoke attempts finish once; remaining jobs are explicitly unattempted.
            with patch.object(ex,'RUN',root/'run'),patch.object(ex,'BASE',root),\
                 patch.object(ex,'verify',return_value={}),\
                 patch.object(ex,'frozen_requests',return_value=[{'job_id':j['job_id'],'body':{},
                     'body_sha256':hashlib.sha256(b'{}').hexdigest()} for j in self.jobs]),\
                 patch.object(ex,'load_context',return_value=self.context),\
                 patch.object(ex,'smoke_replay',return_value={'status':'FAIL_TRANSPORT_OR_MODEL'}),\
                 patch.object(ex,'rows',side_effect=lambda p: self.jobs if str(p).endswith('jobs.jsonl') else original_rows(p)),\
                 patch.object(ex,'StreamTransport',return_value=fake),\
                 patch.object(ex.time,'sleep',return_value=None):
                receipt=ex.collect('TEST-CREDENTIAL-DO-NOT-PERSIST')
            self.assertEqual(fake.call.call_count,3)
            self.assertEqual(receipt['retries'],0)
            self.assertEqual(receipt['records'],288)
            self.assertEqual(receipt['status'],'COLLECTION_STOPPED')
            attempts=original_rows(root/'run/ATTEMPTS.jsonl')
            self.assertEqual(len({r['job_id'] for r in attempts}),len(attempts))
            for p in root.rglob('*'):
                if p.is_file(): self.assertNotIn('TEST-CREDENTIAL-DO-NOT-PERSIST',p.read_text())


original_rows=ex.rows


class StreamTests(unittest.TestCase):
    def frame(self,decoder,obj):
        decoder.line('data: '+json.dumps(obj,ensure_ascii=False))
        decoder.line('')

    def event(self,delta=None,finish=None,model=None,usage=None):
        return {'id':'test-response','model':model or ex.CFG['requested_model'],
                'choices':[] if usage is not None else [{'index':0,'delta':delta or {},'finish_reason':finish}],
                **({'usage':usage} if usage is not None else {})}

    def test_content_separate_from_reasoning_usage_retained(self):
        from stream_transport import StreamDecoder
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        self.frame(d,self.event({'role':'assistant','reasoning_content':'private test reasoning'}))
        self.frame(d,self.event({'content':'{"purchase_threshold":'}))
        self.frame(d,self.event({'content':'9}'},finish='stop'))
        self.frame(d,self.event(usage={'prompt_tokens':12,'completion_tokens':7,'total_tokens':19}))
        d.line('data: [DONE]')
        d.line('')
        p=d.finish_payload()
        self.assertEqual(p['choices'][0]['message']['content'],'{"purchase_threshold":9}')
        self.assertNotIn('private test reasoning',json.dumps(p))
        self.assertEqual(p['usage']['total_tokens'],19)
        self.assertGreater(d.reasoning_chars,0)

    def test_parseable_content_without_done_or_finish_rejected(self):
        from stream_transport import StreamDecoder,StreamProtocolError
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        self.frame(d,self.event({'content':'{"purchase_threshold":9}'},finish='stop'))
        with self.assertRaises(StreamProtocolError): d.finish_payload()
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        self.frame(d,self.event({'content':'{"purchase_threshold":9}'}))
        d.line('data: [DONE]');d.line('')
        with self.assertRaises(StreamProtocolError): d.finish_payload()

    def test_stream_model_drift_and_post_done_data_rejected(self):
        from stream_transport import StreamDecoder,StreamProtocolError
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        with self.assertRaises(StreamProtocolError): self.frame(d,self.event(model='other-model'))
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        self.frame(d,self.event({'content':'{}'},finish='stop'))
        d.line('data: [DONE]');d.line('')
        with self.assertRaises(StreamProtocolError): self.frame(d,self.event({'content':'more'}))

    def test_malformed_json_tool_calls_and_duplicate_finish_rejected(self):
        from stream_transport import StreamDecoder,StreamProtocolError
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        d.line('data: {broken')
        with self.assertRaises(StreamProtocolError): d.line('')
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        with self.assertRaises(StreamProtocolError): self.frame(d,self.event({'tool_calls':[{'id':'t'}]}))
        d=StreamDecoder(ex.CFG['accepted_reported_models'])
        self.frame(d,self.event({'content':'{}'},finish='stop'))
        with self.assertRaises(StreamProtocolError): self.frame(d,self.event(finish='stop'))

if __name__=='__main__':
    unittest.main()
