from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

BASE = pathlib.Path(__file__).resolve().parent
WORKTREE = BASE.parents[1]
SOURCE = WORKTREE / "experiments/myntra_coverage_diag_v02_20261104"
LEGACY = WORKTREE / "experiments/myntra_preference_dev_v01_20261104"
sys.path[:0] = [str(LEGACY), str(SOURCE)]
import environment as ref
import qwen_smoke as transport
import diagnostic as source_diag

INPUT = BASE / "artifacts/input"
PUBLIC = INPUT / "public"
PRIVATE = INPUT / "private"
QWEN = BASE / "artifacts/qwen_reference"
RESULTS = BASE / "results"
RUN = BASE / "artifacts/luna_run"

LOCK = threading.Lock()
STATE = {"attempted": 0, "consecutive_failures": 0, "abort_reason": None,
         "start_monotonic": None}


def read(path):
    return json.loads(pathlib.Path(path).read_text())


def rows(path):
    path = pathlib.Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def dump(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def dump_rows(path, values):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in values))


def sha256(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def relative(path):
    return str(pathlib.Path(path).relative_to(BASE))


def _copy_source_snapshot():
    if INPUT.exists() and any(INPUT.rglob("*")):
        raise FileExistsError("Input snapshot already exists; preserve it")
    for folder in [PUBLIC, PRIVATE, QWEN]:
        folder.mkdir(parents=True, exist_ok=True)
    src_prep = SOURCE / "artifacts/prepared"
    selected = rows(src_prep / "evaluator_only/selected_cases.jsonl")
    profile_ids = {c["profile_id"] for c in selected}
    menu_ids = {c["menu_id"] for c in selected}
    profiles = [p for p in rows(src_prep / "private/profiles.jsonl") if p["profile_id"] in profile_ids]
    menus = [m for m in rows(src_prep / "public/menus.jsonl") if m["menu_id"] in menu_ids]
    original_jobs = rows(src_prep / "private/jobs.jsonl")
    selected_ids = {c["case_id"] for c in selected}
    jobs = [j for j in original_jobs if j["case_id"] in selected_ids]
    templates = read(src_prep / "private/request_templates.json")
    qwen_records = SOURCE / "artifacts/model_run/records"
    qwen_requests = SOURCE / "artifacts/model_run/requests"
    for job in jobs:
        shutil.copyfile(qwen_records / f"{job['job_id']}.json", QWEN / f"{job['job_id']}.json")
        request = qwen_requests / f"{job['job_id']}.json"
        if request.exists():
            (QWEN / "requests").mkdir(exist_ok=True)
            shutil.copyfile(request, QWEN / "requests" / request.name)
    dump_rows(PRIVATE / "selected_cases.jsonl", selected)
    dump_rows(PRIVATE / "profiles.jsonl", profiles)
    dump_rows(PRIVATE / "source_jobs.jsonl", jobs)
    dump(PRIVATE / "source_request_templates.json", {k: v for k, v in templates.items()
        if any(j["job_id"] == k for j in jobs)})
    dump_rows(PUBLIC / "menus.jsonl", menus)
    shutil.copyfile(src_prep / "public/vocabularies.json", PUBLIC / "vocabularies.json")
    shutil.copyfile(LEGACY / "SYSTEM_PROMPT_ZH.txt", INPUT / "SYSTEM_PROMPT_ZH.txt")
    qwen_receipt = read(SOURCE / "artifacts/model_run/RUN_RECEIPT.json")
    dump(INPUT / "SOURCE_RECEIPT.json", {
        "source_experiment": str(SOURCE), "qwen_run_receipt": qwen_receipt,
        "selected_case_ids": [c["case_id"] for c in selected],
        "source_freeze_sha256": sha256(SOURCE / "RUN_FREEZE.json"),
        "qwen_record_count_copied": len(list(QWEN.glob("*.json"))),
        "qwen_request_count_copied": len(list((QWEN / "requests").glob("*.json"))),
        "selection_was_stratified_on_reference": True,
        "reserved_products_included": False
    })


def make_luna_jobs():
    source_jobs = rows(PRIVATE / "source_jobs.jsonl")
    jobs = []
    by_case = {}
    for job in source_jobs:
        by_case.setdefault(job["case_id"], {})[job["job_id"].rsplit("__", 1)[-1]] = job
    for case_id, parts in by_case.items():
        original = parts["base"]
        for i in range(1, 4):
            jobs.append({"job_id": f"{case_id}__base_{i}", "case_id": case_id,
                         "profile_id": original["profile_id"], "menu_id": original["menu_id"],
                         "kind": "choice", "variant": f"base_{i}", "view": "base",
                         "qwen_job_id": ["base", "repeat_same", "repeat_new"][i - 1]})
        for variant in ["reverse", "alias", "care_A", "care_B", "disclosure"]:
            src = parts[variant]
            jobs.append({"job_id": f"{case_id}__{variant}", "case_id": case_id,
                         "profile_id": src["profile_id"], "menu_id": src["menu_id"],
                         "kind": src["kind"], "variant": variant,
                         **({"view": src["view"]} if "view" in src else {}),
                         **({"frame": src["frame"]} if "frame" in src else {}),
                         "qwen_job_id": src["job_id"]})
        src = parts["dialogue"]
        jobs.append({"job_id": f"{case_id}__dialogue", "case_id": case_id,
                     "profile_id": src["profile_id"], "menu_id": src["menu_id"],
                     "kind": "dialogue_choice", "variant": "dialogue", "view": "base",
                     "dependency": f"{case_id}__disclosure", "qwen_job_id": src["job_id"]})
    return jobs


def system_text(profile):
    return (INPUT / "SYSTEM_PROMPT_ZH.txt").read_text().replace(
        "{{PROFILE}}", json.dumps(ref.private_preferences(profile), ensure_ascii=False, sort_keys=True))


def messages_for(job, profile, menu, actual_disclosure=None, recommendation=None):
    if job["kind"] == "dialogue_choice":
        if actual_disclosure is None or recommendation is None:
            raise ValueError("Dialogue prompt requires actual disclosure and recommendation")
        mapping = {x["product_id"]: x["option_id"] for x in transport.shown_options(menu)}
        suggestion = "建议本次不购买" if recommendation["decision"] == "NO_BUY" else "推荐商品 " + mapping[recommendation["selected_id"]]
        final_question = (transport.menu_text(menu) + "\n推荐系统依据你刚才的披露：" + suggestion
                          + "。请依据你原本的画像自己决定，你可以选其他商品，也可以不买。\n" + transport.CHOICE_SCHEMA)
        return [{"role": "system", "content": system_text(profile)},
                {"role": "user", "content": transport.DISCLOSURE_QUESTION},
                {"role": "assistant", "content": actual_disclosure},
                {"role": "user", "content": final_question}]
    return transport.independent_messages(profile, menu, job)


def prompt_from_messages(messages):
    sys_text = messages[0]["content"]
    conv = []
    for msg in messages[1:]:
        role = {"user": "顾客收到的问题", "assistant": "顾客先前的回答"}[msg["role"]]
        conv.append(f"【{role}】\n{msg['content']}")
    return ("你正在执行一项模拟顾客任务。请把下面的顾客画像指令作为本轮角色规则，"
            "只依据给出的画像和商家标签回答最后的问题。不要调用工具、浏览文件或添加解释；"
            "按顾客指令要求输出。\n\n【固定顾客画像与行为规则】\n" + sys_text
            + "\n\n【本轮对话】\n" + "\n\n".join(conv) + "\n")


def prepare():
    if (BASE / "PREPARED.json").exists():
        raise FileExistsError("Prepared inputs already exist; preserve them")
    _copy_source_snapshot()
    jobs = make_luna_jobs()
    if len(jobs) != 72 or len({j["job_id"] for j in jobs}) != 72:
        raise ValueError("Expected exactly 72 unique jobs")
    dump_rows(PRIVATE / "jobs.jsonl", jobs)
    profiles = {p["profile_id"]: p for p in rows(PRIVATE / "profiles.jsonl")}
    menus = {m["menu_id"]: m for m in rows(PUBLIC / "menus.jsonl")}
    templates = {}
    for job in jobs:
        if job["kind"] == "dialogue_choice":
            templates[job["job_id"]] = {"requires_actual_disclosure": True}
        else:
            messages = messages_for(job, profiles[job["profile_id"]], menus[job["menu_id"]])
            templates[job["job_id"]] = {"messages": messages, "prompt": prompt_from_messages(messages)}
    dump(PRIVATE / "prompt_templates.json", templates)
    receipt = {"status": "READY", "profiles": len(profiles), "menus": len(menus),
               "cases": len(rows(PRIVATE / "selected_cases.jsonl")), "planned_jobs": len(jobs),
               "model_calls": 0, "reserved_products": 0,
               "identical_base_prompt_groups": 8,
               "qwen_records_copied": len(list(QWEN.glob("*.json")))}
    dump(BASE / "PREPARED.json", receipt)
    return receipt


def freeze():
    freeze_path = BASE / "FROZEN_CORRECTED.json"
    if freeze_path.exists():
        raise FileExistsError("Freeze already exists")
    files = [BASE / x for x in ["config.json", "PROTOCOL.md", "luna_simulator.py", "test_luna_simulator.py", "PREPARED.json"]]
    files += [p for root in [INPUT] for p in root.rglob("*") if p.is_file()]
    # Freeze the exact historical implementation used for prompt construction and scoring.
    source_files = [SOURCE / x for x in ["diagnostic.py", "analyze.py", "config.json", "RUN_FREEZE.json"]]
    source_files += [LEGACY / x for x in ["environment.py", "qwen_smoke.py", "SYSTEM_PROMPT_ZH.txt"]]
    manifest = {relative(p): sha256(p) for p in sorted(files)}
    manifest.update({"EXTERNAL::" + str(p): sha256(p) for p in sorted(source_files)})
    dump(freeze_path, {"status": "FROZEN_PRE_INFERENCE_REVISION_0_1_1", "files": manifest,
         "sha256_scope": "all protocol/config/code/input/Qwen reference records and prompt templates; plus source code dependencies"})
    return {"status": "FROZEN_PRE_INFERENCE_REVISION_0_1_1", "files": len(manifest)}


def verify_frozen():
    freeze_path = BASE / "FROZEN_CORRECTED.json"
    if not freeze_path.exists():
        freeze_path = BASE / "FROZEN.json"
    frozen = read(freeze_path)["files"]
    for path, expected in frozen.items():
        if path.startswith("EXTERNAL::"):
            target = pathlib.Path(path.removeprefix("EXTERNAL::"))
        else:
            target = BASE / path
        if not target.exists() or sha256(target) != expected:
            raise ValueError("Frozen dependency mismatch: " + path)


def reject_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate_json_key")
        out[k] = v
    return out


def parse_luna(kind, text, shown, vocab):
    if not isinstance(text, str):
        raise ValueError("content_type")
    raw = text.strip()
    fenced = False
    if raw.startswith("```"):
        m = re.fullmatch(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", raw, re.I)
        if not m:
            raise ValueError("incomplete_fence")
        raw, fenced = m.group(1), True
    obj = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    if kind in ["choice", "dialogue_choice"]:
        if not isinstance(obj, dict) or set(obj) != {"decision", "selected_id"}:
            raise ValueError("choice_schema")
        valid_ids = {x["option_id"] for x in shown}
        if obj["decision"] == "NO_BUY":
            if obj["selected_id"] is not None:
                raise ValueError("no_buy_must_be_null")
        elif obj["decision"] == "BUY":
            if not isinstance(obj["selected_id"], str) or obj["selected_id"] not in valid_ids:
                raise ValueError("unknown_option")
        else:
            raise ValueError("unknown_decision")
    elif kind == "care":
        if not isinstance(obj, dict) or set(obj) != {"allowed_care_labels"}:
            raise ValueError("care_schema")
        values = obj["allowed_care_labels"]
        if (not isinstance(values, list) or not values or not all(isinstance(x, str) for x in values)
                or len(values) != len(set(values)) or not set(values).issubset(ref.CARE)):
            raise ValueError("care_domain")
    elif kind == "disclosure":
        ref.validate_disclosure(obj, vocab)
    return {"value": obj, "fenced": fenced}


def _event_metadata(stdout):
    models, usage, thread_ids = set(), [], []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except Exception:
            continue
        if isinstance(event, dict):
            for key in ["model", "model_id", "requested_model"]:
                value = event.get(key)
                if isinstance(value, str):
                    models.add(value)
            if event.get("type") == "thread.started" and event.get("thread_id"):
                thread_ids.append(event["thread_id"])
            if "usage" in event:
                usage.append(event["usage"])
    return sorted(models), thread_ids, usage


def _log_attempt(job, prompt, output_path):
    with LOCK:
        STATE["attempted"] += 1
        number = STATE["attempted"]
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    ledger = BASE / "artifacts/luna_run/ATTEMPTS.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    item = {"job_id": job["job_id"], "attempt_number": number,
            "prompt_sha256": digest, "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "requested_model": read(BASE / "config.json")["requested_model"]}
    with LOCK:
        with ledger.open("a") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    prompt_path = BASE / "artifacts/luna_run/prompts" / (job["job_id"] + ".txt")
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt)
    return digest, number


def _should_abort():
    cfg = read(BASE / "config.json")
    with LOCK:
        if STATE["abort_reason"]:
            return STATE["abort_reason"]
        if time.monotonic() - STATE["start_monotonic"] >= cfg["total_wall_seconds"]:
            STATE["abort_reason"] = "wall_budget"
            return STATE["abort_reason"]
        return None


def _record(job, **kwargs):
    row = {"job_id": job["job_id"], "case_id": job["case_id"], "profile_id": job["profile_id"],
           "menu_id": job["menu_id"], "kind": job["kind"], "variant": job["variant"],
           "attempted": False, "valid": False}
    row.update(kwargs)
    dump(BASE / "artifacts/luna_run/records" / (job["job_id"] + ".json"), row)
    return row


def _run_one(job, prompt, shown, vocab):
    reason = _should_abort()
    if reason:
        return _record(job, not_attempted_reason=reason)
    cfg = read(BASE / "config.json")
    outdir = BASE / "artifacts/luna_run"
    request_hash, attempt_no = _log_attempt(job, prompt, outdir / "responses" / (job["job_id"] + ".txt"))
    response_path = outdir / "responses" / (job["job_id"] + ".txt")
    event_path = outdir / "events" / (job["job_id"] + ".jsonl")
    error_path = outdir / "events" / (job["job_id"] + ".stderr.txt")
    response_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.parent.mkdir(parents=True, exist_ok=True)
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="luna-myntra-")).resolve()
    command = ["codex", "exec", "--model", cfg["requested_model"], "--ephemeral",
               "--ignore-user-config", "--sandbox", "read-only", "--skip-git-repo-check",
               "--json", "--output-last-message", str(response_path), "--cd", str(scratch), "-"]
    started = time.monotonic()
    try:
        completed = subprocess.run(command, input=prompt, text=True, capture_output=True,
                                   timeout=cfg["request_timeout_seconds"], check=False)
        event_path.write_text(completed.stdout)
        error_path.write_text(completed.stderr)
        models, thread_ids, usage = _event_metadata(completed.stdout)
        result = {"attempted": True, "attempt_number": attempt_no, "prompt_sha256": request_hash,
                  "exit_code": completed.returncode, "event_sha256": sha256(event_path),
                  "stderr_sha256": sha256(error_path), "requested_model": cfg["requested_model"],
                  "reported_model_strings": models, "thread_ids": thread_ids,
                  "usage_events": usage, "latency_seconds": time.monotonic() - started}
        if completed.returncode != 0:
            raise RuntimeError("codex_cli_exit_" + str(completed.returncode))
        if models and any(x not in {cfg["requested_model"], "gpt-6-luna"} for x in models):
            with LOCK:
                STATE["abort_reason"] = "reported_model_mismatch"
            raise RuntimeError("reported_model_mismatch")
        if not response_path.exists():
            raise RuntimeError("missing_final_response")
        content = response_path.read_text()
        result["content"] = content
        result["response_sha256"] = sha256(response_path)
        result["parsed"] = parse_luna(job["kind"], content, shown, vocab)
        result["valid"] = True
        with LOCK:
            STATE["consecutive_failures"] = 0
    except subprocess.TimeoutExpired as exc:
        event_path.write_text(exc.stdout if isinstance(exc.stdout, str) else "")
        error_path.write_text("Codex invocation timed out\n")
        result = {"attempted": True, "attempt_number": attempt_no, "prompt_sha256": request_hash,
                  "error_class": "TimeoutExpired", "latency_seconds": time.monotonic() - started}
        _count_failure()
    except Exception as exc:
        if "result" not in locals():
            result = {"attempted": True, "attempt_number": attempt_no, "prompt_sha256": request_hash,
                      "error_class": type(exc).__name__, "error": str(exc)[:240],
                      "latency_seconds": time.monotonic() - started}
        else:
            result.update(error_class=type(exc).__name__, error=str(exc)[:240])
        if not result.get("valid"):
            _count_failure()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if result.get("valid"):
        return _record(job, **result)
    return _record(job, **result)


def _count_failure():
    cfg = read(BASE / "config.json")
    with LOCK:
        STATE["consecutive_failures"] += 1
        if STATE["consecutive_failures"] >= cfg["abort_after_consecutive_cli_failures"]:
            STATE["abort_reason"] = "consecutive_cli_failures"


def _case_worker(case_id, jobs_by_case, profiles, menus, vocabularies):
    jobs = jobs_by_case[case_id]
    job_by_id = {j["job_id"]: j for j in jobs}
    finished = {}
    independent = [j for j in jobs if j["kind"] != "dialogue_choice"]
    for job in independent:
        templates = read(PRIVATE / "prompt_templates.json")
        prompt = templates[job["job_id"]]["prompt"]
        menu = menus[job["menu_id"]]
        shown = transport.shown_options(menu, job.get("view", "base"))
        record = _run_one(job, prompt, shown, vocabularies[str(menu["pool_index"])])
        finished[job["job_id"]] = record
    dialogue = next(j for j in jobs if j["kind"] == "dialogue_choice")
    dependency = finished[dialogue["dependency"]]
    if not dependency.get("valid"):
        finished[dialogue["job_id"]] = _record(dialogue, not_attempted_reason="invalid_disclosure_dependency")
    elif _should_abort():
        finished[dialogue["job_id"]] = _record(dialogue, not_attempted_reason=_should_abort())
    else:
        disclosure_content = dependency["content"]
        disclosure = dependency["parsed"]["value"]
        menu = menus[dialogue["menu_id"]]
        vocab = vocabularies[str(menu["pool_index"])]
        agent = ref.PublicAgent(menu, vocab, "ask_all")
        agent.observe("ASK_ALL", disclosure)
        recommendation = agent.finish()
        messages = messages_for(dialogue, profiles[dialogue["profile_id"]], menu,
                                disclosure_content, recommendation)
        prompt = prompt_from_messages(messages)
        shown = transport.shown_options(menu)
        result = _run_one(dialogue, prompt, shown, vocab)
        result["public_recommendation"] = recommendation
        dump(BASE / "artifacts/luna_run/records" / (dialogue["job_id"] + ".json"), result)
        finished[dialogue["job_id"]] = result
    return {"case_id": case_id, "completed_records": len(finished),
            "attempted": sum(r.get("attempted", False) for r in finished.values()),
            "valid": sum(r.get("valid", False) for r in finished.values())}


def run():
    verify_frozen()
    if RUN.exists():
        raise FileExistsError("A Luna run already exists; no retry or overwrite")
    RUN.mkdir(parents=True)
    cfg = read(BASE / "config.json")
    jobs = rows(PRIVATE / "jobs.jsonl")
    cases = rows(PRIVATE / "selected_cases.jsonl")
    profiles = {p["profile_id"]: p for p in rows(PRIVATE / "profiles.jsonl")}
    menus = {m["menu_id"]: m for m in rows(PUBLIC / "menus.jsonl")}
    vocabularies = read(PUBLIC / "vocabularies.json")
    jobs_by_case = {}
    for job in jobs:
        jobs_by_case.setdefault(job["case_id"], []).append(job)
    for case_id in jobs_by_case:
        jobs_by_case[case_id].sort(key=lambda j: ["choice", "care", "disclosure", "dialogue_choice"].index(
            "dialogue_choice" if j["kind"] == "dialogue_choice" else "care" if j["kind"] == "care" else "disclosure" if j["kind"] == "disclosure" else "choice"))
    dump(RUN / "RUN_STARTED.json", {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
         "planned_jobs": len(jobs), "requested_model": cfg["requested_model"],
         "codex_cli_version": cfg["codex_cli_version"], "concurrency": cfg["concurrency"],
         "retries": 0, "model_calls_before_run": 0})
    STATE["start_monotonic"] = time.monotonic()
    print(json.dumps({"status": "RUN_STARTED", "planned": len(jobs), "concurrency": cfg["concurrency"]}), flush=True)
    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg["concurrency"]) as pool:
        futures = [pool.submit(_case_worker, c["case_id"], jobs_by_case, profiles, menus, vocabularies)
                   for c in cases]
        for future in concurrent.futures.as_completed(futures):
            try:
                summary = future.result()
            except Exception as exc:
                summary = {"error_class": type(exc).__name__, "error": str(exc)[:200]}
            summaries.append(summary)
            print(json.dumps(summary), flush=True)
    records = [read(p) for p in sorted((RUN / "records").glob("*.json"))]
    receipt = {"status": "RUN_COMPLETED", "planned": len(jobs),
               "attempted": sum(x.get("attempted", False) for x in records),
               "valid": sum(x.get("valid", False) for x in records),
               "case_count": len(cases), "model_calls": sum(x.get("attempted", False) for x in records),
               "requested_model": cfg["requested_model"],
               "reported_model_strings": sorted({m for x in records for m in x.get("reported_model_strings", [])}),
               "wall_seconds": time.monotonic() - STATE["start_monotonic"],
               "abort_reason": STATE["abort_reason"], "retries": 0,
               "record_count": len(records), "case_summaries": summaries}
    dump(RUN / "RUN_RECEIPT.json", receipt)
    print(json.dumps(receipt), flush=True)


def canonical(parsed, shown):
    value = parsed["value"]
    mapping = {x["option_id"]: x["product_id"] for x in shown}
    return {"decision": value["decision"],
            "selected_id": mapping[value["selected_id"]] if value["selected_id"] is not None else None}


def same_preferences(a, b):
    return (a["soft"] == b["soft"] and a["purchase_threshold"] == b["purchase_threshold"]
            and set(a["hard"]["allowed_care_labels"]) == set(b["hard"]["allowed_care_labels"])
            and set(a["hard"]["excluded_fabric_labels"]) == set(b["hard"]["excluded_fabric_labels"]))


def analyze_model(records, jobs, selected, profiles, menus, vocabularies, is_qwen=False):
    by_job = {r["job_id"]: r for r in records}
    evaluated = []
    for job in jobs:
        record = by_job.get(job["job_id"], {"attempted": False, "valid": False,
                                              "not_attempted_reason": "missing_record"})
        case = selected[job["case_id"]]
        profile = profiles[job["profile_id"]]
        menu = menus[job["menu_id"]]
        row = {"job_id": job["job_id"], "case_id": job["case_id"],
               "profile_id": job["profile_id"], "stratum": case["stratum"],
               "kind": job["kind"], "variant": job["variant"],
               "planned": True, "attempted": record.get("attempted", False),
               "valid": record.get("valid", False), "correct": False,
               "not_attempted_reason": record.get("not_attempted_reason"),
               "error_class": record.get("error_class"), "validation_error": record.get("error")}
        if job["kind"] in ["choice", "dialogue_choice"]:
            reference = case["reference"]
            row.update(decision_correct=False, hard_violation=None,
                       reference_decision=reference["decision"])
            if record.get("valid"):
                shown = transport.shown_options(menu, job.get("view", "base"))
                choice = canonical(record["parsed"], shown)
                row.update(canonical_choice=choice,
                           correct=ref.score_decision(choice, reference),
                           decision_correct=choice["decision"] == reference["decision"])
                if choice["decision"] == "BUY":
                    row["hard_violation"] = choice["selected_id"] not in reference["feasible_ids"]
        elif job["kind"] == "care":
            row["correct"] = bool(record.get("valid") and set(record["parsed"]["value"]["allowed_care_labels"])
                                  == set(profile["hard"]["allowed_care_labels"]))
        elif job["kind"] == "disclosure":
            row["correct"] = bool(record.get("valid") and same_preferences(record["parsed"]["value"], ref.private_preferences(profile)))
        evaluated.append(row)

    def count(group):
        return {"planned": len(group), "attempted": sum(x["attempted"] for x in group),
                "valid": sum(x["valid"] for x in group), "correct": sum(x["correct"] for x in group)}
    choices = [x for x in evaluated if x["kind"] in ["choice", "dialogue_choice"]]
    by_stratum = {}
    for stratum in ["BUY_UNIQUE", "BUY_TIED", "NO_BUY_FEASIBLE", "NO_BUY_INFEASIBLE"]:
        group = [x for x in choices if x["stratum"] == stratum]
        by_stratum[stratum] = count(group)
        by_stratum[stratum]["decision_correct"] = sum(x["decision_correct"] for x in group)
    by_kind = {k: count([x for x in evaluated if x["kind"] == k])
               for k in ["choice", "care", "disclosure", "dialogue_choice"]}
    profiles_by_case = {}
    for case_id in selected:
        g = [x for x in evaluated if x["case_id"] == case_id and x["kind"] == "choice"]
        corrects = [x for x in g if x["valid"]]
        profiles_by_case[case_id] = {"base_choice_count": len(g), "valid_base": len(corrects),
            "all_valid_base_same_action": len(corrects) == 3 and len({json.dumps(x["canonical_choice"], sort_keys=True) for x in corrects}) == 1,
            "base_choices": [x.get("canonical_choice") for x in g]}
    valid = sum(x["valid"] for x in evaluated)
    summary = {"planned": len(jobs), "attempted": sum(x["attempted"] for x in evaluated),
               "valid": valid, "invalid_attempted": sum(x["attempted"] and not x["valid"] for x in evaluated),
               "not_attempted": sum(not x["attempted"] for x in evaluated),
               "choice_actions_correct": sum(x["correct"] for x in choices),
               "choice_actions_planned": len(choices),
               "choice_decisions_correct": sum(x["decision_correct"] for x in choices),
               "by_kind": by_kind, "by_stratum": by_stratum,
               "hard_violations": sum(x["hard_violation"] is True for x in choices),
               "valid_buy_selections": sum(x.get("canonical_choice", {}).get("decision") == "BUY" for x in choices),
               "base_repeat_stability": profiles_by_case,
               "evaluated_rows": evaluated}
    cfg = read(BASE / "config.json")
    gates = {"valid_fraction": valid >= math.ceil(cfg["minimum_valid_fraction"] * len(jobs)),
             "care_accuracy": by_kind["care"]["correct"] >= math.ceil(cfg["minimum_care_accuracy"] * by_kind["care"]["planned"]),
             "full_disclosure": by_kind["disclosure"]["correct"] >= math.ceil(cfg["minimum_full_disclosure_accuracy"] * by_kind["disclosure"]["planned"]),
             "no_hard_violation": summary["hard_violations"] <= cfg["maximum_selected_hard_violations"]}
    for s, value in by_stratum.items():
        gates["action_" + s] = value["correct"] >= math.ceil(cfg["minimum_action_accuracy_per_stratum"] * value["planned"])
    summary["readiness_screens"] = gates
    summary["readiness"] = "GO_TO_DEV_METHOD_INTEGRATION_ONLY" if all(gates.values()) else "REVISE_SIMULATOR_OR_PROTOCOL"
    summary["failed_screens"] = [k for k, v in gates.items() if not v]
    return summary


def analyze():
    verify_frozen()
    cfg = read(BASE / "config.json")
    jobs = rows(PRIVATE / "jobs.jsonl")
    selected_rows = rows(PRIVATE / "selected_cases.jsonl")
    selected = {x["case_id"]: x for x in selected_rows}
    profiles_list = rows(PRIVATE / "profiles.jsonl")
    profiles = {x["profile_id"]: x for x in profiles_list}
    menus_list = rows(PUBLIC / "menus.jsonl")
    menus = {x["menu_id"]: x for x in menus_list}
    vocab = read(PUBLIC / "vocabularies.json")
    luna_records = [read(p) for p in sorted((RUN / "records").glob("*.json"))] if RUN.exists() else []
    luna = analyze_model(luna_records, jobs, selected, profiles, menus, vocab)
    qwen_records = [read(p) for p in sorted(QWEN.glob("*.json"))]
    src_jobs = rows(PRIVATE / "source_jobs.jsonl")
    # Score the exact historical Qwen task records against the same private references.
    qwen_selected_jobs = [{**j, "variant": j.get("variant", j["kind"])} for j in src_jobs]
    qwen_records = [dict(r, valid=bool(r.get("valid"))) for r in qwen_records]
    qwen = analyze_model(qwen_records, qwen_selected_jobs, selected, profiles, menus, vocab, is_qwen=True)
    report = {"status": "LUNA_DIAGNOSTIC_ANALYZED", "requested_model": cfg["requested_model"],
              "codex_cli_version": cfg["codex_cli_version"], "luna": luna, "qwen_reference": qwen,
              "claim_limit": "Eight reference-stratified synthetic development profiles; Codex-CLI-mediated Luna; not human behavior, population performance, or an adaptive-method comparison.",
              "reserved_products_used": 0, "training_runs": 0}
    dump(RESULTS / "ANALYSIS.json", report)
    dump_rows(RESULTS / "LUNA_ROWS.jsonl", luna["evaluated_rows"])
    dump_rows(RESULTS / "QWEN_REFERENCE_ROWS.jsonl", qwen["evaluated_rows"])
    write_report(report)
    return report


def write_report(report):
    luna, qwen = report["luna"], report["qwen_reference"]
    lines = ["# Luna 模拟顾客诊断", "", "本报告是开发阶段的机制诊断，不是推荐方法比较，也不代表真人。",
             "8个画像按四种参考决策机制分层选择；每类2个画像。保留商品没有进入输入。",
             "Luna通过 Codex CLI 的 `gpt-6-luna` 模型名请求。CLI 没有暴露与 Qwen 相同的温度、top-p、seed 或原始 Chat Completions 协议，且没有独立权重/后端身份证明，因此这是调用路径诊断，不是严格控制的模型能力比较。", "",
             "## 完成情况", "",
             f"Luna：计划 {luna['planned']}，尝试 {luna['attempted']}，有效 {luna['valid']}；训练 0 次、保留商品 0 件。",
             f"Qwen历史参照：计划 {qwen['planned']}，尝试 {qwen['attempted']}，有效 {qwen['valid']}。Qwen的种子和采样参数与Luna CLI不同。", "",
             "## 结果", "",
             "|模型|动作正确|购买决策正确|硬约束违规|画像披露|洗护回答|",
             "|---|---:|---:|---:|---:|---:|"]
    def acc(summary, key):
        x = summary["by_kind"][key]
        return f"{x['correct']}/{x['planned']}"
    for name, summary in [("Luna", luna), ("Qwen（历史）", qwen)]:
        lines.append(f"|{name}|{summary['choice_actions_correct']}/{summary['choice_actions_planned']}|"
                     f"{summary['choice_decisions_correct']}/{summary['choice_actions_planned']}|"
                     f"{summary['hard_violations']}|{acc(summary, 'disclosure')}|{acc(summary, 'care')}|")
    lines += ["", "|参考机制|计划动作|Luna正确|Qwen正确|", "|---|---:|---:|---:|"]
    for s in ["BUY_UNIQUE", "BUY_TIED", "NO_BUY_FEASIBLE", "NO_BUY_INFEASIBLE"]:
        lines.append(f"|{s}|{luna['by_stratum'][s]['planned']}|{luna['by_stratum'][s]['correct']}|{qwen['by_stratum'][s]['correct']}|")
    stable = sum(x["all_valid_base_same_action"] for x in luna["base_repeat_stability"].values())
    comparable = sum(x["valid_base"] == 3 for x in luna["base_repeat_stability"].values())
    lines += ["", f"三次同文本独立调用中，{comparable}/8个画像的三次结果全部有效，其中{stable}/8个画像的决策与商品都完全一致。",
              "", "## 预设屏幕", "",
              f"Luna判定：`{luna['readiness']}`。未通过：{', '.join(luna['failed_screens']) if luna['failed_screens'] else '无'}。",
              "该门槛只决定能否进入后续方法集成开发；即使全部通过，也不表示自适应方法优于基线。",
              "", "## 解释边界", "",
              "该样本刻意覆盖买唯一最优、买并列最优、存在可买但不值得买、没有可买商品四类机制，不能估计真实购物者的购买率。重复调用是同一画像的重复测量，不是新增独立用户。",
              "Qwen与Luna的差异同时混有模型、服务协议、采样控制和Codex代理系统差异，不作因果归因。成功披露画像或接受程序推荐，也不等于验证了真实用户偏好，更不等于方法优势。",
              "", "完整逐条记录见 `ANALYSIS.json`、`LUNA_ROWS.jsonl`、`QWEN_REFERENCE_ROWS.jsonl`；原始请求/响应与 CLI 事件保存在 `artifacts/luna_run/`。", ""]
    (RESULTS / "REPORT_ZH.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "freeze", "verify", "run", "analyze"])
    args = parser.parse_args()
    if args.mode == "prepare":
        print(json.dumps(prepare(), ensure_ascii=False))
    elif args.mode == "freeze":
        print(json.dumps(freeze(), ensure_ascii=False))
    elif args.mode == "verify":
        verify_frozen()
        print("FROZEN_DEPENDENCIES_VERIFIED")
    elif args.mode == "run":
        run()
    else:
        result = analyze()
        print(json.dumps({"status": result["status"], "luna": {k: result["luna"][k] for k in ["planned", "attempted", "valid", "by_stratum", "by_kind", "readiness", "failed_screens"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
