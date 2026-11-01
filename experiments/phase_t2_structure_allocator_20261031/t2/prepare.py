"""Once-only source-frozen smoke, data generation, and teacher-only budgets."""
import json
import os
import secrets
import time
import traceback
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .core import Scheduler,observed_state,teacher_target
from .data import spec,make_world,execute_action,generate,plans,load_rows
from .integrity import verify,write_once

def public_plan(cfg):
    allplans=plans(cfg);pathrows=[];offrows=[]
    for split,worlds in allplans.items():
        if split.startswith('eval_'):
            risks=[64] if split=='eval_variable' else cfg['evaluation']['risks']
            for w in worlds:
                for R in risks:
                    for method in cfg['evaluation']['methods']:
                        pathrows.append({'world_id':w['world_id'],'split':split,'R':R,'method':method,'status':'not_applicable' if method=='T1-MLP' and sum(w['partition'])!=4 else 'completed'})
        elif split in cfg['data']['splits']:
            for w in worlds:
                for pos in range(6):
                    for model in ['T1-MLP','T2-MLP','DeepSets-KL','DeepSets-Info']:
                        offrows.append({'world_id':w['world_id'],'split':split,'position':pos,'state_d':sum(w['partition']),'model':model,'status':'not_applicable' if model=='T1-MLP' and sum(w['partition'])!=4 else 'completed'})
    return {'worlds':[{k:v for k,v in w.items() if k not in ['p','q','M','namespace']} for ws in allplans.values() for w in ws], 'expected_paths':pathrows,'expected_offline':offrows,'scope':'IDs and conditions for evaluator accounting only; never student input'}

def smoke(seed):
    from .information import radial_cost
    from .neural import HierarchicalDeepSets,Predictor
    from phase2b.log_glr import log_glr
    from phase2d.certified import certify_stop
    import torch
    torch.manual_seed(731100);torch.set_num_threads(1)
    pred=Predictor(HierarchicalDeepSets(),'deepsets_kl');out=[];start=time.perf_counter()
    for i,part in enumerate([[4],[1,3]]):
        s=spec('technical_smoke',i,part,[.8,.55],0,16);env,_=make_world(s,seed);public=env.reset();cal=env.get_calibration();sampler=Scheduler(public,cal,16)
        while sampler.t<64:
            if sampler.needs_update():
                state,_,_=observed_state(sampler,cal,16,6144);target=teacher_target(state);w=pred.predict(state);sampler.set_target(w)
                if not np.isfinite(radial_cost(state,w)):raise RuntimeError('Random smoke allocation not identifiable')
            execute_action(env,sampler)
        fit=log_glr(sampler.counts,sampler.groups,cal,sampler.types,sampler.type_accuracy,16,.05)
        gate=certify_stop(sampler.counts,sampler.groups,cal,sampler.types,sampler.type_accuracy,16,.05,candidate_theta=fit['theta'])
        out.append({'world_id':s['world_id'],'online':sampler.t,'costs':dict(env.cost),'gate_certified':gate['certified'],'weights_valid':True})
    return {'status':'passed','worlds':out,'wall_seconds':time.perf_counter()-start,'optimizer_updates':0,'model_api_calls':0,'gpu_jobs':0,'scope':'random-initialized neural forward only; interface check, not trained policy evidence'}

def budget_development(cfg,seed):
    from .evaluate import evaluate_path
    start=time.perf_counter();candidates=cfg['budget_development']['candidate_budgets'];rows=[]
    journal=ROOT/'artifacts/budget_development.jsonl'
    with journal.open('x') as stream:
        for s in plans(cfg)['budget_development']:
            row=evaluate_path(s,seed,64,'Fused-Original',{},candidates,deadline=time.monotonic()+300,budget_only=True)
            stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
            if row['status']!='completed':raise RuntimeError('Budget-development path failed')
            rows.append(row)
    accuracy={B:sum(next(x['guess_exact'] for x in r['readouts'] if x['budget']==B) for r in rows)/len(rows) for B in candidates}
    first=min(candidates,key=lambda B:(abs(accuracy[B]-.5),B));second=min([b for b in candidates if b!=first],key=lambda B:(abs(accuracy[B]-.8),B))
    value={'status':'frozen','readout_budgets':sorted([first,second]),'teacher_only_accuracy_curve':accuracy,'independent_worlds':len(rows),'student_predictions_used':0,'rule':cfg['budget_development']['selection'],'wall_seconds':time.perf_counter()-start,'test_results_used':0,'new_search_after_freeze':False}
    write_once(ROOT/'artifacts/BUDGET_FREEZE.json',value);return value

def audit_data(cfg):
    from .core import validate_state
    start=time.perf_counter();manifest=json.loads((ROOT/'artifacts/data/manifest.json').read_text());assert manifest['status']=='completed'
    seen={};n=0;tests=[]
    for split in ['train','validation']+cfg['data']['splits']:
        rows=load_rows(split);ids={r['world_id'] for r in rows};seen[split]=ids
        assert len(rows)==6*len(ids)
        for r in rows:
            s=validate_state(r['state']);w=np.asarray(r['teacher_weights']);assert len(w)==2*s['d']+len(s['groups']) and np.all(w>=0) and abs(w.sum()-1)<1e-7
            assert all(key not in s for key in ['world_id','p','q','truth','seed','types','reward','teacher_K'])
            n+=1
    for i,left in enumerate(seen):
        for right in list(seen)[i+1:]:assert not seen[left]&seen[right]
    with np.load(ROOT/'artifacts/data/train_cuts.npz',allow_pickle=False) as cuts:
        assert len(cuts.files)==2*1536
        for i,r in enumerate(load_rows('train')):
            c,b=cuts[f'c{i}'],cuts[f'b{i}'];assert c.shape[1]==len(r['teacher_weights']) and c.shape[0]==len(b) and np.all(np.isfinite(c)) and np.all(np.isfinite(b))
    value={'status':'PASS','rows_checked':n,'complete_world_split_disjoint':True,'strict_nested_student_whitelist':True,'teacher_targets_observable_only':True,'cuts_rows_checked':1536,'hidden_values_in_student_inputs':False,'wall_seconds':time.perf_counter()-start,'scope':'Source-backed legal-input and shape/data audit; no human/Natural validity or asymptotic proof.'}
    write_once(ROOT/'audit/DATA_LEAKAGE_AUDIT.json',value);return value

def main():
    verify('generation_freeze.json');cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'artifacts';out.mkdir(exist_ok=False)
    private=out/'private';private.mkdir(mode=0o700);seed=secrets.token_hex(32);path=private/'seed.json';write_once(path,{'development_seed':seed});path.chmod(0o600)
    write_once(private/'plan.json',plans(cfg));(private/'plan.json').chmod(0o600)
    write_once(out/'plan_public.json',public_plan(cfg));start=time.perf_counter();cpu=time.process_time()
    receipt={'status':'started','scientific_retries':0,'model_api_calls':0,'gpu_jobs':0};write_once(out/'prepare_execution.json',receipt)
    try:
        receipt['smoke']=smoke(seed);write_once(out/'smoke.json',receipt['smoke']);print(json.dumps({'stage':'smoke','status':'passed','worlds':2}),flush=True)
        receipt['data']=generate(cfg,seed)
        receipt['data_audit']=audit_data(cfg)
        receipt['budget_development']=budget_development(cfg,seed)
        receipt['status']='completed'
    except Exception as exc:
        receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());raise
    finally:
        receipt.update(outer_wall_seconds=time.perf_counter()-start,outer_cpu_seconds=time.process_time()-cpu)
        (out/'prepare_execution.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
