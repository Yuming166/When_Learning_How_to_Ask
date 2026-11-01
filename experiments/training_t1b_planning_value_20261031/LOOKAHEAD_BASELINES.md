# Non-trained planning baselines

## Material Passport

全部规则在新世界抽样前固定；无训练参数、无模型调用。AnalyticReuse等原代码保持逐字不变。

## 九个策略

|策略|自由查询轮的规则|
|---|---|
|AnalyticReuse|原T1a KL权重、强制探索和累计跟踪|
|Fused-Info|冻结的贪心I(theta;Y) target及其原更新clock/跟踪|
|Fused-D-RRC-Type|冻结融合估计的task/type workload规则|
|Fixed-KL-IG|t<B/2用KL候选；之后用当前信念IG候选|
|Type-Then-Task|首G个自由轮按组号各买一次type，之后用TASK候选|
|Fresh-IG|每个自由轮用当前信念最大I(theta;Y)，区别于冻结Info的延迟target|
|Task-Only|在所有task动作中最大化下一步完整向量MAP成功概率|
|Recovery-1|在KL/IG/TYPE/TASK候选中最大化一步完整向量MAP成功概率|
|Lookahead-2|同候选集合，最大化二步条件期望完整向量MAP成功概率|

所有残差控制器都维护同一KL虚拟累计目标；可偏离实际动作，真实counts仍参与下次欠额。没有改变“Follow KL”的规则来偏袒控制器。前16次强制完全一致；下一强制块t32..39也一致。Pure策略原本做的KL更新仍发生在强制轮，计算成本不隐藏。

KL欠额候选用原精确numpy argmax；其余得分在1e-12内相等时按候选顺序KL/IG/TYPE/TASK或物理动作编号选最前者。TYPE选择max Pr(z=1)(1-Pr(z=1))；它是合法启发式，不是直接观察z。TASK使用下一步完整恢复效用，故Recovery1是比熵贪心更直接的同目标对照。候选可能重复，计算复用但不增加可用动作。

## 二步计算

定义mu_a(h)=P(Y=1|h,a)，数值信念权重w_h。保存

F_(theta,a)=sum_(h:theta(h)=theta) w_h mu_a(h)，
M_(theta,a,c)=sum_(h:theta(h)=theta) w_h mu_a(h)mu_c(h)。

四种二元未来分支的theta未归一化概率分别为M、F_a−M、F_c−M、P(theta)−F_a−F_c+M。每个分支取max_theta，给定第一回答后允许重新选择第二个macro动作，按分支概率加权。未归一化形式已经包含回答概率，不重复乘一次。

第二步macro的IG、TYPE、TASK均由第一步回答条件化后的信念重新计算。若跨过原KL更新clock，以该条件信念的率均值/z_MAP重新运行同一个AnalyticReuse并验收gap/信息，然后更新虚拟cumulative再算第二步KL候选。若下一步是forced则只允许强制动作。没有将原率投影/未来动作冻结成不一致的树。

对每个根状态记录 Q2(KL/IG/TYPE/TASK)、最优值、在Recovery1首动作后的同一二步续策值、它们之差，以及是否改变首动作。二步额外值按同一树和同一候选空间比较；这不是拿V2−V1的不同查询数误当收益。逐层归一化的独立嵌套枚举与矩阵矩公式在测试中对照。

实际执行是每一步重规划，展望深度min(2,B−t)；它是二步receding horizon，不是精确B步最优POMDP解，也不叫完整长时域求解。没有做可选三步，以限制计算和事后搜索自由度。

## 数值与文献界限

连续后验近似来自冻结order32求积；未来条件更新在这个有限数值信念内进行。Bernoulli type似然仍按已知s含噪，不把report置为确定z。原certificate独立于这些浮点后验。

RL用于序贯实验设计并非新概念：[Blau et al., ICML2022](https://proceedings.mlr.press/v162/blau22a.html) 将策略优化转化为MDP并使用深度RL；[Guo et al., ICML2026](https://proceedings.mlr.press/v306/guo26g.html) 结合离线学习策略/后验与在线多步场景树。本轮只检验未知组共享可靠性和付费type的具体有限预算价值；不声称残差RL或二步Bayesian planning本身新颖，也未完成完整新颖性检索。
