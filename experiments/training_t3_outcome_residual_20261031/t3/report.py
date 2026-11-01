"""Frozen statistics/reporting. TEST never selects weights or baselines."""
import hashlib,json,math,shutil
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .integrity import verify,digest
from .runner import BASELINES
from .roster import jobs
from t1b.controller import forced_index

def write(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n' if not isinstance(value,str) else value)

def paired(a,b,seed=63031):
    by_a={r['index']:r for r in a};by_b={r['index']:r for r in b}
    if set(by_a)!=set(by_b):raise RuntimeError('Unpaired world denominator')
    keys=sorted(by_a);delta=np.array([int(by_a[k]['exact'])-int(by_b[k]['exact']) for k in keys]);rng=np.random.default_rng(seed)
    draws=np.zeros(10000)
    for panel in sorted({by_a[k]['panel'] for k in keys}):
        v=np.array([delta[i] for i,k in enumerate(keys) if by_a[k]['panel']==panel]);draws+=rng.choice(v,(10000,len(v)),replace=True).sum(1)
    draws/=len(keys);alpha=.05/7
    return {'n':len(keys),'a_success':sum(by_a[k]['exact'] for k in keys),'b_success':sum(by_b[k]['exact'] for k in keys),
      'wins':int(np.sum(delta==1)),'losses':int(np.sum(delta==-1)),
      'both':sum(by_a[k]['exact'] and by_b[k]['exact'] for k in keys),'neither':sum(not by_a[k]['exact'] and not by_b[k]['exact'] for k in keys),
      'delta_pp':100*float(delta.mean()),'ci95_pp':(100*np.quantile(draws,[.025,.975])).tolist(),
      'family7_ci_pp':(100*np.quantile(draws,[alpha/2,1-alpha/2])).tolist()}

def read_evaluation(folder):
    data=[];checks=0;cert_reasons=Counter();costs=Counter();cpu=0.;gatecpu=0.;startups=0.;private_count=0
    for p in sorted((ROOT/'artifacts'/folder).glob('*/trajectories.jsonl')):
        with p.open() as public,(p.parent/'private/reproduction.jsonl').open() as private:
            first=True
            for line,pline in zip(public,private,strict=True):
                r=json.loads(line);priv=json.loads(pline);private_count+=1;checks+=1
                if r['index']!=priv['job']['index'] or r['split']!=priv['job']['split']:raise RuntimeError('Private/public mismatch')
                counts=np.zeros_like(r['counts']);reports=[[] for _ in r['partition']];history=[];h=hashlib.sha256();offline=None
                for event in priv['trace_prefix']:
                    h.update(json.dumps(event,sort_keys=True,separators=(',',':')).encode()+b'\n');a=event['action'];arg=event['args'];res=event['result']
                    if a=='query':
                        idx=2*arg['j']+'AB'.index(arg['format']);counts[arg['j'],'AB'.index(arg['format']),res['answer']]+=1;history.append(idx)
                    elif a=='ask_type':
                        g=arg['group'];reports[g].append('AB'.index(res['format']));history.append(2*len(counts)+g)
                    elif a=='get_calibration':offline=sum(map(len,res.values()))
                    checks+=1
                e=r['estimation_history'][-1];ah=e['action_history'];L=2*len(counts)
                if len(history)!=r['budget'] or len(ah)!=len(history):raise RuntimeError('Action denominator')
                for t,(physical,entry) in enumerate(zip(history,ah)):
                    if physical!=entry['action']:raise RuntimeError('Action-history mismatch')
                    forced=forced_index(t,L)
                    if entry['forced']!=(forced is not None) or (forced is not None and physical!=forced):raise RuntimeError('Forced-clock mismatch')
                    checks+=1
                if not np.array_equal(counts,r['counts']) or reports!=r['type_answers']:raise RuntimeError('Final observations mismatch')
                if h.hexdigest()!=r['transcript_sha256'] or h.hexdigest()!=priv['full_trace_sha256']:raise RuntimeError('Transcript digest')
                if offline!=r['costs']['offline'] or offline!=2*r['M']:raise RuntimeError('Offline fees')
                if r['online']!=r['budget'] or r['total_acquisition']!=sum(r['costs'].values()):raise RuntimeError('Cost mismatch')
                truth=priv['truth'];exact=r['fit']['theta']==truth
                if exact!=r['exact']:raise RuntimeError('Reward mismatch')
                gate=r['strict_certificate'];reason=gate.get('reason',gate.get('status','unspecified'));cert_reasons[str(reason)]+=1
                if gate['certified'] and not exact:raise RuntimeError('Wrong certified answer')
                probs=np.array(e['joint_theta_distribution']);ti=sum(int(x)<<(len(truth)-j-1) for j,x in enumerate(truth));target=np.zeros_like(probs);target[ti]=1
                decisions=e.get('decision_history',[]);row={k:r[k] for k in ['index','policy','split','panel','partition','alpha','p','q','budget','exact','online','costs','total_acquisition','complete','trajectory_cpu_seconds','trajectory_wall_seconds','gate_cpu_seconds']}
                row.update(brier=float(np.sum((probs-target)**2)),nll=-math.log(max(probs[ti],1e-300)),
                  theta_errors=e['theta_errors'],type_errors=e['type_errors'],p_abs_error=abs(e['p_error']),q_abs_error=abs(e['q_error']),
                  overrides=sum(d['override'] for d in decisions),free_decisions=len(decisions),component_cpu=e['component_cpu'])
                data.append(row);costs.update(r['costs']);cpu+=r['trajectory_cpu_seconds'];gatecpu+=r['gate_cpu_seconds']
                if first:startups+=r['isolation']['worker_startup_cpu'];first=False
                checks+=7
    return data,{'paths':len(data),'private_paths_audited':private_count,'integrity_checks':checks,'passed':True,
      'costs':dict(costs),'worker_cpu':cpu,'terminal_gate_cpu':gatecpu,'worker_startup_cpu_once_per_arm':startups,
      'certificates':sum(r['complete'] for r in data),'wrong_certificates':0,'gate_reasons':dict(cert_reasons)}

def aggregate(records):
    n=len(records);result={'n':n,'success':sum(r['exact'] for r in records)}
    for k in ['online','total_acquisition','brier','nll','theta_errors','type_errors','p_abs_error','q_abs_error','trajectory_cpu_seconds','gate_cpu_seconds']:
        result['mean_'+k]=float(np.mean([r[k] for r in records]));result['sum_'+k]=sum(r[k] for r in records)
    result['mean_type_queries']=float(np.mean([r['costs']['type'] for r in records]));result['mean_task_queries']=float(np.mean([r['costs']['task'] for r in records]));result['mean_offline']=float(np.mean([r['costs']['offline'] for r in records]))
    result['certificates']=sum(r['complete'] for r in records);result['overrides']=sum(r['overrides'] for r in records);result['free_decisions']=sum(r['free_decisions'] for r in records)
    result['override_fraction']=result['overrides']/result['free_decisions'] if result['free_decisions'] else 0
    c=Counter()
    for r in records:c.update(r['component_cpu'])
    result['component_cpu_sums']=dict(c);return result

def estimation_pair(a,b):
    aa={r['index']:r for r in a};bb={r['index']:r for r in b};keys=sorted(aa)
    if set(aa)!=set(bb):raise RuntimeError('Unpaired estimation metric')
    output={}
    for metric in ['brier','nll','p_abs_error','q_abs_error','theta_errors','type_errors']:
        rng=np.random.default_rng(63032);draws=np.zeros(10000);delta=np.array([aa[k][metric]-bb[k][metric] for k in keys])
        for panel in sorted({aa[k]['panel'] for k in keys}):
            x=np.array([delta[i] for i,k in enumerate(keys) if aa[k]['panel']==panel]);draws+=rng.choice(x,(10000,len(x)),replace=True).sum(1)
        draws/=len(keys);output[metric]={'mean_difference':float(delta.mean()),'ci95':np.quantile(draws,[.025,.975]).tolist(),
          'interpretation':'negative favors learned Joint; exploratory secondary metric, no multiplicity claim'}
    return output

def table(rows,columns):
    return '| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+''.join('| '+' | '.join(str(x) for x in r)+' |\n' for r in rows)

def analyze(cfg):
    proof=verify();gate=json.loads((ROOT/'TRAINING_FEASIBILITY_GATE.json').read_text());old=json.loads((ROOT/'HISTORICAL_LEARNABILITY.json').read_text())
    training=json.loads((ROOT/'TRAINING.json').read_text()) if (ROOT/'TRAINING.json').exists() else {'attempts':[]}
    audit={'source_check':proof,'batches':{},'failures':0,'incomplete':0}
    for folder in ['collect_train','collect_development','development_evaluation','test_evaluation']:
        if (ROOT/'artifacts'/folder/'execution.json').exists():
            execution=json.loads((ROOT/'artifacts'/folder/'execution.json').read_text())
            audit['failures']+=sum(r['status']!='completed' for r in execution['completed']);audit['incomplete']+=sum(r['planned']-r['completed'] for r in execution['completed'])
            rec,checks=read_evaluation(folder);audit['batches'][folder]=checks
            if folder=='test_evaluation':test_rows=rec
    cost_path=ROOT/'artifacts/STAGE_COSTS.jsonl';cost_rows=[json.loads(x) for x in cost_path.read_text().splitlines()] if cost_path.exists() else []
    costs={'stages':cost_rows,'aggregate_experiment_cpu_seconds':sum(r['coordinator_cpu_seconds']+r['reaped_descendant_cpu_seconds'] for r in cost_rows),
      'stage_wall_seconds_sum':sum(r['wall_seconds'] for r in cost_rows),'scope':'measured collection, labels, network fitting, DEV/TEST through completion; excludes initial coordinator imports, preparation/reporting and unrelated sessions'}
    for split in ['train','development']:
        p=ROOT/f'artifacts/{split}_label_receipt.json'
        if p.exists():costs[split+'_labels']=json.loads(p.read_text())
    costs['network_fit_cpu_seconds']=sum(r['cpu_seconds'] for r in training['attempts'])
    write('VALIDATION.json',audit);write('COMPUTATIONAL_COST.json',costs)
    learn='# T3 learnability audit\n\n## Material Passport\n\nFrozen historical inputs plus new TRAIN-only posterior simulations; no old private data or confirmation seeds opened.\n\n'
    learn+=f"Historical B32 WorstFact recovered {old['baseline_successes']}/{old['worlds']}; the requested-family **hindsight** oracle recovered {old['candidate_policy_hindsight_oracle']}/{old['worlds']} (headroom {old['candidate_oracle_headroom_pp']:.3f}pp). This is a ceiling for full-policy selection, not a deployable action improvement. All14 frozen policies and T1b's four-macro interface were audited. See HISTORICAL_LEARNABILITY.json for all paired wins/losses and first-free observable associations.\n\n"
    learn+=f"New TRAIN feasibility gate: **{'PASS' if gate['pass'] else 'FAIL'}**. {gate['train_states']} repeated states from48 independent training worlds; candidate disagreement {gate['candidate_disagreement_fraction']:.3f}; mean posterior-rollout Q range {gate['mean_Q_range']:.5f}. Observable correlations: `{json.dumps(gate['observable_associations'])}`. These are exploratory associations with noisy numerical-model labels, not proof of heldout predictability. The weak gate authorizes only the one planned fit. Final learnability is assessed by independent TEST behavior below.\n"
    write('T3_LEARNABILITY_AUDIT.md',learn)
    if not gate['pass'] or 'test_evaluation' not in audit['batches']:
        decision={'overall':'NO-GO_PRETRAINING_GATE' if not gate['pass'] else 'INCOMPLETE_PILOT','training_fits':len(training['attempts']),'automatic_next_stage':False}
        write('T3_FINAL_DECISION.md',f"# T3 final decision\n\n## Material Passport\n\n{decision['overall']}; no effectiveness claim. Gate and execution receipts retained. Training fits: {decision['training_fits']}. No confirmation, additional fitting or Qwen.\n")
        write('T3_ABLATION_RESULTS.md','# T3 ablations\n\n## Material Passport\n\nNot executed after the stopping gate; do not interpret missing results as failures or successes.\n')
        write('T3_CROSS_BUDGET_EVALUATION.md','# T3 cross-budget evaluation\n\n## Material Passport\n\nNot executed after the stopping gate.\n')
        write('T3_COMPUTATIONAL_COST.md',f"# T3 computational cost\n\n## Material Passport\n\nAggregate measured scientific CPU: {costs['aggregate_experiment_cpu_seconds']:.3f}s. Full executed-stage ledger: COMPUTATIONAL_COST.json. Missing stages were not run.\n")
        write('DECISION.json',decision);return
    selection=json.loads((ROOT/'DEV_SELECTION.json').read_text());joint=selection['selection']['Joint']['name'];task=selection['selection']['Task']['name'];typ=selection['selection']['Type']['name']
    names=BASELINES+[task,typ]+[f'Learned-Joint-{s}' for s in cfg['training_seeds']]
    expected=len(jobs('test',cfg))*len(names)
    if len(test_rows)!=expected or audit['failures'] or audit['incomplete']:raise RuntimeError('Full TEST denominator failed')
    grouped={};primary={};pairs={};panels={}
    for B in [16,32,48,64]:
        grouped[str(B)]={n:aggregate([r for r in test_rows if r['budget']==B and r['policy']==n]) for n in names}
    for n in names:primary[n]=[r for r in test_rows if r['budget']==32 and r['policy']==n]
    for n in BASELINES+[task,typ]:pairs[n]=paired(primary[joint],primary[n])
    estimation={n:estimation_pair(primary[joint],primary[n]) for n in BASELINES}
    for panel in ['ID','OOD-rate','OOD-partition','OOD-calibration']:
        panels[panel]={n:paired([r for r in primary[joint] if r['panel']==panel],[r for r in primary[n] if r['panel']==panel]) for n in BASELINES}
    cross={str(B):{n:paired([r for r in test_rows if r['budget']==B and r['policy']==joint],[r for r in test_rows if r['budget']==B and r['policy']==n]) for n in ['WorstFact-MI','IG-Fact-FixedType']} for B in [16,32,48,64]}
    main=grouped['32'];seed_rates=[main[f'Learned-Joint-{s}']['success']/192 for s in cfg['training_seeds']]
    ood_ref=selection['strongest_frozen_reference_by_DEV'];cpu_ratio=main[joint]['mean_trajectory_cpu_seconds']/main['WorstFact-MI']['mean_trajectory_cpu_seconds']
    gates={'at_least_5pp_vs_all_frozen':all(pairs[n]['delta_pp']>=5 for n in BASELINES),
      'positive_family7_paired_lower_vs_all':all(pairs[n]['family7_ci_pp'][0]>0 for n in BASELINES),
      'no_observed_panel_deficit_worse_than_5pp':all(panels[p][n]['delta_pp']>=-5 for p in panels for n in ['WorstFact-MI',ood_ref]),
      'joint_seed_range_at_most_5pp':max(seed_rates)-min(seed_rates)<=.05,
      'no_joint_seed_below_WorstFact':min(seed_rates)>=main['WorstFact-MI']['success']/192,
      'worker_CPU_at_most_2x_WorstFact':cpu_ratio<=2}
    decision={'overall':'GO_DEVELOPMENT_ONLY' if all(gates.values()) else 'NO-GO_FOR_WWW_ENHANCEMENT_THIS_PILOT',
      'gates':gates,'selected_joint':joint,'selected_task':task,'selected_type':typ,'DEV_strongest_reference':ood_ref,
      'training_fits':len(training['attempts']),'statistical_estimation':'see paired joint Brier/NLL and error summaries; no general consistency improvement claim',
      'online_query_cost':'NOT_DEMONSTRATED: equal fixed budgets by design','total_acquisition_cost':'NOT_DEMONSTRATED: equal per-world B+2M by design',
      'worker_cpu_ratio_vs_WorstFact':cpu_ratio,'certified_reliability':'no improvement established by fixed-budget recovery; terminal gate unchanged',
      'automatic_next_stage':False,'independent_confirmation_executed':False,'LLM_calls':0,'GPU_training':False}
    write('RESULTS.json',grouped);write('PAIRED_RESULTS.json',pairs);write('ESTIMATION_PAIRED.json',estimation);write('OOD_RESULTS.json',panels);write('CROSS_BUDGET_RESULTS.json',cross);write('DECISION.json',decision)
    rows_table=[]
    for n in names:
        a=main[n];rows_table.append([n,f"{a['success']}/{a['n']}",f"{100*a['success']/a['n']:.2f}%",f"{a['mean_type_queries']:.2f}",f"{a['mean_brier']:.4f}",f"{a['mean_nll']:.4f}",f"{a['sum_trajectory_cpu_seconds']:.2f}",f"{100*a['override_fraction']:.1f}%"])
    text='# T3 ablation results\n\n## Material Passport\n\nOne bounded development pilot; all192 TEST worlds are independent of TRAIN/DEV and were opened after weight hashes and DEV selection. These are heldout development tests, not independent confirmation.\n\n'
    text+=f"DEV-selected Joint: **{joint}**. DEV-selected strongest frozen comparator: **{ood_ref}**. The other Joint seeds are reported regardless of TEST score.\n\n"
    text+=table(rows_table,['Policy','B32 full recovery','Rate','Mean type','Joint Brier','Joint NLL','Worker CPU(s)','Overrides'])
    text+='\nAll arms have the same paid observation access, posterior approximation, forced clock, joint-MAP decoder, B32 online cost and per-world offline cost. Source routing does not change frozen baseline algorithms. Residual task/type masks hold the alternative task/type action fixed at each observed state; divergent future histories can change future purchase schedules.\n\n'
    text+=table([[n,f"{pairs[n]['delta_pp']:+.2f}",str([round(x,2) for x in pairs[n]['ci95_pp']]),str([round(x,2) for x in pairs[n]['family7_ci_pp']]),pairs[n]['wins'],pairs[n]['losses']] for n in BASELINES],['Selected Joint minus','Delta(pp)','Paired95%','Family7 interval','Wins','Losses'])
    text+='\nIntervals resample complete worlds within four fixed panels; states and budgets are not independent replicates. Family7 adjustment applies to the seven prespecified reference contrasts. No policy is promoted based on TEST ranking. All training losses, DEV-label zero-residual comparators and all9 fit attempts are in TRAINING.json; good MSE does not establish improved decisions.\n'
    text+='\nPaired secondary estimation errors and intervals (joint Brier/NLL, reliability-level absolute errors, fact/type errors) are in ESTIMATION_PAIRED.json. Negative differences favor Joint; these are exploratory and do not inherit the primary family correction.\n'
    write('T3_ABLATION_RESULTS.md',text)
    text='# T3 cross-budget and heldout-regime evaluation\n\n## Material Passport\n\nPrimary B32 uses192 worlds. Each secondary budget uses the same prespecified48-world subset,12 per panel; these overlap B32 worlds and cannot be counted as additional independent worlds. Budgets are separate completed trajectories.\n\n'
    text+=table([[B]+[f"{grouped[str(B)][n]['success']}/{grouped[str(B)][n]['n']}" for n in ['WorstFact-MI','Fresh-IG-Lite','IG-Fact-FixedType',task,typ,joint]] for B in [16,32,48,64]],['Budget','WorstFact','Fresh-IG','FixedType','Task-only','Type-only','Joint'])
    text+='\nB32 selected Joint minus WorstFact by panel:\n\n'
    text+=table([[p,panels[p]['WorstFact-MI']['n'],f"{panels[p]['WorstFact-MI']['delta_pp']:+.2f}",str([round(x,2) for x in panels[p]['WorstFact-MI']['ci95_pp']])] for p in panels],['Panel','Worlds','Delta(pp)','Paired95%'])
    text+='\nUnseen rates, d3/group partitions and alpha1 are held out of both neural fitting and DEV selection. Training only atB32 tests budget transfer at16/48/64. Most d4 B16 trajectories consist entirely of forced queries, so allocation policies cannot differ there. OOD confidence intervals remain wide; a small observed deficit is not a formal no-harm guarantee. Mechanism/Natural/Web validity is untested.\n'
    write('T3_CROSS_BUDGET_EVALUATION.md',text)
    all_costs=Counter();actual_paths=0;certificate=0
    for v in audit['batches'].values():all_costs.update(v['costs']);actual_paths+=v['paths'];certificate+=v['certificates']
    costs.update(actual_world_paths=actual_paths,actual_world_costs=dict(all_costs),online_actions=all_costs['task']+all_costs['type'],total_acquisition=sum(all_costs.values()),
      selected_joint_cpu_ratio_vs_WorstFact=cpu_ratio,network_parameter_count=training['attempts'][0]['parameters'],
      training_label_MSE_by_attempt=[{'mode':r['mode'],'seed':r['seed'],'selected_epoch':r['selected_epoch_by_dev_mse'],'selected_dev_mse':next(h['dev_mse'] for h in r['history'] if h['epoch']==r['selected_epoch_by_dev_mse'])} for r in training['attempts']])
    write('COMPUTATIONAL_COST.json',costs)
    text='# T3 computational and acquisition cost\n\n## Material Passport\n\nCPU-only NumPy neural training; no PyTorch dependency, GPU, language model or API. All actual-world acquisition and posterior-predictive simulation costs are separate ledgers.\n\n'
    text+=f"Executed actual-world paths: **{actual_paths}**. Online actions: **{costs['online_actions']}** (task {all_costs['task']}, type {all_costs['type']}); offline observations {all_costs['offline']}; total acquisition **{sum(all_costs.values())}**. TRAIN/DEV collection and DEV evaluation are included, not discarded as free preparation. Fixed-budget arms have identical online and total acquisition cost per paired world. No equal-reliability query saving was measured.\n\n"
    text+=f"Measured scientific CPU through TEST: **{costs['aggregate_experiment_cpu_seconds']:.2f}s**; sum of measured stage wall times **{costs['stage_wall_seconds_sum']:.2f}s**. Four parallel evaluator lanes are capped; workerCPU is the appropriate additive policy comparison and wall time is not a single-thread speedup. The aggregate includes measured coordinator/reaped descendant CPU after each stage entry, including label generation and subprocess setup; excludes initial coordinator imports, human preparation/reporting and unrelated sessions.\n\n"
    text+=f"Nine fixed MLP fits ({costs['network_parameter_count']} parameters each) consumed {costs['network_fit_cpu_seconds']:.3f}s CPU. Selected Joint / WorstFact B32 workerCPU ratio: **{cpu_ratio:.3f}**. Full labels and component CPU are in COMPUTATIONAL_COST.json and RESULTS.json. Feature/candidate construction includes an AnalyticReuse proposal; a cheap neural forward pass is not an end-to-end speedup. No break-even benefit is claimed when online deployment itself is slower.\n\n"
    text+='Component timers posterior/target/controller are the primary breakdown. feature_and_candidates and network_inference are SUBCOMPONENTS of controller, not extra exclusive CPU; legacy planner timers also overlap. Do not sum overlapping components. Aggregate process/descendant CPU is the complete measured scientific ledger.\n\n'
    for split in ['train','development']:
        c=costs[split+'_labels'];text+=f"{split}: {c['states']} states from{c['worlds']} worlds; {c['continuation_steps']} simulated continuation queries; {c['label_worker_cpu_seconds']:.2f}s measured label-function CPU, {c['wall_seconds']:.2f}s wall. These internal simulations are not online observation purchases; their computational cost is counted.\n\n"
    text+=f"Terminal certified outputs: {certificate}/{actual_paths}; normal non-certifications: {actual_paths-certificate}; infrastructure failures {audit['failures']}; incomplete planned paths {audit['incomplete']}. Gate reason counts are in VALIDATION.json. Numerical exceptions would be execution failures, distinct from a conservative gate refusing certification. Full-budget non-certification is censoring only for certified-stopping time; it is not a missing fixed-budget recovery outcome.\n"
    write('T3_COMPUTATIONAL_COST.md',text)
    worst=pairs['WorstFact-MI'];strong=max(BASELINES,key=lambda n:main[n]['success']);bestpair=pairs[strong]
    text='# T3 final research decision\n\n## Material Passport\n\n'
    text+=f"**{decision['overall']}**. Completed one authorized bounded pilot: 48 TRAIN,24 DEV,192 heldout TEST worlds;9 fixed lightweight neural fits with3 seeds per action mask. No Qwen, PPO, actor-critic escalation or confirmation was run.\n\n"
    text+=f"The DEV-selected Joint recovered **{main[joint]['success']}/192** atB32. WorstFact-MI recovered **{main['WorstFact-MI']['success']}/192**; paired difference **{worst['delta_pp']:+.2f}pp**,95% interval **{[round(x,2) for x in worst['ci95_pp']]}**, wins/losses {worst['wins']}/{worst['losses']}. The descriptively strongest TEST frozen reference was {strong}, {main[strong]['success']}/192; difference {bestpair['delta_pp']:+.2f}pp. Its TEST ranking is descriptive and did not choose the model or primary comparator.\n\n"
    text+=table([[k,'PASS' if v else 'FAIL'] for k,v in gates.items()],['Preregistered engineering/research gate','Result'])
    text+='\nRequired five-part judgment:\n\n'
    text+=f"1. **Statistical estimation:** selected Joint joint-Brier {main[joint]['mean_brier']:.4f}, NLL {main[joint]['mean_nll']:.4f}; WorstFact {main['WorstFact-MI']['mean_brier']:.4f}/{main['WorstFact-MI']['mean_nll']:.4f}. These are allocation-induced descriptive changes using the same estimator, not a new estimator consistency theorem. Complete-recovery improvement must be judged by the paired intervals above.\n"
    text+='2. **Online query cost:** no improvement demonstrated; every paired arm spends the same B. Higher fixed-budget accuracy, if any, would not establish equal-reliability savings.\n'
    text+='3. **Total acquisition cost:** no improvement demonstrated; per world every arm spends B+2M, and training/DEV observations add development cost.\n'
    text+=f"4. **Computation:** nine neural fits cost {costs['network_fit_cpu_seconds']:.3f}s CPU, but posterior-rollout labels and KL candidates dominate additional work. Selected Joint deploy workerCPU is {cpu_ratio:.3f}x WorstFact; no overall speedup is assumed from network-forward timing alone.\n"
    text+=f"5. **Certified stopping reliability:** unchanged gate, {certificate}/{actual_paths} certified in this bounded run. Terminal likelihood includes all task/type/calibration observations. Non-certified fixed-budget guesses carry no delta-correctness claim; no improvement in general numerical certification or asymptotic optimality is established.\n\n"
    text+='The training objective is terminal Bayesian recovery under frozen quadrature, not KL imitation. A single baseline state distribution, noisy K16 rollout labels and baseline-continuation/deployment mismatch limit one-step policy improvement. Exact simulation success cannot establish Natural/Web transfer or real source reliability. Preserve all seeds/checkpoints and negative findings. **Stop here: no automatic extra fitting, tuning or confirmation.** A future new experiment would need separate authorization and a new frozen protocol.\n'
    write('T3_FINAL_DECISION.md',text)
    write('README.md','# T3 bounded outcome-aligned training pilot\n\n'+''.join(f'- [{n}]({n})\n' for n in ['T3_FINAL_DECISION.md','T3_LEARNABILITY_AUDIT.md','T3_FROZEN_PROTOCOL.md','T3_POLICY_ARCHITECTURE.md','T3_ROLLOUT_TRAINING.md','T3_ABLATION_RESULTS.md','T3_CROSS_BUDGET_EVALUATION.md','T3_COMPUTATIONAL_COST.md'])+'\nRun receipts: TRAINING.json, DEV_SELECTION.json, TEST_OPENING_RECEIPT.json, VALIDATION.json, COMPUTATIONAL_COST.json, DECISION.json. Private world keys and raw traces remain ignored locally.\n')

def seal(cfg):
    check=verify();decision=json.loads((ROOT/'DECISION.json').read_text())
    public={str(p.relative_to(ROOT)):digest(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['artifacts','__pycache__','fixtures']) and p.name!='FINAL_RECEIPT.json' and p.suffix!='.pyc'}
    artifacts={str(p.relative_to(ROOT/'artifacts')):digest(p) for p in sorted((ROOT/'artifacts').rglob('*')) if p.is_file()}
    result={'phase':'T3 bounded outcome-aligned residual learning','source_check':check,'decision':decision,
      'public_files':public,'artifact_hashes':artifacts,'training_fits':len(json.loads((ROOT/'TRAINING.json').read_text())['attempts']) if (ROOT/'TRAINING.json').exists() else 0,
      'historical_files_overwritten':0,'confirmation_worlds':0,'LLM_calls':0,'GPU_training':False,'automatic_next_stage':False,
      'privacy':'new private master keys, reproduction traces and all checkpoints retained locally under ignored artifacts; no historical private or reserved confirmation seeds opened',
      'verification_scope':'source/protocol/runtime/history verification and independent ledger replay; not an independent rerun of effectiveness or a general numerical certificate'}
    write('FINAL_RECEIPT.json',result);print(json.dumps({'sealed':True,'public_files':len(public)+1,'artifacts':len(artifacts),'decision':decision['overall']}),flush=True)
