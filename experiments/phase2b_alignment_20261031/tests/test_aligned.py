"""Bounded alignment tests; no model calls or independent confirmation runs."""

from copy import deepcopy
from itertools import product
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "phase2a_theory_optimality_20261030"
sys.path[:0] = [str(ROOT), str(OLD)]

from phase2b.aligned import TheoryAlignedTracking, ordered_grid_projection


def public_fixture(d=4, groups=None, accuracy=True):
    groups = groups or [list(range(d // 2)), list(range(d // 2, d))]
    public = {"d": d, "groups": [{"targets": group} for group in groups], "rate_domain": {"eta": .05}}
    if accuracy:
        public["type_accuracy"] = [.8] * len(groups)
    return public


def fake_allocation(partition, p, q, alpha, type_accuracy, eta, **kwargs):
    # Used only to isolate scheduling/estimation/tracking tests from repeated
    # numerical planning. Real continuous KL smoke tests below do not mock it.
    g = len(partition)
    total = 2 * sum(partition)
    return {"a": [1.] * g, "b": [1.] * g, "c": [0.] * g, "K": total,
            "relative_gap": 0., "lower_bound": total, "upper_bound": total,
            "minimum_information": 1., "iterations": 1, "cuts": 4}


def observe_zero(strategy, action):
    strategy.observe(action, {"format": "A"} if action[0] == "type" else {"answer": 0})


class TestAligned(unittest.TestCase):
    def test_exact_square_blocks_and_forced_bounds(self):
        policy = TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, planning_R=1024)
        policy.next_update = 10**9
        for t in range(2501):
            n = math.isqrt(t // 8)
            expected = t - 8 * n * n
            expected = expected if expected < 8 else None
            self.assertEqual(policy._forced_index(), expected)
            counts = policy.forced.sum(axis=2).reshape(-1)
            lower = math.isqrt(t // 8)
            self.assertTrue(np.all(counts >= lower))
            self.assertTrue(np.all(counts <= lower + 1))
            self.assertLessEqual(int(counts.sum()), math.sqrt(8 * t) + 8)
            action = policy.next(set(range(4)))
            self.assertEqual(policy.last_forced, expected is not None)
            if expected is not None:
                self.assertEqual(action, ("query", expected // 2, "AB"[expected % 2]))
            observe_zero(policy, action)

    def test_estimator_is_forced_only_and_matches_direct_formula(self):
        cal = {"high": [1] * 5, "low": [0] * 5}
        a = TheoryAlignedTracking(public_fixture(), cal, planning_R=1024)
        other_public = public_fixture()
        other_public["oracle_format_types"] = ["B", "A"]  # must never be inspected
        other_public["true_rates"] = [0., 1.]
        b = TheoryAlignedTracking(other_public, {"high": [0] * 5, "low": [1] * 5}, planning_R=1024)
        means10 = np.array([[9, 6], [2, 4], [6, 9], [4, 2]])
        for policy in (a, b):
            policy.forced[:, :, 1] = means10
            policy.forced[:, :, 0] = 10 - means10
            policy.t = 160
        a.counts[:] = 1000
        b.counts[:] = 11
        a.types = [[0] * 200, [1] * 200]
        b.types = [[1] * 300, [0] * 300]
        estimate = a._estimate()
        self.assertEqual(estimate, b._estimate())
        self.assertEqual(estimate["theta"], [1, 0, 1, 0])
        self.assertEqual(estimate["z"], [0, 1])
        self.assertAlmostEqual(estimate["raw_p"], .85)
        self.assertAlmostEqual(estimate["raw_q"], .60)
        self.assertEqual(a.alpha, 5 / 1024)
        self.assertFalse(hasattr(a, "calibration"))
        self.assertFalse(hasattr(a, "public"))

    def test_grid_projection_boundaries_ties_and_independent_enumeration(self):
        for t in (0, 3, 8, 24, 99, 399):
            for raw_p, raw_q in product((.4, .5, .6, .75, .95, 1.), repeat=2):
                projected = ordered_grid_projection(raw_p, raw_q, t)
                n = projected["grid_size"]
                got_loss = (projected["p"] - raw_p)**2 + (projected["q"] - raw_q)**2
                losses = [(.5 + .45 * p / n - raw_p)**2 + (.5 + .45 * q / n - raw_q)**2
                          for q in range(n) for p in range(q + 1, n + 1)]
                self.assertAlmostEqual(got_loss, min(losses), places=14)
                self.assertTrue(.5 <= projected["q"] < projected["p"] <= .95)
        exact = ordered_grid_projection(.95, .5, 100)
        self.assertEqual((exact["p"], exact["q"]), (.95, .5))
        self.assertEqual(ordered_grid_projection(.5, .5, 100)["q"], .5)
        self.assertEqual(ordered_grid_projection(.95, .95, 100)["p"], .95)
        self.assertLess(ordered_grid_projection(.75, .6, 10000)["grid_mesh"],
                        ordered_grid_projection(.75, .6, 100)["grid_mesh"])
        for t in range(4097):
            endpoint = ordered_grid_projection(1., 1., t)
            self.assertEqual(endpoint["p"], .95)
            self.assertTrue(.5 <= endpoint["q"] < endpoint["p"])

    def test_adversarial_changing_targets_pathwise_discrepancy(self):
        policy = TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, 1024)
        policy.next_update = 10**9
        for t in range(5000):
            weights = np.zeros(policy.E)
            if t % 5 == 0:
                # Concentrate on an action opposed to the next forced stream.
                weights[(t * 7 + 9) % policy.E] = 1
            else:
                values = np.array([1 + ((t + 13) * (i + 3)) % 17 for i in range(policy.E)])
                weights = values / values.sum()
            policy.weights = weights
            action = policy.next(range(4))
            observe_zero(policy, action)
            diag = policy.diagnostics()
            error = np.asarray(diag["actual_minus_target"])
            self.assertLessEqual(float(error.max()), diag["tracking_upper_bound"] + 1e-10)
            self.assertGreaterEqual(float(error.min()), diag["tracking_lower_bound"] - 1e-10)

    @patch("phase2b.aligned.solve_allocation", side_effect=fake_allocation)
    def test_delayed_updates_vanishing_requested_tolerance_and_logs(self, mocked):
        policy = TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, 1024)
        for _ in range(2500):
            observe_zero(policy, policy.next(range(4)))
        self.assertGreater(len(policy.estimates), 10)
        self.assertLess(len(policy.estimates), 3 * math.sqrt(policy.t))
        for current, following in zip(policy.estimates, policy.estimates[1:]):
            self.assertEqual(following["online"], current["next_update"])
            self.assertLessEqual(current["next_update"] - current["online"], math.sqrt(current["online"] + 1) + 1)
        self.assertGreater(policy.diagnostics()["last_update_ratio"], .97)
        self.assertLess(policy.requested_tolerance(100000), policy.requested_tolerance(1000))
        self.assertLess(policy.requested_tolerance(10**9), 1e-8)
        self.assertFalse(policy.last_estimate["numerical_floor_active"])
        self.assertGreaterEqual(policy.planner_cpu_seconds, 0)
        self.assertEqual(mocked.call_count, len(policy.estimates))

    def test_actual_solver_boundary_and_weak_separation_smoke(self):
        public = public_fixture(d=2, groups=[[0], [1]])
        for p, q in ((.95, .5), (.80, .79)):
            policy = TheoryAlignedTracking(public, {"high": [], "low": []}, 1024)
            policy.t = 4000
            # Direct forced stream observations produce the nominated raw
            # rates. The planner receives their deterministic grid projection.
            policy.forced[:, 0, 1] = round(100 * p)
            policy.forced[:, 0, 0] = 100 - round(100 * p)
            policy.forced[:, 1, 1] = round(100 * q)
            policy.forced[:, 1, 0] = 100 - round(100 * q)
            policy._update()
            entry = policy.last_estimate
            self.assertTrue(.5 <= entry["q"] < entry["p"] <= .95)
            self.assertGreater(entry["estimated_K"], 0)
            self.assertGreaterEqual(entry["minimum_information"], 1 - 1e-7)
            self.assertLessEqual(entry["solver_relative_gap"], entry["effective_numerical_relative_gap"])
            self.assertAlmostEqual(sum(entry["weights"]), 1)
            self.assertNotIn("shortcut", entry)

    @patch("phase2b.aligned.solve_allocation")
    def test_unattained_numerical_bound_fails_without_a_policy_fallback(self, mocked):
        bad = fake_allocation([2, 2], .8, .6, 0, [.8, .8], .05)
        bad["relative_gap"] = .01
        mocked.return_value = bad
        policy = TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, 1024)
        policy.forced[:, :, 0] = 1
        policy.t = 100
        previous = policy.weights.copy()
        with self.assertRaises(RuntimeError):
            policy._update()
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(len(policy.planning_failures), 1)
        np.testing.assert_array_equal(policy.weights, previous)
        self.assertIsNone(policy.last_estimate)

    @patch("phase2b.aligned.solve_allocation")
    def test_numerical_floor_is_reported_when_it_exceeds_requested_gap(self, mocked):
        fit = fake_allocation([2, 2], .8, .6, 0, [.8, .8], .05)
        fit["relative_gap"] = 3e-8
        mocked.return_value = fit
        policy = TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, 1024)
        policy.forced[:, :, 0] = 1
        policy.t = 200_000_000  # isolated numeric contract test, no trajectory run
        policy._update()
        entry = policy.last_estimate
        self.assertTrue(entry["numerical_floor_active"])
        self.assertGreater(entry["solver_relative_gap"], entry["requested_relative_gap"])
        self.assertLessEqual(entry["solver_relative_gap"], entry["effective_numerical_relative_gap"])

    def test_unavailable_type_questions_and_contract_failures(self):
        policy = TheoryAlignedTracking(public_fixture(accuracy=False), {"high": [], "low": []}, 1024)
        action = policy.next(range(4))
        with self.assertRaises(RuntimeError):
            policy.next(range(4))
        with self.assertRaises(ValueError):
            policy.observe(("query", 1, "A"), {"answer": 0})
        with self.assertRaises(ValueError):
            policy.observe(action, {"answer": 2})
        policy.observe(action, {"answer": 0})
        with self.assertRaises(ValueError):
            policy.next([0, 1])
        with self.assertRaises(ValueError):
            TheoryAlignedTracking(public_fixture(), {"high": [], "low": []}, float("inf"))
        with self.assertRaises(ValueError):
            TheoryAlignedTracking(public_fixture(), {"high": [0], "low": []}, 1024)


if __name__ == "__main__":
    unittest.main()
