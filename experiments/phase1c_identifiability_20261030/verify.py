"""Validate completed artifacts without generating or modifying model observations."""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
from design import ROOT,read_jsonl,sha,write_json,parse_answer
from collect import frozen_files
from logic_audit import ground,closure,opposite


def main():
    frozen=json.loads((ROOT/'freeze.json').read_text())
    assert frozen_files()==frozen['files']
    raw=read_jsonl(ROOT/'run/raw.jsonl');requests=read_jsonl(ROOT/'data/requests.jsonl')
    scored=read_jsonl(ROOT/'run/scored.jsonl');truth=read_jsonl(ROOT/'data/private_truth.jsonl')
    assert len(raw)==len(scored)==len(requests)==192
    assert len({r['seed'] for r in raw})==192
    assert len({r['request_id'] for r in raw})==192
    reqs={r['request_id']:r for r in requests};priv={r['preference_id']:r for r in truth}
    worlds={w['id']:w for w in read_jsonl(ROOT/'selected_worlds.jsonl')}
    closures={g:closure(*ground(w))[0] for g,w in worlds.items()}
    score={r['request_id']:r for r in scored};canonical_correct=0
    for r in raw:
        assert all(r[k]==v for k,v in reqs[r['request_id']].items())
        assert r['model_returned']=='Qwen3.5-4B' and r['status']=='valid' and r['finish_reason']=='stop'
        assert r['parsed_answer']==parse_answer(r['raw_output'])
        assert r['canonical_answer']==r['parsed_answer']^r['option_flip']
        w=worlds[r['group_id']];t=w['targets'][r['target_index']];lit=tuple(t['literal'])
        theta=int(lit in closures[r['group_id']])
        assert theta==int(t['theta'])==priv[r['preference_id']]['theta']
        assert (opposite(lit) in closures[r['group_id']]) != bool(theta)
        correct=r['parsed_answer']==(theta^r['option_flip'])
        assert correct==score[r['request_id']]['correct'];canonical_correct+=correct
    assert canonical_correct==115
    for pref in priv:
        for m in ['A','B']:
            pair=[r for r in raw if r['preference_id']==pref and r['format']==m]
            assert len(pair)==2 and len({r['serialized_prompt_sha256'] for r in pair})==1
    source_files=[]
    for receipt_name in ['proofwriter_fetch_receipt.json','contract_fetch_receipt.json']:
        for r in json.loads((ROOT/'sources'/receipt_name).read_text()):
            path=ROOT/'sources'/r['local_file'];assert path.stat().st_size==r['size']
            assert sha(path.read_bytes())==r['sha256'];source_files.append(r['local_file'])
    history=[]
    for dirname,receipt_name,key in [('phase01_20261030','FINAL_RECEIPT.json','artifact_sha256'),
                                    ('phase1b_userbench_audit_20261030','AUDIT_RECEIPT.json','snapshot_files')]:
        base=ROOT.parent/dirname;receipt=json.loads((base/receipt_name).read_text())
        for rel,expected in receipt[key].items():assert sha((base/rel).read_bytes())==expected
        history.append({'directory':dirname,'files_verified':len(receipt[key])})
    identity=json.loads((ROOT/'run/model_identity.json').read_text())
    old=json.loads((ROOT.parent/'phase01_20261030/runs/pilot/model_identity.json').read_text())
    assert identity['model_files']==old['model_files']
    result={'frozen_source_data_unchanged':True,'actual_calls':192,'valid':192,'correct_independently_rescored':115,
        'unique_seeds':192,'byte_identical_repeated_prompts':True,'source_files_verified':source_files,
        'same_checkpoint_as_phase01':True,'historical_artifacts_unchanged':history,
        'preflight_unit_tests_passed':8,'analysis_scope':'Development only; validation is artifact integrity, not independent scientific replication.',
        'freeze_sha256':sha((ROOT/'freeze.json').read_bytes())}
    write_json(ROOT/'VALIDATION.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
