"""Zero-call source, request, response and deterministic replay verification."""
import collections
import hashlib
import json
import pathlib
import socket
import tempfile

import environment as e
import qwen_smoke as q
import analyze_smoke as a


def verify():
    base = e.BASE
    cfg = e.read(base / "config.json")
    q.validate_freeze()
    checks = collections.Counter()

    def require(ok, category):
        if not ok:
            raise AssertionError(category)
        checks[category] += 1

    prepared = base / "artifacts/prepared"
    run = base / "artifacts/qwen_smoke"
    source = e.rows(base / "artifacts/input/catalogue_strict.jsonl")
    source_by_id = {p["product_id"]: p for p in source}
    menus = e.rows(prepared / "public/menus.jsonl")
    menus_by_id = {m["menu_id"]: m for m in menus}
    profiles = {p["profile_id"]: p for p in e.rows(prepared / "private/profiles.jsonl")}
    references = e.rows(prepared / "evaluator_only/references.jsonl")
    vocabs = e.read(prepared / "public/vocabularies.json")
    public_cases = e.rows(prepared / "public/cases.jsonl")
    used_ids = []
    require(e.digest(base / "artifacts/input/catalogue_strict.jsonl") == cfg["source_sha256"], "source_hash")
    for menu in menus:
        require(len(menu["items"]) == cfg["items_per_menu"], "menu_size")
        for item in menu["items"]:
            raw = source_by_id[item["product_id"]]
            require(raw["split"] == item["source_split"] == "development", "development_only")
            require((raw["gender"], raw["category"]) == (menu["gender"], menu["category"]), "homogeneous_category")
            require(item["attributes"] == {f: raw["attributes"][f]["value"] for f in e.FIELDS}, "literal_source_attributes")
            used_ids.append(item["product_id"])
    require(len(set(used_ids)) == len(used_ids) == 48, "disjoint_menu_item_ids")
    for case in public_cases:
        serialized = json.dumps(case)
        require(not any('"' + key + '"' in serialized for key in ["hard", "soft", "purchase_threshold", "reference", "scores_by_product"]), "public_private_boundary")
    for reference in references:
        items = menus_by_id[reference["menu_id"]]["items"]
        p = profiles[reference["profile_id"]]
        require(e.evaluate_sql(items, p) == reference["reference"], "independent_sql_reference")
    jobs = e.rows(prepared / "private/smoke_jobs.jsonl")
    templates = e.read(prepared / "private/independent_request_templates.json")
    ledger = e.rows(run / "ATTEMPTS.jsonl")
    require(len(ledger) <= cfg["max_generation_attempts"], "call_cap")
    require(len({r["job_id"] for r in ledger}) == len(ledger), "no_retry")
    require({r["job_id"] for r in ledger} == {j["job_id"] for j in jobs}, "planned_attempt_coverage")
    response_ids = []
    for job in jobs:
        rec = e.read(run / "records" / (job["job_id"] + ".json"))
        request_path = base / rec["request_file"]
        body = e.read(request_path)
        require(e.digest(request_path) == rec["request_sha256"], "request_hash")
        require(body["model"] == cfg["expected_model"] and body["seed"] == job["seed"], "model_seed_binding")
        require(not any(key in json.dumps(body) for key in ["scores_by_product", "valid_purchase_ids", "reference_decision", "feasible_ids"]), "reference_not_sent")
        if "dependency" not in job:
            require(body == templates[job["job_id"]], "frozen_request_identity")
        else:
            prior = e.read(run / "records" / (job["dependency"] + ".json"))
            require(body["messages"][:2] == templates[job["dependency"]]["messages"], "real_dialogue_prefix")
            require(body["messages"][2] == {"role": "assistant", "content": prior["content"]}, "actual_reply_in_history")
            agent = e.PublicAgent(menus_by_id[job["menu_id"]], vocabs[str(profiles[job["profile_id"]]["pool_index"])], "ask_all")
            agent.observe("ASK_ALL", prior["parsed"]["value"])
            require(agent.finish() == rec["public_agent_recommendation"], "recommendation_from_disclosure_only")
        response_path = run / "responses" / (job["job_id"] + ".body")
        require(e.digest(response_path) == rec["response_sha256"], "raw_response_hash")
        raw = e.read(response_path)
        require(raw["model"] == cfg["expected_model"], "served_model_identity")
        require(raw["choices"][0]["message"]["content"] == rec["content"], "raw_content_identity")
        parsed = q.parse_reply(job["kind"], rec["content"], rec["finish_reason"], rec["served_model"],
                               q.shown_options(menus_by_id[job["menu_id"]], job.get("view", "base")),
                               vocabs[str(profiles[job["profile_id"]]["pool_index"])], cfg)
        require(parsed == rec["parsed"], "parser_replay")
        response_ids.append(rec["response_id"])
    require(len(set(response_ids)) == len(response_ids), "unique_response_ids")
    # Reproduce prepared artefacts and analytical outputs with networking denied.
    original_socket, original_create = socket.socket, socket.create_connection

    def denied(*args, **kwargs):
        raise RuntimeError("No networking during offline verification")

    summary_before = (base / "results/QWEN_SMOKE.json").read_bytes()
    analysis_before = (base / "artifacts/smoke_analysis_rows.jsonl").read_bytes()
    old_prep = q.PREP
    try:
        socket.socket, socket.create_connection = denied, denied
        with tempfile.TemporaryDirectory(prefix="myntra_preference_replay_") as directory:
            fresh = pathlib.Path(directory) / "prepared"
            e.prepare(fresh)
            q.PREP = fresh
            q.prepare_jobs()
            original_files = sorted(str(p.relative_to(prepared)) for p in prepared.rglob("*") if p.is_file())
            require(original_files == sorted(str(p.relative_to(fresh)) for p in fresh.rglob("*") if p.is_file()), "replayed_input_file_coverage")
            for rel in original_files:
                require((prepared / rel).read_bytes() == (fresh / rel).read_bytes(), "prepared_byte_replay")
            e.offline_episodes(fresh)
            require((base / "artifacts/offline_reference_episodes.jsonl").read_bytes() == (fresh.parent / "offline_reference_episodes.jsonl").read_bytes(), "reference_episode_byte_replay")
        q.PREP = old_prep
        a.analyze()
        require((base / "results/QWEN_SMOKE.json").read_bytes() == summary_before, "analysis_summary_byte_replay")
        require((base / "artifacts/smoke_analysis_rows.jsonl").read_bytes() == analysis_before, "analysis_rows_byte_replay")
    finally:
        q.PREP = old_prep
        socket.socket, socket.create_connection = original_socket, original_create
    preservation = e.read(base / "PRESERVATION_BASE.json")
    root = base.parents[1]
    for relative, expected in preservation["files"].items():
        require(e.digest(root / relative) == expected, "historical_file_preservation")
    receipt = {"status": "PASS", "checks": dict(checks), "total_checks": sum(checks.values()),
               "historical_files_unchanged": len(preservation["files"]), "offline_prepared_files_replayed": 7,
               "attempts_verified": len(ledger), "new_inference_calls": 0,
               "verification_scope": "source_binding_privacy_boundary_ledger_and_replay",
               "human_semantic_review": False}
    e.dump(base / "results/VERIFICATION.json", receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(verify()))
