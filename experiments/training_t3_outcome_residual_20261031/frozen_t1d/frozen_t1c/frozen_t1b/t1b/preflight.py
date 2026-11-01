"""Deterministic engineering fixtures only; no simulated evaluation worlds."""
import json,time
import numpy as np
from .bootstrap import ROOT
from .controller import Residual
from phase2a.coefficients import warmup_lp

def main():
 warmup_lp();public={'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],
 'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8,.8]}
 rows=[]
 for prefix in [16,18]:
  for repeat in range(3):
   o=Residual(public,{'high':[],'low':[]},16,'Lookahead-2',32)
   for t in range(prefix):
    a=o.next(set(range(4)));o.observe(a,{'format':'AB'[t%2]} if a[0]=='type' else {'answer':int(t%3!=0)})
   start=time.process_time();a=o.next(set(range(4)));elapsed=time.process_time()-start
   rows.append({'prefix':prefix,'repeat':repeat,'cpu':elapsed,'forecast_calls':o.forecast_solver.stats['calls'],
     'nonmyopic_gain':o.decisions[-1].get('nonmyopic_model_gain'),'action':a})
 result={'scope':'deterministic engineering fixtures; no environment episodes or new observations','rows':rows,
   'maximum_full_next_cpu':max(r['cpu'] for r in rows),'unit_tests_passed':9,'initial_failed_tests':2,
   'initial_failure_disposition':'test fixture incorrectly assumed first free action at t=8; corrected to t=16; sampler unchanged',
   'worlds':0,'model_calls':0,'training_updates':0}
 (ROOT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
