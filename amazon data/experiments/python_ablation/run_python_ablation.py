"""Amazon truth-response Python ablation, three interventions, zero API calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util,csv
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];SRC=ROOT/'Learning_How_to_Ask_Overleaf/research'
sys.path.insert(0,str(SRC))
from budget_comparison import BudgetBelief,direct_check
from ranking_search import components,signatures
LLM=ROOT/'outputs/amazon_dv_ablation_20261105'
spec=importlib.util.spec_from_file_location('offline_validation',LLM/'run_ablation.py');validation=importlib.util.module_from_spec(spec);spec.loader.exec_module(validation)
METHODS=['Profile information gain','Decision-set information gain','Full decision value','Decision value with frozen initial order']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    files=[Path(__file__),SRC/'experiment_inputs.json',SRC/'common_field_results.json',SRC/'budget_comparison.py',SRC/'richer_preferences.py',SRC/'ranking_search.py',LLM/'run_ablation.py',LLM/'results.json']
    plan={'dataset':'Amazon','profiles':64,'menus':576,'products_per_menu':16,'budgets':list(range(7)),'display_budgets':[3,4,5],'methods':METHODS,
      'answers':'Pure Python truth oracle: model.bits provides selected answers directly. No LLM responses used as input to Python policy trajectories.',
      'interventions':['Replace decision-value question objective with profile entropy reduction; retain adaptation and terminal recommendation.','Replace decision-value objective with decision-set entropy reduction; retain adaptation and terminal recommendation.','Rank empty-history DV scores once, then fix question order; retain answer updates and terminal recommendation.'],
      'tie_rule':'Lowest field index within 1e-12 of maximum; static ranking repeatedly applies this to remaining INITIAL scores.',
      'estimand':'Prior-weighted profiles and equal original menus, using frozen Amazon acceptable-or-no-purchase rule.',
      'bootstrap':{'draws':5000,'seed':20261105563,'unit':'Paired menus, stratified by original seed; common draws for all contrasts.','main_table':'Pointwise percentile 95% intervals to match requested table presentation.','additional':'Bonferroni correction over nine Python variant-budget contrasts, separately from the previous LLM family.','scope':'Conditional on fixed products, constructed profiles and prior; no profile-bootstrap claim.'},
      'design_status':'Post-hoc component analysis; frozen before new pure-Python ablation results. Existing main and LLM results already observed.',
      'new_model_calls':0,'sources':{str(p.relative_to(ROOT)):sha(p) for p in files}}
    if (OUT/'protocol.json').exists():assert read(OUT/'protocol.json')==plan
    else:write(OUT/'protocol.json',plan)
    case=read(SRC/'experiment_inputs.json')['common']['Amazon'];old=read(SRC/'common_field_results.json')['menus']['Amazon']
    model=BudgetBelief(case['config']['prior'],limit=6);rows={r['product_id']:r for r in case['products']}
    mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1);h=-(model.p*np.log(model.p)+(1-model.p)*np.log(1-model.p))
    allrates=[];hits=[];queries=[];orders=[];error=0.;ind_error=0.
    for i,menu in enumerate(case['menus']):
        accept=signatures(*components([rows[x] for x in menu['items']],case['labels'],model),case['config'])
        post=model.marginals(accept);value=[p.max(1) for p in post]
        sig=accept@(1<<np.arange(accept.shape[1]));groups=model.marginals(sig[:,None]==np.unique(sig));ent=[-(p*np.log(np.maximum(p,1e-300))).sum(1) for p in groups]
        scores=model.expect(value[1],0)[0].copy();order=[]
        for _ in range(6):q=int(np.flatnonzero(scores>=scores.max()-1e-12)[0]);order.append(q);scores[q]=-np.inf
        state=np.zeros((4,64),int);hh=[];dd=[];qq=[]
        for b in range(7):
            decision=post[b].argmax(1)[state];hh.append(accept[np.arange(64)[None,:],decision]);dd.append(decision)
            if b==6:break
            policies=np.array([model.choose(np.broadcast_to(h,(len(model.codes[b]),6)),b),model.choose(-model.expect(ent[b+1],b),b),model.choose(model.expect(value[b+1],b),b),np.full(len(model.codes[b]),order[b])])
            q=policies[np.arange(4)[:,None],state];y=model.bits[np.arange(64)[None,:],q];state=model.children[b][state,q,y];qq.append(q)
        hh=np.array(hh);dd=np.array(dd);qq=np.array(qq);rates=hh@mass
        assert np.array_equal(hh[:2,2],hh[:2,3]);assert np.array_equal(dd[:2,2],dd[:2,3]);assert hh[6].all();assert np.array_equal(dd[6,2],dd[6,3])
        assert old[i]['items']==menu['items'] and old[i]['seed']==menu['seed']
        for b in [3,4,5]:
            e=float(np.max(np.abs(rates[b,:3]-old[i]['rates'][str(b)][1:])));assert e<1e-10;error=max(error,e)
        if i in [0,192,384]:
            for b in [3,4,5]:
                for m in range(3):
                    e=abs(direct_check(model,accept,b,m+1)-rates[b,m]);assert e<1e-10;ind_error=max(ind_error,e)
            ih,_,iq=validation.direct(model,accept,model.bits,dd[:,3],order)
            assert np.array_equal(ih,hh[:,3]) and np.array_equal(iq,qq[:,3])
        hits.append(hh);queries.append(qq);orders.append(order);allrates.append(rates)
        if (i+1)%192==0:print('Python menus',i+1,'/576',flush=True)
    arr=np.array(allrates);gaps=100*(arr[:,:,2,None]-arr[:,:,[0,1,3]])
    rng=np.random.default_rng(plan['bootstrap']['seed']);seeds=sorted(set(m['seed'] for m in case['menus']));groups=[np.array([i for i,m in enumerate(case['menus']) if m['seed']==s]) for s in seeds];boot=[]
    for _ in range(50):
        ix=np.hstack([rng.choice(g,size=(100,len(g)),replace=True) for g in groups]);boot.extend(gaps[ix].mean(1))
    ci=np.percentile(boot,[2.5,97.5],axis=0);corr=np.percentile(boot,[2.5/9,100-2.5/9],axis=0);acc=100*arr.mean(0)
    llm=read(LLM/'results.json');comparison=llm['models']['Luna']['budgets']
    assert max(abs(acc[b,2]-comparison[b]['full_dv_percent']) for b in range(7))<1e-9
    assert max(abs(acc[b,3]-comparison[b]['initial_order_dv_percent']) for b in range(7))<1e-9
    out={'dataset':'Amazon','methods':METHODS,'accuracy_percent':acc.tolist(),'contrasts':{},'llm_ablation':{name:{k:v for k,v in r.items() if k not in ['menus','records']} for name,r in llm['models'].items()},'menus':[{'seed':m['seed'],'items':m['items'],'initial_order':orders[i],'rates':arr[i].tolist()} for i,m in enumerate(case['menus'])],
      'checks':{'historical_main_max_error':error,'independent_main_max_error':ind_error,'independent_static_menus':3,'budget_0_1_full_static_equal':True,'budget_6_all_correct':True,'matches_truthful_Luna_ablation':True,'new_model_calls':0},'protocol_sha256':sha(OUT/'protocol.json')}
    for j,k in enumerate([0,1,3]):out['contrasts'][METHODS[k]]=[{'budget':b,'gain_pp':float(gaps[:,b,j].mean()),'pointwise_95_ci_pp':ci[:,b,j].tolist(),'nine_contrast_corrected_ci_pp':corr[:,b,j].tolist() if b in [3,4,5] else None} for b in range(7)]
    for p,h in plan['sources'].items():assert sha(ROOT/p)==h
    out['checks']['source_hashes_unchanged']=True
    write(OUT/'results.json',out)
    np.savez_compressed(OUT/'python_paired_traces.npz',correct=np.array(hits),questions=np.array(queries,dtype=np.int8),initial_orders=np.array(orders,dtype=np.int8),truth=model.bits,profile_weights=mass)
    with (OUT/'python_ablation.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Variant','Budget','Full DV minus variant (pp)','Pointwise 95% lower','Pointwise 95% upper'])
        for name,rr in out['contrasts'].items():
            for r in rr:w.writerow([name,r['budget'],r['gain_pp'],*r['pointwise_95_ci_pp']])
    print(json.dumps({k:[r for r in v if r['budget'] in [3,4,5]] for k,v in out['contrasts'].items()},indent=2),flush=True)

if __name__=='__main__':run()
