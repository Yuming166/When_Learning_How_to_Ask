#!/usr/bin/env python3
"""Reconstruct the sealed theory receipt using exact, offline enumeration.

Run from any directory:
    python3 /path/to/verify_theory_certificates.py

Only the verification receipt is written. The pre-existing theory certificate,
protocol, benchmark grids, and all other experiment files are read-only.
Requires only Python's standard library.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def majority_accuracy(n, p):
    return sum(
        (F(1) if 2 * k > n else F(1, 2) if 2 * k == n else F(0))
        * comb(n, k) * p ** k * (1 - p) ** (n - k)
        for k in range(n + 1)
    )


def enumerate_law(r, a, n, fresh):
    """Enumerate latent theta/B/E states, not the majority-vote formula."""
    law = defaultdict(lambda: [F(0), F(0)])
    for ti, theta in enumerate((-1, 1)):
        for bs in product((-1, 1), repeat=n if fresh else 1):
            pb = F(1, 2)
            for b in bs:
                pb *= r if b == 1 else 1 - r
            for es in product((-1, 1), repeat=n):
                prob = pb
                for e in es:
                    prob *= a if e == 1 else 1 - a
                ys = tuple(
                    theta * (bs[i] if fresh else bs[0]) * es[i]
                    for i in range(n)
                )
                law[ys][ti] += prob
    require(sum(sum(v) for v in law.values()) == 1, "law not normalized")
    return dict(law)


def risk(law):
    return sum(min(v) for v in law.values())


def reconstruct():
    # This is the original auxiliary rational-check grid, not PROTOCOL's
    # performance grid. Changing it would fail exact receipt reconstruction.
    rs = [F(1, 2), F(2, 3), F(3, 4), F(5, 6), F(1)]
    aa = [F(1, 2), F(3, 4), F(4, 5), F(9, 10), F(1)]
    checked = factor_checks = normalization_checks = 0
    boundary_checks = parity_checks = posterior_checks = 0

    for r, a, n in product(rs, aa, range(6)):
        t = r * a + (1 - r) * (1 - a)
        rep = enumerate_law(r, a, n, fresh=False)
        fresh = enumerate_law(r, a, n, fresh=True)
        normalization_checks += 2
        rr, rf = risk(rep), risk(fresh)
        require(rr == r - (2 * r - 1) * majority_accuracy(n, a),
                f"repeat formula mismatch: {(r, a, n)}")
        require(rf == 1 - majority_accuracy(n, t),
                f"fresh formula mismatch: {(r, a, n)}")

        if n == 3:
            x, y = 2 * r - 1, 2 * a - 1
            require(rr - rf == x * (1 - x * x) * y ** 3 / 4,
                    "three-read factorization mismatch")
            factor_checks += 1
        if n in (2, 4):
            require(majority_accuracy(n, a) == majority_accuracy(n - 1, a),
                    "even-parity identity mismatch")
            parity_checks += 1
        if n == 0 or r == F(1, 2) or a == F(1, 2):
            require(rr == rf == F(1, 2), "chance/no-data boundary mismatch")
            boundary_checks += 1
        if r == 1:
            require(rep == fresh, "perfect-root joint laws differ")
            require(rr == 1 - majority_accuracy(n, a),
                    "perfect-root risk mismatch")
            boundary_checks += 1
        if a == 1 and n >= 1:
            require(rr == 1 - r, "perfect-reading repeat mismatch")
            require(rf == 1 - majority_accuracy(n, r),
                    "perfect-reading fresh mismatch")
            boundary_checks += 1
        if r == a == 1 and n >= 1:
            require(rr == rf == 0, "doubly perfect boundary mismatch")
            boundary_checks += 1

        for pair in rep.values():
            mass = sum(pair)
            if mass:
                posterior = pair[1] / mass
                require(1 - r <= posterior <= r,
                        "single-root posterior exceeds reliability ceiling")
                posterior_checks += 1
        checked += 1

    require(checked == 150 and normalization_checks == 300,
            "original enumeration grid changed")
    require(factor_checks == 25, "original factor grid changed")

    # Analytic rectangle certificate: f(z)=z-z^3 is concave on these
    # positive intervals, since f''(z)=-6z<0. Its minimum is at an endpoint.
    xl, xu, yl, yu = F(1, 3), F(2, 3), F(1, 2), F(4, 5)
    require(0 < xl <= xu < 1 and 0 < yl <= yu < 1,
            "nondegenerate rectangle invalid")
    require(-6 * xl < 0 and -6 * yl < 0, "concavity condition fails")
    f = lambda z: z * (1 - z * z)
    rect_gap = min(f(xl), f(xu)) * yl ** 3 / 4
    rect_reverse = xl * min(f(yl), f(yu)) / 4
    require(rect_gap == F(1, 108), "rectangle fresh-gap mismatch")
    require(rect_reverse == F(3, 125), "rectangle repeat-gap mismatch")

    # Exact sparse polynomial coefficient check:
    # M3(xy)/2 - x*M3(y)/2, M3(z)=(3z-z^3)/2.
    polynomial = defaultdict(F)
    for power, coefficient in [(1, F(3, 4)), (3, F(-1, 4))]:
        polynomial[(power, power)] += coefficient
        polynomial[(1, power)] -= coefficient
    polynomial = {key: value for key, value in polynomial.items() if value}
    require(polynomial == {(1, 3): F(1, 4), (3, 3): F(-1, 4)},
            "symbolic n=3 polynomial coefficients mismatch")

    r, a = F(3, 4), F(4, 5)
    t = r * a + (1 - r) * (1 - a)
    x, y = 2 * r - 1, 2 * a - 1
    rr = r - x * majority_accuracy(3, a)
    rf = 1 - majority_accuracy(3, t)
    true = (r * a ** 5 + (1 - r) * (1 - a) ** 5) / (
        a ** 5 + (1 - a) ** 5)
    wrong = t ** 5 / (t ** 5 + (1 - t) ** 5)
    agree = a ** 5 + (1 - a) ** 5
    require(true == F(3073, 4100), "true posterior example mismatch")
    require(wrong == F(371293, 388100), "URL-iid posterior example mismatch")
    require(agree == F(41, 125), "agreement probability example mismatch")
    require(wrong > F(19, 20) and true < F(3, 4),
            "confidence counterexample no longer holds")
    wrong_n4 = t ** 4 / (t ** 4 + (1 - t) ** 4)
    require(wrong_n4 < F(19, 20), "n=5 no longer first 95% all-agree crossing")

    # Independently recover the true example directly from enumerated mass.
    law5 = enumerate_law(r, a, 5, fresh=False)
    positive = law5[(1, 1, 1, 1, 1)]
    negative = law5[(-1, -1, -1, -1, -1)]
    require(positive[1] / sum(positive) == true,
            "enumerated conditional posterior mismatch")
    require(sum(positive) + sum(negative) == agree,
            "enumerated all-agree probability mismatch")

    cost_rows = []
    for c in [F(0), F(1, 4), F(1, 3), F(1, 2), F(1)]:
        nr = int((F(4) - c) // 1)
        nf = int(F(4) // (1 + c))
        rep_risk = r - x * majority_accuracy(nr, a)
        fresh_risk = 1 - majority_accuracy(nf, t)
        require((fresh_risk < rep_risk) == (c <= F(1, 3)),
                "fixed-budget cost reversal mismatch")
        cost_rows.append({
            "c": str(c), "repeat_reads": nr, "fresh_roots": nf,
            "R_repeat": str(rep_risk), "R_fresh": str(fresh_risk),
        })

    certificate = {
        "certificate_id": "W2a-theory-exact-rational-v1",
        "method": "Exact Fraction enumeration over theta, every root B, every read E; Bayes risk is sum_y min(P(theta=-1,y),P(theta=+1,y)). No Monte Carlo.",
        "enumerated_grid": {
            "r": [str(v) for v in rs], "a": [str(v) for v in aa],
            "n": list(range(6)), "configurations": checked,
            "laws_per_configuration": 2,
            "law_probability_normalization_checks": normalization_checks,
        },
        "closed_form_crosschecks": "PASS: all repeated-root and fresh-root formulas match fully enumerated latent-state laws exactly",
        "n3_factorization": "R_repeat-R_fresh = x*(1-x*x)*y**3/4, x=2*r-1,y=2*a-1",
        "n3_factorization_grid_checks": factor_checks,
        "rectangle": {
            "r": ["2/3", "5/6"], "a": ["3/4", "9/10"],
            "same_read_uniform_risk_gap_lower_bound": str(rect_gap),
            "fixed_budget_high_activation_repeat_gap_lower_bound": str(rect_reverse),
            "proof": "Concavity endpoint minima, established analytically in THEORY_RESULTS.md; grid checks are not the proof.",
        },
        "numeric_example": {
            "r": str(r), "a": str(a), "t": str(t),
            "repeat_3_risk": str(rr), "fresh_3_risk": str(rf),
            "risk_gap": str(rr - rf),
            "true_posterior_all_plus_n5": str(true),
            "URL_iid_posterior_all_plus_n5": str(wrong),
            "all_same_sign_probability_n5": str(agree),
        },
        "fixed_budget_example": {
            "B": "4", "ell": "1", "r": str(r), "a": str(a),
            "rows": cost_rows,
        },
        "scope": {
            "network_calls": 0, "model_service_calls": 0,
            "human_signoffs": 0, "simulation_parameters_known": True,
            "natural_web_claim": False,
        },
        "verification_status": "ALL_ASSERTIONS_PASSED",
    }
    additional = {
        "boundary_checks": boundary_checks,
        "even_parity_checks": parity_checks,
        "nonzero_outcome_posterior_ceiling_checks": posterior_checks,
        "additional_exact_laws_for_counterexample": 1,
        "symbolic_n3_coefficients": {
            "x*y^3": "1/4", "x^3*y^3": "-1/4",
        },
        "rectangle_proof_checks": "Exact endpoint values and positive-interval concavity; see the analytic interval proof in THEORY_RESULTS.md.",
        "fixed_budget_threshold": "c<=ell/3 versus ell/3<c<=ell, B=4*ell; five original rational points also verified.",
    }
    return certificate, additional


def main():
    experiment_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=experiment_dir / "theory_certificates.json")
    parser.add_argument("--receipt", type=Path,
                        default=experiment_dir / "theory_verification.json")
    args = parser.parse_args()
    require(args.receipt.resolve() != args.certificate.resolve(),
            "receipt must not overwrite the original certificate")
    certificate_bytes = args.certificate.read_bytes()
    existing = json.loads(certificate_bytes)
    rebuilt, additional = reconstruct()
    require(existing == rebuilt,
            "Reconstructed certificate differs from existing JSON; no certificate was changed")
    receipt = {
        "verification_id": "W2a-theory-reconstruction-v1",
        "status": "PASS",
        "comparison": "Full parsed JSON equality; every original field independently reconstructed",
        "original_certificate_sha256": sha256(certificate_bytes).hexdigest(),
        "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "base_laws_normalized": rebuilt["enumerated_grid"]["law_probability_normalization_checks"],
        "base_risk_formulas_crosschecked": 300,
        "n3_factorization_points": rebuilt["n3_factorization_grid_checks"],
        "additional_checks": additional,
        "original_certificate_unchanged": (
            args.certificate.read_bytes() == certificate_bytes),
        "arithmetic": "fractions.Fraction, exact",
        "network_calls": 0,
        "model_service_calls": 0,
    }
    require(receipt["original_certificate_unchanged"],
            "original certificate changed during verification")
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
