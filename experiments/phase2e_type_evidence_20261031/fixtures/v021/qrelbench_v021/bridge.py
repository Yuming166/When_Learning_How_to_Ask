"""Additive schema bridge only. Does not run an agent, query a provider or grant calibration."""
from .compiler import compile_set,compile_query
from .truth import resolve,render_policy

def public_interaction_view(bundle):
 public=bundle['public'];targets=[]
 for t,p in zip(public['targets'],bundle['propositions']):
  qq=compile_set(p)
  targets.append({'j':t['j'],'id':p.target_id,'group':t['group'],'proposition':p.to_dict(),
   'queries':{m:[q.text for q in qq if q.format==m] for m in ['A','B']},
   'answer_mappings':{m:[dict(q.answer_mapping) for q in qq if q.format==m] for m in ['A','B']}})
 return {**public,'targets':targets,'calibration_size_per_stream':0,
  'rate_domain':{'status':'not_assumed_for_semantic_or_natural_tasks'},'type_accuracy':'unknown'}

def normalize_response(prop,fmt,variant,raw):
 try:return {'answer':int(compile_query(prop,fmt,variant).decode(raw)),'valid':True}
 except (ValueError,TypeError):return {'answer':None,'valid':False}

def provider_context(prop,world):
 """Privileged minimal record context; same function for A/B, never supplied to the agent."""
 record,policy=resolve(prop,world)
 required=next(r for r in prop.required_records if r.collection!='policies')
 context={'entity_id':prop.entity_id,'source_id':prop.source_id,
  'record':{name:record[name] for name in required.required_fields},
  'definitions':'Stock and reservations are nonnegative whole units. Monetary fields are US cents. Dispatch time and request age are nonnegative whole days. Every comparison threshold is inclusive when stated as at most or at least.'}
 if policy is not None:context['policy']=render_policy(prop.policy_id,policy)
 return context
