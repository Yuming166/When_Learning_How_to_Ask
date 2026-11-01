"""Post-run descriptive diagnostics only; no change to frozen decisions/selection."""
from collections import Counter,defaultdict
from design import ROOT,read_jsonl,write_json


def main():
    rows=read_jsonl(ROOT/'run/scored.jsonl');pairs=defaultdict(list)
    for r in rows:pairs[r['preference_id'],r['format']].append(r)
    summary=Counter();examples=[]
    for (pref,fmt),(a,b) in pairs.items():
        summary['pairs']+=1
        summary['agree_pairs']+=a['canonical_answer']==b['canonical_answer']
        summary['both_wrong_pairs']+=not a['correct'] and not b['correct']
        if not a['correct'] and not b['correct'] and len(examples)<4:
            examples.append({'preference_id':pref,'format':fmt,'group_id':a['group_id'],
                'claim':a['prompt'].split('Claim: ')[1].split('\n')[0],'theta':a['theta'],
                'option_flip':a['option_flip'],'digits':[a['parsed_answer'],b['parsed_answer']],
                'verified_depth':a['verified_depth']})
    scores=[]
    for g in dict.fromkeys(r['group_id'] for r in rows):
        agreements={m:sum(int((p:=pairs[f'g{next(r["group_index"] for r in rows if r["group_id"]==g):02d}_t{j:02d}',m])[0]['canonical_answer']==p[1]['canonical_answer']) for j in range(2)) for m in ['A','B']}
        scores.append({'group_id':g,'prefix_agreement_counts':agreements,'tie':agreements['A']==agreements['B']})
    write_json(ROOT/'run/descriptive.json',{'post_hoc_descriptive_only':True,'digits':dict(Counter(r['parsed_answer'] for r in rows)),
        'repeat_pairs':dict(summary),'prefix_agreement_counts':scores,'persistent_wrong_examples':examples,
        'scope':'Both-wrong pairs do not prove conditional noise dependence: heterogeneous item reliability could explain them. No new tuning or gates.'})


if __name__=='__main__':main()
