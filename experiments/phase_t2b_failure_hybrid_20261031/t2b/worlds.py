"""Trusted new development roster. No worlds sampled on import."""
import hashlib
from . import bootstrap
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment
NAMESPACE='phase_t2b_failure_hybrid_20261031'

def specs(cfg):
    rows=[];c=cfg['data'];e=cfg['evaluation']
    for split in e['splits']+['variable','smoke']:
        n=6 if split=='variable' else 2 if split=='smoke' else e['worlds_per_split']
        for i in range(n):
            partition=[[4],[1,3]][i%2];rates=c['train_rates'][(i//2)%3];alpha=c['alphas'][i%3]
            if split=='ood_parameters':rates=c['heldout_rates']
            if split=='ood_partition':partition=[2,2]
            if split=='ood_calibration':alpha=.5
            if split=='variable':partition=[[2],[1,1],[3],[1,2],[2],[1,2]][i];rates=c['train_rates'][i%3]
            kind='eval_'+split if split!='smoke' else 'smoke'
            rows.append({'world_id':hashlib.sha256(f'{NAMESPACE}|{kind}|{i}'.encode()).hexdigest()[:24], 'namespace':NAMESPACE,'kind':kind,'index':i,'partition':partition,'p':rates[0],'q':rates[1],'alpha':alpha,'R':64,'s':.8,'eta':.05,'online_cap':6144})
    return rows

def make_world(spec,seed,R=None):
    if spec['namespace']!=NAMESPACE or not seed:raise ValueError('New T2b development provenance required')
    R=spec['R'] if R is None else R
    ep=make_episode(f"{NAMESPACE}|{seed}|{spec['kind']}",'development',spec['index'],spec['partition'])
    return QueryEnvironment(ep,spec['p'],spec['q'],int(round(spec['alpha']*R)),spec['s'],spec['online_cap'],'iid',False,eta=spec['eta']),ep

def public_plan(cfg):
    rows=specs(cfg);out={'namespace':NAMESPACE,'worlds':[],'expected_paths':[],'expected_offline':[]}
    for s in rows:
        out['worlds'].append({k:v for k,v in s.items() if k not in ['p','q']})
        if s['kind']=='smoke':continue
        for R in ([64] if s['kind']=='eval_variable' else cfg['evaluation']['risks']):
            for m in cfg['evaluation']['methods']:
                out['expected_paths'].append({'world_id':s['world_id'],'split':s['kind'],'R':R,'method':m,'status':'completed'})
    return out
