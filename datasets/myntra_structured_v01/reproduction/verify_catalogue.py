"""Independent source-fidelity and leakage checks; no constructor import/network."""
import argparse
import collections
import csv
import hashlib
import html
import io
import json
import pathlib
import unicodedata

BASE = pathlib.Path(__file__).resolve().parent
SOURCE_NAME = "marketing_sample_for_myntra_com-ecommerce__20190601_20190831__15k_data.csv"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normal(value):
    value = unicodedata.normalize("NFKC", html.unescape(value))
    for char in "‐‑‒–—−":
        value = value.replace(char, "-")
    return " ".join(value.split()).lower()


def read_jsonl(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def verify(source, output):
    checks = collections.Counter()

    def require(ok, category, detail=""):
        if not ok:
            raise AssertionError(f"{category}: {detail}")
        checks[category] += 1

    cfg = json.loads((BASE / "config.json").read_text())
    raw = source.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == cfg["source_sha256"], "source_hash")
    decoded = raw.decode("utf-8-sig")
    table = list(csv.reader(io.StringIO(decoded)))
    header, body = table[0], table[1:]
    live = {i: cells for i, cells in enumerate(body, 2) if any(x.strip() for x in cells)}
    rawdict = {i: dict(zip(header, cells)) for i, cells in live.items()}
    variants = read_jsonl(output / "variants.jsonl")
    claims = read_jsonl(output / "source_claims.jsonl")
    products = read_jsonl(output / "products_all.jsonl")
    strict = read_jsonl(output / "catalogue_strict.jsonl")
    cards = read_jsonl(output / "factual_cards.jsonl")
    accounting = json.loads((output / "source_record_accounting.json").read_text())
    manifest = json.loads((output / "MANIFEST.json").read_text())
    splits = json.loads((output / "split_manifest.json").read_text())
    summary = json.loads((output / "SUMMARY.json").read_text())
    ids = {p["product_id"] for p in products}
    require(len(body) == cfg["expected_source_rows"], "record_denominator")
    require(len(body) == len(variants) + len(accounting["blank_source_records"]) + len(accounting["invalid_records"]), "record_accounting")
    require({v["source_record"] for v in variants}.union(x["source_record"] for x in accounting["invalid_records"]) == set(live), "nonempty_record_coverage")
    require({i for i, row in enumerate(body, 2) if not any(x.strip() for x in row)} == set(accounting["blank_source_records"]), "blank_record_coverage")
    require(ids == {r["product_id"] for r in rawdict.values()}, "product_identity_coverage")
    require(len(ids) == len(products), "one_record_per_product")
    require(len({v["variant_id"] for v in variants}) == len(variants), "variant_identity_uniqueness")
    claim_map = {c["evidence_id"]: c for c in claims}
    require(len(claim_map) == len(claims), "evidence_identity_uniqueness")
    for v in variants:
        original = live[v["source_record"]]
        require(original == v["raw_cells"], "raw_cell_preservation", v["variant_id"])
        require(v["product_id"] == original[header.index("product_id")], "variant_product_binding")
        require(v["variant_id"] == original[header.index("variant_sku")], "variant_sku_binding")
        require(v["size_label"] == (original[header.index("size")] or None), "size_preservation")
        require(v["currency"] is None, "no_invented_currency")
        require(v["split"] == splits[v["product_id"]]["split"], "variant_split_binding")
        if "inventory" in v["recovered_specification_columns"]:
            require(v["inventory"] is None, "specification_not_stock")
    for c in claims:
        original = live[c["source_record"]][c["column_index"]]
        start, end = c["span"]
        require(original[start:end] == c["fragment"], "exact_evidence_span", c["evidence_id"])
        require(header[c["column_index"]] == c["column"], "evidence_column_binding")
        key, value = c["fragment"].split(" : ", 1)
        require(key.strip() == c["key"] and value.strip() == c["value"], "exact_key_value_binding")
        require(normal(value) == c["normalized_value"], "literal_value_normalization")
    by_variant_product = collections.defaultdict(list)
    for v in variants:
        by_variant_product[v["product_id"]].append(v)
    groups = collections.defaultdict(set)
    texts = collections.defaultdict(set)
    for p in products:
        require(p["variant_ids"] == sorted(v["variant_id"] for v in by_variant_product[p["product_id"]]), "product_variant_coverage")
        require(p["source_records"] == sorted(v["source_record"] for v in by_variant_product[p["product_id"]]), "product_record_coverage")
        require(p["source_price"]["currency"] is None and not p["image_urls"], "no_invented_media_or_currency")
        require({"split": p["split"], "leakage_group_id": p["leakage_group_id"]} == splits[p["product_id"]], "product_split_binding")
        groups[p["leakage_group_id"]].add(p["split"])
        for role, value in [("title", p["title"])] + [("description", x) for x in p["source_descriptions"]]:
            if value and p["brand"]:
                texts[(role, normal(p["brand"]), normal(value))].add(p["split"])
        for field, attr in p["attributes"].items():
            values = attr["reported_values"]
            require(attr["status"] == ("unknown" if len(values) == 0 else "reported" if len(values) == 1 else "ambiguous"), "attribute_status")
            require(attr["value"] == (values[0] if len(values) == 1 else None), "unknown_and_ambiguous_not_guessed")
            require({claim_map[e]["normalized_value"] for e in attr["evidence_ids"]} == set(values), "attribute_evidence_coverage")
            for evidence_id in attr["evidence_ids"]:
                require(claim_map[evidence_id]["source_record"] in p["source_records"], "attribute_product_binding")
        require(p["quality"]["strict_eligible"] == all(p["quality"]["gates"].values()), "strict_gate_conjunction")
        require(p["quality"]["exclusion_reasons"] == [g for g in cfg["gate_order"] if not p["quality"]["gates"][g]], "exclusion_completeness")
    for value in groups.values():
        require(len(value) == 1, "no_group_split_leakage")
    for value in texts.values():
        require(len(value) == 1, "no_exact_text_split_leakage")
    require({p["product_id"] for p in strict} == {p["product_id"] for p in products if p["quality"]["strict_eligible"]}, "strict_selection_coverage")
    strict_map = {p["product_id"]: p for p in strict}
    require({c["product_id"] for c in cards} == set(strict_map), "card_coverage")
    for p in strict:
        require(p["gender"] in cfg["adult_genders"] and p["domain"] == "Clothing" and p["category"] in cfg["single_garment_categories"], "strict_category_scope")
        for field in cfg["core_attributes"]:
            require(p["attributes"][field]["status"] == "reported", "strict_core_complete")
        require(not p["quality"]["discordances"], "strict_discordance_free_under_guards")
    for c in cards:
        p = strict_map[c["product_id"]]
        require(c["facts"] == {k: p["attributes"][k]["source_labels"][0] for k in cfg["core_attributes"]}, "card_source_labels")
        require(c["currency"] is None and c["source_price_value"] == p["source_price"]["minimum"], "card_price_fidelity")
        require(c["split"] == p["split"], "card_split_binding")
    pool_ids = []
    for path in sorted((output / "pools").glob("*.jsonl")):
        pool = read_jsonl(path)
        require(len({(p["gender"], p["category"]) for p in pool}) == 1, "homogeneous_pool")
        pool_ids.extend(p["product_id"] for p in pool)
        with path.with_suffix(".csv").open(encoding="utf-8-sig", newline="") as f:
            require(len(list(csv.DictReader(f))) == len(pool), "pool_csv_parity")
    require(sorted(pool_ids) == sorted(strict_map), "pool_partition_coverage")
    for stem, expected in [("products_all", len(products)), ("catalogue_strict", len(strict))]:
        with (output / (stem + ".csv")).open(encoding="utf-8-sig", newline="") as f:
            require(len(list(csv.DictReader(f))) == expected, "main_csv_parity")
    actual_files = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file() and p.name != "MANIFEST.json"}
    require(actual_files == set(manifest["files"]), "manifest_complete")
    for path, expected in manifest["files"].items():
        require(digest(output / path) == expected["sha256"], "output_checksum", path)
        require((output / path).stat().st_size == expected["bytes"], "output_size", path)
    require(manifest["constructor_sha256"] == digest(BASE / "build_catalogue.py"), "constructor_identity")
    require(summary["all_products"] == len(products) and summary["strict_products"] == len(strict), "summary_count_parity")
    require(summary["model_calls"] == 0 and summary["human_semantic_reviews"] == 0, "claim_limits")
    return {"status": "PASS", "checks": dict(checks), "total_checks": sum(checks.values()),
            "products": len(products), "strict_products": len(strict),
            "verified_scope": "source_fidelity_schema_accounting_and_exact_text_leakage_only",
            "human_semantic_validation": False, "model_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, default=BASE / "artifacts/source" / SOURCE_NAME)
    parser.add_argument("--output", type=pathlib.Path, default=BASE / "artifacts/catalogue_v01_final")
    parser.add_argument("--receipt", type=pathlib.Path, default=BASE / "results/VERIFICATION.json")
    args = parser.parse_args()
    receipt = verify(args.source, args.output)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt[k] for k in ["status", "total_checks", "products", "strict_products"]}))


if __name__ == "__main__":
    main()
