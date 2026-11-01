"""Theorem 1 joint KL coefficient: analytic inner fit + cutting-plane LP.

The mathematical semi-infinite program is exact; returned bounds are floating
numerical bounds, not interval-arithmetic certificates. G<=2, finite type KL.
"""
from dataclasses import dataclass,asdict
import itertools
import math
import warnings
import numpy as np
from scipy.optimize import linprog,brentq


def kl(r,x):
    r=np.asarray(r,dtype=float);x=np.asarray(x,dtype=float)
    if np.any((r<0)|(r>1)|(x<=0)|(x>=1)):raise ValueError('Invalid Bernoulli parameters')
    with np.errstate(divide='ignore',invalid='ignore'):
        a=np.where(r>0,r*np.log(r/x),0.)
        b=np.where(r<1,(1-r)*np.log((1-r)/(1-x)),0.)
    out=a+b
    return float(out) if out.ndim==0 else out


def fit_ordered(su,nu,sv,nv,eta=.05):
    """Maximize two weighted binomial log likelihoods on .5<=v<=u<=1-eta."""
    if min(nu,nv)<-1e-12 or not 0<eta<.5:raise ValueError('Invalid fit')
    u=min(1-eta,max(.5,su/nu)) if nu>0 else 1-eta
    v=min(1-eta,max(.5,sv/nv)) if nv>0 else .5
    if u<v:u=v=min(1-eta,max(.5,(su+sv)/(nu+nv)))
    return u,v


def alternatives(G):return [(mask,h) for mask in range(2**G) for h in range(G)]


def coefficients_at(partition,p,q,mask,h,u,v,kappa=None):
    G=len(partition);out=np.zeros(2*G+(G if kappa is not None else 0))
    for g,k in enumerate(partition):
        x,y=(v,u) if mask>>g&1 else (u,v)
        flipped=int(g==h)
        out[g]=(k-flipped)*kl(p,x)+flipped*kl(p,1-x)
        out[G+g]=(k-flipped)*kl(q,y)+flipped*kl(q,1-y)
    if kappa is not None:
        for g in range(G):out[2*G+g]=kappa[g]*int(bool(mask>>g&1))
    return out


def inner(partition,p,q,alpha,x,mask,h,kappa=None,eta=.05):
    G=len(partition);su,nu,sv,nv=alpha*p,alpha,alpha*q,alpha
    for g,k in enumerate(partition):
        a,b=x[g],x[G+g]
        # Complement one true mean rather than constraining a flipped channel.
        good_sum=(k*p+(1-2*p)*int(g==h))*a
        bad_sum=(k*q+(1-2*q)*int(g==h))*b
        if mask>>g&1:
            sv+=good_sum;nv+=k*a;su+=bad_sum;nu+=k*b
        else:
            su+=good_sum;nu+=k*a;sv+=bad_sum;nv+=k*b
    u,v=fit_ordered(su,nu,sv,nv,eta)
    gradient=coefficients_at(partition,p,q,mask,h,u,v,kappa)
    value=alpha*(kl(p,u)+kl(q,v))+float(gradient@x)
    return {'value':value,'u':u,'v':v,'gradient':gradient}


def oracle_coefficient(d,p,q,alpha,eta=.05):
    if not isinstance(d,int) or d<1 or not .5<=q<p<=1-eta or alpha<0:raise ValueError('Invalid oracle problem')
    def info(a):
        u,v=fit_ordered(alpha*p+a*(1+(d-2)*p),alpha+d*a,alpha*q,alpha,eta)
        value=alpha*(kl(p,u)+kl(q,v))+a*(kl(p,1-u)+(d-1)*kl(p,u))
        return value,u,v
    upper=1.
    while info(upper)[0]<1:upper*=2
    a=brentq(lambda a:info(a)[0]-1,0,upper,xtol=1e-13,rtol=1e-13)
    value,u,v=info(a)
    return {'K':d*a,'a':a,'u':u,'v':v,'information':value}


def gamma(d,k,p,q,alpha,eta=.05):
    a=oracle_coefficient(d,p,q,alpha,eta)['a']
    w=max(.5,(alpha*q+a*(1+(k-2)*p))/(alpha+k*a))
    return alpha*kl(q,w)+a*(kl(p,1-w)+(k-1)*kl(p,w))


def critical_alpha(d,k,p,q,eta=.05,upper=100.):
    f=lambda alpha:gamma(d,k,p,q,alpha,eta)-1
    if abs(f(0))<1e-11:return 0.
    if f(0)*f(upper)>0:return None
    return float(brentq(f,0,upper,xtol=1e-10))


def solve_allocation(partition,p,q,alpha,type_accuracy=None,eta=.05,tolerance=2e-7,max_iterations=120):
    partition=tuple(partition);G=len(partition)
    if not 1<=G<=2 or any(k<1 for k in partition) or not .5<=q<p<=1-eta or alpha<0:raise ValueError('Invalid allocation problem')
    if type_accuracy is not None:
        s=np.array([type_accuracy]*G if np.isscalar(type_accuracy) else type_accuracy,dtype=float)
        if len(s)!=G or np.any((s<=.5)|(s>=1)):raise ValueError('Finite known type accuracy required')
        kappa=np.array([kl(v,1-v) for v in s])
    else:kappa=None
    objective=np.array(list(partition)*2+([1]*G if kappa is not None else []),dtype=float)
    rows=[];rhs=[];seen=set();alts=alternatives(G)
    def add(mask,h,u,v):
        key=(mask,h,round(u,13),round(v,13))
        if key in seen:return False
        seen.add(key);rows.append(coefficients_at(partition,p,q,mask,h,u,v,kappa))
        rhs.append(1-alpha*(kl(p,u)+kl(q,v)));return True
    for mask,h in alts:
        for u,v in [(p,q),(.5,.5),(p,p),(1-eta,.5)]:add(mask,h,u,v)
    x=None;lower=None;history=[]
    for iteration in range(max_iterations):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected')
            lp=linprog(objective,A_ub=-np.asarray(rows),b_ub=-np.asarray(rhs),bounds=(0,None),method='highs',
                       options={'threads':1,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        if not lp.success:raise RuntimeError('Allocation LP failed: '+lp.message)
        x=np.maximum(lp.x,0);lower=float(lp.fun)
        fits=[inner(partition,p,q,alpha,x,mask,h,kappa,eta) for mask,h in alts]
        worst=min(f['value'] for f in fits)
        history.append({'iteration':iteration+1,'lower_bound':lower,'minimum_information':worst,'cuts':len(rows)})
        if worst>=1-tolerance:break
        added=sum(add(mask,h,f['u'],f['v']) for (mask,h),f in zip(alts,fits) if f['value']<1-tolerance)
        if added==0:raise RuntimeError('Cutting plane stalled before feasibility')
    else:raise RuntimeError('Allocation solver iteration cap')
    # Monotone radial repair supplies a separately evaluated numerical upper bound.
    def minimum(scale):return min(inner(partition,p,q,alpha,x*scale,m,h,kappa,eta)['value'] for m,h in alts)
    high=1.
    while minimum(high)<1+1e-9:high*=1.001
    low=1.
    for _ in range(35):
        mid=(low+high)/2
        if minimum(mid)>=1+1e-9:high=mid
        else:low=mid
    feasible=x*high;upper=float(objective@feasible)
    final=[inner(partition,p,q,alpha,feasible,m,h,kappa,eta)['value'] for m,h in alts]
    return {'partition':list(partition),'p':p,'q':q,'alpha':alpha,'type_accuracy':None if kappa is None else s.tolist(),
        'K':upper,'lower_bound':lower,'upper_bound':upper,'relative_gap':(upper-lower)/max(1.,upper),
        'a':feasible[:G].tolist(),'b':feasible[G:2*G].tolist(),
        'c':feasible[2*G:].tolist() if kappa is not None else [0.]*G,
        'minimum_information':min(final),'constraints':final,'iterations':len(history),'cuts':len(rows),
        'history':history,'scope':'Exact semi-infinite formulation; floating analytic separation and LP bounds, not interval certification.'}


def warmup_lp():
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unrecognized options detected')
        linprog([1.,1.],A_ub=[[-1.,-1.]],b_ub=[-1.],bounds=(0,None),method='highs',options={'threads':1})
