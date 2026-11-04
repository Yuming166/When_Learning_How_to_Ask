# Independent derivation: top-1 geometry, irrelevant actions, and an exact AND example

Date: 2026-11-03.

This is an independent derivation by a same-family scoped reviewer. It is not external certification, a priority assessment, or an independent model-family review. The only project note read for this derivation was the original `Theory_Note.md`; no other worker's research notes were read. No model, API, GPU, training, or new empirical-elicitation calls were made. One short local CPU calculation evaluated the displayed closed forms; it is a sanity check, not their proof.

The main mathematical results below are information-allocation identities. Their interpretation as exact leading expected-cost coefficients uses the same controlled-sensing change-of-measure and matching-allocation framework as the original note, specialized to a finite decision map. This document does not independently re-prove that entire achievability framework.

## 1. Fixed model, changed decision, and notation

Retain the original observation and information assumptions:

- Signs are fixed, unknown, and belong to `{-1,+1}^d`.
- A known partition has unrestricted fixed unknown group types `z_g in {1,2}`; no type prior or cross-group constraint is assumed.
- The good and other forms have common unknown reliabilities `p,q`, with `1/2 <= q < p <= 1-eta`.
- Repetitions are fresh conditionally independent observations.
- There are two **labelled** reference streams, each of size `M_delta`, with `M_delta/log(1/delta) -> alpha`.
- The oracle knows `z` only. It does **not** know `p` or `q`.
- All task queries cost one. Dedicated type questions are absent in the results below.

The output is now

\[
 f(\theta)=\arg\max_i\{b_i+v_i^\top\theta\}.
\]

For clarity, assume the maximizer is unique at every sign vector in the parameter space. Every explicit catalogue below satisfies this assumption. If ties are excluded only on a restricted state space, that restriction must be stated; a tie-breaking convention must not be silently introduced.

Fix a true sign vector `theta`. For `F subseteq [d]`, write `theta^F` for the vector obtained by reversing exactly the signs in `F`. Define

\[
 \mathcal H=\min_{\subseteq}
 \{F\subseteq[d]:f(\theta^F)\ne f(\theta)\}.
\]

Thus `H` is the family of inclusion-minimal decision-changing flip sets. We assume the decision is nonconstant, so `H` is nonempty and none of its elements is empty.

For `r,x >= 1/2`,

\[
 D(r,1-x)-D(r,x)=(2r-1)\log\frac{x}{1-x}\ge0.
 \tag{1}
\]

Consequently every nonminimal decision-changing alternative is information-dominated by an alternative whose flip set belongs to `H`, at the same alternative types and rates. This reduction does **not** assume that the decision-changing family is upward closed. For example, reversing an additional sign may undo a threshold crossing; a decision-changing set still contains an inclusion-minimal decision-changing subset.

Let `K_f` and `K_or,f` denote the unknown-type and type-revealed information-program values at the fixed instance and calibration ratio. The normalized allocation variables are arbitrary per-coordinate counts `a_j,b_j`, for the true good and other form. Relabelling forms by their true type is a proof device only.

For a type-reversal set `J` and alternative levels `u >= v >= 1/2`, the good-form alternative accuracy in group `g` is `u` when `g notin J`, and `v` when `g in J`; the other-form accuracy is the remaining level. Flip sets reverse the corresponding Bernoulli mean. The calibration term is always

\[
 \alpha\{D(p,u)+D(q,v)\}.
\]

Nothing below reveals the rates to the oracle or treats an unlabelled task coordinate as a labelled reference stream.

## 2. Irrelevant coordinates cannot improve the leading coefficient

### Proposition 1: dominance of globally decision-irrelevant coordinates

Suppose `f(theta)` depends only on coordinates in a nonempty set `R`. Delete all other coordinates and delete empty sharing groups, retaining the induced partition on `R`. Under the coordinate/form interface above, for every finite `alpha >= 0`,

\[
 \boxed{
 K_f^{\rm all\ coordinates}=K_f^{R},\qquad
 K_{\rm or,f}^{\rm all\ coordinates}=K_{\rm or,f}^{R}.
 }
 \tag{2}
\]

In particular, a globally recommendation-irrelevant coordinate cannot strictly lower the optimal leading online cost through rate or type calibration.

**Proof.** Ignoring irrelevant coordinates proves the `<=` inequalities.

For the reverse direction, take any feasible full allocation. If an irrelevant coordinate belongs to a group that still contains relevant coordinates, transfer both of its normalized counts to any relevant coordinate in that same group. Preserve the good/other orientation. For an alternative changing the decision, keep all irrelevant signs unchanged. The transferred observations then have identical divergence if the recipient sign is unchanged, and at least as much divergence if it is reversed, by (1).

An entirely irrelevant group requires one additional step. Transfer its entire good/other allocation to any relevant coordinate in an active group, again preserving good/other orientation. Given any alternative in the reduced problem, extend it to the removed group by choosing its relative type reversal to be the same as that of the recipient group, and leave the removed signs unchanged. This is an allowed full-model alternative: types of different groups are unrestricted nuisance parameters. The old observations in the removed group have divergence `D(r,x)`; their replacements have either `D(r,x)` or `D(r,1-x)`. Hence the reduced allocation's information is at least that of this allowed full alternative. The labelled calibration term is unchanged.

This works for every reduced alternative and preserves total cost. The transferred allocation is therefore feasible in the reduced problem. The oracle proof is the same and simpler because each type is fixed. `square`

**Important limits.** This is a statement about optimal first-order information cost, not about a particular finite-budget estimator. It relies on equal task costs, the same global `(p,q)`, and the original unrestricted group types. It need not hold for a coordinate with a different channel, a special cheap measurement, additional structural restrictions on types, or an extra direct-type interface with heterogeneous costs or accuracies. Those are changes to the information assumptions.

A local version also follows. At a fixed true state, if a coordinate occurs in no member of `H`, all minimal decision-changing alternatives leave it unchanged. Its first-order allocation can be transferred by the same argument. Merely being outside one chosen certificate is weaker and does not imply this condition.

## 3. An exact general oracle formula at zero external calibration

This section sets `alpha=0`. Write

\[
 B_r=D(r,1/2)=\log2-H(r),\qquad h=p-1/2>0.
\]

For `t in [0,1]`, define

\[
 \begin{aligned}
 J_p(t)
 &=\inf_{1/2\le x\le1-\eta}
 \{(1-t)D(p,x)+tD(p,1-x)\}\\
 &=H\!\left(\max\{1/2,p-(2p-1)t\}\right)-H(p).
 \end{aligned}
 \tag{3}
\]

The fitted mean is `max{1/2,p-(2p-1)t}`. Thus `J_p` is increasing and strictly concave up to `t=1/2`, and is constant at `B_p` thereafter.

Let

\[
 \rho_*=
 \max_{w\in\Delta_d}\min_{F\in\mathcal H}\sum_{j\in F}w_j.
 \tag{4}
\]

Equivalently, if

\[
 \tau_*=
 \min_{x\ge0}\left\{\sum_jx_j:
                  \sum_{j\in F}x_j\ge1\quad\forall F\in\mathcal H\right\},
 \tag{5}
\]

then `rho_*=1/tau_*`. This is a fractional hitting-set problem for the decision-changing flip hypergraph.

### Theorem 2: unknown-rate oracle = a fractional flip-cover geometry

At `alpha=0`,

\[
 \boxed{K_{\rm or,f}=\frac1{J_p(\rho_*)}.}
 \tag{6}
\]

An oracle-optimal allocation uses only good-form queries. Its coordinate weights maximize `J_p(min_F w(F))`. If `rho_* >= 1/2`, every weight vector satisfying `w(F)>=1/2` for all `F` is optimal; uniqueness of the full-sign oracle allocation does not extend to a general decision.

**Proof of good-form dominance.** Put

\[
 \lambda=\frac{q-1/2}{p-1/2}\in[0,1).
\]

A binary symmetric channel with contraction factor `lambda` maps `Bern(p)` to `Bern(q)`, `Bern(u)` to `Bern(v_u)`, and `Bern(1-u)` to `Bern(1-v_u)`, where

\[
 v_u=1/2+\lambda(u-1/2)\le u.
\]

The pair `(u,v_u)` is admissible. Data processing gives

\[
 D(q,v_u)\le D(p,u),\qquad
 D(q,1-v_u)\le D(p,1-u).
 \tag{7}
\]

Move every other-form count `b_j` to the good form of the same coordinate. For any flip set, evaluate the mixed design at `(u,v_u)`. Its information is no larger than the all-good design evaluated at `u`; taking the infimum preserves this inequality. Thus good-form queries weakly dominate mixed oracle queries.

For completeness, domination is strict at a feasible oracle optimum whenever any other-form count is positive. For each flip set the all-good design's minimizing mean is below `p`, since that flip set must receive positive total mass. Both sign-preserving and sign-reversing good-form divergences at that mean are positive. Strict BSC contraction then makes the mixed design's information strictly smaller. There are finitely many flip sets, so scaling a dominated all-good allocation slightly down improves cost while retaining feasibility.

For total good-form count `T` and weights `w`, an alternative with flip set `F` has information

\[
 T J_p(w(F)).
\]

Since `J_p` is nondecreasing, maximizing its minimum over `F` gives (4) and (6). `square`

This differs structurally from recovering every sign: the oracle coefficient depends on the fractional geometry of decision-changing flips, rather than on the total number of binary preferences.

## 4. A necessary and sufficient group criterion in the saturated oracle regime

For a group `g`, define the restricted fractional cover complexity

\[
 \tau_{*,g}=
 \min_{x\ge0,\;\mathrm{supp}(x)\subseteq S_g}
 \left\{\sum_jx_j:\sum_{j\in F}x_j\ge1\quad\forall F\in\mathcal H\right\},
 \tag{8}
\]

with value infinity when the constraints are infeasible. Write `rho_{*,g}=1/tau_{*,g}`, taking `1/infinity=0`.

### Theorem 3: exact zero-premium criterion when `tau_* <= 2`

At `alpha=0`, if `rho_* >= 1/2`, equivalently `tau_* <= 2`, then

\[
 \boxed{
 K_f=K_{\rm or,f}=1/B_p
 \quad\Longleftrightarrow\quad
 \exists g:\ \rho_{*,g}\ge1/2
 \quad\Longleftrightarrow\quad
 \min_g\tau_{*,g}\le2.
 }
 \tag{9}
\]

Thus the relevant condition is that **some** sharing group can carry a sufficiently efficient fractional decision certificate. A small group elsewhere, including a globally relevant but unqueried singleton group, need not cause a premium.

**Proof.** The closure alternative `u=v=1/2` has information

\[
 B_p\sum_ja_j+B_q\sum_jb_j,
\]

regardless of the flip set or type pattern. Since `B_q<B_p`, every design costs at least `1/B_p`. Equality requires all good-form queries and total count `T=1/B_p`.

Let an equality-cost all-good design have coordinate weights `w`. Its oracle feasibility implies `w(F)>=1/2` for every minimal decision-changing `F`. For any queried group, set

\[
 L_g=w(S_g)>0,\qquad
 t_g(F)=\frac{w(F\cap S_g)}{L_g}.
\]

Suppose `t_g(F)<1/2`. Since the global flipped mass is at least `1/2`, the complementary queried groups have relative flipped mass strictly greater than `1/2`. Reverse the alternative types of all those complementary groups, leaving `g` unchanged. Fit the alternative high level to

\[
 u=p-(2p-1)t_g(F)>1/2
\]

and the low level to `v=1/2`. This gives information

\[
 T\{L_gJ_p(t_g(F))+(1-L_g)B_p\}<TB_p=1,
\]

contradicting feasibility. Hence every queried group separately satisfies `t_g(F)>=1/2` for every `F`. Normalizing the weights within any such group gives `rho_{*,g}>=1/2`.

Conversely, take weights supported in a group with `w(F)>=1/2` for every `F`. Under any type alternative the sampled group uses only one alternative level, either `u` or `v`. Minimizing over that level gives `J_p(w(F))=B_p`. Hence count `1/B_p` is feasible without knowing the type. `square`

The program has a finite feasible point, closed constraints, and compact cost sublevels. Therefore, if the right-hand side of (9) fails, the premium is **strictly** positive, not merely unattained equality.

### Useful sufficient condition outside the saturated regime

For arbitrary `rho_*`, if an oracle-optimal weight vector can be supported entirely inside one sharing group, then the premium is zero at `alpha=0`. With only one queried group, a type reversal merely changes whether its one fitted accuracy is named `u` or `v`; the fitted accuracy still ranges over `[1/2,1-eta]`.

In particular, if the decision depends only on preferences in a single sharing group, it has zero premium at `alpha=0`, irrespective of the sizes of entirely unqueried groups.

**No general converse is claimed outside `tau_*<=2`.** One group's support is a sufficient condition there, not an established necessary condition.

### A further necessary condition below saturation

Suppose `rho_*<1/2` and equality is achieved by an oracle-optimal all-good weight vector `w`. For any active flip set, `w(F)=rho_*`, every queried group must satisfy

\[
 \frac{w(F\cap S_g)}{w(S_g)}=\rho_*.
 \tag{10}
\]

Otherwise choose a group whose relative flipped mass is below `rho_*`; the complement is above `rho_*`. Assign the alternative high level to the first block and low level to the complement. Their separately fitted information is strictly below `J_p(rho_*)` by strict concavity, yielding an information deficit. This condition on active alternatives is necessary; it is not offered as a complete general zero-premium criterion.

## 5. Three coordinates: a relevant unqueried singleton is harmless

Use two items with scores

\[
 U_A(\theta)=\theta_1+\theta_2+\theta_3,\qquad U_B(\theta)=0.
 \tag{11}
\]

The winner is the three-bit majority. There are no ties. Let the partition be

\[
 S_1=\{1,2\},\qquad S_2=\{3\}.
\]

At the true state `(+,+,+)`, the minimal flip sets are

\[
 \mathcal H=\{\{1,2\},\{1,3\},\{2,3\}\}.
\]

Taking `w_1=w_2=1/2,w_3=0` gives `w(F)>=1/2` for every member. Consequently

\[
 \boxed{\alpha=0:\quad K_f=K_{\rm or,f}=1/B_p.}
 \tag{12}
\]

Only group 1 is queried at first order. Coordinate 3 is globally relevant to the catalogue, yet its singleton group does not affect the premium at this instance. The original full-vector problem with this two-group partition has a strictly positive premium at `alpha=0`.

The same catalogue and partition can have a positive premium at another state. At `(+,-,+)`, the minimal flip sets are `{1}` and `{3}`. The two necessary positive signs lie in different groups; no group alone can give both flip sets mass at least `1/2`. Theorem 3 proves a strictly positive premium. Its exact coefficient is the AND coefficient in the next section, with coordinates 1 and 3 playing the two roles. The extra negative coordinate 2 occurs in no minimal flip set and is dominated by transferring its allocation to coordinate 1.

This supplies a state-dependent structural distinction using only three coordinates, a fixed catalogue, and the original interface.

## 6. Two coordinates: an exact analytic positive-premium formula

Use the catalogue

\[
 U_A(\theta)=\theta_1+\theta_2-1,\qquad U_B(\theta)=0,
 \tag{13}
\]

with singleton groups `{1}|{2}`. Item A wins exactly at `(+,+)`; there are no ties.

Set `alpha=0`, and define

\[
 h=p-1/2,\quad k=q-1/2,\quad
 c=\frac{B_p-B_q}{h+k}>0.
 \tag{14}
\]

### Theorem 4: exact cost at `(+,+)`

At the true state `(+,+)`,

\[
 \boxed{
 K_{\rm or,f}=\frac1{B_p},\qquad
 K_f=\frac2{C_{p,q}},\qquad
 C_{p,q}=2B_q+2kc+\log\cosh c.
 }
 \tag{15}
\]

For every allowed `p>q>=1/2`,

\[
 C_{p,q}<2B_p,
 \qquad
 K_f-K_{\rm or,f}>0.
 \tag{16}
\]

**Proof.** The minimal decision-changing flip sets are `{1}` and `{2}`. Exchange symmetry of the two groups permits common per-coordinate good/other counts `a,b`. Let

\[
 t=a+b,\qquad \lambda=a/t,\qquad
 r=\frac{ap+b(1-q)}{a+b}
   =1/2+\lambda h-(1-\lambda)k.
\]

If both groups retain their type, or both reverse their type, the minimized information for a singleton sign flip is

\[
 2aB_p+2bB_q.
\]

If exactly one group reverses type, the two fitted weighted means before order projection are `r` and `1-r`. For one placement of the singleton sign flip, the order constraint pools both levels at `1/2`; for the other placement it fits the larger mean and clips the smaller one at `1/2`. The worse information over these alternatives is exactly

\[
 \begin{aligned}
 I(a,b)
 &=2aB_p+2bB_q-tB_r\\
 &=tC(\lambda),\\
 C(\lambda)
 &=2\{\lambda B_p+(1-\lambda)B_q\}
   -B_{1/2+\lambda h-(1-\lambda)k}.
 \end{aligned}
 \tag{17}
\]

This is no larger than the retained-type constraint. Reversing both preference signs adds nonnegative divergence to a singleton flip and is redundant.

The cost is `2t`, so `K_f=2/max_{lambda in [0,1]} C(lambda)`. The objective is strictly concave. Its derivative is

\[
 C'(\lambda)=2(B_p-B_q)-(h+k)\ell(r).
 \tag{18}
\]

At `lambda=0` this derivative is positive. At `lambda=1` it is negative because

\[
 2(B_p-B_q)\le2B_p<h\ell(p)\le(h+k)\ell(p).
\]

The strict middle inequality follows by integrating the strictly convex logit function between `1/2` and `p`: its graph lies strictly below its endpoint chord. Thus the maximum is uniquely interior, and

\[
 r_*=\frac1{1+e^{-2c}},\qquad
 \lambda_*=
 \frac{r_*-1/2+k}{h+k}\in(0,1).
 \tag{19}
\]

Writing `x=r-1/2`, the maximized objective is

\[
 2B_q+2kc+
 \sup_x\{2cx-B_{1/2+x}\}
 =2B_q+2kc+\log\cosh c,
\]

where the unconstrained maximizer lies inside the allowed interval by (19). This proves (15). Finally, the first term in (17) is strictly below `2B_p` whenever `lambda<1`; at `lambda=1`, `C(1)=B_p<2B_p`. Compactness gives `max C<2B_p`, proving (16). `square`

For example, direct evaluation at `p=3/4,q=1/2` gives

\[
 K_f\approx15.25915318,\qquad
 K_{\rm or,f}\approx7.64455650.
\]

These decimal evaluations are illustrative only. The strict separation is proved for the entire region `1/2<=q<p<=1-eta` by (16).

### The other three states have zero premium

At every state other than `(+,+)`, select any negative coordinate. Every alternative making A the winner must reverse that coordinate. Allocating only to its true good form gives information `T B_p` under every alternative type pattern, because the alternative probability of the true negative sign is at most `1/2`. The universal `u=v=1/2` lower bound matches this construction. Therefore

\[
 \boxed{
 \theta\ne(+,+),\ \alpha=0:
 \quad K_f=K_{\rm or,f}=1/B_p.
 }
 \tag{20}
\]

The premium is zero or positive depending on the true state, even though the catalogue, partition, rates, and query interface are unchanged.

## 7. What removing outputs does and does not preserve

Reducing the requested output from all signs to top-1 weakly lowers both optimal costs separately. Their difference need not preserve its sign of strict positivity.

At `alpha=0`, the original full-vector theorem gives zero premium only with one sharing group. Within one group every decision also has zero premium, by Theorem 2 and the one-group support argument. Thus, starting from the original full-vector problem, output coarsening at `alpha=0` cannot turn a zero premium into a positive one. It can eliminate a positive premium, as the majority example shows, or leave it positive, as the AND example shows.

For finite positive calibration, creation of a positive premium is possible. The following short analytic argument is already complete; it is supplemental to the zero-calibration results.

### Single-bit recommendation has positive premium for every `alpha>0`

Take a recommendation determined only by one sign. Proposition 1 removes all globally irrelevant coordinates, so the original one-coordinate oracle result applies. For `a>0`, define

\[
 G_r(a)=\inf_{x\ge1/2}
 \{\alpha D(r,x)+aD(p,1-x)\}.
 \tag{21}
\]

Its fitted mean is the weighted average of `r` and `1-p`, clipped below at `1/2`. For `r>1/2` the fitted mean is strictly below `r`; the envelope derivative is

\[
 \partial_rG_r(a)=\alpha\{\ell(r)-\ell(x_r)\}>0.
\]

Continuity at `r=1/2` implies `G_q(a)<G_p(a)` for `p>q`. The oracle information is at least `G_p(a)`, because it adds the nonnegative labelled-q calibration penalty and the rate-order constraint. At its optimal root `a_alpha`,

\[
 G_q(a_\alpha)<G_p(a_\alpha)\le1.
\]

A type-swapped, sign-flipped alternative has information `G_q(a_alpha)`: keep the alternative high level at `p` and fit the low level `x<=p`. Hence the unique reduced oracle allocation is infeasible without knowing the type, and the premium is strictly positive.

### A finite-calibration comparison with full recovery

For full recovery of five signs in one group, set `p=3/4,q=1/2` and take `eta<=1/4`. Let

\[
 A=D(p,1-p)=\tfrac12\log3,\qquad
 B=D(p,1/2)=\tfrac34\log3-\log2.
\]

The original full-recovery criterion uses

\[
 \Gamma_5(\alpha)=\inf_{v\ge1/2}
 \{\alpha D(1/2,v)+a_\alpha F_5(p,v)\}.
\]

Since `a_alpha>=1/A`, Pinsker's inequality and the tangent of `F_5` at `1/2` give, writing `x=v-1/2`,

\[
 \begin{aligned}
 \Gamma_5(\alpha)
 &\ge\frac{5B}{A}
    +\inf_x\left\{2\alpha x^2-\frac3A x\right\}\\
 &\ge\frac{5B}{A}-\frac9{8\alpha A^2}.
 \end{aligned}
\]

Consequently the original full-vector premium is zero throughout the explicit finite region

\[
 \alpha\ge\frac9{8A(5B-A)}.
 \tag{22}
\]

The denominator is positive exactly because

\[
 4(5B-A)=\log(3^{13}/2^{20})>0.
\]

Changing the requested output to a catalogue whose winner depends only on the first sign creates a strictly positive premium for the same positive `alpha`, even if all five coordinate actions remain available. This last full-recovery comparison invokes the original note's proved-information-program criterion; the displayed bound is a separate elementary sufficient inequality.

## 8. Failed conjectures, claim limits, and unresolved directions

1. **“An irrelevant coordinate could strictly lower optimal first-order cost by calibrating the globally shared rates/types.”** Rejected for the original coordinate/form interface: Proposition 1 gives a cost-preserving information-dominance argument. It is not a statement about different costs, different channels, or special direct-type actions.

2. **“The smallest original sharing group still decides top-1 zero premium.”** Rejected. Majority-of-three with partition `{1,2}|{3}` at `(+,+,+)` has zero premium despite the singleton. The singleton sign is even globally relevant.

3. **“A fixed catalogue and partition has one zero-versus-positive answer independent of the true preference state.”** Rejected by either the AND catalogue or the majority catalogue above.

4. **“The full-sign oracle's unique allocation persists after output coarsening.”** Rejected. For a single-bit target at `alpha=0`, the oracle can put any fraction between `1/2` and 1 of its good-form mass on the target coordinate and the remainder on an irrelevant same-channel coordinate, while retaining total coefficient `1/B_p`. Irrelevant queries can be co-optimal; Proposition 1 rules out strict improvement.

5. **“Zero premium always requires an oracle-optimal allocation supported in one group.”** Established as an iff only in the saturated regime `tau_*<=2`. Outside that regime it remains unproved in this note and must not be promoted to a general theorem. The active-flip balance condition (10) is only necessary. No high-dimensional converse or counterexample search is being claimed here.

6. **“Removing output requirements preserves zero premium at every finite calibration ratio.”** Rejected by Section 7. A smaller task changes the oracle's rate-learning burden as well as the unknown-type burden.

7. The results are pointwise fixed-instance asymptotics and information-program identities. They do not establish finite-budget gains, gap-uniform guarantees, Natural/LLM validity, independent certification, or a new universal allocation algorithm. The exact AND formula is analytic; its two decimal evaluations are not evidence for broader numerical generalization.

The most self-contained candidate contribution from this derivation is Theorem 3 together with the two- and three-coordinate catalogues: a group-restricted fractional decision-certificate criterion can replace the smallest-group criterion in an explicit broad regime, and the same recommendation task can exhibit zero or positive format-learning premium depending on its local decision geometry.
