"""Frozen-policy validation on predeclared controlled catalogue mechanisms."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import sys

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "experiments/recommendation_loop_20261103"
sys.path.insert(0, str(OLD))
import run_loop as frozen_runner
from likelihood import JointLikelihood
from relative_ig import RelativeIGPolicy

DEPENDENCIES = [
    "experiments/recommendation_loop_20261103/likelihood.py",
    "experiments/recommendation_loop_20261103/certification.py",
    "experiments/recommendation_loop_20261103/policies.py",
    "experiments/recommendation_loop_20261103/relative_ig.py",
    "experiments/recommendation_loop_20261103/decision_ig.py",
    "experiments/recommendation_loop_20261103/run_loop.py",
    "experiments/phase2d_method_improvement_20261031/phase2d/certified.py",
    "research/general_catalogue_theory_20261103/general_geometry.py",
    "research/top1_decision_theory_20261103/decision_information.py",
    "research/general_catalogue_theory_20261103/CATALOGUE_EXAMPLES.md",
]
LOCAL_SOURCES = ["config.json", "run.py", "analyze.py", "test_protocol.py", "PROTOCOL.md", "README.md"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_worlds(config, *, smoke=False):
    worlds = []
    for cell in config["cells"]:
        public = {"d": cell["d"], "groups": cell["groups"], "eta": config["eta"],
                  "catalogue": {"offsets": cell["offsets"], "slopes": cell["slopes"]}}
        model = JointLikelihood(public)
        for replicate in config["replicate_indices"]:
            for R in config["risk_R_values"]:
                seed_label = f"{cell['catalogue_name']}|replicate{replicate}|responses"
                if smoke:
                    seed_label = "engineering_smoke|" + seed_label
                seed = frozen_runner.stable_seed(config["seed_root"], seed_label)
                worlds.append({
                    "id": f"{cell['id']}__seed{replicate}__R{R}",
                    "cell_id": cell["id"], "premium": cell["premium"],
                    "replicate": replicate, "R": R,
                    "profile_cluster": f"{cell['catalogue_name']}__seed{replicate}",
                    "catalogue_name": cell["catalogue_name"],
                    "profile_kind": "predeclared_all_positive_theory_anchor",
                    "partition_index": cell["partition_index"], "public": public,
                    "private": {"theta": [1] * cell["d"], "types": [0] * model.G,
                                "p": config["generating_p"], "q": config["generating_q"],
                                "winner": int(model.winner_by_theta[0]), "response_seed": seed}})
    return worlds


def worker_init():
    if hasattr(os, "sched_getaffinity"):
        available = sorted(os.sched_getaffinity(0))
        identity = multiprocessing.current_process()._identity
        ordinal = identity[-1] - 1 if identity else 0
        os.sched_setaffinity(0, {available[ordinal % min(2, len(available))]})


def run_arm(world, arm, config):
    # A process-local factory replacement uses the frozen repaired IG class.
    # Its other arms delegate unchanged to the original frozen implementation.
    frozen_runner.ObservablePolicy = RelativeIGPolicy
    record = frozen_runner.run_arm(world, arm, dict(config, R=world["R"]))
    record.update(cell_id=world["cell_id"], premium=world["premium"],
                  replicate=world["replicate"], R=world["R"])
    return record


def freeze(config):
    path = HERE / "FREEZE.json"
    if path.exists():
        raise FileExistsError("the frozen protocol already exists")
    worlds = make_worlds(config)
    record = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "local_sha256": {name: digest(HERE / name) for name in LOCAL_SOURCES},
              "dependency_sha256": {name: digest(ROOT / name) for name in DEPENDENCIES},
              "worlds_sha256": hashlib.sha256(json.dumps(worlds, sort_keys=True).encode()).hexdigest(),
              "planned_trajectories": len(worlds) * len(config["arms"]),
              "model_calls": 0, "training": False}
    path.write_text(json.dumps(record, indent=2) + "\n")
    return record


def check_freeze(config):
    record = json.loads((HERE / "FREEZE.json").read_text())
    for name, expected in record["local_sha256"].items():
        if digest(HERE / name) != expected:
            raise ValueError(f"frozen source changed: {name}")
    for name, expected in record["dependency_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"frozen dependency changed: {name}")
    worlds_hash = hashlib.sha256(json.dumps(make_worlds(config), sort_keys=True).encode()).hexdigest()
    if worlds_hash != record["worlds_sha256"]:
        raise ValueError("world construction changed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "runtime_smoke", "freeze", "main"], required=True)
    args = parser.parse_args()
    config = json.loads((HERE / "config.json").read_text())
    if args.mode == "freeze":
        print(json.dumps(freeze(config), indent=2))
        return
    if args.mode == "main":
        check_freeze(config)
        worlds = make_worlds(config)
    else:
        worlds = make_worlds(config, smoke=True)
        worlds = [w for w in worlds if w["replicate"] == 0 and w["R"] == 3]
        config = dict(config, workers=1, max_queries=24)
        if args.mode == "runtime_smoke":
            worlds = [w for w in worlds if w["cell_id"] == "genuine6_positive"]
            config["max_queries"] = 160
    output = HERE / "artifacts" / args.mode
    output.mkdir(parents=True, exist_ok=False)
    jobs = [(world, arm) for world in worlds for arm in config["arms"]]
    (output / "worlds.json").write_text(json.dumps(worlds, indent=2) + "\n")
    (output / "effective_config.json").write_text(json.dumps(config, indent=2) + "\n")
    (output / "planned_jobs.json").write_text(json.dumps(
        [{"world_id": w["id"], "arm": a} for w, a in jobs], indent=2) + "\n")
    summaries = []

    def collect(world, arm, record):
        (output / f"{world['id']}__{arm}.json").write_text(json.dumps(record, indent=2) + "\n")
        keys = ["world_id", "cell_id", "premium", "catalogue_name", "profile_cluster", "replicate", "R",
                "arm", "status", "queries", "certified_output", "certified_correct", "failure",
                "postprocessing_failure", "wall_seconds", "cpu_seconds", "policy_seconds",
                "policy_cpu_seconds", "gate_seconds", "gate_cpu_seconds", "gate_calls"]
        row = {key: record.get(key) for key in keys}
        summaries.append(row)
        print(json.dumps(dict(done=len(summaries), total=len(jobs), **row)), flush=True)

    def failed(world, arm, error):
        return dict(world_id=world["id"], cell_id=world["cell_id"], premium=world["premium"],
                    catalogue_name=world["catalogue_name"], profile_cluster=world["profile_cluster"],
                    replicate=world["replicate"], R=world["R"], arm=arm,
                    status="FAILED_INFRASTRUCTURE_UNCERTIFIED", queries=None, counts=None, history=None,
                    certificate=None, certified_output=None, certified_correct=None,
                    failure={"type": type(error).__name__, "message": str(error)})

    with ProcessPoolExecutor(max_workers=config["workers"], initializer=worker_init) as pool:
        futures = {}
        for world, arm in jobs:
            try:
                futures[pool.submit(run_arm, world, arm, config)] = world, arm
            except Exception as error:
                collect(world, arm, failed(world, arm, error))
        for future in as_completed(futures):
            world, arm = futures[future]
            try:
                record = future.result()
            except Exception as error:
                record = failed(world, arm, error)
            collect(world, arm, record)
    summaries.sort(key=lambda r: (r["world_id"], r["arm"]))
    (output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    print(json.dumps({"complete": len(summaries), "planned": len(jobs),
                      "certified": sum(r["status"] == "CERTIFIED" for r in summaries),
                      "capped": sum(r["status"] == "CAPPED_UNCERTIFIED" for r in summaries),
                      "failed": sum(r["status"].startswith("FAILED") for r in summaries)}), flush=True)


if __name__ == "__main__":
    main()
