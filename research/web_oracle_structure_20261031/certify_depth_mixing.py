"""Exact rational/log-interval proof that every oracle optimum mixes depths.

No search or floating-point optimization is used by this verifier. All old files
are read only. Decimal strings are display approximations to rational bounds.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from math import comb

ROOT=Path(__file__).resolve().parent
DEPENDENCY=ROOT.parent/'web_unknown_calibration_20261031/certify_threshold_failure.py'
spec=importlib.util.spec_from_file_location('exact_previous',DEPENDENCY)
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
law,kl,bern,dec=previous.law,previous.kl,previous.bern,previous.dec

def pure_law_derivative(r,u,L,negative=True):
    wr=1-r if negative else r
    return [comb(L,k)*(wr*u**k*(1-u)**(L-k)*(F(k)/u-F(L-k)/(1-u))
                       +(1-wr)*(1-u)**k*u**(L-k)*(F(L-k)/u-F(k)/(1-u)))
            for k in range(L+1)]

def run():
    r,p,q=F(3,5),F(19,20),F(3,5)
    eta=F(1,40);alpha=F(1);c=F(1);cap=6
    actions=[(a,L-a) for L in range(1,cap+1) for a in range(L+1)]
    truth={ab:law(r,p,q,*ab) for ab in actions}
    b={1:F(14),2:F(2)}
    cost=sum((c+L)*x for L,x in b.items())
    assert cost==34

    # Exact v profile: min(q,u). Curvature bound covers the entire interval,
    # including u=q, because the profiled calibration is C1 there.
    curvature=(2+sum(x*L*(2*L-1) for L,x in b.items()))/eta**2
    assert curvature==44800
    radius=F(1,4000)
    margins=[]
    for idx in range(950):
        u=F(1,2)+F(2*idx+1,4000)
        lo=bern(p,u)[0]+bern(q,min(q,u))[0]
        slope=(u-p)/(u*(1-u))
        if u<q:slope+=(u-q)/(u*(1-u))
        for L,x in b.items():
            P=truth[(L,0)];Q=law(r,u,u,L,0,True)
            lo+=x*kl(P,Q)[0]
            Qprime=pure_law_derivative(r,u,L)
            assert sum(Qprime)==0
            slope-=x*sum(t*d/z for t,d,z in zip(P,Qprime,Q))
        margin=lo-abs(slope)*radius-curvature*radius**2/2-1
        assert margin>0,(idx,dec(margin))
        margins.append(margin)

    # Arbitrary mixtures of formats at any ONE fixed depth are allowed.
    # For L=1 use a closure alternative u=v=1/2; for all L>=2 use true rates.
    depth_bounds=[]
    target=F(413,10)
    for L in range(1,cap+1):
        u,v=(F(1,2),F(1,2)) if L==1 else (p,q)
        dual=F(100) if L==1 else target
        cal_hi=bern(p,u)[1]+bern(q,v)[1]
        slacks=[]
        for a in range(L+1):
            div=kl(truth[(a,L-a)],law(r,u,v,a,L-a,True))[1]
            slack=c+L-dual*div
            assert slack>0,(L,a,dec(slack))
            slacks.append(slack)
        bound=dual*(1-cal_hi)
        assert bound>=target
        depth_bounds.append(dict(L=L,alternative=[str(u),str(v)],dual_weight=str(dual),
                                 lower_bound_display=dec(bound),actions_checked=L+1,
                                 min_dual_slack_display=dec(min(slacks))))

    # Optional common lower bound on the full oracle; all 27 actions retained.
    u,v=F(73,80),q;dual=F(3329,100)
    slacks=[]
    for a,bb in actions:
        div=kl(truth[(a,bb)],law(r,u,v,a,bb,True))[1]
        slack=c+a+bb-dual*div
        assert slack>0,(a,bb,dec(slack))
        slacks.append(slack)
    full_lower=dual*(1-bern(p,u)[1]-bern(q,v)[1])
    assert full_lower>32
    # Compare the SAME instance when extraction rates are additionally revealed.
    # Single-fact known-rate testing has only the opposite-truth alternative.
    d1=kl(truth[(1,0)],law(r,p,q,1,0,True))
    rate_margin=[]
    for a,bb in actions:
        if (a,bb)==(1,0):continue
        other=kl(truth[(a,bb)],law(r,p,q,a,bb,True))
        margin=d1[0]/2-other[1]/(c+a+bb)
        assert margin>0,(a,bb,dec(margin))
        rate_margin.append(margin)
    result=dict(
      status='PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE',
      parameters=dict(r=str(r),p=str(p),q=str(q),eta=str(eta),alpha=str(alpha),d=1,
                      L_max=cap,c=str(c),ell='1',known_to_oracle='format only'),
      witness=dict(per_fact_blocks={str(k):str(v) for k,v in b.items()},format='pure good',
                   cost=str(cost),global_uniform_information_margin_lower_display=dec(min(margins)),
                   continuous_domain='1/2 <= v <= u <= 39/40',v_profile='min(3/5,u)',
                   cells=950,cell_width='1/2000',second_derivative_bound=str(curvature)),
      single_depth=dict(allowed='any mixture of all formats at that fixed depth',
                        per_depth=depth_bounds,universal_lower_bound=str(target),
                        ratio_to_full_oracle_lower_bound=str(target/cost),
                        relative_cost_reduction_at_least=str(1-cost/target)),
      full_oracle_lower=dict(alternative=[str(u),str(v)],dual_weight=str(dual),
                             actions_checked=len(actions),min_dual_slack_display=dec(min(slacks)),
                             coefficient_lower_bound_display=dec(full_lower)),
      known_rate_comparison=dict(unique_best_action=[1,0],
                                  coefficient_interval_display=[dec(2/d1[1]),dec(2/d1[0])],
                                  min_information_per_cost_advantage_display=dec(min(rate_margin))),
      conclusion='Every cost-optimal full-menu oracle allocation uses at least two distinct depths.',
      limits=['Neither exact optimal cost nor exact support is computed.',
              'Pure-good optimality in the full model remains a separate question.',
              'This is a controlled-model theorem, not an empirical Web/LLM result.'],
      arithmetic=dict(probabilities='exact fractions',log_method='20-term dyadic atanh interval',
                      continuous_check='Taylor lower bound with exact slope and global curvature'),
      source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
      interval_dependency=dict(path=str(DEPENDENCY),sha256=sha256(DEPENDENCY.read_bytes()).hexdigest()))
    (ROOT/'DEPTH_MIXING_CERTIFICATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
