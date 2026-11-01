"""Immutable source and historical receipts, no experiment on import."""
import hashlib
import json
import time
from pathlib import Path
from .bootstrap import ROOT,METHOD,T1

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def write_once(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def history_snapshot():
    files={};receipt_counts={}
    for folder,receipt_name in [(T1,'FINAL_RECEIPT.json'),(METHOD/'phase2e_type_evidence_20261031','FINAL_RECEIPT.json')]:
        receipt_path=folder/receipt_name;receipt=json.loads(receipt_path.read_text());files[str(receipt_path)]=sha(receipt_path)
        bound={}
        for key in ['artifact_sha256','public_files_sha256','local_public_artifacts_sha256']:bound.update(receipt.get(key,{}))
        for name,value in bound.items():
            p=folder/name
            if sha(p)!=value:raise RuntimeError('Historical receipt mismatch: '+str(p))
            files[str(p)]=value
        receipt_counts[folder.name]=len(bound)
    old=Path('/home/gaoym/When_Learning_How_to_Ask/experiments')
    for entry in json.loads((T1/'audit/HISTORY_BEFORE.json').read_text())['receipts']:
        folder=old/entry['experiment'];p=folder/('AUDIT_RECEIPT.json' if entry['experiment']=='phase1b_userbench_audit_20261030' else 'FINAL_RECEIPT.json')
        if sha(p)!=entry['receipt_sha256']:raise RuntimeError('Historical receipt changed')
        files[str(p)]=sha(p);d=json.loads(p.read_text());bound=d.get('artifact_sha256',d.get('snapshot_files'))
        for name,value in bound.items():
            if sha(folder/name)!=value:raise RuntimeError('Historical artifact changed')
            files[str(folder/name)]=value
        receipt_counts[entry['experiment']]=len(bound)
    value={'status':'PASS','checked_unix_time':time.time(),'receipt_bound_counts':receipt_counts,'unique_files':len(files),'files':files}
    continuation=json.loads((ROOT/'audit/CONTINUATION.json').read_text());old=Path(continuation['previous_attempt']);p=old/'FINAL_ATTEMPT_RECEIPT.json'
    if sha(p)!=continuation['previous_receipt_sha256']:raise RuntimeError('Failed initial attempt receipt changed')
    files[str(p)]=sha(p);bound=json.loads(p.read_text())['artifact_sha256']
    for name,h in bound.items():
        if sha(old/name)!=h:raise RuntimeError('Failed initial attempt artifact changed')
        files[str(old/name)]=h
    receipt_counts[old.name]=len(bound)
    value['unique_files']=len(files)
    write_once(ROOT/'audit/HISTORY_BEFORE.json',value);return value

def freeze(name,files):
    dependencies={}
    for package in ['qrelbench_v01_20261030/qrelbench','phase2a_theory_optimality_20261030/phase2a','phase2b_alignment_20261031/phase2b','phase2c_strong_baseline_20261031/phase2c','phase2d_method_improvement_20261031/phase2d','phase2e_type_evidence_20261031/phase2e']:
        for p in (METHOD/package).glob('*.py'):dependencies[str(p)]=sha(p)
    for name1 in ['t1/core.py','t1/mlp.py','artifacts/mlp/mlp_student.pt']:dependencies[str(T1/name1)]=sha(T1/name1)
    theory=Path('/home/gaoym/When_Learning_How_to_Ask/Theory_Note.md');dependencies[str(theory)]=sha(theory)
    value={'created_unix_time':time.time(),'files':{str(p):sha(ROOT/p) for p in sorted(set(files))},'dependencies':dependencies,'scope':'T2 bounded development only; no confirmation'}
    write_once(ROOT/name,value);return value

def verify(name):
    d=json.loads((ROOT/name).read_text())
    for p,v in d['files'].items():
        if sha(ROOT/p)!=v:raise RuntimeError('Frozen source changed: '+p)
    for p,v in d['dependencies'].items():
        if sha(p)!=v:raise RuntimeError('Read-only dependency changed: '+p)
    return d

def verify_history():
    d=json.loads((ROOT/'audit/HISTORY_BEFORE.json').read_text());bad=[p for p,h in d['files'].items() if sha(p)!=h]
    return {'status':'PASS' if not bad else 'FAIL','checked_unix_time':time.time(),'unique_files':len(d['files']),'mismatches':bad}
