"""Offline adaptivity ablation; no model calls. Preserve frozen Amazon scoring."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, importlib.util, json, csv, datetime
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SRC=ROOT/'Learning_How_to_Ask_Overleaf/research'
sys.path.insert(0,str(SRC))
from budget_comparison import BudgetBelief
from ranking_search import components,signatures
spec=importlib.util.spec_from_file_location('frozen_parser',SRC/'luna/luna_table2.py')
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
SOURCES={'Luna':SRC/'luna','DeepSeek':ROOT/'outputs/amazon_deepseek_glm_20261105/deepseek-v4.1-flash','GLM':ROOT/'outputs/amazon_deepseek_glm_20261105/glm-5.3'}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def freeze():
    files=[Path(__file__),SRC/'experiment_inputs.json',SRC/'budget_comparison.py',SRC/'richer_preferences.py',SRC/'ranking_search.py',SRC/'model_answer_banks.py',SRC/'luna/luna_table2.py']
    for d in SOURCES.values():files += [d/'protocol.json',d/'results.json']+sorted(d.glob('amazon_*_response.json'))
    plan={'dataset':'Amazon','models':list(SOURCES),'profiles':64,'menus':576,'budgets':list(range(7)),'display_budgets':[3,4,5],
      'intervention':'Full DV recomputes scores after each answer; initial-order DV ranks the six empty-history DV scores once per menu. Both update the same posterior and terminal decision after answers.',
      'tie_rule':'Repeatedly choose the lowest field index within 1e-12 of the largest remaining initial score, matching local DV choose tolerance. No later score recomputation for static order.',
      'answers':'Exact existing Amazon responses, original strict JSON parser; no retries or repairs. Selected invalid answers permanently mark a trajectory unsuccessful. All 64 profiles remain in denominator.',
      'estimand':'Prior-weighted profile success, equally averaged over the original 576 menus; exact original Amazon acceptance and no-buy rules.',
      'bootstrap':{'draws':5000,'seed':20261105563,'paired':'Same menu draws for both policies and all three models, stratified by three original menu seeds.','pointwise':0.95,'bonferroni_family':'Nine model-budget contrasts (three models times budgets 3,4,5)','scope':'Conditional on fixed products, profiles, priors and single collected answer banks; models are not independent shopper samples.'},
      'new_model_calls':0,'design_status':'Post-hoc component analysis frozen before computing new ablation results.',
      'independent_validation':'Subset-conditioning checks every chosen question and validates production terminal decisions as maximizers within 1e-12. Uses production decisions for numerically tied actions; initial preflight exposed floating-point argmax tie differences in the independent evaluator.',
      'sources':{str(p.relative_to(ROOT)):sha(p) for p in files}}
    p=OUT/'protocol.json'
    if p.exists():assert read(p)==plan
    else:write(p,plan)
    return plan

def direct(model,accept,answers,reference_decisions,static_order=None):
    """Independent per-profile subset conditioning, without ternary state arrays."""
    mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
    hit=np.zeros((7,64),bool);decisions=np.zeros((7,64),int);questions=np.zeros((6,64),int)
    for i in range(64):
        mask=np.ones(64,bool);used=[];alive=True
        for b in range(7):
            scores=mass[mask]@accept[mask]/mass[mask].sum()
            d=int(reference_decisions[b,i])
            assert scores[d]>=scores.max()-1e-12
            decisions[b,i]=d;hit[b,i]=alive and accept[i,d]
            if b==6:break
            if static_order is None:
                scores=np.full(6,-np.inf)
                for q in range(6):
                    if q in used:continue
                    scores[q]=sum(float((mass[child]@accept[child]).max()) for y in [0,1] for child in [mask&(model.bits[:,q]==y)])/mass[mask].sum()
                q=int(np.flatnonzero(scores>=scores.max()-1e-12)[0])
            else:q=int(static_order[b])
            questions[b,i]=q;used.append(q)
            y=int(answers[i,q]);alive &= y>=0
            mask &= model.bits[:,q]==max(y,0)
    return hit,decisions,questions

def run():
    plan=freeze();case=read(SRC/'experiment_inputs.json')['common']['Amazon']
    model=BudgetBelief(case['config']['prior'],limit=6)
    mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
    banks=[];old=[];metadata=[]
    for name,d in SOURCES.items():
        p=read(d/'protocol.json');assert p['inputs_sha256']==sha(SRC/'experiment_inputs.json')
        p['batches']=[b for b in p['batches'] if b['dataset']=='Amazon']
        parser.OUT=d;bb,rr=parser.parse_banks(p);banks.append(bb['Amazon'])
        old.append(read(d/'results.json')['datasets']['Amazon'])
        metadata.append({'name':name,'requested_model':p['requested_model'],'valid_profiles':int((bb['Amazon']>=0).all(1).sum()),'correct_fields':int((bb['Amazon']==model.bits).sum()),'records':rr})
    banks=np.array(banks);rows={r['product_id']:r for r in case['products']}
    hits=[];decs=[];queries=[];orders=[];allrates=[];ind_error=0.;old_error=0.
    for mi,menu in enumerate(case['menus']):
        accept=signatures(*components([rows[x] for x in menu['items']],case['labels'],model),case['config'])
        post=model.marginals(accept);value=[p.max(1) for p in post]
        scores=model.expect(value[1],0)[0].copy();order=[]
        for _ in range(6):
            q=int(np.flatnonzero(scores>=scores.max()-1e-12)[0]);order.append(q);scores[q]=-np.inf
        state=np.zeros((3,2,64),int);alive=np.ones((3,2,64),bool)
        hh=[];dd=[];qq=[]
        for b in range(7):
            decision=post[b].argmax(1)[state]
            hit=accept[np.arange(64)[None,None,:],decision]&alive
            hh.append(hit);dd.append(decision)
            if b==6:break
            dynamic=model.choose(model.expect(value[b+1],b),b)
            q=np.stack([dynamic[state[:,0]],np.full((3,64),order[b])],axis=1)
            y=banks[np.arange(3)[:,None,None],np.arange(64)[None,None,:],q]
            alive &= y>=0
            state=model.children[b][state,q,np.maximum(y,0)];qq.append(q)
        hh=np.array(hh);dd=np.array(dd);qq=np.array(qq);rates=hh@mass
        assert np.array_equal(hh[:2,:,0],hh[:2,:,1])
        assert np.array_equal(dd[:2,:,0],dd[:2,:,1])
        assert np.array_equal(qq[0,:,0],qq[0,:,1])
        assert np.array_equal(hh[6,:,0],hh[6,:,1])
        valid=(banks>=0).all(2);exact=(banks==model.bits).all(2)&valid
        assert hh[6,:,0][exact].all()
        for m in range(3):
            assert np.array_equal(dd[6,m,0,valid[m]],dd[6,m,1,valid[m]])
            om=old[m]['menus'][mi];assert om['items']==menu['items'] and om['seed']==menu['seed']
            for b in [3,4,5]:
                e=abs(rates[b,m,0]-om['rates'][str(b)][3]);old_error=max(old_error,e);assert e<1e-10
        if mi in [0,192,384]:
            for m in range(3):
                for policy in range(2):
                    ih,idc,iq=direct(model,accept,banks[m],dd[:,m,policy],None if policy==0 else order)
                    assert np.array_equal(ih,hh[:,m,policy])
                    assert np.array_equal(iq,qq[:,m,policy])
                    e=float(np.max(np.abs(ih@mass-rates[:,m,policy])));ind_error=max(ind_error,e)
        hits.append(hh);decs.append(dd);queries.append(qq);orders.append(order);allrates.append(rates)
        if (mi+1)%192==0:print('Menus',mi+1,'/576; historical DV and invariants passed',flush=True)
    arr=np.array(allrates);gaps=100*(arr[:,:,:,0]-arr[:,:,:,1]);rng=np.random.default_rng(plan['bootstrap']['seed'])
    seeds=sorted(set(m['seed'] for m in case['menus']));groups=[np.array([i for i,m in enumerate(case['menus']) if m['seed']==s]) for s in seeds]
    boot=[]
    for _ in range(50):
        ix=np.hstack([rng.choice(g,size=(100,len(g)),replace=True) for g in groups]);boot.extend(gaps[ix].mean(1))
    boot=np.array(boot);ci=np.percentile(boot,[2.5,97.5],axis=0);corrected=np.percentile(boot,[2.5/9,100-2.5/9],axis=0)
    result={'dataset':'Amazon','protocol_sha256':sha(OUT/'protocol.json'),'new_model_calls':0,'models':{},'checks':{'menus':576,'historical_DV_max_error':old_error,'independent_replay_max_error':ind_error,'independent_menus':3,'budget_0_1_equal':True,'budget_6_valid_complete_equal':True}}
    for m,name in enumerate(SOURCES):
        rr=[]
        for b in range(7):
            rr.append({'budget':b,'full_dv_percent':float(100*arr[:,b,m,0].mean()),'initial_order_dv_percent':float(100*arr[:,b,m,1].mean()),'gain_pp':float(gaps[:,b,m].mean()),'pointwise_95_ci_pp':ci[:,b,m].tolist(),'nine_contrast_corrected_ci_pp':corrected[:,b,m].tolist() if b in [3,4,5] else None})
        result['models'][name]={**metadata[m],'budgets':rr,'menus':[{'seed':menu['seed'],'items':menu['items'],'initial_order':orders[i],'rates':arr[i,:,m].tolist()} for i,menu in enumerate(case['menus'])]}
    for p,h in plan['sources'].items():assert sha(ROOT/p)==h
    result['checks']['source_hashes_unchanged']=True
    np.savez_compressed(OUT/'paired_traces.npz',correct=np.array(hits),decisions=np.array(decs,dtype=np.int16),questions=np.array(queries,dtype=np.int8),initial_orders=np.array(orders,dtype=np.int8),answers=banks,profile_weights=mass)
    result['trace_layout']='correct and decisions: menu,budget,model,policy,profile; questions: menu,step,model,policy,profile. Models Luna/DeepSeek/GLM; policies full DV/initial-order DV. Banks retain -1 invalid values.'
    write(OUT/'results.json',result)
    with (OUT/'ablation_summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Model','Budget','Full DV (%)','Initial-order DV (%)','Gain (pp)','95% CI low','95% CI high','Corrected CI low','Corrected CI high'])
        for name,r in result['models'].items():
            for row in r['budgets']:w.writerow([name,row['budget'],row['full_dv_percent'],row['initial_order_dv_percent'],row['gain_pp'],*row['pointwise_95_ci_pp'],*(row['nine_contrast_corrected_ci_pp'] or ['', ''])])
    print(json.dumps({n:{'valid_profiles':r['valid_profiles'],'budgets':[x for x in r['budgets'] if x['budget'] in [3,4,5]]} for n,r in result['models'].items()},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':run()
