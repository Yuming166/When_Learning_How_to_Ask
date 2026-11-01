"""Deterministic legal-input contracts; no scientific worlds, models or GPU."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from t1.core import (ACTION_DIM, FEATURE_DIM, STATE_KEYS, SYSTEM_PROMPT, CommonScheduler, build_state,
                     messages_for, parse_percent, quantize_percent, serialize_state, state_features,
                     teacher_target, uniform_legal, validate_state)
from t1.data import DATA_DEFAULTS, ORIGINAL_ROOT, collect_world, evaluation_world_plan, generate_dataset, sha256_file, verify_freeze, world_plan


def public_fixture(partition=(1, 3), types=True):
    start, groups = 0, []
    for size in partition:
        groups.append({"targets": list(range(start, start + size))})
        start += size
    public = {"d": start, "groups": groups, "rate_domain": {"eta": .05}}
    if types:
        public["type_accuracy"] = [.8] * len(groups)
    return public


def state_fixture(public=None):
    public = public or public_fixture()
    counts = np.array([[[2, 8], [4, 6]], [[8, 2], [6, 4]], [[4, 6], [2, 8]], [[6, 4], [8, 2]]])
    return build_state(public, {"high": [1, 1, 0], "low": [0, 1, 0]}, counts, counts,
                       np.zeros((len(public["groups"]), 2), dtype=int), 64, 2048)


class FakeEnvironment:
    """Handwritten functional responses, independent of any generated world."""
    def __init__(self):
        self.cost = {"task": 0, "type": 0, "offline": 0}
        self.log_digest = hashlib.sha256(b"deterministic-contract")

    def reset(self):
        return public_fixture()

    def get_calibration(self):
        self.cost["offline"] = 6
        return {"high": [1, 1, 0], "low": [0, 1, 0]}

    def query(self, j, fmt):
        self.cost["task"] += 1
        return {"answer": j % 2}

    def ask_type(self, group):
        self.cost["type"] += 1
        return {"format": "AB"[group % 2]}


def fake_target(state):
    weights = uniform_legal(state)
    return {"weights": weights.tolist(), "percent": quantize_percent(weights, state),
            "teacher_K": 2., "estimate": {"estimated_K": 2., "online": state["online"]}}


class TestCore(unittest.TestCase):
    def test_allowlist_and_hidden_value_invariance(self):
        public = public_fixture()
        first = state_fixture(public)
        public.update({"world_id": "secret-id", "seed": "secret-seed", "p": .9, "q": .51,
                       "theta": [1, 1, 1, 1], "z": [1, 1], "reward": 100, "oracle_format_types": ["B", "B"]})
        public["groups"][0]["private_type"] = 1
        second = state_fixture(public)
        self.assertEqual(serialize_state(first), serialize_state(second))
        np.testing.assert_array_equal(state_features(first), state_features(second))
        self.assertEqual(set(first), STATE_KEYS)
        self.assertEqual(state_features(first).shape, (FEATURE_DIM,))
        for key in ("world_id", "seed", "p", "theta", "reward"):
            invalid = deepcopy(first)
            invalid[key] = 1
            with self.assertRaises(ValueError):
                serialize_state(invalid)
        invalid = deepcopy(first)
        invalid["calibration"]["high"]["hidden_rate"] = .8
        with self.assertRaises(ValueError):
            serialize_state(invalid)
        self.assertEqual(messages_for(first)[0]["content"], SYSTEM_PROMPT)
        self.assertEqual(messages_for(first)[1]["content"], serialize_state(first))

    def test_percent_quantization_parser_and_padded_actions(self):
        state = state_fixture(public_fixture((4,)))
        weights = uniform_legal(state)
        percent = quantize_percent(weights, state)
        self.assertEqual(sum(percent), 100)
        self.assertEqual(percent[9], 0)
        self.assertEqual(percent[0], 12)  # deterministic lower-index remainder tie
        self.assertTrue(parse_percent(json.dumps(percent), state)["valid"])
        illegal = [0] * 10
        illegal[9] = 100
        invalid = ["```json\n[100,0,0,0,0,0,0,0,0,0]\n```", "[100]", json.dumps(illegal),
                   "[true,99,0,0,0,0,0,0,0,0]", "[100.0,0,0,0,0,0,0,0,0,0]", "[99,0,0,0,0,0,0,0,0,0]"]
        with patch("t1.core.teacher_target", side_effect=AssertionError("invalid output consulted teacher")):
            for text in invalid:
                result = parse_percent(text, state)
                self.assertFalse(result["valid"])
                self.assertIsNone(result["percent"])
                np.testing.assert_array_equal(result["weights"], weights)
        unavailable = state_fixture(public_fixture(types=False))
        illegal[9], illegal[8] = 0, 100
        self.assertFalse(parse_percent(json.dumps(illegal), unavailable)["valid"])

    def test_invalid_counts_and_budget_fail_closed(self):
        state = state_fixture()
        for key, value in (("online", 81), ("remaining", 1)):
            broken = deepcopy(state)
            broken[key] = value
            with self.assertRaises(ValueError):
                validate_state(broken)
        broken = deepcopy(state)
        broken["forced_counts"][0][0][0] += 1
        with self.assertRaises(ValueError):
            validate_state(broken)
        broken = deepcopy(state)
        broken["counts"] = np.full((4, 2, 2), np.uint64(2**64 - 1))
        with self.assertRaises(ValueError):
            validate_state(broken)

    def test_real_teacher_is_frozen_forced_only_update(self):
        from phase2b.aligned import TheoryAlignedTracking
        state = state_fixture()
        target = teacher_target(state)
        direct = TheoryAlignedTracking(public_fixture(), {"high": [0] * 3, "low": [1] * 3}, 64)
        direct.t = state["online"]
        direct.counts[:] = state["counts"]
        direct.forced[:] = state["forced_counts"]
        direct._update()
        np.testing.assert_array_equal(target["weights"], direct.weights)
        self.assertEqual(target["teacher_K"], direct.last_estimate["estimated_K"])
        changed = deepcopy(state)
        changed["calibration"]["high"]["successes"] = 0
        changed["calibration"]["low"]["successes"] = 3
        other = teacher_target(changed)
        np.testing.assert_array_equal(target["weights"], other["weights"])
        self.assertEqual(sum(target["percent"]), 100)

    @patch("phase2b.aligned.solve_allocation", side_effect=AssertionError("scheduler invoked teacher"))
    def test_forced_schedule_block_updates_and_tracking_bounds(self, optimizer):
        scheduler = CommonScheduler(public_fixture(), {"high": [], "low": []}, 64)
        updates = []
        for t in range(1024):
            if scheduler.needs_update():
                updates.append(t)
                with self.assertRaises(RuntimeError):
                    scheduler.next(range(4))
                scheduler.set_target(uniform_legal(scheduler.state()))
            offset = t - 8 * math.isqrt(t // 8) ** 2
            expected_forced = offset if offset < 8 else None
            action = scheduler.next(range(4))
            if expected_forced is not None:
                self.assertEqual(action, ("query", offset // 2, "AB"[offset % 2]))
            result = {"format": "A"} if action[0] == "type" else {"answer": action[1] % 2}
            scheduler.observe(action, result)
            diag = scheduler.diagnostics()
            discrepancy = np.asarray(diag["actual_minus_target"])
            self.assertLessEqual(discrepancy.max(), diag["tracking_upper_bound"] + 1e-8)
            self.assertGreaterEqual(discrepancy.min(), diag["tracking_lower_bound"] - 1e-8)
        self.assertEqual(updates, list(range(8, 1024, 128)))
        optimizer.assert_not_called()


class TestData(unittest.TestCase):
    def test_world_split_isolation_balancing_and_holdouts(self):
        config = {"data": DATA_DEFAULTS}
        data, evaluation = world_plan(config), evaluation_world_plan(config)
        self.assertEqual((len(data), len(evaluation)), (96, 24))
        self.assertEqual(len({r["index"] for r in data + evaluation}), 120)
        self.assertEqual(len({r["world_id"] for r in data + evaluation}), 120)
        train = [r for r in data if r["split"] == "train"]
        self.assertEqual(len(train), 64)
        self.assertEqual(len({(tuple(r["partition"]), r["p"], r["q"], r["alpha"], r["R"]) for r in train}), 16)
        for split in ("validation", "id_test"):
            rows = [r for r in data if r["split"] == split]
            self.assertEqual(sum(r["partition"] == [4] for r in rows), 4)
            self.assertEqual(sum(r["R"] == 64 for r in rows), 4)
        self.assertTrue(all((r["p"], r["q"]) == (.85, .6) for r in data if r["split"] == "ood_parameters"))
        self.assertTrue(all(r["partition"] == [2, 2] for r in data if r["split"] == "ood_partition"))
        self.assertTrue(all(r["partition"] != [2, 2] for r in train))
        self.assertTrue(all(r["R"] == 64 for r in evaluation))
        self.assertEqual(96 * 16, 1536)
        self.assertEqual(64 * 16, 1024)
        with self.assertRaises(ValueError):
            world_plan({"data": {"snapshot_interval": 64}})

    @patch("t1.data.teacher_target", side_effect=fake_target)
    def test_collection_is_predecision_exact_16_and_separates_hidden_source(self, teacher):
        episode = SimpleNamespace(provenance={"private_seed": "never-student"}, truth=[1, 0, 1, 0], types=[0, 1], records=[])
        spec = world_plan({})[0]
        with patch("t1.data.make_world", return_value=(FakeEnvironment(), episode)):
            rows, private = collect_world(spec, "not-used-by-functional-fixture")
        self.assertEqual(len(rows), 16)
        self.assertEqual([row["state"]["online"] for row in rows], [8 + 128 * k for k in range(16)])
        self.assertEqual(teacher.call_count, 16)
        self.assertEqual(private["online_actions"], 1928)
        self.assertTrue(all(row["teacher_estimate"]["online"] == row["state"]["online"] for row in rows))
        self.assertTrue(all(row["state"]["remaining"] == 2048 - row["state"]["online"] for row in rows))
        self.assertNotIn("never-student", json.dumps(rows))
        self.assertNotIn("truth", rows[0]["state"])

    def test_failed_world_retains_legal_partial_state_and_costs(self):
        episode = SimpleNamespace(provenance={"seed": "private"}, truth=[0] * 4, types=[0, 1], records=[])
        with patch("t1.data.make_world", return_value=(FakeEnvironment(), episode)), \
             patch("t1.data.teacher_target", side_effect=RuntimeError("contract failure")):
            with self.assertRaises(RuntimeError) as caught:
                collect_world(world_plan({})[0], "not-used")
        partial = caught.exception.t1_partial
        self.assertEqual(partial["online_actions"], 8)
        self.assertEqual(partial["costs"], {"task": 8, "type": 0, "offline": 6})
        self.assertEqual(partial["partial_observable_state"]["online"], 8)
        self.assertEqual(partial["completed_labels"], [])

    def test_generation_refuses_missing_freeze_before_creating_any_world(self):
        with tempfile.TemporaryDirectory() as folder, patch("t1.data.make_world") as make_world:
            with self.assertRaises((ValueError, FileNotFoundError)):
                generate_dataset({}, Path(folder) / "data", "not-used", Path(folder) / "missing.json")
            make_world.assert_not_called()

    def test_freeze_binds_source_config_and_historical_dependencies(self):
        config = {"data": DATA_DEFAULTS}
        required = ["phase2b_alignment_20261031/phase2b/aligned.py", "phase2a_theory_optimality_20261030/phase2a/coefficients.py",
                    "qrelbench_v01_20261030/qrelbench/data.py", "qrelbench_v01_20261030/qrelbench/environment.py",
                    "qrelbench_v01_20261030/qrelbench/randomness.py"]
        with tempfile.TemporaryDirectory(prefix="t1-freeze-contract-") as folder:
            base = Path(folder)
            (base / "t1").mkdir()
            for name in ("core.py", "data.py"):
                (base / "t1" / name).write_bytes((ROOT / "t1" / name).read_bytes())
            (base / "config.json").write_text(json.dumps(config))
            freeze = {"files": {name: sha256_file(base / name) for name in ("t1/core.py", "t1/data.py", "config.json")},
                      "dependencies": {str(ORIGINAL_ROOT / "experiments" / name): sha256_file(ORIGINAL_ROOT / "experiments" / name) for name in required}}
            path = base / "freeze.json"
            path.write_text(json.dumps(freeze))
            with patch("t1.data.ROOT", base):
                self.assertEqual(verify_freeze(config, path), sha256_file(path))
                (base / "t1/core.py").write_text("# deliberately changed contract fixture\n")
                with self.assertRaisesRegex(ValueError, "changed"):
                    verify_freeze(config, path)

    def test_failed_generation_manifest_and_private_permissions_preserve_cost(self):
        spec = world_plan({})[0]
        failure = RuntimeError("deterministic failure fixture")
        failure.t1_partial = {"world_id": spec["world_id"], "spec": spec, "online_actions": 8,
                              "costs": {"task": 8, "type": 0, "offline": 6}, "completed_labels": [],
                              "partial_observable_state": state_fixture(), "private_seed": "never-public"}
        with tempfile.TemporaryDirectory(prefix="t1-failure-contract-") as folder:
            base = Path(folder)
            out = base / "data"
            with patch("t1.data.ROOT", base), patch("t1.data.verify_freeze", return_value="fixture-freeze"), \
                 patch("t1.data.world_plan", return_value=[spec]), patch("t1.data.collect_world", side_effect=failure):
                with self.assertRaisesRegex(RuntimeError, "deterministic failure"):
                    generate_dataset({}, out, "private-fixture", base / "freeze.json")
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "failed")
            self.assertEqual(manifest["current_world_id"], spec["world_id"])
            self.assertEqual(manifest["generated_online_actions"], 8)
            self.assertEqual(manifest["unique_generated_offline_observations"], 6)
            self.assertNotIn("never-public", json.dumps(manifest))
            private = out / manifest["failed_world"]["private_file"]
            self.assertEqual(private.stat().st_mode & 0o777, 0o600)
            self.assertEqual(private.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(json.loads(private.read_text())["private_seed"], "never-public")


if __name__ == "__main__":
    unittest.main()
