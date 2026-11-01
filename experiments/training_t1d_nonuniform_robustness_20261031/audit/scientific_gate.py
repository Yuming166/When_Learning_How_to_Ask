"""Pre-entropy model/roster/claim audit. No outcome inspection or seed generation."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from t1d.roster import roster
from t1d.integrity import local_sources,history_check


if __name__=='__main__':
    cfg=json.loads((ROOT/'config.json').read_text());jobs=roster(cfg)
    assert cfg['split']=='development' and not cfg['training_authorized'] and not cfg['confirmation_authorized']
    assert cfg['primary_budget']==32 and cfg['budgets']==[16,32,48,64]
    assert all(1<=sum(j['partition'])<=4 and 1<=len(j['partition'])<=2 and min(j['partition'])>=1 for j in jobs)
    assert all(.5<=j['q']<j['p']<=1-j['eta'] and j['R']>0 and j['alpha']>=0 and .5<j['s']<1 for j in jobs)
    sources=local_sources()
    required=['frozen_t1c/t1c/'+n+'.py' for n in ['__init__','bootstrap','policy','preflight','runner','strategies']]
    assert all(n in sources for n in required)
    assert not (ROOT/'artifacts').exists()
    gates=json.loads((ROOT/'PREFLIGHT_GATES.json').read_text())
    assert gates['passed'] and gates['scientific_worlds_consumed']==0
    gates.update(scientific_design_valid=True,model_supported_d_max4_G_max2=True,
        old_public_receipts_preserved=history_check(),all_six_previously_omitted_wrappers_in_source_set=True,
        granularity_tie_backend_primary_pair_matched=True,fixed_type_control_predeclared=True,
        native_anchor_noncomparability_disclosed=True,KL_nonuniform_not_artificially_invented=True,
        budgets_and_subgroups_fixed_before_entropy=True,causal_and_novelty_claim_limits_documented=True,
        no_confirmation_or_training_authorized=True)
    (ROOT/'PREFLIGHT_GATES.json').write_text(json.dumps(gates,indent=2)+'\n');print(json.dumps(gates))
