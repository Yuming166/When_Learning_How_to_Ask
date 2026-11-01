"""Trusted development-only world construction and observable teacher rows."""
import hashlib
import itertools
import json
import os
import time
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .core import Scheduler, observed_state, teacher_target
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment

NAMESPACE='phase_t2_structure_allocator_20261031'

def spec(kind,index,partition,rates,alpha,R=64,behavior='teacher'):
    return {'world_id':hashlib.sha256(f'{NAMESPACE}|{kind}|{index}'.encode()).hexdigest()[:24], 'namespace':NAMESPACE,'kind':kind,'index':index,'partition':list(partition),'p':rates[0],'q':rates[1],'alpha':alpha,'R':R,'M':int(round(alpha*R)),'s':.8,'eta':.05,'online_cap':6144,'behavior':behavior}

def plans(cfg):
    c=cfg['data'];grid=list(itertools.product(c['train_partitions'],c['train_rates'],c['alphas'],c['R']))
    result={}
    for split,n in [('train',c['train_worlds']),('validation',c['validation_worlds'])]+[(s,c['test_worlds_per_split']) for s in c['splits']]:
        rows=[]
        for i in range(n):
            # A fixed coprime traversal spreads smaller splits over the grid.
            part,rates,alpha,R=grid[(i*37+({'train':0,'validation':17}.get(split,43)))%len(grid)]
            if split=='ood_parameters':rates=c['heldout_rates']
            if split=='ood_partition':part=c['heldout_partition']
            if split=='ood_calibration':alpha=c['heldout_alpha']
            behavior_index=int.from_bytes(hashlib.sha256(f'{NAMESPACE}|{split}|{i}|behavior'.encode()).digest()[:8],'big')%3
            rows.append(spec(split,i,part,rates,alpha,R,c['behaviors'][behavior_index]))
        result[split]=rows
    result['budget_development']=[spec('budget_development',i,[[4],[1,3]][i%2],c['train_rates'][(i//2)%3],c['alphas'][(i//6)%3],64) for i in range(cfg['budget_development']['worlds'])]
    for split in cfg['evaluation']['splits']:
        rows=[]
        for i in range(cfg['evaluation']['worlds_per_split']):
            part=[[4],[1,3]][i%2];rates=c['train_rates'][(i//2)%3];alpha=c['alphas'][i%3]
            if split=='ood_parameters':rates=c['heldout_rates']
            if split=='ood_partition':part=c['heldout_partition']
            if split=='ood_calibration':alpha=c['heldout_alpha']
            rows.append(spec('eval_'+split,i,part,rates,alpha))
        result['eval_'+split]=rows
    result['eval_variable']=[spec('eval_variable',i,[[2],[1,1],[3],[1,2],[2],[1,2]][i],c['train_rates'][i%3],c['alphas'][i%3]) for i in range(cfg['evaluation']['extra_variable_worlds'])]
    ids=[s['world_id'] for rows in result.values() for s in rows]
    if len(ids)!=len(set(ids)):raise AssertionError('World split overlap')
    return result

def make_world(s,seed,R=None):
    if s['namespace']!=NAMESPACE or not seed:raise ValueError('Fresh T2-only development namespace required')
    R=s['R'] if R is None else R
    episode=make_episode(f"{NAMESPACE}|{seed}|{s['kind']}",'development',s['index'],s['partition'])
    env=QueryEnvironment(episode,s['p'],s['q'],int(round(s['alpha']*R)),s['s'],s['online_cap'],'iid',False,eta=s['eta'])
    return env,episode

def execute_action(env,sampler):
    action=sampler.next(range(sampler.d))
    response=env.ask_type(action[1]) if action[0]=='type' else env.query(action[1],action[2])
    sampler.observe(action,response)
    return action,response

def collect(s,seed,deadline):
    from .information import build_cuts
    env,episode=make_world(s,seed);public=env.reset();cal=env.get_calibration();sampler=Scheduler(public,cal,s['R'],block=32)
    times=[2*public['d'],16,32,64,256,1024];rows=[];cut_arrays={}
    for k,t in enumerate(times):
        while sampler.t<t:
            if time.monotonic()>deadline:raise TimeoutError('Data collection deadline')
            if sampler.needs_update():
                state,_,_=observed_state(sampler,cal,s['R'],s['online_cap'])
                sampler.set_target(behavior_weights(s,state))
            execute_action(env,sampler)
        state,_,_=observed_state(sampler,cal,s['R'],s['online_cap']);start=time.perf_counter();target=teacher_target(state)
        row={'world_id':s['world_id'],'split':s['kind'],'position':k,'behavior':s['behavior'],'state':state,**target,'label_wall_seconds':time.perf_counter()-start}
        if s['kind']=='train':row['cuts']=build_cuts(state,target['teacher_weights'],target['teacher_K'])
        rows.append(row)
        if sampler.needs_update():sampler.set_target(behavior_weights(s,state,target))
    return rows,{'world_id':s['world_id'],'kind':s['kind'],'online':sampler.t,'costs':dict(env.cost),'truth':episode.truth,'types':episode.types,'provenance':episode.provenance}

def behavior_weights(s,state,target=None):
    if s['behavior']=='teacher':return (target or teacher_target(state))['teacher_weights']
    d=state['d'];G=len(state['groups']);w=np.zeros(2*d+G)
    if s['behavior']=='uniform':w[:2*d]=1/(2*d)
    else:
        for g,members in enumerate(state['groups']):
            for j in members:w[2*j+state['estimate']['z'][g]]=1/d
    return w

def load_rows(split,with_cuts=False):
    rows=[json.loads(s) for s in (ROOT/'artifacts/data'/f'{split}.jsonl').read_text().splitlines() if s]
    if with_cuts:
        with np.load(ROOT/'artifacts/data/train_cuts.npz',allow_pickle=False) as arrays:
            for i,row in enumerate(rows):row['cuts']={'cut_coefficients':arrays[f'c{i}'].tolist(),'cut_offsets':arrays[f'b{i}'].tolist()}
    return rows

def generate(cfg,seed):
    output=ROOT/'artifacts/data';output.mkdir(parents=True,exist_ok=False);private=output/'private';private.mkdir(mode=0o700)
    start=time.monotonic();deadline=start+1800;allplans=plans(cfg);manifest={'status':'started','world_counts':{},'state_counts':{},'generation_scope':'fresh development only','online_actions':0,'unique_offline_observations':0,'splits':{}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    cuts={}
    for split in ['train','validation']+cfg['data']['splits']:
        count=0
        with (output/f'{split}.jsonl').open('x') as stream:
            for s in allplans[split]:
                try:rows,provenance=collect(s,seed,deadline)
                except Exception:
                    manifest.update(status='failed',failed_world_id=s['world_id'],failed_world_partial_cost_unknown=True,wall_seconds=time.monotonic()-start)
                    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
                    raise
                for row in rows:
                    if 'cuts' in row:
                        cut=row.pop('cuts');cuts[f'c{count}']=np.asarray(cut['cut_coefficients'],dtype=np.float64);cuts[f'b{count}']=np.asarray(cut['cut_offsets'],dtype=np.float64)
                    stream.write(json.dumps(row,allow_nan=False)+'\n');count+=1
                stream.flush();p=private/(s['world_id']+'.json');p.write_text(json.dumps(provenance)+'\n');p.chmod(0o600)
                manifest['online_actions']+=provenance['online'];manifest['unique_offline_observations']+=provenance['costs']['offline']
                manifest['world_counts'][split]=manifest['world_counts'].get(split,0)+1
                manifest['state_counts'][split]=count
                (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
                print(json.dumps({'stage':'data','split':split,'worlds':manifest['world_counts'][split],'states':count}),flush=True)
        manifest['state_counts'][split]=count;manifest['splits'][split]=[s['world_id'] for s in allplans[split]]
    np.savez_compressed(output/'train_cuts.npz',**cuts)
    manifest.update(status='completed',wall_seconds=time.monotonic()-start,total_worlds=sum(manifest['world_counts'].values()),total_states=sum(manifest['state_counts'].values()))
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
