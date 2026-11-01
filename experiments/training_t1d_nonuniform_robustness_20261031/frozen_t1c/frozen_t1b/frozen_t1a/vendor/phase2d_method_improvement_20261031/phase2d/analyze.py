"""Frozen, evaluator-only paired analysis; no private seeds or world creation."""
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .bootstrap import ROOT
from .runner import jobs
from .policy import POLICIES
from phase2b.analyze import load, cell, identity, confidence_at
from phase2a.coefficients import solve_allocation, oracle_coefficient


CONTRASTS = {
    "task_without_type": {"D-RRC-NoType": 1, "Aligned-NoType": -1},
    "remaining_type_enabled_advantage": {"D-RRC-Type": 1, "Aligned-Full": -1},
    "kl_type_benefit": {"Aligned-NoType": 1, "Aligned-Full": -1},
    "simple_type_benefit": {"D-RRC-NoType": 1, "D-RRC-Type": -1},
    "interaction": {"Aligned-NoType": 1, "Aligned-Full": -1, "D-RRC-NoType": -1, "D-RRC-Type": 1},
}
TIME_KEYS = ("trajectory_wall_seconds", "trajectory_cpu_seconds", "planner_seconds",
             "planner_cpu_seconds", "glr_seconds", "glr_cpu_seconds")
ERROR_KEYS = ("theta_errors", "type_errors", "p_error", "q_error")


def coverage(rows, cfg):
    plan = jobs(cfg)
    expected = {(policy, job["index"]): job for job in plan for policy in POLICIES}
    observed = Counter(map(identity, rows))
    metadata_errors = []
    for row in rows:
        job = expected.get(identity(row))
        if job is not None:
            for key in ("partition", "alpha", "R", "M", "online_cap", "p", "q", "eta", "s", "stop_mode"):
                if row.get(key) != job[key]:
                    metadata_errors.append({"identity": list(identity(row)), "field": key})
    return {"planned_worlds": len(plan), "planned_trajectories": len(expected), "observed_rows": len(rows),
            "missing": [list(key) for key in sorted(expected.keys() - observed.keys())],
            "unexpected": [list(key) for key in sorted(observed.keys() - expected.keys())],
            "duplicates": [{"identity": list(key), "count": count} for key, count in observed.items() if count != 1],
            "metadata_errors": metadata_errors,
            "exact": observed == Counter(expected.keys()) and not metadata_errors}


def validate_coverage(rows, cfg):
    result = coverage(rows, cfg)
    if not result["exact"]:
        raise ValueError("Expected complete exact world/policy coverage; missing, duplicate, unexpected, or mismatched records")
    return result


def references(cfg):
    """Post-run true-parameter numerical coefficients; never learner inputs."""
    output = []
    for part in cfg["partitions"]:
        for alpha in cfg["alphas"]:
            no_type = solve_allocation(part, cfg["p"], cfg["q"], alpha, None, cfg["eta"])
            with_type = solve_allocation(part, cfg["p"], cfg["q"], alpha, cfg["type_accuracy"], cfg["eta"])
            oracle = oracle_coefficient(sum(part), cfg["p"], cfg["q"], alpha, cfg["eta"])
            output.append({"partition": part, "alpha": alpha, "K_no_type": no_type["K"],
                           "K_with_type": with_type["K"], "K_oracle": oracle["K"],
                           "premium_regime": "zero" if with_type["K"] / oracle["K"] - 1 < 1e-6 else "positive",
                           "no_type_allocation": no_type, "with_type_allocation": with_type,
                           "scope": "evaluator-only config-based float64 population reference, not a stopping-time certificate"})
    return output


def contrast_vectors(by_policy, indices, scale):
    """The same independent world index orders every policy/contrast vector."""
    return {name: np.asarray([sum(weight * by_policy[policy][i]["online"] / scale
                                  for policy, weight in coefficients.items()) for i in indices])
            for name, coefficients in CONTRASTS.items()}


def bootstrap_interval(values, resample_indices):
    draws = np.asarray(values, dtype=float)[resample_indices].mean(axis=1)
    return np.quantile(draws, [.025, .975]).tolist()


def diagnose(row, reference):
    history = row["estimation_history"]
    last = history[-1] if history else None
    no_type = row["policy"].endswith("NoType")
    coefficient = reference["K_no_type" if no_type else "K_with_type"]
    result = {"partition": row["partition"], "alpha": row["alpha"], "R": row["R"],
              "policy": row["policy"], "index": row["index"], "complete": row["complete"],
              "censored": row["censored"], "online": row["online"], "online_over_R": row["online"] / row["R"],
              "reference_K": coefficient, "restricted_online_over_KR": row["online"] / row["R"] / coefficient,
              "forced_fraction": row["forced_tasks"] / row["online"], "updates": len(history),
              "estimates_available": bool(history), "final_beta_over_R": row["fit"]["beta"] / row["R"],
              "history_errors": [{"online": entry["online"], **{key: entry[key] for key in ERROR_KEYS}} for entry in history],
              "scope": "audited evaluator errors only; correlated diagnostics are not additive causal shares"}
    for key in ERROR_KEYS:
        result["last_" + key] = None if last is None else last[key]
        result["history_mean_" + key] = None if not history else float(np.mean([entry[key] for entry in history]))
    for key in ("p_error", "q_error"):
        result["history_mean_abs_" + key] = None if not history else float(np.mean([abs(entry[key]) for entry in history]))
    for key in ("theta_errors", "type_errors"):
        result["updates_with_" + key] = sum(entry[key] > 0 for entry in history)
    discrepancy = np.asarray(row["tracking_diagnostics"]["actual_minus_target"], dtype=float)
    result["tracking_l1_over_t"] = float(abs(discrepancy).sum() / row["online"])
    return result


def analyze_rows(rows, cfg, receipt, refs):
    cov = validate_coverage(rows, cfg)
    if receipt["status"] != "completed":
        raise ValueError("Incomplete execution: retain partial records, do not publish a complete comparison")
    groups = defaultdict(list)
    for row in rows:
        if row["complete"] == row["censored"] or not 0 < row["online"] <= row["online_cap"]:
            raise ValueError("Invalid terminal completion/censoring record")
        if row["censored"] and row["online"] != row["online_cap"]:
            raise ValueError("Infrastructure truncation is not ordinary cap censoring")
        if row["online"] != row["costs"]["task"] + row["costs"]["type"]:
            raise ValueError("Online action accounting mismatch")
        if row["costs"]["offline"] != 2 * row["M"] or row["total_acquisition"] != sum(row["costs"].values()):
            raise ValueError("Acquisition accounting mismatch")
        if row["policy"].endswith("NoType") and row["costs"]["type"] != 0:
            raise ValueError("Unavailable type action was charged")
        groups[cell(row)].append(row)
    summary, paired, curves, diagnostics = [], [], [], []
    rng = np.random.default_rng(cfg["bootstrap_analysis_seed"])
    for key, group in sorted(groups.items()):
        partition, alpha, risk = key
        base = {"partition": list(partition), "alpha": alpha, "R": risk}
        by_policy = {policy: {r["index"]: r for r in group if r["policy"] == policy} for policy in POLICIES}
        indices = sorted(by_policy[POLICIES[0]])
        if any(set(by_policy[p]) != set(indices) for p in POLICIES):
            raise ValueError("Unpaired world indices")
        draws = rng.integers(0, len(indices), size=(cfg["bootstrap_resamples"], len(indices)))
        reference = next(ref for ref in refs if ref["partition"] == list(partition) and ref["alpha"] == alpha)
        for policy in POLICIES:
            rr = [by_policy[policy][i] for i in indices]
            online = np.asarray([row["online"] / risk for row in rr])
            total = np.asarray([row["total_acquisition"] / risk for row in rr])
            summary.append({**base, "policy": policy, "n": len(rr), "world_indices": indices,
                            "completed": sum(r["complete"] for r in rr), "censored": sum(r["censored"] for r in rr),
                            "wrong_certificates": sum(r["complete"] and not r["exact"] for r in rr),
                            "wrong_terminal_guesses": sum(not r["exact"] for r in rr),
                            "wrong_fraction_all": sum(r["complete"] and not r["exact"] for r in rr) / len(rr),
                            "mean_restricted_online_over_R": float(online.mean()),
                            "bootstrap_mean_95": bootstrap_interval(online, draws),
                            "mean_total_acquisition_over_R": float(total.mean()),
                            "bootstrap_total_mean_95": bootstrap_interval(total, draws),
                            "costs": {k: sum(r["costs"][k] for r in rr) for k in ("task", "type", "offline")},
                            "mean_task_over_R": float(np.mean([r["costs"]["task"] / risk for r in rr])),
                            "mean_type_over_R": float(np.mean([r["costs"]["type"] / risk for r in rr])),
                            "mean_offline_over_R": float(np.mean([r["costs"]["offline"] / risk for r in rr])),
                            "premium_regime": reference["premium_regime"],
                            **{k: float(np.mean([r[k] for r in rr])) for k in TIME_KEYS}})
            cap = rr[0]["online_cap"]
            budgets = sorted({min(cap, multiple * risk) for multiple in (1, 2, 4, 8, 12, 16, 24)} | {cap})
            curves.append({**base, "policy": policy, "curve": [confidence_at(rr, b) for b in budgets]})
            diagnostics.extend(diagnose(row, reference) for row in rr)
        for name, vector in contrast_vectors(by_policy, indices, risk).items():
            paired.append({**base, "contrast": name, "coefficients": CONTRASTS[name], "n_pairs": len(indices),
                           "world_indices": indices, "paired_differences_over_R": vector.tolist(),
                           "mean_benefit_over_R": float(vector.mean()), "paired_sd": float(vector.std(ddof=1)),
                           "paired_bootstrap_95": bootstrap_interval(vector, draws),
                           "censored_worlds": sum(any(by_policy[p][i]["censored"] for p in CONTRASTS[name]) for i in indices),
                           "exploratory": True, "multiplicity_adjusted": False,
                           "scope": "independent-world paired restricted-cost contrast; family-specific type schedules"})
    totals = {key: sum(row["costs"][key] for row in rows) for key in ("task", "type", "offline")}
    if totals != receipt["costs_including_partial"]:
        raise ValueError("Execution receipt and all-trajectory acquisition totals differ")
    facts = {"trajectories": len(rows), "independent_worlds": cov["planned_worlds"], "cells": len(groups),
             "per_cell_n": cfg["episodes_per_cell"], "costs": totals, "online_actions": totals["task"] + totals["type"],
             "total_acquisition": sum(totals.values()), "unique_world_offline_observations": sum(2*j["M"] for j in jobs(cfg)),
             "charged_policy_offline_observations": totals["offline"],
             "completed": sum(r["complete"] for r in rows), "censored": sum(r["censored"] for r in rows),
             "wrong_certificates": sum(r["complete"] and not r["exact"] for r in rows),
             "wall_seconds": receipt["seconds"], "evaluator_cpu_seconds": receipt["evaluator_cpu_seconds"],
             **{key: sum(r[key] for r in rows) for key in TIME_KEYS},
             "stop_mode": cfg["stop_mode"], "main_has_strict_certificate": False,
             "new_model_calls": 0, "new_confirmation_worlds": 0, "main_retries": receipt["retries"],
             "bootstrap_resamples": cfg["bootstrap_resamples"], "bootstrap_analysis_seed": cfg["bootstrap_analysis_seed"],
             "scope": "legacy floating main acquisition; certified terminal audit is a separate artifact"}
    return {"facts": facts, "summary": summary, "paired": paired, "coefficients": refs,
            "confidence_curves": curves, "diagnostics": diagnostics, "coverage": cov}


def main():
    cfg = json.loads((ROOT / "config.json").read_text())
    run = ROOT / "artifacts/run"
    receipt = json.loads((run / "execution.json").read_text())
    rows = load(run / "trajectories.jsonl")
    cov = coverage(rows, cfg)
    if receipt["status"] != "completed" or not cov["exact"]:
        (ROOT / "artifacts/analysis_incomplete.json").write_text(json.dumps({"status": "INCOMPLETE_NO_COMPLETE_COMPARISON", "execution": receipt, "coverage": cov}, indent=2) + "\n")
        raise RuntimeError("Incomplete main batch retained; no completed-only or silently reduced analysis")
    out = ROOT / "artifacts/analysis"
    if out.exists():
        raise RuntimeError("Analysis destination exists; no silent overwrite")
    result = analyze_rows(rows, cfg, receipt, references(cfg))
    out.mkdir()
    for name, value in result.items():
        (out / (name + ".json")).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    from .report import plots, write_reports
    plots(result, out, cfg)
    write_reports(result, cfg, ROOT)
    print(json.dumps(result["facts"], indent=2))


if __name__ == "__main__":
    main()
