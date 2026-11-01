"""Qwen proposals are data, never an instruction or authoritative semantic object."""
from .compiler import compile_query,parse_controlled_text,validate_query,CompiledQuery
from .canonical import Proposition
from .common import digest

SURFACE_SCHEMA={
 'type':'object','additionalProperties':False,'required':['target_id','proposition_sha256','forms'],
 'properties':{
  'target_id':{'type':'string'},'proposition_sha256':{'type':'string'},
  'forms':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'object','additionalProperties':False,
   'required':['format','variant','style_id','phrase_id','text'],
   'properties':{'format':{'enum':['A','B']},'variant':{'enum':[0,1]},'style_id':{'enum':[0,1]},'phrase_id':{'enum':[0,1]},'text':{'type':'string'}}}}}}

def validate_surface(prop,payload):
 reasons=[];compiled=[]
 if not isinstance(payload,dict) or set(payload)!={'target_id','proposition_sha256','forms'}:return {'pass':False,'reasons':['schema'],'queries':[]}
 if payload['target_id']!=prop.target_id or payload['proposition_sha256']!=prop.binding_sha256:reasons.append('binding_mismatch')
 forms=payload['forms']
 if not isinstance(forms,list) or len(forms)!=4:return {'pass':False,'reasons':sorted(set(reasons+['full_required_set'])),'queries':[]}
 seen=set()
 for row in forms:
  if not isinstance(row,dict) or set(row)!={'format','variant','style_id','phrase_id','text'}:reasons.append('form_schema');continue
  try:
   # Identity/order/negation/mapping are compiled, not copied from model output.
   query=compile_query(prop,row['format'],row['variant'],style=row['style_id'],phrase=row['phrase_id'])
   if not isinstance(row['text'],str) or row['text']!=query.text:raise ValueError('Surface outside controlled grammar')
   parsed=parse_controlled_text(prop,row['format'],row['variant'],row['text']);validate_query(prop,parsed)
   key=(query.format,query.variant)
   if key in seen:reasons.append('duplicate_form')
   seen.add(key);compiled.append(query)
  except (ValueError,KeyError,TypeError):reasons.append('semantic_grammar_or_domain')
 if seen!={('A',0),('A',1),('B',0),('B',1)}:reasons.append('full_required_set')
 for fmt in ['A','B']:
  texts=[q.text for q in compiled if q.format==fmt]
  if len(texts)==2 and texts[0]==texts[1]:reasons.append('duplicate_paraphrase')
 return {'pass':not reasons,'reasons':sorted(set(reasons)),'queries':[q.to_dict() for q in compiled] if not reasons else []}

def model_fixture(prop):
 return {'target_id':prop.target_id,'proposition_sha256':prop.binding_sha256,
  'forms':[{'format':m,'variant':v,'style_id':v,'phrase_id':v,'text':compile_query(prop,m,v).text} for m in ['A','B'] for v in [0,1]]}

def validate_source(propositions,payloads):
 """All-or-nothing source acceptance; never cherry-pick successful targets."""
 if not isinstance(propositions,(list,tuple)) or len(propositions)!=6 or any(not isinstance(p,Proposition) for p in propositions) or len({p.target_id for p in propositions})!=6 or len({p.source_id for p in propositions})!=1:return {'pass':False,'reasons':['invalid_source_target_spec'],'targets':[]}
 if not isinstance(payloads,list) or len(payloads)!=len(propositions):return {'pass':False,'reasons':['source_target_coverage'],'targets':[]}
 byid={}
 for obj in payloads:
  if not isinstance(obj,dict) or not isinstance(obj.get('target_id'),str):return {'pass':False,'reasons':['source_schema'],'targets':[]}
  if obj['target_id'] in byid:return {'pass':False,'reasons':['duplicate_target'],'targets':[]}
  byid[obj['target_id']]=obj
 if set(byid)!={p.target_id for p in propositions}:return {'pass':False,'reasons':['source_target_coverage'],'targets':[]}
 checks=[validate_surface(p,byid[p.target_id]) for p in propositions]
 return {'pass':all(c['pass'] for c in checks),'reasons':sorted({r for c in checks for r in c['reasons']}),'targets':checks}

def validate_review(review,queries):
 """Machine gating for locally attested independent review. Not proof of reviewer identity."""
 if not isinstance(queries,(list,tuple)) or not queries or any(not isinstance(q,CompiledQuery) for q in queries):return False
 groups={}
 for q in queries:groups.setdefault(q.target_id,[]).append((q.format,q.variant))
 if any(len(forms)!=4 or set(forms)!={('A',0),('A',1),('B',0),('B',1)} for forms in groups.values()):return False
 if not isinstance(review,dict) or not isinstance(review.get('query_hashes'),list) or any(not isinstance(h,str) or len(h)!=64 for h in review['query_hashes']):return False
 if len(review['query_hashes'])!=len(set(review['query_hashes'])):return False
 expected={digest(q.to_dict()) for q in queries}
 if not isinstance(review,dict) or review.get('status')!='PASS' or review.get('scope')!='controlled_language' or set(review.get('query_hashes',[]))!=expected:return False
 if review.get('reviewer_role') not in ['separate_codex_session','independent_human']:return False
 return True

def description_disposition(payload):
 """Novel descriptions stay quarantined; schema validity cannot approve novel semantics."""
 if not isinstance(payload,dict) or set(payload)!={'source_id','description'} or not all(isinstance(v,str) for v in payload.values()):return {'status':'REJECT','reasons':['description_schema']}
 return {'status':'QUARANTINE','reasons':['independent_truth_and_type_leakage_review_required'],'public_export':False}
