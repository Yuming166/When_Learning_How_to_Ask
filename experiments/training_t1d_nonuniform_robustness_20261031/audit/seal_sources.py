"""Seal only after engineering, scientific design and complete-closure gates."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from t1d.integrity import freeze


if __name__=='__main__':
    gates=json.loads((ROOT/'PREFLIGHT_GATES.json').read_text())
    if not gates['passed'] or not gates['scientific_design_valid']:raise RuntimeError('Preflight gates did not pass')
    result=freeze()
    required=['frozen_t1c/t1c/'+n+'.py' for n in ['__init__','bootstrap','policy','preflight','runner','strategies']]
    required+=['t1d/'+n+'.py' for n in ['__init__','bootstrap','integrity','policy','preflight','roster','runner','strategies']]
    sources=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())['sources']
    assert all(n in sources for n in required)
    print(json.dumps({'complete_coverage':True,**result}))
