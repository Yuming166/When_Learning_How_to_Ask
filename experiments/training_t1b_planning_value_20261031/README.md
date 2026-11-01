# T1b — Planning Value Audit before RL

**REVISE：尚未充分证明值得训练RL，保留接口与设计，不启动T2。** 96新开发世界、2592条固定预算路径，未训练RL。

- [预先冻结的协议](T1B_PLANNING_PROTOCOL.md)
- [信念POMDP接口](BELIEF_POMDP_INTERFACE.md)
- [前瞻与强基线](LOOKAHEAD_BASELINES.md)
- [有限预算结果](FINITE_BUDGET_RESULTS.md)
- [条件RL设计，未执行](RL_FEASIBILITY_DESIGN.md)
- [最终判断](FINAL_DECISION.md)

代码在t1b/，冻结T1a依赖在frozen_t1a/，只新增本隔离目录。额外的[宏动作接口](interfaces/README.md)提供prepare/act/finalize与重复动作mask，三项literal-stub测试通过；它未用于已冻结的科学比较，单独绑定INTERFACE_RECEIPT。RESULTS.json保留全部单元/预算；PAIRED_OUTCOMES.json保留逐世界结果；VALIDATION与FINAL_RECEIPT记录范围和hash。

已执行命令（不是再次执行许可）：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v`、`python -m t1b.preflight`、`python -m t1b.runner`。runner拒绝覆盖，预算固定，不自动重试。私有开发熵只保留本地忽略目录；精确复现同一世界需要该本地记录，新的entropy不等于复现。

分析与验证只读取已有结果：`python audit/analyze.py`、`python audit/validate.py`、`python audit/render.py`、`python audit/seal.py`。不得自动启动下一阶段。
