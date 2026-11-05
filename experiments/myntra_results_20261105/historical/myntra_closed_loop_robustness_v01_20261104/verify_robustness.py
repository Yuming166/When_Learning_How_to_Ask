#!/usr/bin/env python3
"""Independent post-run integrity and predeclared-gate audit."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_robustness as run


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def main():
    run.verify_frozen()
    policy = run.load_module("verify_frozen_policy_engine", run.PRIMARY / "engine.py")
    metrics_path = HERE / "results/ROBUSTNESS_METRICS.json"
    trace_path = HERE / "results/PAIRED_CASES.jsonl"
    started_path = HERE / "results/RUN_STARTED.json"
    metrics = json.loads(metrics_path.read_text())
    rows = run.read_jsonl(trace_path)
    require(json.loads(started_path.read_text())["status"] == "FULL_PANEL_STARTED_ONCE", "single_full_run_receipt")
    require(len(rows) == 2784, "full_trace_rows")
    require(run.sha256(trace_path) == metrics["trace_sha256"], "trace_hash")
    require(metrics["model_calls"] == 0 and metrics["training_runs"] == 0, "no_model_or_training")

    panels = {"users_A__prior_A", "users_A__prior_B", "users_B__prior_A", "users_B__prior_B"}
    methods = set(run.CONFIG["methods"])
    keyed = {}
    cases_by_panel = collections.defaultdict(set)
    profiles_by_cohort = collections.defaultdict(set)
    for row in rows:
        key = (row["panel_id"], row["case_id"], row["method"], row["budget"])
        require(key not in keyed, f"duplicate:{key}")
        keyed[key] = row
        cases_by_panel[row["panel_id"]].add(row["case_id"])
        profiles_by_cohort[row["user_cohort"]].add(row["profile_id"])
        if row["method"] != "ask_all":
            require(row["method"] in methods, "known_method")
            require(len(row["query_sequence"]) == row["budget"], f"query_count:{key}")
            require(len(set(row["query_sequence"])) == row["budget"], f"unique_queries:{key}")
            require(set(row["query_sequence"]).issubset(set(policy.CONFIG["query_actions"])), f"legal_queries:{key}")
    require(set(cases_by_panel) == panels, "four_crossed_panels")
    require(all(len(cases_by_panel[p]) == 24 for p in panels), "24_cases_per_panel")
    require({k: len(v) for k, v in profiles_by_cohort.items()} == {"A": 12, "B": 12}, "12_profiles_per_cohort")

    method_counts = collections.Counter((r["panel_id"], r["method"], r["budget"]) for r in rows if r["method"] != "ask_all")
    for panel in panels:
        for method in methods:
            for budget in run.CONFIG["budgets"]:
                require(method_counts[(panel, method, budget)] == 24, f"denominator:{panel}:{method}:{budget}")
            terminal = [r for r in rows if r["panel_id"] == panel and r["method"] == method and r["budget"] == 6]
            require(sum(r["exact_decision_correct"] for r in terminal) == 24, f"six_question_terminal:{panel}:{method}")

    ask_all = [r for r in rows if r["method"] == "ask_all"]
    require(len(ask_all) == 96, "ask_all_denominator")
    require(sum(r["exact_decision_correct"] for r in ask_all) == 96, "ask_all_correct")
    require(all(r["dialogue_turns"] == 1 and r["elicitation_units"] == 6 for r in ask_all), "ask_all_cost")

    primary_budget = run.CONFIG["primary_budget"]
    primary = [r for r in rows if r["method"] != "ask_all" and r["budget"] == primary_budget]
    reference_counts = collections.Counter(r["reference_decision"] for r in primary if r["method"] == "decision_value")
    require(reference_counts == {"BUY": 52, "NO_BUY": 44}, "primary_class_denominator")
    check = {}
    for baseline in run.CONFIG["robustness_gate"]["compare_against"]:
        cluster_diffs = collections.defaultdict(list)
        panel_diffs = {}
        for panel in sorted(panels):
            panel_cases = sorted(cases_by_panel[panel])
            differences = []
            for case_id in panel_cases:
                dv = keyed[(panel, case_id, "decision_value", primary_budget)]
                base = keyed[(panel, case_id, baseline, primary_budget)]
                diff = int(dv["exact_decision_correct"]) - int(base["exact_decision_correct"])
                differences.append(diff)
                cluster = f"{dv['user_cohort']}:{case_id.split(':')[1]}"
                cluster_diffs[cluster].append(diff)
            panel_diffs[panel] = sum(differences) / len(differences)
        cluster_means = {k: sum(v) / len(v) for k, v in cluster_diffs.items()}
        positive_panels = sum(v > 0 for v in panel_diffs.values())
        positive_clusters = sum(v > 0 for v in cluster_means.values())
        pooled = sum(cluster_means.values()) / len(cluster_means)
        gate = (positive_panels >= run.CONFIG["robustness_gate"]["minimum_positive_panels_out_of_4"]
                and positive_clusters >= run.CONFIG["robustness_gate"]["minimum_positive_unique_profile_clusters"]
                and pooled > 0)
        saved = metrics["comparison_gates"][baseline]
        require(panel_diffs == saved["panel_case_mean_difference"], f"saved_panel_diffs:{baseline}")
        require(abs(pooled - saved["pooled_unique_profile_mean_difference"]) < 1e-12, f"saved_pooled:{baseline}")
        require(positive_clusters == saved["positive_unique_profile_clusters"], f"saved_clusters:{baseline}")
        require(gate == saved["gate_pass"], f"saved_gate:{baseline}")
        check[baseline] = {"positive_panels": positive_panels, "panels": 4,
                           "pooled_unique_profile_mean_difference": pooled,
                           "positive_unique_profile_clusters": positive_clusters,
                           "unique_profile_clusters": len(cluster_means), "gate_pass": gate}

    expected_status = "ROBUST_ADVANTAGE_ESTABLISHED_BY_DESCRIPTIVE_GATE" if all(x["gate_pass"] for x in check.values()) else "ROBUST_ADVANTAGE_NOT_ESTABLISHED"
    require(metrics["status"] == expected_status, "status_recomputed")
    receipt = {
        "status": "PASS",
        "verification_scope": "frozen_inputs_trace_integrity_full_denominators_terminal_replay_and_predeclared_descriptive_gate",
        "checks": {
            "frozen_file_bindings": len(json.loads((HERE / "FROZEN.json").read_text())["files"]),
            "crossed_panels": len(panels), "cases_per_panel": 24, "unique_profiles": 24,
            "trace_rows": len(rows), "method_budget_cells": len(panels) * len(methods) * 7,
            "six_question_exact_terminals": len(panels) * len(methods),
            "ask_all_exact_terminals": len(ask_all), "primary_comparisons": check,
            "model_calls": 0, "training_runs": 0,
        },
        "metrics_sha256": run.sha256(metrics_path),
        "trace_sha256": run.sha256(trace_path),
        "freeze_sha256": run.sha256(HERE / "FROZEN.json"),
    }
    target = HERE / "results/VERIFICATION.json"
    if target.exists():
        raise FileExistsError("Preserve existing verification receipt")
    target.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
