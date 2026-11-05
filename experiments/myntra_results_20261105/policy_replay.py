from __future__ import annotations
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'code'))
import engine
import environment as ref
import legacy_replay
CFG = json.loads((HERE/'llm_config.json').read_text())
STATIC = 'decision_value_initial_order'

def initial_rank(menu, prior):
    p = engine.PublicPolicy(ref, menu, prior, "decision_value")
    scores = {a: p.score_query(a) for a in CFG["query_actions"]}
    order = sorted(CFG["query_actions"], key=lambda a: (-scores[a], CFG["query_actions"].index(a)))
    return {"scores": scores, "order": order, "initial_prediction": list(p.predict())}



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
