"""Bounded structural and continuous checks; no model calls or user data."""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from general_geometry import (Catalogue, GeneralProgram, THREE, WEIGHTED,
                              cover_lp, exact_cover_certificate, group_masses,
                              mask_of, minimal_wrong_flips, psi, rows_and_pairs,
                              split_information)

ROOT=Path(__file__).resolve().parent


def log_interval(x, terms=120):
    x=F(x); assert x>0
    z=(x-1)/(x+1); z2=z*z; power=z; total=F(0)
    for j in range(terms):
        total+=2*power/F(2*j+1); power*=z2
    tail=2*abs(power)/(F(2*terms+1)*(1-z2))
    return total-tail,total+tail


def entropy_interval(x):
    x=F(x)
    if x in (0,1): return F(0),F(0)
    a,b=log_interval(x),log_interval(1-x)
    return -x*a[1]-(1-x)*b[1],-x*a[0]-(1-x)*b[0]


def phase_margin_interval(k,p):
    p=F(p); h=entropy_interval(p); h2=entropy_interval(F(1,2))
    hs=entropy_interval(p-(2*p-1)/k)
    # Bp/2 - psi_p(1/k) = (H(.5)+H(p))/2-H(p-(2p-1)/k).
    return (h2[0]+h[0])/2-hs[1],(h2[1]+h[1])/2-hs[0]


def rational_rank(matrix):
    a=[list(map(F,row)) for row in matrix]; rank=0
    for col in range(len(a[0])):
        pivot=next((r for r in range(rank,len(a)) if a[r][col]),None)
        if pivot is None: continue
        a[rank],a[pivot]=a[pivot],a[rank]
        scale=a[rank][col]; a[rank]=[x/scale for x in a[rank]]
        for r in range(len(a)):
            if r != rank:
                scale=a[r][col]; a[r]=[x-scale*y for x,y in zip(a[r],a[rank])]
        rank+=1
    return rank


def catalogue_checks():
    cases={}; exact={}
    for cat in (WEIGHTED,THREE):
        winners,gap,scores=cat.evaluate_cube()
        flips=minimal_wrong_flips(winners,0)
        assert set(winners)==set(range(len(cat.offsets)))
        relevant=[]
        for j in range(cat.d):
            witness=next(s for s in range(1<<cat.d) if winners[s] != winners[s^(1<<j)])
            relevant.append({'coordinate':j+1,'state_mask':witness,
                             'before':winners[witness],'after':winners[witness^(1<<j)]})
        rho,weight=cover_lp(flips,cat.d)
        cases[cat.name]={'dimensions':cat.d,'items':len(cat.offsets),
                        'full_cube_states':len(winners),'winner_counts':[winners.count(i) for i in range(len(cat.offsets))],
                        'minimum_winner_gap_exact':str(gap),'minimal_flips':list(flips),
                        'alternative_winners':[winners[f] for f in flips],
                        'all_coordinates_relevant':relevant,'rho_float':rho}
        if cat==WEIGHTED:
            assert set(flips)=={1,2,12}
            w=(F(1,3),F(1,3),F(1,3),F(0))
            lam=(F(1,3),)*3
            exact[cat.name]=exact_cover_certificate(flips,w,F(1,3),lam)
        else:
            expected=tuple(mask_of(tuple(int(c)-1 for c in s)) for s in ['12','13','234','235','145','236','46','56'])
            assert set(flips)==set(expected)
            w=tuple(F(x,13) for x in (3,2,2,1,1,4))
            by_mask=dict(zip(expected,[F(2,13),F(2,13),F(3,26),F(3,26),F(1,13),F(0),F(5,26),F(5,26)]))
            lam=tuple(by_mask[f] for f in flips)
            exact[cat.name]=exact_cover_certificate(flips,w,F(5,13),lam)
            active=[f for f,l in zip(flips,lam) if l>0]
            rank=rational_rank([[int(bool(f&(1<<j))) for j in range(cat.d)] for f in active])
            assert rank==6
            exact[cat.name]['active_rank']=rank
            # Check the binding-balance obstruction for every proper subset.
            violations=[]
            for mask in range(1,(1<<cat.d)-1):
                W=sum(w[j] for j in range(cat.d) if mask&(1<<j))
                f=next(f for f in active
                       if sum(w[j] for j in range(cat.d) if (mask&f)&(1<<j)) != F(5,13)*W)
                violations.append({'group_mask':mask,'binding_flip_witness':f})
            exact[cat.name]['all_proper_group_subsets_excluded']=violations
    return cases,exact


def entropy_checks():
    rng=np.random.default_rng(20261103)
    maximum=0.; fits=[]
    for case in range(120):
        d=int(rng.integers(2,8)); G=int(rng.integers(1,min(d,4)+1))
        groups=list(range(G))+list(rng.integers(0,G,size=d-G))
        w=rng.dirichlet(np.ones(d))
        if case%5==0:
            w[np.argmax(w)]=0; w/=w.sum()
        flip=int(rng.integers(1,1<<d)); p=float(rng.uniform(.55,.95)); q=.5+(p-.5)*.4
        exhaustive=split_information(p,w,groups,flip)
        prefix=split_information(p,w,groups,flip,sorted_only=True)
        pr=GeneralProgram([flip],groups,p,q)
        x=np.r_[w,np.zeros(d)]
        original=min(pr.evaluate(x,flip,z).value for z in range(1<<G))
        error=max(abs(exhaustive['value']-prefix['value']),abs(exhaustive['value']-original))
        assert error<3e-13
        maximum=max(maximum,error)
        if case<24:
            # Independent constrained minimizer is a cross-check of the imported inner fit.
            fits.append(pr.independently_check_inner(x,flip,case%(1<<G)))
    return {'fixtures':120,'max_prefix_exhaustive_original_difference':maximum,
            'independent_SLSQP_checks':len(fits),'max_SLSQP_difference':max(fits)}


def continuous_checks(catalogues):
    fixtures=[('weighted_shared',[0,0,0,1],WEIGHTED,.8,.6,True),
              ('weighted_split',[0,0,1,1],WEIGHTED,.8,.6,False),
              ('three_shared',[0]*6,THREE,.8,.6,True),
              ('three_split',[0,0,0,1,1,1],THREE,.8,.6,False)]
    answers=[]
    for name,groups,cat,p,q,zero in fixtures:
        flips=catalogues[cat.name]['minimal_flips']; rho=catalogues[cat.name]['rho_float']
        solver=GeneralProgram(flips,groups,p,q)
        fit=solver.solve()
        oracle=1/psi(p,rho)
        assert abs(fit['numerically_repaired_upper_cost']/oracle-1)<2e-6 if zero else fit['numerical_lower_cost']>oracle*1.001
        answers.append({'name':name,'groups':groups,'p':p,'q':q,'oracle_formula':oracle,
                        'predicted_zero_premium':zero,**fit})
    for p,zero in [(.6,True),(.8,False)]:
        k=7; flips=rows_and_pairs(k); groups=[0]*k+[1]*k; q=.55
        fit=GeneralProgram(flips,groups,p,q).solve()
        oracle=1/psi(p,1/k)
        assert abs(fit['numerically_repaired_upper_cost']/oracle-1)<2e-6 if zero else fit['numerical_lower_cost']>oracle*1.0001
        answers.append({'name':f'rows_pairs_k7_p{p}','groups':groups,'p':p,'q':q,
                        'oracle_formula':oracle,'predicted_zero_premium':zero,**fit})
    return answers


def phase_checks():
    exact={}; numerical=[]
    for k,p,zero in [(7,F(3,5),True),(7,F(4,5),False),(8,F(3,4),True),
                     (7,F(73489,100000),True),(7,F(73490,100000),False)]:
        lo,hi=phase_margin_interval(k,p)
        assert lo>0 if zero else hi<0
        # Keep rigorously outward-rounded rational receipts compact. The raw
        # exact series fractions can have thousands of digits at decimal rates.
        scale=10**30
        lo_short=F((lo*scale).__floor__(),scale)
        hi_short=F((hi*scale).__ceil__(),scale)
        assert lo_short <= lo <= hi <= hi_short
        assert lo_short>0 if zero else hi_short<0
        exact[f'k{k}_p{p}']={'k':k,'p':str(p),'margin_lower':str(lo_short),'margin_upper':str(hi_short),
                             'margin_display':[float(lo_short),float(hi_short)],'zero_premium':zero,
                             'status':'EXACT_RATIONAL_LOG_SERIES_SIGN','series_terms':120}
    for p in np.linspace(.51,.99,80):
        numerical.append({'p':float(p),'psi_over_B':psi(float(p),1/7)/psi(float(p),.5)})
    # Realize a bounded arbitrary antichain exactly as affine utilities.
    flips=rows_and_pairs(3); d=6; m=len(flips)
    offsets=[F(0)]+[-F(f.bit_count(),2)+F(i+1,8*(m+1)) for i,f in enumerate(flips)]
    slopes=[(F(0),)*d]+[tuple(-F(1,2) if (f>>j)&1 else F(0) for j in range(d)) for f in flips]
    cat=Catalogue('antichain_realization_k3',tuple(offsets),tuple(slopes))
    winners,gap,_=cat.evaluate_cube()
    assert set(minimal_wrong_flips(winners,0))==set(flips)
    assert set(winners)==set(range(m+1))
    return exact,numerical,{'items':m+1,'states':len(winners),'all_items_win':True,
                            'minimum_gap_exact':str(gap),'minimal_flips_verified':list(flips)}


def main():
    cats,exact=catalogue_checks()
    ent=entropy_checks()
    continuous=continuous_checks(cats)
    signs,curve,realization=phase_checks()
    result={'status':'PASS_BOUNDED_STRUCTURAL_CHECKS_NOT_POLICY_OR_EMPIRICAL_VALIDATION',
            'catalogues':cats,'entropy_reduction':ent,'continuous_cases':continuous,
            'phase_curve_k7':curve,'affine_realization':realization,
            'scripts':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                       for name in ['general_geometry.py','validate_general.py']},
            'imported_previous_solver_sha256':hashlib.sha256((ROOT.parent/'top1_decision_theory_20261103'/'decision_information.py').read_bytes()).hexdigest(),
            'model_calls':0,'training_runs':0,
            'limits':['alpha=0 only; total unknown-type optimum can use both formats',
                      'continuous costs are float diagnostics, not certificates',
                      'true parameters are for complexity analysis, not an online policy']}
    (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'exact_certificates.json').write_text(json.dumps({'catalogue_cover':exact,'phase_signs':signs},indent=2)+'\n')
    print(json.dumps({'status':result['status'],'enumerated_catalogue_states':sum(x['full_cube_states'] for x in cats.values()),
                      'entropy_checks':ent,'continuous_cases':len(continuous),'exact_phase_signs':len(signs)},indent=2))


if __name__=='__main__': main()
