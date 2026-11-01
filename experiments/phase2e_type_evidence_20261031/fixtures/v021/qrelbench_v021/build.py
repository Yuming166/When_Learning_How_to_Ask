"""Build once, or replay exactly from private keys. Offline fixtures, not a benchmark pilot."""
import argparse,secrets
from collections import Counter
from .common import ROOT,read,write,digest,canonical
from .worlds import make_world
from .compiler import compile_set,compile_query,validate_query
from .truth import evaluate,evaluate_sql
from .planning import plan

def bundle_artifacts(key,mode):
 b=make_world(key,mode);public=b['public'];targets=[];all_queries=[]
 for item,prop in zip(public['targets'],b['propositions']):
  queries=compile_set(prop)
  for q in queries:validate_query(prop,q)
  item={**item,'queries':[q.to_dict() for q in queries]};targets.append(item);all_queries.extend(queries)
 public={**public,'targets':targets}
 private={'world':b['private_world'],'grounded_targets':[t.private_dict() for t in b['grounded']],
  'dependencies':b['dependencies'],'mode':mode,'truth_prior':b['truth_prior']}
 bits=[t.truth for t in b['grounded']]
 stats={'mode':mode,'sources':8,'targets':48,'queries':192,'positive_labels':sum(bits),'negative_labels':48-sum(bits),
  'source_positive_counts':[sum(bits[g*6:g*6+6]) for g in range(8)],
  'label_balance_is_acceptance_gate':False,'python_sqlite_agreement':sum(evaluate(p,b['private_world'])==evaluate_sql(p,b['private_world']) for p in b['propositions']),
  'B_correct_option_counts':dict(Counter(q.encode(bits[j]) for j in range(48) for q in all_queries[j*4:j*4+4] if q.format=='B')),
  'A_correct_digit_counts':dict(Counter(q.encode(bits[j]) for j in range(48) for q in all_queries[j*4:j*4+4] if q.format=='A')),
  'predicate_counts':dict(Counter(p.predicate.value for p in b['propositions'])),'equality_constraint_per_source':None,
  'logical_AND_edges':sum(d['relation']=='AND' for d in b['dependencies']),
  'semantic_structures':['direct_boolean_verification','complementary_exclusive_selection'],
  'NL_grammatical_families':2,'variants_per_format':2,'natural_diversity_measured':False}
 return b,public,private,stats,all_queries

def artifacts(keys):
 result={};bundles={};all_queries=[]
 for mode,keyhex in keys.items():
  b,pub,priv,stats,qq=bundle_artifacts(bytes.fromhex(keyhex),mode);bundles[mode]=b;all_queries+=list(qq)
  result[f'public/{mode}.json']=pub;result[f'private/{mode}.json']=priv;result[f'audit/{mode}_stats.json']=stats
 b=bundles['independent_fixture'];result['audit/PROPOSED_REQUEST_PLAN.json']=plan(b)
 representative={}
 for mode,b in bundles.items():
  for p in b['propositions']:representative.setdefault(p.predicate.value,p)
 result['audit/REVIEW_PACKET.json']={'scope':'controlled-language grammar and canonical binding; no labels or private record values',
  'reviewer_limit':'same-family separate Codex session, not human validation or cross-family generalization',
  'all_fixture_query_hashes':[digest(q.to_dict()) for q in all_queries],
  'proposition_classes':[{'proposition':p.to_dict(),
   'allowed_queries':[compile_query(p,m,v,style=s,phrase=ph).to_dict() for m in ['A','B'] for v in [0,1] for s in [0,1] for ph in [0,1]]} for p in representative.values()],
  'review_questions':['Does every rendering have precisely the canonical ground-entity scope?','Are inclusive thresholds, integer stock equivalence and classical NOT correct?',
    'Are A and B equivalent under the same required source records?','Does B add private information or change the proposition?',
    'Could unknown truth/type, validity of whole policy, textual mention or compatibility be substituted?','Which semantic/domain and diversity limitations remain?']}
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--verify-replay',action='store_true');args=ap.parse_args();path=ROOT/'private/FIXTURE_KEYS.json'
 if args.verify_replay:
  keys=read(path);products=artifacts(keys);bad=[p for p,obj in products.items() if canonical(read(ROOT/p))!=canonical(obj)]
  if bad:raise RuntimeError('Deterministic replay mismatch: '+str(bad))
  print('PASS: exact replay of',len(products),'offline artifacts; no model calls');return
 if path.exists():raise RuntimeError('Offline fixtures already exist; use --verify-replay')
 keys={mode:secrets.token_hex(32) for mode in ['independent_fixture','dependent_mechanism_fixture']}
 products=artifacts(keys);write(path,keys)
 for name,obj in products.items():write(ROOT/name,obj)
 write(ROOT/'public/STATUS.json',{'status':'OFFLINE_COMPILER_FIXTURES_ONLY','Qwen_generated_accepted_sources':0,
  'Qwen_calls':0,'4B_calls':0,'agent_runs':0,'held_out_or_confirmation':False,
  'researcher_only_material':'audit and private directories must not be supplied to an agent'})
 print('Built offline fixtures:',len(products),'artifacts;48 independent and48 dependent targets; no model calls')
if __name__=='__main__':main()
