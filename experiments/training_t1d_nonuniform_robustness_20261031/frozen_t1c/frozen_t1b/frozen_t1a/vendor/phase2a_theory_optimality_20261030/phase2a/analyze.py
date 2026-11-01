"""Descriptive development analysis with full denominators and censoring."""
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .policy import POLICIES
from .coefficients import solve_allocation, oracle_coefficient


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def interval(values):
    """Wilson interval for a single cell of independent episode signs."""
    n=len(values)
    if not n:return [None,None]
    p=float(np.mean(values));z=1.959963984540054;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,center-half),min(1.,center+half)]


def confidence_at(rows,B):
    if not rows or any(B>r['online_cap'] for r in rows):raise ValueError('Budget exceeds observation support')
    done=[r['complete'] and r['online']<=B for r in rows]
    wrong=[v and not r['exact'] for v,r in zip(done,rows)]
    costs=[min(r['online'],B) for r in rows]
    return {'B':B,'n':len(rows),'completed':sum(done),'wrong_certificates':sum(wrong),
        'completion_rate':float(np.mean(done)),'completion_wilson':interval(done),
        'wrong_certificate_fraction_all':float(np.mean(wrong)),
        'mean_min_T_B':float(np.mean(costs)),
        'scope':'all trajectories; restricted mean is not E[T]; arithmetic certification is float64'}


def cell(row):
    return (row['scenario'],tuple(row['partition']),row['alpha'],row['R'],row['p'],row['q'],row['channel'])


def grouped(rows,endpoint=False):
    groups=defaultdict(list)
    for r in rows:groups[(cell(r),r['policy'],r['online'] if endpoint else None)].append(r)
    return groups


def cell_fields(key):
    scenario,part,alpha,R,p,q,channel=key
    return {'scenario':scenario,'partition':list(part),'alpha':alpha,'R':R,'p':p,'q':q,'channel':channel}


def main():
    run=ROOT/'artifacts/run';out=ROOT/'artifacts/analysis';out.mkdir(exist_ok=False)
    execution=json.loads((run/'execution.json').read_text())
    if execution['status']!='completed':raise RuntimeError('Incomplete execution: audit partial run before analysis')
    rows=load_jsonl(run/'trajectories.jsonl');snaps=load_jsonl(run/'snapshots.jsonl')
    fb=[r for r in snaps if r['protocol']=='fixed_budget'];fc=[r for r in rows if r['protocol']=='fixed_confidence']
    if len(rows)!=execution['finished_trajectories'] or len(rows)!=execution['planned_trajectories']:
        raise RuntimeError('Completed execution has missing trajectory records')
    if len(fb)!=execution['planned_budget_snapshots']:raise RuntimeError('Missing fixed-budget endpoints')
    if any(sum(r['costs'][k] for r in rows)!=execution['costs_including_partial'][k] for k in ['task','type','offline']):
        raise RuntimeError('Completed execution cost totals disagree with records')
    budget=[];confidence=[];paired=[];coefficients=[]
    for (key,policy,B),rr in grouped(fb,True).items():
        budget.append({**cell_fields(key),'policy':policy,'B':B,'n':len(rr),'exact_count':sum(r['exact'] for r in rr),
            'exact_rate':float(np.mean([r['exact'] for r in rr])),
            'wilson':interval([r['exact'] for r in rr]),
            'mean_task':float(np.mean([r['costs']['task'] for r in rr])),
            'mean_type':float(np.mean([r['costs']['type'] for r in rr])),
            'offline':rr[0]['costs']['offline'],'mean_total':float(np.mean([r['total_acquisition'] for r in rr]))})
    comparisons=defaultdict(dict)
    for r in fb:comparisons[(cell(r),r['online'])].setdefault(r['policy'],{})[r['index']]=r['exact']
    rng=np.random.default_rng(340129)  # analysis resampling only, never used to generate episodes
    for (key,B),policies in comparisons.items():
        for baseline in POLICIES[:-1]:
            left=policies['Information Tracking'];right=policies[baseline]
            if left.keys()!=right.keys():raise RuntimeError('Unpaired budget cell')
            diff=np.array([int(left[i])-int(right[i]) for i in sorted(left)])
            resampled=np.mean(rng.choice(diff,size=(4000,len(diff)),replace=True),axis=1)
            paired.append({**cell_fields(key),'B':B,'baseline':baseline,'n_pairs':len(diff),
                'tracking_minus_baseline':float(diff.mean()),'episode_bootstrap_95':np.quantile(resampled,[.025,.975]).tolist(),
                'exploratory':True,'multiplicity_adjustment':False})
    cg=grouped(fc)
    for (key,policy,_),rr in cg.items():
        cap=rr[0]['online_cap'];completed=[r['online'] for r in rr if r['complete']]
        curve=[confidence_at(rr,B) for B in sorted(set([16,32,48,64,96,128,192,256,512,1024,cap])) if B<=cap]
        confidence.append({**cell_fields(key),'policy':policy,'n':len(rr),'cap':cap,
            'completed':len(completed),'censored':sum(r['censored'] for r in rr),
            'wrong_certificates':sum(r['complete'] and not r['exact'] for r in rr),
            'completed_costs':completed,'completed_conditional_quantiles':np.quantile(completed,[0,.25,.5,.75,1]).tolist() if completed else None,
            'offline':rr[0]['costs']['offline'],'mean_task':float(np.mean([r['costs']['task'] for r in rr])),
            'mean_type':float(np.mean([r['costs']['type'] for r in rr])),
            'mean_total_acquisition':float(np.mean([sum(r['costs'].values()) for r in rr])),
            'curve':curve})
    # These oracle/reference computations happen exclusively after execution, on
    # evaluator records. They cannot feed the learner or select any query.
    primary_keys=sorted(set(cell(r) for r in fc if r['scenario']=='primary_glr'))
    cache={}
    for key in primary_keys:
        _,part,alpha,R,p,q,_=key
        for action_class,s in [('task_only',None),('task_and_type_s.8',.8)]:
            cachekey=(part,alpha,p,q,action_class)
            if cachekey not in cache:cache[cachekey]=solve_allocation(part,p,q,alpha,s)
            value=cache[cachekey]
            coefficients.append({**cell_fields(key),'action_class':action_class,'K':value['K'],
                'K_lower':value['lower_bound'],'K_upper':value['upper_bound'],'oracle_K':oracle_coefficient(sum(part),p,q,alpha)['K']})
    valid=[r for r in fc if r['model_assumptions_hold']];negative=[r for r in fc if not r['model_assumptions_hold']]
    tracking=[r for r in rows if r['policy']=='Information Tracking']
    estimates=[e for r in tracking for e in r['estimation_history']]
    facts={'trajectories':len(rows),'fixed_budget_trajectories':sum(r['protocol']=='fixed_budget' for r in rows),
        'fixed_budget_snapshots':len(fb),'fixed_confidence_trajectories':len(fc),
        'online_actions':sum(r['online'] for r in rows),'task_actions':sum(r['costs']['task'] for r in rows),
        'type_actions':sum(r['costs']['type'] for r in rows),'offline_observations':sum(r['costs']['offline'] for r in rows),
        'in_model_confidence_n':len(valid),'in_model_completed':sum(r['complete'] for r in valid),
        'in_model_censored':sum(r['censored'] for r in valid),
        'in_model_wrong_certificates':sum(r['complete'] and not r['exact'] for r in valid),
        'out_of_model_confidence_n':len(negative),'out_of_model_completed':sum(r['complete'] for r in negative),
        'out_of_model_censored':sum(r['censored'] for r in negative),
        'out_of_model_wrong_certificates':sum(r['complete'] and not r['exact'] for r in negative),
        'planner_seconds':sum(r['planner_seconds'] for r in rows),
        'endpoint_decode_seconds':sum(r['decode_seconds'] for r in rows),'glr_seconds':sum(r['glr_seconds'] for r in rows),
        'tracking_estimator_updates':len(estimates),'model_calls':0,'new_confirmation_episodes':0,
        'actual_wall_seconds':execution['seconds'],'development_only':True,'asymptotic_convergence_established':False,
        'tracking_original_achievability_proof_verified':False,'rigorous_interval_glr_certification':False}
    for name,value in [('facts',facts),('budget',budget),('confidence',confidence),('paired',paired),('confidence_coefficient_references',coefficients)]:
        (out/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n')
    cols=['scenario','partition','alpha','R','p','q','policy','B','n','exact_count','exact_rate','mean_task','mean_type','offline','mean_total']
    with (out/'budget.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(budget)
    plots(budget,confidence,fc,out)
    report(facts,budget,confidence,tracking,coefficients,out)
    print(json.dumps(facts,indent=2))


def plots(budget,confidence,fc,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    def save(fig,name):
        fig.tight_layout();fig.savefig(out/f'{name}.png',dpi=170);fig.savefig(out/f'{name}.pdf');plt.close(fig)
    parts=[[1,15],[2,14],[4,12],[8,8],[16]]
    colors=dict(zip(POLICIES,['#777777','#e58115','#905bb5','#19a7a0','#228b22','#bd3030']))
    fig,axes=plt.subplots(2,5,figsize=(17,6),sharex=True,sharey=True)
    for ai,alpha in enumerate([0,3]):
        for pi,part in enumerate(parts):
            ax=axes[ai,pi]
            for policy in POLICIES:
                rr=sorted([r for r in budget if r['scenario']=='primary' and r['partition']==part and r['alpha']==alpha and r['policy']==policy],key=lambda r:r['B'])
                ax.plot([r['B'] for r in rr],[r['exact_rate'] for r in rr],'o-',markersize=3,label=policy,color=colors[policy])
            ax.set_title(f'{part}, alpha={alpha}; n=8');ax.set_ylim(0,1.03);ax.set_xlabel('Online queries')
            if pi==0:ax.set_ylabel('Exact recovery')
    axes[0,0].legend(fontsize=6,loc='upper left');save(fig,'budget_curves')
    fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
    for ax,(p,q) in zip(axes,[(.75,.6),(.6,.55)]):
        for policy in POLICIES:
            rr=sorted([r for r in budget if r['scenario']=='rate_coverage' and r['p']==p and r['q']==q and r['policy']==policy],key=lambda r:r['B'])
            ax.plot([r['B'] for r in rr],[r['exact_rate'] for r in rr],'o-',label=policy,color=colors[policy])
        ax.set_title(f'p={p}, q={q}; [8,8], alpha=3; n=4');ax.set_xlabel('Online queries');ax.set_ylim(0,1.03)
    axes[0].set_ylabel('Exact recovery');axes[0].legend(fontsize=6);save(fig,'rate_coverage')
    # Primary GLR each panel aggregates the six (partition, alpha) cells at one R.
    # There are only two independent profile indices reused across these cells.
    fig,axes=plt.subplots(4,3,figsize=(13,12))
    for ri,R in enumerate([4,16,64]):
        for policy in POLICIES:
            rr=[r for r in fc if r['scenario']=='primary_glr' and r['R']==R and r['policy']==policy]
            Bs=[16,32,48,64,96,128,192,256,512,1024,2048];curve=[confidence_at(rr,B) for B in Bs]
            axes[0,ri].plot(Bs,[r['completion_rate'] for r in curve],label=policy,color=colors[policy])
            axes[1,ri].plot(Bs,[r['wrong_certificate_fraction_all'] for r in curve],color=colors[policy])
            axes[2,ri].plot(Bs,[r['mean_min_T_B'] for r in curve],color=colors[policy])
        completed=[[r['online'] for r in fc if r['scenario']=='primary_glr' and r['R']==R and r['policy']==policy and r['complete']] for policy in POLICIES]
        for i,values in enumerate(completed):
            if values:axes[3,ri].plot([i]*len(values),values,'o',color=colors[POLICIES[i]],alpha=.5,markersize=4)
        axes[3,ri].set_xticks(range(len(POLICIES)),['RR','RRC','ETC','Direct','Oracle','Track'],rotation=30)
        axes[0,ri].set_title(f'R={R}; 12 paths, two profile indices')
        for ax in axes[:3,ri]:ax.set_xscale('log',base=2);ax.set_xlabel('Online budget B');ax.grid(alpha=.15)
        axes[0,ri].set_ylim(0,1.03)
    for ai,label in enumerate(['Completed / all paths','Wrong certificates / all paths','Mean min(T,B), censored retained','Costs conditional on completion']):axes[ai,0].set_ylabel(label)
    axes[0,0].legend(fontsize=6);save(fig,'confidence_curves')


def report(facts,budget,confidence,tracking,coefficients,out):
    lines=['# Phase 2a bounded development report','',
        '**Decision: mathematical/numerical implementation GO; empirical asymptotic optimality NOT ESTABLISHED.**',
        '',f"Completed {facts['trajectories']} development trajectories, {facts['online_actions']} online actions, {facts['offline_observations']} offline observations, and zero model calls. No independent confirmation set was generated.",
        '', '## Theoretical coefficients and scope','',
        'See [THEORY_PHASE_MAP.md](THEORY_PHASE_MAP.md). The analytic critical alpha for [8,8] is 2.0431602469. The K solver uses the full joint continuous-rate program, without using the Gamma zero-premium shortcut. Independent SLSQP and full alternative enumeration checks are recorded in audit/COEFFICIENT_REVIEW.md. Float64 optimization bounds are numerical, not interval or rational proofs.',
        '', '## Fixed-budget recovery','',
        'All six samplers use the same full-observation joint profile-MLE terminal decoder. Oracle knows group types only, and must still infer signs and rates. Every type query consumes one online action. Calibration is charged as 2M separately. These decoder and calibration settings differ from v0.1; do not compare historical accuracy percentages directly.',
        '', '|Partition|alpha|n per policy|RR @256|RRC @256|ETC @256|Direct @256|Oracle @256|Tracking @256|',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for part in [[1,15],[2,14],[4,12],[8,8],[16]]:
        for alpha in [0,3]:
            rr=[r for r in budget if r['scenario']=='primary' and r['partition']==part and r['alpha']==alpha and r['B']==256]
            lines.append('|'+str(part)+'|'+str(alpha)+'|8|'+ '|'.join(f"{next(r for r in rr if r['policy']==policy)['exact_count']}/8" for policy in POLICIES)+'|')
    lines+=['','The full seven-budget curves and cell-wise Wilson intervals are in artifacts/analysis/budget.json and budget_curves.pdf. Paired episode bootstrap differences are exploratory (n=8 primary, n=4 rate coverage), with no multiplicity correction. Reused episode indices across partitions/alphas do not create independent profiles. No superiority claim is made.',
        '', '## Confidence stopping and censoring','',
        f"Under the iid model: {facts['in_model_completed']}/{facts['in_model_confidence_n']} completed, {facts['in_model_censored']} censored, {facts['in_model_wrong_certificates']} wrong certifications. Outside the iid model: {facts['out_of_model_completed']}/{facts['out_of_model_confidence_n']} completed, {facts['out_of_model_censored']} censored, {facts['out_of_model_wrong_certificates']} wrong certifications. q=1/2 remains in-model; persistent and label-asymmetric controls do not.",
        '', '|R|Policy|Completed / all|Censored|Wrong certified / all|Mean min(T,2048)|',
        '|---:|---|---:|---:|---:|---:|']
    for R in [4,16,64]:
        for policy in POLICIES:
            rr=[r for r in confidence if r['scenario']=='primary_glr' and r['R']==R and r['policy']==policy]
            n=sum(r['n'] for r in rr);completed=sum(r['completed'] for r in rr);wrong=sum(r['wrong_certificates'] for r in rr)
            mean=sum(r['curve'][-1]['mean_min_T_B']*r['n'] for r in rr)/n
            lines.append(f'|{R}|{policy}|{completed}/{n}|{n-completed}|{wrong}/{n}|{mean:.1f}|')
    lines+=['', 'The primary confidence design has only two independent profile indices, reused across partitions and alpha. Confidence JSON retains every cell and negative control. The plots show completion, cumulative wrong certifications divided by all paths, restricted mean cost, and costs conditional on completion. Censored means are not E[T]. Zero observed errors cannot establish delta-correctness.',
        '', 'The GLR enumerates all discrete alternatives and profiles continuous rates analytically for d<=8. Its mathematical optimization is exact, its arithmetic is float64 with interval_certified=false. A numerical stopping margin does not supply a rigorous rounding certificate. d=16 receives only fixed-budget terminal decoding; no sequential d=16 GLR was run.',
        '', '## Observable tracking and computation','',
        f"Information Tracking made {facts['tracking_estimator_updates']} allocation updates. Planner time: {facts['planner_seconds']:.2f}s; endpoint decoding: {facts['endpoint_decode_seconds']:.2f}s; GLR checks: {facts['glr_seconds']:.2f}s. Total run wall time: {facts['actual_wall_seconds']:.2f}s.",
        '', 'The tracker estimates signs/types/rates using forced observations, offline calibration and actual type-query responses; it receives no true signs, group types, rates, private seed, correctness, or evaluation feedback. Its estimator projection, finite coordinate iterations, 32-action update frequency, fixed solver tolerance and deterministic deficit tracking are a precommitted development variant. The original asymptotic achievability proof has not been verified for this implementation.',
        '', '|Scenario|R|alpha|Mean forced fraction (last update)|Mean sign errors|Mean type errors|Mean abs p error|Mean abs q error|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    tg=defaultdict(list)
    for r in tracking:
        if r['estimation_history']:tg[(r['scenario'],r['R'],r['alpha'])].append(r['estimation_history'][-1])
    for (scenario,R,alpha),ee in sorted(tg.items()):
        means=[np.mean([e['forced_tasks']/max(1,e['online']) for e in ee]),np.mean([e['theta_errors'] for e in ee]),np.mean([e['type_errors'] for e in ee]),np.mean([abs(e['p_error']) for e in ee]),np.mean([abs(e['q_error']) for e in ee])]
        lines.append(f'|{scenario}|{R}|{alpha}|'+ '|'.join(f'{v:.4f}' for v in means)+'|')
    lines+=['','Forced observations are also usable task observations; the forced fraction is an allocation cost, not wasted samples. Error diagnostics remain evaluator-only. Raw update-level errors and CPU costs remain in trajectories.jsonl.',
        '', '## Theory versus observed restricted cost','',
        '|Partition|alpha|R|K (tasks + types)|K_oracle|Tracking mean min(T,B)/R|Tracking completed / all|Oracle mean min(T,B)/R|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in coefficients:
        if c['action_class']!='task_and_type_s.8':continue
        def match(policy):return next(r for r in confidence if r['scenario']=='primary_glr' and r['policy']==policy and r['partition']==c['partition'] and r['alpha']==c['alpha'] and r['R']==c['R'])
        a=match('Information Tracking');b=match('Oracle Format')
        lines.append(f"|{c['partition']}|{c['alpha']}|{c['R']}|{c['K']:.5f}|{c['oracle_K']:.5f}|{a['curve'][-1]['mean_min_T_B']/c['R']:.3f}|{a['completed']}/{a['n']}|{b['curve'][-1]['mean_min_T_B']/c['R']:.3f}|")
    lines+=['','K is an asymptotic ONLINE coefficient. The observed column is restricted cost divided by R; heavy censoring can move it below K and does not contradict the lower bound. Offline total 2M is separately charged. These bounded runs do not establish convergence to K, do not empirically verify the d=16 phase transition, and do not authorize confirmation or natural-language claims.',
        '', 'Source and math reviews use separate same-family Codex agents, not external human or cross-model theorem certification. All previous experimental artifacts are preserved.']
    (ROOT/'PILOT_REPORT.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
