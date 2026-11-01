import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T1A=ROOT/'frozen_t1a'
sys.path.insert(0,str(T1A))
for p in sorted((T1A/'vendor').iterdir()):
    if p.is_dir():sys.path.insert(0,str(p))
