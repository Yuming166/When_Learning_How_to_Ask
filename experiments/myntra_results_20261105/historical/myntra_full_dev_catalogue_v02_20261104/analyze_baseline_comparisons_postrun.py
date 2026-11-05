#!/usr/bin/env python3
"""Compute clustered paired 95% intervals for all frozen budget-5 baselines."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

import run_full_dev as run

HERE = Path(__file__).resolve().parent
METRICS = json.loads((HERE / "results/CATALOGUE_METRICS.json").read_text())
TRACE = HERE / "results/PAIRED_CASES.jsonl"
rows = run.read_jsonl(TRACE)
budget = run.CONFIG["primary_budget"]
primary = [row for row in rows if row["budget"] == budget and row["method"] != "ask_all"]
by_case_method = {(row["case_id"], row["method"]): row for row in primary}
case_ids = sorted({row["case_id"] for row in primary})
methods = ["fixed_order", "profile_ig", "decision_set_ig"]
comparisons = {}

for baseline in methods:
    dv = [by_case_method[(case_id, "decision_value")] for case_id in case_ids]
    other = [by_case_method[(case_id, baseline)] for case_id in case_ids]
    differences = [int(a["exact_decision_correct"]) - int(b["exact_decision_correct"])
                   for a, b in zip(dv, other)]
    cluster_means, interval = run.stratified_profile_bootstrap(
        primary, baseline, run.CONFIG["bootstrap_repetitions"], run.CONFIG["bootstrap_seed"])
    counts = collections.Counter(1 if value > 0 else -1 if value < 0 else 0
                                 for value in cluster_means.values())
    comparisons[baseline] = {
        "baseline_correct": sum(row["exact_decision_correct"] for row in other),
        "decision_value_correct": sum(row["exact_decision_correct"] for row in dv),
        "denominator": len(case_ids),
        "baseline_accuracy": sum(row["exact_decision_correct"] for row in other) / len(case_ids),
        "decision_value_accuracy": sum(row["exact_decision_correct"] for row in dv) / len(case_ids),
        "paired_correct_difference": sum(differences),
        "paired_mean_difference": sum(differences) / len(differences),
        "paired_difference_95_ci": [interval["lower_95"], interval["upper_95"]],
        "profile_clusters_positive_negative_tied": {
            "positive": counts[1], "negative": counts[-1], "tied": counts[0]},
        "ci_excludes_zero": interval["lower_95"] > 0 or interval["upper_95"] < 0,
        "interval_method": "10,000-replicate profile-cluster bootstrap stratified by cohort and category; percentile interval",
    }

primary_ci = comparisons["decision_set_ig"]["paired_difference_95_ci"]
saved_ci = METRICS["primary_paired_difference"]["stratified_profile_bootstrap"]
if abs(primary_ci[0] - saved_ci["lower_95"]) > 1e-12 or abs(primary_ci[1] - saved_ci["upper_95"]) > 1e-12:
    raise RuntimeError("Recomputed primary interval does not reproduce the frozen metric")

payload = {
    "status": "POSTRUN_COMPARATIVE_INTERVALS",
    "budget": budget,
    "primary_method": "decision_value",
    "case_denominator": len(case_ids),
    "comparisons": comparisons,
    "primary_interval_reproduces_frozen_metric": True,
    "multiple_comparison_adjustment": "none; intervals are descriptive and unadjusted",
    "trace_sha256": hashlib.sha256(TRACE.read_bytes()).hexdigest(),
    "claim_limit": "Conditional on the deterministic synthetic-profile generator and this finite development catalogue; not a human or held-out-catalogue estimate.",
}
target = HERE / "results/BASELINE_COMPARISONS_POSTRUN.json"
if target.exists():
    raise FileExistsError(f"Preserve existing output: {target}")
target.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False, indent=2))
