"""One bounded post-hoc baseline repair; original pilot is never overwritten."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

import run_loop
from relative_ig import RelativeIGPolicy
from analyze import verify_raw

HERE=Path(__file__).resolve().parent


def main():
    original=json.loads((HERE/'FREEZE.json').read_text())
    for name,digest in original['source_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
    for name,digest in original['dependency_sha256'].items():
        assert hashlib.sha256((HERE.parents[1]/name).read_bytes()).hexdigest()==digest,name
    source=HERE/'artifacts/pilot'
    worlds=json.loads((source/'worlds.json').read_text())
    assert hashlib.sha256(json.dumps(worlds,sort_keys=True).encode()).hexdigest()==original['worlds_sha256']
    config=json.loads((source/'effective_config.json').read_text())
    freeze={'stage':'POSTHOC_NUMERICAL_BASELINE_REPAIR_NOT_CONFIRMATION','planned_trajectories':8,
            'original_freeze_sha256':hashlib.sha256((HERE/'FREEZE.json').read_bytes()).hexdigest(),
            'sources':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
                       ['relative_ig.py','test_relative_ig.py','run_ig_repair.py','REPAIR_PROTOCOL.md']},
            'only_algorithm_change':'scale-invariant relative tie tolerance instead of absolute1e-14',
            'original_Decision_KL_unchanged':True,'quadrature_order':6,'worlds_sha256':original['worlds_sha256']}
    assert not (HERE/'REPAIR_FREEZE.json').exists()
    (HERE/'REPAIR_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
    output=HERE/'artifacts/ig_repair';output.mkdir(exist_ok=False)
    results=[]
    run_loop.initialize_worker()
    # Explicit factory injection into the unchanged runner, scoped to this
    # sequential repair process. It changes only the baseline action tie rule.
    with patch.object(run_loop,'ObservablePolicy',RelativeIGPolicy):
        for world in worlds:
            r=run_loop.run_arm(world,'decision_ig',config)
            r['arm']='decision_ig_relative_repair';r['version']='POSTHOC_NUMERICAL_REPAIR'
            (output/f"{world['id']}.json").write_text(json.dumps(r,indent=2)+'\n')
            results.append(r)
            print(json.dumps({k:r[k] for k in ['world_id','arm','status','queries','certified_correct','failure']}),flush=True)
    replay=verify_raw(results,{w['id']:w for w in worlds},config)
    primary=json.loads((source/'summary.json').read_text())
    method={r['world_id']:r for r in primary if r['arm']=='decision_kl'}
    before={r['world_id']:r for r in primary if r['arm']=='decision_ig'}
    cap=config['max_queries'];cost=lambda r:r['queries'] if r['status']=='CERTIFIED' else cap
    pairs=[{'world_id':r['world_id'],'original_ig_queries':before[r['world_id']]['queries'],
            'repaired_ig_cost':cost(r),'repaired_ig_status':r['status'],
            'decision_kl_cost':cost(method[r['world_id']]),
            'decision_kl_status':method[r['world_id']]['status'],
            'both_certified':r['status']==method[r['world_id']]['status']=='CERTIFIED',
            'baseline_minus_method':cost(r)-cost(method[r['world_id']])} for r in results]
    summary={'stage':freeze['stage'],'attempted':len(results),
             'certified':sum(r['status']=='CERTIFIED' for r in results),
             'wrong_certified':sum(r.get('certified_correct') is False for r in results),
             'capped':sum(r['status']=='CAPPED_UNCERTIFIED' for r in results),
             'failed':sum(r['status'].startswith('FAILED') for r in results),
             'mean_repaired_IG_cost':float(np.mean([cost(r) for r in results])),
             'mean_original_IG_cost':float(np.mean([cost(r) for r in before.values()])),
             'mean_original_Decision_KL_cost':float(np.mean([cost(r) for r in method.values()])),
             'method_cost_lower':sum(x['baseline_minus_method']>0 for x in pairs),
             'method_cost_equal':sum(x['baseline_minus_method']==0 for x in pairs),
             'method_cost_higher':sum(x['baseline_minus_method']<0 for x in pairs),
             'new_controlled_observations':sum(r['queries'] or 0 for r in results),
             'mean_policy_seconds':float(np.mean([r['policy_seconds'] for r in results])),
             'pairs':pairs,'raw_replay':replay,'primary_results_overwritten':False}
    (HERE/'results/ig_repair.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('pairs','raw_replay')},indent=2))


if __name__=='__main__':main()
