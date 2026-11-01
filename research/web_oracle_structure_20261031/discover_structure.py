"""Bounded deterministic finite-grid relaxations, NOT continuous certificates."""
from pathlib import Path
import importlib.util
import json
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('previous_grid',ROOT.parent/'web_unknown_calibration_20261031/explore_calibration.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law,kl,bern=mod.law,mod.kl,mod.bern

def run():
    cap=6; eta=.025
    actions=[(a,L-a) for L in range(1,cap+1) for a in range(L+1)]
    pure=[i for i,(a,b) in enumerate(actions) if b==0]
    rows=[]
    for r in [.6,.8,.95]:
      for p,q in [(.65,.5),(.8,.6),(.95,.6),(.95,.9)]:
        vals=np.unique(np.r_[np.linspace(.5,1-eta,33),p,q])
        uv=np.array([(u,v) for u in vals for v in vals if v<=u])
        cal=bern(p,uv[:,0])+bern(q,uv[:,1])
        pos=[]; neg=[]
        for a,b in actions:
            P=law(r,p,q,a,b)
            pos.append(kl(P,law(r,uv[:,0],uv[:,1],a,b)))
            neg.append(kl(P,law(r,uv[:,0],uv[:,1],a,b,True)))
        pos=np.stack(pos,axis=1); neg=np.stack(neg,axis=1)
        for d in [1,2,4,8]:
          mat=neg+(d-1)*pos
          for alpha in [0,.1,1,10]:
            rhs=1-alpha*cal
            for c in [0,1,10,100]:
              costs=np.array([d*(c+a+b) for a,b in actions])
              full=linprog(costs,A_ub=-mat,b_ub=-rhs,bounds=(0,None),method='highs')
              purelp=linprog(costs[pure],A_ub=-mat[:,pure],b_ub=-rhs,bounds=(0,None),method='highs')
              assert full.success and purelp.success
              one=np.max(np.maximum(rhs,0)[:,None]/mat[:,pure],axis=0)*costs[pure]
              row=dict(r=r,p=p,q=q,d=d,alpha=alpha,c=c,eta=eta,cap=cap,
                       full_grid=float(full.fun),pure_grid=float(purelp.fun),single_grid=float(min(one)),
                       format_gain=float(purelp.fun/full.fun-1),depth_gain=float(min(one)/purelp.fun-1),
                       full_support=[dict(action=actions[i],x=float(x)) for i,x in enumerate(full.x) if x>1e-7],
                       pure_support=[dict(L=actions[i][0],x=float(x)) for i,x in zip(pure,purelp.x) if x>1e-7],
                       pure_dual=[dict(u=float(uv[i,0]),v=float(uv[i,1]),weight=float(-x)) for i,x in enumerate(purelp.ineqlin.marginals) if x< -1e-7])
              rows.append(row)
        print(json.dumps(dict(completed_r=r,p=p,q=q,cases=len(rows))),flush=True)
    out=dict(status='FINITE_GRID_DISCOVERY_ONLY',cases=len(rows),rows=rows)
    (ROOT/'DISCOVERY_GRID.json').write_text(json.dumps(out,indent=2)+'\n')
    summary={k:sorted(rows,key=lambda row:row[k],reverse=True)[:8] for k in ['format_gain','depth_gain']}
    (ROOT/'DISCOVERY_TOP.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':run()
