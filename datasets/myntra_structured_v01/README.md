# 可直接使用的 Myntra 结构化数据集 v0.1

本目录于 2026-11-05 补充发布此前保存在本地的**最终整理版** `catalogue_v01_final`。原数据文件逐字节复制，未重新清洗、筛选、补值或划分。下载仓库后即可读取 CSV/JSONL，无需模型、API 密钥或外部依赖。

## 直接使用

| 文件 | 内容 |
|---|---|
| [catalogue_strict.csv](catalogue/catalogue_strict.csv) · [JSONL](catalogue/catalogue_strict.jsonl) | 471 件核心商品；推荐实验优先使用 |
| [products_all.csv](catalogue/products_all.csv) · [JSONL](catalogue/products_all.jsonl) | 959 个来源商品 ID，保留缺失、歧义和排除原因 |
| [factual_cards.jsonl](catalogue/factual_cards.jsonl) | 471 张中文事实卡，附来源证据 ID |
| [六个品类池](catalogue/pools/) | 女款 Kurtas 214、男款 Kurtas 154、Dresses 67、Tops 21、Tunics 8、Kurtis 7；均有 CSV 和 JSONL |
| [split_manifest.json](catalogue/split_manifest.json) | 固定的商品划分与防泄漏组 |
| [source_claims.jsonl](catalogue/source_claims.jsonl) · [variants.jsonl](catalogue/variants.jsonl) | 18,991 条规格证据和 1,000 条来源尺码/规格记录，含来源字段文本 |
| [SUMMARY.json](catalogue/SUMMARY.json) · [quality_issues.jsonl](catalogue/quality_issues.jsonl) | 覆盖率、清洗统计和质量问题 |

只需要主表时，可在 GitHub 文件页点击 **Raw / Download raw file**；整个数据集随仓库的 **Code → Download ZIP** 一起下载。

从仓库根目录用 Python 标准库读取：

```python
import csv
import json
from pathlib import Path

root = Path("datasets/myntra_structured_v01/catalogue")
with (root / "catalogue_strict.csv").open(encoding="utf-8-sig", newline="") as f:
    products = list(csv.DictReader(f))
print(len(products))  # 471
print(products[0]["neckline"], products[0]["fabric"], products[0]["wash_care"])

# CSV 为扁平表；JSONL 额外保留嵌套来源证据。
with (root / "catalogue_strict.jsonl").open(encoding="utf-8") as f:
    nested_products = [json.loads(line) for line in f if line.strip()]
development = [p for p in nested_products if p["split"] == "development"]
print(len(development))  # 338
```

核心字段为 `neckline`、`sleeve_length`、`fabric`、`wash_care`、`pattern`，另有历史价格、品类、性别、尺码和额外属性。CSV 使用 UTF-8 BOM，属性附带 `*_status`；`unknown`、`ambiguous` 与负标签含义不同。JSONL 的 `attributes.<field>.value` 为规范化标签，`source_labels` 为来源标签。完整字段说明见 [SCHEMA.md](provenance/SCHEMA.md)。

## 保留的划分

| 划分 | 全部商品 | 核心商品 |
|---|---:|---:|
| development | 670 | 338 |
| validation_reserved | 157 | 78 |
| test_reserved | 132 | 55 |
| 合计 | 959 | 471 |

这是商品级划分。实验中的 736 个 Python 案例及每模型 280 个 LLM 案例是另行构造的画像—菜单组合，不能与商品数量混用。本数据目录不含模拟顾客隐藏画像、先验、模型回复或逐案评价真值；实验代码与结果见[实验入口](../../experiments/myntra_results_20261105/README.md)。

## 离线核验与构建代码

```bash
python datasets/myntra_structured_v01/verify_dataset.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s datasets/myntra_structured_v01/reproduction -p test_catalogue.py
```

公开核验检查发布文件哈希、原目录清单、记录解析、CSV/JSONL 主字段对应、原始划分以及六个品类池的完整覆盖，不访问网络或原工作目录。[CHECKS.json](CHECKS.json) 保存本次核验结果；[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) 记录逐文件来源。原始构建器、来源核验器、配置、冻结规则及 29 项语义失败模式测试保存在 [reproduction/](reproduction/)。

如需从原始下载 CSV 重新构建，需另行获得 [固定来源版本](https://huggingface.co/datasets/Gssmc/myntra_dataset/tree/e3037c0e7aba89376ac8ea24f69b416d9d0335cb) 中的 CSV，并核验 SHA256 为 `d8091d2ec14ed95dc887994ce216679069391488fe32905873cbe13bff45ab58`。原 CSV 文件本身未打包；处理后的 `variants.jsonl` 保留了原字段文本。

```bash
python datasets/myntra_structured_v01/reproduction/build_catalogue.py --source /path/to/source.csv --output /tmp/myntra-new-build
python datasets/myntra_structured_v01/reproduction/verify_catalogue.py --source /path/to/source.csv --output /tmp/myntra-new-build --receipt /tmp/myntra-source-check.json
```

输出目录必须为空。构建与核验使用 Python 标准库，不调用模型。

## 来源与适用范围

来源为 `Gssmc/myntra_dataset`，固定 revision `e3037c0e7aba89376ac8ea24f69b416d9d0335cb`，对应 2019 年历史商品记录。来源上传者标注 MIT；原市场内容的权利未由本项目独立核实，本补充不新设第三方数据许可。来源记录见 [SOURCE_RECEIPT.json](provenance/SOURCE_RECEIPT.json)。

这些是商家报告的属性，尚未经过独立人工语义审阅。价格、尺码和库存属于历史快照；币种未知，保持为空；本版本无图像。洗护标签不枚举全部允许方式，面料标签不等于精确成分。完整限制见[原数据卡](provenance/DATASET_CARD.md)。

`provenance/` 中的数据卡、核验及重现收据保留原文，所述“仅本地保存”记录的是早先发布范围。本次另行公开上述整理文件；旧收据不表示公开环境已重新完成原始来源核验。本次没有增加模型调用、训练、人工标注或科学实验。
