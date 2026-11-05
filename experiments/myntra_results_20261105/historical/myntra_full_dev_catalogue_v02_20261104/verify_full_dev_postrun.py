#!/usr/bin/env python3
"""Run the frozen post-run verifier with its omitted FROZEN path supplied."""
from __future__ import annotations

import json
import hashlib
import verify_full_dev


if __name__ == "__main__":
    here = verify_full_dev.HERE
    target = here / "results/VERIFICATION.json"
    if target.exists():
        receipt = json.loads(target.read_text())
        hash_file = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        expected = {
            "freeze_sha256": hash_file(here / "FROZEN.json"),
            "metrics_sha256": hash_file(here / "results/CATALOGUE_METRICS.json"),
            "trace_sha256": hash_file(here / "results/PAIRED_CASES.jsonl"),
        }
        if any(receipt.get(key) != value for key, value in expected.items()):
            raise RuntimeError("Existing verification receipt no longer matches frozen artifacts")
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        # The frozen verifier references this module constant but does not define it.
        # Supply the expected local path without changing the frozen verifier itself.
        verify_full_dev.FROZEN = here / "FROZEN.json"
        verify_full_dev.main()
