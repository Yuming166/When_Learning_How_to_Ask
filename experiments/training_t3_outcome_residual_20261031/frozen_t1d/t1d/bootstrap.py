import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/'frozen_t1c'
sys.path.insert(0,str(FROZEN))
from t1c import bootstrap as frozen_bootstrap
