"""CPU-only analytic/independent numerical checks; no sampled model calls.

Run from the repository root with:
  python -m unittest discover -s experiments/recommendation_loop_20261103 -p test_likelihood_gate.py -v
"""

from __future__ import annotations

import copy
from decimal import Decimal, localcontext, ROUND_UP
from fractions import Fraction
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.optimize import minimize

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification
from certification import CertifiedDecisionGate
from likelihood import JointLikelihood, MAX_TOTAL_OBSERVATIONS


def public(d=2, groups=None, eta="1/100", singleton=False):
    if groups is None:
        groups = [0] * d
    if singleton:
        slopes = [[1 - 2 * ((mask >> j) & 1) for j in range(d)] for mask in range(2**d)]
        offsets = [0] * len(slopes)
    else:
        # OR: item 1 iff at least one theta coordinate is positive.
        slopes, offsets = [[0] * d, [1] * d], [0, d - 1]
    return {"d": d, "groups": groups, "eta": eta,
            "catalogue": {"offsets": offsets, "slopes": slopes}}


def independent_inner_max(counts, groups, theta_mask, z_mask, upper):
    """Numerically optimize raw-answer likelihood; do not call production stats."""
    d = len(groups)
    positive = counts[:, :, 1].astype(float)
    negative = counts[:, :, 0].astype(float)
    correct_positive = np.array([((theta_mask >> j) & 1) == 0 for j in range(d)])[:, None]
    high = np.array([[fmt == ((z_mask >> groups[j]) & 1) for fmt in range(2)] for j in range(d)])
    total = max(1., float(counts.sum()))

    def objective(rates):
        accuracy = np.where(high, rates[0], rates[1])
        prob_positive = np.where(correct_positive, accuracy, 1 - accuracy)
        return -float((positive * np.log(prob_positive)
                       + negative * np.log1p(-prob_positive)).sum()) / total

    results = [minimize(objective, initial, method="SLSQP",
                        bounds=[(.5, upper), (.5, upper)],
                        constraints=[{"type": "ineq", "fun": lambda x: x[0] - x[1]}],
                        options={"ftol": 1e-13, "maxiter": 150})
               for initial in ((.75, .55), (.75, .75))]
    feasible = [r for r in results if r.success and r.x[0] >= r.x[1] - 1e-9]
    if not feasible:
        raise AssertionError(f"independent SciPy optimization failed: {results}")
    return -min(r.fun for r in feasible) * total


class LikelihoodAndGateTests(unittest.TestCase):
    def test_literal_raw_bit_orientation_and_type_masks(self):
        model = JointLikelihood(public(2, [0, 1], singleton=True))
        counts = np.zeros((2, 2, 2), dtype=np.int64)
        theta_mask, z_mask = 2, 1
        for j in range(2):
            for fmt in range(2):
                correct = 80 if fmt == ((z_mask >> j) & 1) else 60
                correct_raw = 1 - ((theta_mask >> j) & 1)
                counts[j, fmt, correct_raw] = correct
                counts[j, fmt, 1 - correct_raw] = 100 - correct
        estimate = model.estimate(counts)
        self.assertEqual(estimate["theta_mask"], theta_mask)
        self.assertEqual(estimate["z_mask"], z_mask)
        self.assertAlmostEqual(estimate["p"], .8)
        self.assertAlmostEqual(estimate["q"], .6)
        self.assertEqual(estimate["item"], theta_mask)
        np.testing.assert_array_equal(model.theta_signs[0], [1, 1])
        np.testing.assert_array_equal(model.theta_signs[2], [1, -1])

    def test_all_inner_maxima_against_independent_scipy_through_d6(self):
        rng = np.random.default_rng(20261103)
        compared = 0
        cases = [(1, [0]), (2, [0, 1]), (4, [0, 1, 0, 1]), (6, [0, 0, 0, 1, 1, 1])]
        for d, groups in cases:
            counts = rng.integers(0, 10, size=(d, 2, 2), dtype=np.int64)
            model = JointLikelihood(public(d, groups))
            table = model.best_table(counts)
            for theta in range(2**d):
                for z in range(2**len(set(groups))):
                    expected = independent_inner_max(counts, groups, theta, z, .99)
                    self.assertAlmostEqual(table["loglik"][theta, z], expected, delta=3e-8)
                    self.assertGreaterEqual(table["p"][theta, z], table["q"][theta, z])
                    compared += 1
        self.assertEqual(compared, 340)

    def test_inner_mle_order_pooling_clipping_and_zero_weights(self):
        model = JointLikelihood(public(1))
        cases = [np.array([[[80, 20], [10, 90]]]),
                 np.array([[[0, 100], [0, 0]]]),
                 np.zeros((1, 2, 2), dtype=int)]
        for counts in cases:
            table = model.best_table(counts)
            for theta in range(2):
                for z in range(2):
                    expected = independent_inner_max(counts, [0], theta, z, .99)
                    self.assertAlmostEqual(table["loglik"][theta, z], expected, delta=3e-8)
        first = model.best_table(cases[0])
        self.assertAlmostEqual(first["p"][0, 0], .55)
        self.assertAlmostEqual(first["q"][0, 0], .55)
        clipped = model.best_table(cases[1])
        self.assertAlmostEqual(clipped["p"][0, 0], .99)
        self.assertAlmostEqual(clipped["q"][0, 0], .5)

    def test_singleton_classes_match_historical_d4_sign_gate(self):
        rng = np.random.default_rng(31991)
        status_map = {"certified": "CERTIFIED", "rejected": "NOT_CERTIFIED", "undetermined": "UNDETERMINED"}
        for d in range(1, 5):
            groups = [j % min(2, d) for j in range(d)]
            conf = public(d, groups, singleton=True)
            for case in range(4):
                counts = rng.integers(0, 20, size=(d, 2, 2), dtype=np.int64)
                if case == 3:
                    counts[:] = 0
                    counts[:, 0, 1] = 150
                candidate = JointLikelihood(conf).estimate(counts)["item"]
                new = CertifiedDecisionGate(conf).check(counts, candidate)
                raw_truth_bits = [1 - ((candidate >> j) & 1) for j in range(d)]
                old = certification._ARITHMETIC.certify_stop(
                    counts, groups, R=3, eta=Fraction(1, 100), candidate_theta=raw_truth_bits)
                self.assertEqual(new["status"], status_map[old["status"]])
                for new_key, old_key in (("gap_lower", "gap_lower"), ("gap_upper", "gap_upper"),
                                         ("threshold_lower", "beta_lower"), ("threshold_upper", "beta_upper")):
                    self.assertLess(abs(Decimal(new[new_key]) - Decimal(old[old_key])), Decimal("1e-40"))

    def test_possible_history_or_witness_excludes_same_item_profiles(self):
        conf = public(2, eta="1/20")
        counts = np.zeros((2, 2, 2), dtype=np.int64)
        counts[0, 0, 1] = 20
        model = JointLikelihood(conf)
        gap = model.decision_gap(counts)
        profile = model.best_table(counts)["loglik"].max(axis=1)
        # theta masks 0 and 2 differ only in the unobserved second coordinate.
        self.assertEqual(profile[0], profile[2])
        self.assertEqual(model.winner_by_theta[0], model.winner_by_theta[2])
        self.assertEqual(profile[0] - max(profile[1:]), 0.)
        self.assertAlmostEqual(gap["gap"], 20 * math.log(1.9))
        self.assertFalse(gap["certified"])
        result = CertifiedDecisionGate(conf).check(counts)
        self.assertEqual(result["status"], "CERTIFIED")
        self.assertEqual(result["item"], 1)
        self.assertEqual(result["lower_witness"]["p"], "19/20")
        self.assertGreater(Decimal(result["gap_lower"]), Decimal(result["threshold_upper"]))
        with localcontext() as ctx:
            ctx.prec = 90
            exact_gap = 20 * (Decimal(19) / Decimal(10)).ln()
            exact_beta = 3 + Decimal(21).ln()
        self.assertLessEqual(Decimal(result["gap_lower"]), exact_gap)
        self.assertGreaterEqual(Decimal(result["gap_upper"]), exact_gap)
        self.assertLessEqual(Decimal(result["threshold_lower"]), exact_beta)
        self.assertGreaterEqual(Decimal(result["threshold_upper"]), exact_beta)
        old = certification._ARITHMETIC.certify_stop(
            counts, [0, 0], R=3, eta=Fraction(1, 20), candidate_theta=[1, 1])
        self.assertEqual(old["status"], "rejected")
        wrong = CertifiedDecisionGate(conf).check(counts, candidate_item=0)
        self.assertEqual(wrong["status"], "NOT_CERTIFIED")
        self.assertIsNone(wrong["item"])

    def test_class_profiles_are_maxima_not_sums_or_posterior(self):
        model = JointLikelihood(public(3, [0, 1, 0]))
        counts = np.arange(12).reshape(3, 2, 2)
        table = model.best_table(counts)
        for item in model.items:
            gap = model.decision_gap(counts, item)
            same = table["loglik"][model.winner_by_theta == item].max()
            other = table["loglik"][model.winner_by_theta != item].max()
            self.assertEqual(gap["candidate_loglik"], same)
            self.assertEqual(gap["alternative_loglik"], other)
            self.assertEqual(gap["gap"], same - other)

    def test_precision_boundary_abstains_and_refinement_resolves(self):
        n = 10**14
        k = math.ceil(math.sqrt(n * (3 + math.log(n + 1)) / 2))
        successes = n // 2 + k
        counts = np.zeros((1, 2, 2), dtype=np.int64)
        counts[0, 0] = [n - successes, successes]
        conf = public(1)
        low = CertifiedDecisionGate(conf, precisions=(16,)).check(counts)
        self.assertEqual(low["status"], "UNDETERMINED")
        self.assertIsNone(low["item"])
        self.assertFalse(low["certified"])
        self.assertLess(Decimal(low["gap_lower"]), Decimal(low["threshold_upper"]))
        self.assertGreater(Decimal(low["gap_upper"]), Decimal(low["threshold_lower"]))
        high = CertifiedDecisionGate(conf, precisions=(50,)).check(counts)
        self.assertEqual(high["status"], "CERTIFIED")
        self.assertEqual(high["item"], 1)
        refined = CertifiedDecisionGate(conf, precisions=(16, 50)).check(counts)
        self.assertEqual([a["status"] for a in refined["precision_attempts"]], ["UNDETERMINED", "CERTIFIED"])

    def test_arithmetic_failure_fails_closed(self):
        counts = np.zeros((2, 2, 2), dtype=np.int64)
        counts[0, 0, 1] = 100
        with patch.object(certification._Intervals, "weighted_logs", side_effect=ArithmeticError("forced")):
            result = CertifiedDecisionGate(public()).check(counts)
        self.assertEqual(result["status"], "UNDETERMINED")
        self.assertIsNone(result["item"])
        self.assertIsNone(result["gap_lower"])
        self.assertEqual(result["reason"], "arithmetic_failure")

    def test_every_d6_state_is_enclosed_without_calling_old_gate(self):
        counts = np.ones((6, 2, 2), dtype=np.int64)
        conf = public(6, [0, 0, 0, 1, 1, 1])
        with patch.object(certification._ARITHMETIC, "certify_stop", side_effect=AssertionError("old gate called")):
            result = CertifiedDecisionGate(conf).check(counts)
        self.assertEqual(result["operation_counts"]["exact_joint_mle_fits"], 256)
        self.assertEqual(result["scope"]["joint_states"], 256)
        self.assertFalse(result["scope"]["old_d4_gate_called"])
        self.assertEqual(result["status"], "NOT_CERTIFIED")
        self.assertIsNone(result["item"])

    def test_malformed_counts_are_rejected_without_coercion(self):
        model, gate = JointLikelihood(public()), CertifiedDecisionGate(public())
        base = np.zeros((2, 2, 2), dtype=np.int64)
        negative = base.copy(); negative[0, 0, 0] = -1
        huge = base.astype(object); huge[0, 0, 0] = MAX_TOTAL_OBSERVATIONS + 1
        mixed_bool = base.tolist(); mixed_bool[0][0][0] = True
        mixed_float = base.tolist(); mixed_float[0][0][0] = 1.0
        not_finite = base.astype(float); not_finite[0, 0, 0] = np.nan
        examples = [np.zeros((2, 2)), np.zeros((1, 2, 2), dtype=int), negative,
                    base.astype(float), base.astype(bool), huge, mixed_bool,
                    mixed_float, not_finite, "counts", [[[0, 1]]]]
        for malformed in examples:
            with self.subTest(counts=str(malformed)[:70]):
                with self.assertRaises(ValueError): model.estimate(malformed)
                with self.assertRaises(ValueError): gate.check(malformed)

    def test_malformed_public_and_gate_constants_are_rejected(self):
        examples = []
        for field, value in (("d", 0), ("d", 7), ("d", True), ("d", 2.),
                             ("groups", [0, 2]), ("groups", [0]), ("groups", [-1, 0]),
                             ("groups", [False, 0]), ("eta", .01), ("eta", "0"),
                             ("eta", "1/2"), ("eta", "garbage"), ("eta", "1/0"),
                             ("eta", "1e-999999999")):
            conf = public(); conf[field] = value; examples.append(conf)
        extra = public(); extra["theta_true"] = [1, 1]; examples.append(extra)
        groups3 = public(3, [0, 1, 2]); examples.append(groups3)
        tie = public(); tie["catalogue"]["offsets"] = [0, 0]; tie["catalogue"]["slopes"] = [[0, 0], [0, 0]]; examples.append(tie)
        slopes = public(); slopes["catalogue"]["slopes"] = [[0], [1]]; examples.append(slopes)
        nonfinite = public(); nonfinite["catalogue"]["offsets"][0] = float("nan"); examples.append(nonfinite)
        for conf in examples:
            with self.subTest(public=conf):
                with self.assertRaises(ValueError): JointLikelihood(conf)
                with self.assertRaises(ValueError): CertifiedDecisionGate(conf)
        for risk in (0, -1, True, 3., Fraction(3, 1), "3", 2**4096):
            with self.assertRaises(ValueError): CertifiedDecisionGate(public(), R=risk)
        for precisions in ((), (15,), (513,), (50, 50), (80, 50), (True,), (16, 32, 64, 80, 120, 256, 512)):
            with self.assertRaises(ValueError): CertifiedDecisionGate(public(), precisions=precisions)

    def test_candidate_item_validation_and_never_winning_items(self):
        conf = public()
        conf["catalogue"]["offsets"].append(-100)
        conf["catalogue"]["slopes"].append([0, 0])
        counts = np.zeros((2, 2, 2), dtype=np.int64)
        for candidate in (-1, 2, 3, True, 1., "1"):
            with self.assertRaises(ValueError): JointLikelihood(conf).decision_gap(counts, candidate)
            with self.assertRaises(ValueError): CertifiedDecisionGate(conf).check(counts, candidate)

    def test_serializable_results_and_input_immutability(self):
        conf = public(3, [0, 1, 0]); snapshot = copy.deepcopy(conf)
        counts = np.arange(12).reshape(3, 2, 2); before = counts.copy()
        model, gate = JointLikelihood(conf), CertifiedDecisionGate(conf)
        json.dumps(model.estimate(counts), allow_nan=False)
        json.dumps(model.decision_gap(counts), allow_nan=False)
        result = gate.check(counts)
        json.dumps(result, allow_nan=False)
        self.assertEqual(conf, snapshot)
        np.testing.assert_array_equal(counts, before)
        # Later mutations of the caller's public dict cannot change inference.
        conf["groups"][:] = [0, 0, 0]
        self.assertEqual(model.groups, (0, 1, 0))

    def test_ambient_decimal_context_does_not_change_certificate(self):
        counts = np.zeros((2, 2, 2), dtype=np.int64); counts[0, 0, 1] = 20
        reference = CertifiedDecisionGate(public()).check(counts)
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.rounding = ROUND_UP
            actual = CertifiedDecisionGate(public()).check(counts)
        for key in ("status", "item", "gap_lower", "gap_upper", "threshold_lower", "threshold_upper"):
            self.assertEqual(actual[key], reference[key])

    def test_maximum_count_scope_uses_exact_integer_statistics(self):
        counts = np.zeros((6, 2, 2), dtype=np.int64)
        counts[0, 0, 1] = MAX_TOTAL_OBSERVATIONS
        conf = public(6, [0, 0, 0, 1, 1, 1])
        model = JointLikelihood(conf)
        table = model.best_table(counts)
        self.assertEqual(int(table["high_totals"][0, 0]), MAX_TOTAL_OBSERVATIONS)
        result = CertifiedDecisionGate(conf).check(counts)
        self.assertEqual(result["total_observations"], MAX_TOTAL_OBSERVATIONS)
        self.assertEqual(result["status"], "CERTIFIED")
        self.assertEqual(result["item"], 1)

    def test_constant_public_recommendation_is_vacuously_certified(self):
        conf = public(6, [0, 1, 0, 1, 0, 1])
        conf["catalogue"] = {"offsets": [2, 0], "slopes": [[0] * 6, [0] * 6]}
        counts = np.zeros((6, 2, 2), dtype=np.int64)
        result = CertifiedDecisionGate(conf).check(counts)
        self.assertEqual(result["status"], "CERTIFIED")
        self.assertEqual(result["item"], 0)
        self.assertEqual(result["gap_lower"], "+Infinity")
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
