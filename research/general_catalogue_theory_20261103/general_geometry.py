"""Decision-geometry checks, not an executable user-query policy.

True parameters are inputs for information-complexity analysis. No inference
service is used. Float optimization results are diagnostics, not certificates.
The previous committed inner KL solver is imported without editing it.
"""
from __future__ import annotations

import importlib.util
import itertools
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

OLD = Path(__file__).resolve().parents[1] / 'top1_decision_theory_20261103'
spec = importlib.util.spec_from_file_location('previous_decision_information', OLD/'decision_information.py')
previous = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
psi, kl = previous.psi, previous.kl


def mask_of(indices):
    return sum(1 << j for j in indices)


def minimal_wrong_flips(winners, state):
    """A state is a bit mask: bit j=1 means theta_j was flipped from +1."""
    wrong = [f for f in range(1, len(winners)) if winners[state ^ f] != winners[state]]
    return tuple(f for f in wrong if not any(s != f and s & f == s for s in wrong))


@dataclass(frozen=True)
class Catalogue:
    name: str
    offsets: tuple
    slopes: tuple

    @property
    def d(self):
        return len(self.slopes[0])

    def evaluate_cube(self):
        winners, gaps, scores = [], [], []
        for mask in range(1 << self.d):
            theta = [1-2*((mask >> j) & 1) for j in range(self.d)]
            values = [Fraction(b)+sum(Fraction(v)*x for v,x in zip(row,theta))
                      for b,row in zip(self.offsets,self.slopes)]
            order = sorted(range(len(values)), key=lambda i:values[i], reverse=True)
            assert values[order[0]] > values[order[1]], (self.name,mask,values)
            winners.append(order[0]); gaps.append(values[order[0]]-values[order[1]])
            scores.append(values)
        return tuple(winners), min(gaps), scores


WEIGHTED = Catalogue('unequal_weight_two_items', (0,-7),
                     ((0,0,0,0),(5,4,2,1)))
THREE = Catalogue('asymmetric_three_items', (0,0,-1),
                  ((0,0,0,0,0,0),(-6,-4,-4,-2,-2,0),(0,-2,-2,-4,-4,-8)))


def cover_lp(flips, d, allowed=None):
    allowed = tuple(range(d)) if allowed is None else tuple(allowed)
    rows = [[-float(bool((f >> j)&1)) for j in allowed]+[1.] for f in flips]
    fit = linprog([0.]*len(allowed)+[-1.], A_ub=rows, b_ub=np.zeros(len(rows)),
                  A_eq=[[1.]*len(allowed)+[0.]], b_eq=[1.],
                  bounds=[(0,None)]*(len(allowed)+1),method='highs')
    if not fit.success:
        raise RuntimeError(fit.message)
    weights=np.zeros(d); weights[list(allowed)]=fit.x[:-1]
    return float(fit.x[-1]),weights


def pooled_score(p, W, T):
    return 0. if W == 0 else W*psi(p,T/W)


def group_masses(w, groups, flip):
    groups=np.asarray(groups,dtype=int)
    W=np.bincount(groups,weights=w,minlength=max(groups)+1)
    T=np.bincount(groups,weights=np.asarray(w)*np.array([(flip>>j)&1 for j in range(len(w))]),
                  minlength=len(W))
    return W,T


def split_information(p, w, groups, flip, sorted_only=False):
    """Two pooled rate classes. Zero masses are omitted exactly, without a cutoff."""
    W,T=group_masses(w,groups,flip)
    active=[g for g in range(len(W)) if W[g] > 0]
    if sorted_only:
        order=sorted(active,key=lambda g:T[g]/W[g])
        subsets=[tuple(order[:k]) for k in range(len(order)+1)]
    else:
        subsets=[tuple(g for i,g in enumerate(active) if (s>>i)&1)
                 for s in range(1 << len(active))]
    best=None
    for subset in subsets:
        complement=[g for g in active if g not in subset]
        WA,TA=sum(W[g] for g in subset),sum(T[g] for g in subset)
        WB,TB=sum(W[g] for g in complement),sum(T[g] for g in complement)
        value=pooled_score(p,WA,TA)+pooled_score(p,WB,TB)
        if best is None or value < best['value']:
            best={'value':float(value),'subset':list(subset),'masses':[float(WA),float(WB)],
                  'flip_masses':[float(TA),float(TB)]}
    return best


class GeneralProgram(previous.DecisionProgram):
    """Reuse committed continuous inner/outer code with an arbitrary flip antichain."""
    def __init__(self, flips, groups, p=.8, q=.6, oracle=False):
        self.groups=np.asarray(groups,dtype=int)
        self.d,self.G=len(groups),max(groups)+1
        assert set(groups)==set(range(self.G)) and .5 <= q < p <= .99
        self.theta=(1,)*self.d
        self.p,self.q,self.alpha,self.oracle=p,q,0.,oracle
        self.flips=tuple(flips)
        assert self.flips and all(0 < f < (1<<self.d) for f in self.flips)
        assert all(not (a != b and a&b == a) for a,b in itertools.product(self.flips,repeat=2))
        self.alternatives=[(f,z) for f in self.flips
                           for z in (range(1) if oracle else range(1<<self.G))]
        self.nvars=2*self.d


def rows_and_pairs(k, short=False):
    pairs=tuple(mask_of((i,k+i)) for i in range(k))
    span=2 if short else k
    return pairs+(mask_of(range(span)),mask_of(range(k,k+span)))


def exact_cover_certificate(flips, weights, rho, dual):
    """Rational primal/dual evidence for rho; no float LP certificate claim."""
    d=len(weights)
    assert sum(weights)==1 and all(x>=0 for x in weights)
    masses=[sum(weights[j] for j in range(d) if (f>>j)&1) for f in flips]
    assert min(masses)==rho and sum(dual)==1 and all(x>=0 for x in dual)
    loads=[sum(l for f,l in zip(flips,dual) if (f>>j)&1) for j in range(d)]
    assert max(loads)==rho
    return {'rho':str(rho),'weights':[str(x) for x in weights],
            'dual':[str(x) for x in dual],'flip_masses':[str(x) for x in masses],
            'dual_column_loads':[str(x) for x in loads],
            'status':'EXACT_FRACTION_PRIMAL_DUAL'}
