"""Closed, immutable typed propositions; truth and witnesses belong to the evaluator."""
from dataclasses import dataclass,asdict
from enum import Enum
import re
def identifier(x):return isinstance(x,str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,63}",x) is not None
from .common import digest

class Predicate(str,Enum):
 AVAILABLE='unreserved_stock_positive'
 PRICE='offer_price_at_most'
 SHIPPING='shipping_fee_zero'
 DISPATCH='dispatch_within'
 FULFILLMENT='fulfillment_eligible'
 ELIGIBLE='request_eligible'

FIELDS={Predicate.AVAILABLE:('stock_units','reserved_units'),Predicate.PRICE:('price_cents',),
 Predicate.SHIPPING:('ship_cents',),Predicate.DISPATCH:('dispatch_days',),
 Predicate.FULFILLMENT:('stock_units','reserved_units','dispatch_days'),
 Predicate.ELIGIBLE:('suspended','premium','age','request_days')}

@dataclass(frozen=True)
class Argument:
 name:str
 kind:str
 value:str|int
 unit:str|None=None
 def __post_init__(self):
  if self.kind in ['entity_ref','policy_ref']:
   if not identifier(self.value) or self.unit is not None:raise ValueError('Invalid reference argument')
  elif self.kind=='nonnegative_integer':
   if type(self.value) is not int or not 0<=self.value<=10**9 or self.unit not in ['US_cent','day']:raise ValueError('Invalid integer/unit')
  else:raise ValueError('Unknown argument type')

@dataclass(frozen=True)
class RecordRef:
 source_id:str
 collection:str
 record_id:str
 required_fields:tuple[str,...]
 def __post_init__(self):
  if self.collection not in ['items','requests','policies'] or not identifier(self.record_id) or not identifier(self.source_id):raise ValueError('Invalid record reference')
  if type(self.required_fields) is not tuple or not self.required_fields or len(set(self.required_fields))!=len(self.required_fields):raise ValueError('Immutable distinct required fields')

@dataclass(frozen=True)
class Proposition:
 target_id:str
 source_id:str
 predicate:Predicate
 arguments:tuple[Argument,...]
 required_records:tuple[RecordRef,...]
 scope:str='single_ground_entity'
 quantification:str='none'
 negation_semantics:str='classical_boolean_complement'
 missing_value_semantics:str='reject_not_false'
 answer_type:str='boolean'
 schema_version:str='0.2.1'
 def __post_init__(self):
  if not isinstance(self.predicate,Predicate):raise ValueError('Predicate must be registered enum')
  if not identifier(self.target_id) or not identifier(self.source_id):raise ValueError('Missing identity')
  if type(self.arguments) is not tuple or type(self.required_records) is not tuple:raise ValueError('Immutable tuples required')
  if any(not isinstance(a,Argument) for a in self.arguments) or any(not isinstance(r,RecordRef) for r in self.required_records):raise ValueError('Typed arguments/records required')
  if self.scope!='single_ground_entity' or self.quantification!='none':raise ValueError('No policy validity or quantified targets')
  if self.negation_semantics!='classical_boolean_complement' or self.missing_value_semantics!='reject_not_false' or self.answer_type!='boolean' or self.schema_version!='0.2.1':raise ValueError('Unsupported semantic contract')
  args={a.name:a for a in self.arguments}
  if len(args)!=len(self.arguments) or 'entity' not in args or args['entity'].kind!='entity_ref':raise ValueError('Exactly one entity binding')
  expected={'entity'}|({'threshold'} if self.predicate in [Predicate.PRICE,Predicate.DISPATCH,Predicate.FULFILLMENT] else set())|({'policy'} if self.predicate==Predicate.ELIGIBLE else set())
  if set(args)!=expected:raise ValueError('Predicate argument signature mismatch')
  if 'threshold' in args:
   a=args['threshold'];unit='US_cent' if self.predicate==Predicate.PRICE else 'day'
   if a.kind!='nonnegative_integer' or a.unit!=unit:raise ValueError('Threshold unit mismatch')
  if 'policy' in args and args['policy'].kind!='policy_ref':raise ValueError('Policy reference required')
  records=self.required_records
  if len(records)!=(2 if self.predicate==Predicate.ELIGIBLE else 1):raise ValueError('Exact required records')
  entity_collection='requests' if self.predicate==Predicate.ELIGIBLE else 'items'
  entity_refs=[r for r in records if r.collection==entity_collection and r.record_id==args['entity'].value]
  if len(entity_refs)!=1 or set(entity_refs[0].required_fields)!=set(FIELDS[self.predicate]):raise ValueError('Record/field binding mismatch')
  if any(r.source_id!=self.source_id for r in records):raise ValueError('Cross-source record reference')
  if self.predicate==Predicate.ELIGIBLE:
   policy_refs=[r for r in records if r.collection=='policies' and r.record_id==args['policy'].value]
   if len(policy_refs)!=1 or set(policy_refs[0].required_fields)!={'min_age','max_request_days','suspension_overrides','premium_exception','version'}:raise ValueError('Executable policy record required')
 @property
 def entity_id(self):return next(a.value for a in self.arguments if a.name=='entity')
 @property
 def threshold(self):return next((a.value for a in self.arguments if a.name=='threshold'),None)
 @property
 def policy_id(self):return next((a.value for a in self.arguments if a.name=='policy'),None)
 def to_dict(self):
  obj=asdict(self);obj['predicate']=self.predicate.value;return obj
 @property
 def binding_sha256(self):return digest(self.to_dict())

@dataclass(frozen=True)
class GroundedTarget:
 proposition:Proposition
 truth:bool
 witness_sha256:str
 def __post_init__(self):
  if type(self.truth) is not bool:raise ValueError('Ground truth must be a boolean')
  if len(self.witness_sha256)!=64:raise ValueError('Invalid private witness digest')
 def private_dict(self):return {'proposition':self.proposition.to_dict(),'truth':self.truth,'private_witness_sha256':self.witness_sha256}

def from_dict(obj):
 keys=set(Proposition.__dataclass_fields__)
 if not isinstance(obj,dict) or set(obj)!=keys:raise ValueError('Unknown/missing proposition fields')
 vals=dict(obj);vals['predicate']=Predicate(vals['predicate'])
 vals['arguments']=tuple(Argument(**a) for a in vals['arguments'])
 vals['required_records']=tuple(RecordRef(**{**r,'required_fields':tuple(r['required_fields'])}) for r in vals['required_records'])
 return Proposition(**vals)
