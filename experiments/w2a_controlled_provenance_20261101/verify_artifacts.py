"""Read-only W2a verification. --recompute also replays all frozen numeric rows.

No network, model clients, corpus regeneration or human-attestation writes.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def load(name):return json.loads((ROOT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(recompute=False):
    freeze=load('FREEZE_RECEIPT.json');assert sha(ROOT/'PROTOCOL.json')==freeze['protocol_sha256']
    parentfiles=0
    for p in freeze['parents']:
        base=ROOT.parent/p['directory'];assert sha(base/'MANIFEST.sha256')==p['manifest_sha256']
        for f in p['files']:assert sha(base/f['path'])==f['sha256'];parentfiles+=1
    proto=load('PROTOCOL.json');laws=load('law_grid.json');costs=load('cost_grid.json')
    g=proto['law_grid'];expected=set(itertools.product(g['r'],g['a'],g['reads']))
    assert {(r['r'],r['a'],r['reads']) for r in laws}==expected and len(laws)==len(expected)
    g=proto['cost_grid'];expected=set(itertools.product(g['r'],g['a'],g['root_activation_cost'],g['budget']))
    assert {(r['r'],r['a'],r['root_cost'],r['budget']) for r in costs}==expected and len(costs)==len(expected)
    for r in costs:
        assert r['DP_risk']<=r['best_static_risk']+2e-12
        assert r['best_static_risk']<=min(r['repeat_risk'],r['fresh_risk'],r['best_fixed_depth_risk'])+2e-12
    inv=load('corpus/evaluator_only/SHA256SUMS.json')
    for f in inv:assert sha(ROOT/'corpus'/f['path'])==f['sha256']
    ic=load('INDEPENDENT_CHECKS.json');assert ic['status']=='PASS'
    assert sha(ROOT/'engine.py')==ic['engine_sha256']
    assert sha(ROOT/'independent_checks.py')==ic['independent_verifier_sha256']
    tv=load('theory_verification.json');assert tv['status']=='PASS'
    assert sha(ROOT/'theory_certificates.json')==tv['original_certificate_sha256']
    assert sha(ROOT/'verify_theory_certificates.py')==tv['verifier_sha256']
    policy=load('center_policy.json');assert sha(ROOT/'INDEPENDENT_EXPECTATIONS.json')==policy['source_receipt_sha256']
    import policy_audit
    assert F(policy_audit.evaluate(policy)['risk']['fraction'])==F(24899,100000)
    subprocess.run([sys.executable,str(ROOT/'generate_corpus.py'),'--verify-only'],check=True,
                   stdout=subprocess.DEVNULL)
    numeric=0
    if recompute:
        from engine import BudgetSolver,repeat_risk,fresh_risk,best_static_allocation
        for r in laws:
            assert abs(repeat_risk(r['reads'],r['r'],r['a'])-r['repeat_one_root_risk'])<2e-12
            assert abs(fresh_risk(r['reads'],r['r'],r['a'])-r['fresh_roots_risk'])<2e-12
            numeric+=2
        solvers={}
        for r in costs:
            key=(r['r'],r['a'],r['root_cost'])
            if key not in solvers:solvers[key]=BudgetSolver(*key)
            assert abs(solvers[key].initial(r['budget'])['risk']-r['DP_risk'])<2e-12
            s=best_static_allocation(r['budget'],r['root_cost'],r['r'],r['a'])
            assert abs(s['risk']-r['best_static_risk'])<2e-12
            numeric+=2
    manifest=ROOT/'MANIFEST.sha256';sealed=0
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            h,rel=line.split('  ',1);assert sha(ROOT/rel)==h,rel;sealed+=1
    return {'status':'PASS','read_only':True,'parent_files_unchanged':parentfiles,
            'law_configurations':len(laws),'cost_configurations':len(costs),
            'corpus_inventory_files':len(inv),'independent_value_comparisons':ic['comparison_count'],
            'numeric_values_recomputed':numeric,'sealed_files_checked':sealed,
            'model_calls':0,'new_web_requests':0}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--recompute',action='store_true')
    args=p.parse_args();print(json.dumps(verify(args.recompute),indent=2))
