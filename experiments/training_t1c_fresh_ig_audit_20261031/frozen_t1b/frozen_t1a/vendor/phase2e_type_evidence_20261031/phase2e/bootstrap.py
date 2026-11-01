import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['qrelbench_v01_20261030','phase2a_theory_optimality_20261030','phase2b_alignment_20261031','phase2c_strong_baseline_20261031','phase2d_method_improvement_20261031']:
    p=str(ROOT.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
