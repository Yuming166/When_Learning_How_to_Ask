"""Bounded deterministic proof checks; no worlds, seeds, APIs, or experiments.

Run from any directory with Python. The historical modules are imported read-only.
The high-precision calculation is a counterexample to a globally conservative
floating GLR crossing/guard, not a counterexample to the exact anytime theorem.
"""

from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import json
import math
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/phase2b_alignment_20261031"))
from phase2b import bootstrap  # noqa: E402,F401
from phase2b.aligned import TheoryAlignedTracking, ordered_grid_projection  # noqa: E402
from phase2b.log_glr import log_glr  # noqa: E402


def forced_prefix_checks():
    checks = 0
    for streams in (2, 4, 8, 16):
        counts = [0] * streams
        for t in range(4097):
            lower = math.isqrt(t // streams)
            assert all(lower <= n <= lower + 1 for n in counts)
            assert sum(counts) <= math.sqrt(streams * t) + streams
            checks += 1
            index = TheoryAlignedTracking._forced_index(SimpleNamespace(t=t, L=streams))
            if index is not None:
                counts[index] += 1
    return checks


def exact_tracking_checks():
    """Adversarially switching simplex targets, calculated with rational numbers."""
    checked = 0
    for actions in (2, 3, 5):
        for mode in range(3):
            cumulative = [Fraction(0)] * actions
            actual = [0] * actions
            forced_total = 0
            for t in range(512):
                if mode == 0:
                    target = (t // 7) % actions
                    weights = [Fraction(int(e == target)) for e in range(actions)]
                elif mode == 1:
                    # Choose a target already oversampled to stress deficit tracking.
                    target = max(range(actions), key=lambda e: actual[e] - cumulative[e])
                    weights = [Fraction(int(e == target)) for e in range(actions)]
                else:
                    denominator = actions * (actions + 1) // 2
                    weights = [Fraction(1 + (e + t) % actions, denominator) for e in range(actions)]
                cumulative = [c + w for c, w in zip(cumulative, weights)]
                forced = TheoryAlignedTracking._forced_index(SimpleNamespace(t=t, L=actions))
                if forced is None:
                    selected = max(range(actions), key=lambda e: cumulative[e] - actual[e])
                else:
                    selected = forced
                    forced_total += 1
                actual[selected] += 1
                discrepancy = [n - c for n, c in zip(actual, cumulative)]
                bound = 1 + forced_total
                assert sum(discrepancy) == 0
                assert max(discrepancy) <= bound
                assert min(discrepancy) >= -(actions - 1) * bound
                assert sum(abs(a) for a in discrepancy) <= 2 * (actions - 1) * bound
                checked += 1
    return checked


def projection_boundary_checks():
    checked = 0
    for eta in (.05, .125):
        for t in (0, 1, 8, 100, 10000, 1000000):
            for p, q in ((.5, .5), (1 - eta, .5), (.8, .6), (.3, .9)):
                result = ordered_grid_projection(p, q, t, eta)
                assert .5 <= result["q"] < result["p"] <= 1 - eta
                checked += 1
    return checked


def floating_glr_guard_counterexample():
    # eta=1/8 is exactly representable, avoiding an ambiguous decimal-domain
    # endpoint. The exact best likelihood is (7/8)^n, and the best opposite-sign
    # likelihood is (1/2)^n. The second format and reference streams are empty.
    n = 1_000_000_000_152
    r = 559615787992.8533
    counts = np.zeros((1, 2, 2), dtype=np.int64)
    counts[0, 0, 1] = n
    fit = log_glr(counts, [[0]], {"high": [], "low": []}, [[]], None, r, eta=.125)
    guard = 1e-8 * (1 + math.log1p(n))
    with localcontext() as context:
        context.prec = 100
        exact_gap = Decimal(n) * (Decimal(7) / Decimal(4)).ln()
        exact_beta = Decimal.from_float(r) + Decimal(n + 1).ln()
        exact_residual = exact_gap - exact_beta
        assert exact_residual < 0
        exact_residual_string = str(exact_residual)
    floating_residual = fit["gap"] - fit["beta"]
    assert n < 2**50
    assert fit["certified"] and floating_residual > guard
    assert not fit["interval_certified"]
    return {
        "n": n, "R_float": r, "eta": .125,
        "floating_gap_minus_beta": floating_residual,
        "policy_guard": guard,
        "high_precision_gap_minus_beta": exact_residual_string,
        "scope": "static count array, outside development scale; no risk violation inferred",
    }


def main():
    start = time.perf_counter()
    result = {
        "forced_prefix_checks": forced_prefix_checks(),
        "rational_tracking_checks": exact_tracking_checks(),
        "ordered_projection_domain_checks": projection_boundary_checks(),
        "floating_glr_guard_counterexample": floating_glr_guard_counterexample(),
        "episodes": 0, "online_actions": 0, "offline_observations": 0,
        "random_seeds_consumed": 0, "optimization_calls": 0,
    }
    result["wall_seconds"] = time.perf_counter() - start
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
