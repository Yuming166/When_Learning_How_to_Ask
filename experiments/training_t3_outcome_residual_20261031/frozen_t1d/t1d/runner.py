"""Single sealed T1d development run; complete source verified before entropy."""
import hashlib,json,math,multiprocessing as mp,os,secrets,sys,time
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .policy import worker
from .strategies import POLICIES
from phase2d.runner import evaluate_job
from qrelbench.rpc import send
from qrelbench.security import protect_evaluator

from .roster import jobs,roster
from .integrity import digest,verify

def main():
 protect_evaluator();cfg=json.loads((ROOT/'config.json').read_text())
 if (ROOT/'artifacts').exists():raise RuntimeError('Refuse overwrite/retry')
 if cfg['split']!='development' or cfg['training_authorized'] or cfg['confirmation_authorized']:raise RuntimeError('Development no training only')
 pre=verify()
 out=ROOT/'artifacts';out.mkdir();private=out/'private';private.mkdir(mode=0o700)
 seed=secrets.token_hex(32);seedpath=private/'seed.json';seedpath.write_text(json.dumps({'development_seed':seed})+'\n');os.chmod(seedpath,0o600)
 plan=jobs(cfg);maximum=sum(j['online_cap'] for j in plan)*len(POLICIES)
 if maximum>cfg['limits']['online_actions']:raise RuntimeError('Planned action cap')
 receipt={'planned_trajectories':len(plan)*len(POLICIES),'independent_worlds':len(roster(cfg)),
  'budgets':cfg['budgets'],'primary_budget':cfg['primary_budget'],'maximum_online_actions':maximum,
  'source_manifest_sha256':digest(ROOT/'SOURCE_MANIFEST.json'),'source_coverage':pre,'seed_commitment':digest(seedpath),'training_updates':0,'model_calls':0,'confirmation_worlds':0,'retries':0}
 (out/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
 started=time.monotonic();cpu=time.process_time();deadline=started+cfg['limits']['wall_seconds'];context=mp.get_context('spawn')
 workers={};counters={'task':0,'type':0,'offline':0};finished=0;status='completed';error=None;current=None
 with (out/'trajectories.jsonl').open('x') as log,(out/'snapshots.jsonl').open('x') as snaps,(private/'reproduction.jsonl').open('x') as repro,(out/'failures.jsonl').open('x') as failed,(private/'partial_reproduction.jsonl').open('x') as partial:
  try:
   for name in POLICIES:
    parent,child=context.Pipe();proc=context.Process(target=worker,args=(child,name));proc.start();child.close();workers[name]=(parent,proc)
   for i,job in enumerate(plan):
    order=POLICIES[i%len(POLICIES):]+POLICIES[:i%len(POLICIES)]
    for name in order:
     current={'policy':name,'index':job['index'],'budget':job['budget']};parent,proc=workers[name]
     if not proc.is_alive():raise RuntimeError('Worker exited')
     def snapshot(row):snaps.write(json.dumps(row)+'\n');snaps.flush()
     def failure(row,priv):failed.write(json.dumps(row)+'\n');failed.flush();partial.write(json.dumps(priv)+'\n');partial.flush()
     final,priv,_=evaluate_job(parent,name,job,seed,deadline,counters,snapshot,failure)
     e=final['estimation_history'][-1];probs=np.array(e['joint_theta_distribution']);truth_index=sum(int(bit)<<(len(priv['truth'])-j-1) for j,bit in enumerate(priv['truth']))
     actual=np.zeros_like(probs);actual[truth_index]=1
     final['posterior_quality_posthoc']={'joint_nll':float(-np.log(max(probs[truth_index],1e-300))),
       'joint_brier':float(np.sum((probs-actual)**2)),'scope':'parent scoring only; not returned to policy'}
     log.write(json.dumps(final)+'\n');log.flush();repro.write(json.dumps(priv)+'\n');repro.flush();finished+=1
    if (i+1)%len(cfg['budgets'])==0:print(json.dumps({'world_budget_pairs':i+1,'fully_completed_worlds':(i+1)//len(cfg['budgets']),'trajectories':finished,'online':counters['task']+counters['type'],'seconds':round(time.monotonic()-started,1)}),flush=True)
   for parent,proc in workers.values():
    send(parent,None);proc.join(timeout=5)
    if proc.is_alive() or proc.exitcode!=0:raise RuntimeError('Worker shutdown failure')
  except Exception as exc:status='failed';error={'type':type(exc).__name__,'message':str(exc),'current':current}
  finally:
   for parent,proc in workers.values():
    if proc.is_alive():proc.terminate();proc.join(timeout=5)
    parent.close()
 try:preserved=verify()==pre
 except Exception as exc:
  preserved=False;status='integrity_failed';error={'type':type(exc).__name__,'message':str(exc),'previous_error':error}
 receipt.update(status=status,error=error,finished_trajectories=finished,costs_including_partial=counters,
  seconds=time.monotonic()-started,evaluator_cpu_seconds=time.process_time()-cpu,frozen_files_preserved=preserved)
 (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 if status!='completed' or not receipt['frozen_files_preserved']:raise SystemExit(1)
if __name__=='__main__':main()
