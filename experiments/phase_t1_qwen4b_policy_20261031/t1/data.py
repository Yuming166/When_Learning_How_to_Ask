"""Trusted evaluator-only T1 world plans and frozen teacher-data collection.

Importing this module creates no world. Generation requires a verified source
freeze and a separately supplied new development seed.
"""
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
from .core import ORIGINAL_ROOT, BLOCK_SIZE, PUBLIC_CAP, CommonScheduler, messages_for, teacher_target

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "phase_t1_qwen4b_policy_20261031"
DATA_DEFAULTS = {
    "train_worlds": 64, "worlds_per_other_split": 8, "snapshots_per_world": 16,
    "snapshot_interval": 128, "public_cap": 2048, "eta": .05, "s": .8,
    "train_rates": [[.8, .55], [.9, .65]], "heldout_rates": [.85, .6],
    "train_partitions": [[4], [1, 3]], "heldout_partition": [2, 2],
    "alphas": [0, 1], "confidence_targets": [64, 256],
}
SPLITS = ("train", "validation", "id_test", "ood_parameters", "ood_partition")


def _data_config(config):
    supplied = config.get("data", {})
    if not isinstance(supplied, dict) or any(key not in DATA_DEFAULTS for key in supplied):
        raise ValueError("Unknown T1 data configuration field")
    if any(value != DATA_DEFAULTS[key] for key, value in supplied.items()):
        raise ValueError("Data configuration differs from the approved bounded protocol")
    return dict(DATA_DEFAULTS)


def _spec(split, number, partition, rates, alpha, risk, offset, cfg):
    index = offset + number
    return {"world_id": hashlib.sha256(f"{NAMESPACE}|{split}|{index}".encode()).hexdigest()[:24],
            "namespace": NAMESPACE, "environment_split": "development", "split": split, "index": index,
            "partition": list(partition), "p": rates[0], "q": rates[1], "alpha": alpha, "R": risk,
            "M": int(alpha * risk), "s": cfg["s"], "eta": cfg["eta"], "online_cap": cfg["public_cap"]}


def world_plan(config):
    """96 fresh data worlds; the manifest, not student input, owns identity."""
    cfg = _data_config(config)
    grid = list(itertools.product(cfg["train_partitions"], cfg["train_rates"], cfg["alphas"], cfg["confidence_targets"]))
    plan = []
    for split_number, split in enumerate(SPLITS):
        count = cfg["train_worlds"] if split == "train" else cfg["worlds_per_other_split"]
        for i in range(count):
            if split == "train":
                part, rates, alpha, risk = grid[i % len(grid)]
            elif split in ("validation", "id_test"):
                # Balanced half-fractions of the16 training cells; validation
                # and ID test use complementary parity, with distinct worlds.
                pbit, rbit, abit = i % 2, (i // 2) % 2, (i // 4) % 2
                risk_bit = pbit ^ rbit ^ abit ^ int(split == "id_test")
                part, rates = cfg["train_partitions"][pbit], cfg["train_rates"][rbit]
                alpha, risk = cfg["alphas"][abit], cfg["confidence_targets"][risk_bit]
            elif split == "ood_parameters":
                part, alpha, risk = list(itertools.product(cfg["train_partitions"], cfg["alphas"], cfg["confidence_targets"]))[i]
                rates = cfg["heldout_rates"]
            else:
                rates, alpha, risk = list(itertools.product(cfg["train_rates"], cfg["alphas"], cfg["confidence_targets"]))[i]
                part = cfg["heldout_partition"]
            plan.append(_spec(split, i, part, rates, alpha, risk, 7_100_000 + 10_000 * split_number, cfg))
    return plan


def evaluation_world_plan(config):
    """24 additional evaluator worlds, disjoint from every data split."""
    cfg = _data_config(config)
    output = []
    for split_number, split in enumerate(("eval_id", "eval_ood_parameters", "eval_ood_partition")):
        if split == "eval_id":
            cells = list(itertools.product(cfg["train_partitions"], cfg["train_rates"], cfg["alphas"]))
        elif split == "eval_ood_parameters":
            cells = [(part, cfg["heldout_rates"], alpha) for part, alpha in itertools.product(cfg["train_partitions"], cfg["alphas"])]
        else:
            cells = [(cfg["heldout_partition"], rates, alpha) for rates, alpha in itertools.product(cfg["train_rates"], cfg["alphas"])]
        for i in range(8):
            part, rates, alpha = cells[i % len(cells)]
            output.append(_spec(split, i, part, rates, alpha, 64, 7_600_000 + 10_000 * split_number, cfg))
    return output


def make_world(spec, development_seed):
    """Trusted boundary: never expose either returned object to a student."""
    if spec["namespace"] != NAMESPACE or spec["environment_split"] != "development":
        raise ValueError("Only fresh namespaced T1 development worlds are allowed")
    if development_seed is None or not str(development_seed):
        raise ValueError("A separately supplied new development seed is required")
    path = str(ORIGINAL_ROOT / "experiments/qrelbench_v01_20261030")
    if path not in sys.path:
        sys.path.insert(0, path)
    from qrelbench.data import make_episode
    from qrelbench.environment import QueryEnvironment
    namespaced_seed = f"{NAMESPACE}|{spec['split']}|{development_seed}"
    episode = make_episode(namespaced_seed, "development", spec["index"], spec["partition"])
    environment = QueryEnvironment(episode, spec["p"], spec["q"], spec["M"], spec["s"],
                                   spec["online_cap"], "iid", False, eta=spec["eta"])
    return environment, episode


def collect_world(spec, development_seed, *, deadline=None):
    """16 labels from pre-action states; caller must verify freeze first."""
    environment, episode = make_world(spec, development_seed)
    scheduler, calibration = None, None
    rows = []
    try:
        public, calibration = environment.reset(), environment.get_calibration()
        scheduler = CommonScheduler(public, calibration, spec["R"], spec["online_cap"], BLOCK_SIZE)
        for target_time in (8 + BLOCK_SIZE * k for k in range(16)):
            while scheduler.t < target_time:
                if deadline is not None and time.monotonic() >= deadline:
                    raise TimeoutError("Frozen T1 data-generation deadline")
                if scheduler.needs_update():
                    raise RuntimeError("A scheduled predecision state was skipped")
                action = scheduler.next(range(4))
                result = environment.ask_type(action[1]) if action[0] == "type" else environment.query(action[1], action[2])
                scheduler.observe(action, result)
            state = scheduler.state()
            if not scheduler.needs_update():
                raise RuntimeError("Teacher label is not at a predecision block boundary")
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("Frozen T1 data-generation deadline")
            target = teacher_target(state)
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("Frozen T1 data-generation deadline during teacher update")
            rows.append({"state": state, "teacher_weights": target["weights"], "teacher_percent": target["percent"],
                         "teacher_estimate": target["estimate"], "teacher_K": target["teacher_K"],
                         "messages": messages_for(state, target["percent"])})
            scheduler.set_target(target["weights"])
    except Exception as exc:
        partial = {"world_id": spec["world_id"], "spec": spec, "provenance": episode.provenance,
                   "truth": episode.truth, "types": episode.types, "records": episode.records,
                   "costs": dict(environment.cost), "calibration": calibration,
                   "online_actions": environment.cost["task"] + environment.cost["type"],
                   "partial_observable_state": None if scheduler is None else scheduler.state(),
                   "completed_labels": rows, "transcript_sha256": environment.log_digest.hexdigest()}
        error = RuntimeError("T1 world collection failed: " + type(exc).__name__ + ": " + str(exc))
        error.t1_partial = partial
        raise error from exc
    private = {"spec": spec, "provenance": episode.provenance, "truth": episode.truth, "types": episode.types,
               "records": episode.records, "online_actions": scheduler.t, "costs": environment.cost,
               "world_id": spec["world_id"], "calibration": calibration,
               "transcript_sha256": environment.log_digest.hexdigest(), "teacher_labels": len(rows)}
    return rows, private


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_freeze(config, freeze_path):
    freeze_path = Path(freeze_path).resolve()
    if not freeze_path.is_relative_to(ROOT.resolve()):
        raise ValueError("Freeze must belong to this isolated T1 experiment")
    freeze = json.loads(freeze_path.read_text())
    files = freeze.get("files", {})
    if not {"t1/core.py", "t1/data.py", "config.json"} <= set(files):
        raise ValueError("Freeze does not bind required T1 source/configuration")
    if json.loads((ROOT / "config.json").read_text()) != config:
        raise ValueError("Supplied configuration differs from frozen configuration")
    for relative, expected in files.items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT.resolve()) or sha256_file(path) != expected:
            raise ValueError("T1 frozen source/configuration/audit changed")
    dependencies = freeze.get("dependencies", {})
    required = {str(ORIGINAL_ROOT / "experiments/phase2b_alignment_20261031/phase2b/aligned.py"),
                str(ORIGINAL_ROOT / "experiments/phase2a_theory_optimality_20261030/phase2a/coefficients.py"),
                str(ORIGINAL_ROOT / "experiments/qrelbench_v01_20261030/qrelbench/data.py"),
                str(ORIGINAL_ROOT / "experiments/qrelbench_v01_20261030/qrelbench/environment.py"),
                str(ORIGINAL_ROOT / "experiments/qrelbench_v01_20261030/qrelbench/randomness.py")}
    if not required <= set(dependencies):
        raise ValueError("Freeze lacks required read-only historical dependencies")
    for absolute, expected in dependencies.items():
        path = Path(absolute).resolve()
        if not path.is_relative_to(ORIGINAL_ROOT.resolve()) or sha256_file(path) != expected:
            raise ValueError("Frozen historical dependency changed")
    return sha256_file(freeze_path)


def generate_dataset(config, output_dir, development_seed, freeze_path):
    """Authorized post-freeze entry point; no seed generation and no retry."""
    cfg = _data_config(config)
    freeze_hash = verify_freeze(config, freeze_path)
    output = Path(output_dir).resolve()
    if not output.is_relative_to(ROOT.resolve()) or output.exists():
        raise ValueError("Fresh output directory inside isolated T1 experiment required")
    output.mkdir(parents=True)
    private_dir = output / "private"
    private_dir.mkdir(mode=0o700)
    os.chmod(private_dir, 0o700)
    manifest = {"namespace": NAMESPACE, "status": "started", "freeze_sha256": freeze_hash,
                "seed_commitment": hashlib.sha256(f"{NAMESPACE}|{development_seed}".encode()).hexdigest(),
                "splits": {split: {"file": split + ".jsonl", "worlds": 0, "states": 0} for split in SPLITS},
                "worlds": [], "data_config": cfg,
                "worlds_completed": 0, "generated_online_actions": 0, "unique_generated_offline_observations": 0,
                "heldout_scope": "heldout parameter pair is inside training rate ranges; not range extrapolation",
                "public_limit_scope": "cap2048; later 256/512 evaluations are intermediate evaluator readouts"}
    started = time.monotonic()
    max_seconds = config.get("limits", {}).get("data_wall_seconds", 1800)
    deadline = started + max_seconds
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    handles = {split: (output / (split + ".jsonl")).open("x") for split in SPLITS}
    try:
        for spec in world_plan(config):
            manifest["current_world_id"] = spec["world_id"]
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            rows, private = collect_world(spec, development_seed, deadline=deadline)
            split = spec["split"]
            start = manifest["splits"][split]["states"]
            encoded = "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n" for row in rows)
            handles[split].write(encoded)
            handles[split].flush()
            private_path = private_dir / (spec["world_id"] + ".json")
            with private_path.open("x") as handle:
                os.chmod(private_path, 0o600)
                json.dump(private, handle, sort_keys=True, indent=2, allow_nan=False)
                handle.write("\n")
            manifest["worlds"].append({"world_id": spec["world_id"], "split": split, "row_start": start,
                                       "row_count": len(rows), "content_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                                       "private_file": str(private_path.relative_to(output))})
            manifest["splits"][split]["states"] += len(rows)
            manifest["splits"][split]["worlds"] += 1
            manifest["worlds_completed"] += 1
            manifest["generated_online_actions"] += private["online_actions"]
            manifest["unique_generated_offline_observations"] += private["costs"]["offline"]
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            print(json.dumps({"worlds_completed": manifest["worlds_completed"], "split": split,
                              "states_completed": sum(value["states"] for value in manifest["splits"].values()),
                              "online_actions": manifest["generated_online_actions"],
                              "seconds": round(time.monotonic() - started, 2)}), flush=True)
        if sum(x["states"] for x in manifest["splits"].values()) != 1536:
            raise RuntimeError("Incomplete teacher-state coverage")
        manifest["status"] = "completed"
        manifest["current_world_id"] = None
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error"] = type(exc).__name__ + ": " + str(exc)
        partial = getattr(exc, "t1_partial", None)
        if partial is not None:
            path = private_dir / (partial["world_id"] + ".failed.json")
            with path.open("x") as handle:
                os.chmod(path, 0o600)
                json.dump(partial, handle, sort_keys=True, indent=2, allow_nan=False)
                handle.write("\n")
            manifest["failed_world"] = {"world_id": partial["world_id"], "online_actions": partial["online_actions"],
                                        "costs": partial["costs"], "retained_predecision_labels": len(partial["completed_labels"]),
                                        "private_file": str(path.relative_to(output))}
            manifest["generated_online_actions"] += partial["online_actions"]
            manifest["unique_generated_offline_observations"] += partial["costs"]["offline"]
        raise
    finally:
        for handle in handles.values():
            handle.close()
        manifest["wall_seconds"] = time.monotonic() - started
        manifest["files"] = {split + ".jsonl": sha256_file(output / (split + ".jsonl")) for split in SPLITS}
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
