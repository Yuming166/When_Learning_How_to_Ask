# T1d — Nonuniform information allocation and robustness

## Material Passport

2026-10-31. Mode: bounded CPU development, run + validate inline using ARS. Branch training/t1d_nonuniform_robustness, base3186587. User authorizes this experiment after gates, not model training or confirmation. Old artifacts remain frozen. No Qwen/LLM API, RL, neural training, paid model, Natural/Web generator changes, or reserved confirmation seed access. Last major Fresh-IG development phase; stop after documented decisions.

## Fixed questions and design

A: does allowing within-group nonuniform fact allocation improve fixed-B full-vector recovery?
B: is Lite better than the strongest predeclared no-training references, rather than just KL?
C: does the direction persist across budgets and held-out regimes?
D: does this exceed standard greedy IG as an independent algorithmic contribution?
E: is there evidence making RL necessary?

Primary comparison: Fresh-IG-Lite minus IG-Uniform-Direct at B32. Both use identical fused order32 posterior, dense joint-theta IG, 1e-12 stable score tie, free-round refresh, forced schedule, action costs and final joint MAP. Uniform constraint implies category mean and balanced within-category execution. IG's granularity x sqrt/fresh 2x2 uses a common cumulative tracker. Type-purchase coupling is tested by the separately fixed pair of FixedType controls. KL nonuniform is structurally not supplied as an artificial equivalent cell; reasons and native-tie anchor limitations are predeclared in the source audit.

14 executed arms: KL-OriginalSolver; KL-AnalyticReuse (the T1c 'Original KL'); KL-Fresh; frozen Fused-Info; IG-Uniform-Block; IG-Fact-Block; IG-Uniform-Fresh; IG-Fact-Fresh; IG-Uniform-Direct; frozen Fresh-IG-Lite; frozen Belief-Gated; WorstFact-MI; IG-Uniform-FixedType; IG-Fact-FixedType. No alias double-counting of T1c Original KL and AnalyticReuse.

## Roster, independence and limits

All R16, known s=.8, eta=.05. Four equally weighted panels, 24 independent new worlds each:

- ID: d4 partitions[1,3]/[2,2]/[4], (p,q)=(.85,.60)/(.75,.60), alpha0/3, 2 replicates per cell.
- OOD-rate: same partitions/calibration; rates(.72,.64)/(.90,.55), 2 replicates per cell. Includes small .08 and large .35 gaps.
- OOD-partition: d3 partitions[1,2]/[3], original two rate pairs and alpha0/3, 3 replicates per cell. This tests a combined partition AND fact-count shift, not a pure partition intervention.
- OOD-calibration: d4 original partitions/rates, alpha1, 4 replicates per cell.

Every world separately executes B16/32/48/64 for all14 arms: 5376 paths, 215040 online actions planned. B32 sole primary; other budgets secondary. Hard cap220000 online and2400 seconds scientific wall. World/order interleaves panel/replicate/cell, budgets and arms cyclically rotate. All arms/budgets share potential-response streams and calibration in a world. Four budgets or repeated groups are correlated; no treating them as separate independent worlds. For d4 B16 is entirely forced (no candidate advantage possible); d3 has4 free rounds at B16. This structural negative control is explicit before execution.

No instance filtering or favorability selection. Development indices1250000+100*cell+rep, a fresh development entropy generated ONLY after SOURCE_MANIFEST and preflight verify. No old/confirmation seed read. Preserved public history can motivate the design but is not pooled with this roster as confirmation. On failure keep partial observations/costs and all planned denominators, do not auto-retry or increase the sample.

## Preflight and complete source binding

Technical gates: contract tests for original/frozen action equivalence on literal streams, group-uniform physical balance, posterior/clock/cost compatibility, singleton target equivalence, worst-fact MI identity, fixed-type timing/cost, hidden-argument rejection. Literal engineering client paths cover every arm, dimension and budget; no QRelBench world/entropy generated. The analysis pipeline must process them without errors. Preflight CPU projects the full bounded run with safety margin; require <=2200 seconds projected against2400 cap.

Freeze ALL new and vendored Python (including analysis/render/seal), config/protocol/source audit/simple ablation/input snapshot/preflight/reference metadata, numerical runtime fingerprints. Test required six formerly omitted wrappers are explicitly present. Hash manifest and document commitment precede artifacts/private/seed.json creation; runner verifies before and after execution. Do not retrofit any T1c receipt. No active-source changes after launch.

## Statistics and full reporting

Primary endpoint: fixed-B joint-theta MAP exact full-vector recovery. Report four-cell paired wins/losses/both, point differences, marginal/per-fact accuracy, joint NLL/Brier, p/q MAE, query counts per fact/group/format and type mix, online/offline/total cost, CPU/wall, invalid/incomplete/noncertified paths. All cells and unfavorable cases retained.

Paired bootstrap20000, seed42031, resampling independent worlds within each of4 panels. This conditions panel totals, allows within-panel case composition variation and is descriptive development uncertainty, not a calibrated universal test for this heterogeneous grid. Cell-stratified bootstrap seed42032 is an explicitly secondary sensitivity; never substitute whichever interval looks better. B16/48/64 and same-world groups are correlated. Raw95% intervals for all contrasts. For Lite against the5 predeclared strong references (KL-OriginalSolver, KL-AnalyticReuse, Fused-Info, Belief-Gated, WorstFact-MI), also report99% Bonferroni-family descriptive intervals (quantiles.005,.995). Do not retrospectively select just the weakest baseline; report the full family and maximum observed recovery with uncertainty limits.

Mechanism factorial effects: nonuniform difference at block/fresh; average nonuniform effect; refresh at uniform/fact and average; difference of refresh effects as interaction. No full KLxIGxgranularity causal attribution. Primary constrained-direct comparison, shared-tracker comparisons and fixed-type pair are reported separately. Do not add trajectory-dependent deltas to claim a unique mediation decomposition.

Fresh posterior diagnostics are recomputed OFFLINE from legal observation prefixes, cached by sufficient state, solely at B32 nonforced task queries for every arm. Never fed back to a sampler or counted as its free planning. Confidence>=.95 queried facts proxy redundancy; terminal confidence<.8 with zero free task queries proxy starvation only when free rounds exist; max free task share>=.5 plus another fact confidence<.8 flags concentration risk. Report continuous HHI, per-fact entropy/confidence, worst-fact entropy, error flags and all thresholds unchanged. Shared-rate information means none of these proxies proves an observation useless or a causal failure. Postprocessing CPU is separately timed.

## Predeclared decision rules

A-main GO: B32 Lite−UniformDirect >=3pp, primary95% lower>0; shared-tracker fresh nonuniform point>=0; ID and pooled OOD each nonnegative; B48/B64 differences nonnegative; complete valid run. If main point<=0 on a complete valid run, NO-GO for this mechanism claim; otherwise unmet gates REVISE. FixedType pair is separately reported for the stronger isolated-task mechanism: its B32 interval must exclude0 positively to support that subclaim; package gain alone cannot supply it.

B strict recovery superiority requires ALL five baseline comparisons99% lower>0. Otherwise 'not established', even if Lite beats KL. Practical-baseline engineering gate separately requires point>=0 and99% lower>=−3pp against every reference. This is a development adoption threshold, not a formal population equivalence guarantee. CPU/Pareto tradeoffs are reported, with no post-hoc rule tuned to winners.

C directional robustness gate: nonnegative Lite−UniformDirect at all secondary budgets and each of4 B32 panels; no partition B32 point harm worse than10pp. Small-panel intervals reported; passing directional gate does not establish uniform robustness. D is source/formulation/limited-primary-literature assessment, not generated by success rates. Lite already maximizes one-step mutual information; claim no new greedy objective without additional mathematical evidence. E no RL training in any outcome; no known remaining beyond-cheap-controller benefit alone implies learned value.

Overall paper judgment separates empirical/practical baseline value from independent method novelty. Positive A/practical results can justify a PROPOSED frozen confirmation protocol; no confirmation run, seed creation or pilot follows automatically. Negative/conditional results remain final scoped findings; no tuning favorable regimes or another major development loop.

## Reliability and computational limits

Order32 posterior and float allocations are approximate, not exact continuous inference or certified plans. Original iid known-s Fraction/Decimal terminal gate covers all observations. Every policy goes to B; any output failing gate is explicitly an uncertified guess/abstention in the reliable-output channel, not a certified answer or an infrastructure failure. No delta-correctness, asymptotic optimality, real-language Agent or Natural transfer claim follows from recovery.

Measure full worker CPU/wall, exclusive posterior/target/controller, terminal estimator and gate, startup timers, parent aggregate CPU, offline analysis separately. Do not sum overlapping legacy planner timers or attribute unmeasured imports/parent costs to a policy. Acquisition costs are fixed by B and M; higher recovery at equal cost is not a measured reduction in cost to equal reliability.
