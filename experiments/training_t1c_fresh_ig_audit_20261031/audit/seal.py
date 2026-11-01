"""Bind final public work and local artifacts; never expose private file contents."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(n):
    return json.loads((ROOT / n).read_text())


def public_files():
    return [p for p in sorted(ROOT.rglob('*')) if p.is_file() and
            p.name != 'FINAL_RECEIPT.json' and not any(x in p.parts for x in ['__pycache__', '.pytest_cache']) and
            'artifacts' not in p.relative_to(ROOT).parts and p.suffix != '.pyc']


def main():
    validation = load('VALIDATION.json')
    result = load('RESULTS.json')
    execution = load('artifacts/execution.json')
    for rel, h in load('freeze.json')['files'].items():
        assert digest(ROOT / rel) == h, rel
    for p, h in load('INPUT_SNAPSHOT.json')['files'].items():
        assert digest(Path(p)) == h, p
    for rel, spec in load('PROVENANCE_DEVIATION.json')['observed_t1c_sources'].items():
        assert digest(ROOT / rel) == spec['sha256'], rel
    assert validation['passed_observed_checks'], validation['error_examples']
    required = ['POLICY_SEMANTICS_AUDIT.md', 'REFRESH_VS_OBJECTIVE_ABLATION.md',
                'PAIRED_FINITE_BUDGET_RESULTS.md', 'COMPUTATIONAL_COST.md',
                'RL_ADDED_VALUE_ASSESSMENT.md', 'FINAL_DECISION.md']
    assert all((ROOT / p).is_file() for p in required)
    pub = {str(p.relative_to(ROOT)): digest(p) for p in public_files()}
    artifacts = {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT / 'artifacts').rglob('*')) if p.is_file()}
    receipt = {
        'status': 'COMPLETED_BOUNDED_DEVELOPMENT' if execution['status'] == 'completed' else 'BOUNDED_RUN_INCOMPLETE',
        'fresh_candidate_preregistered_gate': result['fresh_candidate_preregistered_gate'],
        'rl_added_value': result['rl_added_value'],
        'base_commit': '3186587', 'branch': 'training/t1c_fresh_ig_audit',
        'public_files': pub, 'artifact_files': artifacts,
        'public_file_count_excluding_receipt': len(pub), 'artifact_file_count': len(artifacts),
        'required_deliverables': required, 'source_freeze_sha256': digest(ROOT / 'freeze.json'),
        'preexecution_full_source_hash_binding': False,
        'provenance_deviation_sha256': digest(ROOT / 'PROVENANCE_DEVIATION.json'),
        'original_77_hash_bound_files_preserved': validation['original_hash_bound_files_preserved'],
        'poststart_t1c_snapshot_preserved': validation['poststart_local_source_preserved'],
        'full_historical_public_receipts': validation['old_public_receipts'],
        'validation_sha256': digest(ROOT / 'VALIDATION.json'),
        'input_snapshot_sha256': digest(ROOT / 'INPUT_SNAPSHOT.json'),
        'planned_independent_worlds': 96, 'completed_all_arms_budgets_worlds': result['complete_all_arms_budgets_worlds'],
        'planned_paths': validation['planned_paths'], 'finished_paths': validation['observed_paths'],
        'primary_budget': 32, 'acquisition_costs_including_partial': execution['costs_including_partial'],
        'fixed_budget_guesses_are_certificates': False,
        'training_updates': 0, 'rl_training_rollouts': 0, 'model_calls': 0,
        'confirmation_worlds': 0, 'retries': 0, 'automatic_next_stage': False,
        'privacy': 'artifacts and private new reproduction/entropy ignored by git; hash receipts only; no old seed or reserved confirmation access',
        'numerical_scope': result['numerical_scope'],
    }
    (ROOT / 'FINAL_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    # Stage only the audited public allow-list in this isolated worktree.
    repo = ROOT.parents[1]
    allowed = [str((ROOT / p).relative_to(repo)) for p in pub] + [str((ROOT / 'FINAL_RECEIPT.json').relative_to(repo))]
    subprocess.run(['git', 'add', '--', *allowed], cwd=repo, check=True)
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=repo, check=True)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=repo).decode().strip('\x00').split('\x00')
    assert set(staged) == set(allowed), 'Unexpected staging scope'
    for rel, h in pub.items():
        blob = subprocess.check_output(['git', 'show', ':' + str((ROOT / rel).relative_to(repo))], cwd=repo)
        assert hashlib.sha256(blob).hexdigest() == h, rel
    assert not any('/artifacts/' in p or '__pycache__' in p for p in staged)
    print(json.dumps({'receipt_written': True, 'staged_public_files': len(staged),
                      'artifact_files_local_only': len(artifacts), 'commit_created': False,
                      'required_deliverables': len(required), 'staged_scope_verified': True}))


if __name__ == '__main__':
    main()
