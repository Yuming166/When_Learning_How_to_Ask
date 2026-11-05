#!/usr/bin/env python3
"""Evaluate frozen elicitation policies on every eligible Myntra dev item."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
PRIMARY = HERE.parent / CONFIG["policy_experiment"]
PREVIOUS = HERE.parent / CONFIG["previous_robustness_experiment"]
SOURCE = Path(CONFIG["source_worktree"])
SOURCE_EXP = SOURCE / "experiments/myntra_preference_dev_v01_20261104"
SOURCE_CATALOGUE = SOURCE_EXP / "artifacts/input/catalogue_strict.jsonl"
FROZEN = HERE / "FROZEN.json"
FIELDS = ["neckline", "sleeve_length", "fabric", "wash_care", "pattern"]


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def dump_jsonl(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_engine():
    module = load_module("myntra_full_dev_frozen_engine", PRIMARY / "engine.py")
    return module, module.load_environment(SOURCE)


def keyed_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def audit_source(env):
    if sha256(SOURCE_CATALOGUE) != CONFIG["source_catalogue_sha256"]:
        raise RuntimeError("Catalogue snapshot hash mismatch")
    rows = env.rows(SOURCE_CATALOGUE)
    if len(rows) != 471:
        raise RuntimeError(f"Expected 471 frozen source rows, got {len(rows)}")
    if len({row["product_id"] for row in rows}) != 471:
        raise RuntimeError("Duplicate product IDs in source snapshot")
    split_by_group = collections.defaultdict(set)
    for row in rows:
        split_by_group[row["leakage_group_id"]].add(row["split"])
    mixed_groups = [gid for gid, splits in split_by_group.items() if len(splits) != 1]
    if mixed_groups:
        raise RuntimeError(f"Leakage groups cross reserved splits: {len(mixed_groups)}")
    development = [row for row in rows if row["split"] == "development"]
    reserved = [row for row in rows if row["split"] != "development"]
    if len(development) != 338 or len(reserved) != 133:
        raise RuntimeError(f"Unexpected split sizes: dev={len(development)} reserved={len(reserved)}")
    selected = {(gender, category) for gender, category in CONFIG["pools"]}
    observed = {(row["gender"], row["category"]) for row in development}
    if observed != selected:
        raise RuntimeError(f"Development category set drift: {observed ^ selected}")
    for row in development:
        for field in FIELDS:
            entry = row.get("attributes", {}).get(field, {})
            if entry.get("status") != "reported" or not isinstance(entry.get("value"), str) or not entry["value"]:
                raise RuntimeError(f"Core attribute missing: {row['product_id']}:{field}")
    return rows, development, reserved


def build_menus(env, development):
    menus, vocabularies, provenance = [], {}, {}
    by_pool = collections.defaultdict(list)
    for row in development:
        by_pool[(row["gender"], row["category"])].append(row)
    for pool_index, (gender, category) in enumerate(CONFIG["pools"]):
        candidates = by_pool[(gender, category)]
        vocab = {field: sorted({row["attributes"][field]["value"] for row in candidates}) for field in FIELDS}
        if any(len(values) < 2 for values in vocab.values()):
            raise RuntimeError(f"Insufficient profile vocabulary: {gender}/{category}")
        vocabularies[str(pool_index)] = vocab
        group_map = collections.defaultdict(list)
        for row in candidates:
            group_map[row["leakage_group_id"]].append(row)
        n_menus = math.ceil(len(candidates) / CONFIG["menu_target_size"])
        bins = [[] for _ in range(n_menus)]
        ordered_groups = sorted(
            group_map.items(),
            key=lambda pair: (-len(pair[1]), keyed_hash(
                f"{CONFIG['menu_seed_root']}|{gender}|{category}|group|{pair[0]}")),
        )
        bin_ties = [keyed_hash(f"{CONFIG['menu_seed_root']}|{gender}|{category}|menu|{i}") for i in range(n_menus)]
        for group_id, group_rows in ordered_groups:
            destination = min(range(n_menus), key=lambda i: (len(bins[i]), bin_ties[i]))
            bins[destination].extend(sorted(group_rows, key=lambda row: row["product_id"]))
        for menu_index, source_rows in enumerate(bins):
            menu_id = f"M{pool_index}_{menu_index:02d}"
            items = [{
                "product_id": row["product_id"],
                "attributes": {field: row["attributes"][field]["value"] for field in FIELDS},
            } for row in source_rows]
            menu = {"menu_id": menu_id, "pool_index": pool_index, "gender": gender,
                    "category": category, "items": items}
            menus.append(menu)
            provenance[menu_id] = {
                "pool_index": pool_index,
                "source_product_ids": [row["product_id"] for row in source_rows],
                "leakage_group_ids": sorted({row["leakage_group_id"] for row in source_rows}),
                "item_count": len(source_rows),
            }
    return menus, vocabularies, provenance


def generate_profiles(env, vocabularies, cohort, seed_root, count):
    source_cfg = env.read(env.BASE / "config.json")
    cfg = dict(source_cfg)
    cfg["seed_root"] = seed_root
    cfg["profiles_per_pool"] = count
    profiles = []
    for pool_index in range(len(CONFIG["pools"])):
        for profile in env.generate_profiles(vocabularies[str(pool_index)], pool_index, cfg):
            profile = dict(profile)
            if count == CONFIG["profiles_per_pool_per_cohort"]:
                profile["profile_id"] = f"{cohort}-{profile['profile_id']}"
                profile["user_cohort"] = cohort
            else:
                profile["profile_id"] = f"PRIOR-{profile['profile_id']}"
                profile["prior_bank"] = "C"
            profiles.append(profile)
    return profiles


def construct_prepared(env):
    rows, development, reserved = audit_source(env)
    menus, vocabularies, provenance = build_menus(env, development)
    menu_group_owner = {}
    menu_product_ids = set()
    for menu in menus:
        for product_id in [item["product_id"] for item in menu["items"]]:
            if product_id in menu_product_ids:
                raise RuntimeError(f"Product assigned to multiple menus: {product_id}")
            menu_product_ids.add(product_id)
        for group_id in provenance[menu["menu_id"]]["leakage_group_ids"]:
            if group_id in menu_group_owner and menu_group_owner[group_id] != menu["menu_id"]:
                raise RuntimeError(f"Leakage group split across menus: {group_id}")
            menu_group_owner[group_id] = menu["menu_id"]
    dev_ids = {row["product_id"] for row in development}
    reserved_ids = {row["product_id"] for row in reserved}
    if menu_product_ids != dev_ids or menu_product_ids & reserved_ids:
        raise RuntimeError("Menu coverage is not exactly the development split")

    cohorts = {}
    for cohort, seed in CONFIG["user_cohorts"].items():
        profiles = generate_profiles(env, vocabularies, cohort, seed, CONFIG["profiles_per_pool_per_cohort"])
        if len(profiles) != 24:
            raise RuntimeError(f"Bad user cohort size: {cohort}")
        cohorts[cohort] = profiles
    priors = generate_profiles(env, vocabularies, "C", CONFIG["prior_seed_root"], CONFIG["prior_profiles_per_pool"])
    if len(priors) != len(CONFIG["pools"]) * CONFIG["prior_profiles_per_pool"]:
        raise RuntimeError("Prior bank size mismatch")

    references, cases = [], []
    menus_by_pool = collections.defaultdict(list)
    for menu in menus:
        menus_by_pool[menu["pool_index"]].append(menu)
    for cohort, profiles in cohorts.items():
        for profile in profiles:
            for menu in menus_by_pool[profile["pool_index"]]:
                case_id = f"{profile['profile_id']}__{menu['menu_id']}"
                py = env.evaluate_python(menu["items"], profile)
                sql = env.evaluate_sql(menu["items"], profile)
                if py != sql:
                    raise RuntimeError(f"Independent evaluators disagree: {case_id}")
                cases.append({"case_id": case_id, "profile_id": profile["profile_id"],
                              "user_cohort": cohort, "menu_id": menu["menu_id"],
                              "pool_index": profile["pool_index"]})
                references.append({"case_id": case_id, "profile_id": profile["profile_id"],
                                   "menu_id": menu["menu_id"], "reference": py})

    prepared = HERE / "artifacts/prepared"
    if prepared.exists():
        raise FileExistsError("Prepared data exists; preserve it")
    dump_jsonl(prepared / "public/menus.jsonl", menus)
    dump(prepared / "public/vocabularies.json", vocabularies)
    dump_jsonl(prepared / "public/cases.jsonl", cases)
    dump_jsonl(prepared / "private/user_profiles.jsonl", [p for values in cohorts.values() for p in values])
    dump_jsonl(prepared / "private/prior_profiles.jsonl", priors)
    dump_jsonl(prepared / "evaluator_only/references.jsonl", references)
    dump(prepared / "private/menu_provenance.json", provenance)

    split_counts = collections.Counter(row["split"] for row in rows)
    pool_audit = {}
    for index, (gender, category) in enumerate(CONFIG["pools"]):
        cat_rows = [row for row in development if (row["gender"], row["category"]) == (gender, category)]
        groups = {row["leakage_group_id"] for row in cat_rows}
        pool_menus = [menu for menu in menus if menu["pool_index"] == index]
        pool_audit[f"{gender}/{category}"] = {
            "development_records": len(cat_rows), "leakage_groups": len(groups),
            "attribute_vocab_counts": {field: len(vocabularies[str(index)][field]) for field in FIELDS},
            "menu_count": len(pool_menus), "menu_sizes": sorted(len(menu["items"]) for menu in pool_menus),
            "evaluation_cases": sum(case["pool_index"] == index for case in cases),
        }
    audit = {
        "status": "PASS",
        "source_rows": len(rows), "split_counts": dict(split_counts),
        "development_records_used": len(development), "reserved_records_used": 0,
        "development_item_coverage": len(menu_product_ids),
        "leakage_groups_kept_within_one_menu": len(menu_group_owner),
        "menus": len(menus), "menu_size_distribution": dict(collections.Counter(len(m["items"]) for m in menus)),
        "profile_cohorts": {cohort: len(profiles) for cohort, profiles in cohorts.items()},
        "profiles_per_pool_per_cohort": CONFIG["profiles_per_pool_per_cohort"],
        "prior_bank_profiles": len(priors), "prior_profiles_per_pool": CONFIG["prior_profiles_per_pool"],
        "profile_menu_cases": len(cases), "python_sql_reference_agreement": len(references),
        "pool_audit": pool_audit,
        "source_catalogue_sha256": sha256(SOURCE_CATALOGUE),
        "reserved_item_transmissions": 0, "model_calls": 0,
    }
    dump(HERE / "results/CATALOGUE_AUDIT.json", audit)
    return audit


def verify_frozen():
    if not FROZEN.exists():
        raise RuntimeError("FROZEN.json missing")
    record = json.loads(FROZEN.read_text())
    if record["status"] != "FROZEN_BEFORE_FULL_PANEL":
        raise RuntimeError("Unexpected freeze status")
    for label, entry in record["files"].items():
        path = Path(entry["path"])
        if not path.is_file() or sha256(path) != entry["sha256"]:
            raise RuntimeError(f"Frozen input changed: {label}")
    return record


def load_prepared(env):
    base = HERE / "artifacts/prepared"
    menus = {x["menu_id"]: x for x in read_jsonl(base / "public/menus.jsonl")}
    profiles = {x["profile_id"]: x for x in read_jsonl(base / "private/user_profiles.jsonl")}
    priors = collections.defaultdict(list)
    for row in read_jsonl(base / "private/prior_profiles.jsonl"):
        priors[row["pool_index"]].append(row)
    cases = read_jsonl(base / "public/cases.jsonl")
    references = {x["case_id"]: x["reference"] for x in read_jsonl(base / "evaluator_only/references.jsonl")}
    if len(menus) != 35 or len(profiles) != 48 or len(cases) != 280 or len(references) != 280:
        raise RuntimeError("Prepared denominator drift")
    if any(len(rows) != CONFIG["prior_profiles_per_pool"] for rows in priors.values()) or len(priors) != 6:
        raise RuntimeError("Prepared prior-bank coverage drift")
    return menus, profiles, priors, cases, references


def run_case_panel(policy, env, menus, profiles, priors, cases, selected=None, smoke=False):
    selected_cases = [case for case in cases if selected is None or case["case_id"] in selected]
    output = HERE / ("artifacts/SMOKE_CASES.jsonl" if smoke else "results/PAIRED_CASES.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Preserve prior output: {output}")
    expected_cases = len(selected) if selected is not None else 280
    rows_per_case = len(CONFIG["methods"]) * 7 + 1
    all_rows = []
    with output.open("x", encoding="utf-8") as handle:
        for ordinal, case in enumerate(selected_cases, start=1):
            profile = profiles[case["profile_id"]]
            menu = menus[case["menu_id"]]
            prior = priors[case["pool_index"]]
            record_case = {"case_id": case["case_id"], "menu_id": menu["menu_id"], "public_menu": menu}
            rows = []
            for method in CONFIG["methods"]:
                rows.extend(policy.run_case(env, record_case, profile, prior, method, max(CONFIG["budgets"])))
            rows.append(policy.run_ask_all(env, record_case, profile))
            for row in rows:
                row["case_id"] = case["case_id"]
                row["user_cohort"] = case["user_cohort"]
                row["pool_index"] = case["pool_index"]
                row["gender"] = menu["gender"]
                row["category"] = menu["category"]
                row["menu_size"] = len(menu["items"])
                row["reference_replay_agrees"] = row["reference_target_set"] == (
                    ["NO_BUY"] if references_lookup[case["case_id"]]["decision"] == "NO_BUY"
                    else references_lookup[case["case_id"]]["valid_purchase_ids"])
                handle.write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
            handle.flush()
            os.fsync(handle.fileno())
            all_rows.extend(rows)
            print(f"completed {ordinal}/{expected_cases}: {case['case_id']}", flush=True)
    if len(all_rows) != expected_cases * rows_per_case:
        raise RuntimeError(f"Smoke/full trace row mismatch: {len(all_rows)}")
    if not all(row["reference_replay_agrees"] for row in all_rows):
        raise RuntimeError("Policy trace reference label differs from independent evaluator")
    return output, all_rows


def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def stratified_profile_bootstrap(primary_rows, baseline, reps, seed):
    by_case_method = {(r["case_id"], r["method"]): r for r in primary_rows}
    per_profile = collections.defaultdict(list)
    profile_meta = {}
    for row in primary_rows:
        if row["method"] != "decision_value":
            continue
        other = by_case_method[(row["case_id"], baseline)]
        diff = int(row["exact_decision_correct"]) - int(other["exact_decision_correct"])
        per_profile[row["profile_id"]].append(diff)
        profile_meta[row["profile_id"]] = (row["user_cohort"], row["category"])
    cluster_means = {profile: sum(values) / len(values) for profile, values in per_profile.items()}
    strata = collections.defaultdict(list)
    for profile, meta in profile_meta.items():
        strata[meta].append(profile)
    rng = random.Random(seed)
    samples = []
    for _ in range(reps):
        weighted_sum = 0.0
        total_weight = 0
        for key in sorted(strata):
            ids = strata[key]
            for _ in ids:
                selected = rng.choice(ids)
                weight = len(per_profile[selected])
                weighted_sum += cluster_means[selected] * weight
                total_weight += weight
        samples.append(weighted_sum / total_weight)
    return cluster_means, {"repetitions": reps, "seed": seed,
                           "lower_95": percentile(samples, 0.025),
                           "upper_95": percentile(samples, 0.975),
                           "scope": "synthetic-profile-generator conditional; menus are a finite development-catalogue census"}


def analyze(policy, rows, trace_path):
    b = CONFIG["primary_budget"]
    primary = [row for row in rows if row["method"] != "ask_all" and row["budget"] == b]
    by_case_method = {(r["case_id"], r["method"]): r for r in primary}
    case_ids = sorted({r["case_id"] for r in primary})
    profile_ids = sorted({r["profile_id"] for r in primary})
    cohorts = sorted({r["user_cohort"] for r in primary})
    categories = sorted({r["category"] for r in primary})
    base = CONFIG["primary_baseline"]
    diffs = {}
    for category in categories:
        records = [r for r in primary if r["method"] == "decision_value" and r["category"] == category]
        d = [int(r["exact_decision_correct"]) - int(by_case_method[(r["case_id"], base)]["exact_decision_correct"]) for r in records]
        diffs[category] = {"difference_correct": sum(d), "denominator": len(d), "mean_difference": sum(d) / len(d)}
    cohort_diffs = {}
    for cohort in cohorts:
        records = [r for r in primary if r["method"] == "decision_value" and r["user_cohort"] == cohort]
        d = [int(r["exact_decision_correct"]) - int(by_case_method[(r["case_id"], base)]["exact_decision_correct"]) for r in records]
        cohort_diffs[cohort] = {"difference_correct": sum(d), "denominator": len(d), "mean_difference": sum(d) / len(d)}

    cluster_means, bootstrap = stratified_profile_bootstrap(
        primary, base, CONFIG["bootstrap_repetitions"], CONFIG["bootstrap_seed"])
    profile_positive = sum(value > 0 for value in cluster_means.values())
    pooled_diff = sum(int(by_case_method[(case_id, "decision_value")]["exact_decision_correct"])
                      - int(by_case_method[(case_id, base)]["exact_decision_correct"]) for case_id in case_ids) / len(case_ids)
    positive_categories = sum(x["mean_difference"] > 0 for x in diffs.values())
    gate = (pooled_diff > 0 and bootstrap["lower_95"] > 0
            and all(value["mean_difference"] > 0 for value in cohort_diffs.values())
            and positive_categories >= CONFIG["robustness_gate"]["minimum_positive_categories_out_of_6"]
            and profile_positive >= CONFIG["robustness_gate"]["minimum_positive_profile_clusters_out_of_48"])

    curve_summary = {}
    for method in CONFIG["methods"]:
        curve_summary[method] = {}
        for budget in CONFIG["budgets"]:
            rr = [r for r in rows if r["method"] == method and r["budget"] == budget]
            den = len(rr)
            curve_summary[method][str(budget)] = {
                "correct": sum(r["exact_decision_correct"] for r in rr), "denominator": den,
                "accuracy": sum(r["exact_decision_correct"] for r in rr) / den,
                "buy_correct": sum(r["purchase_recall_case"] for r in rr),
                "no_buy_correct": sum(r["no_buy_correct_case"] for r in rr),
                "false_purchases": sum(r["false_purchase_case"] for r in rr),
                "hard_constraint_violations": sum(r["hard_constraint_violation"] for r in rr),
                "mean_normalized_score_regret": sum(r["normalized_score_regret"] for r in rr) / den,
            }
    panel_metrics = {}
    for cohort in cohorts:
        cohort_rows = [r for r in primary if r["user_cohort"] == cohort]
        panel_metrics[cohort] = {}
        for method in CONFIG["methods"]:
            rr = [r for r in cohort_rows if r["method"] == method]
            panel_metrics[cohort][method] = {"correct": sum(r["exact_decision_correct"] for r in rr),
                                             "denominator": len(rr), "accuracy": sum(r["exact_decision_correct"] for r in rr) / len(rr)}
    by_cat_methods = {}
    for category in categories:
        cat_rows = [r for r in primary if r["category"] == category]
        by_cat_methods[category] = {method: {
            "correct": sum(r["exact_decision_correct"] for r in cat_rows if r["method"] == method),
            "denominator": sum(r["method"] == method for r in cat_rows),
            "accuracy": sum(r["exact_decision_correct"] for r in cat_rows if r["method"] == method)
                        / sum(r["method"] == method for r in cat_rows),
        } for method in CONFIG["methods"]}
    ask_all = [r for r in rows if r["method"] == "ask_all"]
    ref_counts = collections.Counter(r["reference_decision"] for r in primary if r["method"] == "decision_value")
    metrics = {
        "status": "CATALOGUE_ROBUST_ADVANTAGE_ESTABLISHED" if gate else "CATALOGUE_ROBUST_ADVANTAGE_NOT_ESTABLISHED",
        "interpretation": "Frozen finite development-catalogue census and deterministic synthetic users; intervals only conditional on the synthetic profile generator.",
        "primary_method": "decision_value", "primary_baseline": base, "primary_budget": b,
        "profile_menu_cases": len(case_ids), "unique_user_profiles": len(profile_ids),
        "unique_menus": len({r["menu_id"] for r in rows}), "development_products": 338,
        "validation_or_test_products_used": 0,
        "reference_decision_counts": dict(ref_counts),
        "overall_curves": curve_summary,
        "cohort_budget5": panel_metrics,
        "category_budget5": by_cat_methods,
        "primary_paired_difference": {
            "correct_difference": sum(int(by_case_method[(cid, "decision_value")]["exact_decision_correct"])
                                       - int(by_case_method[(cid, base)]["exact_decision_correct"]) for cid in case_ids),
            "denominator": len(case_ids), "mean_difference": pooled_diff,
            "cohort_differences": cohort_diffs,
            "category_differences": diffs,
            "positive_categories": positive_categories,
            "profile_cluster_count": len(cluster_means),
            "positive_profile_clusters": profile_positive,
            "profile_cluster_mean_differences": cluster_means,
            "stratified_profile_bootstrap": bootstrap,
        },
        "ask_all": {"correct": sum(r["exact_decision_correct"] for r in ask_all),
                    "denominator": len(ask_all),
                    "turns": sorted({r["dialogue_turns"] for r in ask_all}),
                    "information_units": sorted({r["elicitation_units"] for r in ask_all})},
        "gate": {**CONFIG["robustness_gate"], "passed": gate},
        "trace_rows": len(rows), "trace_sha256": policy.sha256(trace_path),
        "model_calls": 0, "training_runs": 0,
    }
    dump(HERE / "results/CATALOGUE_METRICS.json", metrics)
    return metrics


# Set by main after loading protected evaluator-only references.
references_lookup = {}


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--full", action="store_true")
    args = parser.parse_args()
    policy, env = load_engine()
    if args.prepare:
        print(json.dumps(construct_prepared(env), ensure_ascii=False, indent=2))
        return
    if args.smoke:
        menus, profiles, priors, cases, refs = load_prepared(env)
        global references_lookup
        references_lookup = refs
        smoke_ids = set(CONFIG["smoke_case_ids"])
        if not smoke_ids <= {case["case_id"] for case in cases}:
            raise RuntimeError("Smoke cases missing")
        output, rows = run_case_panel(policy, env, menus, profiles, priors, cases, smoke_ids, smoke=True)
        if (len(rows) != 58
                or sum(r["method"] != "ask_all" and r["budget"] == 6 and r["exact_decision_correct"] for r in rows) != 8
                or sum(r["method"] == "ask_all" and r["exact_decision_correct"] for r in rows) != 2):
            raise RuntimeError("Smoke terminal or denominator failure")
        receipt = {"status": "PASS", "cases": len(smoke_ids), "trace_rows": len(rows),
                   "prior_profiles_per_pool": CONFIG["prior_profiles_per_pool"],
                   "six_question_exact_terminals": 8, "ask_all_exact": sum(r["method"] == "ask_all" and r["exact_decision_correct"] for r in rows),
                   "trace_sha256": sha256(output), "model_calls": 0}
        dump(HERE / "artifacts/SMOKE_METRICS.json", receipt)
        print(json.dumps(receipt, indent=2))
        return
    verify_frozen()
    started = HERE / "results/RUN_STARTED.json"
    if started.exists():
        raise FileExistsError("Full run already started; preserve evidence and do not rerun")
    dump(started, {"status": "FULL_PANEL_STARTED_ONCE", "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "planned_cases": 280, "planned_trace_rows": 8120})
    menus, profiles, priors, cases, refs = load_prepared(env)
    references_lookup = refs
    output, rows = run_case_panel(policy, env, menus, profiles, priors, cases)
    if len(rows) != 8120:
        raise RuntimeError("Full trace denominator mismatch")
    for method in CONFIG["methods"]:
        terminal = [r for r in rows if r["method"] == method and r["budget"] == 6]
        if len(terminal) != 280 or not all(r["exact_decision_correct"] for r in terminal):
            raise RuntimeError(f"Six-question exact-terminal check failed: {method}")
    ask_all = [r for r in rows if r["method"] == "ask_all"]
    if len(ask_all) != 280 or not all(r["exact_decision_correct"] for r in ask_all):
        raise RuntimeError("Full-profile disclosure check failed")
    print(json.dumps(analyze(policy, rows, output), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
