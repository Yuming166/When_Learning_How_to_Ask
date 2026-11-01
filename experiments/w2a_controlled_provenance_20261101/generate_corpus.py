#!/usr/bin/env python3
"""Privileged fixture construction and independent DOM audit; no networking/inference."""
import argparse
import collections
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import secrets

HERE = Path(__file__).resolve().parent
MARKER = "SIMULATED CONTROLLED FIXTURE — NOT A REAL WEB PAGE"
FAMILIES = ("assertion", "assertion", "attributed", "mixed", "not_addressed")


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(blob):
    return hashlib.sha256(blob).hexdigest()


def keyed(seed, domain, *parts):
    return hashlib.sha256((seed + "|" + domain + "|" + "|".join(map(str, parts))).encode()).digest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(row) + "\n" for row in rows))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def parent_stat_digest():
    # Read metadata only. W1 and W1.1 contents are not corpus inputs.
    result = {}
    for rel in json.loads((HERE / "PROTOCOL.json").read_text())["parent_evidence"]:
        root = HERE / rel
        entries = []
        for p in sorted(root.rglob("*")):
            if p.is_file():
                s = p.stat()
                entries.append([str(p.relative_to(root)), s.st_size, s.st_mtime_ns])
        result[rel] = {"files": len(entries), "size_mtime_manifest_sha256": digest_bytes(canonical(entries).encode())}
    return result


def statement_text(s):
    return (f"SPEAKER {s['speaker']} ASSERTS TARGET {s['target']} VALUE {s['value']} "
            f"ADOPTION {int(s['publisher_adoption'])} RELATION {s['relation']} "
            f"ROOT {s['root_id']} ROLE {s['role']}.")


def render(doc):
    rows = []
    for s in doc["statements"]:
        attrs = {"speaker": s["speaker"], "target": s["target"], "value": s["value"],
                 "adoption": int(s["publisher_adoption"]), "relation": s["relation"],
                 "root": s["root_id"], "role": s["role"]}
        attr = " ".join(f'data-{k}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())
        rows.append(f'<p class="typed-statement" {attr}>{html.escape(statement_text(s))}</p>')
    options = "".join(f"<li>{v}</li>" for v in doc["answer_order"])
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "identifier": doc["page_id"],
          "isBasedOn": "urn:simulated-root:" + doc["root_id"], "genre": "controlled-simulation"}
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
            f"<title>Simulated registry {doc['page_id']}</title>\n"
            f'<script type="application/ld+json">{canonical(ld)}</script></head>\n'
            f'<body><aside class="simulation-marker">{MARKER}</aside>\n'
            f'<article data-page-id="{doc["page_id"]}" data-target="{doc["target"]}" '
            f'data-root="{doc["root_id"]}" data-profile-id="{doc["profile_id"]}">\n'
            f'<h1>Fictional registry statement</h1><p>Target: {doc["target"]}</p>\n'
            + "\n".join(rows) + f"\n<ol class=\"answer-order\">{options}</ol>\n"
            "</article></body></html>\n")


def generate(out, initialize):
    private = out / "evaluator_only"
    private.mkdir(parents=True, exist_ok=True)
    seed_path = private / "seed.txt"
    if not seed_path.exists():
        if not initialize:
            raise ValueError("Missing evaluator seed; use --initialize once, then retain seed.txt")
        seed_path.write_text(secrets.token_hex(32) + "\n")
        seed_path.chmod(0o600)
    seed = seed_path.read_text().strip()
    docs, public, gold, ledger, roots, facts = [], [], [], [], [], []
    for p in range(24):
        profile = f"profile_{p:02d}"
        true_facts = set(sorted(range(8), key=lambda f: keyed(seed, "truth", p, f))[:4])
        yes_first = set(sorted(range(8), key=lambda f: keyed(seed, "order", p, f))[:4])
        for f in range(8):
            fid = f"fact_{p:02d}_{f}"
            target = f"fictional_item_{p:02d}_{f}.permit_active"
            theta = int(f in true_facts)
            order = ["YES", "NO"] if f in yes_first else ["NO", "YES"]
            facts.append({"profile_id": profile, "fact_id": fid, "target": target,
                          "question": f"Does {target} hold?", "answer_order": order,
                          "simulation_marker": MARKER})
            for r in range(4):
                root = "root_" + keyed(seed, "root-id", p, f, r).hex()[:24]
                # Seeded independent source-noise construction, not an empirical independence test.
                correct = int.from_bytes(keyed(seed, "source-draw", p, f, r), "big") < 3 * (2 ** 254)
                report = theta if correct else 1 - theta
                family = FAMILIES[(p * 8 * 4 + f * 4 + r) % len(FAMILIES)]
                topology = "same_root_three_copies" if r == 0 else "three_distinct_roots"
                source = "origin_" + root.removeprefix("root_")
                s = {"speaker": source, "target": target, "value": report,
                     "publisher_adoption": family != "attributed", "relation": "ORIGIN_REPORT",
                     "root_id": root, "role": "PRIMARY_REPORT"}
                statements = [s]
                if family == "attributed":
                    s["relation"] = "ATTRIBUTED_ORIGIN_REPORT"
                elif family == "mixed":
                    statements.append({"speaker": "quoted_challenger", "target": target,
                                       "value": 1 - report, "publisher_adoption": False,
                                       "relation": "CONTROLLED_COUNTERSTATEMENT_OF_ROOT",
                                       "root_id": root, "role": "DEPENDENT_DISTRACTOR"})
                elif family == "not_addressed":
                    statements = [{"speaker": source, "target": target + ".auxiliary",
                                   "value": keyed(seed, "auxiliary", p, f, r)[0] % 2,
                                   "publisher_adoption": True, "relation": "UNRELATED_FIXTURE_STATEMENT",
                                   "root_id": root, "role": "IRRELEVANT"}]
                if family == "assertion":
                    semantic = "ASSERT_SUPPORT" if report else "ASSERT_REFUTE"
                else:
                    semantic = {"attributed": "ATTRIBUTED_ONLY", "mixed": "MIXED",
                                "not_addressed": "NOT_ADDRESSED"}[family]
                roots.append({"root_id": root, "profile_index": p, "fact_index": f, "root_index": r,
                              "theta": theta, "V": report, "source_correct": correct, "source_r": 0.75,
                              "semantic_family": family, "sampling_note": "hash-keyed seeded source-noise fixture"})
                for copy in range(3 if r == 0 else 1):
                    pid = f"page_{p:02d}_{f}_{r}_{copy}"
                    doc = {"simulation_marker": MARKER, "page_id": pid, "profile_id": profile,
                           "fact_id": fid, "target": target, "root_id": root, "answer_order": order,
                           "statements": statements}
                    blob = render(doc)
                    dest = out / "reader_visible" / "pages" / (pid + ".html")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(blob)
                    docs.append(doc)
                    public.append({"simulation_marker": MARKER, "page_id": pid, "profile_id": profile,
                                   "fact_id": fid, "target": target, "declared_root_id": root,
                                   "topology": topology, "copy_index": copy,
                                   "reader_document": "reader_visible/pages/" + pid + ".html",
                                   "simulated_url": "https://simulated.example.invalid/" + pid + ".html"})
                    gold.append({"page_id": pid, "theta": theta, "V_root": report,
                                 "source_correct": correct, "semantic_label": semantic,
                                 "publisher_binary_stance": report if family == "assertion" else None,
                                 "primary_report_visible": family != "not_addressed",
                                 "html_sha256": digest_bytes(blob.encode()),
                                 "statement_sha256": digest_bytes(canonical(statements).encode())})
                    ledger.append({"page_id": pid, "root_id": root, "target": target,
                                   "controlled_operation": "RETAIN" if correct else "FLIP_BINARY_REPORT",
                                   "before_value": theta, "after_source_report": report,
                                   "wrapper": family, "copy_of_same_root": r == 0 and copy > 0,
                                   "simulated_not_natural_error": True})
    write_jsonl(out / "selector_visible" / "manifest.jsonl", public)
    write_jsonl(out / "selector_visible" / "facts.jsonl", facts)
    write_jsonl(out / "reader_visible" / "records.jsonl", docs)
    write_jsonl(private / "roots.jsonl", roots)
    write_jsonl(private / "gold.jsonl", gold)
    write_jsonl(private / "edit_ledger.jsonl", ledger)
    write_json(private / "config.json", {"profiles": 24, "facts_per_profile": 8,
        "source_r": "3/4", "seed_file": "seed.txt", "truth_rule": "First 4 of 8 SHA256 ranks of seed|truth|p|f",
        "seed_and_rule_are_evaluator_only": True, "probability_interpretation": "Finite fixtures; theoretical law enumerations are separate"})


class IndependentParser(HTMLParser):
    """Reconstruct statements from DOM and visible grammar, not generator gold."""
    def __init__(self):
        super().__init__()
        self.statements, self.article, self.current, self.text, self.marker = [], {}, None, [], []
        self.in_marker = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.article = attrs
        if tag == "aside":
            self.in_marker = True
        if tag == "p" and attrs.get("class") == "typed-statement":
            self.current, self.text = attrs, []

    def handle_data(self, data):
        if self.current is not None:
            self.text.append(data)
        if self.in_marker:
            self.marker.append(data)

    def handle_endtag(self, tag):
        if tag == "aside":
            self.in_marker = False
        if tag == "p" and self.current is not None:
            a = self.current
            visible = "".join(self.text)
            m = re.fullmatch(r"SPEAKER (\S+) ASSERTS TARGET (\S+) VALUE ([01]) ADOPTION ([01]) RELATION (\S+) ROOT (\S+) ROLE (\S+)\.", visible)
            if not m:
                raise ValueError("Visible grammar invalid")
            speaker, target, value, adoption, relation, root, role = m.groups()
            expected = {"data-speaker": speaker, "data-target": target, "data-value": value,
                        "data-adoption": adoption, "data-relation": relation, "data-root": root, "data-role": role}
            assert all(a[k] == v for k, v in expected.items()), "DOM/text disagreement"
            self.statements.append({"speaker": speaker, "target": target, "value": int(value),
                                    "publisher_adoption": adoption == "1", "relation": relation,
                                    "root_id": root, "role": role})
            self.current = None


def independently_recompute_truth(seed, p, f):
    # Deliberately does not call keyed(), generate(), or read theta from gold.
    ranks = []
    for item in range(8):
        raw = (seed + "|truth|" + str(p) + "|" + str(item)).encode("utf-8")
        ranks.append((hashlib.sha256(raw).hexdigest(), item))
    ranks.sort()
    return int(any(item == f for _, item in ranks[0:4]))


def classify(parsed):
    relevant = [s for s in parsed.statements if s["target"] == parsed.article["data-target"]]
    if not relevant:
        return "NOT_ADDRESSED", None
    values = {s["value"] for s in relevant}
    if len(values) > 1:
        return "MIXED", None
    if not any(s["publisher_adoption"] for s in relevant):
        return "ATTRIBUTED_ONLY", None
    value = next(iter(values))
    return ("ASSERT_SUPPORT" if value else "ASSERT_REFUTE"), value


def check(out, before, write_reports=True):
    private = out / "evaluator_only"
    seed = (private / "seed.txt").read_text().strip()
    gold = {x["page_id"]: x for x in read_jsonl(private / "gold.jsonl")}
    docs = {x["page_id"]: x for x in read_jsonl(out / "reader_visible" / "records.jsonl")}
    manifests = read_jsonl(out / "selector_visible" / "manifest.jsonl")
    facts = read_jsonl(out / "selector_visible" / "facts.jsonl")
    roots = read_jsonl(private / "roots.jsonl")
    ledger = {x["page_id"]: x for x in read_jsonl(private / "edit_ledger.jsonl")}
    forbidden = {"theta", "V", "V_root", "source_correct", "correctness", "gold", "edit_ledger", "semantic_label", "seed", "truth_rule", "statements", "value"}
    for row in manifests + facts:
        assert not forbidden.intersection(row), "Evaluator or document content in selector input"
    assert len(manifests) == 1152 and len(roots) == 768 and len(facts) == 192
    assert len(list((out / "reader_visible" / "pages").glob("*.html"))) == 1152
    assert len(set(gold)) == len(gold) == len(docs) == len(manifests) == len(ledger)
    labels, groups, fact_balance, order_balance = collections.Counter(), collections.defaultdict(list), collections.defaultdict(list), collections.Counter()
    copies_checked = 0
    for row in manifests:
        pid = row["page_id"]
        blob = (out / row["reader_document"]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == gold[pid]["html_sha256"]
        parser = IndependentParser()
        parser.feed(blob.decode())
        assert "".join(parser.marker) == MARKER
        assert parser.article["data-root"] == row["declared_root_id"]
        assert parser.statements == docs[pid]["statements"]
        semantic, stance = classify(parser)
        assert semantic == gold[pid]["semantic_label"]
        assert stance == gold[pid]["publisher_binary_stance"]
        labels[semantic] += 1
        p, f, r, copy = map(int, pid.removeprefix("page_").split("_"))
        theta = independently_recompute_truth(seed, p, f)
        assert theta == gold[pid]["theta"]
        # Independently regenerate the source noise threshold and compare it to parsed primary statements.
        raw = (seed + "|source-draw|" + str(p) + "|" + str(f) + "|" + str(r)).encode()
        keep = int(hashlib.sha256(raw).hexdigest(), 16) < 3 * 2 ** 254
        value = theta if keep else 1 - theta
        assert value == gold[pid]["V_root"] and keep == gold[pid]["source_correct"]
        edit = ledger[pid]
        assert edit["before_value"] == theta and edit["after_source_report"] == value
        assert edit["controlled_operation"] == ("RETAIN" if keep else "FLIP_BINARY_REPORT")
        assert edit["root_id"] == row["declared_root_id"]
        assert edit["target"] == row["target"] and edit["simulated_not_natural_error"]
        assert edit["copy_of_same_root"] == (r == 0 and copy > 0)
        for s in parser.statements:
            assert s["root_id"] == row["declared_root_id"]
            if s["role"] == "PRIMARY_REPORT":
                assert s["value"] == value
            if s["role"] == "DEPENDENT_DISTRACTOR":
                assert s["value"] == 1 - value and not s["publisher_adoption"]
        groups[row["declared_root_id"]].append((pid, canonical(parser.statements)))
    for root, pages in groups.items():
        assert len(pages) in (1, 3)
        if len(pages) == 3:
            assert len({content for _, content in pages}) == 1
            copies_checked += 1
    for f in facts:
        p, item = map(int, f["fact_id"].removeprefix("fact_").split("_"))
        fact_balance[p].append(independently_recompute_truth(seed, p, item))
        order_balance[(p, f["answer_order"][0])] += 1
    assert all(len(v) == 8 and sum(v) == 4 for v in fact_balance.values())
    assert all(order_balance[(p, answer)] == 4 for p in range(24) for answer in ("YES", "NO"))
    assert set(labels) == {"ASSERT_SUPPORT", "ASSERT_REFUTE", "ATTRIBUTED_ONLY", "MIXED", "NOT_ADDRESSED"}
    assert copies_checked == 192
    for p in range(24):
        for f in range(8):
            selected = [x for x in manifests if x["fact_id"] == f"fact_{p:02d}_{f}"]
            assert len({x["declared_root_id"] for x in selected if x["topology"] == "three_distinct_roots"}) == 3
            assert len({x["declared_root_id"] for x in selected if x["topology"] == "same_root_three_copies"}) == 1
    # Non-mirroring mutation checks: evaluator must reject inconsistent visible text/DOM.
    sample = next(x for x in manifests if gold[x["page_id"]]["semantic_label"] == "ASSERT_SUPPORT")
    html_sample = (out / sample["reader_document"]).read_text()
    malformed = html_sample.replace("VALUE 1 ADOPTION", "VALUE 0 ADOPTION", 1)
    rejected = False
    try:
        IndependentParser().feed(malformed)
    except (ValueError, AssertionError):
        rejected = True
    assert rejected, "DOM/text mutation was not rejected"
    after = parent_stat_digest()
    assert before == after, "Read-only parent metadata changed during corpus execution"
    inventory = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.json":
            inventory.append({"path": str(p.relative_to(out)), "sha256": digest_bytes(p.read_bytes())})
    if write_reports:
        write_json(private / "SHA256SUMS.json", inventory)
    else:
        assert json.loads((private / "SHA256SUMS.json").read_text()) == inventory
    checks = {"status": "PASS", "profiles": 24, "facts": 192, "HTML_pages": 1152,
        "experiment_model_calls": 0, "new_web_requests": 0, "roots": 768,
        "same_root_triplets_checked": copies_checked, "three_distinct_roots_per_fact_checked": 192,
        "truth_labels": {"0": 96, "1": 96}, "per_profile_truth_balance": "4/4",
        "per_profile_answer_order_balance": "4 YES-first / 4 NO-first", "semantic_page_counts": dict(labels),
        "source_error_root_counts": dict(collections.Counter("correct" if x["source_correct"] else "corrupted" for x in roots)),
        "all_statement_DOM_text_record_checks": True, "independent_truth_recomputation": True,
        "source_draw_recomputation": True, "copy_statement_hash_agreement": True,
        "edit_ledger_independently_checked": True,
        "selector_schema_forbidden_fields_absent": True, "DOM_text_disagreement_mutation_rejected": rejected,
        "parent_read_only_guard": {"method": "recursive file size/mtime metadata digest; no parent content used", "before": before, "after": after},
        "protocol_sha256": digest_bytes((HERE / "PROTOCOL.json").read_bytes()),
        "generator_sha256": digest_bytes(Path(__file__).read_bytes()),
        "corpus_inventory_sha256": digest_bytes((private / "SHA256SUMS.json").read_bytes()),
        "example_HTML": "corpus/" + sample["reader_document"],
        "scope": "Construction checks only; not Qwen performance, natural reliability, statistical-independence evidence, or iid-truth evidence"}
    if write_reports:
        write_json(HERE / "CORPUS_CHECKS.json", checks)
    print(json.dumps({k: checks[k] for k in ("status", "HTML_pages", "roots", "semantic_page_counts", "experiment_model_calls")}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initialize", action="store_true", help="Create evaluator-only random seed once; saved seed makes future builds deterministic")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--verify-only", action="store_true", help="Read-only construction/inventory verification; do not regenerate or rewrite reports")
    parser.add_argument("--output", type=Path, default=HERE / "corpus")
    args = parser.parse_args()
    before = parent_stat_digest()
    if args.verify_only and args.initialize:
        parser.error("--verify-only cannot initialize a corpus")
    if not args.check_only and not args.verify_only:
        generate(args.output, args.initialize)
    check(args.output, before, write_reports=not args.verify_only)


if __name__ == "__main__":
    main()
