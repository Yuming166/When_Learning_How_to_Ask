# Existing theory audit and its boundary under provenance dependence

Date: 2026-10-31. Status: mathematical source audit by a delegated same-family collaborator, not a formal verification or independent model-family review. No numerical experiment, model call, training, or historical-artifact edit was performed. This file audits the raw sources directly; it does not rely on another review report.

## 1. Sources and conclusion

Audited sources:

- `/home/gaoym/When_Learning_How_to_Ask/Theory_Note.md`, SHA-256 `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef`.
- `/home/gaoym/.codex/attachments/28232cbe-df30-43d6-ad62-aafa0a112808/Theory_Note_Theorem_1_Expected_Time_Proof.md`, SHA-256 `7012c715c57cdce6e9ca7e8b143a525e35ff3012be38c0d556bfc308f23a3774`.
- The current research-mission attachment was read for proposed extensions; its proposed hierarchical model is not treated as an established assumption of the original theorem.

The original note's actual hash matches the source hash stated in the expected-time attachment. The attachment therefore expands the version actually audited, rather than an unmatched earlier draft.

**Audit verdict:** no mathematical gap was found in the expanded Theorem 1 argument under its stated fixed-instance, fresh-stream model. Its positive-online-information lemma and summable-tail argument address the main expected-time difficulties. The original Theorems 2 and 3 are internally consistent with that model. None of these conclusions validates the finite-precision implementation or extends the result to repeated extraction from persistent, imperfect sources.

**Extension verdict:** a provenance model is a genuine change of statistical experiment. Finite-root saturation is rigorously supportable but is a standard data-processing consequence, not sufficient novelty by itself. The old smallest-group equality cannot be transplanted as a fact-recovery theorem: with finitely many imperfect roots, even a fully type-informed, perfectly extracting oracle has a positive error floor.

## 2. Exact assumptions to preserve

The target is the complete fixed sign vector `theta`, not the latent reports produced by sources. The dimension, known partition, and number of optional type streams are fixed as delta tends to zero. The unknown type is one shared preferred format per known group. Two unknown reliability levels are shared globally:

\[
1/2\le q<p\le1-\eta,\qquad 0<\eta<1/2.
\]

Every action returns a **fresh independent Bernoulli response conditional on the fixed parameter**. Actions may be adaptive; the observation law of an action remains stationary conditional on that parameter. All asymptotic claims are pointwise at a fixed instance. Neither a uniform vanishing-gap statement nor a growing-dimension theorem is claimed.

There are two separately labelled offline streams, each with deterministic size `M_delta`. Their means are specifically `p` and `q`. The labels disclose which calibration stream corresponds to the higher/lower level; they do not reveal the current types or facts. With `R=log(1/delta)`, the theorem assumes `M_delta/R -> alpha < infinity`. The guarantee averages over offline-sample randomness; it is not conditional on every realized calibration dataset. Offline samples are excluded from online stopping time, so total acquisition is a different objective, `2M_delta + E[tau]`.

Optional type answers have an independently established, known accuracy `s_g in (1/2,1)`, are fresh independent observations, cost one, and convey `kappa_g=kl(s_g,1-s_g)` about the type. An uncalibrated self-report does not meet this assumption. The oracle knows only the current types; it remains ignorant of the facts and both channel levels and receives the same offline sample.

The ideal policy uses forced-data consistent estimates, exact continuous profiled likelihood, and an optimal allocation at each estimated instance. The supplied proof does not itself cover a practical posterior estimator, finite precision, heuristic allocation, or a solver with uncontrolled residual error.

## 3. Expected-time proof audit

Write `x` for normalized online counts and `D_0(h,h')` for the sum of the two reference-stream divergences. The program is

\[
K(h,a)=\min_x\left\{\|x\|_1:
 aD_0(h,h')+\sum_e x_eD_e(h,h')\ge1
 \quad\forall\theta'\ne\theta\right\},
\]

with within-group coordinate symmetry, not independent groupwise optimization. Changing common unknown levels changes observations in every group. Summing separately optimized single-group coefficients would discard that coupling.

### Lower bound and reductions

For a stopped adaptive transcript, its KL against an alternative is the offline KL plus expected action counts times fixed per-action KL. Policy probabilities cancel. Uniform correctness and data processing for the event of returning the true vector supply `kl(1-delta,delta)`. This step uses the actual stationary fresh-observation laws.

Within-group symmetrization preserves cost and all alternatives. At fixed alternative types and levels, changing an additional fact sign adds

\[
D(r,1-x)-D(r,x)=(2r-1)\log\frac{x}{1-x}\ge0
\]

because both probabilities lie on the nonadversarial side of one half. Thus exactly one reversed fact suffices for the alternative constraints. This reduction need not survive arbitrary dependent or asymmetric report models.

### Stability without unique optimizers

Uniform sampling of every task stream separates every wrong sign by at least `kl(p,1/2)>0`, locally uniformly around the fixed instance. This gives strict feasibility and bounded optimal counts. Continuity of the KL constraints on their compact alternative set gives continuity of the optimal value and upper hemicontinuity of the optimal set. The normalized true optimal set is compact and convex because all its elements have the same total cost. The proof only requires closeness to this set, not a continuous choice of optimizer.

### The key positive-online-information step

A same-type alternative at the true levels that reverses coordinate `j` forces

\[
x_{j,\mathrm{good}}A_p+x_{j,\mathrm{other}}A_q\ge1,
\quad A_r=\operatorname{kl}(r,1-r).
\]

For any wrong-sign alternative the probability of the true sign on that coordinate is at most one half. Define

\[
\chi=\min_{r\in\{p,q\}:r>1/2}
\frac{\operatorname{kl}(r,1/2)}{\operatorname{kl}(r,1-r)}>0.
\]

Then every feasible allocation supplies at least `chi` online KL against every wrong-sign alternative. When `q=1/2`, omit its `0/0` ratio; its contribution is zero. This is valid and prevents a tight constraint supported entirely by the finite offline sample from spoiling the expected-time upper bound.

### Allocation concentration and likelihood concentration

The explicit square-block forced schedule is disjoint and gives each of the `2d` streams order `sqrt(t)` samples. The sign and type gaps are positive at each fixed instance, so forced-data estimation error is bounded by `C exp(-c sqrt(t))`. A union bound over the last fixed fraction of rounds, convexity of the optimal set, and martingale concentration for action counts give the displayed `Ct exp(-c sqrt(t))` allocation tail. Ignoring offline data in this estimator is permissible; all data still enter stopping.

The Bernoulli likelihood identity in the attachment is particularly useful:

\[
\log\frac{L_t(h)}{L_t(h')}=
M_\delta D_0+\sum_eN_eD_e+
\sum_e(S_e-N_e\mu_e(h))
[\operatorname{logit}\mu_e(h)-\operatorname{logit}\mu_e(h')].
\]

Because all stream means are bounded away from zero and one, one finite sum of residuals controls **all continuous alternatives simultaneously**. No parameter net is needed. Offline residuals fit the same bound because `M_delta=O(t)` at relevant horizons.

The attachment correctly retains the ratio discrepancy `|alpha_delta-alpha| R A_*`; no convergence rate is needed. Positive online information yields a linear margin beyond `(K+epsilon)R`, whereas the stopping overhead is only logarithmic. The tail is summable, establishing finite expectation and the leading coefficient. The additional fixed-delta argument is needed for finite expectation outside the small-delta asymptotic range and is supplied.

### Anytime correctness

The saturated independent-Bernoulli mixture dominates the model likelihood up to the product of stream-count penalties. Including the initial offline sampling period makes its likelihood ratio a mean-one martingale under the true model. Wrong stopping entails a Ville crossing. This proves a marginal, uniform delta guarantee under the model, independently of allocation quality.

**Limit:** that saturated Bernoulli likelihood is not the joint law of repeated outputs sharing a persistent erroneous report. Conditional independence given an unobserved report is insufficient to preserve the original martingale under factual truth alone. A new valid hierarchical likelihood or another valid sequential testing construction is required.

## 4. Oracle and smallest-group claims

The oracle coefficient is `d a_alpha`, with a uniquely optimal task allocation assigning the same first-order good-format count to every fact and no first-order bad-format counts. Its supporting-alternative argument strictly penalizes substituting bad-format counts. The exceptional equal-count argument at `d=2, alpha=0` uses a derivative perturbation; it is included in the note. At `d=1` unequal allocation is not an issue.

The smallest-group theorem checks feasibility of this unique oracle allocation when types are hidden. Finite-information, positive-cost type questions cannot appear at first order if the total cost is exactly the oracle value. Reversed-type alternatives with a reversed fact inside their union produce `Gamma_l(alpha)`, monotone in the union size `l`; the smallest nonempty union is the smallest group. This justifies the necessary-and-sufficient condition, within this experiment.

Preserve its limits:

- At zero calibration, zero premium occurs exactly for one group, despite global sharing of channel levels.
- The entire partition may affect the size of a positive premium.
- Finite-reliability type questions may reduce a positive premium without changing the zero-premium condition.
- A perfect type question is a separate experiment and removes the logarithmic premium with at most `G` extra actions.
- The `alpha -> infinity` statement is a limit of coefficient functions, not an unrestricted joint scaling theorem.
- The displayed calibration example proves existence of nonmonotonicity; it is not a universal shape theorem.

The audit did not rerun the historical numerical certificates or certify their implementation. This report's proof assessment is based on the mathematical arguments.

## 5. Minimal provenance model and exact finite-root obstruction

For one fact, let `theta in {-1,+1}`. Root `r` produces once

\[
V_r=\theta B_r,
\quad \Pr(B_r=1)=\rho_r,
\quad 1/2<\rho_r<1,
\]

where root errors are independent conditional on theta. Every repeated extraction from root `r` is

\[
Y_{r,m,t}=V_rE_{r,m,t},
\quad \Pr(E_{r,m,t}=1)=e_m,
\]

with fresh extraction noise independent conditional on all reports; `e_m` can be the original group's `p` or `q`. A page is assigned to a known root, so duplicated pages share `V_r`. The report is persistent; changing query wording does not redraw it. Source and extraction reliabilities are distinct parameters.

### Proposition 1: finite-root error floor

Suppose only a finite set of `S` imperfect roots can ever be consulted. Any adaptive transcript, including repeated queries, stopping, and its returned answer, is a randomized function of the vector `V` and auxiliary randomness independent of theta. Any side calibration or type streams used here must themselves be independent of theta, with the same nuisance parameters under the two factual hypotheses. Then

\[
D_{\mathrm{KL}}(P_+^T\|P_-^T)
\le D_{\mathrm{KL}}(P_+^V\|P_-^V)
=\sum_{r=1}^S\operatorname{kl}(\rho_r,1-\rho_r).
\]

**Proof:** `theta -> V -> T` is a Markov chain even for adaptive querying and stopping. Apply data processing; conditional root independence factors the report likelihood. The same argument applies to an infinite transcript by the data-processing inequality on the full transcript space. It does not count pages as roots.

Consequently any uniformly delta-correct decision satisfies

\[
\operatorname{kl}(1-\delta,\delta)
\le \sum_r\operatorname{kl}(\rho_r,1-\rho_r).
\]

An exact, sometimes sharper obstruction is the equal-prior Bayes error after observing all reports perfectly:

\[
e_* =\frac12\sum_{v\in\{-1,+1\}^S}
\min\{P_+(v),P_-(v)\}>0.
\]

Every procedure has maximal error at least its average error, which is at least `e_*`. Strict positivity follows because every report vector has positive probability under both hypotheses. For equal `rho`,

\[
e_*=\Pr\{\operatorname{Bin}(S,\rho)<S/2\}
+\tfrac12\Pr\{\operatorname{Bin}(S,\rho)=S/2\}.
\]

This is a standard data-processing/Bayes-overlap result; presenting it alone as a novel information-theoretic theorem is not justified.

### Concrete failure of a transplanted stopping rule

With one root of accuracy `rho=.8`, arbitrarily many informative extractions eventually reveal `V` perfectly. Returning that report still errs with probability `.2`. Even perfect knowledge of the extraction format cannot improve this floor. Applying the original independent-answer likelihood to these extractions can become arbitrarily confident in `V`, thereby violating any advertised factual error bound below `.2`.

This is not cured by putting all facts into one sharing group. Format sharing can remove uncertainty about extraction parameters; it cannot create an additional independently generated root report for a particular fact. Thus the old one-group zero-premium theorem does not establish arbitrarily reliable factual inference in this setting.

### Detectable dependence

For two distinct extractions of one root, encoded as signs,

\[
\operatorname{Cov}(Y_m,Y_n\mid\theta)
=4\rho(1-\rho)(2e_m-1)(2e_n-1).
\]

The same covariance is zero for independent roots conditional on theta. The formula is a direct computation from `V^2=1`. Conditioning matters: with a random theta, marginal correlation between independent roots also contains the shared-truth signal.

## 6. Identifiability: separate three issues

**Single-use composite channels do not identify source and extraction reliability separately.** One extraction from each fresh root has correctness

\[
\bar e=\rho e+(1-\rho)(1-e)
=\tfrac12+(2\rho-1)(e-\tfrac12).
\]

Even labelled factual outcomes identify only this composite mean. For two formats, `(rho,p,q)=(.75,.9,.7)` and `(.9,.75,.625)` both give `(bar p,bar q)=(.7,.6)`. All parameters are better than chance and ordered. Thus fitting effective `p,q` is not an estimate of extraction reliability unless additional information is supplied.

**Repeated extraction can identify the extraction channel, but finite roots retain finite factual information.** For two same-format extractions from the same root, `E[Y_1Y_2]=(2e-1)^2`. Under `e>1/2`, this identifies the positive branch at the distribution level. On a single fixed root, infinitely many extractions can also reveal the report sign and its extraction rate directly from frequencies. This still does not give arbitrarily accurate inference of theta with finitely many imperfect reports.

Do not call the latter obstacle automatically “nonidentifiability”: with known `rho>1/2`, the two marginal report-vector laws are distinct, so theta is identifiable as a model parameter. The obstruction is their positive overlap and the finite amount of independently generated factual evidence in one instance.

**Orientation requires an assumption or anchor.** If root reliability is allowed on both sides of one half with no orientation anchor, the transformation `theta -> -theta`, `rho_r -> 1-rho_r` leaves every observed report/extraction distribution unchanged. This is exact nonidentifiability. Restricting root accuracies above one half removes this symmetry but does not remove the finite-root error floor. Having more fresh independent roots, labelled source calibration, or another anchor addresses different parts of this problem and must be explicitly specified.

## 7. Exact reductions to the original theory

| Proposed setting | Relationship to original experiment | Conditions and limits |
|---|---|---|
| Every root reports truth perfectly, `rho_r=1` | Direct reduction for repeated extractions | The extraction noises must be fresh; groups/types and labelled extraction calibration must match the original assumptions. |
| Target is the latent report `V`, rather than factual truth `theta` | Direct extraction-level reduction | This changes the decision objective. Correct extraction is not factual verification. |
| Every answer uses a new independent root; root accuracy is common `rho>1/2` | Direct reduction through effective levels `bar p,bar q` | There must be enough fresh roots for the asymptotic policy. Two offline streams must calibrate these effective answer levels, not extraction levels alone. No repeated-root dependence remains. |
| A root report is independently regenerated for every query | Same effective-channel reduction | This models new evidence per call, rather than repeated extraction from a persistent Web source. |
| Different actions have different root accuracies | Generally no exact two-level reduction | Effective levels vary by action; the globally shared two-level model and smallest-group formula no longer apply. A new controlled-sensing model may be appropriate. |
| A fixed batch of extractions is taken from each fresh root | An independent block-observation model | Its outputs are mixtures, not the original Bernoulli action streams. General change-of-measure tools transfer, but the old coefficient, isotonic minimizer, and smallest-group proof require new derivation. |
| A finite set of persistent imperfect roots is repeatedly queried | Original factual theorem is false | Uniform arbitrary-delta factual recovery is impossible, even with oracle types and perfect extraction. |

If the new-root cost plus one-query cost is a common constant, the effective-iid reduction rescales online cost by that constant. Action-dependent costs require a cost-weighted program and modified oracle reasoning; the original unit-cost scalar and smallest-group expressions cannot simply be relabelled.

## 8. When source activation costs are first order

A fixed finite inventory incurs at most a constant sum of one-time activation costs, formally lower order relative to `R`. But if all these roots are imperfect and the target is truth, that inventory cannot support the original delta-to-zero guarantee. It is invalid to combine its constant activation cost with a nonexistent successful factual asymptotic regime.

For an unlimited supply of independent fresh roots, let `N` be the number acquired before stopping. Suppose all source accuracies are bounded above by `1-epsilon`, and every acquisition costs at least `c_min>0`. Let `kappa_max` bound their per-root `kl(rho,1-rho)`. For finite expected acquisition count, augmenting the transcript by revealing each acquired latent report at acquisition and applying stopped change of measure gives

\[
\mathbb E_+\!\left[\sum_{r\ \mathrm{acquired}}
 \operatorname{kl}(\rho_r,1-\rho_r)\right]
\ge\operatorname{kl}(1-\delta,\delta).
\]

The augmentation is more informative than the actual extraction transcript; predictable root selection cancels from its likelihood ratio. Therefore

\[
\mathbb E_+N\ge
\frac{\operatorname{kl}(1-\delta,\delta)}{\kappa_{\max}},
\qquad
\mathbb E_+C_{\mathrm{activation}}
\ge\frac{c_{\min}}{\kappa_{\max}}
\operatorname{kl}(1-\delta,\delta).
\]

Activation is then an order-`log(1/delta)` cost. Infinite expected count/cost already satisfies the lower bound trivially. This statement assumes genuinely independent roots and uniform error under both factual hypotheses, not independent-looking pages.

Exceptions are substantive: a perfect source has infinite sign-discrimination KL and can remove the root-count lower bound; a sequence of sources with reliability tending to one has no uniform finite `kappa_max`; activation costs can vanish with delta; and extra side information about theta can supply factual evidence itself. These exceptions must not be suppressed.

## 9. Transfer and claim guidance

**Transfers directly under the exact reductions above:** the original joint coefficient, profiled-mixture correctness, and smallest-group criterion, with the correct effective channel and matching calibration experiment.

**Transfers only as a proof ingredient:** data processing, stopped change of measure, comparisons to a more informative oracle, and cost-aware KL allocation. A hierarchical model requires its actual transcript likelihood and conditional information increments. Repeated actions on an already seen root are not a stationary finite collection of independent Bernoulli streams.

**Becomes false without new assumptions:** arbitrary-delta factual recovery from finite imperfect roots; interpreting independent sampling seeds as independent factual evidence; interpreting a type-informed oracle as a factual oracle; claiming format sharing can remove source error; counting source activation as always lower order.

**Remains an open extension here:** an exact optimal acquisition/extraction frontier with unknown shared formats, persistent roots, and costly activation; an analogue of the smallest-sharing-group criterion; a valid computationally tractable hierarchical stopping certificate. These are not proved by the supplied note or by this audit.

Recommended direction status:

- **GO as a validity boundary:** retain the proven finite-root obstruction and explicit reductions, labelled as standard consequences.
- **REVISE as a new main theorem:** formulate an independent-root block/acquisition problem with a matched oracle and a tractable objective; establish what is new beyond standard controlled sensing before claiming novelty.
- **NO-GO:** reuse the original iid likelihood or coefficient unchanged on repeated extraction from imperfect persistent Web sources.
