# Phase 2c — allocation versus a strong decaying baseline

Development only, 2026-10-31. This document and executable analysis are frozen before drawing this batch's private development seed. Historical theory, experiments and negative results remain unchanged. No confirmation seed is generated or reserved here.

## Question and controlled contrast

Does joint KL allocation improve cost beyond a consistent observable estimator and vanishing exploration? Compare Aligned Tracking, D-RRC, frozen Repeat-and-Compare, Round-Robin, and Format-Only Oracle. D-RRC subclasses the frozen Aligned sampler and replaces only its exploitation-target update: equal coordinate mass on the currently estimated better format. Both retain identical estimator definitions, forced schedule, grid, update cadence, deterministic tracking, decoder, GLR and cost conventions. Their acquired response histories can differ because their actions differ; shared potential streams do not imply pathwise-identical forced estimates.

Both have access to the same offline reference samples and available paid type actions. D-RRC's simple allocation chooses no type actions; Aligned may choose them. Thus the comparison includes whether and how much to buy type information. It is not an isolation of task allocation conditional on identical purchased information. Calibration bits remain available to the common GLR; both allocation estimators deliberately use forced task responses only. No additional computational approximation is introduced in Phase2c.

## One bounded batch

Fixed d=4; partitions [1,3] and [4]; p=.85,q=.60; alpha=0,3; R=16,64,256,1024; known type accuracy .8; public eta=.05. Eight independently generated worlds per cell: 16 cells, 128 worlds, 640 paired policy trajectories. All partition/alpha/R/replicate indices are globally distinct (310000 + 100*cell + replicate); only policies within a world share potential response streams and calibration. R order and policy order rotate deterministically. No cells are dropped according to results.

M=ceil(alpha R) per each labelled high/low reference stream; offline cost=2M, task/type actions each cost1. Check stopping every max(16,ceil(sqrt(R))) actions. Cap B=max(2048,24R), the same for all policies within a cell. Nominal R is used directly in log space. Maximum planned online actions=5,570,560; hard online allowance=5,600,000; wall allowance=1800 seconds; one BLAS thread. No automatic retry, cap extension, parameter search, model calls or confirmation. Any incomplete run is preserved and reported as incomplete.

First run deterministic tests and tiny end-to-end technical fixtures. Only after source and execution review passes is one fresh256bit development seed generated in an evaluator-only private file. It and source/config/audit hashes bind the batch. Technical fixtures and exact replay of existing worlds have separate costs and do not add independent scientific samples.

## Population references and interpretation

Post-run evaluator computes task-only K, task+type K, and Format-Only Oracle K from true p/q. Learners receive none of these. Zero leading premium is [4],alpha=0. Both [1,3] settings and [4],alpha=3 have positive premium under this parameter choice; do not classify all [4] cells as zero-premium.

Main development contrast is paired (Aligned minus D-RRC) online cost/R, with every world retained. Report all16 cells, completion/censoring/wrong certificates, mean min(T,B)/R, total acquisition, and CPU/wall cost. World-level paired bootstrap (4000 resamples, fixed analysis-only seed) gives exploratory95% intervals without multiplicity-adjusted efficacy claims. Censored paths contribute B: this estimates restricted cost, not uncensored E[T]. No completed-only primary analysis. Zero errors cannot verify exp(-1024) risk.

## Offline diagnostics

For every Aligned trajectory retain forced counts, every estimator update, errors in theta/z/p/q, requested and actual floating solver residuals, target/cumulative/actual action counts, final GLR and beta/R, task/type/offline costs, worker CPU and wall time. Offline evaluator additionally compares last estimated and empirical allocation with one true optimizer expanded into labelled actions. Its L1 distance is to this chosen reference, not to the full nonunique optimizer set. Separately compute population minimum KL at actual counts, and the information deficit at K under normalized last/empirical allocations. Do not add these correlated quantities into a causal decomposition.

The historical float64 GLR and optimization are reused exactly. The heuristic stop margin is not a certified arithmetic enclosure; a far-horizon counterexample is documented by the adversarial audit. Actual finite-run residuals do not prove infinite-horizon vanishing solver error or executable delta-correctness.

## Pre-confirmation choices fixed before development results

Future primary R=1024, alpha=0, positive-premium [1,3] and zero-premium [4], selected by theory. Primary outcome is paired restricted online-cost difference/R, B=24576. Positive claim: one-sided superiority; zero control: equivalence within +/-0.25 cost/R. Two claims use Bonferroni error budgets .025 each. Sample-size planning targets80% power for a prespecified positive difference0.5 and zero equivalence margin0.25, using development paired SD inflated1.5, minimum24/maximum512 worlds/configuration. Exact n and any insufficiency are to be reported after development variability is available, before confirmation. No seed, calls, or executable confirmation launch in this phase. Confirmation planning is pre-confirmation registration, not a claim this entire project was preregistered before development.

Independent proof audit distinguishes exact mathematical lower bounds, conditional ideal achievability, and floating numerical behavior. Four-page outline credits established tracking/GLR literature and reserves confirmation placeholders. Stop after the seven requested reports, validated development artifacts, and a readiness judgment.
