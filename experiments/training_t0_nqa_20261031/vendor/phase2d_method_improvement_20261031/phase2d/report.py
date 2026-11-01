"""Post-run reports and standard scientific PNG/PDF artifacts."""
from pathlib import Path

import numpy as np

from .policy import POLICIES


CAPTION = "Development; legacy floating main; all capped paths retained; certified terminal audit is separate"
LABELS = {"task_without_type": "无类型时任务分配收益", "remaining_type_enabled_advantage": "类型可用时剩余优势",
          "kl_type_benefit": "KL 内类型收益", "simple_type_benefit": "D 内类型收益", "interaction": "交互差"}


def plots(result, out, cfg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = dict(zip(POLICIES, ("#ac3030", "#d88b21", "#2869a4", "#278052")))
    summary, refs = result["summary"], result["coefficients"]

    def save(fig, name):
        fig.suptitle(CAPTION, fontsize=9)
        fig.tight_layout(rect=(0, 0, 1, .96))
        fig.savefig(out / (name + ".png"), dpi=180)
        fig.savefig(out / (name + ".pdf"))
        plt.close(fig)

    for total in (False, True):
        fig, axes = plt.subplots(len(cfg["partitions"]), len(cfg["alphas"]), figsize=(12, 8), squeeze=False)
        for pi, partition in enumerate(cfg["partitions"]):
            for ai, alpha in enumerate(cfg["alphas"]):
                ax = axes[pi, ai]
                ref = next(r for r in refs if r["partition"] == partition and r["alpha"] == alpha)
                for policy in POLICIES:
                    rr = sorted((r for r in summary if r["partition"] == partition and r["alpha"] == alpha and r["policy"] == policy), key=lambda r: r["R"])
                    value = "mean_total_acquisition_over_R" if total else "mean_restricted_online_over_R"
                    interval = "bootstrap_total_mean_95" if total else "bootstrap_mean_95"
                    means = [r[value] for r in rr]
                    errors = [[max(0, r[value] - r[interval][0]) for r in rr],
                              [max(0, r[interval][1] - r[value]) for r in rr]]
                    ax.errorbar([r["R"] for r in rr], means, yerr=errors, fmt="o-", color=colors[policy], label=policy, markersize=4, capsize=2)
                    for r in rr:
                        if r["censored"]:
                            ax.plot(r["R"], r[value], "x", color="black", markersize=9)
                for name, style in (("K_no_type", "--"), ("K_with_type", ":")):
                    ax.axhline(ref[name] + (2 * alpha if total else 0), color="#555555", ls=style, lw=1, label=name)
                ax.set(title=f"partition={partition}, alpha={alpha}", xlabel="R = log(1/delta)",
                       ylabel="Restricted total acquisition / R" if total else "Restricted online cost / R")
                ax.set_xscale("log", base=4)
                ax.set_xticks(cfg["Rs"], cfg["Rs"])
                ax.set_ylim(bottom=0)
                ax.grid(alpha=.15)
        axes[0, 0].legend(fontsize=7)
        save(fig, "total_cost_ablation" if total else "online_cost_ablation")

    fig, axes = plt.subplots(len(cfg["partitions"]), len(cfg["alphas"]), figsize=(12, 8), squeeze=False)
    for pi, partition in enumerate(cfg["partitions"]):
        for ai, alpha in enumerate(cfg["alphas"]):
            ax = axes[pi, ai]
            for policy in POLICIES:
                rr = sorted((r for r in summary if r["partition"] == partition and r["alpha"] == alpha and r["policy"] == policy), key=lambda r: r["R"])
                ax.plot([r["trajectory_cpu_seconds"] for r in rr], [r["mean_restricted_online_over_R"] for r in rr], "o-", color=colors[policy], label=policy, markersize=4)
                for r in rr:
                    ax.annotate(str(r["R"]), (r["trajectory_cpu_seconds"], r["mean_restricted_online_over_R"]), fontsize=6, xytext=(3, 3), textcoords="offset points")
            ax.set(title=f"partition={partition}, alpha={alpha}", xlabel="Mean worker CPU seconds / path (labels: R)", ylabel="Restricted online cost / R")
            ax.set_xscale("log")
            ax.grid(alpha=.15)
    axes[0, 0].legend(fontsize=7)
    save(fig, "query_vs_cpu")


def write_reports(result, cfg, root):
    facts, summary, paired = result["facts"], result["summary"], result["paired"]
    root = Path(root)
    lines = ["# Phase 2d：任务与类型询问的四策略消融", "",
             "本报告分析一次预先冻结的开发批次。**主采样使用旧浮点停止规则；认证终点审计和认证重放是独立产物，不能把本批次成本改称为认证策略成本。**", "",
             f"记录 {facts['independent_worlds']} 个独立世界、{facts['trajectories']} 条轨迹、{facts['cells']} 个单元，每单元每策略 n={facts['per_cell_n']}。在线动作 {facts['online_actions']:,} 次；完成 {facts['completed']}/{facts['trajectories']}，上限删失 {facts['censored']}，错误浮点停止输出 {facts['wrong_certificates']}/{facts['trajectories']}。", "",
             f"独立世界共享离线样本共 {facts['unique_world_offline_observations']:,} 个；逐策略比较计费离线观测 {facts['charged_policy_offline_observations']:,} 个。逐策略 acquisition 合计 {facts['total_acquisition']:,}，不能把共享离线样本的唯一数量重复计作新采样量。", "",
             f"批次墙钟 {facts['wall_seconds']:.2f} 秒，evaluator CPU {facts['evaluator_cpu_seconds']:.2f} 秒；工作进程 CPU 合计 {facts['trajectory_cpu_seconds']:.2f} 秒。主批次重试 {facts['main_retries']}，模型调用和确认世界均为 0。", "",
             "四臂采用相同 forced-only theta/z/p/q 估计、网格、强制探索、更新、跟踪及未知组类型 GLR。类型报告只影响共同 GLR 和 D-RRC-Type 的购买节奏，不覆盖任务利用所用的共同 z 估计。两种策略家族采用各自的类型调度；这是四个明确策略的对照，不是统一调度下的纯类型主效应。", "",
             "D-RRC-Type 另有预先声明的公开结构判断：单组且参考样本为零时，直接使用冻结 D-RRC 目标。因此该控制单元中 D-RRC-Type 与 D-RRC-NoType 的相同路径/成本是构造结果，不能当作有限 R 下类型信息永不有用的实验证据，也不宣称其与浮点 Aligned-Full 逐位相同。判断依据是该模型的零领先阶溢价定理，未使用新结果、隐藏参数或标签。", "",
             "|分组|alpha|R|策略|N/R|任务/R|类型/R|离线/R|总获取/R|完成/全部|删失|错误浮点输出/全部|CPU秒|规划CPU秒|",
             "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in summary:
        lines.append(f"|{r['partition']}|{r['alpha']}|{r['R']}|{r['policy']}|{r['mean_restricted_online_over_R']:.4f}|{r['mean_task_over_R']:.4f}|{r['mean_type_over_R']:.4f}|{r['mean_offline_over_R']:.4f}|{r['mean_total_acquisition_over_R']:.4f}|{r['completed']}/{r['n']}|{r['censored']}|{r['wrong_certificates']}/{r['n']}|{r['trajectory_cpu_seconds']:.4f}|{r['planner_cpu_seconds']:.4f}|")
    lines += ["", "所有世界进入 min(T,B)/R 和总获取成本，删失保留其预算上限。未估计无截断 E[T]，未按完成状态筛选。完整均值区间、墙钟、GLR 和规划时长保留于 summary.json。", "",
              "下列四个收益对比均以正值为改善：D-NoType−Aligned-NoType；D-Type−Aligned-Full；Aligned-NoType−Aligned-Full；D-NoType−D-Type。交互差是 KL 内类型收益减 D 内类型收益，其正负仅比较两种具体调度的差别。", "",
              "|分组|alpha|R|无类型任务收益|类型可用剩余优势|KL 内类型收益|D 内类型收益|交互差|", "|---|---:|---:|---|---|---|---|---|"]
    keys = list(LABELS)
    for partition in cfg["partitions"]:
        for alpha in cfg["alphas"]:
            for risk in cfg["Rs"]:
                values = []
                for key in keys:
                    row = next(r for r in paired if r["partition"] == partition and r["alpha"] == alpha and r["R"] == risk and r["contrast"] == key)
                    lo, hi = row["paired_bootstrap_95"]
                    values.append(f"{row['mean_benefit_over_R']:.4f} [{lo:.4f}, {hi:.4f}]")
                lines.append(f"|{partition}|{alpha}|{risk}|" + "|".join(values) + "|")
    lines += ["", f"95% 区间使用 {facts['bootstrap_resamples']} 次独立世界配对重采样，分析种子 {facts['bootstrap_analysis_seed']}；每单元共同的世界重采样索引用于四策略和五个对比。n={facts['per_cell_n']}，未作多重比较校正，仅作探索性描述。逐世界有序对比向量见 paired.json。各 R 使用不同世界。", "",
              "|分组|alpha|K 无类型|K 有类型|K 格式 Oracle|理论溢价|", "|---|---:|---:|---:|---:|---|"]
    for r in result["coefficients"]:
        lines.append(f"|{r['partition']}|{r['alpha']}|{r['K_no_type']:.5f}|{r['K_with_type']:.5f}|{r['K_oracle']:.5f}|{r['premium_regime']}|")
    lines += ["", "上述 K 仅由配置中的真实参数在采样结束后计算，未输入学习器，属于浮点总体参考而非停止时间证书。[4],alpha=0 与 [4],alpha=3 保持分开；正理论溢价不保证有限 R 上优于基线。", "",
              "不能把四个收益相加为独立的任务/类型因果贡献，也不能把描述性交互解释为普遍机制定理。D-RRC-Type 使用完整风险尺度的类型目标，可能多买类型报告；负结果与计算代价应保留。零观测错误不能验证 exp(-R) 级别风险。", "",
              "图：artifacts/analysis/online_cost_ablation.{png,pdf}、total_cost_ablation.{png,pdf}、query_vs_cpu.{png,pdf}。图中全部使用旧浮点主批次；黑叉表示该单元有删失。认证终点审计及认证重放结果请见独立审计产物。"]
    (root / "ABLATION_REPORT.md").write_text("\n".join(lines) + "\n")

    diagnostics = result["diagnostics"]
    lines = ["# Phase 2d：共同估计器与有限 R 诊断", "",
             "本报告覆盖全部四策略、全部记录轨迹，包括删失路径。误差由原始 evaluator 审计记录读取；分析器未读取私有种子、标签文件或重建世界。末次误差与更新历史是描述性诊断，不构成可相加的因果成本解释。", "",
             "|分组|alpha|R|策略|全部/有估计|末次theta/z错误|末次p/q误差|历史p/q绝对误差|有theta/z错更新占比|强制占比|N/(KR)|",
             "|---|---:|---:|---|---:|---|---|---|---|---:|---:|"]
    for row in summary:
        rr = [r for r in diagnostics if all(r[key] == row[key] for key in ("partition", "alpha", "R", "policy"))]
        valid = [r for r in rr if r["estimates_available"]]
        mean = lambda key: "NA" if not valid else f"{np.mean([r[key] for r in valid]):.4f}"
        updates = sum(r["updates"] for r in rr)
        rates = [(sum(r["updates_with_" + key] for r in rr) / updates if updates else float("nan")) for key in ("theta_errors", "type_errors")]
        lines.append(f"|{row['partition']}|{row['alpha']}|{row['R']}|{row['policy']}|{len(rr)}/{len(valid)}|{mean('last_theta_errors')}/{mean('last_type_errors')}|{mean('last_p_error')}/{mean('last_q_error')}|{mean('history_mean_abs_p_error')}/{mean('history_mean_abs_q_error')}|{rates[0]:.4f}/{rates[1]:.4f}|{np.mean([r['forced_fraction'] for r in rr]):.4f}|{np.mean([r['restricted_online_over_KR'] for r in rr]):.4f}|")
    lines += ["", "theta/z 为错误坐标/组数量，p/q 末次误差为带符号估计减真值；历史绝对误差先在每条轨迹内平均再按世界等权平均，错误更新比例则按全部更新数计算。两种汇总单位不同，完整分母及每次更新误差均在 diagnostics.json 保留。缺少估计时明确计数，不把该轨迹作为已完成路径筛掉。", "",
              "无类型策略使用 K_no_type，有类型策略使用 K_with_type 作为总体参考；N/(KR) 仅描述截断成本相对系数的比例，不宣称 D-RRC 已达到某个停止时间定理。", "",
              f"规划 CPU 合计 {facts['planner_cpu_seconds']:.2f} 秒、规划墙钟 {facts['planner_seconds']:.2f} 秒；GLR CPU {facts['glr_cpu_seconds']:.2f} 秒、GLR 墙钟 {facts['glr_seconds']:.2f} 秒。计算时间不折算成在线查询成本。", "",
              "主批次仍是旧浮点停止规则。末次强制样本正确、数值 gap 较小或本批次零错误，均不构成无限时域可执行最优性与极小风险认证。认证原型的终点包围和在线重放由独立审计报告给出。"]
    (root / "ESTIMATION_DIAGNOSTICS.md").write_text("\n".join(lines) + "\n")
