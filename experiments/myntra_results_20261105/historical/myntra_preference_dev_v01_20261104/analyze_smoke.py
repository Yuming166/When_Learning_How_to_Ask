"""Pre-inference-frozen descriptive analysis, never model-judged correctness."""
import collections
import json

import environment as e
import qwen_smoke as q


def canonical_choice(parsed, shown):
    answer = parsed["value"]
    mapping = {x["option_id"]: x["product_id"] for x in shown}
    return {"decision": answer["decision"],
            "selected_id": mapping[answer["selected_id"]] if answer["selected_id"] is not None else None}


def same_preferences(a, b):
    return (a["purchase_threshold"] == b["purchase_threshold"]
            and a["soft"] == b["soft"]
            and set(a["hard"]["allowed_care_labels"]) == set(b["hard"]["allowed_care_labels"])
            and set(a["hard"]["excluded_fabric_labels"]) == set(b["hard"]["excluded_fabric_labels"]))


def analyze():
    q.validate_freeze()
    base = e.BASE
    cfg = e.read(base / "config.json")
    prepared = base / "artifacts/prepared"
    run = base / "artifacts/qwen_smoke"
    jobs = e.rows(prepared / "private/smoke_jobs.jsonl")
    profiles = {p["profile_id"]: p for p in e.rows(prepared / "private/profiles.jsonl")}
    menus = {m["menu_id"]: m for m in e.rows(prepared / "public/menus.jsonl")}
    references = {r["case_id"]: r["reference"] for r in e.rows(prepared / "evaluator_only/references.jsonl")}
    ledger = e.rows(run / "ATTEMPTS.jsonl") if (run / "ATTEMPTS.jsonl").exists() else []
    attempted = {row["job_id"] for row in ledger}
    if len(attempted) != len(ledger) or len(ledger) > cfg["max_generation_attempts"]:
        raise ValueError("Attempt ledger duplicates or cap violation")
    analysis = []
    for job in jobs:
        path = run / "records" / (job["job_id"] + ".json")
        record = e.read(path) if path.exists() else {"valid": False, "attempted": job["job_id"] in attempted,
                                                   "not_attempted_reason": "missing_terminal_record"}
        row = {"job_id": job["job_id"], "profile_id": job["profile_id"], "kind": job["kind"],
               "attempted": record["attempted"], "valid": record["valid"],
               "error_class": record.get("error_class"), "validation_error": record.get("validation_error"),
               "not_attempted_reason": record.get("not_attempted_reason"),
               "fenced": record.get("parsed", {}).get("fenced", False)}
        profile = profiles[job["profile_id"]]
        if job["kind"] in ["choice", "dialogue_choice"]:
            reference = references[job["profile_id"] + "__" + job["menu_id"]]
            row.update(reference_decision=reference["decision"], reference_no_buy_reason=reference["no_buy_reason"],
                       correct=False, decision_correct=False, selected_hard_violation=None, selected_utility_regret=None)
            if job["kind"] == "dialogue_choice":
                recommendation = record.get("public_agent_recommendation")
                row["public_agent_recommendation"] = recommendation
                row["public_agent_recommendation_correct"] = bool(recommendation and e.score_decision(recommendation, reference))
            if record["valid"]:
                choice = canonical_choice(record["parsed"], q.shown_options(menus[job["menu_id"]], job.get("view", "base")))
                row.update(canonical_choice=choice, correct=e.score_decision(choice, reference),
                           decision_correct=choice["decision"] == reference["decision"])
                if choice["decision"] == "BUY":
                    row["selected_hard_violation"] = choice["selected_id"] not in reference["feasible_ids"]
                    if not row["selected_hard_violation"]:
                        row["selected_utility_regret"] = reference["maximum_score"] - reference["scores_by_product"][choice["selected_id"]]
        elif job["kind"] == "care":
            row["correct"] = bool(record["valid"] and set(record["parsed"]["value"]["allowed_care_labels"]) == set(profile["hard"]["allowed_care_labels"]))
        elif job["kind"] == "disclosure":
            row["correct"] = bool(record["valid"] and same_preferences(record["parsed"]["value"], e.private_preferences(profile)))
        analysis.append(row)
    choices = [r for r in analysis if r["kind"] in ["choice", "dialogue_choice"]]
    no_buy = [r for r in choices if r["reference_decision"] == "NO_BUY"]
    buy = [r for r in choices if r["reference_decision"] == "BUY"]
    by_kind = {}
    for kind in ["choice", "care", "disclosure", "dialogue_choice"]:
        group = [r for r in analysis if r["kind"] == kind]
        by_kind[kind] = {"planned": len(group), "attempted": sum(r["attempted"] for r in group),
                         "valid": sum(r["valid"] for r in group), "correct": sum(r["correct"] for r in group)}
    consistency = []
    for pid in cfg["smoke_profiles"]:
        group = [r for r in analysis if r["profile_id"] == pid and r["kind"] == "choice"]
        valid = [r for r in group if r["valid"]]
        consistency.append({"profile_id": pid, "valid_views": len(valid),
                            "all_views_reference_correct": all(r["correct"] for r in group),
                            "decision_stable": len(valid) == 4 and len({r['canonical_choice']['decision'] for r in valid}) == 1,
                            "exact_selected_id_stable": len(valid) == 4 and len({r['canonical_choice']['selected_id'] for r in valid}) == 1,
                            "note": "Different tied maximizers are not correctness failures"})
    records = [e.read(path) for path in sorted((run / "records").glob("*.json"))]
    response_ids = [r["response_id"] for r in records if r.get("response_id")]
    summary = {
        "model": cfg["expected_model"], "profiles": len(cfg["smoke_profiles"]),
        "planned": len(jobs), "attempted": len(ledger), "valid": sum(r["valid"] for r in analysis),
        "invalid_attempted": sum(r["attempted"] and not r["valid"] for r in analysis),
        "not_attempted": sum(not r["attempted"] for r in analysis),
        "unique_response_ids": len(set(response_ids)), "response_ids_recorded": len(response_ids),
        "by_kind": by_kind, "choice_planned": len(choices),
        "choice_optimal_actions_correct": sum(r["correct"] for r in choices),
        "choice_decisions_correct": sum(r["decision_correct"] for r in choices),
        "reference_buy_calls": len(buy), "reference_buy_correct": sum(r["correct"] for r in buy),
        "reference_no_buy_calls": len(no_buy), "reference_no_buy_correct": sum(r["correct"] for r in no_buy),
        "reference_no_buy_with_feasible_goods_calls": sum(r["reference_no_buy_reason"] == "BELOW_OR_EQUAL_THRESHOLD" for r in no_buy),
        "valid_buy_selections": sum(r.get("canonical_choice", {}).get("decision") == "BUY" for r in choices),
        "hard_violating_selections": sum(r["selected_hard_violation"] is True for r in choices),
        "selected_utility_regrets": [r["selected_utility_regret"] for r in choices if r["selected_utility_regret"] is not None],
        "closed_loop_recommendations_correct": sum(r.get("public_agent_recommendation_correct", False) for r in choices),
        "fenced_outputs": sum(r["fenced"] for r in analysis), "consistency": consistency,
        "token_usage": {k: sum((r.get("usage") or {}).get(k, 0) for r in records) for k in ["prompt_tokens", "completion_tokens", "total_tokens"]},
        "scope": "two_constructed_profiles_development_smoke_only",
        "natural_reliability_sharing_established": False, "method_superiority_established": False,
        "human_behavior_validated": False, "reserved_items_transmitted_or_evaluated": 0,
        "positive_negative_purchase_coverage": bool(buy and no_buy),
    }
    e.dump_rows(base / "artifacts/smoke_analysis_rows.jsonl", analysis)
    e.dump(base / "results/QWEN_SMOKE.json", summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(analyze(), ensure_ascii=False))
