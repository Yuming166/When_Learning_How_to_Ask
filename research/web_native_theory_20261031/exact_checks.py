"""Deterministic checks for the Web theory exploration; no sampled worlds.

Bayes risks and Bellman enumeration use exact Fractions. KL values use
80-digit Decimal logs and are numerical checks, not interval certificates.
Run: python exact_checks.py [--plot] from any directory.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent


def as_float(x):
    return float(x)


def likelihood(state, theta, r, a):
    ans = F(1)
    for plus, minus in state:
        f = a ** plus * (1 - a) ** minus
        g = (1 - a) ** plus * a ** minus
        ans *= r * f + (1 - r) * g if theta == 1 else (1 - r) * f + r * g
    return ans


def mass(state, r, a):
    return (likelihood(state, 1, r, a) + likelihood(state, -1, r, a)) / 2


def risk(state, r, a):
    lp, lm = (likelihood(state, t, r, a) for t in (1, -1))
    return min(lp, lm) / (lp + lm)


def child(state, action, y):
    out = list(state)
    if action == len(state):
        out.append((1, 0) if y == 1 else (0, 1))
    else:
        p, m = out[action]
        out[action] = (p + (y == 1), m + (y == -1))
    return tuple(sorted(out))


def one_step(state, action, r, a):
    base = mass(state, r, a)
    total = F(0)
    ps = F(0)
    for y in (1, -1):
        ch = child(state, action, y)
        py = mass(ch, r, a) / base
        ps += py
        total += py * risk(ch, r, a)
    assert ps == 1
    return total


def moments(state, root, r, a):
    z = F(0)
    m = F(0)
    corr = F(0)
    for t in (1, -1):
        for vs in product((1, -1), repeat=len(state)):
            w = F(1, 2)
            for (pos, neg), v in zip(state, vs):
                w *= r if v == t else 1 - r
                w *= a ** pos * (1-a) ** neg if v == 1 else (1-a) ** pos * a ** neg
            z += w
            m += w * t
            corr += w * t * vs[root]
    return m/z, corr/z


def binomial_floor(n, r):
    return sum((F(comb(n, j)) * r**j * (1-r)**(n-j)
                * (F(1) if 2*j < n else F(1, 2) if 2*j == n else F(0))
                for j in range(n+1)), F(0))


def root_majority_error(n, r, a):
    e = binomial_floor(n, a)
    return (1-r) + (2*r-1)*e


def dec(x):
    return Decimal(x.numerator)/Decimal(x.denominator)


def block_kl(n, r, a):
    result = Decimal(0)
    for j in range(n+1):
        f, g = a**j*(1-a)**(n-j), (1-a)**j*a**(n-j)
        pp, pm = r*f+(1-r)*g, (1-r)*f+r*g
        result += Decimal(comb(n, j))*dec(pp)*(dec(pp)/dec(pm)).ln()
    return result


def dp_table(r, a):
    rows = []
    for activation in (0, 1, 3):
        @lru_cache(None)
        def value(state, budget, strategy):
            best = risk(state, r, a)
            available = list(range(len(state)+1))
            if strategy == 'new_only':
                available = [len(state)]
            elif strategy == 'one_root':
                available = [0]
            for act in available:
                cost = 1 + (activation if act == len(state) else 0)
                if cost > budget:
                    continue
                val = F(0)
                base = mass(state, r, a)
                for y in (1, -1):
                    ch = child(state, act, y)
                    val += mass(ch, r, a)/base*value(ch, budget-cost, strategy)
                best = min(best, val)
            return best
        for budget in (3, 5, 7, 9):
            vals = {s: value((), budget, s) for s in ('optimal', 'new_only', 'one_root')}
            assert vals['optimal'] <= min(vals['new_only'], vals['one_root'])
            rows.append({'activation': activation, 'budget': budget,
                         'risk': {k: str(v) for k, v in vals.items()},
                         'risk_decimal': {k: float(v) for k, v in vals.items()}})
        rows[-1]['cached_subproblems_all_budgets_strategies'] = value.cache_info().currsize
    return rows


def main():
    r, a = F(4, 5), F(7, 10)
    states = [((1, 1), (1, 1)), ((2, 0), (0, 2))]
    examples = []
    formula_checks = 0
    for state in states:
        m, corr = moments(state, 0, r, a)
        lr, ln = one_step(state, 0, r, a), one_step(state, len(state), r, a)
        assert m == 0
        assert lr == (1-max(abs(m), (2*a-1)*abs(corr)))/2
        assert ln == (1-max(abs(m), (2*a-1)*(2*r-1)))/2
        costs = {'stop': risk(state,r,a), 'repeat': lr+F(1,100), 'new': ln+F(3,100)}
        examples.append({'state': state, 'theta_mean': str(m), 'theta_root_correlation': str(corr),
                         'repeat_error': str(lr), 'new_error': str(ln),
                         'objectives': {k: str(v) for k,v in costs.items()},
                         'best': min(costs, key=costs.get)})
    assert [e['best'] for e in examples] == ['repeat', 'new']
    # Independent latent-state summation versus the closed one-step identity.
    for x in product(range(3), repeat=4):
        state = ((x[0],x[1]), (x[2],x[3]))
        for root in (0, 1):
            m, corr = moments(state, root, r, a)
            assert one_step(state,root,r,a) == (1-max(abs(m),(2*a-1)*abs(corr)))/2
            formula_checks += 1
    # The exact root-observation Bayes floor equals enumeration over all reports.
    for n in range(1, 9):
        enum = sum((min(r**v.count(1)*(1-r)**v.count(-1),
                        (1-r)**v.count(1)*r**v.count(-1))/2
                    for v in product((1,-1), repeat=n)), F(0))
        assert enum == binomial_floor(n,r)
    with localcontext() as ctx:
        ctx.prec = 80
        ds = [block_kl(k,r,a) for k in range(1,65)]
        cap = (2*dec(r)-1)*(dec(r)/(1-dec(r))).ln()
        assert all(0 < d < cap for d in ds)
        assert all(ds[i+1]>ds[i] for i in range(63))
        batches = []
        for c in (0,1,3,10,50):
            best = max(range(1,65), key=lambda k: ds[k-1]/(c+k))
            rate = ds[best-1]/(c+best)
            # Analytic cap rules out all unenumerated k>=65 (numerically compared).
            tail_bound = cap/(c+65)
            assert rate > tail_bound
            batches.append({'activation':c,'best_k':best,'coefficient':str(1/rate),
                            'max_unenumerated_rate_bound':str(tail_bound),
                            'selected_rate':str(rate)})
        k3threshold = (3*ds[0]-ds[2])/(ds[2]-ds[0])
    # Positive same-root covariance for repeats, conditional on theta.
    covariance = 4*r*(1-r)*(2*a-1)**2
    out = {'scope':'Deterministic analytical enumeration only; no empirical validation.',
           'arithmetic':'Fractions for risks/DP; 80-digit Decimal KL, not directed interval certification',
           'parameters':{'r':str(r),'a':str(a),'query_cost':1},
           'one_step_formula_checks':formula_checks,'floor_checks':8,
           'same_posterior_counterexample':examples,
           'root_covariance':str(covariance),
           'block_kl':{str(k):str(v) for k,v in enumerate(ds,1)},
           'root_kl_cap':str(cap),'batch_comparisons':batches,
           'k3_vs_k1_activation_crossover':str(k3threshold),
           'finite_budget_dp':dp_table(r,a),
           'r08_a09_repeat_vs_new':[{'queries':n,
               'one_root_error':float(root_majority_error(n,r,F(9,10))),
               'new_root_each_query_error':float(binomial_floor(n,F(37,50)))}
               for n in (1,3,5,9,21,51)],
           'model_calls':0,'training_runs':0,'sampled_worlds':0}
    (ROOT/'ANALYTICAL_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    if '--plot' in sys.argv:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
        ns = list(range(1,52,2))
        axes[0].plot(ns,[float(root_majority_error(n,r,F(9,10))) for n in ns],label='Repeat one root')
        axes[0].plot(ns,[float(binomial_floor(n,F(37,50))) for n in ns],label='Fresh root each query')
        axes[0].axhline(.2,color='gray',ls=':',label='One-root floor')
        axes[0].set(xlabel='Extraction queries (activation excluded)',ylabel='Bayes error',title='Source error persists (r=.8, a=.9)')
        axes[0].legend(fontsize=8)
        ks = list(range(1,65))
        axes[1].plot(ks,[float(d) for d in ds],label='Block KL')
        axes[1].axhline(float(cap),color='gray',ls=':',label='Root KL cap')
        axes[1].set(xlabel='Queries per independent root',ylabel='KL (nats)',title='Information saturation (r=.8, a=.7)')
        axes[1].legend(fontsize=8)
        for c in (0,3,10,50):
            rates=[float(ds[k-1])/(c+k) for k in ks]
            axes[2].plot(ks[:30],rates[:30],label=f'Activation cost {c}')
        axes[2].set(xlabel='Queries per root (completed blocks)',ylabel='KL / total cost',title='Cost changes extraction depth')
        axes[2].legend(fontsize=8)
        fig.savefig(ROOT/'analytical_examples.png',dpi=180)
        fig.savefig(ROOT/'analytical_examples.pdf')
        plt.close(fig)
    print(json.dumps({'one_step_checks':formula_checks,'floor_checks':8,
                      'dp_rows':len(out['finite_budget_dp']),
                      'batch_best_k':{v['activation']:v['best_k'] for v in batches},
                      'counterexample_actions':[e['best'] for e in examples],
                      'scope':out['scope']}))


if __name__ == '__main__':
    main()
