# Phase 2a: information allocation and theory validation

Development protocol, fixed before any main-run private seed is drawn or trajectory observed. No Qwen/API/GPU calls, training, independent confirmation, protocol tuning after outcomes, or expansion beyond this development batch is authorized.

## Dependency and theory contract

QRelBench v0.1 remains a read-only dependency. It supplies private independent signs, independent group types, deterministic catalog truth, fresh iid PRF Bernoulli responses, finite reference streams and known-s type queries, isolated evaluator/RPC, and baseline samplers. All v0.1 artifacts and earlier experiments remain unchanged. Theory_Note.md remains unchanged. Controlled planted reliability is not natural-language or human reliability evidence.

The unknown true rates satisfy .5 <= q < p <= 1-eta, eta=.05; there is no known positive separation. Calibration M is PER STREAM: M high and M low, so total acquisition adds 2M. Type queries have public known s=.8 and consume the same online budget as task queries. Oracle receives group types only. No learner receives true signs, rates, seed, response correctness, evaluator diagnostics or scenario identity. Reusing the same private episode index across policies and settings enables pairing and does not create independent profiles.

## A/B: coefficients

Solve the joint semi-infinite KL allocation problem for G<=2 with an analytic inner separation oracle (bounded two-rate weighted isotonic fit), full group-type alternatives and one flipped coordinate from each possible group. Nonempty multi-coordinate flip enumeration is independently checked on small instances. Outer cutting-plane LP produces numerical lower bounds and feasibility-scaled upper bounds. Report floating optimization gap, not a formal interval proof. The main phase map does NOT use the Gamma zero-premium shortcut.

Freeze d=16,p=.85,q=.60, partitions [1,15],[2,14],[4,12],[8,8],[16] and alpha=0,1,2,3,5,10. Report BOTH task-only and task+known-s type-query action classes, K_oracle, Gamma, premium and the critical alpha. An independent SLSQP implementation and full alternative enumeration check small cases. These computations are theoretical; no finite-sample discontinuity or empirical asymptotic convergence is inferred.

## C: observable-data tracking development variant

Estimate signs/types/rates from a forced subset of actual task answers, calibration, and actual type-query answers. Use three precommitted coordinate iterations with a vanishing gap projection, recompute allocation every 32 actions after an initial 2d actions, track cumulative allocation deficits deterministically, and force per-stream counts below .5*sqrt((t+1)/d). Use numeric allocation tolerance 2e-6. The proved Gamma shortcut is permitted inside the tracker but not coefficient validation. All estimates, true evaluator-only errors, forced costs, allocations and CPU times are retained.

This implementation differs from the theorem's precise achievability construction. Its original asymptotic proof has not been independently established for these finite engineering choices. Name it Information Tracking (development variant), not a proved asymptotically optimal implementation.

## D: exact mathematical GLR, floating arithmetic

Joint GLR enumerates signs and group types and analytically profiles the two continuous rates over the closed ordered domain. Calibration and actually acquired known-s type reports enter the likelihood. The alternative is every different sign vector. Use the original mixture-style threshold R+2log(M+1)+sum_jm log(N_jm+1)+sum_g log(N_type,g+1). No coordinate stopping is used. Check every 16 online actions; stop only if gap-beta exceeds 1e-8*(1+online+2M). All numeric records retain interval_certified=false: a margin is not a rigorous rounding certificate. Never infer delta-correctness from zero observed errors.

d=4 primary confidence runs; d=6 and d=8 technical probes. No sequential d=16 GLR is attempted. A vectorized exact mathematical joint profile-MLE decoder supports d<=16 only at precommitted fixed-budget endpoints. All six samplers use that same decoder, with the Oracle's known types constrained. Compared with historical v0.1, both decoder and calibration settings differ: historical accuracy percentages are not directly comparable.

## E: bounded development design

All exact settings are in config.json. Six policies: Round-Robin, Repeat-and-Compare, Explore-Then-Commit, Direct Type Query, Oracle Format, Information Tracking. Preserve baseline samplers from v0.1; common terminal and confidence rules are new and identical across samplers.

Fixed budget: d16, five partitions, alpha0 and3, p=.85,q=.60, eight independent indices per cell, B=32,48,64,96,128,192,256. Set planning R=4, hence M=0 or12 per stream. Each trajectory is run once through B256; seven nested endpoint decodes create the curve. Medium/weak coverage uses precommitted (.75,.60),(.60,.55), [8,8], alpha3, four indices each; no post-hoc parameter selection.

Fixed confidence: d4, partitions [1,3],[2,2],[4], alpha0 and3, R=4,16,64 (delta=exp(-R)), two independent indices per cell, online cap2048. Calibration M=ceil(alpha*R). Technical probes d6 and d8, equal two-group partition, alpha3,R4, one index each, cap1024. Controls: q=.5 iid (in model), label-asymmetric and persistent channels (outside model), d4[2,2],alpha3,R4,two indices,cap1024.

Total: 132 jobs/policy, 792 trajectories, at most626688 online actions and3696 endpoint decodes. Global hard caps:650000 actions,3700 endpoint decodes,900 wall seconds, BLAS/HiGHS one thread. No automatic retries or overwrites. On any failure, retain partial logs and action costs from the interrupted job; mark incomplete execution and omit complete-comparison claims. No missing trajectory is silently dropped. Smoke/audit probes are separately identified and do not enter the main batch.

## Inference, cost, uncertainty

Fixed-budget accuracy is exact recovery and correct-fact count at all seven B. Type actions displace task actions. Charge offline2M separately and include total acquisition. Store paired exploratory bootstrap differences at each cell with fixed resampling seed, 4000 resamples, no multiplicity correction. Cell-wise Wilson intervals have n8 or n4; avoid strong significance or superiority claims. Reused profile indices across partitions, alpha, rates and R are not independent replications.

Fixed confidence records completion versus B, wrong certifications by B divided by ALL trajectories, costs conditional on completion, and mean min(T,B) retaining censored paths. Conditional costs are not unconditional expected completion cost; restricted means are not E[T]. Report all denominators, wrong certificates and capped trajectories separately, including every negative control. Primary cells have only two independent profile indices; pooled descriptive plots reuse those indices and label that limitation.

Compare theoretical K and actual restricted online cost/R in separate columns with completion/censoring. Heavy censoring can put the restricted statistic below K without contradicting its asymptotic lower bound. Do not claim convergence from this batch. Persistent and asymmetric controls are assumption checks, not counterexamples to the original model.

## Isolation, provenance, stopping

Use a new 256-bit evaluator seed, private mode700 directory and mode600 seed file. Spawn workers without seed arguments and confine them with Linux Landlock before any public job. Workers receive only public metadata, answers, calibration, type reports and acknowledgement-only snapshot responses. Frozen hashes bind code, tests, config, this protocol, independent audit files and read-only v0.1 source. Seed commitment is public but seed bytes are not exposed. Private reproduction files remain private. This is a local trusted-policy boundary, not a proof against arbitrary malicious code or kernel attacks.

Independent coefficient, GLR and execution reviews are separate same-family Codex reviews; do not describe them as external experts or cross-model certification. Preserve preflight failures and fixes. Verify all prior receipts before/after main execution. After one bounded run, analysis, integrity/replay checks and a report including negative findings, STOP. Confirmation, natural-language experiments and any larger follow-up require a separate decision.
