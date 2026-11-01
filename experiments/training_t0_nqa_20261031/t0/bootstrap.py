from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
for p in sorted((ROOT/'vendor').glob('*')):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
