"""Trusted bounded CPU evaluator. Learner process gets only public job fields."""
import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import time
from .data import make_episode
from .environment import QueryEnvironment
from .policies import NAMES
from .rpc import worker,send,receive
from .security import protect_evaluator

ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()


def frozen_files():
    paths=sorted((ROOT/'qrelbench').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))
    paths += [ROOT/'configs/development.json',ROOT/'PROTOCOL.md']
    return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}


def build_jobs(cfg):
    if cfg['split']!='development':raise ValueError('Only development is authorized')
    lo,hi=cfg['split_ranges']['development'];jobs=[]
    for partition in cfg['partitions']:
        for budget in cfg['fixed_budget']['budgets']:
            for i in range(cfg['fixed_budget']['episodes']):
                jobs.append({'protocol':'fixed_budget','scenario':'base','partition':partition,'index':lo+i,
                    'online_cap':budget,'calibration_size':cfg['fixed_budget']['calibration_size'],'delta':None,
                    'p':cfg['p'],'q':cfg['q'],'s':cfg['type_accuracy'],'channel':'iid'})
        for delta in cfg['fixed_confidence']['deltas']:
            for i in range(cfg['fixed_confidence']['episodes']):
                jobs.append({'protocol':'fixed_confidence','scenario':'base','partition':partition,'index':lo+1000+i,
                    'online_cap':cfg['fixed_confidence']['online_cap'],
                    'calibration_size':math.ceil(cfg['fixed_confidence']['calibration_alpha']*math.log(1/delta)),
                    'delta':delta,'p':cfg['p'],'q':cfg['q'],'s':cfg['type_accuracy'],'channel':'iid'})
    controls=cfg['controls']
    for c,scenario in enumerate(controls['cases']):
        for protocol,n in [('fixed_budget',controls['episodes']),('fixed_confidence',controls['confidence_episodes'])]:
            for i in range(n):
                p,q=cfg['p'],cfg['q'];s=cfg['type_accuracy'];partition=[8,8];channel='iid'
                if scenario=='equal_informative':p=q=(p+q)/2
                if scenario=='equal_chance':p=q=.5
                if scenario=='no_sharing':partition=[1]*cfg['d']
                if scenario=='perfect_type':s=1.
                if scenario in ['persistent','label_asymmetric']:channel=scenario
                delta=controls['confidence_delta'] if protocol=='fixed_confidence' else None
                jobs.append({'protocol':protocol,'scenario':scenario,'partition':partition,'index':lo+2000+c*100+i,
                    'online_cap':controls['confidence_cap'] if delta else controls['budget'],
                    'calibration_size':math.ceil(cfg['fixed_confidence']['calibration_alpha']*math.log(1/delta)) if delta else cfg['fixed_budget']['calibration_size'],
                    'delta':delta,'p':p,'q':q,'s':s,'channel':channel})
    assert all(lo<=j['index']<=hi and sum(j['partition'])==cfg['d'] for j in jobs)
    return jobs


def evaluate_job(conn,policy,job,master_seed,deadline):
    protect_evaluator()
    episode=make_episode(master_seed,'development',job['index'],job['partition'])
    env=QueryEnvironment(episode,job['p'],job['q'],job['calibration_size'],job['s'],job['online_cap'],job['channel'],policy=='Oracle Format')
    public_job={k:job[k] for k in ['protocol','online_cap','delta']}
    send(conn,public_job)
    allowed={'reset':env.reset,'query':env.query,'ask_type':env.ask_type,'get_calibration':env.get_calibration,'submit':env.submit}
    submitted=False
    while True:
        if time.monotonic()>deadline:raise TimeoutError('Global pilot timeout')
        if not conn.poll(min(1,max(.001,deadline-time.monotonic()))):continue
        message=receive(conn)
        if 'worker_error' in message:raise RuntimeError(message['worker_error'])
        if 'done' in message:
            if not submitted:raise RuntimeError('Worker returned without submission')
            details=message['done'];break
        method=message.get('method');args=message.get('args')
        if method not in allowed or not isinstance(args,dict):raise RuntimeError('Rejected private or malformed RPC')
        try:result=allowed[method](**args)
        except Exception as exc:
            # No internal object repr, rates, seeds or reward in error messages.
            send(conn,{'error':type(exc).__name__});raise
        submitted |= method=='submit'
        send(conn,{'result':result})
    score=env.score();assert score['online']==details['online_actions']
    assert score['online']<=job['online_cap']
    certified=details['certified_predictions']
    any_cert_error=any(int(value)!=episode.truth[int(j)] for j,value in certified.items())
    result={**job,'policy':policy,'episode_id':episode.public['episode_id'],**score,
            'completed':details['completed'],'certified':details['certified'],
            'worker_isolation':details['worker_isolation'],
            'any_certificate_error':any_cert_error,'censored':not details['completed'],
            'certificate_contract_valid':job['channel']=='iid',
            'empirical_scope':'CPU development controlled channel only'}
    return result,{'private_provenance':episode.provenance,'truth':episode.truth,'types':episode.types,
                   'records':episode.records,'public':episode.public,'trace_prefix':env.trace,
                   'counts':details['counts'],'certified_predictions':certified}


def main():
    protect_evaluator()
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(ROOT/'configs/development.json'))
    parser.add_argument('--out',default=str(ROOT/'artifacts/run'));args=parser.parse_args()
    config_bytes=Path(args.config).read_bytes()
    cfg=json.loads(config_bytes);jobs=build_jobs(cfg)
    freeze=json.loads((ROOT/'freeze.json').read_text());assert freeze['files']==frozen_files(),'Frozen source mismatch'
    assert sha(config_bytes)==freeze['files']['configs/development.json'],'Selected config is not frozen'
    seed_bytes=(ROOT/'artifacts/private/evaluator_seed.json').read_bytes()
    assert sha(seed_bytes)==freeze['private_seed_commitment'],'Private seed commitment mismatch'
    assert cfg['master_seed'] is None,'Do not publish a usable evaluation seed'
    master_seed=json.loads(seed_bytes)['development_master_seed']
    planned=sum(j['online_cap'] for j in jobs)*len(NAMES)
    assert planned<=cfg['limits']['maximum_online_actions']
    out=Path(args.out);assert not out.exists(),'No overwrites or silent reruns'
    out.mkdir(parents=True);private=out/'private';private.mkdir(mode=0o700)
    start=time.monotonic();deadline=start+cfg['limits']['wall_seconds'];attempted=actions=0
    status='completed';error=None
    context=mp.get_context('spawn')
    receipt={'planned_episodes':len(jobs)*len(NAMES),'maximum_planned_online_actions':planned,
             'freeze_sha256':sha((ROOT/'freeze.json').read_bytes()),'selected_config_sha256':sha(config_bytes),
             'pid':os.getpid(),'protocol':'development only'}
    (out/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (out/'episodes.jsonl').open('x') as log,(private/'reproduction.jsonl').open('x') as provenance:
        try:
            for policy in NAMES:
                parent,child=context.Pipe();process=context.Process(target=worker,args=(child,policy));process.start();child.close()
                try:
                    for ji,job in enumerate(jobs):
                        if not process.is_alive():raise RuntimeError('Learner process exited')
                        result,details=evaluate_job(parent,policy,job,master_seed,deadline)
                        log.write(json.dumps(result,sort_keys=True)+'\n');log.flush()
                        provenance.write(json.dumps({'policy':policy,'job':job,**details},sort_keys=True)+'\n');provenance.flush()
                        attempted+=1;actions+=result['online']
                        if ji%64==0:print(json.dumps({'policy':policy,'episodes':attempted,'online':actions,'seconds':round(time.monotonic()-start,1)}),flush=True)
                    send(parent,None);process.join(timeout=5)
                    if process.is_alive():raise TimeoutError('Worker shutdown timeout')
                    if process.exitcode!=0:raise RuntimeError('Worker failed')
                finally:
                    if process.is_alive():process.terminate();process.join(timeout=5)
                    parent.close()
        except Exception as exc:
            status='failed';error={'type':type(exc).__name__,'message':str(exc)}
    receipt.update(status=status,error=error,attempted_episodes=attempted,online_actions=actions,
                   seconds=time.monotonic()-start,retries=0,confirmation=False,llm_calls=0)
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)
    if status!='completed':raise SystemExit(1)


if __name__=='__main__':main()
