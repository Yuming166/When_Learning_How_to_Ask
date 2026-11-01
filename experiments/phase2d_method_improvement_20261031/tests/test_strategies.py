"""Deterministic strategy contracts; no statistical worlds or episodes."""

from copy import deepcopy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from phase2d.strategies import AlignedFull, AlignedNoType, DRRCNoType, DRRCType, SAMPLERS, construct_sampler
from phase2b.aligned import TheoryAlignedTracking
from phase2c.decaying import DecayingRepeatAndCompare


def public_fixture(partition=(1, 3), accuracy=(.8, .8)):
    groups, start = [], 0
    for size in partition:
        groups.append({"targets": list(range(start, start + size))})
        start += size
    result = {"d": start, "groups": groups, "rate_domain": {"eta": .05}}
    if accuracy is not None:
        result["type_accuracy"] = list(accuracy)
    return result


def force_fixture(policy, t=1600):
    for g, members in enumerate(policy.groups):
        for j in members:
            for fmt in range(2):
                successes = 8 if fmt == g % 2 else 6
                positives = successes if j % 2 else 10 - successes
                policy.forced[j, fmt, 1] = positives
                policy.forced[j, fmt, 0] = 10 - positives
    policy.counts[:] = policy.forced
    policy.t = t


def uniform_allocation(partition, p, q, alpha, type_accuracy, eta, **kwargs):
    groups, total = len(partition), 2 * sum(partition)
    return {"a": [1.] * groups, "b": [1.] * groups, "c": [0.] * groups,
            "K": total, "lower_bound": total, "upper_bound": total,
            "relative_gap": 0., "minimum_information": 1., "iterations": 1, "cuts": 1}


class PoisonSequence:
    def __len__(self):
        return 5

    def __iter__(self):
        raise AssertionError("calibration values inspected")

    def __getitem__(self, index):
        raise AssertionError("calibration values inspected")


class TestFrozenControls(unittest.TestCase):
    def test_literal_frozen_aliases_and_inherited_control_methods(self):
        self.assertIs(AlignedFull, TheoryAlignedTracking)
        self.assertIs(DRRCNoType, DecayingRepeatAndCompare)
        for cls in SAMPLERS.values():
            for name in ("_estimate", "_forced_index", "next", "observe", "diagnostics"):
                self.assertIs(getattr(cls, name), getattr(TheoryAlignedTracking, name))
        own = {name for name, value in AlignedNoType.__dict__.items() if callable(value)}
        self.assertEqual(own, {"__init__"})
        self.assertIs(AlignedNoType._update, TheoryAlignedTracking._update)
        own_type = {name for name, value in DRRCType.__dict__.items() if callable(value)}
        self.assertEqual(own_type, {"_update"})

    def test_actual_full_class_behavior_on_identical_history(self):
        public = public_fixture((1, 1))
        calibration = {"high": [0, 1], "low": [1, 0]}
        frozen = TheoryAlignedTracking(public, calibration, 32)
        full = AlignedFull(public, calibration, 32)
        for policy in (frozen, full):
            force_fixture(policy)
            policy._update()
        np.testing.assert_array_equal(full.weights, frozen.weights)
        self.assertEqual(full.last_estimate["allocation_c"], frozen.last_estimate["allocation_c"])
        for _ in range(50):
            first, second = frozen.next(range(2)), full.next(range(2))
            self.assertEqual(first, second)
            result = {"format": "AB"[first[1] % 2]} if first[0] == "type" else {"answer": first[1] % 2}
            frozen.observe(first, result)
            full.observe(second, result)
        np.testing.assert_array_equal(full.counts, frozen.counts)
        np.testing.assert_array_equal(full.forced, frozen.forced)
        np.testing.assert_array_equal(full.cumulative, frozen.cumulative)
        self.assertEqual(full.types, frozen.types)
        self.assertEqual(full.next_update, frozen.next_update)

    def test_actual_no_type_solver_omits_type_actions_and_preserves_public(self):
        from phase2b.aligned import solve_allocation
        public = public_fixture((1, 1))
        original = deepcopy(public)
        policy = AlignedNoType(public, {"high": [], "low": []}, 32)
        force_fixture(policy)
        with patch("phase2b.aligned.solve_allocation", wraps=solve_allocation) as optimizer:
            policy._update()
        self.assertGreater(optimizer.call_count, 0)
        for call in optimizer.call_args_list:
            self.assertIsNone(call.args[4])
        self.assertEqual(policy.last_estimate["allocation_c"], [0., 0.])
        np.testing.assert_array_equal(policy.weights[policy.L:], [0., 0.])
        self.assertEqual(public, original)

    @patch("phase2b.aligned.solve_allocation", side_effect=uniform_allocation)
    def test_no_type_strategies_never_emit_type_actions(self, optimizer):
        for cls in (AlignedNoType, DRRCNoType):
            policy = cls(public_fixture(), {"high": [], "low": []}, 32)
            for _ in range(1000):
                action = policy.next(range(policy.d))
                self.assertEqual(action[0], "query")
                policy.observe(action, {"answer": action[1] % 2})
            self.assertEqual(policy.types, [[], []])
            np.testing.assert_array_equal(policy.weights[policy.L:], [0., 0.])


class TestTypeAcquisition(unittest.TestCase):
    def make_policy(self, risk=32, public=None):
        policy = DRRCType(public or public_fixture(), {"high": [], "low": []}, risk)
        force_fixture(policy)
        return policy

    @patch("phase2b.aligned.solve_allocation", side_effect=AssertionError("public guard called joint optimizer"))
    def test_public_structure_guard_matches_frozen_d_path_exactly(self, optimizer):
        public = public_fixture((4,), accuracy=(.8,))
        first = DRRCType(public, {"high": [], "low": []}, 64)
        second = DRRCNoType(public, {"high": [], "low": []}, 64)
        for step in range(800):
            action, comparison = first.next(range(4)), second.next(range(4))
            self.assertEqual(action, comparison)
            self.assertEqual(action[0], "query")
            answer = int((step + 3 * action[1]) % 7 != 0)
            first.observe(action, {"answer": answer})
            second.observe(comparison, {"answer": answer})
            np.testing.assert_array_equal(first.weights, second.weights)
            np.testing.assert_array_equal(first.cumulative, second.cumulative)
        np.testing.assert_array_equal(first.counts, second.counts)
        np.testing.assert_array_equal(first.forced, second.forced)
        self.assertEqual(first.types, [[]])
        self.assertEqual(first.next_update, second.next_update)
        self.assertGreater(len(first.estimates), 20)
        for guarded, frozen in zip(first.estimates, second.estimates):
            self.assertEqual(guarded["weights"], frozen["weights"])
            self.assertEqual(guarded["z"], frozen["z"])
            self.assertEqual(guarded["online"], frozen["online"])
            self.assertEqual(guarded["public_structure_guard"], "single_group_zero_reference_count")
            self.assertFalse(guarded["type_acquisition_enabled"])
        optimizer.assert_not_called()

    def test_public_guard_requires_both_one_group_and_no_references(self):
        cases = [((4,), 0, True), ((4,), 1, False), ((1, 3), 0, False), ((1, 3), 1, False)]
        for partition, references, guarded in cases:
            public = public_fixture(partition, accuracy=(.8,) * len(partition))
            calibration = {"high": [0] * references, "low": [1] * references}
            policy = DRRCType(public, calibration, 64)
            force_fixture(policy)
            policy._update()
            self.assertEqual(policy.last_estimate["public_structure_guard"] is not None, guarded)
            self.assertEqual(policy.last_estimate["paid_type_target_mass"] == 0, guarded)
            if not guarded:
                self.assertEqual(policy.last_estimate["auxiliary_threshold"], 64 + math.log(2 * policy.d + 2 * policy.G))

    def test_single_group_zero_reference_ideal_coefficient_fixture(self):
        from phase2a.coefficients import solve_allocation, oracle_coefficient
        # Fixed coefficient inputs, not sampled worlds or effectiveness data.
        for p, q in ((.85, .6), (.95, .5), (.8, .79)):
            fit = solve_allocation([4], p, q, 0, [.8])
            oracle = oracle_coefficient(4, p, q, 0)
            self.assertAlmostEqual(fit["K"] / oracle["K"], 1., places=6)
            self.assertLess(abs(fit["b"][0]) + abs(fit["c"][0]), 1e-7)

    @patch("phase2b.aligned.solve_allocation", side_effect=AssertionError("D-RRC-Type called joint optimizer"))
    def test_all_four_share_identical_forced_only_estimator(self, optimizer):
        estimates = []
        public = public_fixture()
        public.update({name: object() for name in ("theta", "z", "p", "q", "seed", "oracle_format_types", "evaluation_feedback")})
        for index, cls in enumerate(SAMPLERS.values()):
            policy = cls(public, {"high": PoisonSequence(), "low": PoisonSequence()}, 32)
            force_fixture(policy)
            policy.counts[:] = index + 9
            policy.types = [[index % 2] * (20 + index), [(index + 1) % 2] * (30 + index)]
            estimates.append(policy._estimate())
            self.assertEqual(policy.alpha, 5 / 32)
            self.assertFalse(hasattr(policy, "public"))
            self.assertFalse(hasattr(policy, "calibration"))
        self.assertTrue(all(value == estimates[0] for value in estimates))
        optimizer.assert_not_called()

    def test_type_reports_change_acquisition_but_never_task_orientation(self):
        uncertain = self.make_policy()
        confident = self.make_policy()
        conflicting = self.make_policy()
        # The forced estimator says group 0 prefers A. Reports confidently B
        # must reduce type uncertainty without overriding that task estimate.
        confident.types[0] = [1] * 100
        conflicting.types[0] = [1] * 100 + [0] * 100
        expected = uncertain._estimate()
        for policy in (uncertain, confident, conflicting):
            policy._update()
            self.assertEqual(policy._estimate(), expected)
            for g, members in enumerate(policy.groups):
                for j in members:
                    self.assertEqual(policy.weights[2 * j + 1 - expected["z"][g]], 0.)
        self.assertGreater(uncertain.weights[uncertain.L], 0.)
        self.assertEqual(confident.weights[confident.L], 0.)
        self.assertGreater(confident.weights[confident.L + 1], uncertain.weights[uncertain.L + 1])
        np.testing.assert_array_equal(uncertain.weights, conflicting.weights)

    def test_unresolved_task_workload_controls_type_task_balance(self):
        pending, advanced = self.make_policy(), self.make_policy()
        estimate = advanced._estimate()
        # Change observable nonforced task history in just group 1, preserving
        # every forced observation and every type report.
        for j in advanced.groups[1]:
            fmt, answer = estimate["z"][1], estimate["theta"][j]
            advanced.counts[j, fmt, answer] += 100
        for policy in (pending, advanced):
            policy._update()
        self.assertEqual(pending._estimate(), advanced._estimate())
        self.assertEqual(pending.last_estimate["auxiliary_group_task_workload"][0],
                         advanced.last_estimate["auxiliary_group_task_workload"][0])
        self.assertGreater(pending.last_estimate["auxiliary_group_task_workload"][1],
                           advanced.last_estimate["auxiliary_group_task_workload"][1])
        self.assertGreater(advanced.last_estimate["paid_type_target_mass"],
                           pending.last_estimate["paid_type_target_mass"])
        # Remaining task allocation is always uniform across coordinates.
        marginal = advanced.weights[:advanced.L].reshape(advanced.d, 2).sum(axis=1)
        np.testing.assert_allclose(marginal, np.full(advanced.d, marginal[0]), atol=0, rtol=0)

    def test_zero_task_proxy_work_keeps_full_type_target_until_resolved(self):
        policy = self.make_policy()
        estimate = policy._estimate()
        for g, members in enumerate(policy.groups):
            for j in members:
                policy.counts[j, estimate["z"][g], estimate["theta"][j]] += 1000
        policy._update()
        self.assertEqual(policy.last_estimate["auxiliary_total_task_workload"], 0.)
        self.assertAlmostEqual(policy.last_estimate["paid_type_target_mass"], 1.)
        np.testing.assert_array_equal(policy.weights[:policy.L], np.zeros(policy.L))
        self.assertTrue(all(x > 0 for x in policy.last_estimate["auxiliary_type_deficit"]))
        # Once both auxiliary workloads clear, regular D-RRC resumes.
        policy.types = [[0] * 100, [1] * 100]
        policy._update()
        self.assertEqual(policy.last_estimate["paid_type_target_mass"], 0.)
        reference = DRRCNoType(public_fixture(), {"high": [], "low": []}, 32)
        force_fixture(reference)
        reference._update()
        np.testing.assert_array_equal(policy.weights, reference.weights)

    def test_known_accuracy_and_current_risk_set_type_workloads(self):
        accurate = self.make_policy(public=public_fixture(accuracy=(.9, .6)))
        accurate._update()
        workloads = accurate.last_estimate["auxiliary_type_workload"]
        self.assertLess(workloads[0], workloads[1])
        high_risk = self.make_policy(risk=128)
        low_risk = self.make_policy(risk=32)
        for policy in (high_risk, low_risk):
            policy.types = [[0] * 20, [1] * 20]
            policy._update()
        for g in range(2):
            self.assertGreater(high_risk.last_estimate["auxiliary_type_deficit"][g],
                               low_risk.last_estimate["auxiliary_type_deficit"][g])
        expected = 128 + math.log(2 * high_risk.d + 2 * high_risk.G)
        self.assertEqual(high_risk.last_estimate["auxiliary_threshold"], expected)

    @patch("phase2b.aligned.solve_allocation", side_effect=AssertionError("D-RRC-Type called joint optimizer"))
    def test_continual_1600_step_fixture_cadence_tracking_and_no_optimizer(self, optimizer):
        policy = DRRCType(public_fixture(), {"high": [], "low": []}, 32)
        for step in range(1600):
            action = policy.next(range(policy.d))
            if action[0] == "type":
                # Both agreeing and conflicting reports occur, deterministically.
                report_count = len(policy.types[action[1]])
                result = {"format": "AB"[int(report_count % 5 == 0)]}
            else:
                result = {"answer": action[1] % 2}
            policy.observe(action, result)
            diag = policy.diagnostics()
            discrepancy = np.asarray(diag["actual_minus_target"])
            self.assertLessEqual(float(discrepancy.max()), diag["tracking_upper_bound"] + 1e-9)
            self.assertGreaterEqual(float(discrepancy.min()), diag["tracking_lower_bound"] - 1e-9)
            lower = math.isqrt(policy.t // policy.L)
            self.assertTrue(np.all(policy.forced.sum(axis=2) >= lower))
            self.assertTrue(np.all(policy.forced.sum(axis=2) <= lower + 1))
        self.assertTrue(all(len(reports) > 1 for reports in policy.types))
        self.assertGreater(len(policy.estimates), 20)
        self.assertGreater(policy.last_update / policy.t, .97)
        for current, following in zip(policy.estimates, policy.estimates[1:]):
            self.assertEqual(current["next_update"], following["online"])
            self.assertEqual(current["next_update"], current["online"] + math.ceil(math.sqrt(current["online"] + 1)))
        self.assertEqual(int(policy.counts.sum()) + sum(map(len, policy.types)), 1600)
        optimizer.assert_not_called()

    def test_type_unavailable_falls_back_exactly_to_frozen_d_target(self):
        public = public_fixture(accuracy=None)
        first = self.make_policy(public=public)
        second = DRRCNoType(public, {"high": [], "low": []}, 32)
        force_fixture(second)
        for policy in (first, second):
            policy._update()
        np.testing.assert_array_equal(first.weights, second.weights)

    def test_telemetry_and_factory_are_explicit_and_fail_closed(self):
        self.assertEqual(set(SAMPLERS), {"Aligned-Full", "Aligned-NoType", "D-RRC-NoType", "D-RRC-Type"})
        policy = construct_sampler("D-RRC-Type", public_fixture(), {"high": [], "low": []}, 32)
        force_fixture(policy)
        policy._update()
        entry = policy.last_estimate
        for key in ("auxiliary_threshold", "auxiliary_task_workload", "auxiliary_type_workload",
                    "paid_type_target_mass", "update_seconds", "update_cpu_seconds", "next_update"):
            self.assertIn(key, entry)
        for key in ("estimated_K", "lower_bound", "upper_bound", "solver_seconds"):
            self.assertNotIn(key, entry)
        self.assertEqual(entry["auxiliary_scope"], "allocation_proxies_only_not_a_stopping_certificate")
        with self.assertRaises(KeyError):
            construct_sampler("unknown", public_fixture(), {"high": [], "low": []}, 32)


if __name__ == "__main__":
    unittest.main()
