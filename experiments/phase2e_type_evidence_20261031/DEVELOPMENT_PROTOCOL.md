# Phase 2e bounded development protocol

## Material Passport

2026-10-31; new development only; author request Phase 2e. Source snapshot in
SOURCE_SNAPSHOT.json. No prior efficacy data from this stage exist at freeze.

The fixed existing Exact settings d=4,p=.85,q=.60,eta=.05,s=.8 are crossed with
partitions [1,3] and [4], alpha=0 and 3, R=16 and 256. Four independent worlds
per cell: 32 worlds, nine arms, 288 trajectories. All four structural cells are
retained, including the zero-premium [4],alpha=0 cell. This subset bounds R and
compute; no instance is selected using new-method outcomes. Index range
520000..520703 is development only; new evaluator-only entropy seed, independent
of prior and reserved confirmation seeds. The unchanged Exact generator is used.

Nine arms: literal frozen Aligned-Full, Aligned-NoType, D-RRC-Type,
D-RRC-NoType; Fused-Original, Fused-Info, Fused-D-RRC-Type,
Fused-Original-NoType, Fused-Info-NoType. Frozen refers to sampler source;
all arms in this NEW batch use the common certified gate and existing check
schedule max(16,ceil(sqrt(R))). Historical floating trajectories stay historical.
All report and task queries cost one. Offline cost 2 ceil(alpha R) is charged
per policy, also separately report unique shared offline observations.

Fusion: uniform signs/types and uniform ordered rate-triangle prior. Exact
rational reference precedes approximate 32x32 Gauss-Legendre posterior. No type
report is perfect. Fused-Original changes only the estimate used in the original
coefficient optimizer; Fused-D-RRC-Type does the same for the frozen D rule.
Fused-Info maximizes numerical I(theta;Y_action | all past) per unit cost,
updated at the same sqrt(t) cadence, retaining forced exploration and cumulative
tracking. No Bayes-risk stopping; the certified all-data GLR remains common.
There is no new asymptotic-optimality theorem.

Separate observation-controlled diagnostics on the SAME Aligned-Full transcript
at the pre-existing check-grid point at/after 64 and 256 observations, and its
terminal point: forced-only, all-data posterior, no-type posterior,
no-calibration posterior, explicitly conditional empirical-Bayes plug-in;
32 versus 64 quadrature discrepancy. Diagnostic counterfactual withholding
never purchases new observations. Report each landmark separately with full
world denominator; terminal diagnostics are descriptive at variable horizons.

Primary exploratory comparisons use paired min(T,cap)/R; cap=max(2048,24R).
Never drop censored or wrong trajectories. Distinguish cap censoring, arithmetic
undetermined/rejection, infrastructure failure and certificate acceptance.
Report recovery, p/q error, theta/type errors, tasks/types/offline cost, CPU/wall,
planner and certification costs. Paired raw vectors, percentile bootstrap with
4000 resamples and seed763502; exploratory intervals, no multiplicity-adjusted
claim. Terminal correctness at nominal exp(-R) cannot be empirically validated.

Freeze code, this protocol, configuration and historical dependencies before
seed creation. Maximum 1,200,000 online actions; global 1500-second hard limit;
no automatic retries/extension/confirmation, no model/API/GPU/training calls.
If a run fails, preserve partial costs and stop; fixes require a new labeled
engineering revision, and no failed data are silently replaced.
