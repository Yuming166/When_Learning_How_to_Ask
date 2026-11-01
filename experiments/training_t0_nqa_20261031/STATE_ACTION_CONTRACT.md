# 训练状态、监督标签与动作契约

## Material Passport

T0 接口规范；`t0/nqa_reference.py` 仅验证 reduced planning state 和展开，没有训练执行入口。

|层次|合法内容|使用者|
|---|---|---|
|观测账本|d、分组、eta、已知 s、R、公开 cap、t、任务 counts[j,m,y]、type_counts[g,bit]、两条真实校准流的成功/总数|估计器和外部 evaluator|
|后验摘要|冻结算法由观测计算的 p/q 均值、theta/z 边际、版本及积分阶数|规划状态提取；概率是估计，不是真实类型|
|跟踪账本|forced_counts、actual action counts、累计目标、last/next update|原强制探索/调度器，第一版不学习|
|规划头输入|p_hat、q_hat、alpha、eta、group_sizes、type_accuracy/None、epsilon|MLP / NQA；代码严格白名单|
|监督标签（独立字段）|教师浮点 group_mass、K、solver lower/upper、gap、minimum information、状态/失败原因|仅训练 loss 和离线评估，不能拼入输入|
|审计元数据（独立文件）|role、世界键、条件层、状态父轨迹、代码哈希、耗时|划分/成本审计，禁止进入模型特征|

已知组结构、校准成功数和查询计数确实来自可观测接口；不得将真实 p,q,z,theta 换名为“当前后验”。s 必须是 Exact 公共契约中的已知准确率，不能从 Natural 的未知自报准确率伪造。没有真实校准流的环境不转换成高/低校准样本。空的真实流 M=0 与校准不可用是不同状态。

在声明的 iid 二元通道模型内，各流成功/失败计数给出完整似然统计；原序列顺序不进入该似然。压缩并不意味着这些边际摘要对任意 Bayesian 决策或真实语言历史都充分。完整计数由外部停止器保留，不用压缩摘要替代 GLR。

输入禁止：隐藏答案/率/组类型、评分/奖励、私有 key 或 seed、world/episode/source ID、未来响应、预留确认标签、teacher weight/K 等监督目标。训练集上的归一化统计可以保存；验证/评测不能重新拟合 scaler。R、组大小和观测数可以合法使用，但不能通过实验行号或文件名编码其身份。

动作接口沿用 `(query,j,A|B)` 和 `(type,g)`；网络实际返回合法动作的浮点分布，通过既有累计目标跟踪选出下一步。没有 JSON 百分比整数和 sum=100 约束，避免把语言解析/量化误差掺进第一版学习问题。若将来比较 Qwen，应记录连续权重与其输出编码之间的量化下界，不能通过放宽解析器后追认原闭环结果。

非法分布（NaN/负数/尺寸不符/禁用动作有质量）必须记录。预先固定的部署回退可采用同一 fused D-RRC-Type；回退的估计、计算与查询成本均计入 Student。不得无日志调用昂贵教师来隐藏失败。可选的 on-demand 教师回退必须单列成 Student+Teacher 混合策略，报告真实调用率，不能仍声称纯网络速度。

初始强制任务块、后续 square-block 强制探索、更新时钟、跟踪和 tie rule 与教师匹配。若缓存/慢更新基线改变时钟，须有同样时钟的教师对照。可用 mask、维度泛化接口测试不构成更大 d/G 下的教师或认证支持：当前严格停止范围 d<=4，教师求解器 G<=2。
