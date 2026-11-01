"""Post-ablation interval checks and bounded replays of EXISTING worlds only."""
import json
import math
import multiprocessing as mp
import time
from decimal import Decimal
import numpy as np
from .bootstrap import ROOT,P2C
from .runner import evaluate_job,digest,frozen_files
from .policy import POLICIES,worker
from .certified import certify_stop
from .integrity import strip_timing
from phase2c.analyze import load,identity
from phase2b.log_glr import log_glr
from qrelbench.rpc import send
from qrelbench.security import protect_evaluator


def groups(partition):
    out=[];j=0
    for k in partition:out.append(list(range(j,j+k)));j+=k
    return out


def enclose_terminal(row):
    result=certify_stop(row['counts'],groups(row['partition']),row['calibration'],
        row['type_answers'],[row['s']]*len(row['partition']),row['R'],row['eta'],row['fit']['theta'])
    return {'policy':row['policy'],'index':row['index'],'R':row['R'],'partition':row['partition'],
        'alpha':row['alpha'],'online':row['online'],'legacy_complete':row['complete'],
        'exact_terminal_guess':row['exact'],'certificate':result}


def replay(original,job,seed,deadline,counters,mode):
    context=mp.get_context('spawn');parent,child=context.Pipe()
    process=context.Process(target=worker,args=(child,original['policy']));process.start();child.close()
    failures=[]
    try:
        detail,_,snapshots=evaluate_job(parent,original['policy'],{**job,'stop_mode':mode},seed,deadline,counters,
            on_failure=lambda row,private:failures.append(row))
        send(parent,None);process.join(timeout=5)
        if process.is_alive() or process.exitcode!=0:raise RuntimeError('Existing replay exit failure')
        return detail,snapshots
    finally:
        if process.is_alive():process.terminate();process.join(timeout=5)
        parent.close()
        if failures:
            with (ROOT/'artifacts/certification/replay_failures.jsonl').open('a') as f:
                for row in failures:f.write(json.dumps(row,sort_keys=True)+'\n')


def main():
    protect_evaluator();cfg=json.loads((ROOT/'config.json').read_text())
    freeze=json.loads((ROOT/'freeze.json').read_text())
    if freeze['files']!=frozen_files():raise RuntimeError('Frozen source drift')
    if json.loads((ROOT/'VALIDATION.json').read_text())['trajectories']!=256:raise RuntimeError('Main validation incomplete')
    if not (ROOT/'artifacts/analysis/facts.json').exists():raise RuntimeError('Analyze ablation before stopping audit')
    out=ROOT/'artifacts/certification';out.mkdir(exist_ok=False)
    started=time.monotonic();cpu=time.process_time()
    rows=load(ROOT/'artifacts/run/trajectories.jsonl')
    old=[r for r in load(P2C/'artifacts/run/trajectories.jsonl') if r['policy']!='Oracle Format' and r['complete']]
    static=[]
    with (out/'terminal_enclosures.jsonl').open('x') as log:
        for label,records in [('phase2c_existing_completed',old),('phase2d_existing_completed',[r for r in rows if r['complete']])]:
            for r in records:
                result={'source':label,**enclose_terminal(r)};static.append(result)
                log.write(json.dumps(result,sort_keys=True)+'\n');log.flush()
    n=1000000000152;R=559615787992.8533
    counts=np.zeros((1,2,2),np.int64);counts[0,0,1]=n
    floating=log_glr(counts,[[0]],{'high':[],'low':[]},[[]],[.8],R,eta=.125)
    guard=1e-8*(1+math.log1p(n))
    strict=certify_stop(counts,[[0]],{'high':[],'low':[]},[[]],[.8],R,.125,floating['theta'])
    counterexample={'counts_successes':n,'R_exact_input_float':R,'floating_gap_minus_beta':floating['gap']-floating['beta'],
        'floating_guard':guard,'floating_accepts':floating['gap']-floating['beta']>guard,'gate':strict}
    if not counterexample['floating_accepts'] or strict['certified'] or strict['status']!='rejected':raise RuntimeError('Historical regression changed')
    (out/'counterexample.json').write_text(json.dumps(counterexample,indent=2)+'\n')
    # Replay only already sampled worlds; the private development seed never
    # enters worker arguments, public jobs, logs, or returned certificates.
    seedfile=ROOT/'artifacts/private/seed.json'
    if digest(seedfile)!=freeze['private_seed_commitment']:raise RuntimeError('Seed commitment drift')
    seed=json.loads(seedfile.read_text())['development_seed']
    private={(r['policy'],r['job']['index']):r for r in load(ROOT/'artifacts/run/private/reproduction.jsonl')}
    snapshots=load(ROOT/'artifacts/run/snapshots.jsonl')
    counters={'task':0,'type':0,'offline':0};replays=[];replay_cpu=0.
    replay_started=time.monotonic();deadline=replay_started+cfg['certified_prototype']['wall_seconds']
    status='completed';error=None;current_selection=None
    try:
        with (out/'existing_replays.jsonl').open('x') as log:
            for mode,Rtarget in [('floating',64),('certified',1024)]:
                for name in POLICIES:
                    original=next(r for r in rows if r['policy']==name and r['R']==Rtarget)
                    job=private[identity(original)]['job']
                    remaining=cfg['certified_prototype']['maximum_existing_replay_online_actions']-counters['task']-counters['type']
                    if remaining<job['online_cap']:raise RuntimeError('Replay hard allowance insufficient')
                    current_selection={'policy':name,'index':original['index'],'R':Rtarget,'mode':mode}
                    current,ss=replay(original,job,seed,deadline,counters,mode)
                    replay_cpu+=current['trajectory_cpu_seconds']
                    original_snaps=[s for s in snapshots if identity(s)==identity(original)]
                    if mode=='floating':
                        if strip_timing(original)!=strip_timing(current) or strip_timing(original_snaps)!=strip_timing(ss):
                            raise RuntimeError('Existing floating replay mismatch')
                    same_cost=original['online']==current['online']
                    same_trace=original['transcript_sha256']==current['transcript_sha256']
                    if mode=='certified' and current['complete']:
                        gate=current['strict_certificate']
                        if not gate['certified'] or Decimal(gate['gap_lower'])<=Decimal(gate['beta_upper']):raise RuntimeError('Nonconservative strict replay stop')
                        if current['strictly_certified_output']!=current['fit']['theta']:raise RuntimeError('Certified output mismatch')
                    if mode=='certified' and not current['complete'] and (not current['abstained'] or current['strictly_certified_output'] is not None):
                        raise RuntimeError('Missing abstention')
                    result={'policy':name,'index':original['index'],'R':Rtarget,'mode':mode,'old_online':original['online'],
                        'online':current['online'],'additional_online':current['online']-original['online'],
                        'same_cost':same_cost,'same_trace_hash':same_trace,'complete':current['complete'],
                        'abstained':current['abstained'],'gate_calls':len(current['gate_history']),
                        'gate_seconds':current['gate_seconds'],'trajectory_cpu_seconds':current['trajectory_cpu_seconds'],
                        'strict_certificate':current['strict_certificate'],'full_replay_record':current}
                    replays.append(result);log.write(json.dumps(result,sort_keys=True)+'\n');log.flush()
    except Exception as exc:
        status='failed';error={'type':type(exc).__name__,'message':str(exc),'selection':current_selection}
    result={'status':status,'error':error,'static_worlds_generated':0,'new_confirmation_worlds':0,'model_calls':0,
        'phase2c_terminals':len(old),'phase2d_terminals':sum(r['complete'] for r in rows),
        'certified':sum(r['certificate']['certified'] for r in static),
        'rejected':sum(r['certificate']['status']=='rejected' for r in static),
        'undetermined':sum(r['certificate']['status']=='undetermined' for r in static),
        'static_gate_seconds':sum(r['certificate']['timings_seconds']['total'] for r in static),
        'historical_float_false_crossing_rejected':True,'existing_replays':replays,'replay_costs':counters,
        'replay_worker_cpu_seconds':replay_cpu,'replay_wall_seconds':time.monotonic()-replay_started,
        'wall_seconds':time.monotonic()-started,'evaluator_cpu_seconds':time.process_time()-cpu,
        'scope':'outward arithmetic under documented Fraction/Decimal and model contracts; capped ablations remain legacy-floating acquisitions; no new scientific or confirmation worlds'}
    (ROOT/'CERTIFICATION_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='existing_replays'},indent=2))
    if status!='completed':raise SystemExit(1)


if __name__=='__main__':main()
