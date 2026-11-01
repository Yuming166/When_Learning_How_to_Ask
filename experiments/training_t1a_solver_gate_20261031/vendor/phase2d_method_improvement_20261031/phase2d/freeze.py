"""Explicit one-time development freeze; never creates confirmation seeds."""
import json
import os
import secrets
import time
from .bootstrap import ROOT,V1,P2A,P2B,P2C
from .runner import digest,frozen_files,jobs
from .integrity import history


def main():
    if (ROOT/'freeze.json').exists() or (ROOT/'artifacts/run').exists():
        raise RuntimeError('Already frozen or executed; no replacement/retry')
    if 'FINAL PRE-SEED VERDICT: PASS' not in (ROOT/'audit/EXECUTION_REVIEW.md').read_text():
        raise RuntimeError('Pre-seed execution/analysis review incomplete')
    if any(os.getenv(k)!='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']):
        raise RuntimeError('Set backend thread variables before importing Python')
    cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
    if len(plan)!=64 or len({j['index'] for j in plan})!=64:raise RuntimeError('Plan drift')
    historical=history();seedfile=ROOT/'artifacts/private/seed.json'
    if sum(r['files_verified'] for r in historical)!=353:raise RuntimeError('Historical manifest count changed')
    expected_theory=json.loads((P2C/'freeze.json').read_text())['theory_sha256']
    if digest(ROOT.parents[1]/'Theory_Note.md')!=expected_theory:raise RuntimeError('Original theory changed before freeze')
    if seedfile.exists():raise RuntimeError('No seed replacement')
    audits=['TYPE_BASELINE_SPEC.md','CERTIFIED_STOPPING_SPEC.md','STOPPING_PROOF_AUDIT.md','audit/stopping_independent_checks.py',
            'audit/EXECUTION_REVIEW.md','audit/HISTORY_PRESERVATION_BEFORE.json','RUNTIME.json']
    dependencies={}
    for name,base,package in [('v1',V1,'qrelbench'),('phase2a',P2A,'phase2a'),('phase2b',P2B,'phase2b'),('phase2c',P2C,'phase2c')]:
        dependencies[name]={str(p.relative_to(base)):digest(p) for p in sorted((base/package).glob('*.py'))}
    freeze={'frozen_unix_time':time.time(),'scope':'one bounded development batch, no confirmation',
        'files':frozen_files(),'audits':{p:digest(ROOT/p) for p in audits},'dependencies':dependencies,
        'theory_sha256':digest(ROOT.parents[1]/'Theory_Note.md'),
        'historical_files_verified':sum(r['files_verified'] for r in historical),
        'planned_worlds':len(plan),'planned_trajectories':4*len(plan),'confirmation_seed_created':False}
    # Bind the reviewed source/config/analysis before drawing any main seed.
    preseed=ROOT/'artifacts/preseed_source_commitment.json'
    with preseed.open('x') as f:json.dump(freeze,f,indent=2);f.write('\n')
    seedfile.parent.mkdir(mode=0o700,exist_ok=True)
    with seedfile.open('x') as f:json.dump({'development_seed':secrets.token_hex(32),'split':'development','confirmation':False},f,indent=2);f.write('\n')
    seedfile.chmod(0o600)
    freeze['preseed_source_commitment']=digest(preseed)
    freeze['private_seed_commitment']=digest(seedfile)
    (ROOT/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    print(json.dumps({k:v for k,v in freeze.items() if k not in ['files','audits','dependencies']},indent=2))


if __name__=='__main__':main()
