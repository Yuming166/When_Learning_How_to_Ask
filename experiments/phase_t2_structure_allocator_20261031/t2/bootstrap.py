"""Read-only, hash-bound local dependencies; no provider or GPU imports."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
METHOD = (Path(__file__).resolve().parents[3] / 'experiments')
T1 = (Path(__file__).resolve().parents[3] / 'experiments/phase_t1_qwen4b_policy_20261031')
for name in ['qrelbench_v01_20261030', 'phase2a_theory_optimality_20261030', 'phase2b_alignment_20261031', 'phase2c_strong_baseline_20261031', 'phase2d_method_improvement_20261031', 'phase2e_type_evidence_20261031']:
    path = str(METHOD / name)
    if path not in sys.path:
        sys.path.insert(0, path)
if str(T1) not in sys.path:
    sys.path.append(str(T1))
