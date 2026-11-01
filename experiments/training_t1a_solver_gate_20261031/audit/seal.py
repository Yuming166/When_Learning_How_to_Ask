"""Hash receipts, without publishing private development entropy."""
import hashlib,json,platform,sys
from pathlib import Path
import numpy,scipy
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 result=json.loads((ROOT/'RESULTS.json').read_text());validation=json.loads((ROOT/'VALIDATION.json').read_text())
 assert validation['status']=='PASS'
 runtime={'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,
    'system':platform.system(),'machine':platform.machine(),'host':platform.node(),
    'thread_limits':{'OPENBLAS_NUM_THREADS':1,'OMP_NUM_THREADS':1},
    'worktree':'/home/gaoym/When_Learning_How_to_Ask_training_t1a','branch':'training/t1a_solver_baselines',
    'base_commit':'3186587','model_training_calls':0,'qwen_calls':0,'gpu_calls':0,'external_model_calls':0,
    'development_worlds':32,'confirmation_worlds':0,'new_methods_trained':0,'automatic_retries':0}
 (ROOT/'RUNTIME.json').write_text(json.dumps(runtime,indent=2)+'\n')
 public={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and
    p.name!='FINAL_RECEIPT.json' and 'artifacts' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts}
 artifact={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'artifacts').rglob('*')) if p.is_file()}
 receipt={'status':'COMPLETED_BOUNDED_DEVELOPMENT','decision':result['decision'],'primary':'AnalyticReuse',
   'public_files':public,'artifact_files':artifact,'public_file_count':len(public),'artifact_file_count':len(artifact),
   'historical_inputs_preserved':True,'frozen_source_preserved':True,'input_snapshot_sha256':sha(ROOT/'INPUT_SNAPSHOT.json'),
   'freeze_sha256':sha(ROOT/'freeze.json'),'validation_sha256':sha(ROOT/'VALIDATION.json'),
   'worlds':32,'trajectories':256,'seed_policy':'private fresh development entropy after source freeze; raw seed excluded from public files',
   'certified_outputs':sum(x['certified'] for x in result['arms'].values()),
   'wrong_certified_outputs':sum(x['wrong_certified'] for x in result['arms'].values()),
   'censored_trajectories':sum(x['censored'] for x in result['arms'].values()),
   'model_calls':0,'training_updates':0,'confirmation_worlds':0,'retries':0,
   'exclusions':'self hash excluded; private contents only hash-bound in ignored artifacts; pycache excluded'}
 (ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:v for k,v in receipt.items() if k not in ['public_files','artifact_files']}))
if __name__=='__main__':main()
