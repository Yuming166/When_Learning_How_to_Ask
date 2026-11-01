# Learning How to Ask

未知查询可靠性下的可靠信息获取：共享问法、有限校准、信息分配与 Web 来源读取。

本仓库汇总截至 **2026-11-01** 的理论与 methodology 开发。既有 V5 简报保留为历史起点；代码、开发结果、数学证书及未完成事项分别标明。**受控模型结果不等于真实 Web/用户有效性，理想策略定理也不自动认证近似程序的渐近最优性。**

## 从这里开始

- [目前已有的理论与 WWW 故事](research/www_short_story_20261101/README_ZH.md)
- [全部理论及适用假设](research/www_short_story_20261101/THEORY_INVENTORY.md)
- [贡献与最近邻审计](research/www_short_story_20261101/CONTRIBUTION_AUDIT.md)
- [四页候选论文骨架](research/www_short_story_20261101/PAPER_BLUEPRINT.md)
- [当前 methodology 导航](docs/METHODOLOGY.md)
- [公开版本的范围与复现说明](PUBLICATION.md)

## 理论

| 方向 | 内容与边界 | 入口 |
|---|---|---|
| 原始共享可靠性 | 联合未知率信息复杂度、oracle、最小共享组的零一阶成本判据 | [Theory Note](Theory_Note.md)、[期望时间证明](research/original_expected_time_proof_20261031/EXPECTED_TIME_PROOF.md) |
| Web 来源层 | 区分事实真值、持久报告与抽取；有限来源饱和和状态反例 | [报告](research/web_native_theory_20261031/RESEARCH_REPORT_CN.md) |
| 来源成本与共享 | 已知率下的最优读取深度及共享条件 | [报告](research/web_cost_sharing_20261031/RESEARCH_REPORT_CN.md) |
| 未知率与有限校准 | 连续备择、正确停止、匹配期望在线成本及已知率判据失效反例 | [报告](research/web_unknown_calibration_20261031/RESEARCH_REPORT_CN.md) |
| Oracle 结构 | 纯优形式边界、强制混合深度与尚未解决的一般情况 | [报告](research/web_oracle_structure_20261031/RESEARCH_REPORT_CN.md) |
| 混合深度区域 | 明确参数区域内排除所有固定深度；至少4.85%的渐近在线成本系数差 | [区域定理](research/web_depth_region_20261101/REGION_THEOREM.md) |
| 完美来源控制 | 最大深度足够，并恢复原始共享理论的成本尺度 | [解析定理](research/web_perfect_source_control_20261101/PERFECT_SOURCE_THEOREM.md) |

混合深度与观测自适应是不同性质。强制混合深度定理不声称任何预先安排的混合设计都次优；也不处理未知来源图或不受限制的浏览 Agent。

## Methodology 与开发状态

| 阶段 | 开发内容 | 当前解释 |
|---|---|---|
| QRelBench v0.1 / Phase2a | 受控环境、观测接口、KL规划、GLR与理论系数核对 | 受控开发工具，非自然可靠性证据 |
| Phase2b / Phase2c | 理论对齐的信息跟踪、强衰减基线、证明到代码审计 | 有开发证据；旧确认协议未执行 |
| Phase2d | 类型询问2×2消融与严格停止门 | 认证范围和成本最优性分开 |
| Phase2e | 全证据联合估计、Fused-Original / Fused-Info与严格停止集成 | **完成有界开发，REVISE；未执行独立确认** |
| T1 | Qwen3.5-4B LoRA查询策略与MLP对照 | 技术训练完成；当前配置 **NO-GO** |
| T2 / T2b | DeepSets摊销、解析复用、风险/周期混合控制 | 计算与查询成本折中；未整体升级为主方法 |
| T3 | 面向终端恢复的轻量残差策略 | 冻结pilot **NO-GO**，保留负面结果 |

最新开发方法入口：[Phase2e设计](experiments/phase2e_type_evidence_20261031/METHOD_DESIGN.md)、[实现](experiments/phase2e_type_evidence_20261031/phase2e)、[最终判断](experiments/phase2e_type_evidence_20261031/FINAL_RESEARCH_DECISION.md)。

## Web 机制检查

- [W1 AVeriTeC审计](experiments/w1_averitec_audit_20261101/REPORT_ZH.md)：12条声明、50个URL；2条候选、10条隔离；未建立可运行的自然可靠性评测集。
- [W1.1语义与来源关系](experiments/w1_1_source_semantics_20261101/REPORT_ZH.md)：开发审计，无模型读取实验。
- [W2a受控来源机制](experiments/w2a_controlled_provenance_20261101/REPORT_ZH.md)：已知通道下的精确有限预算计算与稳定自适应分离；1,152份合成HTML是构造语料，**不是1,152次Qwen调用**。本发布保留生成器和汇总，未打包语料与隐藏标签。

## 安装与公开检查

使用Python3.10或更新版本，在独立环境安装核心依赖：

```bash
python -m pip install -r requirements.txt
python scripts/check_publication.py
python scripts/run_public_checks.py
```

公开检查只运行既有的小型工程夹具，不执行完整benchmark、训练、模型服务调用或确认实验。检查源码和可移植导入，不复现需要私有种子与原始轨迹的历史统计。CPU线程限制在检查脚本内设置。

单独检查一个方法阶段：

```bash
python scripts/run_public_checks.py --stage phase2e_type_evidence_20261031
```

训练代码的历史依赖与可选组件见[方法导航](docs/METHODOLOGY.md)。本发布不包含训练数据或权重；上述核心依赖不会下载模型。

## 发布记录

[来源与文件哈希](publication/SOURCE_MANIFEST.json)、[排除项](publication/EXCLUSIONS.json)、[路径兼容修复](publication/PORTABILITY_CHANGES.json)、[本次检查结果](publication/CHECK_RESULTS.json)分别保留。历史receipt/manifest仍描述原始本地完整实验；它们可能引用有意未公开的文件，不应在此源码子集上被误称为完整重放通过。

原仓库的理论笔记及V5 PDF保留；本次没有重写历史统计或启动新的效果实验。
