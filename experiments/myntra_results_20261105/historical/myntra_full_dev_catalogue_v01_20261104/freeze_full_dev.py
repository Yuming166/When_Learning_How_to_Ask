#!/usr/bin/env python3
"""One-shot pre-full-run freeze of code, data, and the preceding result."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
PRIMARY = HERE.parent / CONFIG["policy_experiment"]
PREVIOUS = HERE.parent / CONFIG["previous_robustness_experiment"]
SOURCE = Path(CONFIG["source_worktree"])
SOURCE_EXP = SOURCE / "experiments/myntra_preference_dev_v01_20261104"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bind(files, label, path, expected=None):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Missing frozen input {label}: {path}")
    digest = sha256(path)
    if expected is not None and digest != expected:
        raise RuntimeError(f"Upstream frozen file changed: {label}")
    files[label] = {"path": str(path), "sha256": digest}


def bind_manifest(files, prefix, directory, manifest_path):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    bind(files, f"{prefix}/{manifest_path.name}", manifest_path)
    for name, expected in manifest["files"].items():
        bind(files, f"{prefix}/{name}", Path(directory) / name, expected)


def main():
    target = HERE / "FROZEN.json"
    if target.exists():
        raise FileExistsError("Preserve the existing pre-run freeze")
    audit = json.loads((HERE / "results/CATALOGUE_AUDIT.json").read_text())
    smoke = json.loads((HERE / "artifacts/SMOKE_METRICS.json").read_text())
    if audit.get("status") != "PASS" or audit.get("development_records_used") != 338:
        raise RuntimeError("Complete development catalogue audit before freezing")
    if smoke.get("status") != "PASS" or smoke.get("cases") != 2:
        raise RuntimeError("Smoke must pass before freezing")
    files = {}
    for name in ["config.json", "PROTOCOL.md", "run_full_dev.py", "test_full_dev.py", "freeze_full_dev.py", "verify_full_dev.py"]:
        bind(files, f"current/{name}", HERE / name)
    bind(files, "current/results/CATALOGUE_AUDIT.json", HERE / "results/CATALOGUE_AUDIT.json")

    primary_freeze_path = PRIMARY / "FREEZE.json"
    primary_freeze = json.loads(primary_freeze_path.read_text())
    bind(files, "primary/FREEZE.json", primary_freeze_path)
    for name, expected in primary_freeze["files"].items():
        bind(files, f"primary/{name}", PRIMARY / name, expected)
    bind(files, "primary/results/DEV_METRICS.json", PRIMARY / "results/DEV_METRICS.json")

    previous_freeze_path = PREVIOUS / "FROZEN.json"
    previous_freeze = json.loads(previous_freeze_path.read_text())
    bind(files, "previous_robustness/FROZEN.json", previous_freeze_path)
    for label, entry in previous_freeze["files"].items():
        bind(files, f"previous_robustness/{label}", entry["path"], entry["sha256"])
    for name in ["REPORT_ZH.md", "REPRODUCE.md", "results/ROBUSTNESS_METRICS.json",
                 "results/PAIRED_CASES.jsonl", "results/VERIFICATION.json"]:
        bind(files, f"previous_robustness/{name}", PREVIOUS / name)

    source_rules = SOURCE_EXP / "RULES_FREEZE.json"
    source_run = SOURCE_EXP / "RUN_FREEZE.json"
    bind_manifest(files, "source_rules", SOURCE_EXP, source_rules)
    bind_manifest(files, "source_run", SOURCE_EXP, source_run)

    prepared = HERE / "artifacts/prepared"
    for name in ["public/menus.jsonl", "public/vocabularies.json", "public/cases.jsonl",
                 "private/user_profiles.jsonl", "private/prior_profiles.jsonl",
                 "private/menu_provenance.json", "evaluator_only/references.jsonl"]:
        bind(files, f"prepared/{name}", prepared / name)
    bind(files, "smoke/SMOKE_METRICS.json", HERE / "artifacts/SMOKE_METRICS.json")
    bind(files, "smoke/SMOKE_CASES.jsonl", HERE / "artifacts/SMOKE_CASES.jsonl")

    frozen = {
        "version": CONFIG["version"],
        "status": "FROZEN_BEFORE_FULL_PANEL",
        "full_panel_started": False,
        "python_version": sys.version,
        "platform": platform.platform(),
        "files": files,
        "scope": "all 338 development products; zero validation/test products; 35 menus; two 24-profile cohorts; one independent 2,048-per-pool prior bank",
        "planned": {"development_products": 338, "reserved_products": 133, "menus": 35,
                    "profiles": 48, "profile_menu_cases": 280, "paired_trace_rows": 8120},
        "source_catalogue_sha256": CONFIG["source_catalogue_sha256"],
        "smoke_metrics_sha256": sha256(HERE / "artifacts/SMOKE_METRICS.json"),
        "smoke_trace_sha256": smoke["trace_sha256"],
        "claim_limit": "Development catalogue census with deterministic synthetic profiles; no model calls, no human generalization, no cross-catalogue inference.",
    }
    target.write_text(json.dumps(frozen, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": frozen["status"], "bound_files": len(files),
                      "products": 338, "menus": 35, "cases": 280,
                      "source_catalogue_sha256": frozen["source_catalogue_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
