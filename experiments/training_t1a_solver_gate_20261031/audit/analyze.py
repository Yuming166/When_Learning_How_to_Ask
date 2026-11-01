"""Post-run analysis only: no worlds, actions or optimizer calls."""
import collections,hashlib,json,math,platform,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def readlines(p):return [json.loads(l) for l in p.read_text().splitlines()]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def mean(a):return float(np.mean(a))
def table(headers,rows):return '| '+' | '.join(map(str,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
def fmt(x,n=3):return f'{x:.{n}f}'

def main():
    run=ROOT/'artifacts/closed_loop';receipt=json.loads((run/'execution.json').read_text())
    if receipt['status']!='completed':raise RuntimeError('Incomplete run; retain failures and report partial status')
    rows=readlines(run/'trajectories.jsonl');offline=json.loads((ROOT/'artifacts/offline_summary.json').read_text())
    fixtures=json.loads((ROOT/'artifacts/numerical_fixtures.json').read_text());stored=readlines(ROOT/'artifacts/offline_rows.jsonl')
    for mode,v in offline['arms'].items():
        rr=[r for r in stored if r['mode']==mode]
        v['maximum_deficit']=max(r['maximum_deficit'] for r in rr)
        v['maximum_deficit_at_teacher_K']=max(r['deficit_at_teacher_K'] for r in rr)
        v['maximum_objective_gap_to_teacher_lower']=max(r['objective_gap_to_teacher_lower'] for r in rr)
    names=['Teacher','ExactCache','QuantizedCache','Interpolation','RadialReuse','AnalyticReuse','WarmStart','Fused-D-RRC-Type']
    grouped={n:sorted([r for r in rows if r['policy']==n],key=lambda r:r['index']) for n in names}
    cells=collections.defaultdict(list)
    for i,r in enumerate(grouped['Teacher']):cells[(tuple(r['partition']),r['alpha'],r['R'])].append(i)
    rng=np.random.default_rng(9917)
    bootstrap=np.concatenate([rng.choice(ii,(20000,len(ii)),replace=True) for key,ii in sorted(cells.items())],axis=1)
    base=grouped['Teacher'];basecost=np.array([r['online'] for r in base]);basecpu=np.array([r['trajectory_cpu_seconds'] for r in base])
    def ci_ratio(numer,denom):return np.quantile(np.asarray(numer)[bootstrap].mean(1)/np.asarray(denom)[bootstrap].mean(1),[.025,.975]).tolist()
    summaries={};paired=[]
    for n,rr in grouped.items():
        assert len(rr)==32 and [r['index'] for r in rr]==[r['index'] for r in base]
        cost=np.array([r['online'] for r in rr]);cpu=np.array([r['trajectory_cpu_seconds'] for r in rr])
        planner=np.array([r['planner_cpu_seconds'] for r in rr]);totals=np.array([sum(r['costs'].values()) for r in rr])
        stats=collections.Counter();components=collections.Counter();support_updates=0
        min_info=float('inf');max_gap=-float('inf');violations=0;estimate_times=[]
        for r,b in zip(rr,base):
            if r['estimation_history']:
                stats.update(r['estimation_history'][-1].get('solver_stats',{}));components.update(r['estimation_history'][-1].get('solver_component_cpu',{}))
                for e in r['estimation_history']:
                    if 'minimum_information' in e:
                        min_info=min(min_info,e['minimum_information']);max_gap=max(max_gap,e['solver_relative_gap'])
                        violations+=int(e['minimum_information']<1-1e-7 or not -5e-8<=e['solver_relative_gap']<=e['effective_numerical_relative_gap'])
                        support_updates+=1
            paired.append({'index':r['index'],'partition':r['partition'],'alpha':r['alpha'],'R':r['R'],'policy':n,
              'online':r['online'],'teacher_online':b['online'],'online_difference':r['online']-b['online'],
              'total_acquisition':sum(r['costs'].values()),'teacher_total_acquisition':sum(b['costs'].values()),
              'trajectory_cpu':r['trajectory_cpu_seconds'],'teacher_trajectory_cpu':b['trajectory_cpu_seconds'],
              'complete':r['complete'],'exact':r['exact'],'type':r['costs']['type'],'offline':r['costs']['offline']})
        estimation=[r['estimation_history'][-1] for r in rr if r['estimation_history']]
        gates=[g for r in rr for g in r['gate_history']]
        startup=rr[0]['isolation']['worker_startup_cpu']
        gridcharge=offline['grid_cpu'] if n=='Interpolation' else 0.
        summaries[n]={'worlds':32,'online_mean':mean(cost),'online_sum':int(cost.sum()),'online_ratio':float(cost.sum()/basecost.sum()),
          'query_ratio_ci95':ci_ratio(cost,basecost),'total_mean':mean(totals),'total_sum':int(totals.sum()),
          'total_acquisition_ratio':float(totals.sum()/sum(sum(r['costs'].values()) for r in base)),
          'type_mean':mean([r['costs']['type'] for r in rr]),'offline_mean':mean([r['costs']['offline'] for r in rr]),
          'trajectory_cpu_sum':float(cpu.sum()),'trajectory_cpu_mean':mean(cpu),'cpu_median':float(np.median(cpu)),
          'cpu_p90':float(np.quantile(cpu,.9)),'cpu_range':[float(min(cpu)),float(max(cpu))],
          'speedup':float(basecpu.sum()/cpu.sum()),'speedup_ci95':ci_ratio(basecpu,cpu),
          'charged_speedup':float((basecpu.sum()+base[0]['isolation']['worker_startup_cpu'])/(cpu.sum()+startup+gridcharge)),
          'planner_cpu_sum':float(planner.sum()),'glr_cpu_sum':sum(r['glr_cpu_seconds'] for r in rr),'gate_cpu_sum':sum(r['gate_cpu_seconds'] for r in rr),
          'other_cpu_sum':float(cpu.sum()-planner.sum()-sum(r['glr_cpu_seconds']+r['gate_cpu_seconds'] for r in rr)),
          'wall_sum':sum(r['trajectory_wall_seconds'] for r in rr),'wall_speedup':sum(r['trajectory_wall_seconds'] for r in base)/sum(r['trajectory_wall_seconds'] for r in rr),
          'wall_speedup_ci95':ci_ratio([r['trajectory_wall_seconds'] for r in base],[r['trajectory_wall_seconds'] for r in rr]),'wall_p90':float(np.quantile([r['trajectory_wall_seconds'] for r in rr],.9)),
          'certified':sum(r['complete'] for r in rr),'exact_scoring':sum(r['exact'] for r in rr),
          'wrong_certified':sum(r['complete'] and not r['exact'] for r in rr),'censored':sum(r['censored'] for r in rr),
          'gate_attempts':len(gates),'gate_undetermined':sum(g.get('status')=='undetermined' for g in gates),
          'gate_rejected':sum(not g['certified'] for g in gates),'solver_calls_stats':dict(stats),'solver_cpu_components':dict(components),
          'p_terminal_mae':mean([abs(e['p_error']) for e in estimation]),'q_terminal_mae':mean([abs(e['q_error']) for e in estimation]),
          'type_terminal_errors':sum(e['type_errors'] for e in estimation),'theta_estimate_terminal_errors':sum(e['theta_errors'] for e in estimation),
          'same_online_count_worlds':sum(r['online']==b['online'] for r,b in zip(rr,base)),
          'same_terminal_counts_worlds':sum(r['counts']==b['counts'] and r['type_answers']==b['type_answers'] for r,b in zip(rr,base)),
          'minimum_logged_information':min_info if support_updates else None,'maximum_logged_gap':max_gap if support_updates else None,
          'solver_diagnostic_violations':violations,'planning_updates':support_updates,'startup_cpu':startup,'grid_precompute_charge':gridcharge}
    primary=summaries['AnalyticReuse'];parentcpu=receipt['evaluator_cpu_seconds']
    # Lower bound: charge the entire shared evaluator CPU only to the candidate, none to Teacher.
    conservative=(summaries['Teacher']['trajectory_cpu_sum'])/(primary['trajectory_cpu_sum']+primary['startup_cpu']+parentcpu)
    candidate=summaries['AnalyticReuse']
    pass_gate=candidate['speedup_ci95'][0]>=2 and candidate['query_ratio_ci95'][1]<=1.05 and candidate['censored']<=summaries['Teacher']['censored'] and candidate['certified']>=31 and candidate['wrong_certified']==0
    decision='GO_NO_TRAINING' if pass_gate else 'REVISE_NO_TRAINING_YET'
    cellrows=[]
    for key,ii in sorted(cells.items()):
        b=[base[i] for i in ii];a=[grouped['AnalyticReuse'][i] for i in ii];w=[grouped['WarmStart'][i] for i in ii]
        cellrows.append({'partition':key[0],'alpha':key[1],'R':key[2],'n':len(ii),
          'teacher_online_mean':mean([r['online'] for r in b]),'primary_online_mean':mean([r['online'] for r in a]),
          'primary_speedup':sum(r['trajectory_cpu_seconds'] for r in b)/sum(r['trajectory_cpu_seconds'] for r in a),
          'warm_online_mean':mean([r['online'] for r in w])})
    summary={'status':'ANALYZED_NOT_CONFIRMATORY','decision':decision,'primary':'AnalyticReuse','targets':{'speedup':2,'query_ratio':1.05},
      'arms':summaries,'cells':cellrows,'whole_shared_evaluator_cpu':parentcpu,'conservative_primary_speedup_charging_all_parent_cpu':conservative,
      'execution':receipt,'unique_shared_offline_observations':sum(r['costs']['offline'] for r in base),
      'bootstrap':{'resamples':20000,'seed':9917,'unit':'paired worlds stratified by eight cells','scope':'exploratory percentile intervals, not uniform noninferiority certification'},
      'new_worlds':32,'trajectories':len(rows),'training_updates':0,'model_calls':0,'confirmation_worlds':0}
    dump(ROOT/'RESULTS.json',summary);dump(ROOT/'PAIRED_COSTS.json',paired)
    dump(ROOT/'OFFLINE_RESULTS.json',offline);dump(ROOT/'NUMERICAL_FIXTURES.json',fixtures)
    # Final reports are rendered separately from the single evaluation.
    print(json.dumps({'decision':decision,'primary':candidate,'conservative_speedup':conservative,'seconds':receipt['seconds']}))
if __name__=='__main__':main()
