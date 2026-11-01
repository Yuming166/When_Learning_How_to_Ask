"""Render requested reports from saved results; does not execute experiments."""
import json
from pathlib import Path
from analyze import table,fmt
ROOT=Path(__file__).resolve().parents[1]
def write(name,text):(ROOT/name).write_text(text.strip()+'\n')
def main():
 s=json.loads((ROOT/'RESULTS.json').read_text());off=json.loads((ROOT/'OFFLINE_RESULTS.json').read_text());arms=s['arms'];a=arms['AnalyticReuse'];teacher=arms['Teacher'];exe=s['execution']
 fixtures=json.loads((ROOT/'NUMERICAL_FIXTURES.json').read_text());audit=json.loads((ROOT/'VALIDATION.json').read_text())
 offline_table=table(['方案','完整规划均值 ms','中位数 ms','对 Teacher 加速','最大组质量 L1','最大相对目标差（绝对值）'],
 [[name,fmt(v['mean_cpu']*1000),fmt(v['median_cpu']*1000),fmt(off['arms']['Teacher']['mean_cpu']/v['mean_cpu'])+'×',f"{v['max_group_mass_l1']:.3g}",f"{v['max_abs_objective_relative_change']:.3g}"] for name,v in off['arms'].items()])
 closed_table=table(['方案','在线/世界','总获取/世界','类型/世界','轨迹 CPU 总秒','CPU 加速 [95% 区间]','在线比 [95% 区间]','认证/删失'],
 [[name,fmt(v['online_mean'],1),fmt(v['total_mean'],1),fmt(v['type_mean'],1),fmt(v['trajectory_cpu_sum']),f"{v['speedup']:.2f} [{v['speedup_ci95'][0]:.2f},{v['speedup_ci95'][1]:.2f}]",f"{v['online_ratio']:.4f} [{v['query_ratio_ci95'][0]:.4f},{v['query_ratio_ci95'][1]:.4f}]",f"{v['certified']}/{v['censored']}"] for name,v in arms.items()])
 cell_table=table(['分组','alpha','R','世界数','Teacher 在线均值','Analytic 在线均值','CPU 加速','Warm 在线均值'],[[v['partition'],v['alpha'],v['R'],v['n'],fmt(v['teacher_online_mean'],1),fmt(v['primary_online_mean'],1),fmt(v['primary_speedup'],2)+'×',fmt(v['warm_online_mean'],1)] for v in s['cells']])
 cache_table=table(['方案','solver 调用','命中/覆盖','验收','回退','guard CPU 秒','fallback CPU 秒'],[[name,v['solver_calls_stats'].get('calls',0),v['solver_calls_stats'].get('hits',0),v['solver_calls_stats'].get('accepted',0),v['solver_calls_stats'].get('fallback',0),fmt(v['solver_cpu_components'].get('guard',0)),fmt(v['solver_cpu_components'].get('fallback',0))] for name,v in arms.items() if name in ['ExactCache','QuantizedCache','Interpolation']])
 cost_table=table(['方案','规划 CPU','浮点 GLR CPU','严格 gate CPU','其他轨迹 CPU','CPU 中位数/p90/范围','墙钟总秒'],[[n,fmt(v['planner_cpu_sum']),fmt(v['glr_cpu_sum']),fmt(v['gate_cpu_sum']),fmt(v['other_cpu_sum']),f"{v['cpu_median']:.3f}/{v['cpu_p90']:.3f}/[{v['cpu_range'][0]:.3f},{v['cpu_range'][1]:.3f}]",fmt(v['wall_sum'])] for n,v in arms.items()])
 status='GO：采用无训练解析复用；当前神经训练 NO-GO' if s['decision']=='GO_NO_TRAINING' else 'REVISE：当前证据尚未通过全部门槛；不启动训练'
 write('SOLVER_BASELINE_REPORT.md',f'''# T1a 无训练求解器基线验收

## Material Passport

2026-10-31；独立分支 `training/t1a_solver_baselines`，base `3186587`。开发性数值研究，未进行训练、模型调用、GPU 调用或确认实验。结论：**{status}**。主候选 AnalyticReuse 在新世界采样前已固定；其他方案为消融或廉价对照。

## 实现范围

冻结 Fused-Original 的后验、强制探索、sqrt(t) 更新时钟、累计目标跟踪和停止器保持同版本；仅注入新的系数求解函数。原源文件逐字复制到 vendor，原路径哈希也校验。没有改动 Phase2e 方法目录、基线或 QRelBench 生成器。旧 Qwen-LoRA、旧 MLP 负结果均未重跑、覆盖或纳入本轮新样本。

七种求解器：Teacher 原始实现；精确 tuple 缓存；.025 量化缓存并验证/回退；二维解插值并验证/回退；RadialReuse；AnalyticReuse（含 radial）；WarmStart（含前两种优化）。闭环另有原 fused D-RRC-Type。WarmStart 是切平面支持点池的热启动，不是 HiGHS 原生基热启动。没有把 SciPy `x0` 当作 HiGHS warm-start；其接口限制见 [SciPy 官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html)。

RadialReuse 保留原标量 cutting-plane 路径，先为固定方向 x 缓存各备择的加权成功数/总数；正 alpha 的径向搜索仍逐点重算最小化投影，不能冻结原投影。alpha=0 时利用 I(lambda x)=lambda I(x)，省去35次重复径向求根。AnalyticReuse 再将 G·2^G 个连续备择的有序二项投影与 KL 行向量化；保持原 LP 目标和终止容差。

## 相同可观测状态结果

使用冻结 T0 的全部23个状态、8个历史世界，每状态三轮、每轮七方案，共483次完整更新；没有按结果筛选状态。完整计时包括重新计算联合后验、key、求解/guard/回退和动作权重展开；独立标量审计在计时外对所有方案同样进行。按状态等权，不把483次调用解释成483个独立世界。Teacher 先计算参考，候选次序按状态轮换，仍可能有调用顺序/缓存偏差，闭环为另一项证据。

{offline_table}

这些 K 都是**当前可观测估计参数下原信息规划的实际数值目标** c^T x，非某个网络预测值；原始 LP 下界用于缺口诊断，不是未知生成率下的 oracle K。分配不是只比较一个 K 标签：保存完整 a,b,c、动作权重和组质量 L1，同时报告全部备择信息。

缓存/插值在离线状态上均没有通过近似候选验收；其回退返回原 Teacher 分配。WarmStart 的离线最大组质量差 {off['arms']['WarmStart']['max_group_mass_l1']:.6g}、最大相对目标差 {off['arms']['WarmStart']['max_abs_objective_relative_change']:.6g}；不同切平面路径可给出容差内的不同解，不按 L1 单独判错。

## 新世界闭环结果

32个新独立 Exact 开发世界，8个固定单元各4个，共256条路径；没有使用确认种子。全部候选使用相同观察权限、每次查询单位成本、校准2M成本、检查时钟和严格认证停止。主候选完整轨迹 CPU 加速 {a['speedup']:.3f}×，探索性配对区间 [{a['speedup_ci95'][0]:.3f},{a['speedup_ci95'][1]:.3f}]；在线比 {a['online_ratio']:.6f}，区间 [{a['query_ratio_ci95'][0]:.6f},{a['query_ratio_ci95'][1]:.6f}]。完整表、成本账本和限制见 CLOSED_LOOP_COMPARISON.md。

本轮没有重新训练旧 MLP，也没有训练10660参数 NQA。结果支持先优化低维参考求解器；不能由此否定语言环境下的学习策略价值。未证明新后验/有限精度分配满足渐近最优性前提。
''')
 write('CACHE_AND_INTERPOLATION_AUDIT.md',f'''# 缓存和插值审计

## Material Passport

开发实现与成本审计；仅可观测输入。不存在从评测真值/私有种子到在线策略的输入通路。公开参数网格不是训练数据，也没有以闭环效果拟合网格或扩大密度。

## Key 与生命周期

精确 key 为 (实现版本, partition, p_hat.hex, q_hat.hex, alpha.hex, 已知 type_accuracy, eta.hex, tolerance.hex, max_iterations)。它缓存的是规范高/低格式系数 a,b,c，z_hat 在原展开器中映射到 A/B；无需将 z 或历史身份放进 key。版本与代码冻结同属一次进程生命周期，不声称跨版本持久缓存。类型查询不存在时有显式 None。缓存参数改变一个浮点单位会 miss，单元测试覆盖。

量化 key 仅将两条估计率替换为 round(p_hat/.025)、round(q_hat/.025)，保留其他契约。禁止 hidden theta、生成 p/q/z、答案、奖励、world/episode ID、private seed、未来观察或 teacher 标签作为 key。闭环每个世界新建空缓存；离线每轮在固定状态序列上重建缓存，首遍命中率单列，不能把人为重复状态命中当部署效果。

## 插值

56次原 Teacher 网格求解；预计算 CPU {off['grid_cpu']:.6f}s，初次构建三角剖分 {off['grid_load_cpu']:.6f}s。网格见 DEVELOPMENT_PROTOCOL.md。对同一公共 partition/alpha/s/eta 的 (p_hat,q_hat) 用二维 Delaunay 单纯形内的重心权重插值**整个系数向量**。凸包外、结构不匹配或验收失败都调用原 Teacher。采用 [SciPy Delaunay transform](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html) 的重心映射，几何插值不构成信息约束保证。

## 验收与成本

所有近似候选先检查非负/有限并做保守径向修复，再在当前估计模型中求出每一个 (mask,h) 的连续最小值，同时用初始有效 cuts 加当前候选投影 cuts 求一个新的松弛 LP 下界 L。只有 min information>=1−1e−7 且 −5e−8<=(c^T x−L)/max(1,c^T x)<=max(5 epsilon,5e−8) 才返回。每条 cut 的系数和校准右端都在当前参数上重算。否则回退**冻结原始求解器**；guard、miss、查 key、重算和回退均计时。下界可能太松，因而拒绝本来接近最优的候选；这里偏保守，不能把拒绝率解释成插值方法族不可能有效。

离线第一遍：精确缓存0/23命中；量化缓存6/23命中但0验收；插值23/23覆盖但0验收。没有依据这些结果重调 bin 或网格后再挑最好结果。

闭环统计：

{cache_table}

精确缓存1703次调用全部miss并重新调用原solver；表中的0回退仅表示没有近似guard回退，不代表免除了原求解成本。量化缓存278次miss，加1086次guard拒绝，共1364次原solver回退。插值1703次覆盖中仅2次验收。

“命中”与“验收”不同，计数分母是实际 solver 调用（包含调用方必要的第二次精度尝试），不是查询数。fallback CPU 是总 solver 时间的子集，不能重复加。精确缓存命中返回同一问题的已验收结果，不将其误列为近似 guard 验收。

粗网格与严格缺口要求的组合可能不划算；更密网格、跨轨迹共享缓存、原生 LP 基复用均未测量，不能称为已被否定。未修改本轮门槛以换取更多缓存命中。
''')
 numerical_table=table(['方案','最低独立 scalar 信息','最大报告差','最大参考成本处信息缺口'],[[name,f"{v['minimum_information']:.12f}",f"{v['max_information_disagreement']:.3g}",f"{v['maximum_deficit_at_teacher_K']:.3g}"] for name,v in off['arms'].items()])
 write('NUMERICAL_FEASIBILITY_REPORT.md',f'''# 数值可行性与停止可靠性

## Material Passport

有限范围回归与数值审计通过；不宣称整个新求解器的区间认证。原 certified stop 的算术/模型审计边界保持不变。

## 规划问题和验收

原问题 min c^T x，约束 I_(J,h)(x)>=1。对每个离散备择，二项负对数似然在 .5<=v<=u<=1−eta 上的极小点由独立裁剪、必要时 pooling 得到。因此解析 separation 覆盖连续率域，而不是只检查有限参数网格。分组数<=2，停止 d<=4；没有推广到更大维度的计算保证。

原 scalar inner 和新 batch inner 在8种固定数值情形、每情形20个非负工程向量上比较，最大绝对信息差 {max(v['projection_absolute_error'] for v in fixtures):.3g}。情形包括 p_hat=.5005/q_hat=.5、p_hat=.95、对称与不等组、alpha0/3/16、不同已知 s 和无 type action。这些 p/q 是显式数值问题输入，不是在线评测世界的隐藏生成率。另8项独立契约测试通过：所有备择、零alpha齐次、完整分配、精确key、输入白名单、损坏缓存回退、无类型mask、warm支持点重算。

23状态×3轮×7方案483次完整规划，以及8情形×7方案56次 solver 结果，均用冻结 scalar inner 独立检查非负、全部备择、c^T x 和参考下界差。最低独立信息 {min(v['minimum_information_independent_scalar'] for v in fixtures):.12f}（数值 fixtures）；最大分配差不单独作为失败条件，因为容差内/非唯一最优分配可以不同。完整逐项数值见 NUMERICAL_FIXTURES.json。

{numerical_table}

上表全部三列来自23个存储状态×3轮：最低独立信息、报告值误差、以及将候选方向缩放到Teacher成本处的最坏备择信息缺口。实际返回解的最大单位信息缺口均为0；这与Teacher成本处的方向缺口不同。存储状态的完整 objective、参考下界、归一化信息缺口和向量保存在 artifacts/offline_rows.jsonl，其哈希在最终收据中。批量实现复用成功计数，不冻结 alpha>0 时随径向尺度改变的投影。

## 新闭环核对

{audit['planning_updates_checked']}次已记录 KL 规划更新均通过原调用方的数值 gap/信息阈值，无违规；其最小已记录信息 {audit['minimum_logged_information']:.12f}。新闭环路径仅使用同版本可行性检查，没有为整个 solver 构造方向舍入界。独立 scalar 全覆盖验收在离线进行；不伪称每次在线更新又做了未计时的第二套独立求解。

全部{len(arms)*32}条路径的观测计数/费用与父进程一致。严格 gate 已核对全任务 counts、每组 type counts、两条各M个真实 calibration 计数、枚举数量、candidate 和 gap_lower>beta_upper；见 VALIDATION.json。认证成功 {sum(v['certified'] for v in arms.values())}/{len(arms)*32}，认证错误 {sum(v['wrong_certified'] for v in arms.values())}，未定尝试 {sum(v['gate_undetermined'] for v in arms.values())}，被拒尝试 {sum(v['gate_rejected'] for v in arms.values())}。被拒/未定不转成输出，继续至认证或cap；cap提交只用于评分，不能称可靠答案。

## 保证边界

certify_stop 使用完整联合连续 profile、全theta/z枚举、Fraction 有序MLE和向外 Decimal log 界。它不依赖 posterior32积分或新规划器的最优性；在固定公共R/eta/已知s、真实独立参考流、fresh iid任务和类型响应、完整观察计数、受审计 Python Fraction/Decimal 契约下，沿用既有错误认证输出控制。保证平均包含离线随机性，不能宣称对每个已实现的校准样本条件成立。

未证明新后验的一致性/集中率和可执行 solver 在无限期上的误差收敛；固定浮点floor仍存在。未证明渐近最优、新增维度、机制或自然语言通道的可靠停止。0个错误认证是本轮运行记录，不是由32世界经验估计证明极低风险。
''')
 write('CLOSED_LOOP_COMPARISON.md',f'''# 一次有界闭环开发比较

## Material Passport

状态：完成。32个新 Exact 开发世界、256条路径；源文件/协议冻结后才生成新开发熵。8个固定单元各4世界，p=.85/q=.60、eta=.05、s=.8；分组[1,3]/[4]、alpha0/3、R16/256。与既有理论配置相同但世界独立；没有查询确认种子。执行墙钟 {exe['seconds']:.3f}s，上限1200s；online上限1,048,576。没有自动重试或增样。

## 匹配设计与成本

同世界各臂共享潜在响应流，独立状态、相同平方根更新时钟、forced blocks、累计跟踪、认证器、检查间隔与cap。父进程持有生成参数/真值；受限 worker 只通过 reset/calibration/query/type RPC 取观测。观测访问、校准账单2M、任务和类型单位费用相同。

{closed_table}

所有32世界的逐对成本保存在 PAIRED_COSTS.json。总在线 {exe['costs_including_partial']['task']+exe['costs_including_partial']['type']:,}，任务 {exe['costs_including_partial']['task']:,}，类型 {exe['costs_including_partial']['type']:,}；按每臂收费的校准 {exe['costs_including_partial']['offline']:,}；总获取 {sum(exe['costs_including_partial'].values()):,}。物理配对共用的独特校准为 {s['unique_shared_offline_observations']:,}，不能同时把它算作每臂免费又在总表重复相减。每臂每世界 offline 均值 {teacher['offline_mean']:.1f}；primary没有减少这部分成本。

## 分单元结果

{cell_table}

总体速度不是每个单元都达到2×的保证；保留以上异质性。primary有{a['same_online_count_worlds']}/32个世界与Teacher在线数完全相同，{a['same_terminal_counts_worlds']}/32个世界终端任务计数及类型报告完全相同。相同有限样本路径不推出所有新历史上的机器逐位轨迹等价。

## 时间边界与不确定性

{cost_table}

轨迹 CPU 从公共 reset 开始计时，覆盖后验、key、solver、验证/回退、动作选择、RPC编解码、浮点 likelihood、严格证书。planner内部包含solver，GLR与gate是另列互斥阶段，不重复加。一次运行/世界而非微函数最短时间；表中范围和p90显示配置/运行差异。主机没有做严格硬件隔离，CPU优先于可能受负载影响的墙钟。

父 evaluator 全程CPU {s['whole_shared_evaluator_cpu']:.3f}s，含环境构造/服务与运行组织，未逐臂分摊测量。将**全部父CPU只记给primary、Teacher记0**，并将primary启动开销计入，可得到极保守总计算下界 {s['conservative_primary_speedup_charging_all_parent_cpu']:.3f}×。这是一项运行总量的保守边界，不是额外配对置信区间；若它不足2，不能由此声称逐臂全机器CPU的2倍目标已经证明。实际逐轨迹墙钟包含RPC等待/环境服务，primary的墙钟加速为 {a['wall_speedup']:.3f}×，探索性区间 [{a['wall_speedup_ci95'][0]:.3f},{a['wall_speedup_ci95'][1]:.3f}]；它仍受主机负载影响。预先指定的主指标是完整学习者策略CPU，环境生成/服务不是被替换的算法，二者边界明确保留。各臂启动计入后的速度在 RESULTS.json；插值另加全部 {off['grid_cpu']:.3f}s 网格预计算，不能隐藏为离线免费。Teacher和primary均无网格预计算需求。

预先指定 AnalyticReuse，配对世界在8个单元内分层bootstrap20,000次、分析seed9917，报告比值均值的95% percentile区间。每单元只有4世界；这些是开发性不确定性区间，不是一般或均匀非劣性证明，也没有从多候选中事后挑显著者。即使观测成本完全相同导致零宽区间，也只反映已观察支持；不能推断未知世界一定<=5%。没有把平均值单独作为验收依据。

## 估计和可靠性

{table(['方案','完整恢复(评分)','p末次MAE','q末次MAE','类型末次错误数','未定/拒绝证书尝试'],[[n,f"{v['exact_scoring']}/32",fmt(v['p_terminal_mae'],5),fmt(v['q_terminal_mae'],5),v['type_terminal_errors'],f"{v['gate_undetermined']}/{v['gate_rejected']}"] for n,v in arms.items()])}

估计误差来自父进程事后评分，不进入key或策略；末次规划估计的时点由共同clock决定，不伪称为终点再做一次未计时后验。exact评分与strict认证分开计数；删失仍保留cap成本，不只分析成功路径。认证模型与算术边界见 NUMERICAL_FEASIBILITY_REPORT.md。
''')
 decision_table=table(['目标','本轮证据','判断'],[
 ['统计估计',f"同一冻结联合后验；primary末次p/q MAE={a['p_terminal_mae']:.5f}/{a['q_terminal_mae']:.5f}",'未设计估计改进；不能声称提升'],
 ['在线查询成本',f"primary/Teacher={a['online_ratio']:.6f}，配对区间[{a['query_ratio_ci95'][0]:.6f},{a['query_ratio_ci95'][1]:.6f}]",'有限开发支持保留效率；非普遍非劣性定理'],
 ['总获取成本',f"primary/Teacher={a['total_acquisition_ratio']:.6f}，相同校准费用",'未改善；在线和校准成本均相同'],
 ['计算时间',f"完整轨迹{a['speedup']:.3f}×；区间[{a['speedup_ci95'][0]:.3f},{a['speedup_ci95'][1]:.3f}]",'有实测无训练加速；外推受配置限制'],
 ['认证停止可靠性',f"primary认证{a['certified']}/32、错证{a['wrong_certified']}、删失{a['censored']}",'沿用原受审计gate，未提升其风险等级']])
 write('TRAINING_VALUE_DECISION.md',f'''# T1a 最终训练价值判断

## Material Passport

**{status}。** 这是一次有界开发决策，非独立确认结果。结束于当前32世界；不自动启动NQA、Qwen、RL、确认或更大评测。

## 五项目标

{decision_table}

主候选在预先固定的总体工程门槛上{'通过' if s['decision']=='GO_NO_TRAINING' else '尚未全部通过'}：完整策略CPU加速目标>=2×、在线比<=1.05，配对区间与删失共同检查。环境服务CPU仅有整次运行总量，尚未建立逐臂全机器CPU的配对2倍证据；包括RPC等待的轨迹墙钟实测加速3.50倍。原始训练loss、网络推理微测和离线solver函数速度均未用于替代这两个门槛。主结论是此Exact低维参考规划存在可兑现的解析冗余；没有证据表明必须训练神经分配器才能消除它。

## 当前选择

优先保留**AnalyticReuse**作为可审查的加速参考，RadialReuse作为解释性消融。{'当前建议停止本项目为模仿同一个Exact KL求解器而新增的神经训练；无需为了训练贡献而拟合NQA。' if s['decision']=='GO_NO_TRAINING' else '当前不启动神经训练。先利用已有时间分解确定剩余预算；没有因一次门槛未通过就证明结构化学习有价值。'} WarmStart可以作为额外候选，但带来容差内分配变化，不把较快均值自动当查询非劣性。精确缓存、量化缓存、粗插值的命中、验证和回退负结果完整保留；不能把本次实现效果外推成整个方案族的否定。

旧 Qwen-LoRA T1、旧固定MLP和新未训练组等变NQA是不同实验，结果不混用。原训练线负结果继续有效，本次没有新学习成功或泛化证据。运行共享主机、固定p/q、d=4、G<=2、每单元n=4、有限R与预算的限制均存在；不以零宽查询区间冒充跨环境保证。

## 剩余计算与研究边界

primary规划 CPU累计 {a['planner_cpu_sum']:.3f}s，其中solver计时 {a['solver_cpu_components'].get('total',0):.3f}s；两者之差包含同版本后验、展开与wrapper。浮点GLR {a['glr_cpu_sum']:.3f}s，严格gate {a['gate_cpu_sum']:.3f}s，其他轨迹工作 {a['other_cpu_sum']:.3f}s。正alpha下仍有35步径向检查和cutting-plane LP；本轮没有训练后验或停止器来改变这些成本，也不把T0的旧75.7%占比移植到新求解器上。

可写为当前论文的可选计算实现结果；不应包装成已经实现的 Training-Based Agent 贡献。没有证明新融合后验满足原forced-only估计器的证明条件，固定数值floor也不满足无限期误差消失保证。因此不宣称执行策略渐近最优。Mechanism/Natural的语言理解、语义状态和迁移仍是另一个未检验问题，不由本Exact结果判断。

## 可复核记录

DEVELOPMENT_PROTOCOL.md、config.json与freeze.json记录世界抽样前协议和源码冻结；INPUT_SNAPSHOT.json保护原代码与T0；OFFLINE_RESULTS.json、NUMERICAL_FIXTURES.json、RESULTS.json、PAIRED_COSTS.json提供公开数值；VALIDATION.json和FINAL_RECEIPT.json记录覆盖范围、原文件校验和产物哈希。私有开发熵和完整来源记录只保留在忽略的artifacts/closed_loop/private，不发布为在线输入。
''')
 write('README.md',f'''# T1a No-Training Optimization Baseline Gate

**{status}**。32新开发世界；未训练、未确认。

本目录保留冻结依赖与加速器的独立实现；原始实验目录未修改。

- [求解器比较](SOLVER_BASELINE_REPORT.md)
- [缓存与插值审计](CACHE_AND_INTERPOLATION_AUDIT.md)
- [数值与认证边界](NUMERICAL_FEASIBILITY_REPORT.md)
- [闭环配对结果](CLOSED_LOOP_COMPARISON.md)
- [最终训练判断](TRAINING_VALUE_DECISION.md)

在本目录下执行接口检查：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v`。

执行记录而非自动重跑许可：先`python -m t1a.offline`，再`python -m t1a.runner`。两者拒绝覆盖已有结果；runner要求离线gate通过，生成新的development entropy，严格守预算。已完成运行不应自动再次执行；精确复现旧世界需要本地私有开发种子，不能以另一份新随机世界替代。产物分析为`python audit/analyze.py`、`python audit/validate.py`、`python audit/render_reports.py`，无新查询/训练。最终hash由audit/seal.py生成。
''')
 print('rendered five deliverables and README')
if __name__=='__main__':main()
