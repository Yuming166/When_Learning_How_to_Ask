# Phase 2a independent coefficient review

## Material Passport

- Scope: `Theory_Note.md` Sections 1–6 and 8; independent numerical verification of the coefficient reduction and the requested d=16 phase boundary.
- Status: VERIFIED FOR THE BOUNDED NUMERICAL CHECKS BELOW. This is not an independent proof approval of the full expected-stopping-time theorem or a novelty review.
- Date: 2026-10-30. All computations are CPU only. No model, API, GPU, Qwen, trajectory pilot, or confirmation experiment was run by this review.
- Independent implementation: `audit/independent_coefficients.py`. The file contains no parent solver import. Its optimizer uses continuous two-dimensional inner SLSQP and a nonlinear outer SLSQP, rather than the parent's analytic isotonic separation and cutting-plane outer LP.
- The final parent comparison was performed only after the independent implementation and first results existed. Python 3 environment: NumPy 2.5.3; SciPy 1.18.1. The independent domain uses eta=.01; all nondegenerate fitted means are <=p, so eta=.05 yields the same values for these p<=.85 examples.

## Result

The user's rounded Gamma table and critical alpha=2.0432 are supported. The independently obtained crossing is **2.04316024691419**. For [8,8], alpha=2 is still on the positive-premium side; alpha=3,5,10 are on the zero-leading-premium side. For [4,12], every requested alpha remains on the positive-premium side. These statements concern coefficient programs and Theorem 3, not finite-budget recovery rates or experimentally observed asymptotic convergence.

The independent small-instance coefficient optimizer agrees with the parent solver in all seven checked settings. Both direct-type-disabled and finite-s=.8 direct-type-enabled action classes were checked. The distinction changes positive-premium coefficients and optimal allocations; it does not change the finite-s zero-premium criterion.

## Inner projection derivation and assessed implementation

For a type-reversed group set J and one reversed sign in group h, complement the true Bernoulli mean for that sign. Since D(r,1-x)=D(1-r,x), the original KL objective becomes a constant plus

\[
-S_u\log u-(W_u-S_u)\log(1-u)
-S_v\log v-(W_v-S_v)\log(1-v).
\]

Writing e_g=1{g=h}, the weights and success totals are

\[
\begin{aligned}
W_u&=\alpha+\sum_{g\notin J}k_ga_g+\sum_{g\in J}k_gb_g,\\
S_u&=\alpha p+\sum_{g\notin J}[k_gp+e_g(1-2p)]a_g
                 +\sum_{g\in J}[k_gq+e_g(1-2q)]b_g,\\
W_v&=\alpha+\sum_{g\notin J}k_gb_g+\sum_{g\in J}k_ga_g,\\
S_v&=\alpha q+\sum_{g\notin J}[k_gq+e_g(1-2q)]b_g
                 +\sum_{g\in J}[k_gp+e_g(1-2p)]a_g.
\end{aligned}
\]

The optional type term is constant in (u,v). Each positive-weight coordinate is strictly convex, with unconstrained minimum S/W. If individually clipped means satisfy u>=v, they solve the constrained problem. Otherwise the active order constraint u=v gives the pooled mean (S_u+S_v)/(W_u+W_v), clipped below at .5 and above at 1-eta. The upper clipping cannot be active for these information problems unless the true p itself reaches that bound. Zero-weight parameters can be chosen arbitrarily subject to order and bounds; their minimizer need not be unique. The parent's `fit_ordered` and `inner` implement this projection consistently with these formulas.

Independent check: 240 randomized inner problems, seed 7731030, G=1 or 2, group sizes 1–3, p uniform on [.56,.94], q uniform on [.5,p-.01], alpha in {0,1,3}, and optional s=.8. The set includes exact zero allocations and completely zero online counts. Parent analytic objective versus direct continuous SLSQP objective:

- Maximum absolute difference: **1.637578961322106e-13**.
- Independent inner failures: **0/240**.
- Maximum conservative convex-tangent optimality envelope: **1.166899417037737e-6**. This is deliberately wider than the observed objective difference.

No parent projection function is used inside the independent optimizer.

## Requested d=16 coefficients and phase indicators

Fixed p=.85, q=.60; each offline stream contributes alpha times log(1/delta) observations. Thus total offline observations are 2M, not M. Gamma was computed using independent scalar minimization over w, and the oracle root used an independently minimized continuous two-parameter objective.

| alpha | K_or | Gamma_1 | Gamma_2 | Gamma_4 | Gamma_8 | Gamma_16 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 14.5125336719 | .2452963705 | .4905927409 | .7541871343 | .9104580794 | 1.0000000000 |
| 1 | 14.4236095592 | .2639288548 | .5005807925 | .7591916076 | .9608780729 | 1.0978732460 |
| 2 | 14.3450262990 | .2827361242 | .5040711853 | .7611974909 | .9985886901 | 1.1815236864 |
| 3 | 14.2751936584 | .3016912998 | .5052545401 | .7617420630 | 1.0276833502 | 1.2537719497 |
| 5 | 14.1568020559 | .3276423771 | .5051142943 | .7608920957 | 1.0692534878 | 1.3720886769 |
| 10 | 13.9460724317 | .3479916250 | .5016552851 | .7560372362 | 1.1247982496 | 1.5709634890 |

The independent Gamma minimizer differs from the quoted closed-form w_k by at most 5.57e-9 over this table. The oracle root objective residual is at most 1.6e-15; its inner convex-tangent envelopes are <=2.28e-7. These floating numerical residuals are not interval-arithmetic certificates. The value 2.04316024691419 supports the reported critical point to four decimal places; extra printed digits document agreement, not a formal claim of corresponding certified accuracy.

All ten user-supplied Gamma values at alpha=0 and 3 round correctly to three decimal places. The Gamma_8 crossing residual is 6.7e-16 in the independent computation. Monotonicity of all Gamma_k in alpha was not assumed: Gamma_2 and Gamma_4 already illustrate why general monotonicity should not be inferred from the phase plot.

## Arbitrary sign-subset and type-pattern enumeration

For fixed levels and type pattern, deleting all but one of the reversed signs weakly decreases KL because

\[
D(r,1-x)-D(r,x)=(2r-1)\log[x/(1-x)]\ge0,
\qquad r,x\ge1/2.
\]

Nonnegative action counts preserve the inequality. Taking an infimum over common (u,v) therefore preserves the reduction. With group-symmetric per-coordinate counts, all single-coordinate flips in a group have the same objective; one representative per group suffices. This second step uses the symmetrization argument and must not be silently applied to arbitrary unequal per-coordinate allocations.

The independent code enumerates **every nonempty sign-flip subset and every type pattern** for partitions [1], [2], [1,2], [2,2], and [2,3], at three independently generated allocations per partition (seed 20261030, alpha=0,1,3; the third case allows finite-s=.8 type queries):

- **15 allocation/partition cases**, **660 full alternatives**, d<=5 and G<=2.
- Maximum difference between the full-alternative minimum and group-representative one-flip minimum: **2.775557561562891e-17**.
- **0** pointwise KL deletion violations, checked also at (.5,.5), (.85,.6), (.75,.7), (.95,.55).
- All continuous inner optimizations succeeded; maximum conservative inner tangent envelope 1.24e-6.

This is a finite numerical check of the reduction with a direct mathematical justification; it does not exhaust arbitrary d or certify the stopping-rule implementation.

## Independent outer optimizer and comparison with parent solver

The independent solver minimizes the linear query cost using nonlinear SLSQP constraints. Each constraint is recomputed by continuous inner SLSQP; its outer derivative is the envelope derivative evaluated at the fitted alternative. The independent solver never substitutes the analytic weighted-mean projection.

After convergence, a single LP using the final fixed alternatives gives necessary constraints and a floating numerical lower bound. This LP is a certificate check, not the algorithm that chose the allocation. Inner convexity gives

\[
\inf_{x\in\mathcal D}f(x)\ge
f(x_0)+\min_{v\in\mathrm{vertices}(\mathcal D)}\nabla f(x_0)^\top(v-x_0),
\]

for the triangular domain D. A conservative radial enlargement of the online counts repairs any remaining numerical feasibility deficit using the positive lower bound a_h D(p,.5)+b_h D(q,.5) on online information from the reversed coordinate. The repaired upper allocations pass the tangent feasibility check. The resulting floating upper/lower intervals are shown below.

Parent comparisons use `solve_allocation(..., eta=.01, tolerance=2e-8)`. All seven independent intervals overlap the corresponding parent intervals. Maximum absolute difference between the parent's repaired K and independent raw SLSQP K is **2.99e-8**.

| partition | p,q | alpha | direct s | independent raw K | independent numerical interval | parent numerical interval |
|---|---|---:|---|---:|---|---|
| [1] | .75,.60 | 0 | unavailable | 7.6445565028 | [7.6445565028, 7.6445565043] | [7.6445565028, 7.6445565105] |
| [1] | .75,.60 | 5 | unavailable | 6.0123365287 | [6.0123365274, 6.0123370153] | [6.0123364740, 6.0123365364] |
| [2] | .85,.60 | 1 | unavailable | 3.6227605281 | [3.6227605278, 3.6227608044] | [3.6227604793, 3.6227605411] |
| [1,2] | .85,.60 | 0 | unavailable | 6.8984985114 | [6.8984985101, 6.8984987686] | [6.8984984720, 6.8984985413] |
| [2,2] | .85,.60 | 3 | unavailable | 6.9592487220 | [6.9592487220, 6.9592496230] | [6.9592486788, 6.9592487463] |
| [1,2] | .85,.60 | 1 | .8 | 4.8436531417 | [4.8436531417, 4.8436534067] | [4.8436531417, 4.8436531471] |
| [2,2] | .85,.60 | 3 | .8 | 5.1134190624 | [5.1134190624, 5.1134205714] | [5.1134190624, 5.1134190680] |

All seven nonlinear outer optimizations converged. Independent interval widths are <=1.51e-6. Parent repaired allocations have minimum information >=1.000000001 within floating arithmetic. None of these bounds are formal rational/interval certificates; sub-nanoscopic lower-bound/raw-objective ordering differences are ordinary LP/SLSQP numerical tolerances.

One integration issue was encountered and resolved within the audit: calling HiGHS once with default threads and later with threads=1 can return `HiGHS Status 0: Not Set` in the same process. Both final LP callers use threads=1. This was a numerical-library scheduler configuration issue, not evidence against the coefficient formulation.

## Action class and theorem scope

1. With no direct type action, set c=0 and omit the associated decision variables. An optimizer for that action class is a different comparator from an optimizer that may buy noisy type reports.
2. With finite established s_g, include c_g in cost and kappa_g c_g in each alternative whose type in group g is reversed. For s=.8, kappa=.6 log(4)=.8317766166719345. The parent solver includes these variables and the independent tiny tests check them.
3. Theorem 3's equality criterion is unchanged for finite kappa: at oracle total cost, a positive c would consume cost without reducing the minimum necessary oracle task cost. Positive-premium magnitudes can change substantially, as the [2,2], alpha=3 examples show.
4. A perfect type question is a distinct action model. One error-free report per group gives at most G additional queries and removes the leading premium regardless of the finite-s criterion. It must not be approximated by inserting infinity into the finite-kappa LP.
5. A known-answer response-channel check is not a direct report of z. Its asymptotic domination in Section 8.2 follows from the same nonnegative KL increment, within this specific fresh Bernoulli model.
6. Because the planned comparison includes Direct Type, information tracking must have access to the same established finite-s type action, or be explicitly reported under a separate action class. Parent implementation planning states it will use the same s=.8 and separate both coefficient classes.

No coefficient agreement alone validates the online estimator, no-leakage interface, adaptive tracking, exact GLR, anytime error proof implementation, convergence of realized cost, or finite-budget superiority. Those are separate Phase 2a obligations. The general expected-cost achievability statement in Section 4 was read for compatibility, but the present audit does not replace a line-by-line independent mathematical proof review.

## Reproduction

From the Phase 2a directory:

```bash
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 120 python audit/independent_coefficients.py
```

The script prints the independent grid, crossing, seven coefficient checks with bounds, all enumeration case results, and a `checks_passed` flag to stdout. It writes no result files. `--section grid`, `--section tiny`, and `--section enumeration` isolate the bounded checks. The script deliberately contains no parent imports; parent comparison can be reproduced by calling the parent's `solve_allocation` on each case in the table after running the independent solution, with both LP clients configured for one HiGHS thread. No historical research file was edited by this audit.
