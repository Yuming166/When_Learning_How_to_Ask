"""Fixed six-field cross-catalogue diagnostic; no task selection by outcomes."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
import hashlib, json, re, random
import numpy as np
import pandas as pd
import ranking_search as s
from budget_comparison import BudgetBelief, evaluate, direct_check, METHODS, BUDGETS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '跨数据源与模型检验'
FIELDS = s.FIELDS[:6]
AMAZON = ROOT.parent / 'Amazon_Reviews_2023_Clothing' / '女装衬衫推荐实验' / '实验商品.parquet'
SEEDS = [20261105541, 20261105542, 20261105543]
PRIOR = [.50, .65, .40, .55, .60, .50]


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def fabric(value):
    parts = re.findall(r'(\d+(?:\.\d+)?)%\s*([^+]+)', value)
    if parts:
        value = sorted(((float(p), n.strip()) for p, n in parts), key=lambda a: (-a[0], a[1]))[0][1]
    return {'pure cotton': 'cotton', 'viscose': 'viscose rayon', 'rayon': 'viscose rayon'}.get(value, value)


def row(pid, price, attributes, split):
    return dict(product_id=pid, source_price=dict(minimum=float(price)), split=split,
                attributes={k: dict(value=v, status='reported') for k, v in attributes.items()})


def data():
    with ZipFile(s.prior.SOURCE) as z:
        blob = z.read(next(n for n in z.namelist() if n.endswith('/catalogue_strict.jsonl')))
    myntra = []
    for r in map(json.loads, blob.decode('utf-8-sig').splitlines()):
        if r['gender'] != 'Women' or not all(r['attributes'].get(f, {}).get('status') == 'reported' for f in FIELDS[:-1]):
            continue
        attrs = {f: r['attributes'][f]['value'] for f in FIELDS[:-1]}
        attrs['fabric'] = fabric(attrs['fabric'])
        myntra.append(row(r['product_id'], r['source_price']['minimum'], attrs, r['split']))
    amazon = []
    for r in pd.read_parquet(AMAZON).to_dict('records'):
        h = int(hashlib.sha256(('cross-catalogue-20261105:' + r['parent_asin']).encode()).hexdigest(), 16) % 100
        split = 'development' if h < 70 else 'validation_reserved' if h < 85 else 'test_reserved'
        attrs = dict(sleeve_length={'long_sleeve':'long sleeves','short_sleeve':'short sleeves',
                                   'three_quarter_sleeve':'three-quarter sleeves','cap_sleeve':'cap sleeves',
                                   'sleeveless':'sleeveless'}[r['sleeve']],
                     pattern={'stripes':'striped','polka_dot':'polka dots'}.get(r['pattern'], r['pattern']),
                     neckline={'v_neck':'v-neck','round_neck':'round neck','crew_neck':'round neck'}.get(r['neckline'],r['neckline'].replace('_',' ')),
                     fabric=fabric(r['fabric']),
                     wash_care={'machine_wash_permitted':'machine wash','hand_wash_only':'hand wash'}[r['care']])
        amazon.append(row(r['parent_asin'], r['price'], attrs, split))
    return {'Myntra':myntra, 'Amazon':amazon}


def freeze():
    OUT.mkdir(exist_ok=True)
    datasets = data()
    c = dict(d=6, menu_size=16, answer='acceptable', prior=PRIOR, weights=[1]*5,
             threshold=.55, price_penalty=.05, hard=[])
    plan = dict(config=c, budgets=BUDGETS, methods=METHODS, seeds=SEEDS,
                scope='Post-confirmation common-field diagnostic on existing catalogue records; neither product pool is claimed to be untouched by earlier research.',
                normalization='Five common attributes plus budget. Dominant fibre for Amazon mixtures (largest stated percentage; alphabetical tie); pure cotton -> cotton; viscose/rayon -> viscose rayon; crew/round neck unified; exact sleeve and wash synonyms. Other categorical labels retained.',
                selection='All eligible women products with five reported attributes and price. Per-dataset top-two development attribute labels and median/75th-percentile development prices. Same prior over label ranks, acceptance, methods, sixteen-item menus, and budgets. No tuning.',
                amazon_split='SHA256(cross-catalogue-20261105:ASIN) modulo 100: <70 development, <85 validation, remaining test; Myntra uses supplied splits.',
                source_sha256={str(s.prior.SOURCE):hashlib.sha256(s.prior.SOURCE.read_bytes()).hexdigest(),
                               str(AMAZON):hashlib.sha256(AMAZON.read_bytes()).hexdigest()},
                cases={})
    for name, rows in datasets.items():
        dev = [r for r in rows if r['split']=='development']
        test = [r for r in rows if r['split']=='test_reserved']
        labels = {f:[v for v,n in sorted(Counter(r['attributes'][f]['value'] for r in dev).items(), key=lambda t:(-t[1],t[0]))[:2]] for f in FIELDS[:-1]}
        labels['budget'] = np.quantile([r['source_price']['minimum'] for r in dev],[.5,.75]).tolist()
        menus = [dict(seed=seed,items=ids) for seed in SEEDS for ids in s.menus(test,seed,16,192)]
        plan['cases'][name] = dict(labels=labels,counts=dict(Counter(r['split'] for r in rows)),menus=menus)
    path=OUT/'cross_catalogue_protocol.json'
    if path.exists(): assert json.loads(path.read_text(encoding='utf-8'))==json.loads(json.dumps(plan))
    else: write(path.name,plan)
    return datasets,plan


def run():
    datasets,plan=freeze()
    model=BudgetBelief(PRIOR)
    records={};checks=[]
    for name,case in plan['cases'].items():
        rows={r['product_id']:r for r in datasets[name]}
        records[name]=[]
        for i,menu in enumerate(case['menus']):
            accept=s.signatures(*s.components([rows[x] for x in menu['items']],case['labels'],model),plan['config'])
            rates=evaluate(model,accept)
            if i==0:
                for b in BUDGETS:
                    for m in range(4): checks.append(abs(direct_check(model,accept,b,m)-rates[b][m]))
            records[name].append(dict(**menu,rates=rates))
        print(name, np.round(100*np.mean([[r['rates'][b] for b in BUDGETS] for r in records[name]],axis=0),3).tolist(),flush=True)
    assert max(checks)<1e-10
    rng=np.random.default_rng(20261105544)
    summaries={}
    for name,recs in records.items():
        a=np.array([[r['rates'][b] for b in BUDGETS] for r in recs])
        gaps=100*(a[:,:,3]-a[:,:,2]);groups=[np.array([i for i,r in enumerate(recs) if r['seed']==seed]) for seed in SEEDS]
        boot=[]
        for _ in range(50):
            ix=np.hstack([rng.choice(g,size=(100,len(g)),replace=True) for g in groups]);boot.extend(gaps[ix].mean(1))
        summaries[name]=dict(accuracy_percent=(100*a.mean(0)).tolist(),gain_pp=gaps.mean(0).tolist(),
                             six_comparison_intervals=np.percentile(boot,[100/240,100-100/240],axis=0).T.tolist(),
                             per_seed={str(seed):(100*a[g].mean(0)).tolist() for seed,g in zip(SEEDS,groups)})
    write('cross_catalogue_results.json',dict(methods=METHODS,budgets=BUDGETS,summary=summaries,menus=records,
          independent_check_max_abs_error=max(checks),interval_scope='Paired menus within seed, 5000 resamples, Bonferroni correction over two datasets times three budgets; conditional on catalogue and synthetic population.',
          protocol_sha256=hashlib.sha256((OUT/'cross_catalogue_protocol.json').read_bytes()).hexdigest()))
    print(json.dumps(summaries,indent=2),flush=True)


if __name__=='__main__': run()
