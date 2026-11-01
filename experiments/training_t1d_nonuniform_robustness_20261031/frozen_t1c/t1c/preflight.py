"""One fixed literal-observation engineering trace per arm, no worlds."""
import json,time
from .bootstrap import ROOT
from .strategies import construct,POLICIES
from phase2a.coefficients import warmup_lp

def main():
 warmup_lp();public={'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],
  'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8,.8]}
 cal={'high':[1,1,1,0]*12,'low':[1,0]*24};rows=json.loads((ROOT/'PREFLIGHT.json').read_text())['rows'] if (ROOT/'PREFLIGHT.json').exists() else []
 for name in POLICIES:
  if any(row['policy']==name for row in rows):continue
  o=construct(name,public,cal,16,64);start=time.process_time();wall=time.monotonic()
  for t in range(64):
   a=o.next(set(range(4)));y=int((t*13+a[1]*7+t//3)%5<3)
   o.observe(a,{'answer':y} if a[0]=='query' else {'format':'AB'[y]})
  rows.append({'policy':name,'cpu':time.process_time()-start,'wall':time.monotonic()-wall,
    'updates':len(o.update_history),'literal_records':64,'component_cpu':dict(o.component_cpu)})
 result={'scope':'engineering literal records, not QRelBench worlds or trained rollouts','tests_passed':9,'worlds':0,
   'model_calls':0,'training_updates':0,'literal_records':sum(r['literal_records'] for r in rows),'rows':rows,'total_cpu':sum(r['cpu'] for r in rows)}
 (ROOT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
