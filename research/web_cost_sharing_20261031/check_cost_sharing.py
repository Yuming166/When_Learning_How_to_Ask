"""Deterministic checks of the fixed-menu theorem; no inference or world sampling.

Exact rational arithmetic checks distributions and sufficiency. KL tables use
80-digit Decimal (not directed intervals). LP checks use SciPy/HiGHS doubles
and include every wrong-answer nuisance alternative and every mixed block.
Fixtures are illustrative mathematical checks, not an empirical preregistration.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
import json
from math import comb, log
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent


def block_law(r, p, q, theta, z, na, nb):
    """Works with Fraction, Decimal, or float; counts in lexicographic order."""
    aa, ab = (p, q) if z == 0 else (q, p)
    wr = r if theta == 0 else 1-r
    out = []
    for sa in range(na+1):
        for sb in range(nb+1):
            plus = aa**sa*(1-aa)**(na-sa)*ab**sb*(1-ab)**(nb-sb)
            minus = (1-aa)**sa*aa**(na-sa)*(1-ab)**sb*ab**(nb-sb)
            out.append(comb(na, sa)*comb(nb, sb)*(wr*plus+(1-wr)*minus))
    return out


def divergence(a, b):
    if isinstance(a[0], Decimal):
        return sum(x*(x/y).ln() for x, y in zip(a, b))
    return sum(x*log(x/y) for x, y in zip(a, b))


def pure_information(r, p, q, depth):
    pp = block_law(r, p, q, 0, 0, depth, 0)
    pm = block_law(r, p, q, 1, 0, depth, 0)
    qp = block_law(r, p, q, 0, 1, depth, 0)
    qm = block_law(r, p, q, 1, 1, depth, 0)
    return divergence(pp, pm), divergence(pp, qp), divergence(pp, qm)


def rational_checks():
    records = []
    fixtures = [('4/5', '4/5', '3/5'), ('3/5', '3/4', '1/2')]
    for rr, pp, qq in fixtures:
        r, p, q = map(Fraction, (rr, pp, qq))
        for length in range(1, 5):
            for na in range(length+1):
                nb = length-na
                for theta, z in product(range(2), repeat=2):
                    pmf = block_law(r, p, q, theta, z, na, nb)
                    expanded = [Fraction(0) for _ in pmf]
                    lr_by_count = {}
                    for seq in product(range(2), repeat=length):
                        def prob(t):
                            weight = r if t == 0 else 1-r
                            vals = []
                            for root in range(2):
                                mass = weight if root == 0 else 1-weight
                                for pos, answer in enumerate(seq):
                                    fmt = 0 if pos < na else 1
                                    rate = p if fmt == z else q
                                    mass *= rate if answer == root else 1-rate
                                vals.append(mass)
                            return sum(vals)
                        a, b = prob(theta), prob(1-theta)
                        # In this enumerator 0 denotes a positive answer.
                        sa, sb = seq[:na].count(0), seq[na:].count(0)
                        idx = sa*(nb+1)+sb
                        expanded[idx] += a
                        if idx in lr_by_count:
                            assert lr_by_count[idx] == a/b
                        lr_by_count[idx] = a/b
                    assert expanded == pmf and sum(pmf) == 1
                    records.append([rr, pp, qq, theta, z, na, nb])
    return {'exact_count_law_and_truth_likelihood_sufficiency_checks': len(records),
            'fixtures': fixtures, 'max_depth': 4, 'all_passed': True}


def solve_full_lp(r, p, q, sizes, cap, c, ell=1.0):
    groups = [g for g, k in enumerate(sizes) for _ in range(k)]
    d, ng = len(groups), len(sizes)
    pairs = [(na, length-na) for length in range(1, cap+1)
             for na in range(length+1)]
    actions = [(j, na, nb) for j in range(d) for na, nb in pairs]
    alternatives = [(theta, z) for theta in product(range(2), repeat=d)
                    if any(theta) for z in product(range(2), repeat=ng)]
    kl = {}
    for na, nb in pairs:
        truth = block_law(r, p, q, 0, 0, na, nb)
        for t, z in product(range(2), repeat=2):
            kl[na, nb, t, z] = divergence(truth, block_law(r, p, q, t, z, na, nb))
    mat = np.array([[kl[na, nb, theta[j], z[groups[j]]]
                     for j, na, nb in actions] for theta, z in alternatives])
    costs = np.array([c+ell*(na+nb) for _, na, nb in actions])
    lp = linprog(costs, A_ub=-mat, b_ub=-np.ones(len(alternatives)),
                 bounds=(0, None), method='highs')
    assert lp.success, lp.message
    auv = [pure_information(r, p, q, length) for length in range(1, cap+1)]
    efficiency = [a/(c+ell*length) for length, (a, _, _) in enumerate(auv, 1)]
    best = max(efficiency)
    depths = [i+1 for i, val in enumerate(efficiency)
              if abs(val-best) <= 1e-11*max(1.0, abs(best))]
    gamma = max((auv[length-1][2]+(min(sizes)-1)*auv[length-1][1])
                /auv[length-1][0] for length in depths)
    oracle = d/best
    ratio = lp.fun/oracle
    predicted_zero = gamma >= 1-1e-10
    observed_zero = abs(ratio-1) <= 2e-7
    assert predicted_zero == observed_zero, (r,p,q,sizes,cap,c,gamma,ratio)
    assert ratio >= 1-2e-7
    residual = float(np.min(mat@lp.x)-1)
    duality_gap = abs(float(lp.fun-np.dot(-np.ones(len(alternatives)), lp.ineqlin.marginals)))
    assert residual >= -2e-7
    assert duality_gap <= 1e-6*max(1, lp.fun)
    return dict(r=r,p=p,q=q,group_sizes=sizes,L_max=cap,c=c,ell=ell,
                actions=len(actions),wrong_answer_alternatives=len(alternatives),
                oracle_depths=depths,gamma_at_best=gamma,
                oracle_coefficient=oracle,unknown_coefficient=float(lp.fun),
                cost_ratio=ratio,predicted_zero_premium=predicted_zero,
                primal_min_slack=residual,primal_dual_gap=duality_gap)


def decimal_tables():
    rows = []
    with localcontext() as ctx:
        ctx.prec = 80
        for rr, pp, qq in [('0.8','0.8','0.6'), ('0.8','0.8','0.5'),
                           ('0.95','0.8','0.7'), ('0.51','0.8','0.6'),
                           ('0.999','0.75','0.749')]:
            r,p,q = map(Decimal,(rr,pp,qq))
            previous_a = Decimal(0)
            for length in range(1, 49):
                a,u,v = pure_information(r,p,q,length)
                assert a > previous_a and v >= u-Decimal('1e-70') and u > 0
                previous_a = a
                rows.append(dict(r=rr,p=pp,q=qq,L=length,
                                 A=str(a),U=str(u),V=str(v),
                                 gamma_singleton=str(v/a),
                                 k_required=max(1,1+int(((a-v)/u).to_integral_value(rounding='ROUND_CEILING')))))
    return rows


def balanced_finite_bound(r, p, q, k, c, ell, delta):
    pmf = block_law(r,p,q,0,0,k,k)
    plus = [0.0]*(2*k+1)
    for sa in range(k+1):
        for sb in range(k+1):
            plus[sa+sb] += pmf[sa*(k+1)+sb]
    dbar = divergence(plus, list(reversed(plus)))
    kappa = (2*r-1)*log(r/(1-r))
    rlog = log(1/delta)
    binary = (1-2*delta)*log((1-delta)/delta)
    bound = kappa/dbar*(1+2*k*ell/c)*(rlog+log(r/(1-r)))/binary
    return dict(r=r,p=p,q=q,k=k,c=c,ell=ell,delta=delta,
                Dbar=dbar,oracle_relative_upper_bound=bound)


def depth_intervals(r,p,q,cap,ell=1.0):
    """All pairwise efficiency comparisons give the exact algebraic cost intervals.

    The KL coefficients are evaluated in double precision here; endpoints are
    numerical instantiations of the pairwise crossover formula, not certificates.
    """
    aa=[pure_information(r,p,q,length)[0] for length in range(1,cap+1)]
    out=[]
    for length,a in enumerate(aa,1):
        low,high=0.0,float('inf')
        for j,b in enumerate(aa,1):
            if j==length: continue
            cross=ell*(b*length-a*j)/(a-b)
            if a>b: low=max(low,cross)
            else: high=min(high,cross)
        if low<=high:
            u,v=pure_information(r,p,q,length)[1:]
            out.append(dict(L=length,c_lower=low,c_upper=None if np.isinf(high) else high,
                            gamma_singleton=v/a))
    return out


def main(plot=False):
    exact = rational_checks()
    rows = decimal_tables()
    lp_results = []
    # Every fixture is retained, including near-equal-rate and near-uninformative sources.
    for r,p,q in [(0.8,0.8,0.6),(0.8,0.8,0.5),(0.95,0.8,0.7),
                  (0.51,0.8,0.6),(0.999,0.75,0.749)]:
        for sizes in [[1],[2],[1,2],[2,2]]:
            for cap,c in [(1,0),(2,0),(4,2),(8,20)]:
                lp_results.append(solve_full_lp(r,p,q,sizes,cap,c))
    # Illustrative finite source-cost sweep with a fixed menu, including all mixed blocks.
    cost_sweep = [solve_full_lp(.8,.8,.6,[1],12,c)
                  for c in [0,.5,1,2,3,5,10,20,50,100]]
    cap_control=solve_full_lp(.8,.8,.6,[1],1,100)
    intervals=depth_intervals(.8,.8,.6,12)
    # An exact algebraic crossover is instantiated numerically. Retain every tied optimum.
    a1 = pure_information(.8,.8,.6,1)[0]
    a2 = pure_information(.8,.8,.6,2)[0]
    crossing = (2*a1-a2)/(a2-a1)
    tie_results = [solve_full_lp(.8,.8,.6,sizes,2,crossing)
                   for sizes in [[1],[2],[3],[4]]]
    mixed_checks = []
    for r,p,q in [(.8,.8,.6),(.8,.8,.5),(.51,.75,.749)]:
        for length in range(1,9):
            a = pure_information(r,p,q,length)[0]
            for na in range(length):
                nb = length-na
                val = divergence(block_law(r,p,q,0,0,na,nb),block_law(r,p,q,1,0,na,nb))
                assert val < a
                mixed_checks.append(a-val)
    finite = [balanced_finite_bound(.8,.8,.6,k,c,1,delta)
              for k,c,delta in [(8,100,.05),(16,1000,.01),(16,1000,1e-6)]]
    results = dict(scope='fixed known rates; completed fresh-root blocks; illustrative deterministic checks',
                   exact_arithmetic=exact,decimal_digits=80,interval_certification=False,
                   decimal_information_table=rows,full_lp_checks=lp_results,
                   cost_sweep=cost_sweep,oracle_tie_checks=tie_results,
                   depth_cap_control=cap_control,oracle_depth_cost_intervals=intervals,
                   strict_mixed_dominance_checks=len(mixed_checks),
                   smallest_numeric_dominance_gap=min(mixed_checks),
                   finite_delta_balanced_bounds=finite,
                   randomized_worlds=0,model_calls=0)
    (ROOT/'CHECK_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    if plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1,3,figsize=(12,3.4),constrained_layout=True)
        main_rows = [x for x in rows if (x['r'],x['p'],x['q'])==('0.8','0.8','0.6') and x['L']<=24]
        for col,label in [('A','truth flip A'),('U','type flip U'),('V','joint flip V')]:
            axes[0].plot([x['L'] for x in main_rows],[float(x[col]) for x in main_rows],label=label)
        axes[0].set(xlabel='Reads per fresh source',ylabel='KL per block',title='Information saturation and type learning')
        axes[0].legend(fontsize=8)
        cs=[x['c'] for x in cost_sweep]
        for interval in intervals:
            lo,hi=interval['c_lower'],interval['c_upper']
            if lo>100: continue
            axes[1].hlines(interval['L'],lo,min(100,hi) if hi is not None else 100,color='C0')
            if hi is not None and hi<=100:
                axes[1].plot([hi],[interval['L']],'o',color='C0',ms=3)
        axes[1].scatter(cs,[x['oracle_depths'][0] for x in cost_sweep],s=13)
        axes[1].set(xlabel='Source activation cost (read cost = 1)',ylabel='Oracle depth',title='Pairwise crossover intervals; depth cap = 12')
        axes[2].plot(cs,[x['cost_ratio'] for x in cost_sweep],'o-')
        axes[2].axhline(1,color='gray',ls='--')
        axes[2].set(xlabel='Source activation cost',ylabel='Unknown / oracle leading cost',title='Singleton group; full mixed-action LP')
        for ax in axes[1:]:
            ax.set_xscale('symlog',linthresh=1)
            ax.set_xlim(0,100)
        fig.suptitle('Controlled model r=0.8, p=0.8, q=0.6; mathematical checks, not Web measurements',fontsize=10)
        fig.savefig(ROOT/'cost_sharing_examples.png',dpi=180)
        fig.savefig(ROOT/'cost_sharing_examples.pdf')
        plt.close(fig)
    print(json.dumps(dict(exact_checks=exact['exact_count_law_and_truth_likelihood_sufficiency_checks'],
                         decimal_rows=len(rows),full_lp_checks=len(lp_results)+len(cost_sweep)+len(tie_results)+1,
                         mixed_checks=len(mixed_checks),cost_sweep=cost_sweep,
                         ties=tie_results,finite_delta_bounds=finite),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--plot',action='store_true')
    main(parser.parse_args().plot)
