"""Frozen renderer; current results are never used to change a policy or threshold."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_text())
def num(x,k=3):return 'NA' if x is None else f'{x:.{k}f}'
def pp(x):return 'NA' if x is None else f'{100*x:+.2f}pp'
def effect(x,ci='ci95'):
    return 'NA' if x[ci] is None else pp(x['mean'])+' ['+', '.join(pp(z) for z in x[ci])+']'
def val(z,k,s='mean'):return z.get(k,{}).get(s)
def table(head,rows):return '\n\n'+'\n'.join(['|'+'|'.join(head)+'|','|'+'|'.join(['---']*len(head))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])+'\n\n'
def write(n,s):(ROOT/n).write_text(s.strip()+'\n')


def render(r,v,p,st,runtime,write_files=True):
    docs={};s=r['summaries'];arms=list(s['32']);d=r['decisions']
    passport='''\n## Material Passport\n\nBounded CPU development, run/validate inline. New independent roster96; four deadlines on each world are correlated. No RL, neural training, Qwen/model API or confirmation; no Natural/Web generator modification. Full source/dependency/protocol manifest precedes entropy. T1c missing-wrapper defect and old negative findings remain unchanged. This is source-bound descriptive analysis, not an independently rerun efficacy confirmation.\n'''
    stats='''\nWorld-paired bootstrap20000 within four fixed panels, seed42031; cell-stratified sensitivity seed42032 reported separately. Raw95% intervals are developmental; five strong-reference comparisons also have99% Bonferroni-family descriptive intervals. No simultaneous claim for every secondary table. Small strata and a fixed heterogeneous grid limit coverage and external generalization. Same-world budgets/groups are correlated.\n'''
    reliable=f"\nFixed-budget guesses are NOT certified answers. Terminal audited iid/known-s Fraction/Decimal gate includes all task/type/calibration. Certified outputs={v['certificates']}; wrong certificates={v['wrong_certificates']}; confidence-censored/noncertified={v['strict_confidence_censored']}. Planned paths={v['planned_paths']}, observed={v['finished_paths']}, unfinished={v['uncompleted_planned_paths']}, infrastructure failures={v['infrastructure_failures']}; integrity checks passed={v['passed']}. Gate rejection is distinct from numerical failure or unfinished budget execution. No delta-correctness, asymptotic optimality or real-language Agent claim.\n"
    core=table(['Policy','B16 exact/n','B32 PRIMARY exact/n','B48 exact/n','B64 exact/n','B32 worker CPU/s','B32 type mean'],
        [[a,*[str(s[str(B)][a]['exact'])+'/'+str(s[str(B)][a]['n']) for B in [16,32,48,64]],num(val(s['32'][a],'cpu','sum')),num(val(s['32'][a],'type_queries'),2)] for a in arms])
    text='# Nonuniform allocation ablation\n'+passport
    text+='\nPrimary constraint-matched direct pair uses the SAME dense joint-theta information objective, fresh free-round updates and deterministic score ties. Uniform averages IG within a selected group/format and balances primitive counts there; nonuniform is frozen Lite. An additional shared-tracker2x2 and a fixed-type pair are predeclared. KL nonuniform is not fabricated; original asymptotic KL symmetrization and plug-in differences are documented in POLICY_SEMANTICS_AND_SOURCE_AUDIT. Native log/LP baselines retain their original ties and are not pure mechanism controls.\n'
    text+=table(['Comparison','B16','B32 PRIMARY','B48','B64'],[[k,*[effect(p[str(B)][k]) for B in [16,32,48,64]]] for k in ['Fresh-IG-Lite minus IG-Uniform-Direct','IG-Fact-Fresh minus IG-Uniform-Fresh','IG-Fact-Block minus IG-Uniform-Block','IG-Fact-FixedType minus IG-Uniform-FixedType']])
    text+=table(['IG granularity x refresh effect','B32','B48','B64'],[[k,*[effect(r['factorial'][str(B)][k]) for B in [32,48,64]]] for k in r['factorial']['32']])
    text+='\nB32 mechanism diagnostics: raw descriptive proxy means; lower redundant-query/starvation values are not a proof of useful-information causality.\n'
    text+=table(['Policy','task HHI','free-task max share','worst-fact entropy bits','starved facts','concentration flag','>=.95 confidence task queries'],
        [[a,*[num(val(s['32'][a],k)) for k in ['task_hhi','maximum_free_task_share','worst_fact_uncertainty','starved_facts','overexploration_flag','redundant_confident_queries']]] for a in arms])
    main=p['32']['Fresh-IG-Lite minus IG-Uniform-Direct']
    text+='\nPrimary Lite−uniform constraint effect='+effect(main)+'; ID='+effect(r['ID_nonuniform_pair'])+'; pooled OOD='+effect(r['OOD_nonuniform_pair'])+'. Fixed-type isolated task contrast='+effect(r['fixed_type_nonuniform_pair'])+'.\n'
    text+=table(['Primary paired diagnostic difference (Lite−uniform)','mean','95% interval'],[[k,num(main[k+'_difference']['mean']),'NA' if main[k+'_difference']['ci95'] is None else '['+', '.join(num(x) for x in main[k+'_difference']['ci95'])+']'] for k in ['task_hhi','worst_fact_uncertainty','starved_facts','redundant_confident_queries','type_queries','fact_accuracy']])
    text+='\nPer-fact counts, free counts, terminal marginal confidence/entropy, per-fact posthoc correctness, per-group task/type counts and recovery are retained for EVERY path in MECHANISM_DIAGNOSTICS.json. Flagged/unfavorable paths are not removed. Starvation means terminal confidence<.8 and zero free task queries when free rounds exist; concentration flag means one fact gets>=.5 of free task queries and another remains<.8. These are fixed diagnostics, not optimality tests. Shared reliability means querying a confident fact may still help others. Terminal uncertainty can be a result of allocation; proxy-outcome association is not causal mediation.\n'
    text+=f"\nOffline B32 prefix reconstruction recomputed {r['diagnostic_replay']['unique_recomputed_states']} unique states in {num(r['diagnostic_replay']['CPU_seconds'])} CPU seconds; never returned to policies and excluded from their planning timers. It is not a second scientific run.\n"+stats+reliable
    docs['NONUNIFORM_ALLOCATION_ABLATION.md']=text

    text='# Cross-budget evaluation\n'+passport+core
    text+='\nEach budget was actually run. Belief-Gated knows the deadline; it is not evaluated using a long-path midpoint. d4 B16 is all forced; d3 B16 has4 free rounds. The OOD-partition panel shifts BOTH group partition and fact count. No independent growing-d or general partition-transfer claim follows. Online cost is exactlyB, offline2ceil(alpha R), so higher recovery at equal cost is not a measured saving to equal reliability.\n'
    for dimension in ['panel','partition','rate','gap','alpha']:
        text+='\n## '+dimension+' strata\n'
        text+=table(['Stratum','B','n','Lite exact','UniformDirect exact','Fused-Info exact','AnalyticReuse exact','Belief-Gated exact','WorstFact exact','Lite−uniform 95%'],
            [[name,B,z[str(B)]['arms']['Fresh-IG-Lite']['n'],*[z[str(B)]['arms'][a]['exact'] for a in ['Fresh-IG-Lite','IG-Uniform-Direct','Fused-Info','KL-AnalyticReuse','Belief-Gated','WorstFact-MI']],effect(z[str(B)]['Lite_minus_uniform'])] for name,z in st[dimension].items() for B in [16,32,48,64]])
    text+=stats+reliable;docs['CROSS_BUDGET_EVALUATION.md']=text

    text='# Paired statistical report\n'+passport
    text+='\nPrimary metric is exact complete-vector recovery under the common joint-theta MAP decoder; marginal MAP fact accuracy is separately labeled. Same overall successes do NOT imply same successful worlds or action sequences.\n'
    keys=['Fresh-IG-Lite minus IG-Uniform-Direct']+['Fresh-IG-Lite minus '+a for a in r['strong_reference_family']]+['IG-Fact-FixedType minus IG-Uniform-FixedType']
    text+=table(['B32 pair','n','candidate only','reference only','both success','both fail','95% delta','99% family delta','identical histories'],
        [[k,p['32'][k]['n'],*[p['32'][k][x] for x in ['candidate_only','reference_only','both_success','both_failed']],effect(p['32'][k]),effect(p['32'][k],'ci99') if k.startswith('Fresh-IG-Lite minus ') and k.split(' minus ')[1] in r['strong_reference_family'] else 'not family endpoint',p['32'][k]['identical_action_sequences']] for k in keys])
    text+=table(['B32 pair','panel-stratified95%','cell-stratified sensitivity95%'],[[k,effect(p['32'][k]),effect(p['32'][k]['cell_stratified_sensitivity'])] for k in keys])
    text+=table(['Policy','Joint-MAP fact accuracy','Marginal-MAP fact accuracy','joint NLL','joint Brier','p MAE','q MAE'],
        [[a,*[num(val(s['32'][a],k)) for k in ['fact_accuracy','marginal_MAP_fact_accuracy','joint_nll','joint_brier','p_mae','q_mae']]] for a in arms])
    text+='\nThe maximum observed baseline is descriptive and is not retrospectively adopted as the only reference. Strict improvement requires all five99% lower bounds>0. A practical baseline engineering gate uses nonnegative points and99% lower>=−3pp; it is not proof of population equivalence or a learned-policy result.\n'
    text+='\n## Statistical fallacy coverage (11/11 reviewed)\n'
    text+=table(['Issue','Disposition'],[
        ['Simpson aggregation','All panel/partition/rate/gap/calibration strata retained; no universal claim from pooled average.'],
        ['Ecological inference','Per-fact/group descriptions nested within worlds; no independent-group standard errors.'],
        ['Regression to mean','New roster drawn after seal; old T1c winners not reselected or pooled as confirmation.'],
        ['Base rates','Full denominators and all four paired outcome cells reported.'],
        ['Multiple comparisons','Single primary mechanism contrast; fixed five-reference family99%; other tables descriptive.'],
        ['Confounding','Dense matching plus type-fixed and tracker controls; native anchors not called pure objective interventions.'],
        ['Survivorship','All unfinished/invalid/failure paths disclosed against planned denominator.'],
        ['Look elsewhere','All budgets/arms/strata preserved, no selecting only favorable cells.'],
        ['Forking paths','Complete source/protocol hash before entropy; thresholds unchanged.'],
        ['Causal overreach','Full policy comparisons do not establish proxy mediation or real-language validity.'],
        ['Reverse direction','Terminal uncertainty is downstream of queries; never used retrospectively to pick deployed actions.']])
    text+=stats+reliable;docs['PAIRED_STATISTICAL_REPORT.md']=text

    text='# Computational cost\n'+passport
    text+=table(['Policy B32','CPU total/s','wall total/s','CPU median/ms','CPU p95/ms','posterior/s','target/s','controller/s','terminal belief/s','gate/s','type mean','total acquisition mean'],
        [[a,num(val(s['32'][a],'cpu','sum')),num(val(s['32'][a],'wall','sum')),num(None if val(s['32'][a],'cpu','median') is None else 1000*val(s['32'][a],'cpu','median')),num(None if val(s['32'][a],'cpu','p95') is None else 1000*val(s['32'][a],'cpu','p95')),
          *[num(val(s['32'][a],k,'sum')) for k in ['posterior_cpu','target_cpu','controller_cpu','terminal_belief_cpu','certification_cpu']],num(val(s['32'][a],'type_queries')),num(val(s['32'][a],'total_acquisition'))] for a in arms])
    text+=table(['Reference / Lite worker CPU ratio at B32','ratio','paired95%','Lite recovery difference'],
        [[a,num(p['32']['Fresh-IG-Lite minus '+a].get('reference_over_candidate_CPU',{}).get('ratio')),
          str(p['32']['Fresh-IG-Lite minus '+a].get('reference_over_candidate_CPU',{}).get('ci95')),effect(p['32']['Fresh-IG-Lite minus '+a])] for a in r['strong_reference_family']])
    ex=runtime['scientific_execution']
    text+=f"\nExecution status={ex['status']}; wall={num(ex['seconds'])}s; full worker trajectory CPU={num(runtime['worker_CPU_total'])}s; parent aggregate CPU={num(ex['evaluator_cpu_seconds'])}s; measured kernel warmup CPU={num(sum(runtime['worker_warmup_CPU'].values()))}s. Costs including partial={ex['costs_including_partial']}. Source integrity at end={ex['frozen_files_preserved']}.\n"
    text+='\nThe posterior/target/controller timers are exclusive; legacy planner timers overlap and are not added. Full trajectories include query RPC, observation handling, final estimator and gate. Parent CPU is aggregate and has no defensible per-arm attribution. Python/import work before worker timers and full OS overhead are not completely measured. This is not a full-machine CPU acceleration guarantee. Preflight/analysis are development overhead, reported separately; no GPU training cost exists.\n'
    text+=f"\nPostprocessing CPU={num(runtime['analysis_CPU'])}s and wall={num(runtime['analysis_wall'])}s, including observation-only redundancy replay. These are not online policy costs. Timings concern this machine/d<=4/R16 only; different rate panels, wall load and native implementations limit extrapolation. No cross-batch timing ratio to T1c is claimed.\n"+stats
    docs['COMPUTATIONAL_COST.md']=text

    text='# WWW contribution assessment\n'+passport
    text+=table(['Question','Decision'],[[k,str(z)] for k,z in d.items() if k not in ['C_partition_harms_over_10pp']])
    text+='''
## What the algorithm is

Lite chooses argmax_a I(theta;Y_a | legal history)/unit cost under a numerical fused posterior, subject to the inherited forced schedule. Removing unused KL work and using dense predictive moments improves an implementation; it does not create a new information objective. Group-shared latent reliability, noisy type queries and full-vector recovery define the setting, but no new theorem, estimator or learned policy is supplied here.

Information-theoretic one-step acquisition and Bayesian expected-utility design are established frameworks: [Houlsby et al., 2011](https://arxiv.org/abs/1112.5745), [Chaloner and Verdinelli, 1995](https://www.stat.cmu.edu/tr/tr599/tr599.html). This is a two-source primary check, not an exhaustive priority review. Inference from our formula: naming this implementation a novel greedy-IG algorithm is unsupported, regardless of its development success.

## Defensible positioning

A robust constraint-matched and type-controlled effect can support an empirical mechanism observation and a practical no-training finite-budget baseline in the broader theory/benchmark paper. It cannot by itself establish a novel independent learning method, universal superiority, growing-d robustness, certified stopping or Natural transfer. If worst-fact uncertainty sampling matches/exceeds it, preserve that result rather than rename it as a new contribution. Cheap-controller paired outcomes, CPU and actual action histories are reported, not just total successes.

The T1d scope is complete after these results. No further favorable-regime tuning, neural complexity or RL is launched. If practical evidence is positive a confirmation protocol may be proposed, but its execution and seed access require a later explicit authorization. Existing reserved confirmation seeds remain unopened.
'''+stats+reliable
    docs['WWW_CONTRIBUTION_ASSESSMENT.md']=text

    text='# T1d final decision\n'+passport
    text+='\n**'+d['overall']+'; no RL or automatic confirmation.**\n'
    text+=table(['Separate judgment','Result'],[[k,str(z)] for k,z in d.items() if k not in ['C_partition_harms_over_10pp','stop_after_this_development','confirmation_execute_authorized']])
    text+='\nPrimary B32 nonuniform comparison: '+effect(r['main_nonuniform_pair'])+'. Fixed-type task-granularity comparison: '+effect(r['fixed_type_nonuniform_pair'])+'.\n'+core
    bg=p['32']['Fresh-IG-Lite minus Belief-Gated']
    text+='\nLite versus cheap controller: '+effect(bg)+f"; wins/losses/both-success/both-fail={bg['candidate_only']}/{bg['reference_only']}/{bg['both_success']}/{bg['both_failed']}; identical action sequences={bg['identical_action_sequences']}/{bg['n']}. Equal success counts alone are not equivalence.\n"
    text+='\nA positive whole-policy constraint effect, a positive fixed-type contrast and a proxy reduction answer different questions. Do not attribute the entire gain to one mathematical objective, confidence proxy or refresh rate. KL symmetrization concerns a different asymptotic problem. Conditional or negative panels remain in CROSS_BUDGET_EVALUATION. No result automatically repairs T1c provenance or authorizes another development loop.\n'
    text+='\nThe method is a standard one-step IG implementation in this latent-reliability model; standalone algorithmic novelty is not established. The empirical/practical baseline decision and WWW primary-contribution decision remain separate. All raw paths, failed/unfinished outcomes and full manifests are retained. This phase stops here.\n'+stats+reliable
    docs['FINAL_DECISION.md']=text

    positive = d['A_nonuniform_reproducibility']=='GO' or d['B_practical_baseline_engineering_gate']=='GO'
    if positive:
        docs['CONFIRMATION_PROTOCOL_PROPOSAL.md']='''# Proposed frozen confirmation — NOT EXECUTED

## Material Passport

Conditional follow-up proposal only. No authorization to execute, create entropy, open reserved seeds, or run a training pilot. Current T1d final public/source receipt fixes the method bytes. Any later approved protocol revision must be dated before a fresh confirmation roster exists.

Purpose: confirm the empirical no-training baseline claim, not novel greedy-IG priority. Proposed480 independent worlds, four panels120 each: ID12cellsx10, OOD-rate12x10, OOD-partition8x15, OOD-calibration6x20. Same predeclared rates/partitions/alpha/R as T1d, no selecting favorable cells. New confirmation entropy generated after explicit approval and full source/protocol seal; do not read or reuse reserved Phase3 seeds without separate authorization.

Run six fixed policies: Lite, UniformDirect, AnalyticReuse, frozen Fused-Info, frozen Belief-Gated, WorstFact-MI. B32 primary and B16/48/64 secondary, separate actual runs:11520 paths,460800 online actions planned, fixed acquisition accounting and common joint MAP/terminal certificate distinction. OriginalSolver remains an audited implementation anchor; its allocation objective is already represented by AnalyticReuse. No tuning, retraining, policy replacement, sample enlargement or automatic failed-path retry.

Primary family: Lite vs all five references. Predeclare a stratified paired world analysis, exact four-cell tables,99% family intervals and full failure denominator; secondary budgets/panels are correlated descriptions. Fix an intention-to-evaluate rule for unfinished paths before authorization (no complete-case superiority claim). Source/runtime change requires a new seal before roster generation. Recovery, calibration/online/total cost, worker/parent CPU, wall and certificates remain separate endpoints.

Sample-size rationale is conditional, not established power: for assumed discordance .25 and target difference .08, a normal paired approximation using two-sided per-comparison alpha .01 and80% power gives about445 worlds, so480 is a rounded balanced capacity. This approximation is not guaranteed for true discordance or heterogeneous panels; do not claim a power-certified design. No outcome from this future roster may be used to revise thresholds, choose references or increase N.

Success claim must state which fixed comparisons pass and retain any weak/null/harmful regimes. Even success supports a practical finite-budget baseline, not delta-correctness, general asymptotic optimality, independent algorithmic novelty or RL added value. User must explicitly authorize the final resource/time envelope and execution in a later turn.
'''
    else:
        docs['CONFIRMATION_DISPOSITION.md']='# Confirmation disposition\n\nNo confirmation launch or seed access. Prespecified practical/primary mechanism gates did not support preparing an execution-ready next stage. Preserve the bounded negative/conditional development result; no automatic extra experiment.\n'
    docs['README.md']='''# T1d nonuniform allocation and robustness

Read FINAL_DECISION.md first. The eight requested Markdown deliverables plus FINAL_RECEIPT.json are in this directory. T1D_PROTOCOL.md and POLICY_SEMANTICS_AND_SOURCE_AUDIT.md predate scientific entropy; the remaining reports are produced by the precommitted analyzer/renderer. No training or confirmation occurred.

SOURCE_MANIFEST.json covers all local Python (including copied T1c wrappers and complete dependencies, tests and postprocessing), fixed documents and numerical runtime fingerprints. HISTORICAL_INPUTS.json verifies frozen T1a/T1b/T1c public receipts without rewriting T1c's missing-wrapper record. Artifacts/private and literal engineering fixture records stay git-ignored; final receipt binds their hashes only. Existing reserved seeds were never opened.

RESULTS.json, PAIRED_OUTCOMES.json, STRATIFIED_RESULTS.json, MECHANISM_DIAGNOSTICS.json, RUNTIME.json and VALIDATION.json retain full denominators, all budgets/arms, negative cases and scope. Do not treat fixed-budget guesses as certified answers. The proposed confirmation document, if present, is a proposal with zero execution authorization.

The single scientific runner refuses artifacts overwrite or retry. Recomputing analysis/reports does not generate worlds: `python audit/analyze.py` then `python audit/render.py`; source integrity must remain unchanged and final receipt must be regenerated. Do not delete artifacts to rerun a new scientific batch. The branch is isolated; public allow-list is staged without commit/push/merge.
'''
    if write_files:
        for name,text in docs.items():write(name,text)
    return docs


if __name__=='__main__':
    docs=render(read('RESULTS.json'),read('VALIDATION.json'),read('PAIRED_OUTCOMES.json'),read('STRATIFIED_RESULTS.json'),read('RUNTIME.json'))
    print(json.dumps({'rendered_documents':list(docs)}))
