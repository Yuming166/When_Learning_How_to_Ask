"""Exact-rational posterior + Decimal entropy versus numerical KL information.

Same-context engineering cross-check, not an independent review or new worlds.
"""
from fractions import Fraction as F
from itertools import product
from decimal import Decimal,localcontext
from pathlib import Path
import json,math,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase2e.exact import integral
from phase2e.estimator import posterior,information_scores

def exact_mass(c,groups,cal,reports,s):
    membership={j:g for g,mm in enumerate(groups) for j in mm};mass={}
    for th in product([0,1],repeat=len(c)):
        value=F(0)
        for z in product([0,1],repeat=len(groups)):
            hs,ls=sum(cal['high']),sum(cal['low']);hn,ln=len(cal['high']),len(cal['low'])
            for j in range(len(c)):
                for m in [0,1]:
                    n=sum(c[j][m]);success=c[j][m][th[j]]
                    if m==z[membership[j]]:hs+=success;hn+=n
                    else:ls+=success;ln+=n
            typ=F(1)
            for g,rr in enumerate(reports):
                acc=s[g];matches=sum(v==z[g] for v in rr);typ*=acc**matches*(1-acc)**(len(rr)-matches)
            value+=typ*integral(hs,hn-hs,ls,ln-ls,F(1,20))
        mass[th]=value
    return mass

def entropy(mass):
    total=sum(mass.values());out=Decimal(0)
    for x in mass.values():
        prob=Decimal(x.numerator)*Decimal(total.denominator)/(Decimal(x.denominator)*Decimal(total.numerator))
        if prob:out-=prob*prob.ln()
    return out

def main():
    cases=[];max_error=0
    fixtures=[([[[1,2],[2,0]]],[[0]],{'high':[1],'low':[0]},[[1]]),
              ([[[1,2],[2,0]],[[0,1],[1,1]]],[[0],[1]],{'high':[1,1],'low':[0,1]},[[1],[0]]),
              ([[[1,2],[2,0]],[[0,1],[1,1]]],[[0,1]],{'high':[],'low':[]},[[]])]
    with localcontext() as ctx:
        ctx.prec=80
        for fi,(c,g,cal,reports) in enumerate(fixtures):
            s=[F(4,5)]*len(g);mass=exact_mass(c,g,cal,reports,s);base=sum(mass.values());h=entropy(mass)
            fit=posterior(c,g,cal,reports,list(map(float,s)));scores=information_scores(fit,g,list(map(float,s)))
            for a in range(2*len(c)+len(g)):
                eh=Decimal(0)
                for bit in [0,1]:
                    cc=json.loads(json.dumps(c));rr=[v[:] for v in reports]
                    if a<2*len(c):j,m=divmod(a,2);cc[j][m][bit]+=1
                    else:rr[a-2*len(c)].append(bit)
                    nxt=exact_mass(cc,g,cal,rr,s);prob=sum(nxt.values())/base
                    eh+=Decimal(prob.numerator)/Decimal(prob.denominator)*entropy(nxt)
                exact=float(h-eh);numeric=float(np.exp(scores[a]));error=abs(exact-numeric);max_error=max(max_error,error)
                cases.append({'fixture':fi,'action':a,'exact_information_decimal':str(h-eh),'numerical_information':numeric,'absolute_error':error})
    assert max_error<1e-12,max_error
    dest=ROOT/'audit/INFORMATION_CHECK.json';dest.write_text(json.dumps({'cases':len(cases),'max_absolute_error':max_error,'records':cases,'scope':'same_context_exact_entropy_cross_check_no_worlds'},indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'max_absolute_error':max_error}))
if __name__=='__main__':main()
