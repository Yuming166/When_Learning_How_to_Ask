"""Five observable-only samplers share the same continuous joint GLR."""
import math
import time
from . import bootstrap
from qrelbench.policies import Strategy
from qrelbench.rpc import Client,send,receive
from qrelbench.security import confine_worker
from phase2a.coefficients import warmup_lp
from .aligned import TheoryAlignedTracking
from .log_glr import log_glr

POLICIES=['Round-Robin','Repeat-and-Compare','Direct Type Query','Oracle Format','Aligned Tracking']


def compact(fit):
    return {k:v for k,v in fit.items() if k not in ['profile_log_likelihoods','task_counts','type_counts']}


def run_policy(client,name,job):
    public=client.reset();cal=client.get_calibration();d=public['d']
    strategy=TheoryAlignedTracking(public,cal,job['R']) if name=='Aligned Tracking' else Strategy(name,public)
    groups=[g['targets'] for g in public['groups']]
    oracle=['AB'.index(z) for z in public['oracle_format_types']] if name=='Oracle Format' else None
    online=checks=0;fit=None;glr_seconds=glr_cpu_seconds=0.;complete=False;milestones=list(job['milestones'])
    while online<job['online_cap']:
        action=strategy.next(set(range(d)))
        if action is None:raise RuntimeError('No sampling action before cap')
        result=client.ask_type(action[1]) if action[0]=='type' else client.query(action[1],action[2])
        online+=1;strategy.observe(action,result)
        if online%job['check_every']!=0 and online!=job['online_cap']:continue
        started=time.monotonic();cpu_started=time.process_time()
        fit=log_glr(strategy.counts,groups,cal,strategy.types,public['type_accuracy'],job['R'],
                    public['rate_domain']['eta'],oracle)
        glr_seconds+=time.monotonic()-started;glr_cpu_seconds+=time.process_time()-cpu_started;checks+=1
        margin=1e-8*(1+math.log1p(online+2*len(cal['high'])))
        complete=fit['gap']-fit['beta']>margin
        milestone=bool(milestones and online>=milestones[0])
        while milestones and online>=milestones[0]:milestones.pop(0)
        if milestone or complete or online==job['online_cap']:
            client._call('snapshot',snapshot={'online':online,'fit':compact(fit),'counts':strategy.counts.tolist(),
                'type_answers':strategy.types,'estimate':getattr(strategy,'last_estimate',None),
                'complete':complete,'numeric_margin':margin,'glr_checks':checks})
        if complete:break
    if fit is None:raise RuntimeError('No planned likelihood check executed')
    client.submit(fit['theta'])
    return {'online':online,'complete':complete,'fit':compact(fit),'glr_seconds':glr_seconds,
        'glr_checks':checks,'planner_seconds':getattr(strategy,'planner_seconds',0.),
        'glr_cpu_seconds':glr_cpu_seconds,'planner_cpu_seconds':getattr(strategy,'planner_cpu_seconds',0.),
        'counts':strategy.counts.tolist(),'type_answers':strategy.types,
        'forced_counts':strategy.forced.tolist() if hasattr(strategy,'forced') else None,
        'estimation_history':getattr(strategy,'estimates',[]),
        'sampling_scope':('deterministic bounded-discrepancy extension of the forced-only estimator policy; numerical optimization and GLR are not interval-certified' if name=='Aligned Tracking' else 'frozen v0.1 baseline sampler, common Phase2b log-risk continuous GLR'),
        'tracking_diagnostics':strategy.diagnostics() if hasattr(strategy,'diagnostics') else None,
        'numeric_margin':margin}


def worker(conn,name):
    warmup_lp();isolation=confine_worker()
    while True:
        job=receive(conn)
        if job is None:break
        try:send(conn,{'done':{**run_policy(Client(conn),name,job),'isolation':isolation}})
        except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
    conn.close()
