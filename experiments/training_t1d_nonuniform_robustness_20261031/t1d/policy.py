"""Fixed-budget worker. Guesses and end-of-budget certificates stay distinct."""
import time
import numpy as np
from . import bootstrap
from .strategies import construct,POLICIES
from t1b.belief import Belief,kernel
from phase2e.interface import validate_exact
from phase2d.certified import certify_stop
from phase2a.coefficients import warmup_lp
from qrelbench.rpc import Client,send,receive
from qrelbench.security import confine_worker

def run_policy(client,name,job):
 wall=time.monotonic();cpu=time.process_time();public=client.reset();cal=client.get_calibration();validate_exact(public,cal)
 d=public['d'];groups=[g['targets'] for g in public['groups']];B=job['online_cap']
 sampler=construct(name,public,cal,job['R'],B)
 for online in range(B):
  a=sampler.next(set(range(d)))
  result=client.ask_type(a[1]) if a[0]=='type' else client.query(a[1],a[2])
  sampler.observe(a,result)
 # Same complete-vector decoder for every allocation policy; no score feedback.
 terminal_start=time.process_time()
 b=Belief.from_observation(sampler.counts,groups,cal,sampler.types,public['type_accuracy'],public['rate_domain']['eta'])
 e={**b.summary(),'online':B,'phase':'common_terminal_joint_MAP_decoder','joint_theta_distribution':b.theta_mass.tolist(),
   'entropy_theta':b.entropy(),'quadrature_order':32,'inference':'frozen_joint_quadrature_approximation',
   'controller_cpu':getattr(sampler,'controller_cpu',0.),'controller_stats':dict(getattr(sampler,'controller_stats',{})),
   'decision_history':getattr(sampler,'decisions',[]),
   'forecast_solver_stats':dict(sampler.forecast_solver.stats) if hasattr(sampler,'forecast_solver') else {},
   'forecast_solver_cpu':{},'update_history':sampler.update_history,'action_history':sampler.action_history,
   'component_cpu':dict(sampler.component_cpu),'rule_counts':dict(sampler.rule_counts),
   'common_t16_features':None,'audit_probe_cpu':0.}
 e['terminal_belief_cpu']=time.process_time()-terminal_start;sampler.estimates.append(e)
 guess=e['joint_theta_MAP'];gate_start=time.monotonic();gate_cpu_start=time.process_time()
 gate=certify_stop(sampler.counts,groups,cal,sampler.types,public['type_accuracy'],job['R'],
                   public['rate_domain']['eta'],candidate_theta=guess)
 gate_seconds=time.monotonic()-gate_start;gate_cpu=time.process_time()-gate_cpu_start
 complete=gate['certified'];fit={'theta':guess,'decoder':'common_joint_theta_MAP_order32','fixed_budget_completed':True}
 client._call('snapshot',snapshot={'online':B,'fit':fit,'counts':sampler.counts.tolist(),'type_answers':sampler.types,
   'forced_counts':sampler.forced.tolist(),'estimate':e,'complete':complete,'strict_certificate':gate,
   'fixed_budget_completed':True,'stop_mode':'fixed_budget_with_terminal_certificate','numeric_margin':None,
   'glr_checks':0,'floating_crossing':None})
 client.submit(guess)
 return {'trajectory_wall_seconds':time.monotonic()-wall,'trajectory_cpu_seconds':time.process_time()-cpu,
  'online':B,'complete':complete,'fit':fit,'counts':sampler.counts.tolist(),'type_answers':sampler.types,
  'forced_counts':sampler.forced.tolist(),'glr_seconds':0.,'glr_cpu_seconds':0.,'glr_checks':0,
  'planner_seconds':sampler.planner_seconds,'planner_cpu_seconds':sampler.planner_cpu_seconds,
  'estimation_history':sampler.estimates,'tracking_diagnostics':sampler.diagnostics(),
  'numeric_margin':None,'strict_certificate':gate,'gate_history':[{'online':B,**gate}],
  'gate_seconds':gate_seconds,'gate_cpu_seconds':gate_cpu,
  'strictly_certified_output':guess if complete else None,'abstained':not complete,
  'sampling_scope':'T1d fixed budget; frozen joint posterior; no training; terminal guesses and certificates distinct'}

def worker(conn,name):
 startup=time.process_time();warmup_lp()
 for groups in [((0,),(1,2,3)),((0,1),(2,3)),((0,1,2,3),),((0,),(1,2)),((0,1,2),)]:kernel(sum(map(len,groups)),groups,(.8,)*len(groups),.05,32)
 startup=time.process_time()-startup;isolation=confine_worker();isolation['worker_startup_cpu']=startup
 while True:
  job=receive(conn)
  if job is None:break
  try:send(conn,{'done':{**run_policy(Client(conn),name,job),'isolation':isolation}})
  except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
 conn.close()
