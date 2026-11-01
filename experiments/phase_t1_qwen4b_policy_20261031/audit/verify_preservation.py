"""Read-only final preservation audit; does not load models or private states."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path('/home/gaoym/When_Learning_How_to_Ask/experiments')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    baseline = json.loads((ROOT / 'audit/HISTORY_BEFORE.json').read_text())
    history, problems = [], []
    for entry in baseline['receipts']:
        folder = ORIGINAL / entry['experiment']
        receipt_path = folder / ('AUDIT_RECEIPT.json' if entry['experiment'] == 'phase1b_userbench_audit_20261030' else 'FINAL_RECEIPT.json')
        if digest(receipt_path) != entry['receipt_sha256']:
            problems.append(str(receipt_path))
        receipt = json.loads(receipt_path.read_text())
        bound = receipt.get('artifact_sha256', receipt.get('snapshot_files'))
        if not isinstance(bound, dict) or len(bound) != entry['bound_files']:
            raise ValueError('Historical receipt schema/count changed')
        mismatches = [name for name, expected in bound.items() if not (folder / name).is_file() or digest(folder / name) != expected]
        problems.extend(str(folder / name) for name in mismatches)
        history.append({'experiment': entry['experiment'], 'bound_files': len(bound), 'receipt_unchanged': digest(receipt_path) == entry['receipt_sha256'], 'mismatches': mismatches})
    freezes = []
    for name in ('generation_freeze.json', 'training_freeze.json', 'analysis_freeze.json'):
        data = json.loads((ROOT / name).read_text())
        mismatches = [key for key, value in data['files'].items() if not (ROOT / key).is_file() or digest(ROOT / key) != value]
        mismatches += [key for key, value in data['dependencies'].items() if not Path(key).is_file() or digest(Path(key)) != value]
        problems.extend(mismatches)
        freezes.append({'manifest': name, 'files': len(data['files']), 'read_only_dependencies': len(data['dependencies']), 'mismatches': mismatches})
    environment = json.loads((ROOT / 'audit/ENVIRONMENT.json').read_text())
    checkpoint = Path(environment['checkpoint'])
    checkpoint_mismatches = [key for key, value in environment['checkpoint_files'].items() if not (checkpoint / key).is_file() or (checkpoint / key).stat().st_size != value['bytes'] or digest(checkpoint / key) != value['sha256']]
    problems.extend(checkpoint_mismatches)
    total = sum(row['bound_files'] for row in history)
    if total != baseline['total_files']:
        problems.append('historical total differs')
    result = {'status': 'PASS' if not problems else 'FAIL', 'verified_unix_time': time.time(), 'historical_receipts': history, 'historical_bound_files': total, 'frozen_manifests': freezes, 'checkpoint_files': len(environment['checkpoint_files']), 'checkpoint_bytes': sum(x['bytes'] for x in environment['checkpoint_files'].values()), 'checkpoint_mismatches': checkpoint_mismatches, 'problems': problems, 'scope': 'File preservation only; no scientific model calls, no private seed or truth reads, no execution of earlier confirmation protocols.'}
    target = ROOT / 'audit/PRESERVATION.json'
    if target.exists():
        raise FileExistsError('Do not overwrite final preservation evidence')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'historical_bound_files': total, 'checkpoint_files': result['checkpoint_files'], 'frozen_manifests': len(freezes), 'problems': len(problems)}))
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
