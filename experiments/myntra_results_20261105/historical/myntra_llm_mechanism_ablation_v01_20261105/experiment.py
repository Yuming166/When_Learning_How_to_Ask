"""Frozen response-bank component replay. No transport or model client code."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True
import engine
import environment as ref
import legacy_replay

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text())
INPUT = HERE / "artifacts/input"
RESULTS = HERE / "results"
SOURCES = {m: HERE.parent / c["experiment"] for m, c in CFG["models"].items()}
PYTHON = HERE.parent / CFG["python_ablation"]
STATIC = "decision_value_initial_order"
METRICS = ("reference_decision", "reference_target_set", "selected_action", "exact_decision_correct",
           "purchase_recall_case", "no_buy_correct_case", "false_purchase_case", "hard_constraint_violation",
           "score_regret", "normalized_score_regret")
PATH_FIELDS = ("query_sequence", "valid_query_sequence", "elicitation_units", "dialogue_turns",
               "answer_path_complete", "failed_query_action", "exact_profile_matches_observed",
               "posterior_success_probability")


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")


def dump_rows(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        for value in values:
            f.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def preserve_sources():
    bound, freeze_counts = {}, {}
    for model, base in SOURCES.items():
        frozen = read(base / "FROZEN.json")
        freeze_counts[model] = len(frozen["files"])
        for name, expected in frozen["files"].items():
            p = Path(name) if Path(name).is_absolute() else base / name
            if sha(p) != expected:
                raise RuntimeError(f"Original freeze mismatch: {model}/{name}")
            bound[str(p.resolve())] = expected
    for name, expected in read(PYTHON / "FROZEN.json")["files_sha256"].items():
        p = PYTHON / name
        if sha(p) != expected:
            raise RuntimeError(f"Python mechanism dependency changed: {name}")
        bound[str(p.resolve())] = expected
    for base in [*SOURCES.values(), PYTHON]:
        for p in sorted(base.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                bound[str(p.resolve())] = sha(p)
    return {"files_sha256": bound, "source_freeze_file_counts": freeze_counts}


def prepare():
    if INPUT.exists():
        raise FileExistsError("Preserve previous input snapshot")
    preserved = preserve_sources()
    shared = {"profiles.jsonl": "private/profiles.jsonl", "prior_profiles.jsonl": "private/prior_profiles.jsonl",
              "cases.jsonl": "private/selected_cases.jsonl", "menus.jsonl": "public/menus.jsonl",
              "vocabularies.json": "public/vocabularies.json", "jobs.jsonl": "private/jobs.jsonl"}
    INPUT.mkdir(parents=True)
    for dest, rel in shared.items():
        digests = {sha(base / "artifacts/input" / rel) for base in SOURCES.values()}
        if len(digests) != 1:
            raise RuntimeError(f"Shared input differs across models: {rel}")
        shutil.copyfile(SOURCES["luna"] / "artifacts/input" / rel, INPUT / dest)
    shutil.copyfile(SOURCES["glm"] / "artifacts/reference/ENVIRONMENT_CONFIG.json", INPUT / "environment_config.json")
    shutil.copyfile(PYTHON / "results/INITIAL_QUERY_ORDERS.jsonl", INPUT / "python_initial_orders.jsonl")
    py_static = [r for r in rows(PYTHON / "results/PAIRED_CASES.jsonl") if r["split"] == "development" and r["method"] == STATIC]
    dump_rows(INPUT / "python_static_traces.jsonl", py_static)
    for model, base in SOURCES.items():
        (INPUT / model / "records").mkdir(parents=True)
        for p in sorted((base / "artifacts/run/records").glob("*.json")):
            shutil.copyfile(p, INPUT / model / "records" / p.name)
        shutil.copyfile(base / "results/PAIRED_POLICY_TRACES.jsonl", INPUT / model / "historical_traces.jsonl")
    for name, source_name in (("engine.py", "engine.py"), ("environment.py", "environment.py"), ("legacy_replay.py", "replay.py")):
        if sha(HERE / name) != sha(SOURCES["glm"] / source_name):
            raise RuntimeError(f"Frozen implementation copy mismatch: {name}")
    dump(HERE / "UPSTREAM_PRESERVATION.json", preserved, True)
    data = load_data()
    quality = {}
    for model, info in CFG["models"].items():
        quality[model] = {"records": 288, "attempted": sum(bool(r.get("attempted")) for r in data["raw"][model].values()),
            "valid": sum(bool(r["valid"]) for r in data["banks"][model].values()),
            "exact": sum(bool(r["exact_profile_match"]) for r in data["banks"][model].values()),
            "complete_valid_profiles": sum(all(data["banks"][model][(pid, a)]["valid"] for a in CFG["query_actions"]) for pid in data["profiles"])}
        if quality[model]["valid"] != info["expected_valid"] or quality[model]["exact"] != info["expected_exact"] or quality[model]["attempted"] != 288:
            raise RuntimeError(f"Answer bank provenance/quality drift: {model}")
    for case in data["cases"]:
        profile, menu = data["profiles"][case["profile_id"]], data["menus"][case["menu_id"]]
        if ref.evaluate_python(menu["items"], profile) != ref.evaluate_sql(menu["items"], profile):
            raise RuntimeError("Independent evaluator disagreement")
    common = [pid for pid in data["profiles"] if all(data["banks"][m][(pid, a)]["valid"] for m in CFG["models"] for a in CFG["query_actions"])]
    receipt = {"status": "INPUT_PREFLIGHT_PASS", "cases_per_model": 280, "profiles": 48, "menus": 35,
               "quality": quality, "common_complete_profiles": sorted(common),
               "common_complete_cases": sum(c["profile_id"] in common for c in data["cases"]),
               "upstream_preserved_files": len(preserved["files_sha256"]),
               "source_freeze_file_counts": preserved["source_freeze_file_counts"], "new_model_calls": 0}
    dump(HERE / "PREPARED.json", receipt, True)
    return receipt


def load_data():
    data = {"profiles": {p["profile_id"]: p for p in rows(INPUT / "profiles.jsonl")},
            "menus": {m["menu_id"]: m for m in rows(INPUT / "menus.jsonl")}, "cases": rows(INPUT / "cases.jsonl"),
            "vocab": read(INPUT / "vocabularies.json"), "thresholds": read(INPUT / "environment_config.json")["purchase_thresholds"],
            "priors": collections.defaultdict(list), "banks": {}, "raw": {}, "historical": {}}
    for p in rows(INPUT / "prior_profiles.jsonl"):
        data["priors"][p["pool_index"]].append(p)
    if len(data["profiles"]) != 48 or len(data["menus"]) != 35 or len(data["cases"]) != 280 or len({c["case_id"] for c in data["cases"]}) != 280:
        raise RuntimeError("Shared denominator changed")
    if set(data["priors"]) != set(range(6)) or any(len(v) != 2048 for v in data["priors"].values()):
        raise RuntimeError("Original prior bank changed")
    jobs = rows(INPUT / "jobs.jsonl")
    if len(jobs) != 288 or len({j["job_id"] for j in jobs}) != 288 or len({(j["profile_id"], j["query_action"]) for j in jobs}) != 288:
        raise RuntimeError("Field job coverage changed")
    for model in CFG["models"]:
        rr = [read(p) for p in sorted((INPUT / model / "records").glob("*.json"))]
        records = {r["job_id"]: r for r in rr}
        if len(records) != 288 or len(rr) != 288 or set(records) != {j["job_id"] for j in jobs}:
            raise RuntimeError("Missing/duplicate field response record")
        data["raw"][model], data["banks"][model] = records, {}
        for job in jobs:
            r = records[job["job_id"]]
            if (r["profile_id"], r["query_action"], r["replicate"]) != (job["profile_id"], job["query_action"], 1):
                raise RuntimeError("Field-record linkage changed")
            value = r["parsed"]["value"] if r.get("valid") else None
            if r.get("valid"):
                parsed = legacy_replay.parse_field_answer(job["query_action"], r["content"], data["vocab"][str(job["pool_index"])], data["thresholds"])
                if parsed != value:
                    raise RuntimeError("Original parsed valid answer changed")
            truth = ref.ReferenceUser(data["profiles"][job["profile_id"]]).answer(job["query_action"])
            data["banks"][model][(job["profile_id"], job["query_action"])] = {
                "valid": bool(r.get("valid")), "value": value,
                "exact_profile_match": bool(r.get("valid") and engine.canonical(value) == engine.canonical(truth))}
        hh = rows(INPUT / model / "historical_traces.jsonl")
        lookup = {(r["case_id"], r["method"], r["budget"]): r for r in hh}
        required = {(c["case_id"], m, b) for c in data["cases"] for m in CFG["methods"] for b in CFG["budgets"]}
        if set(lookup) != required or len(lookup) != len(hh):
            raise RuntimeError("Historical trace key coverage changed")
        data["historical"][model] = lookup
    data["python_orders"] = {r["menu_id"]: r for r in rows(INPUT / "python_initial_orders.jsonl") if r["split"] == "development"}
    data["python_static"] = {(r["case_id"], r["budget"]): r for r in rows(INPUT / "python_static_traces.jsonl")}
    if len(data["python_orders"]) != 35 or len(data["python_static"]) != 1960:
        raise RuntimeError("Python ablation reference coverage changed")
    return data


def verify_inputs():
    frozen = read(HERE / "FROZEN.json")
    for name, expected in frozen["files_sha256"].items():
        if sha(HERE / name) != expected:
            raise RuntimeError(f"Frozen dependency changed: {name}")
    upstream = read(HERE / "UPSTREAM_PRESERVATION.json")["files_sha256"]
    for name, expected in upstream.items():
        if sha(name) != expected:
            raise RuntimeError(f"Upstream file changed: {name}")
    return {"frozen_files": len(frozen["files_sha256"]), "preserved_upstream_files": len(upstream)}


def freeze():
    if (RESULTS / "RUN_STARTED.json").exists() or read(HERE / "TEST_RECEIPT.json")["status"] != "PASS":
        raise RuntimeError("Freeze requires passing tests and no started run")
    paths = [HERE / p for p in ("config.json", "PROTOCOL.md", "README_ZH.md", "experiment.py", "analysis.py", "test_ablation.py",
             "engine.py", "environment.py", "legacy_replay.py", "PREPARED.json", "TEST_RECEIPT.json", "UPSTREAM_PRESERVATION.json")]
    paths += sorted(p for p in INPUT.rglob("*") if p.is_file())
    manifest = {"status": "FROZEN_BEFORE_STATIC_LLM_REPLAY", "frozen_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "historical_model_answers_and_full_dv_results_already_observed": True,
                "files_sha256": {str(p.relative_to(HERE)): sha(p) for p in paths}, "new_model_calls": 0}
    dump(HERE / "FROZEN.json", manifest, True)
    return {"status": manifest["status"], "frozen_files": len(paths)}


def initial_rank(menu, prior):
    p = engine.PublicPolicy(ref, menu, prior, "decision_value")
    scores = {a: p.score_query(a) for a in CFG["query_actions"]}
    order = sorted(CFG["query_actions"], key=lambda a: (-scores[a], CFG["query_actions"].index(a)))
    return {"scores": scores, "order": order, "initial_prediction": list(p.predict())}


WORK = None


def init_worker(ranks=None):
    global WORK
    WORK = {"data": load_data(), "ranks": ranks or {}, "predictions": {}}


def order_job(menu_id):
    menu = WORK["data"]["menus"][menu_id]
    rank = initial_rank(menu, WORK["data"]["priors"][menu["pool_index"]])
    old = WORK["data"]["python_orders"][menu_id]
    if any(rank[k] != old[k] for k in ("scores", "order", "initial_prediction")):
        raise RuntimeError("LLM control's initial rank differs from Python control")
    return menu_id, rank


def predict_cached(policy, menu_id, memo):
    key = (menu_id, engine.canonical(policy.known))
    if key not in memo:
        memo[key] = policy.predict()
    return memo[key]


def replay_path(case, profile, prior, bank, vocab, order, source_rows=None, memo=None):
    """Costs/stop state always recomputed; only pure predictions may be cached."""
    menu = case["public_menu"]
    p = engine.PublicPolicy(ref, menu, prior, "decision_value")
    user_attempts, trace = [], []
    stopped, failed, exact = False, None, 0
    if memo is None:
        memo = {}
    source_path = source_rows[6]["query_sequence"] if source_rows is not None else None
    for b in CFG["budgets"]:
        if b > 0 and not stopped:
            action = source_path[len(user_attempts)] if source_rows is not None else order[len(user_attempts)]
            if action not in CFG["query_actions"] or action in user_attempts:
                raise RuntimeError("Repeated or illegal question in path")
            user_attempts.append(action)
            response = bank.get(action)
            if response is None or not response["valid"]:
                stopped, failed = True, action
            else:
                answer = response["value"]
                try:
                    validator = ref.PublicAgent(menu, vocab, "fieldwise")
                    for h in p.history:
                        validator.observe(h["action"], h["answer"])
                    validator.observe(action, answer)
                    p.observe(action, answer)
                    exact += int(response["exact_profile_match"])
                except Exception:
                    stopped, failed = True, action
        recommendation, success = predict_cached(p, menu["menu_id"], memo)
        row = {"case_id": case["case_id"], "profile_id": profile["profile_id"], "stratum": case["stratum"],
               "menu_id": menu["menu_id"], "replicate": 1, "method": "decision_value" if source_rows is not None else STATIC,
               "budget": b, "query_sequence": user_attempts[:], "valid_query_sequence": [h["action"] for h in p.history],
               "elicitation_units": len(user_attempts), "dialogue_turns": len(user_attempts), "answer_path_complete": not stopped,
               "failed_query_action": failed, "exact_profile_matches_observed": exact, "posterior_success_probability": success,
               **engine.episode_metrics(ref, menu["items"], profile, recommendation)}
        if source_rows is not None and any(row[k] != source_rows[b][k] for k in row):
            raise RuntimeError(f"Historical DV replay differs: {case['case_id']}/{b}")
        trace.append(row)
    return trace


def case_job(case):
    data, memo = WORK["data"], WORK["predictions"]
    profile = data["profiles"][case["profile_id"]]
    menu = data["menus"][case["menu_id"]]
    public_case = {**case, "public_menu": menu}
    rank = WORK["ranks"][menu["menu_id"]]
    prior, vocab = data["priors"][profile["pool_index"]], data["vocab"][str(profile["pool_index"])]
    memo[(menu["menu_id"], engine.canonical({}))] = tuple(rank["initial_prediction"])
    output, receipts = [], []
    for model in CFG["models"]:
        bank = {a: data["banks"][model][(profile["profile_id"], a)] for a in CFG["query_actions"]}
        old = [data["historical"][model][(case["case_id"], "decision_value", b)] for b in CFG["budgets"]]
        dynamic = replay_path(public_case, profile, prior, bank, vocab, rank["order"], old, memo)
        static = replay_path(public_case, profile, prior, bank, vocab, rank["order"], None, memo)
        if old[1]["query_sequence"] != [rank["order"][0]]:
            raise RuntimeError("Adaptive and static first question mismatch")
        for b in (0, 1):
            if any(dynamic[b][k] != static[b][k] for k in (*METRICS, *PATH_FIELDS)):
                raise RuntimeError("Budget0/1 invariant failed")
        if dynamic[6]["answer_path_complete"] and static[6]["answer_path_complete"]:
            if any(dynamic[6][k] != static[6][k] for k in METRICS):
                raise RuntimeError("Complete-bank terminal action/metrics mismatch")
        complete_exact = all(r["valid"] and r["exact_profile_match"] for r in bank.values())
        if complete_exact:
            for r in static:
                py = data["python_static"][(case["case_id"], r["budget"])]
                if any(r[k] != py[k] for k in (*METRICS, "query_sequence")):
                    raise RuntimeError("Exact-answer LLM/Python static trace parity failed")
        for method_rows in (dynamic, static):
            for r in method_rows:
                output.append({**r, "model": model, "pool_index": case["pool_index"], "user_cohort": case["user_cohort"],
                               "gender": case["gender"], "category": case["category"],
                               "trajectory_origin": "historical_dv_replayed" if r["method"] == "decision_value" else "new_static_order_replay"})
        receipts.append({"model": model, "case_id": case["case_id"], "historical_dv_rows_exact": 7,
                         "budget_0_1_identical": True, "complete_exact_bank": complete_exact,
                         "python_static_parity_when_exact": True if complete_exact else None})
    return output, receipts


def run():
    verified = verify_inputs()
    data = load_data()
    dump(RESULTS / "RUN_STARTED.json", {"status": "STARTED_ONCE", "planned_rows": 11760,
         "case_jobs": 280, "models": list(CFG["models"]), "new_model_calls": 0, **verified}, True)
    start, count = time.monotonic(), 0
    context = multiprocessing.get_context(CFG["start_method"])
    try:
        with ProcessPoolExecutor(max_workers=CFG["workers"], mp_context=context, initializer=init_worker) as pool:
            ranks = dict(pool.map(order_job, sorted(data["menus"]), chunksize=1))
        dump_rows(RESULTS / "INITIAL_QUERY_ORDERS.jsonl", [{"menu_id": m, **ranks[m]} for m in sorted(ranks)])
        print(json.dumps({"initial_menu_orders": len(ranks), "elapsed_seconds": round(time.monotonic()-start, 1)}), flush=True)
        with (RESULTS / "PAIRED_CASES.jsonl").open("x") as f, (RESULTS / "CASE_REPLAY_RECEIPTS.jsonl").open("x") as receipt:
            with ProcessPoolExecutor(max_workers=CFG["workers"], mp_context=context, initializer=init_worker, initargs=(ranks,)) as pool:
                for i, (rr, checks) in enumerate(pool.map(case_job, data["cases"], chunksize=1), 1):
                    if len(rr) != 42 or len(checks) != 3:
                        raise RuntimeError("Case-model-budget row count mismatch")
                    for r in rr:
                        f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
                    for r in checks:
                        receipt.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
                    f.flush()
                    receipt.flush()
                    count += len(rr)
                    if i == 1 or i % 20 == 0 or i == 280:
                        print(json.dumps({"completed_case_jobs": i, "total": 280, "elapsed_seconds": round(time.monotonic()-start, 1)}), flush=True)
            os.fsync(f.fileno())
            os.fsync(receipt.fileno())
        if count != 11760:
            raise RuntimeError("Incomplete full panel")
        verify_inputs()
        complete = {"status": "COMPLETE", "rows": count, "historical_dv_replayed_rows": 5880,
                    "new_static_rows": 5880, "case_model_receipts": 840, "profiles": 48,
                    "cases_per_model": 280, "elapsed_seconds": time.monotonic()-start,
                    "trace_sha256": sha(RESULTS / "PAIRED_CASES.jsonl"), "new_model_calls": 0, "training_runs": 0}
        dump(RESULTS / "RUN_COMPLETED.json", complete, True)
        return complete
    except BaseException as exc:
        dump(RESULTS / "RUN_FAILURE.json", {"status": "FAILED_PRESERVE_PARTIAL", "exception": type(exc).__name__,
             "message": str(exc), "rows_written": count, "new_model_calls": 0}, True)
        raise


def verify():
    checks = verify_inputs()
    complete = read(RESULTS / "RUN_COMPLETED.json")
    if (RESULTS / "RUN_FAILURE.json").exists() or sha(RESULTS / "PAIRED_CASES.jsonl") != complete["trace_sha256"]:
        raise RuntimeError("Run failure or trace hash mismatch")
    rr = rows(RESULTS / "PAIRED_CASES.jsonl")
    expected = {(m, c["case_id"], method, b) for m in CFG["models"] for c in rows(INPUT / "cases.jsonl") for method in CFG["evaluated_methods"] for b in CFG["budgets"]}
    actual = {(r["model"], r["case_id"], r["method"], r["budget"]) for r in rr}
    if actual != expected or len(rr) != len(actual):
        raise RuntimeError("Exact output key coverage mismatch")
    output = read(RESULTS / "OUTPUT_MANIFEST.json")["files_sha256"]
    for path, expected_hash in output.items():
        if sha(HERE / path) != expected_hash:
            raise RuntimeError("Output hash mismatch")
    checks.update(status="PASS", rows=len(rr), profiles=48, cases_per_model=280,
                  output_files=len(output), new_model_calls=0, training_runs=0)
    dump(RESULTS / "VERIFICATION.json", checks)
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "freeze", "run", "analyze", "verify"))
    command = parser.parse_args().command
    if command == "analyze":
        import analysis
        result = analysis.analyze()
    else:
        result = globals()[command]()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
