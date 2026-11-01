# Phase 2c adversarial proof and implementation audit

Date: 2026-10-31. Scope: Task 4, with read-only inspection of the original theory, Phase 2b addendum and alignment matrix, the forced-only sampler and log-risk GLR, and their inherited coefficient/likelihood implementations. No previous approving review was opened before or during this assessment. This is a separate native same-family Codex review, **NOT_CALIBRATED**, not external-expert, cross-model, or formal verification. No venue criteria or novelty assessment is claimed. Historical artifacts were not edited.

## Main judgment

**PASS** for the exact mathematical information lower bound and the algebraic reductions checked here. **CONDITIONAL** for the expected-time achievability claim under the addendum's ideal numerical-oracle and scheduling contract. **GAP** for transferring exact risk control or asymptotic optimality to the finite-precision Python program.

I did not find a counterexample to the addendum's repaired ideal expected-time argument. In particular, concatenating the offline and adaptive online likelihood increments fixes the fixed-offline-event tail problem. This is a substantive mathematical repair. The implementation gap is real: a static, reproducible count array below the stated observation cap makes the floating GLR and its existing heuristic guard accept a crossing that exact arithmetic rejects. That example is far outside the development experiment's scale and does **not** establish an actual violation of its nominal error probability.

Here PASS means that the supplied argument survives this bounded adversarial derivation under the stated model; it is not a machine certificate. CONDITIONAL records explicit ideal-policy premises. GAP records a missing implication, not a claim that the exploratory results are false.

## Component verdicts

| Component | Verdict | Reason and exact boundary |
|---|---|---|
| Stopped-transcript change-of-measure lower bound | PASS | With finite expected cost, bounded log likelihoods justify the stopped KL identity. Adaptive action probabilities cancel. Uniform sign recovery gives the binary data-processing bound. Infinite expected cost already satisfies the lower bound. |
| Within-group symmetrization and one-sign reduction | PASS | The full alternative set is preserved by within-group coordinate permutations. For candidate rates at least one-half, every extra flipped sign adds nonnegative KL. Closure alternatives follow by continuity. |
| Exact weighted Bernoulli inner projection | PASS | Weighted means, pooling when order is violated, clipping to the public domain, and free zero-weight parameters solve the two-block convex fit. This is an algebraic statement, not a statement that floating evaluations have zero error. |
| Finite positive K, local optimizer stability | PASS | A common all-task repair direction gives a strictly positive information increment in a relative neighborhood of the fixed true parameter. Positive costs compactify sublevels. This proves value continuity and upper hemicontinuity without unique optimizers. |
| Nonunique optimizers and averaging | PASS | At a fixed true parameter all optimizers have cost K, so normalization is linear on their cost hyperplane. Their normalized image is convex and compact. Targets need only approach this set, not converge to a particular optimizer. |
| Forced-only estimator, including q=1/2 | PASS | Deterministic forced samples have stream counts proportional to sqrt(t). Fixed positive sign and type gaps give exp(-c sqrt(t)) error bounds. The ordered deterministic grid approaches boundary and interior true rates. |
| Deterministic cumulative-target tracking | PASS in exact arithmetic | The selected deficit rule and forced overrides give the stated maximum, minimum, and L1 discrepancy bounds. The proof must use targets accumulated on every round, exactly as `aligned.py` does. |
| Strictly positive online information against every wrong sign | PASS | Same-type, true-rate single-coordinate alternatives force positive task information even if calibration or type questions are available. Omitting the q=1/2 zero-over-zero ratio is valid. |
| Uniform likelihood concentration with finite calibration | PASS under the ideal allocation event | Center all 2M offline and t online LLR increments together. For t >= (K+epsilon)R, their total length is O(t); bounded increments and a polynomial-size parameter net yield a tail uniform in both t and small delta. No permanently conditioned offline-good event is needed. |
| Tail summation and exchange to expected stopping time | CONDITIONAL | Valid after the uniform tail and uniform check-gap hypotheses hold. It is not a consequence of consistency, pointwise solver convergence, or convergence in probability alone. |
| Anytime delta error bound | PASS for exact GLR | The saturated Beta mixture starts before offline sampling. Ville applies unconditionally over calibration. It does not imply a guarantee conditional on each realized calibration set. |
| Theorem 1 equality/achievability as an algorithmic statement | CONDITIONAL | The real-arithmetic construction requires actual, delta-uniform allocation accuracy, predictable measurable choices, the stated tracking/updates, and exact likelihood comparisons. These are not proved for the Python backend. |
| Oracle scalar coefficient and uniqueness (Theorem 2) | PASS for the mathematical program | The supporting alternative strictly favors good over other-format counts; unequal good counts violate a coordinate constraint. The d=2, alpha=0 boundary needs the supplied derivative argument. |
| Smallest-group zero-premium criterion (Theorem 3) | PASS as a coefficient identity; CONDITIONAL as an expected-cost identity | At oracle cost, task allocation uniqueness forces zero first-order type-action cost. The reversed-group constraint reduces to Gamma, which is nondecreasing with reversed size. Expected-cost interpretation also needs achievability. |
| Log-risk representation at R=1024 | PASS as a finite computation change | `log_glr.py` reconstructs beta from R directly and avoids exp(-R) underflow. It neither changes the likelihood profiles nor certifies rounding. |
| Actual vanishing error of the Python optimizer | GAP | Requested tolerances vanish; fixed LP, feasibility, radial-pad, and gap floors and non-enclosed KL values do not prove actual errors vanish. |
| Exact delta correctness of the floating GLR/guard | GAP | There is no rigorous likelihood/threshold enclosure. The deterministic counterexample below also defeats the external heuristic guard on an allowed input. |
| An infinite-horizon Python asymptotic theorem | GAP | In addition to arithmetic issues, GLR explicitly refuses totals above 2^50, the estimator has finite float resolution, and planner exceptions abort rather than implement a mathematically specified recovery policy. |

## Derivation of the difficult expected-time step

The relevant anchors are Theory Note Sections 4.2–4.3 and addendum Sections 1–5, especially lines 43, 47–66 and 70. I rederived the following rather than assuming the cited review establishes it.

Write x for grouped counts in R units, T for expansion to action counts, and c^T x for query cost. If X* is the true optimizer set, then W* = {Tx/K : x in X*}. For any wrong-sign alternative a, let d_a(w) be online KL per query under w and let D0(a) be the sum of the two offline reference KLs. Feasibility gives

```
alpha D0(a) + K d_a(w) >= 1,    w in W*.
```

The same-type, true-rate alternative flipping coordinate j imposes `a_g A_p + b_g A_q >= 1`, where `A_r=kl(r,1-r)`. Let `B_r=kl(r,1/2)` and take the minimum positive `B_r/A_r`, omitting q=1/2. A wrong sign makes its probability of the true answer at most one-half. Therefore `d_a(w) >= mu > 0` uniformly over all wrong alternatives and w in W*. This argument remains valid with direct type actions, since a same-type alternative gets no information from them.

If actual proportions are within a fixed tolerance a0 of W*, then for t >= (K+epsilon)R,

```
D_t(a) >= R + (t-KR) mu
            - t Dmax a0 - R |M/R-alpha| D0max.
```

Here `D_t(a)=M D0(a)+sum_e N_e(t)d_e(a)` is the compensator, not a log likelihood with means substituted for observed data. Both negative terms can be made smaller than a fixed fraction of the positive slack uniformly over all such horizons. The addendum's choice of tolerances leaves a positive multiple of t. This is the step that would fail if an alternative had zero online information; the preceding margin explicitly rules that out.

For fixed a, concatenate offline and online centered LLR increments in their observation order. Offline sampling is independent and occurs first; subsequent actions are predictable. The centered sum is a martingale with bounded increments because eta is fixed and known type accuracies are fixed strictly between one-half and one. Since M=O(R)=O(t), Azuma at a deviation proportional to t gives exp(-c t), including offline fluctuations. A two-dimensional t^-2 rate net has O(t^4) elements; bounded likelihood and compensator derivatives make interpolation error O(1/t). The finite sign/type union only changes constants.

For the allocation event, deterministic forced estimates at every update in the late portion [rho t,t] have error probability at most `C t exp(-c sqrt(rho t))`. Local upper hemicontinuity transfers accurate estimates and actually accurate optimizer outputs to distance from W*. Delayed updates of age O(sqrt(t)) do not change the late-time argument. Convexity handles switching among multiple optimizers. Early rounds contribute at most 2rho in L1 and the deterministic tracking error is O(t^-1/2). All constants and accuracy moduli must be independent of delta in the asymptotic range.

The boundary correction is at most `|E|log(t+1)+2log(M+1)`, hence O(log t) for all these horizons. Thus, at check times, `P(tau>t) <= C t^A exp(-c sqrt(t))`. A check interval uniformly bounded by o(R) is absorbed by a smaller internal epsilon. The tail sum after `(K+epsilon)R` is bounded by a polynomial in sqrt(R) times exp(-c' sqrt(R)), so it is o(R). Taking limsup first and epsilon down to zero second is legitimate. This supplies the expected-time upper bound under the ideal contract.

The addendum's assertion of finite expectation for each remaining fixed delta is also defensible, with a separate argument: use the optimizer set for its fixed finite alpha_delta=M/R, obtain its positive online margin, and let the online term eventually dominate the now fixed offline contribution and boundary. No uniform-in-delta threshold is needed for that separate finite-expectation claim.

## Assumptions and quantifiers that must remain explicit

The addendum explicitly states the principal mathematical assumptions. A self-contained theorem or paper version should retain the following complete reading of its contract:

1. Fixed finite d and partition; independent fresh responses; common fixed true p>q>=1/2; fixed eta>0; labelled independent offline reference streams with deterministic equal lengths M_delta; M_delta/R -> finite alpha. Known type accuracies, if type actions exist, are fixed and strictly below one. Neither growing-d nor shrinking-gap uniformity follows.
2. Every sampler action, estimate, selected optimizer, and tie rule is measurable from the observed past and the public inputs. Measurability/predictability is used in both martingale arguments but is only implicit in the ideal-policy bullet list. It is easily supplied for this estimator: at each time its grid is finite, so fix a deterministic optimizer representative at each grid point. No continuously varying unique optimizer selection is needed.
3. At each update the optimization problem uses **alpha_delta=M_delta/R**, not a t-dependent ratio M_delta/t. Feasibility and near-optimality refer to the joint continuous alternative set, not merely a finite set of cuts. One adequate actual-error contract is `x_t>=0`, `I_est(x_t)>=1-e(t)`, and `c^T x_t<=K_est+e(t)`, with e(t)->0 independently of delta. Relative errors can be converted locally because K is positive and locally bounded.
4. Accuracy is an actual bound on every accepted oracle output, or a separately proved failure/recovery bound strong enough for expected-time tails. A requested optimizer tolerance and a logged floating residual are not that bound. A rare unbounded computation failure cannot be discarded when claiming almost-sure stopping.
5. Forced-count, update-age, and tracking constants are uniform in delta near the fixed true parameter. The statement on solver-error moduli in addendum line 43 is essential. For example, being exact only after exp(R) for each delta is pointwise convergence but gives no useful allocation guarantee at t proportional to R.
6. Stop checks continue without an experimental censoring cap, with a maximum gap o(R) uniformly over later horizons. At each check the full continuous joint GLR is exact or conservatively enclosed. A proof for an uncapped mathematical stopping time is not a theorem for `min(tau,cap)` or for submission of an uncertified answer at cap.
7. The mixture starts before the offline sample, and correctness is unconditional over it. A frozen offline-data event with failure probability exp(-cM) independent of later t cannot simply be included unchanged in a tail bound summed over all t.

Items 2 and 6 are minor wording/quantifier clarifications for the ideal theorem, not counterexamples to the specified construction. No new assumption that K is finite or strictly positive is needed: the all-task direction and the same-type sign alternative prove those facts. The actual near-optimal-cost contract in item 3 supplies locally bounded oracle outputs, and approximate feasibility with e(t)<1 ensures nonzero cost for normalization. A finite initial period may use the uniform action distribution. No optimizer-uniqueness or positive-calibration assumption is needed. The most consequential missing proof-to-code implications are items 4 and 6. The paper should present the upper bound as an ideal-policy theorem and avoid using Theorem 1's unqualified headline to certify the executable program.

## Adversarial cases and actual gaps

### A. Floating stopping guard is not globally conservative

Evidence anchors: `log_glr.py:12–18`; inherited `phase2a/glr.py:219–240`; `phase2b/policy.py:35–36`. Confidence: 5/5, explicit arithmetic counterexample and reproducible local check.

Use d=1, eta=1/8, no calibration, no type reports, and a count array containing n=1,000,000,000,152 successes in format A and zero other observations. This is a possible finite observation history under the model, and n<2^50. The public eta and domain endpoint are exactly representable. The best sign has exact profile `(7/8)^n`; the best opposite sign has exact profile `(1/2)^n`. The exact gap is therefore `n log(7/4)` and the exact boundary is `R+log(n+1)`.

At the binary64 input `R=559615787992.8533`:

| Quantity | Value |
|---|---:|
| Floating `gap-beta` | 0.0001220703125 |
| Existing policy guard | 0.0000002863102111608155 |
| 100-digit calculation of exact `gap-beta`, using the exact value of that R float | approximately -0.000006563383799368203 |

Thus the floating test and its guard would stop, while the exact rule would not. The profile calculation uses Decimal logarithms with 100 digits; the sign discrepancy is many orders larger than their rounding precision. This is a counterexample to the guard being a mathematical enclosure. It is outside R=16–1024 and is not evidence of any development endpoint being wrong. It also does not by itself show that the program's actual error probability exceeds delta; that would require an analysis of the error event, not just disagreement with a sufficient stopping boundary.

Minimum remedy for a strict implementation risk theorem: conservative bounds for both profile likelihoods and beta, or a proved floating-error bound with a sufficient guard. Reporting `interval_certified=False` is an honest scope statement, not an arithmetic guarantee. The current experiments may continue to report finite-precision behavior with this limitation.

### B. Requested accuracy does not imply actual vanishing oracle error

Evidence anchors: `aligned.py:140–170, 203–214`; inherited `coefficients.py:102–126`. Confidence: 5/5, direct source inspection.

The requested separation tolerance is `min(1e-4,1/(t+1))`, but accepted relative gaps use `max(5*epsilon,5e-8)`. Once t+1>10^8 that gap floor is active. A fixed `1e-7` information residual is accepted; LP primal/dual tolerances and radial information pad are `1e-9`; cuts are deduplicated at 13 decimals. All information values and putative LP lower/upper bounds are floating calculations without enclosures.

These facts do not prove the allocation proportions fail to converge; a common radial scaling can even cancel when counts are normalized. They do prove that the source does not establish premise (iii). Observing small residuals at all executed updates is finite evidence only. Changing the requested tolerance schedule cannot supply the missing uniform actual-error proof.

Minimum remedy for the mathematical claim: keep the ideal oracle assumption. A strict program theorem would additionally need certified feasibility/optimality control or a justified numerical error analysis, plus a specified recovery policy for optimizer exceptions. Neither is required to label bounded experiments honestly.

### C. The machine implementation has no infinite-horizon guarantee

Evidence anchors: `phase2a/glr.py:24–27, 165–168, 195–197`; `aligned.py:44–45, 186–189`; alignment matrix rows concerning numerical floors and GLR arithmetic. Confidence: 5/5, explicit finite limits.

The GLR rejects total observations exceeding 2^50. The ordered floating grid eventually cannot represent distinct adjacent rates. Planner failures propagate exceptions. Cumulative floating targets do not satisfy the exact discrepancy induction without a roundoff analysis. These are independent reasons not to assert an infinite-horizon theorem for the executable as written. The addendum and alignment matrix already acknowledge most arithmetic limitations and are substantially accurate about them; the observation cap and failure behavior should be named when summarizing implementation scope.

### D. Counterexamples to shortcuts, not to the repaired proof

The following attempted attacks are resolved only because the repaired argument includes the relevant conditions:

- **A fixed bad-calibration event:** its probability is constant as later t grows for fixed delta. Summing it as a tail term diverges. The concatenated LLR martingale avoids this error.
- **Pointwise consistency or convergence in probability:** these alone do not control expected stopping time. A generic nonnegative variable equal to KR with probability 1-exp(-R) and exp(2R) otherwise has normalized typical cost approaching K and exploding mean. The actual summable tail rules out this behavior for the ideal policy.
- **An R-dependent late optimizer:** exact optimization only after exp(R) obeys a weak pointwise-in-time statement but can alter the leading cost. The delta-independent e(t) premise excludes it.
- **Nonunique/discontinuous optimizers:** this does not invalidate tracking because W* is convex. Replacing set convergence by convergence to a preferred optimizer would be an unnecessary stronger assumption.
- **q=1/2, alpha=0, or p=1-eta:** no new counterexample appears. Sign and type gaps remain positive at the fixed true instance, and local arguments use relative neighborhoods. The excluded p=q boundary would destroy those gap arguments.
- **Offline-only tight alternatives:** a positive online margin follows from the single-coordinate same-type constraints, so a rare finite calibration outcome cannot permanently prevent eventual separation under the ideal allocation.

## Deterministic verification receipt

Executed once:

```
python experiments/phase2c_strong_baseline_20261031/audit/adversarial_math_checks.py
```

The new script checked 16,388 forced-schedule prefixes, 4,608 exact-rational tracking states with switching targets, 48 projection-domain boundary inputs, and the static floating-GLR counterexample. All assertions passed. Script wall time was approximately 0.151 seconds, excluding interpreter/import startup; the command took approximately 0.624 seconds. These bounded checks supplement the algebra and do not establish infinite-horizon convergence.

Actual experimental resource use: **0 episodes, 0 online actions, 0 offline observations, 0 seeds, 0 optimization calls, 0 model/API/GPU calls**. The rational schedule states are mathematical checks, not benchmark trajectories. No confirmation namespace or private evaluation result was accessed.

## Source identity and read boundary

Read sources include the five requested theory/alignment/sampler files, inherited `phase2a/coefficients.py` and `phase2a/glr.py`, and the stopping/check-spacing portions of Phase 2b policy/runner. Prior mathematical review files and approving reports were deliberately not opened. No prior result was used to choose a mathematical verdict.

| Input | SHA-256 |
|---|---|
| `Theory_Note.md` | `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef` |
| Phase 2b `PROOF_ADDENDUM.md` | `60d6197e4fe6bb35f5a015d42eaf9394b09eb14c8a77a6076647b65b779eb5e6` |
| Phase 2b `ALIGNMENT_MATRIX.md` | `364b64eec92952f5a985a3ba9b87e65b07444fe32d290e59a373194d40d311a7` |
| Phase 2b `aligned.py` | `67bdf86cbd21a81bde81fde981b9c00308f35d2f911af766fbd28939ae5b4ab0` |
| Phase 2b `log_glr.py` | `2e24081b34fa2b783b85fe5d6d73a3e52574e5466f0fe1eb88ca0513de1233ba` |
| Phase 2a `coefficients.py` | `a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f` |
| Phase 2a `glr.py` | `7ed182834957d09546e855468fc14082d894bb54308f3ef728d591d1e4a330f6` |

## Claim boundary for Phase 2c and the paper

The exact lower bound, continuous information program, and coefficient identities are suitable mathematical claims under the model. The expected-time upper bound is supported for the ideal construction when its actual-oracle, predictability, and uniform scheduling premises are retained. I found no new ideal-math counterexample requiring removal of those results.

Finite Python comparisons can test whether information allocation helps beyond the strong baseline. They cannot prove its asymptotic optimum or a tiny nominal error probability, and zero observed errors do not close the arithmetic gap. The proof audit therefore does not block an honestly scoped independent empirical confirmation, but the experimental and variance/censoring readiness decision belongs to the separate protocol review. It does block describing that confirmation as a certification of exact program delta-correctness or asymptotic optimality.
