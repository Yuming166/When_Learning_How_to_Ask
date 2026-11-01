# Continuous unknown channels, finite calibration, and expected online cost

Date: 2026-10-31. This is a direct mathematical proof for `MODEL_AND_SCOPE.md`, audited against the original expected-time attachment and the preceding finite-state cost proof. It is a same-family collaborator derivation, not formal verification or a literature-priority claim. No model calls, training, simulation, or edits to sealed theory snapshots were performed.

## 1. Result and scope

The continuous-alternative information program has a matching expected-**online-cost** theorem in the stated completed-block model. The two technical issues that require new treatment are:

1. A completed block is a categorical observation, not a collection of independent Bernoulli observations conditional on factual truth.
2. Cost-optimal allocations need not have a common total number of blocks. Their normalized block-frequency set is nevertheless convex, and a cost-clock tail argument gives the correct expected-cost coefficient.

Let \(h=(\theta,z,p,q)\) be a fixed true state with
\(1/2\le q<p\le1-\eta\), and let
\(R=\log(1/\delta)\), \(M_\delta/R\to\alpha<\infty\).
All dimensions, the action menu, source accuracy r, positive per-read cost ell, and activation cost c are fixed as delta tends to zero. No uniformity in a vanishing gap, growing depth cap, changing costs, or r approaching a boundary is asserted.

Write \(\mathcal E\) for the finite block-action set. Action e has known cost
\[
w_e=c+\ell(n_A+n_B),\qquad
0<w_{\min}\le w_e\le w_{\max}<\infty,
\]
finite alphabet \(\mathcal Y_e\) of size \(m_e=(n_A+1)(n_B+1)\), and full block-count distribution \(P_h^e\). Let
\[
D_e(h,h')=D(P_h^e\Vert P_{h'}^e),\qquad
D_0(h,h')=\operatorname{kl}(p,u)+\operatorname{kl}(q,v)
\]
for \(h'=(\theta',z',u,v)\). Alternatives range over
\[
\mathcal H_{\ne\theta}=
\{(\theta',z',u,v):\theta'\ne\theta,
\ 1/2\le v\le u\le1-\eta\}.
\]
The closure is used for optimization. Correctness is required on the original strict domain, and continuity extends information inequalities to its closure.

For \(a\ge0\), define
\[
K(h,a)=\min_{x\ge0}\left\{w\cdot x:
 aD_0(h,h')+\sum_ex_eD_e(h,h')\ge1
 \quad\forall h'\in\mathcal H_{\ne\theta}\right\}.
\tag{1}
\]

**Theorem.** The program is finite, positive, and attained. There is an explicit ongoing exploration-and-tracking policy with a uniformly delta-correct grouped likelihood-ratio stop, finite expected online cost at every admissible instance for every delta, and
\[
\boxed{
\inf_{\pi\ \mathrm{uniformly}\ \delta\text{-correct}}
\mathbb E_h C_{\pi,\delta}
=K(h,\alpha)\log(1/\delta)+o(\log(1/\delta)).}
\tag{2}
\]
The infimum is for recovering theta, not for certifying z. No same-theta nuisance constraint is inserted in (1). All mixed blocks remain in the action menu and all wrong-theta alternatives remain in the program.

## 2. Compactness and bounded likelihoods

For each permitted count pair, the block probability is a positive mixture of products of extraction probabilities. Since extraction probabilities and their complements are bounded below by eta, the finite collection of block alphabets has a common strictly positive lower probability bound over the entire compact alternative domain and all discrete labels. Binomial multiplicities do not compromise positivity.

Consequently all categorical log likelihood ratios and all KL divergences are bounded. The functions \(D_e\) and \(D_0\) are jointly continuous in the true and alternative levels, uniformly on compact sets. In particular, for a fixed true state, finite constants exist with
\[
D_* =\max_{e,h'}D_e(h,h'),\qquad
A_* =\max_{h'}D_0(h,h'),
\]
and with a common bound on every categorical log probability ratio. The two reference streams are Bernoulli streams with the same bounded-probability property.

The information program is convex: each constraint is affine in x for a fixed alternative, and the full feasible set is an intersection of such half-spaces. No Bernoulli isotonic formula for its inner optimization is assumed.

## 3. A positive-online-information lemma

This is the main separation fact needed to retain an expected-cost proof with finite offline information.

Define the effective accuracy of one extraction from a fresh root by
\[
\psi(a)=\tfrac12+(2r-1)(a-\tfrac12),
\quad
B_a=\operatorname{kl}(\psi(a),1/2),
\quad
\kappa_r=\operatorname{kl}(r,1-r).
\]
Set
\[
B_{\min}=\min_{a\in\{p,q\}:a>1/2}B_a>0,
\qquad \chi=B_{\min}/\kappa_r>0.
\tag{3}
\]
When q=1/2 its zero contribution is omitted; p always remains.

Let \(h^{(j)}\) reverse only fact j, retaining the true types and levels. For an action on j put
\(A_e=D_e(h,h^{(j)})\). Every feasible x in (1) satisfies
\[
\sum_{e:\,e\text{ queries }j}x_eA_e\ge1,
\tag{4}
\]
because that alternative has zero offline KL. Source-to-extraction data processing gives \(A_e\le\kappa_r\). Also \(A_e>0\) exactly when the action includes at least one response with true extraction accuracy greater than one half.

Now take any wrong-theta alternative h', and select a fact j it reverses. If \(A_e>0\), choose a queried format with true accuracy a>1/2. The block-count outcome can be postprocessed by selecting a uniformly random response from that format: conditional on its count s, return a positive response with probability s/n. Thus the one-response Bernoulli law is a randomized function of the actual observed counts.

Under h, the probability this response agrees with the true theta_j is \(\psi(a)>1/2\). Under h', its probability of agreeing with that same sign is at most one half, because the alternative fact sign is reversed and both alternative extraction levels are at least one half. Bernoulli data processing therefore gives
\[
D_e(h,h')\ge B_a\ge B_{\min}
\ge\chi A_e.
\]
If \(A_e=0\), the last inequality follows simply from nonnegative KL. Summing and using (4) proves
\[
\boxed{\quad
J_h(x,h'):=\sum_ex_eD_e(h,h')\ge\chi
\quad\text{for every feasible x and every wrong-theta h'.}\quad}
\tag{5}
\]
This handles arbitrary mixed blocks and q=1/2. It does not require a one-truth-flip reduction for arbitrary alternatives.

For local strict feasibility, let y allocate one count to every one-read action (both formats for every fact), and zero to other actions. Every wrong alternative flips some fact; its true-good one-read action supplies at least B_p. Thus
\[
J_h(y,h')\ge B_p>0\qquad\forall h'.
\tag{6}
\]
The lower bound remains positive locally around the fixed true levels.

## 4. Program existence and local stability

Equation (6) makes y/B_p feasible at every a>=0, giving
\[
K(h,a)\le\frac{2d(c+\ell)}{B_p}<\infty.
\]
Summing (4) over facts, and using \(A_e\le\kappa_r\), gives
\[
\sum_ex_e\ge d/\kappa_r,
\qquad K(h,a)\ge w_{\min}d/\kappa_r>0.
\tag{7}
\]
Positive action costs make bounded objective sublevel sets compact. The feasible set is closed, so an optimum is attained.

Fix the true discrete labels. If \((h_n,a_n)\to(h,\alpha)\), constraint left sides converge uniformly over the compact alternative set on every bounded x set. For a true optimizer x, let \(\omega_n\to0\) bound its maximum constraint deficit under \((h_n,a_n)\). Equation (6) makes
\[
x+(\omega_n/B_{p_n})y
\]
feasible for the nearby program. This proves the upper bound on the limiting optimal value. Nearby optimizers are bounded by the locally uniform upper bound and positive costs; every subsequential limit is feasible at the limit parameters. This proves continuity of K and upper hemicontinuity of its optimal set.

Write \(K=K(h,\alpha)\) and
\[
\mathcal X^*=\{x:x\text{ is optimal at }(h,\alpha)\},
\qquad
\mathcal W=\{x/(\mathbf1\cdot x):x\in\mathcal X^*\}.
\tag{8}
\]
The count-normalized optimal set W is nonempty and compact. **It is also convex despite differing total block counts.** Indeed, if \(v_i=x_i/n_i\) for \(n_i=\mathbf1\cdot x_i>0\), then \(\lambda v_1+(1-\lambda)v_2\) is the normalization of the optimal convex combination of x_1 and x_2 with coefficients proportional to \(\lambda/n_1\) and \((1-\lambda)/n_2\).

The inverse normalization is explicit:
\[
x=\frac{K}{w\cdot v}v\in\mathcal X^*,\qquad v\in\mathcal W.
\tag{9}
\]
For every wrong alternative, put \(j_v(h')=J_h(v,h')/(w\cdot v)\). From (1), (5), and (9),
\[
\alpha D_0(h,h')+Kj_v(h')\ge1,
\qquad
j_v(h')\ge\lambda_0:=\chi/K>0,
\tag{10}
\]
and \(j_v(h')\le D_*/w_{\min}\).

Upper hemicontinuity, the positive lower bound on total counts, and continuity of normalization imply: for any rho>0, correct discrete labels, sufficiently accurate estimated levels, and a calibration ratio sufficiently close to alpha ensure that **every** normalized estimated optimizer is within rho of W in l1. No unique optimizer or continuous optimizer selection is needed.

## 5. Lower bound with the finite calibration term

For any uniformly delta-correct policy with finite expected cost under h, bounded increments and finite expected block count justify the stopped likelihood chain rule:
\[
M_\delta D_0(h,h')+
\sum_e\mathbb E_hN_e(\tau)D_e(h,h')
\ge b_\delta:=\operatorname{kl}(1-\delta,\delta)
\tag{11}
\]
for every wrong-theta alternative in the strict domain. The decision event is “output the true theta.” Continuity extends the inequality to the closure.

Equivalently, normalization by b_delta gives
\[
\mathbb E_hC_\tau\ge
b_\delta K(h,M_\delta/b_\delta).
\tag{12}
\]
Since \(b_\delta/R\to1\), \(M_\delta/b_\delta\to\alpha\), and K is continuous, (12) proves the liminf in (2). Infinite expected cost already satisfies the lower bound. The reference data are included in information but excluded from online cost, exactly as stipulated.

## 6. Valid categorical grouped-GLR stopping

The full likelihood includes both reference streams and one categorical observation per completed block. For each theta, profile over z and the compact continuous level domain. Stop when the best theta profile exceeds every other theta profile by at least
\[
\boxed{\quad
\beta(n,\delta)=R+2\log(M_\delta+1)
+\sum_{e\in\mathcal E}
\log\binom{N_e(n)+m_e-1}{m_e-1}.\quad}
\tag{13}
\]
Here n is the online block count. The simpler larger bound replacing each last term by \((m_e-1)\log(N_e(n)+1)\) is also valid.

**Proof of uniform error control.** Saturate the model with one unrestricted categorical distribution per block action and independent Bernoulli distributions for the two reference streams. Give each categorical distribution a Dirichlet(1,...,1) prior and each Bernoulli stream a Beta(1,1) prior.

For a categorical stream with count N and category counts n_y, the integrated likelihood is
\[
Q_e=\frac{(m_e-1)!\prod_y n_y!}{(N+m_e-1)!}
=\frac{1}{\binom{N+m_e-1}{m_e-1}
                 \binom{N}{(n_y)_y}}.
\]
Because a multinomial probability is at most one,
\[
\sup_\mu L_e(\mu)
\le\binom{N+m_e-1}{m_e-1}Q_e.
\]
Each reference stream contributes the analogous factor M_delta+1. Thus the supremum model likelihood is at most the product-mixture likelihood Q times the exponential of the non-R part of (13).

Under the true state, Q/L(h) is a nonnegative mean-one likelihood-ratio martingale when the initial offline sampling period is included. Predictable adaptive block choices do not alter this: their action kernels cancel. At a wrong stop, the competing-answer denominator includes the true-state likelihood, so (13) forces Q/L(h)>=1/delta. Ville's inequality bounds the probability of any wrong stop by delta.

This is a marginal guarantee over calibration randomness, not a guarantee conditional on each realized calibration sample. No assumed independence of the responses *within* a root is used in the saturated mixture; the block outcome is one categorical draw. Almost-sure stopping is supplied below.

## 7. Estimation, exploration, and deterministic tracking

Let A be the number of block actions. Force each action once on rounds
\[
Ak^2+1,\ldots,Ak^2+A\quad(k=0,1,\ldots).
\tag{14}
\]
These blocks are disjoint. The number F(n) of forced rounds is O(sqrt(n)), and every action has order sqrt(n) forced observations.

Use only the forced one-read actions to estimate levels and labels. The two empirical positive-response probabilities for fact j have a sum-minus-one whose true sign is theta_j, separated from zero by
\((2r-1)(p+q-1)>0\). Orient the probabilities by the estimated fact sign. Comparing group averages identifies the preferred format with gap \((2r-1)(p-q)>0\). Invert the known map psi to estimate extraction accuracy, average estimated good and other levels, and project onto a deterministic finite grid in the strict level domain with covering radius over its closure tending to zero. Ties are deterministic.

For every fixed estimation tolerance zeta, Hoeffding bounds give
\[
\Pr_h\{\widehat\theta_n\ne\theta\text{ or }
\widehat z_n\ne z\text{ or }\|(\widehat p_n,\widehat q_n)-(p,q)\|>\zeta\}
\le C_\zeta e^{-c_\zeta\sqrt n}
\tag{15}
\]
for sufficiently large n. These constants do not depend on delta. Inversion by 2r-1 is legitimate because r is fixed and greater than one half. The argument covers q=1/2 and p=1-eta.

At every exploitation round solve (1) at the current estimated state and known ratio \(\alpha_\delta=M_\delta/R\), selecting any fixed measurable optimizer. Normalize it by its **total count**, not its weighted cost, to get a target action probability vector. The grid and deterministic tie rule make an ordinary measurable selection possible; no continuous optimizer rule is required.

Maintain cumulative desired exploitation counts S and actual exploitation counts N_exp. After adding the next target to S, choose the action maximizing S_e-N_exp,e. For an arbitrary sequence of target vectors, this deterministic cumulative-deficit rule has a uniformly bounded l1 discrepancy:
\[
\|N_{\rm exp}-S\|_1\le C_A.
\tag{16}
\]
For completeness, the discrepancy vector N_exp-S sums to zero. Immediately before the chosen action its coordinates sum to -1; incrementing its minimum coordinate leaves every coordinate at most 1 by induction. The zero sum bounds each below by -(A-1). This proves a finite constant bound.

For all sufficiently small delta, alpha_delta is close to alpha. Combine the stability statement following (10), the estimator tail on the interval from gamma*n to n, convexity of W, and (16). For every fixed a>0 there exist constants such that
\[
\Pr_h\{\operatorname{dist}_1(N(n)/n,\mathcal W)>a\}
\le C n e^{-c\sqrt n}
\tag{17}
\]
for all sufficiently large n. To verify it explicitly: approximate each accurate late target by a point of W; replace early and forced targets by arbitrary points of W. Their average is in W. The l1 error is at most rho+2gamma+2F(n)/n+C_A/n. Choose rho,gamma sufficiently small and apply a union bound to (15). This controls nonunique estimated optimizers as well as arbitrary jumping between them.

## 8. Information margin at an actual cost threshold

Let \(C_n=w\cdot N(n)\). Fix epsilon>0 and put
\[
T_\delta=(K+\epsilon)R,
\quad b_\epsilon=\epsilon/(K+\epsilon),
\quad m_0=\lambda_0 b_\epsilon w_{\min}>0.
\]
Suppose C_n>=T_delta and N(n)/n is within l1 distance a of a point v in W. For every wrong alternative,
\[
\left|J_h(N(n),h')-C_n j_v(h')\right|
\le H_* a n,
\quad H_*=D_*\left(1+\frac{w_{\max}}{w_{\min}}\right).
\tag{18}
\]
Indeed subtract n*v, and use \(j_v\le D_*/w_{\min}\) to bound both the information difference and the corresponding cost difference. This is the step that replaces an invalid assumption of a common optimal block-count coefficient.

Using (10) and \(C_n-KR\ge b_\epsilon C_n\ge b_\epsilon w_{\min}n\),
\[
\begin{aligned}
M_\delta D_0+J_h(N(n),h')
&\ge R+(C_n-KR)j_v(h')
 -|\alpha_\delta-\alpha|R A_*-H_*an\\
&\ge R+m_0n
 -|\alpha_\delta-\alpha|R A_*-H_*an.
\end{aligned}
\tag{19}
\]
Since C_n<=w_max*n and C_n>=T_delta,
\(R\le w_{\max}n/(K+\epsilon)\). Choose a with H_*a<=m_0/4 and then choose delta sufficiently small that
\[
|\alpha_\delta-\alpha|A_*w_{\max}/(K+\epsilon)\le m_0/4.
\]
On the allocation-good event,
\[
\boxed{\quad
\inf_{h'\in\mathcal H_{\ne\theta}}
\{M_\delta D_0(h,h')+J_h(N(n),h')\}
\ge R+\tfrac12m_0n
\quad\text{whenever }C_n\ge T_\delta.\quad}
\tag{20}
\]
There is no convergence-rate assumption on alpha_delta beyond its stated limit.

## 9. Uniform continuous-alternative likelihood concentration

For each categorical stream e and outcome y define
\[
Z_{e,y}(n)=S_{e,y}(n)-N_e(n)P_h^e(y).
\]
Treat the two reference streams as categorical streams with two outcomes and fixed count M_delta. The exact finite-alphabet likelihood identity is
\[
\log\frac{L_n(h)}{L_n(h')}
=M_\delta D_0(h,h')+J_h(N(n),h')
+\sum_{e,y}Z_{e,y}(n)
\log\frac{P_h^e(y)}{P_{h'}^e(y)},
\tag{21}
\]
where the sum includes both reference streams using their own Bernoulli probabilities.

Because all probabilities are uniformly positive, there is a finite constant B_* such that the supremum absolute remainder over **all continuous alternatives and discrete labels** is at most
\[
B_*\sum_{e,y}|Z_{e,y}(n)|.
\tag{22}
\]
Every online residual is a bounded-increment martingale over n rounds. Every offline residual is a sum of M_delta independent bounded variables. At the relevant deterministic horizons \(n\ge T_\delta/w_{\max}\), the ratio M_delta/n is uniformly bounded for sufficiently small delta. Azuma/Hoeffding and a union over the fixed finite collection of categories therefore give
\[
\Pr_h\{B_*\sum_{e,y}|Z_{e,y}(n)|>m_0n/4\}
\le C e^{-cn}.
\tag{23}
\]
No continuous-parameter covering net is necessary.

The boundary overhead in (13) is O(log(n+1)) at these horizons: M_delta=O(n), N_e<=n, and all m_e are fixed. Combining (17), (20), and (23), for sufficiently small delta and sufficiently large n with \(n\ge T_\delta/w_{\max}\),
\[
\boxed{\quad
\Pr_h\{\tau_\delta>n,\ C_n\ge T_\delta\}
\le C n e^{-c\sqrt n}.\quad}
\tag{24}
\]
On the complementary event, the true-state likelihood exceeds every wrong-answer likelihood by the boundary, so the grouped profile rule has stopped. Here actions and observations are understood as continued past the first stopping time for analysis.

## 10. Cost-clock tail and expected online cost

It would be incorrect to replace K by a fixed common block-count coefficient; different optimal allocations can have different costs per block. Instead use the hitting index
\[
\nu_s=\inf\{n:C_n\ge s\}
\]
in the indefinitely continued policy. Deterministic bounded positive action costs give
\[
\lceil s/w_{\max}\rceil\le\nu_s\le\lceil s/w_{\min}\rceil,
\qquad C_{\nu_s}<s+w_{\max}.
\tag{25}
\]
For s>=T_delta, the event \(C_{\tau_\delta}>s+w_{\max}\) implies \(\tau_\delta>\nu_s\). Union over the finite possible hitting indices, and use (24) since C_n>=s on the hitting event:
\[
\Pr_h\{C_{\tau_\delta}>s+w_{\max}\}
\le C s^2 e^{-c\sqrt s}
\quad(s\ge T_\delta)
\tag{26}
\]
for sufficiently small delta, after adjusting constants. The extra polynomial factor is harmless; its integral has a vanishing tail.

The real-valued tail integral therefore yields
\[
\mathbb E_h C_{\tau_\delta}
\le (K+\epsilon)R+w_{\max}
 +\int_{T_\delta}^\infty C s^2e^{-c\sqrt s}\,ds
=(K+\epsilon)R+O(1).
\tag{27}
\]
The constants in this epsilon-dependent bound are not claimed uniform as epsilon tends to zero. Divide by R, let delta tend to zero, and then let epsilon tend to zero. Together with (12), this proves (2).

Finite expected cost and almost-sure stopping hold at every fixed delta as well. Repeat the argument with a=alpha_delta as the fixed true reference ratio, its optimal set and K(h,alpha_delta); then no calibration-ratio approximation term occurs. All thresholds and M_delta are finite. Starting at a sufficiently large cost s yields the same integrable tail, with constants allowed to depend on that fixed delta.

## 11. Oracle, calibration costs, and proof boundaries

The type-informed oracle restricts alternatives and profiles to its known z, but retains unknown continuous u,v, the same calibration sample, block laws, and online costs. The proof applies with this restricted alternative set: same-level truth flips still enforce (4), one-read exploration still estimates true facts and levels, and all compactness and likelihood arguments remain valid.

If each calibration observation costs b_cal, the total expected acquisition cost is
\[
2b_{\rm cal}M_\delta+\mathbb E_h C_\tau
=(2b_{\rm cal}\alpha+K(h,\alpha))R+o(R).
\]
This added common resource cost does not change whether learner and type-informed oracle **online** coefficients are equal. It does change ratios of total costs and must be reported explicitly.

The proof does not establish:

- A one-truth-flip reduction for general mixed-block alternatives.
- A pure-good-block oracle, a scalar Gamma criterion, or monotonicity in source cost.
- The known-rate oracle as the appropriate comparator for this continuous model.
- Uniform achievability for alpha tending to infinity with delta, growing L_max, or changing costs.
- Correctness of a finite grid used in the stopping likelihood; the grid is only for the allocation estimate, and the stop profiles the continuous closure.
- Certified implementation from an ordinary numerical optimizer or floating-point likelihood calculation.

The correct conclusion is **GO for the joint information program and ideal expected-online-cost theorem** in this fixed completed-block model. Structural reductions, oracle geometry, and empirical applicability require their own proofs or evidence. The generic likelihood-ratio and information-allocation tools are established machinery; this proof is not a novelty claim.
