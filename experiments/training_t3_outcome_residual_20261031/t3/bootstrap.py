import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'frozen_t1d'))
from t1d import bootstrap as frozen_bootstrap
