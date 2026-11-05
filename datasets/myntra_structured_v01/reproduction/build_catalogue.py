"""Deterministic, standard-library-only construction; never calls a model."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import html
import io
import json
import pathlib
import re
import unicodedata
from decimal import Decimal, InvalidOperation

BASE = pathlib.Path(__file__).resolve().parent
HEADER = [
    "uniq_id", "crawl_timestamp", "product_id", "size", "variant_sku", "brand",
    "care_instructions", "dominant_material", "title", "actual_color",
    "dominant_color", "product_type", "body", "product_details", "size_fit",
    "complete_the_look", "type", "variant_price", "variant_compare_at_price",
    "ideal_for", "is_in_stock", "inventory", "specifications", "",
]
ATTR_KEYS = {
    "neckline": "neck", "sleeve_length": "sleeve length", "fabric": "fabric",
    "wash_care": "wash care", "pattern": "pattern",
    "print_pattern_type": "print or pattern type", "closure": "closure",
    "garment_length": "length", "shape": "shape", "fit": "fit",
    "transparency": "transparency", "occasion": "occasion",
    "component_count": "number of components", "top_fabric": "top fabric",
    "bottom_fabric": "bottom fabric", "dupatta_fabric": "dupatta fabric",
    "fabric_purity": "fabric purity", "fabric_type": "fabric type",
}
CORE = ["neckline", "sleeve_length", "fabric", "wash_care", "pattern"]
CARE_PATTERNS = {
    "machine wash": r"machine[\s-]*wash(?:ing)?\b",
    "hand wash": r"hand[\s-]*wash(?:ing)?\b",
    "dry clean": r"dry[\s-]*clean(?:ing)?\b",
}
SLEEVE_PATTERNS = {
    "long sleeves": r"\blong[\s-]+sleeves?\b",
    "short sleeves": r"\bshort[\s-]+sleeves?\b",
    "three-quarter sleeves": r"\bthree[\s-]+quarter[\s-]+sleeves?\b",
    "sleeveless": r"\bsleeveless\b",
}
# Decorative neck details can coexist with a base neckline; not forced exclusive.
NECK_PATTERNS = {
    "v-neck": r"\bv[\s-]*neck(?:line)?\b", "round neck": r"\bround[\s-]+neck(?:line)?\b",
    "mandarin collar": r"\bmandarin[\s-]+collar\b",
    "shirt collar": r"\bshirt[\s-]+collar\b",
    "boat neck": r"\bboat[\s-]+neck(?:line)?\b", "scoop neck": r"\bscoop[\s-]+neck(?:line)?\b",
    "square neck": r"\bsquare[\s-]+neck(?:line)?\b", "u-neck": r"\bu[\s-]*neck(?:line)?\b",
}
# A limited compatibility dictionary, not a fibre-composition classifier.
MATERIAL_FAMILIES = {
    "cotton": {"cotton"}, "pure cotton": {"cotton"},
    "cotton blend": {"cotton"}, "polyester": {"polyester"},
    "polycotton": {"cotton", "polyester"}, "cotton silk": {"cotton", "silk"},
    "viscose rayon": {"rayon"}, "rayon": {"rayon"}, "viscose": {"rayon"},
    "linen": {"linen"}, "silk": {"silk"}, "pure silk": {"silk"},
    "silk blend": {"silk"}, "dupion silk": {"silk"},
    "tussar silk": {"silk"}, "raw silk": {"silk"},
    "nylon": {"nylon"}, "acrylic": {"acrylic"}, "wool": {"wool"},
    "modal": {"modal"},
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", html.unescape(value))
    value = value.translate(str.maketrans({c: "-" for c in "‐‑‒–—−"}))
    return " ".join(value.split()).casefold()


def decimal_value(value: str) -> str | None:
    try:
        x = Decimal(value.strip().replace(",", ""))
        if not x.is_finite() or x <= 0:
            return None
        return format(x.normalize(), "f")
    except (InvalidOperation, ValueError):
        return None


def unique_labels(values) -> list[str]:
    labels = {}
    for x in values:
        if x.strip():
            labels.setdefault(norm(x), x.strip())
    return [labels[k] for k in sorted(labels)]


def parse_specification(blob: str, row: int, column: str, column_index: int):
    """Return exact source fragments and spans; URLs are not key/value specs."""
    claims, unparsed = [], []
    offset = 0
    chunks = blob.split("|")
    has_spec = any(re.search(r"\s+:\s+", chunk) for chunk in chunks)
    if not has_spec:
        return claims, unparsed
    for part_index, chunk in enumerate(chunks):
        match = re.fullmatch(r"\s*([^:|]+?)\s+:\s+(.+?)\s*", chunk, re.S)
        if match:
            start = offset + len(chunk) - len(chunk.lstrip())
            end = offset + len(chunk.rstrip())
            claims.append({
                "evidence_id": f"r{row}c{column_index}p{part_index}",
                "source_record": row, "column": column,
                "column_index": column_index, "span": [start, end],
                "fragment": blob[start:end], "key": match.group(1).strip(),
                "value": match.group(2).strip(),
                "normalized_key": norm(match.group(1)),
                "normalized_value": norm(match.group(2)),
            })
        elif chunk.strip():
            unparsed.append({"source_record": row, "column": column,
                             "fragment": chunk.strip()})
        offset += len(chunk) + 1
    return claims, unparsed


def attribute(claims: list[dict], key: str) -> dict:
    matches = [x for x in claims if x["normalized_key"] == key]
    values = sorted({x["normalized_value"] for x in matches})
    return {
        "status": "unknown" if not values else "reported" if len(values) == 1 else "ambiguous",
        "value": values[0] if len(values) == 1 else None,
        "reported_values": values,
        "source_labels": unique_labels(x["value"] for x in matches),
        "evidence_ids": sorted(x["evidence_id"] for x in matches),
    }


def care_mentions(text: str):
    text = norm(text)
    positive, negative = set(), set()
    for label, pattern in CARE_PATTERNS.items():
        for m in re.finditer(pattern, text):
            # Limited negation scope; all source text remains available for audit.
            prefix = re.split(r"[;,.|]", text[max(0, m.start() - 55):m.start()])[-1]
            denied = re.search(r"\b(?:do not|don't|not|never|avoid|no)\b", prefix)
            (negative if denied else positive).add(label)
    return positive, negative


def detect_discordance(raw: dict, attrs: dict) -> list[dict]:
    out = []
    positive, negative = care_mentions(raw["care_instructions"])
    care = attrs["wash_care"]["value"]
    if care in negative:
        out.append({"kind": "care_denial_discordance", "spec_value": care,
                    "source_text": raw["care_instructions"]})
    if care and positive and care not in positive:
        out.append({"kind": "care_report_discordance", "spec_value": care,
                    "mentioned_values": sorted(positive),
                    "source_text": raw["care_instructions"]})
    text = norm(raw["title"] + "\n" + raw["product_details"])
    for field, patterns in [("sleeve_length", SLEEVE_PATTERNS), ("neckline", NECK_PATTERNS)]:
        value = attrs[field]["value"]
        mentioned = {label for label, pattern in patterns.items() if re.search(pattern, text)}
        if value in patterns and len(mentioned) == 1 and value not in mentioned:
            out.append({"kind": f"{field}_description_discordance",
                        "spec_value": value, "mentioned_values": sorted(mentioned),
                        "source_text": raw["product_details"]})
    fabric = attrs["fabric"]["value"]
    dominant = norm(raw["dominant_material"])
    a, b = MATERIAL_FAMILIES.get(fabric), MATERIAL_FAMILIES.get(dominant)
    if a and b and not a.intersection(b):
        out.append({"kind": "fabric_label_discordance", "spec_value": fabric,
                    "dominant_material": raw["dominant_material"]})
    return out


def parse_source(raw: bytes):
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")))
    if next(reader) != HEADER:
        raise ValueError("Source header drift; refusing guessed column alignment")
    variants, claims, blank_records, invalid_records = [], [], [], []
    for source_record, cells in enumerate(reader, start=2):
        if len(cells) != len(HEADER):
            raise ValueError(f"Wrong CSV width at logical record {source_record}")
        if not any(x.strip() for x in cells):
            blank_records.append(source_record)
            continue
        r = dict(zip(HEADER, cells))
        row_issues = []
        if not re.fullmatch(r"[0-9]+", r["product_id"]):
            invalid_records.append({"source_record": source_record, "cells": cells,
                                    "reason": "invalid_product_id"})
            continue
        if not re.fullmatch(r"[0-9a-f]{32}", r["uniq_id"]):
            row_issues.append("invalid_source_record_id")
        if not r["variant_sku"].startswith(r["product_id"] + "_"):
            row_issues.append("variant_product_id_mismatch")
        own_claims, unparsed, recovered_columns = [], [], []
        for index in (21, 22, 23):
            own, failed = parse_specification(cells[index], source_record, HEADER[index], index)
            own_claims.extend(own)
            unparsed.extend(failed)
            if own and index != 22:
                recovered_columns.append(HEADER[index] or "extra_23")
        claims.extend(own_claims)
        inventory = r["inventory"].strip()
        if "inventory" in recovered_columns:
            inventory = None
        elif inventory and not re.fullmatch(r"\d+", inventory):
            row_issues.append("non_numeric_inventory")
            inventory = None
        else:
            inventory = int(inventory) if inventory else None
        attrs = {field: attribute(own_claims, key) for field, key in ATTR_KEYS.items()}
        taxonomy = r["type"].split("/")
        price = decimal_value(r["variant_price"])
        if price is None:
            row_issues.append("invalid_source_price")
        variants.append({
            "variant_id": r["variant_sku"], "product_id": r["product_id"],
            "source_record_id": r["uniq_id"], "source_record": source_record,
            "crawl_timestamp": r["crawl_timestamp"], "size_label": r["size"] or None,
            "source_price": price, "currency": None,
            "source_compare_at_price": decimal_value(r["variant_compare_at_price"]),
            "source_stock_label": r["is_in_stock"], "inventory": inventory,
            "domain": taxonomy[0] if len(taxonomy) >= 3 else None,
            "taxonomy_gender": taxonomy[1] if len(taxonomy) >= 3 else None,
            "category": taxonomy[2] if len(taxonomy) >= 3 else None,
            "attributes": attrs, "recovered_specification_columns": recovered_columns,
            "unparsed_specification_fragments": unparsed,
            "row_issues": row_issues, "raw_cells": cells,
            "raw_fields": {k or "extra_23": v for k, v in r.items()},
        })
    return variants, claims, blank_records, invalid_records


def build_products(variants: list[dict], claims: list[dict], config: dict):
    by_product = collections.defaultdict(list)
    by_claim_product = collections.defaultdict(list)
    row_product = {r["source_record"]: r["product_id"] for r in variants}
    for row in variants:
        by_product[row["product_id"]].append(row)
    for claim in claims:
        by_claim_product[row_product[claim["source_record"]]].append(claim)
    products = []
    for pid in sorted(by_product, key=int):
        rows = by_product[pid]
        own = by_claim_product[pid]
        attrs = {field: attribute(own, key) for field, key in ATTR_KEYS.items()}
        values = {key: unique_labels(r["raw_fields"][key] for r in rows)
                  for key in ["title", "brand", "ideal_for", "product_details",
                              "care_instructions", "dominant_material", "size_fit"]}
        identity_ok = all(len(values[key]) == 1 for key in ["title", "brand", "ideal_for"])
        taxonomy = {(r["domain"], r["taxonomy_gender"], r["category"]) for r in rows}
        identity_ok = (identity_ok and len(taxonomy) == 1
                       and all(r["taxonomy_gender"] == r["raw_fields"]["ideal_for"] for r in rows)
                       and all(not r["row_issues"] for r in rows)
                       and all(r["domain"] and r["category"] for r in rows))
        domain, taxonomy_gender, category = sorted(taxonomy, key=str)[0]
        eligible_category = (domain == "Clothing"
                             and taxonomy_gender in config["adult_genders"]
                             and category in config["single_garment_categories"])
        components = attrs["component_count"]["reported_values"]
        one_component = not components or components == ["1"]
        # Compound outfits have several legitimate local attributes; never apply
        # single-garment text guards to them and call those differences errors.
        discordance = []
        if eligible_category and one_component:
            for row in rows:
                discordance.extend(dict(x, source_record=row["source_record"])
                                   for x in detect_discordance(row["raw_fields"], row["attributes"]))
        for key in config["core_attributes"]:
            if attrs[key]["status"] == "ambiguous":
                discordance.append({"kind": "within_product_core_disagreement", "field": key,
                                    "reported_values": attrs[key]["reported_values"]})
        prices = sorted({r["source_price"] for r in rows if r["source_price"] is not None}, key=Decimal)
        gates = {
            "valid_identity_and_taxonomy": identity_ok,
            "adult_single_garment_category": eligible_category,
            "no_reported_multiple_components": one_component,
            "complete_singleton_core_attributes": all(attrs[k]["status"] == "reported" for k in config["core_attributes"]),
            "one_source_price": len(prices) == 1 and all(r["source_price"] is not None for r in rows),
            "no_detected_core_discordance": not discordance,
            "no_unparsed_specification_fragment": not any(r["unparsed_specification_fragments"] for r in rows),
        }
        products.append({
            "product_id": pid, "title": values["title"][0] if values["title"] else None,
            "brand": values["brand"][0] if values["brand"] else None,
            "gender": values["ideal_for"][0] if values["ideal_for"] else None,
            "domain": domain, "category": category, "attributes": attrs,
            "all_specification_claims": sorted({c["normalized_key"] for c in own}),
            "variant_ids": sorted(r["variant_id"] for r in rows),
            "source_records": sorted(r["source_record"] for r in rows),
            "crawl_timestamps": sorted({r["crawl_timestamp"] for r in rows}),
            "size_labels": unique_labels(r["size_label"] or "" for r in rows),
            "source_price": {"values": prices, "minimum": prices[0] if prices else None,
                             "maximum": prices[-1] if prices else None, "currency": None},
            "source_descriptions": values["product_details"],
            "source_care_material_texts": values["care_instructions"],
            "source_dominant_material_labels": values["dominant_material"],
            "source_size_fit_texts": values["size_fit"],
            "image_urls": [], "media_status": "not_provided_in_this_source_file",
            "quality": {"strict_eligible": all(gates.values()), "gates": gates,
                        "exclusion_reasons": [g for g in config["gate_order"] if not gates[g]],
                        "discordances": discordance,
                        "component_count_unreported": not components,
                        "semantic_validation": "automated_limited_guards_only",
                        "ground_truth_scope": "seller_reported_attributes"},
        })
    return products


def assign_splits(products: list[dict], config: dict):
    parent = {p["product_id"]: p["product_id"] for p in products}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b, key=int)] = min(a, b, key=int)

    seen = {}
    for p in products:
        brand = norm(p["brand"] or "")
        texts = [("title", p["title"] or "")]
        texts += [("description", x) for x in p["source_descriptions"]]
        for role, text in texts:
            if not brand or not norm(text):
                continue
            key = (role, brand, norm(text))
            if key in seen:
                union(p["product_id"], seen[key])
            seen[key] = p["product_id"]
    components = collections.defaultdict(list)
    for pid in parent:
        components[find(pid)].append(pid)
    mapping = {}
    if sum(config["split_buckets"].values()) != 100:
        raise ValueError("Split buckets must sum to 100")
    for ids in components.values():
        ids = sorted(ids, key=int)
        group = sha((config["split_salt"] + "|" + "|".join(ids)).encode())
        bucket = int(group[:16], 16) % 100
        boundary = 0
        for split, weight in config["split_buckets"].items():
            boundary += weight
            if bucket < boundary:
                break
        for pid in ids:
            mapping[pid] = {"split": split, "leakage_group_id": group}
    for p in products:
        p.update(mapping[p["product_id"]])
    return mapping, list(components.values())


def write_json(path: pathlib.Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def write_jsonl(path: pathlib.Path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for value in values:
            f.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def flat_row(p: dict):
    row = {k: p[k] for k in ["product_id", "title", "brand", "gender", "category", "split", "leakage_group_id"]}
    for field in ATTR_KEYS:
        row[field] = p["attributes"][field]["value"]
        row[field + "_status"] = p["attributes"][field]["status"]
    row.update({
        "source_price_min": p["source_price"]["minimum"],
        "source_price_max": p["source_price"]["maximum"], "currency": None,
        "size_labels_json": json.dumps(p["size_labels"], ensure_ascii=False),
        "variant_ids_json": json.dumps(p["variant_ids"]),
        "strict_eligible": p["quality"]["strict_eligible"],
        "exclusion_reasons_json": json.dumps(p["quality"]["exclusion_reasons"]),
    })
    return row


def write_csv(path: pathlib.Path, products):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat_row(products[0])) if products else list(flat_row(_empty_product())))
        writer.writeheader()
        writer.writerows(flat_row(p) for p in products)


def _empty_product():
    p = {k: None for k in ["product_id", "title", "brand", "gender", "category", "split", "leakage_group_id"]}
    p.update(attributes={k: {"value": None, "status": "unknown"} for k in ATTR_KEYS},
             source_price={"minimum": None, "maximum": None}, size_labels=[], variant_ids=[],
             quality={"strict_eligible": False, "exclusion_reasons": []})
    return p


def make_card(p: dict):
    facts = {k: p["attributes"][k]["source_labels"][0] for k in CORE}
    labels = {"neckline": "领口", "sleeve_length": "袖长", "fabric": "面料标签",
              "wash_care": "洗护说明", "pattern": "图案"}
    text = [f"商品编号：{p['product_id']}", f"来源分类：{p['gender']} / {p['category']}"]
    text += [f"{labels[k]}：{facts[k]}" for k in CORE]
    text += [f"历史来源价格数值：{p['source_price']['minimum']}（来源未标明币种）",
             "这些是商家陈述；未列出的特征未知。洗护说明未枚举全部允许的处理方式。"]
    return {"product_id": p["product_id"], "split": p["split"],
            "leakage_group_id": p["leakage_group_id"], "facts": facts,
            "evidence_ids": {k: p["attributes"][k]["evidence_ids"] for k in CORE},
            "source_price_value": p["source_price"]["minimum"], "currency": None,
            "recorded_size_labels": p["size_labels"],
            "card_text_zh": "\n".join(text)}


def summarise(products, variants, claims, blanks, invalid, groups, config):
    strict = [p for p in products if p["quality"]["strict_eligible"]]
    remaining = products[:]
    funnel = []
    for gate in config["gate_order"]:
        before = len(remaining)
        remaining = [p for p in remaining if p["quality"]["gates"][gate]]
        funnel.append({"gate": gate, "before": before, "removed": before - len(remaining), "remaining": len(remaining)})
    categories = collections.defaultdict(lambda: {"all_products": 0, "strict_products": 0, "splits": collections.Counter()})
    for p in products:
        key = f"{p['gender']}/{p['category']}"
        categories[key]["all_products"] += 1
        if p["quality"]["strict_eligible"]:
            categories[key]["strict_products"] += 1
            categories[key]["splits"][p["split"]] += 1
    return {
        "version": config["version"], "source_csv_records": len(variants) + len(blanks) + len(invalid),
        "empty_records": len(blanks), "invalid_records": len(invalid),
        "variant_records": len(variants), "unique_variant_ids": len({r['variant_id'] for r in variants}),
        "all_products": len(products), "strict_products": len(strict),
        "products_with_multiple_variants": sum(len(p["variant_ids"]) > 1 for p in products),
        "recovered_inventory_specification_records": sum("inventory" in r["recovered_specification_columns"] for r in variants),
        "specification_claims": len(claims), "unique_specification_keys": len({c['normalized_key'] for c in claims}),
        "sequential_funnel": funnel,
        "overlapping_exclusion_counts": dict(collections.Counter(g for p in products for g in p['quality']['exclusion_reasons'])),
        "discordance_counts": dict(collections.Counter(d['kind'] for p in products for d in p['quality']['discordances'])),
        "coverage_all_products": {k: dict(collections.Counter(p['attributes'][k]['status'] for p in products)) for k in ATTR_KEYS},
        "strict_attribute_distributions": {k: dict(collections.Counter(p['attributes'][k]['value'] for p in strict)) for k in CORE},
        "categories": dict(categories),
        "all_split_counts": dict(collections.Counter(p['split'] for p in products)),
        "strict_split_counts": dict(collections.Counter(p['split'] for p in strict)),
        "leakage_groups": len(groups), "multi_product_text_groups": sum(len(g) > 1 for g in groups),
        "largest_leakage_group": max(map(len, groups), default=0),
        "core_complete_but_excluded": sum(all(p['attributes'][k]['status'] == 'reported' for k in CORE) and not p['quality']['strict_eligible'] for p in products),
        "strict_component_count_unreported": sum(p['quality']['component_count_unreported'] for p in strict),
        "model_calls": 0, "training_runs": 0, "images_downloaded": 0, "human_semantic_reviews": 0,
    }


def build(source: pathlib.Path, output: pathlib.Path, config_path: pathlib.Path):
    config = json.loads(config_path.read_text())
    freeze = json.loads((BASE / "FREEZE.json").read_text())
    for name, digest in freeze["files"].items():
        if sha((BASE / name).read_bytes()) != digest:
            raise ValueError(f"Frozen construction rule changed: {name}")
    if sha(config_path.read_bytes()) != freeze["files"]["config.json"]:
        raise ValueError("Supplied configuration does not match the frozen configuration")
    raw = source.read_bytes()
    if sha(raw) != config["source_sha256"]:
        raise ValueError("Source SHA256 mismatch")
    variants, claims, blanks, invalid = parse_source(raw)
    if len(variants) + len(blanks) + len(invalid) != config["expected_source_rows"]:
        raise ValueError("Source denominator mismatch")
    products = build_products(variants, claims, config)
    mapping, groups = assign_splits(products, config)
    strict = [p for p in products if p["quality"]["strict_eligible"]]
    for v in variants:
        v.update(mapping[v["product_id"]])
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Output directory must be empty; preserve previous outputs")
    write_jsonl(output / "variants.jsonl", variants)
    write_jsonl(output / "source_claims.jsonl", claims)
    write_jsonl(output / "products_all.jsonl", products)
    write_csv(output / "products_all.csv", products)
    write_jsonl(output / "catalogue_strict.jsonl", strict)
    write_csv(output / "catalogue_strict.csv", strict)
    write_jsonl(output / "factual_cards.jsonl", [make_card(p) for p in strict])
    write_jsonl(output / "quality_issues.jsonl", [
        {"product_id": p["product_id"], **p["quality"]}
        for p in products if not p["quality"]["strict_eligible"] or p["quality"]["component_count_unreported"]])
    write_json(output / "source_record_accounting.json", {"blank_source_records": blanks, "invalid_records": invalid,
               "note": "Numbers are logical CSV records, including header as record 1; embedded newlines are not extra records."})
    write_json(output / "split_manifest.json", mapping)
    pools = collections.defaultdict(list)
    for p in strict:
        name = re.sub(r"[^a-z0-9]+", "_", norm(p["gender"] + "_" + p["category"])).strip("_")
        pools[name].append(p)
    for name, pool in sorted(pools.items()):
        write_csv(output / "pools" / f"{name}.csv", pool)
        write_jsonl(output / "pools" / f"{name}.jsonl", pool)
    summary = summarise(products, variants, claims, blanks, invalid, groups, config)
    write_json(output / "SUMMARY.json", summary)
    manifest = {str(p.relative_to(output)): {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
                for p in sorted(output.rglob("*")) if p.is_file()}
    write_json(output / "MANIFEST.json", {
        "source_sha256": sha(raw), "source_repo": config["source_repo"],
        "source_revision": config["source_revision"], "files": manifest,
        "constructor_sha256": sha(pathlib.Path(__file__).read_bytes()),
        "configuration_sha256": sha(config_path.read_bytes()),
        "protocol_sha256": sha((BASE / "PROTOCOL.md").read_bytes()),
    })
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, default=BASE / "artifacts/source/marketing_sample_for_myntra_com-ecommerce__20190601_20190831__15k_data.csv")
    parser.add_argument("--output", type=pathlib.Path, default=BASE / "artifacts/catalogue_v01_final")
    parser.add_argument("--config", type=pathlib.Path, default=BASE / "config.json")
    args = parser.parse_args()
    summary = build(args.source, args.output, args.config)
    print(json.dumps({k: summary[k] for k in ["variant_records", "all_products", "strict_products", "strict_split_counts"]}))


if __name__ == "__main__":
    main()
