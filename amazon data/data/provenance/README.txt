Amazon Reviews 2023 服装、鞋与珠宝：下载与清洗结果
完成日期：2026-11-04（北京时间）

数据范围
  McAuley Lab Clothing_Shoes_and_Jewelry 全量商品元数据和评论。
  Google 扩展包已完整下载；清洗表保留服装、鞋与珠宝类目。
  商品 7,217,881 件，评论 65,346,226 条，常规女装上衣 339,364 件。
  类目包含服装、鞋、珠宝、手袋、配件等，product_group 区分类目。
  “2023”指数据集版本；评论跨越多个年份。

目录
  raw/：官方原始压缩文件，保持原样。
  clean/：清洗后的 Parquet 表。
  code/：下载、清洗、验证及完整运行代码。
  sources.json：来源网址、文件大小与 SHA256。
  quality_report.json：行数、缺失、关联覆盖率、字段覆盖率和校验结果。
  data_dictionary.json：每张表的字段名与类型。
  womens_tops_preview.jsonl：按商品 ID 哈希固定选取的 200 件商品预览。

清洗规则
  1. 按 JSON 字段读取；解析错误会停止执行，便于定位源数据问题。
  2. 文本去 HTML 标签、合并常见空白、解码常见 HTML 实体；商品标题另保留原文。
     完整原文和所有原字段都保存在 raw/ 压缩文件中。
  3. 商品 ID 去首尾空格、转大写，校验 10 位字母数字格式。
     缺少有效商品 ID 或标题的记录进入 products_rejected。
  4. 重复商品组 ID 优先保留特征和描述较完整的一条，其次按评分人数、源行号排序。
  5. 价格仅保留正的有限数值。缺失或异常价格置空，同时保存 price_original 和异常标记。
     价格为原数据抓取时字段，币种未核实；缺失值保持为空。
  6. 评论校验用户、商品 ID、1—5 整数评分及可解析的毫秒时间戳。
     时间转换为 UTC。异常时间范围与负 helpful_votes 单独标记。
     无正文评论及未验证购买评论保留，可用 text_missing 和 verified_purchase 筛选。
  7. 评论用清洗前源字段生成内容标识，删除完全重复的源记录；同用户的多次不同评论保留。
     reviews_rejected 保存无效记录。review_id 为 MD5 的 UUID 表示。
  8. 评论通过 parent_asin 关联商品组。asin 保存具体变体 ID；缺少元数据的评论仍保留。
     product_review_summary 的下载评论数与商品页 rating_number 分别保存。
     source_row 保存原文件中的记录序号，从 1 开始。
  9. 女装上衣按明确路径筛选：Clothing, Shoes & Jewelry > Women > Clothing > Tops, Tees & Blouses。
     女式 T 恤和衬衫分别按下一层 T-Shirts、Blouses & Button-Down Shirts 生成研究表。
 10. 属性规则仅匹配原始卖家元数据中的明确词句，保留来源字段及完整证据文本。
     care/composition/weight/stretch/fit/neckline/sleeve 分别表示洗护、成分、厚薄或重量、弹性、版型、领型、袖型。
     *_mentions 是词句候选，含否定和可能冲突的表述；具体含义可沿 evidence 回查。
     空数组表示未匹配到。每条证据标记 requires_context_review=true。
 11. Google 的标题、描述、图片描述和特征均为 AI 生成，字段统一使用 _ai 后缀。
     Google product_id 与原始 parent_asin 精确关联，扩展字段单独保存。
     每个重复 Google 商品 ID 保留源文件最早一条。

上衣子集属性覆盖率（匹配到至少一条原文证据）
  care: 231,194 件，占上衣子集 68.1%
  composition: 204,974 件，占上衣子集 60.4%
  fit: 103,781 件，占上衣子集 30.6%
  neckline: 179,535 件，占上衣子集 52.9%
  sleeve: 250,499 件，占上衣子集 73.8%
  stretch: 78,579 件，占上衣子集 23.2%
  weight: 95,054 件，占上衣子集 28.0%

交付表
  attribute_distribution.parquet: 2,305 行，0.0 MB
  google_clothing_ai.parquet: 4,736,162 行，1525.8 MB
  product_review_summary.parquet: 7,216,881 行，166.0 MB
  products.parquet: 7,217,881 行，4195.0 MB
  products_rejected.parquet: 595 行，0.4 MB
  reviews.parquet: 65,346,226 行，7300.0 MB
  reviews_rejected.parquet: 0 行，0.0 MB
  womens_blouses_research.parquet: 93,263 行，43.2 MB
  womens_tops.parquet: 339,364 行，165.7 MB
  womens_tops_attribute_evidence.parquet: 2,115,990 行，64.8 MB
  womens_tops_attributes.parquet: 339,364 行，3.6 MB
  womens_tops_brands.parquet: 16,693 行，0.1 MB
  womens_tops_google_ai.parquet: 221,081 行，56.7 MB
  womens_tops_reviews.parquet: 2,767,701 行，297.4 MB
  womens_tshirts_research.parquet: 96,575 行，43.0 MB

常用表关系
  products：每个 parent_asin 一行。
  reviews：每条有效且去重后的评论一行；parent_asin 可多对一关联 products。
  product_review_summary：每个有评论的 parent_asin 一行。
  womens_tops_attribute_evidence：每条属性原文证据一行。
  womens_tops_attributes：每个上衣 parent_asin 一行，属性词句以列表保存。
  womens_tshirts_research / womens_blouses_research：商品、属性词句和评论统计已关联。
  google_clothing_ai：每个有效的 Google 商品 ID 一行。

校验
  主键、行数平衡、评分范围、价格范围、毫秒时间转换、属性关联及评论汇总检查均已通过。
  详细缺失率、关联缺失数及筛除记录数见 quality_report.json。
  属性为原文规则提取候选，准确率需通过人工抽样估计。

读取示例（Python）
  import pandas as pd
  df = pd.read_parquet(r"C:\Users\22797\Documents\EC研究与投稿\Amazon_Reviews_2023_Clothing\clean\womens_tshirts_research.parquet")

大表按需查询（Python + DuckDB）
  import duckdb
  con = duckdb.connect()
  con.sql("SELECT rating, count(*) FROM read_parquet('clean/reviews.parquet') GROUP BY rating").show()

复现（Windows，Python 3.12 或以上；在本数据文件夹运行）
  python -m pip install -r code/requirements.txt
  python code/run_pipeline.py

来源和引用
  原始数据：https://amazon-reviews-2023.github.io/
  McAuley Lab 托管：https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
  Hou et al. (2024), Bridging Language and Items for Retrieval and Recommendation, arXiv:2403.03952.
  Google 扩展：https://huggingface.co/datasets/google/extended_amazon_2023_dataset
  Google 扩展授权：CC-BY-4.0；其字段由 LLM 基于原元数据和图片描述生成。
  原始数据的使用和引用按原发布方说明执行。
