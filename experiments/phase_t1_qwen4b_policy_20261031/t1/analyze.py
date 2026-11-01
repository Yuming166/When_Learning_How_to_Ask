"""CPU-only, post-run T1 analysis with full requested-world denominators.

No private seed/truth file is read, and no model, training or simulator is run.
"""
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
import platform
import sys
from time import perf_counter, process_time

sys.dont_write_bytecode = True
import numpy as np

from .data import world_plan, evaluation_world_plan
from .evaluate import METHODS, QWEN_METHODS

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_RESAMPLES = 4000
BOOTSTRAP_SEED = 731032
OFFLINE_METHODS = ("MLP", "BaseQwen", "LoRA")
TEST_SPLITS = ("id_test", "ood_parameters", "ood_partition")
EVAL_SPLITS = ("eval_id", "eval_ood_parameters", "eval_ood_partition")
POSITIONS = (0, 3, 6, 9, 15)
OFFLINE_METRICS = ("allocation_l1", "forward_kl_epsilon_1e8", "plugin_relative_information_deficit",
                   "percent_l1", "percent_exact", "teacher_rounding_l1", "student_rounding_l1",
                   "inference_wall_seconds", "inference_cpu_seconds", "prompt_tokens", "output_tokens")
LOSS_PAIRS = (("BaseQwen", "LoRA"), ("BaseQwen", "MLP"), ("MLP", "LoRA"))
RECOVERY_PAIRS = (("LoRA", "BaseQwen"), ("LoRA", "MLP"), ("LoRA", "AlignedBlock128"),
                  ("LoRA", "DNoTypeBlock128"), ("LoRA", "DTypeBlock128"),
                  ("MLP", "AlignedBlock128"), ("AlignedBlock128", "NativeAligned"))


def _mean_record(values, requested):
    present = [float(value) for value in values if value is not None]
    if any(not math.isfinite(value) for value in present):
        raise ValueError("Nonfinite metric in retained evaluation records")
    total = math.fsum(present)
    return {"requested": requested, "observed": len(present), "missing_or_undefined": requested - len(present),
            "sum": total, "mean": total / requested if requested and len(present) == requested else None,
            "observed_mean": total / len(present) if present else None}


def _paired(left, right, indices, draws):
    vector = [None if left.get(i) is None or right.get(i) is None else float(left[i]) - float(right[i]) for i in indices]
    complete = all(value is not None for value in vector)
    interval = None
    if complete:
        samples = np.asarray(vector)[draws].mean(axis=1)
        interval = np.quantile(samples, [.025, .975]).tolist()
    return {"world_ids": indices, "requested_pairs": len(indices), "observed_pairs": sum(v is not None for v in vector),
            "missing_pairs": sum(v is None for v in vector), "paired_vector": vector,
            "mean_difference": float(np.mean(vector)) if complete else None, "bootstrap_95": interval,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES if complete else 0,
            "exploratory": True, "multiplicity_adjusted": False}


def _groups_with_pool(groups):
    return list(groups.items()) + [("all_24_worlds", [world for worlds in groups.values() for world in worlds])]


def _world_draws(rng, split, count):
    if split == "all_24_worlds":
        # Preserve the declared equal stratum allocation in descriptive pooled resampling.
        return np.concatenate([rng.integers(0, 8, size=(BOOTSTRAP_RESAMPLES, 8)) + offset
                               for offset in (0, 8, 16)], axis=1)
    return rng.integers(0, count, size=(BOOTSTRAP_RESAMPLES, count))


def _index_unique(rows, key, expected, label):
    keys = [key(row) for row in rows]
    counts = Counter(keys)
    duplicates = [value for value, count in counts.items() if count != 1]
    unexpected = sorted(set(keys) - set(expected))
    if duplicates or unexpected:
        raise ValueError(f"{label}: duplicate or unexpected records; complete-case reduction is forbidden")
    return dict(zip(keys, rows)), {"requested": len(expected), "recorded": len(rows),
                                  "missing": [list(value) for value in sorted(set(expected) - set(keys))]}


def _validate_terminal(row):
    """Check stopping evidence without re-running the gate or reading truth."""
    diagnostic = row["mode"] == "fixed_confidence_diagnostic"
    if type(row["complete"]) is not bool or type(row["abstained"]) is not bool:
        raise ValueError("Completion/abstention flags must be booleans")
    if not diagnostic:
        if row["complete"] or row["abstained"] or row.get("strictly_certified_output") is not None:
            raise ValueError("Fixed-budget guesses cannot be certified outputs")
        return
    if row["abstained"] != (not row["complete"]):
        raise ValueError("Diagnostic output and abstention disagree")
    snapshots = row["snapshots"]
    certified_snapshots = [s for s in snapshots if (s.get("strict_certificate") or {}).get("certified") is True]
    if not row["complete"]:
        if certified_snapshots or row.get("strictly_certified_output") is not None or row["certified_exact"] is not None:
            raise ValueError("Uncertified diagnostic path has a certified output")
        if row["status"] == "completed" and row["online"] != 2048:
            raise ValueError("Completed abstaining diagnostic must reach public cap")
        return
    if len(certified_snapshots) != 1 or not snapshots or certified_snapshots[0] is not snapshots[-1]:
        raise ValueError("Certified stop must have exactly one terminal gate crossing")
    terminal, certificate = snapshots[-1], snapshots[-1]["strict_certificate"]
    output = row.get("strictly_certified_output")
    if (terminal["online"] != row["online"] or type(row["certified_exact"]) is not bool
            or certificate.get("status") != "certified" or certificate.get("decision") != "stop"
            or certificate.get("interval_certified") is not True
            or output != terminal.get("strictly_certified_output") or output != terminal.get("guess")
            or output != certificate.get("candidate_theta") or output != certificate.get("theta")
            or not isinstance(output, list) or len(output) != 4 or any(type(v) is not int or v not in (0, 1) for v in output)):
        raise ValueError("Certified output, terminal candidate and gate receipt disagree")
    try:
        lower, upper = Decimal(certificate["gap_lower"]), Decimal(certificate["beta_upper"])
        if not lower.is_finite() or not upper.is_finite() or lower <= upper:
            raise ValueError("Certified endpoint is not strictly above threshold")
    except (InvalidOperation, TypeError, KeyError) as exc:
        raise ValueError("Invalid certified interval endpoints") from exc
    if not row.get("gate_history") or row["gate_history"][-1] != {"online": row["online"], **certificate}:
        raise ValueError("Terminal certificate differs from retained gate history")


def analyze_records(cfg, data_manifest, offline_records, path_records, receipts, offline_summaries=None):
    """Pure aggregation API; missing outcomes remain unknown, never dropped."""
    data_plan, eval_plan = world_plan(cfg), evaluation_world_plan(cfg)
    test_worlds = {split: sorted(r["world_id"] for r in data_plan if r["split"] == split) for split in TEST_SPLITS}
    eval_worlds = {split: sorted(r["world_id"] for r in eval_plan if r["split"] == split) for split in EVAL_SPLITS}
    diagnostic_worlds = [next(r["world_id"] for r in eval_plan if r["split"] == split) for split in EVAL_SPLITS]
    offline_expected = {(method, world, position) for method in OFFLINE_METHODS for worlds in test_worlds.values() for world in worlds for position in POSITIONS}
    world_split = {world: split for split, worlds in test_worlds.items() for world in worlds}

    def offline_key(row):
        identifier = row.get("row_id", "")
        if not identifier.startswith(str(row.get("world_id")) + ":"):
            raise ValueError("Offline state identifier is not world-bound")
        position = int(identifier.rsplit(":", 1)[1])
        if row.get("split") != world_split.get(row.get("world_id")) or row["state"]["online"] != 8 + 128 * position:
            raise ValueError("Offline split or prespecified predecision position differs")
        return row["method"], row["world_id"], position

    offline, offline_coverage = _index_unique(offline_records, offline_key, offline_expected, "offline")
    expected_paths = {(method, world, "fixed_budget") for method in METHODS for worlds in eval_worlds.values() for world in worlds}
    expected_paths |= {(method, world, "fixed_confidence_diagnostic") for method in METHODS for world in diagnostic_worlds}
    paths, path_coverage = _index_unique(path_records, lambda r: (r["method"], r["world_id"], r["mode"]), expected_paths, "paths")
    eval_split = {r["world_id"]: r["split"] for r in eval_plan}
    for row in path_records:
        _validate_terminal(row)
        diagnostic = row["mode"] == "fixed_confidence_diagnostic"
        if row["split"] != eval_split[row["world_id"]] or row["R"] != (16 if diagnostic else 64) or row["public_online_cap"] != 2048:
            raise ValueError("Path stratum/risk/public-limit contract changed")
        checkpoints = [s["online"] for s in row["snapshots"]]
        if len(checkpoints) != len(set(checkpoints)):
            raise ValueError("Duplicate evaluation readouts")
        if not diagnostic and any(t not in (256, 512) for t in checkpoints):
            raise ValueError("Unexpected primary readout")
        for snapshot in row["snapshots"]:
            if snapshot["costs"]["task"] + snapshot["costs"]["type"] != snapshot["online"] or snapshot["total_acquisition"] != sum(snapshot["costs"].values()):
                raise ValueError("Snapshot acquisition accounting differs")
        if row["costs"]["task"] + row["costs"]["type"] != row["online"] or row["total_acquisition"] != sum(row["costs"].values()):
            raise ValueError("Path acquisition accounting differs")
    requested_worlds = {r["world_id"] for r in data_plan}
    declared_data = {r["world_id"]: r for r in data_plan}
    manifest_worlds = data_manifest.get("worlds", [])
    declared_splits = Counter(r["split"] for r in data_plan)
    data_ok = (data_manifest.get("status") == "completed" and len(manifest_worlds) == 96
               and {r["world_id"] for r in manifest_worlds} == requested_worlds
               and all(r["row_count"] == 16 for r in manifest_worlds)
               and all(r["split"] == declared_data[r["world_id"]]["split"] for r in manifest_worlds)
               and set(data_manifest.get("splits", {})) == set(declared_splits)
               and all(data_manifest["splits"][split].get("states") == count * 16
                       and data_manifest["splits"][split].get("worlds") == count
                       for split, count in declared_splits.items()))
    receipt_ok = all(receipts.get(name, {}).get("status") == "completed" for name in ("training", "mlp", "evaluation"))
    missing_readouts = []
    for method in METHODS:
        for worlds in eval_worlds.values():
            for world in worlds:
                row = paths.get((method, world, "fixed_budget"))
                times = {s["online"] for s in row["snapshots"]} if row else set()
                missing_readouts.extend({"method": method, "world_id": world, "budget": budget} for budget in (256, 512) if budget not in times)
    failed_paths = [{"method": r["method"], "world_id": r["world_id"], "mode": r["mode"], "error": r.get("error")}
                    for r in path_records if r["status"] != "completed"]
    summary_checks = []
    if offline_summaries is not None:
        for summary in offline_summaries:
            actual = [r for r in offline_records if r["method"] == summary["method"]]
            if summary["method"] not in OFFLINE_METHODS or summary["states"] != 120 or summary["recorded_states"] != len(actual):
                raise ValueError("Offline summary receipt does not match requested/raw records")
            summary_checks.append(summary["method"])
        if len(set(summary_checks)) != len(summary_checks):
            raise ValueError("Duplicate offline summary receipt")
    summaries_ok = set(summary_checks) == set(OFFLINE_METHODS)
    aggregate_costs = computational_costs(data_manifest, offline_records, path_records, receipts, eval_plan, diagnostic_worlds)
    qwen_accounted = (aggregate_costs["charged_qwen_calls"] is not None and
                      0 <= aggregate_costs["charged_qwen_calls"] <= 600 and aggregate_costs["charged_unrecorded_qwen_calls"] == 0)
    all_complete = data_ok and receipt_ok and summaries_ok and qwen_accounted and not offline_coverage["missing"] and not path_coverage["missing"] and not missing_readouts and not failed_paths
    coverage = {"status": "COMPLETE" if all_complete else "INCOMPLETE", "data_manifest_complete": data_ok,
                "receipts_completed": receipt_ok, "offline": offline_coverage, "paths": path_coverage,
                "missing_primary_readouts": missing_readouts, "failed_paths": failed_paths,
                "offline_summary_methods": summary_checks, "independent_data_test_worlds": 24,
                "offline_summary_receipts_complete": summaries_ok,
                "qwen_calls_fully_accounted_within_600": qwen_accounted,
                "independent_closed_loop_worlds": 24, "reused_diagnostic_worlds": 3,
                "primary_readouts_requested": 336, "diagnostic_paths_requested": 21}

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    offline_world_rows, offline_summary, offline_pairs = [], [], []
    for split, worlds in _groups_with_pool(test_worlds):
        draws = _world_draws(rng, split, len(worlds))
        values = {}
        for method in OFFLINE_METHODS:
            world_rows = []
            for world in worlds:
                rows = [offline[(method, world, position)] for position in POSITIONS if (method, world, position) in offline]
                metrics = {key: _mean_record([r.get(key) for r in rows], 5) for key in OFFLINE_METRICS}
                item = {"method": method, "split": split, "world_id": world, "requested_states": 5,
                        "observed_states": len(rows), "missing_states": 5 - len(rows),
                        "invalid_fallbacks": sum(r["fallback"] for r in rows), "metrics": metrics}
                if split != "all_24_worlds":
                    offline_world_rows.append(item)
                world_rows.append(item)
                for key in OFFLINE_METRICS:
                    values.setdefault((method, key), {})[world] = metrics[key]["mean"]
            offline_summary.append({"method": method, "split": split, "requested_worlds": len(worlds),
                                    "requested_states": 5 * len(worlds), "observed_states": sum(r["observed_states"] for r in world_rows),
                                    "invalid_fallbacks": sum(r["invalid_fallbacks"] for r in world_rows),
                                    "metrics": {key: _mean_record([values[(method, key)][world] for world in worlds], len(worlds)) for key in OFFLINE_METRICS},
                                    "unit": "within-world mean of five declared states; then equal independent-world weight"})
        for left, right in LOSS_PAIRS:
            for metric in ("allocation_l1", "forward_kl_epsilon_1e8", "plugin_relative_information_deficit", "inference_wall_seconds"):
                offline_pairs.append({"split": split, "left": left, "right": right, "metric": metric,
                                      "direction": "left minus right; positive favors lower loss/cost of right",
                                      **_paired(values[(left, metric)], values[(right, metric)], worlds, draws)})

    primary_summary, primary_pairs = [], []
    for split, worlds in _groups_with_pool(eval_worlds):
        draws = _world_draws(rng, split, len(worlds))
        outcomes = {}
        for method in METHODS:
            rows = [paths[(method, world, "fixed_budget")] for world in worlds if (method, world, "fixed_budget") in paths]
            for budget in (256, 512):
                snapshots = {world: next((s for s in paths[(method, world, "fixed_budget")]["snapshots"] if s["online"] == budget), None)
                             if (method, world, "fixed_budget") in paths else None for world in worlds}
                observed = [s for s in snapshots.values() if s is not None]
                outcomes[(method, budget)] = {world: None if snapshot is None else int(snapshot["guess_exact"]) for world, snapshot in snapshots.items()}
                correct = sum(s["guess_exact"] for s in observed)
                missing = len(worlds) - len(observed)
                costs = {key: sum(s["costs"][key] for s in observed) for key in ("task", "type", "offline")}
                primary_summary.append({"split": split, "method": method, "budget": budget, "requested_worlds": len(worlds),
                                        "recorded_paths": len(rows), "failed_paths": sum(r["status"] != "completed" for r in rows),
                                        "observed_readouts": len(observed), "missing_readouts": missing, "exact_recovered": correct,
                                        "exact_recovery": correct / len(worlds) if not missing else None,
                                        "recovery_identification_bounds": [correct / len(worlds), (correct + missing) / len(worlds)],
                                        "costs_observed_sum": costs,
                                        "total_acquisition": _mean_record([s["total_acquisition"] for s in observed], len(worlds)),
                                        "invalid_fallbacks": sum(s["invalid_fallbacks"] for s in observed),
                                        "inference_calls_observed": sum(sum(p["online"] < budget for p in r["predictions"]) for r in rows),
                                        **{key: _mean_record([s.get(key) for s in observed], len(worlds)) for key in
                                           ("inference_wall_seconds", "inference_cpu_seconds", "elapsed_wall_seconds", "elapsed_cpu_seconds", "prompt_tokens", "output_tokens")},
                                        "scope": "uncertified fixed-budget guesses under public cap2048"})
        for budget in (256, 512):
            for left, right in RECOVERY_PAIRS:
                primary_pairs.append({"split": split, "budget": budget, "left": left, "right": right,
                                      "direction": "left minus right exact-recovery proportion",
                                      **_paired(outcomes[(left, budget)], outcomes[(right, budget)], worlds, draws)})

    diagnostic_summary = []
    for method in METHODS:
        rows = [paths[(method, world, "fixed_confidence_diagnostic")] for world in diagnostic_worlds if (method, world, "fixed_confidence_diagnostic") in paths]
        diagnostic_summary.append({"method": method, "requested_reused_worlds": 3, "recorded_paths": len(rows),
                                   "missing_paths": 3 - len(rows), "failed_paths": sum(r["status"] != "completed" for r in rows),
                                   "certified_outputs": sum(r["complete"] for r in rows),
                                   "wrong_certified_outputs": sum(r["complete"] and r["certified_exact"] is False for r in rows),
                                   "cap_abstentions": sum(r["abstained"] and r["status"] == "completed" and r["online"] == 2048 for r in rows),
                                   "all_abstentions_including_failures": sum(r["abstained"] for r in rows),
                                   "online_cost": _mean_record([r["online"] for r in rows], 3),
                                   "total_acquisition": _mean_record([r["total_acquisition"] for r in rows], 3),
                                   "costs_observed_sum": {key: sum(r["costs"][key] for r in rows) for key in ("task", "type", "offline")},
                                   **{key: _mean_record([r.get(key) for r in rows], 3) for key in
                                      ("wall_seconds", "cpu_seconds", "inference_wall_seconds", "gate_wall_seconds", "prompt_tokens", "output_tokens")},
                                   "scope": "R16 three reused worlds; no independent effectiveness or tiny-risk validation"})

    return {"coverage": coverage, "offline_worlds": offline_world_rows, "offline_summary": offline_summary,
            "offline_paired": offline_pairs, "primary_summary": primary_summary, "primary_paired": primary_pairs,
            "diagnostic_summary": diagnostic_summary, "computational_costs": aggregate_costs,
            "analysis_protocol": {"bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                                  "unit": "independent world; five correlated offline states averaged first",
                                  "interval_scope": "descriptive paired-world resampling sensitivity on fixed heterogeneous condition grids; not calibrated population confidence intervals",
                                  "pooled_scope": "all_24_worlds reuses the same worlds; resamples eight within each declared stratum, no additional independent units",
                                  "percent_targets": "saved teacher_percent labels; never regenerated from serialized float weights; numerical largest-remainder ties retain generation convention",
                                  "confirmation": False, "missing_outcomes": "unknown, with requested denominators retained"}}


def computational_costs(manifest, offline, paths, receipts, eval_plan, diagnostic_ids):
    training, mlp, evaluation = (receipts.get(name, {}) for name in ("training", "mlp", "evaluation"))
    method_totals = []
    for method in METHODS:
        o, p = [r for r in offline if r["method"] == method], [r for r in paths if r["method"] == method]
        calls = len(o) + sum(r["inference_calls"] for r in p)
        latencies = [r["inference_wall_seconds"] for r in o] + [r["inference_wall_seconds"] for path in p for r in path["predictions"]]
        method_totals.append({"method": method, "recorded_offline_calls": len(o), "recorded_path_calls": sum(r["inference_calls"] for r in p),
                              "recorded_calls": calls, "invalid_fallbacks": sum(r["fallback"] for r in o) + sum(r["invalid_fallbacks"] for r in p),
                              "inference_wall_seconds": sum(r["inference_wall_seconds"] for r in o + p),
                              "inference_cpu_seconds": sum(r["inference_cpu_seconds"] for r in o + p),
                              "prompt_tokens": sum(r["prompt_tokens"] for r in o + p), "output_tokens": sum(r["output_tokens"] for r in o + p),
                              "path_wall_seconds": sum(r["wall_seconds"] for r in p), "path_cpu_seconds": sum(r["cpu_seconds"] for r in p),
                              "call_latency_observed": len(latencies),
                              "call_latency_median_seconds": float(np.median(latencies)) if latencies else None,
                              "call_latency_p95_seconds": float(np.quantile(latencies, .95)) if latencies else None,
                              **{key: sum(r.get(key, 0.) for r in p) for key in
                                 ("glr_wall_seconds", "glr_cpu_seconds", "gate_wall_seconds", "gate_cpu_seconds")},
                              "costs_observed_sum": {key: sum(r["costs"][key] for r in p) for key in ("task", "type", "offline")}})
    recorded_qwen = sum(r["recorded_calls"] for r in method_totals if r["method"] in QWEN_METHODS)
    charged_qwen = evaluation.get("policy_calls", {}).get("calls")
    if charged_qwen is not None and charged_qwen < recorded_qwen:
        raise ValueError("Recorded Qwen calls exceed charged inference budget")
    stages = {"data_generation": manifest.get("wall_seconds"), "qwen_sft_including_load_validation_save": training.get("wall_seconds"),
              "mlp_training": mlp.get("training_wall_seconds"), "evaluation_including_shared_load": evaluation.get("wall_seconds")}
    stages_complete = all(value is not None for value in stages.values())
    return {"stages_wall_seconds": stages, "sum_stage_wall_seconds": sum(stages.values()) if stages_complete else None,
            "sum_scope": "recorded stage work, not elapsed pipeline time if stages overlap; loads are already included",
            "qwen_training_load_seconds_included": training.get("load_seconds"),
            "evaluation_shared_resident_load_seconds_included": evaluation.get("resident_model", {}).get("load_seconds"),
            "evaluation_load_scope": "one resident base+adapter shared by BaseQwen/LoRA; no duplicate cold-load attribution",
            "qwen_training_cpu_seconds": training.get("process_cpu_seconds"), "mlp_training_cpu_seconds": mlp.get("training_cpu_seconds"),
            "evaluation_cpu_seconds": evaluation.get("process_cpu_seconds"), "qwen_optimizer_steps": training.get("optimizer_steps"),
            "mlp_optimizer_updates": mlp.get("optimizer_updates"), "qwen_train_target_tokens": training.get("train_target_tokens"),
            "qwen_validation_tokens": training.get("validation_tokens"), "qwen_training_peak_allocated_bytes": training.get("peak_allocated_bytes"),
            "qwen_evaluation_peak_allocated_bytes": evaluation.get("peak_allocated_bytes"), "gpu_kernel_seconds": None,
            "gpu_timing_scope": "synchronized inference wall and peak memory are recorded; no dedicated GPU-kernel-time meter",
            "data_generated_online_actions": manifest.get("generated_online_actions"),
            "data_unique_offline_observations": manifest.get("unique_generated_offline_observations"),
            "primary_planned_unique_reference_observations": sum(2*r["M"] for r in eval_plan),
            "primary_recorded_world_unique_reference_observations": sum(2*r["M"] for r in eval_plan
                if any(p["world_id"] == r["world_id"] and p["mode"] == "fixed_budget" for p in paths)),
            "diagnostic_extra_unique_reference_observations": 0,
            "diagnostic_scope": "same existing three worlds and M; per-policy reference charging is retained separately",
            "charged_qwen_calls": charged_qwen, "recorded_qwen_calls": recorded_qwen,
            "charged_unrecorded_qwen_calls": None if charged_qwen is None else charged_qwen - recorded_qwen,
            "methods": method_totals, "end_to_end_receipts_available": stages_complete
            and training.get("load_seconds") is not None and evaluation.get("resident_model", {}).get("load_seconds") is not None,
            "efficiency_claim": "not inferred from warm inference latency alone"}


def _fmt(value, digits=4):
    return "NA" if value is None else f"{value:.{digits}f}"


def write_reports(result, root):
    root = Path(root)
    cov, costs = result["coverage"], result["computational_costs"]
    if cov["status"] != "COMPLETE":
        lines = ["# T1 evaluation — incomplete coverage", "",
                 "完整评测尚未成立。保留全部计划分母、已有失败和缺失路径；不生成完整比较图，不把未执行的 Qwen 路径补成模型结果。", "",
                 f"离线预测：{cov['offline']['recorded']}/{cov['offline']['requested']}；路径：{cov['paths']['recorded']}/{cov['paths']['requested']}；缺失主读数：{len(cov['missing_primary_readouts'])}/336；失败路径：{len(cov['failed_paths'])}。", "",
                 "详细缺失名单、已有观测统计和费用记录见 artifacts/analysis/coverage.json 与 computational_costs.json。未知结果不按零准确率、零成本或已完成样本替代。"]
        (root / "QUERY_POLICY_EVALUATION.md").write_text("\n".join(lines) + "\n")
        (root / "COMPUTATIONAL_COST.md").write_text("# T1 computational cost — incomplete\n\n费用记录尚不完整，不能据此主张端到端效率。已有成本和未记录调用差额保留于 artifacts/analysis/computational_costs.json。\n")
        return
    lines = ["# T1 query-policy evaluation", "",
             "本轮是受控 iid 通道内的开发评测，独立单位为完整世界。离线使用 24 个数据测试世界，每世界五个预定状态；闭环使用另 24 个世界，每分层八个。所有声明的模型结果已记录。", "",
             "离线先在每个世界内平均五个状态，再等权汇总。L1 和 forward KL 衡量模仿误差；信息缺口是由可观测估计量计算的浮点代理，不是隐藏真参数信息或停止证书。负缺口保留。Qwen 使用整数百分比分配，MLP 使用连续权重；量化误差单独保留。", "",
             "百分比指标沿用数据生成时保存的 teacher_percent 标签，不从已序列化浮点权重重新生成；最大余数法在数值相同余数处保留生成时的顺序约定。", "",
             "|分层|方法|状态/计划|无效回退/计划|L1|Forward KL|信息缺口|每次调用墙钟秒|",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in result["offline_summary"]:
        metrics = row["metrics"]
        lines.append(f"|{row['split']}|{row['method']}|{row['observed_states']}/{row['requested_states']}|{row['invalid_fallbacks']}/{row['requested_states']}|{_fmt(metrics['allocation_l1']['mean'])}|{_fmt(metrics['forward_kl_epsilon_1e8']['mean'])}|{_fmt(metrics['plugin_relative_information_deficit']['mean'])}|{_fmt(metrics['inference_wall_seconds']['mean'])}|")
    lines += ["", "配对改进为左方法减右方法的世界平均损失，正值支持右方法的较低损失。所有区间使用 4,000 次世界配对重采样，固定分析种子 731032；每分层 n=8，未经多重校正。八个世界来自固定且异质的条件组合，因此区间只表示描述性重采样敏感性，不是经过校准的总体置信区间。", "",
              "all_24_worlds 汇总复用同一批世界，不增加样本；其重采样在每个分层内各抽八个世界，保持三层等额。", "",
              "|分层|左−右|指标|均值差|描述性95%重采样范围|", "|---|---|---|---:|---|"]
    for row in result["offline_paired"]:
        if row["metric"] == "inference_wall_seconds":
            continue
        interval = row["bootstrap_95"]
        lines.append(f"|{row['split']}|{row['left']}−{row['right']}|{row['metric']}|{_fmt(row['mean_difference'])}|{interval}|")
    lines += ["", "闭环在公开上限 2048 下读取查询数 256/512 的完整向量恢复。256/512 是 evaluator 的中间读数，未作为更早截止时间输入策略。该表为固定预算猜测准确率，并非认证输出。原始 Aligned 保留其原生更新节奏，其余六策略统一为初始八次强制观察后每 128 步更新。", "",
              "|分层|方法|预算|完整恢复/全部|任务合计|类型合计|离线合计|平均总获取|回退/已记录调用|",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in result["primary_summary"]:
        c = row["costs_observed_sum"]
        lines.append(f"|{row['split']}|{row['method']}|{row['budget']}|{row['exact_recovered']}/{row['requested_worlds']}|{c['task']}|{c['type']}|{c['offline']}|{_fmt(row['total_acquisition']['mean'], 1)}|{row['invalid_fallbacks']}/{row['inference_calls_observed']}|")
    lines += ["", "闭环配对差及每世界向量保留于 primary_paired.json；方向为左减右的完整恢复率，统计单位仍为世界。Native 与 Block128 的差异包含更新节奏，不能归因于模型蒸馏。单组、零参考情形的 D-Type 公共结构判断可能使两个 D 基线构造性相同。", "",
              "R16 的固定置信度诊断复用三个已声明闭环世界，未增加独立样本。只在独立严格门给出区间认证时停止；上限时弃权及评分猜测分开。此处 n=3，不能验证极小风险、渐近最优性或普遍终止。", "",
              "|方法|认证/全部|错误认证/全部|上限弃权/全部|失败|平均在线成本|平均认证门墙钟秒|",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for row in result["diagnostic_summary"]:
        lines.append(f"|{row['method']}|{row['certified_outputs']}/3|{row['wrong_certified_outputs']}/3|{row['cap_abstentions']}/3|{row['failed_paths']}|{_fmt(row['online_cost']['mean'], 1)}|{_fmt(row['gate_wall_seconds']['mean'])}|")
    lines += ["", "训练外参数 (.85,.60) 位于 T1 训练参数范围内，是留出组合而非范围外推；该参数在既往研究出现过。结果限于合成通道，不能外推为自然语言、真实用户或 Web 查询能力。没有根据测试结果选择 checkpoint、提示词或更有利的分层。", "",
              "图为 artifacts/analysis/accuracy_vs_budget.{png,pdf} 与 offline_quality_vs_inference_cost.{png,pdf}。推理延迟图仅显示已加载模型的调用成本；端到端数据生成、训练、加载及评测成本见 COMPUTATIONAL_COST.md。"]
    (root / "QUERY_POLICY_EVALUATION.md").write_text("\n".join(lines) + "\n")
    lines = ["# T1 computational cost", "",
             "以下成本保留数据生成、训练、加载和推理范围。模型调用延迟不能单独证明端到端效率；冷加载、训练摊销及调用频率均影响实际使用。", "",
             "|阶段|已记录墙钟秒|", "|---|---:|"]
    for name, value in costs["stages_wall_seconds"].items():
        lines.append(f"|{name}|{_fmt(value, 2)}|")
    lines += ["", f"阶段墙钟求和为 {_fmt(costs['sum_stage_wall_seconds'], 2)} 秒；若阶段重叠，它是记录工作量之和而非实际起止间隔。SFT 加载 {_fmt(costs['qwen_training_load_seconds_included'], 2)} 秒、评测共享模型加载 {_fmt(costs['evaluation_shared_resident_load_seconds_included'], 2)} 秒均已包含在对应阶段中，不再叠加。Base 与 LoRA 共用一次 resident 模型加载，不能分别重复收费。", "",
              f"数据生成在线动作 {costs['data_generated_online_actions']}，唯一离线观测 {costs['data_unique_offline_observations']}。闭环 24 世界唯一参考观测 {costs['primary_recorded_world_unique_reference_observations']}，三世界诊断复用原观察流，不增加唯一参考样本；下表仍保留每条策略路径的离线计费。", "",
              "|方法|离线预测调用|闭环及诊断调用|无效回退|推理墙钟秒|推理CPU秒|Prompt tokens|Output tokens|任务查询|类型查询|离线计费|",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in costs["methods"]:
        c = row["costs_observed_sum"]
        lines.append(f"|{row['method']}|{row['recorded_offline_calls']}|{row['recorded_path_calls']}|{row['invalid_fallbacks']}|{_fmt(row['inference_wall_seconds'], 2)}|{_fmt(row['inference_cpu_seconds'], 2)}|{row['prompt_tokens']}|{row['output_tokens']}|{c['task']}|{c['type']}|{c['offline']}|")
    lines += ["", f"Qwen 预算计费调用 {costs['charged_qwen_calls']}，完整预测/路径记录调用 {costs['recorded_qwen_calls']}，计费但未记录差额 {costs['charged_unrecorded_qwen_calls']}。SFT optimizer steps={costs['qwen_optimizer_steps']}，MLP updates={costs['mlp_optimizer_updates']}。", "",
              f"Qwen 训练峰值 allocated bytes={costs['qwen_training_peak_allocated_bytes']}；评测峰值={costs['qwen_evaluation_peak_allocated_bytes']}。没有独立 GPU kernel 时间计量；同步推理墙钟、进程 CPU 和峰值显存不能互相替代。", "",
              "离线质量每个方法每世界五次预测；闭环按真实调用次数记账。查询预算 256 和 512 的记录为同一路径的累计前缀，费用合计仅计算路径最终值，未重复相加两次。模型推理墙钟包含接口及观测输入处理；GLR/认证门和环境开销另保留在路径墙钟。", "",
              "调用延迟中位数/P95、GLR 与认证门的墙钟/CPU 合计在 computational_costs.json；分析本身的墙钟、CPU、Python/NumPy/Matplotlib 版本单独记于 artifacts/analysis/execution.json。分析使用 CPU 绘图库环境，其运行时间不混入模型推理。", "",
              f"端到端必要阶段及加载记录齐备：{costs['end_to_end_receipts_available']}。这只是成本可审计性，不自动构成 LLM 相对 MLP 或 CPU 教师的效率优势。"]
    (root / "COMPUTATIONAL_COST.md").write_text("\n".join(lines) + "\n")


def plots(result, out):
    if result["coverage"]["status"] != "COMPLETE":
        return []
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = dict(zip(METHODS, ("#444444", "#a53030", "#c68a20", "#398140", "#7b4eab", "#8888aa", "#247eb2")))
    out = Path(out)
    names = []

    def save(fig, name):
        fig.tight_layout(rect=(0, 0, 1, .92))
        for extension in ("png", "pdf"):
            path = out / (name + "." + extension)
            fig.savefig(path, dpi=180)
            names.append(path.name)
        plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, split in zip(axes, EVAL_SPLITS):
        for method in METHODS:
            rows = sorted((r for r in result["primary_summary"] if r["split"] == split and r["method"] == method), key=lambda r: r["budget"])
            ax.plot([r["budget"] for r in rows], [r["exact_recovery"] for r in rows], "o-", label=method, color=colors[method], markersize=4)
        ax.set(title=split.removeprefix("eval_"), xlabel="Intermediate query-budget readout", ylabel="Exact recovery / 8 worlds", ylim=(-.03, 1.03), xticks=(256, 512))
        ax.grid(alpha=.15)
    axes[0].legend(fontsize=6)
    fig.suptitle("T1 development: 8 independent worlds/stratum; fixed-budget guesses are not certified", fontsize=10)
    save(fig, "accuracy_vs_budget")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    markers = dict(zip(TEST_SPLITS, ("o", "s", "^")))
    for row in result["offline_summary"]:
        if row["split"] == "all_24_worlds":
            continue
        x = row["metrics"]["inference_wall_seconds"]["mean"]
        for ax, metric, label in zip(axes, ("allocation_l1", "plugin_relative_information_deficit"), ("Allocation L1", "Observable plug-in information deficit")):
            y = row["metrics"][metric]["mean"]
            if x is not None and x > 0 and y is not None:
                ax.scatter(x, y, c=colors[row["method"]], marker=markers[row["split"]], label=row["method"] + "/" + row["split"], s=40)
            ax.set(xlabel="Loaded-model inference wall seconds / state (log)", ylabel=label)
            ax.set_xscale("log")
            ax.grid(alpha=.15)
    axes[0].legend(fontsize=6)
    fig.suptitle("Five states averaged per world, then 8 worlds/stratum; warm-call cost excludes training/loading", fontsize=9)
    save(fig, "offline_quality_vs_inference_cost")
    return names


def _read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []


def main():
    started, cpu_started = perf_counter(), process_time()
    from .freeze import verify
    verify("training_freeze.json")
    verify("analysis_freeze.json")
    cfg = json.loads((ROOT / "config.json").read_text())
    artifact = ROOT / "artifacts"
    output = artifact / "analysis"
    if output.exists():
        raise FileExistsError("Analysis output exists; no silent overwrite")
    receipts = {"training": _read_json(artifact / "training/execution.json", {}),
                "mlp": _read_json(artifact / "mlp/mlp_training.json", {}),
                "evaluation": _read_json(artifact / "evaluation/execution.json", {})}
    output.mkdir(parents=True)
    try:
        result = analyze_records(cfg, _read_json(artifact / "data/manifest.json", {}),
                                 _read_jsonl(artifact / "evaluation/offline_predictions.jsonl"),
                                 _read_jsonl(artifact / "evaluation/paths.jsonl"), receipts,
                                 _read_json(artifact / "evaluation/offline_summary.json", None))
        for name, value in result.items():
            (output / (name + ".json")).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
        write_reports(result, ROOT)
        artifacts = plots(result, output)
        (output / "execution.json").write_text(json.dumps({"status": result["coverage"]["status"], "plots": artifacts,
                                                          "model_calls": 0, "simulation_worlds": 0,
                                                          "wall_seconds": perf_counter() - started,
                                                          "cpu_seconds": process_time() - cpu_started,
                                                          "python": platform.python_version(), "executable": sys.executable,
                                                          "numpy": np.__version__,
                                                          "matplotlib": getattr(sys.modules.get("matplotlib"), "__version__", None)}, indent=2) + "\n")
        print(json.dumps(result["coverage"], indent=2))
    except Exception as exc:
        failure = {"status": "FAILED_COVERAGE_OR_SCHEMA_AUDIT", "error": type(exc).__name__ + ": " + str(exc),
                   "model_calls": 0, "simulation_worlds": 0}
        (output / "execution.json").write_text(json.dumps(failure, indent=2) + "\n")
        (ROOT / "QUERY_POLICY_EVALUATION.md").write_text("# T1 evaluation — audit failed\n\n原始记录未通过覆盖或模式审计，未生成有效的完整结果比较。详见 artifacts/analysis/execution.json；保留原始记录，不删除失败。\n")
        (ROOT / "COMPUTATIONAL_COST.md").write_text("# T1 cost — audit failed\n\n记录审计未完成，不能提出完整成本或效率结论。\n")
        raise


if __name__ == "__main__":
    main()
