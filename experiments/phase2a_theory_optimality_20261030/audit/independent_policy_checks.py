"""Bounded deterministic CPU probes for the independent execution audit.

No main experiment, model call, benchmark episode generation, or private input
is used. Output goes to stdout so the audit does not mutate result history.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from phase2a.tracking import InformationTracking
from phase2a.glr import endpoint_mle, profile_glr
from phase2a.coefficients import alternatives, inner


def public_fixture(partition, s=.8):
    groups, targets = [], []
    for g, size in enumerate(partition):
        members = list(range(len(targets), len(targets) + size))
        groups.append({"targets": members})
        targets.extend({"group": g} for _ in members)
    return {"d": len(targets), "groups": groups, "targets": targets,
            "type_accuracy": [s] * len(partition), "rate_domain": {"eta": .05}}


def fitted_fixture(with_calibration):
    """Exact empirical frequencies, with no random sample or private state."""
    public = public_fixture([2, 2])
    calibration = ({"high": [1] * 85 + [0] * 15,
                    "low": [1] * 60 + [0] * 40}
                   if with_calibration else {"high": [], "low": []})
    policy = InformationTracking(public, calibration)
    signs, types = [0, 1, 0, 1], [1, 0]
    for j in range(4):
        for form in range(2):
            good = 8500 if form == types[j // 2] else 6000
            policy.forced[j, form, signs[j]] = good
            policy.forced[j, form, 1 - signs[j]] = 10000 - good
    policy.t = int(policy.forced.sum())
    first = policy._estimate()
    assert first["theta"] == signs and first["z"] == types, first
    assert abs(first["p"] - .85) < 1e-12 and abs(first["q"] - .60) < 1e-12, first
    # Actual exploitation counts are not a source of unlabelled estimator data.
    policy.counts[:] = 777777
    assert policy._estimate() == first
    return {"M": len(calibration["high"]), "estimate": first,
            "nonforced_count_invariance": True}


def forced_schedule(d):
    policy = InformationTracking(public_fixture([d]), {"high": [], "low": []})
    # Isolate tracking/forced-exploration mechanics from an optimizer test.
    policy.next_update = 10**9
    policy.weights[:] = 0
    policy.weights[0] = 1
    rows = []
    for t in range(4096):
        action = policy.next(set(range(d)))
        assert action[0] == "query"
        policy.observe(action, {"answer": int((t // 3) % 2)})
        if t + 1 in (256, 1024, 4096):
            forced = policy.forced.sum(axis=2)
            threshold = .5 * math.sqrt((t + 1) / d)
            # One chosen observation may lag the simultaneously rising threshold.
            assert forced.min() >= math.floor(threshold) - 1
            assert forced.max() - forced.min() <= 1
            rows.append({"t": t + 1, "forced_total": int(forced.sum()),
                         "min_per_stream": int(forced.min()),
                         "max_per_stream": int(forced.max()),
                         "threshold": threshold,
                         "max_tracking_deficit": float(np.max(policy.cumulative - np.r_[
                             policy.counts.sum(axis=2).reshape(-1),
                             [len(x) for x in policy.types]]))})
    return {"d": d, "checkpoints": rows}


def m_zero_decoder():
    counts = np.zeros((2, 2, 2), dtype=np.int64)
    counts[0, 0] = [2, 18]
    counts[0, 1] = [8, 12]
    counts[1, 0] = [18, 2]
    counts[1, 1] = [12, 8]
    cal = {"high": [], "low": []}
    endpoint = endpoint_mle(counts, [[0, 1]], cal, [[]], [.8])
    glr = profile_glr(counts, [[0, 1]], cal, [[]], [.8])
    assert endpoint["theta"] == glr["theta"] == [1, 0]
    assert endpoint["p_hat"] >= endpoint["q_hat"] >= .5
    assert all(k not in endpoint for k in ("certified", "gap", "beta"))
    assert endpoint["reference_count_per_stream"] == 0
    # Empty-data ties are explicit and deterministic, never a certificate.
    empty = profile_glr(np.zeros_like(counts), [[0, 1]], cal, [[]], [.8])
    assert empty["theta"] == [0, 0] and empty["gap"] == 0 and not empty["certified"]
    return {"theta": endpoint["theta"], "p_hat": endpoint["p_hat"],
            "q_hat": endpoint["q_hat"], "no_certificate_in_endpoint": True,
            "empty_tie_theta": empty["theta"]}


def shortcut_diagnostic():
    # Use exactly the true empirical frequencies only as a public-count fixture.
    public = public_fixture([8, 8])
    cal = {"high": [1] * 85 + [0] * 15, "low": [1] * 60 + [0] * 40}
    policy = InformationTracking(public, cal, planning_delta=math.exp(-100 / 3))
    for j in range(16):
        policy.forced[j, 0] = [1500, 8500]
        policy.forced[j, 1] = [4000, 6000]
    policy.t = int(policy.forced.sum())
    policy._update()
    estimate = policy.last_estimate
    # Compare the recorded shortcut minimum with all mathematical alternatives.
    weights = np.asarray(estimate["weights"])
    K = estimate["estimated_K"]
    x = np.r_[[weights[2 * j] * K for j in (0, 8)],
              [weights[2 * j + 1] * K for j in (0, 8)],
              weights[-2:] * K]
    kappa = np.array([.8 * math.log(4) + .2 * math.log(.25)] * 2)
    actual = min(inner([8, 8], estimate["p"], estimate["q"], policy.alpha,
                       x, mask, h, kappa, policy.eta)["value"]
                 for mask, h in alternatives(2))
    assert abs(actual - 1) < 1e-8
    return {"recorded_minimum_information": estimate["minimum_information"],
            "independently_evaluated_minimum": actual,
            "diagnostic_equal": abs(estimate["minimum_information"] - actual) < 1e-8}


def scripted_policy_accounting():
    """Run learner integration against fixed public replies, not an environment."""
    from phase2a.policy import POLICIES, run_policy

    class TranscriptClient:
        def __init__(self, name):
            self.public = public_fixture([2, 2])
            if name == "Oracle Format":
                self.public["oracle_format_types"] = ["A", "B"]
            self.actions, self.snapshots = [], []
            self.predictions = None

        def reset(self):
            return self.public

        def get_calibration(self):
            return {"high": [], "low": []}

        def query(self, j, form):
            self.actions.append(("query", j, form))
            return {"answer": j % 2}

        def ask_type(self, g):
            self.actions.append(("type", g))
            return {"format": "AB"[g % 2]}

        def _call(self, method, **kwargs):
            assert method == "snapshot"
            self.snapshots.append(kwargs["snapshot"])
            return {"recorded": True}

        def submit(self, predictions):
            self.predictions = predictions

    job = {"protocol": "fixed_budget", "planning_delta": .05,
           "update_every": 32, "online_cap": 8, "snapshot_budgets": [4, 8]}
    rows = []
    for name in POLICIES:
        client = TranscriptClient(name)
        result = run_policy(client, name, job)
        task = sum(a[0] == "query" for a in client.actions)
        typed = sum(a[0] == "type" for a in client.actions)
        assert result["online"] == len(client.actions) == task + typed == 8
        assert np.asarray(result["counts"]).sum() == task
        assert sum(map(len, result["type_answers"])) == typed
        assert result["snapshots"] == [4, 8] and len(client.snapshots) == 2
        assert result["fit"]["reference_count_per_stream"] == 0
        assert result["fit"]["purpose"] == "common_fixed_budget_profile_mle_endpoint_decoder"
        assert "certified" not in result["fit"] and client.predictions == result["fit"]["theta"]
        rows.append({"policy": name, "task": task, "type": typed,
                     "online": result["online"], "M": 0})
    # A capped fixed-confidence trajectory stays incomplete and unendorsed.
    client = TranscriptClient("Information Tracking")
    capped = run_policy(client, "Information Tracking", {
        "protocol": "fixed_confidence", "planning_delta": .05,
        "delta": .05, "update_every": 32, "online_cap": 8, "check_every": 4})
    assert not capped["complete"] and not capped["fit"]["certified"]
    assert capped["online"] == 8 and len(client.actions) == 8
    return {"fixed_budget": rows,
            "fixed_confidence_cap_is_incomplete": True}


def evaluator_accounting_fixture():
    """Exercise normal, worker-error, and timeout RPC paths using public fixtures."""
    from types import SimpleNamespace
    from phase2a import runner

    episode = SimpleNamespace(truth=[1, 0], types=[0], records=[],
                              public={"episode_id": "PUBLIC_FIXTURE"}, provenance={})

    class Env:
        def __init__(self, *args):
            self.cost = {"task": 0, "type": 0, "offline": 0}
            self.trace = []
            self.predictions = None

        def reset(self):
            return {"d": 2}

        def get_calibration(self):
            self.cost["offline"] = 4
            return {"high": [1, 0], "low": [0, 1]}

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
            online = self.cost["task"] + self.cost["type"]
            return {"costs": dict(self.cost), "online": online,
                    "total_acquisition": sum(self.cost.values()),
                    "exact": self.predictions == episode.truth, "correct_facts": 2,
                    "transcript_sha256": "PUBLIC_FIXTURE_DIGEST"}

    class Conn:
        def __init__(self, messages, timeout=False):
            self.messages = list(messages)
            self.sent = []
            self.timeout = timeout
            self.expired = False

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

    job = {"protocol": "fixed_confidence", "scenario": "fixture", "partition": [2],
           "alpha": 1, "R": 2, "index": 123456, "p": .85, "q": .6,
           "s": .8, "channel": "iid", "M": 2, "delta": .05,
           "online_cap": 8, "check_every": 4, "snapshot_budgets": [], "update_every": 32}
    common = [{"method": "reset", "args": {}},
              {"method": "get_calibration", "args": {}},
              {"method": "query", "args": {"j": 0, "format": "A"}},
              {"method": "ask_type", "args": {"group": 0}}]
    counts = np.zeros((2, 2, 2), dtype=int)
    counts[0, 0, 1] = 1
    estimate = {"theta": [1, 0], "z": [0], "p": .8, "q": .6}
    snap = {"online": 2, "counts": counts.tolist(), "fit": {"theta": [1, 0]},
            "complete": False, "estimate": estimate}
    detail = {"online": 2, "counts": counts.tolist(), "complete": False,
              "glr_seconds": 0., "decode_seconds": 0., "planner_seconds": 0.,
              "fit": snap["fit"], "isolation": {"fixture": True},
              "estimation_history": [estimate], "type_answers": [[0]],
              "sampling_scope": "fixture"}
    originals = (runner.make_episode, runner.QueryEnvironment, runner.protect_evaluator, runner.time)
    try:
        runner.make_episode = lambda *args: episode
        runner.QueryEnvironment = Env
        runner.protect_evaluator = lambda: None
        conn = Conn(common + [{"method": "snapshot", "args": {"snapshot": snap}},
                              {"method": "submit", "args": {"predictions": [1, 0]}},
                              {"done": detail}])
        runner.time = SimpleNamespace(monotonic=lambda: 0.)
        counters = {"task": 0, "type": 0, "offline": 0}
        final, private, snapshots = runner.evaluate_job(conn, "fixture", job,
                                                       "FIXTURE_NOT_A_SEED", 1., counters)
        assert counters == {"task": 1, "type": 1, "offline": 4}
        assert final["online"] == 2 and final["total_acquisition"] == 6
        assert final["censored"] and not final["complete"] and len(snapshots) == 1
        assert conn.sent[5] == {"result": {"recorded": True}}
        assert all(k not in conn.sent[0] for k in ("p", "q", "index", "scenario", "seed"))
        for name, messages, timeout, expected in (
                ("worker_error", common + [{"worker_error": "FIXTURE_ERROR"}], False, RuntimeError),
                ("timeout", common, True, TimeoutError)):
            conn = Conn(messages, timeout)
            runner.time = SimpleNamespace(monotonic=lambda: 2. if conn.expired else 0.)
            partial = {"task": 0, "type": 0, "offline": 0}
            try:
                runner.evaluate_job(conn, "fixture", job, "FIXTURE_NOT_A_SEED", 1., partial)
            except expected:
                pass
            else:
                raise AssertionError(f"{name} did not fail visibly")
            assert partial == {"task": 1, "type": 1, "offline": 4}
    finally:
        runner.make_episode, runner.QueryEnvironment, runner.protect_evaluator, runner.time = originals
    return {"normal_total_acquisition": 6, "normal_online": 2,
            "snapshot_reply_is_ack_only": True, "capped_final_is_censored": True,
            "worker_error_partial_costs_preserved": True,
            "timeout_partial_costs_preserved": True,
            "private_job_fields_excluded": True}


def main():
    sources = [ROOT / "phase2a" / name for name in
               ("tracking.py", "coefficients.py", "glr.py")]
    report = {"scope": "bounded_deterministic_CPU_fixtures_no_main_experiments",
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sources},
              "estimation": [fitted_fixture(False), fitted_fixture(True)],
              "forced_tracking": [forced_schedule(d) for d in (2, 8, 16)],
              "M_zero_decoder": m_zero_decoder(),
              "shortcut_diagnostic": shortcut_diagnostic()}
    if (ROOT / "phase2a" / "policy.py").exists():
        report["scripted_policy_integration"] = scripted_policy_accounting()
        for name in ("policy.py", "bootstrap.py"):
            source = ROOT / "phase2a" / name
            report["source_sha256"][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    if (ROOT / "phase2a" / "runner.py").exists():
        report["evaluator_RPC_accounting"] = evaluator_accounting_fixture()
        source = ROOT / "phase2a" / "runner.py"
        report["source_sha256"][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
