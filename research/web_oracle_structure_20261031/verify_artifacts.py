"""Verify the sealed artifact set and unchanged historical inputs; no research run."""
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent

def run():
    receipt=json.loads((ROOT/'RECEIPT.json').read_text())
    inputs=json.loads((ROOT/'INPUT_HASHES.json').read_text())
    for name,digest in inputs.items():
        assert sha256((REPO/name).read_bytes()).hexdigest()==digest,name
    for name,digest in receipt['outputs_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    c=json.loads((ROOT/'DEPTH_MIXING_CERTIFICATE.json').read_text())
    assert c['status']=='PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE'
    assert c['source_sha256']==sha256((ROOT/'certify_depth_mixing.py').read_bytes()).hexdigest()
    dependency=ROOT.parent/'web_unknown_calibration_20261031/certify_threshold_failure.py'
    assert c['interval_dependency']['sha256']==sha256(dependency.read_bytes()).hexdigest()
    m=json.loads((ROOT/'MONOTONICITY_OBSTRUCTION_CERTIFICATE.json').read_text())
    assert m['script_sha256']==sha256((ROOT/'certify_monotonicity_obstruction.py').read_bytes()).hexdigest()
    data=json.loads((ROOT/'DISCOVERY_GRID.json').read_text())
    assert data['cases']==len(data['rows'])==768
    for path in ROOT.glob('*.py'):compile(path.read_text(),str(path),'exec')
    for path in ROOT.glob('*.md'):
        for link in re.findall(r'\]\(([^\s)]+)\)',path.read_text()):
            if '://' in link or link.startswith('#'):continue
            assert (path.parent/link.split('#')[0]).exists(),(path.name,link)
    print(json.dumps(dict(status='PASS',unchanged_historical_files=len(inputs),
                          sealed_outputs=len(receipt['outputs_sha256']),
                          certificate_source_hashes='PASS',local_links='PASS',
                          complete_main_discovery_cases=768),indent=2))

if __name__=='__main__':run()
