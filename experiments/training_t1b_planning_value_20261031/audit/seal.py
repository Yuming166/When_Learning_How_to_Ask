"""Bind all deliverables and raw local evidence; never publish private seed."""
from pathlib import Path
import hashlib,json,platform,sys
import numpy,scipy
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((ROOT/'RESULTS.json').read_text());v=json.loads((ROOT/'VALIDATION.json').read_text());assert v['status']=='PASS'
 (ROOT/'RUNTIME.json').write_text(json.dumps({'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,
  'system':platform.system(),'machine':platform.machine(),'host':platform.node(),
  'branch':'training/t1b_planning_value','base_commit':'3186587',
  'thread_limits':{'OPENBLAS_NUM_THREADS':1,'OMP_NUM_THREADS':1},
  'worlds':96,'fixed_budget_paths':2592,'training_updates':0,'rl_training_rollouts':0,
  'gpu_calls':0,'qwen_calls':0,'external_model_calls':0,'confirmation_worlds':0,'automatic_retries':0},indent=2)+'\n')
 public={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='FINAL_RECEIPT.json' and
   'artifacts' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts}
 raw={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'artifacts').rglob('*')) if p.is_file()}
 receipt={'status':'COMPLETED_BOUNDED_DEVELOPMENT','decision':s['decision'],'public_files':public,'artifact_files':raw,
   'public_file_count':len(public),'artifact_file_count':len(raw),'source_freeze_sha256':sha(ROOT/'freeze.json'),
   'input_snapshot_sha256':sha(ROOT/'INPUT_SNAPSHOT.json'),'validation_sha256':sha(ROOT/'VALIDATION.json'),
   'source_files_preserved':True,'all_prior_t1a_public_files_preserved':v['t1a_all_public_files_preserved'],
   'worlds':96,'paths':2592,'primary_budget':32,'interface_adapter':'separate prototype; not used in frozen scientific evaluation',
   'fixed_budget_guess_count':2592,'terminal_strict_certificates':v['certified'],
   'training_updates':0,'rl_training_rollouts':0,'model_calls':0,'confirmation_worlds':0,'retries':0,
   'privacy':'raw private entropy/reproduction stay in ignored local artifacts; only hashes listed',
   'numerical_scope':'order32 numerical posterior and two-step planning; original certificate model/arithmetic unchanged'}
 (ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:v for k,v in receipt.items() if k not in ['public_files','artifact_files']}))
if __name__=='__main__':main()
