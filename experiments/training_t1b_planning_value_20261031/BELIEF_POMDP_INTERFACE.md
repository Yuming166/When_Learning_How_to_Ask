# RL-ready belief-state interface

## Material Passport

T1b接口已实现，但未训练RL。当前控制器为确定性规则与有限二步规划。

潜变量 h=(theta,z,p,q) 在episode内固定；二元任务和type响应在给定h时独立、fresh。可观测账本包括分组、d、eta、已知s、公共R/预算、离线两条真实参考流、任务counts[j,m,y]、type reports、forced counts、actual/cumulative query counts和KL更新时钟。状态 b_t 为同一冻结联合后验，先验为独立均匀theta/z和合法有序率三角形上的均匀密度。数值实现使用order32 Gauss-Legendre近似积分，不是隐藏真实率，也不是将type report当作z。

在该iid模型内，完整账本及跟踪器使数值belief环境可由合法历史确定。仅p/q后验均值不够支持二步规划：代码保留theta/z/率节点的联合权重；不将相关性丢掉。`Belief.condition(a,y)`按已知观测似然更新这些权重；未来y在所有可能结果上积分，没有向环境索取未来样本。

物理动作是(query,j,A|B)与(type,g)，每次成本1。控制器的四个macro为KL、IG、TYPE、TASK，均通过固定规则映射为一个物理动作；forced轮所有宏被同一强制动作覆盖。下一步累计目标在当前KL骨架下更新，残差选择仍计入真实counts；不会凭空获得一次KL动作再额外购买type。宏返回不能STOP或提交答案。最后一步LA2降为LA1；非法动作/非有限数值会失败记录，不允许回报正确答案后继续。

KL表示“使用当前KL虚拟累计目标的最大欠额动作”。IG表示当前完整信念下I(theta;Y)最大的合法动作。TYPE表示z后验方差最大的组（相同已知s=.8），任务选择及tie见LOOKAHEAD_BASELINES。所有argmax具有公开确定性tie rule，不能用世界ID、真值或正确性选择tie。

策略可用：当前后验、观察计数、已用/剩余预算、候选物理动作、KL权重与clock。禁止：真实theta/z/p/q、私有seed/key、episode/source ID、真实参数标签、未来回答、终局评分或任何中间正确性反馈。枚举假设中的theta/z不是环境实际隐藏值。`Belief`构造白名单没有true_p等入口；父进程持有生成配置和reward，受限worker只走原JSON RPC，Landlock边界继承T1a。

最终所有策略共同用argmax_theta sum_(z,p,q) b_B(theta,z,p,q)输出完整向量猜测。它不同于逐bit边际MAP，也不同于GLR最大似然；使用统一decoder排除解码变化造成的收益。估计器用于KL的原边际z_MAP和率均值保持原实现。

预算末独立调用原certify_stop，枚举所有theta/z并profile连续率，包含全部任务、type和校准观测。只有certified=True才发布strict output；其他终局猜测只计fixed-budget准确率。该接口本阶段不训练、不回传中间reward；未来训练adapter只能在终局由可信评测器提供0/1完整恢复reward。
