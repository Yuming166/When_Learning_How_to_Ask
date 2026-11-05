#!/usr/bin/env python3
"""Run the frozen crossed robustness panel using deterministic local policies."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = json.loads((HERE / "config.json").read_text())
PRIMARY = HERE.parent / CONFIG["frozen_policy_experiment"]
SOURCE = Path(CONFIG["source_worktree"])
SOURCE_EXP = SOURCE / "experiments/myntra_preference_dev_v01_20261104"
FREEZE_PATH = HERE / "FROZEN.json"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def append_jsonl(path, values):
    with Path(path).open("a", encoding="utf-8") as f:
        for value in values:
            f.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_frozen():
    if not FREEZE_PATH.exists():
        raise RuntimeError("FROZEN.json is missing; freeze only after tests and smoke pass")
    frozen = json.loads(FREEZE_PATH.read_text())
    for label, entry in frozen["files"].items():
        path = Path(entry["path"])
        if not path.is_file():
            raise RuntimeError(f"Frozen file is missing: {label}={path}")
        if sha256(path) != entry["sha256"]:
            raise RuntimeError(f"Frozen file changed: {label}")
    if frozen["status"] != "FROZEN_BEFORE_FULL_PANEL":
        raise RuntimeError("Unexpected freeze status")
    return frozen


def load_engines():
    policy = load_module("myntra_frozen_policy_engine", PRIMARY / "engine.py")
    env = policy.load_environment(SOURCE)
    return policy, env


def make_cohort(env, label):
    source_cfg = env.read(env.BASE / "config.json")
    cfg = dict(source_cfg)
    cfg["seed_root"] = CONFIG["cohorts"][label]
    cfg["profiles_per_pool"] = CONFIG["profiles_per_pool"]
    prepared = []
    vocabularies = env.read(PRIMARY / "artifacts/prepared/public/vocabularies.json")
    for pool in range(len(source_cfg["pools"])):
        for profile in env.generate_profiles(vocabularies[str(pool)], pool, cfg):
            profile = dict(profile)
            profile["profile_id"] = f"{label}-{profile['profile_id']}"
            profile["robustness_cohort"] = label
            prepared.append(profile)
    if len(prepared) != 12 or len({p["profile_id"] for p in prepared}) != 12:
        raise AssertionError(f"Bad cohort size/IDs for {label}")
    return prepared


def make_prior(env, seed_label, count):
    source_cfg = env.read(env.BASE / "config.json")
    cfg = dict(source_cfg)
    cfg["seed_root"] = CONFIG["prior_seeds"][seed_label]
    cfg["profiles_per_pool"] = count
    vocabularies = env.read(PRIMARY / "artifacts/prepared/public/vocabularies.json")
    return {
        pool: env.generate_profiles(vocabularies[str(pool)], pool, cfg)
        for pool in range(len(source_cfg["pools"]))
    }


def frozen_menus(policy):
    path = PRIMARY / "artifacts/prepared/public/menus.jsonl"
    menus = {menu["menu_id"]: menu for menu in read_jsonl(path)}
    if len(menus) != 6 or sum(len(m["items"]) for m in menus.values()) != 48:
        raise AssertionError("Frozen menu count or item count changed")
    return menus


def cases_for(cohort, menus, case_filter=None):
    cases = []
    for profile in cohort:
        pool_menus = [m for m in menus.values() if m["pool_index"] == profile["pool_index"]]
        for menu in sorted(pool_menus, key=lambda x: x["menu_id"]):
            case_id = f"{profile['robustness_cohort']}:{profile['profile_id'].split('-', 1)[1]}:{menu['menu_id']}"
            if case_filter is None or case_id in case_filter:
                cases.append((case_id, profile, menu))
    return cases


def execute(smoke=False):
    if not smoke:
        verify_frozen()
    policy, env = load_engines()
    menus = frozen_menus(policy)
    cohorts = {name: make_cohort(env, name) for name in CONFIG["cohorts"]}
    count = 128 if smoke else CONFIG["prior_profiles_per_pool"]
    prior_seeds = [CONFIG["smoke_prior_seed"]] if smoke else list(CONFIG["prior_seeds"])
    priors = {seed: make_prior(env, seed, count) for seed in prior_seeds}
    selected = set(CONFIG["smoke_case_ids"]) if smoke else None
    destination = HERE / ("artifacts/SMOKE_CASES.jsonl" if smoke else "results/PAIRED_CASES.jsonl")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Preserve existing run output: {destination}")
    completed_cases = 0
    expected_case_panels = 4 if not smoke else 1
    case_count_per_cohort = 24 if not smoke else 2
    expected_rows = case_count_per_cohort * expected_case_panels * (len(CONFIG["methods"]) * 7 + 1)
    panel_labels = []

    with destination.open("x", encoding="utf-8") as out:
        for user_seed, cohort in cohorts.items():
            if smoke and user_seed != CONFIG["smoke_case_ids"][0].split(":", 1)[0]:
                continue
            for prior_seed in prior_seeds:
                panel_id = f"users_{user_seed}__prior_{prior_seed}"
                panel_labels.append(panel_id)
                selected_cases = cases_for(cohort, menus, selected)
                if not smoke and len(selected_cases) != 24:
                    raise AssertionError(f"Incomplete panel {panel_id}: {len(selected_cases)}")
                if smoke and len(selected_cases) != 2:
                    raise AssertionError(f"Smoke case selection mismatch: {len(selected_cases)}")
                for case_id, profile, menu in selected_cases:
                    rows = []
                    public_case = {"case_id": case_id, "menu_id": menu["menu_id"], "public_menu": menu}
                    prior = priors[prior_seed][profile["pool_index"]]
                    for method in CONFIG["methods"]:
                        rows.extend(policy.run_case(env, public_case, profile, prior, method, max(CONFIG["budgets"])))
                    rows.append(policy.run_ask_all(env, public_case, profile))
                    for row in rows:
                        row["panel_id"] = panel_id
                        row["user_cohort"] = user_seed
                        row["prior_seed"] = prior_seed
                        row["case_id"] = case_id
                        out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    out.flush()
                    os.fsync(out.fileno())
                    completed_cases += 1
                    print(f"completed {panel_id}: {completed_cases}/{case_count_per_cohort * expected_case_panels} cases", flush=True)

    rows = read_jsonl(destination)
    if len(rows) != expected_rows:
        raise AssertionError(f"Trace row denominator: {len(rows)} != {expected_rows}")
    if smoke:
        receipt = {
            "status": "PASS",
            "panels": panel_labels,
            "cases": completed_cases,
            "trace_rows": len(rows),
            "prior_profiles_per_pool": count,
            "model_calls": 0,
            "training_runs": 0,
            "six_question_exact_terminals": sum(r["method"] != "ask_all" and r["budget"] == 6 and r["exact_decision_correct"] for r in rows),
            "full_disclosure_exact_terminals": sum(r["method"] == "ask_all" and r["exact_decision_correct"] for r in rows),
            "trace_sha256": policy.sha256(destination),
        }
        dump(HERE / "artifacts/SMOKE_METRICS.json", receipt)
        if receipt["six_question_exact_terminals"] != 2 * len(CONFIG["methods"]):
            raise AssertionError("Smoke full-disclosure terminal check failed")
        if receipt["full_disclosure_exact_terminals"] != 2:
            raise AssertionError("Smoke ask-all check failed")
        return receipt

    analyze(policy, rows, destination)
    return json.loads((HERE / "results/ROBUSTNESS_METRICS.json").read_text())


def analyze(policy, rows, trace_path):
    budget = CONFIG["primary_budget"]
    primary = [r for r in rows if r["method"] != "ask_all" and r["budget"] == budget]
    by_case = {(r["panel_id"], r["case_id"], r["method"]): r for r in primary}
    panels = sorted({r["panel_id"] for r in primary})
    comparisons = ["fixed_order", "profile_ig"]
    panel_results = {}
    gate_each = {}
    for baseline in comparisons:
        diffs = {}
        for panel in panels:
            pairs = [(by_case[(panel, cid, "decision_value")]["exact_decision_correct"],
                      by_case[(panel, cid, baseline)]["exact_decision_correct"])
                     for p, cid, method in by_case if p == panel and method == "decision_value"]
            diffs[panel] = sum(int(a) - int(b) for a, b in pairs) / len(pairs)
        clusters = collections.defaultdict(list)
        for panel, case_id, method in by_case:
            if method != "decision_value":
                continue
            row_dv = by_case[(panel, case_id, "decision_value")]
            row_base = by_case[(panel, case_id, baseline)]
            cluster = f"{row_dv['user_cohort']}:{row_dv['case_id'].split(':')[1]}"
            clusters[cluster].append(int(row_dv["exact_decision_correct"]) - int(row_base["exact_decision_correct"]))
        cluster_means = {key: sum(values) / len(values) for key, values in sorted(clusters.items())}
        pooled_mean = sum(cluster_means.values()) / len(cluster_means)
        positive_clusters = sum(value > 0 for value in cluster_means.values())
        positive_panels = sum(value > 0 for value in diffs.values())
        passed = (positive_panels >= CONFIG["robustness_gate"]["minimum_positive_panels_out_of_4"]
                  and pooled_mean > 0
                  and positive_clusters >= CONFIG["robustness_gate"]["minimum_positive_unique_profile_clusters"])
        gate_each[baseline] = passed
        panel_results[baseline] = {
            "panel_case_mean_difference": diffs,
            "positive_panels": positive_panels,
            "unique_profile_cluster_count": len(cluster_means),
            "pooled_unique_profile_mean_difference": pooled_mean,
            "positive_unique_profile_clusters": positive_clusters,
            "profile_cluster_mean_differences": cluster_means,
            "gate_pass": passed,
        }

    rows_by = collections.defaultdict(list)
    for r in rows:
        if r["method"] != "ask_all":
            rows_by[(r["method"], r["budget"])].append(r)
    curves = {method: {str(b): {
        "correct": sum(r["exact_decision_correct"] for r in rows_by[(method, b)]),
        "denominator": len(rows_by[(method, b)]),
        "accuracy": sum(r["exact_decision_correct"] for r in rows_by[(method, b)]) / len(rows_by[(method, b)]),
        "purchase_recall_numerator": sum(r["purchase_recall_case"] for r in rows_by[(method, b)]),
        "no_buy_correct_numerator": sum(r["no_buy_correct_case"] for r in rows_by[(method, b)]),
        "false_purchase_numerator": sum(r["false_purchase_case"] for r in rows_by[(method, b)]),
        "hard_constraint_violations": sum(r["hard_constraint_violation"] for r in rows_by[(method, b)]),
        "mean_normalized_score_regret": sum(r["normalized_score_regret"] for r in rows_by[(method, b)]) / len(rows_by[(method, b)]),
    } for b in CONFIG["budgets"]} for method in CONFIG["methods"]}
    panel_summary = {}
    for panel in panels:
        case_rows = [r for r in primary if r["panel_id"] == panel]
        panel_summary[panel] = {
            method: {
                "correct": sum(r["exact_decision_correct"] for r in case_rows if r["method"] == method),
                "denominator": sum(r["method"] == method for r in case_rows),
                "accuracy": sum(r["exact_decision_correct"] for r in case_rows if r["method"] == method) / 24,
            } for method in CONFIG["methods"]
        }
    labels = collections.Counter(r["reference_decision"] for r in primary if r["method"] == "decision_value")
    ask_all = [r for r in rows if r["method"] == "ask_all"]
    metrics = {
        "status": "ROBUST_ADVANTAGE_ESTABLISHED_BY_DESCRIPTIVE_GATE" if all(gate_each.values()) else "ROBUST_ADVANTAGE_NOT_ESTABLISHED",
        "interpretation": "Development robustness evidence only; deterministic users and frozen menus; no population inference.",
        "primary_budget": budget,
        "panels": panel_summary,
        "comparison_gates": panel_results,
        "both_primary_comparisons_pass": all(gate_each.values()),
        "full_denominators": {"panels": len(panels), "cases_per_panel": 24, "unique_profiles": 24,
                              "profile_menu_cases": len(primary) // len(CONFIG["methods"]),
                              "BUY_profile_menu_cases": labels["BUY"], "NO_BUY_profile_menu_cases": labels["NO_BUY"],
                              "full_profile_ask_all": len(ask_all)},
        "curves": curves,
        "ask_all": {"correct": sum(r["exact_decision_correct"] for r in ask_all), "denominator": len(ask_all),
                    "dialogue_turns": sorted({r["dialogue_turns"] for r in ask_all}),
                    "elicitation_units": sorted({r["elicitation_units"] for r in ask_all})},
        "trace_rows": len(rows),
        "trace_sha256": policy.sha256(trace_path),
        "model_calls": 0,
        "training_runs": 0,
        "significance_tests": 0,
        "confidence_intervals": 0,
    }
    dump(HERE / "results/ROBUSTNESS_METRICS.json", metrics)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if args.smoke == args.full:
        parser.error("choose exactly one of --smoke or --full")
    if args.full:
        started = HERE / "results/RUN_STARTED.json"
        if started.exists():
            raise FileExistsError("Full run already started; preserve its evidence and do not rerun")
        verify_frozen()
        dump(started, {"status": "FULL_PANEL_STARTED_ONCE", "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                       "planned_panels": 4, "planned_cases": 96, "planned_trace_rows": 2784})
    print(json.dumps(execute(smoke=args.smoke), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
