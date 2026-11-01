"""Independent finite signed-Horn evaluator and structural benchmark audit."""
import itertools
import json
import re
import hashlib
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
VARS={"someone","something","somebody","x","y"}


def sha(x):
    return hashlib.sha256(x if isinstance(x,bytes) else json.dumps(x,sort_keys=True).encode()).hexdigest()


def parse(s):
    toks=re.findall(r'"[^"\\]*(?:\\.[^"\\]*)*"|\(|\)|->',s)
    pos=0
    def item():
        nonlocal pos
        token=toks[pos];pos+=1
        if token=='(':
            out=[]
            while toks[pos]!=')':out.append(item())
            pos+=1;return tuple(out)
        return json.loads(token) if token.startswith('"') else token
    value=item()
    assert pos==len(toks)
    # Official README: '~' in a rule antecedent is hard negation in OWA;
    # it is negation-as-failure only in the separate CWA directory.
    def owa(x):
        return tuple(owa(y) for y in x) if isinstance(x,tuple) else '-' if x=='~' else x
    return owa(value)


def opposite(lit):return (*lit[:3],'-' if lit[3]=='+' else '+')


def ground(row):
    facts={parse(p['representation']):k for k,p in row['triples'].items()}
    rules=[];constants=set()
    literals=list(facts)
    parsed=[]
    for rid,r in row['rules'].items():
        body,arrow,head=parse(r['representation']);assert arrow=='->'
        parsed.append((body,head,rid));literals+=list(body)+[head]
    for x in literals:
        assert len(x)==4 and x[3] in ['+','-']
        constants.add(x[0])
        if x[1]!='is':constants.add(x[2])
    constants-=VARS
    for body,head,rid in parsed:
        variables=sorted({v for lit in list(body)+[head] for v in lit if v in VARS})
        for values in itertools.product(sorted(constants),repeat=len(variables)):
            bind=dict(zip(variables,values))
            convert=lambda lit:tuple(bind.get(v,v) for v in lit)
            rules.append((tuple(convert(lit) for lit in body),convert(head),rid))
    return facts,rules


def closure(facts,rules):
    proofs={x:frozenset([fid]) for x,fid in facts.items()}
    depths={x:0 for x in facts}
    changed=True
    while changed:
        changed=False
        for body,head,rid in rules:
            if all(x in proofs for x in body):
                support=frozenset([rid]).union(*(proofs[x] for x in body))
                dep=1+max(depths[x] for x in body)
                old=proofs.get(head)
                if old is None or (len(support),sorted(support))<(len(old),sorted(old)):
                    proofs[head]=support;changed=True
                if head not in depths or dep<depths[head]:depths[head]=dep;changed=True
    return proofs,depths


def source_label(value):
    if value is True:return 'True'
    if value is False:return 'False'
    assert value=='Unknown';return value


def candidates(row,proofs,depths):
    result=[]
    for qid,q in row['questions'].items():
        lit=parse(q['representation'])
        if lit[3]!='+':continue  # no syntactic-negation/label shortcut in the pilot
        if (lit in proofs)==(opposite(lit) in proofs):continue
        truth=lit in proofs
        actual=lit if truth else opposite(lit)
        support=proofs[actual]
        result.append({'qid':qid,'question':q['question'],'literal':lit,'theta':truth,
                       'support':sorted(support),'fact_support':sorted(s for s in support if s.startswith('triple')),
                       'verified_depth':depths[actual]})
    # Stable source-based order, not model performance.
    return sorted(result,key=lambda q:sha([row['id'],q['qid']]))


def positive_text(lit):
    subject,verb,obj,sign=lit
    assert sign=='+' and verb in {'is','chases','eats','likes','needs','sees','visits'}
    entity=lambda x:x if x[0].isupper() else 'the '+x
    return (entity(subject)+' '+verb+' '+(obj if verb=='is' else entity(obj))+'.').capitalize() if not subject[0].isupper() else entity(subject)+' '+verb+' '+(obj if verb=='is' else entity(obj))+'.'


def extended_candidates(row,proofs,depths,rules):
    # Targets from official complete implication/proof records, not invented labels.
    ancestors={parse(v['representation']):{k} for k,v in row['triples'].items()}
    changed=True
    while changed:
        changed=False
        for body,head,rid in rules:
            if not all(lit in proofs for lit in body):continue
            union=set().union(*(ancestors.get(lit,set()) for lit in body))
            before=len(ancestors.get(head,set()));ancestors.setdefault(head,set()).update(union)
            changed |= len(ancestors[head])!=before
    out=[]
    for lit,support in proofs.items():
        if opposite(lit) in proofs:continue
        query=(*lit[:3],'+')
        out.append({'qid':'imp_'+sha(query)[:12],'question':positive_text(query),
                    'literal':query,'theta':lit[3]=='+','support':sorted(support),
                    'fact_support':sorted(x for x in support if x.startswith('triple')),
                    'all_fact_ancestors':sorted(ancestors[lit]),
                    'verified_depth':depths[lit]})
    return sorted(out,key=lambda q:sha([row['id'],q['qid']]))


def choose_six(cands):
    # One proof certificate's fact supports must be disjoint. Shared rules are logged.
    # This avoids obvious shared-fact/complement replication, not all logical dependence.
    def search(start,chosen,used,pos,neg,derived):
        if len(chosen)==6:
            return chosen if pos==neg==3 and derived>=2 else None
        if len(cands)-start<6-len(chosen):return None
        for j in range(start,len(cands)):
            c=cands[j];t=int(c['theta'])
            support=set(c.get('all_fact_ancestors',c['fact_support']))
            if (pos>=3 and t) or (neg>=3 and not t) or used & support:continue
            got=search(j+1,chosen+[c],used|support,pos+t,neg+1-t,derived+int(c['verified_depth']>0))
            if got:return got
        return None
    if sum(c['theta'] for c in cands)<3 or sum(not c['theta'] for c in cands)<3:return None
    return search(0,[],set(),0,0,0)


def audit_proofwriter():
    summary={};eligible=[]
    for split in ['train','dev']:
        stats=Counter();hist=Counter();examples=[]
        with (ROOT/f'sources/proofwriter_owa3_meta-{split}.jsonl').open() as f:
            for line in f:
                row=json.loads(line);stats['worlds']+=1
                facts,rules=ground(row);proofs,depths=closure(facts,rules)
                inconsistent=any(opposite(lit) in proofs for lit in proofs)
                stats['inconsistent_worlds']+=int(inconsistent)
                mismatch=[]
                for qid,q in row['questions'].items():
                    lit=parse(q['representation'])
                    pred='True' if lit in proofs else 'False' if opposite(lit) in proofs else 'Unknown'
                    stats['questions']+=1
                    stats['source_'+source_label(q['answer'])]+=1
                    if pred!=source_label(q['answer']):mismatch.append(qid)
                stats['label_mismatches']+=len(mismatch)
                official_proofs={parse(x['representation']) for x in row['proofDetails']}
                stats['complete_implication_mismatch_worlds']+=int(official_proofs!=set(proofs))
                stats['complete_implications']+=len(official_proofs)
                if mismatch or inconsistent or official_proofs!=set(proofs):continue
                cands=candidates(row,proofs,depths)
                hist[len(cands)]+=1
                stats['worlds_with_6_distinct_signed_binary_positive_queries']+=int(len(cands)>=6)
                stats['worlds_with_8_distinct_signed_binary_positive_queries']+=int(len(cands)>=8)
                chosen=choose_six(cands)
                if chosen:
                    stats['worlds_with_6_balanced_certificate_disjoint_targets']+=1
                # Native question lists are sparse. Separately audit the official
                # complete implication inventory as an explicitly adapted target pool.
                ext=extended_candidates(row,proofs,depths,rules)
                stats['extended_worlds_at_least_6']+=int(len(ext)>=6)
                stats['extended_worlds_at_least_8']+=int(len(ext)>=8)
                chosen=choose_six(ext)
                if chosen:
                    stats['extended_worlds_balanced_certificate_disjoint_6']+=1
                    if split=='train':
                        # Public target positions must not encode alternating labels.
                        chosen=sorted(chosen,key=lambda q:sha(['target_order',row['id'],q['literal']]))
                        shared_rules=sum(bool(set(a['support']) & set(b['support'])) for a,b in itertools.combinations(chosen,2))
                        eligible.append({'id':row['id'],'theory':row['theory'],'triples':row['triples'],'rules':row['rules'],
                                         'targets':chosen,'shared_rule_certificate_pairs':shared_rules,
                                         'fact_support_disjoint':True,'target_source':'official proofDetails complete implications, normalized to positive queries'})
        summary[split]={**dict(stats),'positive_binary_target_count_histogram':dict(sorted(hist.items()))}
    selected=sorted(eligible,key=lambda x:sha(['phase1c_frozen_worlds',x['id']]))[:8]
    gate=len(selected)==8 and all(summary[s]['label_mismatches']==summary[s]['complete_implication_mismatch_worlds']==0 for s in summary)
    (ROOT/'proofwriter_structure.json').write_text(json.dumps({'summary':summary,'structural_gate':gate,
        'selected_world_ids':[x['id'] for x in selected],
        'scope':'OWA depth-3 only; no Unknown-to-False merge. Fixed unknown signs need not have independent priors. Disjoint chosen-certificate facts are not a statistical-independence proof.'},indent=2)+'\n')
    (ROOT/'selected_worlds.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in selected))
    print('ProofWriter',json.dumps(summary),'gate',gate,flush=True)


def audit_contractnli():
    summary={};alllabels=None
    for split in ['train','dev','test']:
        f=ROOT/f'sources/contract_{split}.json'
        if not f.exists():return
        data=json.loads(f.read_text());docs=data['documents'];labels=data['labels']
        if alllabels is None:alllabels=labels
        assert labels==alllabels and len(labels)==17
        counts=Counter();binaryhist=Counter();span_overlap=Counter();length=[]
        for doc in docs:
            annotations=doc['annotation_sets'][0]['annotations'];assert len(annotations)==17
            determinate={k:v for k,v in annotations.items() if v['choice'] in ['Entailment','Contradiction']}
            binaryhist[len(determinate)]+=1;counts.update(v['choice'] for v in annotations.values())
            length.append(len(doc['text'].split()))
            for a,b in itertools.combinations(determinate.values(),2):
                span_overlap['pairs']+=1
                span_overlap['shared_evidence_span']+=int(bool(set(a['spans'])&set(b['spans'])))
            assert all(0<=i<len(doc['spans']) for a in annotations.values() for i in a['spans'])
            assert all(0<=a<b<=len(doc['text']) for a,b in doc['spans'])
        summary[split]={'documents':len(docs),'labels':dict(counts),'determinate_binary_count_histogram':dict(sorted(binaryhist.items())),
                        'documents_with_at_least_6':sum(v for k,v in binaryhist.items() if k>=6),
                        'documents_with_at_least_8':sum(v for k,v in binaryhist.items() if k>=8),
                        'word_count_min_median_max':[min(length),sorted(length)[len(length)//2],max(length)],
                        'evidence_overlap':dict(span_overlap)}
    (ROOT/'contractnli_structure.json').write_text(json.dumps({'summary':summary,'labels':alllabels,
        'scope':'Gold human labels/evidence, not an executable logical proof system. NotMentioned excluded and separately counted, never False. Shared evidence is not a complete logical-dependency test.'},indent=2)+'\n')
    print('ContractNLI',json.dumps(summary),flush=True)


if __name__=='__main__':
    audit_proofwriter();audit_contractnli()
