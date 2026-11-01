#!/usr/bin/env python3
"""Exact-rational checks for the alpha=0, L_max=1 singleton counterexample.

The unknown-rate equality is proved analytically in ORACLE_AND_THRESHOLD_AUDIT.md.
This script certifies the strict known-level Gamma comparison and encloses costs.
No optimizer, random sampling, inference, or external package is used.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


def log_bounds(x, n=100):
    if x < 1:
        lo, hi = log_bounds(1 / x, n)
        return -hi, -lo
    z = (x - 1) / (x + 1)
    power, lo = z, F(0)
    for j in range(n):
        lo += 2 * power / (2*j + 1)
        power *= z*z
    return lo, lo + 2*power / ((2*n + 1)*(1-z*z))


def kl_bounds(p, q):
    lo = hi = F(0)
    for a, b in ((p, q), (1-p, 1-q)):
        x, y = log_bounds(a / b)
        lo += a*x
        hi += a*y
    return lo, hi


def display(x):
    with localcontext() as ctx:
        ctx.prec = 60
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def run():
    r, p, q, eta = F(4, 5), F(4, 5), F(3, 5), F(1, 10)
    rho = lambda a: F(1, 2) + (2*r-1)*(a-F(1, 2))
    s, t = rho(p), rho(q)
    assert F(1, 2) <= q < p <= 1-eta
    assert F(1, 2) < t < s < 1
    Bp, Bq = kl_bounds(s, F(1, 2)), kl_bounds(t, F(1, 2))
    A, V = kl_bounds(s, 1-s), kl_bounds(s, 1-t)
    assert Bp[0] > Bq[1] >= 0
    assert V[1] < A[0]
    unknown_cost = (1/Bp[1], 1/Bp[0])
    known_oracle_cost = (1/A[1], 1/A[0])
    gamma = (V[0]/A[1], V[1]/A[0])
    return {
        "status": "PASS_EXACT_RATIONAL_INTERVAL_CERTIFICATE",
        "parameters": {"r": str(r), "p": str(p), "q": str(q),
                       "eta": str(eta), "d": 1, "L_max": 1,
                       "alpha": 0, "c": 0, "ell": 1},
        "effective_accuracy": {"good": str(s), "bad": str(t)},
        "exact_assertions": {"Bp_strictly_greater_than_Bq": True,
                             "known_level_Gamma_strictly_below_one": True},
        "display_only_decimal_bounds": {
            "Bp": list(map(display, Bp)),
            "unknown_learner_and_oracle_common_coefficient": list(map(display, unknown_cost)),
            "known_rate_oracle_coefficient": list(map(display, known_oracle_cost)),
            "known_level_Gamma": list(map(display, gamma)),
        },
        "analytic_equality_argument": (
            "Every wrong-truth response mean is at most 1/2; the alternative "
            "closure point u=v=1/2 attains both stream KL minima. Learner and "
            "unknown-rate oracle therefore share the constraint x_good*Bp + "
            "x_bad*Bq >= 1, uniquely minimized by x_good=1/Bp, x_bad=0."
        ),
        "arithmetic": "Exact Fraction intervals for a 100-term log atanh series with proved tail bound; decimal values only display the endpoints.",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    result = run()
    output = Path(__file__).with_name("singleton_threshold_certificate.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "output": str(output)}))
