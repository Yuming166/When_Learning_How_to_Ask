# T1a No-Training Optimization Baseline Gate

**GO：采用无训练解析复用；当前神经训练 NO-GO**。32新开发世界；未训练、未确认。

本目录保留冻结依赖与加速器的独立实现；原始实验目录未修改。

- [求解器比较](SOLVER_BASELINE_REPORT.md)
- [缓存与插值审计](CACHE_AND_INTERPOLATION_AUDIT.md)
- [数值与认证边界](NUMERICAL_FEASIBILITY_REPORT.md)
- [闭环配对结果](CLOSED_LOOP_COMPARISON.md)
- [最终训练判断](TRAINING_VALUE_DECISION.md)

在本目录下执行接口检查：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v`。

执行记录而非自动重跑许可：先`python -m t1a.offline`，再`python -m t1a.runner`。两者拒绝覆盖已有结果；runner要求离线gate通过，生成新的development entropy，严格守预算。已完成运行不应自动再次执行；精确复现旧世界需要本地私有开发种子，不能以另一份新随机世界替代。产物分析为`python audit/analyze.py`、`python audit/validate.py`、`python audit/render_reports.py`，无新查询/训练。最终hash由audit/seal.py生成。
