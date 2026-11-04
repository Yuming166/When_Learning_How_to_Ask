"""Fixed numerical/action fixtures only; no experiment or world generation."""
import unittest
from unittest.mock import Mock, patch

import numpy as np

from policies import ARMS, ObservablePolicy, forced_action
from relative_ig import RelativeIGPolicy


PUBLIC = {
    "d": 2,
    "groups": [0, 0],
    "eta": "1/100",
    "catalogue": {"offsets": [0, 1], "slopes": [[0, 0], [1, 1]]},
}


def score_fixture(scores, counts=(5, 0, 1, 2), policy_class=RelativeIGPolicy):
    policy = policy_class("decision_ig", PUBLIC)
    policy.counts[:, :, 0] = np.asarray(counts).reshape(2, 2)
    policy.t = int(policy.counts.sum())
    if forced_action(policy.t, policy.d) is not None:
        raise AssertionError("fixture must start outside forced exploration")
    policy.posterior.scores = Mock(return_value=np.asarray(scores, dtype=float))
    return policy


class RelativeIGTests(unittest.TestCase):
    def test_scale_invariance_including_near_ties(self):
        epsilon = np.finfo(float).eps
        fixtures = [
            ([1, 2, 1.5, .5], 1),
            ([1, 1 - 32 * epsilon, .25, 0], 1),
            ([1, 1 - 128 * epsilon, .25, 0], 0),
        ]
        for scores, expected in fixtures:
            for exponent in (-500, -200, 0, 200, 500):
                with self.subTest(scores=scores, exponent=exponent):
                    scaled = np.ldexp(np.asarray(scores, dtype=float), exponent)
                    policy = score_fixture(scaled)
                    self.assertEqual(policy.next(), expected)
                    best = float(max(scaled))
                    self.assertEqual(policy.last_choice["gain_tie_tolerance"],
                                     64 * epsilon * abs(best))
                    self.assertEqual(policy.last_choice["maximum_gain"], best)

    def test_exact_zero_scores_choose_least_count_then_index(self):
        policy = score_fixture([0, 0, 0, 0], counts=(3, 1, 1, 3))
        self.assertEqual(policy.next(), 1)
        self.assertEqual(policy.last_choice["gain_tie_tolerance"], 0)
        self.assertEqual(policy.last_choice["selected_gain"], 0)
        self.assertFalse(policy.last_choice["forced"])

    def test_tiny_positive_gain_ranking_is_preserved(self):
        scores = [1e-80, 4e-80, 3e-80, 2e-80]
        counts = (0, 6, 1, 1)
        repaired = score_fixture(scores, counts)
        frozen = score_fixture(scores, counts, ObservablePolicy)
        self.assertEqual(repaired.next(), 1)
        # Retain the trigger: the frozen absolute threshold merges these gains.
        self.assertEqual(frozen.next(), 0)
        self.assertEqual(repaired.last_choice["selected_gain"], 4e-80)

    def test_forced_schedule_and_every_observation_are_preserved(self):
        policy = RelativeIGPolicy("decision_ig", PUBLIC, quadrature_order=6)
        policy.posterior.scores = Mock(return_value=np.asarray([0, 0, 0, 1.]))
        policy.posterior.observe = Mock(wraps=policy.posterior.observe)
        expected_counts = np.zeros_like(policy.counts)
        for t in range(65):
            expected_forced = forced_action(t, policy.d)
            score_calls = policy.posterior.scores.call_count
            action = policy.next()
            if expected_forced is not None:
                self.assertEqual(action, expected_forced)
                self.assertEqual(policy.last_choice,
                                 {"forced": True, "update_count": 0, "rule": "forced_exploration"})
                self.assertEqual(policy.posterior.scores.call_count, score_calls)
            else:
                self.assertEqual(action, 3)
                self.assertFalse(policy.last_choice["forced"])
                self.assertEqual(policy.posterior.scores.call_count, score_calls + 1)
            self.assertEqual(policy.pending, action)
            answer = t % 2
            expected_counts[action // 2, action % 2, answer] += 1
            policy.observe(action, answer)
            policy.posterior.observe.assert_called_with(action, answer)
            self.assertEqual(policy.posterior.observe.call_count, t + 1)
            self.assertEqual(policy.t, t + 1)
            self.assertIsNone(policy.pending)
            np.testing.assert_array_equal(policy.counts, expected_counts)
            np.testing.assert_array_equal(policy.posterior._counts,
                                          expected_counts.reshape(4, 2))
        self.assertEqual(policy.posterior.order, 6)
        self.assertEqual(policy.posterior.diagnostics()["observations"], 65)
        np.testing.assert_allclose(policy.cumulative, 65 * policy.weights)

    def test_pending_contract_is_preserved(self):
        policy = score_fixture([1, 2, 3, 4])
        action = policy.next()
        before = policy.cumulative.copy()
        with self.assertRaises(RuntimeError):
            policy.next()
        np.testing.assert_array_equal(policy.cumulative, before)
        with self.assertRaises(ValueError):
            policy.observe(action, True)
        with self.assertRaises(ValueError):
            policy.observe((action + 1) % 4, 1)
        self.assertEqual(policy.pending, action)
        policy.observe(action, 1)
        self.assertIsNone(policy.pending)

    def test_non_ig_arms_delegate_to_frozen_parent(self):
        for name in ARMS:
            if name == "decision_ig":
                continue
            policy = RelativeIGPolicy(name, PUBLIC)
            with patch.object(ObservablePolicy, "next", autospec=True, return_value=2) as parent_next:
                self.assertEqual(policy.next(), 2)
                parent_next.assert_called_once_with(policy)

    def test_invalid_score_contract_is_preserved(self):
        for scores in ([1, 2], [0, 1, float("nan"), 2], [0, 1, float("inf"), 2]):
            policy = score_fixture(scores)
            with self.assertRaises(ArithmeticError):
                policy.next()
            self.assertIsNone(policy.pending)


if __name__ == "__main__":
    unittest.main()
