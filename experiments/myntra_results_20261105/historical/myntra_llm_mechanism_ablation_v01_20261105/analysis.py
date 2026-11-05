"""Joint profile resampling for three dependent LLM response channels."""
from __future__ import annotations

import collections
import csv
import hashlib
import numpy as np

import experiment as ex


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


def ci_text(entry, weight="case_equal", field="pointwise_95_ci"):
    v = entry[weight]
    lo, hi = v[field]
    return f"{100*v['difference']:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]"


def make_plot(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True, constrained_layout=True)
    for ax, model in zip(axes, ex.CFG["models"]):
        for method, label, color in (("decision_value", "Adaptive DV", "#1764ab"), (ex.STATIC, "Initial-order DV", "#d77a16")):
            ax.plot(range(7), [100*a["curves"][model][method][str(b)]["accuracy"] for b in range(7)],
                    marker="o", markersize=4, linewidth=1.8, color=color, label=label)
        ax.set(title=ex.CFG["models"][model]["label"], xlabel="Question budget ceiling", xticks=range(7), ylim=(0, 103))
        ax.axvline(5, color="#aaaaaa", linestyle=":", linewidth=0.8)
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Exact decision accuracy (%)")
    axes[0].legend(frameon=False, loc="lower right")
    fig.suptitle("Recorded LLM customer channels: same 280 cases / 48 profiles per model\nPost-hoc paired replay; all original failures retained; zero new model calls", fontsize=11)
    fig.savefig(ex.RESULTS / "THREE_MODEL_ABLATION.png", dpi=200)
    fig.savefig(ex.RESULTS / "THREE_MODEL_ABLATION.pdf")
    plt.close(fig)


def write_report(a):
    lines = ["# 三种 LLM 顾客通道的关键自适应消融", "",
        "状态：完整执行、全分母分析。每个模型280案例、48画像、35菜单；复用各288条原始真实LLM字段回答，本轮新增模型调用和训练均为0。",
        "完整DV与初始DV固定排序共享同一模型回答库；仅移除按回答重新选下一问，仍更新偏好并推荐。",
        "本轮是已查看历史结果后进行的配对回答库重放。推荐方仍为Python，当前不是自由多轮LLM顾客交互。", "",
        "## 主结果与预算敏感性", "", "差值单位为百分点，区间为按画像聚类的点态95%CI；预算5为主比较。", "",
        "|模型|预算|完整DV|初始DV固定顺序|DV−固定顺序（点态95%CI）|", "|---|---:|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        for b in ex.CFG["display_budgets"]:
            dv, static = [a["curves"][model][m][str(b)] for m in ex.CFG["evaluated_methods"]]
            lines.append(f"|{info['label']}|{b}|{dv['correct']}/280 ({100*dv['accuracy']:.2f}%)|{static['correct']}/280 ({100*static['accuracy']:.2f}%)|{ci_text(a['full']['models'][model][str(b)])}|")
    lines += ["", "## 预算5：权重与同时区间", "",
        "|模型|案例均权，点态95%CI|画像均权，点态95%CI|案例均权，3模型主比较同时95%带|案例均权，21对比同时95%带|",
        "|---|---:|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        entry = a["full"]["models"][model]["5"]
        lines.append(f"|{info['label']}|{ci_text(entry)}|{ci_text(entry, 'profile_equal')}|{ci_text(entry, field='simultaneous_primary_three_models_95_band')}|{ci_text(entry, field='simultaneous_21_contrast_95_band')}|")
    lines += ["", "## 预算5的失败、成本与配对分布", "",
        "成本为实际尝试问题数；首次失败也计1单位，此后停问。相同预算上限不保证失败后的实际成本相同。", "",
        "|模型|方法|停问案例/280|平均实际问题数|错误购买|硬约束违规|平均归一化regret|", "|---|---|---:|---:|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        for method in ex.CFG["evaluated_methods"]:
            r = a["curves"][model][method]["5"]
            lines.append(f"|{info['label']}|{method}|{r['stopped_paths']}|{r['mean_actual_question_units']:.3f}|{r['false_purchases']}|{r['hard_violations']}|{r['mean_normalized_regret']:.6f}|")
    lines.append("")
    for model, info in ex.CFG["models"].items():
        entry = a["full"]["models"][model]["5"]
        lines.append(f"{info['label']}：案例胜/平/负{entry['case_wins_ties_losses']}，画像净胜/平/负{entry['profile_net_wins_ties_losses']}。")
        lines.append("")
    lines += ["## 回答库与共同完整有效诊断", "", "|模型|有效字段/288|符合隐藏画像字段/288|完整有效画像/48|", "|---|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        q = a["quality"][model]
        lines.append(f"|{info['label']}|{q['valid']}|{q['exact']}|{q['complete_valid_profiles']}|")
    lines += ["", "全部原传输失败、无效输出和有效但不忠实回答保留，不修复、不补采；失败路径仍按真实推荐动作评分，不能直接记错。",
        f"共同完整有效子集：{a['common_complete']['profiles']}画像、{a['common_complete']['cases_per_model']}案例/模型。该子集排除了失败画像，只作为次要诊断。", "",
        "|模型|预算5完整DV正确数|固定顺序正确数|配对差（点态95%CI）|", "|---|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        cv = a["common_complete_curves"][model]
        lines.append(f"|{info['label']}|{cv['decision_value']['5']['correct']}|{cv[ex.STATIC]['5']['correct']}|{ci_text(a['common_complete']['models'][model]['5'])}|")
    lines += ["", f"共同子集三模型字段值完全一致：{a['common_subset_banks_identical']}。若有效输入相同，确定性策略输出相同不构成额外独立模型证据。", "",
        "## 完整0–6曲线", "", "|模型|预算|完整DV正确数/280|固定顺序正确数/280|差值及点态95%CI|", "|---|---:|---:|---:|---:|"]
    for model, info in ex.CFG["models"].items():
        for b in range(7):
            dv, static = [a["curves"][model][m][str(b)]["correct"] for m in ex.CFG["evaluated_methods"]]
            lines.append(f"|{info['label']}|{b}|{dv}|{static}|{ci_text(a['full']['models'][model][str(b)])}|")
    lines += ["", "## 核验与结论边界", "",
        "- 历史完整DV的5880条预算记录逐字段重放一致，另生成5880条静态记录，共11760行。原动态选问路径复用，未重新搜索。",
        "- 35菜单初始分数、顺序和推荐与Python消融完全一致；六字段均有效且精确时，新静态轨迹与Python静态轨迹一致。",
        "- 每案两策略预算0/1相同。失败可能造成预算6不同；有效但不忠实回答也可能使完整问询后仍推荐错误。",
        "- 48画像、12个pool×cohort层整簇配对抽样10000次；同次抽样同时携带三个模型和该画像全部菜单。模型案例没有合并成840独立样本。",
        "- 案例均权与画像均权分别报告。点态、3主比较同时带、21全曲线同时带有不同覆盖范围；两种权重不合并成统一覆盖保证。",
        "- 区间条件于固定菜单、先验和单次已实现回答库，不覆盖LLM重采样、真人行为或目录外泛化。共同子集为失败排除诊断，不能替换全280案例。",
        "- Luna为请求的CLI别名，服务端身份和采样设置未完整独立核验；DeepSeek/GLM为千问端点报告标识。原传输与解码差异保留，不能将模型差异单独归因于权重。",
        "- 该结果支持的范围是三个指定结构化顾客回答通道中的组件贡献；没有验证自然多轮顾客或LLM驱动推荐端。", "",
        "## 文件与复现", "",
        "PROTOCOL.md、FROZEN.json、TEST_RECEIPT.json、PREPARED.json、results/PAIRED_CASES.jsonl、results/CASE_REPLAY_RECEIPTS.jsonl、",
        "results/ANALYSIS.json、results/ACCURACY_CURVES.csv、results/CONTRASTS.csv、results/THREE_MODEL_ABLATION.pdf、results/VERIFICATION.json。", ""]
    (ex.RESULTS / "REPORT_ZH.md").write_text("\n".join(lines))


def analyze():
    ex.verify_inputs()
    complete = ex.read(ex.RESULTS / "RUN_COMPLETED.json")
    if ex.sha(ex.RESULTS / "PAIRED_CASES.jsonl") != complete["trace_sha256"]:
        raise RuntimeError("Trace hash mismatch")
    rr = ex.rows(ex.RESULTS / "PAIRED_CASES.jsonl")
    prepared = ex.read(ex.HERE / "PREPARED.json")
    common_ids = set(prepared["common_complete_profiles"])
    common = [r for r in rr if r["profile_id"] in common_ids]
    data = ex.load_data()
    model_names = list(ex.CFG["models"])
    identical = all(ex.engine.canonical(data["banks"][model_names[0]][(pid, action)]["value"]) == ex.engine.canonical(data["banks"][m][(pid, action)]["value"])
                    for pid in common_ids for action in ex.CFG["query_actions"] for m in model_names[1:])
    a = {"status": "ANALYZED_COMPLETE", "analysis_status": ex.CFG["analysis_status"], "trace_sha256": complete["trace_sha256"],
         "config": ex.CFG, "quality": prepared["quality"], "curves": curves(rr), "full": joint_bootstrap(rr, ex.CFG),
         "common_complete": joint_bootstrap(common, ex.CFG, "common_complete"), "common_complete_curves": curves(common),
         "common_subset_banks_identical": identical, "trajectory_diagnostics": diagnostics(rr),
         "new_model_calls": 0, "training_runs": 0}
    ex.dump(ex.RESULTS / "ANALYSIS.json", a)
    write_report(a)
    with (ex.RESULTS / "ACCURACY_CURVES.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "method", "budget", *a["curves"][model_names[0]]["decision_value"]["0"]])
        writer.writeheader()
        for model in model_names:
            for method in ex.CFG["evaluated_methods"]:
                for b in range(7):
                    writer.writerow({"model": model, "method": method, "budget": b, **a["curves"][model][method][str(b)]})
    with (ex.RESULTS / "CONTRASTS.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "model", "budget", "weighting", "difference", "pointwise_lower", "pointwise_upper", "simultaneous21_lower", "simultaneous21_upper"])
        for sample in ("full", "common_complete"):
            for model in model_names:
                for b in range(7):
                    for weight in ("case_equal", "profile_equal"):
                        entry = a[sample]["models"][model][str(b)][weight]
                        writer.writerow([sample, model, b, weight, entry["difference"], *entry["pointwise_95_ci"], *entry["simultaneous_21_contrast_95_band"]])
    make_plot(a)
    outputs = [p for p in sorted(ex.RESULTS.iterdir()) if p.is_file() and p.name not in ("OUTPUT_MANIFEST.json", "VERIFICATION.json")]
    ex.dump(ex.RESULTS / "OUTPUT_MANIFEST.json", {"files_sha256": {str(p.relative_to(ex.HERE)): ex.sha(p) for p in outputs}})
    return {"status": a["status"], "primary_budget5": {m: a["full"]["models"][m]["5"] for m in model_names}}
