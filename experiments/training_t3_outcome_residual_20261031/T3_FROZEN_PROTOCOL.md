# T3 — Outcome-Aligned Residual Policy Learning: frozen development protocol

## Material Passport

2026-10-31. Authorized bounded CPU-only training pilot on frozen QRelBench-Exact. Separate branch training/t3_outcome_residual. Historical theory, generators, baselines, results and confirmation sets are read-only. This protocol is frozen before scientific entropy, labels, network fitting and heldout evaluation. All results remain development-only.

## Question and estimand

Can a small residual controller improve complete-vector recovery at B=32 over strong non-trained policies by coordinating task allocation and noisy type purchasing? Reward is 1{joint-MAP theta equals all true bits}. Every task/type observation costs one; offline acquisition costs 2M. B includes both task and type queries. All arms use the same order-32 fused joint posterior, known groups, calibration, s=.8, eta=.05, R=16 and terminal joint-MAP decoder. The prior is the frozen uniform theta/z and continuous ordered-rate triangular prior, numerically integrated by quadrature. It is not exact continuous posterior inference. No true p/q/z/theta, world ID/seed, parameter label, future response or correctness feedback enters deployment features.

## Isolation and denominators

48 TRAIN worlds (12 cells x4), 24 DEV worlds (12x2), 192 TEST worlds (four panels x48). TRAIN and DEV: d4 partitions [1,3]/[2,2]/[4], rates (.85,.60)/(.75,.60), alpha 0/3. TEST: ID; unseen rates (.72,.64)/(.90,.55); unseen d3 partitions [1,2]/[3]; unseen alpha1. config.json contains the complete fixed grid. Three independent random master keys are generated only after source verification; actual QRelBench splits are train/development/test. Indices may repeat across split namespaces but underlying HMAC worlds cannot overlap. No old private seed or reserved confirmation world is opened.

Collect one frozen WorstFact-MI trajectory per TRAIN/DEV world at B32. Extract legal states t16/20/24/28, giving 192 TRAIN and 96 DEV states, not 288 independent worlds. No state-level split. Primary TEST B32 uses all192 worlds. Secondary B16/48/64 each uses the first12 worlds per panel in the prespecified replicate/panel/cell ordering: 48 worlds per budget. These secondary worlds overlap the primary world set and are paired across budgets. All budgets are separate policy runs; no favorable early stopping or continuation-only comparison.

## Pretraining gates

Technical: source/runtime/history closure; common costs/decoder; no hidden-input features; noisy-report update; closed one-step rollout; current-belief immutability; gradient check; scorer row permutation; literal RPC paths and zero-residual equality with frozen WorstFact on d3/d4.

Scientific feasibility for ONE small fit: historical requested-family hindsight oracle headroom >=5pp over WorstFact; at least10% TRAIN states have distinct physical proposals; mean within-state posterior-rollout Q range >=.005; at least one prespecified observable correlation with type-minus-base Q has absolute value >=.10. Correlations use remaining budget, mean fact entropy, mean type entropy, joint MAP mass and posterior rate gap. This weak exploratory gate is not proof of predictability or a valid policy improvement. It authorizes a bounded attempt only. If it fails: stop NO-GO without neural fitting.

## Training and selection

Use K=16 common-random-number rollouts for each enumerated first-answer branch, then frozen WorstFact continuation with the original forced clock. Full remaining horizon to32, never truncate to two steps. Terminal MAP recovery reward and first answer are integrated conditionally to reduce variance. A sampled terminal-reward diagnostic is retained. Exact within the frozen quadrature grid, approximate relative to continuous rates. No test-world hidden values or test outcomes are used for labels.

One shared action-feature MLP (40-32-16-1) per mask (task/type/joint) and seed7101/7102/7103: exactly9 fits,120 epochs each, no hyperparameter sweep. Adam lr.002, batch64, L2 .0001; candidate checkpoints30/60/90/120. Choose each seed's checkpoint by DEV-label MSE, then each mask's seed by DEV episode complete recovery, lower measured CPU, then numerical seed. Freeze hashes before TEST opening. Apply a fixed predicted residual threshold .02. No threshold tuning or actor-critic/PPO stage.

## Comparisons

Seven frozen/fully specified references: WorstFact-MI, Fresh-IG-Lite, Belief-Gated, KL-AnalyticReuse, Fused-Info, Rule-Switch, IG-Fact-FixedType. The last is a strong mechanism control retained prospectively, not renamed as a novel method. Rule-Switch buys one noisy report per group at first free rounds, then alternates WorstFact and Fresh-IG proposals. Residuals use the same legal physical proposal pool and common virtual AnalyticReuse tracker. Task-only retains the base type decision at a given state; type-only fixes the task identity to WorstFact's task proposal; joint learns both. These are action-mask ablations, not guaranteed identical cross-world type schedules after diverging task histories.

DEV: all9 learned fits +7 references,24worlds each. TEST: selected Task and Type plus ALL3 Joint seeds +7 references =12arms x336 world-budget pairs =4032paths. Main selected Joint identity is frozen by DEV. No TEST winner selection. Complete planned actual-world paths:72 collection +384 DEV +4032 TEST =4488. Expected maximum online acquisitions:162048 (verified from roster before launch); fixed cap200000. Simulated counterfactual steps are a distinct training-compute ledger, cap1million; not paid evaluation queries.

## Decision and uncertainty

GO for a WWW enhancement only if the DEV-selected Joint improves B32 recovery by >=5pp over EVERY frozen reference and each paired Bonferroni family7 bootstrap lower bound is >0; no test-panel observed deficit worse than5pp versus WorstFact or the DEV-selected strongest reference; three Joint seeds' B32 accuracy range <=5pp and none below WorstFact; selected Joint worker CPU <=2x WorstFact. The OOD and CPU cutoffs are engineering screens, not formal noninferiority guarantees. Confidence intervals resample complete independent worlds within four fixed panels,10000 paired bootstrap draws, seed63031. Report raw95% and simultaneous family7 intervals. The fixed heterogeneous grid and small development sample limit inference; no population-uniform claim.

Primary comparisons are selected Joint versus seven frozen references. Task-only/type-only and other budgets are explanatory secondary results. Report all seeds, exact paired wins/losses, recovery, task/type/offline/total acquisition, posterior errors, exclusive computation components, total training/labeling/evaluation CPU and wall time, censoring, invalid/incomplete paths and certification outcomes. A fixed budget gives no equal-reliability query-saving estimate.

## Stopping, proof and scope

All paths consume B and call the unchanged certified prototype once at termination using ALL task/type/calibration observations. A refused gate is normal non-certification, not an infrastructure failure. Numerical/model exceptions are separate failures. Only certified output can be called certified. Finite-budget guesses are not delta-correct. The PROOF_ADDENDUM ideal theorem's forced-only estimator, vanishing numerical errors and exact stopping assumptions are not established for this learned policy: no asymptotic-optimality claim. Certification is restricted to the audited arithmetic/model assumptions, not general numerical certification.

Stop after this one pilot, preserving every attempted fit and failure. No automatic retraining, confirmation, GPU, Qwen/LLM/API calls, Web/CRAG/Natural experiments or change to other research lines. A positive Exact result would not prove real language-agent transfer.
