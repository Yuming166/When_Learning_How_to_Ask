"""Validate final tables and write the delivery documentation and a small preview."""
from pathlib import Path
import json
import datetime as dt
import duckdb

ROOT=Path(__file__).resolve().parents[1]
CLEAN=ROOT/'clean'
def q(x): return "'"+str(x).replace('\\','/').replace("'","''")+"'"

def main():
    c=duckdb.connect()
    c.execute("SET threads=6; SET memory_limit='12GB'; SET preserve_insertion_order=false")
    c.execute(f'SET temp_directory={q(ROOT/"_work")}')
    for name,file in [('p','products'),('r','reviews'),('s','product_review_summary'),('t','womens_tops'),
                      ('a','womens_tops_attributes'),('e','womens_tops_attribute_evidence'),('g','google_clothing_ai')]:
        c.execute(f'CREATE VIEW {name} AS SELECT * FROM read_parquet({q(CLEAN/(file+".parquet"))})')
    checks={}
    queries={
        'product_id_duplicates':'SELECT count(*)-count(DISTINCT parent_asin) FROM p',
        'review_id_duplicates':'SELECT count(*)-count(DISTINCT review_id) FROM r',
        'review_source_row_duplicates':'SELECT count(*)-count(DISTINCT source_row) FROM r',
        'invalid_clean_prices':'SELECT count(*) FROM p WHERE price IS NOT NULL AND (price<=0 OR NOT isfinite(price))',
        'invalid_clean_ratings':'SELECT count(*) FROM r WHERE rating NOT IN(1,2,3,4,5) OR rating IS NULL',
        'invalid_clean_review_dates':'SELECT count(*) FROM r WHERE review_datetime_utc IS NULL OR epoch_ms(review_datetime_utc)<>timestamp_ms',
        'attributes_without_top_product':'SELECT count(*) FROM a ANTI JOIN t USING(parent_asin)',
        'tops_without_attribute_row':'SELECT count(*) FROM t ANTI JOIN a USING(parent_asin)',
        'review_summary_count_difference':'SELECT abs((SELECT count(*) FROM r)-(SELECT sum(review_count) FROM s))',
        'evidence_without_top_product':'SELECT count(*) FROM e ANTI JOIN t USING(parent_asin)',
    }
    for name,sql in queries.items():
        checks[name]=c.execute(sql).fetchone()[0]
        print('CHECK',name,checks[name],flush=True)
        if checks[name]!=0: raise AssertionError(name)
    stats={k:json.loads((ROOT/(k+'_statistics.json')).read_text(encoding='utf-8')) for k in ('metadata','reviews','attributes','google')}
    for k,duplicate in [('metadata','duplicate_parent_asin_rows'),('reviews','exact_source_duplicate_rows')]:
        d=stats[k]
        assert d['raw_rows']==d['valid_rows']+d['invalid_rows']
        assert d['valid_rows']-d[duplicate]==d['clean_products' if k=='metadata' else 'clean_reviews']
    product_groups=dict(c.execute('SELECT product_group,count(*) FROM p GROUP BY 1 ORDER BY 2 DESC').fetchall())
    missing=dict(zip(['price_missing','store_missing','brand_reported_missing','features_missing','description_missing','categories_missing','primary_image_missing'],
       c.execute('''SELECT count(*) FILTER(WHERE price IS NULL),count(*) FILTER(WHERE store IS NULL),count(*) FILTER(WHERE brand_reported IS NULL),
       count(*) FILTER(WHERE len(features)=0),count(*) FILTER(WHERE len(description)=0),count(*) FILTER(WHERE len(categories)=0),
       count(*) FILTER(WHERE primary_image_url IS NULL) FROM p''').fetchone()))
    review_profile=dict(zip(['text_missing','helpful_votes_negative','outside_documented_period','first_review_utc','last_review_utc'],
       c.execute('SELECT count(*) FILTER(WHERE text_missing),count(*) FILTER(WHERE helpful_votes_invalid),count(*) FILTER(WHERE outside_documented_period),min(review_datetime_utc),max(review_datetime_utc) FROM r').fetchone()))
    for filename,leaf in [('womens_tshirts_research','T-Shirts'),('womens_blouses_research','Blouses & Button-Down Shirts')]:
        sql=f'''SELECT t.*,a.* EXCLUDE(parent_asin),
          coalesce(s.review_count,0) AS downloaded_review_count,s.reviewers,s.review_rating_mean,
          s.verified_reviews,s.reviews_with_text,s.first_review_utc,s.last_review_utc
          FROM t LEFT JOIN a USING(parent_asin) LEFT JOIN s USING(parent_asin)
          WHERE t.categories[5]={q(leaf)}'''
        c.execute(f'COPY ({sql}) TO {q(CLEAN/(filename+".parquet"))} (FORMAT PARQUET,COMPRESSION ZSTD)')
    subset_counts={n:c.execute(f'SELECT count(*) FROM read_parquet({q(CLEAN/(n+".parquet"))})').fetchone()[0] for n in ('womens_tshirts_research','womens_blouses_research')}
    preview='''SELECT t.parent_asin,t.title,t.store,t.brand_reported,t.category_path,t.price,
       t.features,t.description,a.* EXCLUDE(parent_asin),coalesce(s.review_count,0) AS downloaded_review_count,
       g.title_ai,g.description_ai,g.derived_features_ai
       FROM t LEFT JOIN a USING(parent_asin) LEFT JOIN s USING(parent_asin) LEFT JOIN g USING(parent_asin)
       ORDER BY hash(t.parent_asin) LIMIT 200'''
    c.execute(f'COPY ({preview}) TO {q(ROOT/"womens_tops_preview.jsonl")} (FORMAT JSON,ARRAY false)')
    brands=c.execute('''SELECT coalesce(brand_reported,store,'(missing)') AS brand_or_store,count(*) AS n
       FROM t GROUP BY 1 ORDER BY n DESC LIMIT 15''').fetchall()
    coverage={k:dict(products=v,share=v/max(stats['attributes']['womens_tops'],1)) for k,v in stats['attributes']['products_with_attribute'].items()}
    files=[]
    dictionary={}
    for f in sorted(CLEAN.glob('*.parquet')):
        n=c.execute(f'SELECT count(*) FROM read_parquet({q(f)})').fetchone()[0]
        files.append(dict(file=f.name,rows=n,bytes=f.stat().st_size))
        dictionary[f.name]=[dict(name=r[0],type=r[1]) for r in c.execute(f'DESCRIBE SELECT * FROM read_parquet({q(f)})').fetchall()]
    report=dict(created_date_beijing='2026-11-04',checks=checks,counts=stats,product_groups=product_groups,
      missing_product_fields=missing,review_profile=review_profile,attribute_coverage=coverage,
      focused_subsets=subset_counts,top_womens_tops_brands_or_stores=brands,files=files)
    (ROOT/'quality_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    (ROOT/'data_dictionary.json').write_text(json.dumps(dictionary,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=stats['metadata']['clean_products'];nr=stats['reviews']['clean_reviews'];nt=stats['attributes']['womens_tops']
    coverage_lines='\n'.join(f'  {k}: {v["products"]:,} 件，占上衣子集 {v["share"]:.1%}' for k,v in sorted(coverage.items()))
    file_lines='\n'.join(f'  {f["file"]}: {f["rows"]:,} 行，{f["bytes"]/1e6:.1f} MB' for f in files)
    readme=f'''Amazon Reviews 2023 服装、鞋与珠宝：下载与清洗结果
完成日期：2026-11-04（北京时间）

数据范围
  McAuley Lab Clothing_Shoes_and_Jewelry 全量商品元数据和评论。
  Google 扩展包已完整下载；清洗表保留服装、鞋与珠宝类目。
  商品 {rows:,} 件，评论 {nr:,} 条，常规女装上衣 {nt:,} 件。
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
{coverage_lines}

交付表
{file_lines}

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
  df = pd.read_parquet(r"{CLEAN/'womens_tshirts_research.parquet'}")

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
'''
    (ROOT/'README.txt').write_text(readme,encoding='utf-8')
    c.close()
    print('VALIDATION_COMPLETE',json.dumps(dict(products=rows,reviews=nr,womens_tops=nt,subsets=subset_counts)),flush=True)

if __name__=='__main__': main()
