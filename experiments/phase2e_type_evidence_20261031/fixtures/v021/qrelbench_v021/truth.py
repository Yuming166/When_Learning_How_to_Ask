"""Two executable truth backends, strict domains and authoritative rule renderer."""
import sqlite3
from .canonical import Predicate,FIELDS
POLICY_VERSION='eligibility_v1'
def validate_policy(policy):
 if set(policy)!={'min_age','max_request_days','suspension_overrides','premium_exception','version'}:raise ValueError('Policy fields')
 for name in ['min_age','max_request_days']:
  if type(policy[name]) is not int or not 0<=policy[name]<=10**9:raise ValueError('Policy integer domain')
 if policy['version']!=POLICY_VERSION or policy['suspension_overrides'] is not True or policy['premium_exception'] is not True:raise ValueError('Unsupported rule or precedence')

def resolve(prop,world):
 records=[]
 for ref in prop.required_records:
  try:r=world['sources'][ref.source_id][ref.collection][ref.record_id]
  except (KeyError,TypeError):raise ValueError('Missing required source record') from None
  if not isinstance(r,dict) or not set(ref.required_fields)<=set(r):raise ValueError('Missing required field')
  records.append(r)
 rec=records[0]
 # Required record order is semantically checked rather than inferred from arbitrary dict order.
 collection='requests' if prop.predicate==Predicate.ELIGIBLE else 'items'
 rec=next(r for ref,r in zip(prop.required_records,records) if ref.collection==collection)
 for key in FIELDS[prop.predicate]:
  value=rec[key]
  if key in ['suspended','premium']:
   if type(value) is not bool:raise ValueError('Boolean field required')
  elif type(value) is not int or value<0 or value>10**9:raise ValueError('Bounded nonnegative integer required')
 policy=next((r for ref,r in zip(prop.required_records,records) if ref.collection=='policies'),None)
 if policy is not None:validate_policy(policy)
 return rec,policy

def evaluate(prop,world):
 r,p=resolve(prop,world);k=prop.predicate
 if k==Predicate.AVAILABLE:value=r['stock_units']-r['reserved_units']>0
 elif k==Predicate.PRICE:value=r['price_cents']<=prop.threshold
 elif k==Predicate.SHIPPING:value=r['ship_cents']==0
 elif k==Predicate.DISPATCH:value=r['dispatch_days']<=prop.threshold
 elif k==Predicate.FULFILLMENT:value=r['stock_units']-r['reserved_units']>0 and r['dispatch_days']<=prop.threshold
 else:value=(not r['suspended']) and (r['premium'] or (r['age']>=p['min_age'] and r['request_days']<=p['max_request_days']))
 return bool(value)

def evaluate_sql(prop,world):
 r,p=resolve(prop,world);k=prop.predicate;fields=FIELDS[k];db=sqlite3.connect(':memory:')
 try:
  db.execute('CREATE TABLE r ('+','.join('"'+f+'" INTEGER NOT NULL' for f in fields)+')')
  db.execute('INSERT INTO r VALUES ('+','.join('?' for _ in fields)+')',[int(r[f]) for f in fields])
  expr={Predicate.AVAILABLE:('stock_units-reserved_units>0',[]),Predicate.PRICE:('price_cents<=?',[prop.threshold]),
   Predicate.SHIPPING:('ship_cents=0',[]),Predicate.DISPATCH:('dispatch_days<=?',[prop.threshold]),
   Predicate.FULFILLMENT:('(stock_units-reserved_units>0) AND dispatch_days<=?',[prop.threshold])}
  if k==Predicate.ELIGIBLE:formula='(NOT suspended) AND (premium OR (age>=? AND request_days<=?))';params=[p['min_age'],p['max_request_days']]
  else:formula,params=expr[k]
  return bool(db.execute('SELECT '+formula+' FROM r',params).fetchone()[0])
 finally:db.close()

def render_policy(policy_id,policy):
 validate_policy(policy)
 return (f'Policy {policy_id}: a request is eligible if and only if its account is not suspended AND '
   f'(the account is premium OR (the applicant age is at least {policy["min_age"]} years AND the request age is at most {policy["max_request_days"]} days)). '
   'A suspended account is ineligible even if it is premium. The age and day thresholds are inclusive.')
