"""Bounded, paired CPU development run; no external inference or private APIs."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import time
import traceback

# Set before importing numerical libraries, including in fresh worker processes.
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'

import numpy as np

from certification import CertifiedDecisionGate
from policies import ARMS, ObservablePolicy

HERE=Path(__file__).resolve().parent


def initialize_worker():
    if hasattr(os,'sched_getaffinity'):
        allowed=sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0,{allowed[os.getpid()%min(2,len(allowed))]})


def stable_seed(root,label):
    return int.from_bytes(hashlib.sha256(f'{root}|{label}'.encode()).digest()[:8],'big')


def make_worlds(config):
    worlds=[]
    for cat in config['catalogues']:
        for profile in config['profiles']:
            if profile=='anchor_all_positive': theta=[1]*cat['d']
            else:
                rng=np.random.default_rng(stable_seed(config['seed_root'],cat['name']+'|profile|'+profile))
                theta=[int(x) for x in rng.choice([-1,1],size=cat['d'])]
            for index,groups in enumerate(cat['partitions']):
                name=f"{cat['name']}__{profile}__partition{index}"
                rng=np.random.default_rng(stable_seed(config['seed_root'],name+'|types'))
                types=[int(x) for x in rng.integers(0,2,size=max(groups)+1)]
                public={'d':cat['d'],'groups':groups.copy(),'eta':config['eta'],
                        'catalogue':{'offsets':cat['offsets'],'slopes':cat['slopes']}}
                utilities=[Fraction(b)+sum(Fraction(v)*x for v,x in zip(row,theta))
                           for b,row in zip(cat['offsets'],cat['slopes'])]
                winner=max(range(len(utilities)),key=lambda i:utilities[i])
                assert utilities.count(utilities[winner])==1
                worlds.append({'id':name,'profile_cluster':cat['name']+'__'+profile,
                               'catalogue_name':cat['name'],'profile_kind':profile,
                               'partition_index':index,'public':public,
                               'private':{'theta':theta,'types':types,'p':config['generating_p'],
                                          'q':config['generating_q'],'winner':winner,
                                          'response_seed':stable_seed(config['seed_root'],name+'|responses')}})
    return worlds


def run_arm(world,arm,config):
    wall,cpu=time.perf_counter(),time.process_time()
    record={'world_id':world['id'],'profile_cluster':world['profile_cluster'],
            'catalogue_name':world['catalogue_name'],'profile_kind':world['profile_kind'],
            'partition_index':world['partition_index'],'arm':arm,'status':'RUNNING',
            'history':[],'certificate':None,'certified_output':None,'certified_correct':None,
            'failure':None,'postprocessing_failure':None,
            'runtime':{'cpu_affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
                       'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}},
            'undetermined_gate_events':[],'gate_calls':0,'screen_checks':0,
            'policy_seconds':0.,'policy_cpu_seconds':0.,'gate_seconds':0.,'gate_cpu_seconds':0.}
    policy=None
    try:
        start,pcpu=time.perf_counter(),time.process_time()
        # Reconstruct only the public dictionary: the policy never receives world/private.
        public=json.loads(json.dumps(world['public']))
        policy=ObservablePolicy(arm,public,quadrature_order=config['quadrature_order'],
                                rate_gap=config['unidentified_rate_gap'],
                                tolerance=config['planner_tolerance'],
                                max_iterations=config['planner_max_iterations'])
        record['policy_seconds']+=time.perf_counter()-start
        record['policy_cpu_seconds']+=time.process_time()-pcpu
        gate=CertifiedDecisionGate(public,R=config['R'])
        private=world['private']; d=public['d']
        uniforms=[np.random.default_rng(stable_seed(private['response_seed'],str(a))).random(config['max_queries'])
                  for a in range(2*d)]
        consumed=np.zeros(2*d,dtype=int)
        final_gate=None
        for t in range(config['max_queries']):
            start,pcpu=time.perf_counter(),time.process_time()
            action=policy.next()
            record['policy_seconds']+=time.perf_counter()-start
            record['policy_cpu_seconds']+=time.process_time()-pcpu
            j,fmt=divmod(action,2)
            accuracy=float(Fraction(private['p'] if fmt==private['types'][public['groups'][j]] else private['q']))
            correct=bool(uniforms[action][consumed[action]]<accuracy)
            consumed[action]+=1
            answer=int((private['theta'][j]>0)==correct)
            choice=dict(policy.last_choice)
            start,pcpu=time.perf_counter(),time.process_time()
            policy.observe(action,answer)
            record['policy_seconds']+=time.perf_counter()-start
            record['policy_cpu_seconds']+=time.process_time()-pcpu
            start,pcpu=time.perf_counter(),time.process_time()
            screen=gate.model.decision_gap(policy.counts)
            threshold=config['R']+float(np.log1p(policy.counts.sum(axis=2)).sum())
            record['screen_checks']+=1
            exact=(screen['gap']>=threshold-config['gate_screen_margin']
                   or (t+1)%config['exact_gate_checkpoint']==0 or t+1==config['max_queries'])
            checked_gate=gate.check(policy.counts) if exact else None
            if checked_gate is not None: final_gate=checked_gate
            record['gate_seconds']+=time.perf_counter()-start
            record['gate_cpu_seconds']+=time.process_time()-pcpu
            record['gate_calls']+=int(exact)
            record['history'].append({'t':t+1,'action':action,'answer':answer,**choice,
                                      'gate_status':checked_gate['status'] if exact else 'SCREENED_CONTINUE',
                                      'screen_gap':screen['gap'],'screen_threshold':threshold})
            if exact and checked_gate['status']=='UNDETERMINED':
                record['undetermined_gate_events'].append({'t':t+1,'reason':final_gate['reason']})
            if exact and checked_gate['certified']:
                record['status']='CERTIFIED'; record['certificate']=final_gate
                record['certified_output']=int(final_gate['item'])
                record['certified_correct']=bool(final_gate['item']==private['winner'])
                break
        if record['status']=='RUNNING': record['status']='CAPPED_UNCERTIFIED'
        record['last_gate']=final_gate
        record['terminal_estimate_for_diagnostics_only']=policy.model.estimate(policy.counts)
        if policy.posterior is not None: record['posterior_diagnostics']=policy.posterior.diagnostics()
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        if record['certificate'] is not None:
            record['postprocessing_failure']=error
        else:
            record['status']='FAILED_UNCERTIFIED';record['failure']=error
    if policy is not None:
        record['queries']=int(policy.t)
        record['counts']=policy.counts.tolist()
        record['updates']=policy.updates
        record['forced_queries']=sum(int(x['forced']) for x in record['history'])
    else:
        record.update(queries=0,counts=None,updates=[],forced_queries=0)
    record['restricted_query_cost']=record['queries'] if not record['status'].startswith('FAILED') else None
    record['wall_seconds']=time.perf_counter()-wall; record['cpu_seconds']=time.process_time()-cpu
    record['risk_R']=config['R']; record['risk_bound']=math.exp(-config['R'])
    return record


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['smoke','pilot'],required=True)
    parser.add_argument('--label',default=None,help='new output namespace; existing output is never overwritten')
    args=parser.parse_args(); config=json.loads((HERE/'config.json').read_text())
    worlds=make_worlds(config)
    if args.mode=='smoke':
        config={**config,'max_queries':24,'workers':1}
        worlds=[worlds[0],worlds[-1]]
    else:
        freeze=json.loads((HERE/'FREEZE.json').read_text())
        for name,digest in freeze['source_sha256'].items():
            assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
        for name,digest in freeze['dependency_sha256'].items():
            assert hashlib.sha256((HERE.parents[1]/name).read_bytes()).hexdigest()==digest,name
        assert freeze['worlds_sha256']==hashlib.sha256(json.dumps(worlds,sort_keys=True).encode()).hexdigest()
    label=args.label or args.mode
    if not label.replace('_','').replace('-','').isalnum():raise ValueError('invalid output label')
    output=HERE/'artifacts'/label
    output.mkdir(parents=True,exist_ok=False)
    (output/'worlds.json').write_text(json.dumps(worlds,indent=2)+'\n')
    (output/'effective_config.json').write_text(json.dumps(config,indent=2)+'\n')
    jobs=[(world,arm) for world in worlds for arm in config['arms']]
    (output/'planned_jobs.json').write_text(json.dumps([{'world_id':w['id'],'arm':a} for w,a in jobs],indent=2)+'\n')
    summary=[]
    def collect(world,arm,result):
        file=f"{world['id']}__{arm}.json"
        (output/file).write_text(json.dumps(result,indent=2)+'\n')
        row={key:result[key] for key in ['world_id','profile_cluster','catalogue_name','profile_kind',
             'partition_index','arm','status','queries','restricted_query_cost','certified_output',
             'certified_correct','failure','wall_seconds','cpu_seconds','policy_seconds','gate_seconds','gate_calls']}
        summary.append(row)
        print(json.dumps({'done':len(summary),'total':len(jobs),**row}),flush=True)
    def infrastructure_failure(world,arm,exc):
        return {**{key:world[key] for key in ['profile_cluster','catalogue_name','profile_kind','partition_index']},
                'world_id':world['id'],'arm':arm,'status':'FAILED_INFRASTRUCTURE_UNCERTIFIED',
                'queries':None,'restricted_query_cost':None,'certified_output':None,'certified_correct':None,
                'failure':{'type':type(exc).__name__,'message':str(exc)},'wall_seconds':None,'cpu_seconds':None,
                'policy_seconds':None,'gate_seconds':None,'gate_calls':None,'history':None,'updates':None,'counts':None,
                'certificate':None}
    with ProcessPoolExecutor(max_workers=config['workers'],initializer=initialize_worker) as pool:
        futures={}
        for world,arm in jobs:
            try:futures[pool.submit(run_arm,world,arm,config)]=(world,arm)
            except Exception as exc:collect(world,arm,infrastructure_failure(world,arm,exc))
        for future in as_completed(futures):
            world,arm=futures[future]
            try:result=future.result()
            except Exception as exc:result=infrastructure_failure(world,arm,exc)
            collect(world,arm,result)
    summary.sort(key=lambda x:(x['world_id'],x['arm']))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'stage':args.mode,'attempted':len(summary),
                      'certified':sum(x['status']=='CERTIFIED' for x in summary),
                      'capped':sum(x['status']=='CAPPED_UNCERTIFIED' for x in summary),
                      'failed':sum(x['status'].startswith('FAILED') for x in summary)}),flush=True)


if __name__=='__main__': main()
