import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in sorted((ROOT/'vendor').iterdir()):
    if p.is_dir():sys.path.insert(0,str(p))
