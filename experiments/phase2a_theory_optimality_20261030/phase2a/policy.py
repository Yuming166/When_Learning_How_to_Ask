"""Learner-side observable-data sampling and public snapshot telemetry."""
import math
import time
import numpy as np
from . import bootstrap
from qrelbench.policies import Strategy
from qrelbench.rpc import Client,send,receive
from qrelbench.security import confine_worker
from .coefficients import warmup_lp
from .tracking import InformationTracking
from .glr import profile_glr,endpoint_mle

POLICIES=['Round-Robin','Repeat-and-Compare','Explore-Then-Commit','Direct Type Query','Oracle Format','Information Tracking']


def compact(fit):
    return {k:v for k,v in fit.items() if k not in ['profile_log_likelihoods','task_counts','type_counts']}


def run_policy(client,name,job):
    public=client.reset();cal=client.get_calibration();d=public['d'];G=len(public['groups'])
    strategy=InformationTracking(public,cal,job['planning_delta'],job['update_every']) if name=='Information Tracking' else Strategy(name,public)
    groups=[g['targets'] for g in public['groups']]
    oracle=['AB'.index(z) for z in public['oracle_format_types']] if name=='Oracle Format' else None
    online=0;last_fit=None;snapshots=[];glr_seconds=decode_seconds=0.;complete=False
    while online<job['online_cap']:
        action=strategy.next(set(range(d)))
        if action is None:raise RuntimeError('No action before the planned cap')
        result=client.ask_type(action[1]) if action[0]=='type' else client.query(action[1],action[2])
        online+=1;strategy.observe(action,result)
        endpoint=job['protocol']=='fixed_budget' and online in job['snapshot_budgets']
        stopping=job['protocol']=='fixed_confidence' and (online%job['check_every']==0 or online==job['online_cap'])
        if not endpoint and not stopping:continue
        t=time.monotonic()
        args=(strategy.counts,groups,cal,strategy.types,public['type_accuracy'])
        if endpoint:
            last_fit=endpoint_mle(*args,eta=public['rate_domain']['eta'],oracle_types=oracle)
            decode_seconds+=time.monotonic()-t
        else:
            last_fit=profile_glr(*args,delta=job['delta'],eta=public['rate_domain']['eta'],oracle_types=oracle)
            glr_seconds+=time.monotonic()-t
            # Conservative numerical guard; still not an interval certificate.
            complete=last_fit['gap']-last_fit['beta']>1e-8*(1+online+2*len(cal['high']))
        snapshot={'online':online,'fit':compact(last_fit),'counts':strategy.counts.tolist(),
                  'complete':complete,'estimate':getattr(strategy,'last_estimate',None)}
        client._call('snapshot',snapshot=snapshot);snapshots.append(online)
        if complete:break
    if last_fit is None:
        last_fit=endpoint_mle(strategy.counts,groups,cal,strategy.types,public['type_accuracy'],
                              eta=public['rate_domain']['eta'],oracle_types=oracle)
    client.submit(last_fit['theta'])
    return {'online':online,'complete':job['protocol']=='fixed_budget' or complete,
        'fit':compact(last_fit),'snapshots':snapshots,'glr_seconds':glr_seconds,'decode_seconds':decode_seconds,
        'planner_seconds':getattr(strategy,'planner_seconds',0.),'counts':strategy.counts.tolist(),
        'type_answers':strategy.types,'estimation_history':getattr(strategy,'estimates',[]),
        'sampling_scope':'observable-data tracking development variant; original asymptotic proof not independently established for these finite implementation choices'}


def worker(conn,name):
    # Initialize all numerical backends before file confinement, using a public toy LP.
    warmup_lp();isolation=confine_worker()
    while True:
        job=receive(conn)
        if job is None:break
        try:send(conn,{'done':{**run_policy(Client(conn),name,job),'isolation':isolation}})
        except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
    conn.close()
