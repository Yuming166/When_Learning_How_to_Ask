"""Run existing engineering fixtures from the published checkout only."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CORE = [
    "qrelbench_v01_20261030", "phase2a_theory_optimality_20261030",
    "phase2b_alignment_20261031", "phase2c_strong_baseline_20261031",
    "phase2d_method_improvement_20261031", "phase2e_type_evidence_20261031",
]
OPTIONAL = ["training_t3_outcome_residual_20261031"]
CHILD = r'''
import json, pathlib, sys, unittest
sys.dont_write_bytecode = True
root = pathlib.Path(sys.argv[1]).resolve()
suite = unittest.defaultTestLoader.discover('tests')
result = unittest.TextTestRunner(verbosity=1).run(suite)
prefixes = ('qrelbench', 'phase2a', 'phase2b', 'phase2c', 'phase2d', 'phase2e',
            't1a', 't1b', 't1c', 't1d', 't3')
outside = []
for name, module in list(sys.modules.items()):
    if name.split('.')[0] not in prefixes or not getattr(module, '__file__', None):
        continue
    path = pathlib.Path(module.__file__).resolve()
    if not path.is_relative_to(root):
        outside.append({'module': name, 'file': str(path)})
print(json.dumps({'tests': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'skipped': len(result.skipped),
                  'outside_checkout_modules': outside}))
sys.exit(0 if result.wasSuccessful() and not outside else 1)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="append", choices=CORE + OPTIONAL)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    checks = []
    with tempfile.TemporaryDirectory(prefix="learning-how-to-ask-checks-") as temp:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
               "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
               "MKL_NUM_THREADS": "1", "CUDA_VISIBLE_DEVICES": "",
               "MPLCONFIGDIR": temp, "XDG_CACHE_HOME": temp,
               "PYTHONPATH": os.pathsep.join(str(ROOT/"experiments"/s) for s in CORE)}
        for stage in args.stage or CORE:
            started = time.monotonic()
            try:
                proc = subprocess.run([sys.executable, "-c", CHILD, str(ROOT)],
                                      cwd=ROOT/"experiments"/stage, env=env,
                                      text=True, capture_output=True, timeout=args.timeout)
                summaries = [line for line in proc.stdout.splitlines() if line.startswith('{"tests":')]
                row = {"stage": stage, "exit_code": proc.returncode,
                       "elapsed_seconds": round(time.monotonic()-started, 3)}
                if summaries:
                    row.update(json.loads(summaries[-1]))
                else:
                    row["missing_test_summary"] = True
                if proc.returncode:
                    row["failure_details"] = (proc.stdout + proc.stderr)[-18000:]
            except subprocess.TimeoutExpired:
                row = {"stage": stage, "exit_code": 124, "timeout_seconds": args.timeout}
            checks.append(row)
            print(json.dumps(row), flush=True)
    passed = all(r["exit_code"] == 0 and not r.get("missing_test_summary") for r in checks)
    report = {"scope": "existing engineering fixtures, not new scientific runs",
              "passed": passed, "checks": checks, "new_model_calls": 0,
              "new_training_runs": 0, "confirmation_runs": 0}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
