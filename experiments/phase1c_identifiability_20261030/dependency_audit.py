"""Selected-world dependency diagnostics, without assuming statistical independence."""
import itertools
from collections import defaultdict
from design import ROOT,read_jsonl,write_json
from logic_audit import ground,closure,opposite


def main():
    rows=[]
    for w in read_jsonl(ROOT/'selected_worlds.jsonl'):
        facts,rules=ground(w);proofs,depth=closure(facts,rules)
        graph=defaultdict(set);anc={lit:{fid} for lit,fid in facts.items()}
        for body,head,rid in rules:
            if all(lit in proofs for lit in body):
                for lit in body:graph[lit].add(head)
        changed=True
        while changed:
            changed=False
            for body,head,rid in rules:
                if not all(lit in proofs for lit in body):continue
                union=set().union(*(anc.get(lit,set()) for lit in body))
                before=len(anc.get(head,set()));anc.setdefault(head,set()).update(union)
                changed |= len(anc[head])!=before
        targets=w['targets'];actual=[tuple(t['literal']) if t['theta'] else opposite(t['literal']) for t in targets]
        reach=[];overlap=[]
        for i,lit in enumerate(actual):
            seen=set();todo=list(graph[lit])
            while todo:
                item=todo.pop()
                if item in seen:continue
                seen.add(item);todo.extend(graph[item]-seen)
            for j,other in enumerate(actual):
                if i!=j and other in seen:reach.append([i,j])
        for i,j in itertools.combinations(range(6),2):
            if anc[actual[i]]&anc[actual[j]]:overlap.append([i,j])
        rows.append({'world_id':w['id'],'chosen_certificate_fact_overlap_pairs':0,
            'shared_rule_certificate_pairs':w['shared_rule_certificate_pairs'],
            'all_supported_paths_fact_ancestor_overlap_pairs':overlap,
            'directed_supported_rule_graph_reachability_pairs':reach,
            'target_depths':[t['verified_depth'] for t in targets]})
    write_json(ROOT/'selected_dependencies.json',{'worlds':rows,
        'scope':'Graph edges represent possible rule influence, not necessary dependence. One disjoint proof certificate per target does not rule out alternative shared proofs or related truths. No claim of independent target priors or iid errors.'})
    print(rows)


if __name__=='__main__':main()
