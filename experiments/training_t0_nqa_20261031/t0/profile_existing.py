"""Bounded CPU-only decomposition on existing, public Phase2e prefixes.

No new trajectories, teacher dataset, training, inference model or GPU calls.
Runtime timing wrappers restore originals after each update. Frozen sources
are copied verbatim; their algorithms and outputs are not changed.
"""
import json,time,hashlib
from collections import defaultdict
from unittest.mock import patch
import numpy as np
from .bootstrap import ROOT
from phase2e.strategies import FusedOriginal,FusedInformation
from phase2e import strategies
from phase2b import aligned
from phase2a import coefficients

def load(p):return [json.loads(l) for l in p.read_text().splitlines()]
def group_list(partition):
    out=[];n=0
    for k in partition:out.append(list(range(n,n+k)));n+=k
    return out

def main():
    cfg=json.loads((ROOT/'T0_PROFILE_PLAN.json').read_text())
    manifest=json.loads((ROOT/'INPUT_SNAPSHOT.json').read_text())
    for path,h in manifest['inputs'].items():
        if hashlib.sha256(open(path,'rb').read()).hexdigest()!=h:raise RuntimeError('Input changed: '+path)
    base=ROOT.parent.parent.parent.parent/'When_Learning_How_to_Ask_phase2e/experiments/phase2e_type_evidence_20261031/artifacts'
    # Exact absolute location is recorded in the input snapshot, no private file is read.
    snap_path=next(p for p in manifest['inputs'] if p.endswith('/artifacts/snapshots.jsonl'))
    final_path=next(p for p in manifest['inputs'] if p.endswith('/artifacts/trajectories.jsonl'))
    final=[r for r in load(__import__('pathlib').Path(final_path)) if r['policy']=='Aligned-Full']
    first={}
    for r in final:
        key=(tuple(r['partition']),r['alpha'],r['R'])
        if key not in first or r['index']<first[key]['index']:first[key]=r
    finals={r['index']:r for r in first.values()}
    snapshots=[s for s in load(__import__('pathlib').Path(snap_path)) if s['policy']=='Aligned-Full' and s['index'] in finals and (s['online'] in [64,256] or s['complete'])]
    snapshots.sort(key=lambda s:(s['index'],s['online']))
    if len(snapshots)>cfg['maximum_states']:raise RuntimeError('State cap')
    out=ROOT/'artifacts';out.mkdir(exist_ok=False)
    selected=[]
    for s in snapshots:
        r=finals[s['index']];groups=group_list(s['partition'])
        selected.append({'audit':{'existing_world_index':s['index'],'R':s['R'],'partition':s['partition'],'online':s['online'],'source':'historical Phase2e development; profiling_only_not_future_training'},
          'observation':{'public':{'d':len(s['counts']),'groups':[{'targets':g} for g in groups],
            'rate_domain':{'eta':s['eta'],'levels_unknown':True},'type_accuracy':[s['s']]*len(groups)},
            'R':s['R'],'calibration':r['calibration'],'counts':s['counts'],'forced_counts':s['forced_counts'],'types':s['type_answers'],'online':s['online']}})
    (out/'selected_public_states.json').write_text(json.dumps(selected,indent=2)+'\n')
    coefficients.warmup_lp();started=time.monotonic();rows=[];status='completed';error=None
    original_post=strategies.posterior;original_solve=aligned.solve_allocation;original_lp=coefficients.linprog;original_inner=coefficients.inner
    def sampler(obs,klass=FusedOriginal):
        obj=klass(obs['public'],obs['calibration'],obs['R']);obj.counts=np.asarray(obs['counts'],dtype=np.int64)
        obj.forced=np.asarray(obs['forced_counts'],dtype=np.int64);obj.types=[r[:] for r in obs['types']];obj.t=obs['online'];return obj
    try:
        for index,item in enumerate(selected):
            obs=item['observation']
            for rep in range(cfg['repeats']):
                if time.monotonic()-started>cfg['wall_seconds']:raise TimeoutError('T0 profiling limit')
                obj=sampler(obs);parts=defaultdict(float);calls=defaultdict(int)
                def timed(name,fn):
                    def f(*a,**kw):
                        cpu=time.process_time();wall=time.perf_counter()
                        try:return fn(*a,**kw)
                        finally:parts[name+'_cpu']+=time.process_time()-cpu;parts[name+'_wall']+=time.perf_counter()-wall;calls[name]+=1
                    return f
                wall=time.perf_counter();cpu=time.process_time()
                with patch.object(strategies,'posterior',timed('posterior',original_post)),patch.object(aligned,'solve_allocation',timed('solver',original_solve)),patch.object(coefficients,'linprog',timed('linprog',original_lp)),patch.object(coefficients,'inner',timed('analytic_inner',original_inner)):
                    obj._update()
                total=time.process_time()-cpu;elapsed=time.perf_counter()-wall
                estimate=obj.last_estimate
                key=(tuple(item['audit']['partition']),estimate['p'].hex(),estimate['q'].hex(),obj.alpha.hex(),tuple(obj.type_accuracy),obj.eta.hex(),obj.requested_tolerance(obj.t).hex())
                if rep==0:
                    baseline=sampler(obs);begin=time.process_time();baseline._update();unwrapped=time.process_time()-begin
                    np.testing.assert_allclose(obj.weights,baseline.weights,atol=1e-13,rtol=0)
                    mi=sampler(obs,FusedInformation);begin=time.process_time();mi._update();mi_cpu=time.process_time()-begin
                row={'state_index':index,'audit':item['audit'],'repeat':rep,'teacher_total_cpu':total,'teacher_total_wall':elapsed,
                     **dict(parts),'expand_logging_and_wrapping_cpu':max(0,total-parts['posterior_cpu']-parts['solver_cpu']),
                     'solver_residual_cpu':max(0,parts['solver_cpu']-parts['linprog_cpu']-parts['analytic_inner_cpu']),
                     'calls':dict(calls),'cache_key_sha256':hashlib.sha256(repr(key).encode()).hexdigest(),
                     'unwrapped_update_cpu':unwrapped if rep==0 else None,'fused_info_update_cpu':mi_cpu if rep==0 else None,
                     'instrumented_weights_match':True if rep==0 else None}
                rows.append(row)
                with (out/'profile_rows.jsonl').open('a') as fp:fp.write(json.dumps(row)+'\n')
            print(json.dumps({'profiled_states':index+1,'seconds':round(time.monotonic()-started,2)}),flush=True)
    except Exception as exc:status='failed';error=type(exc).__name__+': '+str(exc)
    def mean(k):return float(np.mean([r[k] for r in rows if r[k] is not None]))
    first_rows=[r for r in rows if r['repeat']==0];keys=[r['cache_key_sha256'] for r in first_rows]
    # Lookup-only upper bound on a repeated identical planning tuple; not a measured deployment hit rate.
    cache={keys[0]:np.zeros(10)};begin=time.process_time()
    for _ in range(10000):unused=cache[keys[0]]
    cache_lookup=(time.process_time()-begin)/10000
    summary={'status':status,'error':error,'states':len(selected),'existing_worlds':len(first),'timed_updates':len(rows),
       'repeats':cfg['repeats'],'seconds':time.monotonic()-started,'mean_cpu':{k:mean(k) for k in ['teacher_total_cpu','posterior_cpu','solver_cpu','linprog_cpu','analytic_inner_cpu','solver_residual_cpu','expand_logging_and_wrapping_cpu','unwrapped_update_cpu','fused_info_update_cpu']},
       'unique_tuple_first_pass_cache_hits':len(keys)-len(set(keys)),'first_pass_tuples':len(keys),'identical_tuple_lookup_cpu':cache_lookup,
       'first_repeat_states_compared_to_unwrapped':len(first_rows),'all_first_repeat_outputs_match_unwrapped':all(r['instrumented_weights_match'] for r in first_rows),
       'scientific_worlds_generated':0,'online_actions':0,'new_calibration_observations':0,'optimizer_updates_for_training':0,'gpu_calls':0,'model_calls':0,
       'scope':'paired stored-state CPU decomposition; not closed-loop policy efficiency or trained-network speed'}
    (out/'profile_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
    if status!='completed':raise SystemExit(1)
if __name__=='__main__':main()
