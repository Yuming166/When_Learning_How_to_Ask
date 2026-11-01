"""Unlabelled selectors. API accepts only past canonical binary responses/IDs."""
import hashlib


def choose(group_id,history):
    scores={'A':0,'B':0}
    for pair in history:
        assert set(pair)=={'A','B'}, 'Selector accepts only unlabelled response pairs'
        for fmt in ['A','B']:
            values=pair[fmt]
            assert len(values)==2 and all(v in (None,0,1) for v in values)
            scores[fmt]+=int(None not in values and values[0]==values[1])
    if scores['A']!=scores['B']:return max(scores,key=scores.get)
    # Fixed before generation; independent of outcomes/labels, deterministic per group.
    return 'AB'[hashlib.sha256(('phase1c_tie|'+group_id).encode()).digest()[0]%2]


def explore_then_commit(group_id,prefix):return choose(group_id,prefix)


def repeat_and_compare(group_id,past):return choose(group_id,past)
