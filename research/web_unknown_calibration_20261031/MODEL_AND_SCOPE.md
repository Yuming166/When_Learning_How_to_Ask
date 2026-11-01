# Unknown extraction rates and finite calibration: fixed scope

Date: 2026-10-31. New stage authorized after web_cost_sharing_20261031. Both previous theory snapshots, original Theory_Note.md, its expected-time proof attachment, and historical experiments are read-only.

## Scientific question

Which source-cost/shared-format conclusions survive when the two common extraction accuracies are unknown and only finite labelled calibration information is available?

Seek a correct joint information program and matching expected-online-cost theorem for the continuous model, then examine the oracle and zero-premium criterion. A counterexample to importing the known-rate result is a useful outcome. Do not assume a scalar smallest-group formula still exists.

## Fixed experiment

- Fixed d binary truths and a known nonempty partition with group sizes k_g. Unknown type z_g in {A,B} shared within each group.
- Known source accuracy r in (1/2,1). Every new independent source serves exactly one fact and carries a persistent report V equal to its truth with probability r.
- Common UNKNOWN extraction levels 1/2 <= q < p <= 1-eta, with fixed known 0<eta<1/2. No known positive gap lower bound. All asymptotic results are pointwise in fixed true parameters. Use compact closure 1/2 <= v <= u <= 1-eta for alternative infima and likelihood suprema.
- All completed block actions (j,n_A,n_B) with 1 <= n_A+n_B <= L_max are available, with finite fixed L_max. Choose the whole block before observing it; use a fresh root, observe format-specific positive counts, discard the root afterward. Conditional on the report, independent extractions have accuracy p for good format and q for other format.
- Cost per block is c+ell*(n_A+n_B), c>=0, ell>0. No revisits, within-block adaptation, shared source purchases across facts, direct type questions, or empirical model calls.
- Before online work, receive two labelled independent calibration streams X_p~Bern(p), X_q~Bern(q), each of deterministic size M_delta, independent of sources and current truths/types. These are success indicators for extracting known source reports, not evidence that a web source is factually true. Their high/low identities are an explicit reference-experiment information assumption; they reveal no current z_g. Source reliability r is not calibrated here.
- R_delta=log(1/delta), M_delta/R_delta -> alpha in [0,infinity). Calibration is an already acquired common resource; minimize expected ONLINE COST. If every reference observation costs b_cal, report total cost separately as 2*b_cal*M_delta + expected online cost. This additive common cost does not change whether learner and oracle online coefficients coincide.
- Uniform delta-correct recovery of the entire truth vector, almost sure stopping for every admissible state; probabilities include calibration randomness. No conditional-on-every-calibration-record guarantee.
- Oracle knows z only, still does not know theta,p,q, and receives exactly the same calibration, action menu and costs. A known-rate oracle is a different, stronger comparator and must be labelled separately.

## Required outputs and boundaries

1. Full continuous-alternative information lower bound with calibration, including all mixed blocks.
2. Valid finite-delta stopping boundary using full categorical block likelihood; no Bernoulli independence assumption within a root.
3. Matching expected-cost proof if it can be completed; correctly handle nonunique optimizers and variable action costs.
4. Test whether one-truth-flip reduction remains valid for arbitrary mixed blocks and arbitrary alternative levels.
5. Audit whether the unknown-rate oracle still uses only pure-good blocks. Known-rate Blackwell garbling depends on unknown levels and must not be reused without proof.
6. Replace unsupported scalar thresholds by a correct oracle-optimal-set feasibility condition; provide a certified counterexample or exact restricted reduction where possible.
7. Separate alpha=0, finite alpha and coefficient limit alpha->infinity. Match calibration channels and parameter domains in reductions to the original note.
8. Deterministic bounded calculations and focused literature comparison; keep numerical optimizers, grid relaxations and exact certificates explicitly distinct.

No model/API/GPU calls, training, new empirical benchmark worlds, or confirmation runs. Do not claim realistic Web validation or priority of generic controlled-testing machinery.
