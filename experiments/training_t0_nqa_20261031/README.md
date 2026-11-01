# Training-Based Reliable Information Elicitation — T0

Status: **T0 COMPLETE; NO TRAINING EXECUTED**.

独立分支 `training/t0_nqa_feasibility`，worktree `/home/gaoym/When_Learning_How_to_Ask_training_t0`。本会话从这里专门负责 Training 线，不修改其他两线代码。

- [T0研究判断](T0_DECISION.md)
- [研究线章程](RESEARCH_CHARTER.md)
- [已有状态剖析与训练可行性](T0_FEASIBILITY_REPORT.md)
- [Neural Query Allocator 设计](NQA_METHOD_DESIGN.md)
- [输入、监督与动作契约](STATE_ACTION_CONTRACT.md)
- [Teacher–Student 协议](TEACHER_STUDENT_PROTOCOL.md)
- [世界划分与泛化协议](SPLIT_GENERALIZATION_PROTOCOL.md)
- [强基线与 Go/No-Go](BASELINES_AND_GO_NO_GO.md)
- [成本摊销与可靠性](COST_AND_RELIABILITY.md)
- [未执行的 T1 提案](T1_EXECUTION_PROPOSAL.md)

T1_CONDITION_ROSTER.json 和 T1_PLAN_DRAFT.json 是候选条件/预算元数据，没有创建世界或私有 seed。`t0/nqa_reference.py` 是固定随机初始化的未训练 NumPy 契约原型，没有训练入口。

当前实测仅复用23个历史公共观测状态，主计时69次、未封装比对23次、Fused-Info参考23次，补充cProfile8次。没有新查询、参考样本、训练更新、Qwen/GPU/API调用。已有状态不作为未来拟合或独立评测数据。

原文件只读快照及其 SHA256 在 INPUT_SNAPSHOT.json；vendor/ 是逐字节代码依赖副本。原 Phase2e、旧 Qwen T1 和 Benchmark 文件均未改动。主计时、补充诊断的格式问题及修复范围均在 artifacts/ 和最终收据保留，不掩盖失败/局限。无独立代理审查或形式化验证主张。

契约检查（不训练）：

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONPATH=experiments/training_t0_nqa_20261031 \
python -m unittest discover -s experiments/training_t0_nqa_20261031/tests -v
```

原主计时入口拒绝覆盖现有 artifacts 目录。无需重跑计时；`t0.render_feasibility` 可从保存的记录重建可行性报告。原始状态、计时与日志只在本地，排除出Git。T0所有结论限定为计算定位和研究设计。
