#!/usr/bin/env python3
"""Create a clean reproduction copy without local users, priors, or outputs."""
import argparse
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
ALLOWLIST = [
    ".gitignore", "config.json", "PROTOCOL.md", "README_ZH.md", "REPRODUCE.md",
    "engine.py", "run.py", "test_closed_loop.py", "freeze.py", "FREEZE.json",
    "verify_results.py", "prepare_reproduction.py",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        raise FileExistsError(f"Destination exists: {destination}")
    destination.mkdir(parents=True)
    for name in ALLOWLIST:
        shutil.copy2(HERE / name, destination / name)
    print(f"Created clean reproduction copy with {len(ALLOWLIST)} allow-listed files: {destination}")


if __name__ == "__main__":
    main()
