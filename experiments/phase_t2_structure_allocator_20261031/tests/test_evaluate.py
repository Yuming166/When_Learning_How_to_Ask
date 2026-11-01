"""Hand-built deterministic environment fixtures; no scientific world generation."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from t2 import evaluate
from t2.core import validate_state
from phase2b.aligned import TheoryAlignedTracking
from phase2e.strategies import FusedOriginal


def fixture_spec(d=4, cap=96, groups=None):
    return {"world_id": "unit-fixture-not-a-scientific-world", "kind": "unit_test",
            "partition": groups or [d], "online_cap": cap, "alpha": .5, "R": 64}


class HandEnvironment:
    """Plain hand fixture; no random seed or hidden scientific generator."""
    def __init__(self, spec, R):
        d, cursor, groups = sum(spec["partition"]), 0, []
        for size in spec["partition"]:
            groups.append({"targets": list(range(cursor, cursor + size))})
            cursor += size
        self.public = {"d": d, "groups": groups, "rate_domain": {"eta": .05},
                       "type_accuracy": [.8] * len(groups)}
        self.cost = {"task": 0, "type": 0, "offline": 0}
        M = int(round(spec["alpha"] * R))
        self.calibration = {"high": [1] * M, "low": [0, 1] * (M // 2) + [0] * (M % 2)}
        self.queries = []

    def reset(self):
        return deepcopy(self.public)

    def get_calibration(self):
        self.cost["offline"] = 2 * len(self.calibration["high"])
        return deepcopy(self.calibration)

    def query(self, j, mode):
        self.cost["task"] += 1
        self.queries.append((j, mode))
        return {"answer": int((j + self.cost["task"] + (mode == "B")) % 2)}

    def ask_type(self, group):
        self.cost["type"] += 1
        return {"format": "AB"[self.cost["type"] % 2]}


def hand_world(spec, seed, R):
    assert seed == "unit-fixture-only"
    env = HandEnvironment(spec, R)
    return env, SimpleNamespace(truth=[0] * sum(spec["partition"]))


def fit_fixture(counts, groups, cal, types, accuracy, R, eta=.05):
    return {"theta": [0] * len(counts), "gap": 0., "beta": float(R), "interval_certified": False}


class ObservablePredictor:
    def __init__(self, t1=False, fail=False):
        self.t1, self.fail, self.states, self.calls = t1, fail, [], 0

    def predict(self, state):
        self.calls += 1
        self.states.append(deepcopy(state))
        if self.fail:
            raise RuntimeError("deliberate unit predictor failure")
        if self.t1:
            assert state["schema"] == "t1_observable_v1"
            assert "estimate" not in state and "world_id" not in state and "truth" not in state
            weights = np.zeros(10)
            weights[8] = 1.
            return {"weights10": weights.tolist(), "valid": True}
        validate_state(state)
        weights = np.zeros(len(state["action_mask"]))
        weights[2 * state["d"]] = 1.
        return weights


class ToyFrozen(TheoryAlignedTracking):
    """Schedule-only fixture with the actual inherited forcing/tracking code."""
    def _estimate(self):
        return {"p": .8, "q": .6, "z": [0] * self.G}

    def _update(self):
        estimate = self._estimate()
        self.weights[:] = 0
        self.weights[:self.L:2] = 1 / self.d
        self.last_estimate = estimate
        self.last_update, self.next_update = self.t, self.t + 3


class EvaluateTests(unittest.TestCase):
    def run_fixture(self, method="T2-MLP", *, cap=96, readouts=(16, 64), R=16,
                    predictor=None, fit=fit_fixture, gate=None, spec=None, baselines=None):
        spec = fixture_spec(cap=cap) if spec is None else spec
        predictor = ObservablePredictor(t1=method == "T1-MLP") if predictor is None else predictor
        gate = (lambda *a, **kw: {"certified": False, "status": "unit_not_certified"}) if gate is None else gate
        with patch.object(evaluate, "ONLINE_CAP", cap), patch.object(evaluate, "make_world", side_effect=hand_world) as world_mock, \
             patch.object(evaluate, "log_glr", side_effect=fit) as glr_mock, \
             patch.object(evaluate, "certify_stop", side_effect=gate) as gate_mock:
            if baselines is None:
                result = evaluate.evaluate_path(spec, "unit-fixture-only", R, method, {method: predictor}, readouts)
            else:
                with patch.object(evaluate, "BASELINES", baselines):
                    result = evaluate.evaluate_path(spec, "unit-fixture-only", R, method, {method: predictor}, readouts)
        return result, predictor, world_mock, glr_mock, gate_mock

    def assert_receipt(self, row):
        self.assertEqual(row["costs"]["task"] + row["costs"]["type"], row["online"])
        self.assertEqual(row["total_acquisition"], row["online"] + row["costs"]["offline"])
        self.assertEqual(len(row["action_trace"]), row["online"])
        self.assertEqual(np.asarray(row["counts"]).sum(), row["costs"]["task"])
        self.assertEqual(sum(map(len, row["type_answers"])), row["costs"]["type"])
        d = len(row["counts"])
        reconstructed = np.zeros((d, 2, 2), dtype=int)
        forced_counts = np.zeros_like(reconstructed)
        for t, (index, bit, forced) in enumerate(row["action_trace"]):
            n = int(np.sqrt(t // (2 * d)))
            offset = t - 2 * d * n * n
            self.assertEqual(forced, int(offset < 2 * d))
            if forced:
                self.assertEqual(index, offset)
            if index < 2 * d:
                reconstructed[index // 2, index % 2, bit] += 1
                if forced:
                    forced_counts[index // 2, index % 2, bit] += 1
        np.testing.assert_array_equal(row["counts"], reconstructed)
        np.testing.assert_array_equal(row["forced_counts"], forced_counts)
        self.assertEqual(row["provider_model_calls"], 0)
        self.assertEqual(row["gpu_calls"], 0)

    def test_cap_abstention_common_schedule_and_observable_boundary(self):
        row, predictor, _, glr, gate = self.run_fixture()
        self.assertEqual(row["status"], "completed")
        self.assertEqual(row["online"], 96)
        self.assertFalse(row["certified"])
        self.assertTrue(row["abstained"])
        self.assertIsNone(row["certified_exact"])
        self.assertEqual(row["glr_checks"], 3)
        self.assertEqual(glr.call_count, 4)  # 16 scores only; 32,64,96 are shared checks.
        self.assertEqual(gate.call_count, 1)
        self.assertEqual(row["gate_history"][0]["online"], 96)
        self.assertEqual([r["online"] for r in row["updates"]], [8, 40, 72])
        self.assertEqual([r["effective_online"] for r in row["readouts"]], [16, 64])
        self.assertEqual(predictor.calls, 3)
        self.assertGreater(row["timings"]["estimation"], 0)
        self.assertGreater(row["timings"]["inference"], 0)
        self.assertGreater(row["timings"]["score_glr"], 0)
        self.assert_receipt(row)

    def test_early_certification_absorbs_future_budget_readouts(self):
        def crossing(*args, **kwargs):
            out = fit_fixture(*args, **kwargs)
            out["gap"] = out["beta"] + 1
            return out
        row, _, _, glr, gate = self.run_fixture(readouts=(64, 96), fit=crossing,
                                               gate=lambda *a, **k: {"certified": True, "status": "unit_certified"})
        self.assertEqual(row["online"], 32)
        self.assertTrue(row["certified"])
        self.assertTrue(row["certified_exact"])
        self.assertFalse(row["abstained"])
        self.assertEqual(glr.call_count, 1)
        self.assertEqual(gate.call_count, 1)
        for snapshot in row["readouts"]:
            self.assertEqual(snapshot["effective_online"], 32)
            self.assertTrue(snapshot["absorbed"])
            self.assertEqual(snapshot["costs"], row["costs"])
            self.assertEqual(snapshot["counts"], row["counts"])
        self.assert_receipt(row)

    def test_scoring_only_crossing_cannot_invoke_gate_or_stop(self):
        def score_only_crossing(counts, *args, **kwargs):
            out = fit_fixture(counts, *args, **kwargs)
            total = int(np.asarray(counts).sum()) + sum(map(len, args[2]))
            if total == 16:
                out["gap"] = out["beta"] + 100
            return out
        row, _, _, _, gate = self.run_fixture(fit=score_only_crossing)
        self.assertEqual(row["online"], 96)
        self.assertEqual(gate.call_count, 1)
        self.assertFalse(row["readouts"][0]["certified"])

    def test_floating_crossing_requires_strict_acceptance(self):
        def crossing(*args, **kwargs):
            out = fit_fixture(*args, **kwargs)
            out["gap"] = out["beta"] + 1
            return out
        row, _, _, _, gate = self.run_fixture(fit=crossing)
        self.assertEqual(gate.call_count, 3)
        self.assertFalse(row["certified"])
        self.assertEqual(row["online"], 96)

    def test_native_and_matched_cadence_and_instance_instrumentation(self):
        self.assertIs(evaluate.BASELINES["Native-Fused-Original"], FusedOriginal)
        original_update, original_estimate = ToyFrozen._update, ToyFrozen._estimate
        mapping = {"Native-Fused-Original": ToyFrozen, "Fused-Original": ToyFrozen}
        native, *_ = self.run_fixture("Native-Fused-Original", baselines=mapping)
        matched, *_ = self.run_fixture("Fused-Original", baselines=mapping)
        self.assertEqual([r["online"] for r in native["updates"]][:4], [8, 11, 14, 17])
        self.assertEqual([r["online"] for r in matched["updates"]], [8, 40, 72])
        self.assertIs(ToyFrozen._update, original_update)
        self.assertIs(ToyFrozen._estimate, original_estimate)
        self.assertGreater(matched["timings"]["estimation"], 0)
        self.assertGreater(matched["timings"]["planning"], 0)
        self.assertEqual(matched["inference_calls"], 0)
        self.assert_receipt(native)
        self.assert_receipt(matched)

    def test_t1_uses_original_raw_state_without_posterior_and_actual_cap(self):
        with patch.object(evaluate, "observed_state", side_effect=AssertionError("T1 must not compute posterior")):
            row, predictor, *_ = self.run_fixture("T1-MLP")
        self.assertEqual(row["status"], "completed", row["error"])
        self.assertEqual(predictor.states[0]["online_cap"], 96)
        self.assertEqual(predictor.states[0]["remaining"], 88)
        self.assertIn("2048_normalization", row["t1_feature_scope"])
        self.assertEqual(len(row["updates"][0]["weights"]), 9)
        self.assert_receipt(row)

    def test_t1_variable_dimension_is_upfront_expected_noncoverage(self):
        row, predictor, world, glr, gate = self.run_fixture("T1-MLP", spec=fixture_spec(d=2))
        self.assertEqual(row["status"], "not_applicable")
        self.assertIsNone(row["error"])
        self.assertEqual(world.call_count, 0)
        self.assertEqual(predictor.calls, 0)
        self.assertEqual(glr.call_count, 0)
        self.assertEqual(gate.call_count, 0)
        self.assertEqual(row["total_acquisition"], 0)

    def test_prediction_failure_preserves_paid_prefix_and_never_retries(self):
        row, predictor, *_ = self.run_fixture(predictor=ObservablePredictor(fail=True), readouts=(4, 64))
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["online"], 8)
        self.assertEqual(predictor.calls, 1)
        self.assertEqual(row["inference_calls"], 1)
        self.assertEqual([r["budget"] for r in row["readouts"]], [4])
        self.assertFalse(row["automatic_retry"])
        self.assertIsNone(row["final_guess_exact"])
        self.assert_receipt(row)

    def test_R_is_supplied_before_calibration_and_costs_include_both_streams(self):
        row, _, world, *_ = self.run_fixture(R=256)
        self.assertEqual(world.call_args.args[2], 256)
        self.assertEqual(row["costs"]["offline"], 256)
        self.assertEqual(len(row["calibration"]["high"]), 128)
        self.assertEqual(row["alpha_effective"], .5)
        self.assert_receipt(row)

    def test_expired_deadline_stops_before_world_or_model_calls(self):
        with patch.object(evaluate, "make_world") as world:
            row = evaluate.evaluate_path(fixture_spec(cap=6144), "unit-fixture-only", 16,
                                         "T2-MLP", {}, (16, 64), deadline=0.)
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["error"]["type"], "TimeoutError")
        self.assertEqual(world.call_count, 0)
        self.assertEqual(row["online"], 0)

    def test_budget_development_stops_at128_with_public_cap6144_and_no_gate(self):
        predictor = ObservablePredictor()
        spec = fixture_spec(cap=6144)
        with patch.object(evaluate, "make_world", side_effect=hand_world), \
             patch.object(evaluate, "log_glr", side_effect=fit_fixture), \
             patch.object(evaluate, "certify_stop", side_effect=AssertionError("development cannot certify")) as gate:
            row = evaluate.evaluate_path(spec, "unit-fixture-only", 64, "T2-MLP",
                                         {"T2-MLP": predictor}, (8, 16, 32, 64, 96, 128), budget_only=True)
        self.assertEqual(row["status"], "completed", row["error"])
        self.assertEqual(row["mode"], "budget_development")
        self.assertEqual(row["online"], 128)
        self.assertEqual(row["online_cap"], 6144)
        self.assertEqual(predictor.states[0]["online_cap"], 6144)
        self.assertEqual(predictor.states[0]["remaining"], 6136)
        self.assertEqual(len(row["readouts"]), 6)
        self.assertFalse(row["certified"])
        self.assertIsNone(row["abstained"])
        self.assertEqual(gate.call_count, 0)
        self.assert_receipt(row)

    def test_progress_journal_blocks_reconstruct_paid_prefix_without_truth(self):
        events = []
        with patch.object(evaluate, "make_world", side_effect=hand_world), \
             patch.object(evaluate, "log_glr", side_effect=fit_fixture):
            row = evaluate.evaluate_path(fixture_spec(cap=6144), "unit-fixture-only", 64,
                                         "T2-MLP", {"T2-MLP": ObservablePredictor()}, (16, 64),
                                         budget_only=True, on_progress=events.append)
        self.assertEqual(row["status"], "completed", row["error"])
        reconstructed = []
        for event in events:
            self.assertNotIn("truth", event)
            self.assertNotIn("seed", event)
            self.assertNotIn("spec", event)
            self.assertEqual(event["action_trace_start"], len(reconstructed))
            reconstructed.extend(event["action_trace_block"])
            self.assertEqual(event["online"], len(reconstructed))
            self.assertEqual(event["costs"]["task"] + event["costs"]["type"], event["online"])
        self.assertEqual(reconstructed, row["action_trace"])
        self.assertEqual(events[-1]["event"], "completed")
        self.assertEqual(events[-1]["costs"], row["costs"])
        self.assertIn("before_scheduled_glr", [event["event"] for event in events])
        self.assertIn("before_estimation_and_allocation", [event["event"] for event in events])

    def test_real_baseline_and_warm_routing_on_hand_environment(self):
        for method in tuple(evaluate.BASELINES) + ("Warm-KL",):
            with self.subTest(method=method):
                row, *_ = self.run_fixture(method, cap=32, readouts=(16, 32))
                self.assertEqual(row["status"], "completed", row["error"])
                self.assertEqual(row["online"], 32)
                self.assert_receipt(row)


if __name__ == "__main__":
    unittest.main()
