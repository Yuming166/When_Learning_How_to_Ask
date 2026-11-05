"""Bounded deterministic closed-loop policy comparison for Myntra v0.1."""
from __future__ import annotations

import collections
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())


def load_environment(source_worktree: Path):
    module_path = source_worktree / CONFIG["source_experiment"] / "environment.py"
    spec = importlib.util.spec_from_file_location("myntra_closed_loop_source_env", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import source environment: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def entropy(values) -> float:
    counts = collections.Counter(values)
    total = sum(counts.values())
    return -sum((count / total) * math.log2(count / total) for count in counts.values() if count)


def query_signature(env, profile, action):
    return canonical(env.ReferenceUser(profile).answer(action))


def merge_answer(preferences: dict, action: str, answer: dict) -> dict:
    result = copy.deepcopy(preferences)
    if action == "purchase_threshold":
        result["purchase_threshold"] = answer["purchase_threshold"]
    else:
        result["soft"]["scores"][action] = copy.deepcopy(answer["scores"])
        if action == "wash_care":
            result["hard"]["allowed_care_labels"] = copy.deepcopy(answer["allowed_care_labels"])
        if action == "fabric":
            result["hard"]["excluded_fabric_labels"] = copy.deepcopy(answer["excluded_fabric_labels"])
    return result


def target_set(env, items, preferences):
    reference = env.evaluate_python(items, preferences)
    if reference["decision"] == "NO_BUY":
        return ("NO_BUY",)
    return tuple(reference["valid_purchase_ids"])


class PublicPolicy:
    """Policy sees a public menu, independent prior draws, and observed answers only."""

    def __init__(self, env, menu, prior_profiles, method):
        if method not in CONFIG["methods"]:
            raise ValueError(f"Unknown method: {method}")
        self.env = env
        self.menu = copy.deepcopy(menu)
        self.items = self.menu["items"]
        self.prior = [env.private_preferences(p) for p in prior_profiles]
        self.method = method
        self.known = {}
        self.history = []
        self._state_cache = {}

    def posterior(self):
        key = canonical(self.known)
        if key in self._state_cache:
            return self._state_cache[key]
        profiles = []
        for prior in self.prior:
            current = copy.deepcopy(prior)
            for action, answer in self.known.items():
                current = merge_answer(current, action, answer)
            profiles.append(current)
        targets = [target_set(self.env, self.items, p) for p in profiles]
        result = (profiles, targets)
        self._state_cache[key] = result
        return result

    def predict(self):
        _, targets = self.posterior()
        actions = ["NO_BUY", *sorted(item["product_id"] for item in self.items)]
        scores = {action: sum(action == "NO_BUY" and target == ("NO_BUY",)
                              or action != "NO_BUY" and action in target for target in targets) / len(targets)
                  for action in actions}
        best = max(scores.values())
        # Fixed conservative tie rule: NO_BUY, then sorted product IDs.
        selected = next(action for action in actions if abs(scores[action] - best) <= 1e-15)
        return selected, scores[selected]

    def score_query(self, action):
        profiles, targets = self.posterior()
        signatures = [query_signature(self.env, p, action) for p in profiles]
        groups = collections.defaultdict(list)
        for idx, signature in enumerate(signatures):
            groups[signature].append(idx)

        if self.method == "profile_ig":
            return entropy(signatures)

        labels = [canonical(target) for target in targets]
        if self.method == "decision_set_ig":
            marginal = entropy(labels)
            conditional = sum(len(indices) / len(labels) * entropy(labels[i] for i in indices)
                              for indices in groups.values())
            return max(0.0, marginal - conditional)

        if self.method == "decision_value":
            before = self.predict()[1]
            after = 0.0
            for indices in groups.values():
                group_targets = [targets[i] for i in indices]
                actions = ["NO_BUY", *sorted(item["product_id"] for item in self.items)]
                best = max(sum(action == "NO_BUY" and target == ("NO_BUY",)
                               or action != "NO_BUY" and action in target for target in group_targets) / len(indices)
                           for action in actions)
                after += len(indices) / len(targets) * best
            return max(0.0, after - before)

        raise ValueError("Fixed-order policy has no adaptive score")

    def next_action(self):
        unanswered = [a for a in CONFIG["query_actions"] if a not in self.known]
        if not unanswered:
            return None
        if self.method == "fixed_order":
            return unanswered[0]
        scored = [(self.score_query(action), -CONFIG["query_actions"].index(action), action)
                  for action in unanswered]
        # Stable action-order tie break, with no result-driven tuning.
        return max(scored)[2]

    def observe(self, action, answer):
        if action in self.known or action not in CONFIG["query_actions"]:
            raise ValueError("Repeated or illegal query action")
        self.known[action] = copy.deepcopy(answer)
        self.history.append({"action": action, "answer": copy.deepcopy(answer)})


def make_prior_profiles(env, vocabularies, prior_count: int):
    source_cfg = env.read(env.BASE / "config.json")
    cfg = copy.deepcopy(source_cfg)
    cfg["seed_root"] = CONFIG["prior_seed_root"]
    cfg["profiles_per_pool"] = prior_count
    return {
        pool: env.generate_profiles(vocabularies[str(pool)], pool, cfg)
        for pool in range(len(source_cfg["pools"]))
    }


def episode_metrics(env, items, profile, action):
    reference = env.evaluate_python(items, profile)
    correct = (action == "NO_BUY" and reference["decision"] == "NO_BUY") or action in reference["valid_purchase_ids"]
    feasible = set(reference["feasible_ids"])
    hard_violation = action != "NO_BUY" and action not in feasible
    optimum = max(0, reference["maximum_score"] - profile["purchase_threshold"]) if reference["maximum_score"] is not None else 0
    if action in reference["valid_purchase_ids"]:
        reward = reference["scores_by_product"][action] - profile["purchase_threshold"]
    else:
        reward = 0
    regret = max(0, optimum - reward)
    return {
        "reference_decision": reference["decision"],
        "reference_target_set": ["NO_BUY"] if reference["decision"] == "NO_BUY" else reference["valid_purchase_ids"],
        "selected_action": action,
        "exact_decision_correct": bool(correct),
        "purchase_recall_case": reference["decision"] == "BUY" and action in reference["valid_purchase_ids"],
        "no_buy_correct_case": reference["decision"] == "NO_BUY" and action == "NO_BUY",
        "false_purchase_case": reference["decision"] == "NO_BUY" and action != "NO_BUY",
        "hard_constraint_violation": bool(hard_violation),
        "score_regret": regret,
        "normalized_score_regret": regret / max(1, optimum),
    }


def run_case(env, case, profile, prior_profiles, method, max_budget):
    menu = case["public_menu"]
    user = env.ReferenceUser(profile)
    policy = PublicPolicy(env, menu, prior_profiles, method)
    records = []

    for budget in range(max_budget + 1):
        action, _posterior_success = policy.predict()
        metrics = episode_metrics(env, menu["items"], profile, action)
        records.append({
            "case_id": case["case_id"], "profile_id": profile["profile_id"],
            "menu_id": menu["menu_id"], "method": method, "budget": budget,
            "elicitation_units": budget, "dialogue_turns": budget,
            "query_sequence": [x["action"] for x in policy.history],
            **metrics,
        })
        if budget == max_budget:
            break
        query = policy.next_action()
        if query is None:
            raise RuntimeError("Policy exhausted actions before the declared budget")
        answer = user.answer(query)
        policy.observe(query, answer)
    return records


def run_ask_all(env, case, profile):
    user = env.ReferenceUser(profile)
    answer = user.answer("ASK_ALL")
    predicted = env.evaluate_python(case["public_menu"]["items"], answer)
    action = predicted["valid_purchase_ids"][0] if predicted["valid_purchase_ids"] else "NO_BUY"
    return {
        "case_id": case["case_id"], "profile_id": profile["profile_id"],
        "menu_id": case["public_menu"]["menu_id"], "method": "ask_all",
        "budget": 6, "elicitation_units": 6, "dialogue_turns": 1,
        "query_sequence": ["ASK_ALL"],
        **episode_metrics(env, case["public_menu"]["items"], profile, action),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
