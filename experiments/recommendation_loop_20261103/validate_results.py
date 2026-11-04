"""Deterministic final audit of existing records; collect no new responses."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import unittest

for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[variable] = '1'

import matplotlib
import numpy as np
import scipy

from analyze import verify_raw
from finalize_analysis import load_records
from policies import ObservablePolicy
from relative_ig import RelativeIGPolicy
from reproduce_in_copy import prepare_copy
from run_loop import make_worlds

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    primary = json.loads((HERE / 'FREEZE.json').read_text())
    repair = json.loads((HERE / 'REPAIR_FREEZE.json').read_text())
    for base, hashes in [(HERE, primary['source_sha256']),
                         (ROOT, primary['dependency_sha256']),
                         (HERE, repair['sources'])]:
        for name, digest in hashes.items():
            assert sha(base / name) == digest, name
    assert sha(HERE / 'FREEZE.json') == repair['original_freeze_sha256']
    config, worlds, records = load_records()
    assert worlds == make_worlds(config)
    assert hashlib.sha256(json.dumps(worlds, sort_keys=True).encode()).hexdigest() == primary['worlds_sha256']
    world_map = {w['id']: w for w in worlds}
    original = [r for (w, a), r in records.items() if a != 'decision_ig_relative_repair']
    repaired = [r for (w, a), r in records.items() if a == 'decision_ig_relative_repair']
    assert len(original) == 40 and len(repaired) == 8
    plan = json.loads((HERE / 'artifacts/pilot/planned_jobs.json').read_text())
    assert {(r['world_id'], r['arm']) for r in original} == {(r['world_id'], r['arm']) for r in plan}
    assert len(plan) == 40
    raw_replay = verify_raw(original + repaired, world_map, config)
    policy_replay = []
    for record in original + repaired:
        repaired_arm = record['arm'] == 'decision_ig_relative_repair'
        factory = RelativeIGPolicy if repaired_arm else ObservablePolicy
        arm = 'decision_ig' if repaired_arm else record['arm']
        policy = factory(arm, world_map[record['world_id']]['public'],
                         quadrature_order=config['quadrature_order'],
                         rate_gap=config['unidentified_rate_gap'],
                         tolerance=config['planner_tolerance'],
                         max_iterations=config['planner_max_iterations'])
        # Read each stored reply only AFTER reproducing that step's action.
        # Future records and private fields never enter the policy object.
        for event in record['history']:
            assert policy.next() == event['action'], (record['world_id'], record['arm'], event['t'])
            assert policy.last_choice['forced'] == event['forced']
            policy.observe(event['action'], event['answer'])
        assert policy.counts.tolist() == record['counts']
        policy_replay.append({'world_id': record['world_id'], 'arm': record['arm'],
                              'actions': policy.t, 'status': 'EXACT_ACTION_HISTORY_MATCH'})
    # Exercise copying and source checks only; do not run a second experiment.
    with tempfile.TemporaryDirectory(prefix='recommendation-copy-check-') as scratch:
        copied, references = prepare_copy(Path(scratch) / 'minimal')
        for name, digest in primary['source_sha256'].items():
            assert sha(copied / name) == digest, name
        for name, digest in primary['dependency_sha256'].items():
            assert sha(copied.parents[1] / name) == digest, name
        assert not (copied / 'artifacts').exists()
        assert not (copied / 'REPAIR_FREEZE.json').exists()
        assert len(references['primary']) == 40 and len(references['repair']) == 8
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_*.py')
    buffer = io.StringIO()
    tests = unittest.TextTestRunner(stream=buffer, verbosity=1).run(suite)
    assert tests.wasSuccessful() and tests.testsRun == 43, buffer.getvalue()
    (HERE / 'results/test_output.txt').write_text(buffer.getvalue())

    base = primary['base_commit']
    old_changes = subprocess.run(
        ['git', 'diff', '--name-only', base, '--', '.', f':(exclude){RELATIVE}/**'],
        cwd=ROOT, text=True, check=True, capture_output=True).stdout.splitlines()
    assert not old_changes, old_changes
    paper_hashes = {}
    for name in ['papers/www2027_recommendation_theory/main.tex',
                 'papers/www2027_recommendation_theory/main.pdf']:
        old = subprocess.run(['git', 'show', f'{base}:{name}'], cwd=ROOT, check=True, capture_output=True).stdout
        assert hashlib.sha256(old).hexdigest() == sha(ROOT / name)
        paper_hashes[name] = sha(ROOT / name)

    # Credential scanning reports only path/category, never a matched secret.
    markers = {
        'github_credential': r'(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})',
        'provider_credential': r'\bsk-[A-Za-z0-9_-]{24,}\b',
        'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'credential_url': r'https?://[^/\s:@]+:[^/\s@]+@',
    }
    parse_counts = {'python': 0, 'json': 0, 'text': 0}
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix in ('.png', '.pdf'):
            continue
        content = path.read_text()
        parse_counts['text'] += 1
        for category, pattern in markers.items():
            assert not re.search(pattern, content), (str(path.relative_to(HERE)), category)
        if path.suffix == '.py':
            ast.parse(content)
            parse_counts['python'] += 1
        elif path.suffix == '.json':
            json.loads(content)
            parse_counts['json'] += 1
    raw_files = [p for p in sorted((HERE / 'artifacts').rglob('*')) if p.is_file()]
    raw_manifest = [{'path': str(p.relative_to(HERE)), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in raw_files]
    (HERE / 'RAW_MANIFEST.json').write_text(json.dumps({
        'scope': 'LOCAL_RAW_FILES_NOT_IMPLICITLY_PUBLISHED', 'files': raw_manifest}, indent=2) + '\n')
    smoke = []
    for stage in ('smoke', 'smoke_after_audit'):
        rows = json.loads((HERE / 'artifacts' / stage / 'summary.json').read_text())
        assert len(rows) == 10 and all(r['queries'] == 24 for r in rows)
        assert all(r['status'] == 'CAPPED_UNCERTIFIED' for r in rows)
        smoke.append({'stage': stage, 'attempted': len(rows), 'queries': sum(r['queries'] for r in rows),
                      'status': 'EXPECTED_SHORT_CAPS_NOT_EFFICACY'})
    relevant_sources = [p for p in HERE.iterdir() if p.suffix in ('.py', '.md') or
                        p.name in ('config.json', 'FREEZE.json', 'REPAIR_FREEZE.json')]
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'DEVELOPMENT_COMPLETE_NOT_CONFIRMATION',
        'base_commit': base,
        'unit_integration_tests': {'run': tests.testsRun, 'failures': len(tests.failures),
                                    'errors': len(tests.errors), 'result': 'PASS'},
        'original_frozen_local_files': len(primary['source_sha256']),
        'original_frozen_dependencies': len(primary['dependency_sha256']),
        'original_freeze_unchanged': True, 'repair_freeze_unchanged': True,
        'old_tracked_files_changed': old_changes, 'paper_sha256': paper_hashes,
        'primary_trajectories': len(original), 'repair_trajectories': len(repaired),
        'primary_queries': sum(r['queries'] for r in original),
        'repair_queries': sum(r['queries'] for r in repaired), 'smoke': smoke,
        'all_48_efficacy_paths_certified': all(r['status'] == 'CERTIFIED' for r in original + repaired),
        'wrong_certificates': sum(r.get('certified_correct') is False for r in original + repaired),
        'raw_replay': raw_replay, 'policy_action_replay': policy_replay,
        'reproduction_copy_preparation': 'PASS_WITH_ZERO_NEW_RESPONSES',
        'fresh_48_trajectory_wrapper_rerun': 'NOT_EXECUTED',
        'model_API_calls': 0, 'training_runs': 0, 'GPU_jobs': 0,
        'profile_clusters': len({w['profile_cluster'] for w in worlds}),
        'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                        'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__,
                        'platform': platform.platform()},
        'source_sha256': {p.name: sha(p) for p in sorted(relevant_sources)},
        'raw_manifest_sha256': sha(HERE / 'RAW_MANIFEST.json'),
        'parse_and_secret_scan': {'result': 'PASS', **parse_counts},
        'risk': 'Conditional analytic exp(-3); zero observed errors is not empirical certification.',
        'review_provenance': 'Same-family assistants; pre-outcome design/source review, not external expert review.',
    }
    (HERE / 'CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['stage', 'unit_integration_tests', 'primary_trajectories',
                                           'repair_trajectories', 'wrong_certificates',
                                           'reproduction_copy_preparation', 'old_tracked_files_changed']}, indent=2))


if __name__ == '__main__':
    main()
