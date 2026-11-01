"""Integrity verification; does not rerun the analytic proof or diagnostics."""
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def run():
    inputs=json.loads((ROOT/'INPUT_HASHES.json').read_text())
    receipt=json.loads((ROOT/'RECEIPT.json').read_text())
    for rel,expected in inputs.items():
        assert digest(REPO/rel)==expected,rel
    outputs=receipt['outputs_sha256']
    for rel,expected in outputs.items():
        assert digest(ROOT/rel)==expected,rel
    present={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
             and p.name!='RECEIPT.json' and '__pycache__' not in p.parts}
    assert present==set(outputs),(present-set(outputs),set(outputs)-present)
    checks=json.loads((ROOT/'IDENTITY_CHECKS.json').read_text())
    assert checks['status']=='PASS_EXACT_RATIONAL_ALGEBRA_CHECKS'
    assert checks['source_sha256']==digest(ROOT/'check_identities.py')
    for rel,expected in checks['dependencies'].items():
        assert digest(REPO/rel)==expected,rel
    assert checks['law_cases']==8640 and checks['count_outcomes']==66880
    assert checks['repacking_allocations']==12 and checks['cost_identities']==144
    for path in ROOT.glob('*.py'):
        compile(path.read_text(),str(path),'exec')
    for path in ROOT.glob('*.md'):
        for link in re.findall(r'\]\(([^\s)]+)\)',path.read_text()):
            if '://' in link or link.startswith('#'):continue
            assert (path.parent/link.split('#')[0]).exists(),(path.name,link)
    print(json.dumps(dict(status='PASS',historical_files_unchanged=len(inputs),
        sealed_outputs=len(outputs),diagnostic_source_bindings='PASS',local_links='PASS',
        general_theorem='Analytic proof; finite diagnostics are supplementary'),indent=2))


if __name__=='__main__':
    run()
