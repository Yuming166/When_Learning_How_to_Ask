#!/usr/bin/env python3
"""Analyze the frozen full 0-6 budget curves with paired profile-cluster CIs."""
from __future__ import annotations

import collections
import hashlib
import json
import math
import random
from pathlib import Path

import run_confirmation as run

HERE = Path(__file__).resolve().parent
BASELINES = ["fixed_order", "profile_ig", "decision_set_ig"]


def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] if lo == hi else ordered[lo] * (hi - position) + ordered[hi] * (position - lo)


def analyze_split(split):
    trace = HERE / f"results/{split}_PAIRED_CASES.jsonl"
    completion = HERE / f"results/{split}_RUN_COMPLETED.json"
    if not trace.is_file() or not completion.is_file():
        raise FileNotFoundError(f"Incomplete frozen split run: {split}")
    rows = run.rows(trace)
    evaluated = [r for r in rows if r["method"] != "ask_all"]
    case_ids = sorted({r["case_id"] for r in evaluated})
    expected_rows = len(case_ids) * len(run.CONFIG["methods"]) * len(run.CONFIG["budgets"]) + len(case_ids)
    if len(rows) != expected_rows:
        raise RuntimeError(f"Trace denominator mismatch for {split}: {len(rows)} != {expected_rows}")
    by_key = {(r["case_id"], r["method"], r["budget"]): r for r in evaluated}
    if len(by_key) != len(evaluated):
        raise RuntimeError(f"Duplicate policy records in {split}")
    profiles = {}
    for row in evaluated:
        profiles[row["profile_id"]] = (row["user_cohort"], row["category"])
    strata = collections.defaultdict(list)
    cases_by_profile = collections.defaultdict(list)
    for case_id in case_ids:
        row = next(r for r in evaluated if r["case_id"] == case_id)
        cases_by_profile[row["profile_id"]].append(case_id)
    for profile_id, meta in profiles.items():
        strata[meta].append(profile_id)
    if set(cases_by_profile) != set(profiles):
        raise RuntimeError("Profile clustering metadata mismatch")

    curves = {}
    for method in run.CONFIG["methods"]:
        curves[method] = {}
        for budget in run.CONFIG["budgets"]:
            correct = sum(bool(by_key[(cid, method, budget)]["exact_decision_correct"]) for cid in case_ids)
            subset = [by_key[(cid, method, budget)] for cid in case_ids]
            curves[method][str(budget)] = {
                "correct": correct, "denominator": len(case_ids), "accuracy": correct / len(case_ids),
                "purchase_recall_cases_correct": sum(bool(r["purchase_recall_case"]) for r in subset),
                "correct_no_buy_cases": sum(bool(r["no_buy_correct_case"]) for r in subset),
                "false_purchase_cases": sum(bool(r["false_purchase_case"]) for r in subset),
                "hard_constraint_violations": sum(bool(r["hard_constraint_violation"]) for r in subset),
                "mean_normalized_score_regret": sum(r["normalized_score_regret"] for r in subset) / len(subset),
            }

    contrasts = [(baseline, budget) for baseline in BASELINES for budget in run.CONFIG["budgets"]]
    observed = {}
    cluster_sum = {key: collections.Counter() for key in contrasts}
    cluster_count = collections.Counter()
    cluster_signs = {}
    for profile_id, profile_cases in cases_by_profile.items():
        cluster_count[profile_id] = len(profile_cases)
        for baseline, budget in contrasts:
            delta = sum(int(by_key[(cid, "decision_value", budget)]["exact_decision_correct"])
                        - int(by_key[(cid, baseline, budget)]["exact_decision_correct"])
                        for cid in profile_cases)
            cluster_sum[(baseline, budget)][profile_id] = delta
    denominator = len(case_ids)
    for key in contrasts:
        observed[key] = sum(cluster_sum[key].values()) / denominator
        vals = [cluster_sum[key][profile] / cluster_count[profile] for profile in cases_by_profile]
        cluster_signs[key] = {"positive": sum(x > 0 for x in vals),
                              "negative": sum(x < 0 for x in vals), "tied": sum(x == 0 for x in vals)}

    rng_seed = run.CONFIG["bootstrap_seed"] + (0 if split == "validation_reserved" else 1)
    rng = random.Random(rng_seed)
    reps = run.CONFIG["bootstrap_repetitions"]
    samples = {key: [] for key in contrasts}
    max_abs_deviations = []
    for _ in range(reps):
        chosen = []
        for stratum in sorted(strata):
            members = strata[stratum]
            chosen.extend(rng.choice(members) for _ in members)
        sampled_denominator = sum(cluster_count[p] for p in chosen)
        draw = {key: sum(cluster_sum[key][p] for p in chosen) / sampled_denominator for key in contrasts}
        deviations = []
        for key in contrasts:
            samples[key].append(draw[key])
            deviations.append(abs(draw[key] - observed[key]))
        max_abs_deviations.append(max(deviations))
    simultaneous_radius = percentile(max_abs_deviations, 0.95)
    paired = {}
    for baseline, budget in contrasts:
        boot = samples[(baseline, budget)]
        pointwise = [percentile(boot, 0.025), percentile(boot, 0.975)]
        estimate = observed[(baseline, budget)]
        simultaneous = [max(-1.0, estimate - simultaneous_radius), min(1.0, estimate + simultaneous_radius)]
        paired.setdefault(baseline, {})[str(budget)] = {
            "decision_value_minus_baseline": estimate,
            "pointwise_profile_cluster_95_ci": pointwise,
            "simultaneous_profile_cluster_95_ci": simultaneous,
            "profile_cluster_signs": cluster_signs[(baseline, budget)],
        }

    # AUC is the arithmetic mean of the seven equally spaced cost points; descriptive only.
    auc = {method: sum(curves[method][str(b)]["accuracy"] for b in run.CONFIG["budgets"])
                   / len(run.CONFIG["budgets"]) for method in run.CONFIG["methods"]}
    auc_diff = {baseline: auc["decision_value"] - auc[baseline] for baseline in BASELINES}
    noninferiority = all(paired[b][str(budget)]["simultaneous_profile_cluster_95_ci"][0] >= 0
                         for b, budget in contrasts)
    primary = paired[run.CONFIG["primary_baseline"]][str(run.CONFIG["primary_budget"])]
    categories = sorted({r["category"] for r in evaluated})
    by_category = {}
    for category in categories:
        case_subset = [cid for cid in case_ids if next(r for r in evaluated if r["case_id"] == cid)["category"] == category]
        by_category[category] = {method: {
            "correct": sum(bool(by_key[(cid, method, run.CONFIG["primary_budget"])]["exact_decision_correct"])
                            for cid in case_subset),
            "denominator": len(case_subset),
            "accuracy": sum(bool(by_key[(cid, method, run.CONFIG["primary_budget"])]["exact_decision_correct"])
                            for cid in case_subset) / len(case_subset),
        } for method in run.CONFIG["methods"]}
    return {
        "split": split, "status": "ALL_BUDGET_NONINFERIORITY_SUPPORTED" if noninferiority
                  else "ALL_BUDGET_NONINFERIORITY_NOT_SUPPORTED",
        "cases": len(case_ids), "unique_profiles": len(profiles),
        "menus": len({r["menu_id"] for r in evaluated}),
        "products": sum(len(x["items"]) for x in run.rows(HERE / f"artifacts/prepared/{split}/public/menus.jsonl")),
        "accuracy_curves": curves, "descriptive_mean_accuracy_over_budgets_0_to_6": auc,
        "descriptive_auc_difference_decision_value_minus_baseline": auc_diff,
        "paired_profile_cluster_contrasts": paired,
        "primary_anchor_budget_5_decision_value_minus_decision_set_ig": primary,
        "simultaneous_family": "3 baselines x 7 budgets; max absolute deviation bootstrap band",
        "simultaneous_radius": simultaneous_radius,
        "all_21_simultaneous_lower_bounds_nonnegative": noninferiority,
        "category_accuracy_at_budget_5": by_category,
        "bootstrap": {"repetitions": reps, "seed": rng_seed,
                      "resampling": "profiles resampled within user-cohort x category strata; all menus for profile clustered",
                      "scope": "synthetic profile-generator uncertainty conditional on fixed finite held-out menus"},
        "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
        "model_calls": 0, "training_runs": 0,
    }


def main():
    run.verify_frozen()
    results = {split: analyze_split(split) for split in run.CONFIG["splits"]}
    payload = {"status": "FROZEN_HELDOUT_ANALYSIS_COMPLETE", "version": run.CONFIG["version"],
               "splits": results,
               "claim_limit": "Deterministic synthetic users; fixed finite reserved products; no human or cross-catalogue claim.",
               "model_calls": 0, "training_runs": 0}
    target = HERE / "results/ANALYSIS.json"
    if target.exists():
        raise FileExistsError("Preserve prior analysis output")
    run.dump(target, payload)
    lines = ["# Myntra 保留集确认结果", "", "本实验使用确定性程序画像，不调用 Qwen/Luna，不代表真人偏好。所有预算 0–6 均保留；区间只反映画像生成分布下的不确定性，商品菜单固定。", ""]
    for split, record in results.items():
        lines += [f"## {split}", "", f"样本：{record['cases']} 个画像-菜单案例，{record['unique_profiles']} 个画像，{record['menus']} 个菜单、{record['products']} 件商品。", "", "|预算|Fixed Order|Profile IG|Decision-Set IG|Decision Value|DV − Decision-Set IG (95% 点态 CI)|", "|---:|---:|---:|---:|---:|---:|"]
        for budget in run.CONFIG["budgets"]:
            curve = record["accuracy_curves"]
            d = record["paired_profile_cluster_contrasts"]["decision_set_ig"][str(budget)]
            ci = d["pointwise_profile_cluster_95_ci"]
            lines.append(f"|{budget}|{curve['fixed_order'][str(budget)]['accuracy']:.1%}|{curve['profile_ig'][str(budget)]['accuracy']:.1%}|{curve['decision_set_ig'][str(budget)]['accuracy']:.1%}|{curve['decision_value'][str(budget)]['accuracy']:.1%}|{d['decision_value_minus_baseline']:+.1%} [{ci[0]:+.1%}, {ci[1]:+.1%}]|")
        anchor = record["primary_anchor_budget_5_decision_value_minus_decision_set_ig"]
        sim = record["paired_profile_cluster_contrasts"]["decision_set_ig"]["5"]["simultaneous_profile_cluster_95_ci"]
        lines += ["", f"预算 5 的历史主比较：DV − Decision-Set IG = {anchor['decision_value_minus_baseline']:+.1%}；点态 95% CI [{anchor['pointwise_profile_cluster_95_ci'][0]:+.1%}, {anchor['pointwise_profile_cluster_95_ci'][1]:+.1%}]，覆盖全部 21 个对比的同时 95% 区间 [{sim[0]:+.1%}, {sim[1]:+.1%}]。", f"所有预算、所有基线的同时下界均非负：**{record['all_21_simultaneous_lower_bounds_nonnegative']}**。判定：`{record['status']}`。", "", "注意：同时区间覆盖 Fixed Order、Profile IG、Decision-Set IG 三个基线与七个预算。预算 6 是完整问询后的正确性检查，不构成效率优势。", ""]
    report = HERE / "results/REPORT_ZH.md"
    if report.exists():
        raise FileExistsError("Preserve prior report")
    report.write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
