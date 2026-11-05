#!/usr/bin/env python3
"""Post-run frozen-input, coverage, denominator, and gate audit."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_full_dev as run


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def main():
    run.verify_frozen()
    policy, env = run.load_engine()
    metrics_path = HERE / "results/CATALOGUE_METRICS.json"
    trace_path = HERE / "results/PAIRED_CASES.jsonl"
    rows = run.read_jsonl(trace_path)
    metrics = json.loads(metrics_path.read_text())
    started = json.loads((HERE / "results/RUN_STARTED.json").read_text())
    completed = json.loads((HERE / "results/RUN_COMPLETED.json").read_text())
    require(started["status"] == "FULL_PANEL_STARTED_ONCE", "single_full_run")
    require(started["planned_cases"] == 280, "planned_case_denominator")
    require(started["workers"] == run.CONFIG["execution_workers"], "frozen_worker_count")
    require(started["start_method"] == run.CONFIG["execution_start_method"], "frozen_start_method")
    require(completed["status"] == "FULL_PANEL_COMPLETED_AND_ANALYZED", "run_completion")
    require(completed["trace_sha256"] == run.sha256(trace_path), "completion_trace_hash")
    require(completed["trace_rows"] == 8120 and completed["cases"] == 280, "completion_denominators")
    require(len(rows) == 8120, "full_trace_rows")
    require(run.sha256(trace_path) == metrics["trace_sha256"], "trace_hash")
    require(metrics["model_calls"] == 0 and metrics["training_runs"] == 0, "no_models_or_training")
    require(all(row["reference_replay_agrees"] for row in rows), "independent_reference_replay")

    prepared = HERE / "artifacts/prepared"
    source_rows, development, reserved = run.audit_source(env)
    menus = run.read_jsonl(prepared / "public/menus.jsonl")
    cases = run.read_jsonl(prepared / "public/cases.jsonl")
    profiles = run.read_jsonl(prepared / "private/user_profiles.jsonl")
    priors = run.read_jsonl(prepared / "private/prior_profiles.jsonl")
    refs = run.read_jsonl(prepared / "evaluator_only/references.jsonl")
    provenance = json.loads((prepared / "private/menu_provenance.json").read_text())
    require(len(source_rows) == 471 and len(development) == 338 and len(reserved) == 133, "source_split")
    require(len(menus) == 35 and len(profiles) == 48 and len(cases) == 280, "prepared_denominators")
    require(len(priors) == 12288 and len(refs) == 280, "prior_and_reference_denominators")
    menu_ids = {item["product_id"] for menu in menus for item in menu["items"]}
    dev_ids = {row["product_id"] for row in development}
    reserved_ids = {row["product_id"] for row in reserved}
    require(menu_ids == dev_ids and not (menu_ids & reserved_ids), "all_and_only_development_products")
    owner = {}
    for menu_id, record in provenance.items():
        for group in record["leakage_group_ids"]:
            require(group not in owner, f"leakage_group_split:{group}")
            owner[group] = menu_id

    unique = {}
    panel_cases = collections.defaultdict(set)
    profile_case_count = collections.Counter()
    for row in rows:
        key = (row["case_id"], row["method"], row["budget"])
        require(key not in unique, f"duplicate_trace:{key}")
        unique[key] = row
        panel_cases[row["user_cohort"]].add(row["case_id"])
        profile_case_count[(row["profile_id"], row["method"], row["budget"])] += 1
        if row["method"] != "ask_all":
            require(row["method"] in run.CONFIG["methods"], "method_id")
            require(len(row["query_sequence"]) == row["budget"], f"query_count:{key}")
            require(len(set(row["query_sequence"])) == row["budget"], f"query_uniqueness:{key}")
            require(set(row["query_sequence"]).issubset(set(policy.CONFIG["query_actions"])), f"legal_queries:{key}")
    require({cohort: len(values) for cohort, values in panel_cases.items()} == {"A": 140, "B": 140}, "cohort_case_counts")

    method_counts = collections.Counter((r["method"], r["budget"]) for r in rows if r["method"] != "ask_all")
    for method in run.CONFIG["methods"]:
        for budget in run.CONFIG["budgets"]:
            require(method_counts[(method, budget)] == 280, f"method_budget_denominator:{method}:{budget}")
        terminal = [r for r in rows if r["method"] == method and r["budget"] == 6]
        require(len(terminal) == 280 and all(r["exact_decision_correct"] for r in terminal), f"terminal:{method}")
    ask_all = [r for r in rows if r["method"] == "ask_all"]
    require(len(ask_all) == 280 and all(r["exact_decision_correct"] for r in ask_all), "ask_all_accuracy")
    require(all(r["dialogue_turns"] == 1 and r["elicitation_units"] == 6 for r in ask_all), "ask_all_cost")

    b = run.CONFIG["primary_budget"]
    primary = [r for r in rows if r["method"] != "ask_all" and r["budget"] == b]
    key_primary = {(r["case_id"], r["method"]): r for r in primary}
    baseline = run.CONFIG["primary_baseline"]
    cohort_diffs = {}
    for cohort in ["A", "B"]:
        rr = [r for r in primary if r["method"] == "decision_value" and r["user_cohort"] == cohort]
        dd = [int(r["exact_decision_correct"]) - int(key_primary[(r["case_id"], baseline)]["exact_decision_correct"]) for r in rr]
        cohort_diffs[cohort] = sum(dd) / len(dd)
    cat_diffs = {}
    for category in sorted({r["category"] for r in primary}):
        rr = [r for r in primary if r["method"] == "decision_value" and r["category"] == category]
        dd = [int(r["exact_decision_correct"]) - int(key_primary[(r["case_id"], baseline)]["exact_decision_correct"]) for r in rr]
        cat_diffs[category] = sum(dd) / len(dd)
    profile_clusters, bootstrap = run.stratified_profile_bootstrap(
        primary, baseline, run.CONFIG["bootstrap_repetitions"], run.CONFIG["bootstrap_seed"])
    pooled = sum(int(key_primary[(cid, "decision_value")]["exact_decision_correct"])
                 - int(key_primary[(cid, baseline)]["exact_decision_correct"])
                 for cid in {r["case_id"] for r in primary}) / 280
    positive_clusters = sum(v > 0 for v in profile_clusters.values())
    positive_categories = sum(v > 0 for v in cat_diffs.values())
    gate = (pooled > 0 and bootstrap["lower_95"] > 0 and all(v > 0 for v in cohort_diffs.values())
            and positive_categories >= run.CONFIG["robustness_gate"]["minimum_positive_categories_out_of_6"]
            and positive_clusters >= run.CONFIG["robustness_gate"]["minimum_positive_profile_clusters_out_of_48"])
    saved = metrics["primary_paired_difference"]
    require(abs(pooled - saved["mean_difference"]) < 1e-12, "saved_pooled_difference")
    require(cohort_diffs == {k: v["mean_difference"] for k, v in saved["cohort_differences"].items()}, "saved_cohort_differences")
    require(cat_diffs == {k: v["mean_difference"] for k, v in saved["category_differences"].items()}, "saved_category_differences")
    require(positive_clusters == saved["positive_profile_clusters"], "saved_profile_cluster_count")
    require(bootstrap == saved["stratified_profile_bootstrap"], "saved_bootstrap")
    require(gate == metrics["gate"]["passed"], "saved_gate")

    receipt = {
        "status": "PASS",
        "scope": "frozen_source_complete_development_coverage_full_denominators_exact_terminals_and_predeclared_gate",
        "checks": {"frozen_files": len(json.loads(FROZEN.read_text())["files"]),
                   "source_records": 471, "development_records_used": 338, "reserved_records_used": 0,
                   "menus": len(menus), "user_profiles": len(profiles), "prior_profiles": len(priors),
                   "profile_menu_cases": len(cases), "trace_rows": len(rows),
                   "method_budget_cells": len(run.CONFIG["methods"]) * 7,
                   "six_question_exact_terminals": len(run.CONFIG["methods"]) * 280,
                   "ask_all_exact_terminals": len(ask_all), "primary_gate_passed": gate,
                   "model_calls": 0, "training_runs": 0},
        "metrics_sha256": run.sha256(metrics_path), "trace_sha256": run.sha256(trace_path),
        "freeze_sha256": run.sha256(FROZEN),
    }
    target = HERE / "results/VERIFICATION.json"
    if target.exists():
        raise FileExistsError("Preserve existing verification receipt")
    target.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
