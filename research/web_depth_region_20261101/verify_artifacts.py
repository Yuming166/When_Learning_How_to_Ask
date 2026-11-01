"""Verify seals, source bindings, and internal exact conclusions; no new research."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def run():
    receipt = json.loads((ROOT/'RECEIPT.json').read_text())
    inputs = json.loads((ROOT/'INPUT_HASHES.json').read_text())
    for rel, expected in inputs.items():
        assert digest(REPO/rel) == expected, rel
    outputs = receipt['outputs_sha256']
    for rel, expected in outputs.items():
        assert digest(ROOT/rel) == expected, rel
    present = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
               if p.is_file() and p.name != 'RECEIPT.json' and '__pycache__' not in p.parts}
    assert present == set(outputs), (present-set(outputs), set(outputs)-present)
    cert = json.loads((ROOT/'REGION_CERTIFICATE.json').read_text())
    assert cert['status'] == 'PASS_EXACT_CERTIFICATE_WITH_ANALYTIC_PERTURBATION_BOUNDS'
    assert cert['source_sha256'] == digest(ROOT/'certify_region.py')
    for rel, expected in cert['dependencies'].items():
        assert digest(REPO/rel) == expected, rel
    assert cert['arithmetic']['nuisance_cells'] == 950
    for key in ['fixed_point_dual_checks', 'robust_dual_checks']:
        checks = cert[key]
        assert len(checks) == 27
        assert len({tuple(row['action']) for row in checks}) == 27
        assert all(F(row['slack_lower_display']) > 0 for row in checks)
    assert F(cert['witness']['perturbed_information_margin_lower']) == F(9, 28000)
    assert cert['intervals']['alpha'] == ['19/20', '6/5']
    assert cert['intervals']['c_over_ell'] == ['1/2', '3/2']
    for row in cert['conclusions']:
        gap, saving = F(row['uniform_additive_gap']), F(row['relative_saving_lower'])
        assert saving == gap/(42+gap)
    for path in ROOT.glob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    for path in ROOT.glob('*.md'):
        for link in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            assert (path.parent/link.split('#')[0]).exists(), (path.name, link)
    print(json.dumps(dict(status='PASS', historical_files_unchanged=len(inputs),
        sealed_outputs=len(outputs), continuous_domain_cells=950,
        fixed_depth_actions_checked=27, certificate_source_bindings='PASS',
        local_links='PASS', scope='Integrity verification; mathematical certificate generated separately'),
        indent=2))


if __name__ == '__main__':
    run()
