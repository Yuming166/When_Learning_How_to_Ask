"""Bounded deterministic grid relaxations; NOT certified continuous optima."""
from pathlib import Path
import json
import numpy as np
from math import comb
from scipy.optimize import linprog, minimize_scalar

ROOT=Path(__file__).resolve().parent


def law(r,a,b,na,nb,negative=False):
    a,b=np.broadcast_arrays(np.asarray(a),np.asarray(b))
    out=[]
    wr=1-r if negative else r
    for sa in range(na+1):
        for sb in range(nb+1):
            plus=a**sa*(1-a)**(na-sa)*b**sb*(1-b)**(nb-sb)
            minus=(1-a)**sa*a**(na-sa)*(1-b)**sb*b**(nb-sb)
            out.append(comb(na,sa)*comb(nb,sb)*(wr*plus+(1-wr)*minus))
    return np.stack(out,axis=-1)


def kl(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return np.sum(a*np.log(a/b),axis=-1)


def bern(a,b): return a*np.log(a/b)+(1-a)*np.log((1-a)/(1-b))


def run(r=.8,p=.8,q=.6,eta=.05,cap=5,c=10,step=.01):
    vals=np.linspace(.5,1-eta,round((.5-eta)/step)+1)
    uv=np.array([(u,v) for u in vals for v in vals if v<=u+1e-12])
    uv=np.concatenate([uv,[[p,q]]])
    actions=[(na,L-na) for L in range(1,cap+1) for na in range(L+1)]
    costs=np.array([c+na+nb for na,nb in actions])
    matrices=[]
    for swapped in [False,True]:
        a,b=(uv[:,1],uv[:,0]) if swapped else (uv[:,0],uv[:,1])
        matrices.append(np.stack([kl(law(r,p,q,na,nb),law(r,a,b,na,nb,True)) for na,nb in actions],axis=-1))
    cal=bern(p,uv[:,0])+bern(q,uv[:,1])
    rows=[]
    for alpha in [0,.1,1,5,20,100]:
        oracle=linprog(costs,A_ub=-matrices[0],b_ub=alpha*cal-1,bounds=(0,None),method='highs')
        unknown=linprog(costs,A_ub=-np.concatenate(matrices),b_ub=np.tile(alpha*cal-1,2),bounds=(0,None),method='highs')
        assert oracle.success and unknown.success
        support=[]
        lam=-unknown.ineqlin.marginals
        for idx in np.flatnonzero(lam>1e-9):
            s,k=divmod(int(idx),len(uv))
            support.append(dict(swapped=bool(s),u=float(uv[k,0]),v=float(uv[k,1]),weight=float(lam[idx])))
        pure=[]
        for length in range(1,cap+1):
            def ratio(u):
                penalty=alpha*(bern(p,u)+bern(q,min(q,u)))
                div=kl(law(r,p,q,length,0),law(r,u,u,length,0,True))
                return max(0,1-penalty)/div
            xs=np.linspace(.5,1-eta,2001)
            ys=np.array([ratio(u) for u in xs])
            candidates=[(ys[0],xs[0]),(ys[-1],xs[-1])]
            for i in range(1,len(xs)-1):
                if ys[i]>=ys[i-1] and ys[i]>=ys[i+1] and ys[i]>0:
                    opt=minimize_scalar(lambda u:-ratio(u),bounds=(xs[i-1],xs[i+1]),method='bounded',
                                        options={'xatol':1e-14})
                    candidates.append((-opt.fun,float(opt.x)))
            amount,u=max(candidates)
            pure.append(dict(L=length,cost=(c+length)*amount,x=amount,u=u))
        rows.append(dict(alpha=alpha,oracle_grid_relaxation=float(oracle.fun),
                         unknown_grid_relaxation=float(unknown.fun),
                         oracle_allocation=[dict(n_A=na,n_B=nb,x=float(x)) for (na,nb),x in zip(actions,oracle.x) if x>1e-8],
                         unknown_allocation=[dict(n_A=na,n_B=nb,x=float(x)) for (na,nb),x in zip(actions,unknown.x) if x>1e-8],
                         unknown_dual_support=support,
                         best_pure_oracle_heuristic=min(pure,key=lambda z:z['cost'])))
    result=dict(status='DETERMINISTIC_GRID_RELAXATION_AND_UNCERTIFIED_1D_HEURISTIC',
                claim_limit='Grid LP gives a relaxation; no continuous-optimality or nonzero-gap certificate follows without extra bounds.',
                parameters=dict(r=r,p=p,q=q,eta=eta,L_max=cap,c=c,ell=1,grid_step=step),
                grid_points=len(uv),actions=actions,rows=rows)
    (ROOT/'GRID_DIAGNOSTIC.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': run()
