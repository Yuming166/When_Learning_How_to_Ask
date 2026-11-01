"""Once-only smoke and two-worker bounded paired evaluation. Never trains."""
import concurrent.futures as futures
import multiprocessing
import os,json,time,sys,traceback
from copy import deepcopy
import numpy as np
from .bootstrap import ROOT,T2
from .integrity import sha,write_once,verify,verify_history
from .worlds import specs,public_plan
from .controllers import METHODS,Controller
from .evaluate import evaluate_path
_MODELS=None

def load_models():
 import torch
 from t2.neural import Predictor
 torch.set_num_threads(1)
 return {name:Predictor.load(T2/'artifacts/training/models'/kind) for name,kind in [('DeepSets-KL','deepsets_kl'),('DeepSets-Info','deepsets_info')]}

def seed():
 p=ROOT/'artifacts/private/seed.json'
 if not p.exists():
  write_once(p,{'development_seed':os.urandom(32).hex(),'namespace':'phase_t2b_failure_hybrid_20261031','confirmation':False});p.chmod(0o600)
  write_once(ROOT/'artifacts/SEED_COMMITMENT.json',{'seed_sha256':sha(p),'created_before_sampling':True})
 elif sha(p)!=json.loads((ROOT/'artifacts/SEED_COMMITMENT.json').read_text())['seed_sha256']:raise RuntimeError('Seed provenance changed')
 return json.loads(p.read_text())['development_seed']

def path(spec,private_seed,R,method,models,deadline,journal,budget_only=False):
 wrapper_start,wrapper_cpu=time.perf_counter(),time.process_time()
 c=Controller(method,models) if method in METHODS else None
 with journal.open('x',buffering=1) as stream:
  def persist(v):stream.write(json.dumps(v,allow_nan=False)+'\n')
  row=evaluate_path(spec,private_seed,R,method,{method:c} if c else {},[32,64],deadline,on_progress=persist,budget_only=budget_only)
 if c:
  total=row['timings']['inference'];neural=c.wall['neural'];raw=c.wall['fallback']+c.wall['risk'];overhead=total-neural-raw
  if overhead < -1e-6:raise RuntimeError('Controller timing exceeds enclosing interval')
  row['timings']['inference']=neural
  row['timings']['planning']=max(0.,total-neural)
  row['controller_accounting']={'wall':c.wall,'cpu':c.cpu,'controller_enclosing_wall':total,'overhead_wall':max(0.,overhead),'fallback_calls':sum(v['fallback'] for v in c.decisions),'allocation_calls':len(c.decisions),'inclusive_scope':'posterior estimation + all controller neural/risk/fallback/overhead'}
  row['controller_decisions']=c.decisions
  if len(c.decisions)!=len(row['updates']):raise RuntimeError('Allocation log coverage mismatch')
 row['inner_evaluator_timing']={k:row['timings'][k] for k in ['wall','cpu']}
 row['timings']['wall']=time.perf_counter()-wrapper_start;row['timings']['cpu']=time.process_time()-wrapper_cpu
 row['timing_scope']='full path wrapper including controller construction and progress journal I/O; excludes outer model load and final parent serialization'
 return row

def smoke():
 verify();verify_history();cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'artifacts/smoke';out.mkdir(exist_ok=False)
 start,cpu=time.perf_counter(),time.process_time();private_seed=seed();models=load_models();rows=[];receipt={'status':'started','worlds':2,'training_updates':0,'gpu_jobs':0,'model_api_calls':0,'automatic_retry':False}
 write_once(out/'execution.json',receipt)
 try:
  for s in [s for s in specs(cfg) if s['kind']=='smoke']:
   local={}
   for m in list(METHODS)+['Literal-Fused-Original','Literal-Fused-Info']:
    row=path(s,private_seed,64,m,models,time.monotonic()+120,out/f"{s['world_id']}_{m}.jsonl",True)
    rows.append(row);local[m]=row
    if row['status']!='completed':raise RuntimeError('Smoke path failed')
   for new,old in [('Fused-Original-Cold','Literal-Fused-Original'),('Fused-Info','Literal-Fused-Info')]:
    for field in ['action_trace','counts','forced_counts','type_answers','costs','final_guess']:
     if local[new][field]!=local[old][field]:raise RuntimeError('Literal baseline parity failed: '+field)
    clean=lambda v:{k:x for k,x in v.items() if k!='timings_seconds'}
    if clean(local[new]['final_fit'])!=clean(local[old]['final_fit']):raise RuntimeError('Literal final GLR parity failed')
   print(json.dumps({'stage':'smoke','world':s['world_id'],'paths':len(local),'literal_parity':True}),flush=True)
  write_once(out/'paths.json',rows);receipt.update(status='completed',paths=len(rows),online_actions=sum(r['online'] for r in rows),offline_path_charges=sum(r['costs']['offline'] for r in rows),literal_parity=True)
 except Exception as e:receipt.update(status='failed',error=repr(e));raise
 finally:
  receipt.update(outer_wall_seconds=time.perf_counter()-start,outer_cpu_seconds=time.process_time()-cpu);(out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')

def worker_init():
 global _MODELS
 start,cpu=time.perf_counter(),time.process_time();_MODELS=load_models()
 write_once(ROOT/'artifacts/evaluation/worker_loads'/f'{os.getpid()}.json',{'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'gpu_jobs':0})

def job(args):
 s,private_seed,R,deadline,methods=args;rows=[]
 # Deterministic rotation avoids always timing the same method first; no outcome input.
 k=(s['index']+R//16)%len(methods);ordered=methods[k:]+methods[:k]
 for m in ordered:
  journal=ROOT/'artifacts/evaluation/journal'/f"{s['world_id']}_{R}_{m}.jsonl"
  rows.append(path(s,private_seed,R,m,_MODELS,deadline,journal))
 return rows

def evaluate():
 verify();verify_history();cfg=json.loads((ROOT/'config.json').read_text());private_seed=seed()
 if json.loads((ROOT/'artifacts/smoke/execution.json').read_text())['status']!='completed':raise RuntimeError('Successful smoke required')
 out=ROOT/'artifacts/evaluation';out.mkdir(exist_ok=False);(out/'journal').mkdir();(out/'worker_loads').mkdir()
 start,cpu=time.perf_counter(),time.process_time();deadline=time.monotonic()+cfg['evaluation']['hard_seconds'];rows=[]
 receipt={'status':'started','expected_paths':624,'new_training_updates':0,'qwen_calls':0,'gpu_jobs':0,'external_api_calls':0,'confirmation_worlds':0,'scientific_retries':0,'worker_count':2};write_once(out/'execution.json',receipt)
 jobs=[]
 for s in specs(cfg):
  if s['kind']=='smoke':continue
  for R in ([64] if s['kind']=='eval_variable' else cfg['evaluation']['risks']):jobs.append((s,private_seed,R,deadline,list(METHODS)))
 try:
  with (out/'paths.jsonl').open('x',buffering=1) as stream:
   with futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'),initializer=worker_init) as pool:
    pending=[pool.submit(job,j) for j in jobs]
    for i,f in enumerate(futures.as_completed(pending),1):
     results=f.result();rows.extend(results)
     for r in results:stream.write(json.dumps(r,allow_nan=False)+'\n')
     print(json.dumps({'stage':'evaluation','jobs_completed':i,'jobs_total':len(jobs),'paths':len(rows),'failed':sum(r['status']=='failed' for r in rows)}),flush=True)
  receipt.update(status='completed' if len(rows)==624 and all(r['status']=='completed' for r in rows) else 'incomplete',path_records=len(rows),failed_paths=sum(r['status']=='failed' for r in rows),online_actions=sum(r['online'] for r in rows),offline_path_charges=sum(r['costs']['offline'] for r in rows))
 except Exception as e:receipt.update(status='failed',error=repr(e),traceback=traceback.format_exc(),unexpected_worker_prefix_cost_unknown=True);raise
 finally:
  receipt.update(outer_wall_seconds=time.perf_counter()-start,outer_parent_cpu_seconds=time.process_time()-cpu);(out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':
 if len(sys.argv)!=2 or sys.argv[1] not in ['smoke','evaluate']:raise SystemExit('Use smoke or evaluate')
 {'smoke':smoke,'evaluate':evaluate}[sys.argv[1]]()
