"""Read-only reuse of frozen QRelBench data/channel/baseline implementations."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
V1=ROOT.parent/'qrelbench_v01_20261030'
if str(V1) not in sys.path:sys.path.insert(0,str(V1))
