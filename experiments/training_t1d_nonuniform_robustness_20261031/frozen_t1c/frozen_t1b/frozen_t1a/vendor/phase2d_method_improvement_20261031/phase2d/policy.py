"""Four sampling arms; common legacy stopping plus an explicit strict mode."""
import math
import time
from . import bootstrap
from .strategies import construct_sampler
from .certified import certify_stop
from qrelbench.rpc import Client,send,receive
from qrelbench.security import confine_worker
from phase2a.coefficients import warmup_lp
from phase2b.log_glr import log_glr

POLICIES=['Aligned-Full','Aligned-NoType','D-RRC-Type','D-RRC-NoType']


def compact(fit):
    return {k:v for k,v in fit.items() if k not in ['profile_log_likelihoods','task_counts','type_counts']}


def run_policy(client,name,job):
    wall=time.monotonic();cpu=time.process_time()
    public=client.reset();cal=client.get_calibration();d=public['d']
    strategy=construct_sampler(name,public,cal,job['R'])
    groups=[g['targets'] for g in public['groups']]
    mode=job['stop_mode']
    if mode not in ['floating','certified']:raise ValueError('Unknown stopping mode')
    online=checks=0;fit=None;complete=False;gate=None;gate_history=[]
    glr_seconds=glr_cpu_seconds=gate_seconds=gate_cpu_seconds=0.
    milestones=list(job['milestones'])
    while online<job['online_cap']:
        action=strategy.next(set(range(d)))
        if action is None:raise RuntimeError('No action before stopping/cap')
        if name.endswith('NoType') and action[0]=='type':raise RuntimeError('Unavailable type action')
        result=client.ask_type(action[1]) if action[0]=='type' else client.query(action[1],action[2])
        online+=1;strategy.observe(action,result)
        if online%job['check_every'] and online!=job['online_cap']:continue
        started=time.monotonic();cpu_started=time.process_time()
        fit=log_glr(strategy.counts,groups,cal,strategy.types,public['type_accuracy'],job['R'],public['rate_domain']['eta'])
        glr_seconds+=time.monotonic()-started;glr_cpu_seconds+=time.process_time()-cpu_started;checks+=1
        margin=1e-8*(1+math.log1p(online+2*len(cal['high'])))
        floating_crossing=fit['gap']-fit['beta']>margin
        complete=floating_crossing if mode=='floating' else False
        if mode=='certified' and (floating_crossing or online==job['online_cap']):
            started=time.monotonic();cpu_started=time.process_time()
            gate=certify_stop(strategy.counts,groups,cal,strategy.types,public['type_accuracy'],job['R'],
                              public['rate_domain']['eta'],candidate_theta=fit['theta'])
            gate_seconds+=time.monotonic()-started;gate_cpu_seconds+=time.process_time()-cpu_started
            gate_history.append({'online':online,**gate});complete=gate['certified']
        milestone=bool(milestones and online>=milestones[0])
        while milestones and online>=milestones[0]:milestones.pop(0)
        if milestone or complete or online==job['online_cap']:
            client._call('snapshot',snapshot={'online':online,'fit':compact(fit),'counts':strategy.counts.tolist(),
                'type_answers':strategy.types,'estimate':strategy.last_estimate,'complete':complete,
                'numeric_margin':margin,'glr_checks':checks,'strict_certificate':gate,
                'floating_crossing':floating_crossing,'stop_mode':mode})
        if complete:break
    if fit is None:raise RuntimeError('No planned likelihood check')
    # The required benchmark submission is a scoring-only terminal guess. It
    # is NOT exposed as a certified answer when the strict gate abstains.
    client.submit(fit['theta'])
    return {'trajectory_wall_seconds':time.monotonic()-wall,'trajectory_cpu_seconds':time.process_time()-cpu,
        'online':online,'complete':complete,'fit':compact(fit),'glr_seconds':glr_seconds,'glr_cpu_seconds':glr_cpu_seconds,
        'glr_checks':checks,'planner_seconds':strategy.planner_seconds,'planner_cpu_seconds':strategy.planner_cpu_seconds,
        'counts':strategy.counts.tolist(),'type_answers':strategy.types,'forced_counts':strategy.forced.tolist(),
        'estimation_history':strategy.estimates,'tracking_diagnostics':strategy.diagnostics(),
        'sampling_scope':'shared frozen forced-only estimator/grid/exploration/tracking; arm-specific target allocation',
        'numeric_margin':margin,'strict_certificate':gate,'gate_history':gate_history,
        'gate_seconds':gate_seconds,'gate_cpu_seconds':gate_cpu_seconds,
        'strictly_certified_output':fit['theta'] if complete and mode=='certified' else None,
        'abstained':mode=='certified' and not complete}


def worker(conn,name):
    warmup_lp();isolation=confine_worker()
    while True:
        job=receive(conn)
        if job is None:break
        try:send(conn,{'done':{**run_policy(Client(conn),name,job),'isolation':isolation}})
        except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
    conn.close()
