"""Numerical joint posterior quadrature and explicitly conditional plug-in.

Enumerates signs/types; continuous integration is approximate Gauss-Legendre.
The action policy is conditioned on the observed adaptive transcript, whose
predictable action factors cancel from likelihood ratios and the posterior.
"""
from functools import lru_cache
from itertools import product
import numpy as np
from scipy.special import logsumexp
from scipy.special import rel_entr
from . import bootstrap
from phase2a.glr import _binomial_mle

@lru_cache(maxsize=32)
def design(d,groups,eta,order):
    G=len(groups)
    theta=np.asarray(list(product([0,1],repeat=d)),dtype=int)
    z=np.asarray(list(product([0,1],repeat=G)),dtype=int)
    joint_theta=np.repeat(theta,len(z),axis=0)
    joint_z=np.tile(z,(len(theta),1))
    membership=np.zeros(d,dtype=int)
    for g,mm in enumerate(groups):membership[list(mm)]=g
    good=joint_z[:,membership,None]==np.arange(2)[None,None,:]
    x,w=np.polynomial.legendre.leggauss(order);u=(x+1)/2;w=w/2
    uu,vv=np.meshgrid(u,u,indexing='ij')
    rates=np.array([.5+(.5-eta)*uu,.5+(.5-eta)*uu*vv]).reshape(2,-1)
    logw=np.log((2*uu*w[:,None]*w[None,:]).ravel())
    return theta,joint_theta,joint_z,good,rates,logw

def sufficient(counts,groups,cal,reports,accuracy,eta,order):
    data=np.asarray(counts,dtype=np.int64)
    theta,jt,jz,good,rates,logw=design(len(data),tuple(map(tuple,groups)),float(eta),order)
    n=data.sum(axis=2)
    successes=np.where(jt[:,:,None]==1,data[None,:,:,1],data[None,:,:,0])
    hs=(successes*good).sum(axis=(1,2))+sum(cal['high'])
    hn=(n[None,:,:]*good).sum(axis=(1,2))+len(cal['high'])
    ls=successes.sum(axis=(1,2))-(hs-sum(cal['high']))+sum(cal['low'])
    ln=n.sum()+2*len(cal['high'])-hn
    typ=np.zeros(len(jt))
    for g,rr in enumerate(reports):
        if rr:
            s=float(accuracy[g]);matches=(np.asarray(rr)[None,:]==jz[:,g,None]).sum(axis=1)
            typ+=matches*np.log(s)+(len(rr)-matches)*np.log1p(-s)
    return theta,jt,jz,good,rates,logw,hs,hn,ls,ln,typ

def posterior(counts,groups,cal,reports,accuracy,eta=.05,order=32,plugin=False):
    theta,jt,jz,good,rates,logw,hs,hn,ls,ln,typ=sufficient(counts,groups,cal,reports,accuracy,eta,order)
    if plugin:
        pp,qq,ll=_binomial_mle(hs,hn,ls,ln,eta)
        best=int(np.argmax(ll+typ));rates=np.array([[pp[best]],[qq[best]]]);logw=np.zeros(1)
    lp,lq=np.log(rates);lfp,lfq=np.log1p(-rates)
    logjoint=hs[:,None]*lp+(hn-hs)[:,None]*lfp+ls[:,None]*lq+(ln-ls)[:,None]*lfq+typ[:,None]+logw
    logjoint-=logsumexp(logjoint)
    w=np.exp(logjoint);state=w.sum(axis=1)
    p,q=(w.sum(axis=0)@rates.T).tolist()
    theta_prob=state@jt;z_prob=state@jz
    return {'theta':(theta_prob>.5).astype(int).tolist(),'z':(z_prob>.5).astype(int).tolist(),
            'theta_prob':theta_prob.tolist(),'z_prob':z_prob.tolist(),'p':float(p),'q':float(q),
            'raw_p':float(p),'raw_q':float(q),'estimator_inputs':'all_tasks_all_type_reports_labelled_calibration_known_groups',
            'inference':'conditional_empirical_Bayes_plugin_not_joint_rate_posterior' if plugin else 'Gauss_Legendre_joint_posterior_approximation',
            'quadrature_order':0 if plugin else order,
            '_logjoint':logjoint,'_theta':theta,'_jt':jt,'_jz':jz,'_good':good,'_rates':rates}

def public_estimate(fit):return {k:v for k,v in fit.items() if not k.startswith('_')}

def information_scores(fit,groups,accuracy,allow_type=True):
    """Log I(theta; next_response | transcript); binary outcomes, unit costs.

    Uses KL form rather than an entropy subtraction; rare wrong-answer states
    retain their log probabilities after the modal sign probability rounds to 1.
    Finite precision may still lose very small dependencies; not certified.
    """
    lj=fit['_logjoint'];jt,jz=fit['_jt'],fit['_jz'];rates=fit['_rates']
    ntheta=len(fit['_theta']);G=len(groups);nz=2**G;d=jt.shape[1]
    ltheta=logsumexp(lj.reshape(ntheta,nz,-1),axis=(1,2))
    membership={j:g for g,mm in enumerate(groups) for j in mm}
    scores=[]
    for a in range(2*d+(G if allow_type else 0)):
        if a<2*d:
            j,m=divmod(a,2);rr=np.where((jz[:,membership[j]]==m)[:,None],rates[0],rates[1])
            mu=np.where(jt[:,j,None]==1,rr,1-rr)
        else:
            g=a-2*d;mu=np.broadcast_to(np.where(jz[:,g,None]==1,accuracy[g],1-accuracy[g]),lj.shape)
        lnum=logsumexp((lj+np.log(mu)).reshape(ntheta,nz,-1),axis=(1,2))
        cond=np.clip(np.exp(lnum-ltheta),1e-15,1-1e-15)
        mean=float(np.clip(np.exp(logsumexp(lnum)),1e-15,1-1e-15))
        # Pairwise differences keep the modal-state deviation proportional to
        # rare-state mass, instead of creating an O(eps^2) information floor.
        delta=((cond[:,None]-cond[None,:])*np.exp(ltheta)[None,:]).sum(axis=1)
        small=np.abs(delta)<1e-3*min(mean,1-mean)
        kval=np.zeros_like(delta)
        for n in range(2,7):
            kval[small]+=delta[small]**n/(n*(n-1))*((-1)**n/mean**(n-1)+1/(1-mean)**(n-1))
        xx=np.clip(mean+delta[~small],1e-15,1-1e-15)
        kval[~small]=rel_entr(xx,mean)+rel_entr(1-xx,1-mean)
        kval=np.maximum(0,kval)
        with np.errstate(divide='ignore'):score=float(logsumexp(ltheta+np.log(kval)))
        scores.append(score)
    return np.asarray(scores)
