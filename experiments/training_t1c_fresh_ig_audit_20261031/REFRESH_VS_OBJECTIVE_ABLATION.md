# T1c — Refresh versus objective ablation

## Evidence scope

本报告来自一个有界、独立的新development批次。没有确认世界、Qwen调用、神经训练、RL更新、PPO或Actor–Critic；没有改写T1a/T1b/T2历史结果、基准生成器或Natural。预先规定B32为主预算，B16/B64为结构/辅助预算。96个世界各重复所有预算和策略，不能把288个预算读数或3456条路径当作独立世界。

协议、配置、依赖、测试和输入快照在新开发entropy生成前已有哈希绑定；runner误用旧目录名，漏列六个本地t1c模块。原freeze未被补写，模块没有在运行后改动；事后hash和早于启动的mtime只能提供支持证据，不能补成预先的完整源码承诺。见[PROVENANCE_DEVIATION.json](PROVENANCE_DEVIATION.json)。本批仍是开发证据。

## What is actually matched

T1a/T1b KL和冻结Fused-Info真实held-target cadence为t_next=t+ceil(sqrt(t+1))，B32更新点为8,11,15,19,24,29；不是32步。新Fresh因子从t8后每轮重算，包含forced轮。字面32步桥接臂仅在t8、40等更新，不能冒充旧T1a。

四臂共用观测、校准、类型准确率、后验实现、动作收费、forced时钟、累计欠额跟踪和最终decoder。KL使用AnalyticReuse，后验均值p/q及边际z-MAP用于KL规划；IG对当前联合theta预测积分，最大化I(theta;Y)/cost。故这是两种定义明确的规划准则比较，不能称对所有KL/IG目标的普遍判断。

原始IG的one-hot事实目标和KL的组内均匀目标具有不同约束。为此同时报告IG-Group两臂：选择平均IG最高的组格式并在组内均匀分配，或选择单独type；其target simplex与KL一致。它仍是一步信息准则对KL备择规划的比较。原2×2中目标差包括组内事实自适应，不能误归因为单纯信息目标。

## 原始可执行规则2×2


|效应|B16|主B32|辅助B64|
|---|---|---|---|
|KL刷新：Fresh−Block|+0.00pp [+0.00pp, +0.00pp]|+1.04pp [-4.17pp, +6.25pp]|+3.12pp [-1.04pp, +7.29pp]|
|IG刷新：Fresh−Block|+0.00pp [+0.00pp, +0.00pp]|+7.29pp [+0.00pp, +14.58pp]|-3.12pp [-8.33pp, +2.08pp]|
|Block下IG−KL|+0.00pp [+0.00pp, +0.00pp]|+3.12pp [-6.25pp, +12.50pp]|+9.38pp [+2.08pp, +15.62pp]|
|Fresh下IG−KL|+0.00pp [+0.00pp, +0.00pp]|+9.38pp [+3.12pp, +16.67pp]|+3.12pp [-3.12pp, +9.38pp]|
|刷新主效应|+0.00pp [+0.00pp, +0.00pp]|+4.17pp [-0.52pp, +8.85pp]|+0.00pp [-3.12pp, +3.65pp]|
|准则主效应|+0.00pp [+0.00pp, +0.00pp]|+6.25pp [+0.00pp, +13.02pp]|+6.25pp [+0.52pp, +11.98pp]|
|交互：IG刷新差−KL刷新差|+0.00pp [+0.00pp, +0.00pp]|+6.25pp [-3.12pp, +15.62pp]|-6.25pp [-12.50pp, +0.00pp]|


## 同组内均匀target空间2×2


|效应|B16|主B32|辅助B64|
|---|---|---|---|
|KL刷新：Fresh−Block|+0.00pp [+0.00pp, +0.00pp]|+1.04pp [-4.17pp, +6.25pp]|+3.12pp [-1.04pp, +7.29pp]|
|IG刷新：Fresh−Block|+0.00pp [+0.00pp, +0.00pp]|+7.29pp [+0.00pp, +14.58pp]|+3.12pp [-2.08pp, +9.38pp]|
|Block下IG−KL|+0.00pp [+0.00pp, +0.00pp]|-4.17pp [-10.42pp, +2.08pp]|+3.12pp [-1.04pp, +7.29pp]|
|Fresh下IG−KL|+0.00pp [+0.00pp, +0.00pp]|+2.08pp [-5.21pp, +9.38pp]|+3.12pp [-2.08pp, +8.33pp]|
|刷新主效应|+0.00pp [+0.00pp, +0.00pp]|+4.17pp [-0.52pp, +8.85pp]|+3.12pp [+0.00pp, +6.25pp]|
|准则主效应|+0.00pp [+0.00pp, +0.00pp]|-1.04pp [-6.25pp, +4.69pp]|+3.12pp [+0.00pp, +6.77pp]|
|交互：IG刷新差−KL刷新差|+0.00pp [+0.00pp, +0.00pp]|+6.25pp [-3.12pp, +15.62pp]|+0.00pp [-7.29pp, +7.29pp]|


## Bridges and execution


|比较|主B32|辅助B64|
|---|---|---|
|同backend、同clock：直接执行−累计跟踪|-1.04pp [-7.29pp, +4.17pp]|+4.17pp [+1.04pp, +8.33pp]|
|实用dense/tie/跳过forced计算版本−log直接执行|+2.08pp [-1.04pp, +6.25pp]|+0.00pp [-3.12pp, +3.12pp]|
|Fresh下单事实IG−组均匀IG|+7.29pp [+0.00pp, +14.58pp]|+0.00pp [-5.21pp, +5.21pp]|
|KL原sqrt−字面32步|+3.12pp [-4.17pp, +10.42pp]|-2.08pp [-8.33pp, +4.17pp]|
|IG原sqrt−字面32步|+15.62pp [+6.25pp, +25.00pp]|+12.50pp [+5.21pp, +20.83pp]|

“Lite−log直接执行”同时改变浮点实现和tie、跳过forced轮更新，不能称纯执行效应。仅“log直接执行−log跟踪”保持目标实现和clock相同。


|B32策略|自由动作不同于当前one-hot目标|自由动作总数|使用后验平均年龄/观察数|
|---|---|---|---|
|IG-Block|525|1536|1.812|
|IG-Fresh|527|1536|0.000|
|IG-32|0|1536|15.500|
|IG-Fresh-Direct|0|1536|0.000|
|Fresh-IG-Lite|0|1536|0.000|


累计跟踪器可能追赶旧目标，故每步更新目标不等于每步执行当前最大IG。该不一致诊断只用于one-hot臂；组均匀目标内多个事实都合法，不能用其单一argmax作同样判断。两个switching臂的日志posterior_online是基础KL候选阶段的时间，之后IG会重算后验；不据此字段判断控制器使用旧信念。

forced轮同样累积目标质量，因此后续欠额可能受forced阶段旧target影响。direct/residual臂继承记录的tracking上/下界字段只作记账，原tracker的理论欠额保证不会自动随新执行规则保留，未用它们认证停止。

## Supported interpretation

原始规则：Fresh下IG−KL为+9.38pp [+3.12pp, +16.67pp]，开发区间全为正；刷新主效应为+4.17pp [-0.52pp, +8.85pp]；准则主效应为+6.25pp [+0.00pp, +13.02pp]。
同target空间：Fresh下IG−KL为+2.08pp [-5.21pp, +9.38pp]，开发区间包含零；刷新主效应为+4.17pp [-0.52pp, +8.85pp]；准则主效应为-1.04pp [-6.25pp, +4.69pp]。

因子差、直接执行差和组内自适应差来自会随策略分歧的轨迹，不能相加成一个唯一的历史收益分解。完整逐世界配对见PAIRED_OUTCOMES.json，事件日志见原始terminal记录。

区间为预定12个单元内、以世界为单位的20000次配对bootstrap百分位区间，seed42017。每单元仅8世界，是固定网格开发不确定性；未作多重比较校正，不宣称总体显著性、确认性发现或普遍优越性。各预算沿用同一批世界；指标和比较不能当独立证据相加。

所有策略始终购买至B，使用同一个order32数值积分联合后验和完整theta向量joint-MAP最终猜测。目标后验不是精确连续后验。末尾另行调用冻结Fraction/Decimal严格gate，覆盖全部task/type/calibration；其范围限于原iid、已知s及已审计算术/模型假设。固定预算恢复率不是认证正确率，不证明delta-correctness、固定置信成本或渐近最优。

本轮主B32中，单独提高KL刷新仅68→69；共同tracker的fresh单事实IG为78，fresh组均匀IG为71，fresh KL为69。优势没有随KL每步刷新而消失，但同target空间下还没有支持纯IG准则优势的正区间。组内事实自适应是重要候选解释，单独对照的区间下界恰为零，不能称已确证的唯一机制。直接执行在B32为77而tracker为78，B64则91对87；“删跟踪器总会更好”也不成立。
