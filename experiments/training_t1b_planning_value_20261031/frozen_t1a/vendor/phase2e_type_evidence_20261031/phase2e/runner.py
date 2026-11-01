"""Sealed development evaluator; original Exact generator and JSON RPC boundary."""
import hashlib
import json
import math
import multiprocessing as mp
import time
import os
import secrets
import sys
from pathlib import Path
from .bootstrap import ROOT
from .policy import worker
from .strategies import POLICIES
from phase2d.runner import evaluate_job,jobs as previous_jobs
from qrelbench.rpc import send
from qrelbench.security import protect_evaluator

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frozen_paths():
    paths=list((ROOT/'phase2e').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+[ROOT/'config.json',ROOT/'DEVELOPMENT_PROTOCOL.md',ROOT/'SOURCE_SNAPSHOT.json',ROOT/'FIXTURE_SNAPSHOT.json']
    for manifest in ['SOURCE_SNAPSHOT.json','FIXTURE_SNAPSHOT.json']:
        data=json.loads((ROOT/manifest).read_text())
        base=ROOT.parents[1] if manifest.startswith('SOURCE') else ROOT/'fixtures/v021'
        for rel,h in data['files'].items():
            p=base/rel
            if digest(p)!=h:raise RuntimeError('Snapshot dependency changed: '+str(p))
            paths.append(p)
    return {str(p.relative_to(ROOT.parents[1])):digest(p) for p in sorted(set(paths))}

def main():
    protect_evaluator();cfg=json.loads((ROOT/'config.json').read_text())
    if (ROOT/'artifacts').exists():raise RuntimeError('Refuse overwrite/retry')
    if cfg['split']!='development' or cfg['master_seed'] is not None or cfg['confirmation_authorized'] or cfg['model_calls_authorized']:raise ValueError('Development only')
    pre=frozen_paths();freeze={'files':pre,'policies':POLICIES,'base_commit':'3186587','time':time.time()}
    (ROOT/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    out=ROOT/'artifacts';out.mkdir();private=out/'private';private.mkdir(mode=0o700)
    seed=secrets.token_hex(32);seedpath=private/'seed.json';seedpath.write_text(json.dumps({'development_seed':seed})+'\n');os.chmod(seedpath,0o600)
    plan=previous_jobs(cfg)
    for j in plan:
        j['index']+=cfg['development_index_start']-410000
        j['scenario']='phase2e_new_development_joint_fusion';j['milestones']=sorted(set(j['milestones']+[64,256]))
    maximum=sum(j['online_cap'] for j in plan)*len(POLICIES)
    if maximum>cfg['limits']['online_actions']:raise RuntimeError('Planned budget exceeded')
    started=time.monotonic();cpu=time.process_time();deadline=started+cfg['limits']['wall_seconds'];context=mp.get_context('spawn')
    counters={'task':0,'type':0,'offline':0};finished=0;status='completed';error=None;current=None;workers={}
    receipt={'planned_trajectories':len(plan)*len(POLICIES),'independent_worlds':len(plan),'maximum_online_actions':maximum,
             'freeze_sha256':digest(ROOT/'freeze.json'),'seed_commitment':digest(seedpath),'model_calls':0,'confirmation_worlds':0,'retries':0,
             'python':sys.version,'stop_mode':'certified','source_snapshot_sha256':digest(ROOT/'SOURCE_SNAPSHOT.json')}
    (out/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
    with (out/'trajectories.jsonl').open('x') as log,(out/'snapshots.jsonl').open('x') as snaps,(private/'reproduction.jsonl').open('x') as repro,(out/'failures.jsonl').open('x') as failed,(private/'partial_reproduction.jsonl').open('x') as partial:
        try:
            for name in POLICIES:
                parent,child=context.Pipe();proc=context.Process(target=worker,args=(child,name));proc.start();child.close();workers[name]=(parent,proc)
            for i,job in enumerate(plan):
                order=POLICIES[i%len(POLICIES):]+POLICIES[:i%len(POLICIES)]
                for name in order:
                    current={'policy':name,'world_index':job['index']};parent,proc=workers[name]
                    if not proc.is_alive():raise RuntimeError('Worker exited')
                    def snapshot(row):snaps.write(json.dumps(row,sort_keys=True)+'\n');snaps.flush()
                    def failure(row,priv):
                        failed.write(json.dumps(row,sort_keys=True)+'\n');failed.flush();partial.write(json.dumps(priv,sort_keys=True)+'\n');partial.flush()
                    final,priv,_=evaluate_job(parent,name,job,seed,deadline,counters,snapshot,failure)
                    log.write(json.dumps(final,sort_keys=True)+'\n');log.flush();repro.write(json.dumps(priv,sort_keys=True)+'\n');repro.flush();finished+=1
                print(json.dumps({'worlds':i+1,'trajectories':finished,'R':job['R'],'online':counters['task']+counters['type'],'seconds':round(time.monotonic()-started,1)}),flush=True)
            for parent,proc in workers.values():
                send(parent,None);proc.join(timeout=5)
                if proc.is_alive() or proc.exitcode!=0:raise RuntimeError('Worker shutdown failed')
        except Exception as exc:
            status='failed';error={'type':type(exc).__name__,'message':str(exc),'current':current}
        finally:
            for parent,proc in workers.values():
                if proc.is_alive():proc.terminate();proc.join(timeout=5)
                parent.close()
    receipt.update(status=status,error=error,finished_trajectories=finished,costs_including_partial=counters,
        seconds=time.monotonic()-started,evaluator_cpu_seconds=time.process_time()-cpu,
        frozen_files_preserved=frozen_paths()==pre)
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
    if status!='completed' or not receipt['frozen_files_preserved']:raise SystemExit(1)
if __name__=='__main__':main()
