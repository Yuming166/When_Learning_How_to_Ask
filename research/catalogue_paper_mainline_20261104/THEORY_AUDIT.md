# General-catalogue theorem audit for the short-paper mainline

Date: 2026-11-04. Status: independent scoped same-family mathematical audit,
based on the named local sources; not external peer review, a priority review,
or proof-assistant verification. No experiments or model calls were run. The
source theory, code, manuscript, and historical results were not changed.

## Verdict

**The structural theorem is usable as the principal theory contribution.** I
found no mathematical counterexample or invalid step in the general equality
criterion, two-rate elimination, unsaturated binding/face restriction, or the
unique-cover example under their stated assumptions. The proof needs a more
explicit strict data-processing argument for good-only oracle necessity; the
companion supplies it. The generic expected-time result is an ideal-policy
framework specialization, not a theorem about the current executable policy.

The cleanest four-page claim is a structural statement about the **additional
leading query cost of learning reliable question formats when only the final
recommendation must be correct**. It is not a theorem that a particular finite
implementation beats IG.

## Audited sources

- `research/general_catalogue_theory_20261103/GENERAL_THEOREM.md`.
- `research/general_catalogue_theory_20261103/CATALOGUE_EXAMPLES.md`.
- `research/general_catalogue_theory_20261103/UNSATURATED_DERIVATION.md`.
- `research/top1_decision_theory_20261103/THEORY_RESULTS.md`.
- `research/original_expected_time_proof_20261031/EXPECTED_TIME_PROOF.md`.
- `experiments/phase2b_alignment_20261031/PROOF_ADDENDUM.md`.
- `Theory_Note.md`, for the model, lower bound, estimator, and mixture gate.

## 1. Scope that must appear with the main theorem

The theorem fixes a finite number of binary preferences, a known partition,
and a known finite-output decision map. A finite affine catalogue is an
application; its winner must be unique at **every** sign vector in the full
allowed cube. The fixed true state has common unknown symmetric accuracies
`1/2 <= q < p <= 1-eta`, `eta>0`, arbitrary unrestricted group format types,
unit-cost coordinate-format questions, and fresh conditionally independent
replies. The oracle is told types only and remains ignorant of rates and
preferences. No direct type-report action is available.

The calibration regime is `M_delta/log(1/delta) -> 0` for **each** labelled
reference stream. It includes `M=0` and genuinely sublinear calibration; it
does not mean that rates are known. The coefficients are pointwise in fixed
rates and fixed dimension. Uniform correctness ranges over the original
instance domain, but the asymptotic efficiency statement is not uniform as
`p-q` or `p-1/2` vanishes.

Constant decision maps have coefficient zero and are excluded from reciprocal
formulas. For a nonconstant full-cube map, every root has a nonempty minimal
wrong-decision family, and its cover value is strictly positive.

## 2. Checked proof components

| Component | Audit result and required wording |
|---|---|
| Minimal wrong-flip reduction | Valid. A wrong flip set contains an inclusion-minimal wrong subset. Adding flips increases each KL term because true reliabilities and candidate rates are at least one half. Monotonicity of the decision map is unnecessary. Keep all minimal wrong subsets, not just singletons or one competitor. |
| Oracle coefficient | Valid at zero calibration: `K_or=1/psi_p(rho)`. This is an unknown-rate oracle; replacing it by the known-rate formula changes the comparison. |
| Every oracle optimum is good-only | Valid with a strict BSC contraction argument. Weak data processing alone is insufficient to infer necessity; the companion explicitly establishes strictness whenever positive other-format mass is used. |
| General rate elimination | Valid for good-only oracle-cost candidates. Candidate types partition groups into exactly two common-rate pools. Independently fit the two pools and exchange their labels to satisfy the rate order. This does not permit a separate rate for every group. |
| Equality iff explicit entropy cuts | Valid. Equality forces an unknown-format optimum to be oracle-optimal and good-only; at that cost, the entropy cuts are exactly the remaining feasibility constraints. Compactness converts failure of feasibility into a strictly positive coefficient gap. |
| Independence from true q | Valid only for the zero-versus-positive boundary at zero calibration and strict `q<p`. The size of a positive premium may depend on q. Finite-query behavior and positive-calibration boundaries are not covered. |
| Sorted prefix evaluation | Valid for a fixed proposed weight, since the high-versus-low pool cost difference increases with group flip fraction. The sorting depends on the weight. It is not a globally fixed list of only `G+1` constraints. |
| Binding balance | Valid for `rho<1/2`: any used group imbalance on a binding flip forces strict entropy loss, even if another pool is in the flat part. Binding balance alone is not sufficient; retain nonbinding cuts. |
| Oracle-face dimension | Valid. Normalized group restrictions yield `L-1` independent tangent directions preserving all active constraints and zero coordinates. The dimension obstruction is necessary, not sufficient. |
| Unique-cover corollary | Valid in the unsaturated regime. Zero premium iff the support of the unique cover-optimal weight lies within one group. Do not omit the regime or replace support by all coordinates unless the optimizer has full support. |

The paper should reserve “oracle-optimal” carefully: below saturation the
cover-LP optimum and the coefficient-optimal normalized coordinate weights
coincide. Above saturation, the complete oracle-optimal set is all weights
whose minimum cover is at least one half, which can be larger than the
max-cover face. A unique max-cover weight above saturation is not enough to
invoke the unsaturated uniqueness corollary.

## 3. Closed versus strict rate domains

True instances satisfy strict `q<p`; the alternative optimization uses the
compact closure `1/2 <= v <= u <= 1-eta`. This is legitimate because every
boundary alternative is a limit of admissible strict alternatives, and all
Bernoulli means and complements remain in `[eta,1-eta]`. KL and likelihood
values are continuous there. Equal fitted rates, especially `(1/2,1/2)`, can
be essential least-favorable **limits**. Excluding them numerically would
produce an incorrect coefficient. Conversely, this closure does not claim
that a uniformly terminating identification procedure exists at an actually
uninformative true state `p=q=1/2`.

The pure-good pool fit is `max(1/2,p-(2p-1)s)`, never above true p, so the
upper cap is respected. Swapping pool labels is allowed because candidate
group types have no cross-group restriction. Both points should remain in
the proof; a model with constrained types would need a new argument.

## 4. General framework attainability: what extends and what does not

The lower bound changes its target event from returning the full profile to
returning the true item. Every wrong-item alternative still imposes the
stopped-transcript KL bound. The minimal-flip reduction above gives the
decision information program without groupwise coordinate symmetrization;
the decision geometry generally destroys that old symmetry.

The original ideal forced-only estimator and repaired joint-concentration
argument extend with these explicit substitutions:

1. Replace wrong-profile alternatives by wrong-item alternatives, and use the
   full ungrouped nonnegative coordinate-format allocation cone.
2. The all-task direction is still uniformly strictly informative locally,
   since any wrong item requires a flipped coordinate on a true good stream.
3. A feasible allocation must satisfy, for each minimal wrong set F,
   `sum_F[a_j D(p,1-p)+b_j D(q,1-q)] >= 1`, by the same-type alternative at
   true rates. Any larger wrong flip contains such an F. Therefore online
   information against every wrong-item alternative is at least a fixed
   positive multiple of this bound. Omit the zero/zero q term when q=1/2.
4. Compact optimal sets, local strict-feasibility repairs, vanishing actual
   solver errors, forced-only estimator concentration, and cumulative tracking
   then give the same summable tail beyond `(K+epsilon) log(1/delta)`.
5. Initialize the saturated mixture before calibration and jointly concentrate
   offline/online increments. Do not condition forever on one calibration-good
   event with fixed positive failure probability.

These steps support the **ideal-policy pointwise** coefficient interpretation.
The general-catalogue files largely cite the repaired proof rather than
repeating its complete tail argument; the paper can state the specialization
and point to a proof companion. It should not present an undocumented finite
implementation as the attaining policy.

The current practical KL allocator uses all-task MLE, fixed float tolerances,
and finite solver caps. Its interval gate can be valid while its allocation
fails the vanishing-actual-error/forced-only tracking contract. Certification
of outputs and asymptotic efficiency of allocation are independent properties.
Order-six IG, Monte Carlo planning, exact short-suffix Bellman diagnostics,
and fixed-R experiments likewise do not prove asymptotic attainment.

## 5. Certification instantiation

Maximize likelihood **within** each item class and compare the best class to
the best different-item class. Do not sum class likelihoods or compare a MAP
posterior with the confidence threshold. On a wrong certified item, true
likelihood belongs to the competing class, so the original saturated
Beta-mixture/Ville bound applies to any predictable action policy. No union
bound over all rate values or catalogue items is needed.

Conservative interval evaluation and common delayed checkpoints preserve this
error bound; they need not stop at the earliest ideal crossing. For ideal
expected-time optimality, check delays must have the stated asymptotically
negligible size and arithmetic/solver errors must obey their own contracts.
“The stopping rule is delta-correct” does not imply “the implementation is
asymptotically optimal” or “the agent is more efficient than IG.”

## 6. Catalogue example and recommended paper emphasis

The three-item catalogue is a clean illustration. Its utility residues
modulo four are distinct, so all 64 states have unique winners. The displayed
primal/dual weights have exact cover value `5/13`; every dual-positive edge
is tight and their incidence equations uniquely force
`(3,2,2,1,1,4)/13`. This optimizer has full support. The unsaturated corollary
therefore implies zero premium exactly when all six coordinates share one
group. A proper partition has strictly positive premium for every allowed
strict pair `q<p`, without relying on floating numerical optimization.

The unequal-weight two-item controls also check out: the unsaturated example
has a one-dimensional oracle face, while the saturated example has equal-size
partitions with different group certificates. They illustrate why a smallest
group-size statistic no longer characterizes recommendation cost.

For four pages, prioritize the general entropy-cut criterion, the compact
unique-cover corollary, and one small genuine catalogue. The rate-dependent
antichain transition and broader counterexamples are useful companion results,
but including every theorem would obscure the main argument. Numerical
coefficient values remain floating diagnostics; exact zero/positive claims
come from the analytic proof. Controlled Bernoulli mechanisms are not evidence
that real users or Web recommendation systems obey this response model.

## 7. Required claim limits for a submission-ready draft

- Describe a decision-specific **leading reliability-learning premium**, not
  a universal gain from recommendation over profile recovery.
- Attribute generic change of measure, tracking, mixture stopping,
  fractional certificates, convex perspectives, and ordered clustering as
  existing tools; the structural boundary is the proposed new consequence.
- State all comparison oracles and calibration resources explicitly.
- Treat the practical certified loop as an instantiation/mechanism test unless
  its stronger attaining-policy contract has separately been established.
- Keep negative finite-method comparisons to strong IG visible. They neither
  refute the structural theorem nor become positive evidence by changing the
  comparator's information or certification opportunities.
