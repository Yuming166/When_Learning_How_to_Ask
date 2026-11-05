#!/usr/bin/env python3
"""Post-run source, denominator, replay, and result-integrity checks."""
from __future__ import annotations

import collections
import json
from pathlib import Path

import engine


HERE = Path(__file__).resolve().parent
SOURCE = Path("/home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104")


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def main():
    env = engine.load_environment(SOURCE)
    input_path = SOURCE / engine.CONFIG["source_experiment"] / "artifacts/input/catalogue_strict.jsonl"
    require(engine.sha256(input_path) == engine.CONFIG["source_catalogue_sha256"], "source_catalogue_hash")
    metrics_path = HERE / "results/DEV_METRICS.json"
    trace_path = HERE / "results/PAIRED_CASES.jsonl"
    result = json.loads(metrics_path.read_text())
    rows = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
    require(result["status"] == "DEVELOPMENT_COMPLETE", "status")
    require(result["model_calls"] == 0 and result["training_runs"] == 0, "no_model_or_training")
    require(result["evaluation_cases"] == 24 and result["evaluation_profiles"] == 12, "full_denominator")
    require(result["reference_class_counts"] == {"BUY": 6, "NO_BUY": 18}, "outcome_class_denominator")
    require(len(rows) == 696, "trace_rows")

    observed = collections.Counter((r["method"], r["budget"]) for r in rows if r["method"] != "ask_all")
    for method in engine.CONFIG["methods"]:
        for budget in range(7):
            require(observed[(method, budget)] == 24, f"denominator:{method}:{budget}")
        final = [r for r in rows if r["method"] == method and r["budget"] == 6]
        require(sum(r["exact_decision_correct"] for r in final) == 24, f"full_disclosure_replay:{method}")
        for row in [r for r in rows if r["method"] == method]:
            require(len(row["query_sequence"]) == row["budget"], f"budget_sequence:{method}:{row['case_id']}:{row['budget']}")
            require(len(set(row["query_sequence"])) == row["budget"], f"no_repeated_questions:{method}:{row['case_id']}:{row['budget']}")

    ask_all = [r for r in rows if r["method"] == "ask_all"]
    require(len(ask_all) == 24, "ask_all_denominator")
    require(sum(r["exact_decision_correct"] for r in ask_all) == 24, "ask_all_exact")
    require(all(r["dialogue_turns"] == 1 and r["elicitation_units"] == 6 for r in ask_all), "ask_all_cost")

    prepared = HERE / "artifacts/prepared"
    profiles = {x["profile_id"]: x for x in env.rows(prepared / "private/profiles.jsonl")}
    menus = {x["menu_id"]: x for x in env.rows(prepared / "public/menus.jsonl")}
    references = {x["case_id"]: x for x in env.rows(prepared / "evaluator_only/references.jsonl")}
    source_items = env.rows(input_path)
    development_ids = {x["product_id"] for x in source_items if x["split"] == "development"}
    checked = 0
    for case_id, record in references.items():
        profile = profiles[record["profile_id"]]
        items = menus[record["menu_id"]]["items"]
        require({x["product_id"] for x in items} <= development_ids, f"development_only:{case_id}")
        require(env.evaluate_python(items, profile) == record["reference"], f"reference_replay:{case_id}")
        checked += 1

    receipt = {
        "status": "PASS",
        "verification_scope": "source_binding_full_denominators_costs_recommendation_replay_and_run_receipt",
        "checks": {
            "source_catalogue_hash": 1,
            "full_denominator_and_class_balance": 1,
            "paired_method_budget_coverage": sum(observed.values()),
            "all_exact_six_question_terminals": len(engine.CONFIG["methods"]),
            "ask_all_one_turn_six_units": 24,
            "independent_reference_replay": checked,
            "development_menu_items_only": 24,
            "model_calls": 0,
            "training_runs": 0,
        },
        "trace_rows": len(rows),
        "evaluated_cases": 24,
        "source_catalogue_sha256": engine.sha256(input_path),
        "result_sha256": engine.sha256(metrics_path),
        "trace_sha256": engine.sha256(trace_path),
    }
    path = HERE / "results/VERIFICATION.json"
    if path.exists():
        raise FileExistsError("Verification receipt exists; preserve it")
    path.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
