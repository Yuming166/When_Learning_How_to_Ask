# Amazon data：清洗商品、实验结果与复现

本目录汇总本轮 Amazon 工作，保留原有仓库目录。新增内容不包含 Gemini 实验结果。当前主实验使用 49 件 Amazon 商品、64 种六字段二选一画像和 576 个菜单；每个菜单 16 件商品。

## 直接查看结果

| 文件 | 内容 |
|---|---|
| [01_Python_两数据集.xlsx](tables/01_Python_两数据集.xlsx) | 已有 Myntra / Amazon Python 主实验，预算 3、4、5 |
| [02_Luna_两数据集.xlsx](tables/02_Luna_两数据集.xlsx) | 已有两数据集 Luna 主实验 |
| [03_Amazon_三模型主实验.xlsx](tables/03_Amazon_三模型主实验.xlsx) · [CSV](tables/03_Amazon_三模型主实验.csv) | Amazon Luna / DeepSeek V4.1 Flash / GLM-5.3：固定顺序、画像信息增益、决策集合信息增益、DV |
| [04_Amazon_三模型消融.xlsx](tables/04_Amazon_三模型消融.xlsx) | 完整 DV 与固定初始顺序 DV；全部 0–6 预算另表保留 |
| [05_Amazon_Python三项消融及LLM汇总.xlsx](tables/05_Amazon_Python三项消融及LLM汇总.xlsx) | Python 三项消融与三模型消融；点态 95% 区间及校正区间 |

01、02 是已完成实验的便于阅读副本；05 的 LLM 部分汇总 04，不是额外实验。03 删除了原本仅作比较的 Gemini 列，其余数值保持原样。

## 清洗后的数据

- [328 件逐项核对衬衫 CSV](data/audited_blouses/products_328.csv) · [Parquet](data/audited_blouses/实验商品.parquet)：早期实验商品池，含卖家属性和价格。
- [逐项核对证据](data/audited_blouses/逐项核对证据.parquet)、[待排查商品](data/audited_blouses/待排查商品.parquet)、[核对说明](data/audited_blouses/核对说明.txt)：保留证据、排除原因和高领修正记录。
- [当前 Amazon 49 商品 CSV](data/frozen_inputs/amazon_products_49.csv)、[576 菜单 CSV](data/frozen_inputs/amazon_menus_576.csv)、[完整 Amazon 设置](data/frozen_inputs/amazon.json)：直接用于当前六字段结果。
- [原始冻结输入](data/frozen_inputs/experiment_inputs.json)：与仓库已有双数据集复现包逐字一致，保留原哈希。其中亦含原 Myntra 和九偏好设置。

328 商品池与当前 49 商品输入是不同层次的对象。表中的 64 是画像数，576 是菜单数，均不是商品数。当前评分是可接受商品或正确不购买；高煜明原版 Myntra 的 48 画像、280 案例及其最优商品评分仍在原目录分别报告。

## 运行与核对

在完整仓库中安装依赖后执行：

```bash
python -m pip install numpy pandas requests pyarrow
python "amazon data/code/reproduce.py"
```

入口仅离线读取数据和已有回复，不调用任何模型。它复用 `experiments/catalogue_robustness_20261105/reproduction` 中已发布的策略代码，检查全部 576 菜单的三模型主实验、三模型动态选问消融和 Python 三项消融，并重算消融的 5000 次配对 bootstrap 区间。核验结果写入 `CHECKS.json`。

`experiments/` 保留字面回复、API 返回型号和用量、协议、结果、逐例数值以及原执行脚本。原执行脚本保留产生环境的相对目录，发布后的运行入口统一为上面的 `code/reproduce.py`。Luna 协议及汇总保留历史两数据集元数据，本目录仅重复打包 Amazon 回复；完整原两数据集回复仍在原目录。

## 结果解释和失败规则

成功率按固定先验加权 64 个画像，再对菜单等权平均。全部画像保留。GLM 首批回复带 Markdown 代码块，沿用原严格 JSON 解析，16 个画像无效；其余 48 个画像全部符合。选到无效回答的轨迹计失败，两种消融策略使用同一规则。Luna、DeepSeek 全部 384 项字段回答符合画像，故其结果与 Python 真值模拟一致。

Python 两项信息增益消融替换选问目标；固定初始顺序消融移除收到回答后的问题重排，保留回答更新和最终推荐。消融表主展示点态区间；明细另给每组九项比较的 Bonferroni 校正区间。区间按原菜单种子分层，以固定商品、画像、先验和这次回答库为条件，三模型共享菜单抽样。

## 来源与全量数据

Amazon 来源为 McAuley Lab 的 Amazon Reviews 2023 / Clothing_Shoes_and_Jewelry。完整来源 URL、文件哈希、字段和质量统计保存在 [provenance](data/provenance/)。其中 README 描述原本地全量清洗工程；本次发布实际范围以本目录和 `MANIFEST.json` 为准。

全量商品 7,217,881 件及评论 65,346,226 条不在本包重复上传；93,263 件衬衫、96,575 件 T 恤的完整研究表亦保留在本地。需要扩展时可按来源重新下载，清洗及审计代码见 `data/rebuild/code/`。运行全量构建时应另建工作目录，把其中 `code` 复制过去，再执行 `code/run_pipeline.py`；该步骤会下载大型原始数据，与离线表格复现分开。

历史价格与商品属性按原数据保存；来源和第三方许可沿用原发布方说明，本包不另授第三方商品内容许可。清洗全量工程中的 Google AI 扩展字段另行标记，当前打包范围见清单。
