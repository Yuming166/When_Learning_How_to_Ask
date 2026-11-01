"""History preservation and trusted evaluator replay of EXISTING trajectories."""
import collections
import json
import multiprocessing as mp
import time
from pathlib import Path
import numpy as np
from .runner import ROOT,digest,frozen_files,jobs,evaluate_job
from .bootstrap import V1
from .policy import POLICIES,worker
from .analyze import load_jsonl
from qrelbench.security import protect_evaluator
from qrelbench.rpc import send


def history():
    result=[]
    for folder,receipt,key in [('phase01_20261030','FINAL_RECEIPT.json','artifact_sha256'),
            ('phase1b_userbench_audit_20261030','AUDIT_RECEIPT.json','snapshot_files'),
            ('phase1c_identifiability_20261030','FINAL_RECEIPT.json','artifact_sha256'),
            ('qrelbench_v01_20261030','FINAL_RECEIPT.json','artifact_sha256')]:
        base=ROOT.parent/folder;doc=json.loads((base/receipt).read_text())
        for rel,h in doc[key].items():
            if digest(base/rel)!=h:raise RuntimeError('Historical artifact changed: '+folder+'/'+rel)
        result.append({'experiment':folder,'files_verified':len(doc[key]),'receipt_sha256':digest(base/receipt)})
    return result


def key(job,policy):
    return (policy,job['protocol'],job['scenario'],tuple(job['partition']),job['alpha'],job['R'],job['p'],job['q'],job['index'])


def strip_timing(value):
    if isinstance(value,dict):return {k:strip_timing(v) for k,v in value.items() if not k.endswith('seconds') and k!='timings_seconds'}
    if isinstance(value,list):return [strip_timing(v) for v in value]
    return value


def main():
    protect_evaluator();freeze=json.loads((ROOT/'freeze.json').read_text())
    if freeze['files']!=frozen_files():raise RuntimeError('Source/config freeze changed')
    for rel,h in freeze['audits'].items():
        if digest(ROOT/rel)!=h:raise RuntimeError('Audit changed')
    for rel,h in freeze['v1_source'].items():
        if digest(V1/rel)!=h:raise RuntimeError('V1 dependency changed')
    if digest(ROOT.parents[1]/'Theory_Note.md')!=freeze['theory_note_sha256']:raise RuntimeError('Theory changed')
    seedfile=ROOT/'artifacts/private/seed.json'
    if digest(seedfile)!=freeze['private_seed_commitment']:raise RuntimeError('Seed commitment changed')
    historical=history();plan=jobs(json.loads((ROOT/'config.json').read_text()));run=ROOT/'artifacts/run'
    execution=json.loads((run/'execution.json').read_text())
    if execution['status']!='completed':raise RuntimeError('Execution incomplete; retain partial failure')
    rows=load_jsonl(run/'trajectories.jsonl');snaps=load_jsonl(run/'snapshots.jsonl');private=load_jsonl(run/'private/reproduction.jsonl')
    expected={key(j,p) for j in plan for p in POLICIES}
    if collections.Counter(key(r,r['policy']) for r in rows)!=collections.Counter(expected):raise RuntimeError('Missing/duplicate trajectories')
    if len(private)!=len(rows):raise RuntimeError('Missing private reproduction record')
    if len(rows)!=execution['planned_trajectories'] or len(rows)!=execution['finished_trajectories']:raise RuntimeError('Receipt denominator mismatch')
    costs={k:sum(r['costs'][k] for r in rows) for k in ['task','type','offline']}
    if costs!=execution['costs_including_partial']:raise RuntimeError('Receipt costs differ')
    bykey={key(r,r['policy']):r for r in rows};privkey={key(r['job'],r['policy']):r for r in private}
    sg=collections.defaultdict(list)
    for s in snaps:sg[key(s,s['policy'])].append(s)
    for k,r in bykey.items():
        priv=privkey[k];counts=np.asarray(priv['counts'])
        if int(counts.sum())!=r['costs']['task'] or sum(map(len,priv['type_answers']))!=r['costs']['type']:raise RuntimeError('Observed action costs differ')
        if r['online']!=r['costs']['task']+r['costs']['type'] or r['costs']['offline']!=2*r['M'] or r['total_acquisition']!=sum(r['costs'].values()):raise RuntimeError('Acquisition accounting')
        # Score integrity against the stored deterministic-evaluator truth;
        # full selected-trajectory replay below regenerates catalog truth.
        if len(priv['truth'])!=len(priv['records']):raise RuntimeError('Missing truth facts')
        if r['exact']!=(r['fit']['theta']==priv['truth']) or r['correct_facts']!=sum(a==b for a,b in zip(r['fit']['theta'],priv['truth'])):raise RuntimeError('Truth score differs')
        if priv['complete_trace_sha256']!=r['transcript_sha256']:raise RuntimeError('Private transcript hash differs')
        if r['protocol']=='fixed_budget':
            if sorted(s['online'] for s in sg[k])!=r['snapshot_budgets'] or not r['complete']:raise RuntimeError('Missing budget endpoint')
        elif (not r['complete'] and r['online']!=r['online_cap']) or r['censored']==r['complete']:raise RuntimeError('Censoring semantics')
        if r['protocol']=='fixed_confidence' and r['complete']:
            if not r['fit']['gap']-r['fit']['beta']>1e-8*(1+r['online']+2*r['M']):raise RuntimeError('Stopping margin differs')
        if not r['isolation']['single_thread_bootstrap']:raise RuntimeError('Worker isolation absent')
        for s in sg[k]:
            if s['exact']!=(s['theta']==priv['truth']) or s['total_acquisition']!=sum(s['costs'].values()):raise RuntimeError('Snapshot truth/cost mismatch')
    # Exact replays use existing sealed development episodes; no new observations
    # or confirmatory profiles are created. Exclude timing-only fields.
    selected=[next(r for r in rows if r['policy']==p and r['protocol']=='fixed_budget') for p in POLICIES]
    for p in ['Oracle Format','Information Tracking']:
        rr=[r for r in rows if r['policy']==p and r['protocol']=='fixed_confidence' and r['scenario']=='primary_glr' and r['complete']]
        if rr:selected.append(max(rr,key=lambda r:r['R']))
    seed=json.loads(seedfile.read_text())['development_seed'];replays=[];replay_cost={'task':0,'type':0,'offline':0}
    for original in selected:
        parent,child=mp.get_context('spawn').Pipe();process=mp.get_context('spawn').Process(target=worker,args=(child,original['policy']));process.start();child.close()
        job=privkey[key(original,original['policy'])]['job']
        try:
            new,_,new_snaps=evaluate_job(parent,original['policy'],job,seed,time.monotonic()+90,replay_cost)
            if strip_timing(original)!=strip_timing(new):raise RuntimeError('Exact trajectory replay differs')
            if strip_timing(sg[key(original,original['policy'])])!=strip_timing(new_snaps):raise RuntimeError('Exact snapshot replay differs')
            send(parent,None);process.join(timeout=5)
            if process.is_alive() or process.exitcode!=0:raise RuntimeError('Replay worker exit')
            replays.append({'policy':original['policy'],'protocol':original['protocol'],'online':new['online'],'exact_record_match_excluding_timing':True,'transcript_sha256_match':True})
        finally:
            if process.is_alive():process.terminate();process.join(timeout=5)
            parent.close()
    result={'source_config_protocol_unchanged':True,'audit_hashes_unchanged':True,'sealed_seed_unchanged':True,
        'historical':historical,'historical_files_verified':sum(h['files_verified'] for h in historical),
        'all_planned_trajectories_accounted_for':True,'trajectories':len(rows),'fixed_budget_snapshots':sum(s['protocol']=='fixed_budget' for s in snaps),
        'costs':costs,'all_cost_denominators_valid':True,'exact_replays':replays,'replay_costs':replay_cost,
        'model_calls':0,'confirmation_episodes':0,'scope':'integrity and exact replay only, not independent scientific confirmation'}
    (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
