"""Typed compiler plus exact controlled-language parse-back. No LLM-owned placeholders."""
from dataclasses import dataclass,asdict
from .canonical import Proposition,Predicate
from .common import digest

PHRASES={
 Predicate.AVAILABLE:(lambda p:f'item {p.entity_id} has more than zero unreserved stock units',lambda p:f'after subtracting reserved units from stock units, item {p.entity_id} has at least one unit remaining'),
 Predicate.PRICE:(lambda p:f'the offered price of item {p.entity_id} is at most {p.threshold} US cents',lambda p:f'item {p.entity_id} has an offered price no greater than {p.threshold} US cents'),
 Predicate.SHIPPING:(lambda p:f'the shipping fee for item {p.entity_id} is zero US cents',lambda p:f'item {p.entity_id} has a shipping fee equal to zero US cents'),
 Predicate.DISPATCH:(lambda p:f'item {p.entity_id} has a dispatch time of at most {p.threshold} days',lambda p:f'the dispatch time for item {p.entity_id} is no greater than {p.threshold} days'),
 Predicate.FULFILLMENT:(lambda p:f'item {p.entity_id} has more than zero unreserved stock units AND a dispatch time of at most {p.threshold} days',lambda p:f'item {p.entity_id} has at least one unit remaining after subtracting reservations AND has a recorded dispatch time of no more than {p.threshold} days'),
 Predicate.ELIGIBLE:(lambda p:f'request {p.entity_id} is eligible under policy {p.policy_id}',lambda p:f'under policy {p.policy_id}, request {p.entity_id} satisfies the eligibility requirements')}
A_START=('Is the following proposition true for the specified source records?','Determine whether the following proposition holds for the specified source records.')
B_START=('Which one of these two mutually exclusive statements is true for the specified source records?','Select the true statement from the following complementary alternatives for the specified source records.')
A_END='Reply with exactly 1 if the proposition is true, or exactly 0 if it is false.'
B_END='Reply with exactly the number of the true option: 0 or 1.'

@dataclass(frozen=True)
class Expression:
 proposition_sha256:str
 negated:bool=False
 def __post_init__(self):
  if type(self.negated) is not bool or not isinstance(self.proposition_sha256,str) or len(self.proposition_sha256)!=64:raise ValueError('Typed expression binding')
 def value(self,truth):
  if type(truth) is not bool:raise ValueError('Boolean valuation required')
  return not truth if self.negated else truth

@dataclass(frozen=True)
class CompiledQuery:
 target_id:str
 proposition_sha256:str
 format:str
 variant:int
 style:int
 phrase:int
 text:str
 answer_mapping:tuple[tuple[str,bool],...]
 alternatives:tuple[Expression,...]
 evidence_refs:tuple[str,...]
 def encode(self,truth):
  if type(truth) is not bool:raise ValueError('Boolean valuation required')
  return next(token for token,value in self.answer_mapping if value==truth)
 def decode(self,token):
  if type(token) is not str or token not in ['0','1']:raise ValueError('Single digit only')
  return dict(self.answer_mapping)[token]
 def to_dict(self):
  obj=asdict(self);obj['answer_mapping']={k:v for k,v in self.answer_mapping};return obj

def compile_query(prop,fmt,variant,*,style=None,phrase=None):
 if not isinstance(prop,Proposition):raise ValueError('Canonical typed proposition required')
 if fmt not in ['A','B'] or type(variant) is not int or variant not in [0,1]:raise ValueError('Format/variant domain')
 style=variant if style is None else style;phrase=variant if phrase is None else phrase
 if type(style) is not int or style not in [0,1] or type(phrase) is not int or phrase not in [0,1]:raise ValueError('Controlled realization IDs only')
 statement=PHRASES[prop.predicate][phrase](prop);binding=prop.binding_sha256
 refs=tuple(f'{r.source_id}/{r.collection}/{r.record_id}' for r in prop.required_records)
 if fmt=='A':
  text=A_START[style]+'\n'+statement+'.\n'+A_END;mapping=(('0',False),('1',True));options=()
 else:
  # Order depends on a PUBLIC target identifier, never truth. The second variant reverses it.
  first_positive=(int(digest(prop.target_id),16)%2)^variant==0
  positive=statement+'.';negative='It is NOT the case that '+statement+'.'
  opt_text=(positive,negative) if first_positive else (negative,positive)
  options=(Expression(binding,not first_positive),Expression(binding,first_positive))
  mapping=(('0',first_positive),('1',not first_positive))
  text=B_START[style]+f'\n0. {opt_text[0]}\n1. {opt_text[1]}\n'+B_END
 return CompiledQuery(prop.target_id,binding,fmt,variant,style,phrase,text,mapping,options,refs)

def parse_controlled_text(prop,fmt,variant,text):
 """Partial, exact grammar: reject unsupported prose rather than infer its semantics."""
 matches=[]
 for style in [0,1]:
  for phrase in [0,1]:
   q=compile_query(prop,fmt,variant,style=style,phrase=phrase)
   if q.text==text:matches.append(q)
 if len(matches)!=1:raise ValueError('Unsupported or ambiguous controlled-language realization')
 return matches[0]

def validate_query(prop,query):
 if not isinstance(query,CompiledQuery) or any(type(v) is not bool for _,v in query.answer_mapping):raise ValueError('Typed mapping required')
 parsed=parse_controlled_text(prop,query.format,query.variant,query.text)
 if parsed!=query:raise ValueError('Text/AST/mapping/evidence mismatch')
 if query.format=='B':
  for value in [False,True]:
   values=[e.value(value) for e in query.alternatives]
   if sum(values)!=1 or not query.alternatives[int(query.encode(value))].value(value):raise ValueError('Complement or answer mapping invalid')
 return True

def compile_set(prop):return tuple(compile_query(prop,m,v) for m in ['A','B'] for v in [0,1])
