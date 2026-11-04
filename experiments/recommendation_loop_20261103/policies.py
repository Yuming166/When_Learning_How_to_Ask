"""Observable recommendation allocators; no stopping or private world inputs."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import time

import numpy as np

from likelihood import JointLikelihood
from decision_ig import QuadratureDecisionIG

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]/'research/general_catalogue_theory_20261103/general_geometry.py'
spec=importlib.util.spec_from_file_location('loop_information_geometry',SOURCE)
geometry=importlib.util.module_from_spec(spec); sys.modules[spec.name]=geometry
spec.loader.exec_module(geometry)

ARMS=('round_robin','joint_dr_rc','decision_ig','profile_kl','decision_kl')


def forced_action(t,d):
    length=2*d; n=math.isqrt(t//length); offset=t-length*n*n
    return offset if offset<length else None


def minimum_flips(winners,state):
    wrong=[f for f in range(1,len(winners)) if winners[state^f] != winners[state]]
    return tuple(f for f in wrong if not any(s!=f and s&f==s for s in wrong))


class ObservablePolicy:
    def __init__(self,name,public,*,quadrature_order=6,rate_gap=1e-8,
                 tolerance=1e-6,max_iterations=150):
        if name not in ARMS: raise ValueError('unknown arm')
        self.name=name
        self.model=JointLikelihood(public)
        if str(self.model.eta) != '1/100':
            raise ValueError('this pilot planner is bounded to eta=1/100')
        self.d,self.G=self.model.d,self.model.G
        self.groups=list(map(int,public['groups']))
        self.counts=np.zeros((self.d,2,2),dtype=np.int64)
        self.weights=np.full(2*self.d,1/(2*self.d))
        self.cumulative=np.zeros(2*self.d)
        self.t=0; self.next_update=2*self.d; self.pending=None
        self.updates=[]; self.last_choice={}; self.cache={}
        self.rate_gap=rate_gap; self.tolerance=tolerance; self.max_iterations=max_iterations
        self.posterior=QuadratureDecisionIG(public,order=quadrature_order) if name=='decision_ig' else None
        self.flip_cache={}

    def _flips(self,state):
        if self.name=='profile_kl': return tuple(1<<j for j in range(self.d))
        if state not in self.flip_cache:
            self.flip_cache[state]=minimum_flips(self.model.winner_by_theta,state)
        return self.flip_cache[state]

    def _update(self):
        wall,cpu=time.perf_counter(),time.process_time()
        estimate=self.model.estimate(self.counts)
        record={'online':self.t,'estimate':estimate,'inference':'all_task_data_joint_continuous_MLE',
                'status':None,'cache_hit':False}
        if estimate['p']-estimate['q'] <= self.rate_gap:
            self.weights=np.full(2*self.d,1/(2*self.d))
            record['status']='UNIDENTIFIED_RATES_UNIFORM_TARGET'
        elif self.name=='joint_dr_rc':
            self.weights=np.zeros(2*self.d)
            for j,g in enumerate(self.groups):
                self.weights[2*j+((estimate['z_mask']>>g)&1)]=1/self.d
            record['status']='UNIFORM_COORDINATES_ESTIMATED_BETTER_FORMAT'
        else:
            flips=self._flips(estimate['theta_mask'])
            if not flips:
                self.weights=np.full(2*self.d,1/(2*self.d))
                record['status']='PUBLIC_CONSTANT_DECISION_UNIFORM_TARGET'
            else:
                key=(flips,estimate['p'],estimate['q'])
                if key in self.cache:
                    allocation=self.cache[key]; record['cache_hit']=True
                else:
                    program=geometry.GeneralProgram(flips,self.groups,estimate['p'],estimate['q'])
                    allocation=program.solve(tolerance=self.tolerance,max_iterations=self.max_iterations)
                    if (not math.isfinite(allocation['numerically_repaired_upper_cost'])
                            or allocation['min_information_after_repair'] < 1-5e-6):
                        raise ArithmeticError('allocation failed the logged numerical feasibility check')
                    self.cache[key]=allocation
                oriented=np.array(allocation['allocation'],dtype=float)
                self.weights=np.zeros(2*self.d)
                for j,g in enumerate(self.groups):
                    fmt=(estimate['z_mask']>>g)&1
                    self.weights[2*j+fmt]=oriented[j]
                    self.weights[2*j+1-fmt]=oriented[self.d+j]
                self.weights/=self.weights.sum()
                record.update(status='FLOAT_CONTINUOUS_KL_TARGET',minimal_flips=list(flips),
                              allocation=allocation,solver_tolerance=self.tolerance,
                              solver_max_iterations=self.max_iterations,
                              asymptotic_error_contract_certified=False)
        if np.any(~np.isfinite(self.weights)) or np.any(self.weights<0) or abs(self.weights.sum()-1)>1e-8:
            raise ArithmeticError('invalid allocation weights')
        self.next_update=self.t+max(2*self.d,math.ceil(math.sqrt(self.t+1)))
        record.update(weights=self.weights.tolist(),next_update=self.next_update,
                      wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu)
        self.updates.append(record)

    def next(self):
        if self.pending is not None: raise RuntimeError('observe pending action first')
        if self.name in ('joint_dr_rc','profile_kl','decision_kl') and self.t>=self.next_update:
            self._update()
        self.cumulative+=self.weights
        forced=forced_action(self.t,self.d)
        details={'forced':forced is not None,'update_count':len(self.updates)}
        if forced is not None: action=forced; details['rule']='forced_exploration'
        elif self.name=='round_robin': action=self.t%(2*self.d); details['rule']='round_robin'
        elif self.name=='decision_ig':
            scores=np.asarray(self.posterior.scores(),dtype=float)
            if scores.shape != (2*self.d,) or np.any(~np.isfinite(scores)):
                raise ArithmeticError('invalid information-gain scores')
            best=scores.max(); ties=np.flatnonzero(scores>=best-1e-14)
            actual=self.counts.sum(axis=2).reshape(-1)
            action=int(ties[np.argmin(actual[ties])])
            details.update(rule='quadrature_decision_information_gain',selected_gain=float(scores[action]))
        else:
            action=int(np.argmax(self.cumulative-self.counts.sum(axis=2).reshape(-1)))
            details['rule']='cumulative_target_deficit'
        self.pending=int(action); self.last_choice=details
        return int(action)

    def observe(self,action,answer):
        if action != self.pending: raise ValueError('action does not match pending request')
        if isinstance(answer,bool) or not isinstance(answer,(int,np.integer)) or answer not in (0,1):
            raise ValueError('raw reply must be integer0/1')
        self.counts[action//2,action%2,answer]+=1
        if self.posterior is not None: self.posterior.observe(action,int(answer))
        self.t+=1; self.pending=None
