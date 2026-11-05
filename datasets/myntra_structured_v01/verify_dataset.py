"""Offline checks for the exact published final catalogue; standard library only."""
from __future__ import annotations

import collections
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = ("neckline", "sleeve_length", "fabric", "wash_care", "pattern")


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def verify():
    release = json.loads((HERE / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()
              and "__pycache__" not in p.parts
              and p.relative_to(HERE).as_posix() not in {"RELEASE_MANIFEST.json", "CHECKS.json"}}
    require(actual == set(release["files_sha256"]), "Release inventory mismatch")
    for rel, expected in release["files_sha256"].items():
        require(digest(HERE / rel) == expected, f"Release hash mismatch: {rel}")
    source = json.loads((HERE / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    for entry in source["source_files"]:
        p = HERE / entry["path"]
        require(p.stat().st_size == entry["bytes"] and digest(p) == entry["sha256"],
                f"Source-copy mismatch: {entry['path']}")

    data = HERE / "catalogue"
    frozen = json.loads((data / "MANIFEST.json").read_text(encoding="utf-8"))
    require({str(p.relative_to(data)) for p in data.rglob("*") if p.is_file()}
            == set(frozen["files"]) | {"MANIFEST.json"}, "Frozen catalogue inventory mismatch")
    for rel, expected in frozen["files"].items():
        p = data / rel
        require(p.stat().st_size == expected["bytes"] and digest(p) == expected["sha256"],
                f"Frozen catalogue hash mismatch: {rel}")

    parsed = {}
    for p in data.rglob("*"):
        if p.suffix == ".json":
            json.loads(p.read_text(encoding="utf-8"))
        elif p.suffix == ".jsonl":
            parsed[str(p.relative_to(data))] = rows(p)
    products, strict = parsed["products_all.jsonl"], parsed["catalogue_strict.jsonl"]
    cards, variants = parsed["factual_cards.jsonl"], parsed["variants.jsonl"]
    claims = parsed["source_claims.jsonl"]
    require((len(products), len(strict), len(cards), len(variants), len(claims))
            == (959, 471, 471, 1000, 18991), "Record counts changed")
    product_map = {p["product_id"]: p for p in products}
    strict_map = {p["product_id"]: p for p in strict}
    require(len(product_map) == len(products) and len(strict_map) == len(strict), "Duplicate product ID")
    require(strict_map == {k: v for k, v in product_map.items() if v["quality"]["strict_eligible"]},
            "Strict selection mismatch")
    require({c["product_id"] for c in cards} == set(strict_map), "Fact-card coverage mismatch")
    evidence = {c["evidence_id"] for c in claims}
    require(len(evidence) == len(claims), "Duplicate evidence ID")
    split_map = json.loads((data / "split_manifest.json").read_text(encoding="utf-8"))
    groups = collections.defaultdict(set)
    for p in products:
        require(split_map[p["product_id"]] == {k: p[k] for k in ("split", "leakage_group_id")},
                "Split binding mismatch")
        groups[p["leakage_group_id"]].add(p["split"])
        for attr in p["attributes"].values():
            require(set(attr["evidence_ids"]) <= evidence, "Missing attribute evidence")
    require(all(len(splits) == 1 for splits in groups.values()), "Group leaks across splits")
    all_splits = dict(collections.Counter(p["split"] for p in products))
    strict_splits = dict(collections.Counter(p["split"] for p in strict))
    require(all_splits == {"development": 670, "validation_reserved": 157, "test_reserved": 132},
            "All-product split counts changed")
    require(strict_splits == {"development": 338, "validation_reserved": 78, "test_reserved": 55},
            "Strict split counts changed")

    tables = [data / "products_all.csv", data / "catalogue_strict.csv", *sorted((data / "pools").glob("*.csv"))]
    for path in tables:
        with path.open(encoding="utf-8-sig", newline="") as f:
            flat = list(csv.DictReader(f))
        nested = parsed[str(path.with_suffix(".jsonl").relative_to(data))]
        require(len(flat) == len(nested), f"CSV row mismatch: {path.name}")
        for a, b in zip(flat, nested):
            require(all(a[k] == b[k] for k in ("product_id", "split", "leakage_group_id")),
                    f"CSV identity mismatch: {path.name}")
            for field in CORE:
                attr = b["attributes"][field]
                require(a[field] == (attr["value"] or "") and a[field + "_status"] == attr["status"],
                        f"CSV attribute mismatch: {path.name}/{field}")
    expected_pools = {"women_kurtas": 214, "men_kurtas": 154, "women_dresses": 67,
                      "women_tops": 21, "women_tunics": 8, "women_kurtis": 7}
    pool_rows = {p.stem: parsed[str(p.relative_to(data))] for p in (data / "pools").glob("*.jsonl")}
    require({k: len(v) for k, v in pool_rows.items()} == expected_pools, "Pool counts changed")
    pooled = []
    for pool in pool_rows.values():
        require(len({(p["gender"], p["category"]) for p in pool}) == 1, "Mixed-category pool")
        require(all(p == strict_map.get(p["product_id"]) for p in pool), "Pool product mismatch")
        pooled.extend(p["product_id"] for p in pool)
    require(sorted(pooled) == sorted(strict_map), "Pools do not partition strict catalogue")
    return {"status": "PASS", "scope": "published file integrity, record parsing and cross-table consistency",
            "release_content_files": len(actual), "exact_source_copies": len(source["source_files"]),
            "catalogue_files": len(frozen["files"]) + 1, "products": len(products),
            "strict_products": len(strict), "variants": len(variants), "specification_claims": len(claims),
            "factual_cards": len(cards), "csv_tables": len(tables), "pools": expected_pools,
            "all_split_counts": all_splits, "strict_split_counts": strict_splits,
            "new_model_calls": 0, "raw_source_fidelity_rechecked_by_this_command": False}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))
