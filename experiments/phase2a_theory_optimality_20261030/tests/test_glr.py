"""Independent, bounded GLR checks; runnable with stdlib unittest.

The scalar checker enumerates candidate signs/types using Python loops, and
maximizes by checking all interior/edge stationary points and triangle corners.
The SciPy checker evaluates raw answer probabilities and uses SLSQP instead of
the production aggregation/isotonic code. Neither imports a private GLR helper.
"""

from itertools import product
from math import log
import unittest

import numpy as np
from scipy.optimize import minimize

from phase2a.glr import endpoint_mle, profile_glr


def _direct_loglikelihood(p, q, theta, z, counts, groups, calibration, reports, accuracy):
    total = 0.0
    for g, members in enumerate(groups):
        for j in members:
            for fmt in range(2):
                rate = p if fmt == z[g] else q
                prob1 = rate if theta[j] else 1 - rate
                total += int(counts[j, fmt, 1]) * log(prob1)
                total += int(counts[j, fmt, 0]) * log(1 - prob1)
        for report in reports[g]:
            total += log(accuracy[g] if report == z[g] else 1 - accuracy[g])
    for label, rate in (("high", p), ("low", q)):
        for answer in calibration[label]:
            total += log(rate if answer else 1 - rate)
    return total


def scalar_profiles(counts, groups, calibration, reports, accuracy, eta=.05, oracle_types=None):
    """Finite candidate stationary-point checker, independently coded."""
    profiles = []
    z_vectors = list(product((0, 1), repeat=len(groups))) if oracle_types is None else [tuple(oracle_types)]
    for theta in product((0, 1), repeat=len(counts)):
        best = -np.inf
        for z in z_vectors:
            successes = [sum(calibration["high"]), sum(calibration["low"])]
            totals = [len(calibration["high"]), len(calibration["low"])]
            for g, members in enumerate(groups):
                for j in members:
                    for fmt in range(2):
                        block = int(fmt != z[g])
                        successes[block] += int(counts[j, fmt, theta[j]])
                        totals[block] += int(sum(counts[j, fmt]))
            hi = successes[0] / totals[0] if totals[0] else .5
            lo = successes[1] / totals[1] if totals[1] else .5
            clip = lambda x: max(.5, min(1 - eta, x))
            pool = sum(successes) / sum(totals) if sum(totals) else .5
            # Corners, stationary points on each edge, and interior stationary.
            candidates = [(.5, .5), (1 - eta, .5), (1 - eta, 1 - eta),
                          (clip(hi), .5), (1 - eta, clip(lo)),
                          (clip(pool), clip(pool))]
            if .5 <= lo <= hi <= 1 - eta:
                candidates.append((hi, lo))
            value = max(_direct_loglikelihood(p, q, theta, z, counts, groups, calibration, reports, accuracy)
                        for p, q in candidates)
            best = max(best, value)
        profiles.append(best)
    return np.asarray(profiles)


def scipy_profiles(counts, groups, calibration, reports, accuracy, eta=.05, oracle_types=None):
    """Enumerate discrete states; optimize each continuous triangle with SLSQP."""
    profiles = []
    residuals = []
    failures = []
    z_vectors = list(product((0, 1), repeat=len(groups))) if oracle_types is None else [tuple(oracle_types)]
    for theta in product((0, 1), repeat=len(counts)):
        best = -np.inf
        for z in z_vectors:
            objective = lambda x: -_direct_loglikelihood(x[0], x[1], theta, z, counts, groups, calibration, reports, accuracy)
            fit = minimize(objective, [.73, .60], method="SLSQP", bounds=[(.5, 1 - eta)] * 2,
                           constraints=[{"type": "ineq", "fun": lambda x: x[0] - x[1]}],
                           options={"ftol": 1e-11, "maxiter": 100})
            residuals.append(max(0., fit.x[1] - fit.x[0], .5 - min(fit.x), max(fit.x) - (1 - eta)))
            if not fit.success:
                failures.append((theta, z, fit.message))
            best = max(best, -fit.fun)
        profiles.append(best)
    return np.asarray(profiles), residuals, failures


def tiny_case(d):
    rng = np.random.default_rng(20261030 + d)
    counts = rng.integers(0, 4, size=(d, 2, 2))
    groups = [list(range(d // 2)), list(range(d // 2, d))]
    calibration = {"high": [1, 1, 0], "low": [0, 1, 0]}
    reports = [[0, 0, 1], [1, 1]]
    accuracy = [.8, .7]
    return counts, groups, calibration, reports, accuracy


class TestGLR(unittest.TestCase):
    def test_full_scalar_enumeration_d4_d6_d8(self):
        for d in (4, 6, 8):
            with self.subTest(d=d):
                args = tiny_case(d)
                got = profile_glr(*args)
                expected = scalar_profiles(*args)
                np.testing.assert_allclose(got["profile_log_likelihoods"], expected, atol=4e-12, rtol=0)
                order = np.sort(expected)
                self.assertAlmostEqual(got["gap"], order[-1] - order[-2], places=11)
                self.assertEqual(got["joint_candidates"], 2 ** (d + 2))

    def test_full_scipy_enumeration_d4_d6_d8(self):
        for d in (4, 6, 8):
            with self.subTest(d=d):
                args = tiny_case(d)
                got = profile_glr(*args)
                expected, residuals, failures = scipy_profiles(*args)
                # SLSQP can report positive-direction line-search failure at a
                # boundary optimum. Preserve statuses in the audit, and test
                # objective agreement/feasibility rather than hiding them.
                self.assertLess(max(residuals), 1e-7)
                np.testing.assert_allclose(got["profile_log_likelihoods"], expected, atol=3e-7, rtol=0)

    def test_zero_observations_and_deterministic_ties(self):
        got = profile_glr(np.zeros((4, 2, 2), int), [[0, 1], [2, 3]])
        self.assertEqual(got["theta"], [0] * 4)
        self.assertEqual(got["alternative_theta"], [0, 0, 0, 1])
        self.assertEqual(got["z"], [0, 0])
        self.assertEqual((got["p_hat"], got["q_hat"]), (.5, .5))
        self.assertEqual(got["gap"], 0.)
        self.assertAlmostEqual(got["beta"], log(20))
        self.assertFalse(got["certified"])

    def test_calibration_and_type_only_never_identify_signs(self):
        got = profile_glr(np.zeros((4, 2, 2), int), [[0, 1], [2, 3]],
                          {"high": [1] * 12, "low": [0] * 12},
                          [[1] * 9, [0] * 8], [.9, .8])
        self.assertEqual(got["z"], [1, 0])
        self.assertEqual(got["theta"], [0] * 4)
        self.assertEqual((got["p_hat"], got["q_hat"]), (.95, .5))
        self.assertEqual(got["gap"], 0)
        self.assertFalse(got["certified"])
        self.assertAlmostEqual(got["beta"], log(20) + 2 * log(13) + log(10) + log(9))

    def test_pooling_and_unobserved_rate_cases(self):
        # Fixed type 0, four high failures / twelve low successes: pool to .75.
        counts = np.zeros((1, 2, 2), int)
        counts[0, 0, 0], counts[0, 1, 1] = 4, 12
        got = profile_glr(counts, [[0]], oracle_types=[0])
        expected = scalar_profiles(counts, [[0]], {"high": [], "low": []}, [[]], [.75], oracle_types=[0])
        np.testing.assert_allclose(got["profile_log_likelihoods"], expected, atol=1e-12, rtol=0)
        # Only low observed. High is free above low; representative sets p=q.
        counts = np.zeros((1, 2, 2), int)
        counts[0, 1, 1] = 8
        got = profile_glr(counts, [[0]], oracle_types=[0])
        self.assertEqual((got["p_hat"], got["q_hat"]), (.95, .95))
        counts = counts[:, ::-1].copy()
        got = profile_glr(counts, [[0]], oracle_types=[0])
        self.assertEqual((got["p_hat"], got["q_hat"]), (.95, .5))

    def test_oracle_fixes_only_types(self):
        args = tiny_case(4)
        got = profile_glr(*args, oracle_types=[0, 1])
        expected = scalar_profiles(*args, oracle_types=[0, 1])
        np.testing.assert_allclose(got["profile_log_likelihoods"], expected, atol=4e-12, rtol=0)
        self.assertTrue(got["oracle_types_fixed"])
        self.assertEqual(got["type_candidates"], 1)
        self.assertEqual(got["z"], [0, 1])
        self.assertTrue(.5 <= got["q_hat"] <= got["p_hat"] <= .95)

    def test_threshold_stream_counts_and_actual_crossing(self):
        counts = np.zeros((4, 2, 2), int)
        counts[:, :, 1] = 64
        got = profile_glr(counts, [[0, 1], [2, 3]], {"high": [1, 0], "low": [0, 1]},
                          [[0, 1, 0], [1]], [.8, .7], delta=.01)
        self.assertAlmostEqual(got["beta"], log(100) + 2 * log(3) + 8 * log(65) + log(4) + log(2))
        self.assertTrue(got["certified"])
        self.assertFalse(got["interval_certified"])
        self.assertEqual(got["theta"], [1] * 4)

    def test_all_group_types_are_enumerated_up_to_d8(self):
        # Worst supported combinatorial size: 256 signs x 256 types.
        counts = np.zeros((8, 2, 2), int)
        got = profile_glr(counts, [[j] for j in range(8)])
        self.assertEqual(got["joint_candidates"], 65536)
        self.assertEqual(got["gap"], 0)

    def test_membership_vector_and_sign_flip_equivariance(self):
        counts, groups, calibration, reports, accuracy = tiny_case(4)
        a = profile_glr(counts, groups, calibration, reports, accuracy)
        b = profile_glr(counts, [0, 0, 1, 1], calibration, reports, accuracy)
        self.assertEqual(a["profile_log_likelihoods"], b["profile_log_likelihoods"])
        flipped = counts.copy()
        flipped[1] = flipped[1, :, ::-1]
        c = profile_glr(flipped, groups, calibration, reports, accuracy)
        # The lexicographic representative itself need not transform when
        # there are tied MLEs. Compare the whole permuted profile instead.
        np.testing.assert_allclose(c["profile_log_likelihoods"],
                                   [a["profile_log_likelihoods"][i ^ 4] for i in range(16)],
                                   atol=1e-12, rtol=0)
        self.assertAlmostEqual(a["gap"], c["gap"], places=12)

    def test_bounded_endpoint_extension_and_no_stopping_claim(self):
        counts = np.zeros((16, 2, 2), int)
        counts[:, :, 1] = 4
        got = endpoint_mle(counts, [list(range(8)), list(range(8, 16))])
        self.assertEqual(got["joint_candidates"], 262144)
        self.assertEqual(got["theta"], [1] * 16)
        for key in ("gap", "beta", "certified", "interval_certified"):
            self.assertNotIn(key, got)
        self.assertNotIn("profile_log_likelihoods", got)
        with self.assertRaises(ValueError):
            endpoint_mle(np.zeros((4, 2, 2), int), [[0], [1], [2, 3]])
        small_args = tiny_case(4)
        endpoint = endpoint_mle(*small_args, include_profiles=True)
        repeated = endpoint_mle(*small_args, include_profiles=True)
        glr = profile_glr(*small_args)
        for key in ("theta", "z", "p_hat", "q_hat", "profile_log_likelihoods"):
            self.assertEqual(endpoint[key], glr[key])
            self.assertEqual(endpoint[key], repeated[key])

    def test_reject_invalid_inputs_and_d16(self):
        empty = np.zeros((4, 2, 2), int)
        with self.assertRaises(ValueError):
            profile_glr(np.zeros((16, 2, 2), int), [list(range(16))])
        with self.assertRaises(ValueError):
            profile_glr(empty, [[0, 1], [1, 2, 3]])
        with self.assertRaises(ValueError):
            profile_glr(empty, [[0, 1], [2, 3]], {"high": [1], "low": []})
        with self.assertRaises(ValueError):
            profile_glr(empty, [[0, 1], [2, 3]], type_answers=[[0], []])
        with self.assertRaises(ValueError):
            profile_glr(empty, [[0, 1], [2, 3]], type_accuracy=[.5, .8])
        with self.assertRaises(ValueError):
            profile_glr(empty, [[0, 1], [2, 3]], oracle_types=[1, 2])
        fractional = empty.astype(float)
        fractional[0, 0, 0] = .5
        with self.assertRaises(ValueError):
            profile_glr(fractional, [[0, 1], [2, 3]])
        too_large = np.zeros((1, 2, 2), dtype=np.int64)
        too_large[0, 0, 0] = 2**50 + 1
        with self.assertRaises(ValueError):
            profile_glr(too_large, [[0]])


if __name__ == "__main__":
    unittest.main()
