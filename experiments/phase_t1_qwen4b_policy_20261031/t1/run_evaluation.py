"""One bounded seven-policy evaluation; all predictions and partial paths kept."""
from collections import OrderedDict
import json
from pathlib import Path
import time
import traceback

from .qwen import ROOT,dump,model_load,QwenPolicy,claim_device
from .freeze import verify


def selected_offline_rows():
    manifest=json.loads((ROOT/'artifacts/data/manifest.json').read_text())
    positions={0,3,6,9,15};result=[]
    for split in ['id_test','ood_parameters','ood_partition']:
        rows=[json.loads(x) for x in (ROOT/'artifacts/data'/manifest['splits'][split]['file']).open()]
        for world in [x for x in manifest['worlds'] if x['split']==split]:
            for k in sorted(positions):
                row=dict(rows[world['row_start']+k])
                row.update(world_id=world['world_id'],split=split,row_id=world['world_id']+f':{k}')
                result.append(row)
    assert len(result)==120
    return result


def main():
    import torch
    from .data import evaluation_world_plan
    from .mlp import MLPStudent
    from .evaluate import InferenceBudget,baseline_predictors,evaluate_offline,evaluate_world,METHODS
    verify('training_freeze.json')
    verify('analysis_freeze.json')
    assert json.loads((ROOT/'artifacts/training/execution.json').read_text())['status']=='completed'
    assert json.loads((ROOT/'artifacts/mlp/mlp_training.json').read_text())['status']=='completed'
    output=ROOT/'artifacts/evaluation'
    if output.exists():raise FileExistsError('No scientific evaluation retry/overwrite')
    output.mkdir()
    cfg=json.loads((ROOT/'config.json').read_text());started=time.perf_counter();cpu=time.process_time()
    deadline=started+cfg['evaluation']['hard_seconds'];budget=InferenceBudget(limit=600)
    receipt={'status':'started','policy_calls':budget.record(),'offline_requested_per_method':120,
        'closed_loop_worlds_requested':24,'diagnostic_worlds_requested':3,'methods':list(METHODS),
        'confirmation_worlds':0,'external_model_api_calls':0,'retries':0}
    dump(output/'execution.json',receipt)
    try:
        seed=json.loads((ROOT/'artifacts/private/seed.json').read_text())['development_seed']
        plan=evaluation_world_plan(cfg)
        diagnostic=[next(x for x in plan if x['split']==split) for split in ['eval_id','eval_ood_parameters','eval_ood_partition']]
        expected=json.loads((ROOT/'audit/EVALUATION_PLAN.json').read_text())
        assert [x['world_id'] for x in plan]==expected['evaluation_world_ids']
        assert [x['world_id'] for x in diagnostic]==expected['diagnostic_world_ids']
        model,tok,loadmeta=model_load(adapter=ROOT/'artifacts/adapters/final')
        torch.cuda.reset_peak_memory_stats()
        base=QwenPolicy(model,tok,adapter_enabled=False)
        lora=QwenPolicy(model,tok,adapter_enabled=True)
        mlp=MLPStudent.load(ROOT/'artifacts/mlp/mlp_student.pt')
        rows=selected_offline_rows();offline_summaries=[]
        with (output/'offline_predictions.jsonl').open('x') as log:
            def persist(row):log.write(json.dumps(row,allow_nan=False)+'\n');log.flush()
            for name,predictor in [('MLP',mlp),('BaseQwen',base),('LoRA',lora)]:
                result=evaluate_offline(rows,predictor,method=name,budget=budget,
                    is_qwen=name in ('BaseQwen','LoRA'),deadline=deadline,on_record=persist)
                offline_summaries.append(result['summary'])
                dump(output/'offline_summary.json',offline_summaries)
                dump(output/'call_budget.json',budget.record())
                print(json.dumps({'phase':'offline','method':name,'status':result['status'],'calls':budget.calls}),flush=True)
                if result['status']!='completed':raise RuntimeError('Incomplete offline evaluation: '+str(result.get('error')))
        methods=OrderedDict([('NativeAligned',None)])
        methods.update(baseline_predictors());methods['MLP']=mlp;methods['BaseQwen']=base;methods['LoRA']=lora
        assert list(methods)==list(METHODS)
        with (output/'events.jsonl').open('x') as eventlog,(output/'paths.jsonl').open('x') as paths:
            def event(item):eventlog.write(json.dumps(item,allow_nan=False)+'\n');eventlog.flush()
            for phase,specs,risk,isdiag in [('main',plan,64,False),('diagnostic',diagnostic,16,True)]:
                for i,spec in enumerate(specs):
                    result=evaluate_world(spec,seed,methods,R=risk,readouts=(256,512),public_cap=2048,
                        budget=budget,deadline=deadline,diagnostic=isdiag,on_event=event)
                    for row in result['records']:
                        row['evaluation_phase']=phase
                        paths.write(json.dumps(row,allow_nan=False)+'\n');paths.flush()
                    dump(output/'call_budget.json',budget.record())
                    print(json.dumps({'phase':phase,'world':i+1,'of':len(specs),'status':result['status'],'calls':budget.calls}),flush=True)
                    if result['status']!='completed':raise RuntimeError('Incomplete closed loop: '+str(result.get('not_run_methods')))
        receipt.update(status='completed',policy_calls=budget.record(),resident_model=loadmeta,
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            wall_seconds=time.perf_counter()-started,process_cpu_seconds=time.process_time()-cpu)
    except BaseException as exc:
        receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc(),policy_calls=budget.record(),
            wall_seconds=time.perf_counter()-started,process_cpu_seconds=time.process_time()-cpu)
        dump(output/'execution.json',receipt);raise
    dump(output/'execution.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='resident_model'},indent=2),flush=True)


if __name__=='__main__':
    with claim_device():main()
