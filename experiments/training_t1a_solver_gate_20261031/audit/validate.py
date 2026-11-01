"""Independent saved-result consistency checks, no new experiment actions."""
import hashlib,json,math
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 snap=json.loads((ROOT/'INPUT_SNAPSHOT.json').read_text())
 for p,h in snap['files'].items():assert sha(p)==h,p
 freeze=json.loads((ROOT/'freeze.json').read_text())
 for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
 rows=[json.loads(l) for l in (ROOT/'artifacts/closed_loop/trajectories.jsonl').read_text().splitlines()]
 assert len(rows)==256
 groups={};updates=0;mininfo=float('inf');maxgap=0.;gates=0
 for r in rows:
  assert r['stop_mode']=='certified'
  assert r['p']==.85 and r['q']==.6 and r['eta']==.05 and r['s']==.8
  assert r['online']<=r['online_cap'] and r['costs']['offline']==2*r['M']
  counts=np.asarray(r['counts']);tasks=int(counts.sum());types=sum(map(len,r['type_answers']))
  assert tasks==r['costs']['task'] and types==r['costs']['type'] and tasks+types==r['online']
  assert all(len(v)==r['M'] for v in r['calibration'].values())
  assert r['total_acquisition']==sum(r['costs'].values())
  assert r['censored']==(not r['complete']) and r['abstained']==(not r['complete'])
  if r['complete']:
   g=r['strict_certificate'];gates+=1
   assert g['certified'] and g['interval_certified'] and g['status']=='certified'
   assert Decimal(g['gap_lower'])>Decimal(g['beta_upper'])
   assert g['theta']==r['strictly_certified_output']==r['fit']['theta']
   assert g['total_observations']==r['online']+2*r['M']
   assert g['reference_count_per_stream']==r['M']
   assert g['task_counts']==counts.sum(axis=2).tolist()
   assert g['type_counts']==list(map(len,r['type_answers']))
   d=sum(r['partition']);G=len(r['partition'])
   assert g['sign_candidates']==2**d and g['type_candidates']==2**G and g['joint_candidates']==2**(d+G)
   assert Fraction(g['exact_input_parameters']['R'])==Fraction(r['R'])
   assert Fraction(g['exact_input_parameters']['eta'])==Fraction(r['eta'])
   assert list(map(Fraction,g['exact_input_parameters']['type_accuracy']))==[Fraction(r['s'])]*G
  else:assert r['strictly_certified_output'] is None
  assert r['isolation']['no_new_privileges'] and r['isolation']['landlock_abi']>=4
  key=(r['index'],tuple(r['partition']),r['alpha'],r['R'])
  groups.setdefault(key,[]).append(r)
  for e in r['estimation_history']:
   if 'minimum_information' not in e:continue
   updates+=1;mininfo=min(mininfo,e['minimum_information']);maxgap=max(maxgap,e['solver_relative_gap'])
   assert e['minimum_information']>=1-1e-7 and -5e-8<=e['solver_relative_gap']<=e['effective_numerical_relative_gap']
   assert e['next_update']-e['online']==math.ceil(math.sqrt(e['online']+1))
   weights=np.asarray(e['weights']);assert np.isfinite(weights).all() and (weights>=0).all() and abs(weights.sum()-1)<1e-7
 assert len(groups)==32 and all(len(v)==8 for v in groups.values())
 assert all(len({json.dumps(r['calibration'],sort_keys=True) for r in rr})==1 for rr in groups.values())
 offline=[json.loads(l) for l in (ROOT/'artifacts/offline_rows.jsonl').read_text().splitlines()]
 fixtures=json.loads((ROOT/'artifacts/numerical_fixtures.json').read_text())
 assert len(offline)==483 and len(fixtures)==56
 for r in offline+fixtures:
  assert r['finite_nonnegative'] and r['minimum_information_independent_scalar']>=1-1e-7
  assert -5e-8<=r['own_relative_gap']<=5e-4
 # Check the full T0 dependency snapshot as well, preserving historical negative-result reports.
 t0path=next(Path(p) for p in snap['files'] if p.endswith('training_t0_nqa_20261031/INPUT_SNAPSHOT.json'))
 earlier=json.loads(t0path.read_text());previous=earlier.get('inputs',earlier.get('files',{}))
 for p,h in previous.items():assert sha(p)==h,p
 result={'status':'PASS','scope':'saved-result consistency + frozen-dependency hashes; not a general mathematical certificate',
   'independent_worlds':32,'matched_arms':8,'trajectories_checked':len(rows),'complete_gate_records_checked':gates,
   'planning_updates_checked':updates,'minimum_logged_information':mininfo,'maximum_logged_relative_gap':maxgap,
   'offline_updates_independently_scalar_checked':len(offline),'deterministic_fixture_solver_results_checked':len(fixtures),
   'public_input_files_preserved':len(snap['files']),'frozen_files_preserved':len(freeze['files']),
   'prior_T0_inputs_preserved':len(previous),'training_updates':0,'model_calls':0,'confirmation_worlds':0,
   'new_worlds_generated_by_analysis':0}
 (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
