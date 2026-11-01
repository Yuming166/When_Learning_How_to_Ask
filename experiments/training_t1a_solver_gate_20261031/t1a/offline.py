"""One bounded stored-state benchmark, plus deterministic numerical fixtures."""
import hashlib,json,time,itertools
import numpy as np
from .bootstrap import ROOT
from .solvers import Model,Solver,old,x_of,load_grid
from .strategies import construct,SOLVER_ARMS

def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def sampler(item,mode,grid):
    obs=item['observation'];obj=construct(mode,obs['public'],obs['calibration'],obs['R'],grid)
    obj.counts=np.asarray(obs['counts'],dtype=np.int64);obj.forced=np.asarray(obs['forced_counts'],dtype=np.int64)
    obj.types=[r[:] for r in obs['types']];obj.t=obs['online'];return obj

def audit(args,fit,ref):
    part,p,q,alpha,s,eta,tol,limit=args;m=Model(*args[:6]);x=x_of(fit,s is not None);values=[]
    for mask,h in old.alternatives(len(part)):values.append(old.inner(part,p,q,alpha,x,mask,h,m.kappa,eta)['value'])
    upper=float(m.cost@x);gap=(upper-ref['lower_bound'])/max(1.,upper)
    reference_x=x_of(ref,s is not None);weights=x/upper;reference_weights=reference_x/ref['K']
    at_reference=x*(ref['K']/upper)
    information_at_reference=min(old.inner(part,p,q,alpha,at_reference,mask,h,m.kappa,eta)['value'] for mask,h in m.alts)
    return {'objective':upper,'teacher_objective':ref['K'],'objective_relative_change':upper/ref['K']-1,
       'objective_gap_to_teacher_lower':gap,'minimum_information_independent_scalar':min(values),
       'maximum_deficit':max(0.,1-min(values)),'deficit_at_teacher_K':max(0.,1-information_at_reference),
       'allocation_l1_group_mass':float(np.abs((weights-reference_weights)*m.cost).sum()),
       'reported_vs_independent_information_error':abs(fit['minimum_information']-min(values)),
       'finite_nonnegative':bool(np.isfinite(x).all() and (x>=0).all()),'own_relative_gap':fit['relative_gap']}

def main():
    out=ROOT/'artifacts';out.mkdir(exist_ok=False);old.warmup_lp();started=time.monotonic()
    manifest=json.loads((ROOT/'INPUT_SNAPSHOT.json').read_text())
    assert all(hashlib.sha256(open(p,'rb').read()).hexdigest()==h for p,h in manifest['files'].items())
    public_states=json.loads((ROOT/'inputs/public_states.json').read_text())
    # Public numerical grid, not generating parameters or evaluation-fitted grid.
    grid_raw=[];grid_start=time.process_time();grid_solves=0
    for part,alpha in itertools.product([[1,3],[4]],[0.,3.]):
        pts=[];xs=[]
        for p,q in itertools.product([.65,.75,.85,.95],[.5,.6,.7,.8,.9]):
            if q>=p:continue
            f=old.solve_allocation(part,p,q,alpha,[.8]*len(part),.05,tolerance=1e-4,max_iterations=200)
            pts.append([p,q]);xs.append(x_of(f).tolist());grid_solves+=1
        grid_raw.append({'partition':part,'alpha':alpha,'type_accuracy':[.8]*len(part),'eta':.05,'points':pts,'xs':xs})
    grid_cpu=time.process_time()-grid_start;dump(out/'grid.json',grid_raw)
    load_start=time.process_time();grid=load_grid(grid_raw);grid_load_cpu=time.process_time()-load_start
    rows=[];first=[]
    with (out/'offline_rows.jsonl').open('x') as log:
        for rep in range(3):
            solvers={mode:Solver(mode,grid) for mode in SOLVER_ARMS}
            for index,item in enumerate(public_states):
                # Fused estimation and expansion are included for every candidate.
                baseline=sampler(item,'Teacher',grid);baseline.solver=solvers['Teacher']
                begin=time.process_time();baseline._update();teacher_cpu=time.process_time()-begin
                estimate=baseline.last_estimate;part=[len(g) for g in baseline.groups]
                args=(part,estimate['p'],estimate['q'],baseline.alpha,baseline.type_accuracy,baseline.eta,baseline.requested_tolerance(baseline.t),200)
                ref={'a':estimate['allocation_a'],'b':estimate['allocation_b'],'c':estimate['allocation_c'],
                     'K':estimate['estimated_K'],'lower_bound':estimate['lower_bound'],'minimum_information':estimate['minimum_information'],
                     'relative_gap':estimate['solver_relative_gap']}
                order=SOLVER_ARMS[index%len(SOLVER_ARMS):]+SOLVER_ARMS[:index%len(SOLVER_ARMS)]
                for mode in order:
                    if mode=='Teacher':obj=baseline;elapsed=teacher_cpu
                    else:
                        obj=sampler(item,mode,grid);obj.solver=solvers[mode];begin=time.process_time();obj._update();elapsed=time.process_time()-begin
                    e=obj.last_estimate;fit={'a':e['allocation_a'],'b':e['allocation_b'],'c':e['allocation_c'],'K':e['estimated_K'],
                      'lower_bound':e['lower_bound'],'minimum_information':e['minimum_information'],'relative_gap':e['solver_relative_gap']}
                    row={'repeat':rep,'state_index':index,'existing_world_index':item['audit']['existing_world_index'],'mode':mode,
                      'full_planning_cpu':elapsed,'weights':obj.weights.tolist(),'planning_input':{'p_hat':args[1],'q_hat':args[2],'alpha':args[3],'partition':part},
                      **audit(args,fit,ref),'cumulative_stats':dict(obj.solver.stats),'cumulative_cpu':dict(obj.solver.cpu)}
                    rows.append(row);log.write(json.dumps(row)+'\n');log.flush()
                if rep==0:first.append({'args':list(args),'fit':ref})
            print(json.dumps({'offline_repeat':rep+1,'seconds':time.monotonic()-started}),flush=True)
    # Edge fixtures: close rates, boundary q=.5, unequal/symmetric groups, no type, heterogeneous s, positive alpha.
    fixtures=[]
    for part,p,q,alpha,s in [([1,3],.5005,.5,0,[.8,.8]),([4],.95,.9,3,[.8]),
      ([2,2],.8,.6,0,[.8,.8]),([1,3],.85,.6,3,[.65,.9]),([1,1],.7,.5,0,None),
      ([4],.85,.6,16,None),([1,3],.85,.6,0,None),([2,2],.95,.5,3,[.8,.8])]:
        args=(part,p,q,alpha,s,.05,1e-4,200);reference=old.solve_allocation(*args)
        m=Model(*args[:6]);random=np.random.default_rng(421)
        # Deterministic engineering vectors, not scientific worlds.
        max_projection_error=0.
        for _ in range(20):
            x=random.uniform(0,20,size=len(m.cost));batch=m.fits(x)[0]
            scalar=np.array([old.inner(part,p,q,alpha,x,mask,h,m.kappa,.05)['value'] for mask,h in m.alts])
            max_projection_error=max(max_projection_error,float(np.max(np.abs(batch-scalar))))
        for mode in SOLVER_ARMS:
            solver=Solver(mode,grid);begin=time.process_time();fit=solver(*args);elapsed=time.process_time()-begin
            fixtures.append({'mode':mode,'input':{'partition':part,'p_hat':p,'q_hat':q,'alpha':alpha,'type_accuracy':s},
              'cpu':elapsed,**audit(args,fit,reference),'projection_absolute_error':max_projection_error,'stats':dict(solver.stats)})
    dump(out/'numerical_fixtures.json',fixtures)
    summary={'states':len(public_states),'historical_worlds':8,'repeats':3,'updates':len(rows),'grid_solves':grid_solves,
      'grid_cpu':grid_cpu,'grid_load_cpu':grid_load_cpu,'fixture_cases':8,'fixture_evaluations':len(fixtures),'seconds':time.monotonic()-started,'arms':{}}
    for mode in SOLVER_ARMS:
        rr=[r for r in rows if r['mode']==mode]
        summary['arms'][mode]={'mean_cpu':float(np.mean([r['full_planning_cpu'] for r in rr])),
          'median_cpu':float(np.median([r['full_planning_cpu'] for r in rr])),
          'max_group_mass_l1':max(r['allocation_l1_group_mass'] for r in rr),
          'max_abs_objective_relative_change':max(abs(r['objective_relative_change']) for r in rr),
          'minimum_information':min(r['minimum_information_independent_scalar'] for r in rr),
          'max_information_disagreement':max(r['reported_vs_independent_information_error'] for r in rr),
          'first_pass_stats':[r['cumulative_stats'] for r in rr if r['repeat']==0][-1]}
    eligible=all(r['finite_nonnegative'] and r['minimum_information_independent_scalar']>=1-1e-7 and -5e-8<=r['own_relative_gap']<=5e-4 for r in rows+fixtures)
    summary['closed_loop_eligible']=eligible;dump(out/'offline_summary.json',summary);print(json.dumps(summary),flush=True)
    if not eligible:raise RuntimeError('Offline numerical gate failed; do not run closed loop')
if __name__=='__main__':main()
