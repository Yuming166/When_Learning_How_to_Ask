"""Reproducible cleaning. Run stages: metadata, attributes, google, reviews, report.

Requires Python 3.12+, duckdb>=1.4, pyarrow, orjson, requests.
All generated tables are Parquet; the source archives remain unchanged.
"""
from pathlib import Path
import argparse
import concurrent.futures as cf
import errno
import gzip
import html
import json
import re
import shutil
import threading
import time
import zipfile
import msvcrt
import duckdb
import orjson
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PART_ROWS = 500000
RAW, CLEAN, WORK = (ROOT / x for x in ('raw', 'clean', '_work'))
for p in (CLEAN, WORK):
    p.mkdir(exist_ok=True)

def q(x):
    return "'" + str(x).replace('\\', '/').replace("'", "''") + "'"

def connect():
    c = duckdb.connect()
    c.execute("SET threads=6; SET memory_limit='12GB'; SET preserve_insertion_order=false")
    c.execute('SET enable_progress_bar=true; SET enable_progress_bar_print=false')
    c.execute(f'SET temp_directory={q(WORK)}')
    c.execute(r"""CREATE MACRO txt(s) AS nullif(trim(regexp_replace(
        regexp_replace(replace(replace(replace(replace(replace(replace(replace(
        coalesce(s,''),'&nbsp;',' '),'&amp;','&'),'&quot;','"'),'&#39;',chr(39)),
        '&#x27;',chr(39)),'&lt;','<'),'&gt;','>'), '<[^>]*>', ' ', 'g'),
        '[\s\x00-\x08\x0B\x0C\x0E-\x1F]+',' ','g')), '')""")
    return c

def copy(c, sql, path):
    t = time.monotonic()
    print('WRITING', path.name, flush=True)
    stop=threading.Event()
    def progress():
        while not stop.wait(25):
            print('PROCESSING',path.name,round(c.query_progress(),1),'percent',flush=True)
    threading.Thread(target=progress,daemon=True).start()
    try:
        c.execute(f'COPY ({sql}) TO {q(path)} (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)')
    finally:
        stop.set()
    print('WROTE', path.name, f'{time.monotonic()-t:.1f}s', flush=True)

def unpack_gzip(filename):
    src=RAW/filename
    dst=WORK/filename.removesuffix('.gz')
    ready=WORK/(filename+'.unpacked.json')
    if ready.exists() and dst.exists():
        state=json.loads(ready.read_text())
        if state=={'compressed_bytes':src.stat().st_size,'uncompressed_bytes':dst.stat().st_size}:
            return dst
    print('DECOMPRESSING',filename,flush=True)
    # Python zlib validates the gzip CRC. An ordinary JSONL file supports parallel JSON scans.
    n=0
    with gzip.open(src,'rb') as inp,dst.open('wb') as out:
        while buf:=inp.read(16*1024*1024):
            out.write(buf);n+=len(buf)
            if n%(1024*1024*1024)==0: print('DECOMPRESSED',filename,round(n/1e9,1),'GB',flush=True)
    ready.write_text(json.dumps({'compressed_bytes':src.stat().st_size,'uncompressed_bytes':n}))
    return dst

def parallel_metadata_copy(sql,src):
    parts_dir=WORK/'metadata_json_parts'
    output_dir=WORK/'metadata_normalized_parts'
    parts_dir.mkdir(exist_ok=True);output_dir.mkdir(exist_ok=True)
    parts=[];rows=0;out=None
    try:
        with src.open('rb') as f:
            for line in f:
                if not line.strip():continue
                if rows%500000==0:
                    if out:out.close()
                    part=parts_dir/f'part_{len(parts):04d}.jsonl'
                    parts.append((part,rows));out=part.open('wb',buffering=1024*1024)
                out.write(line);rows+=1
    finally:
        if out:out.close()
    def normalize(item):
        i,(part,offset)=item;pc=connect()
        pc.execute("SET threads=1; SET memory_limit='1GB'")
        query=sql.replace(q(src),q(part)).replace('ordinality AS source_row',f'ordinality+{offset} AS source_row')
        try:
            pc.execute(f'COPY ({query}) TO {q(output_dir/f"part_{i:04d}.parquet")} (FORMAT PARQUET,COMPRESSION ZSTD,ROW_GROUP_SIZE 100000)')
        finally:pc.close()
    with cf.ThreadPoolExecutor(6) as pool:
        futures=[pool.submit(normalize,x) for x in enumerate(parts)]
        for i,f in enumerate(cf.as_completed(futures),1):
            f.result();print('METADATA_PARTS_NORMALIZED',i,'/',len(parts),flush=True)
    return output_dir/'*.parquet'

def stats(stage, values):
    (ROOT / (stage + '_statistics.json')).write_text(json.dumps(values, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(stage, json.dumps(values, default=str), flush=True)

def metadata():
    c = connect()
    src = unpack_gzip('meta_Clothing_Shoes_and_Jewelry.jsonl.gz')
    columns = "{'main_category':'VARCHAR','title':'VARCHAR','average_rating':'DOUBLE','rating_number':'BIGINT','features':'VARCHAR[]','description':'VARCHAR[]','price':'VARCHAR','store':'VARCHAR','categories':'VARCHAR[]','details':'JSON','parent_asin':'VARCHAR','images':'JSON'}"
    sql=f"""WITH a AS (
        SELECT ordinality AS source_row, upper(trim(parent_asin)) AS parent_asin,
          txt(title) AS title, title AS title_original, txt(store) AS store,
          txt(json_extract_string(details, '$.Brand')) AS brand_reported,
          txt(main_category) AS main_category,
          list_filter(list_transform(coalesce(categories,[]), lambda x: txt(x)),lambda x: x IS NOT NULL) AS categories,
          list_filter(list_transform(coalesce(features,[]), lambda x: txt(x)),lambda x: x IS NOT NULL) AS features,
          list_filter(list_transform(coalesce(description,[]), lambda x: txt(x)),lambda x: x IS NOT NULL) AS description,
          details AS details_json, price AS price_original,
          CASE WHEN try_cast(price AS DOUBLE)>0 AND isfinite(try_cast(price AS DOUBLE))
               THEN try_cast(price AS DOUBLE) END AS price,
          CASE WHEN average_rating BETWEEN 1 AND 5 THEN average_rating END AS average_rating,
          CASE WHEN rating_number>=0 THEN rating_number END AS rating_number,
          coalesce(json_extract_string(images,'$[0].hi_res'),json_extract_string(images,'$[0].large')) AS primary_image_url
        FROM read_json({q(src)},format='newline_delimited',columns={columns}, maximum_object_size=67108864) WITH ORDINALITY
      ), b AS (
        SELECT *, array_to_string(categories,' > ') AS category_path,
          array_to_string(features,' | ') AS features_text,
          array_to_string(description,' | ') AS description_text,
          list_contains(categories,'Clothing') AS is_apparel,
          list_slice(categories,1,4)=['Clothing, Shoes & Jewelry','Women','Clothing','Tops, Tees & Blouses'] AS is_womens_top,
          CASE WHEN list_contains(categories,'Shoes') THEN 'shoes'
               WHEN list_contains(categories,'Jewelry') THEN 'jewelry'
               WHEN list_contains(categories,'Watches') THEN 'watches'
               WHEN list_has_any(categories,['Handbags & Wallets','Luggage & Travel Gear']) THEN 'bags_luggage'
               WHEN list_contains(categories,'Clothing') THEN 'apparel'
               WHEN list_has_any(categories,['Accessories','Shoe, Jewelry & Watch Accessories']) THEN 'accessories'
               ELSE 'other_or_unknown' END AS product_group,
          regexp_full_match(coalesce(parent_asin,''),'[A-Z0-9]{{10}}') AND title IS NOT NULL AS valid_product,
          price_original IS NOT NULL AND (try_cast(price_original AS DOUBLE) IS NULL OR try_cast(price_original AS DOUBLE)<=0 OR NOT isfinite(try_cast(price_original AS DOUBLE))) AS price_invalid
        FROM a
      ) SELECT * FROM b"""
    stage=parallel_metadata_copy(sql,src)
    c.execute(f'CREATE VIEW m AS SELECT * FROM read_parquet({q(stage)})')
    n, valid, distinct = c.execute('SELECT count(*),count(*) FILTER(WHERE valid_product),count(DISTINCT parent_asin) FILTER(WHERE valid_product) FROM m').fetchone()
    # Stable selection of the most informative metadata record for a repeated parent ASIN.
    if valid == distinct:
        selected='SELECT * EXCLUDE(valid_product) FROM m WHERE valid_product'
    else:
        selected="""WITH keep AS (
          SELECT source_row FROM m WHERE valid_product
          QUALIFY row_number() OVER(PARTITION BY parent_asin ORDER BY
          len(features)+len(description) DESC,rating_number DESC NULLS LAST,source_row)=1)
          SELECT m.* EXCLUDE(valid_product) FROM m SEMI JOIN keep USING(source_row)"""
    copy(c, selected, CLEAN / 'products.parquet')
    copy(c, 'SELECT * FROM m WHERE NOT valid_product', CLEAN / 'products_rejected.parquet')
    stats('metadata', dict(raw_rows=n, valid_rows=valid, clean_products=distinct,
                          invalid_rows=n-valid, duplicate_parent_asin_rows=valid-distinct))
    c.close()

SPACE = re.compile(r'\s+')
TAG = re.compile(r'<[^>]*>')
def text(x):
    return SPACE.sub(' ', html.unescape(TAG.sub(' ', str(x or '')))).strip()

PATTERNS = {
 'care': re.compile(r'\b(?:(?:do\s+not|don[\u2019\x27]t|not|never)\s+)?(?:machine[ -]wash(?:able|ing)?|hand[ -]wash(?:able|ing)?|dry[ -]clean(?:ing|able)?|tumble[ -]dry|line[ -]dry|hang[ -]dry|lay\s+flat\s+to\s+dry|do\s+not\s+bleach|do\s+not\s+iron)\b', re.I),
 'composition': re.compile(r'\b(?:100(?:\.0+)?|[1-9]?\d(?:\.\d+)?)\s*%\s*(?:organic\s+|recycled\s+|combed\s+|pima\s+|ring[ -]spun\s+)?(?:cotton|polyester|spandex|elastane|lycra|rayon|viscose|modal|lyocell|tencel|linen|flax|nylon|polyamide|wool|silk|acrylic|bamboo|cashmere|polyurethane)\b', re.I),
 'weight': re.compile(r'\b(?:light[ -]?weight|mid[ -]?weight|medium[ -]?weight|heavy[ -]?weight|thin\s+fabric|thick\s+fabric)\b', re.I),
 'stretch': re.compile(r'\b(?:(?:no|non|not)[ -])?stretch(?:y|able)?\b|\b(?:four|4|two|2)[ -]way[ -]stretch\b', re.I),
 'fit': re.compile(r'\b(?:relaxed|regular|classic|slim|loose|fitted|oversized|athletic|tailored|standard)\s+fit\b|\b(?:loose[ -]fitting|form[ -]fitting|bodycon)\b', re.I),
 'neckline': re.compile(r'\b(?:v[ -]neck|crew[ -]neck|round[ -]neck|scoop[ -]neck|boat[ -]neck|collared\s+neck|turtleneck|mock\s+neck|henley)\b', re.I),
 'sleeve': re.compile(r'\b(?:long[ -]sleeve(?:d)?|short[ -]sleeve(?:d)?|sleeveless|cap[ -]sleeve(?:d)?|three[ -]quarter\s+sleeve(?:d)?|3/4\s+sleeve(?:d)?)\b', re.I),
}
HIGH_NECK = re.compile(r'\bhigh[\s\-‐‑‒–—]*(?:neck(?:line|ed)?|collar(?:ed)?)\b', re.I)

def attribute_matches(row):
    evidence = []
    # Details may contain literal care/material specifications; administrative fields are excluded.
    sources = [('title', row['title'])]
    sources += [(f'features[{i}]', s) for i, s in enumerate(row['features'] or [])]
    sources += [(f'description[{i}]', s) for i, s in enumerate(row['description'] or [])]
    details = orjson.loads(row['details_json'] or '{}')
    if isinstance(details, dict):
        for k, v in details.items():
            if re.search(r'fabric|material|care|fit|neck|sleeve|stretch|weight', k, re.I) and not re.search(r'package|shipping|item weight', k, re.I):
                sources.append(('details.' + k, text(v)))
    seen = set()
    for source, passage in sources:
        if not passage:
            continue
        patterns = list(PATTERNS.items())
        if 'Blouses & Button-Down Shirts' in (row.get('categories') or []):
            patterns.append(('neckline', HIGH_NECK))
        for attribute, pattern in patterns:
            for m in pattern.finditer(passage):
                value = m.group(0).lower()
                key = (attribute, value, source)
                if key in seen:
                    continue
                seen.add(key)
                evidence.append(dict(parent_asin=row['parent_asin'], attribute=attribute,
                  value=value, source_field=source, evidence=passage,
                  evidence_type='seller_metadata_rule_match', requires_context_review=True))
    return evidence

EVIDENCE_SCHEMA = pa.schema([
    ('parent_asin',pa.string()),('attribute',pa.string()),('value',pa.string()),
    ('source_field',pa.string()),('evidence',pa.string()),('evidence_type',pa.string()),
    ('requires_context_review',pa.bool_())])

def attributes():
    c = connect()
    src = CLEAN / 'products.parquet'
    copy(c, f'SELECT * FROM read_parquet({q(src)}) WHERE is_womens_top', CLEAN / 'womens_tops.parquet')
    out = CLEAN / 'womens_tops_attribute_evidence.parquet'
    total = 0
    with pq.ParquetWriter(out,EVIDENCE_SCHEMA,compression='zstd') as w:
        for batch in pq.ParquetFile(CLEAN/'womens_tops.parquet').iter_batches(batch_size=10000,columns=['parent_asin','title','features','description','details_json','categories']):
            matches=[]
            for row in batch.to_pylist():
                matches.extend(attribute_matches(row))
            if matches:
                w.write_table(pa.Table.from_pylist(matches,schema=EVIDENCE_SCHEMA))
            total += len(batch)
            if total % 100000 == 0:
                print('ATTRIBUTE_PRODUCTS', total, flush=True)
    c.execute(f'CREATE VIEW e AS SELECT * FROM read_parquet({q(out)})')
    fields = ','.join(f"coalesce(list(DISTINCT value ORDER BY value) FILTER(WHERE attribute='{a}'),[]) AS {a}_mentions" for a in PATTERNS)
    copy(c, f"""SELECT p.parent_asin,{fields} FROM read_parquet({q(CLEAN/'womens_tops.parquet')}) p
       LEFT JOIN e USING(parent_asin) GROUP BY p.parent_asin""",CLEAN/'womens_tops_attributes.parquet')
    copy(c, 'SELECT attribute,value,count(DISTINCT parent_asin) AS products FROM e GROUP BY ALL ORDER BY attribute,products DESC', CLEAN/'attribute_distribution.parquet')
    copy(c, f"""SELECT coalesce(brand_reported,store,'(missing)') AS brand_or_store,
       count(*) AS products,count(*) FILTER(WHERE price IS NOT NULL) AS with_price
       FROM read_parquet({q(CLEAN/'womens_tops.parquet')}) GROUP BY 1 ORDER BY products DESC""",CLEAN/'womens_tops_brands.parquet')
    coverage = dict(c.execute('SELECT attribute,count(DISTINCT parent_asin) FROM e GROUP BY 1').fetchall())
    stats('attributes',dict(womens_tops=total,products_with_attribute=coverage,
       evidence_rows=c.execute('SELECT count(*) FROM e').fetchone()[0]))
    c.close()

def google():
    archive = RAW / 'extended_amazon2023_dataset.jsonl.zip'
    stage=WORK/'google_clothing.parquet'
    unpacked=WORK/'google_extension.jsonl'
    with zipfile.ZipFile(archive) as z:
        names=[x for x in z.namelist() if x.endswith('.jsonl') and not x.startswith('__MACOSX/') and not Path(x).name.startswith('._')]
        if len(names)!=1:
            raise ValueError('Unexpected Google ZIP members')
        # Stream the data member; macOS resource-fork files are archive metadata.
        # Reading to EOF also verifies the ZIP member's CRC.
        with z.open(names[0]) as f,unpacked.open('wb') as out:
            shutil.copyfileobj(f,out,length=16*1024*1024)
    c=connect()
    counts=dict(c.execute(f"SELECT data_source,count(*) FROM read_json({q(unpacked)},format='newline_delimited',columns={{'data_source':'VARCHAR'}}) GROUP BY 1").fetchall())
    cols="{'data_source':'VARCHAR','product_id':'VARCHAR','image_description':'VARCHAR','title_to_display':'VARCHAR','description_to_display':'VARCHAR','derived_features':'VARCHAR[]'}"
    copy(c,f"""SELECT upper(trim(product_id)) AS parent_asin,data_source,
         txt(image_description) AS image_description_ai,txt(title_to_display) AS title_ai,
         txt(description_to_display) AS description_ai,
         list_filter(list_transform(coalesce(derived_features,[]),lambda x: txt(x)),lambda x: x IS NOT NULL) AS derived_features_ai,
         ordinality AS source_row FROM read_json({q(unpacked)},format='newline_delimited',columns={cols}) WITH ORDINALITY
         WHERE data_source IN ('Clothing, Shoes & Jewelry','Clothing_Shoes_and_Jewelry')""",stage)
    c.execute(f'CREATE VIEW g AS SELECT * FROM read_parquet({q(stage)})')
    n=c.execute('SELECT count(*) FROM g').fetchone()[0]
    copy(c,"""WITH keep AS (SELECT min(source_row) AS source_row FROM g
         WHERE regexp_full_match(parent_asin,'[A-Z0-9]{10}') GROUP BY parent_asin)
         SELECT g.* FROM g SEMI JOIN keep USING(source_row)""",CLEAN/'google_clothing_ai.parquet')
    while not (ROOT/'metadata_statistics.json').exists():
        time.sleep(5)
    copy(c,f"""SELECT p.parent_asin,g.* EXCLUDE(parent_asin) FROM read_parquet({q(CLEAN/'products.parquet')}) p
        JOIN read_parquet({q(CLEAN/'google_clothing_ai.parquet')}) g USING(parent_asin) WHERE p.is_womens_top""",CLEAN/'womens_tops_google_ai.parquet')
    matched=c.execute(f"SELECT count(*) FROM read_parquet({q(CLEAN/'google_clothing_ai.parquet')}) g SEMI JOIN read_parquet({q(CLEAN/'products.parquet')}) p USING(parent_asin)").fetchone()[0]
    cleaned=c.execute(f'SELECT count(*) FROM read_parquet({q(CLEAN/"google_clothing_ai.parquet")})').fetchone()[0]
    invalid_ids=c.execute("SELECT count(*) FROM g WHERE NOT coalesce(regexp_full_match(parent_asin,'[A-Z0-9]{10}'),false)").fetchone()[0]
    stats('google',dict(archive_rows_by_category=dict(counts),clothing_rows=n,
        clean_clothing_products=cleaned,matched_to_original_metadata=matched,
        unmatched_to_original_metadata=cleaned-matched,
        invalid_id_rows=invalid_ids,duplicate_product_id_rows=n-invalid_ids-cleaned,
        note='All *_ai fields are LLM-generated; product_id is joined to parent_asin without fuzzy matching.'))
    c.close()

def reviews():
    c=connect()
    # Independent parts preserve exact source ordinals and allow six JSON scans at once.
    # DuckDB's global WITH ORDINALITY otherwise serializes a single large scan.
    part_dir=WORK/'review_json_parts'
    part_dir.mkdir(exist_ok=True)
    parts=[]
    rows=0
    out=None
    print('DECOMPRESSING_AND_PARTITIONING_REVIEWS',flush=True)
    try:
        with gzip.open(RAW/'Clothing_Shoes_and_Jewelry.jsonl.gz','rb') as f:
            for line in f:
                if not line.strip(): continue
                if rows%REVIEW_PART_ROWS==0:
                    if out: out.close()
                    part=part_dir/f'part_{len(parts):04d}.jsonl'
                    parts.append((part,rows))
                    out=part.open('wb',buffering=1024*1024)
                    if rows%5000000==0: print('REVIEW_INPUT_ROWS',rows,flush=True)
                out.write(line)
                rows+=1
    finally:
        if out: out.close()
    src=WORK/'__REVIEW_PART__.jsonl'
    cols="{'rating':'DOUBLE','title':'VARCHAR','text':'VARCHAR','images':'JSON','asin':'VARCHAR','parent_asin':'VARCHAR','user_id':'VARCHAR','timestamp':'BIGINT','sort_timestamp':'BIGINT','helpful_vote':'BIGINT','helpful_votes':'BIGINT','verified_purchase':'BOOLEAN'}"
    stage_dir=WORK/'review_normalized_parts'
    stage_dir.mkdir(exist_ok=True)
    stage=stage_dir/'*.parquet'
    sql=f"""WITH a AS (
       SELECT ordinality AS source_row,
         md5(to_json(struct_pack(rating:=rating,title:=title,text:=text,images:=images,asin:=asin,
              parent_asin:=parent_asin,user_id:=user_id,timestamp:=timestamp,sort_timestamp:=sort_timestamp,
              helpful_vote:=helpful_vote,helpful_votes:=helpful_votes,verified_purchase:=verified_purchase)))::UUID AS review_id,
         trim(user_id) AS user_id, upper(trim(asin)) AS asin,upper(trim(parent_asin)) AS parent_asin,
         rating,txt(title) AS review_title,txt(text) AS review_text,
         coalesce(timestamp,sort_timestamp) AS timestamp_ms,
         coalesce(helpful_vote,helpful_votes) AS helpful_votes,verified_purchase,
         images AS images_json
       FROM read_json({q(src)},format='newline_delimited',columns={cols},maximum_object_size=67108864) WITH ORDINALITY
     ) SELECT *,
       CASE WHEN timestamp_ms BETWEEN -2208988800000 AND 4102444800000 THEN epoch_ms(timestamp_ms) END AS review_datetime_utc,
       regexp_full_match(coalesce(parent_asin,''),'[A-Z0-9]{{10}}') AND regexp_full_match(coalesce(asin,''),'[A-Z0-9]{{10}}')
           AND nullif(user_id,'') IS NOT NULL AND rating IN (1,2,3,4,5)
           AND timestamp_ms BETWEEN -2208988800000 AND 4102444800000 AS valid_review,
       review_text IS NULL AS text_missing,
       helpful_votes<0 AS helpful_votes_invalid,
       timestamp_ms<epoch_ms(TIMESTAMP '1996-05-01') OR timestamp_ms>=epoch_ms(TIMESTAMP '2023-10-01') AS outside_documented_period
       FROM a"""
    def normalize_part(item):
        i,(part,offset)=item
        pc=connect()
        pc.execute("SET threads=1; SET memory_limit='1GB'")
        part_sql=sql.replace(q(src),q(part)).replace('ordinality AS source_row',f'ordinality+{offset} AS source_row')
        dst=stage_dir/f'part_{i:04d}.parquet'
        try:
            pc.execute(f'COPY ({part_sql}) TO {q(dst)} (FORMAT PARQUET,COMPRESSION ZSTD,ROW_GROUP_SIZE 100000)')
        finally:
            pc.close()
    with cf.ThreadPoolExecutor(6) as pool:
        futures=[pool.submit(normalize_part,item) for item in enumerate(parts)]
        for i,future in enumerate(cf.as_completed(futures),1):
            future.result()
            if i%10==0 or i==len(parts): print('REVIEW_PARTS_NORMALIZED',i,'/',len(parts),flush=True)
    c.execute(f'CREATE VIEW r AS SELECT * FROM read_parquet({q(stage)})')
    n,valid,unique=c.execute('SELECT count(*),count(*) FILTER(WHERE coalesce(valid_review,false)), count(DISTINCT review_id) FILTER(WHERE coalesce(valid_review,false)) FROM r').fetchone()
    # Source-content hash covers every field in the published review schema, before text normalization.
    if valid == unique:
        selected='SELECT * EXCLUDE(valid_review) FROM r WHERE valid_review'
    else:
        selected="""WITH keep AS (SELECT min(source_row) AS source_row FROM r
           WHERE valid_review GROUP BY review_id)
           SELECT r.* EXCLUDE(valid_review) FROM r SEMI JOIN keep USING(source_row)"""
    copy(c,selected,CLEAN/'reviews.parquet')
    copy(c,'SELECT * FROM r WHERE NOT coalesce(valid_review,false)',CLEAN/'reviews_rejected.parquet')
    c.execute(f'CREATE VIEW rc AS SELECT * FROM read_parquet({q(CLEAN/"reviews.parquet")})')
    while not (ROOT/'metadata_statistics.json').exists():
        time.sleep(5)
    c.execute(f'CREATE VIEW p AS SELECT parent_asin,is_apparel,is_womens_top FROM read_parquet({q(CLEAN/"products.parquet")})')
    copy(c,"""SELECT r.* FROM rc r SEMI JOIN (SELECT parent_asin FROM p WHERE is_womens_top) p USING(parent_asin)""",CLEAN/'womens_tops_reviews.parquet')
    copy(c,"""SELECT r.parent_asin,count(*) AS review_count, count(DISTINCT user_id) AS reviewers,
       avg(rating) AS review_rating_mean,count(*) FILTER(WHERE verified_purchase) AS verified_reviews,
       count(*) FILTER(WHERE NOT text_missing) AS reviews_with_text,
       min(review_datetime_utc) AS first_review_utc,max(review_datetime_utc) AS last_review_utc
       FROM rc r GROUP BY parent_asin""",CLEAN/'product_review_summary.parquet')
    unmatched=c.execute('SELECT count(*) FROM rc ANTI JOIN p USING(parent_asin)').fetchone()[0]
    stats('reviews',dict(raw_rows=n,valid_rows=valid,clean_reviews=unique,invalid_rows=n-valid,
       exact_source_duplicate_rows=valid-unique,reviews_without_product_metadata=unmatched,
       womens_tops_reviews=c.execute(f'SELECT count(*) FROM read_parquet({q(CLEAN/"womens_tops_reviews.parquet")})').fetchone()[0]))
    c.close()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['metadata','attributes','google','reviews'])
    args=parser.parse_args()
    # A Windows byte-range lock permits overlapping stages and prevents duplicate writers.
    with (WORK/(args.stage+'.lock')).open('a+b') as lock:
        lock.seek(0,2)
        if lock.tell()==0: lock.write(b'0');lock.flush()
        while True:
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError as e:
                if e.errno not in (errno.EACCES,errno.EDEADLK): raise
                time.sleep(5)
        try:
            if not (ROOT/(args.stage+'_statistics.json')).exists():
                globals()[args.stage]()
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

if __name__=='__main__':
    main()
