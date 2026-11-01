"""One bounded T3 pilot. Split seeds are generated once, after source sealing."""
import json,multiprocessing as mp,os,secrets,time
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from .bootstrap import ROOT
from .policy import worker
from .evaluator import evaluate
from .roster import jobs
from .integrity import verify,digest
from qrelbench.rpc import send
from qrelbench.security import protect_evaluator

BASELINES=['WorstFact-MI','Fresh-IG-Lite','Belief-Gated','KL-AnalyticReuse','Fused-Info','Rule-Switch','IG-Fact-FixedType']

def run_arm(name,plan,seed,directory,model_path,deadline):
    protect_evaluator();directory.mkdir();context=mp.get_context('spawn');conn,child=context.Pipe()
    proc=context.Process(target=worker,args=(child,name,model_path));proc.start();child.close()
    counters={'task':0,'type':0,'offline':0};cpu=time.process_time();wall=time.monotonic();finished=0;status='completed';error=None
    private=directory/'private';private.mkdir(mode=0o700)
    with (directory/'trajectories.jsonl').open('x') as log,(private/'reproduction.jsonl').open('x') as repro:
        try:
            for j in plan:
                row,priv=evaluate(conn,name,j,seed,deadline,counters)
                log.write(json.dumps(row)+'\n');log.flush();repro.write(json.dumps(priv)+'\n');repro.flush();finished+=1
            send(conn,None);proc.join(timeout=5)
            if proc.is_alive() or proc.exitcode!=0:raise RuntimeError('Worker shutdown failure')
        except Exception as exc:
            status='failed';error={'type':type(exc).__name__,'message':str(exc),'partial':getattr(exc,'partial',None)}
        finally:
            if proc.is_alive():proc.terminate();proc.join(timeout=5)
            conn.close()
    receipt={'name':name,'status':status,'error':error,'completed':finished,'planned':len(plan),'costs':counters,
      'parent_cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-wall,'model_sha256':digest(model_path) if model_path else None}
    (directory/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def batch(split,names,models,cfg,subfolder):
    pre=verify();out=ROOT/'artifacts';target=out/subfolder
    if target.exists():raise RuntimeError('No overwrite or automatic retry')
    target.mkdir();secret=json.loads((out/'private/seeds.json').read_text())[split]
    plan=jobs(split,cfg);start=time.monotonic();cpu=time.process_time();deadline=start+cfg['limits']['stage_wall_seconds']
    receipt={'split':split,'names':names,'jobs_per_arm':len(plan),'source_check':pre,'completed':[],'status':'started'}
    (target/'started.json').write_text(json.dumps(receipt,indent=2)+'\n')
    context=mp.get_context('spawn')
    with ProcessPoolExecutor(max_workers=cfg['parallel_processes'],mp_context=context) as pool:
        pending={pool.submit(run_arm,n,plan,secret,target/n,models.get(n),deadline):n for n in names}
        for f in as_completed(pending):
            r=f.result();receipt['completed'].append(r)
            print(json.dumps({'batch':subfolder,'arm':r['name'],'status':r['status'],'paths':r['completed'],'seconds':round(time.monotonic()-start,1)}),flush=True)
    receipt.update(status='completed' if all(r['status']=='completed' for r in receipt['completed']) else 'failed',
      wall_seconds=time.monotonic()-start,coordinator_cpu_seconds=time.process_time()-cpu,source_check_end=verify())
    (target/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if receipt['status']!='completed':raise RuntimeError('Incomplete batch; preserved and stopped')
    return receipt

def initialize():
    verify();out=ROOT/'artifacts'
    if out.exists():raise RuntimeError('Pilot entropy already exists')
    out.mkdir();private=out/'private';private.mkdir(mode=0o700)
    path=private/'seeds.json';path.write_text(json.dumps({s:secrets.token_hex(32) for s in ['train','development','test']}));os.chmod(path,0o600)
    (out/'started.json').write_text(json.dumps({'seed_commitment':digest(path),'source_manifest_sha256':digest(ROOT/'SOURCE_MANIFEST.json'),
      'confirmation_seeds_opened':False,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'retries':0},indent=2)+'\n')

def rows(folder):
    for p in sorted((ROOT/'artifacts'/folder).glob('*/trajectories.jsonl')):
        with p.open() as f:
            for line in f:yield json.loads(line)
