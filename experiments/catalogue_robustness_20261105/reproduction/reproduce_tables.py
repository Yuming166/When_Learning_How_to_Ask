"""Recompute this revision's new numeric tables from bundled inputs and answers.

No network or model calls. Run: python reproduce_tables.py
Use --quick for a three-menu-per-case consistency check.
Earlier six-field numbers are author-reported and are not reconstructed here.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, argparse
import numpy as np
from budget_comparison import BudgetBelief, evaluate, BUDGETS
from model_answer_banks import replay
from ranking_search import components, signatures

HERE=Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE/name).read_text(encoding='utf-8'))


def key(menu):
    return menu['seed'],tuple(menu['items'])


def check_case(name,case,recorded,answers=None,quick=False):
    model=BudgetBelief(case['config']['prior'])
    products={r['product_id']:r for r in case['products']}
    old={key(r):r for r in recorded}
    menus=case['menus'][::192] if quick else case['menus']
    results=[];error=0.
    for menu in menus:
        accept=signatures(*components([products[x] for x in menu['items']],case['labels'],model),case['config'])
        result=evaluate(model,accept) if answers is None else replay(model,accept,answers)
        for b in BUDGETS:
            delta=float(np.max(np.abs(np.array(result[b])-old[key(menu)]['rates'][str(b)])))
            assert delta<1e-10,(name,menu,b,delta)
            error=max(error,delta)
        results.append([result[b] for b in BUDGETS])
    print(name, 'menus',len(menus),'max error',error,flush=True)
    if not quick:print(np.round(100*np.mean(results,axis=0),6).tolist(),flush=True)


def run():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    inputs=read('experiment_inputs.json')
    check_case('Nine-preference simulation',inputs['primary'],read('nine_preference_results.json')['menus'],quick=args.quick)
    common=read('common_field_results.json')
    for name,case in inputs['common'].items():
        check_case(name+' common-field simulation',case,common['menus'][name],quick=args.quick)
    results=read('model_bank_results.json')
    responses=[json.loads(x) for x in (HERE/'model_bank_responses.jsonl').read_text(encoding='utf-8').splitlines()]
    for model,by_dataset in results['results'].items():
        for name,result in by_dataset.items():
            bank={r['profile']:r['answers'] for r in responses if r['model']==model and r['dataset']==name}
            assert set(bank)==set(range(64))
            answers=np.array([bank[i] for i in range(64)])
            check_case(model+' / '+name,inputs['common'][name],result['menus'],answers,args.quick)
    luna_dir=HERE/'luna'
    if luna_dir.exists():
        protocol=json.loads((luna_dir/'protocol.json').read_text(encoding='utf-8'))
        luna=json.loads((luna_dir/'results.json').read_text(encoding='utf-8'))
        banks={name:np.full((64,6),-1,dtype=int) for name in inputs['common']}
        for batch in protocol['batches']:
            raw=json.loads((luna_dir/batch['response_file']).read_text(encoding='utf-8-sig'))
            for i in batch['profiles']:
                rows=[r for r in raw['answers'] if r.get('id')=='C%03d'%i]
                a=rows[0].get('answers') if len(rows)==1 else None
                if isinstance(a,list) and len(a)==6 and all(type(v) is str and v in ['A','B'] for v in a):
                    banks[batch['dataset']][i]=[int(v=='B') for v in a]
        for name,result in luna['datasets'].items():
            check_case('gpt-6-luna / '+name,inputs['common'][name],result['menus'],banks[name],args.quick)
    print('All selected checks passed; no model requests were made.')


if __name__=='__main__':run()
