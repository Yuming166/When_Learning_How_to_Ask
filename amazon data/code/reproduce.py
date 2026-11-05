"""Run from any directory: python 'amazon data/code/reproduce.py'. No network calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
HERE=Path(__file__).resolve().parents[1];REPO=HERE.parent
CORE=REPO/'experiments/catalogue_robustness_20261105/reproduction'
sys.path.insert(0,str(CORE))
from budget_comparison import BudgetBelief
from ranking_search import components,signatures
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 if (HERE/'MANIFEST.json').exists():
  for rel,h in read(HERE/'MANIFEST.json')['sha256'].items():assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==h,rel
 spec=importlib.util.spec_from_file_location('original_parser',CORE/'luna/luna_table2.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
 paths=[HERE/'experiments/luna_existing',HERE/'experiments/amazon_models/deepseek-v4.1-flash',HERE/'experiments/amazon_models/glm-5.3']
 names=['Luna','DeepSeek','GLM'];banks=[];original=[]
 for p in paths:
  plan=read(p/'protocol.json');plan['batches']=[x for x in plan['batches'] if x['dataset']=='Amazon'];parser.OUT=p
  bank,_=parser.parse_banks(plan);banks.append(bank['Amazon']);original.append(read(p/'results.json')['datasets']['Amazon'])
 case=read(HERE/'data/frozen_inputs/amazon.json');model=BudgetBelief(case['config']['prior'],limit=6)
 banks=np.array(banks+[model.bits]);mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
 rows={r['product_id']:r for r in case['products']};llm=read(HERE/'experiments/llm_ablation/results.json');py=read(HERE/'experiments/python_ablation/results.json')
 h=-(model.p*np.log(model.p)+(1-model.p)*np.log(1-model.p));allrates=[];maxerr=0.
 for i,menu in enumerate(case['menus']):
  accept=signatures(*components([rows[x] for x in menu['items']],case['labels'],model),case['config']);post=model.marginals(accept);value=[p.max(1) for p in post]
  sig=accept@(1<<np.arange(accept.shape[1]));groups=model.marginals(sig[:,None]==np.unique(sig));ent=[-(p*np.log(np.maximum(p,1e-300))).sum(1) for p in groups]
  scores=model.expect(value[1],0)[0].copy();order=[]
  for _ in range(6):q=int(np.flatnonzero(scores>=scores.max()-1e-12)[0]);order.append(q);scores[q]=-np.inf
  state=np.zeros((4,5,64),int);alive=np.ones_like(state,bool);rr=[]
  for b in range(7):
   decision=post[b].argmax(1)[state];rr.append((accept[np.arange(64)[None,None,:],decision]&alive)@mass)
   if b==6:break
   policies=np.array([np.full(len(model.codes[b]),b),model.choose(np.broadcast_to(h,(len(model.codes[b]),6)),b),model.choose(-model.expect(ent[b+1],b),b),model.choose(model.expect(value[b+1],b),b),np.full(len(model.codes[b]),order[b])])
   q=policies[np.arange(5)[None,:,None],state];y=banks[np.arange(4)[:,None,None],np.arange(64)[None,None,:],q];alive &= y>=0;state=model.children[b][state,q,np.maximum(y,0)]
  rr=np.array(rr);assert np.allclose(rr[:2,:,3],rr[:2,:,4],atol=1e-12);assert np.allclose(rr[6,:,3],rr[6,:,4],atol=1e-12)
  for m,name in enumerate(names):
   for b in [3,4,5]:maxerr=max(maxerr,float(np.max(np.abs(rr[b,m,:4]-original[m]['menus'][i]['rates'][str(b)]))))
   maxerr=max(maxerr,float(np.max(np.abs(rr[:,m,3:5]-llm['models'][name]['menus'][i]['rates']))))
  maxerr=max(maxerr,float(np.max(np.abs(rr[:,3,1:5]-py['menus'][i]['rates']))));assert maxerr<1e-10
  allrates.append(rr)
  if (i+1)%192==0:print(i+1,'/576 menus verified',flush=True)
 arr=np.array(allrates);gllm=100*(arr[:,:,:3,3]-arr[:,:,:3,4]);gpy=100*(arr[:,:,3,3,None]-arr[:,:,3,[1,2,4]])
 rng=np.random.default_rng(20261105563);seeds=sorted(set(m['seed'] for m in case['menus']));groups=[np.array([i for i,m in enumerate(case['menus']) if m['seed']==s]) for s in seeds];bl=[];bp=[]
 for _ in range(50):
  ix=np.hstack([rng.choice(g,size=(100,len(g)),replace=True) for g in groups]);bl.extend(gllm[ix].mean(1));bp.extend(gpy[ix].mean(1))
 for boot,records in [(bl,[llm['models'][n]['budgets'] for n in names]),(bp,list(py['contrasts'].values()))]:
  point=np.percentile(boot,[2.5,97.5],axis=0);corr=np.percentile(boot,[2.5/9,100-2.5/9],axis=0)
  for j,records_j in enumerate(records):
   for b in [3,4,5]:
    assert np.max(np.abs(point[:,b,j]-records_j[b]['pointwise_95_ci_pp']))<1e-9
    assert np.max(np.abs(corr[:,b,j]-records_j[b]['nine_contrast_corrected_ci_pp']))<1e-9
 checks={'status':'PASS','amazon_products':len(case['products']),'menus':len(case['menus']),'profiles':64,'models':names,'new_model_calls':0,'main_and_ablation_max_abs_error':maxerr,'bootstrap_draws':5000,'pointwise_and_corrected_intervals_verified':True,'valid_profiles':{n:int((banks[i]>=0).all(1).sum()) for i,n in enumerate(names)}}
 (HERE/'CHECKS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
