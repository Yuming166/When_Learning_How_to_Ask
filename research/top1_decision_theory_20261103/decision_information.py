"""Small decision-level KL programs; CPU only, no inference service.

Parameters are true-instance inputs for information-complexity analysis, not
information supplied to a deployed query-selection policy. Numerical optimization
is diagnostic, not a certified stopping rule or a proof of exact optimum.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.optimize import linprog, minimize


def kl(r, x):
    r, x = np.asarray(r), np.asarray(x)
    return r * np.log(r / x) + (1-r) * np.log((1-r) / (1-x))


def entropy(p):
    return -p*np.log(p)-(1-p)*np.log(1-p)


def psi(p, rho):
    rho = min(0.5, rho)
    return float(entropy(p-(2*p-1)*rho)-entropy(p))


def decision(theta, threshold):
    return int(sum(x > 0 for x in theta) >= threshold)


def minimal_flips(theta, threshold):
    positive = decision(theta, threshold)
    active = [j for j, x in enumerate(theta) if (x > 0) == bool(positive)]
    effective_t = threshold if positive else len(theta)-threshold+1
    need = len(active)-effective_t+1
    return [sum(1 << j for j in js) for js in combinations(active, need)]


@dataclass
class Inner:
    value: float
    row: np.ndarray
    levels: tuple[float, float]
    offline: float


class DecisionProgram:
    def __init__(self, theta, groups, threshold, p=.8, q=.6, alpha=0., oracle=False):
        self.theta = tuple(theta)
        self.groups = np.asarray(groups, dtype=int)
        self.d, self.G = len(theta), int(max(groups))+1
        assert 1 <= threshold <= self.d  # Constant decisions are outside this solver.
        assert set(groups) == set(range(self.G)) and len(groups) == self.d
        assert .5 <= q < p <= .99 and alpha >= 0  # Diagnostic domain: eta=.01.
        self.p, self.q, self.alpha, self.oracle = p, q, alpha, oracle
        self.flips = minimal_flips(theta, threshold)
        self.alternatives = [(f, z) for f in self.flips
                             for z in (range(1) if oracle else range(1 << self.G))]
        self.nvars = 2*self.d

    def row(self, flip, zmask, u, v):
        swapped = ((zmask >> self.groups) & 1).astype(bool)
        flipped = np.array([(flip >> j) & 1 for j in range(self.d)], dtype=bool)
        good_candidate = np.where(swapped, v, u)
        other_candidate = np.where(swapped, u, v)
        good_true = np.where(flipped, 1-self.p, self.p)
        other_true = np.where(flipped, 1-self.q, self.q)
        return np.r_[kl(good_true, good_candidate), kl(other_true, other_candidate)]

    def evaluate(self, x, flip, zmask):
        # Weighted Bernoulli isotonic fit, independently checked by SLSQP.
        weights, means, dest = [self.alpha, self.alpha], [self.p, self.q], [0, 1]
        for j, g in enumerate(self.groups):
            swapped = (zmask >> int(g)) & 1
            flipped = (flip >> j) & 1
            weights.extend([x[j], x[self.d+j]])
            means.extend([1-self.p if flipped else self.p,
                          1-self.q if flipped else self.q])
            dest.extend([swapped, 1-swapped])
        weights, means, dest = np.array(weights), np.array(means), np.array(dest)
        W = np.bincount(dest, weights=weights, minlength=2)
        R = np.bincount(dest, weights=weights*means, minlength=2)
        if W[0] == 0:
            v = max(.5, R[1]/W[1]) if W[1] else .5
            u = max(v, self.p)
        elif W[1] == 0:
            u = max(.5, R[0]/W[0]); v = .5
        else:
            u, v = max(.5, R[0]/W[0]), max(.5, R[1]/W[1])
            if u < v:
                u = v = max(.5, (R[0]+R[1])/(W[0]+W[1]))
        row = self.row(flip, zmask, u, v)
        offline = self.alpha*float(kl(self.p, u)+kl(self.q, v))
        return Inner(float(x@row+offline), row, (float(u), float(v)), offline)

    def independently_check_inner(self, x, flip, zmask):
        analytic = self.evaluate(x, flip, zmask)
        def objective(uv):
            return float(x@self.row(flip, zmask, *uv)
                         +self.alpha*(kl(self.p, uv[0])+kl(self.q, uv[1])))
        fit = minimize(objective, [self.p, self.q], method='SLSQP',
                       bounds=[(.5, .99), (.5, .99)],
                       constraints={'type':'ineq', 'fun':lambda uv:uv[0]-uv[1]},
                       options={'ftol':1e-12, 'maxiter':200})
        if not fit.success:
            raise RuntimeError(fit.message)
        assert abs(float(fit.fun)-analytic.value) < 1e-8
        return abs(float(fit.fun)-analytic.value)

    def solve(self, tolerance=2e-8, max_iterations=150):
        rows, rhs = [], []
        for f, z in self.alternatives:
            for u, v in [(self.p, self.q), (.5, .5), (self.p, .5)]:
                rows.append(self.row(f, z, u, v))
                rhs.append(1-self.alpha*float(kl(self.p, u)+kl(self.q, v)))
        for iteration in range(max_iterations):
            fit = linprog(np.ones(self.nvars), A_ub=-np.array(rows), b_ub=-np.array(rhs),
                          bounds=(0, None), method='highs',
                          options={'primal_feasibility_tolerance':1e-9,
                                   'dual_feasibility_tolerance':1e-9})
            if not fit.success:
                raise RuntimeError(fit.message)
            inners = [(f, z, self.evaluate(fit.x, f, z)) for f, z in self.alternatives]
            worst = min(i.value for _, _, i in inners)
            if worst >= 1-tolerance:
                # Scaling is a mathematical feasibility repair for exact inners.
                # Here inner values and the LP are floating, so labels remain diagnostic.
                scale = max(1., 1/worst)
                x = fit.x*scale
                return {'numerical_lower_cost':float(fit.fun),
                        'numerically_repaired_upper_cost':float(x.sum()),
                        'min_information_before_repair':worst,
                        'min_information_after_repair':min(self.evaluate(x,f,z).value for f,z in self.alternatives),
                        'allocation':x.tolist(), 'iterations':iteration+1,
                        'cuts':len(rows), 'alternative_patterns':len(self.alternatives),
                        'status':'FLOAT_DIAGNOSTIC_NOT_CERTIFIED'}
            for f, z, inner in inners:
                if inner.value < 1-tolerance:
                    rows.append(inner.row); rhs.append(1-inner.offline)
        raise RuntimeError('Exchange solver iteration cap; do not report as convergence')


def threshold_oracle(theta, threshold, p):
    assert 1 <= threshold <= len(theta)
    d = len(theta); positive = decision(theta, threshold)
    n = sum((x > 0) == bool(positive) for x in theta)
    t = threshold if positive else d-threshold+1
    r = n-t+1
    return {'active':n, 'effective_threshold':t, 'flip_size':r,
            'rho':r/n, 'oracle_cost':1/psi(p,r/n),
            'required_largest_active_group':min(n,max(1,2*(t-1)))}


def finite_calibration_oracle(theta, threshold, p, q, alpha):
    shape = threshold_oracle(theta, threshold, p)
    n, r = shape['active'], shape['flip_size']
    def fitted(a):
        u = max(.5, (alpha*p+a*(r+(n-2*r)*p))/(alpha+n*a))
        if u >= q:
            return u, q
        u = max(.5, (alpha*(p+q)+a*(r+(n-2*r)*p))/(2*alpha+n*a))
        return u, u
    def value(a):
        u,v = fitted(a)
        return float(alpha*(kl(p,u)+kl(q,v))+a*(r*kl(p,1-u)+(n-r)*kl(p,u)))
    lo,hi = 0.,1.
    while value(hi) < 1:
        hi *= 2
    for _ in range(90):
        mid = (lo+hi)/2
        if value(mid) < 1:
            lo = mid
        else:
            hi = mid
    a = (lo+hi)/2
    return {**shape, 'a':a, 'oracle_cost':n*a, 'fitted_levels':fitted(a),
            'root_residual':value(a)-1}


def finite_gamma(k, n, r, p, q, alpha, a):
    assert k >= r
    v = max(.5, (alpha*q+a*(r+(k-2*r)*p))/(alpha+k*a))
    return float(alpha*kl(q,v)+a*(r*kl(p,1-v)+(k-r)*kl(p,v)))
