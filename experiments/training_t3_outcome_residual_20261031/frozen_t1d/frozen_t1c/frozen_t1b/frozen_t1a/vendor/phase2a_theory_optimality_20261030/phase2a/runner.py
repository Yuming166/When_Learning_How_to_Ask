"""Trusted evaluator: frozen development plan, complete partial-action accounting."""
import argparse
import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path
import time
import numpy as np
from . import bootstrap
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment
from qrelbench.security import protect_evaluator
from qrelbench.rpc import send,receive
from .policy import POLICIES,worker

ROOT=bootstrap.ROOT


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_files():
    files=sorted((ROOT/'phase2a').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))+[ROOT/'config.json',ROOT/'PROTOCOL.md']
    return {str(p.relative_to(ROOT)):digest(p) for p in files}


def jobs(cfg):
    if cfg['split']!='development' or cfg['master_seed'] is not None:raise ValueError('Only sealed-seed development authorized')
    out=[];fb=cfg['fixed_budget'];fc=cfg['fixed_confidence']
    def add(protocol,scenario,part,alpha,R,index,p,q,cap,check=16,channel='iid',budgets=None):
        out.append({'protocol':protocol,'scenario':scenario,'partition':part,'alpha':alpha,'R':R,
            'index':index,'p':p,'q':q,'s':cfg['type_accuracy'],'channel':channel,
            'M':math.ceil(alpha*R),'delta':math.exp(-R),'online_cap':cap,'check_every':check,
            'snapshot_budgets':budgets or [],'update_every':cfg['tracking_update_every']})
    for part in fb['partitions']:
        for alpha in fb['alphas']:
            for i in range(fb['episodes']):add('fixed_budget','primary',part,alpha,fb['planning_R'],110000+i,fb['p'],fb['q'],max(fb['budgets']),budgets=fb['budgets'])
    for p,q in fb['coverage_rates']:
        for i in range(fb['coverage_episodes']):add('fixed_budget','rate_coverage',fb['coverage_partition'],fb['coverage_alpha'],fb['planning_R'],111000+i,p,q,max(fb['budgets']),budgets=fb['budgets'])
    for part in fc['partitions']:
        for alpha in fc['alphas']:
            for R in fc['Rs']:
                for i in range(fc['episodes']):add('fixed_confidence','primary_glr',part,alpha,R,112000+i,fc['p'],fc['q'],fc['online_cap'],fc['check_every'])
    for d in fc['technical_dimensions']:
        for i in range(fc['technical_episodes']):add('fixed_confidence','dimension_probe',[d//2,d-d//2],fc['technical_alpha'],fc['technical_R'],113000+i,fc['p'],fc['q'],fc['technical_cap'],fc['check_every'])
    neg=cfg['negative_controls']
    for ni,scenario in enumerate(neg['cases']):
        for i in range(neg['episodes']):
            add('fixed_confidence',scenario,neg['partition'],neg['alpha'],neg['R'],114000+ni*100+i,fc['p'],.5 if scenario=='q_boundary' else fc['q'],neg['online_cap'],fc['check_every'],
                scenario if scenario in ['persistent','label_asymmetric'] else 'iid')
    return out


def public_job(job):
    # No p/q, scenario/rate identifier, private index, seed, signs or types.
    return {'protocol':job['protocol'],'online_cap':job['online_cap'],'delta':job['delta'],
        'planning_delta':job['delta'],'snapshot_budgets':job['snapshot_budgets'],
        'check_every':job['check_every'],'update_every':job['update_every']}


def audit_estimate(estimate,episode,p,q):
    if estimate is None:return None
    return {**estimate,'theta_errors':sum(a!=b for a,b in zip(estimate['theta'],episode.truth)),
            'type_errors':sum(a!=b for a,b in zip(estimate['z'],episode.types)),
            'p_error':estimate['p']-p,'q_error':estimate['q']-q}


def evaluate_job(conn,name,job,seed,deadline,counters,on_snapshot=None):
    protect_evaluator();episode=make_episode(seed,'development',job['index'],job['partition'])
    env=QueryEnvironment(episode,job['p'],job['q'],job['M'],job['s'],job['online_cap'],job['channel'],name=='Oracle Format')
    observed=np.zeros((sum(job['partition']),2,2),dtype=int);snapshots=[];submitted=False
    send(conn,public_job(job))
    methods={'reset':env.reset,'query':env.query,'ask_type':env.ask_type,'get_calibration':env.get_calibration,'submit':env.submit}
    while True:
        if time.monotonic()>deadline:raise TimeoutError('Frozen global runtime cap')
        if not conn.poll(min(1,max(.001,deadline-time.monotonic()))):continue
        message=receive(conn)
        if 'worker_error' in message:raise RuntimeError(message['worker_error'])
        if 'done' in message:
            if not submitted:raise RuntimeError('Worker omitted terminal submission')
            detail=message['done'];break
        method=message.get('method');args=message.get('args')
        if not isinstance(args,dict):raise RuntimeError('Malformed RPC')
        if method=='snapshot':
            if submitted:raise RuntimeError('Snapshot after terminal submission')
            snap=args['snapshot']
            if snap['online']!=sum(env.cost[k] for k in ['task','type']):raise RuntimeError('Snapshot count mismatch')
            if not np.array_equal(np.asarray(snap['counts']),observed):raise RuntimeError('Snapshot observations differ from server transcript')
            theta=snap['fit']['theta'];correct=theta==episode.truth
            row={**job,'policy':name,'episode_id':episode.public['episode_id'],'online':snap['online'],
                'costs':dict(env.cost),'total_acquisition':sum(env.cost.values()),'theta':theta,
                'exact':correct,'correct_facts':sum(a==b for a,b in zip(theta,episode.truth)),
                'complete':True if job['protocol']=='fixed_budget' else snap['complete'],
                'fit':snap['fit'],'estimate':audit_estimate(snap['estimate'],episode,job['p'],job['q']),
                'guarantee_scope':'float64 exact formulation, no rigorous interval rounding guarantee',
                'model_assumptions_hold':job['channel']=='iid'}
            snapshots.append(row)
            if on_snapshot:on_snapshot(row)
            # Truth and evaluation fields stay server-side; only acknowledgement.
            send(conn,{'result':{'recorded':True}});continue
        if method not in methods:raise RuntimeError('Private or unsupported RPC method')
        before=dict(env.cost)
        try:
            result=methods[method](**args)
            if method=='query':observed[args['j'],'AB'.index(args['format']),result['answer']]+=1
        except Exception as exc:
            send(conn,{'error':type(exc).__name__});raise
        finally:
            # Includes the interrupted job; never completed-only action accounting.
            for k in ['task','type','offline']:counters[k]+=env.cost[k]-before[k]
        submitted|=method=='submit';send(conn,{'result':result})
    score=env.score()
    if score['online']!=detail['online']:raise RuntimeError('Final count mismatch')
    if not np.array_equal(detail['counts'],observed):raise RuntimeError('Final count table mismatch')
    final={**job,'policy':name,'episode_id':episode.public['episode_id'],**score,
        'complete':detail['complete'],'censored':not detail['complete'],
        'glr_seconds':detail['glr_seconds'],'decode_seconds':detail['decode_seconds'],
        'planner_seconds':detail['planner_seconds'],'fit':detail['fit'],'isolation':detail['isolation'],
        'model_assumptions_hold':job['channel']=='iid',
        'estimation_history':[audit_estimate(e,episode,job['p'],job['q']) for e in detail['estimation_history']],
        'sampling_scope':detail['sampling_scope']}
    private={'job':job,'policy':name,'provenance':episode.provenance,'records':episode.records,
        'truth':episode.truth,'types':episode.types,'counts':detail['counts'],'type_answers':detail['type_answers'],
        'trace_prefix':env.trace,'complete_trace_sha256':score['transcript_sha256']}
    return final,private,snapshots


def main():
    protect_evaluator();parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(ROOT/'artifacts/run'));args=parser.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
    freeze=json.loads((ROOT/'freeze.json').read_text())
    if freeze['files']!=frozen_files():raise RuntimeError('Source/config/protocol freeze mismatch')
    seedfile=ROOT/'artifacts/private/seed.json'
    if digest(seedfile)!=freeze['private_seed_commitment']:raise RuntimeError('Private seed commitment changed')
    for rel,h in freeze['audits'].items():
        if digest(ROOT/rel)!=h:raise RuntimeError('Independent audit changed')
    for rel,h in freeze['v1_source'].items():
        if digest(bootstrap.V1/rel)!=h:raise RuntimeError('Frozen benchmark dependency changed')
    maximum=sum(j['online_cap'] for j in plan)*len(POLICIES)
    decodes=sum(len(j['snapshot_budgets']) for j in plan)*len(POLICIES)
    if maximum>cfg['limits']['online_actions'] or decodes>cfg['limits']['endpoint_decodes']:raise RuntimeError('Planned development resource cap exceeded')
    seed=json.loads(seedfile.read_text())['development_seed'];out=Path(args.out)
    if out.exists():raise RuntimeError('No overwrites or automatic retries')
    out.mkdir();private=out/'private';private.mkdir(mode=0o700)
    started=time.monotonic();deadline=started+cfg['limits']['wall_seconds'];context=mp.get_context('spawn')
    counters={'task':0,'type':0,'offline':0};finished=0;status='completed';error=None;current=None
    receipt={'planned_trajectories':len(plan)*len(POLICIES),'maximum_online_actions':maximum,'planned_budget_snapshots':decodes,
        'freeze_sha256':digest(ROOT/'freeze.json'),'model_calls':0,'confirmation':False,'retries':0}
    (out/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (out/'trajectories.jsonl').open('x') as log,(out/'snapshots.jsonl').open('x') as snaps,(private/'reproduction.jsonl').open('x') as repro:
        try:
            for name in POLICIES:
                parent,child=context.Pipe();process=context.Process(target=worker,args=(child,name));process.start();child.close()
                try:
                    for i,job in enumerate(plan):
                        current={'policy':name,'job_index':i,'job':job}
                        if not process.is_alive():raise RuntimeError('Worker exited')
                        def snapshot(row):snaps.write(json.dumps(row,sort_keys=True)+'\n');snaps.flush()
                        final,priv,_=evaluate_job(parent,name,job,seed,deadline,counters,snapshot)
                        log.write(json.dumps(final,sort_keys=True)+'\n');log.flush()
                        repro.write(json.dumps(priv,sort_keys=True)+'\n');repro.flush();finished+=1
                        if i%16==0:print(json.dumps({'policy':name,'trajectories':finished,'online':counters['task']+counters['type'],'seconds':round(time.monotonic()-started,1)}),flush=True)
                    send(parent,None);process.join(timeout=5)
                    if process.is_alive() or process.exitcode!=0:raise RuntimeError('Worker shutdown failure')
                finally:
                    if process.is_alive():process.terminate();process.join(timeout=5)
                    parent.close()
        except Exception as exc:status='failed';error={'type':type(exc).__name__,'message':str(exc),'current':current}
    receipt.update(status=status,error=error,finished_trajectories=finished,costs_including_partial=dict(counters),
        online_actions=counters['task']+counters['type'],seconds=time.monotonic()-started)
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
    if status!='completed':raise SystemExit(1)


if __name__=='__main__':main()
