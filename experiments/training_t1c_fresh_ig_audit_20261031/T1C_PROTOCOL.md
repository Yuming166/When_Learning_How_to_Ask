# T1c preregistered Fresh-IG mechanism and fairness comparison

## Material Passport

无训练、有界新开发；分支training/t1c_fresh_ig_audit，base3186587。冻结T1a/T1b/T2结果和基准生成器；本协议/源码/工程检查完成后才生成新development entropy。没有RL、PPO、Actor-Critic、Qwen、LoRA、Natural改动或确认世界。此处GO仅是开发研究判断，不自动进入确认/训练。

## 设计和命名

主2×2：KL-Block、KL-Fresh、IG-Block、IG-Fresh。**Block表示真实审计的sqrt held-target，不是32。** 四臂都使用同一个冻结order32联合后验、全部观察、原forced blocks、累计目标跟踪器、同一最终joint-theta MAP decoder，唯一区别是目标KL/IG和刷新sqrt/fresh。KL用AnalyticReuse；IG用同一个冻结log-information实现。Fresh在t8后每轮（含forced）重算；Block为8,11,15,19,24,29,...。该对照不将KL概率向量硬变成最大权重动作，不制造错误的执行等价。

另外八臂（含目标空间审计）：KL-32/IG-32（t8,40,...，共同tracker与decoder，桥接T2的cadence而非复现T2世界/GLR读数）；IG-Fresh-Direct（与IG-Fresh完全同后验/IG数值实现/clock，只去掉动作欠额执行）；Fresh-IG-Lite（T1b dense+stable-tie直接选IG、跳过forced轮无用更新并删除废弃KL工作）；Budget-Switch；Belief-Gated。

另加IG-Group-Block/IG-Group-Fresh：把同一IG得分在每组每格式内取平均，选择最高均值的组格式并在组内均匀分配，或购买最高IG的type。其归一化target空间与KL一致。

因此总12臂。主2×2是原始可执行分配规则的比较，IG单动作one-hot与KL组内均匀target并非同一受限分配类，不能将主效应叫成“只改数学目标”的纯效应。新增group-matched 2×2才在相同组内均匀分配空间中比较目标；若它与原始IG表现不同，归因须包含组内事实自适应这一因素，不能强行等同。IG-Fresh是tracked因子臂，不冒充T1b Fresh-IG；后者的实用语义对应Lite。相同目标的sqrt/fresh比较支持刷新机制分析；同backend的track/direct比较支持执行机制分析。Lite与same-backend direct之间还含IG实现/tie与forced轮计算差别，单列而不强行称纯执行效应。

## 无训练预算控制

两个control都保持sqrt KL虚拟累计目标并遵守相同forced动作。

Budget-Switch：根据公开B和forced时钟算出总自由查询数，前ceil(总自由数/2)个自由轮执行KL欠额候选，其后直接选当前dense IG。B32为8个KL自由轮+8个IG自由轮，不使用会在t16退化的B/2墙钟切换。

Belief-Gated：每个自由轮计算当前theta互信息。若最大IG<=1e-14执行KL；否则若剩余自由查询<=8，或 I(a_KL)/max_a I(a)<.75，选当前最大IG，否则选KL。门槛固定、未由旧世界胜负或新结果拟合。状态仅用当前合法信念、实际counts、虚拟target和剩余预算，不读隐藏真值或未来奖励。

## 固定实例矩阵与预算

沿用T1b的完整理论配置而非筛选有利点：d4，partition[1,3]/[2,2]/[4]，p=.85/.75，q=.60，alpha0/3，R16、s=.8、eta=.05。12单元各8新独立世界，共96；各世界在B16/32/64分别运行所有臂，共3456路径。B32是唯一主预算，B16是无自由动作结构对照，B64辅助。保持同世界潜在回答流与校准配对；不同预算的同世界不能当独立样本。

M=ceil(alpha*R)，每路径2M计费；在线task/type各1。总计划129024 online，硬上限135000；1800秒wall。按replicate×partition×rate×alpha顺序，预算和臂执行顺序循环轮换；无自动增样或科学重试，失败保留部分观察。索引1050000起，新私有开发entropy在freeze后生成；不读任何保留确认seed，也不复用旧开发实例。

## 主要分析

完整恢复、joint posterior NLL/Brier、p/q末次误差、type次数和成本、全策略CPU/wall、目标更新/选样日志、终局certificates、非法/不完整/未认证路径全部报告。每路径始终到B，末尾独立gate；未认证猜测不是可靠输出，也不是被丢弃的样本。

按12单元内配对世界bootstrap20000次（seed42017），主B32。预定比较：IG-Fresh−KL-Fresh、IG-Block−KL-Block；KL-Fresh−KL-Block、IG-Fresh−IG-Block；刷新主效应=两种目标的刷新差均值，目标主效应=两个cadence的IG−KL差均值，交互=两种刷新差之差；IG-Fresh-Direct−IG-Fresh；IG-Group两臂与KL组成同空间2×2，并对照单动作IG；Lite−各KL/IG/控制；literal32桥。报告逐对四格胜负和全部预算。固定异质网格、每单元n8，区间仅开发不确定性，不称校准总体显著性/确认性因果保证。不事后选一个预算/单元作主结果。

Fresh practical candidate的开发GO门槛：Lite相对KL-Block B32点差>=3pp且区间下界>0，同时相对KL-Fresh点差>=0且区间下界>=0，全部预算完成/无非法动作。若只存在正向点信号而门槛未齐，REVISE；若对两种KL点差均<=0，当前candidate NO-GO。IG目标本身的优势还需共同tracker下IG-Fresh−KL-Fresh与主效应支持，不能由直接执行臂胜出代替。

## 可观测特征与学习必要性

所有臂在t16、任何自由动作前，由相同原始观察计算一次公共特征probe（CPU单列并计入全轨迹）：joint theta entropy/(d log2)、mean z entropy/log2、p_hat/q_hat/gap、MAP质量、M/R。它不是额外查询或真值。分析预定二分：theta entropy>=.5、type entropy>=.5、estimated gap>=.15、alpha0/3；报告各bin的Lite−KL和IG-Fresh−KL-Fresh配对差、样本数和不确定性。终局真值只用于事后检验关联，不选部署动作，不训练回归器或调整阈值。

若共同初始信念type-high/low两个bin均至少24世界，在B32和B64均呈相反方向且绝对差>=3pp、对应区间排除0，并且两个预定控制未覆盖该收益，可准备另行RL设计；这是强资源门槛，不是必要理论条件。否则RL额外价值未建立，不启动训练。廉价控制本身有效也不自动意味着RL必要。本阶段结束后不添加新规则、深度或实验。

## 数值和可靠性界限

所有目标后验是冻结order32近似积分，不是精确连续后验；KL上下界与IG为浮点计算。共同已审计certify_stop仍处理全task/type/calibration，受原iid/已知s/Fraction-Decimal条件约束。任一预算内猜测不能据恢复率宣称delta-correctness或固定置信渐近最优；direct/residual执行也不自动保留原tracker欠额界。

记录并保护旧T1a/T1b全public receipt；只读T2协议、配置、实现与报告，不导入其neural/training入口。新实验只新增本工作树目录，所有私有原始来源/entropy留在忽略目录。
