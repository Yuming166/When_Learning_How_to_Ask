"""Read only frozen public T1b results; never read prior private seeds."""
import json,math,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 snap=json.loads((ROOT/'INPUT_SNAPSHOT.json').read_text());p=next(Path(p) for p in snap['files'] if p.endswith('training_t1b_planning_value_20261031/artifacts/trajectories.jsonl'))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==snap['files'][str(p)]
 rows=[json.loads(l) for l in p.read_text().splitlines()];by={(r['index'],r['budget'],r['policy']):r for r in rows}
 ids=sorted({r['index'] for r in rows});cells={}
 for j,i in enumerate(ids):
  r=by[i,32,'AnalyticReuse'];cells.setdefault((tuple(r['partition']),r['p'],r['alpha']),[]).append(j)
 rng=np.random.default_rng(32017);boot=np.concatenate([rng.choice(v,(20000,len(v)),replace=True) for k,v in sorted(cells.items())],axis=1)
 result={'scope':'historical T1b development, post-hoc audit; not new confirmation','budgets':{},'unit':'96 worlds, repeated budgets not independent'}
 for B in [16,32,64]:
  fresh=np.array([by[i,B,'Fresh-IG']['exact'] for i in ids]);kl=np.array([by[i,B,'AnalyticReuse']['exact'] for i in ids]);diff=fresh.astype(float)-kl
  n=int(np.sum(diff!=0));small=min(int(sum(diff>0)),int(sum(diff<0)))
  exact=1. if n==0 else min(1.,2*sum(math.comb(n,j) for j in range(small+1))/2**n)
  result['budgets'][B]={'fresh_only':int(sum(diff>0)),'kl_only':int(sum(diff<0)),
   'both_success':int(sum(fresh&kl)),'both_failed':int(sum(~fresh&~kl)),
   'difference':float(diff.mean()),'paired_stratified_ci95':np.quantile(diff[boot].mean(1),[.025,.975]).tolist(),
   'exact_discordant_binomial_p_two_sided':exact,'p_scope':'reference McNemar calculation under exchangeable fair discordant signs; heterogeneous-grid weak-null inference not established'}
 result['B32_KL_updates']=[e['online'] for e in by[ids[0],32,'AnalyticReuse']['estimation_history'] if e.get('phase')!='common_terminal_joint_MAP_decoder']
 result['B32_IG_updates']=[e['online'] for e in by[ids[0],32,'Fused-Info']['estimation_history'] if e.get('phase')!='common_terminal_joint_MAP_decoder']
 (ROOT/'HISTORICAL_PAIRED_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
