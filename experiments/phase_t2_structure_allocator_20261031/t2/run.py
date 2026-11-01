"""Once-only CPU fitting and bounded evaluation launchers."""
import concurrent.futures as futures
import json
import math
import multiprocessing
import os
import sys
import time
import traceback
from pathlib import Path
import numpy as np
from .bootstrap import ROOT,T1
from .integrity import verify,write_once,sha
from .data import load_rows,plans

ALIASES={'T2-MLP':'mlp','DeepSets-KL':'deepsets_kl','DeepSets-Info':'deepsets_info'}
_MODELS=None

def load_models():
    import torch
    from .neural import Predictor
    from t1.mlp import MLPStudent
    torch.set_num_threads(1)
    models={name:Predictor.load(ROOT/'artifacts/training/models'/kind) for name,kind in ALIASES.items()}
    models['T1-MLP']=MLPStudent.load(T1/'artifacts/mlp/mlp_student.pt')
    return models

def fit_all():
    from .neural import fit
    verify('training_freeze.json');cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'artifacts/training';out.mkdir(exist_ok=False)
    start,cpu=time.perf_counter(),time.process_time();receipt={'status':'started','models':{},'scientific_retries':0,'gpu_jobs':0,'qwen_calls':0}
    write_once(out/'execution.json',receipt)
    try:
        before=time.perf_counter();rows=load_rows('train',True);receipt['data_loading_wall_seconds']=time.perf_counter()-before
        for kind in cfg['training']['models']:
            write_once(out/'attempts'/f'{kind}.json',{'status':'started','kind':kind,'attempt':1,'started_unix_time':time.time()})
            before,before_cpu=time.perf_counter(),time.process_time()
            pred=fit(rows,kind,out/'models'/kind,steps=cfg['training']['steps'],seed=cfg['training']['seed'],batch_size=cfg['training']['batch_size'],lr=cfg['training']['lr'])
            receipt['models'][kind]={'outer_wall_seconds':time.perf_counter()-before,'outer_cpu_seconds':time.process_time()-before_cpu,'inner_receipt':pred.receipt,'checkpoint_sha256':sha(out/'models'/kind/'model.pt')}
            print(json.dumps({'phase':'fit','kind':kind,'status':'completed','outer_wall_seconds':receipt['models'][kind]['outer_wall_seconds']}),flush=True)
            (out/'execution.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
        receipt['status']='completed'
    except Exception as exc:
        receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());raise
    finally:
        receipt.update(outer_wall_seconds=time.perf_counter()-start,outer_cpu_seconds=time.process_time()-cpu)
        (out/'execution.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')

def offline(models,out,deadline):
    from .core import normalize
    from .information import radial_cost
    cfg=json.loads((ROOT/'config.json').read_text());count=0
    with (out/'offline.jsonl').open('x') as stream:
        for split in cfg['data']['splits']:
            for row in load_rows(split):
                state=row['state'];target=np.asarray(row['teacher_weights'],dtype=float)
                for name in ['T1-MLP','T2-MLP','DeepSets-KL','DeepSets-Info']:
                    if time.monotonic()>deadline:raise TimeoutError('Offline evaluation deadline')
                    result={'world_id':row['world_id'],'split':split,'position':row['position'],'state_d':state['d'],'model':name,'status':'completed'}
                    if name=='T1-MLP' and state['d']!=4:result['status']='not_applicable'
                    else:
                        before=time.perf_counter()
                        if name=='T1-MLP':
                            # Frozen T1 input receives the same counts, actual R/cap;
                            # its original feature scaling remains unchanged.
                            from t1.core import validate_state as validate_t1
                            ts={k:v for k,v in state.items() if k not in ['estimate']};ts['schema']='t1_observable_v1';ts['action_mask']=[1]*8+[int(g<len(state['groups'])) for g in range(2)]
                            prediction=models[name].predict(validate_t1(ts));w=np.asarray(prediction['weights10'])[:len(target)]
                        else:w=models[name].predict(state)
                        wall=time.perf_counter()-before;w=normalize(w,state);K=radial_cost(state,w);smooth=(w+1e-8)/(1+len(w)*1e-8);mask=target>0
                        result.update(allocation_l1=float(np.abs(target-w).sum()),forward_kl=float(np.sum(target[mask]*np.log(target[mask]/smooth[mask]))),radial_cost=float(K) if math.isfinite(K) else None,teacher_K=row['teacher_K'],relative_regret=float(K/row['teacher_K']-1) if math.isfinite(K) else None,radial_infinite=not math.isfinite(K),inference_wall_seconds=wall,weights=w.tolist())
                    stream.write(json.dumps(result,allow_nan=False)+'\n');stream.flush();count+=1
            print(json.dumps({'phase':'offline','split':split,'records':count}),flush=True)
    return count

def _worker_init():
    global _MODELS
    start,cpu=time.perf_counter(),time.process_time();_MODELS=load_models()
    write_once(ROOT/'artifacts/evaluation/worker_loads'/f'{os.getpid()}.json',{'pid':os.getpid(),'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'gpu_jobs':0})

def _job(job):
    from .evaluate import evaluate_path
    s,seed,R,readouts,deadline,methods=job;rows=[]
    for method in methods:
        journal=ROOT/'artifacts/evaluation/journal'/f"{s['world_id']}_{R}_{method}.jsonl";journal.parent.mkdir(exist_ok=True)
        with journal.open('x',buffering=1) as stream:
            def persist(record):stream.write(json.dumps(record,allow_nan=False)+'\n')
            row=evaluate_path(s,seed,R,method,_MODELS,readouts,deadline=deadline,on_progress=persist)
        rows.append(row)
        if row['status'] not in ['completed','not_applicable']:break
    return rows

def evaluate():
    verify('training_freeze.json');verify('analysis_freeze.json');cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'artifacts/evaluation';out.mkdir(exist_ok=False)
    start,cpu=time.perf_counter(),time.process_time();deadline=time.monotonic()+cfg['evaluation']['hard_seconds'];receipt={'status':'started','scientific_retries':0,'qwen_calls':0,'gpu_jobs':0,'external_api_calls':0,'expected_applicable_paths':852,'expected_nonapplicable_paths':6}
    write_once(out/'execution.json',receipt)
    try:
        before=time.perf_counter();models=load_models();receipt['parent_model_load_wall_seconds']=time.perf_counter()-before
        receipt['offline_records']=offline(models,out,deadline);del models
        seed=json.loads((ROOT/'artifacts/private/seed.json').read_text())['development_seed'];budgets=json.loads((ROOT/'artifacts/BUDGET_FREEZE.json').read_text())['readout_budgets'];allplans=plans(cfg);jobs=[]
        for split,worlds in allplans.items():
            if not split.startswith('eval_'):continue
            for s in worlds:
                for R in ([64] if split=='eval_variable' else cfg['evaluation']['risks']):jobs.append((s,seed,R,budgets,deadline,cfg['evaluation']['methods']))
        (out/'worker_loads').mkdir();completed=0;path_count=0;failed_count=0;not_applicable=0
        with (out/'paths.jsonl').open('x') as log:
            with futures.ProcessPoolExecutor(max_workers=cfg['evaluation']['workers'],mp_context=multiprocessing.get_context('spawn'),initializer=_worker_init) as pool:
                pending={pool.submit(_job,j):j[0]['world_id'] for j in jobs}
                for future in futures.as_completed(pending):
                    rows=future.result()
                    for row in rows:
                        log.write(json.dumps(row,allow_nan=False)+'\n');path_count+=1
                        failed_count+=int(row['status']=='failed');not_applicable+=int(row['status']=='not_applicable')
                    log.flush();completed+=1
                    print(json.dumps({'phase':'closed_loop','jobs_completed':completed,'jobs_total':len(jobs),'records':len(rows),'failed':sum(r['status']=='failed' for r in rows)}),flush=True)
        receipt.update(status='completed' if path_count==858 and failed_count==0 and not_applicable==6 else 'incomplete',world_risk_jobs=completed,path_records=path_count,failed_paths=failed_count,not_applicable_paths=not_applicable)
    except Exception as exc:
        receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc(),unexpected_worker_partial_cost_unknown=True);raise
    finally:
        receipt.update(outer_wall_seconds=time.perf_counter()-start,outer_parent_cpu_seconds=time.process_time()-cpu)
        (out/'execution.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ['fit','evaluate']:raise SystemExit('Use fit or evaluate')
    fit_all() if sys.argv[1]=='fit' else evaluate()
