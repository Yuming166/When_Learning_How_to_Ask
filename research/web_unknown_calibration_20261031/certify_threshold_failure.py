"""Exact-rational interval certificate; continuous oracle feasibility included.

This certifies bounds, not numerical optimizers. No model calls or random draws.
Logs use range reduction and a finite atanh series with a rational remainder.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TERMS=20


def basic_log(x):
    assert 1<=x<=2
    z=(x-1)/(x+1)
    zz=z*z
    power=z
    lo=F(0)
    for i in range(TERMS):
        lo+=2*power/(2*i+1)
        power*=zz
    return lo,lo+2*power/((2*TERMS+1)*(1-zz))


LN2=basic_log(F(2))


@lru_cache(maxsize=20000)
def log_bounds(x):
    assert x>0
    power=0
    while x<1:
        x*=2
        power-=1
    while x>2:
        x/=2
        power+=1
    lo,hi=basic_log(x)
    if power>=0:
        return lo+power*LN2[0],hi+power*LN2[1]
    return lo+power*LN2[1],hi+power*LN2[0]


def kl(P,Q):
    lo=hi=F(0)
    for p,q in zip(P,Q):
        a,b=log_bounds(p/q)
        lo+=p*a
        hi+=p*b
    return lo,hi


def bern(p,q): return kl([p,1-p],[q,1-q])


def law(r,a,b,na,nb,negative=False):
    wr=1-r if negative else r
    out=[]
    for sa in range(na+1):
        for sb in range(nb+1):
            f=a**sa*(1-a)**(na-sa)*b**sb*(1-b)**(nb-sb)
            rev=(1-a)**sa*a**(na-sa)*(1-b)**sb*b**(nb-sb)
            out.append(comb(na,sa)*comb(nb,sb)*(wr*f+(1-wr)*rev))
    assert sum(out)==1
    return out


def dec(x):
    with localcontext() as ctx:
        ctx.prec=50
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def run():
    r,p,q=F(4,5),F(4,5),F(3,5)
    c,cap,alpha=10,5,1
    # Certify the previously proved known-rate criterion at its unique depth.
    information={}
    for length in range(1,cap+1):
        truth=law(r,p,q,length,0)
        information[length]=dict(A=kl(truth,law(r,p,q,length,0,True)),
                                 V=kl(truth,law(r,q,p,length,0,True)))
    a5=information[5]['A']
    assert all(a5[0]/15>information[L]['A'][1]/(10+L) for L in range(1,5))
    gamma_lower=information[5]['V'][0]/a5[1]
    assert gamma_lower>1

    # The inner KL is not a convex Bernoulli-isotonic problem after marginalizing V.
    truth5=law(r,p,q,5,0)
    endpoint_left=kl(truth5,law(r,F(1,2),F(1,2),5,0,True))
    midpoint=kl(truth5,law(r,F(3,5),F(3,5),5,0,True))
    endpoint_right=kl(truth5,law(r,F(7,10),F(7,10),5,0,True))
    jensen_violation=midpoint[0]-(endpoint_left[1]+endpoint_right[1])/2
    assert jensen_violation>0

    # Unknown-rate lower bound from one allowed alternative and a feasible dual weight.
    # Alternative theta=-, z=B, u=p, v=1/2. Two calibration-stream KLs reduce to kl(q,1/2).
    dual_weight=F(25)
    margins=[]
    for length in range(1,cap+1):
        for na in range(length+1):
            nb=length-na
            div=kl(law(r,p,q,na,nb),law(r,F(1,2),p,na,nb,True))
            margin=F(c+length)-dual_weight*div[1]
            assert margin>0
            margins.append(margin)
    calibration=bern(q,F(1,2))
    lower=dual_weight*(1-calibration[1])

    # Continuous known-z oracle feasibility: x=1.61 copies of pure-good depth 5.
    # For given u, v=min(q,u) minimizes calibration; online law does not depend on v.
    # A global absolute derivative bound is 2/eta + x*L/eta=201, eta=1/20.
    x=F(161,100)
    derivative_bound=F(201)
    half_cell=F(1,4000)
    certified_margin=None
    minimum_midpoint=None
    for idx in range(900):
        u=F(1,2)+F(2*idx+1,4000)
        cc1=bern(p,u)
        cc2=bern(q,min(q,u))
        online=kl(law(r,p,q,5,0),law(r,u,u,5,0,True))
        center_lower=cc1[0]+cc2[0]+x*online[0]
        margin=center_lower-derivative_bound*half_cell-1
        assert margin>0,(idx,dec(margin))
        certified_margin=margin if certified_margin is None else min(certified_margin,margin)
        minimum_midpoint=center_lower if minimum_midpoint is None else min(minimum_midpoint,center_lower)
    upper=15*x
    assert lower>upper
    result={
      'status':'PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE',
      'model':{'r':str(r),'p':str(p),'q':str(q),'eta':'1/20','d':1,'L_max':cap,'c':c,'ell':1,'alpha':alpha},
      'known_rate_comparison':{'unique_oracle_depth':5,'gamma_singleton_lower_bound_display':dec(gamma_lower),
                               'leading_premium':'zero by previous proved theorem'},
      'nonconvex_inner_kl':{'alternative_good_rates':['1/2','3/5','7/10'],
                            'midpoint_minus_average_endpoints_lower_display':dec(jensen_violation),
                            'scope':'Pure-good depth-5 truth-flip KL versus alternative extraction level; alpha=0 inner objective.'},
      'unknown_rate_lower_bound':{'alternative':{'theta':'negative','z':'B','u':str(p),'v':'1/2'},
                                  'dual_weight':str(dual_weight),'all_action_constraints_checked':20,
                                  'minimum_dual_slack_lower_display':dec(min(margins)),
                                  'coefficient_lower_display':dec(lower)},
      'unknown_rate_known_z_oracle_upper':{'action':[5,0],'count_coefficient':str(x),
                                         'coefficient_upper':str(upper),
                                         'continuous_domain':'1/2 <= v <= u <= 19/20',
                                         'v_profile':'min(3/5,u)',
                                         'u_cells':900,'cell_width':'1/2000',
                                         'global_derivative_bound':str(derivative_bound),
                                         'minimum_uniform_information_margin_display':dec(certified_margin)},
      'premium_lower_display':dec(lower-upper),
      'ratio_lower_display':dec(lower/upper),
      'arithmetic':{'probabilities':'exact Fraction','log_terms':TERMS,
                    'log_method':'dyadic range reduction; atanh series; proved geometric remainder',
                    'assertions':'exact rational interval comparisons','decimal_values':'display approximations only'},
      'claim_limit':'Certifies a positive premium and failure of known-rate zero-premium criterion; does not compute either exact continuous optimum.',
      'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest()
    }
    (ROOT/'THRESHOLD_FAILURE_CERTIFICATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': run()
