import argparse,json,time,multiprocessing as mp,resource
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from .bootstrap import ROOT
from .core import features,ValueNet
from .rollout import action_values
from .audit import label_gate
from .train import fit
from .runner import initialize,batch,rows,BASELINES
from .integrity import verify,digest
from .policy import warm
from t1b.belief import Belief
from qrelbench.security import confine_worker

def label_init():warm();confine_worker()

def label_one(item):
    s,seed,K=item;start=time.process_time()
    b=Belief.from_observation(np.asarray(s['counts']),s['groups'],s['calibration'],s['reports'],s['accuracy'],s['eta'])
    s['features']=features(b,s['groups'],np.asarray(s['counts']),s['reports'],len(s['calibration']['high']),s['t'],s['B'],s['proposals']).tolist()
    s['values']=action_values(b,s['proposals'].values(),s['t'],s['B'],K,np.random.default_rng(seed))
    s['values']['q']={str(k):v for k,v in s['values']['q'].items()}
    s['label_total_cpu_seconds']=time.process_time()-start;return s

def label(split,cfg):
    verify();path=ROOT/f'artifacts/{split}_labels.jsonl'
    if path.exists():raise RuntimeError('No label retries')
    inputs=[]
    for row in rows('collect_'+split):
        for s in row['estimation_history'][-1]['training_states']:
            # Explicit allowlist copied from worker output. No posthoc audited
            # theta_errors, true parameters, reward or episode identifier.
            s={k:s[k] for k in ['t','B','d','groups','counts','reports','calibration','accuracy','eta','proposals']}
            s['world_index']=row['index'];inputs.append(s)
    start=time.monotonic();cpu=time.process_time();count=0;steps=0;label_cpu=0.;all_states=[]
    with path.open('x') as out,ProcessPoolExecutor(max_workers=cfg['parallel_processes'],mp_context=mp.get_context('spawn'),initializer=label_init) as pool:
        tasks=[(s,cfg['label_seed']+(0 if split=='train' else 100000)+i,cfg['rollouts_per_branch']) for i,s in enumerate(inputs)]
        for s in pool.map(label_one,tasks):
            out.write(json.dumps(s)+'\n');out.flush();all_states.append(s);count+=1
            steps+=s['values']['continuation_steps'];label_cpu+=s['label_total_cpu_seconds']
            if count%12==0:print(json.dumps({'label_split':split,'states':count,'steps':steps,'seconds':round(time.monotonic()-start,1)}),flush=True)
    receipt={'split':split,'worlds':len(set(s['world_index'] for s in all_states)),'states':count,'continuation_steps':steps,
      'K_per_first_answer_branch':cfg['rollouts_per_branch'],'label_worker_cpu_seconds':label_cpu,'wall_seconds':time.monotonic()-start,
      'coordinator_cpu_seconds':time.process_time()-cpu,'labels_sha256':digest(path),'source_check':verify()}
    (ROOT/f'artifacts/{split}_label_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if split=='train':
        gate=label_gate(all_states,cfg);(ROOT/'TRAINING_FEASIBILITY_GATE.json').write_text(json.dumps(gate,indent=2)+'\n')
        print(json.dumps(gate),flush=True)

def load_states(split):
    with (ROOT/f'artifacts/{split}_labels.jsonl').open() as f:return [json.loads(x) for x in f]

def training(cfg):
    verify();gate=json.loads((ROOT/'TRAINING_FEASIBILITY_GATE.json').read_text())
    if not gate['pass']:raise RuntimeError('Scientific gate rejected training')
    target=ROOT/'artifacts/models'
    if target.exists():raise RuntimeError('No additional training rounds')
    target.mkdir();train_states=load_states('train');dev_states=load_states('development');attempts=[]
    receipt={'started':True,'feasibility_gate_sha256':digest(ROOT/'TRAINING_FEASIBILITY_GATE.json'),'train_labels_sha256':digest(ROOT/'artifacts/train_labels.jsonl'),
      'dev_labels_sha256':digest(ROOT/'artifacts/development_labels.jsonl'),'attempts':attempts,'test_access':False}
    (ROOT/'TRAINING.json').write_text(json.dumps(receipt,indent=2)+'\n')
    for mode in ['task','type','joint']:
        for seed in cfg['training_seeds']:
            r=fit(train_states,dev_states,mode,seed,target,cfg['network']);attempts.append(r)
            (ROOT/'TRAINING.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps({'training':mode,'seed':seed,'cpu':r['cpu_seconds'],'selected_epoch':r['selected_epoch_by_dev_mse']}),flush=True)
    receipt['completed']=True;receipt['source_check']=verify();(ROOT/'TRAINING.json').write_text(json.dumps(receipt,indent=2)+'\n')

def dev(cfg):
    tr=json.loads((ROOT/'TRAINING.json').read_text());models={}
    for r in tr['attempts']:models[f"Learned-{r['mode'].title()}-{r['seed']}"]=str(ROOT/'artifacts/models'/r['selected_checkpoint'])
    batch('development',BASELINES+list(models),models,cfg,'development_evaluation')
    all_rows=list(rows('development_evaluation'));selection={};scores={}
    for name in BASELINES+list(models):
        a=[r for r in all_rows if r['policy']==name]
        scores[name]={'successes':sum(r['exact'] for r in a),'worlds':len(a),'worker_cpu':sum(r['trajectory_cpu_seconds'] for r in a)}
    for mode in ['Task','Type','Joint']:
        candidates=[n for n in models if n.startswith('Learned-'+mode+'-')]
        winner=min(candidates,key=lambda n:(-scores[n]['successes'],scores[n]['worker_cpu'],int(n.rsplit('-',1)[1])))
        selection[mode]={'name':winner,'model_path':models[winner],'sha256':digest(models[winner])}
    strongest=min(BASELINES,key=lambda n:(-scores[n]['successes'],scores[n]['worker_cpu'],n))
    result={'selection':selection,'scores':scores,'strongest_frozen_reference_by_DEV':strongest,
      'selection_rule':'DEV complete-world recovery, then lower measured worker CPU, then seed/name; no TEST outcomes',
      'test_access_before_selection':False,'source_check':verify()}
    (ROOT/'DEV_SELECTION.json').write_text(json.dumps(result,indent=2)+'\n')

def test(cfg):
    selection=json.loads((ROOT/'DEV_SELECTION.json').read_text());tr=json.loads((ROOT/'TRAINING.json').read_text());models={}
    for mode in ['Task','Type']:
        chosen=selection['selection'][mode];models[chosen['name']]=chosen['model_path']
    for r in tr['attempts']:
        if r['mode']=='joint':models[f"Learned-Joint-{r['seed']}"]=str(ROOT/'artifacts/models'/r['selected_checkpoint'])
    (ROOT/'TEST_OPENING_RECEIPT.json').write_text(json.dumps({'dev_selection_sha256':digest(ROOT/'DEV_SELECTION.json'),
      'model_hashes':{n:digest(p) for n,p in models.items()},'selection_frozen_before_test':True,'independent_confirmation':False},indent=2)+'\n')
    batch('test',BASELINES+list(models),models,cfg,'test_evaluation')

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['initialize','collect','label-train','label-dev','train','dev','test','analyze','seal']);args=p.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text())
    cpu_start=time.process_time();wall_start=time.monotonic();usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    child_start=usage.ru_utime+usage.ru_stime
    def cost_receipt():
        u=resource.getrusage(resource.RUSAGE_CHILDREN)
        d={'stage':args.stage,'wall_seconds':time.monotonic()-wall_start,
          'coordinator_cpu_seconds':time.process_time()-cpu_start,
          'reaped_descendant_cpu_seconds':u.ru_utime+u.ru_stime-child_start,
          'scope':'aggregate CPU after stage entry, includes reaped descendants; excludes initial coordinator import and other sessions'}
        path=ROOT/'artifacts/STAGE_COSTS.jsonl'
        if path.parent.exists() and args.stage not in ('analyze','seal'):
            with path.open('a') as f:f.write(json.dumps(d)+'\n')
    import atexit;atexit.register(cost_receipt)
    if args.stage=='initialize':initialize()
    elif args.stage=='collect':
        for split in ['train','development']:batch(split,['Collect-Worst'],{},cfg,'collect_'+split)
    elif args.stage=='label-train':label('train',cfg)
    elif args.stage=='label-dev':label('development',cfg)
    elif args.stage=='train':training(cfg)
    elif args.stage=='dev':dev(cfg)
    elif args.stage=='test':test(cfg)
    elif args.stage=='analyze':
        from .report import analyze;analyze(cfg)
    elif args.stage=='seal':
        from .report import seal;seal(cfg)

if __name__=='__main__':main()
