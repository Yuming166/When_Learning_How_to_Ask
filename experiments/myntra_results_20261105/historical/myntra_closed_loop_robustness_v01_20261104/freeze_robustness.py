#!/usr/bin/env python3
"""Create a one-shot pre-full-run hash freeze after tests and smoke pass."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
PRIMARY = HERE.parent / CONFIG["frozen_policy_experiment"]
SOURCE = Path(CONFIG["source_worktree"])
SOURCE_EXP = SOURCE / "experiments/myntra_preference_dev_v01_20261104"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bind(files, label, path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Missing frozen input {label}: {path}")
    files[label] = {"path": str(path), "sha256": sha256(path)}


def main():
    target = HERE / "FROZEN.json"
    if target.exists():
        raise FileExistsError("Preserve the existing pre-run freeze")
    smoke = json.loads((HERE / "artifacts/SMOKE_METRICS.json").read_text())
    if smoke.get("status") != "PASS" or smoke.get("cases") != 2:
        raise RuntimeError("Smoke must pass before freezing")
    files = {}
    for name in ["config.json", "ROBUSTNESS_PROTOCOL.md", "run_robustness.py", "test_robustness.py", "freeze_robustness.py"]:
        bind(files, f"robustness/{name}", HERE / name)
    old_freeze_path = PRIMARY / "FREEZE.json"
    old_freeze = json.loads(old_freeze_path.read_text())
    bind(files, "primary/FREEZE.json", old_freeze_path)
    for name, expected in old_freeze["files"].items():
        path = PRIMARY / name
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Original frozen experiment drifted: {name}")
        bind(files, f"primary/{name}", path)
    bind(files, "primary/results/DEV_METRICS.json", PRIMARY / "results/DEV_METRICS.json")
    bind(files, "source/RULES_FREEZE.json", SOURCE_EXP / "RULES_FREEZE.json")
    bind(files, "source/RUN_FREEZE.json", SOURCE_EXP / "RUN_FREEZE.json")
    run_freeze = json.loads((SOURCE_EXP / "RUN_FREEZE.json").read_text())
    for name, expected in run_freeze["files"].items():
        path = SOURCE_EXP / name
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Source experiment drifted: {name}")
        bind(files, f"source/{name}", path)
    bind(files, "smoke/SMOKE_METRICS.json", HERE / "artifacts/SMOKE_METRICS.json")
    bind(files, "smoke/SMOKE_CASES.jsonl", HERE / "artifacts/SMOKE_CASES.jsonl")
    result = {
        "version": CONFIG["version"],
        "status": "FROZEN_BEFORE_FULL_PANEL",
        "full_panel_started": False,
        "python_version": sys.version,
        "platform": platform.platform(),
        "files": files,
        "source_catalogue_sha256": CONFIG["source_catalogue_sha256"],
        "planned": {"user_cohorts": 2, "prior_banks": 2, "crossed_panels": 4,
                    "unique_profiles": 24, "profile_menu_cases": 96, "trace_rows": 2784},
        "smoke_receipt_sha256": sha256(HERE / "artifacts/SMOKE_METRICS.json"),
        "smoke_trace_sha256": smoke["trace_sha256"],
        "claim_limit": "Development robustness only; no model calls, no training, no population inference.",
    }
    target.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "bound_files": len(files),
                      "catalogue_sha256": result["source_catalogue_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
