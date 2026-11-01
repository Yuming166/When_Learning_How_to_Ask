"""External macro-action adapter; interface prototype, NOT used in T1b trials.

Receives only an original observation client. Terminal rewards must come from
an external trusted training evaluator, never from this agent-facing object.
"""
import copy
from t1b.controller import Residual,candidate_indices
from t1b.belief import index,action
from phase2e.interface import validate_exact

class MacroBeliefInterface:
 def __init__(self,client,R,budget):
  self.client=client;pub=client.reset();cal=client.get_calibration();validate_exact(pub,cal)
  self.public={k:copy.deepcopy(pub[k]) for k in ['d','groups','rate_domain','type_accuracy']}
  self.sampler=Residual(self.public,cal,R,'AnalyticReuse',budget);self.prepared=None
 def prepare(self):
  o=self.sampler
  if o.t>=o.budget:raise RuntimeError('Episode ended; no further policy state/action')
  if self.prepared is None:
   # Prepare the shared KL tracker exactly once for the next actual observation.
   base=super(Residual,o).next(set(range(o.d)));b=o.root_belief()
   choices=[index(base,o.d)]*4 if o.last_forced else candidate_indices(b,index(base,o.d),o.d)
   mask=[];seen=set()
   for c in choices:mask.append(c not in seen);seen.add(c)
   summary=b.summary()
   state={'d':o.d,'groups':[list(g) for g in o.groups],'eta':o.eta,'type_accuracy':list(o.type_accuracy),
    'R':o.planning_R,'budget':o.budget,'online':o.t,'remaining_budget':o.budget-o.t,
    'calibration':copy.deepcopy(o.calibration),'task_counts':o.counts.tolist(),'forced_counts':o.forced.tolist(),
    'type_reports':copy.deepcopy(o.types),'p_hat':summary['p'],'q_hat':summary['q'],
    'theta_prob':summary['theta_prob'],'z_prob':summary['z_prob'],
    'joint_MAP_probability':summary['joint_MAP_probability'],'weights_KL':o.weights.tolist(),
    'cumulative_KL':o.cumulative.tolist(),'actual_counts':o._actual_counts().tolist(),
    'next_update':o.next_update,'forced':o.last_forced,'candidate_actions':choices,'legal_macro_mask':mask}
   self.prepared={'state':state,'choices':choices}
  return copy.deepcopy(self.prepared['state'])
 def act(self,macro):
  state=self.prepare()
  if type(macro) is not int or not 0<=macro<4 or not state['legal_macro_mask'][macro]:raise ValueError('Illegal/duplicate macro')
  o=self.sampler;a=action(self.prepared['choices'][macro],o.d);o._pending=a
  result=self.client.ask_type(a[1]) if a[0]=='type' else self.client.query(a[1],a[2])
  o.observe(a,result);self.prepared=None
  return {'observation':copy.deepcopy(result),'physical_action':a,'online_cost':1,'done':o.t==o.budget,'reward':None}
 def finalize(self):
  o=self.sampler
  if o.t!=o.budget:raise RuntimeError('Terminal decoding only after the full budget')
  b=o.root_belief();guess=b.summary()['joint_theta_MAP']
  from phase2d.certified import certify_stop
  gate=certify_stop(o.counts,o.groups,o.calibration,o.types,o.type_accuracy,o.planning_R,o.eta,candidate_theta=guess)
  return {'guess':guess,'strict_certificate':gate,'strict_output':guess if gate['certified'] else None,'reward':None}
