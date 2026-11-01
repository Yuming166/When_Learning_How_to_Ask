"""Observable-data information tracking with forced exploration; no true state API."""
import math
import time
import numpy as np
from .coefficients import solve_allocation,oracle_coefficient,gamma,fit_ordered


class InformationTracking:
    def __init__(self,public,calibration,planning_delta=.05,update_every=32):
        self.public=public;self.calibration=calibration;self.d=public['d'];self.G=len(public['groups'])
        if self.G>2:raise ValueError('Phase2a supports G<=2')
        self.counts=np.zeros((self.d,2,2),dtype=np.int64)
        self.forced=np.zeros_like(self.counts);self.types=[[] for _ in range(self.G)]
        self.alpha=len(calibration['high'])/math.log(1/planning_delta)
        self.eta=public['rate_domain']['eta'];self.update_every=update_every
        self.weights=np.r_[np.full(2*self.d,1/(2*self.d)),np.zeros(self.G)]
        self.cumulative=np.zeros(2*self.d+self.G);self.t=0;self.next_update=2*self.d
        self.estimates=[];self.last_forced=False;self.planner_seconds=0.;self.last_estimate=None

    def _estimate(self):
        n=self.forced.sum(axis=2)
        means=np.divide(self.forced[:,:,1],n,out=np.full(n.shape,.5),where=n>0)
        theta=(means.sum(axis=1)>1).astype(int)
        cal=self.calibration;M=len(cal['high']);eta=self.eta
        p,q=fit_ordered(sum(cal['high']),M,sum(cal['low']),M,eta) if M else (.75,.55)
        z=np.zeros(self.G,dtype=int)
        # Finite iterations define the precommitted estimator. Forced observations
        # alone identify signs/types consistently; calibration and type data assist.
        for _ in range(3):
            for g,group in enumerate(self.public['groups']):
                scores=[];s=self.public['type_accuracy'][g]
                for candidate in [0,1]:
                    value=0.
                    for j in group['targets']:
                        for m in [0,1]:
                            r=p if m==candidate else q
                            good=self.forced[j,m,theta[j]];bad=self.forced[j,m,1-theta[j]]
                            value+=good*math.log(r)+bad*math.log1p(-r)
                    for answer in self.types[g]:value+=math.log(s if answer==candidate else 1-s)
                    scores.append(value)
                z[g]=int(scores[1]>scores[0])
            good_s=sum(cal['high']);good_n=M;bad_s=sum(cal['low']);bad_n=M
            for j in range(self.d):
                g=self.public['targets'][j]['group'];m=z[g]
                good_s+=self.forced[j,m,theta[j]];good_n+=n[j,m]
                bad_s+=self.forced[j,1-m,theta[j]];bad_n+=n[j,1-m]
            p,q=fit_ordered(good_s,good_n,bad_s,bad_n,eta)
            # A vanishing estimator projection, not a known true-gap assumption.
            eps=.02/(1+math.log1p(self.t))
            if p-q<eps:
                middle=(p+q)/2
                q=max(.5,min(1-eta-eps,middle-eps/2));p=q+eps
        return {'theta':theta.tolist(),'z':z.tolist(),'p':float(p),'q':float(q),
                'forced_tasks':int(self.forced.sum()),'alpha_effective':self.alpha,
                'projection_gap_floor':.02/(1+math.log1p(self.t))}

    def _update(self):
        start=time.monotonic();est=self._estimate();part=[len(g['targets']) for g in self.public['groups']]
        p,q=est['p'],est['q']
        # Independently checked Theorem3 shortcut; coefficient phase-map solver
        # itself never uses this shortcut (avoids circular boundary verification).
        if gamma(self.d,min(part),p,q,self.alpha,self.eta)>=1-1e-10:
            oracle=oracle_coefficient(self.d,p,q,self.alpha,self.eta)
            allocation={'K':oracle['K'],'a':[oracle['a']]*self.G,'b':[0.]*self.G,'c':[0.]*self.G,
                        'relative_gap':0.,'minimum_information':min(1.,gamma(self.d,min(part),p,q,self.alpha,self.eta)),'shortcut':'Theorem3'}
        else:
            allocation=solve_allocation(part,p,q,self.alpha,self.public['type_accuracy'],self.eta,tolerance=2e-6)
        weights=np.zeros(2*self.d+self.G)
        for g,group in enumerate(self.public['groups']):
            z=est['z'][g]
            for j in group['targets']:
                weights[2*j+z]=allocation['a'][g]/allocation['K']
                weights[2*j+1-z]=allocation['b'][g]/allocation['K']
            weights[2*self.d+g]=allocation['c'][g]/allocation['K']
        if abs(weights.sum()-1)>1e-7:raise RuntimeError('Tracking target does not sum to one')
        self.weights=weights;seconds=time.monotonic()-start;self.planner_seconds+=seconds
        self.last_estimate={**est,'online':self.t,'weights':weights.tolist(),'estimated_K':allocation['K'],
            'solver_relative_gap':allocation['relative_gap'],'solver_seconds':seconds,
            'minimum_information':allocation['minimum_information']}
        self.estimates.append(self.last_estimate)

    def next(self,active):
        if self.t>=self.next_update:
            self._update();self.next_update=self.t+self.update_every
        self.cumulative+=self.weights
        minimum=.5*math.sqrt((self.t+1)/self.d)
        forced_n=self.forced.sum(axis=2).reshape(-1)
        deficient=np.flatnonzero(forced_n<minimum)
        if len(deficient):
            index=int(deficient[np.argmin(forced_n[deficient])]);self.last_forced=True
            return ('query',index//2,'AB'[index%2])
        self.last_forced=False
        actual=np.r_[self.counts.sum(axis=2).reshape(-1),[len(x) for x in self.types]]
        index=int(np.argmax(self.cumulative-actual))
        if index<2*self.d:return ('query',index//2,'AB'[index%2])
        return ('type',index-2*self.d)

    def observe(self,action,result):
        self.t+=1
        if action[0]=='type':self.types[action[1]].append('AB'.index(result['format']));return
        _,j,m=action;m='AB'.index(m);answer=result['answer'];self.counts[j,m,answer]+=1
        if self.last_forced:self.forced[j,m,answer]+=1
