"""Predeclared complete-denominator analysis and paired-tape replay."""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import json
from pathlib import Path

import run as harness
import numpy as np
from certification import CertifiedDecisionGate
from policies import forced_action

HERE = Path(__file__).resolve().parent


def verify_record(record, world, config):
    if record["status"].startswith("FAILED_INFRASTRUCTURE"):
        return {"world_id": world["id"], "arm": record["arm"],
                "status": "UNAVAILABLE_INFRASTRUCTURE_FAILURE"}
    public, private = world["public"], world["private"]
    d = public["d"]
    counts = np.zeros((d, 2, 2), dtype=np.int64)
    consumed = np.zeros(2 * d, dtype=int)
    tapes = [np.random.default_rng(harness.frozen_runner.stable_seed(private["response_seed"], str(a))).random(config["max_queries"])
             for a in range(2 * d)]
    exact_events = 0
    for t, event in enumerate(record["history"]):
        action, answer = event["action"], event["answer"]
        j, fmt = divmod(action, 2)
        mandatory = forced_action(t, d)
        assert event["t"] == t + 1
        assert event["forced"] == (mandatory is not None)
        if mandatory is not None:
            assert action == mandatory
        accuracy = float(Fraction(private["p"] if fmt == private["types"][public["groups"][j]] else private["q"]))
        correct = tapes[action][consumed[action]] < accuracy
        consumed[action] += 1
        assert answer == int((private["theta"][j] > 0) == correct)
        counts[j, fmt, answer] += 1
        threshold = world["R"] + float(np.log1p(counts.sum(axis=2)).sum())
        assert threshold == event["screen_threshold"]
        exact = (event["screen_gap"] >= threshold - config["gate_screen_margin"]
                 or (t + 1) % config["exact_gate_checkpoint"] == 0 or t + 1 == config["max_queries"])
        assert exact == (event["gate_status"] != "SCREENED_CONTINUE")
        exact_events += int(exact)
        if event["gate_status"] == "CERTIFIED":
            assert t == len(record["history"]) - 1
    matches_counts = counts.tolist() == record["counts"] and int(counts.sum()) == record["queries"]
    if record["status"].startswith("FAILED"):
        assert record["certificate"] is None and record["certified_output"] is None
        return {"world_id": world["id"], "arm": record["arm"],
                "status": "FAILED_PATH_RETAINED", "history_matches_terminal_counts": matches_counts}
    assert matches_counts
    assert exact_events == record["gate_calls"]
    if record["status"] == "CERTIFIED":
        certificate = CertifiedDecisionGate(public, R=world["R"]).check(counts)
        assert certificate["certified"] and certificate["item"] == record["certified_output"]
        assert record["certified_correct"] == (certificate["item"] == private["winner"])
        assert certificate["gap_lower"] == record["certificate"]["gap_lower"]
        assert certificate["threshold_upper"] == record["certificate"]["threshold_upper"]
    else:
        assert record["status"] == "CAPPED_UNCERTIFIED"
        assert record["certificate"] is None and record["certified_output"] is None
        assert record["queries"] == config["max_queries"]
    return {"world_id": world["id"], "arm": record["arm"], "status": "RAW_REPLAY_PASS",
            "queries": record["queries"], "terminal_certificate_rechecked": record["status"] == "CERTIFIED"}


def percentile(values):
    return [float(x) for x in np.quantile(values, [.025, .975])]


def analyze(mode="main"):
    source = HERE / "artifacts" / mode
    config = json.loads((source / "effective_config.json").read_text())
    if mode == "main":
        harness.check_freeze(config)
    worlds = {w["id"]: w for w in json.loads((source / "worlds.json").read_text())}
    plan = json.loads((source / "planned_jobs.json").read_text())
    expected = {(r["world_id"], r["arm"]) for r in plan}
    assert len(expected) == len(plan)
    records = [json.loads((source / f"{world}__{arm}.json").read_text()) for world, arm in sorted(expected)]
    assert {(r["world_id"], r["arm"]) for r in records} == expected
    summaries = json.loads((source / "summary.json").read_text())
    assert {(r["world_id"], r["arm"]) for r in summaries} == expected
    replay = [verify_record(r, worlds[r["world_id"]], config) for r in records]
    if mode != "main":
        result = {"stage": mode, "attempted": len(records), "replay": replay,
                  "observed_cpu_seconds": sum(r.get("cpu_seconds") or 0 for r in records),
                  "observed_queries": sum(r.get("queries") or 0 for r in records)}
        (source / "replay_receipt.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "replay"}, indent=2))
        return result
    cap = config["max_queries"]
    cost = lambda r: r["queries"] if r["status"] == "CERTIFIED" else cap
    by_key = {(r["cell_id"], r["replicate"], r["R"], r["arm"]): r for r in records}
    cells = {c["id"]: c for c in config["cells"]}
    catalogues = list(dict.fromkeys(c["catalogue_name"] for c in config["cells"]))
    seeds = config["replicate_indices"]
    n = len(seeds)
    rng = np.random.default_rng(config["bootstrap_seed"])
    draws = {name: rng.integers(0, n, size=(config["bootstrap_repetitions"], n)) for name in catalogues}
    aggregates, vectors = [], {}
    for cell in cells.values():
        for R in config["risk_R_values"]:
            for arm in config["arms"]:
                rows = [by_key[cell["id"], seed, R, arm] for seed in seeds]
                values = np.asarray([cost(r) for r in rows], dtype=float)
                key = cell["id"], R, arm
                vectors[key] = values
                boot = values[draws[cell["catalogue_name"]]].mean(axis=1)
                aggregates.append({
                    "cell_id": cell["id"], "catalogue_name": cell["catalogue_name"], "R": R, "arm": arm,
                    "attempted": n, "certified": sum(r["status"] == "CERTIFIED" for r in rows),
                    "wrong_certified": sum(r.get("certified_correct") is False for r in rows),
                    "capped": sum(r["status"] == "CAPPED_UNCERTIFIED" for r in rows),
                    "failed": sum(r["status"].startswith("FAILED") for r in rows),
                    "postprocessing_failures": sum(r.get("postprocessing_failure") is not None for r in rows),
                    "restricted_mean_queries": float(values.mean()), "bootstrap_mean_ci95": percentile(boot),
                    "paired_seed_cost_vector": values.tolist(),
                    "mean_policy_seconds": float(np.mean([r.get("policy_seconds") or 0 for r in rows])),
                    "mean_gate_seconds": float(np.mean([r.get("gate_seconds") or 0 for r in rows])),
                    "cpu_seconds": sum(r.get("cpu_seconds") or 0 for r in rows),
                    "wall_seconds_sum": sum(r.get("wall_seconds") or 0 for r in rows)})
    comparisons = []
    for cell in cells.values():
        for R in config["risk_R_values"]:
            method = vectors[cell["id"], R, "decision_kl"]
            for baseline in ("decision_ig", "round_robin"):
                difference = vectors[cell["id"], R, baseline] - method
                boot = difference[draws[cell["catalogue_name"]]].mean(axis=1)
                comparisons.append({"cell_id": cell["id"], "R": R, "baseline": baseline,
                                    "baseline_minus_KL_vector": difference.tolist(),
                                    "mean_baseline_minus_KL": float(difference.mean()),
                                    "bootstrap_ci95": percentile(boot),
                                    "KL_lower_equal_higher": [int((difference > 0).sum()), int((difference == 0).sum()), int((difference < 0).sum())]})
    partition_effects = []
    for catalogue in catalogues:
        zero = next(c["id"] for c in cells.values() if c["catalogue_name"] == catalogue and c["premium"] == "zero")
        positive = next(c["id"] for c in cells.values() if c["catalogue_name"] == catalogue and c["premium"] == "positive")
        for R in config["risk_R_values"]:
            for arm in config["arms"]:
                difference = vectors[positive, R, arm] - vectors[zero, R, arm]
                partition_effects.append({"catalogue_name": catalogue, "R": R, "arm": arm,
                                          "positive_minus_zero_vector": difference.tolist(),
                                          "mean_positive_minus_zero": float(difference.mean()),
                                          "bootstrap_ci95": percentile(difference[draws[catalogue]].mean(axis=1))})
    pooled_comparisons = []
    for R in config["risk_R_values"]:
        for baseline in ("decision_ig", "round_robin"):
            all_diff, boot_means = [], []
            for catalogue in catalogues:
                ids = [c["id"] for c in cells.values() if c["catalogue_name"] == catalogue]
                values = np.stack([vectors[cell, R, baseline] - vectors[cell, R, "decision_kl"] for cell in ids]).mean(axis=0)
                all_diff.extend(values.tolist())
                boot_means.append(values[draws[catalogue]].mean(axis=1))
            pooled_comparisons.append({"R": R, "baseline": baseline,
                                       "cluster_mean_difference_vector": all_diff,
                                       "mean_baseline_minus_KL": float(np.mean(all_diff)),
                                       "bootstrap_ci95": percentile(np.mean(boot_means, axis=0))})
    # R is used only by the gate, so histories must coincide until the shorter run stops.
    prefix_checks = []
    for cell in cells:
        for seed in seeds:
            for arm in config["arms"]:
                low, high = (by_key[cell, seed, R, arm] for R in config["risk_R_values"])
                if low["status"].startswith("FAILED") or high["status"].startswith("FAILED"):
                    prefix_checks.append({"cell_id": cell, "seed": seed, "arm": arm, "status": "FAILED_PATH_RETAINED"})
                    continue
                lhs = [(r["action"], r["answer"]) for r in low["history"]]
                rhs = [(r["action"], r["answer"]) for r in high["history"]]
                assert lhs == rhs[:len(lhs)]
                prefix_checks.append({"cell_id": cell, "seed": seed, "arm": arm, "status": "R_PREFIX_PASS"})
    result = {"stage": "FROZEN_CONTROLLED_THEORY_ANCHOR_VALIDATION", "attempted": len(records),
              "worlds": len(worlds), "catalogue_anchors": len(catalogues), "response_seed_clusters": len(catalogues) * n,
              "certified": sum(r["status"] == "CERTIFIED" for r in records),
              "wrong_certified": sum(r.get("certified_correct") is False for r in records),
              "capped": sum(r["status"] == "CAPPED_UNCERTIFIED" for r in records),
              "failed": sum(r["status"].startswith("FAILED") for r in records),
              "observed_queries": sum(r.get("queries") or 0 for r in records),
              "observed_cpu_seconds": sum(r.get("cpu_seconds") or 0 for r in records),
              "aggregates": aggregates, "paired_comparisons": comparisons,
              "partition_effects": partition_effects, "pooled_policy_comparisons": pooled_comparisons,
              "raw_replay": replay, "cross_R_prefix_checks": prefix_checks,
              "cost_definition": "certified query count; full cap for every noncertified/failed trajectory",
              "uncertainty": "percentile cluster bootstrap of six paired response tapes within each fixed catalogue; joint pairing retained across partitions/R/arms; not profile or catalogue generalization",
              "risk": "analytic iid-model exp(-R); zero observed errors does not estimate or certify this risk",
              "oracle_empirical_baseline": None, "new_model_calls": 0, "training": False}
    target = HERE / "results"
    target.mkdir(exist_ok=True)
    (target / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    with (target / "plot_data.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["cell_id", "catalogue_name", "R", "arm", "attempted", "certified", "restricted_mean_queries", "ci_lower", "ci_upper"])
        writer.writeheader()
        for row in aggregates:
            writer.writerow({**{k: row[k] for k in writer.fieldnames if k not in {"ci_lower", "ci_upper"}},
                             "ci_lower": row["bootstrap_mean_ci95"][0], "ci_upper": row["bootstrap_mean_ci95"][1]})
    lines = ["# Controlled catalogue-mechanism validation", "",
             f"{result['attempted']} frozen trajectories; {result['certified']} certified; {result['capped']} capped; {result['failed']} failed; {result['wrong_certified']} wrong certified.", "",
             "| Cell | R | Arm | Certified | Capped | Failed | Mean restricted queries | 95% tape-bootstrap interval |",
             "|---|---:|---|---:|---:|---:|---:|---|" ]
    for row in aggregates:
        lo, hi = row["bootstrap_mean_ci95"]
        lines.append(f"| {row['cell_id']} | {row['R']} | {row['arm']} | {row['certified']}/{n} | {row['capped']} | {row['failed']} | {row['restricted_mean_queries']:.2f} | [{lo:.2f}, {hi:.2f}] |")
    lines += ["", "Restricted query cost assigns the full cap to noncertified and failed paths; these are not completed stopping times.", "",
              "## Matched partition contrasts", "", "Positive-premium minus zero-premium cost on the same response tapes:", "",
              "| Catalogue | R | Arm | Mean difference | 95% interval |", "|---|---:|---|---:|---|"]
    for row in partition_effects:
        lo, hi = row["bootstrap_ci95"]
        lines.append(f"| {row['catalogue_name']} | {row['R']} | {row['arm']} | {row['mean_positive_minus_zero']:.2f} | [{lo:.2f}, {hi:.2f}] |")
    lines += ["", "## Paired policy comparisons", "", "Positive values favor KL. Pooling weights both catalogues and their partitions equally.", "",
              "| R | Baseline | Mean baseline minus KL | 95% clustered interval |", "|---:|---|---:|---|"]
    for row in pooled_comparisons:
        lo, hi = row["bootstrap_ci95"]
        lines.append(f"| {row['R']} | {row['baseline']} | {row['mean_baseline_minus_KL']:.2f} | [{lo:.2f}, {hi:.2f}] |")
    lines += ["", "## Interpretation limits", "",
              "Only two fixed all-positive theory-anchor profiles were tested. Bootstrap uncertainty concerns iid response tapes conditional on these anchors. Six seeds per catalogue provide limited uncertainty resolution.",
              "Every group has true better format A. This isolates sharing structure, but a fixed-A baseline would be a trivial strong alternative in these particular controlled states. The benchmark does not establish natural latent reliability discovery or broad method superiority.",
              "The zero/positive label describes an asymptotic unknown-type versus known-type coefficient premium. No empirical known-type oracle was run; a finite positive-minus-zero partition contrast is a mechanism diagnostic, not a direct estimator or proof of that premium.",
              "The KL allocator uses finite-tolerance continuous optimization and IG uses order-6 quadrature. Common delayed exact stopping certifies individual decisions under the iid channel; it does not establish algorithmic optimality, SOTA performance, human realism, or an earliest stopping time.",
              "Raw answers, complete failures, paired seed vectors, interval methods, and runtimes are retained. No path was replaced, retried, filtered, or used to tune a method."]
    (target / "RESULTS.md").write_text("\n".join(lines) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), layout="constrained")
    labels = {"decision_kl": "Decision KL", "decision_ig": "Repaired IG", "round_robin": "Round robin"}
    colors = ["#2874ad", "#d08024", "#888888"]
    for i, catalogue in enumerate(catalogues):
        for j, R in enumerate(config["risk_R_values"]):
            ax = axes[i, j]
            for k, arm in enumerate(config["arms"]):
                rows = [next(r for r in aggregates if r["cell_id"] == f"{catalogue}_{premium}" and r["R"] == R and r["arm"] == arm)
                        for premium in ("zero", "positive")]
                means = np.asarray([r["restricted_mean_queries"] for r in rows])
                ci = np.asarray([r["bootstrap_mean_ci95"] for r in rows]).T
                x = np.arange(2) + (k - 1) * .24
                ax.bar(x, means, width=.23, color=colors[k], label=labels[arm])
                ax.errorbar(x, means, yerr=np.maximum(0, np.vstack((means - ci[0], ci[1] - means))), fmt="none", color="black", linewidth=.7, capsize=2)
            ax.set_xticks([0, 1], ["Zero-premium partition", "Positive-premium partition"], fontsize=8)
            ax.set_title(f"{catalogue}, R={R}")
            ax.set_ylabel("Restricted queries")
            ax.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(fontsize=8)
    for suffix in ("png", "pdf"):
        fig.savefig(target / f"mechanism_comparison.{suffix}", dpi=200)
    plt.close(fig)
    print(json.dumps({k: result[k] for k in ["attempted", "certified", "wrong_certified", "capped", "failed", "observed_queries", "observed_cpu_seconds", "pooled_policy_comparisons"]}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "runtime_smoke", "main"], default="main")
    analyze(parser.parse_args().mode)
