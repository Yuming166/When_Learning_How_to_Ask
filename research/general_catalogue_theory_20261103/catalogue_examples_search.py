"""Bounded, deterministic catalogue checks; CPU only, no inference or network.

This file checks three explicitly specified catalogues on their full sign cubes.
The cover witnesses are verified in exact rational arithmetic. Optional KL
program outputs reuse the prior decision-information solver and remain floating
diagnostics, not certified optimum intervals or stopping rules.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


TWO = [
    (0, 0, 0, 0, 0, 0),
    (0, 3, 2, 2, 1, 1),
]
TWO_UNSAT = [
    (0, 0, 0, 0, 0),
    (-7, 5, 4, 2, 1),
]
THREE = [
    (0, 0, 0, 0, 0, 0, 0),
    (0, -6, -4, -4, -2, -2, 0),
    (-1, 0, -2, -2, -4, -4, -8),
]


def subset(mask, d):
    return tuple(j + 1 for j in range(d) if mask >> j & 1)


def mask_of(indices):
    return sum(1 << (j - 1) for j in indices)


def evaluate_catalogue(rows):
    """Index sign vectors by their flipped coordinates relative to all +1."""
    d = len(rows[0]) - 1
    winners, utilities = [], []
    for mask in range(1 << d):
        theta = [-1 if mask >> j & 1 else 1 for j in range(d)]
        values = [r[0] + sum(v*t for v, t in zip(r[1:], theta)) for r in rows]
        assert values.count(max(values)) == 1, (mask, values)
        winners.append(values.index(max(values)))
        utilities.append(values)
    wrong = [m for m in range(1, 1 << d) if winners[m] != winners[0]]
    family = [m for m in wrong if not any(n != m and n & m == n for n in wrong)]
    relevance = []
    for j in range(d):
        witnesses = [m for m in range(1 << d) if winners[m] != winners[m ^ (1 << j)]]
        assert witnesses, j
        m = min(witnesses)
        relevance.append((j+1, subset(m, d), winners[m], winners[m ^ (1 << j)]))
    return d, winners, utilities, family, relevance


def exact_cover_check(d, family, w, dual):
    """Primal and dual feasible at equal value, with no float comparisons."""
    assert len(w) == d and len(dual) == len(family)
    assert sum(w) == sum(dual) == 1
    assert min(w) >= 0 and min(dual) >= 0
    covers = [sum(w[j] for j in range(d) if m >> j & 1) for m in family]
    loads = [sum(lam for m, lam in zip(family, dual) if m >> j & 1) for j in range(d)]
    assert min(covers) == max(loads)
    return min(covers), covers, loads


def floating_lp(d, family, support=None):
    if support is None:
        support = list(range(d))
    matrix = np.array([[int(m >> j & 1) for j in support] for m in family])
    fit = linprog([0]*len(support) + [-1],
                  A_ub=np.c_[-matrix, np.ones(len(family))],
                  b_ub=np.zeros(len(family)),
                  A_eq=[[1]*len(support) + [0]], b_eq=[1],
                  bounds=(0, None), method="highs")
    assert fit.success, fit.message
    return [str(Q(float(x)).limit_denominator(10000)) for x in fit.x]


def continuous_checks(results):
    source = Path(__file__).parents[1] / "top1_decision_theory_20261103" / "decision_information.py"
    spec = importlib.util.spec_from_file_location("decision_information", source)
    module = importlib.util.module_from_spec(spec)
    # dataclass resolves annotations through sys.modules.
    import sys
    sys.dont_write_bytecode = True
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for label, d, family, groups in [
        ("two_unsat_zero_123__4", 4, results["two_unsat"][3], [0, 0, 0, 1]),
        ("two_unsat_positive_12__34", 4, results["two_unsat"][3], [0, 0, 1, 1]),
        ("two_zero_12__345", 5, results["two"][3], [0, 0, 1, 1, 1]),
        ("two_positive_14__235", 5, results["two"][3], [0, 1, 1, 0, 1]),
        ("three_zero_all", 6, results["three"][3], [0]*6),
        ("three_positive_123__456", 6, results["three"][3], [0, 0, 0, 1, 1, 1]),
    ]:
        instance = module.DecisionProgram([1]*d, groups, 1, p=.8, q=.6, alpha=0.)
        instance.flips = family
        instance.alternatives = [(f, z) for f in family for z in range(1 << instance.G)]
        answer = instance.solve(tolerance=2e-9)
        residual = max(instance.independently_check_inner(
            np.array(answer["allocation"]), f, z) for f, z in instance.alternatives)
        print(label, answer)
        print("independent_inner_max_abs_error", residual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--continuous", action="store_true")
    args = parser.parse_args()
    results = {name: evaluate_catalogue(rows) for name, rows in [
        ("two_unsat", TWO_UNSAT), ("two", TWO), ("three", THREE)]}
    witnesses = {
        "two_unsat": ([Q(1,3), Q(1,3), Q(1,3), Q(0)], [Q(1,3)]*3),
        "two": ([Q(3,9), Q(2,9), Q(2,9), Q(1,9), Q(1,9)],
                [Q(1,9), Q(1,9), Q(2,9), Q(2,9), Q(1,3)]),
        "three": ([Q(3,13), Q(2,13), Q(2,13), Q(1,13), Q(1,13), Q(4,13)],
                  [Q(2,13), Q(2,13), Q(3,26), Q(3,26), Q(1,13), Q(0), Q(5,26), Q(5,26)]),
    }
    for name, (d, winners, utilities, family, relevance) in results.items():
        w, dual = witnesses[name]
        rho, covers, loads = exact_cover_check(d, family, w, dual)
        print(name, "winner_counts", [winners.count(k) for k in range(len(utilities[0]))])
        print("minimal_flips", [(subset(m, d), winners[m]) for m in family])
        print("rho", str(rho), "primal", list(map(str, w)), "dual", list(map(str, dual)))
        print("covers", list(map(str, covers)), "column_loads", list(map(str, loads)))
        print("LP_check", floating_lp(d, family))
        print("global_relevance_witnesses", relevance)
        if name == "three":
            active = [m for m, c in zip(family, covers) if c == rho]
            matrix = [[Q(int(m >> j & 1)) for j in range(d)] for m in active]
            # Seven tight equations determine all six weights: use exact elimination.
            augmented = [row + [rho] for row in matrix]
            pivot = 0
            for col in range(d):
                index = next(i for i in range(pivot, len(augmented)) if augmented[i][col])
                augmented[pivot], augmented[index] = augmented[index], augmented[pivot]
                value = augmented[pivot][col]
                augmented[pivot] = [x/value for x in augmented[pivot]]
                for i in range(len(augmented)):
                    if i != pivot:
                        multiple = augmented[i][col]
                        augmented[i] = [a-multiple*b for a,b in zip(augmented[i], augmented[pivot])]
                pivot += 1
            assert [row[-1] for row in augmented[:d]] == w
            print("exact_active_rank", pivot, "unique_oracle_weight", True)
    print("two_restricted_12", floating_lp(5, results["two"][3], [0,1]))
    print("two_restricted_345", floating_lp(5, results["two"][3], [2,3,4]))
    print("two_restricted_14", floating_lp(5, results["two"][3], [0,3]))
    print("two_restricted_235", floating_lp(5, results["two"][3], [1,2,4]))
    if args.continuous:
        continuous_checks(results)


if __name__ == "__main__":
    main()
