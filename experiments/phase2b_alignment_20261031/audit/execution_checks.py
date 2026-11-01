"""Independent bounded public-fixture checks; never runs the main batch."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def resource_contract():
    Rs = [16, 64, 256, 1024]
    caps = [max(2048, 24 * R) for R in Rs]
    checks = [max(16, math.ceil(math.sqrt(R))) for R in Rs]
    trajectories_per_R = 2 * 2 * 4 * 5
    online = sum(caps) * trajectories_per_R
    offline = sum(2 * 3 * R * 2 * 4 * 5 for R in Rs)
    glr = sum(math.ceil(cap / step) for cap, step in zip(caps, checks)) * trajectories_per_R
    assert online == 2785280 and offline == 326400 and glr == 112640
    assert math.exp(-1024) == 0
    return {"R": Rs, "caps": caps, "check_every": checks,
            "trajectories": 320, "independent_worlds": 64,
            "maximum_online": online, "offline": offline,
            "maximum_GLR_checks": glr, "float_delta_1024_underflows": True}


def forced_only_observable_contract():
    from phase2b import bootstrap
    from phase2b.aligned import TheoryAlignedTracking

    class LengthOnly:
        def __len__(self):
            return 7

        def __iter__(self):
            raise AssertionError("allocation estimator read calibration bit values")

        def __getitem__(self, index):
            raise AssertionError("allocation estimator read calibration bit values")

    class GuardedPublic(dict):
        allowed = {"d", "groups", "rate_domain", "type_accuracy"}

        def __getitem__(self, key):
            assert key in self.allowed, f"unapproved public field read: {key}"
            return super().__getitem__(key)

        def get(self, key, default=None):
            assert key in self.allowed, f"unapproved public field read: {key}"
            return super().get(key, default)

    public = GuardedPublic({"d": 4, "groups": [{"targets": [0]}, {"targets": [1, 2, 3]}],
                            "rate_domain": {"eta": .05}, "type_accuracy": [.8, .8],
                            "truth": "MUST_NOT_READ", "p": "MUST_NOT_READ",
                            "q": "MUST_NOT_READ", "seed": "MUST_NOT_READ",
                            "oracle_format_types": "MUST_NOT_READ"})
    policies = [TheoryAlignedTracking(public, {"high": LengthOnly(), "low": LengthOnly()}, 1024)
                for _ in range(2)]
    theta, z = [0, 1, 1, 0], [1, 0]
    for p in policies:
        for j in range(4):
            g = 0 if j == 0 else 1
            for m in range(2):
                good = 17 if m == z[g] else 12
                p.forced[j, m, theta[j]] = good
                p.forced[j, m, 1 - theta[j]] = 20 - good
        p.t = 160
    policies[0].counts[:] = 1
    policies[1].counts[:] = 900000
    policies[0].types = [[0] * 1000, [1] * 2000]
    policies[1].types = [[1] * 2000, [0] * 1000]
    a, b = (p._estimate() for p in policies)
    assert a == b and a["theta"] == theta and a["z"] == z
    assert abs(a["raw_p"] - .85) < 1e-12 and abs(a["raw_q"] - .60) < 1e-12
    assert policies[0].alpha == 7 / 1024
    assert not hasattr(policies[0], "public") and not hasattr(policies[0], "calibration")
    return {"R": 1024, "alpha": 7 / 1024, "theta": a["theta"], "z": a["z"],
            "raw_p": a["raw_p"], "raw_q": a["raw_q"],
            "calibration_bit_access_forbidden": True,
            "nonforced_counts_and_type_report_invariance": True,
            "hidden_field_reads_forbidden": True}


def log_risk_without_underflow():
    from phase2b.log_glr import log_glr
    counts = np.array([[[23, 57], [41, 39]], [[57, 23], [39, 41]]])
    groups = [[0], [1]]
    calibration = {"high": [1, 0, 1, 1], "low": [0, 1, 0, 1]}
    reports = [[0, 1, 0], [1]]
    low = log_glr(counts, groups, calibration, reports, [.8, .8], 16)
    high = log_glr(counts, groups, calibration, reports, [.8, .8], 1024)
    expected = 1024 + 2 * math.log(5) + sum(math.log(81) for _ in range(4)) + math.log(4) + math.log(2)
    assert abs(high["beta"] - expected) < 1e-11
    assert abs(high["beta"] - low["beta"] - 1008) < 1e-11
    for field in ("theta", "z", "gap", "p_hat", "q_hat", "profile_log_likelihoods"):
        assert low[field] == high[field]
    assert high["interval_certified"] is False and high["log_inverse_delta"] == 1024
    return {"R": 1024, "beta": high["beta"], "profiles_unchanged_by_R": True,
            "delta_underflow_does_not_enter_profile_or_boundary": True}


def plan_and_public_job_contract():
    from phase2b.runner import jobs, public_job
    cfg = json.loads((ROOT / "config.json").read_text())
    plan = jobs(cfg)
    assert len(plan) == 64 and len({j["index"] for j in plan}) == 64
    cells = {}
    for j in plan:
        cell = (tuple(j["partition"]), j["alpha"], j["R"])
        cells.setdefault(cell, []).append(j)
        assert j["M"] == j["alpha"] * j["R"]
        assert j["online_cap"] == max(2048, 24 * j["R"])
        assert j["check_every"] == max(16, math.ceil(math.sqrt(j["R"])))
        assert set(public_job(j)) == {"R", "online_cap", "check_every", "milestones"}
        assert j["protocol"] == "fixed_confidence" and j["channel"] == "iid"
    assert len(cells) == 16 and all(len(v) == 4 for v in cells.values())
    assert sum(j["online_cap"] for j in plan) * 5 == 2785280
    assert sum(2 * j["M"] for j in plan) * 5 == 326400
    return {"globally_unique_world_indices": 64, "cells": 16, "worlds_per_cell": 4,
            "paired_policies_per_world": 5, "public_job_fields": sorted(public_job(plan[0]))}


def partial_rpc_accounting_contract():
    from types import SimpleNamespace
    from phase2b import runner

    episode = SimpleNamespace(truth=[1, 0], types=[0], records=[],
                              public={"episode_id": "PUBLIC_FIXTURE"}, provenance={})

    class Env:
        def __init__(self, *args, **kwargs):
            self.cost = {"task": 0, "type": 0, "offline": 0}
            self.trace = []
            self.predictions = None
            self._cal = None

        def reset(self):
            return {"d": 2}

        def get_calibration(self):
            self.cost["offline"] = 4
            self._cal = {"high": [1, 0], "low": [0, 1]}
            return self._cal

        def query(self, j, format):
            self.cost["task"] += 1
            return {"answer": 1}

        def ask_type(self, group):
            self.cost["type"] += 1
            return {"format": "A"}

        def submit(self, predictions):
            self.predictions = predictions
            return {"submitted": True}

        def score(self):
            return {"costs": dict(self.cost), "online": 2, "total_acquisition": 6,
                    "exact": self.predictions == episode.truth, "correct_facts": 2,
                    "transcript_sha256": "PUBLIC_FIXTURE_DIGEST"}

    class Conn:
        def __init__(self, messages, timeout=False):
            self.messages, self.sent = list(messages), []
            self.timeout, self.expired = timeout, False

        def send_bytes(self, data):
            self.sent.append(json.loads(data))

        def recv_bytes(self):
            return json.dumps(self.messages.pop(0)).encode()

        def poll(self, timeout):
            if self.messages:
                return True
            assert self.timeout
            self.expired = True
            return False

    job = {"partition": [2], "alpha": 2 / 1024, "R": 1024, "index": 999999,
           "replicate": 0, "p": .85, "q": .60, "s": .8, "eta": .05, "M": 2,
           "online_cap": 2, "check_every": 1, "milestones": [1, 2], "channel": "iid",
           "protocol": "fixed_confidence", "scenario": "PUBLIC_FIXTURE"}
    common = [{"method": "reset", "args": {}},
              {"method": "get_calibration", "args": {}},
              {"method": "query", "args": {"j": 0, "format": "A"}},
              {"method": "ask_type", "args": {"group": 0}}]
    counts = np.zeros((2, 2, 2), dtype=int)
    counts[0, 0, 1] = 1
    snap = {"online": 2, "counts": counts.tolist(), "type_answers": [[0]],
            "fit": {"theta": [1, 0]}, "complete": False, "estimate": None,
            "numeric_margin": 1e-8, "glr_checks": 1}
    detail = {**snap, "glr_seconds": 0., "planner_seconds": 0.,
              "glr_cpu_seconds": 0., "planner_cpu_seconds": 0., "tracking_diagnostics": None,
              "forced_counts": None, "estimation_history": [],
              "isolation": {"fixture": True}, "sampling_scope": "fixture"}
    original = (runner.make_episode, runner.QueryEnvironment, runner.protect_evaluator, runner.time)
    try:
        runner.make_episode = lambda *args: episode
        runner.QueryEnvironment = Env
        runner.protect_evaluator = lambda: None
        runner.time = SimpleNamespace(monotonic=lambda: 0.)
        conn = Conn(common + [{"method": "snapshot", "args": {"snapshot": snap}},
                              {"method": "submit", "args": {"predictions": [1, 0]}},
                              {"done": detail}])
        counters = {"task": 0, "type": 0, "offline": 0}
        final, _, snapshots = runner.evaluate_job(conn, "fixture", job, "NOT_A_SEED", 1., counters)
        assert counters == {"task": 1, "type": 1, "offline": 4}
        assert final["censored"] and not final["complete"] and final["total_acquisition"] == 6
        assert final["calibration"] == {"high": [1, 0], "low": [0, 1]}
        assert conn.sent[5] == {"result": {"recorded": True}} and len(snapshots) == 1
        assert set(conn.sent[0]) == {"R", "online_cap", "check_every", "milestones"}
        for messages, timeout, expected in (
                (common + [{"worker_error": "PUBLIC_FIXTURE_ERROR"}], False, RuntimeError),
                (common, True, TimeoutError)):
            conn = Conn(messages, timeout)
            runner.time = SimpleNamespace(monotonic=lambda: 2. if conn.expired else 0.)
            counters = {"task": 0, "type": 0, "offline": 0}
            try:
                runner.evaluate_job(conn, "fixture", job, "NOT_A_SEED", 1., counters)
            except expected:
                pass
            else:
                raise AssertionError("interrupted job did not fail visibly")
            assert counters == {"task": 1, "type": 1, "offline": 4}
    finally:
        runner.make_episode, runner.QueryEnvironment, runner.protect_evaluator, runner.time = original
    return {"snapshot_ack_only": True, "capped_fixture_is_censored": True,
            "normal_and_interrupted_costs": {"task": 1, "type": 1, "offline": 4},
            "worker_error_and_timeout_preserve_partial_costs": True,
            "R1024_without_float_delta": True}


def main():
    sources = [ROOT / "phase2b" / name for name in ("log_glr.py", "aligned.py")]
    report = {"scope": "bounded_public_fixtures_no_main_experiments",
              "resources": resource_contract(),
              "forced_only_observable": forced_only_observable_contract(),
              "log_risk": log_risk_without_underflow(),
              "source_sha256": {str(source.relative_to(ROOT)):
                                hashlib.sha256(source.read_bytes()).hexdigest() for source in sources}}
    if (ROOT / "phase2b" / "runner.py").exists():
        report["plan_public_job"] = plan_and_public_job_contract()
        report["partial_RPC_costs"] = partial_rpc_accounting_contract()
        for name in ("runner.py", "policy.py"):
            p = ROOT / "phase2b" / name
            report["source_sha256"][str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps(report,
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
