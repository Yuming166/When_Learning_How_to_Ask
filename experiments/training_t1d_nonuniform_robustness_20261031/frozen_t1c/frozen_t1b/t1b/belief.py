"""Finite quadrature belief and exact-in-that-belief predictive moments.

Continuous reliability integration is the frozen order-32 approximation, not
exact Bayesian integration. Enumerated theta/z are hypotheses, never truth.
"""
from functools import lru_cache
import numpy as np
from scipy.special import rel_entr
from . import bootstrap
from phase2e.estimator import posterior,design

@lru_cache(maxsize=16)
def kernel(d,groups,accuracy,eta,order):
    theta,jt,jz,good,rates,logw=design(d,groups,eta,order)
    G=len(groups);nz=2**G;nt=len(theta);nr=rates.shape[1]
    membership={j:g for g,mm in enumerate(groups) for j in mm};mu=[]
    for j in range(d):
        for m in range(2):
            rr=np.where((jz[:,membership[j]]==m)[:,None],rates[0],rates[1])
            mu.append(np.where(jt[:,j,None]==1,rr,1-rr))
    for g,s in enumerate(accuracy):
        mu.append(np.broadcast_to(np.where(jz[:,g,None]==1,s,1-s),(len(jt),nr)))
    return {'mu':np.asarray(mu).reshape(2*d+G,nt,nz*nr),
            'theta':theta,'z':jz[:nz], 'p':np.tile(rates[0],nz),'q':np.tile(rates[1],nz),
            'nr':nr,'nz':nz,'d':d,'G':G}

class Belief:
    def __init__(self,fit,groups,accuracy,eta):
        d=len(fit['theta']);self.k=kernel(d,tuple(map(tuple,groups)),tuple(accuracy),float(eta),fit['quadrature_order'])
        self.w=np.exp(fit['_logjoint']).reshape(len(self.k['theta']),-1)
        self._first=None;self._second=None;self._summary=None
    @classmethod
    def from_observation(cls,counts,groups,cal,reports,accuracy,eta,order=32):
        return cls(posterior(counts,groups,cal,reports,accuracy,eta,order),groups,accuracy,eta)
    @property
    def theta_mass(self):return self.w.sum(axis=1)
    def first(self):
        if self._first is None:self._first=np.einsum('tn,atn->ta',self.w,self.k['mu'],optimize=True)
        return self._first
    def second(self):
        if self._second is None:
            # Weighted Gram matrix, one per theta. Future responses are fresh
            # conditionally independent given the same latent hypothesis.
            mu=self.k['mu'];self._second=np.stack([(mu[:,t,:]*self.w[t])@mu[:,t,:].T for t in range(len(self.w))])
        return self._second
    def condition(self,action,outcome):
        child=object.__new__(Belief);child.k=self.k;like=self.k['mu'][action]
        child.w=self.w*(like if outcome else 1-like);prob=float(child.w.sum());child.w/=prob
        child._first=child._second=child._summary=None
        return prob,child
    def summary(self):
        if self._summary is None:
            mass=self.theta_mass;z_mass=self.w.reshape(len(mass),self.k['nz'],self.k['nr']).sum(axis=(0,2))
            rates_mass=self.w.sum(axis=0);tp=mass@self.k['theta'];zp=z_mass@self.k['z']
            self._summary={'p':float(rates_mass@self.k['p']),'q':float(rates_mass@self.k['q']),
             'theta_prob':tp.tolist(),'z_prob':zp.tolist(),'z':(zp>.5).astype(int).tolist(),
             'theta':(tp>.5).astype(int).tolist(),'joint_theta_MAP':self.k['theta'][int(np.argmax(mass))].tolist(),
             'joint_MAP_probability':float(max(mass))}
        return self._summary
    def ig(self):
        f=self.first();mass=self.theta_mass[:,None];py=f.sum(axis=0)[None,:]
        info=(rel_entr(np.maximum(f,0),mass*py)+rel_entr(np.maximum(mass-f,0),mass*(1-py))).sum(axis=0)
        return np.maximum(info,0)
    def recovery(self):
        f=self.first();mass=self.theta_mass[:,None]
        return np.max(f,axis=0)+np.max(mass-f,axis=0)
    def entropy(self):
        m=self.theta_mass;return float(-np.sum(np.where(m>0,m*np.log(np.maximum(m,1e-300)),0)))

def index(action,d):return 2*action[1]+'AB'.index(action[2]) if action[0]=='query' else 2*d+action[1]
def action(i,d):return ('query',i//2,'AB'[i%2]) if i<2*d else ('type',i-2*d)
def stable_argmax(values,tolerance=1e-12):
    a=np.asarray(values);return int(np.flatnonzero(a>=max(a)-tolerance)[0])
