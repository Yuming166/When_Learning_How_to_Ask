"""Read-only historical complementarity; legal-feature associations, not oracle gains."""
import json
import numpy as np
from .bootstrap import ROOT
from .core import binary_entropy

def historical():
    pin=json.loads((ROOT/'HISTORICAL_INPUTS.json').read_text());old=pin['public_receipts']['T1d']['root']
    data={};features={}
    with open(old+'/artifacts/trajectories.jsonl') as f:
        for line in f:
            r=json.loads(line)
            if r['budget']!=32:continue
            key=r['index'];data.setdefault(key,{})[r['policy']]=int(r['exact'])
            if r['policy']=='WorstFact-MI':
                first=next(e for e in r['estimation_history'] if e['online']==4*sum(r['partition']))
                features[key]={'type_entropy':float(np.mean(binary_entropy(first['z_prob']))/np.log(2)),
                  'mean_fact_entropy':float(np.mean(binary_entropy(first['theta_prob']))/np.log(2)),
                  'joint_map_probability':first['joint_MAP_probability'],'estimated_gap':first['p']-first['q']}
    keys=sorted(data);names=sorted(data[keys[0]]);base=np.array([data[k]['WorstFact-MI'] for k in keys]);pairs={}
    for n in names:
        y=np.array([data[k][n] for k in keys]);delta=y-base
        associations={}
        for feature in next(iter(features.values())):
            x=np.array([features[k][feature] for k in keys])
            associations[feature]={'correlation_with_paired_outcome':float(np.corrcoef(x,delta)[0,1]) if np.std(delta)>0 and np.std(x)>0 else None}
        pairs[n]={'successes':int(y.sum()),'wins':int(np.sum((y==1)&(base==0))),
          'losses':int(np.sum((y==0)&(base==1))),'observable_prefix_associations':associations}
    oracle=np.array([max(data[k].values()) for k in keys])
    subset=['WorstFact-MI','Fresh-IG-Lite','KL-AnalyticReuse','Fused-Info','IG-Fact-FixedType']
    candidate_oracle=np.array([max(data[k][n] for n in subset) for k in keys])
    result={'worlds':len(keys),'baseline_successes':int(base.sum()),'all_policy_hindsight_oracle':int(oracle.sum()),
      'candidate_policy_hindsight_oracle':int(candidate_oracle.sum()),'candidate_oracle_headroom_pp':float(100*np.mean(candidate_oracle-base)),
      'pairs':pairs,'prefix':'first free round at t=4d; all arms share only forced task history at this point',
      'scope':'Historical development-only opportunity audit. Full-policy oracle cannot select actions; associations are exploratory, not deployable gains.',
      'T1b_interface':'Four macro proposals KL/IG/TYPE/TASK; all legal joint posterior. T3 adds WorstFact and a task fallback; physical actions deduplicated.',
      'historical_private_or_confirmation_access':False}
    (ROOT/'HISTORICAL_LEARNABILITY.json').write_text(json.dumps(result,indent=2)+'\n');return result

def label_gate(states,cfg):
    # This is a deliberately weak feasibility gate for one small fit, not a
    # validation of predictability or population policy improvement.
    diff=[];corr=[];disagree=0;variability=[]
    for s in states:
        q=s['values']['q'];base=s['proposals']['worst'];X=np.asarray(s['features'])
        disagree+=len(set(s['proposals'].values()))>1
        typ=s['proposals']['type'];adv=float(q[str(typ)])-float(q[str(base)])
        diff.append(adv);corr.append(X[base,[2,5,8,11,14]].tolist())
        variability.append(max(q.values())-min(q.values()))
    corr=np.asarray(corr);delta=np.asarray(diff);values=[]
    for i in range(corr.shape[1]):
        values.append(float(np.corrcoef(corr[:,i],delta)[0,1]) if np.std(corr[:,i])>1e-10 and np.std(delta)>1e-10 else 0.)
    old=json.loads((ROOT/'HISTORICAL_LEARNABILITY.json').read_text())
    gates={'historical_candidate_headroom_at_least_5pp':old['candidate_oracle_headroom_pp']>=5,
      'candidate_disagreement_at_least_10percent':disagree/len(states)>=.10,
      'mean_within_state_Q_range_at_least_005':float(np.mean(variability))>=.005,
      'observable_association_abs_at_least_010':max(map(abs,values))>=.10}
    return {'pass':all(gates.values()),'gates':gates,'train_states':len(states),'candidate_disagreement_fraction':disagree/len(states),
      'mean_Q_range':float(np.mean(variability)),'type_advantage_sd':float(np.std(delta)),
      'observable_associations':dict(zip(['remaining_budget','mean_fact_entropy','mean_type_entropy','joint_map_probability','posterior_rate_gap'],values)),
      'qualification':'Exploratory feasibility only. Repeated states are clustered by world. Correlation is not a learnability theorem, value-label accuracy guarantee, or a test result.'}
