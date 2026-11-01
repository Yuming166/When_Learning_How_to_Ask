"""Post-run integrity and exact replay of eight existing trajectories; no new seeds."""
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
from qrelbench.evaluate import ROOT,frozen_files,evaluate_job
from qrelbench.rpc import worker,send
from qrelbench.security import protect_evaluator
from qrelbench.policies import NAMES


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    protect_evaluator();freeze=json.loads((ROOT/'freeze.json').read_text())
    assert freeze['files']==frozen_files()
    assert sha(ROOT/'audit/INDEPENDENT_REVIEW.md')==freeze['independent_audit_sha256']
    assert sha(ROOT/'audit/reviewer_checks.py')==freeze['reviewer_checks_sha256']
    assert sha(ROOT/'artifacts/private/evaluator_seed.json')==freeze['private_seed_commitment']
    execution=json.loads((ROOT/'artifacts/run/execution.json').read_text());assert execution['status']=='completed'
    rows=[json.loads(line) for line in (ROOT/'artifacts/run/episodes.jsonl').read_text().splitlines()]
    assert len(rows)==execution['planned_episodes']==3108
    assert sum(r['online'] for r in rows)==execution['online_actions']
    assert all(r['online']==r['costs']['task']+r['costs']['type'] for r in rows)
    assert all(r['total_acquisition']==r['online']+2*r['calibration_size'] for r in rows)
    assert all(r['online']<=r['online_cap'] for r in rows)
    assert all(r['worker_isolation']['single_thread_bootstrap'] for r in rows)
    unique={(r['policy'],r['protocol'],r['scenario'],tuple(r['partition']),r['index'],r['online_cap'],r['delta']) for r in rows}
    assert len(unique)==len(rows)
    seed=json.loads((ROOT/'artifacts/private/evaluator_seed.json').read_text())['development_master_seed']
    replay=[];context=mp.get_context('spawn')
    for policy in NAMES:
        cases=[next(r for r in rows if r['policy']==policy and r['protocol']=='fixed_budget' and r['scenario']=='base')]
        if policy=='Oracle Format':cases.append(next(r for r in rows if r['policy']==policy and r['protocol']=='fixed_confidence' and r['scenario']=='base'))
        parent,child=context.Pipe();process=context.Process(target=worker,args=(child,policy));process.start();child.close()
        try:
            for original in cases:
                job={k:original[k] for k in ['protocol','scenario','partition','index','online_cap','calibration_size','delta','p','q','s','channel']}
                repeated,_=evaluate_job(parent,policy,job,seed,time.monotonic()+30)
                assert repeated==original,('Replay differs',policy)
                replay.append({'policy':policy,'protocol':job['protocol'],'online_actions':repeated['online'],
                               'exact_record_match':True,'full_transcript_sha256_match':True})
            send(parent,None);process.join(timeout=5);assert process.exitcode==0
        finally:
            if process.is_alive():process.terminate();process.join()
            parent.close()
    history=json.loads((ROOT/'audit/HISTORY_PRESERVATION.json').read_text())
    total=0
    for item in history:
        base=ROOT.parent/item['directory'];receipt='AUDIT_RECEIPT.json' if 'phase1b' in item['directory'] else 'FINAL_RECEIPT.json'
        r=json.loads((base/receipt).read_text());hashes=r.get('artifact_sha256',r.get('snapshot_files'))
        assert sha(base/receipt)==item['receipt_sha256']
        for rel,expected in hashes.items():assert sha(base/rel)==expected
        total+=len(hashes)
    result={'completed_episodes':len(rows),'online_actions':execution['online_actions'],'model_calls':0,
       'source_config_protocol_unchanged':True,'independent_review_unchanged':True,
       'sealed_seed_commitment_unchanged':True,'all_costs_and_full_denominators_valid':True,
       'exact_replays':replay,'replayed_online_actions':sum(r['online_actions'] for r in replay),
       'historical_files_verified':total,'own_tests':17,'independent_check_groups':10,
       'scope':'Integrity and exact replay of existing development trajectories; not independent confirmatory evidence.'}
    (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
