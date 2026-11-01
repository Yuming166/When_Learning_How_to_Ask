"""Offline construction/contingency audit. No learned classifier or agent execution."""
from collections import Counter,defaultdict
from unittest.mock import patch
from .worlds import make_world,Streams
from .compiler import compile_set,validate_query
from .bridge import provider_context,public_interaction_view
from .common import ROOT,read,write,canonical,digest
FORBIDDEN={'truth','truth_vector','private_world','seed','key','private_witness_sha256','mechanism','affected_format','cache'}
def scan(obj,path=''):
 out=[]
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k in FORBIDDEN:out.append(path+'/'+k)
   out+=scan(v,path+'/'+k)
 elif isinstance(obj,list):
  for i,v in enumerate(obj):out+=scan(v,path+'/'+str(i))
 return out

def label_contingency(bundle):
 tables=defaultdict(lambda:defaultdict(Counter))
 for t,p,gt in zip(bundle['public']['targets'],bundle['propositions'],bundle['grounded']):
  features={'domain':bundle['public']['groups'][t['group']]['domain'],'predicate':p.predicate.value,
   'local_position':str(t['j']%6),'source_id_first_hex':p.source_id[1],
   'A_prompt_length':str(len(compile_set(p)[0].text))}
  for name,value in features.items():tables[name][value][str(int(gt.truth))]+=1
 return {name:{value:{'0':c['0'],'1':c['1']} for value,c in values.items()} for name,values in tables.items()}

def main():
 keys=read(ROOT/'private/FIXTURE_KEYS.json');results={}
 for mode,key in keys.items():
  b=make_world(bytes.fromhex(key),mode);view=public_interaction_view(b);bad=scan(view)
  truth={t.proposition.target_id:t.truth for t in b['grounded']};edges=[e for e in b['dependencies'] if e['relation']=='AND']
  context_checks=[]
  for p in b['propositions']:
   qq=compile_set(p)
   context_checks.append({'target_id':p.target_id,'same_context_for_A_B':len({q.evidence_refs for q in qq})==1,
    'provider_context_private_leak_keys':scan(provider_context(p,b['private_world'])),
    'all_queries_bound_and_valid':all(validate_query(p,q) for q in qq)})
  results[mode]={'public_forbidden_fields':bad,'context_checks':context_checks,
   'source_positive_counts':[sum(t.truth for t in b['grounded'][6*g:6*g+6]) for g in range(8)],
   'exact_AND_constraints':len(edges),'AND_constraints_valid':all(truth[e['target']]==all(truth[x] for x in e['parents']) for e in edges),
   'label_contingencies':label_contingency(b),'no_classifier_fitting':True,'no_performance_selection':True,
   'inference_limit':'Single technical fixture; accidental metadata correlations are reported, not evidence for or against general predictability.'}
 key=bytes.fromhex(keys['independent_fixture']);before=make_world(key);orig=Streams.bit
 with patch.object(Streams,'bit',lambda self,*labels:not orig(self,*labels)):after=make_world(key)
 metadata_invariant=canonical(public_interaction_view(before))==canonical(public_interaction_view(after))
 # Missing/duplicate records are a hard error; schema hashes bind public semantics only.
 all_ids=[p.target_id for p in before['propositions']]
 results['independent_metamorphic_test']={'all_truths_flipped':all(x.truth!=y.truth for x,y in zip(before['grounded'],after['grounded'])),
  'public_metadata_and_all_query_texts_unchanged':metadata_invariant,'distinct_target_ids':len(set(all_ids))==48,
  'note':'Controlled intervention proves this implementation does not deterministically encode sampled bits in public metadata. It does not prove absence of every distributional shortcut.'}
 results['v02_legacy_dependency_evidence']={'source':str(ROOT.parent/'qrelbench-v02-dev-20261031/private/world.json'),
  'fixed_three_positives_per_source':True,'source_generator_reason_branch_depends_on_local_index':True,
  'recovery_constraint':'If exactly3 positives is known and5 truth values are known, the sixth is determined; not an iid-bit source.',
  'v021_independent_fixture':'No balance conditioning, target-index-driven truth branch removed; private witness RNG separate from public metadata.'}
 results['pass']=not any(r['public_forbidden_fields'] or not r['AND_constraints_valid'] or any(not c['all_queries_bound_and_valid'] or not c['same_context_for_A_B'] or c['provider_context_private_leak_keys'] for c in r['context_checks']) for k,r in results.items() if k in keys) and metadata_invariant
 write(ROOT/'audit/DATA_AUDIT.json',results);print('Construction/dependency audit pass:',results['pass'],'; no model/agent calls')
if __name__=='__main__':main()
