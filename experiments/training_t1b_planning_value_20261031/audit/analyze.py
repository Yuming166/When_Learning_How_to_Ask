"""Analyze the single sealed evaluation; no actions or training."""
from pathlib import Path
import collections,hashlib,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
NAMES=['AnalyticReuse','Fused-Info','Fused-D-RRC-Type','Fixed-KL-IG','Type-Then-Task','Fresh-IG','Task-Only','Recovery-1','Lookahead-2']
def dump(path,x):path.write_text(json.dumps(x,indent=2)+'\n')
def lines(path):return [json.loads(l) for l in path.read_text().splitlines()]
def main():
 receipt=json.loads((ROOT/'artifacts/execution.json').read_text())
 if receipt['status']!='completed':raise RuntimeError('Do not treat incomplete run as completed comparison')
 rows=lines(ROOT/'artifacts/trajectories.jsonl');by={(r['index'],r['budget'],r['policy']):r for r in rows}
 ids=sorted({r['index'] for r in rows});ref=[by[i,32,'AnalyticReuse'] for i in ids]
 cells=collections.defaultdict(list)
 for j,r in enumerate(ref):cells[(tuple(r['partition']),r['p'],r['alpha'])].append(j)
 rng=np.random.default_rng(22017);boot=np.concatenate([rng.choice(ii,(20000,len(ii)),replace=True) for key,ii in sorted(cells.items())],axis=1)
 summaries={};comparisons=[];percell=[];pairrows=[]
 for B in [16,32,64]:
  summaries[B]={}
  for name in NAMES:
   rr=[by[i,B,name] for i in ids];correct=np.array([r['exact'] for r in rr],float)
   decisions=[d for r in rr for d in r['estimation_history'][-1]['decision_history']]
   two=[d for d in decisions if 'nonmyopic_model_gain' in d]
   e=[r['estimation_history'][-1] for r in rr];macros=collections.Counter(d['macro'] for d in decisions)
   cc={k:sum(r['costs'][k] for r in rr) for k in ['task','type','offline']}
   dct={'worlds':len(rr),'successes':int(correct.sum()),'accuracy':float(correct.mean()),
    'accuracy_ci95':np.quantile(correct[boot].mean(1),[.025,.975]).tolist(),
    'online_sum':sum(r['online'] for r in rr),'online_mean':B,'costs':cc,'total_acquisition_sum':sum(cc.values()),
    'type_mean':cc['type']/len(rr),'offline_mean':cc['offline']/len(rr),
    'trajectory_cpu':sum(r['trajectory_cpu_seconds'] for r in rr),'trajectory_wall':sum(r['trajectory_wall_seconds'] for r in rr),
    'cpu_median':float(np.median([r['trajectory_cpu_seconds'] for r in rr])),
    'cpu_p90':float(np.quantile([r['trajectory_cpu_seconds'] for r in rr],.9)),
    'planner_cpu':sum(r['planner_cpu_seconds'] for r in rr),'controller_cpu':sum(x['controller_cpu'] for x in e),
    'forecast_solver_cpu':sum(x['forecast_solver_cpu'].get('total',0) for x in e),
    'terminal_belief_cpu':sum(x['terminal_belief_cpu'] for x in e),'gate_cpu':sum(r['gate_cpu_seconds'] for r in rr),
    'certified':sum(r['complete'] for r in rr),'wrong_certified':sum(r['complete'] and not r['exact'] for r in rr),
    'gate_undetermined':sum(g['status']=='undetermined' for r in rr for g in r['gate_history']),
    'fixed_budget_completed':sum(r['online']==B for r in rr),'terminal_uncertified':sum(not r['complete'] for r in rr),
    'joint_nll_mean':float(np.mean([r['posterior_quality_posthoc']['joint_nll'] for r in rr])),
    'joint_brier_mean':float(np.mean([r['posterior_quality_posthoc']['joint_brier'] for r in rr])),
    'p_mae':float(np.mean([abs(x['p_error']) for x in e])),'q_mae':float(np.mean([abs(x['q_error']) for x in e])),
    'terminal_type_errors':sum(x['type_errors'] for x in e),'macros':dict(macros),'controlled_actions':len(decisions),
    'two_step_decisions':len(two),'model_gain_over_1e6':sum(d['nonmyopic_model_gain']>1e-6 for d in two),
    'model_gain_positive_fraction':sum(d['nonmyopic_model_gain']>1e-6 for d in two)/max(1,len(two)),
    'model_gain_mean':float(np.mean([d['nonmyopic_model_gain'] for d in two])) if two else 0,
    'model_gain_max':max([d['nonmyopic_model_gain'] for d in two],default=0),
    'different_from_myopic':sum(d['different_from_myopic_action'] for d in two)}
   summaries[B][name]=dct
   for r in rr:
    pairrows.append({'index':r['index'],'partition':r['partition'],'p_design':r['p'],'alpha':r['alpha'],'budget':B,
      'policy':name,'complete_recovery':r['exact'],'terminal_certified':r['complete'],'online':r['online'],
      'type':r['costs']['type'],'offline':r['costs']['offline'],'cpu':r['trajectory_cpu_seconds'],
      'posterior_nll':r['posterior_quality_posthoc']['joint_nll']})
  target=np.array([by[i,B,'Lookahead-2']['exact'] for i in ids],float)
  for name in NAMES[:-1]:
   baseline=np.array([by[i,B,name]['exact'] for i in ids],float);diff=target-baseline
   comparisons.append({'budget':B,'reference':name,'difference':float(diff.mean()),
     'ci95':np.quantile(diff[boot].mean(1),[.025,.975]).tolist(),'wins':int(sum(diff>0)),
     'losses':int(sum(diff<0)),'ties':int(sum(diff==0)),'n':len(diff)})
  for key,ii in sorted(cells.items()):
   rr=[by[ids[j],B,'AnalyticReuse'] for j in ii]
   rec={name:sum(by[ids[j],B,name]['exact'] for j in ii) for name in NAMES}
   percell.append({'partition':key[0],'p':key[1],'alpha':key[2],'budget':B,'n':len(ii),
       'success_counts':rec,'reference_ceiling':rec['AnalyticReuse']/len(ii)>=.95})
 primary=[c for c in comparisons if c['budget']==32];kl=next(c for c in primary if c['reference']=='AnalyticReuse');one=next(c for c in primary if c['reference']=='Recovery-1')
 secondary=all(c['difference']>=0 for c in primary if c['reference'] not in ['AnalyticReuse','Recovery-1'])
 la=summaries[32]['Lookahead-2']
 passed=(kl['difference']>=.03 and kl['ci95'][0]>0 and one['difference']>=.01 and one['ci95'][0]>0 and secondary and la['model_gain_positive_fraction']>=.05)
 decision='GO' if passed else ('NO-GO' if kl['difference']<=0 and one['difference']<=0 else 'REVISE')
 result={'status':'BOUNDED_DEVELOPMENT_ONLY','decision':decision,'worlds':len(ids),'trajectories':len(rows),'primary_budget':32,
   'summaries':summaries,'paired_accuracy_differences':comparisons,'cells':percell,'execution':receipt,
   'gate_checks':{'gain_vs_KL':kl,'gain_vs_same_objective_one_step':one,'not_below_other_cheap_baselines_by_point':secondary,
                 'positive_model_gain_fraction':la['model_gain_positive_fraction'],'passed':passed},
   'training_updates':0,'rl_training_rollouts':0,'model_calls':0,'confirmation_worlds':0,
   'uncertainty':'world-paired stratified 20000 percentile bootstrap, seed22017; exploratory, not confirmation'}
 dump(ROOT/'RESULTS.json',result);dump(ROOT/'PAIRED_OUTCOMES.json',pairrows)
 print(json.dumps({'decision':decision,'gate':result['gate_checks'],'B32':summaries[32]}))
if __name__=='__main__':main()
