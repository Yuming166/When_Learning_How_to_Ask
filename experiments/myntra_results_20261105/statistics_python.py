from __future__ import annotations
import collections
import hashlib
import numpy as np

def cluster_arrays(records, contrasts):
    index = {(r["split"], r["case_id"], r["method"], r["budget"]): r for r in records}
    if len(index) != len(records):
        raise RuntimeError("Duplicated rows cannot enter analysis")
    case_rows = [r for r in records if r["method"] == "decision_value" and r["budget"] == 0]
    clusters = collections.defaultdict(list)
    meta = {}
    for row in case_rows:
        pid = (row["split"], row["profile_id"])
        clusters[pid].append(row["case_id"])
        meta[pid] = (row["split"], row["pool_index"], row["user_cohort"])
    ids = sorted(clusters)
    sums = np.zeros((len(ids), len(contrasts), 7), dtype=np.int64)
    sizes = np.array([len(clusters[pid]) for pid in ids], dtype=np.int64)
    strata = collections.defaultdict(list)
    for i, pid in enumerate(ids):
        strata[meta[pid]].append(i)
        for c, contrast in enumerate(contrasts):
            for b in range(7):
                sums[i, c, b] = sum(
                    int(index[(pid[0], cid, contrast["treatment"], b)]["exact_decision_correct"])
                    - int(index[(pid[0], cid, contrast["control"], b)]["exact_decision_correct"])
                    for cid in clusters[pid])
    return ids, sums, sizes, strata



def bootstrap(records, config, label):
    ids, sums, sizes, strata = cluster_arrays(records, config["contrasts"])
    reps = config["bootstrap_repetitions"]
    # Group labels, not outcomes, determine reproducible independent RNG streams.
    offset = 0 if label == "pooled" else int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], "big")
    seed = config["bootstrap_seed"] + offset
    rng = np.random.default_rng(seed)
    sampled_sums = np.zeros((reps, 2, 7), dtype=np.int64)
    sampled_sizes = np.zeros(reps, dtype=np.int64)
    sampled_profile_means = np.zeros((reps, 2, 7))
    means = sums / sizes[:, None, None]
    for key in sorted(strata):
        choices = np.array(strata[key])
        sample = rng.choice(choices, size=(reps, len(choices)), replace=True)
        sampled_sums += sums[sample].sum(axis=1)
        sampled_sizes += sizes[sample].sum(axis=1)
        sampled_profile_means += means[sample].sum(axis=1)
    estimates = {"case_equal": sums.sum(axis=0) / sizes.sum(), "profile_equal": means.mean(axis=0)}
    distributions = {"case_equal": sampled_sums / sampled_sizes[:, None, None],
                     "profile_equal": sampled_profile_means / len(ids)}
    result = {"cases": int(sizes.sum()), "profiles": len(ids), "strata": len(strata),
              "repetitions": reps, "seed": seed, "numpy_version": np.__version__,
              "scope": config["claim_scope"], "contrasts": {}}
    for c, contrast in enumerate(config["contrasts"]):
        result["contrasts"][contrast["name"]] = {**contrast, "budgets": {}}
        for b in range(7):
            case_diffs = []
            index = {(r["split"], r["case_id"], r["method"], r["budget"]): r for r in records}
            for row in records:
                if row["method"] == contrast["treatment"] and row["budget"] == b:
                    other = index[(row["split"], row["case_id"], contrast["control"], b)]
                    case_diffs.append(int(row["exact_decision_correct"]) - int(other["exact_decision_correct"]))
            entry = {"difference_correct": int(sums[:, c, b].sum()),
                     "case_wins_ties_losses": [sum(d > 0 for d in case_diffs), sum(d == 0 for d in case_diffs), sum(d < 0 for d in case_diffs)],
                     "profile_net_wins_ties_losses": [int((sums[:, c, b] > 0).sum()), int((sums[:, c, b] == 0).sum()), int((sums[:, c, b] < 0).sum())]}
            for weighting, dist in distributions.items():
                point = estimates[weighting]
                interval = np.quantile(dist[:, c, b], [0.025, 0.975], method="linear")
                radius = float(np.quantile(np.max(np.abs(dist - point[None, :, :]), axis=(1, 2)), 0.95, method="linear"))
                entry[weighting] = {"difference": float(point[c, b]), "pointwise_95_ci": interval.tolist(),
                                    "simultaneous_14_contrast_95_band": [float(point[c, b]) - radius, float(point[c, b]) + radius]}
            result["contrasts"][contrast["name"]]["budgets"][str(b)] = entry
    return result



def method_curves(records, methods):
    result = {}
    for method in methods:
        result[method] = {}
        for b in range(7):
            rr = [r for r in records if r["method"] == method and r["budget"] == b]
            profile = collections.defaultdict(list)
            for r in rr:
                profile[(r["split"], r["profile_id"])].append(int(r["exact_decision_correct"]))
            result[method][str(b)] = {
                "correct": sum(r["exact_decision_correct"] for r in rr), "cases": len(rr),
                "case_equal_accuracy": sum(r["exact_decision_correct"] for r in rr) / len(rr),
                "profile_equal_accuracy": sum(sum(v) / len(v) for v in profile.values()) / len(profile),
                "correct_buy": sum(r["purchase_recall_case"] for r in rr),
                "correct_no_buy": sum(r["no_buy_correct_case"] for r in rr),
                "false_purchase": sum(r["false_purchase_case"] for r in rr),
                "hard_violations": sum(r["hard_constraint_violation"] for r in rr),
                "mean_normalized_regret": sum(r["normalized_score_regret"] for r in rr) / len(rr),
                "mean_score_regret": sum(r["score_regret"] for r in rr) / len(rr)}
    return result
