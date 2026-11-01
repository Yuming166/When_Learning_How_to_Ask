# Auxiliary discovery provenance

Date: 2026-10-31. This note reconstructs the independent oracle-audit agent's preliminary calculations from its still-visible tool-call source and returned outputs. **No calculation was rerun to prepare this note.** The original commands passed inline Python through shell stdin; they did not create script files or temporary result files. Their Python variables are no longer available after process exit. The sources below are recovered from the execution transcript, not from a newly executed reconstruction.

The main retained `DISCOVERY_GRID.json` scan and its reported 768 cases are separate. They are **not** the complete denominator of every exploratory computation performed during this research stage. The auxiliary loops below use different units, include repeated/overlapping parameter states, and must not be added to the 768 as though they formed a common experiment. None is an empirical benchmark or involves model responses.

## Inventory and known completeness

| ID | Purpose | Known planned scope | Execution record | Evidentiary use |
|---|---|---|---|---|
| A | Same-depth pure-good versus mixed comparison on the candidate profiled alternative curve | 864 base `(r,p,q,d,L)` settings; 21 u values each; 81,648 mixed-block comparisons, inferred from source loops | Completed, exit 0, final output `(0, None)`; no per-case records | Preliminary absence of a detected violation only; not a theorem or a complete oracle optimization |
| B | Pure-good depth-allocation LP discovery, alpha=0 | 1,000 LPs planned, 901 alternative-u grid points each, 12 depths | Interrupted with Ctrl-C while inside `scipy.optimize.linprog`; exit 130; actual completed LP count **unknown** | No final result used; no completed best-allocation output survived |
| C | Attack a proposed coordinatewise KL monotonicity lemma | 9,828 parameter states and 19,656 signed derivative comparisons, inferred from source loops | Completed, exit 0; one negative same-truth derivative reported | Generated a candidate subsequently superseded by the retained exact interval certificate |
| D | Inspect the two derivatives at the candidate from C | One parameter state, two derivatives | Completed, exit 0 | Preliminary arithmetic only; superseded by exact interval certificate |
| E | Inspect the pure-good opposite-truth KL near u=p | Four parameter settings, three u evaluations each | Completed, exit 0 | No theorem inferred; not used as evidence for global nuisance-rate monotonicity |
| F | Evaluate the proposed F_d derivative at three d values | Three arithmetic evaluations from D's floating values | Completed, exit 0 | Selected a simple d for subsequent exact certification |

The counts for A and C are mathematical counts of the executed, non-interrupted source loops. There were no per-case execution receipts, so this note does not present reconstructed observations for each comparison. Exact timestamps and a per-case failure/timing log were not recorded. The original source shown below is the available provenance.

### A. Completed same-depth comparison

Interpreter: `python` from the current shell. Its exact executable/version was not captured in this command. Tool output recorded wall time 2.738895225 seconds and exit code 0. The final printed value was:

```text
(0, None)
```

`worst` starts at zero and updates only for a positive floating-point gap. Thus the result means no positive gap was detected in these calculations; it is not a rigorous assertion that every real-valued gap is nonpositive.

There are nine valid `(p,q)` pairs after `q>=p` filtering. Hence the base count is `4*9*4*6=864`, and the mixed comparison count is `4*9*4*21*(2+3+4+5+6+7)=81648`. These comparisons do not solve the oracle allocation problem.

```python
import math,itertools

def law(r,a,b,na,nb,neg=False):
 w=1-r if neg else r
 return [math.comb(na,sa)*math.comb(nb,sb)*(w*a**sa*(1-a)**(na-sa)*b**sb*(1-b)**(nb-sb)+(1-w)*(1-a)**sa*a**(na-sa)*(1-b)**sb*b**(nb-sb)) for sa in range(na+1) for sb in range(nb+1)]
def kl(P,Q):return sum(p*math.log(p/q) for p,q in zip(P,Q))
worst=(0,None)
for r,p,q,d,L in itertools.product([.55,.65,.8,.95],[.6,.75,.9],[.5,.55,.7,.85],[1,2,4,8],range(2,8)):
 if q>=p:continue
 Pgood=law(r,p,q,L,0)
 for i in range(21):
  u=.5+(p-.5)*i/20;v=min(q,u)
  Fgood=kl(Pgood,law(r,u,v,L,0,True))+(d-1)*kl(Pgood,law(r,u,v,L,0))
  for nb in range(1,L+1):
   na=L-nb;P=law(r,p,q,na,nb)
   F=kl(P,law(r,u,v,na,nb,True))+(d-1)*kl(P,law(r,u,v,na,nb))
   gap=F-Fgood
   if gap>worst[0]:worst=(gap,(r,p,q,d,L,u,v,na,nb,Fgood,F))
print(worst)
```

### B. Interrupted pure-depth LP scan

Interpreter: `/storage/gaoym/wcl_v100_venv/bin/python`. A preceding environment check returned SciPy `1.18.1`. NumPy version and full environment metadata were not captured in this auxiliary command. It initially returned a running session after ten seconds, session ID `7135`. After the parent reported a stronger depth-mixture candidate and requested focus on proof, the agent sent Ctrl-C to its own running process. The command exited with code 130 and a `KeyboardInterrupt` traceback inside SciPy/HiGHS (`highs.run()`).

The only `print` in this program is after all loops. That print was never reached, and neither its in-memory `best` variable nor intermediate LP outputs were persisted. The actual number of LPs completed, their parameter locations, their solver statuses, and their candidate allocations are **unknown**. No claim about their values or signs is made. Planned count: `5*5*4*10=1000` LPs. Every LP was a finite-grid relaxation; no continuous-domain certificate would have followed from completion alone.

```python
import numpy as np
from scipy.special import gammaln,xlogy
from scipy.optimize import linprog
best=(0,None)
for r in [.55,.65,.8,.9,.95]:
 for p in [.6,.7,.8,.9,.95]:
  us=np.linspace(.5,.95,901)
  ds=[];same=[]
  for L in range(1,13):
   n=np.arange(L+1);co=np.exp(gammaln(L+1)-gammaln(n+1)-gammaln(L-n+1))
   P=co*(r*p**n*(1-p)**(L-n)+(1-r)*(1-p)**n*p**(L-n))
   f=co[None,:]*us[:,None]**n*(1-us[:,None])**(L-n)
   g=f[:,::-1]
   Qp=r*f+(1-r)*g;Qm=(1-r)*f+r*g
   ds.append(np.sum(xlogy(P[None,:],P[None,:]/Qm),axis=1));same.append(np.sum(xlogy(P[None,:],P[None,:]/Qp),axis=1))
  for d in [1,2,4,8]:
   mat=(np.array(ds)+(d-1)*np.array(same)).T
   for c in [0,.1,.5,1,2,5,10,20,50,100]:
    costs=c+np.arange(1,13)
    sol=linprog(costs,A_ub=-mat,b_ub=-np.ones(len(us)),bounds=(0,None),method='highs')
    singles=costs/mat.min(axis=0);gain=singles.min()/sol.fun-1
    if gain>best[0]:best=(gain,dict(r=r,p=p,d=d,c=c,cost=sol.fun,single=singles.min(),singledepth=int(singles.argmin()+1),allocation=[(i+1,float(x)) for i,x in enumerate(sol.x) if x>1e-8],activeu=[float(us[i]) for i in np.argsort(mat@sol.x)[:5]]))
print(best)
```

The retained termination trace ended as follows:

```text
  File ".../scipy/optimize/_linprog_highs.py", line 355, in _linprog_highs
    res = _highs_wrapper(...)
  File ".../scipy/optimize/_highspy/_highs_wrapper.py", line 206, in _highs_wrapper
    run_status = highs.run()
KeyboardInterrupt
```

### C. Completed coordinatewise derivative attack

Interpreter: shell `python`; exact version not captured. Recorded wall time 1.285418301 seconds, exit 0. Final output:

```text
minimum derivatives same and opposite [(-0.000502497969853348, (2, 0.95, [0.65, 0.825], (0.65, 0.65), False)), (0, None)]
```

The state count is `4*(3**2*3**1+3**3*3**2+3**4*3**3)=9828`; each state evaluates both signs. This attacked a general vector-accuracy lemma, so some scanned vectors have more than two distinct accuracies and are not individual actions of the original two-format model. The returned two-coordinate counterexample does fit the relevant two-level structure. The `1e-10` update tolerance is part of the exploratory code. The original tied alternative was subsequently perturbed to a strict admissible pair and certified in the retained `certify_monotonicity_obstruction.py`; that certificate is the proof artifact.

```python
import itertools,math

def law(r,aa,neg=False):
 w=1-r if neg else r
 out=[]
 for yy in itertools.product((0,1),repeat=len(aa)):
  f=math.prod(a if y else 1-a for a,y in zip(aa,yy));g=math.prod(1-a if y else a for a,y in zip(aa,yy));out.append(w*f+(1-w)*g)
 return out
mins=[(0,None),(0,None)]
for L in [2,3,4]:
 for r in [.51,.6,.8,.95]:
  for bb in itertools.product([.5,.65,.85],repeat=L):
   for flags in itertools.product((0,1,2),repeat=L-1):
    aa=[bb[0]]+[b if f==0 else (1+b)/2 if f==1 else .99 for b,f in zip(bb[1:],flags)]
    P=law(r,aa);P1=law(r,[1]+aa[1:]);P0=law(r,[0]+aa[1:]);der=[x-y for x,y in zip(P1,P0)]
    for neg in [False,True]:
     Q=law(r,bb,neg);val=sum(dp*math.log(p/q) for dp,p,q in zip(der,P,Q))
     if val<mins[int(neg)][0]-1e-10:mins[int(neg)]=(val,(L,r,aa,bb,neg))
print('minimum derivatives same and opposite',mins)
```

### D. Candidate derivative inspection

Completed, exit 0. The output was `False -0.000502497969853348` and `True 0.9772728160470087`.

```python
import itertools,math
r=.95;aa=[.65,.825];bb=[.65,.65]
def law(aa,neg=False):
 w=1-r if neg else r
 return [w*math.prod(a if y else 1-a for a,y in zip(aa,yy))+(1-w)*math.prod(1-a if y else a for a,y in zip(aa,yy)) for yy in itertools.product((0,1),repeat=2)]
P=law(aa);DP=[x-y for x,y in zip(law([1,aa[1]]),law([0,aa[1]]))]
for neg in [False,True]:
 Q=law(bb,neg);val=sum(dp*math.log(p/q) for dp,p,q in zip(DP,P,Q));print(neg,val)
```

### E. Local nuisance-rate inspection

Completed, exit 0. This was a local inspection, not a grid search establishing any global monotonicity or global minimizer.

```python
import math

def law(r,a,L,neg=False):
 w=1-r if neg else r
 return [math.comb(L,i)*(w*a**i*(1-a)**(L-i)+(1-w)*(1-a)**i*a**(L-i)) for i in range(L+1)]
def kl(P,Q):return sum(p*math.log(p/q) for p,q in zip(P,Q))
for r,p,L in [(.8,.8,5),(.6,.95,2),(.9,.6,6),(.8,.8,10)]:
 P=law(r,p,L)
 print(r,p,L,[(round(u,3),kl(P,law(r,u,L,True))) for u in [p-.01,p,p+.01]])
```

Recorded output:

```text
0.8 0.8 5 [(0.79, 0.6585761014697276), (0.8, 0.6626893768787976), (0.81, 0.669186515657788)]
0.6 0.95 2 [(0.94, 0.07403752655650894), (0.95, 0.07256945000157938), (0.96, 0.07490832377283595)]
0.9 0.6 6 [(0.59, 0.2622574459694346), (0.6, 0.28667925888889556), (0.61, 0.31164715653438335)]
0.8 0.8 10 [(0.79, 0.7882345993475013), (0.8, 0.7869910236269658), (0.81, 0.7916885630106567)]
```

### F. Arithmetic choice of d for a later certificate

Completed, exit 0. This used rounded outputs from D and was superseded by the exact certificate.

```python
a=-.000502497969853348;b=.9772728160470087
for d in [1946,2000,4096]:print(d,b+(d-1)*a)
```

Recorded output:

```text
1946 -8.573531775313281e-05
2000 -0.027220625689834077
4096 -1.0804563705024512
```

## Completed parent depth certificate and review scope

The parent's depth proof is now completed, with `DEPTH_MIXING_CERTIFICATE.json` reporting `PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE`. It gives a continuously feasible mixed-depth witness costing 34 and a lower bound of 41.3 for every allocation confined to one depth, including arbitrary format mixtures at that depth. The certificate and the separate `DEPTH_STRUCTURE_AUDIT.md` retain their own validation scope.

For this provenance update, this independent oracle-audit agent read the completed JSON status and bounds. It **did not rerun the depth certificate or independently audit its full construction in this provenance task**. The completed-status update should not be interpreted as an additional independent execution. The old statement that the parent was still certifying the result is superseded by this artifact reference.
