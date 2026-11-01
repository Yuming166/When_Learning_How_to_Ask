# Independent audit: unknown rates, oracle structure, and sharing thresholds

Date: 2026-10-31. Scope: exactly `MODEL_AND_SCOPE.md`. Historical theory and experiments and both earlier Web theory snapshots remain unchanged. All calculations here are deterministic; no model calls, training, or empirical benchmark worlds were used.

**Main conclusions.** The one-truth-flip reduction survives arbitrary mixed blocks and arbitrary alternative extraction levels. The known-level channel-garbling proof does not by itself establish the structure of the unknown-rate oracle. For the restricted menu \(L_{\max}=1\), however, its unique pure-good oracle and a modified scalar sharing criterion can be proved directly, retaining calibration of raw extraction levels. This gives an exact counterexample to importing the known-level Gamma: for a singleton fact and zero first-order calibration, the unknown-rate learner and unknown-rate oracle have equal leading coefficients although the known-level Gamma is strictly below one. With that same one-read menu and singleton fact, **every finite positive calibration ratio creates a strictly positive format premium**. The multi-read oracle structure remains unproved by this audit; no claim that it must use bad or mixed blocks is made.

## 1. One truth flip suffices, even for mixed blocks and continuous alternatives

Consider a block's full response vector \(y\in\{-1,+1\}^L\). Its true extraction accuracies are \(a_i\in\{p,q\}\), and its alternative accuracies are \(b_i\in\{u,v\}\), possibly with the type swapped. All are at least \(1/2\). Let
\[
 F_a(y)=\prod_i a_i^{(1+y_i)/2}(1-a_i)^{(1-y_i)/2},
 \qquad P_a^+(y)=rF_a(y)+(1-r)F_a(-y).
\]
The alternative truth log likelihood ratio is
\[
 g_b(y)=\log\frac{P_b^+(y)}{P_b^-(y)}
 =\log\frac{r\exp(T_b(y))+1-r}{(1-r)\exp(T_b(y))+r},
 \qquad T_b(y)=\sum_i y_i\operatorname{logit}(b_i).
\]
Because \(b_i\ge1/2\) and \(r>1/2\), this function is coordinatewise nondecreasing and odd: \(g_b(-y)=-g_b(y)\). Therefore
\[
 \mathbb E_{P_a^+}g_b(Y)=(2r-1)\mathbb E_{F_a}g_b(Y)\ge0.
\]
The inequality follows by coupling the independent signs under \(F_a\) above independent fair signs coordinatewise. The fair-sign expectation of an odd function is zero. Consequently
\[
 \boxed{D(P_a^+\Vert P_b^-)-D(P_a^+\Vert P_b^+)
 =\mathbb E_{P_a^+}g_b(Y)\ge0.}
\tag{1}
\]
The response order within each format is exchangeable, and the two format-specific counts are sufficient under both states. Thus (1) holds for the actual count observations too. The argument covers \(q=1/2\), \(v=1/2\), ties \(u=v\), and type swaps; strictness is not needed.

Hold an alternative's full type vector and its common levels \((u,v)\) fixed. Replacing any flipped truth by its true sign cannot increase its online KL contribution, by (1), and does not change calibration KL. From any wrong-truth alternative, retain just one of its flipped truths. Its total information is no larger. Thus all wrong-truth constraints are equivalent to the constraints for **exactly one flipped fact**, still ranging over every alternative type vector and all \((u,v)\) in the compact ordered closure. This reduction does not eliminate the common continuous nuisance or the alternative type patterns.

## 2. What the known-rate garbling proof does and does not prove

At the true levels, a bad extraction can be simulated from a good extraction by an extra flip probability \((p-q)/(2p-1)\). In the known-rate oracle comparison this same map also generates the alternative law, because the alternative changes truth while the known format assignment and levels remain fixed. For an unknown-rate alternative \((u,v)\), the needed flip probability is instead \((u-v)/(2u-1)\), when that expression is defined. These are generally different.

Data processing compares two distributions passed through a **common** stochastic kernel. A true-parameter garbling alone is therefore not a proof that a mixed/bad block is less useful against every continuous oracle alternative. It also is not evidence of the opposite statement. The generic multi-read oracle could still be pure-good under a different argument; that question remains open in this audit.

Likewise, even a pure-good oracle need not choose the known-rate optimal depth or a single depth. Its robust objective includes calibration and an infimum over shared alternative levels. The earlier finite set \(\mathcal M(c)=\arg\max_L A_L/(c+\ell L)\) is not the unknown-rate oracle's feasible optimal set.

## 3. The universally valid replacement for a scalar threshold

Let
\[
 D_0(u,v)=\operatorname{kl}(p,u)+\operatorname{kl}(q,v),
\]
and let \(\mathcal F_{\rm or}(h,\alpha)\) be the set of optimal allocations in the continuous-alternative oracle program, with current types revealed and levels still unknown:
\[
 \min_{x\ge0}\sum_e w_ex_e,
 \qquad
 \alpha D_0(u,v)+\sum_e x_eD_e(h,h')\ge1
\]
for all wrong-truth alternatives with \(z'=z\). The full learner also imposes every alternative type vector. Then
\[
 \boxed{K_{\rm learner}=K_{\rm or}
 \iff \exists x\in\mathcal F_{\rm or}(h,\alpha)
 \text{ satisfying every learner constraint}.}
\tag{2}
\]
By Section 1, only single-fact truth flips need to be checked in (2), but all alternative types and levels remain. This is an exact oracle-optimal-set feasibility condition, not a new scalar formula.

Attainment is available: the action menu is finite, its costs are strictly positive, alternative KLs are continuous on a compact domain, and a finite feasible allocation exists using one-read actions. A bounded objective sublevel is compact. Therefore absence of a feasible oracle optimizer implies a strictly larger learner coefficient. This conclusion is about information programs; their operational expected-cost interpretation uses the separately supplied continuous-model achievability proof.

## 4. Exact restricted result for one read per root

Now restrict to \(L_{\max}=1\). Define the affine factual response accuracy
\[
 \rho(a)=\tfrac12+(2r-1)(a-\tfrac12),
 \qquad s=\rho(p),\quad t=\rho(q),
\]
and, for \(d\ge1\),
\[
 F_d(s,b)=\operatorname{kl}(s,1-b)+(d-1)\operatorname{kl}(s,b)
 =d\operatorname{kl}(s,b)+(2s-1)\operatorname{logit}(b).
\]
Each online response comes from a fresh root, so this is an iid binary response problem with online levels \(\rho(p),\rho(q)\). **Calibration still has raw levels \(p,q\)**. Replacing its KL by \(\operatorname{kl}(\rho(p),\rho(u))\) would change the experiment.

Define
\[
 S_{d,\alpha}(a)=\inf_{1/2\le v\le u\le1-\eta}
 \left\{\alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,v)]
       +aF_d(s,\rho(u))\right\}.
\tag{3}
\]
This continuous function is strictly increasing from zero to infinity in \(a\): the online term is uniformly at least \(\operatorname{kl}(s,1/2)>0\). Let \(a_\alpha\) be its unique positive root \(S_{d,\alpha}(a_\alpha)=1\).

**Restricted oracle theorem.** Its coefficient is
\[
 K_{{\rm or},\alpha}=(c+\ell)d a_\alpha.
\tag{4}
\]
Its unique information-optimal allocation uses \(a_\alpha\) good-format one-read blocks per fact and zero first-order bad-format blocks.

**Proof.** With types known, average any feasible allocation over permutations of facts after aligning their good labels. The symmetric problem has per-fact counts \(a,b\), objective \((c+\ell)d(a+b)\), and constraint
\[
 \inf_{u\ge v\ge1/2}\{\alpha D_0(u,v)
 +aF_d(s,\rho(u))+bF_d(t,\rho(v))\}\ge1.
\]
At \((a_\alpha,0)\), a minimizing pair can be chosen with \(u_*\le p\) and \(v_*\!=\min(q,u_*)\). Clipping both levels at \(p\) cannot increase any term, and minimizing the remaining calibration term gives the stated \(v_*\). Let
\[
 A=F_d(s,\rho(u_*)),\qquad B=F_d(t,\rho(v_*)).
\]
Then \(A>B\). If \(u_*\le q\), both second arguments coincide and are no larger than \(t<s\). The derivative
\[
 \partial_x F_d(x,b)=d\operatorname{logit}(x)-(d-2)\operatorname{logit}(b)
\]
is strictly positive in the required comparison. If \(u_*>q\), then \(v_*=q\), \(B=\operatorname{kl}(t,1-t)\), and
\[
 A=d\operatorname{kl}(s,\rho(u_*))
 +(2s-1)\operatorname{logit}(\rho(u_*))
 >\operatorname{kl}(t,1-t).
\]
Evaluating at this fixed minimizing pair shows that any \(a+b\le a_\alpha\) with \(b>0\) has information strictly below one. Thus the symmetric optimum is pure-good. Symmetrization preserves the total bad count, so every optimum is pure-good.

For unequal good counts at the optimum, choose a fact with count below their mean. At the same minimizing pair, its one-truth-flip constraint strictly decreases if \(u_*>1/2\), because the sign-flip increment is \((2s-1)\operatorname{logit}(\rho(u_*))>0\). For \(d\ge2\), the only boundary possibility requiring care is \(d=2,\alpha=0,u_*=1/2\): the derivative in \(u\) becomes negative for the under-sampled fact, so a small increase above one half makes its constraint strictly less than one. Specifically its derivative is proportional to \(4(2s-1)(x_j-a_\alpha)<0\). For \(d>2\), or \(d=2,\alpha>0\), the objective derivative at one half is negative, so this boundary cannot minimize. For \(d=1\), there is no unequal allocation. This establishes uniqueness and (4).

This proof is an affine-channel adaptation of the original note's supporting-alternative argument. It is a justified restricted transfer; the Bernoulli closed-form optimizer from that note does not transfer because the offline and online KLs use different parameter maps.

## 5. Restricted scalar criterion with the correct calibration channel

For the one-read menu, put
\[
 \widetilde\Gamma_k(\alpha)
 =\inf_{1/2\le v\le1-\eta}
 \left\{\alpha\operatorname{kl}(q,v)
       +a_\alpha F_k(s,\rho(v))\right\}.
\tag{5}
\]
Then
\[
 \boxed{K_{{\rm learner},\alpha}=K_{{\rm or},\alpha}
 \iff \widetilde\Gamma_{k_{\min}}(\alpha)\ge1.}
\tag{6}
\]

**Proof.** The oracle allocation is unique. Consider its feasibility under an alternative that flips the types of groups containing \(l\) facts in total. If the one flipped truth lies in those groups, set the alternative good level to \(u=p\), which fits every unaffected good-format stream and its calibration exactly. The remaining expression is (5) with \(k=l\). Its minimizer is no larger than \(p\), so the order constraint is respected. It is nondecreasing in \(l\), because adding one more unchanged fact adds \(a_\alpha\operatorname{kl}(s,\rho(v))\ge0\). The smallest possible nonempty union has size \(k_{\min}\).

If the flipped truth lies outside the type-flipped set, a minimizing pair may be clipped to \(v\le u\le p\). For its type-flipped but truth-unchanged facts,
\(\operatorname{kl}(s,\rho(v))\ge\operatorname{kl}(s,\rho(u))\).
Replacing those contributions by the latter terms produces exactly an oracle constraint, whose value is at least one. An unchanged-type alternative is already an oracle alternative. Section 1 covers all additional truth flips. Thus (5) is the only extra binding family, proving (6).

The scalar result is confined to \(L_{\max}=1\). It is not evidence for the same scalar reduction with multi-read roots or mixed blocks.

## 6. Exact counterexample to the imported known-level Gamma

Take \(d=1\), \(L_{\max}=1\), and \(\alpha=0\), at any fixed admissible \(r,p,q\). Write
\[
 B_p=\operatorname{kl}(\rho(p),1/2),\qquad
 B_q=\operatorname{kl}(\rho(q),1/2),\quad B_p>B_q\ge0.
\]
Under every wrong-truth alternative, the probability of the true positive sign on either queried format is at most one half. Hence its per-format KL is at least \(B_p\) or \(B_q\), respectively. The alternative closure point \(u=v=1/2\) attains both bounds simultaneously, irrespective of its type. This is also the limit of valid strict alternatives.

Both the unknown-rate oracle and the learner therefore have exactly the same single LP constraint
\[
 x_{\rm good}B_p+x_{\rm bad}B_q\ge1,
\]
and the same unique optimum
\[
 \boxed{K_{{\rm learner},0}=K_{{\rm or},0}
       =\frac{c+\ell}{B_p}.}
\tag{7}
\]
In contrast, the known-level singleton ratio is
\[
 \Gamma^{\rm known}_{1,1}
 =\frac{\operatorname{kl}(\rho(p),1-\rho(q))}
        {\operatorname{kl}(\rho(p),1-\rho(p))}<1,
\]
because \(1-\rho(q)>1-\rho(p)\) and both are at most one half. Importing that known-level criterion would incorrectly predict a positive unknown-format premium in (7). The discrepancy reflects a weaker unknown-rate oracle; it is not an improvement in the learner's absolute query efficiency.

For the rational instance
\[
 r=4/5,\quad p=4/5,\quad q=3/5,\quad\eta=1/10,
 \quad c=0,\quad\ell=1,
\]
we have \(\rho(p)=17/25\), \(\rho(q)=14/25\),
\[
 B_p=0.0662777229875189918259398317593768\ldots,
\]
\[
 K_{{\rm learner},0}=K_{{\rm or},0}
 =15.0880258844787678417167545290272\ldots,
\]
whereas the known-rate oracle coefficient is \(3.6851707227842846010\ldots\) and its known-level Gamma is \(0.4309410500164748953\ldots<1\).

The exact rational interval certificate in `singleton_threshold_certificate.py` verifies the strict numerical comparisons and writes `singleton_threshold_certificate.json`. The equality of the unknown-rate optima follows from the analytic closure-point argument, not from a parameter grid or a numerical optimizer. An \(\alpha=0\) asymptotic calibration ratio allows sublinear calibration counts; it does not require literally zero calibration observations.

## 7. For the same singleton, every positive finite calibration ratio has a premium

Continue to assume \(d=1,L_{\max}=1\), but let \(0<\alpha<\infty\). Take the minimizing pair \((u_*,\min(q,u_*))\) at the unique oracle allocation \(a_\alpha\).

- If \(u_*\le q\), the type-swapped learner alternative with low level \(v=u_*\) and high level \(u=p\) has information
  \[
  \alpha\operatorname{kl}(q,u_*)
  +a_\alpha\operatorname{kl}(s,1-\rho(u_*))
  =1-\alpha\operatorname{kl}(p,u_*)<1.
  \]
- If \(u_*>q\), choose the type-swapped alternative with levels \((p,q)\). Its information is
  \[
  a_\alpha\operatorname{kl}(s,1-\rho(q))
  <a_\alpha\operatorname{kl}(s,1-\rho(u_*))\le1.
  \]

In both cases the unique oracle allocation is infeasible for the learner. Therefore
\[
 \boxed{K_{{\rm learner},\alpha}>K_{{\rm or},\alpha}
       \quad\text{for every fixed }0<\alpha<\infty.}
\tag{8}
\]
At \(\alpha=0\), equality holds by (7). This is a classification change at zero calibration; it does not assert a discontinuity in the values themselves, nor monotonicity of the premium for positive \(\alpha\). This restricted consequence is closely related to the original note's calibration mechanism and is not claimed as an independent novelty discovery.

## 8. Calibration limits and claim boundaries

For either oracle or learner in the full finite block menu, its coefficient is nonincreasing in \(\alpha\): additional calibration relaxes the same information constraints. It is always at least the appropriate known-rate coefficient, because setting \((u,v)=(p,q)\) gives zero calibration KL and retains all known-rate alternatives.

The coefficient converges to that known-rate coefficient as \(\alpha\to\infty\). To see the upper bound, take a known-rate optimal allocation and add an arbitrarily small allocation of all one-read actions. The latter supplies a positive uniform separation against every wrong-truth alternative, since some true good stream has factual accuracy above one half while the wrong-truth mean is at most one half. By continuity, the added slack covers a neighborhood of \((p,q)\). Outside that neighborhood, compactness gives a strictly positive minimum calibration KL, so a sufficiently large \(\alpha\) handles all remaining alternatives. Let the added allocation tend to zero.

This proves the coefficient limit without substituting known levels at any finite calibration ratio. The difference or ratio of learner and oracle coefficients need not inherit either coefficient's monotonicity. A generic multi-read scalar smallest-group criterion, unique pure-good oracle, or known-rate optimal-depth formula requires additional proof and is not established here.

The original calibration streams concern extraction from known reports. They are not factual-source labels. No calculation here supports replacing them by effective factual-accuracy streams, treating source-correlated responses as iid Bernoulli trials within a block, or claiming that a natural Web/LLM system obeys this model.

## 9. Independent audit of the parent's finite-calibration counterexample

The separately implemented `certify_threshold_failure.py` and its `THRESHOLD_FAILURE_CERTIFICATE.json` were read and independently checked for mathematical validity. This audit did not rerun that certificate or modify either artifact. Its exact-rational assertions and continuous-domain coverage support the following opposite-direction example:
\[
 r=p=4/5,\quad q=3/5,\quad\eta=1/20,\quad d=1,
 \quad L_{\max}=5,\quad c=10,\quad\ell=1,\quad\alpha=1.
\]
The known-rate oracle's unique depth is five, with certified singleton Gamma above \(1.0903799\); the known-rate theorem therefore has zero premium. Under unknown rates and finite calibration, the certificate instead proves
\[
 K_{\rm learner}\ge24.496612161232778\ldots,
 \qquad K_{\rm or}\le24.15,
\]
so the online coefficient premium is at least \(0.346612161232778\ldots\), and its relative ratio is at least \(1.014352470444421\ldots\). These are certified lower/upper bounds, not estimates of the exact optima.

The lower-bound logic is sound. One admissible wrong-truth, swapped-type alternative has levels \((u,v)=(4/5,1/2)\). Its calibration KL is exactly \(\operatorname{kl}(3/5,1/2)\). All twenty available blocks of total depth one through five, including all mixed blocks, satisfy the certified dual inequalities
\[
 25 D_e(h,h')\le 10+L_e.
\]
Hence any feasible learner allocation costs at least
\(25[1-\operatorname{kl}(3/5,1/2)]\). The smallest certified dual slack exceeds \(0.2706505\), so the conclusion does not depend on a nearly tight rounding comparison.

The oracle upper bound is also global, rather than a pointwise grid check. The proposed oracle allocation uses \(161/100\) pure-good depth-five blocks, costing \(483/20=24.15\). Its information for an alternative good level \(u\) is
\[
 f(u)=\operatorname{kl}(4/5,u)
 +\operatorname{kl}(3/5,\min(3/5,u))
 +\frac{161}{100}D(P_{4/5,5}^+\Vert P_{u,5}^-).
\]
Profiling \(v=\min(q,u)\) is exact, since a pure-good block has no online dependence on \(v\). Each raw calibration log score has magnitude at most \(1/\eta=20\). A five-read binomial component log score has magnitude at most \(5/\eta=100\); the root mixture score is a posterior-weighted average of these component scores and obeys the same bound. Thus \(f\) is globally Lipschitz with constant at most
\[
 20+20+(161/100)100=201.
\]
The piecewise calibration profile is continuous and satisfies the same bound across \(u=q\). The 900 equal cells cover exactly \([1/2,19/20]\), each with midpoint radius \(1/4000\). Subtracting \(201/4000\) from each certified midpoint lower bound therefore covers every continuous alternative. The resulting uniform information margin is above \(0.00798205\). This is an independently checked continuous feasibility proof; it assumes neither pure-good optimality nor convexity of the multi-read inner problem.

The same script now also certifies a useful nonconvexity counterexample. At \(r=p=4/5,L=5\), let
\(g(u)=D(P_{4/5,5}^+\Vert P_{u,5}^-)\).
Exact intervals give
\[
 g(3/5)-\tfrac12[g(1/2)+g(7/10)]
 >0.0838853423967573.
\]
The three points are admissible in the alternative closure; the irrelevant alternative bad level can be held at one half throughout. Therefore the pure-good multi-read online KL is not convex in its alternative extraction rate. At \(\alpha=0\), this directly gives a nonconvex inner objective. This does not prove nonconvexity at every positive calibration ratio, but it rules out blindly reusing the elementary Bernoulli/isotonic optimizer for the general model.

Together with Section 6, the two counterexamples show that importing the known-rate scalar criterion can fail in **both directions**: it can predict a premium where the correct unknown-rate oracle has none, and it can predict zero premium where finite-calibration unknown rates produce a certified positive gap.
