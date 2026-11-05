from __future__ import annotations
import collections
import hashlib
from types import SimpleNamespace
import numpy as np
ex = SimpleNamespace(STATIC='decision_value_initial_order')

def joint_bootstrap(records, config, label="full"):
    models = list(config["models"])
    lookup = {(r["model"], r["case_id"], r["method"], r["budget"]): r for r in records}
    if len(lookup) != len(records):
        raise RuntimeError("Duplicate analysis key")
    case_rows = [r for r in records if r["model"] == models[0] and r["method"] == "decision_value" and r["budget"] == 0]
    clusters, metadata = collections.defaultdict(list), {}
    for r in case_rows:
        clusters[r["profile_id"]].append(r["case_id"])
        metadata[r["profile_id"]] = (r["pool_index"], r["user_cohort"])
    ids = sorted(clusters)
    sizes = np.array([len(clusters[p]) for p in ids], dtype=np.int64)
    sums = np.zeros((len(ids), len(models), 7), dtype=np.int64)
    strata = collections.defaultdict(list)
    case_diffs = {}
    for i, pid in enumerate(ids):
        strata[metadata[pid]].append(i)
        for m, model in enumerate(models):
            for b in range(7):
                diffs = [int(lookup[(model, cid, "decision_value", b)]["exact_decision_correct"])
                         - int(lookup[(model, cid, ex.STATIC, b)]["exact_decision_correct"]) for cid in clusters[pid]]
                sums[i, m, b] = sum(diffs)
                case_diffs.setdefault((model, b), []).extend(diffs)
    means = sums / sizes[:, None, None]
    seed = config["bootstrap_seed"] + (0 if label == "full" else int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], "big"))
    rng = np.random.default_rng(seed)
    reps = config["bootstrap_repetitions"]
    sampled_sums = np.zeros((reps, len(models), 7), dtype=np.int64)
    sampled_sizes = np.zeros(reps, dtype=np.int64)
    sampled_means = np.zeros((reps, len(models), 7))
    for stratum in sorted(strata):
        candidates = np.array(strata[stratum])
        # One common draw carries ALL models and menus for each selected profile.
        sample = rng.choice(candidates, size=(reps, len(candidates)), replace=True)
        sampled_sums += sums[sample].sum(axis=1)
        sampled_sizes += sizes[sample].sum(axis=1)
        sampled_means += means[sample].sum(axis=1)
    points = {"case_equal": sums.sum(axis=0) / sizes.sum(), "profile_equal": means.mean(axis=0)}
    draws = {"case_equal": sampled_sums / sampled_sizes[:, None, None], "profile_equal": sampled_means / len(ids)}
    radii = {}
    for weight, dist in draws.items():
        deviation = np.abs(dist - points[weight][None, :, :])
        radii[weight] = {"primary_three_models": float(np.quantile(deviation[:, :, 5].max(axis=1), 0.95, method="linear")),
                        "all_21": float(np.quantile(deviation.max(axis=(1, 2)), 0.95, method="linear"))}
    result = {"profiles": len(ids), "cases_per_model": int(sizes.sum()), "strata": len(strata), "repetitions": reps,
              "seed": seed, "shared_profile_draws_across_models": True, "numpy_version": np.__version__, "models": {}}
    for m, model in enumerate(models):
        result["models"][model] = {}
        for b in range(7):
            d = case_diffs[(model, b)]
            entry = {"difference_correct": int(sums[:, m, b].sum()),
                "case_wins_ties_losses": [sum(v > 0 for v in d), sum(v == 0 for v in d), sum(v < 0 for v in d)],
                "profile_net_wins_ties_losses": [int((sums[:, m, b] > 0).sum()), int((sums[:, m, b] == 0).sum()), int((sums[:, m, b] < 0).sum())]}
            for weight, dist in draws.items():
                point = float(points[weight][m, b])
                entry[weight] = {"difference": point, "pointwise_95_ci": np.quantile(dist[:, m, b], [0.025, 0.975], method="linear").tolist(),
                    "simultaneous_21_contrast_95_band": [point-radii[weight]["all_21"], point+radii[weight]["all_21"]]}
                if b == 5:
                    radius = radii[weight]["primary_three_models"]
                    entry[weight]["simultaneous_primary_three_models_95_band"] = [point-radius, point+radius]
            result["models"][model][str(b)] = entry
    return result



def curves(records):
    result = {}
    for model in ex.CFG["models"]:
        result[model] = {}
        for method in ex.CFG["evaluated_methods"]:
            result[model][method] = {}
            for b in range(7):
                rr = [r for r in records if (r["model"], r["method"], r["budget"]) == (model, method, b)]
                profiles = collections.defaultdict(list)
                for r in rr:
                    profiles[r["profile_id"]].append(int(r["exact_decision_correct"]))
                result[model][method][str(b)] = {"correct": sum(r["exact_decision_correct"] for r in rr), "cases": len(rr),
                    "accuracy": sum(r["exact_decision_correct"] for r in rr) / len(rr),
                    "profile_equal_accuracy": sum(sum(v) / len(v) for v in profiles.values()) / len(profiles),
                    "stopped_paths": sum(not r["answer_path_complete"] for r in rr),
                    "mean_actual_question_units": sum(r["elicitation_units"] for r in rr) / len(rr),
                    "false_purchases": sum(r["false_purchase_case"] for r in rr),
                    "hard_violations": sum(r["hard_constraint_violation"] for r in rr),
                    "mean_normalized_regret": sum(r["normalized_score_regret"] for r in rr) / len(rr)}
    return result



def diagnostics(records):
    index = {(r["model"], r["case_id"], r["method"], r["budget"]): r for r in records}
    result = {}
    for model in ex.CFG["models"]:
        result[model] = {}
        for b in range(7):
            rr = [r for r in records if (r["model"], r["method"], r["budget"]) == (model, "decision_value", b)]
            cc = [index[(model, r["case_id"], ex.STATIC, b)] for r in rr]
            result[model][str(b)] = {
                "different_attempted_prefix": sum(r["query_sequence"] != c["query_sequence"] for r, c in zip(rr, cc)),
                "different_selected_action": sum(r["selected_action"] != c["selected_action"] for r, c in zip(rr, cc)),
                "different_stop_state": sum(r["answer_path_complete"] != c["answer_path_complete"] for r, c in zip(rr, cc))}
    return result
