import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/'frozen_t1b'
sys.path.insert(0,str(FROZEN));sys.path.insert(0,str(FROZEN/'frozen_t1a'))
for p in sorted((FROZEN/'frozen_t1a/vendor').iterdir()):
    if p.is_dir():sys.path.insert(0,str(p))
