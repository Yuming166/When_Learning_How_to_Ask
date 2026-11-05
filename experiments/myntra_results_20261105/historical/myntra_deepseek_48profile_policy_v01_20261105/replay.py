from __future__ import annotations
import json
from pathlib import Path
import engine
import environment as ref
CFG = json.loads((Path(__file__).resolve().parent / "config.json").read_text())

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
