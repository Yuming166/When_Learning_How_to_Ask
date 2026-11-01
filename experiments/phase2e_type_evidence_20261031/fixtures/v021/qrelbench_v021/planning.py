"""Prepare frozen LOCAL request artifacts only. No API, model or agent execution code."""
from .surface import SURFACE_SCHEMA
from .compiler import compile_set,compile_query
from .common import digest

def request_for_target(prop):
 allowed=[compile_query(prop,m,v,style=s,phrase=p).to_dict() for m in ['A','B'] for v in [0,1] for s in [0,1] for p in [0,1]]
 return {'kind':'surface_candidate','target_id':prop.target_id,'proposition':prop.to_dict(),
  'schema':SURFACE_SCHEMA,'allowed_controlled_realizations':allowed,
  'instruction':'Choose two distinct controlled realizations per format for this exact target. Return exactly four forms covering A0,A1,B0,B1. Copy the selected text exactly. Do not write a new proposition, logical condition, answer mapping, placeholder or policy. Novel wording is rejected by this phase.',
  'contains_private_truth_or_record':False}

def plan(bundle):
 requests=[]
 for group in bundle['public']['groups']:
  targets=[bundle['propositions'][j] for j in group['targets']]
  requests.append({'request_id':'surface_'+group['id'],'kind':'surface_batch','response_schema':{'type':'array','minItems':6,'maxItems':6,'items':SURFACE_SCHEMA},'targets':[request_for_target(p) for p in targets]})
  requests.append({'request_id':'description_'+group['id'],'kind':'source_description','source_id':group['id'],'domain':group['domain'],
   'allowed_scope':group['description'],'instruction':'Propose one neutral source description. No facts, labels, rules, reliability claims or hidden source configurations. This prose will be quarantined pending independent review.'})
 return {'status':'PROPOSED_FROZEN_NOT_EXECUTED','authority':'offline planning only; no calls authorized by this artifact',
  'generation':{'intended_model':'Qwen3.6-35B-A3B','endpoint_status':'not probed this session; identity and service must be checked before separately authorized execution',
   'planned_requests':16,'maximum_attempts':16,'surface_batches':8,'description_requests':8,'targets':48,
   'temperature':.3,'top_p':.95,'thinking':False,'max_tokens_surface_batch':8192,'max_tokens_description':256,'retries':0,
   'schema_note':'Provider schema enforcement is optional; local full validation mandatory; actual serving support unverified'},
  'answering':{'current_authorized_calls':0,'proposed_future_maximum_calls':304,'fact_first_pass':192,'repeat_variant0':96,
   'direct_type':8,'metadata_only':8,'smoke_calls_included_in_fact_total':16,'intended_model':'Qwen3.5-4B',
   'prerequisites':['all8 sources full192 forms accepted','independent semantic review with zero unresolved cases','description leakage review or no descriptions','new answering authorization and source/model/runtime freeze']},
  'source_gate':'All6 targets x4 required forms pass or source rejected. No group/format gap or algorithm score gate.',
  'no_generator_truth_access':True,'requests':requests}
