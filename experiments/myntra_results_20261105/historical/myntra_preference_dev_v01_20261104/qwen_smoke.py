"""Bounded local-model observations; private outcomes never enter the public agent."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import time
import urllib.error
import urllib.request

import environment as e

BASE = e.BASE
PREP = BASE / "artifacts/prepared"
CHOICE_SCHEMA = ('只输出恰含decision和selected_id两个键的JSON。decision只能为"BUY"或"NO_BUY"；'
                 '购买时selected_id为一个当前商品代号，不买时selected_id为JSON null。')
CARE_SCHEMA = ('只输出JSON：{"allowed_care_labels":["原始标签"]}。'
               '只使用dry clean、hand wash、machine wash，列出全部愿意接受的标签，不重复。')
DISCLOSURE_QUESTION = ('请完整披露已设定的hard、soft和purchase_threshold，保持全部原始字段、'
                       '标签及整数分数，包括0分标签，不添加其他键。只输出JSON，三个顶层键恰为'
                       'hard、soft、purchase_threshold。hard包含allowed_care_labels、excluded_fabric_labels；'
                       'soft包含scores，scores包含neckline、sleeve_length、fabric、wash_care、pattern。')
CARE_QUESTIONS = {
    "A": "对商家建议的洗护方式，你愿意接受哪些类别？",
    "B": "分别考虑商家建议dry clean、hand wash、machine wash的衣物：哪些洗护建议是你愿意接受的？",
}


def shown_options(menu, view="base"):
    size = len(menu["items"])
    shown = [{"option_id": f"C{(i + 3) % size if view == 'alias' else i:02d}",
              "product_id": item["product_id"], "attributes": item["attributes"]}
             for i, item in enumerate(menu["items"])]
    return list(reversed(shown)) if view == "reverse" else shown


def menu_text(menu, view="base"):
    public = [{"option_id": x["option_id"], "attributes": x["attributes"]}
              for x in shown_options(menu, view)]
    return (f"当前商品类别：{menu['gender']} / {menu['category']}。以下只有商家给出的五项标签；"
            "顺序不表示推荐优先级，代号不代表商品质量。\n"
            + json.dumps(public, ensure_ascii=False, sort_keys=True))


def system(profile):
    return (BASE / "SYSTEM_PROMPT_ZH.txt").read_text().replace(
        "{{PROFILE}}", json.dumps(e.private_preferences(profile), ensure_ascii=False, sort_keys=True))


def independent_messages(profile, menu, job):
    if job["kind"] == "choice":
        question = menu_text(menu, job["view"]) + "\n你这次会购买哪件，还是都不买？\n" + CHOICE_SCHEMA
    elif job["kind"] == "care":
        question = CARE_QUESTIONS[job["frame"]] + "\n" + CARE_SCHEMA
    elif job["kind"] == "disclosure":
        question = DISCLOSURE_QUESTION
    else:
        raise ValueError("Dependent messages require actual prior disclosure")
    return [{"role": "system", "content": system(profile)}, {"role": "user", "content": question}]


def payload(job, messages, cfg):
    max_tokens = cfg["disclosure_max_tokens"] if job["kind"] == "disclosure" else cfg["care_max_tokens"] if job["kind"] == "care" else cfg["choice_max_tokens"]
    return {"model": cfg["expected_model"], "messages": messages, "temperature": cfg["temperature"],
            "top_p": cfg["top_p"], "max_tokens": max_tokens, "seed": job["seed"],
            "stream": False, "chat_template_kwargs": {"enable_thinking": cfg["enable_thinking"]}}


def reject_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate JSON key")
        out[key] = value
    return out


def parse_reply(kind, text, finish_reason, model, shown, vocab, cfg):
    if model != cfg["expected_model"] or finish_reason != "stop":
        raise ValueError("model_or_finish_reason")
    if not isinstance(text, str):
        raise ValueError("content_type")
    text = text.strip()
    fenced = False
    if text.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text, re.I)
        if not match:
            raise ValueError("incomplete_fence")
        text, fenced = match.group(1), True
    obj = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    if kind in ["choice", "dialogue_choice"]:
        if not isinstance(obj, dict) or set(obj) != {"decision", "selected_id"}:
            raise ValueError("choice_schema")
        option_ids = {x["option_id"] for x in shown}
        if obj["decision"] == "NO_BUY":
            if obj["selected_id"] is not None:
                raise ValueError("no_buy_must_be_null")
        elif obj["decision"] == "BUY":
            if not isinstance(obj["selected_id"], str) or obj["selected_id"] not in option_ids:
                raise ValueError("unknown_option")
        else:
            raise ValueError("unknown_decision")
    elif kind == "care":
        if not isinstance(obj, dict) or set(obj) != {"allowed_care_labels"}:
            raise ValueError("care_schema")
        seq = obj["allowed_care_labels"]
        if (not isinstance(seq, list) or not seq or not all(isinstance(x, str) for x in seq)
                or len(seq) != len(set(seq)) or not set(seq).issubset(e.CARE)):
            raise ValueError("care_domain")
    elif kind == "disclosure":
        e.validate_disclosure(obj, vocab)
    else:
        raise ValueError("unknown_job_kind")
    return {"value": obj, "fenced": fenced}


def prepare_jobs():
    cfg = e.read(BASE / "config.json")
    profiles = {p["profile_id"]: p for p in e.rows(PREP / "private/profiles.jsonl")}
    menus = e.rows(PREP / "public/menus.jsonl")
    jobs, templates = [], {}
    if (PREP / "private/smoke_jobs.jsonl").exists():
        raise FileExistsError("Preserve existing job plan")
    for profile_id in cfg["smoke_profiles"]:
        profile = profiles[profile_id]
        menu = next(m for m in menus if m["pool_index"] == profile["pool_index"])
        specs = [{"kind": "choice", "view": view, "suffix": "choice_" + view}
                 for view in ["base", "repeat", "reverse", "alias"]]
        specs += [{"kind": "care", "frame": frame, "suffix": "care_" + frame} for frame in ["A", "B"]]
        specs += [{"kind": "disclosure", "suffix": "disclosure"},
                  {"kind": "dialogue_choice", "view": "base", "suffix": "dialogue", "dependency": profile_id + "__disclosure"}]
        for spec in specs:
            job_id = profile_id + "__" + spec.pop("suffix")
            job = {"job_id": job_id, "profile_id": profile_id, "menu_id": menu["menu_id"],
                   "seed": e.number(job_id + "|response", cfg) % 2147483647, **spec}
            jobs.append(job)
            if "dependency" not in job:
                templates[job_id] = payload(job, independent_messages(profile, menu, job), cfg)
    if len(jobs) != cfg["max_generation_attempts"] or len({j['seed'] for j in jobs}) != len(jobs):
        raise ValueError("Job plan count/seed mismatch")
    e.dump_rows(PREP / "private/smoke_jobs.jsonl", jobs)
    e.dump(PREP / "private/independent_request_templates.json", templates)
    return {"planned_jobs": len(jobs), "independent": len(templates), "dependent": len(jobs) - len(templates)}


def freeze():
    if (BASE / "RUN_FREEZE.json").exists():
        raise FileExistsError("Inference freeze already exists")
    files = [BASE / name for name in ["config.json", "PROTOCOL.md", "SYSTEM_PROMPT_ZH.txt", "RULES_FREEZE.json",
                                       "environment.py", "qwen_smoke.py", "analyze_smoke.py", "test_environment.py", "test_smoke.py"]]
    files += [p for p in PREP.rglob("*") if p.is_file()]
    files += [BASE / "artifacts/input/catalogue_strict.jsonl"]
    e.dump(BASE / "RUN_FREEZE.json", {"files": {str(p.relative_to(BASE)): e.digest(p) for p in sorted(files)}})
    return {"frozen_files": len(files)}


def validate_freeze():
    for path, digest in e.read(BASE / "RUN_FREEZE.json")["files"].items():
        if e.digest(BASE / path) != digest:
            raise ValueError("Pre-inference file changed: " + path)


def run():
    validate_freeze()
    cfg = e.read(BASE / "config.json")
    if cfg["concurrency"] != 1 or cfg["retries"] != 0:
        raise ValueError("Unsupported execution settings")
    jobs = e.rows(PREP / "private/smoke_jobs.jsonl")
    if len(jobs) > cfg["max_generation_attempts"]:
        raise ValueError("Call cap")
    profiles = {p["profile_id"]: p for p in e.rows(PREP / "private/profiles.jsonl")}
    menus = {m["menu_id"]: m for m in e.rows(PREP / "public/menus.jsonl")}
    vocabs = e.read(PREP / "public/vocabularies.json")
    templates = e.read(PREP / "private/independent_request_templates.json")
    out = BASE / "artifacts/qwen_smoke"
    if out.exists():
        raise FileExistsError("Never retry an existing run")
    out.mkdir()
    start = time.monotonic()
    with urllib.request.urlopen(cfg["endpoint"] + "/models", timeout=8) as response:
        discovery = json.load(response)
    model_ids = [x["id"] for x in discovery.get("data", [])]
    e.dump(out / "MODEL_DISCOVERY.json", {"model_ids": model_ids, "endpoint": cfg["endpoint"]})
    if cfg["expected_model"] not in model_ids:
        raise ValueError("Expected local model not served")
    finished, attempted, abort = {}, 0, None
    for job in jobs:
        job_id = job["job_id"]
        record = {"job_id": job_id, "kind": job["kind"], "attempted": False, "valid": False}
        elapsed = time.monotonic() - start
        if abort or elapsed >= cfg["total_wall_seconds"]:
            record["not_attempted_reason"] = abort or "wall_budget"
        elif "dependency" in job and not finished[job["dependency"]]["valid"]:
            record["not_attempted_reason"] = "invalid_disclosure_dependency"
        else:
            menu = menus[job["menu_id"]]
            profile = profiles[job["profile_id"]]
            vocab = vocabs[str(menu["pool_index"])]
            body = templates.get(job_id)
            if body is None:
                prior = finished[job["dependency"]]
                public_agent = e.PublicAgent(menu, vocab, "ask_all")
                public_agent.observe("ASK_ALL", prior["parsed"]["value"])
                recommendation = public_agent.finish()
                mapping = {x["product_id"]: x["option_id"] for x in shown_options(menu)}
                suggestion = ("建议本次不购买" if recommendation["decision"] == "NO_BUY"
                              else "推荐商品 " + mapping[recommendation["selected_id"]])
                messages = templates[job["dependency"]]["messages"] + [
                    {"role": "assistant", "content": prior["content"]},
                    {"role": "user", "content": menu_text(menu) + "\n推荐系统依据你刚才的披露：" + suggestion
                     + "。请依据你原本的画像自己决定，你可以选其他商品，也可以不买。\n" + CHOICE_SCHEMA}]
                body = payload(job, messages, cfg)
                record["public_agent_recommendation"] = recommendation
            request_path = out / "requests" / (job_id + ".json")
            e.dump(request_path, body)
            record.update(attempted=True, request_sha256=e.digest(request_path),
                          request_file=str(request_path.relative_to(BASE)),
                          started_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
            attempted += 1
            if attempted > cfg["max_generation_attempts"]:
                raise AssertionError("Call cap exceeded")
            with (out / "ATTEMPTS.jsonl").open("a") as ledger:
                ledger.write(json.dumps({"job_id": job_id, "attempt_number": attempted,
                                         "request_sha256": record["request_sha256"]}) + "\n")
            call_start = time.monotonic()
            try:
                http = urllib.request.Request(cfg["endpoint"] + "/chat/completions",
                                              data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(http, timeout=min(cfg["request_timeout_seconds"], cfg["total_wall_seconds"] - elapsed)) as response:
                    raw = response.read()
                response_path = out / "responses" / (job_id + ".body")
                response_path.parent.mkdir(parents=True, exist_ok=True)
                response_path.write_bytes(raw)
                result = json.loads(raw)
                choice = result["choices"][0]
                record.update(content=choice["message"]["content"], response_id=result.get("id"),
                              served_model=result.get("model"), finish_reason=choice.get("finish_reason"),
                              usage=result.get("usage"), response_sha256=e.digest(response_path))
                record["parsed"] = parse_reply(job["kind"], record["content"], record["finish_reason"],
                                               record["served_model"], shown_options(menu, job.get("view", "base")), vocab, cfg)
                record["valid"] = True
            except Exception as error:
                record["error_class"] = type(error).__name__
                if isinstance(error, urllib.error.HTTPError):
                    error_path = out / "responses" / (job_id + ".http_error.body")
                    error_path.parent.mkdir(parents=True, exist_ok=True)
                    error_path.write_bytes(error.read())
                    record["http_status"] = error.code
                elif isinstance(error, ValueError):
                    record["validation_error"] = str(error)[:160]
                if record.get("served_model") and record["served_model"] != cfg["expected_model"]:
                    abort = "model_identity_drift"
            record["latency_seconds"] = time.monotonic() - call_start
        finished[job_id] = record
        e.dump(out / "records" / (job_id + ".json"), record)
        print(json.dumps({"job_id": job_id, "attempted": record["attempted"], "valid": record["valid"]}), flush=True)
    e.dump(out / "RUN_RECEIPT.json", {"planned": len(jobs), "attempted": attempted,
           "valid": sum(r["valid"] for r in finished.values()),
           "wall_seconds": time.monotonic() - start, "model": cfg["expected_model"],
           "retries": 0, "model_discovery_gets": 1})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "freeze", "run"])
    args = parser.parse_args()
    if args.mode == "prepare":
        print(json.dumps(prepare_jobs()))
    elif args.mode == "freeze":
        print(json.dumps(freeze()))
    else:
        run()


if __name__ == "__main__":
    main()
