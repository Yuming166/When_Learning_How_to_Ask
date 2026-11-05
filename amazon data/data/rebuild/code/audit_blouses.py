"""Reproduce the 451-item screen and audit seller claims against original JSONL records."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import gzip, hashlib, html, json, re, sys, unicodedata
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'clean/womens_blouses_research.parquet'
OUT = ROOT / '女装衬衫推荐实验'
WORK = ROOT / '_work/blouse_audit'
OUT.mkdir(exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)
HIGH = re.compile(r'\bhigh[\s\-‐‑‒–—]*(?:neck(?:line|ed)?|collar(?:ed)?)\b', re.I)
PILOT_PATTERNS = {'solid':r'\bsolid(?:[ -]colou?r)?\b','striped':r'\bstriped\b',
                  'floral':r'\bfloral\b','plaid':r'\bplaid\b','dots':r'\bpolka[ -]dots?\b'}
FIELDS = ['neckline','sleeve','fabric','care','pattern','price']
CN = dict(zip(FIELDS,['领型','袖长','面料','洗护','图案','价格']))
def norm(s):
    return ' '.join(unicodedata.normalize('NFKC',html.unescape(re.sub(r'<[^>]*>',' ',str(s or '')))).lower().translate(str.maketrans({v:'-' for v in '‐‑‒–—'})).split())
def utterances(r):
    yield 'title', r['title']
    for field in ['features','description']:
        for i,s in enumerate(r.get(field) or []):
            if isinstance(s,str) and s.strip(): yield f'{field}[{i}]',s
    det=r.get('details') if 'details' in r else json.loads(r.get('details_json') or '{}')
    for k,v in (det or {}).items():
        if isinstance(v,str) and re.search(r'neck|collar|sleeve|material|fabric|care|wash|pattern|print|price',k,re.I):
            yield 'details.'+k,v

def old_gate(r):
    # Reproduce the previous audit verbatim, including its deliberately narrow candidate screen.
    if not (r['price'] is not None and len(r['sleeve_mentions'])==1 and r['composition_mentions'] and r['care_mentions']):return False
    if sum(bool(re.search(p,r['title'],re.I)) for p in PILOT_PATTERNS.values())!=1:return False
    m={s.lower().strip() for s in r['features']}
    method='machine' if 'machine wash' in m else 'hand_only' if 'hand wash only' in m else None
    if not method:return False
    body=' '.join([r['title'],*r['features'],r['description_text'] or '']).lower()
    if method=='machine' and re.search(r'hand[ -]wash only|do not machine wash|not machine wash|dry clean only',body):return False
    if method=='hand_only' and (re.search(r'machine.{0,18}wash|wash.{0,18}machine',body) or re.search(r'machine.{0,18}hand.{0,18}wash',body)):return False
    compositions={tuple(sorted((float(p),v.lower().strip()) for p,v in re.findall(r'(\d+(?:\.\d+)?)\s*%\s*([a-z][a-z -]*?)(?=\s*[,;/&+]|\s+\d|$)',s.strip(),re.I))) for s in r['features'] if re.fullmatch(r'\s*(?:\d+(?:\.\d+)?\s*%\s*[a-z][a-z -]*\s*(?:[,;/&+]\s*)?)+',s,re.I)}
    return len({a for a in compositions if a and abs(sum(x[0] for x in a)-100)<.01})==1

def select():
    selected={}; hits=[]; cols=['parent_asin','source_row','title','price','price_original','features','description','description_text','details_json','neckline_mentions','sleeve_mentions','composition_mentions','care_mentions']
    for batch in pq.ParquetFile(SOURCE).iter_batches(columns=cols,batch_size=4096):
        for r in batch.to_pylist():
            old=[v for v in r['neckline_mentions'] if not HIGH.fullmatch(v)]
            high=[(s,t) for s,t in utterances(r) if HIGH.search(t)]
            if high:
                hits.append(dict(parent_asin=r['parent_asin'],source_row=r['source_row'],old_mentions=old,
                                 high_evidence=[dict(source=s,text=t) for s,t in high]))
            if len(old)>1 or (not old and not high) or not old_gate(r):continue
            selected[r['source_row']]={'id':r['parent_asin'],'cohort':'原451' if old else '补回高领',
                                        'price':r['price'],'old_neck':old}
    ids=sorted(d['id'] for d in selected.values() if d['cohort']=='原451')
    assert len(ids)==len(set(ids))==451
    pq.write_table(pa.Table.from_pylist(hits),OUT/'全衬衫高领原文索引.parquet',compression='zstd')
    return selected,hashlib.sha256('\n'.join(ids).encode()).hexdigest()

def get_raw(sel):
    p=WORK/'selected_seller_rows.jsonl'
    if p.exists():
        records=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()]
        if {r['row'] for r in records}==set(sel):return records
    records=[]
    src=ROOT/'raw/meta_Clothing_Shoes_and_Jewelry.jsonl.gz'
    with gzip.open(src,'rb') as f:
        for n,line in enumerate(f,1):
            if n not in sel:continue
            r=json.loads(line)
            assert r['parent_asin']==sel[n]['id']
            records.append({k:r.get(k) for k in ('parent_asin','title','features','description','details','price','store')}|{'row':n})
            if len(records)==len(sel):break
    assert len(records)==len(sel)
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf-8')
    return records
if __name__=='__main__' and '--prepare' in sys.argv:
    s,fp=select()
    print('cohorts',Counter(x['cohort'] for x in s.values()),'sha256',fp,flush=True)
    print('original rows',len(get_raw(s)),flush=True)

