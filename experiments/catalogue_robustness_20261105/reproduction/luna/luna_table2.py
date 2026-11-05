"""Frozen Luna answer-bank collection and offline Table 2 scoring.

prepare creates cards, never answers. Eight fresh Luna customer agents supply
the response files. score only parses those files and replays fixed policies.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import csv, hashlib, json, random, argparse
from datetime import datetime, timezone
import numpy as np
from budget_comparison import BudgetBelief, BUDGETS, METHODS
from model_answer_banks import replay
from ranking_search import components, signatures

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Luna跨数据集三四五题'
SOURCE = ROOT.parent / 'Learning_How_to_Ask_Overleaf' / 'research'
TABLE1 = ROOT.parent / 'outputs' / '01a1aa41-ac77-79e1-b73c-320625254096'
FIELDS = ['sleeve_length','pattern','neckline','fabric','wash_care','budget']
NAMES = ['sleeve length','pattern','neckline','main fabric','wash care','maximum price']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def prepare():
    OUT.mkdir(exist_ok=True)
    inputs=read(SOURCE/'experiment_inputs.json')['common']
    protocol=read(TABLE1/'cross_catalogue_protocol.json')
    assert protocol == read(SOURCE/'common_field_protocol.json')
    plan=dict(requested_model='gpt-6-luna',requested_reasoning='low',
        collection='Eight fresh customer-only agent sessions, 16 prescribed profiles per session; four batches per catalogue. No parent conversation inherited. Each model supplies a six-field answer bank; only selected answers are disclosed during policy replay.',
        identity='Requested model is recorded by the orchestration tool; no separate server-side weight identity is asserted.',
        fields=FIELDS,methods=METHODS,budgets=BUDGETS,profiles_per_dataset=64,
        menus_per_dataset=576,products_per_menu=16,shuffle_seed=20261105561,
        protocol_sha256=sha(TABLE1/'cross_catalogue_protocol.json'),
        table1_results_sha256=sha(TABLE1/'cross_catalogue_results.json'),
        inputs_sha256=sha(SOURCE/'experiment_inputs.json'),
        failures='No retry or repair of completed replies. Missing, duplicated, malformed or non-A/B profile replies are all-invalid banks. Every profile remains in the denominator; a trajectory selecting an invalid answer counts as unsuccessful.',
        scope='Post-confirmation structured-answer interface check using constructed preferences, fixed menus and unchanged methods. Batches are not independent human shoppers; menu intervals condition on the observed answer bank.',
        batches=[])
    for name,case in inputs.items():
        model=BudgetBelief(case['config']['prior'])
        order=list(range(64));random.Random(plan['shuffle_seed']+(name=='Amazon')).shuffle(order)
        for batch in range(4):
            bid=name.lower()+'_'+str(batch+1)
            indices=order[batch*16:(batch+1)*16]
            qs='\n'.join(f'{i+1}. {label}: A = {case["labels"][field][0]}; B = {case["labels"][field][1]}.' for i,(field,label) in enumerate(zip(FIELDS,NAMES)))
            cards=[]
            for i in indices:
                cards.append('Customer C%03d\n'%i+'\n'.join(f'- {label}: {case["labels"][field][int(v)]}' for label,field,v in zip(NAMES,FIELDS,model.bits[i])))
            prompt=('Answer as each of the following separate shoppers, using that shopper\'s fixed preference card. '
                    'For each shopper answer the same six questions below. Keep each shopper\'s preferences separate. '
                    'For maximum price select the stated maximum, not a lower acceptable price. '
                    'Answer each question with A or B.\n\nQuestions (the answer array must use this order):\n'+qs+
                    '\n\nPreference cards:\n\n'+'\n\n'.join(cards)+
                    '\n\nReturn only one JSON object with an "answers" array. Each element has exactly "id" '
                    '(the customer ID) and "answers" (six A/B strings, in question order). '
                    'Give every listed shopper once and no explanations.\n')
            path=OUT/(bid+'_prompt.txt');path.write_text(prompt,encoding='utf-8')
            plan['batches'].append(dict(id=bid,dataset=name,profiles=indices,prompt_file=path.name,
                prompt_sha256=sha(path),response_file=bid+'_response.json'))
    dest=OUT/'protocol.json'
    if dest.exists():assert read(dest)==plan
    else:write(dest,plan)
    print('Frozen',len(plan['batches']),'batches; protocol SHA256',sha(dest),flush=True)

def parse_banks(plan):
    banks={name:np.full((64,6),-1,dtype=int) for name in ['Myntra','Amazon']}
    records=[]
    for batch in plan['batches']:
        path=OUT/batch['response_file']
        raw=path.read_text(encoding='utf-8-sig')
        try:
            obj=json.loads(raw);rows=obj['answers']
            assert isinstance(rows,list)
        except Exception:
            rows=[]
        for i in batch['profiles']:
            matches=[r for r in rows if isinstance(r,dict) and r.get('id')=='C%03d'%i]
            answer=matches[0].get('answers') if len(matches)==1 else None
            valid=isinstance(answer,list) and len(answer)==6 and all(type(v) is str and v in ['A','B'] for v in answer)
            if valid:banks[batch['dataset']][i]=[int(v=='B') for v in answer]
            records.append(dict(dataset=batch['dataset'],profile=i,batch=batch['id'],valid=bool(valid),
                answers=banks[batch['dataset']][i].tolist(),raw_file=path.name,raw_sha256=sha(path)))
    return banks,records

def independent_replay(model,accept,answers,budget,method):
    """Direct posterior-subset computation, independent of state-array replay."""
    prior=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
    _,groups=np.unique(accept@(1<<np.arange(accept.shape[1])),return_inverse=True)
    def entropy(p):
        p=p[p>0];return -float(p@np.log(p))
    total=0.
    for i,truth in enumerate(model.bits):
        mask=np.ones(64,dtype=bool);used=[];valid=True
        for step in range(budget):
            if method==0:q=step
            else:
                scores=np.full(6,-np.inf)
                for j in range(6):
                    if j in used:continue
                    score=0.
                    for y in [0,1]:
                        child=mask&(model.bits[:,j]==y);mass=prior[child].sum();w=prior[child]/mass
                        v=(-entropy(w) if method==1 else -entropy(np.bincount(groups[child],weights=w)) if method==2 else float((w@accept[child]).max()))
                        score+=mass/prior[mask].sum()*v
                    scores[j]=score
                q=int(np.flatnonzero(scores>=scores.max()-1e-12)[0])
            y=answers[i,q]
            if y<0:valid=False;break
            mask &= model.bits[:,q]==y;used.append(q)
        if valid:
            decision=int((prior[mask]@accept[mask]).argmax())
            total+=prior[i]*accept[i,decision]
    return total

def score():
    plan=read(OUT/'protocol.json');inputs=read(SOURCE/'experiment_inputs.json')['common']
    assert sha(TABLE1/'cross_catalogue_protocol.json')==plan['protocol_sha256']
    assert sha(SOURCE/'experiment_inputs.json')==plan['inputs_sha256']
    banks,records=parse_banks(plan)
    result=dict(model=plan['requested_model'],methods=METHODS,budgets=BUDGETS,
        protocol_sha256=sha(OUT/'protocol.json'),response_records=records,datasets={})
    for name,case in inputs.items():
        model=BudgetBelief(case['config']['prior']);rows={r['product_id']:r for r in case['products']}
        menus=[];errors=[]
        for i,menu in enumerate(case['menus']):
            accept=signatures(*components([rows[x] for x in menu['items']],case['labels'],model),case['config'])
            rates=replay(model,accept,banks[name])
            if i==0:
                for budget in BUDGETS:
                    for method in range(4):
                        err=abs(independent_replay(model,accept,banks[name],budget,method)-rates[budget][method])
                        assert err<1e-10;errors.append(err)
            menus.append(dict(**menu,rates=rates))
            if (i+1)%192==0:print(name,i+1,'/576',flush=True)
        arr=np.array([[r['rates'][b] for b in BUDGETS] for r in menus]);acc=100*arr.mean(0)
        gaps=100*(arr[:,:,3]-arr[:,:,2]);rng=np.random.default_rng(20261105562)
        boot=[]
        for _ in range(50):
            ix=np.hstack([rng.choice(np.arange(j,j+192),size=(100,192),replace=True) for j in [0,192,384]])
            boot.extend(gaps[ix].mean(1))
        ci=np.percentile(boot,[100/240,100-100/240],axis=0).T
        result['datasets'][name]=dict(accuracy_percent=acc.tolist(),dv_minus_set_ig_pp=(acc[:,3]-acc[:,2]).tolist(),
            dv_minus_set_ig_corrected_interval_pp=ci.tolist(),correct_fields=int((banks[name]==model.bits).sum()),
            total_fields=384,valid_profiles=int((banks[name]>=0).all(1).sum()),total_profiles=64,
            independent_replay_max_error=max(errors),menus=menus)
    result['interval_scope']='5000 paired-menu resamples within each of three seeds, Bonferroni correction over six dataset-budget contrasts; conditions on fixed products, synthetic profiles and the collected model answer banks.'
    write(OUT/'results.json',result)
    with (OUT/'table2_luna.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Dataset','Questions']+METHODS)
        for name,r in result['datasets'].items():
            for b,row in zip(BUDGETS,r['accuracy_percent']):w.writerow([name,b]+[f'{x:.2f}' for x in row])
    print(json.dumps({n:{k:v for k,v in r.items() if k!='menus'} for n,r in result['datasets'].items()},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','score']);a=p.parse_args()
    prepare() if a.action=='prepare' else score()
