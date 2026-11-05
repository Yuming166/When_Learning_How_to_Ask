"""Prepare an isolated byte-identical snapshot; zero network/model calls."""
from __future__ import annotations
import ast
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LUNA = ROOT / 'experiments/myntra_luna_48profile_policy_v01_20261105'
LEGACY = ROOT / 'experiments/myntra_preference_dev_v01_20261104'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if (BASE / 'PREPARED.json').exists():
        raise RuntimeError('Snapshot already prepared; do not overwrite')
    old_freeze = json.loads((LUNA / 'FROZEN.json').read_text())
    for name, expected in old_freeze['files'].items():
        if digest(name) != expected:
            raise RuntimeError('Original Luna frozen source changed: ' + name)
    cfg = json.loads((LUNA / 'config.json').read_text())
    cfg.update(version='myntra-deepseek-48profile-policy-v0.1',
               requested_model='deepseek-v4.1-flash',
               base_url='https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1',
               accepted_reported_models=['deepseek-v4.1-flash', 'deepseek-v4.1-flash-1017'],
               api_parameters={'temperature': 1.0, 'top_p': 1.0,
                               'enable_thinking': True, 'reasoning_effort': 'high',
                               'max_tokens': 8192, 'stream': False},
               bootstrap_repetitions=10000, bootstrap_seed=202611041955,
               source_luna_experiment=str(LUNA),
               note='Same-data second deployment structured-answer transfer check; not human or held-out evidence.')
    cfg.pop('codex_cli_version_observed_before_freeze', None)
    (BASE / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
    shutil.copytree(LUNA / 'artifacts/input', BASE / 'artifacts/input')
    reference = BASE / 'artifacts/reference'
    reference.mkdir(parents=True)
    for filename in ('ANALYSIS.json', 'REPORT_ZH.md', 'PAIRED_POLICY_TRACES.jsonl'):
        shutil.copy2(LUNA / 'results' / filename, reference / ('LUNA_' + filename))
    shutil.copytree(LUNA / 'artifacts/run/records', reference / 'luna_records')
    shutil.copy2(LUNA / 'FROZEN.json', reference / 'LUNA_FROZEN.json')
    shutil.copy2(LUNA / 'parallel_replay_analysis.py', reference / 'luna_replay_source.py')
    shutil.copy2(LEGACY / 'environment.py', BASE / 'environment.py')
    shutil.copy2(LEGACY / 'config.json', reference / 'ENVIRONMENT_CONFIG.json')
    shutil.copy2(LUNA / 'engine.py', BASE / 'engine.py')
    source = (LUNA / 'parallel_replay_analysis.py').read_text()
    required = ['_reject_duplicate_keys', 'parse_field_answer', '_case_trace']
    functions = {n.name: ast.get_source_segment(source, n) for n in ast.parse(source).body
                 if isinstance(n, ast.FunctionDef) and n.name in required}
    header = ('from __future__ import annotations\nimport json\nfrom pathlib import Path\n'
              'import engine\nimport environment as ref\n'
              'CFG = json.loads((Path(__file__).resolve().parent / "config.json").read_text())\n\n')
    (BASE / 'replay.py').write_text(header + '\n\n'.join(functions[n] for n in required) + '\n')
    receipt = {'status': 'PREPARED_ZERO_MODEL_CALLS', 'original_luna_freeze_verified': True,
               'source_luna': str(LUNA), 'model_calls': 0,
               'engine_byte_equal': digest(BASE/'engine.py') == digest(LUNA/'engine.py'),
               'environment_byte_equal': digest(BASE/'environment.py') == digest(LEGACY/'environment.py'),
               'extracted_functions': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in functions.items()},
               'input_files': len([p for p in (BASE/'artifacts/input').rglob('*') if p.is_file()])}
    (BASE / 'PREPARED.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
