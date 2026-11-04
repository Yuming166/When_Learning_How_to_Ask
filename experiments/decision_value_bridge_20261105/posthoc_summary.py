"""Descriptive clarification after frozen run; no new experiments or inference."""
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import run
import numpy as np
HERE=Path(__file__).resolve().parent

def main():
    config=json.loads((HERE/'config.json').read_text());run.check_freeze(config)
    data=json.loads((HERE/'results/analysis.json').read_text())
    source=HERE/'artifacts/main'
    plan=json.loads((source/'planned_jobs.json').read_text())
    records=[json.loads((source/f"{p['world_id']}__{p['arm']}.json").read_text()) for p in plan]
    keys=['world_id','cell_id','R','replicate','arm','status','queries','restricted_cost','certified_correct','failure_type','failure_message']
    with (HERE/'results/paired_outcomes.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for r in records:
            writer.writerow({**{k:r.get(k) for k in keys[:7]},'restricted_cost':r['queries'] if r['status']=='CERTIFIED' else config['max_queries'],'certified_correct':r.get('certified_correct'),'failure_type':(r.get('failure') or {}).get('type'),'failure_message':(r.get('failure') or {}).get('message')})
    bykey={(r['world_id'],r['arm']):r for r in records}
    equal_cost=equal_history=zero=choices=0
    for r in records:
        if r['arm']!='decision_value':continue
        rr=bykey[r['world_id'],'round_robin']
        equal_cost+=r['queries']==rr['queries']
        equal_history+=[(e['action'],e['answer']) for e in r['history']]==[(e['action'],e['answer']) for e in rr['history']]
        events=[e for e in r['history'] if not e['forced']]
        choices+=len(events);zero+=sum(e['zero_gain_fallback'] for e in events)
    standardized=[]
    for track,risks in [('anchor',[3,9]),('type_audit',[9])]:
        for R in risks:
            for budget in config['fixed_budgets']:
                for arm in config['arms']:
                    rows=[r for r in data['fixed_budget_snapshots'] if r['track']==track and r['R']==R and r['budget']==budget and r['arm']==arm]
                    rates={cat:float(np.mean([r['correct'] for r in rows if r['catalogue_name']==cat])) for cat in ['weighted5','genuine6']}
                    standardized.append(dict(track=track,R=R,budget=budget,arm=arm,raw_correct=sum(r['correct'] for r in rows),raw_denominator=len(rows),raw_accuracy=float(np.mean([r['correct'] for r in rows])),catalogue_specific_accuracy=rates,equal_catalogue_accuracy=float(np.mean(list(rates.values())))))
    supplement=dict(status='POSTHOC_DESCRIPTIVE_CLARIFICATION_NO_NEW_TRAJECTORIES',DV_paths=66,DV_RR_equal_query_counts=equal_cost,DV_RR_identical_action_answer_paths=equal_history,DV_nonforced_choices=choices,DV_exact_zero_gain_choices=zero,DV_exact_zero_fraction=zero/choices,standardized_fixed_budget_accuracy=standardized)
    (HERE/'results/posthoc_clarification.json').write_text(json.dumps(supplement,indent=2)+'\n')
    # Optional compact raw archive. It contains repository-relative paths and
    # fixed metadata, so replay evidence can be distributed without 264 loose files.
    archive=HERE/'results/synthetic_raw_replay.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w') as tar:
                for p in sorted((HERE/'artifacts').rglob('*.json')):
                    payload=p.read_bytes();info=tarfile.TarInfo(str(p.relative_to(HERE)))
                    info.size=len(payload);info.mtime=0;info.mode=0o644
                    tar.addfile(info,io.BytesIO(payload))
    (HERE/'results/archive_receipt.json').write_text(json.dumps(dict(path=str(archive.relative_to(HERE)),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size,contents='all engineering and main synthetic raw JSON artifacts; repository-relative paths',raw_manifest='RECEIPT.json',freeze_unchanged=True),indent=2)+'\n')
    print(json.dumps({k:v for k,v in supplement.items() if k!='standardized_fixed_budget_accuracy'},indent=2))

if __name__=='__main__':main()
