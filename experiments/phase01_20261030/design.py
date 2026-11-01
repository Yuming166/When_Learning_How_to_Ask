"""Deterministic private preference cards; no model-generated labels or rates."""
import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM = "Use the supplied decision policy and evidence only. Return exactly one digit, 0 or 1. Do not explain."
DOMAINS = [
    ("online_shopping", ["durability", "delivery_speed", "price", "privacy"]),
    ("content_feed", ["relevance", "novelty", "advertising", "source_quality"]),
    ("travel_booking", ["comfort", "flexibility", "price", "travel_time"]),
    ("cloud_service", ["uptime", "portability", "price", "data_control"]),
]
QUESTIONS = {
    "A": [
        "Evaluate the two complete options individually under the decision policy. Which option does the user prefer?",
        "Assess each complete candidate using the stated policy. Which candidate is preferred by this user?",
    ],
    "B": [
        "Compare the attribute differences between the options under the decision policy. Which option does the user prefer?",
        "Contrast the candidates attribute by attribute using the stated policy. Which candidate is preferred by this user?",
    ],
}


def sha(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()


def seed_for(*values):
    return int(sha(values)[:8], 16) % (2**31)


def read_jsonl(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows))


def utility(policy, values):
    if policy["kind"] == "weighted_sum":
        return sum(w * x for w, x in zip(policy["weights"], values))
    return tuple(policy["directions"][i] * values[i] for i in policy["priority"])


def decision(policy, options):
    left, right = (utility(policy, v) for v in options)
    if left == right:
        raise ValueError("Tied options are outside this binary decision benchmark")
    return int(right > left)


def contrast_decision(policy, options):
    """Separate difference-based evaluator to check the equivalent decision."""
    diff = [b - a for a, b in zip(*options)]
    if policy["kind"] == "weighted_sum":
        score = sum(policy["weights"][i] * diff[i] for i in range(len(diff)))
    else:
        score = next((policy["directions"][i] * diff[i] for i in policy["priority"] if diff[i]), 0)
    if score == 0:
        raise ValueError("Tied options")
    return int(score > 0)


def policy_text(policy, attributes):
    if policy["kind"] == "weighted_sum":
        return ("The user's utility is the sum of attribute value times its signed weight. "
                "Higher utility is preferred. Signed weights: " + "; ".join(
                    f"{a} = {w:+d}" for a, w in zip(attributes, policy["weights"])) + ".")
    return ("The user compares attributes in strict priority order, stopping at the first unequal attribute. "
            "Lower-priority attributes never override that comparison. Order and desired direction: " + "; ".join(
                f"{attributes[i]} ({'higher' if policy['directions'][i] > 0 else 'lower'} is better)"
                for i in policy["priority"]) + ".")


def parse_answer(raw):
    # No extracting a digit from explanations, truncations, or reasoning text.
    text = raw.strip()
    return int(text) if text in ("0", "1") else None


def make_dataset(config, stage):
    smoke = stage == "smoke"
    count = config["smoke_profiles" if smoke else "pilot_profiles"]
    root_seed = config["smoke_seed" if smoke else "pilot_seed"]
    reps = config["smoke_replicates" if smoke else "pilot_replicates"]
    private, requests, public = [], [], []
    for pi in range(count):
        pid = f"{stage}_p{pi:02d}"
        rng = random.Random(seed_for(root_seed, pi))
        domains = rng.sample(DOMAINS, 2)
        for gi, (domain, attrs) in enumerate(domains):
            gid = f"{pid}_g{gi}"
            policy = {"kind": rng.choice(["weighted_sum", "lexicographic"])}
            if policy["kind"] == "weighted_sum":
                policy["weights"] = [rng.choice([i for i in range(-7, 8) if i]) for _ in attrs]
            else:
                policy["priority"] = rng.sample(list(range(4)), 4)
                policy["directions"] = [rng.choice([-1, 1]) for _ in attrs]
            card = policy_text(policy, attrs)
            meta = {"profile_id": pid, "group_id": gid, "group_index": gi,
                    "domain": domain, "attributes": attrs, "group_size": 4}
            public.append(meta)
            for ji in range(4):
                item = f"{gid}_j{ji}"
                while True:
                    options = [[rng.randint(-12, 12) for _ in attrs] for _ in range(2)]
                    if utility(policy, options[0]) != utility(policy, options[1]):
                        break
                # Independent fair canonical answer bit; no forced balance across preferences.
                theta = rng.randrange(2)
                if decision(policy, options) != theta:
                    options.reverse()
                assert decision(policy, options) == contrast_decision(policy, options) == theta
                private.append({**meta, "preference_id": item, "preference_index": ji,
                                "policy": policy, "options": options, "theta": theta})
                for rep in range(reps):
                    template = rep if smoke else int(rep >= 4)
                    order = [0, 1] if (rep % 2 == 0) else [1, 0]
                    # Byte-identical evidence, option order, answer mapping for the paired formats.
                    evidence = "Private decision policy:\n" + card + "\nAttribute order: " + ", ".join(attrs) + ".\n"
                    evidence += "\n".join(f"Option {label}: " + ", ".join(
                        f"{a}={v}" for a, v in zip(attrs, options[canonical]))
                        for label, canonical in enumerate(order))
                    for fmt in ["A", "B"]:
                        request_id = f"{item}_{fmt}_r{rep}"
                        prompt = evidence + "\nQuestion: " + QUESTIONS[fmt][template] + "\nAnswer with the preferred option's digit."
                        requests.append({**meta, "request_id": request_id, "kind": "task",
                                         "preference_id": item, "preference_index": ji, "format": fmt,
                                         "replicate": rep, "template_id": f"{fmt}_t{template}",
                                         "template_index": template, "option_order": order,
                                         "evidence_sha256": sha(evidence.encode()),
                                         "system": SYSTEM, "prompt": prompt,
                                         "seed": seed_for(root_seed, request_id)})
            # Self report receives the private policy; metadata predictor receives only public data.
            # Both see the same two query descriptions, no outcomes or measured best-format label.
            for kind in ["direct", "metadata"]:
                for template in range(2):
                    mapping = ["A", "B"] if template == 0 else ["B", "A"]
                    evidence = ("Private decision policy:\n" + card if kind == "direct" else
                                "Public group metadata only:\n" + json.dumps({k: meta[k] for k in ["domain", "attributes", "group_size"]}))
                    descriptions = "\n".join(f"Format {i}: {QUESTIONS[fmt][template]}" for i, fmt in enumerate(mapping))
                    prompt = (evidence + "\n" + descriptions +
                              "\nPredict which format will produce more correct preference answers for this group. "
                              "No feedback is available. Answer with that format's digit, 0 or 1.")
                    rid = f"{gid}_{kind}_t{template}"
                    requests.append({**meta, "request_id": rid, "kind": kind, "replicate": template,
                                     "template_id": f"{kind}_t{template}", "template_index": template,
                                     "format_order": mapping, "system": SYSTEM, "prompt": prompt,
                                     "seed": seed_for(root_seed, rid)})
    random.Random(seed_for(root_seed, "request_order")).shuffle(requests)
    return private, requests, public


def validate(private, requests, config, stage):
    tasks = [r for r in requests if r["kind"] == "task"]
    lookup = {r["preference_id"]: r for r in private}
    pairs = {}
    target_counts = [0, 0]
    length_gaps = []
    for r in tasks:
        p = lookup[r["preference_id"]]
        assert decision(p["policy"], p["options"]) == contrast_decision(p["policy"], p["options"]) == p["theta"]
        assert not any(k in r for k in ["theta", "correct", "best_format", "policy"])
        target_counts[r["option_order"].index(p["theta"])] += 1
        pairs.setdefault((r["preference_id"], r["replicate"]), []).append(r)
    for pair in pairs.values():
        a, b = sorted(pair, key=lambda r: r["format"])
        assert a["evidence_sha256"] == b["evidence_sha256"]
        assert a["prompt"].split("\nQuestion:")[0] == b["prompt"].split("\nQuestion:")[0]
        assert a["option_order"] == b["option_order"]
        length_gaps.append(abs(len(a["prompt"]) - len(b["prompt"])))
    assert target_counts[0] == target_counts[1]
    assert len(set(r["request_id"] for r in requests)) == len(requests)
    assert len(set(r["seed"] for r in requests)) == len(requests)
    expected_profiles = config["smoke_profiles" if stage == "smoke" else "pilot_profiles"]
    expected_reps = config["smoke_replicates" if stage == "smoke" else "pilot_replicates"]
    assert len(private) == expected_profiles * 8
    assert len(tasks) == expected_profiles * 8 * 2 * expected_reps
    assert len(requests) == len(tasks) + expected_profiles * 2 * 2 * 2
    return {"pass": True, "stage": stage, "profiles": expected_profiles, "preferences": len(private),
            "task_requests": len(tasks), "auxiliary_requests": len(requests) - len(tasks),
            "total_requests": len(requests), "answer_label_counts": target_counts,
            "max_format_character_gap": max(length_gaps),
            "scope": "Construction and evaluator equivalence; not proof of LLM semantic comprehension"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["smoke", "pilot"])
    args = ap.parse_args()
    config = json.loads((ROOT / "config.json").read_text())
    out = ROOT / "data" / args.stage
    if out.exists():
        raise SystemExit("Refuse to overwrite generated data")
    private, requests, public = make_dataset(config, args.stage)
    receipt = validate(private, requests, config, args.stage)
    out.mkdir(parents=True)
    write_jsonl(out / "private_truth.jsonl", private)
    write_jsonl(out / "requests.jsonl", requests)
    write_jsonl(out / "public_metadata.jsonl", public)
    write_json(out / "construction_checks.json", receipt)
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
