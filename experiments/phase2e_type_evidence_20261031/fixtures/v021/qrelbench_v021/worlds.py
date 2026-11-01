"""Offline fixtures: independent target bits or explicitly dependent mechanism worlds."""
import hashlib,hmac,random
from .canonical import Proposition,Predicate,Argument,RecordRef,GroundedTarget,FIELDS
from .common import digest
from .truth import evaluate,evaluate_sql,POLICY_VERSION

class Streams:
 def __init__(self,key):
  if type(key) is not bytes or len(key)<16:raise ValueError('At least128 bits evaluator entropy')
  self.key=key
 def block(self,*labels):return hmac.new(self.key,'|'.join(map(str,labels)).encode(),hashlib.sha256).digest()
 def bit(self,*labels):return bool(self.block(*labels)[0]&1)
 def rng(self,*labels):return random.Random(int.from_bytes(self.block(*labels),'big'))
 def identity(self,kind,*labels):return kind+self.block('public_identifier',kind,*labels).hex()[:16]

def make_prop(sid,eid,target_id,predicate,policy_id=None,threshold=None):
 args=[Argument('entity','entity_ref',eid)]
 if predicate in [Predicate.PRICE,Predicate.DISPATCH,Predicate.FULFILLMENT]:args.append(Argument('threshold','nonnegative_integer',threshold,'US_cent' if predicate==Predicate.PRICE else 'day'))
 refs=[RecordRef(sid,'requests' if predicate==Predicate.ELIGIBLE else 'items',eid,FIELDS[predicate])]
 if predicate==Predicate.ELIGIBLE:
  args.append(Argument('policy','policy_ref',policy_id));refs.append(RecordRef(sid,'policies',policy_id,('min_age','max_request_days','suspension_overrides','premium_exception','version')))
 return Proposition(target_id,sid,predicate,tuple(args),tuple(refs))

def policy_value(record,policy):return not record['suspended'] and (record['premium'] or (record['age']>=policy['min_age'] and record['request_days']<=policy['max_request_days']))

def item_witness(predicate,value,rng,threshold=None):
 rec={'stock_units':rng.randint(0,20),'reserved_units':rng.randint(0,10),'price_cents':rng.randint(0,20000),
  'ship_cents':rng.choice([0,100,300,500]),'dispatch_days':rng.randint(0,10)}
 if predicate==Predicate.AVAILABLE:
  reserved=rng.randint(1,10);rec.update(reserved_units=reserved,stock_units=reserved+rng.randint(1,5) if value else rng.randint(0,reserved))
 elif predicate==Predicate.PRICE:rec['price_cents']=rng.randint(0,threshold) if value else threshold+rng.randint(1,10000)
 elif predicate==Predicate.SHIPPING:rec['ship_cents']=0 if value else rng.randint(1,10)*100
 elif predicate==Predicate.DISPATCH:rec['dispatch_days']=rng.randint(0,threshold) if value else threshold+rng.randint(1,7)
 else:raise ValueError('Unsupported independent witness')
 return rec

def request_witness(value,rng,policy):
 for _ in range(1024):
  rec={'suspended':bool(rng.getrandbits(1)),'premium':bool(rng.getrandbits(1)),
   'age':rng.choice([16,17,18,20,21,25,40]),'request_days':rng.choice([0,14,15,29,30,31,45,60])}
  if policy_value(rec,policy)==value:return rec
 raise RuntimeError('Witness construction failed; do not change sampled truth')

def make_world(key,mode='independent_fixture'):
 if mode not in ['independent_fixture','dependent_mechanism_fixture']:raise ValueError('Explicit dependency mode required')
 streams=Streams(key);world={'sources':{}};props=[];sampled_bits=[];dependencies=[]
 public={'benchmark':'QRelBench','version':'0.2.1-dev','namespace':'offline_technical_fixture',
  'approved_natural_dataset':False,'d':48,'groups':[],'targets':[],'formats':['A','B'],
  'calibration':'unavailable','type_report_accuracy':'unknown'}
 kinds=[Predicate.AVAILABLE,Predicate.PRICE,Predicate.SHIPPING,Predicate.DISPATCH,Predicate.AVAILABLE,Predicate.PRICE]
 for g in range(8):
  sid=streams.identity('s',g);domain='commerce' if g<4 else 'policy';pid=streams.identity('r','policy',g)
  policy={'min_age':18,'max_request_days':30,'suspension_overrides':True,'premium_exception':True,'version':POLICY_VERSION}
  if mode=='dependent_mechanism_fixture' and domain=='policy':
   rng=streams.rng('private_policy_parameters',g);policy.update(min_age=rng.choice([18,21]),max_request_days=rng.choice([14,30]))
  world['sources'][sid]={'items':{},'requests':{},'policies':{pid:policy} if domain=='policy' else {}}
  group={'id':sid,'domain':domain,'targets':list(range(g*6,g*6+6)),
   'description':'Fictional inventory, offered pricing, shipping and dispatch information.' if domain=='commerce' else 'Fictional request eligibility information governed by an explicit policy.'}
  public['groups'].append(group);shared={}
  for local in range(6):
   j=g*6+local;target_id=streams.identity('t',g,local);eid=streams.identity('e',g,local)
   kind=kinds[local] if domain=='commerce' else Predicate.ELIGIBLE;threshold=10000 if kind==Predicate.PRICE else 3 if kind==Predicate.DISPATCH else None
   rng=streams.rng('private_record_witness',g,local);sampled=None
   if mode=='dependent_mechanism_fixture' and domain=='commerce':
    branch=local%3;entity_slot=local//3;eid=streams.identity('e','shared',g,entity_slot)
    kind=[Predicate.AVAILABLE,Predicate.DISPATCH,Predicate.FULFILLMENT][branch];threshold=3 if branch in [1,2] else None
    if entity_slot not in shared:
     rr=streams.rng('private_shared_record',g,entity_slot)
     shared[entity_slot]={'stock_units':rr.randint(0,10),'reserved_units':rr.randint(0,10),'price_cents':rr.randint(0,20000),'ship_cents':rr.choice([0,500]),'dispatch_days':rr.randint(0,6)}
    rec=dict(shared[entity_slot])
    if branch==2:dependencies.append({'target':target_id,'relation':'AND','parents':[props[-2].target_id,props[-1].target_id], 'exact_constraint':'fulfillment = available_stock AND dispatch_within_threshold'})
   elif mode=='dependent_mechanism_fixture' and domain=='policy':
    rec={'suspended':bool(rng.getrandbits(1)),'premium':bool(rng.getrandbits(1)),'age':rng.randint(16,40),'request_days':rng.randint(0,60)}
   else:
    sampled=streams.bit('private_independent_truth',g,local);sampled_bits.append(sampled)
    rec=item_witness(kind,sampled,rng,threshold) if domain=='commerce' else request_witness(sampled,rng,policy)
   prop=make_prop(sid,eid,target_id,kind,pid,threshold)
   world['sources'][sid]['requests' if domain=='policy' else 'items'][eid]=rec
   value=evaluate(prop,world)
   if value!=evaluate_sql(prop,world) or sampled is not None and value!=sampled:raise RuntimeError('Truth witness mismatch')
   props.append(prop)
   public['targets'].append({'j':j,'id':target_id,'group':g,'proposition':prop.to_dict()})
  dependencies.append({'source':sid,'relation':'shared_policy_specification' if domain=='policy' else 'record_ownership',
   'targets':[p.target_id for p in props[g*6:g*6+6]],'statistical_label_dependence':mode=='dependent_mechanism_fixture',
   'note':'Fixed policy, separate independently realized records' if mode=='independent_fixture' else 'Shared source policy parameters or shared record and derived targets'})
 grounded=[]
 for prop in props:
  # Private digest stays private; exposing low-entropy record hashes could be a dictionary attack.
  witnesses=[world['sources'][ref.source_id][ref.collection][ref.record_id] for ref in prop.required_records]
  grounded.append(GroundedTarget(prop,evaluate(prop,world),digest(witnesses)))
 return {'public':public,'private_world':world,'propositions':props,'grounded':grounded,
  'dependencies':dependencies,'mode':mode,'truth_prior':'independent domain-separated pseudorandom Bernoulli(0.5) bits; no per-source/dataset balance conditioning' if mode=='independent_fixture' else 'record/policy-derived dependent truths; not a theory-faithful label model',
  'public_export_is_fixture':True}
