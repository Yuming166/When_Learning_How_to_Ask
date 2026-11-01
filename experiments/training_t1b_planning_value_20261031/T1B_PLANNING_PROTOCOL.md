# T1b — Long-Horizon Planning Value Audit

## Material Passport

2026-10-31；仅开发、无训练。独立分支 `training/t1b_planning_value`，base `3186587`。本协议在新开发世界抽样前冻结。用户授权附件要求先验证非短视规划价值，禁止本阶段训练RL、Qwen、LoRA、PPO、确认实验或修改基准生成器。这里的分支预测和无训练比较是解析Bayesian lookahead，不是采集RL训练rollouts。

## 问题和不可变参考

T1a 已解决一部分求解器计算冗余；本轮问的是：在有限预算下，偏离原KL分配能否提高完整事实向量恢复率，而且收益是否来自第二步决策，而非换了目标函数。AnalyticReuse、联合后验、原始跟踪器、认证器和Exact生成器均从T1a逐字复制并hash绑定，原工作树不修改。仅新增控制器与评测包装。

主指标为预算 B=32 的完整事实向量恢复率。所有臂使用同一最终 joint-theta MAP decoder；其后验来自冻结order32联合积分。预算16与64为预先固定的辅助设置，全部报告，不依结果排除天花板单元。B16是结构性强制探索对照：原L=2d=8的square-block在t=0..7和8..15均强制，控制器没有干预机会。该发现来自工程fixture检查，未生成科学世界。

## 固定矩阵和预算

完整笛卡尔积：d4，partition=[1,3]/[2,2]/[4]，生成p=.85/.75，q=.60，alpha0/3，已知s=.8，eta=.05。12单元，每单元8个新独立世界，共96世界。每世界在B16/32/64各评一次，9臂共2592条路径。不同预算重复同一世界，不算288个独立世界。

公共planning_R=16在离线采样前固定，M=ceil(alpha*R)，每条路径校准费用2M，在线任务/类型每个均计1。alpha是M/R而非M/B。父进程用于生成世界的p/q不可传给worker；其后验先验覆盖整个合法率三角形，不以评测两点作为先验。保留[1,3]/[2,2]/[4]完整结构，不按任何实测效果或隐含真值筛选实例。其理论premium状态可按固定生成配置由审计器标注，不能进入策略。

最多96,768在线动作（上限100,000）、1500秒墙钟，无重试、无自动增样。预计算数值fixture预算9项测试+6次定时next；不采样环境世界。实际开跑前冻结代码、输入快照与协议，再生成新私有development entropy；索引从910000开始，与保留确认seed完全隔离。世界顺序replicate×partition×rate×alpha；预算按replicate轮换；臂逐世界预算轮换执行，禁止按结果改顺序。

## 预先规定的对照

AnalyticReuse；冻结Fused-Info；冻结Fused-D-RRC-Type；Fixed-KL-IG；Type-Then-Task；Fresh-IG；Task-Only；Recovery-1；Lookahead-2。后六者使用同一个不可变KL规划骨架与同一组候选动作，规则在LOOKAHEAD_BASELINES.md中固定。所有保留同一forced blocks及KL更新clock；冻结Info/D-RRC保持自身原target规则。禁止让Lookahead独享新的观察、decoder或未来样本。

固定预算episode始终执行B次查询；不会因为非认证的后验置信高而提前结束。每次候选规划只用当前可观测后验预测二元未来回答。最终reward/正确性只在父评测器终局计分，绝不返回控制器作为中间反馈。

## 主分析和RL门槛

按12单元内配对世界bootstrap20,000次（分析seed22017），报告准确率差和比值、配对赢/输/同、世界级不确定性。不同预算保留同一个world block，预算32为唯一主比较。每个单元n8，开发percentile区间不作确认性显著性或均匀非劣性证明。报告所有单元及全部预算；reference完整恢复率>=.95的单元标记ceiling但不删除。

GO for a future RL pilot须同时满足：B32 Lookahead2相对AnalyticReuse点改善>=3个百分点且95%开发区间下界>0；相对Recovery1改善>=1个百分点且区间下界>0；相对其余每个廉价基线的点差>=0；并有超过1e-6的非短视模型增益（至少5%的LA2有效决策）。这些是探索性资源门槛，不是理论常数。多候选的辅助结果不能取代预先指定的LA2与B32。

若对KL和Recovery1的点差均<=0，给本轮RL训练NO-GO；若存在正向信号而上述门槛不全满足，REVISE，明确不足，不加样本。即使GO也只交付后续Actor-Critic设计，本阶段不训练。不能以LA2只胜KL、未胜同目标一步规划，推断RL长期规划价值。

## 报告和数值限制

报告完整向量恢复、任务/类型/2M成本、joint posterior NLL/Brier、末次率/类型误差、策略选择、全轨迹CPU/墙钟与controller/KL/分支优化开销。完整公开观察账本和私有来源保留receipt。固定预算猜测与预算末严格certificate分开，gate拒绝意味着未认证，不是固定预算episode失败；不把这些路径删掉。没有固定置信停止成本实验。

所有概率推演对order32离散求积信念是精确的条件更新/二步矩，但连续后验积分仍是数值近似。预先固定敏感性检查：12单元replicate0、B32、Recovery1和LA2，共24终点，与order64比较，不因误差/效果挑选状态。小样本精确Fraction参考和嵌套分支枚举检验单独保留。不得宣称新控制器满足Theorem1渐近最优条件，也不把Exact结论外推Mechanism/Natural。

原始第一次工程测试有两项因误认t8为首个自由动作而失败；fixture改到t16后9项通过。原调度器未改，初始失败日志保留，未发生实验失败/重跑或科学世界消耗。
