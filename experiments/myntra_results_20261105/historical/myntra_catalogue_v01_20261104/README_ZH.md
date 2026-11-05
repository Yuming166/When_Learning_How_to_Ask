# Myntra结构化服饰目录 v0.1

已完成：959个商品ID完整整理；471件通过有限自动一致性检查的成人单件服饰；
保留1,000条尺码/规格记录及全部来源。0模型调用、0训练、0新增人工审阅。

先看[研究报告](REPORT_ZH.md)和[数据说明](DATASET_CARD.md)。

本地文件（数据不纳入Git）：

- [完整本地数据包 ZIP](artifacts/Myntra_Structured_Catalogue_v01.zip)
- [471件核心目录 CSV](artifacts/catalogue_v01_final/catalogue_strict.csv)
- [959个商品完整表 CSV](artifacts/catalogue_v01_final/products_all.csv)
- [女款Kurtas：214件](artifacts/catalogue_v01_final/pools/women_kurtas.csv)
- [男款Kurtas：154件](artifacts/catalogue_v01_final/pools/men_kurtas.csv)
- [连衣裙：67件](artifacts/catalogue_v01_final/pools/women_dresses.csv)
- [事实卡 JSONL](artifacts/catalogue_v01_final/factual_cards.jsonl)
- [全部规格来源](artifacts/catalogue_v01_final/source_claims.jsonl)
- [核验结果](results/VERIFICATION.json)

核心字段：neckline、sleeve_length、fabric、wash_care、pattern。额外保留衣长、
开合方式、版型、透明度、场合、部件面料、历史价格、尺码及来源状态。
CSV的每个属性附带status列；未知/多值歧义不会变成负标签。

这些是商家报告的标签，不是完整物理规格或真人偏好。原文件不含图像和币种。
研究范围、选择规则、缺失分母与限制见[DATASET_CARD.md](DATASET_CARD.md)。
推荐模拟需另外固定画像和购买门槛，允许多件可接受以及不购买。

复现使用Python标准库，见[REPRODUCE.md](REPRODUCE.md)；JSON记录约定见
[SCHEMA.md](SCHEMA.md)及[product.schema.json](schemas/product.schema.json)。
