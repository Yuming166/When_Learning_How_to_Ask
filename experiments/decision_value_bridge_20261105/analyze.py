"""Frozen paired analysis, full adaptive replay, and common fixed-budget readout."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import run as harness
import numpy as np
from decision_value import BridgePolicy
from decision_ig import QuadratureDecisionIG
from legacy_analysis import verify_record, percentile
HERE=Path(__file__).resolve().parent

def audit_job(job):
    record,world,config=job
    receipt=verify_record(record,world,config)
    if record['history'] is None:
        return receipt,[dict(world_id=world['id'],cell_id=world['cell_id'],track=world['track'],catalogue_name=world['catalogue_name'],replicate=world['replicate'],R=world['R'],arm=record['arm'],budget=b,item=None,certified=False,carried_forward=False,available=False,correct=False) for b in config['fixed_budgets']]
    p=BridgePolicy(record['arm'],world['public'],quadrature_order=config['quadrature_order'],rate_gap=config['unidentified_rate_gap'],tolerance=config['planner_tolerance'],max_iterations=config['planner_max_iterations'])
    readout=QuadratureDecisionIG(world['public'],order=config['quadrature_order'])
    snapshots={}
    for event in record['history']:
        assert p.next()==event['action'],(world['id'],record['arm'],event['t'])
        if 'selected_gain' in event:
            assert np.isclose(p.last_choice['selected_gain'],event['selected_gain'],rtol=1e-12,atol=0.)
        p.observe(event['action'],event['answer'])
        readout.observe(event['action'],event['answer'])
        if event['t'] in config['fixed_budgets']:
            snapshots[event['t']]=int(np.argmax(readout._summary()['item_probability']))
    receipt['full_adaptive_replay']=True
    result=[]
    for budget in config['fixed_budgets']:
        carried=record['status']=='CERTIFIED' and record['queries']<=budget
        item=record['certified_output'] if carried else snapshots.get(budget)
        result.append(dict(world_id=world['id'],cell_id=world['cell_id'],track=world['track'],catalogue_name=world['catalogue_name'],replicate=world['replicate'],R=world['R'],arm=record['arm'],budget=budget,item=item,certified=carried,carried_forward=carried and record['queries']<budget,available=item is not None,correct=item is not None and item==world['private']['winner']))
    return receipt,result

def analyze(mode):
    source=HERE/'artifacts'/mode
    config=json.loads((source/'effective_config.json').read_text())
    if mode=='main':harness.check_freeze(config)
    worlds={w['id']:w for w in json.loads((source/'worlds.json').read_text())}
    plan=json.loads((source/'planned_jobs.json').read_text())
    assert len({(x['world_id'],x['arm']) for x in plan})==len(plan)
    records=[json.loads((source/f"{x['world_id']}__{x['arm']}.json").read_text()) for x in plan]
    assert {(r['world_id'],r['arm']) for r in records}=={(r['world_id'],r['arm']) for r in json.loads((source/'summary.json').read_text())}
    with ProcessPoolExecutor(max_workers=config['workers'],initializer=harness.worker_init) as pool:
        audited=list(pool.map(audit_job,[(r,worlds[r['world_id']],config) for r in records]))
    replay=[r for r,s in audited];snapshots=[row for r,s in audited for row in s]
    result=dict(stage=mode,attempted=len(records),certified=sum(r['status']=='CERTIFIED' for r in records),wrong_certified=sum(r.get('certified_correct') is False for r in records),capped=sum(r['status']=='CAPPED_UNCERTIFIED' for r in records),failed=sum(r['status'].startswith('FAILED') for r in records),postprocessing_failures=sum(r.get('postprocessing_failure') is not None for r in records),observed_queries=sum(r.get('queries') or 0 for r in records),observed_cpu_seconds=sum(r.get('cpu_seconds') or 0 for r in records),raw_replay=replay)
    if mode!='main':
        (source/'replay_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='raw_replay'}));return
    n=len(config['replicate_indices']); seeds=config['replicate_indices']; arms=config['arms']
    catalogues=list(dict.fromkeys(c['catalogue_name'] for c in config['cells']))
    rng=np.random.default_rng(config['bootstrap_seed'])
    draws={cat:rng.integers(0,n,(config['bootstrap_repetitions'],n)) for cat in catalogues}
    bykey={(r['cell_id'],r['R'],r['replicate'],r['arm']):r for r in records}
    cost=lambda r:r['queries'] if r['status']=='CERTIFIED' else config['max_queries']
    vectors={};aggregates=[];paired=[]
    for cell in config['cells']:
        cat=cell['catalogue_name']
        for R in cell.get('risk_R_values',config['risk_R_values']):
            for arm in arms:
                rows=[bykey[cell['id'],R,s,arm] for s in seeds]
                v=np.array([cost(r) for r in rows]);vectors[cell['id'],R,arm]=v
                aggregates.append(dict(cell_id=cell['id'],track=cell['track'],catalogue_name=cat,R=R,arm=arm,attempted=n,certified=sum(r['status']=='CERTIFIED' for r in rows),wrong_certified=sum(r.get('certified_correct') is False for r in rows),capped=sum(r['status']=='CAPPED_UNCERTIFIED' for r in rows),failed=sum(r['status'].startswith('FAILED') for r in rows),restricted_mean_queries=float(v.mean()),paired_seed_cost_vector=v.tolist(),bootstrap_mean_ci95=percentile(v[draws[cat]].mean(axis=1)),mean_policy_cpu_seconds=float(np.mean([r.get('policy_cpu_seconds') or 0 for r in rows])),mean_gate_cpu_seconds=float(np.mean([r.get('gate_cpu_seconds') or 0 for r in rows])),nonforced_choices=sum(sum(not e['forced'] for e in r['history'] or []) for r in rows),zero_gain_choices=sum(sum(e.get('zero_gain_fallback',False) for e in r['history'] or []) for r in rows)))
            for baseline in arms[1:]:
                diff=vectors[cell['id'],R,baseline]-vectors[cell['id'],R,'decision_value']
                paired.append(dict(cell_id=cell['id'],track=cell['track'],R=R,baseline=baseline,baseline_minus_DV_vector=diff.tolist(),mean_baseline_minus_DV=float(diff.mean()),bootstrap_ci95=percentile(diff[draws[cat]].mean(axis=1)),DV_lower_equal_higher=[int((diff>0).sum()),int((diff==0).sum()),int((diff<0).sum())]))
    pooled=[]
    for track,risks in [('anchor',config['risk_R_values']),('type_audit',[9])]:
        for R in risks:
            for baseline in arms[1:]:
                meanvec=[];boots=[]
                for cat in catalogues:
                    cells=[c['id'] for c in config['cells'] if c['track']==track and c['catalogue_name']==cat]
                    v=np.mean([vectors[c,R,baseline]-vectors[c,R,'decision_value'] for c in cells],axis=0)
                    meanvec.extend(v.tolist());boots.append(v[draws[cat]].mean(axis=1))
                pooled.append(dict(track=track,R=R,baseline=baseline,mean_baseline_minus_DV=float(np.mean(meanvec)),bootstrap_ci95=percentile(np.mean(boots,axis=0)),cluster_mean_difference_vector=meanvec))
    prefix=[]
    for cell in config['cells']:
        if cell['track']!='anchor':continue
        for seed in seeds:
            for arm in arms:
                lo,hi=[bykey[cell['id'],r,seed,arm] for r in config['risk_R_values']]
                if any(r['status'].startswith('FAILED') for r in (lo,hi)):continue
                lhs=[(e['action'],e['answer']) for e in lo['history']];rhs=[(e['action'],e['answer']) for e in hi['history']]
                assert lhs==rhs[:len(lhs)]
                prefix.append(dict(cell_id=cell['id'],replicate=seed,arm=arm,status='R_PREFIX_PASS'))
    snapby={(r['cell_id'],r['R'],r['replicate'],r['arm'],r['budget']):r for r in snapshots}
    snapagg=[];snapcomp=[]
    for track,risks in [('anchor',config['risk_R_values']),('type_audit',[9])]:
        for R in risks:
            for budget in config['fixed_budgets']:
                for arm in arms:
                    rows=[r for r in snapshots if r['track']==track and r['R']==R and r['budget']==budget and r['arm']==arm]
                    snapagg.append(dict(track=track,R=R,budget=budget,arm=arm,attempted=len(rows),correct=sum(r['correct'] for r in rows),available=sum(r['available'] for r in rows),certified=sum(r['certified'] for r in rows),carried_forward=sum(r['carried_forward'] for r in rows)))
                for baseline in arms[1:]:
                    vals=[];boots=[]
                    for cat in catalogues:
                        cells=[c['id'] for c in config['cells'] if c['track']==track and c['catalogue_name']==cat]
                        v=np.mean([[int(snapby[c,R,s,'decision_value',budget]['correct'])-int(snapby[c,R,s,baseline,budget]['correct']) for s in seeds] for c in cells],axis=0)
                        vals.extend(v.tolist());boots.append(v[draws[cat]].mean(axis=1))
                    snapcomp.append(dict(track=track,R=R,budget=budget,baseline=baseline,mean_DV_minus_baseline_accuracy=float(np.mean(vals)),bootstrap_ci95=percentile(np.mean(boots,axis=0))))
    result.update(aggregates=aggregates,paired_comparisons=paired,pooled_policy_comparisons=pooled,cross_R_prefix_checks=prefix,fixed_budget_snapshots=snapshots,fixed_budget_aggregates=snapagg,fixed_budget_comparisons=snapcomp,response_seed_clusters=12,main_anchor_trajectories=192,type_audit_trajectories=72,new_model_calls=0,cost_definition='certified queries; full 2500 for every cap/failure',uncertainty='10000 paired six-seed resamples per fixed catalogue, shared across partitions, types, risks and arms; conditional not population generalization')
    target=HERE/'results';target.mkdir(exist_ok=True)
    (target/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Decision Value bridge results','',f"{len(records)} trajectories: {result['certified']} certified, {result['capped']} capped, {result['failed']} failed, {result['wrong_certified']} wrong certified.",'','| Cell | R | Arm | Certified | Mean restricted queries | 95% conditional interval |','|---|---:|---|---:|---:|---|']
    for r in aggregates:lines.append(f"| {r['cell_id']} | {r['R']} | {r['arm']} | {r['certified']}/6 | {r['restricted_mean_queries']:.2f} | {r['bootstrap_mean_ci95']} |")
    lines+=['','Positive cost contrasts favor DV. Anchor and type-audit outcomes remain separate; pooled values weight catalogues equally and cells equally within each catalogue.','','| Track | R | Baseline | Baseline minus DV | 95% paired cluster interval |','|---|---:|---|---:|---|']
    for r in pooled:lines.append(f"| {r['track']} | {r['R']} | {r['baseline']} | {r['mean_baseline_minus_DV']:.2f} | {r['bootstrap_ci95']} |")
    lines+=['','## Fixed-budget common posterior-MAP readout','','These are complete-denominator counts. Uncertified guesses are not certificates; certified outputs are carried forward.','','| Track | R | Budget | Arm | Correct/attempted | Certified | Carried |','|---|---:|---:|---|---:|---:|---:|']
    for r in snapagg:lines.append(f"| {r['track']} | {r['R']} | {r['budget']} | {r['arm']} | {r['correct']}/{r['attempted']} | {r['certified']} | {r['carried_forward']} |")
    lines+=['','## Limits','','Decision Value is a one-step VOI instantiation with Q6 approximate joint belief, not a new VOI principle or an asymptotically optimal allocator. Exact GLR certification is inherited and independent of posterior scoring. Six seeds per fixed catalogue give limited uncertainty resolution; there are 12 response-tape clusters, not 264 independent users. Two all-positive constructed preference profiles, at most two groups, known partitions and iid rates remain substantial constraints. Type reversal/mixing is a bounded audit. No empirical oracle or unknown-versus-known-type premium is estimated. Full vectors, adaptive replay, failures, zero-gain counts, fixed-budget records and runtimes are retained in analysis.json.']
    (target/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    manifest={str(p.relative_to(HERE)):harness.digest(p) for p in sorted(source.glob('*.json'))}
    manifest['results/analysis.json']=harness.digest(target/'analysis.json')
    (HERE/'RECEIPT.json').write_text(json.dumps(dict(complete=True,planned=len(plan),observed=len(records),adaptive_replay_count=sum(r.get('full_adaptive_replay',False) for r in replay),cross_R_prefix_count=len(prefix),sha256=manifest),indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['attempted','certified','wrong_certified','capped','failed','observed_queries','observed_cpu_seconds','pooled_policy_comparisons']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['smoke','runtime_smoke','main'],default='main');analyze(p.parse_args().mode)
