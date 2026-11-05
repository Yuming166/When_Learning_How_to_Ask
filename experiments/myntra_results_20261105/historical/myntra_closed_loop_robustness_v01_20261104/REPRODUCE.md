# 复核与复现

## 复核本轮已完成结果

在本目录运行：

```bash
python -m unittest -v test_robustness.py
python verify_robustness.py
```

验证器会检查冻结文件哈希、96 条画像-menu × 先验记录的完整覆盖、2,784 条轨迹行、所有方法与预算的分母、预算 6 的精确终点、整档询问成本，以及预先约定的描述性门槛。

## 在隔离副本中重新运行完整面板

不要删除或覆盖本目录的运行收据和结果。要重新运行，请将本目录复制到新的实验目录，并确保旁边仍有冻结的 `myntra_closed_loop_dev_v01_20261104`、原始 Myntra 来源工作目录以及相同的解释器环境。隔离副本中保留同样的 `config.json`、策略和协议；删除副本中的旧 `FROZEN.json`、`artifacts/SMOKE_*` 与 `results/` 运行产物后，依次运行：

```bash
python -m unittest -v test_robustness.py
python run_robustness.py --smoke
python freeze_robustness.py
python run_robustness.py --full
python verify_robustness.py
```

完整面板大约需要十几分钟到半小时，取决于机器性能。完整运行会创建一次性 `RUN_STARTED.json`；中断后应保留中间轨迹并将其报告为不完整运行，不要在同一目录重启或挑选性补跑。

完整运行只使用本地确定性代码，不调用模型/API/GPU，也不训练模型。重新运行会重复同一冻结菜单和两个种子配置；它用于复算与实现审计，不会构成新的独立确认样本。
