"""One authorized 192-call run; first 24 included as technical smoke, no retries."""
import json
import os
import time
from pathlib import Path
from design import ROOT,read_jsonl,write_json,parse_answer,sha
from local_sampler import LocalSampler


def frozen_files():
    paths=[ROOT/n for n in ['config.json','design.py','policies.py','collect.py','local_sampler.py',
        'analyze.py','PROTOCOL.md','selected_worlds.jsonl','proofwriter_structure.json','logic_audit.py',
        'selected_dependencies.json','dependency_audit.py','test_phase1c.py']]
    paths+=sorted((ROOT/'data').glob('*'))
    return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths if p.is_file()}


def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    freeze=json.loads((ROOT/'freeze.json').read_text())
    assert frozen_files()==freeze['files'], 'Frozen protocol mismatch'
    requests=read_jsonl(ROOT/'data/requests.jsonl')
    assert len(requests)==cfg['total_generation_cap']==192
    run=ROOT/'run';assert not run.exists(), 'Never overwrite/retry this run'
    run.mkdir()
    write_json(run/'started.json',{'pid':os.getpid(),'time':time.time(),'planned':192,
                                 'freeze_sha256':sha((ROOT/'freeze.json').read_bytes())})
    start=time.monotonic();sampler=LocalSampler(cfg)
    write_json(run/'model_identity.json',sampler.identity)
    done=invalid=errors=0;status='completed';smoke_rows=[]
    with (run/'raw.jsonl').open('x') as log:
        for row in requests:
            if time.monotonic()-start>cfg['timeout_seconds']:status='timeout';break
            record={**row,'config_sha256':sha((ROOT/'config.json').read_bytes()),
                    'freeze_sha256':sha((ROOT/'freeze.json').read_bytes())}
            t=time.monotonic()
            try:
                record.update(sampler.generate(row))
                answer=parse_answer(record['raw_output']) if record['finish_reason']=='stop' else None
                record['parsed_answer']=answer
                record['canonical_answer']=answer^row['option_flip'] if answer is not None else None
                record['status']='valid' if answer is not None else 'invalid'
                invalid+=int(answer is None)
            except Exception as exc:
                record.update(status='error',error_type=type(exc).__name__,parsed_answer=None,canonical_answer=None)
                errors+=1
            record['seconds']=time.monotonic()-t;record['completed_unix_time']=time.time()
            log.write(json.dumps(record,ensure_ascii=False)+'\n');log.flush();done+=1
            if row['group_index']==0:smoke_rows.append(record)
            if done%24==0:print(json.dumps({'done':done,'invalid':invalid,'errors':errors,'seconds':round(time.monotonic()-start,1)}),flush=True)
            if done==24:
                passed=errors==0 and invalid<=1
                write_json(run/'smoke_gate.json',{'calls_included_in_total':24,'pass':passed,
                    'accuracy_used':False,'valid':24-invalid,'invalid':invalid,'errors':errors})
                if not passed:status='smoke_gate_failed';break
            if errors>=cfg['max_infrastructure_failures']:status='infrastructure_stop';break
    write_json(run/'execution.json',{'planned':192,'attempted':done,'unattempted':192-done,
        'status':status,'invalid':invalid,'errors':errors,'seconds':time.monotonic()-start,
        'freeze_sha256':sha((ROOT/'freeze.json').read_bytes())})
    print(json.dumps({'status':status,'attempted':done}),flush=True)


if __name__=='__main__':main()
