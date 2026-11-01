"""Frozen-source checks and exact existing-trajectory replay, never new worlds."""
import json
import math
import multiprocessing as mp
import time
from collections import Counter,defaultdict
import numpy as np
from .bootstrap import ROOT,V1,P2A,P2B
from .runner import digest,frozen_files,jobs,evaluate_job
from .policy import POLICIES,worker,compact
from phase2b.log_glr import log_glr
from .analyze import load,identity
from phase2b.integrity import history as previous_history
from qrelbench.rpc import send
from qrelbench.security import protect_evaluator


def history():
    result=previous_history();receipt=json.loads((P2B/'FINAL_RECEIPT.json').read_text())
    for rel,h in receipt['artifact_sha256'].items():
        if digest(P2B/rel)!=h:raise RuntimeError('Historical Phase2b artifact changed: '+rel)
    return result+[{'experiment':P2B.name,'files_verified':len(receipt['artifact_sha256']),'receipt_sha256':digest(P2B/'FINAL_RECEIPT.json')}]


def strip_timing(value):
    if isinstance(value,dict):return {k:strip_timing(v) for k,v in value.items() if not k.endswith('seconds') and k!='timings_seconds'}
    if isinstance(value,list):return [strip_timing(v) for v in value]
    return value


def main():
    validation_started=time.monotonic();validation_cpu=time.process_time()
    protect_evaluator();freeze=json.loads((ROOT/'freeze.json').read_text())
    if freeze['files']!=frozen_files():raise RuntimeError('Frozen code/config/protocol changed')
    for rel,h in freeze['audits'].items():
        if digest(ROOT/rel)!=h:raise RuntimeError('Frozen proof/audit changed')
    for label,base in [('v1',V1),('phase2a',P2A),('phase2b',P2B)]:
        for rel,h in freeze['dependencies'][label].items():
            if digest(base/rel)!=h:raise RuntimeError('Frozen dependency changed')
    if digest(ROOT.parents[1]/'Theory_Note.md')!=freeze['theory_sha256']:raise RuntimeError('Historical theory changed')
    seedfile=ROOT/'artifacts/private/seed.json'
    if digest(seedfile)!=freeze['private_seed_commitment']:raise RuntimeError('Private seed commitment changed')
    historical=history();run=ROOT/'artifacts/run';receipt=json.loads((run/'execution.json').read_text())
    if receipt['status']!='completed':raise RuntimeError('Execution incomplete; preserve partial/missing records')
    rows=load(run/'trajectories.jsonl');snaps=load(run/'snapshots.jsonl');private=load(run/'private/reproduction.jsonl')
    cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
    expected={(p,j['index']) for j in plan for p in POLICIES}
    if Counter(identity(r) for r in rows)!=Counter(expected):raise RuntimeError('Missing/duplicate identities')
    if len(rows)!=receipt['finished_trajectories'] or len(rows)!=receipt['planned_trajectories'] or len(private)!=len(rows):raise RuntimeError('Incorrect denominator')
    costs={k:sum(r['costs'][k] for r in rows) for k in ['task','type','offline']}
    if costs!=receipt['costs_including_partial']:raise RuntimeError('Cost accounting differs')
    priv={(r['policy'],r['job']['index']):r for r in private};bykey={identity(r):r for r in rows};ss=defaultdict(list);blind=0
    for s in snaps:ss[identity(s)].append(s)
    for k,r in bykey.items():
        p=priv[k];counts=np.asarray(r['counts']);cal=r['calibration'];type_counts=sum(map(len,r['type_answers']))
        if int(counts.sum())!=r['costs']['task'] or type_counts!=r['costs']['type'] or r['online']!=r['costs']['task']+r['costs']['type'] or r['total_acquisition']!=sum(r['costs'].values()):raise RuntimeError('Action cost/count mismatch')
        if len(cal['high'])!=r['M'] or len(cal['low'])!=r['M'] or r['costs']['offline']!=2*r['M']:raise RuntimeError('Offline cost/count mismatch')
        if r['censored']==r['complete'] or (r['censored'] and r['online']!=r['online_cap']):raise RuntimeError('Censoring mismatch')
        if r['online']%r['check_every']!=0 and r['online']!=r['online_cap']:raise RuntimeError('Stopping check schedule mismatch')
        if r['exact']!=(r['fit']['theta']==p['truth']) or r['correct_facts']!=sum(a==b for a,b in zip(r['fit']['theta'],p['truth'])):raise RuntimeError('Truth scoring mismatch')
        if r['complete']!=(r['fit']['gap']-r['fit']['beta']>r['numeric_margin']):raise RuntimeError('Strict numeric stop mismatch')
        if p['full_trace_sha256']!=r['transcript_sha256']:raise RuntimeError('Full trace hash mismatch')
        if not r['isolation']['single_thread_bootstrap']:raise RuntimeError('Worker unconfined')
        if r['policy'] in ['Aligned Tracking','D-RRC']:
            diagnostic=r['tracking_diagnostics'];L=2*sum(r['partition']);E=L+len(r['partition']);t=r['online']
            epoch=math.isqrt(t//L);offset=min(L,t-L*epoch*epoch)
            expected_forced=np.array([epoch+int(e<offset) for e in range(L)])
            if not np.array_equal(np.asarray(diagnostic['forced_task_counts']).reshape(-1),expected_forced) or r['forced_tasks']!=int(expected_forced.sum()):raise RuntimeError('Forced-prefix contract differs')
            actual=np.asarray(diagnostic['actual_minus_target']);bound=1+r['forced_tasks']
            if actual.max()>bound+1e-6 or actual.min()<-(E-1)*bound-1e-6 or abs(float(actual.sum()))>1e-6:raise RuntimeError('Tracking discrepancy bound differs')
            if t-diagnostic['last_update']>math.sqrt(t+1)+1:raise RuntimeError('Update-age bound differs')
            for estimate in r['estimation_history']:
                if r['policy']=='Aligned Tracking':
                    if estimate['solver_relative_gap']>estimate['effective_numerical_relative_gap'] or estimate['minimum_information']<1-1e-7:raise RuntimeError('Allocation numerical contract differs')
                elif estimate['paid_type_target_mass']!=0 or any(estimate['weights'][L:]):raise RuntimeError('D-RRC type allocation differs')
        groups=[];start=0
        for size in r['partition']:groups.append(list(range(start,start+size)));start+=size
        oracle=p['types'] if r['policy']=='Oracle Format' else None
        # Pure likelihood recomputation uses true types only for declared Oracle.
        fit=compact(log_glr(counts,groups,cal,r['type_answers'],[r['s']]*len(groups),r['R'],r['eta'],oracle))
        if strip_timing(fit)!=strip_timing(r['fit']):raise RuntimeError('Final GLR recomputation differs')
        blind+=1
        if not ss[k] or ss[k][-1]['online']!=r['online']:raise RuntimeError('Missing terminal snapshot')
        prior=np.zeros_like(counts)
        for snapshot in ss[k]:
            raw=np.asarray(snapshot['counts'])
            if np.any(raw<prior) or np.any(raw>counts):raise RuntimeError('Snapshot count prefix mismatch')
            prior=raw
            if snapshot['online']!=snapshot['costs']['task']+snapshot['costs']['type'] or snapshot['exact']!=(snapshot['fit']['theta']==p['truth']):raise RuntimeError('Snapshot cost/truth mismatch')
    for j in plan:
        paired=[bykey[(p,j['index'])] for p in POLICIES]
        if len({r['episode_id'] for r in paired})!=1 or any(r['calibration']!=paired[0]['calibration'] for r in paired):raise RuntimeError('Unpaired problem/reference data')
    # One highest-R existing trajectory per policy, plus one censored existing
    # path if the first five do not include one. All data already exist.
    selected=[next(r for r in rows if r['policy']==p and r['R']==max(cfg['Rs'])) for p in POLICIES]
    if not any(r['censored'] for r in selected):
        censored=next((r for r in rows if r['censored']),None)
        if censored:selected.append(censored)
    seed=json.loads(seedfile.read_text())['development_seed'];replay_costs={'task':0,'type':0,'offline':0};replays=[]
    replay_started=time.monotonic();replay_worker_cpu=0.
    for original in selected:
        parent,child=mp.get_context('spawn').Pipe();process=mp.get_context('spawn').Process(target=worker,args=(child,original['policy']));process.start();child.close()
        try:
            new,_,snapshots=evaluate_job(parent,original['policy'],priv[identity(original)]['job'],seed,time.monotonic()+180,replay_costs)
            if strip_timing(original)!=strip_timing(new) or strip_timing(ss[identity(original)])!=strip_timing(snapshots):raise RuntimeError('Exact existing-trajectory replay differs')
            replay_worker_cpu+=new['trajectory_cpu_seconds']
            send(parent,None);process.join(timeout=5)
            if process.is_alive() or process.exitcode!=0:raise RuntimeError('Replay worker exit')
            replays.append({'policy':original['policy'],'R':original['R'],'online':original['online'],'censored':original['censored'],'full_record_match_excluding_timing':True,'transcript_hash_match':True})
        finally:
            if process.is_alive():process.terminate();process.join(timeout=5)
            parent.close()
    result={'source_config_protocol_unchanged':True,'proof_audit_hashes_unchanged':True,'seed_commitment_unchanged':True,
        'trajectories':len(rows),'independent_worlds':len(plan),'all_expected_identities_present':True,
        'costs':costs,'all_cost_censoring_pairing_checks_pass':True,'final_GLRS_recomputed':blind,
        'historical':historical,'historical_files_verified':sum(r['files_verified'] for r in historical),
        'exact_existing_replays':replays,'replay_costs':replay_costs,'model_calls':0,'new_confirmation_worlds':0,
        'existing_replay_wall_seconds':time.monotonic()-replay_started,'existing_replay_worker_cpu_seconds':replay_worker_cpu,
        'validation_wall_seconds':time.monotonic()-validation_started,'validation_evaluator_cpu_seconds':time.process_time()-validation_cpu,
        'scope':'data integrity and existing-world replay, not new scientific replication'}
    (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
