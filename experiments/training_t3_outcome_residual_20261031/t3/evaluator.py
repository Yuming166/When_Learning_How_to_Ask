"""Frozen evaluator body with explicit independent-world split support.

The original method hardcodes 'development'. This additive adapter changes that
one construction argument and checks split/action ledger consistency. No change
to the generator, channels, costs, oracle access, or potential-response streams.
"""
import json,time
import numpy as np
from . import bootstrap
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment
from qrelbench.rpc import send,receive
from qrelbench.security import protect_evaluator
from phase2d.runner import public_job,audit_estimate

def evaluate(conn,name,job,seed,deadline,counters):
    protect_evaluator();episode=make_episode(seed,job['split'],job['index'],job['partition'])
    env=QueryEnvironment(episode,job['p'],job['q'],job['M'],job['s'],job['online_cap'],job['channel'],False,eta=job['eta'])
    counts=np.zeros((sum(job['partition']),2,2),int);reports=[[] for _ in job['partition']];submitted=False
    methods={'reset':env.reset,'get_calibration':env.get_calibration,'query':env.query,'ask_type':env.ask_type,'submit':env.submit}
    send(conn,public_job(job))
    try:
        while True:
            if time.monotonic()>deadline:raise TimeoutError('Frozen runtime ceiling')
            if not conn.poll(min(1,max(.001,deadline-time.monotonic()))):continue
            msg=receive(conn)
            if msg is None:raise RuntimeError('Worker disconnected')
            if 'worker_error' in msg:raise RuntimeError(msg['worker_error'])
            if 'done' in msg:
                if not submitted:raise RuntimeError('Missing submission')
                detail=msg['done'];break
            method=msg.get('method');args=msg.get('args')
            if not isinstance(args,dict):raise RuntimeError('Malformed RPC')
            if method=='snapshot':
                s=args['snapshot']
                if submitted or s['online']!=env.cost['task']+env.cost['type'] or not np.array_equal(s['counts'],counts) or s['type_answers']!=reports:
                    raise RuntimeError('Snapshot ledger mismatch')
                send(conn,{'result':{'recorded':True}});continue
            if method not in methods:raise RuntimeError('Unsupported RPC')
            before=dict(env.cost)
            try:
                result=methods[method](**args)
                if method=='query':counts[args['j'],'AB'.index(args['format']),result['answer']]+=1
                if method=='ask_type':reports[args['group']].append('AB'.index(result['format']))
            finally:
                for k in counters:counters[k]+=env.cost[k]-before[k]
            submitted|=method=='submit';send(conn,{'result':result})
        score=env.score()
        if score['online']!=detail['online'] or not np.array_equal(detail['counts'],counts) or detail['type_answers']!=reports:
            raise RuntimeError('Final ledger mismatch')
        # True parameters/errors and reward are attached only after submission.
        final={**job,'policy':name,'episode_id':episode.public['episode_id'],**score,**detail,
          'estimation_history':[audit_estimate(e,episode,job['p'],job['q']) for e in detail['estimation_history']],
          'calibration':env._cal,'censored':not detail['complete']}
        priv={'job':job,'policy':name,'provenance':episode.provenance,'truth':episode.truth,'types':episode.types,
          'trace_prefix':env.trace,'full_trace_sha256':score['transcript_sha256']}
        return final,priv
    except Exception as exc:
        partial={'job':job,'policy':name,'error':str(exc),'costs':dict(env.cost),'counts':counts.tolist(),
          'reports':reports,'submitted':submitted,'trace_sha256':env.log_digest.hexdigest()}
        exc.partial=partial;raise
