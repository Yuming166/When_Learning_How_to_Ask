# T1d policy and source audit

## Material Passport

Mode: run/validate, inline audit. 2026-10-31. Read-only inputs: frozen T1a/T1b/T1c public receipts, their source copies, Theory_Note and PROOF_ADDENDUM. No old private seed, confirmation file, training model or Natural source opened. Evidence is local source verification, not an independent external review.

## Historical preservation and previous defect

HISTORICAL_INPUTS.json binds every public byte of T1a (88 including receipt), T1b (100), T1c (108), plus their public trajectory files and relevant proofs. Old code/data/reports/negative findings/receipts stay unchanged. T1c's six wrappers (__init__, bootstrap, policy, preflight, runner, strategies) are copied byte-for-byte along with their dependency tree. The T1c preexecution manifest omitted these wrappers because frozen_paths globbed t1b rather than t1c. The post-start snapshot and final public receipt do not retroactively repair that precommitment. Its original PROVENANCE_DEVIATION remains intact.

T1d local_sources recursively includes ALL Python sources in this experiment: new wrappers/runner/integrity, postprocessing/render/seal, tests, and all vendored sources. Before entropy generation, SOURCE_MANIFEST binds this exact source set, protocols/config, engineering preflight, historical input receipts and runtime fingerprints. Addition/removal/change of a Python file fails verification. Runtime fingerprints cover Python executable/stdlib/native extensions and NumPy/SciPy package sources/native libraries, not all OS facilities. Full checks run before entropy, at run end and final sealing. They do not make numerical integration or the OS formally certified.

## Names, actual policies and common information

T1c 'Original KL' IS Fused-Original + AnalyticReuse, at sqrt update points (d4 B32: 8,11,15,19,24,29). It is not the forced-only Aligned estimator and is not the T2 matched 32-step baseline. T1d KL-AnalyticReuse preserves this policy. KL-OriginalSolver is a separate implementation anchor: same fused estimator and allocation problem but original frozen optimizer. It is not a second statistical objective. KL-Fresh uses AnalyticReuse at every t>=2d including forced rounds.

Fused-Info preserves frozen log-information, one-hot target, sqrt updates and cumulative deficit tracking. Fresh-IG-Lite preserves the actual frozen dense IG, 1e-12 stable score ties, direct action on every FREE round, unchanged forced actions, and no discarded KL work. Belief-Gated preserves T1c sqrt KL backbone plus fresh dense IG, choosing IG if maxIG>1e-14 and (remaining free<=8 or IG(KL proposal)/maxIG<.75), otherwise KL. It may choose IG yet execute the same physical action as the KL proposal. Same total successes never imply equal histories or population equivalence.

All policies receive identical legal reset/calibration/query/type information and the same public R/deadline. Hidden truth/z/generating rates/seed and scoring errors live only in the parent. All have task/type action access, including the worst-fact policy. Type reports have known accuracy .8, not perfect z labels. All use the same order32 approximate fused posterior and joint-theta MAP final decoder; marginal MAP accuracy is scored separately after actions. Offline 2M, task/type each1 are billed. Every deadline is executed separately; no long-path readout substitutes for a deadline-dependent run.

## Controlled granularity and refresh factors

IG-Uniform-Block/Fresh and IG-Fact-Block/Fresh share dense numerical IG, score tie tolerance1e-12, inherited cumulative tracker, available actions, and matched clock. Uniform chooses highest MEAN IG group-format (or individual type) and spreads target1/k within that group-format; Fact chooses best primitive action. All tracker deficit ties use native lowest-index argmax. The factor design is IG granularity x sqrt/fresh, not an artificial full KL x IG x granularity cube.

IG-Uniform-Direct matches Lite's free-round refresh and dense backend. It chooses the highest-mean-IG group-format/type category, and within a chosen task category selects the least-used member/format, lowest index on integer ties. Its task counts within each group-format differ by at most1. Lite selects a single highest-IG primitive action. These are the primary constraint-matched pair. They differ in the within-group constraint and its consequent optimal category/type purchases; downstream histories need not coincide.

The two FixedType controls buy exactly one noisy report per group at the first G FREE rounds (t=4d+g), then choose only task actions under the same dense objective, free-round refresh and granularity constraint. They retain type availability but follow that fixed rule. No further type purchases. This isolates granularity under matched type observations/timing/costs. It does not assert that this imposed schedule is optimal.

Frozen anchors retain their native numerical/tie behavior: Fused-Info uses log IG and exact numpy argmax; KL uses original deterministic LP/deficit rules. They are reference baselines, not used to identify a pure granularity effect. The controlled dense pairs match ties exactly. Converting a frozen anchor to a different near-tie rule would change its policy, so no silent 'fairness correction' is applied. Lowest-index ties mean no claim of full permutation equivariance.

## Why there is no claimed KL-Nonuniform arm

Theory_Note line120 explicitly allows symmetrizing any feasible leading-coefficient allocation over permutations within a group without increasing cost or losing alternative constraints. The frozen solver parameterizes that reduced group-uniform space. Allowing fact-specific weights in the SAME asymptotic KL problem still admits a uniform optimum; selecting a different nonunique optimum would not isolate current fact uncertainty. Weighting KL by posterior fact confidence changes the objective, and splitting a shared group into separate latent types changes the model. Neither is a pure missing factorial cell. We do not implement either and label it 'same KL'. This symmetry is about the asymptotic allocation problem, not finite-transcript optimality.

KL uses posterior p/q means and z marginal MAP in its plug-in allocation; IG integrates predictions about the full theta. Common posterior/evidence does not make these the same functional. Direct/residual execution does not automatically retain old cumulative tracking bounds. No new optimality or stopping theorem is asserted.

## Simple uncertainty alternative and scientific boundaries

WorstFact-MI is separately frozen in SIMPLE_SCHEDULE_ABLATION_PLAN: choose the highest marginal entropy fact, then maximize I(theta_j;Y_a) over ALL available task/type actions. It is untrained, one-step, observes no hidden truth, and is not tuned on the new roster. Forced schedule/decoder/costs remain common.

Policy comparisons are development estimates. Query concentration, >=.95 confidence 'redundancy', and low-confidence unqueried facts are diagnostic proxies, not causal mediation or proof that a query was useless. Shared rates allow an apparently confident fact's response to inform others. Frozen certified terminal gate includes all observations; non-certification is explicitly retained.
