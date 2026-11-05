# Luna 模拟顾客实验

本目录记录在 Myntra 开发集上，通过 Codex CLI 请求 `gpt-6-luna` 扮演固定画像顾客的 72 次受控诊断。它复用此前 Qwen 诊断的 8 个机制覆盖案例，属于开发分析；不代表真人偏好，也不比较推荐算法。

核心结果见 [results/REPORT_ZH.md](results/REPORT_ZH.md)，逐项指标见 `results/ANALYSIS.json`，CLI 用量和后处理核对见 `results/POSTHOC_AUDIT.json`。原始提示、回答、CLI 事件、Qwen 历史参照和零调用预运行收据均保存在 `artifacts/`。

验证冻结输入与代码：

```bash
python luna_simulator.py verify
python -m unittest -v test_luna_simulator.py
```

重算评分与报告时，先运行 `python luna_simulator.py analyze`，再运行 `python posthoc_audit.py`（后者修正基础重复调用的稳定性汇总并写入资源用量）。模型请求已完成；不要在此目录重复执行 `run`。若要重新采样，应另建版本、冻结新协议，并记录新的调用预算。

保留集确认结果见同工作树中的 `myntra_heldout_confirmation_v01_20261104/results/REPORT_ZH.md`；两项实验共享方法评价目标，但模拟器实验不参与保留集方法排名或调参。
