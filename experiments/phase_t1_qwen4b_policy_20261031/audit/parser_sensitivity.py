"""Outcome-informed POST-HOC sensitivity of saved offline allocation outputs.

Reads only completed public offline records and their public manifest. It
does not load a model, query an environment, inspect private provenance, or
change any frozen parser/policy. The only relaxed condition is positive raw
integer mass instead of an exact sum of 100, followed by normalization.
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from t1.core import parse_percent
from t1.evaluate import allocation_metrics

METHODS = ("MLP", "BaseQwen", "LoRA")
SPLITS = ("id_test", "ood_parameters", "ood_partition")
POSITIONS = (0, 3, 6, 9, 15)
METRICS = ("allocation_l1", "forward_kl_epsilon_1e8")


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def relaxed_raw(raw, mask):
    """Recheck every contract, including masks hidden by a prior sum error."""
    output = {"valid": False, "raw_sum": None, "raw_sum_minus_100": None,
              "shape_ok": False, "integers_in_range": False, "mask_ok": None,
              "strict_mass_ok": None, "positive_mass": None, "error": None}
    fallback = [float(bool(value)) / sum(mask) for value in mask]
    try:
        values = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return {**output, "error": "invalid_json", "weights": fallback,
                "detail": type(exc).__name__ + ": " + str(exc)}
    if not isinstance(values, list) or len(values) != 10:
        return {**output, "error": "not_array_length10", "weights": fallback}
    output["shape_ok"] = True
    if any(type(value) is not int or not 0 <= value <= 100 for value in values):
        return {**output, "error": "not_integer_0_to_100", "weights": fallback}
    output["integers_in_range"] = True
    total = sum(values)
    output.update(raw_sum=total, raw_sum_minus_100=total - 100,
                  mask_ok=all(not value or bool(legal) for value, legal in zip(values, mask)),
                  strict_mass_ok=total == 100, positive_mass=total > 0)
    if not output["mask_ok"]:
        return {**output, "error": "illegal_mask", "weights": fallback}
    if total <= 0:
        return {**output, "error": "nonpositive_sum", "weights": fallback}
    return {**output, "valid": True, "weights": [value / total for value in values]}


def metric_subset(teacher, weights, mask):
    # Only continuous L1/KL are retained. Percent labels are not relabelled or
    # compared; saved teacher weights suffice for these two frozen metrics.
    values = allocation_metrics(teacher, weights, mask)
    return {key: values[key] for key in METRICS}


def _self_checks():
    mask = [1] * 9 + [0]
    assert relaxed_raw("[99,0,0,0,0,0,0,0,0,0]", mask)["valid"]
    assert relaxed_raw("[98,0,0,0,0,0,0,0,0,1]", mask)["error"] == "illegal_mask"
    assert relaxed_raw("[99,0,0,0,0,0,0,0,0,1]", mask)["error"] == "illegal_mask"
    assert relaxed_raw("[0,0,0,0,0,0,0,0,0,0]", mask)["error"] == "nonpositive_sum"
    assert relaxed_raw("[100,0,0,0,0,0,0,0,0,0]", mask)["valid"]
    assert relaxed_raw("[true,0,0,0,0,0,0,0,0,0]", mask)["error"] == "not_integer_0_to_100"
    assert relaxed_raw("[1.0,0,0,0,0,0,0,0,0,0]", mask)["error"] == "not_integer_0_to_100"
    assert relaxed_raw("[101,0,0,0,0,0,0,0,0,0]", mask)["error"] == "not_integer_0_to_100"
    assert relaxed_raw("[]", mask)["error"] == "not_array_length10"
    assert relaxed_raw("not json", mask)["error"] == "invalid_json"
    return 10


def _verify_coverage(rows, manifest):
    expected_worlds = {split: {row["world_id"] for row in manifest["worlds"] if row["split"] == split}
                       for split in SPLITS}
    if any(len(worlds) != 8 for worlds in expected_worlds.values()):
        raise ValueError("Public manifest does not contain eight worlds per declared held-out stratum")
    expected = {f"{world}:{position}" for worlds in expected_worlds.values()
                for world in worlds for position in POSITIONS}
    if len(expected) != 120 or len(rows) != 360 or set(r["method"] for r in rows) != set(METHODS):
        raise ValueError("Require the complete frozen 120-state output for each of three methods")
    reference = {}
    for method in METHODS:
        subset = [row for row in rows if row["method"] == method]
        if len(subset) != 120 or {r["row_id"] for r in subset} != expected:
            raise ValueError("Missing/duplicated frozen offline rows for " + method)
        if Counter(row["split"] for row in subset) != Counter({split: 40 for split in SPLITS}):
            raise ValueError("Incorrect stratum coverage")
        for row in subset:
            if row["world_id"] not in expected_worlds[row["split"]]:
                raise ValueError("World identifier does not match public split")
            identity = digest_json({"state": row["state"], "teacher_weights": row["teacher_weights"]})
            if row["row_id"] in reference and reference[row["row_id"]] != identity:
                raise ValueError("Methods did not receive the same state and teacher label")
            reference[row["row_id"]] = identity
    return expected_worlds


def _distribution(values):
    if not values:
        return None
    return {"count": len(values), "min": min(values), "max": max(values),
            "mean": statistics.fmean(values), "median": statistics.median(values),
            "frequency": dict(sorted(Counter(values).items()))}


def _summarize(records):
    result = {}
    for method in METHODS:
        selected = [r for r in records if r["method"] == method]
        methodsum = {}
        for split in ("all", *SPLITS):
            rows = selected if split == "all" else [r for r in selected if r["split"] == split]
            n = len(rows)
            raw = [r["diagnostic_parse"] for r in rows if r["diagnostic_parse"] is not None]
            sums = [r["raw_sum"] for r in raw if r["raw_sum"] is not None]
            deviations = [v - 100 for v in sums]
            methodsum[split] = {
                "states": n, "worlds": len({r["world_id"] for r in rows}),
                "strict_valid": sum(r["strict_valid"] for r in rows),
                "diagnostic_valid": sum(r["diagnostic_valid"] for r in rows),
                "recovered_only_by_relaxing_sum": sum(r["recovered_sum_only"] for r in rows),
                "retained_fallback": sum(not r["diagnostic_valid"] for r in rows),
                "saved_first_error_counts": dict(Counter(r["saved_error"] for r in rows if r["saved_error"])),
                "all_raw_mask_violations": sum(r["mask_ok"] is False for r in raw),
                "sum_and_mask_violations": sum(r["mask_ok"] is False and r["strict_mass_ok"] is False for r in raw),
                "raw_sum": _distribution(sums), "raw_sum_deviation": _distribution(deviations),
                "raw_absolute_sum_deviation": _distribution([abs(v) for v in deviations]),
                "metrics": {metric: {
                    "strict_mean": statistics.fmean(r["strict_metrics"][metric] for r in rows),
                    "diagnostic_mean": statistics.fmean(r["diagnostic_metrics"][metric] for r in rows),
                    "diagnostic_minus_strict_mean": statistics.fmean(r["delta_metrics"][metric] for r in rows),
                    "denominator": n,
                } for metric in METRICS},
            }
        result[method] = methodsum
    return result


def _worlds_and_pairs(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[row["method"], row["split"], row["world_id"]].append(row)
    means = []
    for (method, split, world), rows in sorted(grouped.items()):
        if len(rows) != 5:
            raise ValueError("World cluster must contain exactly the five frozen positions")
        means.append({"method": method, "split": split, "world_id": world, "states": 5,
                      "strict": {metric: statistics.fmean(r["strict_metrics"][metric] for r in rows) for metric in METRICS},
                      "diagnostic": {metric: statistics.fmean(r["diagnostic_metrics"][metric] for r in rows) for metric in METRICS},
                      "delta": {metric: statistics.fmean(r["delta_metrics"][metric] for r in rows) for metric in METRICS}})
    index = {(r["method"], r["world_id"]): r for r in means}
    pairs = []
    for split in ("all", *SPLITS):
        worlds = sorted({r["world_id"] for r in means if split == "all" or r["split"] == split})
        for left, right in (("BaseQwen", "LoRA"), ("MLP", "LoRA"), ("BaseQwen", "MLP")):
            for mode in ("strict", "diagnostic"):
                for metric in METRICS:
                    vector = [index[left, world][mode][metric] - index[right, world][mode][metric]
                              for world in worlds]
                    pairs.append({"split": split, "left": left, "right": right, "mode": mode,
                                  "metric": metric, "world_ids": worlds, "left_minus_right": vector,
                                  "mean_difference": statistics.fmean(vector), "world_denominator": len(worlds),
                                  "uncertainty_scope": "descriptive paired vectors; no new bootstrap or population inference"})
    return means, pairs


def _report(result):
    summary = result["summary"]
    lines = [
        "# POST-HOC parser sensitivity of existing T1 offline outputs", "",
        "This outcome-informed diagnostic was requested after observing the frozen parser's failures. "
        "It does not replace the frozen primary results. All 120 states per method remain in every overall denominator; "
        "each stratum contains 40 states from eight worlds, with five fixed positions per world.", "",
        "The diagnostic reparses each saved Qwen raw string. It retains the JSON array, length 10, integer range "
        "0–100, nonnegativity, and complete action-mask checks. Only exact total 100 is relaxed to any positive "
        "total, followed by normalization. Every other failure keeps the same uniform legal fallback. "
        "MLP weights remain unchanged. Only continuous allocation L1 and the frozen smoothed forward KL are compared; "
        "no teacher percentage labels are regenerated or evaluated.", "",
        "## All-state results", "",
        "| Method | Strict valid / 120 | Diagnostic valid / 120 | L1 strict → diagnostic | KL strict → diagnostic |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for method in METHODS:
        row = summary[method]["all"]
        l1, kl = (row["metrics"][metric] for metric in METRICS)
        lines.append(f"| {method} | {row['strict_valid']} | {row['diagnostic_valid']} | "
                     f"{l1['strict_mean']:.6f} → {l1['diagnostic_mean']:.6f} | "
                     f"{kl['strict_mean']:.6f} → {kl['diagnostic_mean']:.6f} |")
    lines += ["", "## Full raw-contract audit", ""]
    for method in ("BaseQwen", "LoRA"):
        row = summary[method]["all"]
        lines.append(f"- {method}: {row['recovered_only_by_relaxing_sum']} outputs recovered solely by sum normalization; "
                     f"{row['retained_fallback']} retain fallback. Raw mask violations: {row['all_raw_mask_violations']}, "
                     f"including {row['sum_and_mask_violations']} simultaneous sum violations. "
                     f"Raw sum histogram: `{json.dumps(row['raw_sum']['frequency'], sort_keys=True)}`.")
    lines += ["", "Saved parser errors report only the first failed check. In particular, a sum error does not "
              "establish that the mask was correct. The diagnostic independently rechecks every raw mask position.", "",
              "## Stratum results", "",
              "| Stratum | Method | Strict → diagnostic valid / 40 | L1 strict → diagnostic | KL strict → diagnostic |",
              "| --- | --- | ---: | ---: | ---: |"]
    for split in SPLITS:
        for method in METHODS:
            row = summary[method][split]
            l1, kl = (row["metrics"][metric] for metric in METRICS)
            lines.append(f"| {split} | {method} | {row['strict_valid']} → {row['diagnostic_valid']} | "
                         f"{l1['strict_mean']:.6f} → {l1['diagnostic_mean']:.6f} | "
                         f"{kl['strict_mean']:.6f} → {kl['diagnostic_mean']:.6f} |")
    lines += ["", "The JSON artifact retains all 360 row-level records, 72 method/world means, and paired "
              "world vectors for BaseQwen−LoRA, MLP−LoRA, and BaseQwen−MLP, separately by stratum and overall. "
              "These are descriptive summaries of the fixed heterogeneous grid, with no new bootstrap or calibrated population interval.", "",
              "## Interpretation and limits", "",
              "This comparison separates sensitivity to the exact-sum interface rule from the allocation content in "
              "these saved outputs. It does not establish the performance of a normalized-output policy in closed loop: "
              "changing an early allocation would change later observations and prompts. Query cost, recovery accuracy, "
              "and certified stopping for that counterfactual policy are therefore unmeasured.", "",
              "The initial BaseQwen prompt specified the legal input/output allocation interface but did not supply "
              "an objective-aware explanation of the teacher's KL design criterion or worked allocation examples. "
              "This limits conclusions about pretrained Qwen's best achievable planning ability. The saved base-model "
              "initialization and the trained adapter remain the actual comparisons; this diagnostic does not create a "
              "new objective-aware baseline or tune a prompt after outcomes.", "",
              "The primary parser/policy, trained weights, experimental configuration, and report sources were not edited. "
              "No model inference, worlds, queries, private provenance, or new labels were used. A later proposal to normalize "
              "outputs would require a separate frozen evaluation and cannot inherit the current closed-loop claims.", "",
              "## Reproduction and provenance", "",
              "Run `PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/wcl_v100_venv/bin/python audit/parser_sensitivity.py` "
              "from the T1 experiment directory. The script refuses to overwrite outputs. "
              "Input files and the diagnostic source are SHA-256 bound in the JSON artifact.", "",
              "- [Complete diagnostic JSON](../artifacts/diagnostics/parser_sensitivity.json)",
              "- [Diagnostic source](parser_sensitivity.py)",
              f"- Diagnostic JSON SHA-256: `{result['artifact_sha256']}`", ""]
    return "\n".join(lines)


def main():
    checks = _self_checks()
    source_paths = [ROOT / "artifacts/evaluation/offline_predictions.jsonl",
                    ROOT / "artifacts/data/manifest.json", ROOT / "t1/evaluate.py",
                    ROOT / "t1/core.py", Path(__file__).resolve()]
    contents = {str(path.relative_to(ROOT)): path.read_bytes() for path in source_paths}
    rows = [json.loads(line) for line in contents["artifacts/evaluation/offline_predictions.jsonl"].splitlines()]
    manifest = json.loads(contents["artifacts/data/manifest.json"])
    expected_worlds = _verify_coverage(rows, manifest)
    records = []
    for row in rows:
        state, method = row["state"], row["method"]
        strict = metric_subset(row["teacher_weights"], row["weights10"], state["action_mask"])
        if any(not math.isclose(strict[key], row[key], rel_tol=1e-12, abs_tol=1e-12) for key in METRICS):
            raise ValueError("Frozen metric reconstruction disagrees with saved primary output")
        diagnostic = None
        if method == "MLP":
            weights, valid = row["weights10"], row["valid"]
        else:
            frozen_parse = parse_percent(row["prediction"]["raw"], state)
            if frozen_parse["valid"] != row["valid"] or any(abs(a - b) > 1e-12 for a, b in zip(frozen_parse["weights"], row["weights10"])):
                raise ValueError("Frozen parser reconstruction disagrees with saved primary output")
            diagnostic = relaxed_raw(row["prediction"]["raw"], state["action_mask"])
            weights, valid = diagnostic["weights"], diagnostic["valid"]
            if row["valid"] and not valid:
                raise ValueError("Relaxation unexpectedly rejected a strict-valid output")
        updated = metric_subset(row["teacher_weights"], weights, state["action_mask"])
        record = {"method": method, "world_id": row["world_id"], "row_id": row["row_id"],
                  "split": row["split"], "position": row["position"],
                  "source_state_and_teacher_sha256": digest_json({"state": state, "teacher_weights": row["teacher_weights"]}),
                  "raw": row["prediction"]["raw"], "saved_error": row["prediction"].get("error"),
                  "strict_valid": row["valid"], "diagnostic_valid": valid,
                  "recovered_sum_only": not row["valid"] and valid,
                  "diagnostic_parse": diagnostic, "strict_weights": row["weights10"],
                  "diagnostic_weights": weights, "strict_metrics": strict, "diagnostic_metrics": updated,
                  "delta_metrics": {key: updated[key] - strict[key] for key in METRICS}}
        if method == "MLP" and any(record["delta_metrics"].values()):
            raise AssertionError("The MLP control changed")
        records.append(record)
    worlds, pairs = _worlds_and_pairs(records)
    result = {
        "status": "completed", "analysis_type": "OUTCOME_INFORMED_POST_HOC_OFFLINE_PARSER_SENSITIVITY",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "selection_context": "Requested after observing strict parser validity counts; all outputs included regardless of result",
        "primary_results_unchanged": True, "closed_loop_counterfactual_measured": False,
        "relaxed_condition": "exact sum100 -> any positive sum then normalize; every other contract unchanged",
        "frozen_metric_definition": "L1 and teacher || normalized(student + 1e-8 on legal actions)",
        "coverage": {"states_per_method": 120, "methods": list(METHODS), "rows": 360,
                     "worlds_per_stratum": {key: len(value) for key, value in expected_worlds.items()},
                     "positions_per_world": list(POSITIONS)},
        "new_model_calls": 0, "new_worlds": 0, "new_online_queries": 0, "new_labels": 0,
        "private_data_read": False, "parser_self_checks": checks,
        "source_bindings": {name: {"sha256": digest_bytes(content), "bytes": len(content)}
                            for name, content in contents.items()},
        "summary": _summarize(records), "world_means": worlds, "paired_world_vectors": pairs,
        "records": records,
        "limitations": ["Outcome-informed post-hoc descriptive sensitivity, not frozen primary analysis",
                        "No counterfactual closed-loop cost/recovery/stopping inference",
                        "Base initialization lacked an objective-aware teacher design explanation/examples",
                        "No new bootstrap, prompt search, parser deployment, model call, or world generation"],
    }
    for path in source_paths:
        name = str(path.relative_to(ROOT))
        if digest_bytes(path.read_bytes()) != digest_bytes(contents[name]):
            raise RuntimeError("Source changed during diagnostic: " + name)
    target = ROOT / "artifacts/diagnostics/parser_sensitivity.json"
    report = ROOT / "audit/PARSER_SENSITIVITY.md"
    if target.exists() or report.exists():
        raise FileExistsError("Refuse to overwrite post-hoc diagnostic artifacts")
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with target.open("xb") as handle:
        handle.write(encoded)
    report.write_text(_report({**result, "artifact_sha256": digest_bytes(encoded)}))
    print(json.dumps({"status": result["status"], "artifact": str(target), "report": str(report),
                      "summary": {method: result["summary"][method]["all"] for method in METHODS}}, indent=2))


if __name__ == "__main__":
    main()
