"""Phase-specific immutable source commitments; no seed draw on import."""
from pathlib import Path
import hashlib
import json
import time

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=Path('/home/gaoym/When_Learning_How_to_Ask')


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def freeze(name,*,training=False):
    destination=ROOT/name
    if destination.exists():raise FileExistsError('Do not overwrite a freeze')
    relevant=['t1/core.py','t1/data.py','config.json','TRAINING_PROTOCOL.md',
              'audit/ENVIRONMENT.json','artifacts/smoke.json','artifacts/smoke_long.json',
              'audit/T1_DESIGN_REVIEW.md','audit/EVALUATION_PLAN.json','audit/HISTORY_BEFORE.json']
    if training:
        relevant+=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'t1').glob('*.py')) if p.name!='analyze.py']
        relevant+=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('*.py')) if p.name!='test_analysis.py']
        relevant+=['DATA_LEAKAGE_AUDIT.md','audit/TOKENIZATION.json','audit/T1_DESIGN_REVIEW.md',
                   'generation_freeze.json','artifacts/data/manifest.json']
        relevant+=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'artifacts/data').glob('*.jsonl'))]
    files={rel:digest(ROOT/rel) for rel in sorted(set(relevant))}
    dependencies={}
    for experiment,package in [('qrelbench_v01_20261030','qrelbench'),
        ('phase2a_theory_optimality_20261030','phase2a'),('phase2b_alignment_20261031','phase2b'),
        ('phase2c_strong_baseline_20261031','phase2c'),('phase2d_method_improvement_20261031','phase2d')]:
        for p in sorted((ORIGINAL/'experiments'/experiment/package).glob('*.py')):
            dependencies[str(p)]=digest(p)
    dependencies[str(ORIGINAL/'Theory_Note.md')]=digest(ORIGINAL/'Theory_Note.md')
    record={'created_unix_time':time.time(),'stage':'pre-training' if training else 'pre-new-development-seed',
        'files':files,'dependencies':dependencies,'scope':'T1-only development; no previous confirmation instances'}
    destination.write_text(json.dumps(record,indent=2)+'\n')
    return record


def verify(name):
    record=json.loads((ROOT/name).read_text())
    for rel,h in record['files'].items():assert digest(ROOT/rel)==h,rel
    for absolute,h in record['dependencies'].items():assert digest(absolute)==h,absolute
    return record


def freeze_analysis():
    destination=ROOT/'analysis_freeze.json'
    if destination.exists():raise FileExistsError('Do not overwrite analysis freeze')
    files={rel:digest(ROOT/rel) for rel in ['t1/analyze.py','tests/test_analysis.py']}
    record={'created_unix_time':time.time(),'stage':'before any held-out model evaluation',
            'files':files,'dependencies':{},'bootstrap':'world-clustered paired; 4000 resamples, seed731032',
            'scope':'analysis only, no fit/data/policy changes'}
    destination.write_text(json.dumps(record,indent=2)+'\n')
    return record
