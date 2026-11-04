"""Exact finite-prior certificates; no API calls and no experiment-runner changes."""
from fractions import Fraction as F
from itertools import product
from math import log
import json
from pathlib import Path

def prior(a,b):
    out=[]
    for t1,t2,z,k in product((-1,1),(-1,1),(0,1),(0,1)):
        p,q=[(F(9,10),F(3,5)),(F(22,25),F(31,50))][k]
        mass=(a if t1==1 else 1-a)*(b if t2==1 else 1-b)/4
        out.append(((t1,t2,z,p,q),mass))
    return out

def branch(pr,e,y):
    j,m=e
    out=[]
    for state,w in pr:
        r=state[3] if state[2]==m else state[4]
        out.append((state,w*(r if y==state[j] else 1-r)))
    mass=sum(w for _,w in out)
    return mass,[(s,w/mass) for s,w in out]

def value(pr):
    return max(sum(w for s,w in pr if s[0]==t) for t in (-1,1))

def dv(pr,e):
    return sum(mass*value(post) for mass,post in (branch(pr,e,y) for y in (-1,1)))-value(pr)

def entropy(x):
    x=float(x)
    return -x*log(x)-(1-x)*log(1-x)

def ig(pr,e):
    pred,_=branch(pr,e,1)
    return entropy(pred)-sum(float(w)*entropy(s[3] if s[2]==e[1] else s[4]) for s,w in pr)

pr=prior(F(77,100),F(99,100))
actions=list(product((0,1),(0,1)))
assert all(dv(pr,e)==0 for e in actions)
final=F(0)
branches=[]
for y in (-1,1):
    mass,post=branch(pr,(1,0),y)
    e=(0,0 if y==1 else 1)
    continuation=sum(m*value(b) for m,b in (branch(post,e,r) for r in (-1,1)))
    final+=mass*continuation
    branches.append({'reply':y,'probability':str(mass),'next_action':e,'success':str(continuation),'dv_next':str(dv(post,e))})
assert final>value(pr)
minimum_margin=min(mass*(sum(w for s,w in post if s[0]==1)-sum(w for s,w in post if s[0]==-1)) for e in actions for mass,post in (branch(pr,e,y) for y in (-1,1)))
assert minimum_margin==F(1,50)
fixed_policy_success=F(0)
for y in (-1,1):
    mass,post=branch(pr,(1,0),y)
    e=(0,0 if y==1 else 1)
    for r in (-1,1):
        m,last=branch(post,e,r)
        chosen_success=sum(w for s,w in last if s[0]==r)
        assert chosen_success==value(last)
        fixed_policy_success+=mass*m*chosen_success
assert fixed_policy_success==final
assert final-value(pr)-7*F(1,1000)==F(2903,250000)
rev=prior(F(7,10),F(1,2))
assert dv(rev,(0,0))==F(1,20) and dv(rev,(1,0))==0
assert ig(rev,(1,0))>ig(rev,(0,0))
report={'scope':'arbitrary admissible full-sign-support belief; no reachability-from-uniform claim',
'myopia':{'prior_success':str(value(pr)),'all_one_step_dv':[str(dv(pr,e)) for e in actions], 'two_step_success':str(final),'two_step_gain':str(final-value(pr)),'branches':branches,'minimum_one_step_unnormalized_winner_margin':str(minimum_margin),'open_neighborhood_radius':'1/1000','open_neighborhood_gain_lower_bound':'2903/250000'},
'reversal':{'target_dv':str(dv(rev,(0,0))),'auxiliary_dv':str(dv(rev,(1,0))),'target_joint_ig_nats':ig(rev,(0,0)),'auxiliary_joint_ig_nats':ig(rev,(1,0)), 'ig_difference_exact':'log(2)-h(3/5)>0'}}
p=Path(__file__).with_name('EXACT_CERTIFICATES.json')
p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
