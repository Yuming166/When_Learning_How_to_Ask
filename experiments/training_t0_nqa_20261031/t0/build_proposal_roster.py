"""Deterministic condition metadata only; no world, seed or response generation."""
import hashlib,itertools,json
from .bootstrap import ROOT

def condition(p,q,part,alpha,R):return {'p':p,'q':q,'partition':part,'alpha':alpha,'R':R,'eta':.05,'s':.8}
def key(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def main():
    a=condition(.8,.6,[1,3],1,16);b=condition(.9,.5,[4],3,64)
    bank=[condition(p,q,list(part),alpha,R) for p,q,part,alpha,R in itertools.product([.7,.8,.9],[.5,.6,.65],[(1,1),(1,3),(4,)],[0,1,3],[16,64]) if q<p]
    ordered=sorted(bank,key=lambda c:hashlib.sha256(('T1KLD-v1|condition-v1|'+key(c)).encode()).hexdigest())
    train=[a,b]+[c for c in ordered if key(c) not in {key(a),key(b)}][:126]
    validation=[train[4*i] for i in range(32)]
    strata={
     'ID':[a,b],
     'rate_interpolation':[condition(.85,.55,[1,3],1,16),condition(.85,.55,[4],3,64)],
     'rate_extrapolation':[condition(.65,.5,[4],3,16),condition(.94,.8,[1,3],3,16)],
     'grouping':[condition(.8,.6,[2,2],1,16),condition(.9,.5,[2,2],3,64)],
     'fact_count':[condition(.8,.6,[1,2],1,16),condition(.9,.5,[3],3,64)],
     'calibration':[condition(.8,.6,[1,3],2,16),condition(.9,.5,[4],6,64)],
     'risk_budget':[condition(.8,.6,[1,3],1,128),condition(.9,.5,[4],3,256)],
     'joint_shift':[condition(.85,.55,[1,2],6,128),condition(.94,.8,[3],2,128)]}
    dev=[{'stratum':name,'condition':c,'condition_replicate_slot':i} for name,cc in strata.items() for c in cc for i in range(4)]
    assert len(train)==128 and len(validation)==32 and len(dev)==64
    train_keys={key(c) for c in train}
    assert all(key(d['condition']) not in train_keys for d in dev if d['stratum']!='ID')
    assert {sum(c['partition']) for c in train}=={2,4}
    assert all(c['eta']==.05 and c['q']<c['p']<=.95 for c in train+validation+[d['condition'] for d in dev])
    exact_dev_ceiling=11*sum(max(2048,24*d['condition']['R']) for d in dev)
    obj={'status':'PROPOSED_METADATA_NOT_WORLDS','seeds_generated':0,'worlds_generated':0,'sampling_authorized':False,
         'train_condition_slots':train,'validation_condition_slots':validation,'development_condition_slots':dev,
         'development_max_actions_11_arms':exact_dev_ceiling,'all_stages_online_ceiling_from_roster':160*1024+exact_dev_ceiling,
         'note':'Same condition in two roles means independent future worlds; no role shares a latent world or potential response streams. Condition metadata is evaluator-only, never Student input.'}
    (ROOT/'T1_CONDITION_ROSTER.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'condition_slots':224,'new_worlds':0,'train_d':[2,4],'heldout_d':3,'proposed_max_online_actions':obj['all_stages_online_ceiling_from_roster']}))
if __name__=='__main__':main()
