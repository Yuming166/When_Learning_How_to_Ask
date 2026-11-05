"""Controlled categorical preferences with an explicit outside option.

PublicAgent never loads private profiles or evaluator labels. Real Qwen
responses are a separate observation channel, not a manually flipped oracle.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import hashlib
import json
import pathlib
import sqlite3

BASE = pathlib.Path(__file__).resolve().parent
FIELDS = ["neckline", "sleeve_length", "fabric", "wash_care", "pattern"]
CARE = ["dry clean", "hand wash", "machine wash"]


def read(path):
    return json.loads(pathlib.Path(path).read_text())


def rows(path):
    return [json.loads(line) for line in pathlib.Path(path).read_text().splitlines() if line.strip()]


def dump(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def dump_rows(path, values):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def number(label, cfg):
    return int.from_bytes(hashlib.sha256((cfg["seed_root"] + "|" + label).encode()).digest()[:8], "big")


def private_preferences(profile):
    return copy.deepcopy({key: profile[key] for key in ["hard", "soft", "purchase_threshold"]})


def validate_disclosure(value, vocab):
    if not isinstance(value, dict) or set(value) != {"hard", "soft", "purchase_threshold"}:
        raise ValueError("disclosure_keys")
    hard = value["hard"]
    if not isinstance(hard, dict) or set(hard) != {"allowed_care_labels", "excluded_fabric_labels"}:
        raise ValueError("hard_schema")
    for key, allowed in [("allowed_care_labels", CARE), ("excluded_fabric_labels", vocab["fabric"])]:
        seq = hard[key]
        if (not isinstance(seq, list) or not all(isinstance(x, str) for x in seq)
                or len(set(seq)) != len(seq) or not set(seq).issubset(allowed)):
            raise ValueError("hard_value_domain")
    if not hard["allowed_care_labels"]:
        raise ValueError("empty_care_set")
    if type(value["purchase_threshold"]) is not int:
        raise ValueError("threshold_type")
    if not isinstance(value["soft"], dict) or set(value["soft"]) != {"scores"}:
        raise ValueError("soft_schema")
    scores = value["soft"]["scores"]
    if not isinstance(scores, dict) or set(scores) != set(FIELDS):
        raise ValueError("score_fields")
    for field in FIELDS:
        if not isinstance(scores[field], dict) or set(scores[field]) != set(vocab[field]):
            raise ValueError("score_vocabulary")
        if not all(type(x) is int for x in scores[field].values()):
            raise ValueError("score_value_type")
    return value


def evaluate_python(items, profile):
    feasible, scores = [], {}
    for item in items:
        attrs = item["attributes"]
        if attrs["wash_care"] not in profile["hard"]["allowed_care_labels"]:
            continue
        if attrs["fabric"] in profile["hard"]["excluded_fabric_labels"]:
            continue
        pid = item["product_id"]
        feasible.append(pid)
        scores[pid] = sum(profile["soft"]["scores"][f][attrs[f]] for f in FIELDS)
    maximum = max(scores.values()) if scores else None
    favorites = sorted(pid for pid in feasible if scores[pid] == maximum)
    buy = maximum is not None and maximum > profile["purchase_threshold"]
    return {"feasible_ids": sorted(feasible), "scores_by_product": scores,
            "relative_favorite_ids": favorites, "maximum_score": maximum,
            "decision": "BUY" if buy else "NO_BUY",
            "valid_purchase_ids": favorites if buy else [],
            "no_buy_reason": None if buy else "NO_FEASIBLE_ITEM" if not feasible else "BELOW_OR_EQUAL_THRESHOLD"}


def evaluate_sql(items, profile):
    """Separate implementation: relational joins, hard filters and integer sum."""
    with contextlib.closing(sqlite3.connect(":memory:")) as db:
        db.executescript("""
            CREATE TABLE feature(item TEXT, field TEXT, value TEXT);
            CREATE TABLE rating(field TEXT, value TEXT, score INTEGER);
            CREATE TABLE allowed_care(value TEXT);
            CREATE TABLE excluded_fabric(value TEXT);
        """)
        db.executemany("INSERT INTO feature VALUES (?,?,?)",
                       [(i["product_id"], f, i["attributes"][f]) for i in items for f in FIELDS])
        db.executemany("INSERT INTO rating VALUES (?,?,?)",
                       [(f, v, score) for f, values in profile["soft"]["scores"].items() for v, score in values.items()])
        db.executemany("INSERT INTO allowed_care VALUES (?)", [(x,) for x in profile["hard"]["allowed_care_labels"]])
        db.executemany("INSERT INTO excluded_fabric VALUES (?)", [(x,) for x in profile["hard"]["excluded_fabric_labels"]])
        result = db.execute("""
            SELECT f.item, SUM(r.score)
            FROM feature f JOIN rating r ON f.field=r.field AND f.value=r.value
            WHERE f.item IN (
                SELECT c.item FROM feature c JOIN allowed_care a ON c.value=a.value
                WHERE c.field='wash_care'
            ) AND f.item NOT IN (
                SELECT t.item FROM feature t JOIN excluded_fabric x ON t.value=x.value
                WHERE t.field='fabric'
            ) GROUP BY f.item ORDER BY f.item
        """).fetchall()
        scores = dict(result)
        if result:
            maximum = max(score for _, score in result)
            favorites = sorted(pid for pid, score in result if score == maximum)
            buying = maximum > profile["purchase_threshold"]
        else:
            maximum, favorites, buying = None, [], False
        return {"feasible_ids": sorted(scores), "scores_by_product": scores,
                "relative_favorite_ids": favorites, "maximum_score": maximum,
                "decision": "BUY" if buying else "NO_BUY",
                "valid_purchase_ids": favorites if buying else [],
                "no_buy_reason": None if buying else "NO_FEASIBLE_ITEM" if not scores else "BELOW_OR_EQUAL_THRESHOLD"}


class ReferenceUser:
    """Lossless deterministic user for software wiring checks only."""
    def __init__(self, profile):
        self._preferences = private_preferences(profile)

    def answer(self, action):
        if action == "ASK_ALL":
            return copy.deepcopy(self._preferences)
        if action == "purchase_threshold":
            return {"purchase_threshold": self._preferences["purchase_threshold"]}
        if action not in FIELDS:
            raise ValueError("Unsupported query")
        out = {"field": action, "scores": copy.deepcopy(self._preferences["soft"]["scores"][action])}
        if action == "wash_care":
            out["allowed_care_labels"] = self._preferences["hard"]["allowed_care_labels"][:]
        if action == "fabric":
            out["excluded_fabric_labels"] = self._preferences["hard"]["excluded_fabric_labels"][:]
        return out


class PublicAgent:
    """Transparent disclosure baseline, not the proposed reliability learner."""
    def __init__(self, public_menu, public_vocab, strategy="fieldwise"):
        self.items = copy.deepcopy(public_menu["items"])
        self.vocab = copy.deepcopy(public_vocab)
        self.strategy = strategy
        self.observed = {"hard": {}, "soft": {"scores": {}}}
        self.history = []

    def next_action(self):
        if self.strategy == "ask_all":
            return "ASK_ALL" if not self.history else None
        for field in FIELDS:
            if field not in self.observed["soft"]["scores"]:
                return field
        return "purchase_threshold" if "purchase_threshold" not in self.observed else None

    def observe(self, action, answer):
        if action == "ASK_ALL":
            self.observed = copy.deepcopy(validate_disclosure(answer, self.vocab))
        elif action == "purchase_threshold":
            if set(answer) != {"purchase_threshold"} or type(answer["purchase_threshold"]) is not int:
                raise ValueError("Threshold response schema")
            self.observed["purchase_threshold"] = answer["purchase_threshold"]
        elif action in FIELDS:
            keys = {"field", "scores"}
            extra = {"wash_care": "allowed_care_labels", "fabric": "excluded_fabric_labels"}.get(action)
            if extra:
                keys.add(extra)
            if set(answer) != keys or answer["field"] != action:
                raise ValueError("Field response schema")
            if set(answer["scores"]) != set(self.vocab[action]) or not all(type(v) is int for v in answer["scores"].values()):
                raise ValueError("Field response values")
            self.observed["soft"]["scores"][action] = copy.deepcopy(answer["scores"])
            if extra:
                self.observed["hard"][extra] = copy.deepcopy(answer[extra])
        else:
            raise ValueError("Unsupported action")
        self.history.append({"action": action, "answer": copy.deepcopy(answer)})

    def finish(self):
        try:
            preferences = validate_disclosure(self.observed, self.vocab)
        except ValueError:
            return {"status": "INSUFFICIENT_PREFERENCES", "decision": None, "selected_id": None}
        reference = evaluate_python(self.items, preferences)
        return {"status": "READY_FROM_DISCLOSURE", "decision": reference["decision"],
                "selected_id": reference["valid_purchase_ids"][0] if reference["valid_purchase_ids"] else None}


def score_decision(answer, reference):
    if answer["decision"] == "NO_BUY":
        return reference["decision"] == "NO_BUY" and answer["selected_id"] is None
    return reference["decision"] == "BUY" and answer["selected_id"] in reference["valid_purchase_ids"]


def generate_profiles(vocab, pool_index, cfg):
    result = []
    for local in range(cfg["profiles_per_pool"]):
        pid = f"P{pool_index * cfg['profiles_per_pool'] + local:02d}"
        mask = 1 + number(pid + "|care", cfg) % 7
        allowed = [v for i, v in enumerate(CARE) if mask & (1 << i)]
        fabric = vocab["fabric"]
        excluded = [fabric[number(pid + "|excluded", cfg) % len(fabric)]] if number(pid + "|exclude_switch", cfg) % 4 == 0 else []
        scores = {}
        for field, values in vocab.items():
            favorite = number(pid + "|" + field + "|favorite", cfg) % len(values)
            avoid = (favorite + 1 + number(pid + "|" + field + "|avoid", cfg) % (len(values) - 1)) % len(values)
            importance = 1 + number(pid + "|" + field + "|importance", cfg) % 2
            scores[field] = {v: 2 * importance if i == favorite else -importance if i == avoid else 0
                             for i, v in enumerate(values)}
        result.append({"profile_id": pid, "pool_index": pool_index, "development_only": True,
                       "hard": {"allowed_care_labels": allowed, "excluded_fabric_labels": excluded},
                       "soft": {"scores": scores},
                       "purchase_threshold": cfg["purchase_thresholds"][number(pid + "|threshold", cfg) % len(cfg["purchase_thresholds"]) ]})
    return result


def prepare(output):
    for name, expected in read(BASE / "RULES_FREEZE.json")["files"].items():
        if digest(BASE / name) != expected:
            raise ValueError("Construction rules changed after freeze")
    cfg = read(BASE / "config.json")
    source = BASE / "artifacts/input/catalogue_strict.jsonl"
    if digest(source) != cfg["source_sha256"]:
        raise ValueError("Catalogue snapshot hash mismatch")
    source_items = rows(source)
    if len(source_items) != 471:
        raise ValueError("Expected all 471 source catalogue records")
    if output.exists():
        raise FileExistsError("Preserve existing prepared data")
    development = [x for x in source_items if x["split"] == "development"]
    profiles, menus, vocabs = [], [], {}
    for pool_index, (gender, category) in enumerate(cfg["pools"]):
        candidates = [x for x in development if x["gender"] == gender and x["category"] == category]
        candidates.sort(key=lambda x: number(f"menu|{gender}|{category}|{x['product_id']}", cfg))
        vocab = {f: sorted({x["attributes"][f]["value"] for x in candidates}) for f in FIELDS}
        if any(len(v) < 2 for v in vocab.values()):
            raise ValueError("Profile generation requires at least two labels per field")
        vocabs[str(pool_index)] = vocab
        profiles.extend(generate_profiles(vocab, pool_index, cfg))
        for menu_index in range(cfg["menus_per_pool"]):
            start = menu_index * cfg["items_per_menu"]
            selected = candidates[start:start + cfg["items_per_menu"]]
            if len(selected) != cfg["items_per_menu"]:
                raise ValueError("Not enough development items")
            items = [{"product_id": p["product_id"],
                      "attributes": {f: p["attributes"][f]["value"] for f in FIELDS},
                      "source_split": p["split"], "leakage_group_id": p["leakage_group_id"]} for p in selected]
            menus.append({"menu_id": f"M{pool_index}{menu_index}", "pool_index": pool_index,
                          "gender": gender, "category": category, "items": items})
    references, public_cases = [], []
    for profile in profiles:
        validate_disclosure(private_preferences(profile), vocabs[str(profile["pool_index"])])
        for menu in menus:
            if menu["pool_index"] != profile["pool_index"]:
                continue
            case_id = profile["profile_id"] + "__" + menu["menu_id"]
            a, z = evaluate_python(menu["items"], profile), evaluate_sql(menu["items"], profile)
            if a != z:
                raise ValueError("Independent evaluators disagree")
            references.append({"case_id": case_id, "profile_id": profile["profile_id"], "menu_id": menu["menu_id"], "reference": a})
            public_cases.append({"case_id": case_id, "menu_id": menu["menu_id"], "public_menu": menu})
    dump_rows(output / "public/menus.jsonl", menus)
    dump_rows(output / "public/cases.jsonl", public_cases)
    dump(output / "public/vocabularies.json", vocabs)
    dump_rows(output / "private/profiles.jsonl", profiles)
    dump_rows(output / "evaluator_only/references.jsonl", references)
    used = {x["product_id"] for m in menus for x in m["items"]}
    reserved = {x["product_id"] for x in source_items if x["split"] != "development"}
    if used & reserved:
        raise ValueError("Reserved item entered a development menu")
    summary = {"source_catalogue_records_scanned": len(source_items), "development_source_items": len(development),
               "profiles": len(profiles), "menus": len(menus), "cases": len(references),
               "menu_items": len(used), "reserved_items_transmitted_or_evaluated": 0,
               "reference_evaluators_agree": True,
               "reference_decisions": dict(collections.Counter(r["reference"]["decision"] for r in references)),
               "no_buy_reasons": dict(collections.Counter(r["reference"]["no_buy_reason"] for r in references if r["reference"]["decision"] == "NO_BUY")),
               "tied_favorite_cases": sum(len(r["reference"]["relative_favorite_ids"]) > 1 for r in references),
               "profile_outcome_filtering": False, "model_calls": 0}
    dump(BASE / "results/CONSTRUCTION.json", summary)
    return summary


def offline_episodes(prepared):
    profiles = {p["profile_id"]: p for p in rows(prepared / "private/profiles.jsonl")}
    cases = rows(prepared / "public/cases.jsonl")
    references = {r["case_id"]: r["reference"] for r in rows(prepared / "evaluator_only/references.jsonl")}
    vocabs = read(prepared / "public/vocabularies.json")
    episodes = []
    for case in cases:
        profile_id = case["case_id"].split("__")[0]
        for strategy in ["ask_all", "fieldwise"]:
            agent = PublicAgent(case["public_menu"], vocabs[str(case["public_menu"]["pool_index"])], strategy)
            user = ReferenceUser(profiles[profile_id])
            while (action := agent.next_action()) is not None:
                agent.observe(action, user.answer(action))
            final = agent.finish()
            episodes.append({"case_id": case["case_id"], "strategy": strategy,
                             "questions": len(agent.history), "final": final,
                             "correct": score_decision(final, references[case["case_id"]])})
    dump_rows(prepared.parent / "offline_reference_episodes.jsonl", episodes)
    summary = {"episodes": len(episodes), "correct": sum(e["correct"] for e in episodes),
               "strategies": {s: {"episodes": sum(e["strategy"] == s for e in episodes),
                                    "questions_per_episode": sorted({e["questions"] for e in episodes if e["strategy"] == s})}
                              for s in ["ask_all", "fieldwise"]},
               "scope": "lossless_reference_user_software_closure_only", "model_calls": 0,
               "method_superiority_established": False}
    dump(BASE / "results/OFFLINE_CLOSURE.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "offline"])
    parser.add_argument("--prepared", type=pathlib.Path, default=BASE / "artifacts/prepared")
    args = parser.parse_args()
    print(json.dumps(prepare(args.prepared) if args.mode == "prepare" else offline_episodes(args.prepared)))


if __name__ == "__main__":
    main()
