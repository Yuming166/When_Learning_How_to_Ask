"""One audited CPU baseline fit, never a candidate search."""
import json
from .qwen import ROOT
from .freeze import verify
from .mlp import train_mlp


if __name__=='__main__':
    verify('training_freeze.json')
    assert 'FINAL PRE-TRAIN VERDICT: PASS' in (ROOT/'DATA_LEAKAGE_AUDIT.md').read_text()
    rows=[json.loads(x) for x in (ROOT/'artifacts/data/train.jsonl').open()]
    result=train_mlp(rows,ROOT/'artifacts/mlp')
    print(json.dumps({k:v for k,v in result.items() if k!='loss_history'},indent=2),flush=True)
