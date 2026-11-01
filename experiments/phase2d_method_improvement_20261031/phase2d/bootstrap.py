"""Read-only historical packages, resolved relative to this experiment."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V1=ROOT.parent/'qrelbench_v01_20261030'
P2A=ROOT.parent/'phase2a_theory_optimality_20261030'
P2B=ROOT.parent/'phase2b_alignment_20261031'
P2C=ROOT.parent/'phase2c_strong_baseline_20261031'
for path in [V1,P2A,P2B,P2C]:
    if str(path) not in sys.path:sys.path.insert(0,str(path))
