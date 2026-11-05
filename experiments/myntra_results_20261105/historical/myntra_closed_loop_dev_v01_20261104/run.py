#!/usr/bin/env python3
"""Run smoke or the one-shot, bounded Myntra closed-loop development panel."""
from __future__ import annotations

import argparse
import collections
import json
import platform
from pathlib import Path

import engine


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"
PREPARED = ARTIFACTS / "prepared"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def verify_frozen(source_worktree: Path):
    freeze_path = HERE / "FREEZE.json"
    if not freeze_path.exists():
        raise RuntimeError("Full run requires FREEZE.json; run the smoke stage and freeze first")
    freeze = json.loads(freeze_path.read_text())
    for relative, expected in freeze["files"].items():
        path = HERE / relative
        if engine.sha256(path) != expected:
            raise RuntimeError(f"Frozen experiment file changed: {relative}")
    source = source_worktree / engine.CONFIG["source_experiment"]
    if engine.sha256(source / "environment.py") != freeze["source_environment_sha256"]:
        raise RuntimeError("Source environment changed after freeze")
    if engine.sha256(source / "artifacts/input/catalogue_strict.jsonl") != freeze["source_catalogue_sha256"]:
        raise RuntimeError("Source catalogue changed after freeze")


def ensure_prepared(env):
    if not PREPARED.exists():
        env.prepare(PREPARED)
    required = [
        PREPARED / "public/menus.jsonl",
        PREPARED / "public/cases.jsonl",
        PREPARED / "public/vocabularies.json",
        PREPARED / "private/profiles.jsonl",
        PREPARED / "evaluator_only/references.jsonl",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Prepared data incomplete: " + ", ".join(missing))


def data_bundle(env):
    menus = {item["menu_id"]: item for item in load_jsonl(PREPARED / "public/menus.jsonl")}
    profiles = {item["profile_id"]: item for item in load_jsonl(PREPARED / "private/profiles.jsonl")}
    cases = load_jsonl(PREPARED / "public/cases.jsonl")
    references = {item["case_id"]: item for item in load_jsonl(PREPARED / "evaluator_only/references.jsonl")}
    vocabularies = json.loads((PREPARED / "public/vocabularies.json").read_text())
    if len(profiles) != 12 or len(menus) != 6 or len(cases) != 24 or len(references) != 24:
        raise RuntimeError("Unexpected v0.1 denominator")
    for case in cases:
        if case["case_id"] not in references:
            raise RuntimeError(f"Missing evaluator record for {case['case_id']}")
        if case["menu_id"] not in menus:
            raise RuntimeError(f"Missing public menu for {case['menu_id']}")
    return menus, profiles, cases, references, vocabularies


def summarize(rows, profile_ids):
    by_profile = collections.defaultdict(list)
    for row in rows:
        by_profile[row["profile_id"]].append(row)

    def mean(key, subset=rows):
        return sum(float(row[key]) for row in subset) / len(subset) if subset else None

    buy_rows = [row for row in rows if row["reference_decision"] == "BUY"]
    no_buy_rows = [row for row in rows if row["reference_decision"] == "NO_BUY"]
    profile_metric_means = {}
    for metric in ["exact_decision_correct", "score_regret", "normalized_score_regret", "hard_constraint_violation"]:
        per_profile = []
        for pid in profile_ids:
            current = by_profile.get(pid, [])
            if current:
                per_profile.append(sum(float(x[metric]) for x in current) / len(current))
        profile_metric_means[metric] = sum(per_profile) / len(per_profile) if per_profile else None
    return {
        "cases": len(rows),
        "profiles": len(by_profile),
        "case_mean_exact_decision_accuracy": mean("exact_decision_correct"),
        "profile_cluster_mean_exact_decision_accuracy": profile_metric_means["exact_decision_correct"],
        "buy_cases": len(buy_rows),
        "buy_case_recall": sum(bool(x["purchase_recall_case"]) for x in buy_rows) / len(buy_rows) if buy_rows else None,
        "no_buy_cases": len(no_buy_rows),
        "no_buy_specificity": sum(bool(x["no_buy_correct_case"]) for x in no_buy_rows) / len(no_buy_rows) if no_buy_rows else None,
        "false_purchase_rate_on_no_buy_cases": sum(bool(x["false_purchase_case"]) for x in no_buy_rows) / len(no_buy_rows) if no_buy_rows else None,
        "case_mean_score_regret": mean("score_regret"),
        "profile_cluster_mean_score_regret": profile_metric_means["score_regret"],
        "case_mean_normalized_score_regret": mean("normalized_score_regret"),
        "profile_cluster_mean_normalized_score_regret": profile_metric_means["normalized_score_regret"],
        "case_hard_constraint_violation_rate": mean("hard_constraint_violation"),
        "profile_cluster_mean_hard_constraint_violation_rate": profile_metric_means["hard_constraint_violation"],
    }


def run_stage(stage: str, source_worktree: Path):
    env = engine.load_environment(source_worktree)
    ensure_prepared(env)
    if stage == "full":
        verify_frozen(source_worktree)
        out_file = HERE / "results/DEV_METRICS.json"
        trace_file = HERE / "results/PAIRED_CASES.jsonl"
        if out_file.exists() or trace_file.exists():
            raise FileExistsError("Full-run outputs exist; preserving this one-shot panel")
        prior_count = engine.CONFIG["prior_profiles_per_pool"]
        case_ids = None
    else:
        out_file = ARTIFACTS / "SMOKE_METRICS.json"
        trace_file = ARTIFACTS / "SMOKE_CASES.jsonl"
        if out_file.exists() or trace_file.exists():
            raise FileExistsError("Smoke outputs exist; preserving prior smoke evidence")
        prior_count = 128
        case_ids = set(engine.CONFIG["smoke_case_ids"])

    menus, profiles, all_cases, refs, vocabularies = data_bundle(env)
    cases = [case for case in all_cases if case_ids is None or case["case_id"] in case_ids]
    if case_ids is not None and {case["case_id"] for case in cases} != case_ids:
        raise RuntimeError("Declared smoke case IDs are not available")
    prior_by_pool = engine.make_prior_profiles(env, vocabularies, prior_count)
    all_records = []
    by_method_budget = collections.defaultdict(list)

    for case in cases:
        profile_id = refs[case["case_id"]]["profile_id"]
        profile = profiles[profile_id]
        menu = menus[case["menu_id"]]
        public_case = {"case_id": case["case_id"], "menu_id": case["menu_id"], "public_menu": menu}
        prior = prior_by_pool[int(profile["pool_index"])]
        for method in engine.CONFIG["methods"]:
            records = engine.run_case(env, public_case, profile, prior, method, 6)
            for row in records:
                all_records.append(row)
                by_method_budget[(method, row["budget"])].append(row)
        all_records.append(engine.run_ask_all(env, public_case, profile))

    profile_ids = sorted({refs[case["case_id"]]["profile_id"] for case in cases})
    summaries = []
    fixed_lookup = {}
    for budget in range(7):
        fixed_lookup[budget] = {row["case_id"]: row for row in by_method_budget[("fixed_order", budget)]}
    for method in engine.CONFIG["methods"]:
        for budget in range(7):
            rows = by_method_budget[(method, budget)]
            summary = summarize(rows, profile_ids)
            summary.update({"method": method, "budget": budget,
                            "mean_dialogue_turns": sum(row["dialogue_turns"] for row in rows) / len(rows),
                            "mean_elicitation_units": sum(row["elicitation_units"] for row in rows) / len(rows)})
            if method != "fixed_order":
                paired = []
                for row in rows:
                    base = fixed_lookup[budget][row["case_id"]]
                    paired.append({"profile_id": row["profile_id"],
                                   "difference": float(row["exact_decision_correct"]) - float(base["exact_decision_correct"])})
                cluster = collections.defaultdict(list)
                for item in paired:
                    cluster[item["profile_id"]].append(item["difference"])
                summary["paired_accuracy_difference_vs_fixed_order_case_mean"] = sum(x["difference"] for x in paired) / len(paired)
                summary["paired_accuracy_difference_vs_fixed_order_profile_mean"] = sum(sum(v) / len(v) for v in cluster.values()) / len(cluster)
            summaries.append(summary)

    ask_all = [row for row in all_records if row["method"] == "ask_all"]
    overall = {
        "status": "DEVELOPMENT_COMPLETE",
        "stage": stage,
        "model_calls": 0,
        "training_runs": 0,
        "source_catalogue_sha256": engine.CONFIG["source_catalogue_sha256"],
        "source_environment_sha256": engine.sha256(source_worktree / engine.CONFIG["source_experiment"] / "environment.py"),
        "prior_seed_root": engine.CONFIG["prior_seed_root"],
        "prior_profiles_per_pool": prior_count,
        "evaluation_cases": len(cases),
        "evaluation_profiles": len(profile_ids),
        "reference_class_counts": dict(collections.Counter(refs[case["case_id"]]["reference"]["decision"] for case in cases)),
        "posterior_estimation": "Empirical Monte Carlo prior, generated independently from held-out evaluation profiles using the frozen synthetic profile generator.",
        "policy_methods": summaries,
        "whole_profile_shortcut": summarize(ask_all, profile_ids) | {"method": "ask_all", "dialogue_turns": 1, "elicitation_units": 6},
        "claim_scope": "Descriptive development results for deterministic exact disclosure under a constructed synthetic profile prior; no reliability, human, Qwen/Luna, or generalization claim.",
        "python_version": platform.python_version(),
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(overall, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    trace_file.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in all_records))
    print(json.dumps({"stage": stage, "episodes": len(cases), "prior_per_pool": prior_count,
                      "methods": len(engine.CONFIG["methods"]), "metrics": str(out_file),
                      "paired_rows": len(all_records), "ask_all_accuracy": overall["whole_profile_shortcut"]["case_mean_exact_decision_accuracy"]},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["smoke", "full"], required=True)
    parser.add_argument("--source-worktree", type=Path,
                        default=Path("/home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104"))
    args = parser.parse_args()
    run_stage(args.stage, args.source_worktree.resolve())


if __name__ == "__main__":
    main()
