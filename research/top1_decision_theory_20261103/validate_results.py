"""Deterministic numerical checks and exact rational witness calculations."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from decision_information import (DecisionProgram, decision, finite_calibration_oracle,
                                  finite_gamma, kl, minimal_flips, threshold_oracle)

ROOT = Path(__file__).resolve().parent


def log_interval(x, terms=80):
    x = F(x); assert x > 0
    z = (x-1)/(x+1)
    z2, power, total = z*z, z, F(0)
    for j in range(terms):
        total += 2*power/F(2*j+1)
        power *= z2
    tail = 2*abs(power)/(F(2*terms+1)*(1-z2))
    return total-tail, total+tail


def kl_interval(p, q):
    a,b = log_interval(p/q),log_interval((1-p)/(1-q))
    return p*a[0]+(1-p)*b[0], p*a[1]+(1-p)*b[1]


def rational_certificates():
    p,q = F(4,5),F(3,5)
    bp,bq,w = kl_interval(p,F(1,2)),kl_interval(q,F(1,2)),kl_interval(q,1-p)
    # Dual of two necessary information constraints for majority-3 singleton groups.
    # All logs are enclosed using exact rational convergent-series bounds.
    assert (2*w[0]+bq[0])/3 > 2*bp[1]/3
    lower = 1+(bp[0]-bq[1])/(2*w[1]-bq[0])
    upper = 1+(bp[1]-bq[0])/(2*w[0]-bq[1])
    assert lower > F(123,100)
    # Possible observation history, not generated model data: 20 plus answers
    # on one coordinate, no other observations, eta=.05 and delta=.01.
    lr = F(19,10)**20
    threshold = F(100)*21
    assert lr > threshold
    return {
        'kind':'EXACT_RATIONAL_LOG_ENCLOSURES_AND_HISTORY_WITNESS',
        'majority3_singleton_premium':{
            'p':'4/5','q':'3/5','alpha':0,
            'ratio_lower_exact':str(lower),'ratio_upper_exact':str(upper),
            'ratio_display':[float(lower),float(upper)],
            'certified_ratio_greater_than':'123/100',
            'interpretation':'unknown-type cost / type-only-oracle cost exceeds 1.23; not an optimal-cost evaluation',
            'log_series_terms':80},
        'decision_GLR_history':{
            'task':'OR on 3 preferences','eta':'1/20','delta':'1/100',
            'history':'20 plus answers on one form of coordinate 1; all other counts zero',
            'decision_likelihood_ratio':str(lr),'mixture_threshold_ratio':str(threshold),
            'decision_test_crosses':True,'full_profile_likelihood_ratio':'1',
            'full_profile_test_crosses':False,
            'status':'possible-history mathematical fixture, not an experiment'}
    }


def combinatorial_checks():
    states = 0
    for d in range(1,6):
        for theta in itertools.product((-1,1), repeat=d):
            for t in range(1,d+1):
                target = decision(theta,t); minimal = minimal_flips(theta,t)
                wrong = []
                for mask in range(1,1<<d):
                    other = tuple(-x if (mask>>j)&1 else x for j,x in enumerate(theta))
                    if decision(other,t) != target:
                        wrong.append(mask)
                exhaustive_min = [m for m in wrong if not any(s != m and s&m == s for s in wrong)]
                assert set(minimal)==set(exhaustive_min)
                shape=threshold_oracle(theta,t,.8)
                assert shape['rho']>0 and shape['oracle_cost']>0
                states += 1
    return states


def independent_inner_checks():
    rng=np.random.default_rng(20261103)
    errors=[]
    for alpha in (0.,.7,2.):
        prog=DecisionProgram([1,1,-1],[0,1,1],2,p=.8,q=.6,alpha=alpha)
        for _ in range(12):
            x=rng.integers(0,5,size=6).astype(float)
            flip,z=prog.alternatives[int(rng.integers(len(prog.alternatives)))]
            errors.append(prog.independently_check_inner(x,flip,z))
    return errors


def coefficient_checks():
    cases=[
        ('majority3_shared',[1,1,1],[0,0,1],2,.8,.6,0.),
        ('majority3_singletons',[1,1,1],[0,1,2],2,.8,.6,0.),
        ('majority5_4plus1',[1]*5,[0,0,0,0,1],3,.8,.6,0.),
        ('majority5_3plus2',[1]*5,[0,0,0,1,1],3,.8,.6,0.),
        ('near_boundary_together',[1,1,1,-1,-1],[0,0,0,1,1],3,.8,.6,0.),
        ('near_boundary_split',[1,1,-1,1,-1],[0,0,0,1,1],3,.8,.6,0.),
        ('majority_negative_symmetry',[-1,-1,-1],[0,0,1],2,.8,.6,0.),
        ('OR_positive',[1,1,-1],[0,1,2],1,.8,.6,0.),
        ('OR_negative',[-1,-1,-1],[0,1,2],1,.8,.6,0.),
        ('AND2_singletons',[1,1],[0,1],2,.8,.6,0.),
        ('active_group_positive_calibration',[1]*5+[-1],[0,0,0,0,0,1],5,.75,.5,25.),
        ('active_group_two_flips_positive_calibration',[1]*9+[-1],[0]*9+[1],8,.75,.5,100.),
    ]
    results=[]
    for name,theta,groups,t,p,q,alpha in cases:
        u=DecisionProgram(theta,groups,t,p,q,alpha).solve()
        o=DecisionProgram(theta,groups,t,p,q,alpha,oracle=True).solve()
        formula=finite_calibration_oracle(theta,t,p,q,alpha)
        assert abs(o['numerically_repaired_upper_cost']-formula['oracle_cost'])<2e-5
        active=[j for j,x in enumerate(theta) if (x>0)==bool(decision(theta,t))]
        active_sizes=[sum(groups[j]==g for j in active) for g in set(groups)]
        if alpha==0:
            predicted=max(active_sizes)>=formula['required_largest_active_group']
        else:
            k=min(k for k in active_sizes if k>0)
            predicted=k>formula['flip_size'] and finite_gamma(k,formula['active'],formula['flip_size'],p,q,alpha,formula['a'])>=1
        gap=u['numerically_repaired_upper_cost']-o['numerically_repaired_upper_cost']
        assert (abs(gap)<2e-5) if predicted else (gap>1e-4)
        if name=='AND2_singletons':
            bp,bq=float(kl(p,.5)),float(kl(q,.5)); k=q-.5
            c=(bp-bq)/(p+q-1)
            exact=2/(2*bq+2*k*c+math.log(math.cosh(c)))
            assert abs(exact-u['numerically_repaired_upper_cost'])<2e-5
            formula['AND_closed_form']=exact
        results.append({'name':name,'theta':theta,'groups':groups,'threshold':t,
                        'p':p,'q':q,'alpha':alpha,'predicted_zero_premium':bool(predicted),
                        'unknown':u,'oracle':o,'analytic_oracle':formula})
    # Positive-OR reduction checked against single-bit program at each alpha.
    curves=[]
    for alpha in (0.,.1,.25,.5,1.,2.,4.,8.):
        one=DecisionProgram([1],[0],1,alpha=alpha).solve()
        multi=DecisionProgram([1,1,-1],[0,1,2],1,alpha=alpha).solve()
        oracle=finite_calibration_oracle([1],1,.8,.6,alpha)
        assert abs(one['numerically_repaired_upper_cost']-multi['numerically_repaired_upper_cost'])<2e-5
        if alpha:
            assert one['numerical_lower_cost']>oracle['oracle_cost']+1e-4
        curves.append({'alpha':alpha,'decision_cost':one['numerically_repaired_upper_cost'],
                       'oracle_cost':oracle['oracle_cost'],
                       'premium':one['numerically_repaired_upper_cost']-oracle['oracle_cost']})
    return results,curves


def main():
    combinatorial=combinatorial_checks()
    inner_errors=independent_inner_checks()
    cases,curve=coefficient_checks()
    certificate=rational_certificates()
    result={'status':'PASS_BOUNDED_NUMERICAL_CHECKS_NOT_EMPIRICAL_VALIDATION',
            'decision_states_exhaustively_checked':combinatorial,
            'independent_SLSQP_inner_checks':len(inner_errors),
            'max_inner_value_difference':max(inner_errors),
            'coefficient_cases':cases,'OR_calibration_curve':curve,
            'new_model_calls':0,'new_training_runs':0,
            'scripts':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                       for name in ['decision_information.py','validate_results.py']},
            'limits':['floating LP bounds are diagnostic, not formal certificates',
                      'oracle input parameters are for complexity evaluation, not a deployed query agent',
                      'no claim of first identification/certificate framework or natural-user validity']}
    (ROOT/'numerical_results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'exact_certificates.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'combinatorial_cases':combinatorial,
                      'independent_inner_checks':len(inner_errors),
                      'coefficient_cases':len(cases),'calibration_curve_points':len(curve),
                      'rational_lower_premium_ratio':certificate['majority3_singleton_premium']['ratio_display'][0]},indent=2))


if __name__=='__main__':
    main()
