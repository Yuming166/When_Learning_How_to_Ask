"""Frozen-objective/cadence factorial and predeclared untrained controls."""
import math,time
from collections import Counter
import numpy as np
from . import bootstrap
from t1a.strategies import WithSolver
from t1b.belief import Belief,index,action,stable_argmax
from phase2e.strategies import FusedInformation

POLICIES=['KL-Block','KL-Fresh','IG-Block','IG-Fresh','KL-32','IG-32',
          'IG-Fresh-Direct','Fresh-IG-Lite','Budget-Switch','Belief-Gated','IG-Group-Block','IG-Group-Fresh']
MAIN_FACTOR=['KL-Block','KL-Fresh','IG-Block','IG-Fresh']

def uncertainty(b):
 s=b.summary();z=np.clip(np.asarray(s['z_prob']),0,1)
 hz=-np.sum(np.where(z>0,z*np.log(np.maximum(z,1e-300)),0)+np.where(z<1,(1-z)*np.log(np.maximum(1-z,1e-300)),0))
 return {'theta_entropy_fraction':b.entropy()/(b.k['d']*math.log(2)),
   'type_entropy_fraction':float(hz)/(b.k['G']*math.log(2)),
   'p_hat':s['p'],'q_hat':s['q'],'estimated_gap':s['p']-s['q'],
   'joint_MAP_probability':s['joint_MAP_probability']}

def free_count(L,B):
 return sum((t-L*math.isqrt(t//L)**2)>=L for t in range(B))

class Factor(WithSolver):
 def __init__(self,public,cal,R,objective='KL',cadence='sqrt',execution='track',budget=32):
  super().__init__(public,cal,R,'AnalyticReuse',{})
  self.objective=objective;self.cadence=cadence;self.execution=execution;self.budget=budget;self.allow_type=True
  self.component_cpu=Counter();self.update_history=[];self.action_history=[];self.rule_counts=Counter();self.fit_online=None
 def _estimate(self):
  begin=time.process_time()
  try:
   fit=super()._estimate();self.fit_online=self.t;return fit
  finally:self.component_cpu['posterior']+=time.process_time()-begin
 def current_belief(self):
  if self.fit_online!=self.t:self._estimate()
  return Belief(self._posterior,self.groups,self.type_accuracy,self.eta)
 def _update(self):
  begin=time.process_time();before=self.component_cpu['posterior']
  if self.objective=='KL':super()._update()
  else:
   FusedInformation._update(self)
   if self.objective=='IG-Group':
    # Same normalized group-uniform target space as KL; reuse frozen log IG.
    from scipy.special import logsumexp
    logs=np.asarray([v if v is not None else -np.inf for v in self.last_estimate['action_log_information']])
    candidates=[]
    for members in self.groups:
     for fmt in range(2):candidates.append(float(logsumexp([logs[2*j+fmt] for j in members])-math.log(len(members))))
    candidates.extend(logs[self.L:].tolist());winner=int(np.argmax(candidates));self.weights=np.zeros(self.E)
    if winner<2*self.G:
     g,fmt=divmod(winner,2)
     for j in self.groups[g]:self.weights[2*j+fmt]=1/len(self.groups[g])
    else:self.weights[self.L+winner-2*self.G]=1
    self.weights/=self.weights.sum();self.last_estimate.update(weights=self.weights.tolist(),allocation_rule='group_uniform_expected_theta_information',group_log_information=[v if np.isfinite(v) else None for v in candidates],paid_type_target_mass=float(self.weights[self.L:].sum()))
  if self.cadence=='fresh':self.next_update=self.t+1
  elif self.cadence=='32':self.next_update=self.t+32
  self.last_estimate['next_update']=self.next_update
  self.component_cpu['target']+=max(0,time.process_time()-begin-(self.component_cpu['posterior']-before))
  self.update_history.append({'online':self.t,'next_update':self.next_update,'objective':self.objective,
   'cadence':self.cadence,'weights':self.weights.tolist(),'posterior_online':self.fit_online})
 def _record(self,a,track):
  self.action_history.append({'online_before':self.t,'action':index(a,self.d),'forced':self.last_forced,
    'tracked_candidate':track,'target_argmax':int(np.argmax(self.weights)),'last_target_update':self.last_update,
    'posterior_online':self.fit_online,'selection_rule':self.execution})
 def next(self,active):
  a=super().next(active);tracked=index(a,self.d)
  if self.execution=='direct' and not self.last_forced:
   a=action(int(np.argmax(self.weights)),self.d);self._pending=a
  self._record(a,tracked);return a

class FreshLite(Factor):
 """T1b Fresh-IG physical semantics, without unused KL/candidate work."""
 def __init__(self,public,cal,R,budget):super().__init__(public,cal,R,'IG','fresh_free','direct_dense',budget)
 def next(self,active):
  if self._pending is not None:raise RuntimeError('Pending observation')
  if set(active)!=set(range(self.d)):raise ValueError('All targets active')
  forced=self._forced_index();self.last_forced=forced is not None
  if forced is None:
   wall=time.perf_counter();begin=time.process_time();before=self.component_cpu['posterior']
   b=self.current_belief();chosen=stable_argmax(b.ig());self.weights=np.zeros(self.E);self.weights[chosen]=1
   self.last_update=self.t;self.next_update=self.t+1
   elapsed=time.process_time()-begin
   self.component_cpu['target']+=max(0,elapsed-(self.component_cpu['posterior']-before))
   self.planner_cpu_seconds+=elapsed;self.planner_seconds+=time.perf_counter()-wall
   self.last_estimate={**b.summary(),'online':self.t,'weights':self.weights.tolist(),'next_update':self.next_update,
    'allocation_rule':'current_joint_theta_mutual_information_direct_dense_stable_tie'}
   self.estimates.append(self.last_estimate)
   self.update_history.append({'online':self.t,'next_update':self.next_update,'objective':'IG','cadence':'fresh_free',
     'weights':self.weights.tolist(),'posterior_online':self.fit_online})
  else:chosen=forced
  self.cumulative+=self.weights;a=action(chosen,self.d);self._pending=a;self._record(a,chosen);return a

class Switching(Factor):
 def __init__(self,public,cal,R,budget,mode):
  super().__init__(public,cal,R,'KL','sqrt','residual',budget);self.mode=mode;self.free_seen=0;self.total_free=free_count(self.L,budget)
 def next(self,active):
  a=super().next(active)
  if self.last_forced:return a
  start=time.process_time();before=self.component_cpu['posterior'];remaining_free=self.total_free-self.free_seen
  diagnostic={};choose_ig=False
  if self.mode=='Budget-Switch':choose_ig=self.free_seen>=math.ceil(self.total_free/2)
  else:choose_ig=True
  if choose_ig:
   b=self.current_belief();scores=b.ig();best=stable_argmax(scores);maximum=float(scores[best])
   ratio=1. if maximum<=1e-14 else float(scores[index(a,self.d)]/maximum)
   diagnostic={**uncertainty(b),'kl_to_best_IG_ratio':ratio,'remaining_free_queries':remaining_free}
   if self.mode=='Belief-Gated':choose_ig=maximum>1e-14 and (remaining_free<=8 or ratio<.75)
   if choose_ig:a=action(best,self.d);self._pending=a
  self.rule_counts['IG' if choose_ig else 'KL']+=1;self.free_seen+=1
  self.component_cpu['controller']+=max(0,time.process_time()-start-(self.component_cpu['posterior']-before))
  self.action_history[-1].update(action=index(a,self.d),selection_rule='IG' if choose_ig else 'KL',**diagnostic)
  return a

def construct(name,public,cal,R,B):
 mapping={'KL-Block':('KL','sqrt','track'),'KL-Fresh':('KL','fresh','track'),
   'IG-Block':('IG','sqrt','track'),'IG-Fresh':('IG','fresh','track'),
   'KL-32':('KL','32','track'),'IG-32':('IG','32','track'),
   'IG-Fresh-Direct':('IG','fresh','direct'),'IG-Group-Block':('IG-Group','sqrt','track'),
   'IG-Group-Fresh':('IG-Group','fresh','track')}
 if name in mapping:return Factor(public,cal,R,*mapping[name],budget=B)
 if name=='Fresh-IG-Lite':return FreshLite(public,cal,R,B)
 if name in ['Budget-Switch','Belief-Gated']:return Switching(public,cal,R,B,name)
 raise ValueError('Unknown policy')
