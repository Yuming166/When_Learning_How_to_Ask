# Perfect sources remove the necessity of depth mixing

Date: 2026-11-01. This is an analytic mechanism-control theorem. It deliberately extends the preceding model to the boundary **r=1, known under every hypothesis**. Earlier results for r in (1/2,1) remain unchanged. The general proof below does not depend on a numerical parameter grid.

## 1. Fixed scope and notation

Keep the [unknown-extraction model](../web_unknown_calibration_20261031/MODEL_AND_SCOPE.md), with only the source reliability changed to r=1. There are d fixed binary truths, a known partition into nonempty groups, and an unknown preferred format z_g per group. The common extraction rates satisfy

\[
1/2\le q<p\le1-\eta,\qquad 0<\eta<1/2.
\]

Every block (j,a,b) concerns one fact j, uses a new source, and contains a readings of format A and b of format B, with 1<=a+b<=N for a fixed finite cap N. Its cost is c+ell(a+b), where c>=0 and ell>0. All compositions are available. A whole block is selected before any of its outcomes; only its two positive counts are observed. There are no revisits, within-block adaptation, direct type queries, or shared access costs across different facts.

At r=1 a source report equals the fact deterministically. Conditional on the fixed state, extraction randomness is fresh and independent, including across readings of one source. The model still has unknown p,q and unknown preferred formats. It does **not** assert that an unverified real webpage is perfectly reliable.

Two independently labelled reference streams have laws Bern(p) and Bern(q), each of length M_delta with M_delta/log(1/delta)->alpha<infinity. Their identities and information match the original [Theory_Note.md](../../Theory_Note.md). Their common already-acquired cost is excluded from online cost. The oracle knows z only, not theta,p,q; both sides receive the same calibration.

Let h=(theta,z,p,q). For a single extraction of format m on fact j define its positive-response probability

\[
\mu_{jm}(h)=\frac{1+\theta_j(2e_{jm}(h)-1)}2,
\qquad
e_{jm}(h)=\begin{cases}p,&m=z_{g(j)},\\q,&m\ne z_{g(j)}.\end{cases}
\]

For an alternative h'=(theta',z',u,v), use the same formula with ordered rates 1/2<=v<=u<=1-eta, including the compact closure. Put

\[
d_{jm}(h,h')=\operatorname{kl}(\mu_{jm}(h),\mu_{jm}(h')),
\qquad C(h,h')=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]

For either comparison class B in {learner,oracle}, H_B consists of all wrong-truth alternatives, with arbitrary z' for the learner and fixed z'=z for the oracle. Define the original unit-cost independent-read coefficient, **with direct type queries absent**, by

\[
T_B(h,\alpha)=\min_{t\ge0}\left\{\sum_{j,m}t_{jm}:
\alpha C(h,h')+\sum_{j,m}t_{jm}d_{jm}(h,h')\ge1
\quad\forall h'\in H_B\right\}.
\tag{1}
\]

Write K_B^(N) for the perfect-source block information-program coefficient, and K_B,[L] for its restriction to depth L, retaining every format composition at that depth.

## 2. Main theorem

**Theorem (exact cost scaling and maximal-depth sufficiency).** For every admissible fixed h, fixed d, partition, N, c,ell, and finite alpha,

\[
\boxed{K_B^{(N)}(h,\alpha)=\left(\ell+\frac cN\right)T_B(h,\alpha),
\quad B\in\{\mathrm{learner},\mathrm{oracle}\}.}
\tag{2}
\]

The same value is attained using only the 2d pure-format cap actions (j,N,0) and (j,0,N). In particular, a single common depth N suffices for every fact, even for the unknown-format learner.

If c>0, **every information-optimal full-menu allocation is supported only at depth N**. This is a statement about asymptotic allocation coefficients; an asymptotically optimal policy may still make a sublinear number of shorter blocks.

For any fixed L in {1,...,N},

\[
\boxed{K_{B,[L]}=\left(\ell+\frac cL\right)T_B,\qquad
K_{B,[L]}-K_B^{(N)}=c\left(\frac1L-\frac1N\right)T_B.}
\tag{3}
\]

Since T_B>0, shorter fixed depths are strictly worse if c>0 and L<N. If c=0, every fixed depth can attain the same optimum ell T_B; not every allocation is thereby optimal. If N=1, the statement is immediate.

These are also the exact leading **expected online-cost** coefficients for uniformly delta-correct policies. There exist policies using only pure-format depth-N blocks with finite expected cost and

\[
\inf_\pi\mathbb E_h C_{\pi,\delta}
=K_B^{(N)}(h,\alpha)\log(1/\delta)
+o(\log(1/\delta)).
\tag{4}
\]

All asymptotics are pointwise with d,N,c,ell,h fixed. No finite-delta policy equivalence or growing-cap guarantee is asserted.

## 3. Additive KL for the actual observed counts

At r=1, for block (j,a,b), the two observed counts have the product law

\[
P_h^{j,a,b}(s,t)=\binom as\mu_{jA}^{s}(1-\mu_{jA})^{a-s}
\binom bt\mu_{jB}^{t}(1-\mu_{jB})^{b-t}.
\tag{5}
\]

The binomial coefficients cancel in the likelihood ratio against any h'. Its logarithm is a sum of s, a-s, t, b-t times the corresponding single-read log ratios. Taking expectation and using E s=a mu_jA and E t=b mu_jB gives

\[
\boxed{D(P_h^{j,a,b}\Vert P_{h'}^{j,a,b})
=a\,d_{jA}(h,h')+b\,d_{jB}(h,h').}
\tag{6}
\]

This holds simultaneously for every truth flip, type pattern, and continuous rate alternative. It is an identity for the observed counts, not an argument requiring access to an unobserved ordered response sequence. Unknown p,q do not break it because r=1 holds under both hypotheses.

## 4. Repacking preserves every information constraint

Given a nonnegative block allocation x, let its read totals be

\[
t_{jA}=\sum_{a,b}a x_{j,a,b},\qquad
t_{jB}=\sum_{a,b}b x_{j,a,b}.
\tag{7}
\]

By (6), its complete online KL against every alternative is exactly sum t_jm d_jm. The calibration term is unchanged. Therefore x is block-feasible if and only if its t is feasible in (1).

Let S=sum t_jm=sum (a+b)x_jab. Its cost has the exact decomposition

\[
\sum_{j,a,b}(c+\ell(a+b))x_{j,a,b}
=\left(\ell+\frac cN\right)S
+c\sum_{j,a,b}\left(1-\frac{a+b}{N}\right)x_{j,a,b}.
\tag{8}
\]

The last term is nonnegative. Thus every feasible x costs at least (ell+c/N)T_B.

Conversely, given any feasible t, define

\[
\widehat x_{j,N,0}=t_{jA}/N,\qquad
\widehat x_{j,0,N}=t_{jB}/N,
\tag{9}
\]

and all other coordinates zero. Its read totals equal t exactly. It preserves all constraints, including the coupled calibration and group alternatives, and costs (ell+c/N)sum t. Applying this to an optimizer of (1) proves (2) and the cap-only pure-format realization.

If c>0 and an optimal x assigned positive mass to any depth below N, (8)-(9) would strictly reduce cost without changing any constraint. This contradiction proves the all-optima support statement. The same argument with L in place of N gives (3).

More precisely, the full optimal set for c>0 consists exactly of the cap-supported allocations whose projected read totals solve (1). Such learner allocations may contain mixed-format cap blocks; pure blocks are sufficient, not mandatory. For c=0, any depth decomposition of an optimal t is optimal.

## 5. Why the expected-cost theorem extends to r=1

The preceding [continuous expected-cost proof](../web_unknown_calibration_20261031/CONTINUOUS_COST_PROOF.md) assumed r<1. Its positive-online-information argument divided by kl(r,1-r), which is infinite at r=1. Taking that formula's limit would not supply the required positive bound. We replace that step explicitly.

### 5.1 Positive online information and program stability

Let kappa(e)=kl(e,1-e) and

\[
\chi=\min_{e\in\{p,q\}:e>1/2}
\frac{\operatorname{kl}(e,1/2)}{\kappa(e)}>0.
\tag{10}
\]

The p term always exists; omit q if q=1/2. Both p,q are bounded below one, so every included denominator is finite and positive.

For any feasible allocation, consider the alternative reversing only fact j at the true types and rates. Its calibration KL is zero. In projected read totals it enforces

\[
\sum_m t_{jm}\kappa(e_{jm})\ge1.
\tag{11}
\]

Now take any wrong-truth alternative h', and select a fact j that it reverses. A response agreeing with true theta_j has true probability e_jm, but alternative probability at most 1/2. Thus

\[
d_{jm}(h,h')\ge\operatorname{kl}(e_{jm},1/2)
\ge\chi\kappa(e_{jm}).
\]

For e_jm=1/2 both right-hand quantities are zero. Combining with (11) and nonnegativity from other facts proves

\[
\boxed{\sum_ex_eD_e(h,h')\ge\chi
\quad\text{for every feasible x and every wrong-truth h'.}}
\tag{12}
\]

This replaces the failed source-KL denominator at the boundary.

To establish strict feasibility using only cap actions, allocate one block to each of the 2d pure-format cap streams. Every wrong alternative reverses a fact whose true-good stream supplies at least N kl(p,1/2)>0. This separation remains positive locally. Same-level truth flips imply

\[
\sum_{j,m}t_{jm}\ge d/\kappa(p)>0.
\]

Positive action costs and finite N give compact bounded-cost sublevels. Closed constraints and strict feasibility imply attained optima, local boundedness and continuity of values, and upper hemicontinuity of optimal sets by the feasible-repair argument in the preceding proof. These statements apply to both the full menu and the pure cap menu.

### 5.2 Estimation without any shorter block

For the cap-only policy, force each of the 2d streams on a square-root schedule. A block count divided by N is an independent bounded observation with mean mu_jm. The sign of mu_jA+mu_jB-1 identifies theta_j with nonzero gap p+q-1; after orientation, group differences identify z_g with gap p-q. The two oriented levels then estimate p,q.

Hoeffding bounds over the forced blocks give error probabilities at most C exp(-c_0 sqrt(n)) at each fixed estimation tolerance, with n the block count. The mean estimator uses counts, so it respects the actual observation and no-within-block-decision protocol. The oracle needs only the analogous truth/rate estimates with z fixed.

At each exploitation step, solve the cap-menu information program at the current estimate and alpha_delta=M_delta/log(1/delta), normalize the optimal counts, and track the desired frequencies with the deterministic cumulative-deficit rule. This uses exact optimization; no solver approximation guarantee is claimed.

### 5.3 Correct stopping and integrable tails

Every cap stream has N+1 count outcomes, each of probability at least eta^N under every state and alternative. Thus the categorical likelihood and log-ratio bounds remain finite even though the latent source report is degenerate.

Use the grouped profile likelihood over complete truth vectors and unknown parameters, including both calibration streams. A valid boundary at block n is

\[
\beta(n,\delta)=\log(1/\delta)+2\log(M_\delta+1)
+\sum_{j,m}\log\binom{N_{jm}(n)+N}{N},
\tag{13}
\]

where N_jm(n) is the number of cap blocks, not the number of individual reads. A Dirichlet(1,...,1) mixture per categorical stream and a Beta(1,1) mixture per calibration stream give the same likelihood-ratio martingale proof as before. Hence the rule is uniformly delta-correct, marginally over calibration randomness.

With all cap blocks costing w_N=c+ell N, cost is exactly w_N n. The normalized optimal allocation set is convex and compact. The estimator tail, local stability, and bounded tracking discrepancy yield allocation-error probabilities C n exp(-c_0 sqrt(n)). Equation (12) supplies a strictly positive information growth rate beyond the target cost (K_B^(N)+epsilon)log(1/delta). The finite-alphabet residual identity controls all continuous alternatives simultaneously; its failure probability decays exponentially in n. The overhead in (13) is O(log n) at relevant horizons.

Consequently, for every fixed epsilon>0 and sufficiently small delta, the continued policy satisfies

\[
\Pr_h\{C_{\tau_\delta}>s+w_N\}
\le C s^2e^{-c_0\sqrt{s}},
\quad s\ge(K_B^{(N)}+\epsilon)\log(1/\delta),
\tag{14}
\]

after increasing the fixed starting horizon if needed. Constants may depend on the instance and epsilon. Integrating gives the limsup coefficient K_B^(N); the same argument with alpha_delta fixed gives almost-sure stopping and finite expectation for each fixed delta.

For the lower bound, the stopped transcript KL is M_delta C plus expected action counts times (6). Uniform delta-correctness makes it at least kl(1-delta,delta). Dividing by that quantity and using continuity of the program at M_delta/kl(1-delta,delta)->alpha yields the matching liminf. This proves (4).

This is an endpoint extension with its failed hypothesis repaired, not an appeal to continuity in r and not an exact finite-delta simulation of an adaptive single-read policy by batches.

## 6. Original oracle and sharing results are recovered exactly

Let a_alpha denote the scalar from original Theorem 2, so the independent-read oracle coefficient is d a_alpha and its unique optimal read allocation gives a_alpha to the good format of every fact and zero to the other format. Then

\[
K_{\rm oracle}^{(N)}=(\ell+c/N)d a_\alpha.
\tag{15}
\]

If c>0, the unique block allocation has a_alpha/N pure-good depth-N blocks per fact and no other blocks. If c=0, the good-format read totals are still unique but their depth decompositions can differ.

Write Gamma_k(alpha) for the original smallest-sharing-group quantity, with the original p,q calibration and without direct type queries. Because both sides are multiplied by the same positive factor,

\[
\boxed{K_{\rm learner}^{(N)}=K_{\rm oracle}^{(N)}
\iff T_{\rm learner}=T_{\rm oracle}
\iff\Gamma_{k_{\min}}(\alpha)\ge1.}
\tag{16}
\]

Likewise,

\[
K_{\rm learner}^{(N)}-K_{\rm oracle}^{(N)}
=(\ell+c/N)(T_{\rm learner}-T_{\rm oracle}),\qquad
\frac{K_{\rm learner}^{(N)}}{K_{\rm oracle}^{(N)}}
=\frac{T_{\rm learner}}{T_{\rm oracle}}.
\tag{17}
\]

Thus at r=1, source access cost and a common depth cap rescale both online costs but **do not change the zero-premium sharing criterion or the relative format premium**. They can change the absolute premium through the scale factor. This contrasts with the nontrivial cost-dependent sharing structure already proved for the known-extraction-rate imperfect-source model; a general scalar criterion for imperfect sources with finite calibration remains open.

## 7. Mechanism comparison with the existing theorems

For the following table, the comparison object is consistently the **format-aware oracle**. The rates are always p=.95,q=.6; take d=1,N=6,c=ell=1,eta=.025 and alpha=1, supplying the same calibration when rates are additionally revealed.

| Source condition | Extraction-rate information | Optimal depth conclusion | Evidence |
|---|---|---|---|
| r=1, known perfect | p,q unknown; finite calibration | Every optimal allocation has depth 6; pure-good allocation is unique | Equations (2), (8), and (15) |
| r=.6, persistent imperfect | p,q additionally revealed | Unique optimum is pure-good depth 1 | Existing exact known-rate comparison in DEPTH_MIXING_CERTIFICATE.json |
| r=.6, persistent imperfect | p,q unknown; finite calibration | Every optimal allocation uses at least two depths | Existing full-menu continuous certificate: K_or<=34<41.3<=min_L K_L |

The last phenomenon persists in the explicit [five-dimensional region](../web_depth_region_20261101/REGION_THEOREM.md), including alpha in [.95,1.20] and c/ell in [.5,1.5]. Its region-wide relative saving against all fixed depths is at least 5/103.

More generally, with known p,q and any fixed imperfect r, the existing [known-rate oracle theorem](../web_cost_sharing_20261031/THEORY_RESULTS.md) admits a pure-good single-depth optimum at a maximizer of truth KL per cost. Ties can allow other mixed-depth optima, so only the particular center instance above asserts uniqueness.

These controls show that neither unknown extraction rates alone nor persistent source errors with known extraction rates force multi-depth oracle allocation. Their joint presence with the stated finite calibration and costs can force it on a nondegenerate region. This is a mechanism separation within the model, not an empirical causal study or a classification of all imperfect-source instances.

## 8. Boundaries to keep explicit

- Perfect reliability must be known under all alternatives. Merely setting the true r to one while permitting uncertain source rates in alternatives does not give (6).
- Source access and extraction costs are homogeneous, and cap N is common to all facts/formats. Other cost functions need their own comparison.
- The fixed completed-block restriction is retained. Allowing indefinite source revisits or removing the finite cap defines another decision problem.
- No direct type-query action is present. Such an action has a different cost/information structure and is not scaled by repacking task reads.
- The theorem preserves total read information, not finite-delta adaptive histories. Batch boundaries can affect finite-budget performance.
- Every optimum having only maximal-depth support does not forbid o(log(1/delta)) shorter exploration blocks in another asymptotically optimal policy. Our attaining construction can itself use only maximal-depth blocks.
- Adding paid calibration changes total-cost ratios; formulas (2)-(3), (15)-(17) concern online costs.
- Count-law additivity and repacking are standard mathematical ingredients. The contribution of this control is to isolate the mechanism behind the previously certified persistent-source depth separation; no standalone priority claim is made for batching.
