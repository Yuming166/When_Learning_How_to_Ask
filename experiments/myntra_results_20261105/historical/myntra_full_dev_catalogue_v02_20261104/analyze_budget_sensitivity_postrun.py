#!/usr/bin/env python3
"""Summarize the frozen 0-6 budget curve and clustered DV-vs-Decision-Set-IG intervals."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

import run_full_dev as run

HERE = Path(__file__).resolve().parent
TRACE = HERE / "results/PAIRED_CASES.jsonl"
rows = run.read_jsonl(TRACE)
curves = {}
for budget in run.CONFIG["budgets"]:
    sample = [row for row in rows if row["budget"] == budget and row["method"] != "ask_all"]
    by_case_method = {(row["case_id"], row["method"]): row for row in sample}
    case_ids = sorted({row["case_id"] for row in sample})
    accuracies = {}
    for method in run.CONFIG["methods"]:
        correct = sum(by_case_method[(case_id, method)]["exact_decision_correct"] for case_id in case_ids)
        accuracies[method] = {"correct": correct, "denominator": len(case_ids), "accuracy": correct / len(case_ids)}
    differences = [int(by_case_method[(case_id, "decision_value")]["exact_decision_correct"])
                   - int(by_case_method[(case_id, "decision_set_ig")]["exact_decision_correct"])
                   for case_id in case_ids]
    cluster_means, interval = run.stratified_profile_bootstrap(
        sample, "decision_set_ig", run.CONFIG["bootstrap_repetitions"], run.CONFIG["bootstrap_seed"])
    sign_counts = collections.Counter("positive" if value > 0 else "negative" if value < 0 else "tie"
                                      for value in cluster_means.values())
    curves[str(budget)] = {
        "accuracy_by_method": accuracies,
        "decision_value_minus_decision_set_ig": {
            "correct_difference": sum(differences),
            "mean_difference": sum(differences) / len(differences),
            "95_ci": [interval["lower_95"], interval["upper_95"]],
            "profile_cluster_signs": {"positive": sign_counts["positive"],
                                       "negative": sign_counts["negative"],
                                       "tied": sign_counts["tie"]},
        },
    }

payload = {
    "status": "POSTRUN_BUDGET_SENSITIVITY",
    "trace_sha256": hashlib.sha256(TRACE.read_bytes()).hexdigest(),
    "budgets": curves,
    "interval_method": "10,000-replicate profile-cluster bootstrap stratified by cohort and category; percentile intervals; no multiple-comparison adjustment",
    "claim_limit": "Exploratory budget curve on the frozen development catalogue; budget 4 was not the preregistered primary point and must be confirmed independently before emphasis.",
}
target = HERE / "results/BUDGET_SENSITIVITY_POSTRUN.json"
if target.exists():
    raise FileExistsError(f"Preserve existing output: {target}")
target.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False, indent=2))
