# Python 机制消融复现

这是已查看完整方法结果后设计的组件消融。原始三个划分和原冻结结论均保留。
唯一新增策略为“初始 DV 排序后固定提问”，仍逐步更新已知偏好和推荐。

首次执行顺序（已有运行证据时，不要重复 run）：

```bash
PYTHONDONTWRITEBYTECODE=1 python experiment.py prepare
PYTHONDONTWRITEBYTECODE=1 python test_mechanism.py
PYTHONDONTWRITEBYTECODE=1 python experiment.py freeze
PYTHONDONTWRITEBYTECODE=1 python experiment.py run
PYTHONDONTWRITEBYTECODE=1 python experiment.py analyze
PYTHONDONTWRITEBYTECODE=1 python experiment.py verify
```

`analyze` 仅离线分析已有轨迹；`verify` 核验冻结输入、历史文件保全和输出哈希。
详细冻结定义、权重和区间见 PROTOCOL.md。无 API 调用、无训练。
