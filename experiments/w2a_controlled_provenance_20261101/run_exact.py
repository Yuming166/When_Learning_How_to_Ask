"""Run only the frozen CPU law/cost grids; writes reproducible numeric outputs."""
import csv
import json
import math
import time
from pathlib import Path

from engine import (BudgetSolver,repeat_risk,fresh_risk,fixed_depth_risk,
                    root_information,confidence_diagnostic,root_count_law,best_static_allocation)

ROOT=Path(__file__).resolve().parent


def dump(name,rows):
    (ROOT/name).write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')


def csvdump(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    proto=json.loads((ROOT/'PROTOCOL.json').read_text())
    grid=proto['law_grid'];laws=[]
    for r in grid['r']:
        for a in grid['a']:
            for n in grid['reads']:
                repeat=repeat_risk(n,r,a);fresh=fresh_risk(n,r,a)
                # Independent count-likelihood sum, not only the closed form.
                p,q=root_count_law(n,r,a)
                brute=0.5*sum(min(x,y) for x,y in zip(p,q))
                assert abs(brute-repeat)<3e-14
                laws.append({'r':r,'a':a,'reads':n,'repeat_one_root_risk':repeat,
                    'copies_one_root_risk':repeat,'fresh_roots_risk':fresh,
                    'fresh_advantage_same_reads':repeat-fresh,
                    'repeat_source_floor':1-r,
                    'root_KL':None if not math.isfinite(root_information(n,r,a)) else root_information(n,r,a),
                    'root_KL_status':'FINITE' if math.isfinite(root_information(n,r,a)) else 'INFINITE',
                    'copy_comparison':'identical stipulated channel, not model measurement'})
    csvdump('law_grid.csv',laws);dump('law_grid.json',laws)
    costs=[];grid=proto['cost_grid'];started=time.monotonic()
    for r in grid['r']:
        for a in grid['a']:
            for c in grid['root_activation_cost']:
                solver=BudgetSolver(r,a,c)
                for budget in grid['budget']:
                    nr=max(0,budget-c);nf=budget//(c+1)
                    rr=repeat_risk(nr,r,a);rf=fresh_risk(nf,r,a)
                    candidates=[{'depth':0,'roots':0,'risk':0.5,'spent':0}]
                    for k in range(1,budget+1):
                        roots=budget//(c+k)
                        if roots:candidates.append({'depth':k,'roots':roots,
                            'risk':fixed_depth_risk(roots,k,r,a),'spent':roots*(c+k)})
                    fixed=min(candidates,key=lambda x:(x['risk'],x['spent'],x['depth']))
                    static=best_static_allocation(budget,c,r,a)
                    result=solver.initial(budget)
                    assert result['risk']<=static['risk']+3e-12
                    assert static['risk']<=min(rr,rf,fixed['risk'])+3e-12
                    costs.append({'r':r,'a':a,'root_cost':c,'read_cost':1,'budget':budget,
                        'repeat_risk':rr,'copies_risk':rr,'repeat_reads':nr,'repeat_spent':c+nr if nr else 0,
                        'fresh_risk':rf,'fresh_roots':nf,'fresh_spent':nf*(c+1),
                        'best_fixed_depth_risk':fixed['risk'],'best_fixed_depth':fixed['depth'],
                        'best_fixed_roots':fixed['roots'],'best_fixed_spent':fixed['spent'],
                        'best_static_risk':static['risk'],'best_static_depths':str(static['depths']),
                        'best_static_candidates':static['candidates'],
                        'DP_risk':result['risk'],'DP_first_action':str(result['first_action']),
                        'DP_states_at_completion':result['states'],
                        'DP_gain_over_best_fixed':fixed['risk']-result['risk'],
                        'DP_gain_over_best_static':static['risk']-result['risk']})
                print(f'completed r={r}, a={a}, c={c}: {len(solver._values)} states; elapsed={time.monotonic()-started:.1f}s',flush=True)
    csvdump('cost_grid.csv',costs);dump('cost_grid.json',costs)
    conf=[confidence_diagnostic(n,0.75,0.8) for n in range(1,16)]
    csvdump('confidence_diagnostic.csv',conf);dump('confidence_diagnostic.json',conf)
    controls=[]
    for r,a in [(0.5,0.8),(0.75,0.5),(1,0.8),(0.75,1),(1,1)]:
        for n in [1,3,5,9,15]:
            controls.append({'r':r,'a':a,'reads':n,'iid_read_repeat_risk':repeat_risk(n,r,a),
                'fresh_risk':fresh_risk(n,r,a),
                'sticky_extractor_repeat_risk':1-(r*a+(1-r)*(1-a)),
                'interpretation':'sticky extraction draws one E per root and reuses it; outside iid-reading assumption'})
    # Interior sticky-extractor negative control at the common central setting.
    for n in [1,3,5,9,15]:
        controls.append({'r':0.75,'a':0.8,'reads':n,'iid_read_repeat_risk':repeat_risk(n,.75,.8),
            'fresh_risk':fresh_risk(n,.75,.8),'sticky_extractor_repeat_risk':0.35,
            'interpretation':'same one-read marginal, different repeat dependence'})
    csvdump('boundary_and_dependency_controls.csv',controls);dump('boundary_and_dependency_controls.json',controls)
    gains=[r for r in costs if r['DP_gain_over_best_fixed']>1e-12]
    summary={'law_configurations':len(laws),'cost_configurations':len(costs),
        'copy_law_max_risk_difference':max(abs(r['repeat_one_root_risk']-r['copies_one_root_risk']) for r in laws),
        'same_reads_interior_fresh_strict_advantages':sum(r['fresh_advantage_same_reads']>1e-12 for r in laws if r['reads']>1 and r['r']<1),
        'cost_grid_repeat_beats_fresh':sum(r['repeat_risk']<r['fresh_risk']-1e-12 for r in costs),
        'cost_grid_fresh_beats_repeat':sum(r['fresh_risk']<r['repeat_risk']-1e-12 for r in costs),
        'DP_strict_improvement_over_best_fixed_configurations':len(gains),
        'max_DP_absolute_gain_over_best_fixed':max(r['DP_gain_over_best_fixed'] for r in costs),
        'max_gain_configuration':max(costs,key=lambda r:r['DP_gain_over_best_fixed']),
        'DP_strict_improvement_over_best_static_configurations':sum(r['DP_gain_over_best_static']>1e-12 for r in costs),
        'max_DP_absolute_gain_over_best_static':max(r['DP_gain_over_best_static'] for r in costs),
        'max_static_gain_configuration':max(costs,key=lambda r:r['DP_gain_over_best_static']),
        'controls':len(controls),'model_calls':0,'natural_error_observations':0,
        'numerical_method':'Exhaustive finite-state/count probability calculations in float64; independently checked small rational cases',
        'not_claimed':'Observed Qwen performance, real Web errors, natural independent-root costs, unknown-channel optimality'}
    dump('EXACT_SUMMARY.json',summary)
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
