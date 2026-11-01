"""Read-only dependencies; neither historical experiment is modified."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V1=ROOT.parent/'qrelbench_v01_20261030'
P2A=ROOT.parent/'phase2a_theory_optimality_20261030'
for path in [V1,P2A]:
    if str(path) not in sys.path:sys.path.insert(0,str(path))
