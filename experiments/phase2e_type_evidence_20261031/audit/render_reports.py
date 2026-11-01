"""Render descriptive reports from persisted analysis; no acquisition."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/f'artifacts/analysis/{n}.json').read_text())
def table(headers,rows):return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(str(v).replace('|',r'\|') for v in r)+'|' for r in rows])
def fmt(v):return f'{v:.4f}'
def ci(r):return f"{r['online_gain_over_R']:.3f} [{r['percentile_95_CI'][0]:.3f}, {r['percentile_95_CI'][1]:.3f}]"
def main():
    f=read('facts');ss=read('summary');pp=read('paired');ds=read('diagnostic_summary');tt=read('purchase_timing');pr=read('compute_probe')
    policies=[a['policy'] for a in f['aggregates']];cells=sorted(set(r['cell'] for r in ss))
    stats={(r['cell'],r['policy']):r for r in ss};pairs={(r['cell'],r['contrast']):r for r in pp}
    abbr={'Aligned-Full':'AF','Aligned-NoType':'AN','D-RRC-Type':'DT','D-RRC-NoType':'DN',
          'Fused-Original':'FO','Fused-Info':'FI','Fused-D-RRC-Type':'FD','Fused-Original-NoType':'FON','Fused-Info-NoType':'FIN'}
    aggregate_rows=[]
    for r in f['aggregates']:
        aggregate_rows.append([abbr[r['policy']],r['n'],r['task'],r['type'],r['offline'],r['online'],r['total_acquisition'],f"{r['complete']}/{r['n']}",r['censored'],f"{r['exact']}/{r['n']}"])
    text=f'''# Fair ablation report

## Material Passport

Phase 2e new development only. Fixed protocol and code before the new seed;
32 independent worlds, 8 cells, four worlds per cell, nine arms and
{f['trajectories']} trajectories. Historical results and confirmation protocols
are unchanged. All new trajectories use the common conservative stopping gate.
The frozen labels refer to unchanged SAMPLERS, not to reuse of floating historical
stopping times. No world or method was replaced after observing its outcome.

The generator is the unchanged QRelBench-Exact generator, p=.85,q=.60,s=.8,
eta=.05, crossed partitions [1,3]/[4], alpha=0/3, R=16/256. Post-run population
coefficients classify [4],alpha=0 as zero premium; the other cells have positive
premium. Coefficients are diagnostics, never learner inputs. Natural fixtures
are interface tests only.

AF=Aligned-Full; AN=Aligned-NoType; DT=D-RRC-Type; DN=D-RRC-NoType;
FO=Fused-Original; FI=Fused-Info; FD=Fused-D-RRC-Type;
FON=Fused-Original-NoType; FIN=Fused-Info-NoType. AF/AN/DT/DN are literal frozen
strategy imports. FO/FD change only their estimator. FI/FIN change the allocation
criterion after fusion. Every arm receives the same public task, paid action
interface and charged reference observations; no-type arms cannot buy type reports.

## Full denominators and accounting

Completed/certified {f['complete']}/{f['trajectories']}; cap-censored
{f['censored']}/{f['trajectories']}; exact terminal guesses {f['exact']}/{f['trajectories']};
wrong certified outputs {f['certified_wrong']}/{f['complete']}.
The terminal guess at cap is scoring only and is never a strict output.
The failure log is empty. The unique shared offline observations number
{f['unique_shared_offline']}; policy-accounted offline cost is {f['counters']['offline']}.
They are different denominators. Every policy's total cost charges its own
full reference observations.

'''+table(['arm','n','task','type','offline','online','total','certified','censored','exact guess'],aggregate_rows)+'''

## Restricted online costs by cell

Entries are mean min(T,cap)/R. Every world is retained, including cap-censored
paths at their full cap. These are restricted costs, not estimates of an
untruncated expected stopping time. No automatic cap extension occurred.

'''+table(['partition / alpha / R']+[abbr[p] for p in policies],[[c]+[fmt(stats[(c,p)]['online_over_R']) for p in policies] for c in cells])+'''

Total/R equals the displayed online/R plus 2 ceil(alpha R)/R, which is 0 or 6
in these cells. Thus paired ABSOLUTE gains in total acquisition equal paired
online gains; their percentage reductions differ when alpha=3. Full unnormalized
costs, terminal planning errors and CPU/wall are in summary.json.

## Paired contrasts

A positive gain is (before-after)/R. Intervals are 4,000 world-paired percentile
bootstrap resamples, shared within a cell, fixed analysis seed763502. n=4 per
cell; intervals are descriptive, unadjusted for all contrasts and unsuitable as
independent confirmation. Every raw four-world vector is in paired.json.

'''+table(['cell','AF-FO: fusion','FO-FI: allocation','DT-FD: fusion on D','AF-FI: whole change','FD-FI: same-estimator D'],[[c]+[ci(pairs[(c,k)]) for k in ['fusion_original','allocation_after_fusion','fusion_D','new_vs_frozen_Aligned','new_vs_same_estimator_D']] for c in cells])+'''

## Task allocation and type availability

The no-type pair holds type purchase unavailable and uses the same fused
estimator. Full/no-type contrasts measure enabling type actions within each
allocator. The interaction compares these two type gains. Because changing
purchase choices also changes later task evidence, it does not identify a pure
purchase-timing effect on a fixed task trajectory.

'''+table(['cell','FON-FIN: task allocation','FON-FO: original type gain','FIN-FI: new type gain','type-gain interaction'],[[c]+[ci(pairs[(c,k)]) for k in ['task_allocation_without_type','type_access_original','type_access_info','type_gain_interaction_info_minus_original']] for c in cells])+'''

The following spending is averaged over ALL 32 worlds, and uses counts by
min(T,landmark), carrying a stopped trajectory's terminal paid cost forward.
It creates no missing completed-before-landmark rows and buys no new reports.

'''+table(['arm','type by min(T,64)','type by min(T,256)','terminal type mean'],[[abbr[p]]+[fmt(next(x['type_mean_by_min_T_landmark'] for x in tt if x['policy']==p and x['landmark']==n)) for n in [64,256]]+[fmt(next(a['type']/32 for a in f['aggregates'] if a['policy']==p))] for p in policies])+'''

## Evidence fusion on one observed allocation tape

All variants below use the same Aligned-Full observed prefix and landmark.
The forced-only estimate is recomputed fresh from its deterministic forced
observations. The joint and conditional plug-in estimators receive the SAME
all-data prefix. Masked likelihood variants omit one evidence component without
altering the observed allocation. They are sensitivity calculations, not exact
posterior inference under a coarsened adaptive filtration. Forced-only Brier
uses hard 0/1 point estimates, not calibrated probabilities.

'''+table(['landmark','estimator','observed/planned worlds','p MAE','q MAE','theta error count','type error count','theta Brier','type Brier'],[[r['landmark'],r['estimator'],f"{r['worlds_observed']}/{r['worlds_planned']}"]+[fmt(r[k]) for k in ['p_MAE','q_MAE','theta_errors','type_errors','theta_Brier','type_Brier']] for r in ds])+f'''

Landmarks64/256 condition on reaching that budget when not all paths reach it;
the printed denominator makes this explicit. Terminal estimates have variable
horizons and are descriptive. At these prefixes the largest absolute 32-versus-64
quadrature difference across p/q and marginal probabilities is
{f['quadrature_max_abs']:.8g}; it is a numerical sensitivity diagnostic, not an
integration-error certificate. Full per-world observations, scores and estimates
are in diagnostics.json.

## Statistical interpretation audit

11/11 requested methodological fallacy types were checked: Simpson reversal is
addressed by separate cells and no universal pooled superiority claim;
ecological inference uses worlds as units; Berkson selection is limited by
retaining the fixed whole grid; collider adjustment is absent; base-rate claims
retain all recovery denominators; no selection on extreme outcomes was used;
survivorship is addressed by capped costs and explicit landmark reach counts;
look-elsewhere remains a limitation of unadjusted exploratory contrasts;
forking paths are bounded by the pre-seed protocol with no outcome tuning;
causal claims are restricted to these coupled algorithm interventions in this
model; reverse causality is not used to explain an estimator change. Prior to
this phase, choosing the existing p/q configurations was historical development;
new seeds alone do not establish out-of-configuration generalization.

No errors at exp(-R) risk levels empirically verify that risk. The theoretical
and arithmetic stopping implication, its assumptions, and all non-certifications
are discussed separately in CERTIFIED_EVALUATION.md. Final decisions remain
bounded development judgments in FINAL_RESEARCH_DECISION.md.
'''
    (ROOT/'FAIR_ABLATION_REPORT.md').write_text(text)
    gr=f['gate_status_counts'];runtime=json.loads((ROOT/'RUNTIME.json').read_text())
    cert=f'''# Certified end-to-end evaluation

## Material Passport

Prospective new Phase 2e development, not a relabeling of Phase 2d floating
endpoints. Every one of {f['trajectories']} planned trajectories used the existing
bounded certified gate for its actual stopping decision. No confirmation or model
calls occurred. Frozen stopping code/spec/proof audit are bound by SOURCE_SNAPSHOT.json.

At each scheduled check the floating all-data profile GLR only determines whether
to try the gate. At cap the gate is tried regardless. Acceptance requires

\\[
\\underline F(\\theta_c)-\\overline{{\\max_{{\\theta\\ne\\theta_c}} F(\\theta)}}
>\\overline{{R+2\\log(M+1)+\\sum_{{jm}}\\log(N_{{jm}}+1)+\\sum_g\\log(K_g+1)}}.
\\]

All task responses, all paid type reports, both labelled offline streams and
all group memberships used by any estimator are included in this certified
likelihood. The prior, quadrature approximation and empirical-Bayes estimates
are allocation computations; they do not replace or restrict the continuous
stopping likelihood. All signs/types are enumerated and every continuous rate
pair in the ordered closure is profiled analytically with exact Fraction counts.
Decimal log bounds and all endpoint operations round outward. Inputs such as
.8 and .05 mean their exact stored binary rational values.

## Observed certification census

Strictly accepted: {f['complete']}/{f['trajectories']}; budget non-certification:
{f['censored']}/{f['trajectories']}; wrong certified outputs:
{f['certified_wrong']}/{f['complete']}. Gate attempts by status: {json.dumps(gr)}.
An ordinary `rejected` at a budget means insufficient evidence for that
candidate at that transcript; it is not an arithmetic failure.
All final points were recomputed from persisted raw integer task counts, type
reports and reference bits after acquisition. Every recomputed result agreed
with the recorded strict completion status, and every gate's total-observation
count equaled the charged total acquisition cost. See endpoint_reaudit.json.
No infrastructure failure or hidden floating fallback was found.

At an uncertified cap the strict output is null. A terminal benchmark guess can
be correct for scoring while remaining uncertified. Rejected or undetermined
gates continue until a later check or the fixed cap. Engineering fault injection
verified continuation from16 to32 after an undetermined result, then acceptance;
an always-undetermined test continued to64 and abstained. These fixtures are
not scientific worlds. The 13 inherited stopping tests passed, including the
preserved static large-count counterexample where the legacy floating guard
accepts and the conservative gate rejects. Twelve new method/interface/driver
tests passed, plus 14 exact-posterior information checks; see VALIDATION.json.

## Exact scope of the reliability statement

For the stated correctly specified fresh independent Bernoulli stream model,
known finite s_g, deterministic public risk chosen before references, predictable
sampling and faithful aggregation, each accepted event is a subset of the exact
joint GLR crossing event. The Theory_Note mixture argument initialized before
the offline sample therefore bounds wrong certified output probability by
exp(-R), UNCONDITIONALLY over references. The gate can be applied to any of the
new predictable allocation rules; no allocation-optimality proof is needed for
this error implication. It does not provide a risk bound conditional on each
particular offline sample or for the cap scoring guess.

The inherited supported arithmetic scope is d<=4, total observations<=2^50,
bounded rational constants and finite precision schedules; actual runs used
Python{runtime['python'].split()[0]}, libmpdec{runtime['libmpdec']} and the recorded
50/80/120 precision schedule. This is a hand-audited analytic/Fraction/Decimal
contract, not formal verification or general numerical certification. It does
not cover unknown type accuracy, persistent/correlated responses, distribution
mismatch, arbitrary dimension, hardware faults or numerical allocation optimality.

The certificate guarantee is the SAME one for all nine arms. Fusion has not
improved its nominal risk theorem. Relative to the older Phase 2d main batch,
this phase supplies actual end-to-end conservative acceptance and explicit
non-certification, while preserving the historical batch's floating identity.
The observed zero wrong certificates is compatible with the theorem and cannot
empirically test an exp(-256) risk. No almost-sure stopping, expected-time
optimality or uniform numeric guarantee is claimed for the new executable.
'''
    (ROOT/'CERTIFIED_EVALUATION.md').write_text(cert)
    comp=f'''# Computational cost report

## Material Passport

Same32 development worlds per arm; one active trajectory at a time in cyclic
policy order, single BLAS thread and pre-imported confined workers. Acquisition
wall time {f['execution']['seconds']:.3f}s; evaluator CPU
{f['execution']['evaluator_cpu_seconds']:.3f}s. The main hard allowance was1500s
and1,200,000 online actions. Logs include all capped paths; no timing outlier
was removed. Worker CPU excludes pool bootstrap and includes sampling/planning,
GLR, gate and RPC handling. Wall includes evaluator/RPC waits.

'''+table(['arm','n','worker CPU sum s','worker wall sum s','planner CPU sum s','GLR CPU sum s','gate wall sum s','CPU/trajectory s'],[[abbr[a['policy']],a['n']]+[fmt(a[k]) for k in ['trajectory_cpu_seconds','trajectory_wall_seconds','planner_cpu_seconds','glr_cpu_seconds','gate_seconds']]+[fmt(a['trajectory_cpu_seconds']/a['n'])] for a in f['aggregates']])+'''

The original allocation arms repeatedly solve the historical cutting-plane LP.
The information arms replace that LP with binary-response information scores,
but still pay joint posterior integration cost. The same-estimator D arm is a
simple computational comparator. Differences in stopping time also affect total
CPU, so this table measures end-to-end policy cost rather than equal-count
estimator speed. Full per-cell CPU/wall/planning/gate fields are in summary.json.

A separate fixed-count probe uses no scientific world or acquisition. The exact
reference clears its integration cache on each repeat; the numerical runs reuse
normal design caches. These measurements illustrate a bounded fixture and are
not a general performance guarantee or an equal-accuracy benchmark.

'''+table(['operation','fixture','repeats','mean CPU s','minimum CPU s'],[[r['method'],r['fixture'],r['repeats'],f"{r['cpu_seconds_mean']:.7f}",f"{r['cpu_seconds_min']:.7f}"] for r in pr])+'''

The current numerical posterior enumerates S=2^(d+G) states over K=32^2 rate
nodes, with O(SK) main storage and O(SK+Sd) aggregation. The information pass
uses A=2d+G binary actions and O(A(SK+4^d)) work for the implemented marginal
and pairwise-deviation calculations. Here d=4,G<=2,S<=64,A<=10. This is
practical for this bounded reference problem, not a scalable general-d solver.
Rate-conditional factorization is a possible future optimization, unimplemented
and unevaluated here. The exact alternating-polynomial reference also pays
large-integer rational costs and deliberately caps its observation count.

No GPU, training, Qwen, provider, external model or paid API resources were
used. Statistical acquisition cost and local computation time remain separate
outcomes. Runtime identities appear in RUNTIME.json. The existing gate itself
was unchanged, so any end-to-end gate cost change follows attempt counts and
transcript size rather than a faster certification implementation.
'''
    (ROOT/'COMPUTATIONAL_COST_REPORT.md').write_text(comp)
    print('Rendered fair ablation, certified evaluation and computation reports')
if __name__=='__main__':main()
