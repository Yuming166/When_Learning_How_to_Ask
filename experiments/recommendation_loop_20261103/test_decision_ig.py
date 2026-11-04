"""Deterministic correctness checks; these are not an efficacy experiment."""
from copy import deepcopy
import json
import unittest

import numpy as np

try:
    from .decision_ig import QuadratureDecisionIG
except ImportError:
    from decision_ig import QuadratureDecisionIG


def fixture(d=3):
    return {"d": d, "groups": [0] * d, "eta": "1/100",
            "catalogue": {"offsets": [0, 0],
                          "slopes": [[0] * d, [1] + [0] * (d - 1)]}}


class DecisionIGTests(unittest.TestCase):
    def test_triangle_prior_moments_and_default(self):
        public = fixture()
        del public["eta"]
        model = QuadratureDecisionIG(public)
        diagnostic = model.diagnostics()
        length = .49
        self.assertAlmostEqual(diagnostic["posterior_mean_p"], .5 + 2 * length / 3, places=14)
        self.assertAlmostEqual(diagnostic["posterior_mean_q"], .5 + length / 3, places=14)
        self.assertEqual(diagnostic["quadrature_nodes"], 36)
        self.assertEqual(diagnostic["joint_states"], 8 * 2 * 36)
        self.assertFalse(diagnostic["posterior_certification"])
        self.assertIn("approximate", diagnostic["inference"])

    def test_predictive_normalization_and_nonnegative_entropies(self):
        public = fixture(4)
        public["groups"] = [0, 1, 0, 1]
        model = QuadratureDecisionIG(public)
        for action, answer in [(0, 1), (3, 0), (0, 1), (6, 0), (5, 1), (3, 1)]:
            model.observe(action, answer)
        diagnostic = model.diagnostics()
        prediction = np.array(diagnostic["posterior_predictive"])
        np.testing.assert_allclose(prediction.sum(axis=1), 1, atol=2e-15)
        self.assertTrue(np.all((prediction > 0) & (prediction < 1)))
        self.assertAlmostEqual(diagnostic["posterior_mass"], 1, places=14)
        for key in ["theta_probability", "item_probability", "type_probability", "target_probability"]:
            self.assertAlmostEqual(sum(diagnostic[key]), 1, places=14)
        self.assertGreaterEqual(diagnostic["target_entropy"], 0)
        self.assertTrue(np.all(np.array(diagnostic["entropy_after_answer"]) >= 0))
        self.assertTrue(np.all(model.scores() >= 0))
        np.testing.assert_allclose(model.scores(), diagnostic["target_entropy"] -
                                   np.array(diagnostic["expected_entropy_after_answer"]), atol=2e-14)
        json.dumps(diagnostic, allow_nan=False)

    def test_item_target_differs_from_theta_target(self):
        public = fixture()
        decision = QuadratureDecisionIG(public)
        theta = QuadratureDecisionIG(public, target="theta")
        self.assertGreater(decision.scores()[0], .05)
        np.testing.assert_allclose(decision.scores()[2:], 0, atol=1e-28)
        np.testing.assert_allclose(theta.scores(), theta.scores()[0], atol=3e-15)
        self.assertGreater(theta.scores()[2], .05)
        np.testing.assert_allclose(decision.diagnostics()["item_probability"], [.5, .5], atol=2e-15)

    def test_no_history_symmetry_for_majority_catalogue(self):
        public = fixture()
        public["catalogue"] = {"offsets": [0, 0], "slopes": [[0, 0, 0], [1, 1, 1]]}
        public["groups"] = [0, 1, 1]
        model = QuadratureDecisionIG(public)
        np.testing.assert_allclose(model.scores(), model.scores()[0], atol=3e-15)
        np.testing.assert_allclose(model.diagnostics()["posterior_predictive"], .5, atol=2e-15)
        self.assertEqual(model.diagnostics()["maximizers_within_float_tolerance"], list(range(6)))

    def test_mask_and_answer_conventions(self):
        model = QuadratureDecisionIG(fixture(2))
        model.observe(0, 1)
        theta_probability = np.array(model.diagnostics()["theta_probability"])
        # A positive raw answer favors bit 0 (positive), not mask bit 1.
        positive_probability = theta_probability[[0, 2]].sum()
        self.assertAlmostEqual(positive_probability, .5 + .49 / 2, places=14)
        self.assertGreater(positive_probability, .5)

    def test_incremental_matches_independent_batch_likelihood(self):
        public = fixture(2)
        public["groups"] = [0, 1]
        model = QuadratureDecisionIG(public)
        transcript = [(0, 1), (1, 1), (3, 0), (2, 1), (0, 0), (3, 0), (2, 0)]
        for action, answer in transcript:
            model.observe(action, answer)
        # Independently construct the unnormalized full joint posterior.
        x, weights = np.polynomial.legendre.leggauss(6)
        nodes, weights = (x + 1) / 2, weights / 2
        expected = np.empty((4, 4, 6, 6))
        for theta in range(4):
            for types in range(4):
                for si, s in enumerate(nodes):
                    for ti, t in enumerate(nodes):
                        p, q = .5 + .49 * s, .5 + .49 * s * t
                        probability = 2 * s * weights[si] * weights[ti] / 16
                        for action, answer in transcript:
                            j, fmt = divmod(action, 2)
                            rate = p if ((types >> public["groups"][j]) & 1) == fmt else q
                            positive = 1 - rate if (theta >> j) & 1 else rate
                            probability *= positive if answer else 1 - positive
                        expected[theta, types, si, ti] = probability
        evidence = expected.sum()
        expected /= evidence
        np.testing.assert_allclose(model._weights, expected.ravel(), rtol=8e-15, atol=2e-17)
        self.assertAlmostEqual(model.diagnostics()["log_transcript_evidence"], np.log(evidence), places=13)
        reverse = QuadratureDecisionIG(public)
        for action, answer in reversed(transcript):
            reverse.observe(action, answer)
        np.testing.assert_allclose(model.scores(), reverse.scores(), rtol=2e-13, atol=2e-15)

    def test_quadrature_order_sensitivity_short_fixture(self):
        public = fixture(3)
        public["groups"] = [0, 1, 1]
        public["catalogue"] = {"offsets": [0, "1/5", "-1/7"],
                               "slopes": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
        low, high = QuadratureDecisionIG(public, order=4), QuadratureDecisionIG(public, order=8)
        transcript = [(0, 1), (3, 0), (4, 1), (1, 1), (3, 1), (4, 0)]
        for action, answer in transcript:
            low.observe(action, answer)
            high.observe(action, answer)
        # The six-reply predictive integrand can have degree eight in s:
        # order four (exact through degree seven) need not match to roundoff.
        # This deliberately loose, explicit sensitivity bound is not a claim
        # of a certified integration error or a method-performance comparison.
        np.testing.assert_allclose(low.scores(), high.scores(), atol=1e-4, rtol=0)
        np.testing.assert_allclose(low.diagnostics()["item_probability"],
                                   high.diagnostics()["item_probability"], atol=2e-12, rtol=0)

    def test_rejects_hidden_fields_and_invalid_public_data(self):
        for name in ["theta", "z", "p", "q", "true_rates", "calibration", "history", "seed"]:
            public = fixture()
            public[name] = 0
            with self.assertRaises(ValueError):
                QuadratureDecisionIG(public)
        public = fixture()
        public["catalogue"]["true_item"] = 0
        with self.assertRaises(ValueError):
            QuadratureDecisionIG(public)
        for change in [{"groups": [0, 2, 2]}, {"groups": [1, 1, 1]},
                       {"eta": .01}, {"eta": "0"}, {"eta": "1/2"}, {"d": True}]:
            public = {**fixture(), **change}
            with self.assertRaises(ValueError):
                QuadratureDecisionIG(public)
        public = fixture()
        public["catalogue"]["slopes"][1] = [0, 0, 0]
        with self.assertRaisesRegex(ValueError, "tied best"):
            QuadratureDecisionIG(public)
        public = fixture()
        public["catalogue"]["offsets"][1] = float("nan")
        with self.assertRaises(ValueError):
            QuadratureDecisionIG(public)

    def test_observe_validation_and_score_copy(self):
        model = QuadratureDecisionIG(deepcopy(fixture()))
        before = model.scores()
        copy = model.scores()
        copy[:] = 10
        np.testing.assert_array_equal(model.scores(), before)
        for action, answer in [(-1, 0), (6, 1), (0, 2), (0., 1), (0, True)]:
            with self.assertRaises(ValueError):
                model.observe(action, answer)
        self.assertEqual(model.diagnostics()["observations"], 0)

    def test_constant_decision_has_zero_information(self):
        public = fixture(3)
        public["catalogue"] = {"offsets": [1, 0], "slopes": [[0, 0, 0], [0, 0, 0]]}
        model = QuadratureDecisionIG(public)
        for action, answer in [(0, 1), (4, 0), (5, 1), (3, 1)]:
            model.observe(action, answer)
            np.testing.assert_allclose(model.scores(), 0, atol=1e-28)
            self.assertEqual(model.diagnostics()["target_entropy"], 0)
            self.assertTrue(np.all(np.asarray(model.diagnostics()["entropy_after_answer"]) >= 0))

    def test_concentrated_posterior_stays_finite_without_certification(self):
        model = QuadratureDecisionIG(fixture(2))
        for _ in range(150):
            for action in range(4):
                model.observe(action, 1)
        diagnostic = model.diagnostics()
        self.assertTrue(np.isfinite(model.scores()).all())
        self.assertTrue(np.all(model.scores() >= 0))
        self.assertFalse(diagnostic["posterior_certification"])
        self.assertIsNone(diagnostic["stopping_rule"])
        json.dumps(diagnostic, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
