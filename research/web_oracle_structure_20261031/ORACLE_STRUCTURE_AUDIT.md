# Oracle structure: independent proofs and a failed monotonicity lemma

Date: 2026-10-31. The model is exactly the previous `web_unknown_calibration_20261031/MODEL_AND_SCOPE.md`, which is read-only. All statements concern the fixed finite completed-block action menu, known source accuracy \(r\), unknown common extraction levels \(p,q\), the same two labelled calibration streams, and the type-informed oracle. No model calls, training, or empirical benchmark worlds were used.

**Outcome.** A pure-good oracle structure can be proved for two substantial regimes: **zero first-order calibration \(\alpha=0\), with any \(q\ge1/2\); and true \(q=1/2\), with any finite \(\alpha\)**. In both regimes every optimal information allocation has zero first-order weight on bad or mixed blocks. It may still need multiple depths. For \(q>1/2,\alpha>0\), pure-good optimality remains unresolved in this audit. A plausible coordinatewise-KL monotonicity lemma is false; a rational interval certificate below blocks that proof route without refuting pure-good optimality itself.

## 1. Oracle information program and the distinction between format and depth

Align each known good format as A and each true fact as positive. For a block \(e=(n_A,n_B)\) of total depth \(L\), let \(P_{p,q}^{+;e}\) be its true two-count law and \(P_{u,v}^{\pm;e}\) its alternative law. Define
\[
 F_{d,e}(u,v)=D(P_{p,q}^{+;e}\Vert P_{u,v}^{-;e})
 +(d-1)D(P_{p,q}^{+;e}\Vert P_{u,v}^{+;e}).
\]
The exact oracle value can be symmetrized over all facts. With per-fact block counts \(b_e\), it minimizes
\[
 d\sum_e(c+\ell L_e)b_e
\]
subject to
\[
 \alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,v)]
 +\sum_e b_eF_{d,e}(u,v)\ge1
 \quad\text{for every }1/2\le v\le u\le1-\eta.
\tag{1}
\]
The one-truth-flip reduction and existence of an optimizer were proved in the preceding stage. Symmetrization preserves the total mass on blocks containing bad-format reads, as well as feasibility and cost.

For a pure-good block write
\[
 F_{d,L}^{p}(u)
 =D(P_{p,L}^{+}\Vert P_{u,L}^{-})
 +(d-1)D(P_{p,L}^{+}\Vert P_{u,L}^{+}).
\]
It is independent of the alternative bad level \(v\). Thus the pure-good restricted program, allowing any mixture of depths, has constraints
\[
 \alpha[\operatorname{kl}(p,u)+
              \operatorname{kl}(q,\min(q,u))]
 +\sum_{L=1}^{L_{\max}}b_LF_{d,L}^{p}(u)\ge1
 \quad(1/2\le u\le1-\eta).
\tag{2}
\]
Here \(\min(q,u)\) exactly profiles the calibration loss over \(v\). Pure-good **format** optimality means that this program attains the full oracle value. It does not imply that an optimum has only one nonzero \(b_L\), or that the known-rate information-per-cost depth is optimal.

## 2. A common garbling along an admissible alternative curve

Set
\[
 \beta=\frac{2q-1}{2p-1}\in[0,1),
 \qquad v_\beta(u)=\frac12+\beta\left(u-\frac12\right).
\tag{3}
\]
For every admissible \(u\), this alternative level satisfies \(1/2\le v_\beta(u)\le u\le1-\eta\). Consider the binary symmetric channel whose sign multiplier has expectation \(\beta\). It maps a true accuracy \(p\) to \(q\), and simultaneously maps an alternative accuracy \(u\) to \(v_\beta(u)\).

Start from \(L=n_A+n_B\) pure-good responses. Independently apply this additional channel to precisely the \(n_B\) coordinates designated as bad. Under the true state this produces the block's actual mixed law \(P_{p,q}^{+;e}\); under either alternative truth it produces \(P_{u,v_\beta(u)}^{\pm;e}\). This is genuinely a **common stochastic kernel**, depending on the fixed true pair \(p,q\) used in the mathematical comparison but not on which of the two compared distributions generated the data. Therefore
\[
 D(P_{p,L}^{+}\Vert P_{u,L}^{\pm})
 \ge D(P_{p,q}^{+;e}\Vert
              P_{u,v_\beta(u)}^{\pm;e}).
\tag{4}
\]
Unlike an invalid argument that fixes the true garbling while silently allowing arbitrary \(v\), (4) explicitly restricts the alternatives to the admissible curve (3). The calibration consequences of that restriction matter below.

### Strictness for the opposite-truth comparison

If \(n_B>0\), the negative-truth inequality in (4) is strict for every \(u\in[1/2,1-\eta]\).

To prove this, use the full response vectors before aggregating counts. Both pure-good distributions \(P_{p,L}^{+}\) and \(P_{u,L}^{-}\) are exchangeable and have full support. The additional channel on any designated bad coordinate has both transitions positive, because \(\beta<1\). Equality in KL data processing would require the original likelihood ratio to be constant between input vectors differing in that coordinate. Hence it would be independent of that coordinate. Exchangeability then makes it independent of every coordinate: alternatively, its value depends only on the positive count, and independence of one coordinate forces equal values at each adjacent count from 0 to \(L\). It would be constant, giving \(P_{p,L}^{+}=P_{u,L}^{-}\).

That is impossible. The first distribution's response mean is \(\rho(p)>1/2\), whereas the second's is \(1-\rho(u)\le1/2\). Thus opposite-truth KL decreases strictly. Format-specific counts are sufficient before and after the transformation, so the strict statement applies to the actual recorded observations too.

Combining with the non-strict unchanged-truth inequality yields
\[
 \Delta_e(u):=F_{d,L}^{p}(u)
               -F_{d,e}(u,v_\beta(u))>0
 \quad(n_B>0).
\tag{5}
\]
The functions are continuous on a compact \(u\)-interval. For each fixed such block, \(\inf_u\Delta_e(u)>0\). No assumption that \(u\le p\), or that the inner objective is convex, was used.

## 3. Pure-good optimality with zero first-order calibration

**Theorem A.** If \(\alpha=0\), for every fixed admissible \(r,p,q\), every \(d\), finite menu, and source/query costs, all oracle-optimal information allocations assign zero mass to blocks containing bad-format responses.

**Proof.** Suppose an oracle-optimal allocation contains such a block with positive mass. Symmetrize over all facts, preserving cost, feasibility, and positive bad-block mass. For every \(u\), its constraint (1) holds in particular at \(v=v_\beta(u)\).

Replace each block by a pure-good block of the same depth and retain its count. The cost is unchanged. By (5), the new online information is at least \(1+\varepsilon\) for every \(u\), where
\[
 \varepsilon=
 \sum_{e:n_B>0} b_e\inf_u\Delta_e(u)>0.
\]
At \(\alpha=0\), the pure-good information has no dependence on \(v\), so this is uniform slack over the entire original alternative domain, not just the curve (3).

Let \(M=\max_u\sum_L b'_LF_{d,L}^{p}(u)<\infty\) for the replacement allocation. Multiplying its online counts by \(1-\varepsilon/(2M)\) leaves information at least \(1+\varepsilon/2\), while strictly decreasing cost. The factor is positive since the information improvement is bounded by the new online information. This contradicts optimality. Therefore every optimum has zero bad-block mass. ∎

This proof covers \(\alpha=0\) as an asymptotic calibration ratio; sublinear calibration observations are permitted. It proves a statement about first-order allocations. A uniformly correct adaptive procedure may still use sublinear exploration of other formats to estimate nuisance parameters.

## 4. Pure-good optimality when the true bad format is uninformative

**Theorem B.** If the true \(q=1/2\), the same all-optima pure-good conclusion holds for every finite \(\alpha\ge0\).

**Proof.** In this case \(\beta=0\) and \(v_\beta(u)=1/2\). The common garbling replaces each designated bad coordinate by an independent fair sign. For a pure-good allocation, \(v=1/2\) also minimizes the calibration penalty \(\operatorname{kl}(1/2,v)\) subject to \(v\le u\), for every \(u\).

After the same symmetrization and same-depth replacement as in Theorem A,
\[
 \alpha\operatorname{kl}(p,u)
 +\sum_L b'_LF_{d,L}^{p}(u)\ge1+\varepsilon
 \quad\text{uniformly in }u.
\]
For every other \(v\), the calibration term is no smaller and the pure-good online term is unchanged. Thus the uniform slack covers the full alternative domain. The same small scaling of online counts reduces cost while preserving feasibility, contradicting any optimal allocation with bad-block mass. ∎

The two theorems use the entire finite block menu and permit arbitrary depth mixtures. They do not assume that the best pure-good depth is unique or known-rate optimal.

## 5. Why the same argument does not settle positive calibration with q above one half

When \(q>1/2\) and \(\alpha>0\), the curve (3) generally does not minimize the raw low-rate calibration KL. The old mixed allocation is known to satisfy
\[
 \alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,v_\beta(u))]
 +I_{\rm mixed}(u,v_\beta(u))\ge1.
\]
The replacement pure-good allocation must instead handle the smaller penalty
\[
 \alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,\min(q,u))].
\]
The extra online KL from replacement has not been proved to compensate for this calibration difference. Discarding the difference would be an error. Both prior boundary proofs avoid it exactly: calibration disappears when \(\alpha=0\), or the curve and profile coincide when \(q=1/2\).

One valid comparison survives. Let \(K_{\rm pure}(\alpha)\) denote the pure-good restricted oracle coefficient, still allowing mixed depths, and \(K_{\rm full}(\alpha)\) the full oracle coefficient. Then
\[
 \boxed{K_{\rm pure}((1+\beta^2)\alpha)
       \le K_{\rm full}(\alpha)
       \le K_{\rm pure}(\alpha).}
\tag{6}
\]
The second inequality follows from restriction of allocations. A sharper contraction than ordinary data processing proves the first. Let \(T(t)=1/2+\beta(t-1/2)\). Direct differentiation gives
\[
 \frac{d}{du}\operatorname{kl}(T(p),T(u))
 =\frac{\beta^2(u-p)}{T(u)(1-T(u))},
 \qquad
 \frac{d}{du}\operatorname{kl}(p,u)
 =\frac{u-p}{u(1-u)}.
\]
Because \(T(u)(1-T(u))\ge u(1-u)\), integrating from \(p\) to \(u\) gives
\(\operatorname{kl}(q,v_\beta(u))\le\beta^2\operatorname{kl}(p,u)\).
For \(u<p\), the integrand signs and the reversed integration orientation both reverse, yielding the same inequality. Replacing a full feasible allocation by pure-good blocks of the same depths therefore gives
\[
 (1+\beta^2)\alpha\operatorname{kl}(p,u)+I_{\rm pure}(u)\ge1.
\]
At calibration ratio \((1+\beta^2)\alpha\), the actual profiled two-stream penalty is at least \((1+\beta^2)\alpha\operatorname{kl}(p,u)\), so that allocation is pure-good feasible. Its cost has not increased. This compares **different calibration budgets** and cannot be advertised as pure-good optimality at the same positive budget. The sandwich collapses at \(\alpha=0\), and also at \(q=1/2\) where \(\beta=0\), consistently with Theorems A and B. The sharper contraction step was independently proposed by the parent and checked here by the displayed derivative argument.

## 6. A coordinatewise monotonicity route is false

A proposed route was to prove that, with all true coordinate accuracies at least their alternative counterparts, raising any true coordinate cannot decrease
\(D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{+})\), or at least its oracle combination
\[
 F_d(\boldsymbol a,\boldsymbol b)
 =D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{-})
 +(d-1)D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{+}).
\]
Both universal claims are false.

Take exact parameters
\[
 r=19/20,\quad
 \boldsymbol a=(13/20,33/40),\quad
 \boldsymbol b=(13/20,650000001/10^9).
\]
Every true accuracy is at least its alternative counterpart, and the two alternative levels are strictly ordered. Interpreting the first coordinate as bad and the second as good is admissible, for example with \(\eta=1/40\). Exact interval arithmetic certifies
\[
 \frac{\partial}{\partial a_1}
 D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{+})
 <-0.0005024980320364,
\]
whereas the opposite-truth derivative is approximately \(0.977272815713176\). Thus at \(d=2000\),
\[
 \frac{\partial F_{2000}}{\partial a_1}
 <-0.0272207503276.
\]
This is not merely a numerical derivative. The derivative is evaluated as
\[
 \sum_y P'_a(y)\log\frac{P_a(y)}{Q(y)},
\]
where \(P'_a\) is computed exactly from the affine dependence on the first true accuracy, and its entries sum to zero. Logarithms are enclosed by exact rational atanh-series bounds with a proved remainder.

The same certificate also checks a finite change: increasing \(a_1\) by exactly \(10^{-6}\) decreases \(F_{2000}\) by more than \(2.3592333837477\times10^{-8}\). Both the derivative and finite-difference signs are rational interval comparisons, not floating-point finite differences.

Files: `certify_monotonicity_obstruction.py` and `MONOTONICITY_OBSTRUCTION_CERTIFICATE.json`, status `PASS_EXACT_RATIONAL_INTERVAL_CERTIFICATE`.

**Scope of this counterexample.** It invalidates the proposed coordinatewise monotonicity lemma, including its \(F_d\) version for general fixed \(d\). It does not show that replacing the whole mixed block by a pure-good block reduces information, does not show a mixed-format oracle optimum, and does not contradict Theorems A or B. In particular, a local decrease when increasing a coordinate near \(q\) may be followed by a larger increase before that coordinate reaches \(p\).

## 7. Exploratory checks and what remains open

A bounded deterministic grid over the proposed same-depth comparison at \(v=\min(q,u)\), with \(r\in\{.55,.65,.8,.95\}\), \(p\in\{.6,.75,.9\}\), several lower \(q\)'s, \(d\in\{1,2,4,8\}\), and depths two through seven, found no violation. These preliminary calculations are not a certificate of the comparison or of pure-good optimality. Their original inline source, recovered summary output, loop-derived scope, and execution status are preserved in `AUXILIARY_DISCOVERY_PROVENANCE.md`; per-case records were not captured. A separate exploratory pure-depth LP scan was interrupted after the parent supplied a stronger depth-mixture candidate. Its planned scope is retained, its actual completion count is unknown, and no result from that interrupted scan is used here. These auxiliary explorations are separate from the 768 cases of the fully retained main scan.

The parent has completed `DEPTH_MIXING_CERTIFICATE.json`, with status `PASS_EXACT_RATIONAL_CONTINUOUS_DOMAIN_CERTIFICATE`: a feasible mixed-depth allocation costs 34, whereas every allocation confined to one depth costs at least 41.3, including arbitrary format mixtures at that fixed depth. This addresses **depth**, not the unresolved positive-calibration **format** question. This audit agent read the completed status and bounds for the provenance update; it did not independently rerun the depth certificate or audit its full construction in that update. The separate certificate and `DEPTH_STRUCTURE_AUDIT.md` state their own validation scope. Its conclusion is not inferred from the preliminary grids reported above.

The remaining substantive open question is whether every optimal oracle allocation remains pure-good when both \(q>1/2\) and \(\alpha>0\). The common-garbling curve supplies exact boundary results and a calibration-budget sandwich, but not a full theorem. No present artifact licenses importing the known-rate oracle depth rule or asserting a general one-dimensional oracle allocation.
