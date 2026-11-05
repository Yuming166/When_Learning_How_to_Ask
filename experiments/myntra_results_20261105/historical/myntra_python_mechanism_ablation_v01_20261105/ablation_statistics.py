"""Paired profile-cluster analysis; no policy execution or model access."""
from __future__ import annotations

import collections
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import experiment as exp


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


def trajectory_diagnostics(records):
    index = {(r["split"], r["case_id"], r["method"], r["budget"]): r for r in records}
    out = {}
    for b in range(7):
        rr = [r for r in records if r["method"] == "decision_value" and r["budget"] == b]
        controls = [index[(r["split"], r["case_id"], exp.CFG["new_method"], b)] for r in rr]
        out[str(b)] = {"cases": len(rr),
            "different_query_prefix": sum(r["query_sequence"] != c["query_sequence"] for r, c in zip(rr, controls)),
            "different_queried_field_set": sum(set(r["query_sequence"]) != set(c["query_sequence"]) for r, c in zip(rr, controls)),
            "different_selected_action": sum(r["selected_action"] != c["selected_action"] for r, c in zip(rr, controls))}
    return out


def interval_text(entry, weighting="case_equal"):
    d = entry[weighting]
    lo, hi = d["pointwise_95_ci"]
    return f"{100*d['difference']:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]"


def make_plot(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.1), constrained_layout=True)
    x = np.arange(7)
    styles = [("decision_value", "Adaptive DV", "#1764ab"),
              (exp.CFG["new_method"], "Initial-order DV", "#d77a16"),
              ("decision_set_ig", "Decision-Set IG", "#4b8150")]
    for method, label, color in styles:
        axes[0].plot(x, [100*a["curves"][method][str(b)]["case_equal_accuracy"] for b in x],
                     marker="o", color=color, label=label, linewidth=1.8, markersize=4)
    axes[0].set(xlabel="Question budget", ylabel="Exact decision accuracy (%)", xticks=x, ylim=(0, 103))
    axes[0].legend(frameon=False, loc="lower right")
    for cname, label, color, offset in (("adaptivity", "DV - initial-order DV", "#1764ab", -0.06),
                                       ("decision_objective", "DV - Decision-Set IG", "#4b8150", 0.06)):
        entries = a["groups"]["pooled"]["contrasts"][cname]["budgets"]
        y = np.array([100*entries[str(b)]["case_equal"]["difference"] for b in x])
        ci = np.array([entries[str(b)]["case_equal"]["pointwise_95_ci"] for b in x]) * 100
        axes[1].errorbar(x + offset, y, yerr=np.stack((y-ci[:, 0], ci[:, 1]-y)),
                         marker="o", color=color, capsize=3, label=label, markersize=4, linewidth=1.5)
    axes[1].axhline(0, color="#666666", linewidth=0.8)
    axes[1].set(xlabel="Question budget", ylabel="Paired accuracy difference (pp)", xticks=x)
    axes[1].legend(frameon=False, loc="upper right")
    for ax in axes:
        ax.axvline(5, color="#aaaaaa", linestyle=":", linewidth=0.9, zorder=0)
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Controlled synthetic-user ablation: 736 cases, 288 profiles\nPost-hoc pooled analysis; case weighting; pointwise 95% profile-cluster intervals", fontsize=11)
    fig.savefig(exp.RESULTS / "MECHANISM_ABLATION.png", dpi=200)
    fig.savefig(exp.RESULTS / "MECHANISM_ABLATION.pdf")
    plt.close(fig)


def report(a):
    curves, pooled = a["curves"], a["groups"]["pooled"]
    names = {"fixed_order": "原固定顺序", "profile_ig": "Profile IG", "decision_set_ig": "Decision-Set IG",
             "decision_value": "完整 DV", "decision_value_initial_order": "初始 DV 固定顺序"}
    lines = ["# Python 机制消融：合并受控基准", "",
        "状态：完整执行并分析。736 个画像–菜单案例，288 个画像，54 个固定菜单；模型调用和训练均为 0。",
        "这是查看完整方法结果后设计、在新增消融结果产生前冻结的事后组件分析；原开发/验证/测试结果不改写。", "",
        "## 主要结果", "", "正确数和准确率以全部 736 案例为分母；差值和区间单位均为百分点。", "",
        "|预算|完整 DV|初始 DV 固定顺序|DV − 固定顺序（点态95%CI）|DV − Decision-Set IG（点态95%CI）|",
        "|---|---:|---:|---:|---:|"]
    for b in exp.CFG["display_budgets"]:
        dv, static = curves["decision_value"][str(b)], curves[exp.CFG["new_method"]][str(b)]
        adapt = pooled["contrasts"]["adaptivity"]["budgets"][str(b)]
        obj = pooled["contrasts"]["decision_objective"]["budgets"][str(b)]
        lines.append(f"|{b}|{dv['correct']}/736 ({100*dv['case_equal_accuracy']:.2f}%)|{static['correct']}/736 ({100*static['case_equal_accuracy']:.2f}%)|{interval_text(adapt)}|{interval_text(obj)}|")
    primary = pooled["contrasts"]["adaptivity"]["budgets"]["5"]
    lines += ["", f"预算5主消融：{interval_text(primary)}；画像均权敏感性：{interval_text(primary, 'profile_equal')}。",
        f"配对案例胜/平/负：{primary['case_wins_ties_losses']}；画像净胜/平/负：{primary['profile_net_wins_ties_losses']}。",
        "画像平局表示跨菜单净正确数相同，不保证提问路径或每个菜单结果相同。", ""]
    for weighting, label in (("case_equal", "案例均权"), ("profile_equal", "画像均权")):
        lo, hi = primary[weighting]["simultaneous_14_contrast_95_band"]
        lines.append(f"{label}预算5主消融的14对比同时95%区间：[{100*lo:+.2f}, {100*hi:+.2f}]。")
    d = primary["case_equal"]
    if d["pointwise_95_ci"][0] > 0:
        interpretation = "当前合并基准的案例平均结果支持在线调整提问顺序的正向贡献。"
    elif d["pointwise_95_ci"][1] < 0:
        interpretation = "当前合并基准上，预算5的在线重排表现低于初始固定排序；保留该负结果，不调整消融定义。"
    else:
        interpretation = "当前预算5区间包含0，尚不能清楚确定在线重排的平均收益方向；这不证明两种策略等价。"
    lines += ["", interpretation, "", "## 完整预算曲线", "",
              "|预算|原固定顺序|Profile IG|Decision-Set IG|初始 DV 固定顺序|完整 DV|", "|---|---:|---:|---:|---:|---:|"]
    for b in range(7):
        values = [curves[m][str(b)]["correct"] for m in ("fixed_order", "profile_ig", "decision_set_ig", exp.CFG["new_method"], "decision_value")]
        lines.append("|" + str(b) + "|" + "|".join(f"{v}/736 ({100*v/736:.2f}%)" for v in values) + "|")
    lines += ["", "## 原划分分项", "", "|划分|案例/画像|预算3 DV−固定顺序|预算4|预算5|", "|---|---:|---:|---:|---:|"]
    for split in exp.CFG["splits"]:
        g = a["groups"]["split:" + split]
        vals = [interval_text(g["contrasts"]["adaptivity"]["budgets"][str(b)]) for b in (3, 4, 5)]
        lines.append(f"|{split}|{g['cases']}/{g['profiles']}|" + "|".join(vals) + "|")
    lines += ["", "## 品类池分项（预算5）", "", "|品类池|案例/画像|DV−固定顺序（点态95%CI）|", "|---|---:|---:|"]
    for label, g in a["groups"].items():
        if label.startswith("pool:"):
            lines.append(f"|{label[5:]}|{g['cases']}/{g['profiles']}|{interval_text(g['contrasts']['adaptivity']['budgets']['5'])}|")
    lines += ["", "## 轨迹与推荐差异", "", "|预算|提问前缀不同|已问字段集合不同|最终动作不同|", "|---|---:|---:|---:|"]
    for b, d in a["trajectory_diagnostics"].items():
        lines.append(f"|{b}|{d['different_query_prefix']}|{d['different_queried_field_set']}|{d['different_selected_action']}|")
    lines += ["", "## 错误与约束（预算5）", "", "|策略|错误购买|硬约束违规|平均归一化regret|", "|---|---:|---:|---:|"]
    for method in ("decision_value", exp.CFG["new_method"], "decision_set_ig"):
        m = curves[method]["5"]
        lines.append(f"|{names[method]}|{m['false_purchase']}|{m['hard_violations']}|{m['mean_normalized_regret']:.6f}|")
    lines += ["", "## 实现、核验与解释边界", "",
        "- 初始顺序由原 score_query 在空历史下计算，按原动作顺序处理精确并列；同一菜单的所有顾客共用该顺序。",
        "- 仅固定下一问；偏好覆盖更新、最终推荐、硬约束、NO_BUY 和 OOV 规则全部保留。",
        "- 历史四策略逐条重算隐藏真值指标，历史 DV 另逐条重放观察和推荐；原自适应问题选择路径直接复用，未重新搜索。",
        "- 原历史指标共20608条，历史DV推荐共5152条，新静态轨迹5152条；预算0/1/6推荐逐案一致，预算6全部正确。",
        "- 按split×pool×cohort分层（合并32层），按画像整簇配对bootstrap 10000次，菜单随画像携带；同时区间覆盖2对比×7预算。",
        "- 案例均权会给予菜单较多的画像更大权重；画像均权单列，不能通过选择有利权重改变主结果。",
        "- 问题预算相同不代表计算量相同；初始排序及重复预测采用精确确定性缓存，缓存不增加样本。",
        "- 区间仅描述固定菜单条件下合成画像生成器的不确定性，不覆盖真实顾客、目录外泛化或历史方法选择。",
        "- 先验敏感性未在本轮改变；未新增LLM交互或购买行为实验。", "",
        "## 复现文件", "",
        "PROTOCOL.md、FROZEN.json、TEST_RECEIPT.json、results/PAIRED_CASES.jsonl、results/CASE_REPLAY_RECEIPTS.jsonl、",
        "results/INITIAL_QUERY_ORDERS.jsonl、results/ANALYSIS.json、results/ACCURACY_CURVES.csv、results/CONTRASTS.csv、results/VERIFICATION.json。", ""]
    return "\n".join(lines)


def analyze():
    exp.verify_inputs()
    complete = exp.read(exp.RESULTS / "RUN_COMPLETED.json")
    trace = exp.RESULTS / "PAIRED_CASES.jsonl"
    if exp.sha(trace) != complete["trace_sha256"]:
        raise RuntimeError("Trace differs from completed run")
    records = exp.rows(trace)
    methods = exp.CFG["historical_methods"] + [exp.CFG["new_method"]]
    groups = {"pooled": records}
    groups.update({"split:" + s: [r for r in records if r["split"] == s] for s in exp.CFG["splits"]})
    pools = sorted({(r["gender"], r["category"]) for r in records})
    groups.update({"pool:" + g + "/" + c: [r for r in records if (r["gender"], r["category"]) == (g, c)] for g, c in pools})
    a = {"status": "ANALYZED_COMPLETE", "analysis_status": exp.CFG["analysis_status"],
         "config": exp.CFG, "trace_sha256": exp.sha(trace), "curves": method_curves(records, methods),
         "groups": {label: bootstrap(rr, exp.CFG, label) for label, rr in groups.items()},
         "split_curves": {s: method_curves(groups["split:" + s], methods) for s in exp.CFG["splits"]},
         "trajectory_diagnostics": trajectory_diagnostics(records), "model_calls": 0, "training_runs": 0}
    exp.dump(exp.RESULTS / "ANALYSIS.json", a)
    (exp.RESULTS / "REPORT_ZH.md").write_text(report(a))
    with (exp.RESULTS / "ACCURACY_CURVES.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "budget", *a["curves"][methods[0]]["0"]])
        writer.writeheader()
        for m in methods:
            for b in range(7):
                writer.writerow({"method": m, "budget": b, **a["curves"][m][str(b)]})
    with (exp.RESULTS / "CONTRASTS.csv").open("w", newline="") as f:
        fields = ["group", "contrast", "budget", "weighting", "cases", "profiles", "difference", "pointwise_lower", "pointwise_upper", "simultaneous_lower", "simultaneous_upper"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for label, group in a["groups"].items():
            for cname, contrast in group["contrasts"].items():
                for b, entry in contrast["budgets"].items():
                    for weighting in ("case_equal", "profile_equal"):
                        v = entry[weighting]
                        writer.writerow({"group": label, "contrast": cname, "budget": b, "weighting": weighting,
                            "cases": group["cases"], "profiles": group["profiles"], "difference": v["difference"],
                            "pointwise_lower": v["pointwise_95_ci"][0], "pointwise_upper": v["pointwise_95_ci"][1],
                            "simultaneous_lower": v["simultaneous_14_contrast_95_band"][0],
                            "simultaneous_upper": v["simultaneous_14_contrast_95_band"][1]})
    make_plot(a)
    outputs = sorted(p for p in exp.RESULTS.iterdir() if p.is_file() and p.name not in ("OUTPUT_MANIFEST.json", "VERIFICATION.json"))
    exp.dump(exp.RESULTS / "OUTPUT_MANIFEST.json", {"files_sha256": {str(p.relative_to(exp.HERE)): exp.sha(p) for p in outputs}})
    primary = a["groups"]["pooled"]["contrasts"]["adaptivity"]["budgets"]["5"]
    return {"status": a["status"], "primary_adaptivity_budget5": primary}
