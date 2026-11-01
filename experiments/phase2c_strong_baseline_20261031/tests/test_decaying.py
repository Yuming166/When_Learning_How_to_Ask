"""Deterministic D-RRC contract checks; no development/confirmation episodes."""

from copy import deepcopy
import inspect
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from phase2c.decaying import DecayingRepeatAndCompare
from phase2b.aligned import TheoryAlignedTracking


def public_fixture(partition=(1, 3), type_actions=True):
    groups, start = [], 0
    for size in partition:
        groups.append({"targets": list(range(start, start + size))})
        start += size
    public = {"d": start, "groups": groups, "rate_domain": {"eta": .05}}
    if type_actions:
        public["type_accuracy"] = [.8] * len(partition)
    return public


def set_forced_fixture(policy, group_types=(0, 1), t=1600):
    """Observable counts, without passing the fixture labels into the policy."""
    for g, members in enumerate(policy.groups):
        for j in members:
            for fmt in range(2):
                correct = 9 if fmt == group_types[g] else 6
                positives = correct if j % 2 else 10 - correct
                policy.forced[j, fmt, 1] = positives
                policy.forced[j, fmt, 0] = 10 - positives
    policy.t = t


def mock_good_only_allocation(partition, p, q, alpha, type_accuracy, eta, **kwargs):
    # Contract fixture: supply a good-only optimizer target to isolate the
    # equality of target expansion, without claiming this is always optimal.
    total = sum(partition)
    g = len(partition)
    return {"a": [1.] * g, "b": [0.] * g, "c": [0.] * g,
            "K": total, "lower_bound": total, "upper_bound": total,
            "relative_gap": 0., "minimum_information": 1., "iterations": 1, "cuts": 1}


class PoisonSequence:
    """Calibration length is public; looking at values is forbidden here."""

    def __len__(self):
        return 5

    def __iter__(self):
        raise AssertionError("calibration values were inspected")

    def __getitem__(self, index):
        raise AssertionError("calibration values were inspected")


class TestDecaying(unittest.TestCase):
    def test_only_the_target_update_is_overridden(self):
        own_methods = {name for name, value in DecayingRepeatAndCompare.__dict__.items() if callable(value)}
        self.assertEqual(own_methods, {"_update"})
        self.assertEqual(inspect.signature(DecayingRepeatAndCompare), inspect.signature(TheoryAlignedTracking))
        for method in ("_estimate", "_forced_index", "next", "observe", "diagnostics"):
            self.assertIs(getattr(DecayingRepeatAndCompare, method), getattr(TheoryAlignedTracking, method))

    @patch("phase2b.aligned.solve_allocation", side_effect=mock_good_only_allocation)
    def test_identical_forced_fixtures_have_identical_estimates_and_cadence(self, optimizer):
        public, cal = public_fixture(), {"high": [1, 0] * 3, "low": [0, 1] * 3}
        baseline = DecayingRepeatAndCompare(public, cal, 1024)
        aligned = TheoryAlignedTracking(public, cal, 1024)
        for policy in (baseline, aligned):
            set_forced_fixture(policy)
        estimate = aligned._estimate()
        self.assertEqual(baseline._estimate(), estimate)
        baseline._update()
        self.assertEqual(optimizer.call_count, 0)
        aligned._update()
        self.assertEqual(optimizer.call_count, 1)
        for key in estimate:
            self.assertEqual(baseline.last_estimate[key], aligned.last_estimate[key])
        self.assertEqual(baseline.next_update, aligned.next_update)
        self.assertEqual(baseline.last_update, aligned.last_update)
        self.assertEqual(baseline.alpha, 6 / 1024)
        for t in range(2501):
            baseline.t = aligned.t = t
            self.assertEqual(baseline._forced_index(), aligned._forced_index())

    def test_uniform_coordinate_allocation_and_zero_other_type_mass(self):
        for partition, group_types in (((1, 3), (0, 1)), ((1, 3), (1, 0)), ((4,), (1,))):
            for type_actions in (False, True):
                policy = DecayingRepeatAndCompare(public_fixture(partition, type_actions), {"high": [], "low": []}, 1024)
                set_forced_fixture(policy, group_types)
                policy._update()
                expected = np.zeros(policy.E)
                for g, members in enumerate(policy.groups):
                    for j in members:
                        expected[2 * j + group_types[g]] = 1 / policy.d
                np.testing.assert_array_equal(policy.weights, expected)
                np.testing.assert_array_equal(policy.weights[:policy.L].reshape(policy.d, 2).sum(axis=1),
                                              np.full(policy.d, 1 / policy.d))
                self.assertEqual(float(policy.weights[policy.L:].sum()), 0.)

    @patch("phase2b.aligned.solve_allocation", side_effect=AssertionError("D-RRC invoked KL solver"))
    def test_noiseless_5000_steps_no_optimizer_and_pathwise_bounds(self, optimizer):
        policy = DecayingRepeatAndCompare(public_fixture(), {"high": [], "low": []}, 1024)
        for _ in range(5000):
            action = policy.next(range(policy.d))
            self.assertEqual(action[0], "query")
            policy.observe(action, {"answer": action[1] % 2})
            diag = policy.diagnostics()
            discrepancy = np.asarray(diag["actual_minus_target"])
            self.assertLessEqual(float(discrepancy.max()), diag["tracking_upper_bound"] + 1e-9)
            self.assertGreaterEqual(float(discrepancy.min()), diag["tracking_lower_bound"] - 1e-9)
            forced = policy.forced.sum(axis=2)
            lower = math.isqrt(policy.t // policy.L)
            self.assertTrue(np.all(forced >= lower))
            self.assertTrue(np.all(forced <= lower + 1))
            self.assertLessEqual(int(forced.sum()), math.sqrt(policy.L * policy.t) + policy.L)
        optimizer.assert_not_called()
        self.assertEqual(int(policy.counts.sum()), 5000)
        self.assertEqual(policy.types, [[], []])
        self.assertGreater(len(policy.estimates), 50)
        self.assertGreater(policy.last_update / policy.t, .98)
        for current, following in zip(policy.estimates, policy.estimates[1:]):
            self.assertEqual(current["next_update"], following["online"])
        self.assertGreaterEqual(policy.planner_seconds, 0)
        self.assertGreaterEqual(policy.planner_cpu_seconds, 0)

    def test_later_observations_can_reverse_format_preference(self):
        policy = DecayingRepeatAndCompare(public_fixture(), {"high": [], "low": []}, 64)
        set_forced_fixture(policy, (0, 1), t=1600)
        policy._update()
        first = policy.weights.copy()
        set_forced_fixture(policy, (1, 0), t=2500)
        policy._update()
        self.assertEqual(policy.last_estimate["z"], [1, 0])
        self.assertFalse(np.array_equal(first, policy.weights))
        self.assertEqual(len(policy.estimates), 2)
        self.assertFalse(hasattr(policy, "commit"))

    def test_no_forbidden_input_or_excluded_observation_assistance(self):
        public = public_fixture()
        public.update({"oracle_format_types": object(), "theta": object(), "z": object(),
                       "p": object(), "q": object(), "seed": object(), "evaluation_feedback": object()})
        poison_cal = {"high": PoisonSequence(), "low": PoisonSequence()}
        policy = DecayingRepeatAndCompare(public, poison_cal, 1024)
        comparison = DecayingRepeatAndCompare(public_fixture(), {"high": [1] * 5, "low": [0] * 5}, 1024)
        for candidate in (policy, comparison):
            set_forced_fixture(candidate)
        policy.counts[:] = 999
        comparison.counts[:] = 2
        policy.types = [[0] * 100, [1] * 100]
        comparison.types = [[1] * 20, [0] * 20]
        self.assertEqual(policy._estimate(), comparison._estimate())
        policy._update()
        comparison._update()
        np.testing.assert_array_equal(policy.weights, comparison.weights)
        self.assertEqual(policy.alpha, comparison.alpha)
        self.assertFalse(hasattr(policy, "public"))
        self.assertFalse(hasattr(policy, "calibration"))

    def test_telemetry_is_factual_and_has_no_fake_optimization_fields(self):
        policy = DecayingRepeatAndCompare(public_fixture(), {"high": [], "low": []}, 1024)
        set_forced_fixture(policy)
        policy._update()
        log = policy.last_estimate
        for key in ("theta", "z", "p", "q", "raw_p", "raw_q", "weights", "forced_task_counts",
                    "update_seconds", "update_cpu_seconds", "next_update", "alpha_effective"):
            self.assertIn(key, log)
        self.assertNotIn("estimated_K", log)
        self.assertNotIn("lower_bound", log)
        self.assertNotIn("upper_bound", log)
        self.assertFalse(any(key.startswith("solver_") for key in log))
        self.assertEqual(log["paid_type_target_mass"], 0.)

    @patch("phase2b.aligned.solve_allocation", side_effect=mock_good_only_allocation)
    def test_good_only_uniform_aligned_target_can_coincide(self, optimizer):
        # In particular, G=1, alpha=0 has this ideal allocation. No artificial
        # perturbation is added to manufacture a contrast with Aligned.
        public, cal = public_fixture((4,)), {"high": [], "low": []}
        aligned = TheoryAlignedTracking(public, cal, 1024)
        baseline = DecayingRepeatAndCompare(public, cal, 1024)
        for policy in (aligned, baseline):
            set_forced_fixture(policy, (0,))
            policy._update()
        np.testing.assert_array_equal(aligned.weights, baseline.weights)
        self.assertEqual(optimizer.call_count, 1)


if __name__ == "__main__":
    unittest.main()
