# Computational cost

## Material Passport

Bounded CPU development, run/validate inline. New independent roster96; four deadlines on each world are correlated. No RL, neural training, Qwen/model API or confirmation; no Natural/Web generator modification. Full source/dependency/protocol manifest precedes entropy. T1c missing-wrapper defect and old negative findings remain unchanged. This is source-bound descriptive analysis, not an independently rerun efficacy confirmation.


|Policy B32|CPU total/s|wall total/s|CPU median/ms|CPU p95/ms|posterior/s|target/s|controller/s|terminal belief/s|gate/s|type mean|total acquisition mean|
|---|---|---|---|---|---|---|---|---|---|---|---|
|KL-OriginalSolver|65.042|65.858|902.193|974.587|2.445|60.807|0.000|0.333|1.048|1.990|76.000|
|KL-AnalyticReuse|18.539|19.373|196.993|244.542|3.163|13.177|0.000|0.422|1.281|1.990|76.000|
|KL-Fresh|50.354|51.437|533.535|692.847|8.792|39.568|0.000|0.369|1.145|2.042|76.000|
|Fused-Info|23.639|24.480|242.480|383.930|2.209|19.548|0.000|0.373|1.131|1.104|76.000|
|IG-Uniform-Block|6.680|7.509|68.415|113.929|3.326|0.799|0.000|0.558|1.359|1.875|76.000|
|IG-Fact-Block|8.693|9.555|95.853|121.198|4.303|0.965|0.000|0.726|1.838|1.177|76.000|
|IG-Uniform-Fresh|18.101|19.187|178.696|246.627|12.259|3.023|0.000|0.432|1.240|1.677|76.000|
|IG-Fact-Fresh|18.579|19.659|200.282|243.347|12.853|2.882|0.000|0.443|1.248|0.927|76.000|
|IG-Uniform-Direct|13.585|14.525|131.101|194.142|8.660|2.207|0.000|0.469|1.384|1.042|76.000|
|Fresh-IG-Lite|11.312|12.242|124.646|180.551|7.165|1.628|0.000|0.465|1.333|0.875|76.000|
|Belief-Gated|23.919|24.960|263.321|333.874|7.662|12.274|1.793|0.432|1.207|0.875|76.000|
|WorstFact-MI|11.895|12.818|127.838|194.421|7.451|2.201|0.000|0.450|1.345|0.990|76.000|
|IG-Uniform-FixedType|11.316|12.249|125.185|188.299|7.041|1.711|0.000|0.442|1.412|1.625|76.000|
|IG-Fact-FixedType|12.617|13.547|126.373|188.313|8.126|1.799|0.000|0.478|1.422|1.625|76.000|



|Reference / Lite worker CPU ratio at B32|ratio|paired95%|Lite recovery difference|
|---|---|---|---|
|KL-OriginalSolver|5.750|[5.31445386833882, 6.169469372032412]|+5.21pp [-3.12pp, +13.54pp]|
|KL-AnalyticReuse|1.639|[1.5546121808566296, 1.7254457875383216]|+3.12pp [-5.21pp, +11.46pp]|
|Fused-Info|2.090|[1.9946550461973764, 2.186613791011341]|+3.12pp [-3.12pp, +9.38pp]|
|Belief-Gated|2.115|[2.0279401554574563, 2.203115552354936]|-1.04pp [-3.12pp, +0.00pp]|
|WorstFact-MI|1.052|[0.9975021978642131, 1.1064877841165286]|-3.12pp [-7.29pp, +1.04pp]|


Execution status=completed; wall=1447.757s; full worker trajectory CPU=1354.020s; parent aggregate CPU=93.060s; measured kernel warmup CPU=0.462s. Costs including partial={'task': 204915, 'type': 10125, 'offline': 236544}. Source integrity at end=True.

The posterior/target/controller timers are exclusive; legacy planner timers overlap and are not added. Full trajectories include query RPC, observation handling, final estimator and gate. Parent CPU is aggregate and has no defensible per-arm attribution. Python/import work before worker timers and full OS overhead are not completely measured. This is not a full-machine CPU acceleration guarantee. Preflight/analysis are development overhead, reported separately; no GPU training cost exists.

Postprocessing CPU=54.517s and wall=54.522s, including observation-only redundancy replay. These are not online policy costs. Timings concern this machine/d<=4/R16 only; different rate panels, wall load and native implementations limit extrapolation. No cross-batch timing ratio to T1c is claimed.

World-paired bootstrap20000 within four fixed panels, seed42031; cell-stratified sensitivity seed42032 reported separately. Raw95% intervals are developmental; five strong-reference comparisons also have99% Bonferroni-family descriptive intervals. No simultaneous claim for every secondary table. Small strata and a fixed heterogeneous grid limit coverage and external generalization. Same-world budgets/groups are correlated.
