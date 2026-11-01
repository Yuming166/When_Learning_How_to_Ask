# Phase 2d P0 — task/type ablation and certified stopping

## Material Passport

2026-10-31; user explicitly chose only the2x2ablation and stopping certificate. Work in branch `phase2d_method_improvement` and this new directory. Phase2c numerical strategy, data, receipt and its unexecuted165+24-world confirmation protocol remain unchanged. No confirmation seed, model call, training, RL, solver acceleration or uncertainty-aware policy is authorized in this stage.

## Frozen question and four arms

Does joint KL allocation help without direct type questions, and how much advantage remains when a competitive simple sampler can buy type information? Four strategies:

|Arm|Joint KL targets|Type actions|
|---|---|---|
|Aligned-Full|yes; literal frozen class|available|
|Aligned-NoType|yes; same class with type allocation removed, c=0|prohibited by evaluator|
|D-RRC-Type|no; uniform estimated-good task target plus active type acquisition|available|
|D-RRC-NoType|no; literal frozen D-RRC|prohibited by evaluator|

All share the forced-only theta/z/p/q estimator, ordered grid, balanced square-block exploration, update cadence, cumulative tracking, reference data, full unknown-z GLR and check/cost conventions. Type reports aid the common GLR; scheduling-only auxiliary likelihood ratios in D-RRC-Type never replace the common estimator. Histories differ under different actions; pairing does not imply pathwise-identical estimates. NoType removes actions, not the nuisance type hypotheses.

D-RRC-Type uses full R-scale type LLR targets, continuously updated known-s uncertainty and estimated remaining task workload. It can buy many reports, with no arbitrary small type-share cap. Type target is NOT reduced merely because a plug-in fact proxy seems confident. One prespecified public-structure guard strengthens the baseline: if G=1 AND M=0, it delegates exactly to frozen D-RRC-NoType. Thus the D-Type/D-NoType tie in that control is by construction, not inferred evidence that type questions never help at finite R. The theorem motivates the leading-order guard, not bitwise equality with the floating Full sampler. All other configurations use the full target. This avoids a weak one-report or prematurely committed baseline. Its rule is a heuristic, may overbuy some groups and has no asserted joint information optimality; full formula and exclusions in TYPE_BASELINE_SPEC.md.

## One bounded development batch

Existing QRelBench iid environment only. Fixed d=4, partitions[1,3] and[4], p=.85,q=.60, alpha0/3, R16/64/256/1024, eta=.05 and known s=.8. Four independent worlds per16cell:64worlds,256trajectories. These are development samples, no confirmatory interpretation. All cells retained; no outcome-based tuning or selection. Globally distinct private indices410000+100*cell+replicate and fresh development seed; policies pair within world only. M=ceil(alpha R) per reference stream, offline=2M per compared policy; unique sampled references separately counted.

Online task/type each cost1. Shared cap max(2048,24R), checks max(16,ceil(sqrt(R))). Planned maximum online=2,228,224; hard allowance2,250,000. Work deadline1800seconds plus cleanup; single BLAS thread, one active trajectory. No retry, replacement seed or cap extension. Preserve partial/failed/missing trajectories if batch incomplete. Before drawing seed, run deterministic and actual confined-worker fixtures, review source/statistical plan, verify353receipt-bound historical files and original theory, and persist source/config/audit hashes.

The primary acquisition batch retains the common **legacy floating stopping rule** so the type ablation changes sampling/action availability only. Full is the exact original sampler; this is not a new certified-policy confirmation. Numerical stopping safety is examined separately after the ablation data are fixed.

## Prespecified measurements and contrasts

World is the independent unit. Report all16cell means of restricted online cost min(T,B)/R, task/type counts, total acquisition/R, completion, wrong certificates/all, estimator errors and CPU/wall. Censored paths contribute B and remain in every denominator; no uncensored E[T] claim. Profile-wise/scientific-world paired bootstrap4000resamples, fixed analysis seed763401, yields exploratory95% intervals; no multiplicity-adjusted effectiveness claims from n4.

Primary policy contrasts, positive value favors the named improvement: (1) D-NoType minus Aligned-NoType, task allocation without type action; (2) D-Type minus Aligned-Full, joint optimization versus type-aware simple rule; (3) Aligned-NoType minus Aligned-Full, type availability within KL policy; (4) D-NoType minus D-Type, type acquisition within simple policy. Report their paired vectors, intervals, and interaction=(3)-(4), not independent-policy SEs. These are effects of four defined policies under the simulator, not additive causal shares of task/type information.

Compute K_no_type and K_with_type separately as evaluator-only references after running. Neither true p/q/z/theta, offline coefficients nor scores may select actions. Keep zero-premium[4],alpha0 separate from positive-premium[4],alpha3; positive premium is not a finite-R superiority guarantee. Retain negative outcomes and runtime costs.

## Certified stopping prototype, kept separate

Target d<=4, total observations<=2^50. Exact rational continuous MLE on the closed ordered-rate domain and exhaustive all signs/types; directed Decimal interval bounds for every profile and the original beta. Interpret binary floats exactly, including exact1-eta and1-s. Only candidate lower minus ALL wrong-answer upper > beta upper can certify. Float GLR may filter candidate times; inability to enclose/cross means continue or abstain, never fallback to a floating success. At cap a scoring-only guess is distinct from a certified output.

Required deterministic checks: old far-horizon false crossing must be rejected, zero-weight/tie/domain/invalid/hostile-context cases, rational-series independent log bounds and exact rational optimality checks. Tests must exercise an undetermined/rejected gate followed by continued sampling and cap abstention.

After the one ablation batch: independently enclose every completed non-Oracle Phase2c terminal state and every new completed ablation terminal state. These are static existing observations,0newworlds/queries. Report passes, rejects, overlaps, precision and CPU/wall; no deletion. Independently recompute every new floating terminal GLR. Exactly replay one existing R64 path per arm in floating mode, plus one existing R1024 path per arm through the online certified gate. If a certified replay crosses later, retain additional calls/delay; do not force identical cost. Replay limit200,000online actions/300seconds work; no new world or seed and no hidden feedback returned to sampler. An exact count array near the crossing supplies a fail-closed refusal fixture even if ordinary observed stops all certify.

The numerical enclosure closes a specific arithmetic implication under the documented Fraction/Decimal/libmpdec and model contracts. It is not a proof of solver accuracy, eventual stopping for every sampler, infinite-horizon executable optimality, nominal tiny-risk empirical verification, or conditional-on-calibration risk control. No sharper mixture boundary is adopted without a separate derivation. Source literature: Kaufmann & Koolen (JMLR2021), https://www.jmlr.org/papers/v22/18-798.html; this motivates the martingale context, not a drop-in boundary replacement.

## Final decision and stopping point

Deliver ablation results/failures, baseline spec, certified algorithm/spec/tests, independent stopping proof audit, data validation/replay receipts, and a method-version decision. If changed strategies/gate are proposed for confirmation, assign a new explicit version and design; do not silently amend or merge into Phase2c's existing protocol. Preserve all353prior receipt-bound files. Stop after Phase2d P0; no Phase3, acceleration or uncertainty pilot.
