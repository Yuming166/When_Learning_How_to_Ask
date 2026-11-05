#!/usr/bin/env python3
"""Freeze the bounded panel after smoke; refuses to overwrite the receipt."""
import json
import platform
from pathlib import Path

import engine


HERE = Path(__file__).resolve().parent


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-worktree", type=Path,
                        default=Path("/home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104"))
    args = parser.parse_args()
    source_worktree = args.source_worktree.resolve()
    target = HERE / "FREEZE.json"
    if target.exists():
        raise FileExistsError("FREEZE.json already exists; preserve it")
    source = source_worktree / engine.CONFIG["source_experiment"]
    env = engine.load_environment(source_worktree)
    env.prepare(HERE / "artifacts/freeze_replay_check")
    files = ["config.json", "PROTOCOL.md", "engine.py", "run.py", "test_closed_loop.py", "freeze.py"]
    payload = {
        "status": "FROZEN_BEFORE_FULL_PANEL",
        "source_worktree_label": source_worktree.name,
        "source_environment_sha256": engine.sha256(source / "environment.py"),
        "source_rules_freeze_sha256": engine.sha256(source / "RULES_FREEZE.json"),
        "source_catalogue_sha256": engine.sha256(source / "artifacts/input/catalogue_strict.jsonl"),
        "files": {name: engine.sha256(HERE / name) for name in files},
        "python_version": platform.python_version(),
        "full_panel_started": False,
    }
    if payload["source_catalogue_sha256"] != engine.CONFIG["source_catalogue_sha256"]:
        raise RuntimeError("Source catalogue hash differs from frozen config")
    target.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"freeze": str(target), "files": len(files),
                      "source_catalogue_sha256": payload["source_catalogue_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
