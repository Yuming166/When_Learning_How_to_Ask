"""Deterministic non-trained residual controls and bounded Bayesian lookahead."""
import math,time
from collections import Counter
import numpy as np
from . import bootstrap
from .belief import Belief,index,action,stable_argmax
from t1a.strategies import WithSolver
from t1a.solvers import Solver
from phase2e.strategies import FusedInformation,FusedDRRCType

MACROS=['KL','IG','TYPE','TASK']
POLICIES=['AnalyticReuse','Fused-Info','Fused-D-RRC-Type','Fixed-KL-IG','Type-Then-Task','Fresh-IG','Task-Only','Recovery-1','Lookahead-2']

def forced_index(t,L):
    n=math.isqrt(t//L);offset=t-L*n*n
    return int(offset) if offset<L else None

def candidate_indices(belief,kl,d):
    # Task prioritization optimizes the same complete-vector MAP utility as
    # lookahead. This makes a strong untrained objective-matched baseline.
    zp=np.asarray(belief.summary()['z_prob'])
    return [int(kl),stable_argmax(belief.ig()),2*d+stable_argmax(zp*(1-zp)),stable_argmax(belief.recovery()[:2*d])]

class Residual(WithSolver):
    def __init__(self,public,cal,R,mode,budget):
        super().__init__(public,cal,R,'AnalyticReuse',{})
        self.mode=mode;self.budget=int(budget);self.forecast_solver=Solver('AnalyticReuse')
        self.decisions=[];self.controller_stats=Counter();self.controller_cpu=0.;self.type_purchases=0
    def root_belief(self):
        if self.last_update==self.t and self._posterior is not None:return Belief(self._posterior,self.groups,self.type_accuracy,self.eta)
        return Belief.from_observation(self.counts,self.groups,self.calibration,self.types,self.type_accuracy,self.eta)
    def forecast_kl(self,belief,t,actual,cumulative):
        forced=forced_index(t,self.L)
        if forced is not None:return forced
        weights=self.weights
        if t>=self.next_update:
            e=belief.summary();epsilon=self.requested_tolerance(t);allocation=None
            for attempt in range(2):
                fit=self.forecast_solver([len(g) for g in self.groups],e['p'],e['q'],self.alpha,self.type_accuracy,self.eta,
                  tolerance=epsilon*.1**attempt,max_iterations=200)
                if -5e-8<=fit['relative_gap']<=max(5*epsilon,5e-8) and fit['minimum_information']>=1-1e-7:
                    allocation=fit;break
            if allocation is None:raise FloatingPointError('Hypothetical KL forecast failed numerical acceptance')
            weights=np.zeros(self.E)
            for g,mm in enumerate(self.groups):
                for j in mm:
                    weights[2*j+e['z'][g]]=allocation['a'][g]/allocation['K']
                    weights[2*j+1-e['z'][g]]=allocation['b'][g]/allocation['K']
                weights[self.L+g]=allocation['c'][g]/allocation['K']
            weights/=weights.sum()
        return int(np.argmax(cumulative+weights-actual))
    def lookahead(self,b,choices):
        f=b.first();moment=b.second();mass=b.theta_mass;by_action={};a1=choices[stable_argmax(b.recovery()[choices])]
        for a in dict.fromkeys(choices):
            total=0.;actual=self._actual_counts().copy();actual[a]+=1
            for y in [0,1]:
                prob,child=b.condition(a,y)
                kl=self.forecast_kl(child,self.t+1,actual,self.cumulative)
                forced=forced_index(self.t+1,self.L)
                nextchoices=[forced] if forced is not None else candidate_indices(child,kl,self.d)
                branch=[]
                for c in nextchoices:
                    if y:one=moment[:,a,c];zero=f[:,a]-one
                    else:one=f[:,c]-moment[:,a,c];zero=mass-f[:,a]-one
                    branch.append(float(max(one)+max(zero)))
                total+=max(branch)
            by_action[a]=total
        values=[by_action[a] for a in choices]
        best=stable_argmax(values);chosen=choices[best]
        a1_pos=choices.index(a1)
        return chosen,{'two_step_value':values[best],'two_step_value_after_myopic_first':values[a1_pos],
                       'nonmyopic_model_gain':values[best]-values[a1_pos],
                       'different_from_myopic_action':chosen!=a1,'q2':values}
    def next(self,active):
        base=super().next(active)
        if self.mode=='AnalyticReuse' or self.last_forced:return base
        begin=time.process_time();b=self.root_belief();kl=index(base,self.d)
        choices=candidate_indices(b,kl,self.d);diagnostic={};macro=None
        if self.mode=='Fixed-KL-IG':macro=0 if self.t<self.budget//2 else 1;chosen=choices[macro]
        elif self.mode=='Type-Then-Task':
            if self.type_purchases<self.G:chosen=self.L+self.type_purchases;macro=2
            else:chosen=choices[3];macro=3
        elif self.mode=='Fresh-IG':chosen=choices[1];macro=1
        elif self.mode=='Task-Only':chosen=choices[3];macro=3
        elif self.mode=='Recovery-1' or self.budget-self.t==1:
            macro=stable_argmax(b.recovery()[choices]);chosen=choices[macro]
        elif self.mode=='Lookahead-2':
            chosen,diagnostic=self.lookahead(b,choices);macro=choices.index(chosen)
        else:raise ValueError('Unknown residual mode')
        chosen_action=action(chosen,self.d);self._pending=chosen_action
        self.controller_stats['controlled_actions']+=1;self.controller_stats[MACROS[macro]]+=1
        if chosen>=self.L:self.type_purchases+=1
        elapsed=time.process_time()-begin;self.controller_cpu+=elapsed
        self.decisions.append({'online_before':self.t,'remaining_budget':self.budget-self.t,'macro':MACROS[macro],
          'primitive_action':chosen,'candidate_actions':choices,'posterior_MAP_probability':b.summary()['joint_MAP_probability'],
          'controller_cpu':elapsed,'forecast_solver_calls':self.forecast_solver.stats['calls'],**diagnostic})
        return chosen_action

def construct(name,public,cal,R,budget):
    if name=='Fused-Info':return FusedInformation(public,cal,R)
    if name=='Fused-D-RRC-Type':return FusedDRRCType(public,cal,R)
    return Residual(public,cal,R,name,budget)
