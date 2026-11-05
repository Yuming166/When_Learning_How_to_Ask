"""One-shot, zero-model-call component ablation on immutable Myntra cases."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
CFG = json.loads((HERE / "config.json").read_text())
INPUT = HERE / "artifacts/input"
RESULTS = HERE / "results"
DEV = EXPERIMENTS / CFG["development_experiment"]
HELD = EXPERIMENTS / CFG["heldout_experiment"]
PRIMARY = EXPERIMENTS / CFG["policy_experiment"]
SOURCE = Path(CFG["source_worktree"]) / CFG["source_experiment"]
METRICS = ("reference_decision", "reference_target_set", "selected_action",
           "exact_decision_correct", "purchase_recall_case", "no_buy_correct_case",
           "false_purchase_case", "hard_constraint_violation", "score_regret",
           "normalized_score_regret")


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")


def dump_rows(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_policy_environment():
    engine = load_module("mechanism_frozen_engine", PRIMARY / "engine.py")
    env_dev = engine.load_environment(Path(CFG["source_worktree"]))
    env_held = engine.load_environment(Path(CFG["source_worktree"]))
    held = load_module("mechanism_frozen_heldout", HELD / "run_confirmation.py")
    env_held.evaluate_python = held.evaluate_python_oov
    env_held.evaluate_sql = held.evaluate_sql_oov
    if engine.CONFIG["query_actions"] != CFG["query_actions"]:
        raise RuntimeError("Question action/order drift")
    return engine, {s: env_dev if s == "development" else env_held for s in CFG["splits"]}


def upstream_files():
    bound = {}
    for label, entry in read(DEV / "FROZEN.json")["files"].items():
        path = Path(entry["path"])
        if not path.is_file() or sha(path) != entry["sha256"]:
            raise RuntimeError(f"Development freeze mismatch: {label}")
        bound[str(path)] = entry["sha256"]
    for label, digest in read(HELD / "FROZEN.json")["files_sha256"].items():
        path = Path(label) if Path(label).is_absolute() else HELD / label
        if not path.is_file() or sha(path) != digest:
            raise RuntimeError(f"Held-out freeze mismatch: {label}")
        bound[str(path.resolve())] = digest
    for directory in (DEV, HELD):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                bound[str(path.resolve())] = sha(path)
    for path in (PRIMARY / "engine.py", PRIMARY / "config.json", SOURCE / "environment.py",
                 SOURCE / "config.json", SOURCE / "RULES_FREEZE.json",
                 SOURCE / "artifacts/input/catalogue_strict.jsonl"):
        bound[str(path)] = sha(path)
    if sha(SOURCE / "artifacts/input/catalogue_strict.jsonl") != CFG["source_catalogue_sha256"]:
        raise RuntimeError("Catalogue hash drift")
    return bound


def source_layout(split):
    base = DEV / "artifacts/prepared" if split == "development" else HELD / "artifacts/prepared" / split
    trace = DEV / "results/PAIRED_CASES.jsonl" if split == "development" else HELD / f"results/{split}_PAIRED_CASES.jsonl"
    return base, trace


def prepare():
    if INPUT.exists():
        raise FileExistsError("Preserve the existing input snapshot")
    preserved = upstream_files()
    for split in CFG["splits"]:
        base, trace = source_layout(split)
        for rel in ("public/menus.jsonl", "public/cases.jsonl", "private/user_profiles.jsonl",
                    "evaluator_only/references.jsonl"):
            dest = INPUT / split / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base / rel, dest)
        shutil.copyfile(trace, INPUT / split / "historical_traces.jsonl")
    shutil.copyfile(DEV / "artifacts/prepared/private/prior_profiles.jsonl", INPUT / "prior_profiles.jsonl")
    dump(HERE / "UPSTREAM_PRESERVATION.json", {"files_sha256": preserved,
         "status": "ORIGINAL_FILES_HASHED_BEFORE_NEW_COMPONENT_OUTCOMES"}, True)
    data = load_data()
    engine, environments = load_policy_environment()
    for case in data["cases"]:
        split, cid = case["split"], case["case_id"]
        menu = data["menus"][(split, case["menu_id"])]
        profile = data["profiles"][(split, case["profile_id"])]
        expected = data["references"][(split, cid)]
        py = environments[split].evaluate_python(menu["items"], profile)
        sql = environments[split].evaluate_sql(menu["items"], profile)
        if py != sql or py != expected:
            raise RuntimeError(f"Independent ground truth mismatch: {split}/{cid}")
    receipt = {"status": "INPUT_AND_REFERENCE_PREFLIGHT_PASS", "cases": len(data["cases"]),
               "profiles": len(data["profiles"]), "menus": len(data["menus"]),
               "prior_draws": sum(map(len, data["priors"].values())),
               "upstream_preserved_files": len(preserved), "reference_python_sql_agreement": 736,
               "new_component_outcomes_generated": False, "model_calls": 0, "training_runs": 0}
    dump(HERE / "PREPARED.json", receipt, True)
    return receipt


def load_data():
    data = {k: {} for k in ("menus", "profiles", "references", "historical")}
    data["cases"] = []
    data["priors"] = collections.defaultdict(list)
    for prior in rows(INPUT / "prior_profiles.jsonl"):
        data["priors"][prior["pool_index"]].append(prior)
    if set(data["priors"]) != set(range(6)) or any(len(p) != 2048 for p in data["priors"].values()):
        raise RuntimeError("Original prior bank coverage changed")
    all_products = set()
    for split in CFG["splits"]:
        base = INPUT / split
        menus = rows(base / "public/menus.jsonl")
        profiles = rows(base / "private/user_profiles.jsonl")
        cases = rows(base / "public/cases.jsonl")
        refs = rows(base / "evaluator_only/references.jsonl")
        if (len(cases), len(profiles), len(menus)) != (CFG["expected_cases"][split],
                CFG["expected_profiles"][split], CFG["expected_menus"][split]):
            raise RuntimeError(f"Input denominator drift: {split}")
        for key, values, id_key in (("menus", menus, "menu_id"), ("profiles", profiles, "profile_id")):
            for value in values:
                ident = (split, value[id_key])
                if ident in data[key]:
                    raise RuntimeError(f"Duplicate {key}: {ident}")
                data[key][ident] = value
        if len(refs) != len(cases) or len({c["case_id"] for c in cases}) != len(cases):
            raise RuntimeError("Case/reference coverage drift")
        for ref in refs:
            ident = (split, ref["case_id"])
            if ident in data["references"]:
                raise RuntimeError("Duplicate reference")
            data["references"][ident] = ref["reference"]
        products = [i["product_id"] for m in menus for i in m["items"]]
        if len(products) != CFG["expected_products"][split] or len(set(products)) != len(products) or set(products) & all_products:
            raise RuntimeError("Product coverage overlap or drift")
        all_products.update(products)
        for case in cases:
            case = {**case, "split": split}
            profile = data["profiles"][(split, case["profile_id"])]
            menu = data["menus"][(split, case["menu_id"])]
            if profile["pool_index"] != case["pool_index"] or menu["pool_index"] != case["pool_index"]:
                raise RuntimeError("Profile/menu prior pool mismatch")
            if profile["user_cohort"] != case["user_cohort"]:
                raise RuntimeError("Cohort mismatch")
            if (split, case["case_id"]) not in data["references"]:
                raise RuntimeError("Missing case reference")
            data["cases"].append(case)
        historical = [r for r in rows(base / "historical_traces.jsonl") if r["method"] in CFG["historical_methods"]]
        if len(historical) != len(cases) * 28:
            raise RuntimeError("Historical trace denominator drift")
        for row in historical:
            key = (split, row["case_id"], row["method"], row["budget"])
            if key in data["historical"] or row["budget"] not in CFG["budgets"]:
                raise RuntimeError("Duplicate/illegal historical row")
            data["historical"][key] = {**row, "split": split}
        for case in cases:
            for method in CFG["historical_methods"]:
                for budget in CFG["budgets"]:
                    row = data["historical"][(split, case["case_id"], method, budget)]
                    if len(row["query_sequence"]) != budget or len(set(row["query_sequence"])) != budget:
                        raise RuntimeError("Historical query prefix invalid")
    return data


def freeze():
    if (RESULTS / "RUN_STARTED.json").exists():
        raise RuntimeError("Cannot freeze after the component run starts")
    tests = read(HERE / "TEST_RECEIPT.json")
    if tests["status"] != "PASS":
        raise RuntimeError("Meaningful component tests must pass before freeze")
    paths = [HERE / name for name in ("config.json", "PROTOCOL.md", "README_ZH.md", "experiment.py",
             "ablation_statistics.py", "test_mechanism.py", "PREPARED.json", "TEST_RECEIPT.json",
             "UPSTREAM_PRESERVATION.json")]
    paths += sorted(p for p in INPUT.rglob("*") if p.is_file())
    record = {"status": "FROZEN_BEFORE_NEW_COMPONENT_OUTCOMES", "frozen_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "historical_results_previously_observed": True,
              "files_sha256": {str(p.relative_to(HERE)): sha(p) for p in paths},
              "model_calls": 0, "training_runs": 0}
    dump(HERE / "FROZEN.json", record, True)
    return {"status": record["status"], "frozen_files": len(paths)}


def verify_inputs():
    frozen = read(HERE / "FROZEN.json")
    for rel, digest in frozen["files_sha256"].items():
        if sha(HERE / rel) != digest:
            raise RuntimeError(f"Frozen ablation dependency changed: {rel}")
    preserved = read(HERE / "UPSTREAM_PRESERVATION.json")["files_sha256"]
    for path, digest in preserved.items():
        if sha(path) != digest:
            raise RuntimeError(f"Original file changed: {path}")
    return {"frozen_files": len(frozen["files_sha256"]), "preserved_upstream_files": len(preserved)}


def initial_order(engine, env, menu, priors):
    """No hidden user/profile or answer is accepted by this function."""
    policy = engine.PublicPolicy(env, menu, priors, "decision_value")
    scores = {a: policy.score_query(a) for a in CFG["query_actions"]}
    order = sorted(CFG["query_actions"], key=lambda a: (-scores[a], CFG["query_actions"].index(a)))
    if order[0] != policy.next_action():
        raise RuntimeError("Initial rank disagrees with original DV tie-breaking")
    prediction = policy.predict()
    return {"scores": scores, "order": order, "initial_prediction": list(prediction)}


WORKER = None


def initialize_worker(orders=None):
    global WORKER
    engine, envs = load_policy_environment()
    WORKER = {"engine": engine, "envs": envs, "data": load_data(), "orders": orders or {}, "predictions": {}}


def execute_order(key):
    split, menu_id = key
    menu = WORKER["data"]["menus"][key]
    rank = initial_order(WORKER["engine"], WORKER["envs"][split], menu,
                         WORKER["data"]["priors"][menu["pool_index"]])
    return key, rank


def cached_predict(policy, split, menu_id, memo, engine):
    key = (split, menu_id, engine.canonical(policy.known))
    if key not in memo:
        memo[key] = policy.predict()
    return memo[key]


def execute_case(case):
    ctx = WORKER
    engine, data = ctx["engine"], ctx["data"]
    split, cid = case["split"], case["case_id"]
    env = ctx["envs"][split]
    profile = data["profiles"][(split, case["profile_id"])]
    menu = data["menus"][(split, case["menu_id"])]
    priors = data["priors"][case["pool_index"]]
    menu_key = (split, menu["menu_id"])
    if menu_key not in ctx["orders"]:
        ctx["orders"][menu_key] = initial_order(engine, env, menu, priors)
    rank = ctx["orders"][menu_key]
    memo = ctx["predictions"]
    memo[(split, menu["menu_id"], engine.canonical({}))] = tuple(rank["initial_prediction"])
    reference = data["references"][(split, cid)]
    historical_rows = []
    for method in CFG["historical_methods"]:
        for b in CFG["budgets"]:
            old = data["historical"][(split, cid, method, b)]
            metrics = engine.episode_metrics(env, menu["items"], profile, old["selected_action"])
            if any(old[k] != metrics[k] for k in METRICS):
                raise RuntimeError(f"Historical hidden-reference replay mismatch: {split}/{cid}/{method}/{b}")
            historical_rows.append({**old, "trajectory_origin": "immutable_historical_trace",
                                    "hidden_reference_replay_agrees": True})

    # Replay every historical DV prediction from its original observed answers.
    dynamic = engine.PublicPolicy(env, menu, priors, "decision_value")
    user = env.ReferenceUser(profile)
    full_path = data["historical"][(split, cid, "decision_value", 6)]["query_sequence"]
    for b in CFG["budgets"]:
        old = data["historical"][(split, cid, "decision_value", b)]
        if old["query_sequence"] != full_path[:b] or not set(full_path) == set(CFG["query_actions"]):
            raise RuntimeError("Historical DV path is not a legal shared prefix")
        predicted, _ = cached_predict(dynamic, split, menu["menu_id"], memo, engine)
        if predicted != old["selected_action"]:
            raise RuntimeError(f"Original DV predictor drift: {split}/{cid}/{b}")
        if b < 6:
            dynamic.observe(full_path[b], user.answer(full_path[b]))

    static = engine.PublicPolicy(env, menu, priors, "decision_value")
    new_rows = []
    for b in CFG["budgets"]:
        predicted, success = cached_predict(static, split, menu["menu_id"], memo, engine)
        metrics = engine.episode_metrics(env, menu["items"], profile, predicted)
        row = {"case_id": cid, "profile_id": case["profile_id"], "menu_id": menu["menu_id"],
               "split": split, "pool_index": case["pool_index"], "user_cohort": case["user_cohort"],
               "gender": menu["gender"], "category": menu["category"], "menu_size": len(menu["items"]),
               "method": CFG["new_method"], "budget": b, "elicitation_units": b, "dialogue_turns": b,
               "query_sequence": [h["action"] for h in static.history], "initial_query_order": rank["order"],
               "posterior_predicted_success": success, "trajectory_origin": "new_static_order_ablation",
               "hidden_reference_replay_agrees": True, **metrics}
        new_rows.append(row)
        if b < 6:
            q = rank["order"][b]
            static.observe(q, user.answer(q))
    for b in (0, 1, 6):
        old = data["historical"][(split, cid, "decision_value", b)]
        if any(new_rows[b][k] != old[k] for k in METRICS):
            raise RuntimeError(f"Budget {b} component invariant failed: {split}/{cid}")
    if full_path[0] != rank["order"][0] or not new_rows[6]["exact_decision_correct"]:
        raise RuntimeError("First-query or full-disclosure invariant failed")
    target = ["NO_BUY"] if reference["decision"] == "NO_BUY" else reference["valid_purchase_ids"]
    if any(r["reference_target_set"] != target for r in new_rows):
        raise RuntimeError("Frozen reference target changed")
    return {"rows": historical_rows + new_rows,
            "initial_order": {"split": split, "menu_id": menu["menu_id"], "pool_index": case["pool_index"], **rank},
            "receipt": {"split": split, "case_id": cid, "historical_metric_replays": 28,
                        "historical_dv_prediction_replays": 7, "new_rows": 7,
                        "budgets_0_1_6_identical": True, "first_query_identical": True,
                        "terminal_correct": True}}


def run():
    verified = verify_inputs()
    data = load_data()
    started = {"status": "STARTED_ONCE", "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "cases": 736, "planned_trace_rows": 736 * 35, "workers": CFG["workers"],
               "historical_dv_path_reselected": False, "historical_dv_predictions_replayed": True,
               "model_calls": 0, "training_runs": 0, **verified}
    dump(RESULTS / "RUN_STARTED.json", started, True)
    clock_start = time.monotonic()
    traces = RESULTS / "PAIRED_CASES.jsonl"
    receipts = RESULTS / "CASE_REPLAY_RECEIPTS.jsonl"
    order_map = {}
    count = 0
    try:
        context = multiprocessing.get_context(CFG["start_method"])
        with ProcessPoolExecutor(max_workers=CFG["workers"], mp_context=context,
                                 initializer=initialize_worker) as order_pool:
            ranks = dict(order_pool.map(execute_order, sorted(data["menus"]), chunksize=1))
        print(json.dumps({"initial_orders_completed": len(ranks),
                          "elapsed_seconds": round(time.monotonic() - clock_start, 1)}), flush=True)
        with traces.open("x", encoding="utf-8") as f, receipts.open("x", encoding="utf-8") as r:
            with ProcessPoolExecutor(max_workers=CFG["workers"], mp_context=context,
                                     initializer=initialize_worker, initargs=(ranks,)) as pool:
                for ordinal, result in enumerate(pool.map(execute_case, data["cases"], chunksize=1), 1):
                    if len(result["rows"]) != 35:
                        raise RuntimeError("Per-case row count invalid")
                    for row in result["rows"]:
                        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    r.write(json.dumps(result["receipt"], ensure_ascii=False, sort_keys=True) + "\n")
                    f.flush()
                    r.flush()
                    count += len(result["rows"])
                    order = result["initial_order"]
                    key = (order["split"], order["menu_id"])
                    if key in order_map and order_map[key] != order:
                        raise RuntimeError("Static initial order depends on hidden user or worker")
                    order_map[key] = order
                    if ordinal == 1 or ordinal % 16 == 0 or ordinal == 736:
                        print(json.dumps({"completed_cases": ordinal, "total": 736,
                                          "elapsed_seconds": round(time.monotonic() - clock_start, 1)}), flush=True)
            os.fsync(f.fileno())
            os.fsync(r.fileno())
        if count != 25760 or len(order_map) != 54:
            raise RuntimeError("Full panel/order coverage mismatch")
        dump_rows(RESULTS / "INITIAL_QUERY_ORDERS.jsonl", [order_map[k] for k in sorted(order_map)])
        verify_inputs()
        complete = {"status": "COMPLETE", "cases": 736, "trace_rows": count, "menu_orders": len(order_map),
                    "historical_metric_replays": 20608, "historical_dv_prediction_replays": 5152,
                    "new_static_rows": 5152, "elapsed_seconds": time.monotonic() - clock_start,
                    "trace_sha256": sha(traces), "model_calls": 0, "training_runs": 0}
        dump(RESULTS / "RUN_COMPLETED.json", complete, True)
        return complete
    except BaseException as exc:
        dump(RESULTS / "RUN_FAILURE.json", {"status": "FAILED_PRESERVE_PARTIAL", "exception": type(exc).__name__,
             "message": str(exc), "trace_rows_written": count, "model_calls": 0}, True)
        raise


def verify():
    result = verify_inputs()
    completed = read(RESULTS / "RUN_COMPLETED.json")
    if completed["status"] != "COMPLETE" or sha(RESULTS / "PAIRED_CASES.jsonl") != completed["trace_sha256"]:
        raise RuntimeError("Completed trace hash invalid")
    if (RESULTS / "RUN_FAILURE.json").exists():
        raise RuntimeError("Failure evidence requires review")
    manifest = read(RESULTS / "OUTPUT_MANIFEST.json")
    for rel, digest in manifest["files_sha256"].items():
        if sha(HERE / rel) != digest:
            raise RuntimeError(f"Output changed: {rel}")
    data = rows(RESULTS / "PAIRED_CASES.jsonl")
    keys = {(r["split"], r["case_id"], r["method"], r["budget"]) for r in data}
    if len(data) != 25760 or len(keys) != len(data):
        raise RuntimeError("Output coverage or key uniqueness failed")
    receipts = rows(RESULTS / "CASE_REPLAY_RECEIPTS.jsonl")
    if len(receipts) != 736 or len({(r["split"], r["case_id"]) for r in receipts}) != 736:
        raise RuntimeError("Case replay receipt coverage invalid")
    result.update({"status": "PASS", "unique_trace_rows": len(data), "cases": len(receipts),
                   "profiles": len({(r["split"], r["profile_id"]) for r in data}),
                   "output_files_verified": len(manifest["files_sha256"]), "model_calls": 0, "training_runs": 0})
    dump(RESULTS / "VERIFICATION.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "freeze", "run", "analyze", "verify"))
    args = parser.parse_args()
    if args.command == "analyze":
        import ablation_statistics
        result = ablation_statistics.analyze()
    else:
        result = globals()[args.command]()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
