# Computational cost report

## Material Passport

Same 32 development worlds per arm; one active trajectory at a time in cyclic
policy order, single BLAS thread and pre-imported confined workers. Acquisition
wall time 884.276s; evaluator CPU
72.626s. The main hard allowance was 1500s
and 1,200,000 online actions. Logs include all capped paths; no timing outlier
was removed. Worker CPU excludes pool bootstrap and includes sampling/planning,
GLR, gate and RPC handling. Wall includes evaluator/RPC waits.

|arm|n|worker CPU sum s|worker wall sum s|planner CPU sum s|GLR CPU sum s|gate wall sum s|CPU/trajectory s|
|---|---|---|---|---|---|---|---|
|Aligned-Full|32|158.4894|165.0578|153.1445|1.2481|0.5183|4.9528|
|Aligned-NoType|32|184.4988|191.0025|179.2332|1.2514|0.4672|5.7656|
|D-RRC-NoType|32|16.6127|26.1899|0.6205|4.0182|0.9505|0.5191|
|D-RRC-Type|32|13.3021|20.6302|0.7591|3.0921|1.0965|0.4157|
|Fused-Original|32|141.6424|147.1126|137.1566|1.0182|0.4897|4.4263|
|Fused-Info|32|64.5860|69.8825|60.2730|1.0089|0.5327|2.0183|
|Fused-D-RRC-Type|32|16.5322|22.5106|9.8159|1.5482|0.6790|0.5166|
|Fused-Original-NoType|32|165.3330|171.3827|160.6623|1.0865|0.4653|5.1667|
|Fused-Info-NoType|32|59.4773|65.2897|54.9365|1.0597|0.4764|1.8587|

The original allocation arms repeatedly solve the historical cutting-plane LP.
The information arms replace that LP with binary-response information scores,
but still pay joint posterior integration cost. The same-estimator D arm is a
simple computational comparator. Differences in stopping time also affect total
CPU, so this table measures end-to-end policy cost rather than equal-count
estimator speed. Full per-cell CPU/wall/planning/gate fields are in summary.json.

A separate fixed-count probe uses no scientific world or acquisition. The exact
reference clears its integration cache on each repeat; the numerical runs reuse
normal design caches. These measurements illustrate a bounded fixture and are
not a general performance guarantee or an equal-accuracy benchmark.

|operation|fixture|repeats|mean CPU s|minimum CPU s|
|---|---|---|---|---|
|exact_cold|2_targets_2_groups_12_task_reference_obs_2_type_reports|10|0.0075138|0.0074269|
|quadrature_32|2_targets_2_groups_12_task_reference_obs_2_type_reports|10|0.0011395|0.0009742|
|conditional_plugin|2_targets_2_groups_12_task_reference_obs_2_type_reports|10|0.0004189|0.0004018|
|quadrature_64|2_targets_2_groups_12_task_reference_obs_2_type_reports|10|0.0042133|0.0037640|
|quadrature_plus_10_action_information|4_targets_2_groups_fixed_counts|10|0.0412092|0.0404033|

The current numerical posterior enumerates S=2^(d+G) states over K=32^2 rate
nodes, with O(SK) main storage and O(SK+Sd) aggregation. The information pass
uses A=2d+G binary actions and O(A(SK+4^d)) work for the implemented marginal
and pairwise-deviation calculations. Here d=4,G<=2,S<=64,A<=10. This is
practical for this bounded reference problem, not a scalable general-d solver.
Rate-conditional factorization is a possible future optimization, unimplemented
and unevaluated here. The exact alternating-polynomial reference also pays
large-integer rational costs and deliberately caps its observation count.

No GPU, training, Qwen, provider, external model or paid API resources were
used. Statistical acquisition cost and local computation time remain separate
outcomes. Runtime identities appear in RUNTIME.json. The existing gate itself
was unchanged, so any end-to-end gate cost change follows attempt counts and
transcript size rather than a faster certification implementation.

The post-hoc stored-prefix quadrature sensitivity check took8.82s and acquired
zero observations; it is outside the main trajectory timings. Its larger-order
computations did not modify the frozen arm. It found92/92 recomputed action
argmax agreements, with a remaining numerical-accuracy limitation discussed in
the final decision. Report generation, endpoint re-audit and these numerical
probes are local analysis, not additional scientific runs.
