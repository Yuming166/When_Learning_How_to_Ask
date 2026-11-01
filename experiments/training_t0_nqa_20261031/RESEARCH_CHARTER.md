# Training-Based Reliable Information Elicitation：研究线章程

## Material Passport

2026-10-31，Asia/Shanghai。本轮为 T0 设计与已有状态 CPU 剖析；不执行训练。独立分支 `training/t0_nqa_feasibility`，独立 worktree；输入版本见 INPUT_SNAPSHOT.json。

本线研究：能否学习可靠性推断或查询资源分配的计算过程，在保留统计停止条件的同时降低计算与获取成本？训练是候选手段，其价值必须超过无训练的缓存、优化器复用和简单策略。

|研究线|负责范围|本线的接口|
|---|---|---|
|Theory & Method|Aligned/Fused 方法、后验、GLR/认证、理论证明|只读导入冻结版本，不修改方法源码或证明|
|Benchmark|Exact/Mechanism/Natural 数据、语义、响应通道、科学验收|只消费已验收接口；不生成 Natural 任务，不调用回答模型|
|Training（本会话）|状态表示、轻量分配器、蒸馏、泛化和摊销成本|当前完成 T0；T1/T2 均为未执行提案|

T0：定位开销、正式设计、原型契约和门槛。T1：先学习冻结 Fused-Original 的 KL 分配，保留其估计器与外部停止器。T2：仅在轻量方案证明额外价值，并且语言输入确有必要后，再考虑 Qwen3.5-4B LoRA。

新 T1 暂称 **T1-KLD-v1**，避免与目录 `When_Learning_How_to_Ask_training_t1` 中已完成的旧 Qwen pilot 混淆。旧 pilot 的教师为 forced-only Aligned，不是 Fused-Original；其 NO-GO 是有意义的历史负结果，不是本轮新方案的有效性试验。本线不恢复它、不覆盖其结果，不复用其训练/测试世界。本轮只核对读取报告的历史回执哈希，没有重新分析旧私有数据。

当前授权仅覆盖 T0。允许数学与接口测试、在已有观测状态上运行 CPU 求解器以剖析开销；不允许新科学轨迹、训练更新、Qwen 加载/生成、GPU 计算、模型 API、RL、超参搜索或确认实验。已有状态不会被纳入将来的独立训练/评测样本。T1 提案不是执行授权。

WWW 增强贡献的必要性独立判断：如果缓存/同计算量简单策略足够，或离线训练成本无法摊销，则不把训练加入主论文。Exact 结果不能替代 Mechanism/Natural 的科学验收或证明语言环境泛化。
