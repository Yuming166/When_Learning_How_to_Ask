"""Frozen source-based construction; no model outputs are read here."""
import json
import hashlib
import re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent
SYSTEM='You answer questions about a fictional rule world. Use only the supplied facts and forward rules. An explicitly negative fact is distinct from a missing fact. Do not use negation by failure or contraposition. Work out the result silently and return only one digit: 0 or 1.'
HEADERS={
 0:{'A':'Does the claim follow from the facts and rules? Select its truth status.',
    'B':'Which truth status is established by the facts and rules? Select the status of the claim.'},
 1:{'A':'Determine whether the claim is supported by the given facts and rules. Choose its status.',
    'B':'Choose the established status for this claim using the given facts and rules.'}}


def sha(x):
    return hashlib.sha256(x if isinstance(x,bytes) else json.dumps(x,sort_keys=True).encode()).hexdigest()


def read_jsonl(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x]


def write_json(path,obj):Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')


def parse_answer(raw):
    s=raw.strip()
    return int(s) if re.fullmatch('[01]',s) else None


def main():
    audit=json.loads((ROOT/'proofwriter_structure.json').read_text());assert audit['structural_gate']
    worlds=read_jsonl(ROOT/'selected_worlds.jsonl');assert len(worlds)==8
    requests=[];truth=[];checks=[]
    for gi,w in enumerate(worlds):
        assert len(w['targets'])==6
        # Stratified option randomization: equal correct digits in every world;
        # 2/4 flipped items in alternating worlds gives 24/24 overall order balance.
        flipped=set()
        for theta in [False,True]:
            stratum=sorted([t for t in w['targets'] if t['theta']==theta],
                           key=lambda t:sha(['option_randomization',w['id'],t['qid']]))
            flipped.update(t['qid'] for t in stratum[:1+gi%2])
        for j,t in enumerate(w['targets']):
            flip=int(t['qid'] in flipped)
            template=int(j>=2)
            evidence='Facts:\n'+'\n'.join(x['text'] for x in w['triples'].values())+'\nRules:\n'+'\n'.join(x['text'] for x in w['rules'].values())
            common=evidence+'\n\nClaim: '+t['question']+'\nExactly one status below is provable. Missing evidence alone does not prove the explicit negation.\n'
            statuses=['The explicit negation of the claim follows.','The claim follows.']
            if flip:statuses=statuses[::-1]
            options='\n'.join(str(i)+': '+s for i,s in enumerate(statuses))+'\nReturn only 0 or 1.'
            pref=f'g{gi:02d}_t{j:02d}'
            truth.append({'group_id':w['id'],'group_index':gi,'preference_id':pref,'target_index':j,
                          'theta':int(t['theta']),'correct_digit':int(t['theta'])^flip,
                          'source_qid':t['qid'],'proof':t['support'],'verified_depth':t['verified_depth']})
            for fmt in ['A','B']:
                prompt=common+HEADERS[template][fmt]+'\n'+options
                for repeat in range(2):
                    n=len(requests)
                    requests.append({'request_id':f'phase1c_{n:04d}','kind':'task','group_id':w['id'],
                       'group_index':gi,'preference_id':pref,'target_index':j,'format':fmt,
                       'template_id':template,'repeat':repeat,'option_flip':flip,'seed':2026103003+n,
                       'system':SYSTEM,'prompt':prompt,'evidence_sha256':sha(evidence.encode()),
                       'stage':'smoke' if gi==0 else 'remainder'})
            checks.append({'preference_id':pref,'same_evidence':True,'same_claim_and_options':True,
                           'only_header_differs':True,'same_prompt_within_repeated_format':True})
    assert len(requests)==192 and len({r['seed'] for r in requests})==192
    assert Counter(t['theta'] for t in truth)=={0:24,1:24}
    assert Counter(t['correct_digit'] for t in truth)=={0:24,1:24}
    assert Counter(r['option_flip'] for r in requests)=={0:96,1:96}
    data=ROOT/'data';data.mkdir(exist_ok=True)
    for name,rows in [('requests',requests),('private_truth',truth)]:
        (data/f'{name}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    write_json(data/'construction_checks.json',{'requests':192,'groups':8,'distinct_targets':48,
        'truth_labels':dict(Counter(t['theta'] for t in truth)),
        'correct_digits':dict(Counter(t['correct_digit'] for t in truth)),
        'option_flips':dict(Counter(r['option_flip'] for r in requests)),
        'checks':checks,'semantic_scope':'Two headers ask the same provability decision over identical evidence, claim and answer options; syntactic checks and logical mapping, not a human equivalence study.'})
    print('constructed',len(requests),'requests')


if __name__=='__main__':main()
