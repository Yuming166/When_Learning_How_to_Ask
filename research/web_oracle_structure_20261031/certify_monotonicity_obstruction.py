#!/usr/bin/env python3
"""Certify failure of a proposed coordinatewise-KL monotonicity lemma.

This does not refute pure-good oracle optimality. Exact rational intervals are
used for all signs; no optimization, sampling, or model inference is performed.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def log_bounds(x, n=100):
    if x < 1:
        lo, hi = log_bounds(1/x, n)
        return -hi, -lo
    z = (x-1)/(x+1)
    power, lo = z, F(0)
    for j in range(n):
        lo += 2*power/(2*j+1)
        power *= z*z
    return lo, lo + 2*power/((2*n+1)*(1-z*z))


def law(r, a, negative=False):
    w = 1-r if negative else r
    values = []
    for yy in product((0, 1), repeat=len(a)):
        f = g = F(1)
        for ai, yi in zip(a, yy):
            f *= ai if yi else 1-ai
            g *= 1-ai if yi else ai
        values.append(w*f+(1-w)*g)
    assert sum(values) == 1
    return values


def weighted_logs(weights, P, Q):
    lo = hi = F(0)
    for weight, p, q in zip(weights, P, Q):
        left, right = log_bounds(p/q)
        if weight >= 0:
            lo += weight*left
            hi += weight*right
        else:
            lo += weight*right
            hi += weight*left
    return lo, hi


def add(a, b, multiplier=1):
    assert multiplier >= 0
    return a[0]+multiplier*b[0], a[1]+multiplier*b[1]


def display(x):
    with localcontext() as ctx:
        ctx.prec = 50
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def run():
    r = F(19, 20)
    a = [F(13, 20), F(33, 40)]
    # A strict ordered alternative; the original closed-boundary example was
    # b=(.65,.65). This perturbation keeps the counterexample in u>v.
    b = [F(13, 20), F(13, 20)+F(1, 10**9)]
    assert all(x >= y >= F(1, 2) for x, y in zip(a, b))
    P = law(r, a)
    DP = [x-y for x, y in zip(law(r, [1, a[1]]), law(r, [0, a[1]]))]
    assert sum(DP) == 0
    same = weighted_logs(DP, P, law(r, b))
    opposite = weighted_logs(DP, P, law(r, b, True))
    d = 2000
    total = add(opposite, same, d-1)
    assert same[1] < 0
    assert total[1] < 0

    step = F(1, 10**6)
    Pnext = law(r, [a[0]+step, a[1]])
    previous = add(weighted_logs(P, P, law(r, b, True)),
                   weighted_logs(P, P, law(r, b)), d-1)
    following = add(weighted_logs(Pnext, Pnext, law(r, b, True)),
                    weighted_logs(Pnext, Pnext, law(r, b)), d-1)
    decrease = previous[0]-following[1]
    assert decrease > 0
    return {
        "status": "PASS_EXACT_RATIONAL_INTERVAL_CERTIFICATE",
        "r": str(r), "true_coordinate_accuracies": list(map(str, a)),
        "alternative_coordinate_accuracies": list(map(str, b)),
        "all_true_coordinates_at_least_alternative_coordinates": True,
        "alternative_good_rate_strictly_above_bad_rate": True,
        "derivative_same_truth_display_bounds": list(map(display, same)),
        "derivative_opposite_truth_display_bounds": list(map(display, opposite)),
        "F_d": d, "F_derivative_display_bounds": list(map(display, total)),
        "finite_coordinate_increase": str(step),
        "F_strict_decrease_lower_endpoint_display": display(decrease),
        "claim_limit": "Refutes coordinatewise monotonicity of same-truth KL and F_d; does not refute replacing a complete mixed block by a pure-good block, or pure-good oracle optimality.",
        "arithmetic": "Exact Fraction logarithm intervals, 100 atanh terms and proved geometric tail; decimal strings display endpoints only.",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("MONOTONICITY_OBSTRUCTION_CERTIFICATE.json")
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "output": str(output)}))
