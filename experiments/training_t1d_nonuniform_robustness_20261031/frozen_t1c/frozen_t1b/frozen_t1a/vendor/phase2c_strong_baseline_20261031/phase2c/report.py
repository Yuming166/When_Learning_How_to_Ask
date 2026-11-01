"""Generate reviewable reports and scientific plot artifacts from frozen data."""
import json
import numpy as np
from .bootstrap import ROOT
from .policy import POLICIES


def plots(summary,refs,diagnostics,out,cfg):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors=dict(zip(POLICIES,['#888888','#dd8613','#356cc2','#248744','#bb3030']))
    def save(fig,name):
        fig.tight_layout();fig.savefig(out/f'{name}.png',dpi=170);fig.savefig(out/f'{name}.pdf');plt.close(fig)
    for total in [False,True]:
        fig,axes=plt.subplots(2,2,figsize=(12,8))
        for pi,part in enumerate(cfg['partitions']):
            for ai,alpha in enumerate(cfg['alphas']):
                ax=axes[pi,ai];ref=next(r for r in refs if r['partition']==part and r['alpha']==alpha)
                for policy in POLICIES:
                    rr=sorted([r for r in summary if r['partition']==part and r['alpha']==alpha and r['policy']==policy],key=lambda x:x['R'])
                    shift=2*alpha if total else 0
                    ys=[r['mean_restricted_online_over_R']+shift for r in rr]
                    lo=[max(0,y-(r['bootstrap_mean_95'][0]+shift)) for r,y in zip(rr,ys)]
                    hi=[max(0,r['bootstrap_mean_95'][1]+shift-y) for r,y in zip(rr,ys)]
                    ax.errorbar(cfg['Rs'],ys,yerr=[lo,hi],fmt='o-',color=colors[policy],label=policy,markersize=4,capsize=2)
                    for r,y in zip(rr,ys):
                        if r['censored']:ax.plot(r['R'],y,'x',color='black',markersize=9)
                for key,label,style,color in [('K_task_type','K tasks+type',':','#222222'),('K_uniform_true_good_ray','Uniform-good ray','--','#356cc2'),('K_oracle','K format Oracle','--','#248744')]:
                    ax.axhline(ref[key]+(2*alpha if total else 0),ls=style,color=color,lw=1,label=label)
                ax.set_xscale('log',base=4);ax.set_xticks(cfg['Rs'],cfg['Rs']);ax.set_ylim(bottom=0)
                ax.set_xlabel('R = log(1/delta)');ax.set_ylabel('Restricted total acquisition / R' if total else 'Restricted online cost / R')
                ax.set_title(f'{part}, alpha={alpha}: {ref["premium_regime"]} premium');ax.grid(alpha=.15)
        axes[0,0].legend(fontsize=6);fig.suptitle('Development only; n=8 worlds/cell; exploratory world-bootstrap 95% intervals; x=censoring',fontsize=9)
        save(fig,'total_cost_comparison' if total else 'online_cost_comparison')
    fig,axes=plt.subplots(2,3,figsize=(13,7))
    specs=[('forced_fraction','Forced task fraction'),('final_beta_over_R','GLR boundary / R'),
           ('empirical_information_deficit_at_K','Population allocation deficit at K'),
           ('last_target_l1_to_one_true_optimizer','Last target L1 to one true optimizer'),
           ('tracking_l1_over_t','Tracking L1 / t'),('maximum_solver_relative_gap','Maximum float optimization gap')]
    for ax,(key,label) in zip(axes.flat,specs):
        for part in cfg['partitions']:
            for alpha in cfg['alphas']:
                ys=[np.mean([r[key] for r in diagnostics if r['partition']==part and r['alpha']==alpha and r['R']==R]) for R in cfg['Rs']]
                ax.plot(cfg['Rs'],ys,'o-',label=f'{part}, alpha={alpha}',markersize=4)
        ax.set_xscale('log',base=4);ax.set_xticks(cfg['Rs'],cfg['Rs']);ax.set_xlabel('R');ax.set_title(label,fontsize=9)
    axes[0,0].legend(fontsize=6);fig.suptitle('Aligned offline diagnostics; correlated readouts, not additive causal contributions',fontsize=9)
    save(fig,'cost_gap_diagnostics')


def write_reports(facts,summary,paired,refs,diagnostics,confirm,cfg):
    def mean(rr,key):return float(np.mean([r[key] for r in rr]))
    def row(part,alpha,R,policy):return next(r for r in summary if r['partition']==part and r['alpha']==alpha and r['R']==R and r['policy']==policy)
    lines=['# Phase 2c：强衰减探索基线比较','',
        '**本轮属于一次有界开发比较；没有独立确认样本。主比较为 Aligned 与 D-RRC。**','',
        f"完成{facts['independent_worlds']}个独立世界、{facts['trajectories']}条配对轨迹，每单元{facts['per_cell_n']}个世界。在线动作{facts['online_actions']:,}（任务{facts['costs']['task']:,}，付费类型{facts['costs']['type']:,}）；逐策略计费离线观测{facts['costs']['offline']:,}，独立世界实际离线参考{facts['unique_world_offline_observations']:,}。总获取成本{facts['total_acquisition']:,}。主批次墙钟{facts['wall_seconds']:.2f}秒，工作进程CPU合计{facts['trajectory_cpu_seconds']:.2f}秒，评估器CPU{facts['evaluator_cpu_seconds']:.2f}秒。模型调用、确认样本、主批次重试均为0。",'',
        'D-RRC与Aligned共用强制样本估计器、渐细网格、更新时刻、O(sqrt(t))探索、累计跟踪和GLR；唯一采样差异是更新时的目标分配。D-RRC将质量均分给各偏好当前估计的最佳形式，不调用联合KL优化器。两者拥有相同离线数据及可选类型询问，Aligned可主动购买类型信息而D-RRC分配0；所以本比较包含类型购买决策，不能称为固定购买信息后的纯任务分配消融。潜在响应流配对，不保证不同动作历史下的强制响应逐位相同。','',
        '|分组|alpha|理论溢价|R|Aligned N/R|D-RRC N/R|配对差 A-D /R [探索性95%区间]|A/D 删失|',
        '|---|---:|---|---:|---:|---:|---|---:|']
    for ref in refs:
        for R in cfg['Rs']:
            a=row(ref['partition'],ref['alpha'],R,'Aligned Tracking');b=row(ref['partition'],ref['alpha'],R,'D-RRC')
            p=next(x for x in paired if x['partition']==ref['partition'] and x['alpha']==ref['alpha'] and x['R']==R and x['baseline']=='D-RRC')
            lo,hi=p['paired_bootstrap_95']
            lines.append(f"|{ref['partition']}|{ref['alpha']}|{ref['premium_regime']}|{R}|{a['mean_restricted_online_over_R']:.4f}|{b['mean_restricted_online_over_R']:.4f}|{p['aligned_minus_baseline_over_R']:.4f} [{lo:.4f}, {hi:.4f}]|{a['censored']}/{b['censored']}|")
    lines+=['','全体世界均进入平均min(T,B)/R；若删失，无截断E[T]未被识别。区间按独立世界配对重采样，n=8且未作多重校正，仅描述开发不确定性。R之间使用不同世界，不构成单世界随R变化的实验。','',
        '|分组|alpha|K tasks+type|K Oracle|均匀真好形式射线系数|R=1024 相对D-RRC节省|',
        '|---|---:|---:|---:|---:|---:|']
    for ref in refs:
        p=next(x for x in paired if x['partition']==ref['partition'] and x['alpha']==ref['alpha'] and x['R']==1024 and x['baseline']=='D-RRC')
        lines.append(f"|{ref['partition']}|{ref['alpha']}|{ref['K_task_type']:.4f}|{ref['K_oracle']:.4f}|{ref['K_uniform_true_good_ray']:.4f}|{100*p['relative_restricted_cost_reduction']:.2f}%|")
    lines+=['','射线系数为离线总体信息参考，假定质量均分到真实好形式；不是额外Oracle策略运行，不是D-RRC期望停止时间定理。小组约束可能使“持续估计正确但始终只问好形式”的分配缺少识别其他类型假设的有效信息。存在正溢价并不逻辑蕴含Aligned一定胜出，必须逐单元看实测。只有[4],alpha=0为本参数下的零溢价对照；[4],alpha=3仍为正溢价。','',
        '|策略|完成/全部|删失|错误认证/全部|任务查询|类型查询|采样+规划+GLR墙钟秒|工作进程CPU秒|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for policy in POLICIES:
        rr=[r for r in summary if r['policy']==policy];n=sum(r['n'] for r in rr)
        lines.append(f"|{policy}|{sum(r['completed'] for r in rr)}/{n}|{sum(r['censored'] for r in rr)}|{sum(r['wrong_certificates'] for r in rr)}/{n}|{sum(r['costs']['task'] for r in rr)}|{sum(r['costs']['type'] for r in rr)}|{sum(r['trajectory_wall_seconds']*r['n'] for r in rr):.2f}|{sum(r['trajectory_cpu_seconds']*r['n'] for r in rr):.2f}|")
    lines+=['','所有五个策略的16单元、区间、配对差、成本及CPU数据见artifacts/analysis/{summary,paired,confidence_curves}.json；原始逐轨迹、检查点及完整更新历史见artifacts/run。Format-Only Oracle只知道真实组形式，不知道符号或p/q。旧RRC固定探索比例，保留作次要参照。零错误不能验证exp(-R)的极小风险；浮点GLR不具有严格区间证书。','',
        '图：artifacts/analysis/online_cost_comparison.{png,pdf}与total_cost_comparison.{png,pdf}。所有结论仅适用于受控Bernoulli通道；自然Qwen/人类效果未建立。审计为分离的同模型家族代理审阅，不是外部数学专家或机器形式证明。']
    (ROOT/'BASELINE_COMPARISON.md').write_text('\n'.join(lines)+'\n')
    lines=['# Phase 2c：有限R成本与理论K的差距','',
        '**诊断区分分配的信息不足、估计误差、停止阈值及跟踪误差，但不将它们相加为因果贡献。** 每条Aligned轨迹都有以下数据，不按完成状态筛选。真实参数仅在主实验完成后的离线分析器使用，不经RPC回传策略。','',
        '|分组|alpha|R|N/(KR)-1|强制比例|末次theta/z错误|beta/R|实际分配在K处信息缺口|末次目标信息缺口|跟踪L1/t|',
        '|---|---:|---:|---:|---:|---|---:|---:|---:|---:|']
    for ref in refs:
        for R in cfg['Rs']:
            rr=[r for r in diagnostics if r['partition']==ref['partition'] and r['alpha']==ref['alpha'] and r['R']==R]
            lines.append(f"|{ref['partition']}|{ref['alpha']}|{R}|{mean(rr,'restricted_ratio_over_K')-1:.4f}|{mean(rr,'forced_fraction'):.4f}|{mean(rr,'last_theta_errors'):.3f}/{mean(rr,'last_type_errors'):.3f}|{mean(rr,'final_beta_over_R'):.4f}|{mean(rr,'empirical_information_deficit_at_K'):.4f}|{mean(rr,'last_target_information_deficit_at_K'):.4f}|{mean(rr,'tracking_l1_over_t'):.4f}|")
    lines+=['','计算方式：对归一化分配w，将在线计数设为K*w，离线计数设为alpha，求全部错误符号/类型及连续候选p/q的最小总体KL I(alpha,Kw)。信息缺口=max(0,1-I)。该指标避免把非唯一最优分配间的欧氏距离误判为信息损失。另保留与一个指定真实最优解的L1距离；它不是到最优解集合的距离。实际计数的总体最小KL/R与GLR/R之差是随机观测及profile效应的描述值，不是可相加的“随机成本”。','',
        '|分组|alpha|R=1024 p误差均值|q误差均值|末次目标至一个真最优解L1|实际分配L1|最大数值相对gap|最小请求容差|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for ref in refs:
        rr=[r for r in diagnostics if r['partition']==ref['partition'] and r['alpha']==ref['alpha'] and r['R']==1024]
        lines.append(f"|{ref['partition']}|{ref['alpha']}|{mean(rr,'last_p_error'):.4f}|{mean(rr,'last_q_error'):.4f}|{mean(rr,'last_target_l1_to_one_true_optimizer'):.4f}|{mean(rr,'empirical_allocation_l1_to_one_true_optimizer'):.4f}|{max(r['maximum_solver_relative_gap'] for r in rr):.3g}|{min(r['minimum_requested_tolerance'] for r in rr):.3g}|")
    lines+=['',f"主批次规划墙钟{facts['planner_seconds']:.2f}秒、规划CPU{facts['planner_cpu_seconds']:.2f}秒、GLR墙钟{facts['glr_seconds']:.2f}秒、GLR CPU{facts['glr_cpu_seconds']:.2f}秒；这两项不与在线查询成本混合。所有Aligned原始误差、每次更新、强制计数、累计分配偏差、求解上下界均保留。",'',
        '固定数值下限仍在：LP primal/dual1e-9、信息径向pad1e-9、切面13位去重、接受信息残差1e-7及相对gap下限。请求容差下降不蕴含实际无限期误差消失。有限批次未触发某个下限，也不能证明它可忽略于无限时域。','',
        '这些观察能识别哪些机制在有限R仍然活跃；要分配各机制的因果贡献，需要另行冻结干预/消融实验，本轮没有执行。完整逐轨迹诊断为artifacts/analysis/diagnostics.json，图为cost_gap_diagnostics.{png,pdf}。']
    (ROOT/'COST_GAP_DIAGNOSTICS.md').write_text('\n'.join(lines)+'\n')
    confirmation_report(confirm,facts,cfg)


def confirmation_report(plan,facts,cfg):
    c=plan['design_choices'];lines=['# Independent confirmation — frozen protocol, NOT EXECUTED','',
        '**Status: FROZEN_NOT_EXECUTED. No confirmation seed or world has been consumed.** This is a pre-confirmation registration informed by development variability, not a retrospective claim of preregistered development. The final artifact receipt binds this document and source. Execution requires a new explicit decision; no launcher is provided here.','',
        '## Fixed scientific contrast and estimand','',
        'R=1024, d=4, p=.85, q=.60, eta=.05, known type accuracy .8, alpha=0. Positive-premium partition[1,3]; zero-premium partition[4]. These two configurations were fixed in PHASE2C_PROTOCOL.md before this development batch. Two policies only: frozen Aligned Tracking and D-RRC, same observation interface, paid-action availability, GLR/check schedule and cost accounting. No tuning or additional strategies after confirmation starts. The positive contrast includes Aligned choosing paid type actions; claims must preserve that scope.','',
        'An independent world is one statistical unit. Within world i, define D_i=(min(T_Aligned,24576)-min(T_D-RRC,24576))/1024. Lower is better. Both potential stopping streams share private theta/z, calibration and per-action potential response streams; independent worlds have disjoint indices and a fresh evaluator-only master seed. Indices and seed must be outside every development namespace. Freeze and verify all code/protocol hashes before seed generation; the future seed is absent in this phase.','',
        'This is a restricted-cost estimand even if no censoring occurs. Retain capped values at24576; never drop a censored or incorrect path. No extrapolation to E[T], no automatic cap extension. Report per-policy completion and any wrong certificate with full denominators. A missing/failed infrastructure trajectory is not ordinary cap censoring: preserve it, mark the confirmation incomplete, and do not silently replace or rerun it.','',
        '## Exact planned sample sizes','',
        '|Regime|Development pairs|Paired SD(D)|Inflated planning SD|Target effect / equivalence margin|Exact independent worlds|Approx. planning power|',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in plan['configurations']:
        power='not attainable under cap' if r['approximate_planning_power'] is None else f"{r['approximate_planning_power']:.4f}"
        lines.append(f"|{r['regime']}|{r['development_pairs']}|{r['development_paired_sd']:.5f}|{r['inflated_planning_sd']:.5f}|{r['prespecified_effect_or_margin']:.2f}|{r['exact_n_worlds']}|{power}|")
    lines+=['','The planning rule was fixed before development outcomes: inflate observed paired SD by1.5; choose the smallest integer n in[24,512] reaching80% approximate power. Positive planning uses a one-sided noncentral-t model for a prespecified mean difference-0.5. Zero planning uses centered t-model approximation for +/-0.25 equivalence. These effect thresholds were not chosen from the observed mean difference. Small development n and possible heavy tails limit this power estimate; the minimum24 is retained even for observed zero SD. An observed identical path does not establish zero variance over all worlds. If no n passes512, planning is insufficient and confirmation must be revised before any seed. No optional stopping or interim efficacy checks.','',
        f"Planned online hard ceiling across the two policies/configurations is {plan['global_online_action_ceiling']} actions; alpha=0 implies no offline observations. A separate execution freeze must give a wall allowance and verify resources without changing the estimand, n or cap. That allowance is not permission to execute now.",'',
        '## Confidence intervals, multiplicity, and decisions','',
        'Analyze each configuration separately. Positive claim H0:E[D]>=0 uses a one-sided97.5% paired t upper confidence bound U_pos, allocating family error.025. Declare numerical cost superiority only if U_pos<0. Report paired mean/SD, two-sided95% interval, and relative restricted-cost reduction as secondary. The prespecified0.5 is for power planning, not an additional unregistered success threshold.','',
        'Zero control uses TOST with per-test alpha.025: the two-sided95% paired t interval[L_zero,U_zero] must lie strictly within[-.25,.25] to declare equivalence. These two claims have nominal Bonferroni family error<=.05 under the stated t-interval assumptions. Intervals rely on independent worlds and approximate normality of sample means; they are not distribution-free finite-sample coverage certificates. Also report a fixed20000 world-paired percentile bootstrap sensitivity interval using an analysis-only fixed seed763299; it does not replace the prespecified t decisions. Never resample individual responses or count policies as independent worlds.','',
        'Overall scientific success requires positive superiority AND zero equivalence AND every planned trajectory recorded AND zero observed wrong certificates. If a positive lower one-sided97.5% bound is>=0, classify the efficacy hypothesis as not supported / unfavorable; if the zero-control interval lies completely outside the equivalence band, classify the zero-control claim as unfavorable. Other crossed or wide intervals are inconclusive. Any wrong certificate triggers failure of the observed correctness guard and a numerical audit; this is not a statistical test of exp(-1024) correctness. More censoring in Aligned cannot be concealed by its restricted cost: if either primary policy has >5% cap censoring in either configuration, overall expected-stopping interpretation is inconclusive even if the restricted metric passes. Infrastructure failure makes the run incomplete, not a negative efficacy estimate.','',
        '## Secondary outcomes and claim limits','',
        'Report N/R, min(T,B)/R, total acquisition/R, task/type counts, per-policy completion, wrong certificates/all worlds, wall and CPU time, forced fractions, estimator errors, actual solver gaps and beta/R. No multiplicity-adjusted claims from secondary outcomes. No pooling development with confirmation. No extra R, alpha, model, task or baseline selected after seeing confirmation. Preserve all failures and private reproduction records with public checksums.','',
        'The proof audit licenses an exact model-level lower bound and conditional ideal achievability. The current float64 sampler has non-certified numerical optimizers and GLR; confirmation can evaluate this frozen numerical policy, but cannot certify its exact risk bound or asymptotic optimality. Positive synthetic cost results do not establish natural-LLM reliability sharing, human effects or universal baseline superiority.','',
        f"Source development batch: {facts['independent_worlds']} worlds / {facts['trajectories']} trajectories. These are excluded from confirmation. Protocol provenance: PHASE2C_PROTOCOL.md, config.json, artifacts/analysis/confirmation_plan.json, FINAL_RECEIPT.json. No new confirmatory seeds used."]
    (ROOT/'CONFIRMATORY_PROTOCOL.md').write_text('\n'.join(lines)+'\n')
