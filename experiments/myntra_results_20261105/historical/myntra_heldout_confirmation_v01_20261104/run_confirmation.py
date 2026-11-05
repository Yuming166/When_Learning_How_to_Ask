#!/usr/bin/env python3
"""One-shot validation/test panel using frozen development policies."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import math
import multiprocessing
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
SOURCE = Path(CONFIG["source_worktree"])
SOURCE_EXP = SOURCE / CONFIG["source_experiment"]
SOURCE_CATALOGUE = SOURCE_EXP / "artifacts/input/catalogue_strict.jsonl"
DEV_EXP = HERE.parent / CONFIG["development_experiment"]
PRIMARY_EXP = HERE.parent / CONFIG["primary_experiment"]
PREPARED = HERE / "artifacts/prepared"
FIELDS = ["neckline", "sleeve_length", "fabric", "wash_care", "pattern"]
FROZEN = HERE / "FROZEN.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def dump(path: Path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def dump_rows(path: Path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def load_dev_runner():
    path = DEV_EXP / "run_full_dev.py"
    spec = importlib.util.spec_from_file_location("myntra_heldout_frozen_dev_run", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen dev runner: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DEV = load_dev_runner()


def evaluate_python_oov(items, profile):
    """Frozen evaluator: values outside dev support have neutral score zero."""
    feasible, scores = [], {}
    for item in items:
        attrs = item["attributes"]
        if attrs["wash_care"] not in profile["hard"]["allowed_care_labels"]:
            continue
        if attrs["fabric"] in profile["hard"]["excluded_fabric_labels"]:
            continue
        pid = item["product_id"]
        feasible.append(pid)
        scores[pid] = sum(profile["soft"]["scores"][field].get(attrs[field], 0) for field in FIELDS)
    maximum = max(scores.values()) if scores else None
    favorites = sorted(pid for pid in feasible if scores[pid] == maximum)
    buy = maximum is not None and maximum > profile["purchase_threshold"]
    return {"feasible_ids": sorted(feasible), "scores_by_product": scores,
            "relative_favorite_ids": favorites, "maximum_score": maximum,
            "decision": "BUY" if buy else "NO_BUY",
            "valid_purchase_ids": favorites if buy else [],
            "no_buy_reason": None if buy else "NO_FEASIBLE_ITEM" if not feasible else "BELOW_OR_EQUAL_THRESHOLD"}


def evaluate_sql_oov(items, profile):
    """Independent relational evaluator with LEFT JOIN/COALESCE for OOV values."""
    import sqlite3

    with sqlite3.connect(":memory:") as db:
        db.executescript("""
            CREATE TABLE feature(item TEXT, field TEXT, value TEXT);
            CREATE TABLE rating(field TEXT, value TEXT, score INTEGER);
            CREATE TABLE allowed_care(value TEXT);
            CREATE TABLE excluded_fabric(value TEXT);
        """)
        db.executemany("INSERT INTO feature VALUES (?,?,?)",
                       [(i["product_id"], field, i["attributes"][field]) for i in items for field in FIELDS])
        db.executemany("INSERT INTO rating VALUES (?,?,?)",
                       [(field, value, score) for field, values in profile["soft"]["scores"].items()
                        for value, score in values.items()])
        db.executemany("INSERT INTO allowed_care VALUES (?)",
                       [(x,) for x in profile["hard"]["allowed_care_labels"]])
        db.executemany("INSERT INTO excluded_fabric VALUES (?)",
                       [(x,) for x in profile["hard"]["excluded_fabric_labels"]])
        result = db.execute("""
            SELECT f.item, SUM(COALESCE(r.score, 0))
            FROM feature f LEFT JOIN rating r ON f.field=r.field AND f.value=r.value
            WHERE f.item IN (
                SELECT c.item FROM feature c JOIN allowed_care a ON c.value=a.value
                WHERE c.field='wash_care'
            ) AND f.item NOT IN (
                SELECT t.item FROM feature t JOIN excluded_fabric x ON t.value=x.value
                WHERE t.field='fabric'
            ) GROUP BY f.item ORDER BY f.item
        """).fetchall()
    scores = dict(result)
    if scores:
        maximum = max(scores.values())
        favorites = sorted(pid for pid, score in scores.items() if score == maximum)
        buy = maximum > profile["purchase_threshold"]
    else:
        maximum, favorites, buy = None, [], False
    return {"feasible_ids": sorted(scores), "scores_by_product": scores,
            "relative_favorite_ids": favorites, "maximum_score": maximum,
            "decision": "BUY" if buy else "NO_BUY",
            "valid_purchase_ids": favorites if buy else [],
            "no_buy_reason": None if buy else "NO_FEASIBLE_ITEM" if not scores else "BELOW_OR_EQUAL_THRESHOLD"}


def keyed_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def audit_source(env):
    if sha256(SOURCE_CATALOGUE) != CONFIG["source_catalogue_sha256"]:
        raise RuntimeError("Catalogue snapshot hash mismatch")
    source = env.rows(SOURCE_CATALOGUE)
    if len(source) != 471 or len({x["product_id"] for x in source}) != 471:
        raise RuntimeError("Frozen catalogue row/product denominator changed")
    allowed_splits = {"development", *CONFIG["splits"]}
    if {x["split"] for x in source} != allowed_splits:
        raise RuntimeError("Unexpected split labels")
    split_counts = collections.Counter(x["split"] for x in source)
    expected_counts = {"development": 338, "validation_reserved": 78, "test_reserved": 55}
    if dict(split_counts) != expected_counts:
        raise RuntimeError(f"Split counts changed: {dict(split_counts)}")
    group_splits = collections.defaultdict(set)
    for item in source:
        group_splits[item["leakage_group_id"]].add(item["split"])
        for field in FIELDS:
            entry = item.get("attributes", {}).get(field, {})
            if entry.get("status") != "reported" or not isinstance(entry.get("value"), str) or not entry["value"]:
                raise RuntimeError(f"Incomplete core attribute: {item['product_id']}:{field}")
    crossing = [group for group, splits in group_splits.items() if len(splits) > 1]
    if crossing:
        raise RuntimeError(f"Leakage groups cross splits: {len(crossing)}")
    selected = {tuple(pool) for pool in CONFIG["pools"]}
    for split in CONFIG["splits"]:
        found = {(x["gender"], x["category"]) for x in source if x["split"] == split}
        if not found <= selected:
            raise RuntimeError(f"Unexpected pool in {split}: {found - selected}")
    development = [x for x in source if x["split"] == "development"]
    dev_vocab = {str(i): {field: sorted({x["attributes"][field]["value"] for x in development
                                         if (x["gender"], x["category"]) == (gender, category)})
                          for field in FIELDS}
                 for i, (gender, category) in enumerate(CONFIG["pools"])}
    oov = {}
    split_pool_counts = {}
    for split in CONFIG["splits"]:
        subset = [x for x in source if x["split"] == split]
        split_pool_counts[split] = {f"{g}/{c}": sum((x["gender"], x["category"]) == (g, c) for x in subset)
                                    for g, c in CONFIG["pools"]}
        split_oov = {}
        for i, (gender, category) in enumerate(CONFIG["pools"]):
            pool_rows = [x for x in subset if (x["gender"], x["category"]) == (gender, category)]
            values = {field: sorted({x["attributes"][field]["value"] for x in pool_rows}) for field in FIELDS}
            split_oov[f"{gender}/{category}"] = {
                field: sorted(set(values[field]) - set(dev_vocab[str(i)][field])) for field in FIELDS
            }
        oov[split] = split_oov
    return source, dev_vocab, {
        "status": "PASS", "records": len(source), "split_counts": dict(split_counts),
        "leakage_groups": len(group_splits), "cross_split_leakage_groups": 0,
        "split_pool_counts": split_pool_counts, "unseen_values_by_split_pool_field": oov,
        "unseen_policy": CONFIG["unseen_attribute_policy"],
        "catalogue_sha256": sha256(SOURCE_CATALOGUE), "method_outcomes_computed": False,
    }


def build_menus(source, split):
    subset = [x for x in source if x["split"] == split]
    menus, vocabularies, provenance = [], {}, {}
    by_pool = collections.defaultdict(list)
    for row in subset:
        by_pool[(row["gender"], row["category"])].append(row)
    for pool_index, (gender, category) in enumerate(CONFIG["pools"]):
        candidates = by_pool[(gender, category)]
        if not candidates:
            continue
        vocab = {field: sorted({row["attributes"][field]["value"] for row in candidates}) for field in FIELDS}
        vocabularies[str(pool_index)] = vocab
        groups = collections.defaultdict(list)
        for row in candidates:
            groups[row["leakage_group_id"]].append(row)
        n_menus = math.ceil(len(candidates) / CONFIG["menu_target_size"])
        bins = [[] for _ in range(n_menus)]
        root = CONFIG["menu_seed_roots"][split]
        ordered = sorted(groups.items(), key=lambda pair: (-len(pair[1]), keyed_hash(
            f"{root}|{gender}|{category}|group|{pair[0]}")))
        ties = [keyed_hash(f"{root}|{gender}|{category}|menu|{i}") for i in range(n_menus)]
        for group_id, group_rows in ordered:
            destination = min(range(n_menus), key=lambda i: (len(bins[i]), ties[i]))
            bins[destination].extend(sorted(group_rows, key=lambda row: row["product_id"]))
        for menu_index, selected in enumerate(bins):
            menu_id = f"{split[:3]}-M{pool_index}_{menu_index:02d}"
            items = [{"product_id": row["product_id"],
                      "attributes": {field: row["attributes"][field]["value"] for field in FIELDS}}
                     for row in selected]
            menus.append({"menu_id": menu_id, "pool_index": pool_index, "gender": gender,
                          "category": category, "split": split, "items": items})
            provenance[menu_id] = {"source_product_ids": [x["product_id"] for x in selected],
                                   "leakage_group_ids": sorted({x["leakage_group_id"] for x in selected}),
                                   "item_count": len(selected)}
    item_ids = [item["product_id"] for menu in menus for item in menu["items"]]
    expected = {x["product_id"] for x in subset}
    if len(item_ids) != len(set(item_ids)) or set(item_ids) != expected:
        raise RuntimeError(f"{split} menu coverage is not exact")
    return menus, vocabularies, provenance


def generate_users(env, dev_vocab, split, represented_pools):
    source_cfg = env.read(env.BASE / "config.json")
    profiles = []
    for cohort, seed in CONFIG["user_cohort_seed_roots"][split].items():
        cfg = dict(source_cfg)
        cfg["seed_root"] = seed
        cfg["profiles_per_pool"] = CONFIG["profiles_per_pool_per_cohort"]
        for pool_index, (gender, category) in enumerate(CONFIG["pools"]):
            # Do not create profiles with no held-out menu in this split.
            if pool_index not in represented_pools:
                continue
            for profile in env.generate_profiles(dev_vocab[str(pool_index)], pool_index, cfg):
                profile = dict(profile)
                profile["profile_id"] = f"{split[:3]}-{cohort}-{profile['profile_id']}"
                profile["user_cohort"] = cohort
                profile["evaluation_split"] = split
                profile["development_only"] = False
                profiles.append(profile)
    return profiles


def prepare_split(env, split, source, dev_vocab):
    menus, menu_vocab, provenance = build_menus(source, split)
    menu_pools = {m["pool_index"] for m in menus}
    profiles = generate_users(env, dev_vocab, split, menu_pools)
    if {p["pool_index"] for p in profiles} != menu_pools:
        raise RuntimeError(f"Profile/menu pool mismatch: {split}")
    prior_file = DEV_EXP / "artifacts/prepared/private/prior_profiles.jsonl"
    prior_profiles = rows(prior_file)
    priors = collections.defaultdict(list)
    for profile in prior_profiles:
        priors[profile["pool_index"]].append(profile)
    if not menu_pools <= set(priors) or any(len(priors[p]) != CONFIG["prior_profiles_per_pool"] for p in menu_pools):
        raise RuntimeError("Development prior bank mismatch")
    menus_by_pool = collections.defaultdict(list)
    for menu in menus:
        menus_by_pool[menu["pool_index"]].append(menu)
    cases, references = [], []
    for profile in profiles:
        for menu in menus_by_pool[profile["pool_index"]]:
            case_id = f"{profile['profile_id']}__{menu['menu_id']}"
            py = evaluate_python_oov(menu["items"], profile)
            sql = evaluate_sql_oov(menu["items"], profile)
            if py != sql:
                raise RuntimeError(f"Independent OOV evaluators disagree: {case_id}")
            cases.append({"case_id": case_id, "profile_id": profile["profile_id"],
                          "user_cohort": profile["user_cohort"], "menu_id": menu["menu_id"],
                          "pool_index": profile["pool_index"], "split": split})
            references.append({"case_id": case_id, "profile_id": profile["profile_id"],
                               "menu_id": menu["menu_id"], "reference": py})
    base = PREPARED / split
    dump_rows(base / "public/menus.jsonl", menus)
    dump_rows(base / "public/cases.jsonl", cases)
    dump(base / "public/vocabularies.json", menu_vocab)
    dump_rows(base / "private/user_profiles.jsonl", profiles)
    dump(base / "private/menu_provenance.json", provenance)
    dump_rows(base / "evaluator_only/references.jsonl", references)
    return {"split": split, "products": sum(len(m["items"]) for m in menus), "menus": len(menus),
            "profiles": len(profiles), "cases": len(cases), "profile_menu_case_denominator": len(cases),
            "menu_size_distribution": dict(collections.Counter(len(m["items"]) for m in menus)),
            "represented_pools": sorted(menu_pools), "reference_evaluators_agree": True,
            "unseen_value_policy": "development-support neutral zero", "model_calls": 0}


def prepare():
    if PREPARED.exists():
        raise FileExistsError("Prepared data already exists; preserve it")
    policy, env = DEV.load_engine()
    env.evaluate_python = evaluate_python_oov
    env.evaluate_sql = evaluate_sql_oov
    source, dev_vocab, audit = audit_source(env)
    source_cfg = env.read(env.BASE / "config.json")
    if source_cfg["seed_root"] != "myntra-preference-dev-v01-20261104":
        raise RuntimeError("Unexpected development profile generator seed")
    summaries = {split: prepare_split(env, split, source, dev_vocab) for split in CONFIG["splits"]}
    prior_digest = sha256(DEV_EXP / "artifacts/prepared/private/prior_profiles.jsonl")
    dump(HERE / "DATA_AUDIT.json", audit)
    dump(HERE / "results/PREPARED.json", {"status": "PREPARED_NO_METHOD_OUTCOMES",
         "splits": summaries, "source_catalogue_sha256": sha256(SOURCE_CATALOGUE),
         "development_prior_profiles_sha256": prior_digest, "model_calls": 0})
    return {"audit": audit, "prepared": summaries}


def files_to_freeze():
    paths = [HERE / "config.json", HERE / "PROTOCOL.md", HERE / "README_ZH.md", HERE / "DATA_AUDIT.json",
             HERE / "run_confirmation.py", HERE / "test_confirmation.py", HERE / "analyze_confirmation.py",
             HERE / "results/PREPARED.json", SOURCE_CATALOGUE,
             SOURCE_EXP / "environment.py", SOURCE_EXP / "config.json", SOURCE_EXP / "RULES_FREEZE.json",
             DEV_EXP / "config.json", DEV_EXP / "FROZEN.json",
             DEV_EXP / "run_full_dev.py", DEV_EXP / "artifacts/prepared/private/prior_profiles.jsonl",
             PRIMARY_EXP / "engine.py", PRIMARY_EXP / "config.json"]
    for split in CONFIG["splits"]:
        base = PREPARED / split
        paths.extend([base / "public/menus.jsonl", base / "public/cases.jsonl", base / "public/vocabularies.json",
                      base / "private/user_profiles.jsonl", base / "private/menu_provenance.json",
                      base / "evaluator_only/references.jsonl"])
    return paths


def freeze():
    if FROZEN.exists():
        raise FileExistsError("Freeze already exists; preserve it")
    for split in CONFIG["splits"]:
        if (HERE / f"results/{split}_RUN_STARTED.json").exists():
            raise RuntimeError("A held-out run has already started")
    missing = [str(p) for p in files_to_freeze() if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Cannot freeze missing artifacts: {missing}")
    entries = {str(p.relative_to(HERE)) if p.is_relative_to(HERE) else str(p): sha256(p)
               for p in files_to_freeze()}
    record = {"status": "FROZEN_BEFORE_HELDOUT_OUTCOMES", "version": CONFIG["version"],
              "files_sha256": entries, "split_runs_started": [],
              "methods": CONFIG["methods"], "budgets": CONFIG["budgets"],
              "simultaneous_family": CONFIG["simultaneous_family"], "model_calls": 0,
              "training_runs": 0, "claim_limit": "synthetic deterministic user simulator; fixed finite reserved catalogue items"}
    dump(FROZEN, record)
    return record


def verify_frozen():
    if not FROZEN.is_file():
        raise RuntimeError("FROZEN.json missing")
    record = json.loads(FROZEN.read_text())
    if record.get("status") != "FROZEN_BEFORE_HELDOUT_OUTCOMES":
        raise RuntimeError("Unexpected freeze status")
    for path, expected in record["files_sha256"].items():
        p = Path(path) if Path(path).is_absolute() else HERE / path
        if not p.is_file() or sha256(p) != expected:
            raise RuntimeError(f"Frozen input changed: {path}")
    return record


def load_prepared(split):
    base = PREPARED / split
    menus = {x["menu_id"]: x for x in rows(base / "public/menus.jsonl")}
    profiles = {x["profile_id"]: x for x in rows(base / "private/user_profiles.jsonl")}
    cases = rows(base / "public/cases.jsonl")
    refs = {x["case_id"]: x["reference"] for x in rows(base / "evaluator_only/references.jsonl")}
    prior_rows = rows(DEV_EXP / "artifacts/prepared/private/prior_profiles.jsonl")
    priors = collections.defaultdict(list)
    for profile in prior_rows:
        priors[profile["pool_index"]].append(profile)
    if len(cases) != len(refs) or len(cases) != len({x["case_id"] for x in cases}):
        raise RuntimeError(f"Prepared case/reference denominator drift in {split}")
    return menus, profiles, priors, cases, refs


_WORKER_CONTEXT = None


def initialize_worker():
    global _WORKER_CONTEXT
    policy, env = DEV.load_engine()
    env.evaluate_python = evaluate_python_oov
    env.evaluate_sql = evaluate_sql_oov
    menus, profiles, priors, cases = load_prepared_for_worker()
    _WORKER_CONTEXT = (policy, env, menus, profiles, priors, cases)


def load_prepared_for_worker():
    # Each split is assigned by an environment variable before the pool is created.
    split = os.environ["MYNTRA_HELDOUT_SPLIT"]
    base = PREPARED / split
    menus = {x["menu_id"]: x for x in rows(base / "public/menus.jsonl")}
    profiles = {x["profile_id"]: x for x in rows(base / "private/user_profiles.jsonl")}
    cases = rows(base / "public/cases.jsonl")
    prior_rows = rows(DEV_EXP / "artifacts/prepared/private/prior_profiles.jsonl")
    priors = collections.defaultdict(list)
    for profile in prior_rows:
        priors[profile["pool_index"]].append(profile)
    return menus, profiles, priors, cases


def execute_case(case):
    if _WORKER_CONTEXT is None:
        raise RuntimeError("Worker context was not initialized")
    policy, env, menus, profiles, priors, _ = _WORKER_CONTEXT
    profile = profiles[case["profile_id"]]
    menu = menus[case["menu_id"]]
    prior = priors[case["pool_index"]]
    public_case = {"case_id": case["case_id"], "menu_id": menu["menu_id"], "public_menu": menu}
    output = []
    for method in CONFIG["methods"]:
        output.extend(policy.run_case(env, public_case, profile, prior, method, max(CONFIG["budgets"])))
    output.append(policy.run_ask_all(env, public_case, profile))
    for record in output:
        record.update({"split": case["split"], "user_cohort": case["user_cohort"],
                       "pool_index": case["pool_index"], "gender": menu["gender"],
                       "category": menu["category"], "menu_size": len(menu["items"])})
    return output


def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] if lo == hi else ordered[lo] * (hi - position) + ordered[hi] * (position - lo)


def run_split(split):
    verify_frozen()
    if split not in CONFIG["splits"]:
        raise ValueError(f"Not a reserved split: {split}")
    started = HERE / f"results/{split}_RUN_STARTED.json"
    completed = HERE / f"results/{split}_RUN_COMPLETED.json"
    trace = HERE / f"results/{split}_PAIRED_CASES.jsonl"
    if started.exists() or completed.exists() or trace.exists():
        raise FileExistsError(f"Preserve existing {split} run evidence")
    menus, profiles, priors, cases, refs = load_prepared(split)
    run_started = dt.datetime.now(dt.timezone.utc).isoformat()
    clock_start = time.monotonic()
    dump(started, {"status": "HELDOUT_PANEL_STARTED_ONCE", "split": split,
                   "started_utc": run_started, "cases": len(cases),
                   "planned_trace_rows": len(cases) * (len(CONFIG["methods"]) * 7 + 1),
                   "workers": CONFIG["workers"], "model_calls": 0})
    rows_written = 0
    os.environ["MYNTRA_HELDOUT_SPLIT"] = split
    ctx = multiprocessing.get_context(CONFIG["start_method"])
    with trace.open("x", encoding="utf-8") as out:
        with ProcessPoolExecutor(max_workers=CONFIG["workers"], mp_context=ctx,
                                 initializer=initialize_worker) as executor:
            for ordinal, case_rows in enumerate(executor.map(execute_case, cases, chunksize=1), start=1):
                if len(case_rows) != len(CONFIG["methods"]) * 7 + 1:
                    raise RuntimeError("Per-case method/budget denominator drift")
                out.write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in case_rows))
                out.flush()
                os.fsync(out.fileno())
                rows_written += len(case_rows)
                if ordinal % 20 == 0 or ordinal == len(cases):
                    print(f"{split}: completed {ordinal}/{len(cases)} cases", flush=True)
    trace_rows = rows(trace)
    if rows_written != len(cases) * 29 or len(trace_rows) != rows_written:
        raise RuntimeError("Trace denominator mismatch")
    if len({(r["case_id"], r["method"], r["budget"]) for r in trace_rows if r["method"] != "ask_all"}) != len(cases) * 28:
        raise RuntimeError("Duplicate/missing case-method-budget records")
    for row in trace_rows:
        ref = refs[row["case_id"]]
        expected = ["NO_BUY"] if ref["decision"] == "NO_BUY" else ref["valid_purchase_ids"]
        if row["reference_target_set"] != expected:
            raise RuntimeError(f"Evaluator replay mismatch: {row['case_id']} / {row['method']} / {row['budget']}")
    for method in CONFIG["methods"]:
        terminal = [r for r in trace_rows if r["method"] == method and r["budget"] == 6]
        if len(terminal) != len(cases) or not all(r["exact_decision_correct"] for r in terminal):
            raise RuntimeError(f"Full exact disclosure failed at terminal budget: {method}")
    ask_all = [r for r in trace_rows if r["method"] == "ask_all"]
    if len(ask_all) != len(cases) or not all(r["exact_decision_correct"] for r in ask_all):
        raise RuntimeError("Whole-profile terminal replay failed")
    dump(completed, {"status": "HELDOUT_PANEL_COMPLETED", "split": split,
                     "started_utc": run_started, "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                     "elapsed_seconds": time.monotonic() - clock_start, "cases": len(cases),
                     "trace_rows": rows_written, "trace_sha256": sha256(trace),
                     "model_calls": 0, "training_runs": 0})
    return json.loads(completed.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "freeze", "run"])
    parser.add_argument("--split", choices=CONFIG["splits"])
    args = parser.parse_args()
    if args.mode == "prepare":
        print(json.dumps(prepare(), ensure_ascii=False, indent=2))
    elif args.mode == "freeze":
        print(json.dumps(freeze(), ensure_ascii=False, indent=2))
    else:
        if args.split is None:
            parser.error("--split is required for run")
        print(json.dumps(run_split(args.split), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
