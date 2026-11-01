"""Fixed mathematical count fixtures, no benchmark world or random seed."""
from fractions import Fraction as F
from pathlib import Path
import sys,time,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase2e.exact import exact_posterior,integral
from phase2e.estimator import posterior,information_scores

def main():
    c=[[[1,2],[2,0]],[[0,1],[1,1]]];g=[[0],[1]];cal={'high':[1,1],'low':[0,1]};r=[[1],[0]];s=[F(4,5)]*2
    results=[]
    for name in ['exact_cold','quadrature_32','conditional_plugin','quadrature_64']:
        times=[]
        for _ in range(10):
            if name=='exact_cold':integral.cache_clear()
            started=time.process_time()
            if name=='exact_cold':out=exact_posterior(c,g,cal,r,s)
            else:out=posterior(c,g,cal,r,[.8]*2,order=64 if name=='quadrature_64' else 32,plugin=name=='conditional_plugin')
            times.append(time.process_time()-started)
        results.append({'method':name,'repeats':10,'fixture':'2_targets_2_groups_12_task_reference_obs_2_type_reports','cpu_seconds_mean':float(np.mean(times)),'cpu_seconds_min':min(times)})
    counts=np.array([[[10,100],[15,40]],[[20,80],[15,35]],[[70,25],[10,50]],[[20,90],[20,40]]]);gg=[[0],[1,2,3]]
    times=[]
    for _ in range(10):
        started=time.process_time();out=posterior(counts,gg,cal,[[0,0],[1,0]],[.8,.8]);scores=information_scores(out,gg,[.8,.8]);times.append(time.process_time()-started)
    results.append({'method':'quadrature_plus_10_action_information','repeats':10,'fixture':'4_targets_2_groups_fixed_counts','cpu_seconds_mean':float(np.mean(times)),'cpu_seconds_min':min(times)})
    dest=ROOT/'artifacts/analysis/compute_probe.json';dest.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
if __name__=='__main__':main()
