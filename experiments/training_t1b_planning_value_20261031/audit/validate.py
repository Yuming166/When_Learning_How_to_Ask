"""Audit recorded costs, boundaries and finite numerical posterior checks."""
import hashlib,json,math,sys
from pathlib import Path
from decimal import Decimal
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from t1b import bootstrap
from t1b.belief import Belief
from phase2e.estimator import posterior

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=json.loads((ROOT/'artifacts/execution.json').read_text());assert receipt['status']=='completed'
 freeze=json.loads((ROOT/'freeze.json').read_text());snap=json.loads((ROOT/'INPUT_SNAPSHOT.json').read_text())
 for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
 for p,h in snap['files'].items():assert sha(p)==h,p
 t1a_receipt=next(Path(p) for p in snap['files'] if p.endswith('/FINAL_RECEIPT.json'))
 t1a=json.loads(t1a_receipt.read_text())
 for p,h in t1a['public_files'].items():assert sha(t1a_receipt.parent/p)==h,p
 rows=[json.loads(l) for l in (ROOT/'artifacts/trajectories.jsonl').read_text().splitlines()]
 assert len(rows)==2592
 worlds={r['index'] for r in rows};assert len(worlds)==96
 groups={};two=0;mindiff=1.;controlled=0;certified=0;calcounts={}
 for r in rows:
  B=r['budget'];assert r['online']==B and B in [16,32,64]
  data=np.asarray(r['counts']);task=int(data.sum());ty=sum(map(len,r['type_answers']))
  assert task==r['costs']['task'] and ty==r['costs']['type'] and task+ty==B
  assert r['costs']['offline']==2*r['M'] and all(len(v)==r['M'] for v in r['calibration'].values())
  assert r['total_acquisition']==sum(r['costs'].values())
  e=r['estimation_history'][-1];p=np.asarray(e['joint_theta_distribution']);assert np.isfinite(p).all() and (p>=0).all() and abs(p.sum()-1)<1e-12
  assert r['fit']['theta']==e['joint_theta_MAP']
  gate=r['strict_certificate'];assert gate['total_observations']==B+2*r['M']
  assert gate['task_counts']==data.sum(axis=2).tolist() and gate['type_counts']==list(map(len,r['type_answers']))
  assert gate['reference_count_per_stream']==r['M'] and gate['joint_candidates']==2**(4+len(r['partition']))
  assert r['complete']==gate['certified'] and r['censored']==(not gate['certified'])
  if gate['certified']:
   certified+=1;assert Decimal(gate['gap_lower'])>Decimal(gate['beta_upper'])
   assert gate['theta']==r['strictly_certified_output']==r['fit']['theta']
  else:assert r['strictly_certified_output'] is None
  assert r['isolation']['landlock_abi']>=4 and r['isolation']['no_new_privileges']
  assert sum(np.asarray(r['tracking_diagnostics']['forced_task_counts']).ravel())==r['forced_tasks']
  expectedforced=sum(1 for t in range(B) if (t-8*math.isqrt(t//8)**2)<8)
  assert r['forced_tasks']==expectedforced
  for d in e['decision_history']:
   controlled+=1;assert d['online_before']>=16 and d['remaining_budget']==B-d['online_before']
   assert d['macro'] in ['KL','IG','TYPE','TASK'] and 0<=d['primitive_action']<8+len(r['partition'])
   if 'nonmyopic_model_gain' in d:
    two+=1;mindiff=min(mindiff,d['nonmyopic_model_gain']);assert d['nonmyopic_model_gain']>=-2e-12
  groups.setdefault((r['index'],B),[]).append(r)
  calcounts.setdefault(r['index'],set()).add(json.dumps(r['calibration'],sort_keys=True))
 assert len(groups)==288 and all(len(g)==9 for g in groups.values())
 assert all(len(v)==1 for v in calcounts.values())
 # B16 cannot be influenced by residual controllers: all observations match.
 for key,rr in groups.items():
  if key[1]!=16:continue
  assert len({json.dumps((r['counts'],r['type_answers']),sort_keys=True) for r in rr})==1
  assert len({tuple(r['fit']['theta']) for r in rr})==1
 # The half-budget fixed switch coincides with Fresh-IG at B32.
 for key,rr in groups.items():
  if key[1]!=32:continue
  a=next(r for r in rr if r['policy']=='Fixed-KL-IG');b=next(r for r in rr if r['policy']=='Fresh-IG')
  assert a['counts']==b['counts'] and a['type_answers']==b['type_answers']
 # Predeclared numerical sensitivity panel; no policy reruns or new actions.
 panel=[]
 for r in rows:
  if r['replicate']!=0 or r['budget']!=32 or r['policy'] not in ['Recovery-1','Lookahead-2']:continue
  groups2=[];j=0
  for size in r['partition']:groups2.append(list(range(j,j+size)));j+=size
  high=posterior(r['counts'],groups2,r['calibration'],r['type_answers'],[r['s']]*len(groups2),r['eta'],order=64)
  w=np.exp(high['_logjoint']);mass=w.reshape(16,2**len(groups2),-1).sum(axis=(1,2));e=r['estimation_history'][-1]
  panel.append({'index':r['index'],'policy':r['policy'],'budget':32,'maximum_joint_theta_mass_error':float(np.max(np.abs(mass-np.asarray(e['joint_theta_distribution'])))),
    'p_error_32_vs_64':abs(e['p']-high['p']),'q_error_32_vs_64':abs(e['q']-high['q']),
    'joint_MAP_agrees':high['_theta'][int(np.argmax(mass))].tolist()==e['joint_theta_MAP']})
 assert len(panel)==24
 (ROOT/'QUADRATURE_SENSITIVITY.json').write_text(json.dumps(panel,indent=2)+'\n')
 result={'status':'PASS','scope':'finite saved-record and numerical consistency audit; not general solver or posterior certification',
   'source_hashes_preserved':len(freeze['files']),'historical_hashes_preserved':len(snap['files']),'t1a_all_public_files_preserved':len(t1a['public_files']),
   'independent_worlds':96,'paths':len(rows),'matched_world_budget_pairs':len(groups),'all_B16_actions_match':True,
   'all_observation_cost_records_checked':len(rows),'all_terminal_certificates_checked':len(rows),'certified':certified,
   'controlled_actions_checked':controlled,'two_step_decisions_checked':two,'minimum_two_step_gain':mindiff,
   'sensitivity_states':len(panel),'maximum_joint_mass_error_32_64':max(p['maximum_joint_theta_mass_error'] for p in panel),
   'sensitivity_joint_MAP_agrees':sum(p['joint_MAP_agrees'] for p in panel),
   'training_updates':0,'rl_training_rollouts':0,'confirmation_worlds':0,'analysis_new_worlds':0}
 (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
