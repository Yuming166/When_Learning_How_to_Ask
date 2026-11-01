"""Trusted evaluator: globally independent cells and interleaved paired policies."""
import hashlib
import json
import math
import multiprocessing as mp
import time
from pathlib import Path
import numpy as np
from .bootstrap import ROOT,V1,P2A
from .policy import POLICIES,worker
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment
from qrelbench.rpc import send,receive
from qrelbench.security import protect_evaluator


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_files():
    paths=sorted((ROOT/'phase2b').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))+[ROOT/'config.json',ROOT/'PROTOCOL.md']
    return {str(p.relative_to(ROOT)):digest(p) for p in paths}


def jobs(cfg):
    if cfg['split']!='development' or cfg['master_seed'] is not None:raise ValueError('Sealed development only')
    result=[]
    for i in range(cfg['episodes_per_cell']):
        order=cfg['Rs'][i%len(cfg['Rs']):]+cfg['Rs'][:i%len(cfg['Rs'])]
        for R in order:
            for pi,part in enumerate(cfg['partitions']):
                for ai,alpha in enumerate(cfg['alphas']):
                    cell=(pi*len(cfg['alphas'])+ai)*len(cfg['Rs'])+cfg['Rs'].index(R)
                    cap=max(cfg['cap_floor'],cfg['cap_R_multiplier']*R);check=max(cfg['check_floor'],math.ceil(math.sqrt(R)))
                    milestones=sorted({min(cap,math.ceil(v/check)*check) for v in [R,2*R,4*R,8*R,12*R,16*R,24*R,cap]})
                    result.append({'partition':part,'alpha':alpha,'R':R,'index':210000+cell*100+i,
                        'replicate':i,'p':cfg['p'],'q':cfg['q'],'s':cfg['type_accuracy'],'eta':cfg['eta'],
                        'M':math.ceil(alpha*R),'online_cap':cap,'check_every':check,'milestones':milestones,
                        'channel':'iid','protocol':'fixed_confidence','scenario':'convergence_diagnostic'})
    return result


def public_job(job):return {k:job[k] for k in ['R','online_cap','check_every','milestones']}


def audit_estimate(estimate,episode,p,q):
    if estimate is None:return None
    return {**estimate,'theta_errors':sum(a!=b for a,b in zip(estimate['theta'],episode.truth)),
        'type_errors':sum(a!=b for a,b in zip(estimate['z'],episode.types)),
        'p_error':estimate['p']-p,'q_error':estimate['q']-q}


def evaluate_job(conn,name,job,seed,deadline,counters,on_snapshot=None):
    protect_evaluator();episode=make_episode(seed,'development',job['index'],job['partition'])
    env=QueryEnvironment(episode,job['p'],job['q'],job['M'],job['s'],job['online_cap'],job['channel'],name=='Oracle Format',eta=job['eta'])
    counts=np.zeros((sum(job['partition']),2,2),dtype=int);reports=[[] for _ in job['partition']]
    snapshots=[];submitted=False;send(conn,public_job(job))
    methods={'reset':env.reset,'get_calibration':env.get_calibration,'query':env.query,'ask_type':env.ask_type,'submit':env.submit}
    while True:
        if time.monotonic()>deadline:raise TimeoutError('Frozen global runtime cap')
        if not conn.poll(min(1,max(.001,deadline-time.monotonic()))):continue
        message=receive(conn)
        if 'worker_error' in message:raise RuntimeError(message['worker_error'])
        if 'done' in message:
            if not submitted:raise RuntimeError('Missing terminal submission')
            detail=message['done'];break
        method=message.get('method');args=message.get('args')
        if not isinstance(args,dict):raise RuntimeError('Malformed RPC')
        if method=='snapshot':
            if submitted:raise RuntimeError('Late snapshot')
            s=args['snapshot']
            if s['online']!=env.cost['task']+env.cost['type'] or not np.array_equal(s['counts'],counts) or s['type_answers']!=reports:
                raise RuntimeError('Snapshot observation/cost mismatch')
            fit=s['fit'];row={**job,'policy':name,'episode_id':episode.public['episode_id'],**s,
                'costs':dict(env.cost),'total_acquisition':sum(env.cost.values()),'exact':fit['theta']==episode.truth,
                'estimate':audit_estimate(s['estimate'],episode,job['p'],job['q'])}
            snapshots.append(row)
            if on_snapshot:on_snapshot(row)
            send(conn,{'result':{'recorded':True}});continue
        if method not in methods:raise RuntimeError('Unsupported/private RPC')
        before=dict(env.cost)
        try:
            result=methods[method](**args)
            if method=='query':counts[args['j'],'AB'.index(args['format']),result['answer']]+=1
            if method=='ask_type':reports[args['group']].append('AB'.index(result['format']))
        except Exception as exc:send(conn,{'error':type(exc).__name__});raise
        finally:
            for k in ['task','type','offline']:counters[k]+=env.cost[k]-before[k]
        submitted|=method=='submit';send(conn,{'result':result})
    score=env.score()
    if score['online']!=detail['online'] or not np.array_equal(detail['counts'],counts) or detail['type_answers']!=reports:
        raise RuntimeError('Final observation/cost mismatch')
    final={**job,'policy':name,'episode_id':episode.public['episode_id'],**score,
        'complete':detail['complete'],'censored':not detail['complete'],'fit':detail['fit'],
        'numeric_margin':detail['numeric_margin'],'glr_checks':detail['glr_checks'],
        'glr_seconds':detail['glr_seconds'],'planner_seconds':detail['planner_seconds'],
        'glr_cpu_seconds':detail['glr_cpu_seconds'],'planner_cpu_seconds':detail['planner_cpu_seconds'],
        'tracking_diagnostics':detail['tracking_diagnostics'],
        'forced_tasks':int(np.asarray(detail['forced_counts']).sum()) if detail['forced_counts'] is not None else 0,
        'estimation_history':[audit_estimate(e,episode,job['p'],job['q']) for e in detail['estimation_history']],
        'isolation':detail['isolation'],'sampling_scope':detail['sampling_scope'],
        'counts':counts.tolist(),'type_answers':reports,'calibration':env._cal}
    private={'job':job,'policy':name,'provenance':episode.provenance,'records':episode.records,'truth':episode.truth,
        'types':episode.types,'trace_prefix':env.trace,'full_trace_sha256':score['transcript_sha256']}
    return final,private,snapshots


def main():
    protect_evaluator();cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
    freeze=json.loads((ROOT/'freeze.json').read_text())
    if freeze['files']!=frozen_files():raise RuntimeError('Frozen source/config changed')
    for rel,h in freeze['audits'].items():
        if digest(ROOT/rel)!=h:raise RuntimeError('Frozen proof/audit changed')
    for label,base in [('v1',V1),('phase2a',P2A)]:
        for rel,h in freeze['dependencies'][label].items():
            if digest(base/rel)!=h:raise RuntimeError('Historical source dependency changed')
    maximum=sum(j['online_cap'] for j in plan)*len(POLICIES)
    if maximum>cfg['limits']['online_actions']:raise RuntimeError('Planned action cap exceeded')
    seedfile=ROOT/'artifacts/private/seed.json'
    if digest(seedfile)!=freeze['private_seed_commitment']:raise RuntimeError('Seed commitment changed')
    seed=json.loads(seedfile.read_text())['development_seed'];out=ROOT/'artifacts/run'
    if out.exists():raise RuntimeError('No overwrite or automatic retry')
    out.mkdir();private=out/'private';private.mkdir(mode=0o700)
    started=time.monotonic();deadline=started+cfg['limits']['wall_seconds'];context=mp.get_context('spawn')
    counters={'task':0,'type':0,'offline':0};finished=0;status='completed';error=None;current=None;workers={}
    receipt={'planned_trajectories':len(plan)*len(POLICIES),'independent_worlds':len(plan),
        'maximum_online_actions':maximum,'freeze_sha256':digest(ROOT/'freeze.json'),'retries':0,
        'model_calls':0,'confirmation':False,'policy_order':'interleaved per world, cyclic rotation'}
    (out/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (out/'trajectories.jsonl').open('x') as log,(out/'snapshots.jsonl').open('x') as snapshots,(private/'reproduction.jsonl').open('x') as repro:
        try:
            for name in POLICIES:
                parent,child=context.Pipe();process=context.Process(target=worker,args=(child,name));process.start();child.close();workers[name]=(parent,process)
            for i,job in enumerate(plan):
                order=POLICIES[i%len(POLICIES):]+POLICIES[:i%len(POLICIES)]
                for name in order:
                    current={'policy':name,'job_index':i,'job':job};parent,process=workers[name]
                    if not process.is_alive():raise RuntimeError('Worker exited')
                    def snapshot(row):snapshots.write(json.dumps(row,sort_keys=True)+'\n');snapshots.flush()
                    final,priv,_=evaluate_job(parent,name,job,seed,deadline,counters,snapshot)
                    log.write(json.dumps(final,sort_keys=True)+'\n');log.flush();repro.write(json.dumps(priv,sort_keys=True)+'\n');repro.flush();finished+=1
                print(json.dumps({'worlds':i+1,'trajectories':finished,'R':job['R'],
                    'online':counters['task']+counters['type'],'seconds':round(time.monotonic()-started,1)}),flush=True)
            for parent,process in workers.values():
                send(parent,None);process.join(timeout=5)
                if process.is_alive() or process.exitcode!=0:raise RuntimeError('Worker shutdown failure')
        except Exception as exc:status='failed';error={'type':type(exc).__name__,'message':str(exc),'current':current}
        finally:
            for parent,process in workers.values():
                if process.is_alive():process.terminate();process.join(timeout=5)
                parent.close()
    receipt.update(status=status,error=error,finished_trajectories=finished,
        costs_including_partial=counters,online_actions=counters['task']+counters['type'],seconds=time.monotonic()-started)
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
    if status!='completed':raise SystemExit(1)


if __name__=='__main__':main()
