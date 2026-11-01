"""Bounded technical fixtures only; no development/confirmation seed access."""

from copy import deepcopy
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_PATH))

from phase2d.policy import POLICIES, run_policy, worker
from phase2d.runner import ROOT, evaluate_job, jobs, public_job
from phase2b.log_glr import log_glr
from qrelbench.rpc import send


TECHNICAL_SEED = "separate-phase2d-technical-fixture"


def technical_job(R=16, M=0, mode="floating"):
    return {
        "partition": [1, 3], "alpha": M / R, "R": R, "index": 419000,
        "replicate": 0, "p": .85, "q": .6, "s": .8, "eta": .05,
        "M": M, "online_cap": 64, "check_every": 16,
        "milestones": [32, 64], "stop_mode": mode, "channel": "iid",
        "protocol": "fixed_confidence", "scenario": "technical_unit_fixture",
    }


class FakeClient:
    """No simulator: deterministic public responses for control-flow tests."""

    def __init__(self):
        self.queries = []
        self.snapshots = []
        self.submissions = []

    def reset(self):
        return {"d": 1, "groups": [{"targets": [0]}],
                "rate_domain": {"eta": .05}, "type_accuracy": [.8]}

    def get_calibration(self):
        return {"high": [], "low": []}

    def query(self, j, fmt):
        self.queries.append((j, fmt))
        return {"answer": 1}

    def ask_type(self, group):
        raise AssertionError("NoType sampler requested a type action")

    def _call(self, method, **args):
        if method != "snapshot":
            raise AssertionError("Unexpected fake RPC")
        self.snapshots.append(deepcopy(args["snapshot"]))
        return {"recorded": True}

    def submit(self, predictions):
        self.submissions.append(list(predictions))
        return {}


def high_floating_fit(*args, **kwargs):
    # Deliberately authorize only the approximate prefilter. The strict gate
    # must still determine whether any output is certified.
    return {"theta": [1], "gap": 10000., "beta": 1.,
            "certified": True, "interval_certified": False}


class IntegrationTests(unittest.TestCase):
    def test_declared_plan_caps_and_public_job_scope(self):
        cfg = json.loads((ROOT / "config.json").read_text())
        plan = jobs(cfg)
        self.assertEqual(len(plan), 64)
        self.assertEqual(len({job["index"] for job in plan}), 64)
        self.assertEqual(len(POLICIES), 4)
        self.assertEqual(len(plan) * len(POLICIES), 256)
        self.assertEqual(sum(job["online_cap"] for job in plan) * len(POLICIES), 2_228_224)
        self.assertLessEqual(sum(job["online_cap"] for job in plan) * len(POLICIES),
                             cfg["limits"]["online_actions"])
        for job in plan:
            self.assertEqual(set(public_job(job)),
                             {"R", "online_cap", "check_every", "milestones", "stop_mode"})
            self.assertEqual(job["stop_mode"], "floating")
            self.assertLessEqual(job["check_every"], 32)

    def test_actual_confined_four_arm_workers_and_common_glr(self):
        total = {"task": 0, "type": 0, "offline": 0}
        context = mp.get_context("spawn")
        for name in POLICIES:
            parent, child = context.Pipe()
            process = context.Process(target=worker, args=(child, name))
            process.start()
            child.close()
            try:
                for R, M, mode in ((16, 0, "floating"), (1024, 3, "certified")):
                    with self.subTest(policy=name, R=R, M=M, mode=mode):
                        job = technical_job(R, M, mode)
                        counters = {"task": 0, "type": 0, "offline": 0}
                        final, _, snapshots = evaluate_job(
                            parent, name, job, TECHNICAL_SEED, time.monotonic() + 60, counters)
                        for key in total:
                            total[key] += counters[key]
                        self.assertEqual(final["online"], 64)
                        self.assertEqual(counters["task"] + counters["type"], 64)
                        self.assertEqual(counters["offline"], 2 * M)
                        self.assertEqual([s["online"] for s in snapshots], [32, 64])
                        self.assertTrue(final["censored"])
                        self.assertFalse(final["complete"])
                        self.assertIsNone(final["strictly_certified_output"])
                        self.assertGreater(final["trajectory_wall_seconds"], 0)
                        self.assertGreater(final["trajectory_cpu_seconds"], 0)
                        isolation = final["isolation"]
                        self.assertGreaterEqual(isolation["landlock_abi"], 4)
                        self.assertTrue(isolation["single_thread_bootstrap"])
                        self.assertTrue(isolation["no_new_privileges"])
                        self.assertEqual(isolation["handled_new_file_operations"], "denied")
                        self.assertEqual(isolation["tcp_bind_connect"], "denied")

                        # Recompute from the complete public observation record,
                        # retaining all unknown group types for every arm.
                        common = log_glr(final["counts"], [[0], [1, 2, 3]],
                                         final["calibration"], final["type_answers"],
                                         [.8, .8], R, eta=.05)
                        for key in ("theta", "z", "p_hat", "q_hat", "gap", "beta",
                                    "log_likelihood", "alternative_log_likelihood"):
                            self.assertEqual(final["fit"][key], common[key])
                        self.assertFalse(final["fit"]["oracle_types_fixed"])
                        self.assertEqual(final["fit"]["type_candidates"], 4)
                        self.assertEqual(final["fit"]["log_inverse_delta"], R)
                        self.assertFalse(final["fit"]["interval_certified"])
                        if name.endswith("NoType"):
                            self.assertEqual(counters["type"], 0)
                            self.assertEqual(final["type_answers"], [[], []])
                        if mode == "certified":
                            self.assertTrue(final["abstained"])
                            self.assertEqual(final["strict_certificate"]["status"], "rejected")
                            self.assertFalse(final["strict_certificate"]["certified"])
                            self.assertEqual(final["gate_history"][-1]["online"], 64)
                            self.assertEqual(final["strict_certificate"]["total_observations"], 64 + 2 * M)
                        else:
                            self.assertFalse(final["abstained"])
                            self.assertIsNone(final["strict_certificate"])
                            self.assertEqual(final["gate_history"], [])
                send(parent, None)
                process.join(timeout=5)
                self.assertEqual(process.exitcode, 0)
            finally:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=5)
                parent.close()
        self.assertEqual(total["task"] + total["type"], 512)
        self.assertEqual(total["offline"], 24)

    def test_parent_rejects_type_rpc_for_each_notype_arm_before_charging(self):
        conn = SimpleNamespace(poll=lambda timeout: True)
        forbidden = {"method": "ask_type", "args": {"group": 0}}
        for name in ("Aligned-NoType", "D-RRC-NoType"):
            counters = {"task": 0, "type": 0, "offline": 0}
            with self.subTest(policy=name), \
                 patch("phase2d.runner.receive", return_value=forbidden), \
                 patch("phase2d.runner.send"):
                with self.assertRaisesRegex(RuntimeError, "Type actions unavailable"):
                    evaluate_job(conn, name, technical_job(), TECHNICAL_SEED,
                                 time.monotonic() + 5, counters)
            self.assertEqual(counters, {"task": 0, "type": 0, "offline": 0})

    def test_strict_undetermined_gate_continues_then_accepts_at_next_check(self):
        client = FakeClient()
        decisions = [
            {"status": "undetermined", "certified": False, "interval_certified": False},
            {"status": "certified", "certified": True, "interval_certified": True},
        ]
        with patch("phase2d.policy.log_glr", side_effect=high_floating_fit), \
             patch("phase2d.policy.certify_stop", side_effect=decisions) as gate:
            result = run_policy(client, "D-RRC-NoType", public_job(technical_job(mode="certified")))
        self.assertEqual(len(client.queries), 32)
        self.assertEqual(result["online"], 32)
        self.assertEqual([row["online"] for row in result["gate_history"]], [16, 32])
        self.assertEqual([row["status"] for row in result["gate_history"]], ["undetermined", "certified"])
        self.assertEqual(gate.call_count, 2)
        self.assertEqual(gate.call_args.kwargs["candidate_theta"], [1])
        self.assertTrue(result["complete"])
        self.assertFalse(result["abstained"])
        self.assertEqual(result["strictly_certified_output"], [1])
        self.assertEqual(client.submissions, [[1]])
        self.assertEqual([s["online"] for s in client.snapshots], [32])
        self.assertTrue(client.snapshots[-1]["complete"])

    def test_strict_persistent_undetermined_abstains_at_cap(self):
        client = FakeClient()
        unresolved = {"status": "undetermined", "certified": False, "interval_certified": False}
        with patch("phase2d.policy.log_glr", side_effect=high_floating_fit), \
             patch("phase2d.policy.certify_stop", return_value=unresolved) as gate:
            result = run_policy(client, "D-RRC-NoType", public_job(technical_job(mode="certified")))
        self.assertEqual(len(client.queries), 64)
        self.assertEqual(result["online"], 64)
        self.assertEqual(gate.call_count, 4)
        self.assertEqual([row["online"] for row in result["gate_history"]], [16, 32, 48, 64])
        self.assertFalse(result["complete"])
        self.assertTrue(result["abstained"])
        self.assertIsNone(result["strictly_certified_output"])
        # Submission is retained only for benchmark terminal scoring.
        self.assertEqual(client.submissions, [[1]])
        self.assertEqual([s["online"] for s in client.snapshots], [32, 64])
        self.assertTrue(all(not s["complete"] for s in client.snapshots))


if __name__ == "__main__":
    unittest.main()
