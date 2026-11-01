"""Strict observable boundary and matched scheduler. No evaluator inputs."""
import math
from copy import deepcopy
from time import perf_counter
import numpy as np
from . import bootstrap
from phase2b.aligned import TheoryAlignedTracking
from phase2e.estimator import posterior, public_estimate
from phase2a.coefficients import solve_allocation

SCHEMA = 't2_observable_v1'
KEYS = {'schema','d','groups','eta','known_s','counts','forced_counts','type_report_counts','calibration','R','online','online_cap','remaining','estimate','action_mask'}

def validate_state(state):
    if not isinstance(state,dict) or set(state)!=KEYS or state['schema']!=SCHEMA:
        raise ValueError('Observable state whitelist violated')
    s=deepcopy(state);d=s['d'];groups=s['groups'];G=len(groups)
    if type(d) is not int or d<1 or G<1 or any(not g for g in groups) or sorted(j for g in groups for j in g)!=list(range(d)):
        raise ValueError('Invalid partition')
    if any(type(j) is not int for g in groups for j in g):raise ValueError('Invalid fact index')
    for key,shape in [('counts',(d,2,2)),('forced_counts',(d,2,2)),('type_report_counts',(G,2))]:
        a=np.asarray(s[key])
        if a.shape!=shape or a.dtype.kind not in 'iu' or np.any(a<0):raise ValueError('Invalid observation counts')
    if np.any(np.asarray(s['forced_counts'])>np.asarray(s['counts'])):raise ValueError('Forced counts exceed actual')
    if set(s['calibration'])!={'high','low'}:raise ValueError('Calibration whitelist')
    for x in s['calibration'].values():
        if set(x)!={'successes','total'} or any(type(v) is not int for v in x.values()) or not 0<=x['successes']<=x['total']:raise ValueError('Calibration counts')
    if s['calibration']['high']['total']!=s['calibration']['low']['total']:raise ValueError('Unequal reference lengths')
    if not 0<float(s['eta'])<.5 or not math.isfinite(float(s['R'])) or s['R']<=0:raise ValueError('Invalid public risk/domain')
    known=s['known_s']
    if known is not None and (len(known)!=G or any(not .5<float(v)<1 for v in known)):raise ValueError('Known group accuracies')
    expected=[1]*(2*d)+[int(known is not None)]*G
    if s['action_mask']!=expected or any(type(v) is not int for v in s['action_mask']):raise ValueError('Action mask')
    if known is None and np.asarray(s['type_report_counts']).sum():raise ValueError('Unavailable reports')
    online=int(np.asarray(s['counts']).sum()+np.asarray(s['type_report_counts']).sum())
    if any(type(s[k]) is not int for k in ['online','online_cap','remaining']) or s['online']!=online or not 0<=online<=s['online_cap'] or s['remaining']!=s['online_cap']-online:raise ValueError('Time/budget inconsistent')
    e=s['estimate']
    if set(e)!={'p','q','theta_prob','z_prob','z'} or not .5<=e['q']<e['p']<=1-s['eta']:raise ValueError('Estimated rate domain')
    if len(e['theta_prob'])!=d or len(e['z_prob'])!=G or len(e['z'])!=G or any(type(v) is not int or v not in [0,1] for v in e['z']):raise ValueError('Estimated dimensions')
    if any(not math.isfinite(float(v)) or not 0<=v<=1 for v in e['theta_prob']+e['z_prob']):raise ValueError('Estimated probabilities')
    return s

def calibration_bits(summary):
    return {k:[1]*v['successes']+[0]*(v['total']-v['successes']) for k,v in summary.items()}

def observed_state(sampler,calibration,R,cap):
    start=perf_counter()
    fit=posterior(sampler.counts,sampler.groups,calibration,sampler.types,sampler.type_accuracy,sampler.eta)
    state={'schema':SCHEMA,'d':sampler.d,'groups':[list(g) for g in sampler.groups],'eta':sampler.eta,'known_s':list(sampler.type_accuracy) if sampler.type_accuracy is not None else None,
           'counts':sampler.counts.tolist(),'forced_counts':sampler.forced.tolist(),'type_report_counts':[[x.count(0),x.count(1)] for x in sampler.types],
           'calibration':{k:{'successes':sum(v),'total':len(v)} for k,v in calibration.items()},'R':float(R),'online':int(sampler.t),'online_cap':int(cap),'remaining':int(cap-sampler.t),
           'estimate':{k:fit[k] for k in ['p','q','theta_prob','z_prob','z']},'action_mask':[1]*(2*sampler.d)+[int(sampler.type_accuracy is not None)]*sampler.G}
    return validate_state(state),fit,perf_counter()-start

def expand_allocation(state,allocation):
    weights=np.zeros(2*state['d']+len(state['groups']))
    for g,members in enumerate(state['groups']):
        for j in members:
            weights[2*j+state['estimate']['z'][g]]=allocation['a'][g]/allocation['K']
            weights[2*j+1-state['estimate']['z'][g]]=allocation['b'][g]/allocation['K']
        weights[2*state['d']+g]=allocation['c'][g]/allocation['K']
    return normalize(weights,state)

def normalize(weights,state):
    values=np.asarray(weights,dtype=float);mask=np.asarray(state['action_mask'],dtype=bool)
    if values.shape!=mask.shape or np.any(~np.isfinite(values)) or np.any(values<0) or np.any(values[~mask]>1e-10) or abs(float(values.sum())-1)>1e-5:raise ValueError('Invalid continuous allocation')
    values[~mask]=0
    return values/values.sum()

def teacher_target(state,solver=None):
    state=validate_state(state);e=state['estimate'];epsilon=TheoryAlignedTracking.requested_tolerance(state['online']);attempts=[]
    solve=solve_allocation if solver is None else solver.solve
    for attempt in range(2):
        fit=solve([len(g) for g in state['groups']],e['p'],e['q'],state['calibration']['high']['total']/state['R'],state['known_s'],state['eta'],tolerance=epsilon*.1**attempt,max_iterations=200)
        attempts.append({'gap':fit['relative_gap'],'minimum_information':fit['minimum_information']})
        if -5e-8<=fit['relative_gap']<=max(5*epsilon,5e-8) and fit['minimum_information']>=1-1e-7:break
    else:raise RuntimeError('Teacher numerical acceptance failed')
    return {'teacher_weights':expand_allocation(state,fit).tolist(),'teacher_K':float(fit['K']),'solver':{'iterations':fit['iterations'],'cuts':fit['cuts'],'relative_gap':fit['relative_gap'],'attempts':attempts}}

class Scheduler(TheoryAlignedTracking):
    """Original square-block exploration and tracking; target injected externally."""
    def __init__(self,public,calibration,R,block=32):
        super().__init__(public,calibration,R);self.block=block;self.ready=False
    def needs_update(self):return self.t>=self.L and self.t>=self.next_update
    def set_target(self,weights):
        a=np.asarray(weights,dtype=float)
        if a.shape!=(self.E,) or np.any(~np.isfinite(a)) or np.any(a<0) or abs(a.sum()-1)>1e-6:raise ValueError('Illegal scheduler target')
        self.weights=a/a.sum();self.last_update=self.t;self.next_update=self.t+self.block
    def _update(self):raise RuntimeError('Planner must inject target before scheduling')
