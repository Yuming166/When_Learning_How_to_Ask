"""Frozen T2 descriptive analysis. No Torch, model loading, or simulation.

Analysis is driven by the explicit public expected-key manifests. Failed paths
remain in coverage denominators; incomplete paired metrics are unavailable.
All resampling units are whole worlds, retaining every R or snapshot together.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = "Fused-Original"
OFFLINE_MODELS = ("T1-MLP", "T2-MLP", "DeepSets-KL", "DeepSets-Info")
TIMINGS = ("estimation", "planning", "inference", "glr", "score_glr", "gate", "environment", "wall", "cpu")
RANGE_NOTE = "95% percentile world-cluster bootstrap descriptive range; not a calibrated confidence or noninferiority interval"


class CoverageError(ValueError):
    """Missing, duplicate, unexpected, or internally inconsistent evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CoverageError(message)


def _finite(value: Any, label: str, *, nonnegative: bool = True) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label}: expected number")
    value = float(value)
    _require(math.isfinite(value) and (not nonnegative or value >= 0), f"{label}: invalid number")
    return value


def _key(row: dict, fields: tuple[str, ...]) -> tuple:
    _require(all(field in row for field in fields), f"Missing identity field: {fields}")
    return tuple(row[field] for field in fields)


def _index(rows: list[dict], fields: tuple[str, ...], label: str) -> dict[tuple, dict]:
    result = {}
    for row in rows:
        key = _key(row, fields)
        _require(key not in result, f"Duplicate {label}: {key}")
        result[key] = row
    return result


def validate_plan(plan: dict, config: dict) -> tuple[dict, dict]:
    """Validate the manifest itself against frozen grid sizes and model scope."""
    paths = _index(plan["expected_paths"], ("world_id", "split", "R", "method"), "planned path")
    offline = _index(plan["expected_offline"], ("world_id", "split", "position", "model"), "planned offline state")
    e, data = config["evaluation"], config["data"]
    main_splits = {"eval_" + split for split in e["splits"]}
    world_splits = defaultdict(set)
    for row in paths.values():
        world_splits[row["split"]].add(row["world_id"])
    _require(set(world_splits) == main_splits | {"eval_variable"}, "Unexpected or missing evaluation stratum")
    seen_worlds = set()
    for split, worlds in world_splits.items():
        expected_n = e["extra_variable_worlds"] if split == "eval_variable" else e["worlds_per_split"]
        _require(len(worlds) == expected_n, f"Wrong world denominator for {split}")
        _require(not seen_worlds.intersection(worlds), "A world appears in multiple evaluation strata")
        seen_worlds.update(worlds)
        risks = [e["extra_variable_R"]] if split == "eval_variable" else e["risks"]
        for world in worlds:
            expected = {(world, split, R, m) for R in risks for m in e["methods"]}
            actual = {key for key in paths if key[0] == world}
            _require(actual == expected, f"Incomplete planned world: {world}")
            for key in expected:
                status = "not_applicable" if split == "eval_variable" and key[3] == "T1-MLP" else "completed"
                _require(paths[key]["status"] == status, f"Wrong planned applicability: {key}")
    offline_worlds = defaultdict(set)
    for row in offline.values():
        offline_worlds[row["split"]].add(row["world_id"])
    _require(set(offline_worlds) == set(data["splits"]), "Wrong offline split coverage")
    positions = set(range(len(data["snapshot_times"])))
    for split, worlds in offline_worlds.items():
        _require(len(worlds) == data["test_worlds_per_split"], f"Wrong offline world denominator: {split}")
        _require(not seen_worlds.intersection(worlds), "Offline/evaluation world overlap")
        seen_worlds.update(worlds)
        for world in worlds:
            expected = {(world, split, pos, model) for pos in positions for model in OFFLINE_MODELS}
            actual = {key for key in offline if key[0] == world}
            _require(actual == expected, f"Incomplete planned offline world: {world}")
            dims = {offline[key]["state_d"] for key in expected}
            _require(len(dims) == 1 and next(iter(dims)) in (2, 3, 4), "Invalid offline world dimensions")
            d = next(iter(dims))
            for key in expected:
                status = "not_applicable" if key[3] == "T1-MLP" and d != 4 else "completed"
                _require(offline[key]["status"] == status, "Wrong offline applicability")
    return paths, offline


def _costs(row: dict, online_field: str, label: str) -> None:
    online = _finite(row[online_field], label + ".online")
    costs = row["costs"]
    _require(set(costs) >= {"task", "type", "offline"}, label + ": missing acquisition cost")
    task, type_, offline = (_finite(costs[k], label + "." + k) for k in ("task", "type", "offline"))
    _require(task + type_ == online, label + ": task/type counts disagree with online")
    _require(_finite(row["total_acquisition"], label + ".total") == online + offline, label + ": total acquisition mismatch")


def validate_coverage(paths: list[dict], offline: list[dict], plan: dict, config: dict, budgets: list[int]) -> dict:
    expected_paths, expected_offline = validate_plan(plan, config)
    actual_paths = _index(paths, ("world_id", "split", "R", "method"), "path")
    actual_offline = _index(offline, ("world_id", "split", "position", "model"), "offline state")
    _require(set(actual_paths) == set(expected_paths), f"Path coverage mismatch: missing={len(set(expected_paths)-set(actual_paths))}, unexpected={len(set(actual_paths)-set(expected_paths))}")
    _require(set(actual_offline) == set(expected_offline), f"Offline coverage mismatch: missing={len(set(expected_offline)-set(actual_offline))}, unexpected={len(set(actual_offline)-set(expected_offline))}")
    _require(len(budgets) == 2 and budgets == sorted(set(budgets)) and all(type(b) is int and b > 0 for b in budgets), "Expected two distinct frozen readout budgets")
    readouts_observed = 0
    for key, row in actual_paths.items():
        expected = expected_paths[key]
        status = row["status"]
        if expected["status"] == "not_applicable":
            _require(status == "not_applicable", f"Out-of-scope method executed: {key}")
            continue
        _require(status in ("completed", "failed"), f"Applicable path silently excluded: {key}")
        readings = row.get("readouts", [])
        readout_map = _index(readings, ("budget",), "budget readout")
        _require(set(readout_map) <= {(b,) for b in budgets}, f"Unexpected readout budget: {key}")
        for readout in readings:
            _costs(readout, "effective_online", f"readout {key}")
            _require(readout["effective_online"] <= readout["budget"], "Readout uses future observations")
            _require(type(readout["guess_exact"]) is bool and type(readout["absorbed"]) is bool, "Invalid readout status")
        readouts_observed += len(readings)
        if status == "failed":
            continue  # Prefixes are retained, but absent measurements are not filled.
        _require(set(readout_map) == {(b,) for b in budgets}, f"Completed path missing fixed-budget evidence: {key}")
        _costs(row, "online", f"path {key}")
        for timing in TIMINGS:
            _finite(row["timings"][timing], f"{key}.{timing}")
        for field in ("certified", "abstained", "final_guess_exact"):
            _require(type(row[field]) is bool, f"Invalid {field}: {key}")
        _require(row["abstained"] == (not row["certified"]), f"Abstention/certification mismatch: {key}")
        _require(type(row["certified_exact"]) is bool if row["certified"] else row["certified_exact"] is None, f"Invalid certified correctness: {key}")
        if row["certified"]:
            _require(row["certified_exact"] == row["final_guess_exact"], "Certificate/final guess mismatch")
        for reading in readings:
            _require(reading["costs"]["offline"] == row["costs"]["offline"], "Readout calibration acquisition mismatch")
            _require(reading["effective_online"] == min(row["online"], reading["budget"]), "Incorrect absorbed readout cost")
    for key, row in actual_offline.items():
        expected = expected_offline[key]
        _require(row["status"] == expected["status"] and row["state_d"] == expected["state_d"], f"Offline applicability mismatch: {key}")
        if row["status"] == "not_applicable":
            continue
        for field in ("allocation_l1", "forward_kl", "teacher_K", "inference_wall_seconds"):
            _finite(row[field], f"offline {key}.{field}")
        _require(row["teacher_K"] > 0 and type(row["radial_infinite"]) is bool, "Invalid offline radial contract")
        if row["radial_infinite"]:
            _require(row["radial_cost"] is None and row["relative_regret"] is None, "Infinite radial value must use explicit null and flag")
        else:
            radial = _finite(row["radial_cost"], "radial_cost")
            regret = _finite(row["relative_regret"], "relative_regret", nonnegative=False)
            _require(abs(regret - (radial/row["teacher_K"]-1)) <= 1e-5*max(1, abs(regret)), "Radial regret arithmetic mismatch")
    main_rows = [r for r in paths if r["split"] != "eval_variable"]
    main_applicable = [r for r in main_rows if r["status"] != "not_applicable"]
    variable_applicable = [r for r in paths if r["split"] == "eval_variable" and r["status"] != "not_applicable"]
    return {
        "status": "complete_key_coverage", "path_records_expected": len(expected_paths),
        "path_records_observed": len(paths), "path_status_counts": dict(Counter(r["status"] for r in paths)),
        "main_path_records": len(main_rows), "main_applicable": len(main_applicable),
        "variable_applicable": len(variable_applicable),
        "readout_cells_expected": 2*(len(main_applicable)+len(variable_applicable)),
        "main_readout_cells_expected": 2*len(main_applicable),
        "variable_readout_cells_expected": 2*len(variable_applicable),
        "readout_cells_observed": readouts_observed,
        "offline_records_expected": len(expected_offline), "offline_records_observed": len(offline),
        "offline_status_counts": dict(Counter(r["status"] for r in offline)),
        "all_applicable_paths_completed": all(r["status"] == "completed" for r in paths if r["status"] != "not_applicable"),
    }


def _extended(value: float) -> dict:
    return {"value": float(value) if math.isfinite(value) else None, "infinite": bool(math.isinf(value))}


def clustered_ratio(world_ids: list[str], numerator: list[float], denominator: list[float], *, resamples: int = 4000, seed: int = 731102) -> dict:
    """Ratio of sums with a whole-world, all-risk cluster bootstrap."""
    _require(len(world_ids) == len(numerator) == len(denominator) and len(world_ids) > 0, "Empty or mismatched paired vectors")
    _require(resamples > 0, "Invalid bootstrap count")
    groups = defaultdict(lambda: [0., 0.])
    for world, num, den in zip(world_ids, numerator, denominator):
        groups[world][0] += _finite(num, "paired numerator")
        groups[world][1] += _finite(den, "paired denominator")
    values = np.asarray([groups[w] for w in sorted(groups)], dtype=float)
    if values[:, 1].sum() <= 0:
        return {"available": False, "reason": "zero aggregate denominator", "world_clusters": len(values), "paired_records": len(world_ids)}
    samples = np.random.default_rng(seed).integers(0, len(values), size=(resamples, len(values)))
    totals = values[samples].sum(1)
    ratios = np.divide(totals[:, 0], totals[:, 1], out=np.full(resamples, np.inf), where=totals[:, 1] > 0)
    limits = np.quantile(ratios, [.025, .975], method="inverted_cdf")
    return {"available": True, "point": float(values[:, 0].sum()/values[:, 1].sum()),
            "descriptive_bootstrap_range": [_extended(float(v)) for v in limits],
            "world_clusters": len(values), "paired_records": len(world_ids),
            "resamples": resamples, "seed": seed, "range_note": RANGE_NOTE,
            "bootstrap_zero_denominator_count": int((totals[:, 1] <= 0).sum()),
            "estimand": "ratio_of_sums; every repeated R retained inside its world cluster"}


def world_mean(values: list[float], *, resamples: int, seed: int) -> dict:
    """Input is one mean per world; infinity is retained, never filtered."""
    _require(bool(values) and all(not math.isnan(v) for v in values), "Invalid world means")
    array = np.asarray(values, dtype=float)
    samples = np.random.default_rng(seed).integers(0, len(array), size=(resamples, len(array)))
    draws = array[samples].mean(1)
    limits = np.quantile(draws, [.025, .975], method="inverted_cdf")
    return {"point": _extended(float(array.mean())), "descriptive_bootstrap_range": [_extended(float(v)) for v in limits],
            "world_clusters": len(array), "infinite_worlds": int(np.isinf(array).sum()),
            "resamples": resamples, "seed": seed, "range_note": RANGE_NOTE}


def summarize_paths(paths: list[dict], budgets: list[int]) -> tuple[list[dict], list[dict]]:
    grouped = defaultdict(list)
    for row in paths:
        grouped[(row["split"], row["R"], row["method"])].append(row)
    summary, readouts = [], []
    for (split, R, method), rows in sorted(grouped.items()):
        applicable = [r for r in rows if r["status"] != "not_applicable"]
        completed = [r for r in applicable if r["status"] == "completed"]
        complete = bool(applicable) and len(completed) == len(applicable)
        record = {"split": split, "R": R, "method": method, "expected_records": len(rows),
                  "applicable": len(applicable), "completed": len(completed),
                  "failed": len(applicable)-len(completed), "not_applicable": len(rows)-len(applicable),
                  "certified": sum(r["certified"] for r in completed),
                  "wrong_certificates": sum(r["certified"] and not r["certified_exact"] for r in completed),
                  "abstained": sum(r["abstained"] for r in completed),
                  "final_guess_exact_observed": sum(r["final_guess_exact"] for r in completed),
                  "cost_metrics_available": complete,
                  "online_restricted_cost_mean": float(np.mean([r["online"] for r in completed])) if complete else None,
                  "total_acquisition_restricted_cost_mean": float(np.mean([r["total_acquisition"] for r in completed])) if complete else None,
                  "timing_seconds_total": {k: sum(r["timings"][k] for r in completed) if complete else None for k in TIMINGS}}
        record["certification_yield_expected"] = record["certified"]/len(applicable) if applicable else None
        summary.append(record)
        for budget in budgets:
            observed = [reading for row in applicable for reading in row.get("readouts", []) if reading["budget"] == budget]
            correct = sum(r["guess_exact"] for r in observed)
            all_present = bool(applicable) and len(observed) == len(applicable)
            readouts.append({"split": split, "R": R, "method": method, "budget": budget,
                            "expected_applicable": len(applicable), "observed": len(observed),
                            "missing": len(applicable)-len(observed), "exact_count": correct,
                            "exact_rate": correct/len(applicable) if all_present else None,
                            "exact_observed_fraction": correct/len(observed) if observed else None,
                            "exact_yield_expected": correct/len(applicable) if applicable else None,
                            "absorbed": sum(r["absorbed"] for r in observed),
                            "mean_effective_online": float(np.mean([r["effective_online"] for r in observed])) if all_present else None,
                            "mean_total_acquisition": float(np.mean([r["total_acquisition"] for r in observed])) if all_present else None,
                            "ceiling_flag": bool(all_present and correct == len(applicable))})
    return summary, readouts


def paired_analysis(paths: list[dict], config: dict) -> tuple[list[dict], list[dict]]:
    indexed = {(r["world_id"], r["R"], r["method"]): r for r in paths}
    vectors = []
    for row in paths:
        if row["method"] == REFERENCE or row["status"] == "not_applicable":
            continue
        teacher = indexed[(row["world_id"], row["R"], REFERENCE)]
        complete = row["status"] == teacher["status"] == "completed"
        item = {"world_id": row["world_id"], "split": row["split"], "R": row["R"], "method": row["method"],
                "reference": REFERENCE, "complete_pair": complete, "candidate_status": row["status"], "teacher_status": teacher["status"]}
        if complete:
            for prefix, source in (("candidate", row), ("teacher", teacher)):
                item.update({prefix+"_online": source["online"], prefix+"_total_acquisition": source["total_acquisition"],
                             prefix+"_inclusive_compute": sum(source["timings"][k] for k in ("estimation", "planning", "inference")),
                             prefix+"_wall": source["timings"]["wall"], prefix+"_certified": source["certified"],
                             prefix+"_certified_exact": source["certified_exact"], prefix+"_abstained": source["abstained"]})
        vectors.append(item)
    groups = defaultdict(list)
    for row in vectors:
        scopes = [(row["split"], row["R"]), (row["split"], "pooled_R")]
        if row["split"] != "eval_variable":
            scopes += [("main_pooled", row["R"]), ("main_pooled", "pooled_R")]
        for split, R in scopes:
            groups[(split, R, row["method"])].append(row)
    results = []
    bs = {"resamples": config["analysis"]["bootstrap_resamples"], "seed": config["analysis"]["bootstrap_seed"]}
    for (split, R, method), rows in sorted(groups.items(), key=lambda item: str(item[0])):
        complete = all(r["complete_pair"] for r in rows)
        result = {"split": split, "R": R, "method": method, "reference": REFERENCE,
                  "expected_pairs": len(rows), "complete_pairs": sum(r["complete_pair"] for r in rows),
                  "world_clusters": len({r["world_id"] for r in rows}), "paired_metrics_available": complete}
        if complete:
            worlds = [r["world_id"] for r in rows]
            for metric, numerator, denominator in (
                ("online_restricted_cost_ratio", "candidate_online", "teacher_online"),
                ("total_acquisition_restricted_cost_ratio", "candidate_total_acquisition", "teacher_total_acquisition"),
                ("inclusive_compute_speedup", "teacher_inclusive_compute", "candidate_inclusive_compute"),
                ("wall_speedup", "teacher_wall", "candidate_wall"),
            ):
                result[metric] = clustered_ratio(worlds, [r[numerator] for r in rows], [r[denominator] for r in rows], **bs)
            strict = all(r["candidate_certified"] and r["teacher_certified"] and
                         r["candidate_certified_exact"] is True and r["teacher_certified_exact"] is True and
                         not r["candidate_abstained"] and not r["teacher_abstained"] for r in rows)
            query, speed = result["online_restricted_cost_ratio"], result["inclusive_compute_speedup"]
            q_hi = query.get("descriptive_bootstrap_range", [{}, {}])[1].get("value")
            s_lo = speed.get("descriptive_bootstrap_range", [{}, {}])[0].get("value")
            result["engineering_flags"] = {
                "all_candidate_and_teacher_paths_certified_correctly_without_abstention": strict,
                "query_descriptive_range_upper_le_1_05": q_hi is not None and q_hi <= config["go_targets"]["query_ratio_upper"],
                "inclusive_speedup_descriptive_range_lower_ge_2": s_lo is not None and s_lo >= config["go_targets"]["planning_speedup_lower"],
            }
            result["all_engineering_flags_pass"] = all(result["engineering_flags"].values())
        else:
            result["unavailable_reason"] = "At least one planned pair failed; no completed-pair-only estimate"
            result["all_engineering_flags_pass"] = False
        result["decision"] = "manual_review_required; descriptive ranges do not establish population noninferiority"
        results.append(result)
    return results, sorted(vectors, key=lambda r: (r["split"], r["world_id"], r["R"], r["method"]))


def offline_analysis(rows: list[dict], config: dict) -> tuple[list[dict], list[dict]]:
    groups = defaultdict(list)
    for row in rows:
        groups[("all_applicable", row["split"], row["model"])].append(row)
        if row["state_d"] == 4:
            groups[("matched_d4", row["split"], row["model"])].append(row)
    result, world_vectors = [], []
    bs = {"resamples": config["analysis"]["bootstrap_resamples"], "seed": config["analysis"]["bootstrap_seed"]}
    for (scope, split, model), group in sorted(groups.items()):
        completed = [r for r in group if r["status"] == "completed"]
        worlds = defaultdict(list)
        for row in completed:
            worlds[row["world_id"]].append(row)
        per_world = []
        for world, states in sorted(worlds.items()):
            values = {"allocation_l1": float(np.mean([r["allocation_l1"] for r in states])),
                      "forward_kl": float(np.mean([r["forward_kl"] for r in states])),
                      "relative_regret": float(np.mean([np.inf if r["radial_infinite"] else r["relative_regret"] for r in states])),
                      "inference_wall_seconds": float(np.mean([r["inference_wall_seconds"] for r in states]))}
            per_world.append(values)
            world_vectors.append({"scope": scope, "split": split, "model": model, "world_id": world,
                                  "states": len(states), "radial_infinite_states": sum(r["radial_infinite"] for r in states),
                                  "world_means": {k: _extended(v) for k, v in values.items()}})
        item = {"scope": scope, "split": split, "model": model, "expected_states": len(group),
                "completed_states": len(completed), "not_applicable_states": len(group)-len(completed),
                "world_clusters": len(worlds), "radial_infinite_states": sum(r["radial_infinite"] for r in completed),
                "averaging": "six positions averaged within each world first; equal weight across eligible worlds; infinity retained"}
        item["metrics"] = {metric: world_mean([w[metric] for w in per_world], **bs) for metric in
                           ("allocation_l1", "forward_kl", "relative_regret", "inference_wall_seconds")} if per_world else {}
        result.append(item)
    return result, world_vectors


def aggregate(paths: list[dict], offline: list[dict], plan: dict, config: dict, budgets: list[int]) -> dict:
    coverage = validate_coverage(paths, offline, plan, config, budgets)
    path_summary, readout_summary = summarize_paths(paths, budgets)
    paired, paired_vectors = paired_analysis(paths, config)
    offline_summary, offline_vectors = offline_analysis(offline, config)
    return {"coverage": coverage, "readout_budgets": budgets, "path_summary": path_summary,
            "fixed_budget_summary": readout_summary, "paired_summary": paired, "paired_vectors": paired_vectors,
            "offline_summary": offline_summary, "offline_world_vectors": offline_vectors,
            "analysis_scope": config["analysis"]["scope"], "range_note": RANGE_NOTE,
            "decision": "manual_review_required", "reference": REFERENCE,
            "native_reference_note": "Native-Fused-Original is shown separately; the main matched reference is Fused-Original"}


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, dict) and "infinite" in value:
        return "infinity" if value["infinite"] else _fmt(value["value"], digits)
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def _range_text(statistic: dict | None) -> str:
    if not statistic or not statistic.get("available", True):
        return "unavailable"
    point = statistic["point"]
    limits = statistic["descriptive_bootstrap_range"]
    return f"{_fmt(point)} [{_fmt(limits[0])}, {_fmt(limits[1])}]"


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"] +
                     ["| " + " | ".join(_fmt(v).replace("|", "/") for v in row) + " |" for row in rows])


def evaluation_report(result: dict) -> str:
    cov = result["coverage"]
    lines = ["# T2 evaluation", "", "Final decision: **manual review required**. This report does not automatically declare GO.", "",
             f"Observed {cov['path_records_observed']}/{cov['path_records_expected']} planned path records; "
             f"main applicable paths {cov['main_applicable']}; variable-d applicable paths {cov['variable_applicable']}. "
             f"Status counts: {json.dumps(cov['path_status_counts'], sort_keys=True)}. "
             f"Fixed-budget cells observed {cov['readout_cells_observed']}/{cov['readout_cells_expected']} "
             f"(main {cov['main_readout_cells_expected']}, variable-d {cov['variable_readout_cells_expected']}).", "",
             f"Offline records: {cov['offline_records_observed']}/{cov['offline_records_expected']}; "
             f"statuses {json.dumps(cov['offline_status_counts'], sort_keys=True)}.", "",
             "The main matched teacher is **Fused-Original**. Native-Fused-Original is a separate native-scheduler reference. "
             "Warm-KL is retained as the warm-start optimization baseline. T1-MLP is the frozen original comparator; "
             "T2-MLP uses the same legal posterior features as the new structural models.", "",
             "All cap abstentions are included in online and total-acquisition restricted costs. These costs are not "
             "means over successful paths and are not uncensored mean stopping times. Failed pairs make the paired "
             "estimate unavailable instead of being silently removed.", "",
             "Repeated risks and snapshots are clustered by whole world. Main pooled comparisons contain 24 world "
             "clusters, not 72 independent worlds; each stratum has six worlds. Offline metrics average the six "
             "snapshots within a world before comparing worlds. Every infinity remains in the radial mean and "
             "bootstrap distribution. Matched-d4 offline tables keep the T1 comparator on a common state set.", "",
             RANGE_NOTE + ". " + result["analysis_scope"], "", "## Main paired engineering readouts", "",
             "Each entry is point [descriptive bootstrap lower, upper]. The engineering target is online query ratio "
             "at most 1.05 and inclusive estimator/planner/inference speedup at least 2. A point estimate alone is "
             "insufficient. Both candidate and matched teacher must certify every applicable path correctly, with "
             "zero abstentions, before the strict flags can all pass. Passing flags still requires manual interpretation.", ""]
    primary = [r for r in result["paired_summary"] if r["split"] == "main_pooled" and r["R"] == "pooled_R"]
    lines += [_table(["Method", "Pairs / clusters", "Online restricted ratio", "Total acquisition ratio", "Inclusive compute speedup", "All strict flags"],
                     [[r["method"], f"{r['complete_pairs']}/{r['expected_pairs']} / {r['world_clusters']}",
                       _range_text(r.get("online_restricted_cost_ratio")), _range_text(r.get("total_acquisition_restricted_cost_ratio")),
                       _range_text(r.get("inclusive_compute_speedup")), r["all_engineering_flags_pass"]] for r in primary]), "",
              "## Per-stratum and risk path denominators", "",
              _table(["Stratum", "R", "Method", "Complete / applicable", "N/A", "Certified", "Wrong cert.", "Abstain", "Mean online restricted", "Mean total acquisition"],
                     [[r["split"], r["R"], r["method"], f"{r['completed']}/{r['applicable']}", r["not_applicable"], r["certified"],
                       r["wrong_certificates"], r["abstained"], r["online_restricted_cost_mean"], r["total_acquisition_restricted_cost_mean"]] for r in result["path_summary"]]), "",
              "## Fixed-budget exact recovery and ceiling flags", "",
              "Exact rate uses the full expected applicable denominator only when every planned readout exists. "
              "The table retains missing-readout counts; expected-denominator exact yield and observed fractions "
              "are separate JSON fields. An early certified path is absorbed with its actual acquisition cost. "
              "A ceiling flag means all observed planned readouts in that cell are exact; it is descriptive, not a generalization guarantee.", "",
              _table(["Stratum", "R", "Method", "Budget", "Exact / expected", "Observed", "Missing", "Exact rate", "Absorbed", "Ceiling"],
                     [[r["split"], r["R"], r["method"], r["budget"], f"{r['exact_count']}/{r['expected_applicable']}", r["observed"],
                       r["missing"], r["exact_rate"], r["absorbed"], r["ceiling_flag"]] for r in result["fixed_budget_summary"]]), "",
              "## Exact offline allocation quality", "",
              _table(["Scope", "Split", "Model", "States / planned", "N/A", "Worlds", "Infinite radial states", "L1", "Forward KL", "Exact relative radial regret", "Inference seconds"],
                     [[r["scope"], r["split"], r["model"], f"{r['completed_states']}/{r['expected_states']}", r["not_applicable_states"], r["world_clusters"], r["radial_infinite_states"],
                       *[_range_text(r["metrics"].get(m)) for m in ("allocation_l1", "forward_kl", "relative_regret", "inference_wall_seconds")]] for r in result["offline_summary"]]), "",
              "The information-training loss used finite cuts; this offline table uses the separate exact radial evaluator. "
              "The experiment supports only this simulator, frozen condition grid, models, and budget. No novelty, human-dialogue, or population noninferiority claim is made.", ""]
    return "\n".join(lines)


def computational_report(result: dict, receipts: dict) -> str:
    lines = ["# T2 computational cost", "", "The target speedup is the ratio of sums of **estimation + planning + inference** seconds "
             "for the matched Fused-Original teacher and each candidate. It includes Fused estimation. "
             "Gate, stopping GLR, evaluation-only score GLR, environment, wall and CPU are reported separately. "
             "Wall speedup is an additional measured quantity and includes their realized overhead. "
             "Summed component timers are not asserted to partition wall time exactly.", "",
             "All ratios use complete planned pairs, including cap abstentions; no successful-path-only compute average is used. "
             "Risk repetitions stay inside the same world during resampling. " + RANGE_NOTE + ".", "",
             "## Matched paired compute", ""]
    primary = [r for r in result["paired_summary"] if r["split"] == "main_pooled" and r["R"] == "pooled_R"]
    lines += [_table(["Method", "Pairs", "World clusters", "Inclusive compute speedup", "Wall speedup"],
                     [[r["method"], f"{r['complete_pairs']}/{r['expected_pairs']}", r["world_clusters"],
                       _range_text(r.get("inclusive_compute_speedup")), _range_text(r.get("wall_speedup"))] for r in primary]), "",
              "## Per-stratum, risk and method timing totals", "",
              _table(["Stratum", "R", "Method", "Complete / applicable", *TIMINGS],
                     [[r["split"], r["R"], r["method"], f"{r['completed']}/{r['applicable']}",
                       *[r["timing_seconds_total"][k] for k in TIMINGS]] for r in result["path_summary"]]), "",
              "## Preparation and training accounting", "",
              _table(["Stage", "Scope", "Outer wall seconds", "CPU seconds", "CPU scope", "Status"],
                     [[row["stage"], row["accounting_scope"], row["outer_wall_seconds"], row["cpu_seconds"], row["cpu_scope"], row["status"]]
                      for row in execution_accounting(receipts)]), "",
              "Raw preparation, training and evaluation execution receipts are preserved in `artifacts/analysis/execution_receipts.json`. "
              "They remain separate from policy-time speedups: teacher-label construction and network fitting are not free. "
              "Outer wall/CPU totals must not be added to their nested substage totals a second time. "
              "No break-even or amortized advantage is claimed without a declared deployment denominator.", "",
              "```json", json.dumps(receipts, indent=2, sort_keys=True, allow_nan=False), "```", "",
              "T1-MLP is the frozen historical reference, not an additional T2 fit. T2-MLP, DeepSets-KL and DeepSets-Info "
              "are the three new fixed final-checkpoint fits. Per-state inference latency is reported with the exact "
              "allocation-quality table and matched-d4 denominators in T2_EVALUATION.md.", ""]
    return "\n".join(lines)


def execution_accounting(receipts: dict) -> list[dict]:
    """Keep outer totals and nested model/stage costs explicitly separate."""
    rows = []
    for key, label in (("preparation_execution", "Preparation incl. data/labels and budget development"),
                       ("training_execution", "Three-fit training total"),
                       ("evaluation_execution", "Evaluation outer process/pool")):
        receipt = receipts.get(key, {})
        parent_only = "outer_parent_cpu_seconds" in receipt
        rows.append({"stage": label, "accounting_scope": "outer_total",
                     "outer_wall_seconds": receipt.get("outer_wall_seconds"),
                     "cpu_seconds": receipt.get("outer_parent_cpu_seconds") if parent_only else receipt.get("outer_cpu_seconds"),
                     "cpu_scope": "parent process only; excludes worker CPU" if parent_only else "current process",
                     "status": receipt.get("status", "not supplied")})
    training = receipts.get("training_execution", {})
    for kind, receipt in sorted(training.get("models", {}).items()):
        rows.append({"stage": kind, "accounting_scope": "component_of_training_total_do_not_add_again",
                     "outer_wall_seconds": receipt.get("outer_wall_seconds"), "cpu_seconds": receipt.get("outer_cpu_seconds"),
                     "cpu_scope": "current process", "status": "recorded"})
    prepare = receipts.get("preparation_execution", {})
    for key in ("data", "budget_development"):
        receipt = prepare.get(key, {})
        if receipt:
            rows.append({"stage": key, "accounting_scope": "component_of_preparation_total_do_not_add_again",
                         "outer_wall_seconds": receipt.get("wall_seconds"), "cpu_seconds": None,
                         "cpu_scope": "not separately measured", "status": receipt.get("status", "recorded")})
    return rows


def verify_analysis_freeze(root: Path) -> dict:
    """Hash verification only; deliberately does not import experiment modules."""
    path = root / "analysis_freeze.json"
    _require(path.is_file(), "Missing pre-outcome analysis source freeze")
    manifest = json.loads(path.read_text())
    _require({"t2/analyze.py", "tests/test_analysis.py"} <= set(manifest["files"]), "Analysis source/tests absent from freeze")
    for name, expected in manifest["files"].items():
        file = root / name
        _require(file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() == expected, "Frozen source changed: " + name)
    for name, expected in manifest.get("dependencies", {}).items():
        file = Path(name)
        _require(file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() == expected, "Frozen dependency changed: " + name)
    return {"status": "PASS", "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_files": len(manifest["files"]), "dependencies": len(manifest.get("dependencies", {}))}


def render_figures(result: dict, directory: Path) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    directory.mkdir(parents=True, exist_ok=True)
    outputs = []
    colors = dict(zip(OFFLINE_MODELS, ("#6f6f6f", "#31688e", "#35b779", "#b63679")))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    scopes = [r for r in result["offline_summary"] if r["scope"] == "matched_d4" and r["metrics"]]
    splits = sorted({r["split"] for r in scopes})
    for mi, model in enumerate(OFFLINE_MODELS):
        selected = {r["split"]: r for r in scopes if r["model"] == model}
        for si, split in enumerate(splits):
            if split not in selected:
                continue
            row = selected[split]
            x = si + (mi-1.5)*.16
            for ax, metric, scale in ((axes[0], "relative_regret", 1), (axes[1], "inference_wall_seconds", 1000)):
                stat = row["metrics"][metric]
                point = stat["point"]
                label = model if si == 0 else None
                if point["infinite"]:
                    ax.annotate(f"∞ ({row['radial_infinite_states']}/{row['completed_states']})", (x, .98), xycoords=("data", "axes fraction"), rotation=90, va="top", ha="center", color=colors[model], fontsize=8)
                    continue
                ax.scatter([x], [point["value"]*scale], color=colors[model], label=label, s=22)
                lo, hi = [v["value"] for v in stat["descriptive_bootstrap_range"]]
                if lo is not None and hi is not None:
                    ax.vlines(x, lo*scale, hi*scale, color=colors[model], linewidth=1.3)
    for ax in axes:
        ax.set_xticks(range(len(splits)), [s.replace("ood_", "OOD ").replace("id_test", "ID") for s in splits], rotation=15)
        ax.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Exact relative radial regret (world mean)")
    axes[1].set_ylabel("Inference milliseconds (world mean)")
    axes[0].set_title("Exact allocation quality; matched d=4")
    axes[1].set_title("Inference latency; matched d=4")
    handles, labels = axes[1].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="outside lower center", ncols=4, fontsize=8)
    for extension in ("png", "pdf"):
        path = directory / ("offline_exact_regret_latency." + extension)
        fig.savefig(path, dpi=180)
        outputs.append(str(path))
    plt.close(fig)
    selected = [r for r in result["paired_summary"] if r["split"] == "main_pooled" and r["R"] == "pooled_R"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    for i, row in enumerate(selected):
        for ax, metric in ((axes[0], "online_restricted_cost_ratio"), (axes[1], "inclusive_compute_speedup")):
            stat = row.get(metric)
            if not stat or not stat.get("available"):
                ax.text(.02, i, "unavailable", transform=ax.get_yaxis_transform(), fontsize=8)
                continue
            ax.scatter(stat["point"], i, color="#31688e", s=25)
            lo, hi = [v["value"] for v in stat["descriptive_bootstrap_range"]]
            if lo is not None and hi is not None:
                ax.hlines(i, lo, hi, color="#31688e")
    for ax in axes:
        ax.set_yticks(range(len(selected)), [r["method"] for r in selected])
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=.2)
    axes[0].axvline(1, color="gray", linestyle=":")
    axes[0].axvline(1.05, color="#b63679", linestyle="--", label="1.05 target")
    axes[0].set_xlabel("Online restricted query cost / matched teacher")
    axes[1].axvline(2, color="#b63679", linestyle="--", label="2x target")
    axes[1].set_xlabel("Teacher / student estimation + planning + inference")
    axes[0].set_title("Query cost, including cap abstentions")
    axes[1].set_title("Inclusive compute speedup")
    fig.suptitle("Main pooled worlds; descriptive world-cluster bootstrap ranges", fontsize=11)
    for extension in ("png", "pdf"):
        path = directory / ("paired_query_compute." + extension)
        fig.savefig(path, dpi=180)
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def analyze(root: str | Path = ROOT, outdir: str | Path | None = None) -> dict:
    root = Path(root)
    outdir = Path(outdir) if outdir is not None else root / "artifacts/analysis"
    if outdir.exists() and (not outdir.is_dir() or any(outdir.iterdir())):
        raise FileExistsError("Analysis output must be empty; refusing to replace an earlier attempt")
    for name in ("T2_EVALUATION.md", "COMPUTATIONAL_COST.md"):
        if (root/name).exists():
            raise FileExistsError("Refusing to replace an existing analysis report: " + name)
    outdir.mkdir(parents=True, exist_ok=True)
    started, cpu_started = time.perf_counter(), time.process_time()
    execution = {"status": "started", "analysis_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "python_version": platform.python_version(), "numpy_version": str(np.__version__),
                 "matplotlib_version": None, "model_calls": 0, "simulation_worlds": 0,
                 "scientific_retries": 0, "decision": "manual_review_required"}
    (outdir/"execution.json").write_text(json.dumps(execution, indent=2, sort_keys=True)+"\n")
    try:
        import matplotlib
        execution["matplotlib_version"] = str(matplotlib.__version__)
        freeze_check = verify_analysis_freeze(root)
        inputs = {"config": root/"config.json", "plan": root/"artifacts/plan_public.json",
                  "budget": root/"artifacts/BUDGET_FREEZE.json", "paths": root/"artifacts/evaluation/paths.jsonl",
                  "offline": root/"artifacts/evaluation/offline.jsonl",
                  "preparation_execution": root/"artifacts/prepare_execution.json",
                  "training_execution": root/"artifacts/training/execution.json",
                  "evaluation_execution": root/"artifacts/evaluation/execution.json"}
        missing = [str(path) for path in inputs.values() if not path.is_file()]
        _require(not missing, "Missing required analysis inputs: " + ", ".join(missing))
        config, plan, budget = (_read_json(inputs[k]) for k in ("config", "plan", "budget"))
        result = aggregate(_read_jsonl(inputs["paths"]), _read_jsonl(inputs["offline"]), plan, config, budget["readout_budgets"])
        execution["coverage"] = result["coverage"]
        receipts = {key: _read_json(inputs[key]) for key in ("preparation_execution", "training_execution", "evaluation_execution")}
        result["analysis_freeze_check"] = freeze_check
        result["execution_accounting"] = execution_accounting(receipts)
        result["provenance"] = {name: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in inputs.items()}
        result["analysis_source_sha256"] = execution["analysis_source_sha256"]
        for filename, value in (("aggregate.json", result), ("paired_vectors.json", result["paired_vectors"]),
                                ("offline_world_vectors.json", result["offline_world_vectors"]), ("execution_receipts.json", receipts)):
            (outdir/filename).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")
        (root/"T2_EVALUATION.md").write_text(evaluation_report(result))
        (root/"COMPUTATIONAL_COST.md").write_text(computational_report(result, receipts))
        execution["figures"] = render_figures(result, outdir/"figures")
        execution["status"] = "completed"
        return result
    except Exception as exc:
        execution.update(status="failed", error_type=type(exc).__name__, error=str(exc), automatic_retry=False)
        raise
    finally:
        execution.update(outer_wall_seconds=time.perf_counter()-started, outer_cpu_seconds=time.process_time()-cpu_started)
        (outdir/"execution.json").write_text(json.dumps(execution, indent=2, sort_keys=True, allow_nan=False)+"\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--outdir", type=Path)
    args = parser.parse_args()
    result = analyze(args.root, args.outdir)
    print(json.dumps({"coverage": result["coverage"], "decision": result["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
