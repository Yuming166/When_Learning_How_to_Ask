"""Pooled, no-retry SSE transport; final content is isolated from reasoning."""
from __future__ import annotations
import json
from pathlib import Path
import re
import time
import threading
import requests


class StreamProtocolError(RuntimeError):
    def __init__(self,reason,status=None,models=None):
        super().__init__(reason)
        self.reason=reason
        self.status=status
        self.models=models or []


class StreamDecoder:
    def __init__(self,accepted_models):
        self.accepted=set(accepted_models)
        self.models=set()
        self.response_ids=set()
        self.fragments=[]
        self.reasoning_chars=0
        self.usage=None
        self.finish=None
        self.done=False
        self.events=0
        self.data=[]

    def line(self,line):
        if line=='':
            self.dispatch()
        elif line.startswith(':'):
            return
        elif line.startswith('data:'):
            self.data.append(line[5:].lstrip(' '))
        elif line.startswith(('event:','id:','retry:')):
            return
        else:
            raise StreamProtocolError('unexpected_sse_line')

    def dispatch(self):
        if not self.data:
            return
        text='\n'.join(self.data)
        self.data=[]
        if self.done:
            raise StreamProtocolError('data_after_done')
        if text=='[DONE]':
            self.done=True
            return
        try:
            event=json.loads(text)
        except Exception as exc:
            raise StreamProtocolError('malformed_sse_json') from exc
        if not isinstance(event,dict) or event.get('error'):
            raise StreamProtocolError('stream_error_event')
        self.events+=1
        model=event.get('model')
        if model:
            self.models.add(model)
            if model not in self.accepted:
                raise StreamProtocolError('reported_model_mismatch',models=sorted(self.models))
        if event.get('id'):
            self.response_ids.add(event['id'])
            if len(self.response_ids)>1:
                raise StreamProtocolError('multiple_response_ids')
        if event.get('usage') is not None:
            if not isinstance(event['usage'],dict):
                raise StreamProtocolError('usage_type')
            self.usage=event['usage']
        choices=event.get('choices')
        if not isinstance(choices,list):
            raise StreamProtocolError('choices_type')
        if not choices:
            return
        if len(choices)!=1 or choices[0].get('index',0)!=0:
            raise StreamProtocolError('unexpected_choice_index')
        choice=choices[0]
        delta=choice.get('delta') or {}
        if not isinstance(delta,dict):
            raise StreamProtocolError('delta_type')
        if delta.get('role') not in (None,'assistant'):
            raise StreamProtocolError('unexpected_delta_role')
        if delta.get('tool_calls') or delta.get('function_call'):
            raise StreamProtocolError('unexpected_tool_call')
        content=delta.get('content')
        reasoning=delta.get('reasoning_content')
        if content is not None:
            if not isinstance(content,str):
                raise StreamProtocolError('content_type')
            if self.finish is not None and content:
                raise StreamProtocolError('content_after_finish')
            self.fragments.append(content)
        if reasoning is not None:
            if not isinstance(reasoning,str):
                raise StreamProtocolError('reasoning_type')
            self.reasoning_chars+=len(reasoning)
        finish=choice.get('finish_reason')
        if finish is not None:
            if self.finish is not None:
                raise StreamProtocolError('duplicate_finish')
            self.finish=finish

    def finish_payload(self):
        self.dispatch()
        if not self.done or self.finish is None:
            raise StreamProtocolError('incomplete_stream')
        if len(self.models)!=1:
            raise StreamProtocolError('missing_or_inconsistent_model',models=sorted(self.models))
        if len(self.response_ids)!=1 or not all(isinstance(x,str) and x.strip() for x in self.response_ids):
            raise StreamProtocolError('missing_or_inconsistent_response_id')
        return {'id':next(iter(self.response_ids),None),'model':next(iter(self.models)),
                'usage':self.usage,'choices':[{'index':0,'finish_reason':self.finish,
                 'message':{'role':'assistant','content':''.join(self.fragments)}}]}


class StreamTransport:
    def __init__(self,cfg):
        self.cfg=cfg
        self.local=threading.local()
        self.sessions=[]
        self.lock=threading.Lock()

    def session_for_thread(self):
        if not hasattr(self.local,'session'):
            session=requests.Session()
            session.trust_env=False
            session.mount('https://',requests.adapters.HTTPAdapter(max_retries=0,pool_connections=1,pool_maxsize=1))
            self.local.session=session
            with self.lock:
                self.sessions.append(session)
        return self.local.session

    def call(self,endpoint,body,api_key,path):
        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        def redact(text):
            return re.sub(r'sk-[A-Za-z0-9_.-]+','[REDACTED]',text.replace(api_key,'[REDACTED]'))
        started=time.monotonic()
        decoder=StreamDecoder(self.cfg['accepted_reported_models'])
        with self.session_for_thread().post(endpoint,data=body,
            headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json','Accept':'text/event-stream'},
            timeout=(self.cfg['connect_timeout_seconds'],self.cfg['request_timeout_seconds']),stream=True,allow_redirects=False) as response:
            if response.status_code!=200:
                path.write_text(redact(response.text)+'\n')
                raise StreamProtocolError('http_error',status=response.status_code)
            if 'text/event-stream' not in response.headers.get('Content-Type','').lower():
                path.write_text(redact(response.text)+'\n')
                raise StreamProtocolError('unexpected_content_type',status=response.status_code)
            size=0
            with path.open('w') as handle:
                for raw in response.iter_lines(chunk_size=4096,decode_unicode=False):
                    if time.monotonic()-started>self.cfg['request_timeout_seconds']:
                        raise StreamProtocolError('stream_wall_timeout')
                    line=raw.decode('utf-8') if isinstance(raw,bytes) else raw
                    size+=len(raw)
                    if size>8*1024*1024:
                        raise StreamProtocolError('stream_byte_limit')
                    handle.write(redact(line)+'\n')
                    handle.flush()
                    decoder.line(line)
            payload=decoder.finish_payload()
            return payload,{'http_status':200,'provider_request_id':response.headers.get('x-request-id'),
                'sse_complete':True,'sse_events':decoder.events,'reasoning_chars':decoder.reasoning_chars,
                'response_stream_bytes':size}

    def close(self):
        for session in self.sessions:
            session.close()
