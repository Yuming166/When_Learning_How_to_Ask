# T2b 原生预运行源码审计

结论：**PASS，允许进入预定技术 smoke；完整评测仍以 smoke 的接口及字面参考轨迹对齐通过为前提。** 没有发现需要阻止冻结的政策或停止语义错误。此结论不评价策略效果、不保证查询非劣，也不替代运行后的完整覆盖审计。

## 审计边界

本审计由原生同系列代理完成，采用共享会话与源码上下文；父代理已经提供旧 T2 归因结果，因此不是盲审、跨模型验证或形式化证明。审计读取冻结 T2 与新增 T2b 的公开源码/记录，不读取私有种子、隐藏真值或保留确认世界。只做静态源码和 AST 检查；没有运行模型、环境、求解器或新世界。随后对统计代理定稿的 analyze.py、分析测试及冻结依赖的覆盖/聚类辅助函数补充了有界源码检查；本审计没有执行新评测或依据新结果修改实现。

## 关键检查

- **合法信息边界通过。** `controllers.py:12-20,37-54` 风险规则只取严格白名单状态和冻结学生分配；模型先收到可观测状态的复制件。类型超配、后验不确定性和集中度来自当下观测，没有 theta 真值、真实可靠性、世界ID、未来回答或正确率输入。阈值在旧轨迹事后审计后固定且零搜索；这属于公开的开发选择，不能称为与旧结果无关的先验设计。
- **同一后验通过。** `evaluate.py:228-250` 每次更新从原始可观测计数计算一次冻结联合后验；`Controller.info` 直接使用这个合法 posterior fit，调用原始 information_scores，不额外重估或把最终 GLR/正确率注入控制器。神经父策略和冷/复用教师仍走相同状态、相同调度。
- **调度和严格门通过。** 与冻结 T2 evaluator 的差分仅涉及本地入口、控制器接口、可观测 posterior 传递、世界构造和新增 fit_history。初始2d、32步更新、平方强制探索、累计追踪及行动成本沿用原实现。静态 AST 比较确认整个 `not budget_only and (crossing or cap)` 严格停止分支与旧 T2 完全相同；检查条件、margin、candidate_theta 和 certify_stop 参数未变。预算32/64只读评分，不修改策略或输出证书。
- **强参考通过。** AnalyticReuse 通过局部命名空间加载固定哈希的 T1a solver，未修改全局 solver、历史 vendor 或停止门。数学等价不承诺每个新状态浮点并列轨迹相同；任何差异必须保留。Cold 与 Info 的 smoke 还将分别对照字面冻结策略，不能仅凭此静态审计声称长轨迹一致。
- **成本边界修复后通过。** 审计曾指出 Controller 构造及 wrapper 后处理在原始路径计时之外；父代理已在冻结前修复 `run.py:28-44`，现在外层 wall/CPU 从 Controller 构造前开始并覆盖日志与后处理，保留原 evaluator 内层计时。神经前向即使随后回退也收费；风险、fallback、校验、归一化等都处于 enclosing prediction 时间内，`planning + inference` 保持该总量。完整路径CPU还包括跟踪、环境、GLR与严格门；外层模型冷加载、进程启动与父进程序列化另报，不应与嵌套时段重复相加。
- **新开发来源通过。** `worlds.py:6,8-35` 新命名空间生成固定32世界条件名册，24主世界×3R×8方法加6变事实世界×8方法，共624条；2个smoke世界另行20条64步技术路径。`run.seed` 在 source verify 后才创建新的OS随机主种子并写承诺；`make_episode` 固定 development split，未访问旧确认种子。世界/R内共享潜在回答流是配对设计，三R不能独立计为72世界。
- **冻结和失败保留通过。** `integrity.py` 历史哈希验证、源码/依赖冻结、只写一次目录与记录；主驱动不重试失败路径。全局超时或进程失败的未知前缀费用须保留为未知。原5%查询门槛、原零弃权要求、优化无训练参考、各R/OOD全分母在协议中明确保留。描述性bootstrap范围不得写成人群置信区间或已证明非劣。

- **完整名册与聚类分析通过。** `analyze.aggregate` 复用冻结 T2 的 validate_coverage，要求所有624条计划身份完全覆盖，拒绝重复、意外键、缺失预算与错误成本；失败路径保留分母，相关配对/均值标为不可用。`paired_analysis` 两个参考均按完整世界/R配对，main与variable分开；clustered_ratio 先按world合并各R，再用同一固定种子做4000次整世界重采样，不把72条重复R记录当72个独立世界。新增与恢复弃权分别计数，不能用净恢复掩盖新失败。
- **验收与部署算术通过。** 查询上界1.05、inclusive compute下界2、原候选和参考全部正确认证零弃权均显式保留；完整路径CPU下界2另列 latency_flags，不偷换原三门。最终结论仍需综合各标记手工判断，程序没有自动GO。部署差值使用总获取与完整路径CPU，明确lambda非负、M与训练摊销情景及未知历史成本；组件计时不重复添加。所有区间有描述性、开发多候选和非正式非劣限制，固定预算读数独立成表。

## 验证证据与尚待执行

本次静态检查解析当前10个t2b源文件和4个测试文件，严格停止条件 AST 一致。阅读父代理在最终改动后保存的 `logs/controller_tests_final.log`（7项）及 `logs/analysis_tests_final.log`（11项）：全部通过，包括私有字段拒绝、共享posterior不重复计算、周期回退、624名册、失败完整分母、弃权不抵销、CPU标记与摊销算术。未复跑会调用数值求解器的 reuse 测试。本次不执行技术 smoke；父代理在所有文件冻结后按协议执行，不得因结果不佳修改阈值。

统计实现已补充静态审查；所有新源码/文档定稿后再校验本审计所列哈希。下方是本次审计快照，后续改动需显式复核，不能沿用本PASS概括未审查修改。

## 审计源码快照

| 文件 | SHA256 |
|---|---|
| `HYBRID_CONTROLLER_PROTOCOL.md` | `9f857c07237f8bd84e56fe8444f0c626e9d1bc5ffac706b480457cbb3b1056f0` |
| `ANALYSIS_SCOPE.md` | `8a9b2777507e56a7858d4b453396f70773d79f9fe09a9bc78738b3c1bd14f779` |
| `config.json` | `404ff2666ae21981902e56fe7a7f6e4f68d2f9b9f4f907c7d7a3500c89598efc` |
| `t2b/controllers.py` | `008415e350d9b9b75f0a9896c4ee073fe7f87ee58e435396f68bd3c2e65cd83d` |
| `t2b/evaluate.py` | `d9bd0dc70499cae15077ef39e1975bd6a10d327ac0090b00e3b16bd31ad69f1d` |
| `t2b/run.py` | `3914863bf98be455d948531175b63fc4b12530245bb501580dafe6a4a24e0b93` |
| `t2b/worlds.py` | `8c2eede4f43cf995858a767b301e860cffee65cee2123dee04fcca519eb21f67` |
| `t2b/integrity.py` | `a1ad8ecc437ac273e1d9b4c9efeec89f414e9980c9bfac01e5341e60c8beb155` |
| `t2b/reuse.py` | `43d296c344cb68a43a6ec3793c9f3e5db281d2590f798fe0b5b311620435c0d4` |
| `t2b/analyze.py` | `d0c71667af7847d8ef3054fa4c8404517a91f7225238bc28a11960be400842e7` |
| `tests/test_analysis.py` | `5ab8a7963a80a67c0089f681587370958a6c428cc5259e9f6606a03a573f26b7` |
| `logs/controller_tests_final.log` | `c910bba864b96f9d94bedc14da2d43cfb35ca6c08f254ce5b395d536742d1a3b` |
| `logs/analysis_tests_final.log` | `316f442acc6530ea7991536194d7f50bf2fbb8fc5bc93f16a21594b6463df0b1` |
| `CONDITIONAL_TRAINING_PROPOSAL.md` | `88c144a4e431900ced1f5c89018ef4ffecd74c37e91d64fbc3377948c7b238fd` |
