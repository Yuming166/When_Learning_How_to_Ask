"""Zero-model-call audit and conservative binary extraction from UserBench.

This does not run the upstream environment, import its API clients, or measure
Qwen reliability. Mutually exclusive contrasts are an explicit narrow audit
allow-list, not an assertion that all other preferences cannot be adapted.
"""
import argparse
import ast
import collections
import copy
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Tuple, List

ROOT = Path(__file__).resolve().parent
PIN = "80506d2ab484cab843e60a2401ff3e0290d05b87"
PAIRS = [
    ("flight", "path", "prefer direct flight", "prefer one-stop layover flight"),
    ("flight", "company", "prefer consistent airline brand along all flights", "prefer different airline brand along different flights"),
    ("hotel", "room", "prefer King room", "prefer Double room"),
    ("rental_car", "model", "prefer electric car", "prefer gasoline car"),
    ("restaurant", "expectation", "prefer having cheap restaurant", "prefer having expensive restaurant"),
    ("apartment", "room", "prefer only one bedroom", "prefer having at least three bedrooms"),
]


def sha(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def public_observation(observation):
    """Only conversational feedback is a task observation in this adapter."""
    feedback = observation.get("feedback")
    step = observation.get("step_count")
    if not isinstance(feedback, str) or not isinstance(step, int):
        raise ValueError("Malformed public feedback")
    return {"feedback": feedback, "step_count": step}


def exclusive_labels(row):
    results = []
    for aspect, category, left, right in PAIRS:
        if aspect not in row["dimensions"]:
            continue
        active = {p[2] for p in row[aspect]["preferences"]}
        present = [left in active, right in active]
        # Absence of both is unknown; presence of both is conflict, never coerced.
        if sum(present) != 1:
            continue
        results.append({"aspect": aspect, "category": category,
                        "alternatives": [left, right], "theta": int(present[1])})
    return results


def probe_native_reset(source, row, scenario_id):
    """Execute only five AST-extracted pure reset methods, never upstream imports."""
    import numpy as np
    tree = ast.parse((source / "travelgym/env/travel_env.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TravelEnv")
    names = {"reset", "_initialize_preferences", "_initialize_state_list", "_calculate_elicitation_ratio", "_get_remaining_preferences_summary"}
    methods = [copy.deepcopy(n) for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in methods} == names
    namespace = {"Any": Any, "Dict": Dict, "Tuple": Tuple, "List": List, "random": random, "np": np}
    exec(compile(ast.Module(body=methods, type_ignores=[]), "upstream_reset_methods", "exec"), namespace)
    task = {"id": scenario_id, "scenario": row["scenario"], "initial_desc": row["initial_description"],
            "dimensions": row["dimensions"], "preferences": row}
    attrs = {name: namespace[name] for name in names}
    attrs["_get_next_task"] = lambda self: task
    NativeReset = type("NativeResetOnly", (), attrs)
    env = NativeReset()
    env.config = SimpleNamespace(verbose=False)
    obs, info = env.reset(seed=93017)
    safe = public_observation(obs)
    return {"probe_scope": "Unmodified upstream method AST; imports/LLM clients/steps never executed",
            "task_description_equals_full_private_scenario": obs["task_description"] == row["scenario"],
            "private_summary_count": len(info["preferences_summary"]),
            "private_summary_example": info["preferences_summary"][:2],
            "observation_keys": sorted(obs), "info_keys": sorted(info),
            "public_projection_keys": sorted(safe),
            "public_feedback_equals_initial_description": safe["feedback"] == row["initial_description"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/home/gaoym/userbench-source-20261030"))
    ap.add_argument("--output", type=Path, default=ROOT)
    args = ap.parse_args()
    source, out = args.source, args.output
    out.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    assert commit == PIN, "Source version drift"
    assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=source, text=True).strip()
    import pyarrow.parquet as pq
    import pyarrow
    rows, file_counts, file_hashes = {}, {}, {}
    for f in sorted((source / "travelgym/data").glob("*.json")):
        contents = f.read_bytes()
        data = json.loads(contents)
        assert not set(rows) & set(data)
        rows.update(data)
        file_counts[f.name] = len(data)
        file_hashes[str(f.relative_to(source))] = sha(contents)
    splits = {"train": set(), "test": set()}
    split_counts, split_prompts = {}, {}
    for f in sorted((source / "data").glob("*_multiturn_onechoice/*.parquet")):
        data = pq.read_table(f).to_pylist()
        ids = [r["reward_model"]["id"] for r in data]
        assert len(ids) == len(set(ids))
        assert not splits[f.stem] & set(ids)
        splits[f.stem].update(ids)
        split_counts[str(f.relative_to(source))] = len(data)
        file_hashes[str(f.relative_to(source))] = sha(f.read_bytes())
        for r in data:
            split_prompts[r["reward_model"]["id"]] = r["prompt"]
        # Single-/multi-choice presentation variants must not count as independent profiles.
        other = source / "data" / f.parent.name.replace("_onechoice", "") / f.name
        other_ids = {r["reward_model"]["id"] for r in pq.read_table(other).to_pylist()}
        assert other_ids == set(ids)
    assert not splits["train"] & splits["test"]
    assert splits["train"] | splits["test"] == set(rows)
    ontology, cues = collections.defaultdict(set), collections.defaultdict(set)
    bundles, pref_sets, cue_sets = {}, {}, {}
    n_prefs, group_size = collections.Counter(), collections.Counter()
    literal_opening_hits = []
    native_option_issues = collections.Counter()
    all_items, extracted_per_profile, eligible_groups = [], collections.Counter(), collections.Counter()
    pair_counts = collections.defaultdict(collections.Counter)
    for sid, row in rows.items():
        split = "train" if sid in splits["train"] else "test"
        bundle_set, pref_set, cue_set = set(), set(), set()
        total = 0
        private_card = []
        for aspect in row["dimensions"]:
            data = row[aspect]
            prefs = data["preferences"]
            total += len(prefs)
            group_size[len(prefs)] += 1
            bundle_set.add(sha([aspect, prefs]))
            for p in prefs:
                key = tuple(p[:3])
                cue = tuple(p[:4])
                ontology[aspect].add(key)
                cues[aspect].add(cue)
                pref_set.add(key); cue_set.add(cue)
                private_card.append({"aspect": p[0], "category": p[1], "preference": p[2], "implicit_cue": p[3]})
                if p[2].lower() in row["initial_description"].lower() or p[3].lower() in row["initial_description"].lower():
                    literal_opening_hits.append(sid)
            option_ids = [p["id"] for options in data["options"].values() for p in options]
            if len(option_ids) != len(set(option_ids)):
                native_option_issues["duplicate_option_id_in_aspect"] += 1
            if not set(data["correct_ids"]) <= set(option_ids):
                native_option_issues["correct_id_missing_from_options"] += 1
            if data["best_id"] not in data["correct_ids"]:
                native_option_issues["best_id_not_correct"] += 1
        n_prefs[total] += 1
        bundles[sid], pref_sets[sid], cue_sets[sid] = bundle_set, pref_set, cue_set
        contrasts = exclusive_labels(row)
        extracted_per_profile[len(contrasts)] += 1
        by_aspect = collections.Counter(x["aspect"] for x in contrasts)
        eligible_groups.update(by_aspect.values())
        for c in contrasts:
            pair = c["aspect"] + "/" + c["category"]
            pair_counts[pair][f"{split}_theta{c['theta']}"] += 1
            all_items.append({"scenario_id": sid, "opaque_profile_id": sha([PIN, sid])[:16], "official_split": split,
                              **c, "private_card": private_card, "initial_description": row["initial_description"]})
    overlap = {}
    for label, mapping in [("exact_preference", pref_sets), ("exact_preference_and_cue", cue_sets), ("exact_aspect_bundle", bundles)]:
        train = set().union(*(mapping[s] for s in splits["train"]))
        test = set().union(*(mapping[s] for s in splits["test"]))
        overlap[label] = {"train_distinct": len(train), "test_distinct": len(test), "shared_distinct": len(train & test),
                          "test_distinct_already_in_train_fraction": len(train & test) / len(test),
                          "test_profiles_with_any_shared": sum(bool(mapping[s] & train) for s in splits["test"])}
    leakage_probe_id = min(splits["train"], key=lambda s: sha(["probe", s]))
    probe = probe_native_reset(source, rows[leakage_probe_id], leakage_probe_id)
    selected = sorted((x for x in all_items if x["official_split"] == "train"), key=lambda x: sha(["audit_preview", x["scenario_id"], x["aspect"], x["category"]]))[:8]
    previews = []
    truths = []
    for i, item in enumerate(selected):
        # No response generation. These are construction previews only.
        order = [0, 1] if i % 2 == 0 else [1, 0]
        alternatives = [item["alternatives"][j].removeprefix("prefer ") for j in order]
        evidence = "The two alternatives are otherwise identical. Compare only the stated feature.\n" + "\n".join(f"Option {j}: {v}" for j, v in enumerate(alternatives))
        public = {"profile_id": item["opaque_profile_id"], "group": item["aspect"], "category": item["category"],
                  "options": alternatives, "common_evidence": evidence,
                  "A": "Which of these two alternatives matches your stated preference? Answer only 0 or 1.",
                  "B": "If choosing between these otherwise identical options, which would you select under your stated preference? Answer only 0 or 1."}
        previews.append(public)
        truths.append({"profile_id": item["opaque_profile_id"], "group": item["aspect"], "category": item["category"],
                       "ground_truth_digit": order.index(item["theta"]), "private_card": item["private_card"],
                       "source_scenario_id": item["scenario_id"], "semantic_alternatives": item["alternatives"],
                       "source_theta": item["theta"]})
    # Do not pretend eight preview rows are independent profiles.
    preview_scope = {"items": len(previews), "distinct_profiles": len({r["profile_id"] for r in previews}),
                     "scope": "TRAIN-only construction previews; no model responses and no reliability measurements"}
    summary = {"upstream_commit": PIN, "model_calls": 0, "upstream_modified": False, "pyarrow": pyarrow.__version__,
               "scenario_count": len(rows), "official_splits": {k: len(v) for k, v in splits.items()},
               "scenario_id_overlap": 0, "per_json_counts": file_counts, "parquet_counts": split_counts,
               "native_preference_counts_per_scenario": dict(sorted(n_prefs.items())),
               "native_group_sizes": dict(sorted(group_size.items())),
               "distinct_preferences_by_aspect": {k: len(v) for k, v in ontology.items()},
               "distinct_preference_cue_pairs_by_aspect": {k: len(v) for k, v in cues.items()},
               "distinct_exact_cue_texts": len({c[3] for values in cues.values() for c in values}),
               "cross_split_reuse": overlap,
               "literal_preference_or_cue_in_initial_description_profiles": len(set(literal_opening_hits)),
               "literal_scan_limit": "Exact string scan only, not a semantic non-leakage certificate",
               "native_option_structural_issues": dict(native_option_issues),
               "conservative_binary_extraction": {"definition": "Exactly one explicitly active value from one of six predeclared mutually exclusive contrasts; absence remains unknown",
                   "items": len(all_items), "scenario_item_count_histogram": dict(sorted(extracted_per_profile.items())),
                   "group_item_count_histogram_for_nonempty_groups": dict(sorted(eligible_groups.items())),
                   "pair_value_counts": {k: dict(v) for k, v in pair_counts.items()},
                   "limit": "Narrow allow-list coverage, not a bound on all possible alternative adaptations"},
               "reset_leakage_probe": probe, "preview": preview_scope,
               "findings": {"native_environment": "REVISE; cannot directly validate unknown binary reliability channels",
                            "data_source": "CONDITIONAL_GO_FOR_ADAPTATION; empirical reliability not measured"},
               "source_data_sha256": file_hashes}
    write_json(out / "audit_summary.json", summary)
    write_jsonl(out / "preference_catalog.jsonl", [dict(aspect=a, category=p[1], preference=p[2], cue_count=sum(tuple(c[:3]) == p for c in cues[a])) for a in sorted(ontology) for p in sorted(ontology[a])])
    write_jsonl(out / "preview_public.jsonl", previews)
    write_jsonl(out / "preview_private.jsonl", truths)
    write_json(out / "source_manifest.json", {"repository": "https://github.com/SalesforceAIResearch/UserBench", "commit": commit,
               "source_path": str(source), "files": {str(p.relative_to(source)): sha(p.read_bytes()) for p in sorted(source.rglob('*')) if p.is_file() and '.git' not in p.parts}})
    print(json.dumps({k: v for k, v in summary.items() if k not in ["source_data_sha256", "parquet_counts", "per_json_counts"]}, indent=2))


if __name__ == "__main__":
    main()
