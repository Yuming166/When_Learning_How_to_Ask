#!/usr/bin/env python3
"""Exact-rational interval certificate for the Gamma monotonicity counterexample.

No external packages, inference, sampling, or benchmark generation are used.
The decimal strings in the JSON are display approximations; every mathematical
assertion is checked using exact Fraction interval endpoints.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import comb
from pathlib import Path


def log_bounds(x, n=80):
    if x < 1:
        lo, hi = log_bounds(1 / x, n)
        return -hi, -lo
    z = (x - 1) / (x + 1)
    z2, power, lo = z * z, z, F(0)
    for j in range(n):
        lo += 2 * power / (2 * j + 1)
        power *= z2
    hi = lo + 2 * power / ((2 * n + 1) * (1 - z2))
    return lo, hi


def kl_bounds(P, Q):
    lo = hi = F(0)
    for p, q in zip(P, Q):
        a, b = log_bounds(p / q)
        lo += p * a
        hi += p * b
    return lo, hi


def display(x):
    with localcontext() as ctx:
        ctx.prec = 60
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def run():
    r, p, q = F(17, 20), F(39, 40), F(487, 500)

    def law(L, a):
        return [comb(L, i) * (r * a**i * (1-a)**(L-i)
                + (1-r) * (1-a)**i * a**(L-i))
                for i in range(L + 1)]

    bounds = {}
    for L in (1, 2, 3):
        P, Q = law(L, p), law(L, q)
        assert sum(P) == sum(Q) == 1
        bounds[L] = (kl_bounds(P, P[::-1]),
                     kl_bounds(P, Q), kl_bounds(P, Q[::-1]))
        assert bounds[L][0][0] > 0

    def gamma_bounds(L, k):
        A, U, V = bounds[L]
        return ((V[0] + (k-1)*U[0]) / A[1],
                (V[1] + (k-1)*U[1]) / A[0])

    decreasing = []
    for k in (1, 2):
        old, new = gamma_bounds(2, k), gamma_bounds(3, k)
        margin = old[0] - new[1]
        assert margin > 0
        decreasing.append({
            "group_size": k, "old_depth": 2, "new_depth": 3,
            "exact_rational_interval_comparison_passed": True,
            "old_gamma_bounds_display": list(map(display, old)),
            "new_gamma_bounds_display": list(map(display, new)),
            "positive_margin_lower_endpoint_display": display(margin),
        })

    choices = []
    for c, chosen in ((15, 2), (25, 3)):
        lower = bounds[chosen][0][0] / (c + chosen)
        competitors = []
        for L in (1, 2, 3):
            if L == chosen:
                continue
            margin = lower - bounds[L][0][1] / (c + L)
            assert margin > 0
            competitors.append({
                "depth": L,
                "exact_positive_margin_check_passed": True,
                "margin_lower_endpoint_display": display(margin),
            })
        choices.append({"source_cost": c, "unique_oracle_depth": chosen,
                        "competitor_comparisons": competitors})

    return {
        "status": "PASS_EXACT_RATIONAL_INTERVAL_CERTIFICATE",
        "parameters": {"r": str(r), "p": str(p), "q": str(q),
                       "ell": 1, "L_max": 3},
        "method": {"log_atanh_series_terms": 80,
                   "arithmetic": "exact fractions with proved geometric remainder",
                   "decimal_display_precision": 60,
                   "display_values_are_not_interval_assertions": True},
        "gamma_decreases": decreasing,
        "oracle_choices": choices,
        "scope": "Refutes monotonic Gamma in depth/cost; does not refute monotonic integer k_required or equality indicator.",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    result = run()
    path = Path(__file__).with_name("certified_counterexample.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "output": str(path)}))
