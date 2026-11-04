"""Explicitly requested reproduction only; never overwrite the research tree.

This entry point copies the hash-bound minimal pipeline into a NEW directory,
runs the same 40+8 bounded controlled trajectories, and checks terminal records
against the published aggregates. It is not used to generate new evidence for
the present development report. No model, API or training dependency is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


def prepare_copy(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('Reproduction destination must be new')
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError('Choose a reproduction destination outside this research tree')
    primary = json.loads((HERE / 'FREEZE.json').read_text())
    repair = json.loads((HERE / 'REPAIR_FREEZE.json').read_text())
    for base, hashes in [(HERE, primary['source_sha256']),
                         (ROOT, primary['dependency_sha256']),
                         (HERE, repair['sources'])]:
        for name, digest in hashes.items():
            if hashlib.sha256((base / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f'Frozen source mismatch: {name}')
    copied = destination / RELATIVE
    copied.mkdir(parents=True, exist_ok=False)
    for source in HERE.iterdir():
        if source.is_file() and (source.suffix in ('.py', '.md') or
                                 source.name in ('config.json', 'FREEZE.json')):
            shutil.copy2(source, copied / source.name)
    for name in primary['dependency_sha256']:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (copied / 'results').mkdir()
    # The one-shot repair runner creates its own manifest IN THIS NEW COPY.
    # Preserve the original as a reference without changing the source tree.
    shutil.copy2(HERE / 'REPAIR_FREEZE.json', copied / 'REPAIR_FREEZE.reference.json')
    references = {
        'primary': json.loads((HERE / 'results/analysis.json').read_text())['raw_replay'],
        'repair': json.loads((HERE / 'results/ig_repair.json').read_text())['raw_replay'],
    }
    (copied / 'reference_terminal_queries.json').write_text(json.dumps(references, indent=2) + '\n')
    return copied, references


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', required=True)
    parser.add_argument('--prepare-only', action='store_true',
                        help='Copy/check source without generating any responses')
    args = parser.parse_args()
    copied, references = prepare_copy(args.destination)
    if args.prepare_only:
        print(json.dumps({'prepared': str(copied), 'observations_generated': 0}))
        return
    environment = os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        environment[key] = '1'
    commands = [
        [sys.executable, '-B', str(copied / 'run_loop.py'), '--mode', 'pilot'],
        [sys.executable, '-B', str(copied / 'analyze.py')],
        [sys.executable, '-B', str(copied / 'run_ig_repair.py')],
        [sys.executable, '-B', str(copied / 'finalize_analysis.py')],
    ]
    for command in commands:
        subprocess.run(command, cwd=Path(args.destination).resolve(), env=environment, check=True)
    differences = []
    for stage, file in [('primary', 'analysis.json'), ('repair', 'ig_repair.json')]:
        actual = json.loads((copied / 'results' / file).read_text())['raw_replay']
        key = lambda r: (r['world_id'], r['arm'], r['status'], r['queries'],
                         r['terminal_certificate_rechecked'])
        if sorted(map(key, actual)) != sorted(map(key, references[stage])):
            differences.append(stage)
    verdict = {'terminal_queries_and_replay': 'MATCH' if not differences else 'MISMATCH',
               'different_stages': differences, 'independent_confirmation': False,
               'timings_expected_to_match': False, 'new_output': str(copied)}
    (copied / 'REPRODUCTION.json').write_text(json.dumps(verdict, indent=2) + '\n')
    print(json.dumps(verdict, indent=2))
    if differences:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
