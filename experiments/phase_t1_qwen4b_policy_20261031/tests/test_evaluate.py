"""Synthetic technical tests only: no generated worlds, model calls or training."""

from copy import deepcopy
import json
import math
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from t1.core import STATE_KEYS, build_state, quantize_percent, uniform_legal
from t1.evaluate import (
    EvaluationDeadline, InferenceBudget, InferenceLimit, METHODS, allocation_metrics,
    call_predictor, evaluate_offline, evaluate_world, paired_recovery,
    percent_round, plugin_information, summarize_paths,
)
from t1.mlp import _training_arrays, train_mlp


def fixture_state(partition=(2, 2), M=64):
    groups, start = [], 0
    for length in partition:
        groups.append({"targets": list(range(start, start + length))})
        start += length
    public = {"d": 4, "groups": groups, "type_accuracy": [.8] * len(groups),
              "rate_domain": {"eta": .05}}
    counts = [[[1, 3], [2, 2]] for _ in range(4)]
    calibration = {"high": [1] * M, "low": [0] * M}
    return build_state(public, calibration, counts, counts, [[0, 0] for _ in groups], 64, 2048)


def uniform_prediction(state):
    return {"weights10": uniform_legal(state).tolist(), "valid": True,
            "raw": "synthetic fixture", "prompt_tokens": 11, "output_tokens": 7}


def row_for(state, split="id_test", world="fixture"):
    weights = uniform_legal(state).tolist()
    return {"state": state, "teacher_weights": weights,
            "teacher_percent": quantize_percent(weights, state),
            "split": split, "world_id": world, "row_id": world + "_0"}


class FakeEnvironment:
    """Entirely deterministic responses; no QRelBench world generation."""

    def __init__(self, M=64):
        self.M = M
        self.cost = {"task": 0, "type": 0, "offline": 0}
        self.truth = [0, 1, 0, 1]
        self.submitted = None

    def reset(self):
        return {"d": 4, "groups": [{"targets": [0, 1]}, {"targets": [2, 3]}],
                "type_accuracy": [.8, .8], "rate_domain": {"eta": .05},
                "theta": "must_not_enter_student_input", "seed": "private_fixture"}

    def get_calibration(self):
        self.cost["offline"] = 2 * self.M
        return {"high": [1] * self.M, "low": [0] * self.M}

    def query(self, j, fmt):
        if sum(self.cost[k] for k in ("task", "type")) >= 2048:
            raise AssertionError("Exceeded public cap")
        self.cost["task"] += 1
        return {"answer": self.truth[j]}

    def ask_type(self, group):
        self.cost["type"] += 1
        return {"format": "AB"[group % 2]}

    def submit(self, predictions):
        self.submitted = predictions

    def score(self):
        return {"exact": self.submitted == self.truth, "costs": dict(self.cost)}


def fake_world(spec, seed):
    env = FakeEnvironment(spec.get("M", 64))
    return env, SimpleNamespace(truth=env.truth)


def fake_spec():
    return {"world_id": "synthetic_evaluation_fixture", "index": 0,
            "split": "eval_id", "online_cap": 2048, "M": 64}


def fake_fit(*args):
    return {"theta": [0, 1, 0, 1], "gap": 10000., "beta": 1.,
            "certified": True, "interval_certified": False}


class EvaluationTests(unittest.TestCase):
    def test_legal_fallback_keeps_invalid_raw_and_counts_call(self):
        state = fixture_state((4,))
        raw = {"weights10": [0.] * 9 + [1.], "valid": True,
               "raw": "illegal padded action", "prompt_tokens": 13, "output_tokens": 9}
        budget = InferenceBudget(limit=2)
        result = call_predictor(lambda _: raw, state, method="BaseQwen", budget=budget, is_qwen=True)
        self.assertEqual(budget.calls, 1)
        self.assertFalse(result["valid"])
        self.assertTrue(result["fallback"])
        self.assertEqual(result["prediction"], raw)
        self.assertEqual(result["weights10"], uniform_legal(state).tolist())
        self.assertEqual(result["weights10"][-1], 0)
        self.assertEqual(result["prompt_tokens"], 13)
        with self.assertRaises(ValueError):
            call_predictor(lambda _: raw, state, method="MLP")

    def test_budget_deadline_and_canonical_input_boundaries(self):
        state = fixture_state()
        budget = InferenceBudget(limit=1)
        received = []
        def predictor(value):
            received.append(value)
            self.assertEqual(set(value), STATE_KEYS)
            value["counts"][0][0][0] += 1
            return uniform_prediction(state)
        call_predictor(predictor, state, method="LoRA", budget=budget, is_qwen=True)
        self.assertEqual(state["counts"][0][0][0], 1)
        with self.assertRaises(InferenceLimit):
            call_predictor(predictor, state, method="LoRA", budget=budget, is_qwen=True)
        self.assertEqual(len(received), 1)
        with self.assertRaises(EvaluationDeadline):
            call_predictor(predictor, state, method="MLP", deadline=perf_counter() - 1)
        contaminated = deepcopy(state)
        contaminated["teacher_estimate"] = {"p": .9}
        with self.assertRaises(ValueError):
            call_predictor(predictor, contaminated, method="MLP")

    def test_percent_rounding_and_forward_kl_include_all_legal_actions(self):
        state = fixture_state((4,))
        weights = uniform_legal(state).tolist()
        rounded = percent_round(weights, state["action_mask"])
        self.assertEqual(rounded, quantize_percent(weights, state))
        self.assertEqual(sum(rounded), 100)
        self.assertEqual(rounded[-1], 0)
        metrics = allocation_metrics(weights, weights, state["action_mask"], rounded)
        self.assertEqual(metrics["allocation_l1"], 0)
        self.assertLess(metrics["forward_kl_epsilon_1e8"], 1e-12)
        self.assertTrue(metrics["percent_exact"])
        corner = [1.] + [0.] * 9
        shifted = allocation_metrics(weights, corner, state["action_mask"], rounded)
        self.assertTrue(math.isfinite(shifted["forward_kl_epsilon_1e8"]))
        self.assertGreater(shifted["allocation_l1"], 1)

    def test_information_metric_matches_frozen_inner_with_alpha_over_K(self):
        from phase2a.coefficients import alternatives, inner, kl
        state = fixture_state()
        estimate = {"p": .8, "q": .6, "z": [0, 1]}
        # Four good task weights .15, four low .05, two type weights .1.
        weights = [.15, .05, .15, .05, .05, .15, .05, .15, .1, .1]
        K = 5.
        coefficient_weights = [.15, .15, .05, .05, .1, .1]
        rho = (64 / 64) / K
        kappa = [kl(.8, .2), kl(.8, .2)]
        reference = min(inner([2, 2], .8, .6, rho, coefficient_weights, mask, group, kappa, .05)["value"]
                        for mask, group in alternatives(2))
        actual = plugin_information(state, weights, estimate, K)
        self.assertAlmostEqual(actual, reference, places=12)
        wrong_alpha = min(inner([2, 2], .8, .6, 1., coefficient_weights, mask, group, kappa, .05)["value"]
                          for mask, group in alternatives(2))
        self.assertGreater(abs(actual - wrong_alpha), 1e-5)
        # Nonuniform allocations must not be group-averaged: three entirely
        # unobserved signs yield zero information even with labelled references.
        self.assertAlmostEqual(plugin_information(state, [1.] + [0.] * 9, estimate, K), 0., places=12)

    def test_offline_retains_invalids_full_denominators_and_partial_receipt(self):
        rows = [row_for(fixture_state(), split, str(i))
                for i, split in enumerate(("id_test", "ood_parameters", "ood_partition"))]
        budget, saved = InferenceBudget(limit=2), []
        bad = lambda _: {"raw": "not json", "valid": False, "error": "parse failure"}
        result = evaluate_offline(rows, bad, method="BaseQwen", budget=budget, is_qwen=True,
                                  on_record=lambda record: saved.append(deepcopy(record)))
        self.assertEqual(result["status"], "interrupted")
        self.assertEqual(result["summary"]["states"], 3)
        self.assertEqual(result["summary"]["recorded_states"], 2)
        self.assertEqual(result["summary"]["invalid_fallbacks"], 2)
        self.assertEqual(result["summary"]["not_run_states"], 1)
        self.assertEqual(result["summary"]["by_split"]["ood_partition"]["states"], 1)
        self.assertEqual(result["summary"]["by_split"]["ood_partition"]["not_run_states"], 1)
        self.assertEqual(len(saved), 2)
        self.assertTrue(all(r["prediction"]["raw"] == "not json" for r in saved))
        self.assertEqual(result["summary"]["allocation_l1"]["denominator"], 2)
        self.assertEqual(result["summary"]["allocation_l1"]["requested_states"], 3)

    def test_fixed_budget_shared_scheduler_readouts_and_hidden_metadata_exclusion(self):
        states, events = [], []
        def predictor(state):
            states.append(deepcopy(state))
            self.assertEqual(set(state), STATE_KEYS)
            return uniform_prediction(state)
        with patch("t1.data.make_world", side_effect=fake_world), \
             patch("t1.evaluate._common_fit", side_effect=fake_fit):
            result = evaluate_world(fake_spec(), "never_used", {"MLP": predictor}, on_event=events.append)
        self.assertEqual(result["status"], "completed")
        path = result["records"][0]
        self.assertEqual([s["online"] for s in states], [8, 136, 264, 392])
        self.assertTrue(all(s["online_cap"] == 2048 for s in states))
        self.assertEqual([s["online"] for s in path["snapshots"]], [256, 512])
        self.assertEqual(path["online"], 512)
        self.assertEqual(sum(path["costs"][k] for k in ("task", "type")), 512)
        self.assertEqual(path["costs"]["offline"], 128)
        self.assertEqual(path["inference_calls"], 4)
        self.assertIsNone(path["strictly_certified_output"])
        self.assertFalse(path["complete"])
        self.assertNotIn("evaluation_truth", path)
        self.assertEqual(len(path["action_trace"]), 512)
        self.assertEqual(sum(event["kind"] == "action" for event in events), 512)
        self.assertEqual(events[-1]["kind"], "path_result")

    def test_strict_diagnostic_never_uses_floating_crossing_then_accepts(self):
        decisions = [{"certified": False, "status": "undetermined"},
                     {"certified": True, "status": "certified"}]
        with patch("t1.data.make_world", side_effect=fake_world), \
             patch("t1.evaluate._common_fit", side_effect=fake_fit), \
             patch("t1.evaluate._strict_gate", side_effect=decisions):
            result = evaluate_world(fake_spec(), "never_used", {"MLP": uniform_prediction}, R=16, diagnostic=True)
        path = result["records"][0]
        self.assertEqual(path["online"], 256)
        self.assertEqual([s["online"] for s in path["gate_history"]], [128, 256])
        self.assertTrue(path["complete"])
        self.assertFalse(path["abstained"])
        self.assertEqual(path["strictly_certified_output"], [0, 1, 0, 1])
        self.assertEqual(path["alpha_effective"], 4)

    def test_strict_cap_abstention_and_16_call_bound(self):
        budget = InferenceBudget(limit=16)
        with patch("t1.data.make_world", side_effect=fake_world), \
             patch("t1.evaluate._common_fit", side_effect=fake_fit), \
             patch("t1.evaluate._strict_gate", return_value={"certified": False, "status": "undetermined"}):
            result = evaluate_world(fake_spec(), "never_used", {"BaseQwen": uniform_prediction},
                                    R=16, diagnostic=True, budget=budget)
        path = result["records"][0]
        self.assertEqual(path["online"], 2048)
        self.assertEqual(budget.calls, 16)
        self.assertEqual(len(path["gate_history"]), 16)
        self.assertTrue(path["abstained"])
        self.assertIsNone(path["strictly_certified_output"])
        self.assertEqual(path["final_guess"], [0, 1, 0, 1])
        self.assertTrue(path["final_guess_exact"])

    def test_interrupted_world_retains_partial_calls_and_stops_next_methods(self):
        budget, events = InferenceBudget(limit=1), []
        with patch("t1.data.make_world", side_effect=fake_world), \
             patch("t1.evaluate._common_fit", side_effect=fake_fit):
            result = evaluate_world(fake_spec(), "never_used", {"BaseQwen": uniform_prediction, "LoRA": uniform_prediction},
                                    budget=budget, on_event=events.append)
        self.assertEqual(result["status"], "interrupted")
        self.assertEqual(result["not_run_methods"], ["LoRA"])
        path = result["records"][0]
        self.assertEqual(path["online"], 136)
        self.assertEqual(path["error"]["type"], "InferenceLimit")
        self.assertEqual(len(path["predictions"]), 1)
        self.assertEqual(len(path["action_trace"]), 136)
        self.assertEqual(sum(e["kind"] == "prediction" for e in events), 1)

    def test_summaries_include_wholly_missing_methods_and_world_pairs(self):
        with patch("t1.data.make_world", side_effect=fake_world), \
             patch("t1.evaluate._common_fit", side_effect=fake_fit):
            result = evaluate_world(fake_spec(), "never_used", {"MLP": uniform_prediction})
        records = result["records"]
        worlds = [fake_spec()["world_id"], "missing_world"]
        summary = summarize_paths(records, expected_world_ids=worlds)
        self.assertEqual(set(summary), set(METHODS))
        self.assertEqual(summary["MLP"]["readouts"]["512"]["denominator"], 2)
        self.assertEqual(summary["MLP"]["readouts"]["512"]["observed_readouts"], 1)
        self.assertEqual(summary["BaseQwen"]["missing_paths"], 2)
        paired = paired_recovery(records, "MLP", "LoRA", expected_world_ids=worlds)
        self.assertEqual(paired["denominator"], 2)
        self.assertEqual(paired["missing_pairs"], 2)

    def test_mlp_preprocessing_does_not_use_label_metadata_as_features(self):
        state = fixture_state()
        clean = row_for(state)
        poisoned = {**clean, "teacher_estimate": object(), "teacher_K": object(), "truth": object()}
        self.assertEqual(_training_arrays([clean]), _training_arrays([poisoned]))
        self.assertEqual(len(_training_arrays([clean])[0][0]), 69)

    def test_mlp_failure_receipt_and_no_automatic_retry_without_training(self):
        def fail_without_training(rows, destination, **kwargs):
            kwargs["progress"]({"completed_epochs": 2, "optimizer_updates": 2, "synthetic_fixture": True})
            raise RuntimeError("synthetic pre-training failure")
        with TemporaryDirectory() as directory, \
             patch("t1.mlp._train_mlp_once", side_effect=fail_without_training) as fake:
            with self.assertRaisesRegex(RuntimeError, "synthetic"):
                train_mlp([], directory)
            failed = json.loads((Path(directory) / "mlp_failed.json").read_text())
            self.assertEqual(failed["completed_epochs"], 2)
            self.assertFalse(failed["automatic_retry"])
            self.assertTrue((Path(directory) / "mlp_started.json").exists())
            with self.assertRaises(FileExistsError):
                train_mlp([], directory)
            self.assertEqual(fake.call_count, 1)


if __name__ == "__main__":
    unittest.main()
