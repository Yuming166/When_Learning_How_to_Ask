# 三种 LLM 顾客回答通道下的关键机制消融

复用三模型原始真实回答，每模型280案例/48画像；新增模型调用为0。
比较完整DV与初始DV固定排序。推荐方为Python；本轮不扩展为自由多轮顾客交互。

首次执行顺序；已有运行证据时不要重复run：

```bash
PYTHONDONTWRITEBYTECODE=1 python experiment.py prepare
PYTHONDONTWRITEBYTECODE=1 python test_ablation.py
PYTHONDONTWRITEBYTECODE=1 python experiment.py freeze
PYTHONDONTWRITEBYTECODE=1 python experiment.py run
PYTHONDONTWRITEBYTECODE=1 python experiment.py analyze
PYTHONDONTWRITEBYTECODE=1 python experiment.py verify
```

`analyze`仅分析保存轨迹；`verify`核验冻结输入、上游保全与输出。
主结果使用全分母，另列三模型共同完整有效的诊断子集。
