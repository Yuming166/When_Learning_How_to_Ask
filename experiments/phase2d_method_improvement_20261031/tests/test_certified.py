"""Deterministic arithmetic checks; no episodes, seeds, APIs, or model calls."""

from decimal import Context, Decimal, Inexact, ROUND_HALF_EVEN, Rounded, localcontext
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from phase2d.certified import _Intervals, _ordered_mle, certify_stop


def rational_log_bounds(value, terms=120):
    """Independent rational atanh series with a proven geometric tail bound."""
    value = Fraction(value)
    scale = 0
    while value < 1:
        value *= 2
        scale -= 1
    while value >= 2:
        value /= 2
        scale += 1

    def series(x):
        t = (x - 1) / (x + 1)
        total = sum((2 * t**(2 * k + 1) / (2 * k + 1) for k in range(terms)), Fraction())
        tail = 2 * t**(2 * terms + 1) / ((2 * terms + 1) * (1 - t * t))
        return total, total + tail

    lo, hi = series(value)
    two_lo, two_hi = series(Fraction(2))
    if scale >= 0:
        return lo + scale * two_lo, hi + scale * two_hi
    return lo + scale * two_hi, hi + scale * two_lo


def exact_profiles_by_grid(counts, membership, calibration, reports, accuracies, eta):
    """Independent integer-power likelihood maximization for tiny fixtures.

    Enumerate all fractions k/n up to total Bernoulli count, plus endpoints.
    This contains every unpooled/pooled empirical mean and clipping endpoint.
    No implementation MLE helper or logarithm is used to choose the maximum.
    """
    total = sum(sum(pair) for row in counts for pair in row) + 2 * len(calibration["high"])
    rates = {Fraction(1, 2), 1 - eta}
    rates.update(Fraction(k, n) for n in range(1, total + 1) for k in range(n + 1)
                 if Fraction(1, 2) <= Fraction(k, n) <= 1 - eta)
    pairs = [(p, q) for p in rates for q in rates if q <= p]
    result = {}
    for theta in product((0, 1), repeat=len(counts)):
        best = Fraction()
        for z in product((0, 1), repeat=len(reports)):
            for p, q in pairs:
                likelihood = Fraction(1)
                for j, row in enumerate(counts):
                    for fmt, pair in enumerate(row):
                        rate = p if fmt == z[membership[j]] else q
                        likelihood *= rate**pair[theta[j]] * (1 - rate)**pair[1 - theta[j]]
                for name, rate in (("high", p), ("low", q)):
                    for answer in calibration[name]:
                        likelihood *= rate if answer else 1 - rate
                for g, answers in enumerate(reports):
                    for answer in answers:
                        likelihood *= accuracies[g] if answer == z[g] else 1 - accuracies[g]
                best = max(best, likelihood)
        result[theta] = best
    return result


class TestCertifiedStopping(unittest.TestCase):
    def assert_encloses_rational_log(self, lower, upper, argument):
        reference_lo, reference_hi = rational_log_bounds(argument)
        self.assertLessEqual(Fraction(Decimal(lower)), reference_lo)
        self.assertGreaterEqual(Fraction(Decimal(upper)), reference_hi)

    def test_exact_mle_pooling_clipping_and_zero_weights(self):
        cases = [
            ((0, 0, 0, 0), (Fraction(1, 2), Fraction(1, 2))),
            ((0, 0, 3, 4), (Fraction(3, 4), Fraction(3, 4))),
            ((3, 4, 0, 0), (Fraction(3, 4), Fraction(1, 2))),
            ((1, 4, 3, 4), (Fraction(1, 2), Fraction(1, 2))),
            ((2, 3, 4, 5), (Fraction(3, 4), Fraction(3, 4))),
            ((9, 10, 1, 10), (Fraction(7, 8), Fraction(1, 2))),
        ]
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                self.assertEqual(_ordered_mle(*arguments, Fraction(1, 8)), expected)

    def test_low_count_profiles_against_independent_exact_integer_powers(self):
        for flat in product((0, 1), repeat=4):
            counts = [[list(flat[:2]), list(flat[2:])]]
            cal = {"high": [], "low": []}
            exact = exact_profiles_by_grid(counts, [0], cal, [[]], [Fraction(3, 4)], Fraction(1, 8))
            result = certify_stop(counts, [0], R=2, eta=.125, include_profiles=True)
            for profile in result["profiles"]:
                self.assert_encloses_rational_log(profile["loglik_lower"], profile["loglik_upper"],
                                                 exact[tuple(profile["theta"])])
            self.assertFalse(result["certified"])

    def test_joint_types_references_and_continuous_profile_independent_check(self):
        counts = [[[0, 2], [1, 0]], [[1, 0], [0, 1]]]
        cal = {"high": [1], "low": [0]}
        reports, accuracy = [[0, 1], [1]], [Fraction(3, 4), Fraction(4, 5)]
        result = certify_stop(counts, [[0], [1]], cal, reports, accuracy, R=3,
                              eta=Fraction(1, 8), include_profiles=True)
        exact = exact_profiles_by_grid(counts, [0, 1], cal, reports, accuracy, Fraction(1, 8))
        for profile in result["profiles"]:
            self.assert_encloses_rational_log(profile["loglik_lower"], profile["loglik_upper"],
                                             exact[tuple(profile["theta"])])
        # beta = R + log((M+1)^2 prod(n_jm+1) prod(k_g+1)).
        correction = 4 * 3 * 2 * 2 * 2 * 3 * 2
        beta_lo, beta_hi = rational_log_bounds(correction)
        self.assertLessEqual(Fraction(Decimal(result["beta_lower"])), 3 + beta_lo)
        self.assertGreaterEqual(Fraction(Decimal(result["beta_upper"])), 3 + beta_hi)

    def test_positive_negative_and_supplied_wrong_candidate(self):
        counts = [[[0, 100], [0, 0]]]
        positive = certify_stop(counts, [[0]], R=1, eta=.125)
        self.assertEqual(positive["status"], "certified")
        self.assertEqual(positive["theta"], [1])
        self.assertGreater(Decimal(positive["gap_lower"]), Decimal(positive["beta_upper"]))
        self.assertTrue(positive["interval_certified"])
        wrong = certify_stop(counts, [[0]], R=1, eta=.125, candidate_theta=[0])
        self.assertEqual(wrong["theta"], [0])
        self.assertEqual(wrong["status"], "rejected")
        self.assertLess(Decimal(wrong["gap_upper"]), 0)
        self.assertEqual(wrong["decision"], "continue_or_abstain")
        large_r = certify_stop(counts, [[0]], R=1024, eta=.125)
        self.assertEqual(large_r["status"], "rejected")
        json.dumps(positive, allow_nan=False)

    def test_ties_zero_observations_and_dimension_four(self):
        zero = [[[0, 0], [0, 0]] for _ in range(4)]
        result = certify_stop(zero, [[0], [1], [2], [3]], R=1, include_profiles=True)
        self.assertEqual(result["theta"], [0, 0, 0, 0])
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["joint_candidates"], 256)
        self.assertEqual(len(result["profiles"]), 16)
        self.assertEqual(Decimal(result["gap_lower"]), 0)
        counts = [[[0, 100], [0, 100]] for _ in range(4)]
        result = certify_stop(counts, [0, 1, 2, 3], R=1, eta=.125)
        self.assertEqual(result["theta"], [1, 1, 1, 1])
        self.assertEqual(result["status"], "certified")

    def test_binary_float_domain_endpoint_is_not_float_subtraction(self):
        result = certify_stop([[[0, 100], [0, 0]]], [[0]], R=1, eta=.05)
        exact_upper = 1 - Fraction.from_float(.05)
        self.assertNotEqual(exact_upper, Fraction.from_float(1 - .05))
        self.assertEqual(Fraction(result["exact_input_parameters"]["upper_rate"]), exact_upper)
        self.assertEqual(Fraction(result["lower_witness"]["p"]), exact_upper)
        decimal = certify_stop([[[0, 100], [0, 0]]], [[0]], R=1, eta=Decimal(".05"))
        self.assertEqual(Fraction(decimal["lower_witness"]["p"]), Fraction(19, 20))
        self.assertNotEqual(result["gap_lower"], decimal["gap_lower"])

    def test_log_intervals_against_exact_rational_series_and_widths(self):
        for argument in (Fraction(1), Fraction(7, 4), Fraction(1, 7),
                         Fraction(2, 3), Fraction(1, 2**100)):
            intervals = []
            for precision in (30, 60):
                lower, upper = _Intervals(precision).log(argument)
                self.assert_encloses_rational_log(str(lower), str(upper), argument)
                intervals.append((Fraction(lower), Fraction(upper)))
            self.assertLessEqual(intervals[0][0], intervals[1][0])
            self.assertGreaterEqual(intervals[0][1], intervals[1][1])
            if argument != 1:
                self.assertLess(intervals[1][1] - intervals[1][0],
                                (intervals[0][1] - intervals[0][0]) / 10**20)

    def test_undetermined_at_low_precision_then_resolved(self):
        context = Context(prec=100, rounding=ROUND_HALF_EVEN)
        gap = context.multiply(Decimal(100), context.ln(Decimal("1.75")))
        critical_r = context.subtract(gap, context.ln(Decimal(101)))
        # An exact rational input just above the true threshold, resolvable at 50 digits.
        risk = Fraction(critical_r) + Fraction(1, 10**40)
        low = certify_stop([[[0, 100], [0, 0]]], [[0]], R=risk, eta=.125, precisions=(16,))
        self.assertEqual(low["status"], "undetermined")
        self.assertFalse(low["certified"])
        resolved = certify_stop([[[0, 100], [0, 0]]], [[0]], R=risk, eta=.125,
                                precisions=(16, 50, 80))
        self.assertEqual(resolved["status"], "rejected")
        self.assertEqual([a["precision"] for a in resolved["precision_attempts"]], [16, 50])

    def test_independent_of_hostile_ambient_decimal_context(self):
        args = ([[[1, 20], [2, 15]]], [[0]])
        reference = certify_stop(*args, R=2, eta=Decimal(".05"))
        with localcontext() as ambient:
            ambient.prec, ambient.Emax, ambient.Emin = 2, 2, -2
            ambient.traps[Inexact] = ambient.traps[Rounded] = True
            actual = certify_stop(*args, R=2, eta=Decimal(".05"))
            self.assertEqual(ambient.prec, 2)
            self.assertFalse(any(ambient.flags.values()))
        for key in ("theta", "status", "gap_lower", "gap_upper", "beta_lower", "beta_upper"):
            self.assertEqual(actual[key], reference[key])

    def test_call_performs_no_import_or_file_access(self):
        with patch("builtins.open", side_effect=AssertionError("file access")), \
             patch("builtins.__import__", side_effect=AssertionError("late import")):
            result = certify_stop([[[0, 100], [0, 0]]], [[0]], R=1)
        self.assertTrue(result["certified"])

    def test_arithmetic_failure_is_fail_closed(self):
        with patch("phase2d.certified._Intervals.log", side_effect=OverflowError("fixture")):
            result = certify_stop([[[0, 100], [0, 0]]], [[0]], R=1)
        self.assertEqual(result["status"], "undetermined")
        self.assertEqual(result["reason"], "arithmetic_failure")
        self.assertFalse(result["certified"])
        self.assertIsNone(result["gap_lower"])

    def test_old_float_guard_false_acceptance_is_rejected(self):
        # Imports are read-only and happen before any confinement.
        from phase2d import bootstrap  # noqa: F401
        from phase2b.log_glr import log_glr
        import numpy as np
        n, risk = 1_000_000_000_152, 559615787992.8533
        counts = np.array([[[0, n], [0, 0]]], dtype=np.int64)
        old = log_glr(counts, [[0]], {"high": [], "low": []}, [[]], None, risk, eta=.125)
        self.assertTrue(old["certified"])
        self.assertGreater(old["gap"] - old["beta"], 1e-8 * (1 + math.log1p(n)))
        new = certify_stop(counts, [[0]], R=risk, eta=.125)
        self.assertEqual(new["status"], "rejected")
        self.assertLess(Decimal(new["gap_upper"]), Decimal(new["beta_lower"]))
        with localcontext() as context:
            context.prec = 150
            exact_gap = Decimal(n) * (Decimal(7) / Decimal(4)).ln()
            exact_beta = Decimal.from_float(risk) + Decimal(n + 1).ln()
        self.assertLessEqual(Decimal(new["gap_lower"]), exact_gap)
        self.assertGreaterEqual(Decimal(new["gap_upper"]), exact_gap)
        self.assertLessEqual(Decimal(new["beta_lower"]), exact_beta)
        self.assertGreaterEqual(Decimal(new["beta_upper"]), exact_beta)

    def test_validation_rejects_unsupported_or_malformed_inputs(self):
        base = dict(counts=[[[0, 1], [0, 0]]], groups=[[0]], R=1)
        invalid = [
            {"counts": []}, {"counts": [[[0, 1], [0, 0]]] * 5},
            {"counts": [[[0, 1, 2], [0, 0]]]}, {"counts": [[[0, -1], [0, 0]]]},
            {"counts": [[[0, 1.0], [0, 0]]]}, {"counts": [[[False, 1], [0, 0]]]},
            {"counts": [[[0, 2**50 + 1], [0, 0]]]}, {"groups": [[0], [0]]},
            {"groups": [1]}, {"groups": [[]]}, {"groups": []},
            {"calibration": {"high": [1], "low": []}}, {"calibration": {"high": []}},
            {"calibration": {"high": [2], "low": [1]}}, {"type_answers": [[1]]},
            {"type_answers": []}, {"type_accuracy": [.5]}, {"type_accuracy": [1.]},
            {"type_accuracy": [float("nan")]}, {"R": 0}, {"R": -1}, {"R": float("inf")},
            {"R": float("nan")}, {"R": "1"}, {"R": Decimal("1e10000")},
            {"R": Fraction(1, 2**5000)}, {"eta": 0}, {"eta": .5},
            {"eta": float("nan")}, {"candidate_theta": [2]}, {"candidate_theta": []},
            {"precisions": ()}, {"precisions": (15,)}, {"precisions": (513,)},
            {"precisions": (80, 50)}, {"precisions": (50, 50)},
        ]
        for change in invalid:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    certify_stop(**(base | change))


if __name__ == "__main__":
    unittest.main()
