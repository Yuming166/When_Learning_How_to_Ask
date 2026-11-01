# Oracle depth, continuous certificates, and conditional sharing criteria

Date: 2026-10-31. Scope is exactly the preceding `web_unknown_calibration_20261031/MODEL_AND_SCOPE.md`: fixed finite completed-block menu, known source accuracy, unknown common extraction levels, finite labelled calibration, and an oracle knowing only the preferred formats. This is a delegated same-family mathematical audit, not formal verification or a novelty claim. No model calls, training, numerical search, or certificate rerun was performed by this auditor. The parent's new certificate and its retained output were read directly; old snapshots were read-only.

## 1. Main findings

1. **Single depth is not generally optimal.** The parent's exact continuous certificate is valid and is stronger than a conditional pure-good counterexample: it proves that every full-menu oracle-optimal allocation in its fixture uses at least two distinct depths, even though every format split is available at a fixed depth. It does not establish exactly two depths or global pure-good optimality.
2. Conditional on restricting to pure-good allocations, the oracle has an exact one-dimensional semi-infinite LP and an attained positive-measure dual. There is an optimal dual supported on at most L_max nuisance rates. This is a **dual** support bound; it is not an at-most-two-depth theorem for the primal.
3. A useful additional lemma does hold: the same-truth pure-good KL decreases as an alternative rate moves from one half toward p, and increases beyond p. The opposite-truth KL increases beyond p. These properties permit clipping pure-good alternatives at p and give an exact one-dimensional groupwise feasibility test on any pure-good oracle-optimal allocation.
4. A scalar smallest-group criterion follows if the oracle optimum is unique and pure-good, or under explicitly stated symmetry/optimal-face conditions. Existence of one pure-good optimum by itself does not justify discarding other oracle optima or averaging across unequal sharing groups.
5. **At zero first-order calibration, the equality classification is complete:** for every fixed admissible state and fixed partition, K_learner=K_oracle if and only if G=1. This uses the all-optima pure-good theorem in `ORACLE_STRUCTURE_AUDIT.md`, allows nonunique allocations and arbitrary depth mixtures, and includes q=1/2 and p=1-eta. Section 9 proves the result; it is not a single-depth theorem or a growing-d uniform limit.

## 2. The pure-good oracle is a robust depth-design problem

Put
\[
H_L(t)=D(P_{p,L}^{+}\Vert P_{t,L}^{+}),\qquad
J_L(t)=D(P_{p,L}^{+}\Vert P_{t,L}^{-}),\qquad
\Delta_L(t)=J_L(t)-H_L(t)\ge0.
\]
These are pure-good block laws; the true extraction accuracy is p. The final inequality is the previously proved one-truth-flip lemma.

If only pure-good actions are allowed, oracle symmetry permits a common per-fact allocation b_L. The alternative bad level has no online effect, so its exact profile is v=min(q,u). Define
\[
C_\alpha(u)=\alpha\{\operatorname{kl}(p,u)
 +\operatorname{kl}(q,\min(q,u))\},
\]
\[
F_{d,L}(u)=J_L(u)+(d-1)H_L(u),\qquad w_L=c+\ell L.
\]
Then the restricted oracle value is
\[
K_{\rm pure}=d\min_{b\ge0}\sum_{L=1}^{L_{\max}}w_Lb_L
\]
subject to
\[
C_\alpha(u)+\sum_Lb_LF_{d,L}(u)\ge1
\quad\forall u\in[1/2,1-\eta].
\tag{1}
\]
This restriction is not asserted to equal the full oracle until pure-good sufficiency is separately proved. It always supplies feasible upper bounds on the full oracle.

If only one depth L is used, its exact restricted value is
\[
K_{\rm pure,one\ depth\ L}
=d w_L\sup_{u\in[1/2,1-\eta]}
\frac{(1-C_\alpha(u))_+}{F_{d,L}(u)}.
\tag{2}
\]
The denominator is uniformly positive: a marginal of the flipped fact already separates its true probability above one half from every wrong-sign alternative probability at most one half. Equation (2) is a robust constraint, not the known-rate ratio w_L/A_L.

For general b, different depths can compensate at different nuisance rates. Nonconvexity of the inner mixture objective blocks an argument based only on one stationary rate or on differentiating a putative single least-favorable rate.

## 3. A rigorous dual support statement

Let m=L_max and write r_alpha(u)=1-C_alpha(u). The per-fact-cost primal in (1) has dual
\[
\max_{\mu\ge0}\int r_\alpha(u)\,d\mu(u)
\quad\text{subject to}\quad
\int F_{d,L}(u)\,d\mu(u)\le w_L
\quad(L=1,\ldots,m),
\tag{3}
\]
where mu is a finite nonnegative measure on the compact rate interval.

**Strong duality and attainment.** One-read pure-good actions have a uniformly positive F_{d,1}, so increasing b_1 provides a uniformly strict feasible allocation. Take nested finite rate grids with dense union. Their finite LP values increase to the full primal value: their optimal allocations are uniformly bounded by positive costs and a common feasible allocation; every convergent subsequence satisfies all dense-grid constraints and, by continuity, the full interval constraints.

Each finite-grid LP has a nonnegative dual measure. Its total mass is bounded by w_1/min F_{d,1}. A weakly convergent subsequence therefore yields a feasible measure in (3), with objective equal to the limiting primal value, because all integrands are continuous on a compact interval. This proves strong duality and dual attainment without assuming inner convexity.

For any optimal pair b*,mu*, complementary slackness gives
\[
\operatorname{supp}\mu^*\subseteq
\left\{u:\sum_Lb_L^*F_{d,L}(u)=r_\alpha(u)\right\}.
\tag{4}
\]
On this contact set the objective integrand r_alpha is a fixed linear combination of the m functions F_{d,L}. Conic Caratheodory reduction of the m-dimensional vector of their integrals consequently replaces mu* by an optimal dual measure with **at most m atoms**, all on that contact set. The objective remains unchanged and all dual action inequalities are preserved.

This does not bound primal depth support by the number of nuisance coordinates, nor by the number of atoms in a particular dual certificate. In a semi-infinite problem, movement away from currently tight constraints can make formerly slack neighboring rates active. Without additional global shape results, stationary equations at one or two rates do not certify feasibility. No nontrivial universal upper bound on primal depth support is proved here; the trivial bound for the pure menu is L_max, and the certificate below proves that one is insufficient.

The analogous full-format dual has at most as many atoms as there are per-fact actions, by the same argument. The two-dimensional nuisance domain does not itself imply a two-atom or two-action theorem.

## 4. Monotonicity of same-truth pure-good KL

The following lemma is useful even though J_L(t) itself can be nonconvex.

**Lemma.** For fixed r>1/2, p>1/2 and L:

- H_L(t) is nonincreasing on [1/2,p] and nondecreasing on [p,1-eta].
- J_L(t) is nondecreasing on [p,1-eta].

**Proof.** Let beta=logit(t), and decompose the observed count S into its magnitude Z=|2S-L| and the sign of 2S-L. The magnitude distribution Q_beta is independent of r. Apart from a fixed multiplicity for each allowed z, its mass is proportional to
\[
\frac{\cosh(\beta z/2)}{[2\cosh(\beta/2)]^L}.
\]
The z=0 multiplicity is handled separately but has the same parameter dependence. For beta_2>beta_1>=0, the ratio Q_beta2(z)/Q_beta1(z) is increasing in z: the logarithmic derivative of its z-dependent factor is
\[
\tfrac12\{\beta_2\tanh(\beta_2z/2)
            -\beta_1\tanh(\beta_1z/2)\}\ge0.
\]
Thus larger beta stochastically increases Z. The score is
\[
s_\beta(z)=\frac z2\tanh(\beta z/2)
 -\frac L2\tanh(\beta/2),
\]
which is nondecreasing in z and has expectation zero under Q_beta. For beta<=beta_p, stochastic ordering gives
\(E_{Q_{\beta_p}}s_\beta\ge0\), hence
\[
\frac{d}{d\beta}D(Q_{\beta_p}\Vert Q_\beta)
=-E_{Q_{\beta_p}}s_\beta\le0.
\]
The inequality reverses for beta>=beta_p.

For z>0, the conditional probability of a positive count sign under positive truth is
\[
b_z(t)=\tfrac12+\tfrac{2r-1}{2}
                    \tanh(z\operatorname{logit}(t)/2),
\]
which increases in t. The sign contribution at z=0 is zero. The KL chain rule yields
\[
H_L(t)=D(Q_p\Vert Q_t)+
\sum_zQ_p(z)\operatorname{kl}(b_z(p),b_z(t)).
\tag{5}
\]
Every Bernoulli term decreases up to t=p and increases thereafter, so H has the stated monotonicity. For J, replace the second Bernoulli argument by 1-b_z(t). That sign-KL contribution increases with t, because b_z(p)>=1/2 while 1-b_z(t)<=1/2. At t>=p the magnitude contribution also increases. This proves the lemma. All distributions are positive and differentiable on the compact interval; one-sided boundary limits pose no problem. ∎

The result does not assert monotonicity of J below p or convexity of either full nuisance objective.

## 5. Exact two-layer constraint structure on a pure-good oracle face

Consider any fixed **oracle-optimal pure-good allocation** x_{j,L}; it need not be symmetric or use one depth. Define
\[
H_j(t)=\sum_Lx_{j,L}H_L(t),\qquad
\Delta_j(t)=\sum_Lx_{j,L}\Delta_L(t).
\]
The oracle layer consists of
\[
\alpha\{\operatorname{kl}(p,u)+\operatorname{kl}(q,v)\}
+\sum_iH_i(u)+\Delta_j(u)\ge1
\quad\forall j,\quad 1/2\le v\le u\le1-\eta,
\tag{6}
\]
and the equality w dot x=K_o identifying its optimal face.

For pure-good actions all alternative levels can be clipped at p. The monotonicity lemma reduces every affected H or J term when its argument above p is replaced by p; the calibration terms also decrease under this clipping because q<=p. Hence it suffices to use u,v<=p.

Suppose an alternative changes the type in a set of groups J and flips truth j.

- If j lies outside the changed-type groups, each changed group's H_i(v) is at least H_i(u), since v<=u<=p. Replacing those terms by H_i(u) reduces the expression to an oracle constraint (6). These alternatives are automatically safe.
- If j lies in changed group g, the alternative's u-dependent terms are alpha*kl(p,u) and the H_i(u) of unchanged-type groups. All are nonnegative and simultaneously vanish at u=p, which is feasible for v<=p. The remaining changed groups contribute nonnegative H terms. Thus the least informative type-change set containing j is the single group g.

Therefore the **additional learner layer** on this fixed pure-good allocation is exactly
\[
\boxed{
\inf_{1/2\le v\le p}
\left\{\alpha\operatorname{kl}(q,v)
 +\sum_{i\in S_g}H_i(v)+\Delta_j(v)\right\}\ge1
\quad\forall g,\ j\in S_g.}
\tag{7}
\]
One-truth-flip reduction covers all larger truth changes. No further type patterns need to be checked on this pure-good face.

Averaging within each group preserves oracle optimality and learner feasibility. With common per-fact depth profiles b_{g,L} inside each group, define
\[
\Gamma_k(b;\alpha)=
\inf_{1/2\le v\le p}
\left\{\alpha\operatorname{kl}(q,v)
 +\sum_Lb_L[J_L(v)+(k-1)H_L(v)]\right\}.
\tag{8}
\]
Then (7) is exactly Gamma_{k_g}(b_g;alpha)>=1 for every group, **subject also to the coupled oracle layer (6) and optimal total cost**. Group depth profiles cannot be independently chosen without that oracle constraint.

For each fixed profile b, Gamma_k is nondecreasing in k, since each H_L is nonnegative. The issue is whether an oracle-optimal learner-feasible witness may be assumed to have the same profile in all groups.

### When a scalar smallest-group criterion follows

- If the full oracle optimum is **unique and pure-good**, coordinate permutation symmetry forces a common profile b* for all facts. Then
  \[
  K=K_o\quad\Longleftrightarrow\quad
  \Gamma_{k_{\min}}(b^*;\alpha)\ge1.
  \tag{9}
  \]
  The profile may use several depths; uniqueness does not mean a single depth.
- If every full oracle optimum is pure-good and all groups have the same size k, the partition's permutation symmetries are transitive on facts. Averaging any learner-feasible oracle optimizer over them yields a common profile b. Thus equality holds iff some common-profile oracle optimizer has Gamma_k(b;alpha)>=1. Compactness permits writing a maximum over that common-profile optimal set.
- For arbitrary unequal groups with a nonunique oracle face, (7)--(8) remain exact on the pure-good face. A single common-profile test is sufficient when it passes, but its necessity has not been proved here.

If only **one** pure-good oracle optimizer is known to exist, failure of every tested pure-good profile does not establish a premium: another, possibly mixed-format oracle optimizer could satisfy the learner constraints. An exact global equality statement then remains the complete-oracle-optimal-set feasibility condition from the preceding stage. These quantifiers must be retained.

## 6. Continuous certificate templates

A pure-good candidate b has exact global information function
\[
f(u)=C_\alpha(u)+\sum_Lb_LF_{d,L}(u).
\]
Global feasibility can be established by covering the entire interval with rational cells and bounding logs and between-grid behavior. A conservative Lipschitz bound is
\[
|f'(u)|\le\frac{2\alpha+d\sum_LL b_L}{\eta}.
\tag{10}
\]
The profile min(q,u) is continuous and differentiable at u=q; its derivative there is zero on both sides for the second calibration term.

A useful sharper Taylor certificate has the global curvature bound
\[
|f''(u)|\le
\frac{2\alpha+d\sum_L b_L L(2L-1)}{\eta^2}
\tag{11}
\]
where second derivatives are taken on either side of u=q; the first derivative is globally Lipschitz. To prove (11), a component L-read likelihood has |f'/f|<=L/eta and |f''/f|<=L(L-1)/eta^2 by direct product differentiation. The same raw derivative bounds hold for its positive mixture. Therefore
\[
|(\log Q)''|\le L(2L-1)/\eta^2.
\]
Each raw Bernoulli calibration KL contributes at most 1/eta^2. Weighted KL sums and d fact contributions give (11). Because the profiled calibration is C1, the Taylor remainder bound also holds for cells crossing q.

At a rational midpoint u_0, likelihood probabilities and the derivative f'(u_0) are rational; only the value f(u_0) needs log intervals. A lower bound over a radius-h cell is
\[
f(u)\ge f_{\rm lower}(u_0)-|f'(u_0)|h-\tfrac12B h^2.
\tag{12}
\]
A midpoint scan without this between-point control is not a continuous certificate.

To rule out a single depth L even allowing **all its format splits**, take any finite nonnegative dual combination of admissible alternative-rate constraints. If its weighted KL is at most c+ell*L for each format split, it lower-bounds every allocation using that depth. A single alternative may suffice. This avoids any prior assumption that pure-good actions dominate the full unknown-rate family.

## 7. Independent read audit of the depth-mixing certificate

Read directly:

- `certify_depth_mixing.py`
- `DEPTH_MIXING_CERTIFICATE.json`
- the imported exact-rational log and block-law functions in the prior sealed `certify_threshold_failure.py`.

**Audit result: PASS.** The proof logic, orientation of the derivative, interval coverage, Taylor bound, and dual comparisons are consistent. This audit did not rerun the verifier or perform a second numerical search.

The exact fixture is
\[
r=3/5,\quad p=19/20,\quad q=3/5,\quad
\eta=1/40,\quad d=1,\quad\alpha=1,\quad
c=\ell=1,\quad L_{\max}=6.
\]
All 27 mixed/pure actions remain available. The feasible allocation uses 14 pure-good depth-one blocks and 2 pure-good depth-two blocks, costing
\[
14(1+1)+2(1+2)=34.
\]
The oracle bad-level profile is exactly min(q,u). Its global curvature bound is
\[
\frac{2+14\cdot1+2\cdot2(2\cdot2-1)}{(1/40)^2}
=44800.
\]
The script computes the exact derivative of the negative-truth mixture and checks its probabilities' derivatives sum to zero. Its 950 cells of width 1/2000 cover exactly [1/2,39/40], with radius 1/4000. Applying (12) gives a stored strictly positive uniform information margin above 0.0285716211. Thus the full continuous-domain oracle coefficient is at most 34.

For depth one, the closure alternative u=v=1/2 and dual weight 100 lower-bound its coefficient by more than 48.52325. For every depth from two through six, the unchanged true rates and dual weight 41.3 give a lower bound 41.3. Every format split at each depth is checked, with positive interval slack. Hence
\[
K_{\rm every\ single\ depth}\ge41.3>34\ge K_o.
\tag{13}
\]
The closure alternative is legitimate by continuity of the information program; no correctness guarantee at equal-level unidentifiable states is assumed.

A separate common dual alternative (u,v)=(73/80,3/5), weight 3329/100, checks all 27 actions and proves
\[
32.9477982818\ldots\le K_o\le34.
\tag{14}
\]
No exact optimum or exact optimal support is inferred. Equation (13) proves that **every full-menu oracle-optimal allocation has at least two distinct depths**. Pure-good optimality need not be resolved first. The comparison covers arbitrary mixtures of formats at a fixed depth, rather than only pure single-depth candidates.

The certified single-depth/full-oracle cost ratio is at least 413/340; the relative reduction from the best single-depth coefficient to the full optimum is at least 73/413. These are asymptotic online-cost coefficient statements under finite calibration, not finite-budget empirical improvements. The generic expected-cost theorem from the preceding stage gives their operational asymptotic meaning.

The imported logarithm code uses dyadic range reduction and a positive atanh-series remainder bound; probabilities, derivatives, and comparisons use exact fractions. Printed decimals are displays only. The evidence is a mathematical computer-assisted certificate with readable bounds, not machine-checked formal verification.

## 8. Recommendation and unresolved points

**GO:** retain the certified failure of single-depth oracle structure and the continuous certification method. It directly changes the known-rate structural picture and does not depend on proving pure-good optimality first.

**GO, conditional statement:** retain the pure-good-face group constraints (7), the profile Gamma in (8), and the explicitly qualified scalar consequences. They reduce many type patterns to one-dimensional group checks without asserting more oracle structure than has been proved.

**REVISE:** global pure-good optimality when both alpha>0 and q>1/2, a universal primal depth-support bound stronger than the finite menu, and a general positive-calibration unequal-group scalar criterion with nonunique oracle optima. None follows from a one-dimensional nuisance parameter or from the bounded grid search finding no mixed-format gain. The subsequently completed `ORACLE_STRUCTURE_AUDIT.md` proves all-optima pure-good structure at alpha=0 and at q=1/2; the former permits the unconditional equality classification below.

The generic measure duality and convex optimal-face reasoning are standard tools. Novelty assessment should focus on the certified structural separation and any further proved sharing consequences, not on relabelling those tools.

## 9. Zero-calibration sharing classification for the full multiread menu

**Theorem.** Fix any admissible r,p,q,eta, any finite positive d, any nonempty partition into G groups, finite L_max>=1, and costs c>=0, ell>0, exactly as in the inherited scope. If M_delta/log(1/delta) tends to zero, then the optimal expected-online-cost coefficients satisfy
\[
\boxed{K_{\rm learner}=K_{\rm oracle}\quad\Longleftrightarrow\quad G=1.}
\tag{15}
\]
For every fixed state with G>1 the inequality is strict. This is a statement about the full completed-block action menu and allows all mixed-format blocks and all mixtures of depths in both optimization problems.

**Premise checked.** Theorem A in `ORACLE_STRUCTURE_AUDIT.md` proves that at alpha=0 **every** oracle-optimal allocation is pure-good. Its common-garbling curve is admissible even at q=1/2, its opposite-truth KL decrease is strict for every block containing a bad read, and compactness makes that decrease uniformly positive. Same-depth replacement followed by a small scaling therefore excludes any bad-read mass from any optimum. The theorem does not require a single depth or a unique optimizer. The continuous expected-cost theorem from the preceding stage identifies the information-program values used here with the optimal expected-cost coefficients.

**Step 1: every fact receives positive allocation.** Take an arbitrary oracle optimizer x. It is pure-good by that premise, so write its counts as x_{j,L}. The alternative that changes only truth j while retaining p,q and all types gives
\[
\sum_L x_{j,L}J_L(p)\ge1.
\tag{16}
\]
Thus every fact j has at least one positive x_{j,L}. All J_L(p) are positive and finite under the fixed interior source accuracy and extraction upper bound.

**Step 2: an active oracle constraint exists below p.** At alpha=0 define
\[
f_j(u)=\sum_iH_i(u)+\Delta_j(u)
      =\sum_{i\ne j}H_i(u)+\sum_Lx_{j,L}J_L(u).
\tag{17}
\]
The exact oracle constraints are f_j(u)>=1 for all j and all u in [1/2,1-eta]. They cover larger truth changes because each additional flipped fact adds a nonnegative Delta term. If every constraint were strict, continuity on the compact rate interval and finiteness of d would give a uniform minimum greater than one. Scaling every count down by that minimum would preserve feasibility and strictly reduce cost. Hence some j and u_* have f_j(u_*)=1.

The derivatives at p satisfy H_L'(p)=0 and J_L'(p)>0 for every L. To see the strict inequality, use the magnitude/sign decomposition in Section 4. The magnitude KL derivative vanishes at its matching parameter. For each positive magnitude z, the derivative of the opposite-sign Bernoulli term is
\[
\left.\frac{d}{dt}\operatorname{kl}
       (b_z(p),1-b_z(t))\right|_{t=p}
=b_z'(p)\frac{2b_z(p)-1}{b_z(p)(1-b_z(p))}>0.
\tag{18}
\]
Here r>1/2, p>1/2, and z>0 imply b_z(p)>1/2 and b_z'(p)>0. Every finite L>=1 has a positive probability of at least one such z. The z=0 contribution, when present, is zero. Consequently, by (16),
\[
f_j'(p)=\sum_Lx_{j,L}J_L'(p)>0
\quad\text{for every }j.
\tag{19}
\]
Since p>1/2, a sufficiently small left perturbation stays in the rate interval and has f_j(p-epsilon)<f_j(p). Feasibility then implies f_j(p)>1. For u>=p, Section 4 makes each H_L(u) and J_L(u) nondecreasing, so f_j(u)>=f_j(p)>1. Therefore **every active constraint has u_*<p**, including when p=1-eta; the last derivative argument uses only a left perturbation at that boundary.

**Step 3: more than one group excludes every oracle optimizer.** Let g contain the active fact j. Consider the learner alternative that changes only truth j and type z_g, keeps all other truths/types fixed, and takes alternative levels
\[
(u,v)=(p,u_*).
\tag{20}
\]
This is an admissible strictly ordered pair because 1/2<=u_*<p<=1-eta. Each actually queried good format outside g remains a high-rate format and has exactly its true distribution, so its KL is zero. Each such format inside g becomes a low-rate format with rate u_*. The total learner constraint at this alternative is thus
\[
\sum_{i\in S_g}H_i(u_*)+\Delta_j(u_*)
=f_j(u_*)-\sum_{i\notin S_g}H_i(u_*)
=1-\sum_{i\notin S_g}H_i(u_*).
\tag{21}
\]
For any L, H_L(t)>0 when t differs from p: the pure block count has expectation L[1/2+(2r-1)(t-1/2)], which identifies t because r>1/2. Every fact outside g has positive allocation by Step 1. If G>1 there is at least one such fact, so the expression in (21) is strictly less than one. This arbitrary oracle optimizer is therefore learner-infeasible.

Both information programs attain their finite minima: action costs are positive, the action menu is finite, the constraint set is closed, and a finite feasible design exists. The learner feasible set is a subset of the oracle feasible set. Equality of their values would therefore produce a learner optimizer that is also an oracle optimizer, contradicting (21). Hence K_learner>K_oracle for G>1. No symmetry, common depth profile, uniqueness, or uniform margin over the entire optimal face was needed.

**Step 4: one group admits a learner-feasible oracle optimizer.** If G=1, take any pure-good oracle optimizer. An alternative type is either unchanged, which is covered by the oracle constraints, or flipped for every fact. In the latter case the only queried format now has the common alternative rate v. Its online likelihood is exactly that of an oracle alternative having high rate v; the remaining alternative low rate has no online effect and there is no first-order calibration term. The oracle constraints cover every v in [1/2,1-eta] and every wrong truth vector. At v=1/2 or at equal alternative levels this statement uses the compact closure already required by the program; it does not assume correctness at an unidentifiable equal-level state. Thus the allocation is learner-feasible, proving equality. Equivalently, when the sole group contains all facts, the additional constraint (7) is the same oracle function f_j(v)>=1 restricted to v<=p. This completes the proof. ∎

**Boundary and scope checks.** The true q=1/2 is allowed throughout. The strict derivative needs p>1/2, which follows from p>q>=1/2. An active u_*=1/2 causes no problem: (20) still has strict high/low separation. The boundary p=1-eta also causes no problem, as shown in Step 2. The conclusion applies when calibration is sublinear in log(1/delta), not only when literally no reference samples are available. It compares first-order optimal coefficients for fixed d, partition, menu, and parameters; it asserts neither finite-delta equality of expected costs nor a uniform premium bounded away from zero along changing dimensions or parameters. In particular, no single-depth rule follows from (15), and the positive-calibration depth-mixing certificate remains a separate result.
