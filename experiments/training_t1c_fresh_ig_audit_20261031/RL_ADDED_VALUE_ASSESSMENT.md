# T1c — Is reinforcement learning needed?

## Evidence scope

本报告来自一个有界、独立的新development批次。没有确认世界、Qwen调用、神经训练、RL更新、PPO或Actor–Critic；没有改写T1a/T1b/T2历史结果、基准生成器或Natural。预先规定B32为主预算，B16/B64为结构/辅助预算。96个世界各重复所有预算和策略，不能把288个预算读数或3456条路径当作独立世界。

协议、配置、依赖、测试和输入快照在新开发entropy生成前已有哈希绑定；runner误用旧目录名，漏列六个本地t1c模块。原freeze未被补写，模块没有在运行后改动；事后hash和早于启动的mtime只能提供支持证据，不能补成预先的完整源码承诺。见[PROVENANCE_DEVIATION.json](PROVENANCE_DEVIATION.json)。本批仍是开发证据。

## Non-trained controls

Budget-Switch按自由轮数前半KL、后半IG，B32为8+8；避免旧B/2墙钟规则在forced16后直接退化成全IG。Belief-Gated使用当前合法后验：剩余自由轮<=8或KL候选IG/maxIG<.75时选IG（maxIG>1e-14），其余KL。两者固定于新seed之前，没有用隐藏真值、终局评分或事后最优规则选动作。


|策略|B32恢复/96|B32 CPU/s|相对KL-Block差|Lite减该策略|B64恢复/96|
|---|---|---|---|---|---|
|Budget-Switch|75/96|20.128|+7.29pp [+0.00pp, +15.62pp]|+4.17pp [-3.12pp, +11.46pp]|88/96|
|Belief-Gated|79/96|22.246|+11.46pp [+4.17pp, +19.79pp]|+0.00pp [+0.00pp, +0.00pp]|88/96|



|B32控制器|自由KL执行次数|自由IG执行次数|
|---|---|---|
|Budget-Switch|768|768|
|Belief-Gated|162|1374|



|B32控制器|实际动作不同于当时KL提案的次数|自由动作总数|
|---|---|---|
|Budget-Switch|676|1536|
|Belief-Gated|1284|1536|

控制器标记选IG时仍可能与KL提案选同一个动作；实际override统计只对当时同一状态下的KL提案，不能当完整KL反事实轨迹。

## Observable predecision features

所有策略在t16首次自由动作前，使用同一批原始观察计算共同probe；逐世界逐臂/预算一致性已经验证。预定bins为theta熵占比>=.5、组类型熵占比>=.5、估计p−q>=.15、alpha0/3。不按最终轨迹胜负重划bin，不训练回归器或搜索阈值。

表中每行报告同一bin内配对恢复差；这是事后检验关联，不能当作一个已部署的“先看真值再切换”策略。不同特征bins重叠，不能相加。所有空bin也保留。熵bin可能与alpha和分组结构关联，未控制所有此类混杂，不宣称特征的因果异质性或一个已验证的泛化预测器。


|共同t16 bin|n|B32 Lite−KL|B64 Lite−KL|B32 tracked IG−fresh KL|B64 tracked IG−fresh KL|
|---|---|---|---|---|---|
|theta_entropy_half/low|32|+9.38pp [+3.12pp, +18.75pp]|+9.38pp [+0.00pp, +18.75pp]|+3.12pp [-6.25pp, +12.50pp]|+3.12pp [-9.38pp, +15.62pp]|
|theta_entropy_half/high|64|+12.50pp [+1.56pp, +23.44pp]|+10.94pp [+4.69pp, +17.19pp]|+12.50pp [+4.69pp, +20.31pp]|+3.12pp [-3.12pp, +9.38pp]|
|type_entropy_half/low|0|NA|NA|NA|NA|
|type_entropy_half/high|96|+11.46pp [+4.17pp, +19.79pp]|+10.42pp [+5.21pp, +16.67pp]|+9.38pp [+3.12pp, +16.67pp]|+3.12pp [-3.12pp, +9.38pp]|
|gap_015/low|49|+2.04pp [-6.12pp, +10.20pp]|+10.20pp [+2.04pp, +20.41pp]|+8.16pp [+0.00pp, +16.33pp]|-2.04pp [-12.24pp, +6.12pp]|
|gap_015/high|47|+21.28pp [+8.51pp, +34.04pp]|+10.64pp [+4.26pp, +17.02pp]|+10.64pp [+2.13pp, +21.28pp]|+8.51pp [+2.13pp, +14.89pp]|
|alpha/low|48|+14.58pp [+4.17pp, +27.08pp]|+16.67pp [+8.33pp, +25.00pp]|+16.67pp [+6.25pp, +27.08pp]|+4.17pp [-6.25pp, +14.58pp]|
|alpha/high|48|+8.33pp [-2.08pp, +18.75pp]|+4.17pp [-2.08pp, +12.50pp]|+2.08pp [-6.25pp, +10.42pp]|+2.08pp [-4.17pp, +8.33pp]|

同target空间的IG-Group配对区间、特征取值摘要及每个新世界的合法probe见BELIEF_FEATURES.json；按分组/p/alpha的全部表现见STRATIFIED_RESULTS.json。未声称已经构建可泛化的预测器。

## Resource gate and decision

预定type-high/low每bin至少24世界：False。进一步要求B32和B64均出现相反方向、幅度至少3pp、区间排除零的KL/IG优势，且简单控制器尚未覆盖收益。


|比较|B32相反且区间排零|B64相反且区间排零|两预算均满足|
|---|---|---|---|
|Lite_minus_KL_Block|False|False|False|
|IG_Fresh_minus_KL_Fresh|False|False|False|


RL结论：**NO-GO_TRAINING_ADDED_VALUE_UNESTABLISHED**。“超过两个简单控制”的区间检查只是保守的附加描述性条件，并非预先声明的必要统计检验；不以它替代预定type-bin条件。在未建立稳定、可观测且未被廉价规则覆盖的剩余收益时，不设计带执行授权的新RL pilot，不启动训练。

本批type熵预定low bin为0世界，high bin为96世界，无法检验预定的双区间异质性条件；不能在看到结果后另调type阈值补足样本。B32中Belief-Gated与Lite逐世界恢复成败完全一致，但动作序列完全相同仅44/96；它们不是被误接成同一个策略。Belief-Gated CPU更多，未显示额外恢复收益。其余预定bins也没有建立在B32/B64都稳定出现、区间排零的相反KL/IG优势，故当前缺乏训练切换器的可用证据。

本批比较的是无训练策略。RL可能在更长预算、更大d或其他分布有价值仍是未检验假设；不能将“RL额外价值未建立”写成对所有RL的否定。保留既有残差动作接口即可，没必要为了论文加入模型训练。若未来另行批准研究，仍须保持认证停止独立于学习策略；当前结果不满足自动启动任何后续阶段的授权。

区间为预定12个单元内、以世界为单位的20000次配对bootstrap百分位区间，seed42017。每单元仅8世界，是固定网格开发不确定性；未作多重比较校正，不宣称总体显著性、确认性发现或普遍优越性。各预算沿用同一批世界；指标和比较不能当独立证据相加。

所有策略始终购买至B，使用同一个order32数值积分联合后验和完整theta向量joint-MAP最终猜测。目标后验不是精确连续后验。末尾另行调用冻结Fraction/Decimal严格gate，覆盖全部task/type/calibration；其范围限于原iid、已知s及已审计算术/模型假设。固定预算恢复率不是认证正确率，不证明delta-correctness、固定置信成本或渐近最优。
