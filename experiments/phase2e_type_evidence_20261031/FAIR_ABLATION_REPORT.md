# Fair ablation report

## Material Passport

Phase 2e new development only. Fixed protocol and code before the new seed;
32 independent worlds, 8 cells, four worlds per cell, nine arms and
288 trajectories. Historical results and confirmation protocols
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

Completed/certified 287/288; cap-censored
1/288; exact terminal guesses 288/288;
wrong certified outputs 0/287.
The terminal guess at cap is scoring only and is never a strict output.
The failure log is empty. The unique shared offline observations number
13056; policy-accounted offline cost is 117504.
They are different denominators. Every policy's total cost charges its own
full reference observations.

|arm|n|task|type|offline|online|total|certified|censored|exact guess|
|---|---|---|---|---|---|---|---|---|---|
|AF|32|35270|4506|13056|39776|52832|32/32|0|32/32|
|AN|32|39376|0|13056|39376|52432|32/32|0|32/32|
|DN|32|55344|0|13056|55344|68400|31/32|1|32/32|
|DT|32|34734|6914|13056|41648|54704|32/32|0|32/32|
|FO|32|29596|3316|13056|32912|45968|32/32|0|32/32|
|FI|32|28673|3135|13056|31808|44864|32/32|0|32/32|
|FD|32|29897|6887|13056|36784|49840|32/32|0|32/32|
|FON|32|36288|0|13056|36288|49344|32/32|0|32/32|
|FIN|32|35120|0|13056|35120|48176|32/32|0|32/32|

## Restricted online costs by cell

Entries are mean min(T,cap)/R. Every world is retained, including cap-censored
paths at their full cap. These are restricted costs, not estimates of an
untruncated expected stopping time. No automatic cap extension occurred.

|partition / alpha / R|AF|AN|DN|DT|FO|FI|FD|FON|FIN|
|---|---|---|---|---|---|---|---|---|---|
|[1, 3]\|alpha=0\|R=16|18.7500|21.0000|38.2500|34.5000|20.2500|19.2500|21.0000|21.2500|17.7500|
|[1, 3]\|alpha=0\|R=256|11.5469|9.4688|17.4375|9.9531|7.7656|7.4688|8.8438|9.2812|9.0000|
|[1, 3]\|alpha=3\|R=16|48.0000|35.0000|50.2500|57.0000|26.5000|24.0000|31.0000|29.2500|25.5000|
|[1, 3]\|alpha=3\|R=256|8.5312|10.2812|15.9219|8.5312|7.1094|6.9688|8.2969|8.6562|8.6875|
|[4]\|alpha=0\|R=16|20.0000|20.0000|20.0000|20.0000|18.2500|16.5000|18.2500|18.2500|16.5000|
|[4]\|alpha=0\|R=256|6.5469|6.5469|6.5469|6.5469|6.4062|6.2344|6.4062|6.4062|6.2188|
|[4]\|alpha=3\|R=16|18.2500|25.5000|26.7500|31.5000|20.5000|18.2500|22.0000|18.0000|17.5000|
|[4]\|alpha=3\|R=256|5.6562|5.8125|5.6875|6.7031|5.5156|5.5156|6.6094|5.6719|5.5625|

Total/R equals the displayed online/R plus 2 ceil(alpha R)/R, which is 0 or 6
in these cells. Thus paired ABSOLUTE gains in total acquisition equal paired
online gains; their percentage reductions differ when alpha=3. Full unnormalized
costs, terminal planning errors and CPU/wall are in summary.json.

## Paired contrasts

A positive gain is (before-after)/R. Intervals are 4,000 world-paired percentile
bootstrap resamples, shared within a cell, fixed analysis seed763502. n=4 per
cell; intervals are descriptive, unadjusted for all contrasts and unsuitable as
independent confirmation. Every raw four-world vector is in paired.json.

|cell|AF-FO: fusion|FO-FI: allocation|DT-FD: fusion on D|AF-FI: whole change|FD-FI: same-estimator D|
|---|---|---|---|---|---|
|[1, 3]\|alpha=0\|R=16|-1.500 [-3.250, 0.250]|1.000 [-0.500, 2.500]|13.500 [0.000, 36.250]|-0.500 [-1.000, 0.000]|1.750 [-0.500, 4.000]|
|[1, 3]\|alpha=0\|R=256|3.781 [0.312, 9.906]|0.297 [0.094, 0.547]|1.109 [0.000, 3.188]|4.078 [0.406, 10.438]|1.375 [1.281, 1.500]|
|[1, 3]\|alpha=3\|R=16|21.500 [5.500, 49.500]|2.500 [-0.006, 5.000]|26.000 [3.000, 63.500]|24.000 [8.250, 52.750]|7.000 [6.000, 8.250]|
|[1, 3]\|alpha=3\|R=256|1.422 [0.344, 2.500]|0.141 [-0.141, 0.406]|0.234 [0.000, 0.469]|1.562 [0.375, 2.750]|1.328 [1.062, 1.609]|
|[4]\|alpha=0\|R=16|1.750 [-0.500, 4.000]|1.750 [1.000, 3.250]|1.750 [-0.500, 4.000]|3.500 [1.250, 5.000]|1.750 [1.000, 3.250]|
|[4]\|alpha=0\|R=256|0.141 [0.000, 0.422]|0.172 [0.031, 0.312]|0.141 [0.000, 0.422]|0.312 [0.031, 0.688]|0.172 [0.031, 0.312]|
|[4]\|alpha=3\|R=16|-2.250 [-4.000, -0.500]|2.250 [1.250, 3.500]|9.500 [-2.000, 21.000]|0.000 [-1.250, 1.000]|3.750 [3.000, 4.500]|
|[4]\|alpha=3\|R=256|0.141 [0.031, 0.266]|0.000 [-0.094, 0.125]|0.094 [0.016, 0.203]|0.141 [0.031, 0.250]|1.094 [0.938, 1.250]|

## Task allocation and type availability

The no-type pair holds type purchase unavailable and uses the same fused
estimator. Full/no-type contrasts measure enabling type actions within each
allocator. The interaction compares these two type gains. Because changing
purchase choices also changes later task evidence, it does not identify a pure
purchase-timing effect on a fixed task trajectory.

|cell|FON-FIN: task allocation|FON-FO: original type gain|FIN-FI: new type gain|type-gain interaction|
|---|---|---|---|---|
|[1, 3]\|alpha=0\|R=16|3.500 [3.000, 4.000]|1.000 [-1.000, 3.000]|-1.500 [-4.000, 0.500]|-2.500 [-4.000, -1.000]|
|[1, 3]\|alpha=0\|R=256|0.281 [0.094, 0.406]|1.516 [0.953, 1.938]|1.531 [1.406, 1.719]|0.016 [-0.281, 0.453]|
|[1, 3]\|alpha=3\|R=16|3.750 [2.000, 5.506]|2.750 [1.000, 4.500]|1.500 [-1.506, 5.750]|-1.250 [-5.025, 2.500]|
|[1, 3]\|alpha=3\|R=256|-0.031 [-0.438, 0.359]|1.547 [1.344, 1.734]|1.719 [1.375, 2.125]|0.172 [-0.156, 0.500]|
|[4]\|alpha=0\|R=16|1.750 [1.000, 3.250]|0.000 [0.000, 0.000]|0.000 [0.000, 0.000]|0.000 [0.000, 0.000]|
|[4]\|alpha=0\|R=256|0.188 [0.062, 0.312]|0.000 [0.000, 0.000]|-0.016 [-0.047, 0.000]|-0.016 [-0.047, 0.000]|
|[4]\|alpha=3\|R=16|0.500 [-1.500, 2.500]|-2.500 [-4.750, -1.000]|-0.750 [-1.500, 0.000]|1.750 [-0.500, 4.500]|
|[4]\|alpha=3\|R=256|0.109 [0.000, 0.219]|0.156 [0.125, 0.188]|0.047 [-0.062, 0.125]|-0.109 [-0.203, -0.031]|

The following spending is averaged over ALL 32 worlds, and uses counts by
min(T,landmark), carrying a stopped trajectory's terminal paid cost forward.
It creates no missing completed-before-landmark rows and buys no new reports.

|arm|type by min(T,64)|type by min(T,256)|terminal type mean|
|---|---|---|---|
|AF|4.4062|24.3125|140.8125|
|AN|0.0000|0.0000|0.0000|
|DN|0.0000|0.0000|0.0000|
|DT|16.0312|50.3750|216.0625|
|FO|4.1562|21.0938|103.6250|
|FI|3.0625|19.6562|97.9688|
|FD|13.8125|50.6562|215.2188|
|FON|0.0000|0.0000|0.0000|
|FIN|0.0000|0.0000|0.0000|

## Evidence fusion on one observed allocation tape

All variants below use the same Aligned-Full observed prefix and landmark.
The forced-only estimate is recomputed fresh from its deterministic forced
observations. The joint and conditional plug-in estimators receive the SAME
all-data prefix. Masked likelihood variants omit one evidence component without
altering the observed allocation. They are sensitivity calculations, not exact
posterior inference under a coarsened adaptive filtration. Forced-only Brier
uses hard 0/1 point estimates, not calibrated probabilities.

|landmark|estimator|observed/planned worlds|p MAE|q MAE|theta error count|type error count|theta Brier|type Brier|
|---|---|---|---|---|---|---|---|---|
|256|conditional_plugin|30/32|0.0178|0.0412|0.0000|0.0000|0.0000|0.0000|
|256|forced_only_hard|30/32|0.0522|0.0727|0.1667|0.1667|0.0417|0.0833|
|256|joint_32|30/32|0.0181|0.0331|0.0000|0.0000|0.0000|0.0004|
|256|masked_reference_likelihood|30/32|0.0227|0.0423|0.0000|0.0000|0.0000|0.0004|
|256|masked_type_likelihood|30/32|0.0181|0.0329|0.0000|0.0333|0.0000|0.0167|
|64|conditional_plugin|32/32|0.0392|0.0543|0.0625|0.0938|0.0060|0.0492|
|64|forced_only_hard|32/32|0.0531|0.0906|0.3125|0.2812|0.0781|0.1875|
|64|joint_32|32/32|0.0340|0.0410|0.0625|0.0938|0.0065|0.0485|
|64|masked_reference_likelihood|32/32|0.0445|0.0500|0.0625|0.0938|0.0075|0.0521|
|64|masked_type_likelihood|32/32|0.0335|0.0410|0.0312|0.0938|0.0046|0.0506|
|terminal|conditional_plugin|32/32|0.0145|0.0356|0.0000|0.0000|0.0000|0.0000|
|terminal|forced_only_hard|32/32|0.0381|0.0523|0.0312|0.0000|0.0078|0.0000|
|terminal|joint_32|32/32|0.0145|0.0308|0.0000|0.0000|0.0000|0.0000|
|terminal|masked_reference_likelihood|32/32|0.0148|0.0366|0.0000|0.0000|0.0000|0.0000|
|terminal|masked_type_likelihood|32/32|0.0145|0.0310|0.0000|0.0000|0.0000|0.0000|

Landmarks64/256 condition on reaching that budget when not all paths reach it;
the printed denominator makes this explicit. Terminal estimates have variable
horizons and are descriptive. At these prefixes the largest absolute 32-versus-64
quadrature difference across p/q and marginal probabilities is
0.0018835008; it is a numerical sensitivity diagnostic, not an
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
