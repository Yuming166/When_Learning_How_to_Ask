"""Additive numerical solvers. No hidden world fields or stopping decisions.

All bounds here are floating numerical diagnostics, not arithmetic certificates.
"""
import copy
import itertools
import math
import time
import warnings
from collections import Counter
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import Delaunay
from . import bootstrap
from phase2a import coefficients as old

VERSION='t1a-v1'
PAD=1e-9

def scalar_kl(p,u):
    return p*math.log(p/u)+(1-p)*math.log((1-p)/(1-u))

def bkl(p,u):
    return p*np.log(p/u)+(1-p)*np.log((1-p)/(1-u))

class Model:
    def __init__(self,partition,p,q,alpha,type_accuracy,eta):
        self.k=np.asarray(partition,dtype=float);self.G=len(partition)
        self.p=float(p);self.q=float(q);self.alpha=float(alpha);self.eta=float(eta)
        if not 1<=self.G<=2 or np.any(self.k<1) or not .5<=q<p<=1-eta or alpha<0:
            raise ValueError('Invalid observable allocation parameters')
        self.s=None if type_accuracy is None else np.broadcast_to(type_accuracy,(self.G,)).astype(float).copy()
        if self.s is not None and np.any((self.s<=.5)|(self.s>=1)):raise ValueError('Invalid known type accuracy')
        self.kappa=None if self.s is None else bkl(self.s,1-self.s)
        self.alts=old.alternatives(self.G)
        self.swap=np.asarray([[bool(m>>g&1) for g in range(self.G)] for m,h in self.alts])
        self.flip=np.asarray([[int(g==h) for g in range(self.G)] for m,h in self.alts])
        self.cost=np.r_[self.k,self.k,np.ones(self.G) if self.s is not None else []]
    def rows(self,u,v,indices=None):
        ids=np.arange(len(self.alts)) if indices is None else np.asarray(indices)
        u=np.broadcast_to(u,(len(ids),));v=np.broadcast_to(v,(len(ids),))
        swap=self.swap[ids];flip=self.flip[ids]
        hi=np.where(swap,v[:,None],u[:,None]);lo=np.where(swap,u[:,None],v[:,None])
        a=(self.k-flip)*bkl(self.p,hi)+flip*bkl(self.p,1-hi)
        b=(self.k-flip)*bkl(self.q,lo)+flip*bkl(self.q,1-lo)
        row=np.c_[a,b] if self.kappa is None else np.c_[a,b,swap*self.kappa]
        rhs=1-self.alpha*(bkl(self.p,u)+bkl(self.q,v))
        return row,rhs
    def prepare(self,x):
        gsum=(self.k*self.p+(1-2*self.p)*self.flip)*x[:self.G]
        bsum=(self.k*self.q+(1-2*self.q)*self.flip)*x[self.G:2*self.G]
        gn=self.k*x[:self.G];bn=self.k*x[self.G:2*self.G]
        return (np.where(self.swap,bsum,gsum).sum(1),np.where(self.swap,bn,gn).sum(1),
                np.where(self.swap,gsum,bsum).sum(1),np.where(self.swap,gn,bn).sum(1))
    def fits_prepared(self,x,stats,scale=1.,gradient=True):
        su,nu,sv,nv=[r*scale for r in stats]
        su=su+self.alpha*self.p;nu=nu+self.alpha;sv=sv+self.alpha*self.q;nv=nv+self.alpha
        u=np.divide(su,nu,out=np.full_like(su,1-self.eta),where=nu>0)
        v=np.divide(sv,nv,out=np.full_like(sv,.5),where=nv>0)
        u=np.clip(u,.5,1-self.eta);v=np.clip(v,.5,1-self.eta)
        pooled=np.clip(np.divide(su+sv,nu+nv,out=np.full_like(su,.5),where=nu+nv>0),.5,1-self.eta)
        violate=u<v;u=np.where(violate,pooled,u);v=np.where(violate,pooled,v)
        rows,rhs=self.rows(u,v)
        values=(1-rhs)+rows@(x*scale)
        return values,u,v,rows
    def fits(self,x):return self.fits_prepared(x,self.prepare(x))
    def repair(self,x):
        stats=self.prepare(x);first=float(min(self.fits_prepared(x,stats)[0]));calls=1
        if not math.isfinite(first) or first<=0:raise FloatingPointError('Zero/nonfinite radial information')
        if self.alpha==0:
            # No calibration term: the minimized information is homogeneous.
            high=max(1.,(1+PAD)/first)*(1+2e-14)
        else:
            low=high=1.
            while float(min(self.fits_prepared(x,stats,high)[0]))<1+PAD:
                high*=1.001;calls+=1
                if calls>10000:raise RuntimeError('Radial bracket cap')
            for _ in range(35):
                mid=(low+high)/2;calls+=1
                if float(min(self.fits_prepared(x,stats,mid)[0]))>=1+PAD:high=mid
                else:low=mid
        x=x*high;values=self.fits(x)[0]
        if min(values)<1-1e-8:raise FloatingPointError('Radial feasibility residual')
        return x,values,calls
    def initial(self):
        n=len(self.alts);u=np.repeat([self.p,.5,self.p,1-self.eta],n);v=np.repeat([self.q,.5,self.p,.5],n)
        ids=np.tile(np.arange(n),4);rows,rhs=self.rows(u,v,ids)
        cuts=[(int(i),float(a),float(b)) for i,a,b in zip(ids,u,v)]
        return list(rows),list(rhs),cuts

def lp_solve(cost,rows,rhs):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unrecognized options detected')
        lp=linprog(cost,A_ub=-np.asarray(rows),b_ub=-np.asarray(rhs),bounds=(0,None),method='highs',
          options={'threads':1,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    if not lp.success:raise RuntimeError('LP failed: '+lp.message)
    return lp

def package(m,x,lower,values,iterations,cuts,history,**extra):
    K=float(m.cost@x)
    return {'partition':m.k.astype(int).tolist(),'p':m.p,'q':m.q,'alpha':m.alpha,
      'type_accuracy':None if m.s is None else m.s.tolist(), 'K':K,'lower_bound':float(lower),'upper_bound':K,
      'relative_gap':(K-lower)/max(1.,K),'a':x[:m.G].tolist(),'b':x[m.G:2*m.G].tolist(),
      'c':x[2*m.G:].tolist() if m.s is not None else [0.]*m.G,
      'minimum_information':float(min(values)),'constraints':values.tolist(),
      'iterations':iterations,'cuts':cuts,'history':history,'scope':'floating diagnostics; not interval certified',**extra}

def x_of(fit,available=True):return np.asarray(fit['a']+fit['b']+(fit['c'] if available else []))

def optimized(partition,p,q,alpha,type_accuracy=None,eta=.05,tolerance=2e-7,max_iterations=120,analytic=True,seeds=()):
    m=Model(partition,p,q,alpha,type_accuracy,eta)
    rows,rhs,cuts=m.initial();seen={(i,round(u,13),round(v,13)) for i,u,v in cuts}
    def add(i,u,v):
        key=(int(i),round(float(u),13),round(float(v),13))
        if key in seen:return False
        seen.add(key)
        if analytic:r,b=m.rows([u],[v],[i]);row=r[0];bound=b[0]
        else:
            mask,h=m.alts[i];row=old.coefficients_at(partition,p,q,mask,h,u,v,m.kappa);bound=1-alpha*(old.kl(p,u)+old.kl(q,v))
        rows.append(row);rhs.append(bound);cuts.append((int(i),float(u),float(v)));return True
    if not analytic:
        rows=[];rhs=[];cuts=[];seen=set()
        for i in range(len(m.alts)):
            for u,v in [(p,q),(.5,.5),(p,p),(1-eta,.5)]:add(i,u,v)
    for i,u,v in seeds:add(i,u,v)
    history=[];latest=[]
    for iteration in range(max_iterations):
        lp=lp_solve(m.cost,rows,rhs);x=np.maximum(lp.x,0);lower=float(lp.fun)
        if analytic:values,u,v,grads=m.fits(x)
        else:
            fs=[old.inner(partition,p,q,alpha,x,mask,h,m.kappa,eta) for mask,h in m.alts]
            values=np.array([f['value'] for f in fs]);u=np.array([f['u'] for f in fs]);v=np.array([f['v'] for f in fs])
        worst=float(min(values));history.append({'iteration':iteration+1,'lower_bound':lower,'minimum_information':worst,'cuts':len(rows)})
        latest.append([(i,float(a),float(b)) for i,(a,b) in enumerate(zip(u,v))]);latest=latest[-2:]
        if worst>=1-tolerance:break
        if not sum(add(i,u[i],v[i]) for i in range(len(m.alts)) if values[i]<1-tolerance):raise RuntimeError('Cutting plane stalled')
    else:raise RuntimeError('Solver iteration cap')
    x,values,calls=m.repair(x)
    return package(m,x,lower,values,len(history),len(rows),history,radial_calls=calls,
                   support=[c for group in latest for c in group])

def canonical(partition,p,q,alpha,type_accuracy,eta,tolerance,max_iterations,quantized=False):
    # Whitelist of the allocation problem. Counts, identity, truth and seeds absent.
    rates=(round(p/.025),round(q/.025)) if quantized else (float(p).hex(),float(q).hex())
    accuracy=None if type_accuracy is None else tuple(np.broadcast_to(type_accuracy,(len(partition),)).astype(float).tolist())
    return (VERSION,tuple(partition),rates,float(alpha).hex(),accuracy,float(eta).hex(),float(tolerance).hex(),max_iterations)

class Solver:
    def __init__(self,mode,grid=None):
        self.mode=mode;self.cache={};self.support={};self.grid=grid or {};self.stats=Counter();self.cpu=Counter()
    def __call__(self,partition,p,q,alpha,type_accuracy=None,eta=.05,tolerance=2e-7,max_iterations=120):
        args=(partition,p,q,alpha,type_accuracy,eta,tolerance,max_iterations)
        started=time.process_time();self.stats['calls']+=1
        try:
            if self.mode=='Teacher':return old.solve_allocation(*args)
            if self.mode in ('RadialReuse','AnalyticReuse','WarmStart'):
                structure=(tuple(partition),alpha,tuple(type_accuracy) if type_accuracy is not None else None,eta)
                seeds=self.support.get(structure,()) if self.mode=='WarmStart' else ()
                fit=optimized(*args,analytic=self.mode!='RadialReuse',seeds=seeds)
                if seeds:self.stats['warm_calls']+=1
                self.support[structure]=fit['support'];return fit
            key=canonical(*args,quantized=self.mode=='QuantizedCache')
            if self.mode=='ExactCache':
                if key in self.cache:self.stats['hits']+=1;return copy.deepcopy(self.cache[key])
                fit=old.solve_allocation(*args);self.cache[key]=copy.deepcopy(fit);return fit
            m=Model(*args[:6]);candidate=None
            if self.mode=='QuantizedCache' and key in self.cache:
                self.stats['hits']+=1;candidate=x_of(self.cache[key],type_accuracy is not None)
            if self.mode=='Interpolation':
                gridkey=grid_key(partition,alpha,type_accuracy,eta)
                grid=self.grid.get(gridkey)
                if grid is not None:
                    point=np.array([p,q]);tri=grid['tri'];simplex=int(tri.find_simplex(point))
                    if simplex>=0:
                        transform=tri.transform[simplex];bary=transform[:2]@(point-transform[2]);weights=np.r_[bary,1-bary.sum()]
                        candidate=weights@grid['xs'][tri.simplices[simplex]];self.stats['hits']+=1
            if candidate is not None:
                checked=time.process_time()
                try:
                    candidate=np.maximum(candidate,0);candidate,values,radial=m.repair(candidate)
                    rows,rhs,_=m.initial();_,u,v,grads=m.fits(candidate);r,b=m.rows(u,v);rows.extend(r);rhs.extend(b)
                    lower=float(lp_solve(m.cost,rows,rhs).fun)
                    fit=package(m,candidate,lower,values,0,len(rows),[],radial_calls=radial)
                    gap=fit['relative_gap']
                    # Same tolerance budget as the teacher caller; full continuous separation.
                    if -5e-8<=gap<=max(5*tolerance,5e-8) and min(values)>=1-1e-7:
                        self.stats['accepted']+=1;return fit
                    self.stats['guard_reject']+=1
                except (FloatingPointError,RuntimeError):self.stats['guard_error']+=1
                finally:self.cpu['guard']+=time.process_time()-checked
            self.stats['fallback']+=1
            fallback=time.process_time();fit=old.solve_allocation(*args);self.cpu['fallback']+=time.process_time()-fallback
            if self.mode=='QuantizedCache':self.cache[key]=copy.deepcopy(fit)
            return fit
        finally:self.cpu['total']+=time.process_time()-started

def grid_key(partition,alpha,type_accuracy,eta):
    return (tuple(partition),float(alpha),None if type_accuracy is None else tuple(type_accuracy),float(eta))

def load_grid(raw):
    out={}
    for group in raw:
        key=grid_key(group['partition'],group['alpha'],group['type_accuracy'],group['eta'])
        points=np.array(group['points']);out[key]={'tri':Delaunay(points),'xs':np.array(group['xs'])}
    return out
