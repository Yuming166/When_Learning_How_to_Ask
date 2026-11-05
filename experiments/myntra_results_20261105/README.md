# Myntra：Python 与三种 LLM 顾客通道的结果和机制消融

本发布对应原 Myntra 六字段偏好获取实验：**Python 合并面板 736 案例/288画像；LLM 每模型同一 280 案例/48画像**。推荐策略均为 training-free Python。Luna、DeepSeek V4.1 Flash、GLM-5.3 提供结构化顾客字段回答。

整理好的商品数据随后单独补充发布，见 **[Myntra结构化数据集](../../datasets/myntra_structured_v01/README.md)**：959个商品、471件核心商品，包含CSV/JSONL、六个品类池、事实卡和固定商品划分。

这与仓库另一个[目录匹配实验](../catalogue_robustness_20261105/README.md)是不同实验：该实验使用 Myntra/Amazon、576菜单和64种二元偏好。本发布保留它及论文原样，不合并两者样本或结论。

## 结果入口

- [完整结果与统计边界](RESULTS_ZH.md)：原四策略、三模型复核、Python与LLM关键消融、两种权重及失败账目。
- [Python/LLM测试方法](METHODS_ZH.md)：信息边界、DV目标、提问预算、回答库、失败停问和聚类统计。
- [Python机制消融原报告](historical/myntra_python_mechanism_ablation_v01_20261105/results/REPORT_ZH.md) · [PDF曲线](historical/myntra_python_mechanism_ablation_v01_20261105/results/MECHANISM_ABLATION.pdf)。
- [三模型机制消融原报告](historical/myntra_llm_mechanism_ablation_v01_20261105/results/REPORT_ZH.md) · [PDF曲线](historical/myntra_llm_mechanism_ablation_v01_20261105/results/THREE_MODEL_ABLATION.pdf)。
- [原保留集报告](historical/myntra_heldout_confirmation_v01_20261104/results/REPORT_ZH.md)：保留测试集预算5相对Decision-Set IG的弱收益和原同时区间判定。

## 可直接运行的公开复现

从仓库根目录运行，Python 3.10+，依赖见仓库根目录 `requirements.txt`：

```bash
python -m pip install -r requirements.txt
python experiments/myntra_results_20261105/reproduce.py verify
PYTHONDONTWRITEBYTECODE=1 python experiments/myntra_results_20261105/test_public_release.py
python experiments/myntra_results_20261105/reproduce.py summary --output /tmp/myntra-summary.json
python experiments/myntra_results_20261105/reproduce.py analyze --output /tmp/myntra-reanalysis
```

`summary` 重算各方法计数、准确率、失败率和实际成本。`analyze` 从白名单投影记录重算Python的合并/划分/品类统计、两种权重，以及三个LLM共享画像抽样的点态和同时区间；逐项对照已保存分析，容差 `1e-12`。全部在CPU离线执行，无模型调用、训练或网络请求。

本结果包支持**数值统计复现和toy机制测试**。商品目录现已在上述独立数据目录发布；隐藏偏好/先验、逐画像序列化请求、原始模型回答与运行日志仍未上传，因此本入口不重新生成真实模型回答，也不从原商品输入重新运行全部策略。通用自有系统模板和提示构造代码保留，用于说明方法。原始来源/回答完整性检查收据描述本地完整实验，不是结果包重新完成了这些检查。

## 代码与文件

| 文件 | 用途 |
|---|---|
| `code/engine.py`、`code/environment.py`、`policy_replay.py` | 原策略、评价器和失败重放逻辑；可接受另行准备的输入，公开测试使用toy输入 |
| `statistics_python.py`、`statistics_llm.py` | 从已执行版本逐字提取的统计函数，另加相对路径导入包装 |
| `records/python.csv`、`records/llm.csv` | 25,760和29,400条数值投影；保留聚类标识、完整0–6预算、实际成本和失败路径 |
| `historical/` | 16个实验的原代码、配置、协议、报告、汇总与冻结记录；包括失败和被取代版本 |
| `SOURCE_MANIFEST.json`、`PROJECTION.json` | 原文件哈希、转换和数值投影来源 |
| `MANIFEST.json`、`CHECKS.json`、`EXCLUSIONS.json` | 本公开包的完整性、发布检查和排除说明 |

`historical/` 是原始来源快照，保留原绝对路径和对未公开输入的引用。模型采集代码也位于这些快照中：[Luna](historical/myntra_luna_48profile_policy_v01_20261105/luna_48_policy_comparison.py)、[DeepSeek](historical/myntra_deepseek_48profile_policy_v02_20261105/experiment.py)、[GLM与流式传输](historical/myntra_glm53_48profile_policy_v02_20261105/experiment.py)。这些历史入口依赖本地完整输入，不能直接当作新运行的便携命令。未来采集应另设实验目录和预算；API凭据由环境或交互输入提供，未包含在发布包。

数值投影不含商品属性、购买目标集合、隐藏偏好、实例化提示或模型回复；商品动作转为案例内一致的哈希，跨模型/方法/预算的动作相同性保持。它保留原评价结果，不能替代用原隐藏真值重新评分。第三方数据条款及既有[目录数据卡](historical/myntra_catalogue_v01_20261104/DATASET_CARD.md)的再分发边界保持不变；本发布不新设项目或数据许可。
