import hashlib,json
from pathlib import Path
from .bootstrap import ROOT

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def sources():
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(ROOT.rglob('*.py'))
            if '__pycache__' not in p.parts and 'artifacts' not in p.relative_to(ROOT).parts}

def history():
    data=json.loads((ROOT/'HISTORICAL_INPUTS.json').read_text());n=0
    for entry in data['public_receipts'].values():
        for rel,h in entry['files'].items():
            if digest(Path(entry['root'])/rel)!=h:raise RuntimeError('History changed '+rel)
            n+=1
    for p,h in data['additional_readonly_files'].items():
        if digest(p)!=h:raise RuntimeError('Historical input changed '+p)
    return n

def freeze():
    if (ROOT/'SOURCE_MANIFEST.json').exists() or (ROOT/'artifacts').exists():raise RuntimeError('No reseal/retry')
    names=['config.json','T3_FROZEN_PROTOCOL.md','T3_POLICY_ARCHITECTURE.md','T3_ROLLOUT_TRAINING.md',
      'HISTORICAL_INPUTS.json','HISTORICAL_LEARNABILITY.json','LITERATURE_SOURCES.json','RUNTIME_DEPENDENCIES.json','PREFLIGHT.json']
    names += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'audit').glob('*.txt'))]
    data={'sources':sources(),'documents':{n:digest(ROOT/n) for n in names},'historical_public_files':history(),
      'scope':'complete recursive experiment Python source closure and inherited verified Python/NumPy/SciPy runtime; not full OS attestation'}
    (ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps(data,indent=2)+'\n');return verify()

def verify():
    data=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    if data['sources']!=sources():raise RuntimeError('Source set/bytes changed')
    for n,h in data['documents'].items():
        if digest(ROOT/n)!=h:raise RuntimeError('Protocol/document changed '+n)
    runtime=json.loads((ROOT/'RUNTIME_DEPENDENCIES.json').read_text())
    for p,h in runtime['files'].items():
        if digest(p)!=h:raise RuntimeError('Numerical runtime changed '+p)
    return {'passed':True,'sources':len(data['sources']),'documents':len(data['documents']),
      'runtime_files':len(runtime['files']),'historical_public_files':history(),'manifest_sha256':digest(ROOT/'SOURCE_MANIFEST.json')}
