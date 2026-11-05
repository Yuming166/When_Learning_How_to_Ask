"""Portable numerical reanalysis of the explicitly published evaluation subset."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
import statistics_python as py_math
import statistics_llm as llm_math

HERE = Path(__file__).resolve().parent
PY = "myntra_python_mechanism_ablation_v01_20261105"
LLM = "myntra_llm_mechanism_ablation_v01_20261105"
BOOLS = ["exact_decision_correct", "purchase_recall_case", "no_buy_correct_case", "false_purchase_case", "hard_constraint_violation", "answer_path_complete"]
INTS = ["pool_index", "budget", "elicitation_units", "dialogue_turns"]
FLOATS = ["score_regret", "normalized_score_regret"]
METHODS = ["fixed_order", "profile_ig", "decision_set_ig", "decision_value", "decision_value_initial_order"]
SENSITIVE = {
    "provider_key": re.compile(r"\bsk-[A-Za-z0-9_.-]{24,}"),
    "github_token": re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_url": re.compile(r"https?://[^/\s:@]+:[^/\s@]+@"),
}


def read(p):
    return json.loads(Path(p).read_text())


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_records(kind):
    with (HERE / "records" / f"{kind}.csv").open(newline="") as f:
        records = list(csv.DictReader(f))
    for r in records:
        for key in BOOLS:
            if r[key] not in ("0", "1"):
                raise ValueError("Invalid boolean in evaluation projection")
            r[key] = r[key] == "1"
        for key in INTS:
            r[key] = int(r[key])
        for key in FLOATS:
            r[key] = float(r[key])
            if not math.isfinite(r[key]):
                raise ValueError("Nonfinite evaluation metric")
        for key in ("query_sequence", "valid_query_sequence"):
            r[key] = r[key].split(";") if r[key] else []
        r["failed_query_action"] = r["failed_query_action"] or None
        r["selected_action"] = r.pop("selected_action_code")
    return records


def check_coverage(python, llm):
    for name, records, count in (("python", python, 25760), ("llm", llm, 29400)):
        keys = {(r["split"], r["model"], r["case_id"], r["method"], r["budget"]) for r in records}
        if len(keys) != len(records) or len(records) != count:
            raise RuntimeError(f"{name}: duplicated or missing evaluation records")
        for r in records:
            if not (0 <= r["budget"] <= 6) or r["method"] not in METHODS:
                raise RuntimeError("Illegal budget/method")
            q = r["query_sequence"]
            if len(set(q)) != len(q) or len(q) != r["elicitation_units"] or len(q) > r["budget"]:
                raise RuntimeError("Invalid question cost/prefix")
            if r["answer_path_complete"]:
                if len(q) != r["budget"] or q != r["valid_query_sequence"] or r["failed_query_action"] is not None:
                    raise RuntimeError("Complete-path inconsistency")
            elif not q or q[-1] != r["failed_query_action"] or q[:-1] != r["valid_query_sequence"]:
                raise RuntimeError("Stopped-path inconsistency")
    if {r["model"] for r in python} != {"python"}:
        raise RuntimeError("Unexpected Python model field")
    for split, ncases, nprofiles in (("development", 280, 48), ("validation_reserved", 264, 120), ("test_reserved", 192, 120)):
        rr = [r for r in python if r["split"] == split]
        if len({r["case_id"] for r in rr}) != ncases or len({r["profile_id"] for r in rr}) != nprofiles:
            raise RuntimeError("Python split denominator drift")
        expected = {(cid, m, b) for cid in {r["case_id"] for r in rr} for m in METHODS for b in range(7)}
        if {(r["case_id"], r["method"], r["budget"]) for r in rr} != expected:
            raise RuntimeError("Incomplete Python method coverage")
    llm_models = {r["model"] for r in llm}
    if llm_models != {"luna", "deepseek", "glm"} or {r["split"] for r in llm} != {"development"}:
        raise RuntimeError("LLM model or split drift")
    shared_cases = None
    for model in sorted(llm_models):
        rr = [r for r in llm if r["model"] == model]
        cases = {r["case_id"] for r in rr}
        if len(cases) != 280 or len({r["profile_id"] for r in rr}) != 48:
            raise RuntimeError("LLM denominator drift")
        if shared_cases is not None and cases != shared_cases:
            raise RuntimeError("Models no longer share the same cases")
        shared_cases = cases
        expected = {(cid, m, b) for cid in cases for m in METHODS for b in range(7)}
        if {(r["case_id"], r["method"], r["budget"]) for r in rr} != expected:
            raise RuntimeError("Incomplete LLM method coverage")
    return {"python_rows": len(python), "python_cases": 736, "python_profiles": 288,
            "llm_rows": len(llm), "llm_cases_per_model": 280, "llm_shared_profiles": 48}


def verify():
    manifest = read(HERE / "MANIFEST.json")
    actual_files = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()
                    and "__pycache__" not in p.parts and str(p.relative_to(HERE)) not in {"MANIFEST.json", "CHECKS.json"}}
    if actual_files != set(manifest["files_sha256"]):
        raise RuntimeError("Public manifest does not cover the exact published file inventory")
    for rel, expected in manifest["files_sha256"].items():
        if digest(HERE / rel) != expected:
            raise RuntimeError(f"Public file changed: {rel}")
    provenance = read(HERE / "SOURCE_MANIFEST.json")
    for entry in [*provenance["source_files"], *provenance["derived_files"]]:
        if digest(HERE / entry["path"]) != entry["published_sha256"]:
            raise RuntimeError(f"Export provenance mismatch: {entry['path']}")
    parsed = {"python": 0, "json": 0, "text": 0}
    for rel in manifest["files_sha256"]:
        path = HERE / rel
        if path.suffix in {".png", ".pdf"}:
            continue
        text = path.read_text()
        for kind, pattern in SENSITIVE.items():
            if pattern.search(text):
                raise RuntimeError(f"Sensitive pattern in {rel}: {kind}; value withheld")
        parsed["text"] += 1
        if path.suffix == ".py":
            ast.parse(text, filename=rel)
            parsed["python"] += 1
        elif path.suffix == ".json":
            json.loads(text)
            parsed["json"] += 1
    coverage = check_coverage(load_records("python"), load_records("llm"))
    return {"status": "PASS", "manifest_files": len(manifest["files_sha256"]), **parsed, **coverage,
            "new_model_calls": 0, "scope": "published subset only; does not rerun original raw-source validation"}


def summarize():
    python, llm = load_records("python"), load_records("llm")
    coverage = check_coverage(python, llm)
    llm_math.ex.CFG = {**read(HERE / "llm_config.json"), "evaluated_methods": METHODS}
    return {"coverage": coverage, "python_curves": py_math.method_curves(python, METHODS),
            "llm_curves": llm_math.curves(llm), "new_model_calls": 0}


def compare(actual, expected, path="root"):
    if isinstance(expected, dict):
        keys = set(expected) - {"numpy_version"}
        if keys != set(actual) - {"numpy_version"}:
            raise AssertionError(f"Reanalysis key mismatch: {path}")
        for key in keys:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"Reanalysis list length mismatch: {path}")
        for i, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, path + f"/{i}")
    elif isinstance(expected, (float, int)):
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError(f"Reanalysis numeric mismatch: {path}")
    elif actual != expected:
        raise AssertionError(f"Reanalysis value mismatch: {path}")


def analyze(output):
    python, llm = load_records("python"), load_records("llm")
    coverage = check_coverage(python, llm)
    py_cfg, llm_cfg = read(HERE / "python_config.json"), read(HERE / "llm_config.json")
    py_reference = read(HERE / "historical" / PY / "results/ANALYSIS.json")
    llm_reference = read(HERE / "historical" / LLM / "results/ANALYSIS.json")
    groups = {"pooled": python}
    groups.update({"split:" + s: [r for r in python if r["split"] == s] for s in py_cfg["splits"]})
    pools = sorted({(r["gender"], r["category"]) for r in python})
    groups.update({"pool:" + gender + "/" + category: [r for r in python if (r["gender"], r["category"]) == (gender, category)] for gender, category in pools})
    py_result = {"curves": py_math.method_curves(python, METHODS),
                 "groups": {label: py_math.bootstrap(rr, py_cfg, label) for label, rr in groups.items()}}
    compare(py_result["curves"], py_reference["curves"], "python/curves")
    compare(py_result["groups"], py_reference["groups"], "python/groups")
    llm_math.ex.CFG = llm_cfg
    common_ids = set(read(HERE / "llm_panel_metadata.json")["common_complete_profiles"])
    common = [r for r in llm if r["profile_id"] in common_ids]
    llm_result = {"curves": llm_math.curves(llm), "full": llm_math.joint_bootstrap(llm, llm_cfg),
                  "common_complete": llm_math.joint_bootstrap(common, llm_cfg, "common_complete"),
                  "common_complete_curves": llm_math.curves(common), "trajectory_diagnostics": llm_math.diagnostics(llm)}
    for key, value in llm_result.items():
        compare(value, llm_reference[key], "llm/" + key)
    output = Path(output).resolve()
    if output.is_relative_to(HERE):
        raise ValueError("Choose an output directory outside the immutable public package")
    output.mkdir(parents=True, exist_ok=True)
    for filename, value in (("python_reanalysis.json", py_result), ("llm_reanalysis.json", llm_result)):
        (output / filename).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    result = {"status": "PASS_ALL_PUBLISHED_STATISTICS_MATCH", **coverage,
              "python_bootstrap_groups": len(groups), "bootstrap_repetitions": 10000,
              "llm_shared_draws_across_models": True, "tolerance": 1e-12,
              "output": str(output), "new_model_calls": 0, "scope": "statistics from published projections; no strategy/model re-execution"}
    (output / "REANALYSIS_RECEIPT.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "summary", "analyze"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "analyze":
        if args.output is None:
            parser.error("analyze requires --output outside the package")
        result = analyze(args.output)
    elif args.command == "summary":
        result = summarize()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    else:
        result = verify()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
