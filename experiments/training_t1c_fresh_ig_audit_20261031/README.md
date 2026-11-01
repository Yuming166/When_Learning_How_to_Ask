# T1c — Fresh-IG mechanism and fairness audit

分支training/t1c_fresh_ig_audit，base3186587。状态：completed；Fresh候选门槛=GO；RL=NO-GO_TRAINING_ADDED_VALUE_UNESTABLISHED。独立新开发、无训练、无确认。

## Read first

- [FINAL_DECISION.md](FINAL_DECISION.md)
- [POLICY_SEMANTICS_AUDIT.md](POLICY_SEMANTICS_AUDIT.md)
- [REFRESH_VS_OBJECTIVE_ABLATION.md](REFRESH_VS_OBJECTIVE_ABLATION.md)
- [PAIRED_FINITE_BUDGET_RESULTS.md](PAIRED_FINITE_BUDGET_RESULTS.md)
- [COMPUTATIONAL_COST.md](COMPUTATIONAL_COST.md)
- [RL_ADDED_VALUE_ASSESSMENT.md](RL_ADDED_VALUE_ASSESSMENT.md)

## Reproducibility

T1C_PROTOCOL.md/config.json/freeze.json保存预定设计和真实原始清单；PROVENANCE_DEVIATION.json明确六个新模块未被预先hash绑定，勿把事后快照当预承诺。

INPUT_SNAPSHOT.json绑定只读历史源码/报告，frozen_t1b保留完整相同依赖，不改生成器或旧基线。tests/test_factorial.py及audit/工程日志覆盖cadence、动作、组均匀空间及Lite回归。无需GPU或模型。

RESULTS.json、PAIRED_OUTCOMES.json、STRATIFIED_RESULTS.json、GROUP_RESULTS.json、TYPE_PURCHASE_TIMING.json、BELIEF_FEATURES.json、RUNTIME.json、VALIDATION.json保留全部开发统计及分母。FINAL_RECEIPT.json hash绑定最终public文件与本地artifacts；原始结果和新私有reproduction在被git忽略的artifacts。没有读取旧seed或保留确认seed；新truth仅在动作完成后父端评分。

唯一科学运行已结束。runner拒绝覆盖已有artifacts；不要删除目录后自动重试。原始模块保持运行时字节不变。重算报告仅运行`python audit/analyze.py`、`python audit/render.py`，不导入训练/策略或生成新世界；之后receipt需要重新生成以反映字节变动。

本分支仅暂存本实验allow-list，不自动提交、推送或合并；无下一阶段授权。
