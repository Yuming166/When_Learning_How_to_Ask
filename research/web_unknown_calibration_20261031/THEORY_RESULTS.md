# Unknown extraction rates with finite calibration

Date: 2026-10-31. Scope: MODEL_AND_SCOPE.md. Mathematical conclusions are for a fixed finite completed-source-block experiment; they are not empirical Web or LLM claims.

## 1. What changes relative to the known-rate result

Keep known source accuracy r∈(1/2,1), a known partition of d truths into G nonempty groups, and a finite menu of all blocks (j,n_A,n_B) of lengths 1 through L_max. Each block uses its own independent persistent source report. Its cost is w_e=c+ell(n_A+n_B)>0.

The high/low extraction rates are now common UNKNOWN parameters
\[
1/2\le q<p\le1-\eta,\qquad 0<\eta<1/2.
\]
The type-informed oracle knows z only; it also has to handle unknown p,q. Both procedures receive independent labelled Bern(p) and Bern(q) reference streams of M_delta observations each. These calibrate extraction of known source reports, not source truthfulness, and reveal no current type or truth. Let
\[
R=\log(1/\delta),\qquad M_\delta/R\longrightarrow\alpha\in[0,\infty).
\]
Calibration is an already acquired common resource. The objective is expected online cost; if each reference observation costs b_cal, total cost adds the common deterministic 2b_cal M_delta. Correctness includes calibration randomness and is not conditional on every calibration record.

Write h=(theta,z,p,q) and let H_wrong be all wrong-truth alternatives with continuous rate domain
\[
\mathcal D=\{(u,v):1/2\le v\le u\le1-\eta\}.
\]
This compact closure gives the same information infima and likelihood suprema as the strict p>q domain. Source accuracy r remains known; no revisits or within-block adaptation are permitted.

## 2. Exact information characterization

For action e, let P_h^e be its full two-count mixture law, integrating out the persistent report. Define
\[
D_e(h,h')=D(P_h^e\Vert P_{h'}^e),\qquad
C(h,h')=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]
The leading online cost program is
\[
\boxed{
K(h,\alpha)=\min_{x\ge0}w^\top x
\quad\text{s.t.}\quad
\alpha C(h,h')+\sum_ex_eD_e(h,h')\ge1
\quad\forall h'\in\mathcal H_{\rm wrong}.}
\tag{1}
\]
This is a convex semi-infinite linear program in allocation counts. It need not have a convex nuisance-rate minimization. No requirement is imposed to certify z,p,q as outputs.

**Theorem 1 (exact expected-online-cost coefficient).** For fixed d, partition, finite L_max, fixed r,p,q,c,ell,eta and finite alpha,
\[
\inf_{\pi\ \text{uniformly }\delta\text{-correct}}
\mathbb E_h C_\pi
=K(h,\alpha)R+o(R).
\tag{2}
\]
The same statement holds for the type-informed oracle with the same calibration and unknown p,q, restricting alternatives to z'=z.

### Lower bound

Stopped change of measure gives, for every wrong-truth alternative,
\[
M_\delta C(h,h')+
\sum_e\mathbb E_hN_e(\tau)D_e(h,h')
\ge b_\delta:=\operatorname{kl}(1-\delta,\delta).
\tag{3}
\]
The action probabilities cancel in the likelihood ratio. The decision event is outputting the true truth vector. Compactness of bounded nonnegative count vectors, M_delta/R→alpha and b_delta/R→1 yield the liminf bound. Infinite expected cost is trivial.

Calibration contains no direct information about theta, but it does contain information about the full unknown state. Calling it ancillary to p,q would be incorrect.

### Valid stopping rule

Let m_e=(n_A+1)(n_B+1) be a block's count-alphabet size. For each candidate truth vector, profile the likelihood of BOTH calibration streams and all blocks over z,u,v. Stop when the highest candidate profile log likelihood exceeds the highest profile for a different truth vector by
\[
\boxed{
\beta(t,\delta)=R+2\log(M_\delta+1)
+\sum_e\log\binom{N_e(t)+m_e-1}{m_e-1}.}
\tag{4}
\]
This is a categorical block likelihood, not a product of conditionally-on-truth independent reads.

To prove correctness, integrate a separate unrestricted categorical probability vector for each block action against Dirichlet(1,...,1), and a separate Bernoulli mean for each calibration stream against Beta(1,1). The saturated likelihood maximum is at most
\[
Q_t(M_\delta+1)^2\prod_e\binom{N_e(t)+m_e-1}{m_e-1}.
\]
Under any true state, Q_t/L_t(h) is a nonnegative mean-one martingale when the calibration sampling period is included. A wrong stop crosses 1/delta; Ville's inequality gives the uniform error guarantee. Conditional on a particular calibration record the ratio need not start at one, so this proof does not give a recordwise conditional guarantee.

### Achievability and the cost issue

The complete proof is in CONTINUOUS_COST_PROOF.md. The key points are:

1. Square-root forced exploration of both one-read formats on every fact estimates full discrete labels and p,q consistently. Their marginal accuracies are rho(a)=1/2+(2r−1)(a−1/2), so known r permits inversion. Every fixed estimation-error tolerance has an exp(−const sqrt(t)) tail.
2. Compact alternative domain, uniformly positive outcome probabilities, and a uniformly separating exploration allocation give existence, local boundedness and continuity of program values and upper hemicontinuity of optimal sets.
3. Nonunique cost-optimal allocations have a convex normalized block-frequency image. If X* is the optimal set, then
   \[
   \mathcal W=\{x/(\boldsymbol1^\top x):x\in X^*\},
   \qquad x=\frac{K v}{w^\top v}.
   \]
   Projective reweighting proves convexity; it must not be justified by incorrectly claiming that all optimizers have the same block count.
4. Deterministic cumulative tracking follows the estimated normalized allocations. Uniform positive online information remains available against every wrong-truth alternative, even when a calibration constraint is tight. Specifically, let B_min be the minimum of kl(rho(a),1/2) over the true informative rates a∈{p,q}. A feasible allocation satisfies
   \[
   \sum_ex_eD_e(h,h')\ge\chi:=B_{\min}/\kappa(r)>0
   \quad\text{for every wrong-truth }h',
   \]
   where kappa(r)=kl(r,1−r). Indeed a flipped fact has a same-level truth-KL constraint of at least one; each block's truth KL is at most kappa(r). From any informative such block, a single informative-coordinate marginal already has KL at least B_min against a flipped-truth alternative.
5. Concentration of the finitely many empirical category counts controls likelihoods uniformly over the continuous parameter domain. Cost-hitting-time tails, rather than one fixed block-count horizon, yield
   \[
   \Pr_h(C_{\tau_\delta}>s+w_{\max})
   \le C s^2e^{-c_0\sqrt s},
   \qquad s\ge(K+\epsilon)R
   \]
   for sufficiently small delta and large horizons. Integrating the tail gives E C_tau≤(K+epsilon)R+O(1), then epsilon↓0.

The construction stops almost surely and has finite expected cost for every admissible state and fixed delta. It uses exact variational optimization and exact likelihood profiles. A numerical grid or local optimizer does not inherit this theorem.

## 3. One flipped truth still suffices, even for mixed blocks

**Lemma 2.** Fix any true block extraction rates a_i≥1/2 and alternative extraction rates b_i≥1/2, with the same known r. Then
\[
D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{-})
\ge D(P_{\boldsymbol a}^{+}\Vert P_{\boldsymbol b}^{+}).
\tag{5}
\]
This includes arbitrary mismatches of type and continuous rate levels.

**Proof.** On the full signed response vector y, put T(y)=sum_i y_i logit(b_i). The alternative truth log likelihood ratio is
\[
g_{\boldsymbol b}(y)=
\log\frac{r e^{T(y)}+1-r}{(1-r)e^{T(y)}+r}.
\]
It is odd and coordinatewise nondecreasing. Conditional on a positive true source report, F_a is a product sign distribution with each positive probability at least 1/2. It stochastically dominates independent fair signs, whose expectation of the odd g is zero. The true positive-truth mixture therefore gives
\[
E_{P_{\boldsymbol a}^{+}}g_{\boldsymbol b}
=(2r-1)E_{F_{\boldsymbol a}}g_{\boldsymbol b}\ge0.
\]
This expectation is precisely the difference in (5). Format-specific counts are sufficient, so the proof applies to the observed block laws. ∎

Orient the true state so all truths are positive and A is good in each group, purely as a proof symmetry. Let b_{g,a,b} be per-fact counts of an (a,b) block in group g. Let J be the set of type-flipped groups; their alternative channel pairs are (v,u), while the other groups use (u,v). Write d_{g,a,b}^{+}(u,v;J) and d_{g,a,b}^{-}(u,v;J) for the corresponding KLs with an unchanged or flipped truth.

Group symmetrization and Lemma 2 give the exact reduced constraints
\[
\begin{split}
\mathcal I_{J,h}(b;\alpha)=\inf_{(u,v)\in\mathcal D}\{
&\alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,v)]\\
&+\sum_g k_g\sum_{a,b}b_{g,a,b}d_{g,a,b}^{+}(u,v;J)\\
&+\sum_{a,b}b_{h,a,b}
[d_{h,a,b}^{-}(u,v;J)-d_{h,a,b}^{+}(u,v;J)]\}\ge1 .
\end{split}
\tag{6}
\]
There are G 2^G continuous-minimization constraints. The objective is sum_g k_g sum_{a,b}(c+ell(a+b)) b_{g,a,b}. Every wrong-truth alternative dominates one with only one truth flipped at the same alternative types and levels; conversely all displayed alternatives are allowed.

Thus a useful part of the original Theorem 1 reduction survives the persistent-source extension exactly.

## 4. What can be said about the unknown-rate oracle

Since the oracle knows all types, arbitrary coordinate permutations after true-format relabelling are symmetries. Its VALUE can therefore be computed with a common per-fact allocation b_{a,b}:
\[
\boxed{
K_o(h,\alpha)=
d\min_{b\ge0}\sum_{a,b}w_{a,b}b_{a,b}
}
\]
subject to
\[
\inf_{(u,v)\in\mathcal D}
\left\{\alpha C(p,q;u,v)+
\sum_{a,b}b_{a,b}
\left[D(P_{p,q}^{+;a,b}\Vert P_{u,v}^{-;a,b})
+(d-1)D(P_{p,q}^{+;a,b}\Vert P_{u,v}^{+;a,b})\right]\right\}\ge1.
\tag{7}
\]
Symmetry of the optimum value does not characterize its entire optimal set.

The previous pure-good dominance argument does not automatically apply. Its postprocessing probability (p−q)/(2p−1) depends on unknown parameters. A pure-good block law is unchanged if q changes at fixed p, whereas a block containing the other format generally changes. No one parameter-independent kernel from the pure-good block can reproduce that entire family. This observation blocks the old proof, but is not a proof that mixed blocks must be optimal for truth recovery.

Keep every mixed block in the oracle program until a valid structural theorem proves an elimination. The bounded numerical diagnostics below found pure-good optima in their tested grid relaxations; they do not settle this question.

### The valid general equality criterion

Let X_o^*(h,alpha) be the COMPLETE oracle-optimal set in the original full count space, or its group-symmetrized version. Define
\[
\Psi(h,\alpha)=
\max_{x\in X_o^*(h,\alpha)}
\min_{\substack{h'\ {\rm wrong\ truth}\\z'\ne z}}
\{\alpha C(h,h')+\sum_ex_eD_e(h,h')\}.
\tag{8}
\]
The minimum includes all continuous alternative levels; the maximum is attained because the optimal set is compact and the profiled information is continuous.

**Theorem 3 (general no-premium criterion).**
\[
K(h,\alpha)=K_o(h,\alpha)
\quad\Longleftrightarrow\quad\Psi(h,\alpha)\ge1.
\tag{9}
\]
If it fails, the coefficients differ strictly.

**Proof.** The learner's feasible set is contained in the oracle's. Equality of attained minima occurs iff at least one oracle-optimal allocation also meets all added type-changing wrong-truth constraints. Compactness rules out an equal unattained infimum. This is exactly (8). ∎

This is a correct variational condition, not yet a smallest-group scalar formula for general multi-read blocks. Feasibility on an oracle-optimal set is a standard nested-optimization observation; the contribution must come from further structure or the proved separations.

## 5. Exact connection for one-read sources

When L_max=1, online answers are Bernoulli with effective accuracy
\[
\rho(a)=1/2+(2r-1)(a-1/2).
\]
Their admissible upper endpoint is rho(1−eta), while the reference streams remain Bern(p), Bern(q). Replacing calibration by Bern(rho(p)), Bern(rho(q)) would change the experiment.

Define s=rho(p) and
\[
F_k(s,t)=\operatorname{kl}(s,1-t)+(k-1)\operatorname{kl}(s,t),
\]
\[
S_{d,\alpha}^{(r)}(a)=
\inf_{1/2\le v\le u\le1-\eta}
\{\alpha[\operatorname{kl}(p,u)+\operatorname{kl}(q,v)]
+aF_d(s,\rho(u))\}.
\tag{10}
\]
Let a_alpha be the unique positive root S(a)=1. Then the oracle coefficient is (c+ell)d a_alpha and its unique optimal allocation uses a_alpha good-format queries per fact. With
\[
\Gamma_k^{(r)}(\alpha)=
\inf_{1/2\le v\le1-\eta}
\{\alpha\operatorname{kl}(q,v)+a_\alpha F_k(s,\rho(v))\},
\tag{11}
\]
one has
\[
K=K_o
\quad\Longleftrightarrow\quad
\Gamma_{k_{\min}}^{(r)}(\alpha)\ge1.
\tag{12}
\]
The full proof is in ORACLE_AND_THRESHOLD_AUDIT.md. It adapts the original supporting-alternative argument with the affine online channel but the original calibration laws. It does not reuse the original elementary fitted-mean formulas: the raw calibration and affine online likelihoods are different functions of u,v.

At alpha=0, the original effective-channel conclusion returns: equality iff G=1. In particular, d=1 has
\[
K=K_o=(c+\ell)/\operatorname{kl}(\rho(p),1/2).
\tag{13}
\]
For d=1 and every finite alpha>0, the one-read learner has a strictly positive premium. This is a structural consequence of the adapted original theorem, not a claim that increasing calibration always worsens the premium.

Equation (13) already shows that the known-rate criterion cannot be used with an unknown-rate oracle: it can incorrectly predict a positive premium where the correct unknown-rate comparison has zero premium.

## 6. Certified opposite-direction failure with multiple reads

The more consequential failure is that the known-rate formula can predict ZERO premium while finite calibration leaves a strictly POSITIVE premium.

Take the exact rational parameters
\[
r=p=4/5,\quad q=3/5,\quad\eta=1/20,\quad
d=1,\quad L_{\max}=5,\quad c=10,\quad\ell=1,\quad\alpha=1.
\tag{14}
\]
All 20 mixed/pure block actions are available.

**Known-rate comparison.** Depth 5 uniquely maximizes A_L/(10+L) and its singleton V_5/A_5>1.0903799. The prior known-rate theorem therefore gives zero leading premium.

**Unknown-rate learner lower bound.** Use the single admissible alternative with truth flipped, type flipped, u=4/5, v=1/2. Its calibration KL is kl(3/5,1/2). For EVERY one of the 20 actions, the exact interval certificate proves
\[
25\,D_e(h,h')\le w_e .
\]
Multiplying the information constraint by 25 yields
\[
K(h,1)\ge25[1-\operatorname{kl}(3/5,1/2)]
>24.4966121612.
\tag{15}
\]
This is a dual lower bound, not a numerical optimum.

**Unknown-rate, type-informed oracle upper bound.** Allocate x=161/100 pure-good length-5 blocks, giving cost 15x=24.15. Since this block's law depends only on u, the calibration-minimizing v is exactly min(3/5,u). It suffices to prove
\[
f(u)=\operatorname{kl}(4/5,u)+
\operatorname{kl}(3/5,\min(3/5,u))
+\frac{161}{100}D(P_{4/5,5}^{+}\Vert P_{u,5}^{-})\ge1
\tag{16}
\]
throughout [1/2,19/20].

The certificate covers that WHOLE interval with 900 adjacent cells of width 1/2000. It evaluates lower bounds at rational midpoints using exact rational probabilities and bounded logarithm-series remainders. Each raw Bernoulli KL derivative has absolute value at most 1/eta=20. A mixture log score is a posterior convex average of component binomial scores, each bounded by L/eta=100. Therefore f is globally 201-Lipschitz. Subtracting 201/4000 at every midpoint certifies
\[
\inf_uf(u)>1.007982.
\]
This is continuous-domain feasibility, not a finite-grid assumption. Theorem 1 consequently gives K_o(h,1)≤24.15 without needing to know the oracle's exact optimal structure.

Combining the two certificates:
\[
\boxed{
K(h,1)-K_o(h,1)>0.346612,\qquad
K(h,1)/K_o(h,1)>1.014352.}
\tag{17}
\]
These are conservative rigorous bounds on asymptotic online coefficients, not claims about their exact values or finite-budget accuracy.

### The inner mixture optimization really can be nonconvex

For the same r=p=.8, define f_0(u)=D(P_{p,5}^{+}||P_{u,5}^{-}). Exact intervals certify
\[
f_0(.6)-\tfrac12[f_0(.5)+f_0(.7)]>0.083885.
\tag{18}
\]
Approximate values are .722583, .589174 and .688222 respectively. Thus even the pure-good, alpha=0 inner objective need not be convex in the alternative reliability. The original Bernoulli isotonic projection cannot be used as an exact solver here.

The executable certify_threshold_failure.py and THRESHOLD_FAILURE_CERTIFICATE.json bind all of these assertions. Exact fractions are used for every comparison; decimal strings are displays.

## 7. Calibration limits and comparison boundaries

For each fixed experiment, K(h,alpha) and K_o(h,alpha) are nonincreasing in alpha. Their difference need not be monotone. A common additive calibration acquisition cost leaves equality of their coefficients unchanged, but changes their relative total-cost ratio.

As alpha→infinity in the coefficient functions, each converges to the corresponding KNOWN-RATE fixed-menu coefficient from the previous snapshot. Indeed, same-rate alternatives have zero calibration KL and give the known-rate lower bound. For the reverse approximation, take a slightly enlarged known-rate feasible allocation. Continuity gives strict feasibility in a neighborhood of the true rates; away from it, compactness makes the positive calibration KL uniformly bounded below. Sufficiently large finite alpha makes those remaining constraints feasible. Let the enlargement vanish.

This is a limit of coefficient functions after the fixed-alpha expected-cost theorem. It does not assert uniform convergence in a growing menu, closing rate gaps, r approaching a boundary, or a simultaneous arbitrary M_delta/R→infinity regime.

The numerical grid diagnostic deliberately retains alpha=0,.1,1,5,20,100 for the fixed parameter fixture. Its LPs minimize over allocations while checking only a finite nuisance grid, so they are RELAXATIONS. Equality of two grid values at alpha=20 or 100 does not certify equality of the continuous values. A local one-dimensional search supplies exploratory candidate oracle allocations only. The exact certificate was constructed separately to settle the alpha=1 separation.

## 8. What has and has not been solved

Completed: continuous joint-information program, uniform finite-delta categorical stopping, matching expected-online-cost theorem, exact one-flip reduction, oracle value reduction and complete-set equality criterion, a one-read smallest-group theorem with the correct calibration channel, and a certified multi-read counterexample to transplanting the known-rate threshold.

Open: pure-good versus mixed optimality of the general multi-read unknown-rate oracle; a scalar smallest-group criterion for that model; how source cost changes that criterion; revisiting and within-source adaptation; unknown source reliability and dependence; empirical validity.

The new results connect the original model to a persistent-source model, but they do not establish general Web-agent optimality. Generic calibration KL bounds, Dirichlet-mixture stopping, and controlled-testing allocations have direct predecessors; see CALIBRATION_NOVELTY_AUDIT.md. The proof reviews share context and model family and are not formal machine verification.
