#!/usr/bin/env python3
"""Supplement the frozen category-name aggregation with the six gender/category pools."""
from __future__ import annotations

import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
SAVED_METRICS = json.loads((HERE / "results/CATALOGUE_METRICS.json").read_text())
PRIMARY_METHOD = SAVED_METRICS["primary_method"]
rows = [json.loads(line) for line in (HERE / "results/PAIRED_CASES.jsonl").read_text().splitlines()]
paired = {(row["case_id"], row["method"]): row for row in rows
          if row["budget"] == CONFIG["primary_budget"] and row["method"] != "ask_all"}
diffs = collections.defaultdict(list)
for row in rows:
    if row["budget"] != CONFIG["primary_budget"] or row["method"] != PRIMARY_METHOD:
        continue
    baseline = paired[(row["case_id"], CONFIG["primary_baseline"])]
    diffs[(row["gender"], row["category"])].append(
        int(row["exact_decision_correct"]) - int(baseline["exact_decision_correct"]))

pool_metrics = {
    f"{gender}/{category}": {
        "correct_difference": sum(values),
        "denominator": len(values),
        "mean_difference": sum(values) / len(values),
        "direction": "positive" if sum(values) > 0 else "negative" if sum(values) < 0 else "tie",
    }
    for (gender, category), values in sorted(diffs.items())
}
payload = {
    "status": "SUPPLEMENTAL_POSTRUN_AUDIT",
    "purpose": "Recompute the frozen six-pool robustness criterion by gender/category because the frozen metrics aggregate both Kurtas pools under one category name.",
    "source_trace_sha256": __import__("hashlib").sha256(
        (HERE / "results/PAIRED_CASES.jsonl").read_bytes()).hexdigest(),
    "method": PRIMARY_METHOD,
    "baseline": CONFIG["primary_baseline"],
    "budget": CONFIG["primary_budget"],
    "pools": pool_metrics,
    "positive_pools": sum(x["direction"] == "positive" for x in pool_metrics.values()),
    "negative_pools": sum(x["direction"] == "negative" for x in pool_metrics.values()),
    "tied_pools": sum(x["direction"] == "tie" for x in pool_metrics.values()),
    "six_pool_gate_passed": sum(x["direction"] == "positive" for x in pool_metrics.values()) >= 4,
    "positive_profile_clusters": SAVED_METRICS["primary_paired_difference"]["positive_profile_clusters"],
    "predeclared_profile_cluster_gate_passed": SAVED_METRICS["primary_paired_difference"]["positive_profile_clusters"] >= CONFIG["robustness_gate"]["minimum_positive_profile_clusters_out_of_48"],
    "claim_limit": "Post-run diagnostic of the already frozen trace; no method, data, or outcome was changed.",
}
target = HERE / "results/POSTRUN_POOL_ANALYSIS.json"
if target.exists():
    raise FileExistsError(f"Preserve existing output: {target}")
target.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False, indent=2))
