from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import engine


BASE = pathlib.Path(__file__).resolve().parent
WORKTREE = BASE.parents[1]
CFG = json.loads((BASE / "config.json").read_text())
OLD_LUNA = WORKTREE / CFG["source_luna_simulator"]
LEGACY = WORKTREE / "experiments/myntra_preference_dev_v01_20261104"
FULL_DEV = WORKTREE / "experiments/myntra_full_dev_catalogue_v02_20261104"
INPUT = BASE / "artifacts/input"
PRIVATE = INPUT / "private"
PUBLIC = INPUT / "public"
PROMPTS = INPUT / "prompts"
RUN = BASE / "artifacts/run"
RECORDS = RUN / "records"
RESULTS = BASE / "results"

sys.path[:0] = [str(OLD_LUNA), str(LEGACY)]
import environment as ref
import luna_simulator as luna_transport

LOCK = threading.Lock()
STATE = {"started": None, "attempted": 0, "transport_failures": 0,
         "consecutive_transport_failures": 0, "abort_reason": None}


def read(path):
    return json.loads(pathlib.Path(path).read_text())


def read_rows(path):
    path = pathlib.Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_rows(path, values):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def sha256(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _copy_snapshot():
    if (BASE / "PREPARED.json").exists():
        raise FileExistsError("Prepared snapshot already exists; preserve it")
    src_private = OLD_LUNA / "artifacts/input/private"
    src_public = OLD_LUNA / "artifacts/input/public"
    cases = read_rows(src_private / "selected_cases.jsonl")
    profiles = read_rows(src_private / "profiles.jsonl")
    menus = read_rows(src_public / "menus.jsonl")
    vocab = read(src_public / "vocabularies.json")
    profile_ids = {c["profile_id"] for c in cases}
    menu_ids = {c["menu_id"] for c in cases}
    profiles = [p for p in profiles if p["profile_id"] in profile_ids]
    menus = [m for m in menus if m["menu_id"] in menu_ids]
    if len(cases) != 8 or len(profiles) != 8 or len(menus) != len(menu_ids) or len(menu_ids) != 5:
        raise ValueError("The frozen eight-case Luna input inventory changed")
    if {c["stratum"] for c in cases} != {"BUY_UNIQUE", "BUY_TIED", "NO_BUY_FEASIBLE", "NO_BUY_INFEASIBLE"}:
        raise ValueError("Expected the four frozen decision strata")

    full_dev_cfg = read(FULL_DEV / "config.json")
    full_dev_pool = {tuple(pair): idx for idx, pair in enumerate(full_dev_cfg["pools"])}
    menu_by_id = {m["menu_id"]: m for m in menus}
    cases = [{**c, "prior_pool_index": full_dev_pool[(menu_by_id[c["menu_id"]]["gender"],
                                                     menu_by_id[c["menu_id"]]["category"])]}
             for c in cases]
    write_rows(PRIVATE / "selected_cases.jsonl", cases)
    write_rows(PRIVATE / "profiles.jsonl", profiles)
    write_rows(PUBLIC / "cases.jsonl", [
        {"case_id": c["case_id"], "profile_id": c["profile_id"], "menu_id": c["menu_id"]}
        for c in cases
    ])
    write_rows(PUBLIC / "menus.jsonl", menus)
    write_json(PUBLIC / "vocabularies.json", vocab)
    shutil.copyfile(OLD_LUNA / "artifacts/input/SYSTEM_PROMPT_ZH.txt", INPUT / "SYSTEM_PROMPT_ZH.txt")

    prior_path = FULL_DEV / "artifacts/prepared/private/prior_profiles.jsonl"
    all_priors = read_rows(prior_path)
    relevant_pools = sorted({c["prior_pool_index"] for c in cases})
    priors = [p for p in all_priors if p["pool_index"] in relevant_pools]
    counts = {i: sum(p["pool_index"] == i for p in priors) for i in relevant_pools}
    if any(counts[i] != 2048 for i in relevant_pools):
        raise ValueError(f"Full-development relevant prior bank count mismatch: {counts}")
    write_rows(PRIVATE / "prior_profiles.jsonl", priors)

    profile_by_id = {p["profile_id"]: p for p in profiles}
    jobs, prompt_rows = [], []
    for case in cases:
        profile = profile_by_id[case["profile_id"]]
        pool_vocab = vocab[str(profile["pool_index"])]
        for replicate in (1, 2):
            for action in CFG["query_actions"]:
                job_id = f"{case['case_id']}__r{replicate}__{action}"
                question = query_question(action, pool_vocab)
                messages = [
                    {"role": "system", "content": customer_system_text(profile)},
                    {"role": "user", "content": question},
                ]
                prompt = luna_transport.prompt_from_messages(messages)
                job = {"job_id": job_id, "case_id": case["case_id"],
                       "profile_id": case["profile_id"], "menu_id": case["menu_id"],
                       "stratum": case["stratum"], "pool_index": profile["pool_index"],
                       "query_action": action, "replicate": replicate,
                       "kind": "field_answer"}
                jobs.append(job)
                prompt_rows.append({**job, "prompt": prompt,
                                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
    if len(jobs) != 96 or len({j["job_id"] for j in jobs}) != 96:
        raise ValueError("Expected 96 unique response-bank calls")
    write_rows(PRIVATE / "jobs.jsonl", jobs)
    write_rows(PROMPTS / "requests.jsonl", prompt_rows)
    write_json(BASE / "PREPARED.json", {
        "status": "PREPARED_ZERO_MODEL_CALLS",
        "source_luna_simulator": str(OLD_LUNA),
        "source_full_dev_prior": str(prior_path),
        "cases": len(cases), "unique_profiles": len(profiles), "menus": len(menus),
        "response_bank_replicates": 2, "actions_per_profile": 6,
        "planned_calls": len(jobs), "model_calls": 0,
        "prior_counts_by_full_catalogue_pool": {str(k): v for k, v in counts.items()},
        "reserved_products_used": 0,
    })


def query_question(action, pool_vocab):
    if action == "purchase_threshold":
        return (
            "这轮只询问你的购买意愿门槛。请按固定画像中预先设定的原始整数门槛回答，"
            "不要根据眼前商品重新判断，也不要披露其他偏好字段。\n"
            '只输出 JSON：{"purchase_threshold":整数}。'
        )
    labels = pool_vocab[action]
    extra = ""
    required = ["field", "scores"]
    if action == "wash_care":
        extra = (
            "另外，按画像返回你愿意接受的全部商家洗护标签，"
            "只能从 dry clean、hand wash、machine wash 中选择，且至少一个。"
        )
        required.append("allowed_care_labels")
    elif action == "fabric":
        extra = "另外，返回画像中排除的商家面料标签，可以为空列表。"
        required.append("excluded_fabric_labels")
    schema = {"field": action, "scores": {label: "整数" for label in labels}}
    if action == "wash_care":
        schema["allowed_care_labels"] = ["原始洗护标签"]
    if action == "fabric":
        schema["excluded_fabric_labels"] = ["原始面料标签"]
    return (
        f"这轮只询问 {action} 这一项偏好。请按固定画像，把下列每个商家标签对应的原始整数偏好分数逐项返回；"
        "不要重新推断、调整分数或披露其他维度。标签必须原样保留。\n"
        + json.dumps(labels, ensure_ascii=False) + "\n" + extra + "\n"
        + "返回对象必须且只能包含这些键：" + ", ".join(required) + "。\n"
        + "只输出 JSON：" + json.dumps(schema, ensure_ascii=False)
    )


def customer_system_text(profile):
    template = (INPUT / "SYSTEM_PROMPT_ZH.txt").read_text()
    private = ref.private_preferences(profile)
    return template.replace("{{PROFILE}}", json.dumps(private, ensure_ascii=False, sort_keys=True))


def _source_manifest_paths():
    paths = [
        BASE / "config.json", BASE / "PROTOCOL.md", BASE / "engine.py",
        BASE / "luna_policy_comparison.py", BASE / "test_luna_policy_comparison.py",
        BASE / "PREPARED.json",
        OLD_LUNA / "PROTOCOL.md", OLD_LUNA / "FROZEN_CORRECTED.json",
        OLD_LUNA / "config.json", OLD_LUNA / "luna_simulator.py",
        OLD_LUNA / "artifacts/input/SYSTEM_PROMPT_ZH.txt",
        OLD_LUNA / "artifacts/input/private/selected_cases.jsonl",
        OLD_LUNA / "artifacts/input/private/profiles.jsonl",
        OLD_LUNA / "artifacts/input/public/menus.jsonl",
        OLD_LUNA / "artifacts/input/public/vocabularies.json",
        LEGACY / "environment.py", LEGACY / "qwen_smoke.py",
        FULL_DEV / "FROZEN.json", FULL_DEV / "config.json",
        FULL_DEV / "artifacts/prepared/private/prior_profiles.jsonl",
        OLD_LUNA / "results/REPORT_ZH.md",
    ]
    paths.extend(p for p in INPUT.rglob("*") if p.is_file())
    failed_prep = BASE / "artifacts/preparation_failed_pool_index_mismatch_0_1_0"
    if failed_prep.exists():
        paths.extend(p for p in failed_prep.rglob("*") if p.is_file())
    return sorted({p.resolve() for p in paths})


def freeze():
    if not (BASE / "PREPARED.json").exists():
        raise FileNotFoundError("Run prepare before freezing")
    if RUN.exists() and any(RUN.glob("records/*.json")):
        raise RuntimeError("Model-call records already exist; cannot freeze after inference")
    version = subprocess.run(["codex", "--version"], text=True, capture_output=True, check=True).stdout.strip()
    files = {}
    for path in _source_manifest_paths():
        if not path.is_file():
            raise FileNotFoundError(path)
        files[str(path)] = sha256(path)
    manifest = {
        "status": "FROZEN_PRE_INFERENCE",
        "frozen_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested_model": CFG["requested_model"],
        "codex_cli_version": version,
        "planned_calls": 96,
        "smoke_calls": 12,
        "full_calls_after_smoke": 84,
        "sha256_scope": "protocol, config, code, source snapshots, private/public inputs, generated prompts, prior bank, and upstream dependencies",
        "files": files,
    }
    write_json(BASE / "FROZEN.json", manifest)
    return manifest


def verify_frozen():
    frozen = read(BASE / "FROZEN.json")
    if frozen.get("status") != "FROZEN_PRE_INFERENCE":
        raise ValueError("Unexpected freeze status")
    failures = []
    for name, expected in frozen["files"].items():
        path = pathlib.Path(name)
        if not path.is_file() or sha256(path) != expected:
            failures.append(name)
    if failures:
        raise RuntimeError("Frozen input/code changed: " + ", ".join(failures[:8]))
    return frozen


def _reject_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate_json_key")
        obj[key] = value
    return obj


def parse_field_answer(action, text, vocab, purchase_thresholds):
    if not isinstance(text, str):
        raise ValueError("content_type")
    raw = text.strip()
    if raw.startswith("```"):
        import re
        match = re.fullmatch(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", raw, re.I)
        if not match:
            raise ValueError("incomplete_fence")
        raw = match.group(1)
    obj = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    if action == "purchase_threshold":
        if not isinstance(obj, dict) or set(obj) != {"purchase_threshold"}:
            raise ValueError("threshold_schema")
        value = obj["purchase_threshold"]
        if type(value) is not int or value not in purchase_thresholds:
            raise ValueError("threshold_domain")
        return obj
    required = {"field", "scores"}
    if action == "wash_care":
        required.add("allowed_care_labels")
    if action == "fabric":
        required.add("excluded_fabric_labels")
    if not isinstance(obj, dict) or set(obj) != required or obj.get("field") != action:
        raise ValueError("field_schema")
    scores = obj["scores"]
    if not isinstance(scores, dict) or set(scores) != set(vocab[action]):
        raise ValueError("score_keys")
    score_alphabet = {-2, -1, 0, 2, 4}
    if not all(type(value) is int and value in score_alphabet for value in scores.values()):
        raise ValueError("score_domain")
    if action == "wash_care":
        labels = obj["allowed_care_labels"]
        if (not isinstance(labels, list) or not labels or len(labels) != len(set(labels))
                or not set(labels).issubset(set(ref.CARE))):
            raise ValueError("care_domain")
    if action == "fabric":
        labels = obj["excluded_fabric_labels"]
        if (not isinstance(labels, list) or len(labels) != len(set(labels))
                or not set(labels).issubset(set(vocab["fabric"]))):
            raise ValueError("excluded_fabric_domain")
    return obj


def _event_metadata(stdout):
    models, usage, thread_ids = set(), [], []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except Exception:
            continue
        if not isinstance(event, dict):
            continue
        for key in ("model", "model_id", "requested_model"):
            val = event.get(key)
            if isinstance(val, str):
                models.add(val)
        if event.get("type") == "thread.started" and event.get("thread_id"):
            thread_ids.append(event["thread_id"])
        if "usage" in event:
            usage.append(event["usage"])
    return sorted(models), thread_ids, usage


def _save_record(job_id, record):
    path = RECORDS / (job_id + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def _record_base(job):
    return {k: job[k] for k in ("job_id", "case_id", "profile_id", "menu_id", "stratum",
                                "query_action", "replicate", "kind")}


def _transport_failure(reason):
    with LOCK:
        STATE["transport_failures"] += 1
        STATE["consecutive_transport_failures"] += 1
        if STATE["consecutive_transport_failures"] >= 3:
            STATE["abort_reason"] = "three_consecutive_cli_failures"


def _transport_success():
    with LOCK:
        STATE["consecutive_transport_failures"] = 0


def _run_one(job, prompt, vocab, thresholds):
    with LOCK:
        abort = STATE["abort_reason"]
        elapsed = time.monotonic() - STATE["started"] if STATE["started"] else 0
        if not abort and elapsed >= CFG["total_wall_seconds"]:
            STATE["abort_reason"] = abort = "wall_budget"
        if abort:
            record = {**_record_base(job), "attempted": False, "valid": False,
                      "not_attempted_reason": abort}
            _save_record(job["job_id"], record)
            return record
        STATE["attempted"] += 1
        attempt_no = STATE["attempted"]

    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    ledger = RUN / "ATTEMPTS.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    attempt = {"job_id": job["job_id"], "attempt_number": attempt_no,
               "prompt_sha256": prompt_hash,
               "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "requested_model": CFG["requested_model"]}
    with LOCK:
        with ledger.open("a") as f:
            f.write(json.dumps(attempt, ensure_ascii=False) + "\n")
    prompt_path = RUN / "prompts" / (job["job_id"] + ".txt")
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt)
    response_path = RUN / "responses" / (job["job_id"] + ".txt")
    event_path = RUN / "events" / (job["job_id"] + ".jsonl")
    stderr_path = RUN / "events" / (job["job_id"] + ".stderr.txt")
    response_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.parent.mkdir(parents=True, exist_ok=True)
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="luna-policy-myntra-")).resolve()
    command = ["codex", "exec", "--model", CFG["requested_model"], "--ephemeral",
               "--ignore-user-config", "--sandbox", "read-only", "--skip-git-repo-check",
               "--json", "--output-last-message", str(response_path), "--cd", str(scratch), "-"]
    started = time.monotonic()
    base = {**_record_base(job), "attempted": True, "attempt_number": attempt_no,
            "prompt_sha256": prompt_hash, "requested_model": CFG["requested_model"]}
    try:
        completed = subprocess.run(command, input=prompt, text=True, capture_output=True,
                                   timeout=CFG["request_timeout_seconds"], check=False)
        event_path.write_text(completed.stdout)
        stderr_path.write_text(completed.stderr)
        models, thread_ids, usage = _event_metadata(completed.stdout)
        record = {**base, "exit_code": completed.returncode,
                  "event_sha256": sha256(event_path), "stderr_sha256": sha256(stderr_path),
                  "reported_model_strings": models, "thread_ids": thread_ids,
                  "usage_events": usage, "latency_seconds": time.monotonic() - started}
        allowed = {CFG["requested_model"], "gpt-6-luna"}
        if models and any(m not in allowed for m in models):
            with LOCK:
                STATE["abort_reason"] = "reported_model_mismatch"
            record.update(valid=False, error_class="reported_model_mismatch")
            _transport_failure("reported_model_mismatch")
        elif completed.returncode != 0:
            record.update(valid=False, error_class="codex_cli_exit",
                          error=f"exit_{completed.returncode}")
            _transport_failure("nonzero_exit")
        elif not response_path.is_file():
            record.update(valid=False, error_class="missing_final_response")
            _transport_failure("missing_final_response")
        else:
            content = response_path.read_text()
            record.update(content=content, response_sha256=sha256(response_path))
            try:
                parsed = parse_field_answer(job["query_action"], content, vocab, thresholds)
                record.update(valid=True, parsed={"value": parsed})
                _transport_success()
            except Exception as exc:
                record.update(valid=False, error_class=type(exc).__name__,
                              parse_error=str(exc)[:200])
                _transport_success()
    except subprocess.TimeoutExpired as exc:
        event_path.write_text(exc.stdout if isinstance(exc.stdout, str) else "")
        stderr_path.write_text("Codex invocation timed out\n")
        record = {**base, "valid": False, "error_class": "TimeoutExpired",
                  "event_sha256": sha256(event_path), "stderr_sha256": sha256(stderr_path),
                  "latency_seconds": time.monotonic() - started}
        _transport_failure("timeout")
    except Exception as exc:
        event_path.write_text("")
        stderr_path.write_text(f"{type(exc).__name__}: {exc}\n")
        record = {**base, "valid": False, "error_class": type(exc).__name__,
                  "error": str(exc)[:240], "event_sha256": sha256(event_path),
                  "stderr_sha256": sha256(stderr_path), "latency_seconds": time.monotonic() - started}
        _transport_failure("exception")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    _save_record(job["job_id"], record)
    return record


def run_phase(phase):
    frozen = verify_frozen()
    if phase not in {"smoke", "full"}:
        raise ValueError("phase must be smoke or full")
    jobs = read_rows(PRIVATE / "jobs.jsonl")
    profiles = read_rows(PRIVATE / "profiles.jsonl")
    vocab_all = read(PUBLIC / "vocabularies.json")
    source_cfg = read(LEGACY / "config.json")
    thresholds = source_cfg["purchase_thresholds"]
    if phase == "full":
        smoke = read(BASE / "SMOKE_RECEIPT.json")
        if smoke.get("transport_failures", 0) > 0 or smoke.get("model_mismatch", False):
            return {"status": "STOPPED_AFTER_SMOKE_TRANSPORT_FAILURE", "model_calls": 0,
                    "smoke_receipt": str(BASE / "SMOKE_RECEIPT.json")}
    smoke_profile = CFG["smoke_profile_id"]
    if phase == "smoke":
        profile_ids = [smoke_profile]
    else:
        profile_ids = [p["profile_id"] for p in profiles]
    selected = [j for j in jobs if j["profile_id"] in set(profile_ids)]
    if phase == "full":
        selected = jobs
    existing = {p.stem for p in RECORDS.glob("*.json")}
    attempted = {r["job_id"] for r in read_rows(RUN / "ATTEMPTS.jsonl")}
    pending = []
    for job in selected:
        if job["job_id"] in existing:
            continue
        if job["job_id"] in attempted:
            record = {**_record_base(job), "attempted": True, "valid": False,
                      "error_class": "attempted_without_terminal_record_no_retry"}
            _save_record(job["job_id"], record)
            existing.add(job["job_id"])
            continue
        pending.append(job)

    if phase == "smoke" and len(pending) != 12:
        raise RuntimeError(f"Smoke slice expects 12 new calls, found {len(pending)}")
    if phase == "full" and len(pending) + len(existing) < 96:
        raise RuntimeError("Full phase inventory is incomplete")

    RUN.mkdir(parents=True, exist_ok=True)
    STATE.update(started=time.monotonic(), attempted=0, transport_failures=0,
                 consecutive_transport_failures=0, abort_reason=None)
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    prompt_map = {x["job_id"]: x["prompt"] for x in read_rows(PROMPTS / "requests.jsonl")}
    profile_pool = {p["profile_id"]: p["pool_index"] for p in profiles}
    print(json.dumps({"status": "RUN_STARTED", "phase": phase,
                      "planned_new": len(pending), "concurrency": CFG["concurrency"]}), flush=True)
    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CFG["concurrency"]) as pool:
        future_map = {}
        for job in pending:
            future = pool.submit(_run_one, job, prompt_map[job["job_id"]],
                                 vocab_all[str(profile_pool[job["profile_id"]])], thresholds)
            future_map[future] = job
        for future in concurrent.futures.as_completed(future_map):
            job = future_map[future]
            try:
                result = future.result()
                summaries.append({"job_id": job["job_id"], "attempted": result.get("attempted"),
                                  "valid": result.get("valid"),
                                  "error": result.get("error_class")})
            except Exception as exc:
                summaries.append({"job_id": job["job_id"], "runner_exception": type(exc).__name__})
            print(json.dumps(summaries[-1], ensure_ascii=False), flush=True)

    all_records = [read(p) for p in sorted(RECORDS.glob("*.json"))]
    phase_attempted = sum(s.get("attempted") is True for s in summaries)
    phase_transport_failures = sum(s.get("error") in {
        "TimeoutExpired", "codex_cli_exit", "missing_final_response", "reported_model_mismatch"
    } for s in summaries)
    model_mismatch = any(r.get("error_class") == "reported_model_mismatch" for r in all_records)
    receipt = {
        "status": "PHASE_COMPLETED" if len(summaries) == len(pending) else "PHASE_INCOMPLETE",
        "phase": phase, "started_utc": started_utc,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "planned_total": len(jobs), "planned_phase_new": len(pending),
        "attempted_phase": phase_attempted, "valid_phase": sum(s.get("valid") is True for s in summaries),
        "transport_failures": phase_transport_failures,
        "model_mismatch": model_mismatch,
        "concurrency": CFG["concurrency"], "requested_model": CFG["requested_model"],
        "reported_model_strings": sorted({m for r in all_records for m in r.get("reported_model_strings", [])}),
        "abort_reason": STATE["abort_reason"],
        "records_present": len(all_records), "attempts_total": len(read_rows(RUN / "ATTEMPTS.jsonl")),
        "retries": 0, "summaries": summaries,
    }
    receipt_path = BASE / ("SMOKE_RECEIPT.json" if phase == "smoke" else "RUN_RECEIPT.json")
    write_json(receipt_path, receipt)
    print(json.dumps({"status": receipt["status"], "phase": phase,
                      "attempted": phase_attempted, "valid": receipt["valid_phase"],
                      "transport_failures": phase_transport_failures,
                      "records_present": len(all_records), "abort_reason": STATE["abort_reason"]}), flush=True)
    return receipt


def _case_trace(env, case, profile, prior, method, replicate, bank, vocab, thresholds):
    policy = engine.PublicPolicy(env, case["public_menu"], prior, method)
    trace, attempted_actions = [], []
    stopped = False
    failed_action = None
    exact_valid_answers = 0
    for budget in CFG["budgets"]:
        if budget > 0 and not stopped:
            action = policy.next_action()
            if action is None:
                stopped = True
                failed_action = "no_legal_action"
            else:
                attempted_actions.append(action)
                response = bank.get((action, replicate))
                if response is None or not response.get("valid"):
                    stopped = True
                    failed_action = action
                else:
                    answer = response["parsed"]["value"]
                    try:
                        # Validation is independent of the hidden profile's values.
                        validator = ref.PublicAgent(case["public_menu"], vocab, "fieldwise")
                        for prior_entry in policy.history:
                            validator.observe(prior_entry["action"], prior_entry["answer"])
                        validator.observe(action, answer)
                        policy.observe(action, answer)
                        exact_valid_answers += int(response.get("exact_profile_match", False))
                    except Exception:
                        stopped = True
                        failed_action = action
        recommendation, posterior_success = policy.predict()
        metrics = engine.episode_metrics(env, case["public_menu"]["items"], profile, recommendation)
        trace.append({
            "case_id": case["case_id"], "profile_id": profile["profile_id"],
            "stratum": case["stratum"], "menu_id": case["menu_id"],
            "replicate": replicate, "method": method, "budget": budget,
            "query_sequence": attempted_actions[:],
            "valid_query_sequence": [x["action"] for x in policy.history],
            "elicitation_units": len(attempted_actions), "dialogue_turns": len(attempted_actions),
            "answer_path_complete": not stopped,
            "failed_query_action": failed_action,
            "exact_profile_matches_observed": exact_valid_answers,
            "posterior_success_probability": posterior_success,
            **metrics,
        })
    return trace


def analyze():
    verify_frozen()
    cases_raw = read_rows(PRIVATE / "selected_cases.jsonl")
    profiles = {p["profile_id"]: p for p in read_rows(PRIVATE / "profiles.jsonl")}
    menus = {m["menu_id"]: m for m in read_rows(PUBLIC / "menus.jsonl")}
    vocab_all = read(PUBLIC / "vocabularies.json")
    prior_rows = read_rows(PRIVATE / "prior_profiles.jsonl")
    prior_by_pool = {pool: [p for p in prior_rows if p["pool_index"] == pool] for pool in range(3)}
    env = engine.load_environment(WORKTREE)
    all_response_records = {r["job_id"]: r for r in (read(p) for p in sorted(RECORDS.glob("*.json")))}
    answer_bank = {}
    field_quality = {}
    for job in read_rows(PRIVATE / "jobs.jsonl"):
        response = all_response_records.get(job["job_id"])
        profile = profiles[job["profile_id"]]
        action = job["query_action"]
        expected = ref.ReferenceUser(profile).answer(action)
        record = dict(response or {"job_id": job["job_id"], "valid": False,
                                   "error_class": "not_attempted_no_record", "attempted": False})
        exact = bool(record.get("valid") and canonical(record["parsed"]["value"]) == canonical(expected))
        record["exact_profile_match"] = exact
        answer_bank[(job["profile_id"], job["replicate"], action)] = record
        q = field_quality.setdefault(action, {"planned": 0, "attempted": 0, "valid": 0, "exact": 0})
        q["planned"] += 1
        q["attempted"] += int(record.get("attempted") is True)
        q["valid"] += int(record.get("valid") is True)
        q["exact"] += int(exact)

    traces = []
    for case_row in cases_raw:
        profile = profiles[case_row["profile_id"]]
        case = {**case_row, "public_menu": menus[case_row["menu_id"]]}
        prior = prior_by_pool[case_row["prior_pool_index"]]
        vocab = vocab_all[str(profile["pool_index"])]
        for replicate in (1, 2):
            bank = {(a, replicate): answer_bank[(profile["profile_id"], replicate, a)]
                    for a in CFG["query_actions"]}
            for method in CFG["methods"]:
                traces.extend(_case_trace(env, case, profile, prior, method, replicate, bank, vocab,
                                          read(LEGACY / "config.json")["purchase_thresholds"]))
    write_rows(RESULTS / "PAIRED_POLICY_TRACES.jsonl", traces)

    by_method_budget = {}
    for method in CFG["methods"]:
        by_method_budget[method] = {}
        for budget in CFG["budgets"]:
            rows = [r for r in traces if r["method"] == method and r["budget"] == budget]
            by_method_budget[method][str(budget)] = {
                "n": len(rows), "correct": sum(r["exact_decision_correct"] for r in rows),
                "accuracy": sum(r["exact_decision_correct"] for r in rows) / len(rows) if rows else None,
                "hard_violations": sum(r["hard_constraint_violation"] for r in rows),
                "false_purchases": sum(r["false_purchase_case"] for r in rows),
                "missed_buy": sum(r["reference_decision"] == "BUY" and not r["purchase_recall_case"] for r in rows),
                "failed_paths": sum(not r["answer_path_complete"] for r in rows),
                "mean_query_units": sum(r["elicitation_units"] for r in rows) / len(rows) if rows else None,
            }

    case_lookup = {(r["case_id"], r["replicate"], r["method"], r["budget"]): r for r in traces}
    selected_by_id = {c["case_id"]: c for c in cases_raw}
    strata_profiles = {}
    for c in cases_raw:
        strata_profiles.setdefault(c["stratum"], []).append(c["profile_id"])
    profile_ids = [c["profile_id"] for c in cases_raw]
    pairwise = {}
    bootstrap_reps = 10000
    for budget in CFG["budgets"]:
        pairwise[str(budget)] = {}
        for baseline in [m for m in CFG["methods"] if m != "decision_value"]:
            key_diffs = {}
            profile_diffs = {pid: [] for pid in profile_ids}
            wins = ties = losses = 0
            for case in cases_raw:
                for replicate in (1, 2):
                    dv = case_lookup[(case["case_id"], replicate, "decision_value", budget)]["exact_decision_correct"]
                    bl = case_lookup[(case["case_id"], replicate, baseline, budget)]["exact_decision_correct"]
                    diff = int(dv) - int(bl)
                    key_diffs[(case["case_id"], replicate)] = diff
                    profile_diffs[case["profile_id"]].append(diff)
                    wins += diff > 0
                    losses += diff < 0
                    ties += diff == 0
            cluster_mean = {pid: sum(vals) / len(vals) for pid, vals in profile_diffs.items()}
            observed = sum(cluster_mean.values()) / len(cluster_mean)
            rng = random.Random(20261105 + 100 * budget + len(baseline))
            samples = []
            for _ in range(bootstrap_reps):
                picked = []
                for stratum, ids in strata_profiles.items():
                    picked.extend(rng.choice(ids) for _ in range(len(ids)))
                samples.append(sum(cluster_mean[p] for p in picked) / len(picked))
            samples.sort()
            lo = samples[int(0.025 * bootstrap_reps)]
            hi = samples[int(0.975 * bootstrap_reps)]
            pairwise[str(budget)][baseline] = {
                "difference": observed, "cluster_bootstrap_95_ci": [lo, hi],
                "case_bank_wins": int(wins), "case_bank_ties": int(ties),
                "case_bank_losses": int(losses),
                "profile_clusters_win": sum(v > 0 for v in cluster_mean.values()),
                "profile_clusters_tie": sum(v == 0 for v in cluster_mean.values()),
                "profile_clusters_loss": sum(v < 0 for v in cluster_mean.values()),
                "profile_cluster_differences": cluster_mean,
            }

    answer_exact = sum(q["exact"] for q in field_quality.values())
    answer_valid = sum(q["valid"] for q in field_quality.values())
    run_receipt_path = BASE / "RUN_RECEIPT.json"
    smoke_receipt_path = BASE / "SMOKE_RECEIPT.json"
    summary = {
        "status": "ANALYZED_COMPLETE" if len(all_response_records) == 96 else "ANALYZED_INCOMPLETE",
        "requested_model": CFG["requested_model"],
        "reported_model_strings": sorted({m for r in all_response_records.values()
                                           for m in r.get("reported_model_strings", [])}),
        "unique_profiles": len(cases_raw), "response_bank_replicates": 2,
        "planned_calls": 96, "records_present": len(all_response_records),
        "attempted_calls": sum(r.get("attempted") is True for r in all_response_records.values()),
        "valid_answers": answer_valid, "exact_profile_field_matches": answer_exact,
        "field_answer_quality": field_quality,
        "budget_metrics": by_method_budget,
        "decision_value_pairwise": pairwise,
        "primary_budget": CFG["primary_budget"],
        "confidence_interval_note": "Stratified bootstrap resamples eight unique profile clusters within the four purposive strata; the two response-bank repeats travel with each profile. Intervals describe only this selected development panel.",
        "smoke_receipt": read(smoke_receipt_path) if smoke_receipt_path.exists() else None,
        "run_receipt": read(run_receipt_path) if run_receipt_path.exists() else None,
        "claim_limit": "Eight purposively selected synthetic personas; structured score elicitation; Codex CLI alias requested, backend not independently attested; not human evidence or independent confirmation.",
    }
    write_json(RESULTS / "ANALYSIS.json", summary)
    write_report(summary)
    return summary


def _pct(x):
    return "n/a" if x is None else f"{100*x:.1f}%"


def write_report(summary):
    methods = CFG["methods"]
    b = str(CFG["primary_budget"])
    lines = [
        "# Luna 模拟顾客下的四种提问策略比较",
        "",
        "## Material Passport",
        "",
        f"- 状态：`{summary['status']}`；请求模型：`{summary['requested_model']}`；Codex CLI：`{summary.get('run_receipt', {}).get('codex_cli_version', '0.166.0 (freeze observation)' ) if summary.get('run_receipt') else '0.166.0 (freeze observation)'}`。",
        "- 设计：8 个开发画像 × 2 个独立回答库；每个画像—维度回答调用一次并在四种策略间配对共享。最多 96 次 Luna 调用。",
        "- 四种策略：Fixed Order、Profile IG、Decision-Set IG、Decision Value；推荐方由原冻结 Python 策略实现，非 LLM agent。",
        "- 主要预算：5 个字段问题；完整预算 0–6 均保留。所有回答由全新的独立 Codex CLI 会话生成，重置对话历史。",
        "",
        "## 预算 5 的结果",
        "",
        "| 策略 | 正确推荐 | 准确率 | 无效/中断回答路径 | 硬约束违规 | 平均提问数 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method in methods:
        row = summary["budget_metrics"][method][b]
        lines.append(f"| {method} | {row['correct']}/{row['n']} | {_pct(row['accuracy'])} | {row['failed_paths']}/{row['n']} | {row['hard_violations']} | {row['mean_query_units']:.2f} |")
    lines += ["", "Decision Value 相对三个基线的画像簇配对差：", "",
              "| 基线 | 准确率差 | 画像簇 bootstrap 95% 区间 | 画像簇胜/平/负 | 案例—回答库胜/平/负 |",
              "|---|---:|---:|---:|---:|"]
    for baseline in [m for m in methods if m != "decision_value"]:
        row = summary["decision_value_pairwise"][b][baseline]
        ci = row["cluster_bootstrap_95_ci"]
        lines.append(f"| {baseline} | {100*row['difference']:+.1f} pp | [{100*ci[0]:+.1f}, {100*ci[1]:+.1f}] pp | {row['profile_clusters_win']}/{row['profile_clusters_tie']}/{row['profile_clusters_loss']} | {row['case_bank_wins']}/{row['case_bank_ties']}/{row['case_bank_losses']} |")
    lines += ["", "## 各预算准确率", "",
              "| 问题预算 | Fixed Order | Profile IG | Decision-Set IG | Decision Value | DV − Decision-Set IG (95% 区间) |",
              "|---:|---:|---:|---:|---:|---:|"]
    for budget in CFG["budgets"]:
        values = [summary["budget_metrics"][m][str(budget)]["accuracy"] for m in methods]
        comp = summary["decision_value_pairwise"][str(budget)]["decision_set_ig"]
        lo, hi = comp["cluster_bootstrap_95_ci"]
        lines.append(f"| {budget} | " + " | ".join(_pct(x) for x in values)
                     + f" | {100*comp['difference']:+.1f} pp [{100*lo:+.1f}, {100*hi:+.1f}] |")
    lines += ["", "## Luna 回答与运行完整性", "",
              f"计划 {summary['planned_calls']} 次，已有终态记录 {summary['records_present']} 条，实际调用 {summary['attempted_calls']} 次；解析有效 {summary['valid_answers']} 条，其中与隐藏固定画像逐字段完全一致 {summary['exact_profile_field_matches']} 条。",
              "",
              "| 问询维度 | 计划 | 调用 | 有效解析 | 与隐藏画像完全一致 |",
              "|---|---:|---:|---:|---:|"]
    for action in CFG["query_actions"]:
        q = summary["field_answer_quality"][action]
        lines.append(f"| {action} | {q['planned']} | {q['attempted']} | {q['valid']} | {q['exact']} |")
    lines += ["", "## 解释边界", "",
              "上一轮 Luna 模拟器在 BUY_TIED 行为屏幕中为 9/12，未达到预设门槛。本轮仍保留该负面结果；当前小样本是机制覆盖样本，不代表顾客总体。模型收到完整固定画像，只回答系统策略实际询问的单个字段；这不是自然发生的人类购物对话。两份回答库是同一批画像的重复测量，置信区间按画像聚类并按四个预设机制分层，不能外推为人群显著性。",
              "",
              "Luna 的最终购买选择未作为本轮结果；推荐策略根据只通过已问字段获得的信息做出商品/NO_BUY 决策，再由隐藏画像的确定性规则评分。因此这衡量的是策略在该模型回答过程下的决策表现，不是实际用户接受率。Codex CLI 请求了模型别名 `gpt-6-luna`；服务端权重身份及采样参数未独立证明。",
              "",
              "## 复现材料", "",
              "`FROZEN.json` 绑定了源数据、输入提示、程序、先验抽样及 CLI 版本。原始回答、事件流、错误日志和尝试账本位于 `artifacts/run/`；策略逐案轨迹见 `results/PAIRED_POLICY_TRACES.jsonl`；汇总见 `results/ANALYSIS.json`。"]
    (RESULTS / "REPORT_ZH.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "freeze", "verify", "smoke", "full", "analyze"])
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps(_copy_snapshot(), ensure_ascii=False))
    elif args.command == "freeze":
        print(json.dumps(freeze(), ensure_ascii=False))
    elif args.command == "verify":
        frozen = verify_frozen()
        print(json.dumps({"status": "FROZEN_HASHES_PASS", "files": len(frozen["files"]) }))
    elif args.command == "smoke":
        print(json.dumps(run_phase("smoke"), ensure_ascii=False))
    elif args.command == "full":
        print(json.dumps(run_phase("full"), ensure_ascii=False))
    elif args.command == "analyze":
        print(json.dumps(analyze(), ensure_ascii=False))


if __name__ == "__main__":
    main()
