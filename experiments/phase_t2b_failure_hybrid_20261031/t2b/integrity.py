"""Hash-bound inputs, source freeze and historical preservation."""
import hashlib,json,time
from pathlib import Path
from .bootstrap import ROOT,T2,T1A,T1B

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write_once(path,value):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def snapshot():
 files={}
 for root,keys in [(T2,['artifact_sha256']),(T1A,['public_files','artifact_files']),(T1B,['public_files','artifact_files'])]:
  p=root/'FINAL_RECEIPT.json';receipt=json.loads(p.read_text());files[str(p)]=sha(p)
  for key in keys:
   for name,value in receipt[key].items():
    p=root/name
    if sha(p)!=value:raise RuntimeError('Historical receipt mismatch: '+str(p))
    files[str(p)]=value
 history=json.loads((T2/'audit/HISTORY_BEFORE.json').read_text())['files']
 for p,h in history.items():
  if sha(p)!=h:raise RuntimeError('Earlier historical mismatch')
  files[p]=h
 value={'status':'PASS','unique_files':len(files),'files':files,'created_unix_time':time.time()}
 write_once(ROOT/'audit/HISTORY_BEFORE.json',value);return value

def verify_history():
 d=json.loads((ROOT/'audit/HISTORY_BEFORE.json').read_text());bad=[p for p,h in d['files'].items() if sha(p)!=h]
 if bad:raise RuntimeError('Historical artifacts changed')
 return {'status':'PASS','files':len(d['files'])}

def freeze():
 deps={}
 for name in ['generation_freeze.json','training_freeze.json','analysis_freeze.json']:
  d=json.loads((T2/name).read_text())
  for p,h in d['dependencies'].items():
   if sha(p)!=h:raise RuntimeError('T2 dependency mismatch')
   deps[p]=h
 for p in (T2/'t2').glob('*.py'):deps[str(p)]=sha(p)
 for kind in ['deepsets_kl','deepsets_info']:
  for p in (T2/'artifacts/training/models'/kind).iterdir():
   if p.is_file():deps[str(p)]=sha(p)
 for name in ['artifacts/prepare_execution.json','artifacts/training/execution.json']:deps[str(T2/name)]=sha(T2/name)
 deps[str(T1A/'t1a/solvers.py')]=sha(T1A/'t1a/solvers.py')
 names=[p for folder in ['t2b','tests'] for p in (ROOT/folder).glob('*.py')]
 names += [ROOT/n for n in ['config.json','HYBRID_CONTROLLER_PROTOCOL.md','POLICY_ALIGNMENT_AUDIT.md','FAILURE_STATE_ATTRIBUTION.md','ANALYSIS_SCOPE.md','artifacts/plan_public.json','audit/PRE_RUN_REVIEW.md','CONDITIONAL_TRAINING_PROPOSAL.md']]
 names += list((ROOT/'logs').glob('*tests*.log'))
 files={str(p.relative_to(ROOT)):sha(p) for p in names}
 d={'files':files,'dependencies':deps,'created_unix_time':time.time(),'scope':'T2b no-training bounded independent development; before new world sampling'}
 write_once(ROOT/'generation_freeze.json',d);return d

def verify(name='generation_freeze.json'):
 d=json.loads((ROOT/name).read_text())
 for p,h in d['files'].items():
  if sha(ROOT/p)!=h:raise RuntimeError('Frozen source changed: '+p)
 for p,h in d['dependencies'].items():
  if sha(p)!=h:raise RuntimeError('Frozen dependency changed: '+p)
 return d
