# Independent confirmation — frozen protocol, NOT EXECUTED

**Status: FROZEN_NOT_EXECUTED. No confirmation seed or world has been consumed.** This is a pre-confirmation registration informed by development variability, not a retrospective claim of preregistered development. The final artifact receipt binds this document and source. Execution requires a new explicit decision; no launcher is provided here.

## Fixed scientific contrast and estimand

R=1024, d=4, p=.85, q=.60, eta=.05, known type accuracy .8, alpha=0. Positive-premium partition[1,3]; zero-premium partition[4]. These two configurations were fixed in PHASE2C_PROTOCOL.md before this development batch. Two policies only: frozen Aligned Tracking and D-RRC, same observation interface, paid-action availability, GLR/check schedule and cost accounting. No tuning or additional strategies after confirmation starts. The positive contrast includes Aligned choosing paid type actions; claims must preserve that scope.

An independent world is one statistical unit. Within world i, define D_i=(min(T_Aligned,24576)-min(T_D-RRC,24576))/1024. Lower is better. Both potential stopping streams share private theta/z, calibration and per-action potential response streams; independent worlds have disjoint indices and a fresh evaluator-only master seed. Indices and seed must be outside every development namespace. Freeze and verify all code/protocol hashes before seed generation; the future seed is absent in this phase.

This is a restricted-cost estimand even if no censoring occurs. Retain capped values at24576; never drop a censored or incorrect path. No extrapolation to E[T], no automatic cap extension. Report per-policy completion and any wrong certificate with full denominators. A missing/failed infrastructure trajectory is not ordinary cap censoring: preserve it, mark the confirmation incomplete, and do not silently replace or rerun it.

## Exact planned sample sizes

|Regime|Development pairs|Paired SD(D)|Inflated planning SD|Target effect / equivalence margin|Exact independent worlds|Approx. planning power|
|---|---:|---:|---:|---:|---:|---:|
|positive|8|1.51711|2.27566|0.50|165|0.8012|
|zero|8|0.00000|0.00000|0.25|24|1.0000|

The planning rule was fixed before development outcomes: inflate observed paired SD by1.5; choose the smallest integer n in[24,512] reaching80% approximate power. Positive planning uses a one-sided noncentral-t model for a prespecified mean difference-0.5. Zero planning uses centered t-model approximation for +/-0.25 equivalence. These effect thresholds were not chosen from the observed mean difference. Small development n and possible heavy tails limit this power estimate; the minimum24 is retained even for observed zero SD. An observed identical path does not establish zero variance over all worlds. If no n passes512, planning is insufficient and confirmation must be revised before any seed. No optional stopping or interim efficacy checks.

Planned online hard ceiling across the two policies/configurations is 9289728 actions; alpha=0 implies no offline observations. A separate execution freeze must give a wall allowance and verify resources without changing the estimand, n or cap. That allowance is not permission to execute now.

## Confidence intervals, multiplicity, and decisions

Analyze each configuration separately. Positive claim H0:E[D]>=0 uses a one-sided97.5% paired t upper confidence bound U_pos, allocating family error.025. Declare numerical cost superiority only if U_pos<0. Report paired mean/SD, two-sided95% interval, and relative restricted-cost reduction as secondary. The prespecified0.5 is for power planning, not an additional unregistered success threshold.

Zero control uses TOST with per-test alpha.025: the two-sided95% paired t interval[L_zero,U_zero] must lie strictly within[-.25,.25] to declare equivalence. These two claims have nominal Bonferroni family error<=.05 under the stated t-interval assumptions. Intervals rely on independent worlds and approximate normality of sample means; they are not distribution-free finite-sample coverage certificates. Also report a fixed20000 world-paired percentile bootstrap sensitivity interval using an analysis-only fixed seed763299; it does not replace the prespecified t decisions. Never resample individual responses or count policies as independent worlds.

Overall scientific success requires positive superiority AND zero equivalence AND every planned trajectory recorded AND zero observed wrong certificates. If a positive lower one-sided97.5% bound is>=0, classify the efficacy hypothesis as not supported / unfavorable; if the zero-control interval lies completely outside the equivalence band, classify the zero-control claim as unfavorable. Other crossed or wide intervals are inconclusive. Any wrong certificate triggers failure of the observed correctness guard and a numerical audit; this is not a statistical test of exp(-1024) correctness. More censoring in Aligned cannot be concealed by its restricted cost: if either primary policy has >5% cap censoring in either configuration, overall expected-stopping interpretation is inconclusive even if the restricted metric passes. Infrastructure failure makes the run incomplete, not a negative efficacy estimate.

## Secondary outcomes and claim limits

Report N/R, min(T,B)/R, total acquisition/R, task/type counts, per-policy completion, wrong certificates/all worlds, wall and CPU time, forced fractions, estimator errors, actual solver gaps and beta/R. No multiplicity-adjusted claims from secondary outcomes. No pooling development with confirmation. No extra R, alpha, model, task or baseline selected after seeing confirmation. Preserve all failures and private reproduction records with public checksums.

The proof audit licenses an exact model-level lower bound and conditional ideal achievability. The current float64 sampler has non-certified numerical optimizers and GLR; confirmation can evaluate this frozen numerical policy, but cannot certify its exact risk bound or asymptotic optimality. Positive synthetic cost results do not establish natural-LLM reliability sharing, human effects or universal baseline superiority.

Source development batch: 128 worlds / 640 trajectories. These are excluded from confirmation. Protocol provenance: PHASE2C_PROTOCOL.md, config.json, artifacts/analysis/confirmation_plan.json, FINAL_RECEIPT.json. No new confirmatory seeds used.
