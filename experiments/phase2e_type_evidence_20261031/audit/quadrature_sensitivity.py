"""Post-hoc numerical sensitivity on stored prefixes; no actions or new worlds.

All Fused-Info 64/256/terminal prefixes; order128 only for the five largest
order32/64 marginal discrepancies. This diagnoses, and does not tune, the arm.
"""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase2e.estimator import posterior,information_scores

def delta(a,b):return max(float(np.max(np.abs(np.array(a[k])-b[k]))) for k in ['p','q','theta_prob','z_prob'])
def main():
    load=lambda p:[json.loads(l) for l in p.read_text().splitlines()]
    raw=load(ROOT/'artifacts/trajectories.jsonl');snaps=load(ROOT/'artifacts/snapshots.jsonl')
    ref={r['index']:r['calibration'] for r in raw if r['policy']=='Fused-Info'}
    selected=[s for s in snaps if s['policy']=='Fused-Info' and (s['online'] in [64,256] or s['complete'])]
    rows=[];started=time.perf_counter()
    for s in selected:
        groups=[];offset=0
        for n in s['partition']:groups.append(list(range(offset,offset+n)));offset+=n
        args=(s['counts'],groups,ref[s['index']],s['type_answers'],[s['s']]*len(groups),s['eta'])
        a=posterior(*args,order=32);b=posterior(*args,order=64)
        ia=information_scores(a,groups,args[4]);ib=information_scores(b,groups,args[4]);aa,ab=int(np.argmax(ia)),int(np.argmax(ib))
        regret=float(ib[ab]-ib[aa]);rows.append({'world':s['index'],'online':s['online'],'complete':s['complete'],'marginal_max_abs_32_64':delta(a,b),
              'action_32':aa,'action_64':ab,'argmax_same':aa==ab,'log_information_regret_under_64':regret if np.isfinite(regret) else None,
              'scope':'recomputed potential next allocation; at terminal it is NOT an action actually taken'})
    top=sorted(range(len(rows)),key=lambda i:rows[i]['marginal_max_abs_32_64'],reverse=True)[:5]
    for i in top:
        s=selected[i];groups=[];offset=0
        for n in s['partition']:groups.append(list(range(offset,offset+n)));offset+=n
        args=(s['counts'],groups,ref[s['index']],s['type_answers'],[s['s']]*len(groups),s['eta'])
        b=posterior(*args,order=64);c=posterior(*args,order=128)
        rows[i]['marginal_max_abs_64_128']=delta(b,c)
    obj={'post_hoc':True,'prefixes':len(rows),'worlds':len(set(r['world'] for r in rows)),
         'argmax_same':sum(r['argmax_same'] for r in rows),'maximum_marginal_abs_32_64':max(r['marginal_max_abs_32_64'] for r in rows),
         'maximum_log_information_regret_under_64':max(r['log_information_regret_under_64'] for r in rows if r['log_information_regret_under_64'] is not None),
         'top5_maximum_marginal_abs_64_128':max(rows[i]['marginal_max_abs_64_128'] for i in top),
         'seconds':time.perf_counter()-started,'new_observations':0,'method_modified':False,'records':rows}
    (ROOT/'artifacts/analysis/quadrature_sensitivity.json').write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in obj.items() if k!='records'}))
if __name__=='__main__':main()
