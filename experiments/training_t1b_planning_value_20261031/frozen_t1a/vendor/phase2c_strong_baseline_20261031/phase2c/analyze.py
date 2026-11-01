"""Development-only, all-world paired analysis and evaluator-only diagnostics."""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .runner import jobs
from .policy import POLICIES
from phase2b.analyze import load, identity, cell, confidence_at, resample_mean
from phase2a.coefficients import solve_allocation, oracle_coefficient, fit_ordered, kl


def population_information(task_counts, type_counts, types, partition, p, q, M, eta=.05, s=.8):
    """Minimum population KL; evaluator only. Fractional counts are allowed.

    Exact finite alternative-sign/type reduction, continuous analytic rate fit;
    float64 evaluation. Orientation uses private true types only after sampling.
    """
    n=np.asarray(task_counts,dtype=float);c=np.asarray(type_counts,dtype=float)
    d=sum(partition);G=len(partition)
    if n.shape!=(d,2) or c.shape!=(G,) or np.any(n<0) or np.any(c<0):
        raise ValueError('Invalid population counts')
    membership=[g for g,k in enumerate(partition) for _ in range(k)]
    minimum=math.inf;kappa=kl(s,1-s)
    for mask in range(2**G):
        for j in range(d):
            su,nu,sv,nv=M*p,M,M*q,M
            for i,g in enumerate(membership):
                a,b=n[i,types[g]],n[i,1-types[g]]
                sp=(p if i!=j else 1-p)*a;sq=(q if i!=j else 1-q)*b
                if mask>>g&1:sv+=sp;nv+=a;su+=sq;nu+=b
                else:su+=sp;nu+=a;sv+=sq;nv+=b
            u,v=fit_ordered(su,nu,sv,nv,eta)
            value=M*(kl(p,u)+kl(q,v))
            for i,g in enumerate(membership):
                x,y=(v,u) if mask>>g&1 else (u,v)
                if i==j:x,y=1-x,1-y
                value+=n[i,types[g]]*kl(p,x)+n[i,1-types[g]]*kl(q,y)
            value+=sum(c[g]*kappa for g in range(G) if mask>>g&1)
            minimum=min(minimum,value)
    return float(minimum)


def expand_weights(allocation, partition, types):
    d=sum(partition);w=np.zeros(2*d+len(partition));j=0
    for g,k in enumerate(partition):
        for _ in range(k):
            w[2*j+types[g]]=allocation['a'][g]/allocation['K']
            w[2*j+1-types[g]]=allocation['b'][g]/allocation['K'];j+=1
        w[2*d+g]=allocation['c'][g]/allocation['K']
    return w/w.sum()


def information_at_weights(weights, K, alpha, types, partition, p, q, eta=.05, s=.8):
    w=np.asarray(weights,float);d=sum(partition)
    if abs(w.sum()-1)>1e-7:raise ValueError('Weights must sum to1')
    return population_information((K*w[:2*d]).reshape(d,2),K*w[2*d:],types,partition,p,q,alpha,eta,s)


def references(cfg):
    from scipy.optimize import brentq
    result=[]
    for part in cfg['partitions']:
        for alpha in cfg['alphas']:
            args=(part,cfg['p'],cfg['q'],alpha)
            task=solve_allocation(*args);typed=solve_allocation(*args,cfg['type_accuracy'])
            oracle=oracle_coefficient(sum(part),cfg['p'],cfg['q'],alpha)
            uniform=np.zeros(2*sum(part)+len(part));uniform[0:2*sum(part):2]=1/sum(part)
            def ray(K):return information_at_weights(uniform,K,alpha,[0]*len(part),part,cfg['p'],cfg['q'],cfg['eta'],cfg['type_accuracy'])
            high=1.
            while ray(high)<1:high*=2
            uniform_K=brentq(lambda K:ray(K)-1,0,high,xtol=1e-10)
            result.append({'partition':part,'alpha':alpha,'K_task_only':task['K'],'K_task_type':typed['K'],
                'K_oracle':oracle['K'],'K_uniform_true_good_ray':uniform_K,'task_allocation':task,'typed_allocation':typed,
                'premium_regime':'zero' if typed['K']/oracle['K']-1<1e-6 else 'positive',
                'scope':'post-run evaluator population reference, no learner input; ray coefficient is not a proved D-RRC stopping-time theorem'})
    return result


def diagnose(row, private, reference):
    last=row['estimation_history'][-1];hist=row['estimation_history'];d=sum(row['partition'])
    tasks=np.asarray(row['counts']).sum(axis=2);types=np.array(list(map(len,row['type_answers'])))
    actual=np.r_[tasks.reshape(-1),types]/row['online'];weights=np.asarray(last['weights'])
    refweights=expand_weights(reference['typed_allocation'],row['partition'],private['types'])
    kwargs=dict(K=reference['K_task_type'],alpha=row['M']/row['R'],types=private['types'],
                partition=row['partition'],p=row['p'],q=row['q'],eta=row['eta'],s=row['s'])
    info=population_information(tasks,types,private['types'],row['partition'],row['p'],row['q'],row['M'],row['eta'],row['s'])
    last_info=information_at_weights(weights,**kwargs);actual_info=information_at_weights(actual,**kwargs)
    tracking=np.asarray(row['tracking_diagnostics']['actual_minus_target'])
    return {'partition':row['partition'],'alpha':row['alpha'],'R':row['R'],'index':row['index'],'complete':row['complete'],
        'online':row['online'],'online_over_R':row['online']/row['R'],'restricted_ratio_over_K':row['online']/row['R']/reference['K_task_type'],
        'forced_tasks':row['forced_tasks'],'forced_fraction':row['forced_tasks']/row['online'],
        'last_theta_errors':last['theta_errors'],'last_type_errors':last['type_errors'],
        'last_p_error':last['p_error'],'last_q_error':last['q_error'],
        'updates_with_sign_error':sum(e['theta_errors']>0 for e in hist),
        'updates_with_type_error':sum(e['type_errors']>0 for e in hist),'updates':len(hist),
        'last_grid_mesh':last['grid_mesh'],'last_target_l1_to_one_true_optimizer':float(abs(weights-refweights).sum()),
        'empirical_allocation_l1_to_one_true_optimizer':float(abs(actual-refweights).sum()),
        'last_target_population_information_at_K':last_info,'last_target_information_deficit_at_K':max(0.,1-last_info),
        'empirical_population_information_at_K':actual_info,'empirical_information_deficit_at_K':max(0.,1-actual_info),
        'population_min_KL_over_R':info/row['R'],'final_beta_over_R':row['fit']['beta']/row['R'],
        'observed_GLR_minus_population_KL_over_R':(row['fit']['gap']-info)/row['R'],
        'tracking_l1_over_t':float(abs(tracking).sum()/row['online']),
        'tracking_linf':float(abs(tracking).max()),
        'maximum_solver_relative_gap':max(e['solver_relative_gap'] for e in hist),
        'last_solver_relative_gap':last['solver_relative_gap'],
        'minimum_solver_information':min(e['minimum_information'] for e in hist),
        'minimum_requested_tolerance':min(e['requested_tolerance'] for e in hist),
        'numerical_floor_active':any(e['numerical_floor_active'] for e in hist),
        'online_task_cost':row['costs']['task'],'online_type_cost':row['costs']['type'],
        'offline_cost':row['costs']['offline'],'total_acquisition':row['total_acquisition'],
        **{k:row[k] for k in ['trajectory_wall_seconds','trajectory_cpu_seconds','glr_seconds','glr_cpu_seconds','planner_seconds','planner_cpu_seconds']},
        'scope':'true quantities evaluator-only; chosen-reference L1 is not optimizer-set distance; correlated diagnostics are not additive causes'}


def confirmation_plan(rows,cfg):
    """No world generation. Prespecified design plus development-only SD planning."""
    from scipy.stats import nct,t
    c=cfg['future_confirmation_planning'];output=[]
    for label,part in [('positive',c['primary_positive_partition']),('zero',c['primary_zero_partition'])]:
        rr=[r for r in rows if r['partition']==part and r['alpha']==c['primary_alpha'] and r['R']==c['primary_R']]
        a={r['index']:r for r in rr if r['policy']=='Aligned Tracking'};b={r['index']:r for r in rr if r['policy']=='D-RRC'}
        diff=np.array([(a[i]['online']-b[i]['online'])/c['primary_R'] for i in sorted(a)])
        sd=float(diff.std(ddof=1));inflated=c['variance_inflation_sd']*sd
        effect=c['meaningful_difference_over_R'] if label=='positive' else c['equivalence_margin_over_R']
        def power(n):
            if inflated==0:return 1.
            crit=t.ppf(1-c['familywise_alpha']/2,n-1);nc=effect*math.sqrt(n)/inflated
            return float(nct.cdf(-crit,n-1,-nc)) if label=='positive' else float(max(0.,nct.cdf(nc-crit,n-1,0)-nct.cdf(-nc+crit,n-1,0)))
        chosen=next((n for n in range(c['minimum_n_per_configuration'],c['maximum_n_per_configuration']+1) if power(n)>=c['power']),None)
        output.append({'regime':label,'partition':part,'alpha':c['primary_alpha'],'R':c['primary_R'],
            'development_pairs':len(diff),'development_difference_mean':float(diff.mean()),
            'development_paired_sd':sd,'inflated_planning_sd':inflated,'prespecified_effect_or_margin':effect,
            'exact_n_worlds':chosen,'approximate_planning_power':None if chosen is None else power(chosen),
            'censored_development_pairs':sum(a[i]['censored'] or b[i]['censored'] for i in a),
            'scope':'t-model power heuristic, not a finite-sample coverage guarantee; zero SD gives minimum n, no general variance-zero assertion'})
    return {'status':'FROZEN_NOT_EXECUTED','seed':None,'confirmatory_worlds_consumed':0,'configurations':output,
        'design_choices':c,'global_online_action_ceiling':None if any(r['exact_n_worlds'] is None for r in output) else sum(r['exact_n_worlds'] for r in output)*2*c['future_online_cap']}


def main():
    cfg=json.loads((ROOT/'config.json').read_text());run=ROOT/'artifacts/run';receipt=json.loads((run/'execution.json').read_text())
    if receipt['status']!='completed':raise RuntimeError('Preserve partial run; no complete comparison')
    rows=load(run/'trajectories.jsonl');plan=jobs(cfg);expected={(p,j['index']) for j in plan for p in POLICIES}
    if Counter(map(identity,rows))!=Counter(expected):raise RuntimeError('Missing or duplicate trajectories')
    private={(r['policy'],r['job']['index']):r for r in load(run/'private/reproduction.jsonl')}
    if private.keys()!=expected:raise RuntimeError('Private record coverage differs')
    out=ROOT/'artifacts/analysis';out.mkdir(exist_ok=False)
    refs=references(cfg);groups=defaultdict(list);summary=[];paired=[];curves=[];diagnostics=[]
    rng=np.random.default_rng(cfg['bootstrap_analysis_seed'])
    for r in rows:groups[(cell(r),r['policy'])].append(r)
    for (key,policy),rr in sorted(groups.items()):
        part,alpha,R=key;costs=[r['online']/R for r in rr];ref=next(x for x in refs if x['partition']==list(part) and x['alpha']==alpha)
        summary.append({'partition':list(part),'alpha':alpha,'R':R,'policy':policy,'n':len(rr),
            'premium_regime':ref['premium_regime'],'completed':sum(r['complete'] for r in rr),'censored':sum(r['censored'] for r in rr),
            'wrong_certificates':sum(r['complete'] and not r['exact'] for r in rr),
            'mean_restricted_online_over_R':float(np.mean(costs)),'bootstrap_mean_95':resample_mean(costs,rng,cfg['bootstrap_resamples']),
            'costs':{k:sum(r['costs'][k] for r in rr) for k in ['task','type','offline']},
            'mean_total_acquisition_over_R':float(np.mean([r['total_acquisition']/R for r in rr])),
            **{k:float(np.mean([r[k] for r in rr])) for k in ['trajectory_wall_seconds','trajectory_cpu_seconds','glr_seconds','glr_cpu_seconds','planner_seconds','planner_cpu_seconds']}})
        cap=rr[0]['online_cap'];Bs=sorted({min(cap,b) for b in [R,2*R,4*R,8*R,12*R,16*R,24*R,cap]})
        curves.append({'partition':list(part),'alpha':alpha,'R':R,'policy':policy,'curve':[confidence_at(rr,B) for B in Bs]})
    for key in sorted({cell(r) for r in rows}):
        part,alpha,R=key;a={r['index']:r for r in groups[(key,'Aligned Tracking')]}
        for policy in POLICIES[:-1]:
            b={r['index']:r for r in groups[(key,policy)]}
            if a.keys()!=b.keys():raise RuntimeError('Unpaired policy cell')
            diff=[(a[i]['online']-b[i]['online'])/R for i in sorted(a)]
            paired.append({'partition':list(part),'alpha':alpha,'R':R,'baseline':policy,'n_pairs':len(diff),
                'aligned_minus_baseline_over_R':float(np.mean(diff)),'paired_bootstrap_95':resample_mean(diff,rng,cfg['bootstrap_resamples']),
                'paired_differences_over_R':diff,'paired_sd':float(np.std(diff,ddof=1)),
                'aligned_censored':sum(r['censored'] for r in a.values()),'baseline_censored':sum(r['censored'] for r in b.values()),
                'relative_restricted_cost_reduction':1-sum(r['online'] for r in a.values())/sum(r['online'] for r in b.values()),
                'exploratory':True,'multiplicity_adjusted':False})
    for r in rows:
        if r['policy']=='Aligned Tracking':
            ref=next(x for x in refs if x['partition']==r['partition'] and x['alpha']==r['alpha'])
            diagnostics.append(diagnose(r,private[identity(r)],ref))
    totals={k:sum(r['costs'][k] for r in rows) for k in ['task','type','offline']}
    if totals!=receipt['costs_including_partial']:raise RuntimeError('Acquisition accounting differs')
    facts={'trajectories':len(rows),'independent_worlds':len(plan),'cells':len(groups)//len(POLICIES),'per_cell_n':cfg['episodes_per_cell'],
        'costs':totals,'online_actions':totals['task']+totals['type'],'total_acquisition':sum(totals.values()),
        'unique_world_offline_observations':sum(2*j['M'] for j in plan),
        'completed':sum(r['complete'] for r in rows),'censored':sum(r['censored'] for r in rows),
        'wrong_certificates':sum(r['complete'] and not r['exact'] for r in rows),'wall_seconds':receipt['seconds'],
        'evaluator_cpu_seconds':receipt['evaluator_cpu_seconds'],
        **{k:sum(r[k] for r in rows) for k in ['trajectory_cpu_seconds','planner_seconds','glr_seconds','planner_cpu_seconds','glr_cpu_seconds']},
        'new_model_calls':0,'new_confirmation_worlds':0,'main_retries':0,'exact_machine_arithmetic_certificate':False}
    confirm=confirmation_plan(rows,cfg)
    for name,value in [('facts',facts),('summary',summary),('paired',paired),('coefficients',refs),('confidence_curves',curves),('diagnostics',diagnostics),('confirmation_plan',confirm)]:
        (out/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n')
    from .report import plots,write_reports
    plots(summary,refs,diagnostics,out,cfg)
    write_reports(facts,summary,paired,refs,diagnostics,confirm,cfg)
    print(json.dumps(facts,indent=2))


if __name__=='__main__':main()
