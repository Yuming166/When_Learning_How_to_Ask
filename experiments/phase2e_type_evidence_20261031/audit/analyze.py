"""Post-run analysis only: no acquisition, new seeds, or model calls."""
import json
import math
import sys
import time
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase2e import bootstrap
from phase2e.estimator import posterior,public_estimate
from phase2e.strategies import construct_sampler,POLICIES
from phase2d.certified import certify_stop
from phase2a.coefficients import solve_allocation,oracle_coefficient

def rows(path):return [json.loads(l) for l in path.read_text().splitlines()]
def write(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def cell(r):return (tuple(r['partition']),r['alpha'],r['R'])
def label(c):return f'{list(c[0])}|alpha={c[1]}|R={c[2]}'
def main():
    receipt=json.loads((ROOT/'artifacts/execution.json').read_text());assert receipt['status']=='completed'
    raw=rows(ROOT/'artifacts/trajectories.jsonl');snaps=rows(ROOT/'artifacts/snapshots.jsonl')
    assert len(raw)==receipt['planned_trajectories']==288
    assert len({(r['index'],r['policy']) for r in raw})==len(raw)
    assert not (ROOT/'artifacts/failures.jsonl').read_text()
    out=ROOT/'artifacts/analysis';out.mkdir(exist_ok=False)
    cfg=json.loads((ROOT/'config.json').read_text());rng=np.random.default_rng(cfg['bootstrap_analysis_seed'])
    stats=[];pairs=[];grouped=defaultdict(list);gate_status=defaultdict(int);isolation=[]
    endpoint_gates=[]
    for r in raw:
        assert r['online']==sum(r['costs'][k] for k in ['task','type'])
        assert np.asarray(r['counts']).sum()==r['costs']['task']
        assert sum(map(len,r['type_answers']))==r['costs']['type']
        assert sum(map(len,r['calibration'].values()))==r['costs']['offline']==2*r['M']
        assert r['total_acquisition']==sum(r['costs'].values())
        assert r['stop_mode']=='certified'
        assert r['complete']==(r['strictly_certified_output'] is not None)
        if r['complete']:assert r['strict_certificate']['certified']
        if r['policy'].endswith('NoType'):assert r['costs']['type']==0
        assert r['isolation']['handled_new_file_operations']=='denied'
        gg=[];offset=0
        for k in r['partition']:gg.append(list(range(offset,offset+k)));offset+=k
        check=certify_stop(r['counts'],gg,r['calibration'],r['type_answers'],[r['s']]*len(gg),r['R'],r['eta'],candidate_theta=r['fit']['theta'])
        assert check['certified']==r['complete']
        assert check['total_observations']==r['total_acquisition']
        endpoint_gates.append({'world':r['index'],'policy':r['policy'],'status':check['status'],'precision':check['precision'],'total_observations':check['total_observations']})
        for h in r['gate_history']:gate_status[h['status']]+=1
        grouped[cell(r)].append(r)
    contrasts=[('fusion_original','Aligned-Full','Fused-Original'),
               ('allocation_after_fusion','Fused-Original','Fused-Info'),
               ('fusion_D','D-RRC-Type','Fused-D-RRC-Type'),
               ('new_vs_frozen_Aligned','Aligned-Full','Fused-Info'),
               ('new_vs_same_estimator_D','Fused-D-RRC-Type','Fused-Info'),
               ('task_allocation_without_type','Fused-Original-NoType','Fused-Info-NoType'),
               ('type_access_original','Fused-Original-NoType','Fused-Original'),
               ('type_access_info','Fused-Info-NoType','Fused-Info')]
    for c,rr in sorted(grouped.items()):
        worlds=sorted(set(r['index'] for r in rr));assert len(worlds)==4
        by={(r['index'],r['policy']):r for r in rr};resample=rng.integers(0,4,size=(cfg['bootstrap_resamples'],4))
        for name in POLICIES:
            pp=[by[(i,name)] for i in worlds]
            est=[r['estimation_history'][-1] for r in pp]
            stats.append({'cell':label(c),'partition':list(c[0]),'alpha':c[1],'R':c[2],'policy':name,'n':4,
              **{key:float(np.mean([r[key] for r in pp])) for key in ['online','total_acquisition','trajectory_cpu_seconds','trajectory_wall_seconds','planner_cpu_seconds','planner_seconds','gate_seconds','gate_cpu_seconds','glr_cpu_seconds','glr_seconds']},
              **{key:float(np.mean([r['costs'][key] for r in pp])) for key in ['task','type','offline']},
              'online_over_R':float(np.mean([r['online']/r['R'] for r in pp])),
              'total_over_R':float(np.mean([r['total_acquisition']/r['R'] for r in pp])),
              'complete':sum(r['complete'] for r in pp),'exact':sum(r['exact'] for r in pp),'censored':sum(r['censored'] for r in pp),
              'certified_wrong':sum(r['complete'] and not r['exact'] for r in pp),
              'planning_theta_error_rate':float(np.mean([e['theta_errors']/4 for e in est])),
              'planning_type_error_rate':float(np.mean([e['type_errors']/len(c[0]) for e in est])),
              'planning_p_MAE':float(np.mean([abs(e['p_error']) for e in est])),
              'planning_q_MAE':float(np.mean([abs(e['q_error']) for e in est]))})
        for contrast,before,after in contrasts:
            v=np.array([(by[(i,before)]['online']-by[(i,after)]['online'])/c[2] for i in worlds])
            tv=np.array([(by[(i,before)]['total_acquisition']-by[(i,after)]['total_acquisition'])/c[2] for i in worlds]);assert np.array_equal(v,tv)
            ci=np.percentile(v[resample].mean(axis=1),[2.5,97.5])
            denom=np.mean([by[(i,before)]['online'] for i in worlds]);td=np.mean([by[(i,before)]['total_acquisition'] for i in worlds])
            pairs.append({'cell':label(c),'contrast':contrast,'before':before,'after':after,'worlds':worlds,'n':4,'online_gain_over_R':float(v.mean()),'total_gain_over_R':float(tv.mean()),'paired_vector':v.tolist(),'percentile_95_CI':ci.tolist(),
               'relative_online_reduction':float(v.mean()*c[2]/denom),'relative_total_reduction':float(v.mean()*c[2]/td)})
        vv=[]
        for i in worlds:
            cost=lambda p:by[(i,p)]['online']/c[2]
            vv.append((cost('Fused-Info-NoType')-cost('Fused-Info'))-(cost('Fused-Original-NoType')-cost('Fused-Original')))
        v=np.array(vv);pairs.append({'cell':label(c),'contrast':'type_gain_interaction_info_minus_original','n':4,'paired_vector':vv,'online_gain_over_R':float(v.mean()),'percentile_95_CI':np.percentile(v[resample].mean(axis=1),[2.5,97.5]).tolist()})
    # Private fields are evaluator truth only; never pass seed/records to an estimator.
    truth={}
    for r in rows(ROOT/'artifacts/private/reproduction.jsonl'):truth[r['job']['index']]=(r['truth'],r['types'])
    selected=[s for s in snaps if s['policy']=='Aligned-Full' and (s['online'] in [64,256] or s['complete'] or s['online']==s['online_cap'])]
    diagnostics=[]
    terminal={r['index']:r for r in raw if r['policy']=='Aligned-Full'}
    for s in selected:
        t,z=truth[s['index']];cal=terminal[s['index']]['calibration'];groups=[];offset=0
        for k in s['partition']:groups.append(list(range(offset,offset+k)));offset+=k
        pub={'d':4,'groups':[{'targets':g} for g in groups],'rate_domain':{'eta':s['eta'],'levels_unknown':True},'type_accuracy':[s['s']]*len(groups)}
        frozen=construct_sampler('Aligned-Full',pub,cal,s['R']);frozen.forced=np.array(s['forced_counts']);frozen.t=s['online'];forced=frozen._estimate()
        forced['theta_prob']=list(map(float,forced['theta']));forced['z_prob']=list(map(float,forced['z']))
        allfit=posterior(s['counts'],groups,cal,s['type_answers'],pub['type_accuracy'],s['eta'])
        variants={'forced_only_hard':forced,'joint_32':allfit,
          'masked_type_likelihood':posterior(s['counts'],groups,cal,[[] for _ in groups],pub['type_accuracy'],s['eta']),
          'masked_reference_likelihood':posterior(s['counts'],groups,{'high':[],'low':[]},s['type_answers'],pub['type_accuracy'],s['eta']),
          'conditional_plugin':posterior(s['counts'],groups,cal,s['type_answers'],pub['type_accuracy'],s['eta'],plugin=True)}
        started=time.perf_counter();fine=posterior(s['counts'],groups,cal,s['type_answers'],pub['type_accuracy'],s['eta'],order=64);fine_time=time.perf_counter()-started
        keys=['p','q','theta_prob','z_prob']
        error=max(float(np.max(np.abs(np.asarray(allfit[k])-np.asarray(fine[k])))) for k in keys)
        landmarks=([str(s['online'])] if s['online'] in [64,256] else [])+(['terminal'] if s['complete'] or s['online']==s['online_cap'] else [])
        for mark in landmarks:
            for name,f in variants.items():
                diagnostics.append({'world':s['index'],'cell':label(cell(s)),'landmark':mark,'online':s['online'],'estimator':name,
                    'theta_errors':sum(a!=b for a,b in zip(f['theta'],t)),'type_errors':sum(a!=b for a,b in zip(f['z'],z)),
                    'theta_Brier':float(np.mean((np.asarray(f['theta_prob'])-t)**2)),
                    'type_Brier':float(np.mean((np.asarray(f['z_prob'])-z)**2)),
                    'p_error':f['p']-s['p'],'q_error':f['q']-s['q'],'p_MAE':abs(f['p']-s['p']),'q_MAE':abs(f['q']-s['q']),
                    'quadrature_32_vs_64_max_abs':error,'fine_seconds':fine_time,'estimate':public_estimate(f)})
    diagnostic_summary=[]
    dd=defaultdict(list)
    for r in diagnostics:dd[(r['landmark'],r['estimator'])].append(r)
    for (landmark,est),rr in sorted(dd.items()):
        diagnostic_summary.append({'landmark':landmark,'estimator':est,'worlds_observed':len(rr),'worlds_planned':32,
          **{k:float(np.mean([r[k] for r in rr])) for k in ['theta_Brier','type_Brier','p_MAE','q_MAE','theta_errors','type_errors']},
          'quadrature_max_abs':max(r['quadrature_32_vs_64_max_abs'] for r in rr)})
    coefficients=[]
    for part in cfg['partitions']:
        for alpha in cfg['alphas']:
            known=oracle_coefficient(4,cfg['p'],cfg['q'],alpha,cfg['eta'])['K']
            fitted=solve_allocation(part,cfg['p'],cfg['q'],alpha,cfg['type_accuracy'],cfg['eta'])['K']
            coefficients.append({'partition':part,'alpha':alpha,'K_with_type':fitted,'K_oracle':known,'premium':fitted-known,'scope':'post_run_population_reference_only_not_input_to_policy'})
    aggregates=[]
    for name in POLICIES:
        pp=[r for r in raw if r['policy']==name]
        aggregates.append({'policy':name,'n':len(pp),'online':sum(r['online'] for r in pp),'task':sum(r['costs']['task'] for r in pp),'type':sum(r['costs']['type'] for r in pp),
          'offline':sum(r['costs']['offline'] for r in pp),'total_acquisition':sum(r['total_acquisition'] for r in pp),'complete':sum(r['complete'] for r in pp),'censored':sum(r['censored'] for r in pp),'exact':sum(r['exact'] for r in pp),
          **{k:sum(r[k] for r in pp) for k in ['trajectory_cpu_seconds','trajectory_wall_seconds','planner_cpu_seconds','gate_seconds','glr_cpu_seconds']}})
    timing=[]
    snap_index={(r['index'],r['policy'],r['online']):r for r in snaps}
    for name in POLICIES:
        pp=[r for r in raw if r['policy']==name]
        for landmark in [64,256]:
            spent=[]
            for r in pp:
                tt=min(landmark,r['online']);ss=snap_index[(r['index'],name,tt)]
                spent.append(ss['costs']['type'])
            timing.append({'policy':name,'landmark':landmark,'worlds':len(pp),'type_mean_by_min_T_landmark':float(np.mean(spent)),'type_vector':spent})
    facts={'trajectories':len(raw),'worlds':32,'counters':receipt['costs_including_partial'],'unique_shared_offline':sum(r['costs']['offline'] for r in raw if r['policy']=='Aligned-Full'),
       'complete':sum(r['complete'] for r in raw),'exact':sum(r['exact'] for r in raw),'certified_wrong':sum(r['complete'] and not r['exact'] for r in raw),
       'censored':sum(r['censored'] for r in raw),'gate_status_counts':dict(gate_status),'gate_checks':sum(gate_status.values()),
       'quadrature_max_abs':max(r['quadrature_32_vs_64_max_abs'] for r in diagnostics),'coefficients':coefficients,'aggregates':aggregates,'execution':receipt}
    for name,obj in [('summary',stats),('paired',pairs),('diagnostics',diagnostics),('diagnostic_summary',diagnostic_summary),('facts',facts),('endpoint_reaudit',endpoint_gates),('purchase_timing',timing)]:write(out/f'{name}.json',obj)
    print(json.dumps({'trajectories':len(raw),'complete':facts['complete'],'censored':facts['censored'],'diagnostic_records':len(diagnostics),'quadrature_max_abs':facts['quadrature_max_abs']}))
if __name__=='__main__':main()
