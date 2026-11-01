# Provenance, repeated extraction, and the price of learning a query interface

Research derivation, 31 October 2026. Mathematical claims are stated below with their domains. They are not claims of literature priority, formal verification, or validation on Web/LLM data. The original Theory_Note.md and every historical experiment remain separate and unchanged.

## 1. Minimal statistical experiment

For the smallest problem, there is one fixed unknown truth θ ∈ {−1,+1}. Each **independent provenance root** i draws one persistent report

\[
V_i=\theta B_i,\qquad \Pr(B_i=+1)=r,\quad 1/2<r<1.
\]

The B_i are independent. A known map assigns pages to roots; accessing another copy of a root does not redraw B_i. URLs, domains, and root identities are different objects. Metadata and root selection do not secretly reveal truth. Independence is an assumption about information origin, not something inferred from different URLs.

An extraction in format m returns

\[
Y_{i,m,t}=V_i E_{i,m,t},\qquad
\Pr(E_{i,m,t}=+1)=a_m.
\]

Conditional on the persistent reports, extraction errors are fresh, mutually independent, stationary, and independent of source errors. For the format-learning version, a_m is p or q according to an unknown preferred format z, with 1/2 ≤ q < p < 1. For d facts, retain the original known partition and z_g, and explicitly assume root–fact errors independent across both roots and facts for the coordinatewise statements below. Logical relationships between facts or shared root-wide failure events would require a different model.

Activation costs c ≥ 0 per newly used root; extraction costs ℓ > 0 per response. Repeated reads pay ℓ. Activation plus first read costs c+ℓ. Costs are known. Activating a root alone reveals no factual information. For the single-fact results this is the total objective C=cN+ℓT. Multi-fact shared activation is a separate optimization problem; do not sum per-fact activation charges when one purchase serves several facts.

Two decision objectives must remain distinct:

1. Fixed budget: minimize specified-prior Bayes error with C≤B. The examples use a uniform prior on θ.
2. Fixed confidence: stop almost surely, with error at most δ under each θ (and every admissible nuisance value in the stated experiment), minimizing expected C.

Two parameter regimes are used, visibly:

- **K: known channels.** r and extraction accuracy a are known. This is the tractable acquisition problem in Propositions 3–4.
- **U: original-type uncertainty.** z_g,p,q are unknown; labelled calibration and optional type queries retain their original definitions. Calibration of extraction accuracy is not calibration of source factual accuracy. Propositions 1–2 remain obstructions even when those nuisance parameters are revealed. A complete optimal coefficient for U with root revisits has **not** been proved.

Proposition 5 is an intermediate regime: known r,p,q, unknown z, one fact. It is not the original unknown-p/q theorem. Its oracle additionally knows z and otherwise has identical information.

## 2. Proposition 1: saturation and a factual error floor

Let only S imperfect independent roots be available. Fix all nuisance parameters, identically under θ=+ and θ=−. Let H contain all adaptive actions, responses, independent calibration/type information, stopping, and output. Then

\[
\mathrm{KL}(P_+^H\Vert P_-^H)
\le S\kappa(r),\qquad
\kappa(r)=\operatorname{kl}(r,1-r).
\tag{1}
\]

Every uniformly δ-correct procedure must consequently satisfy

\[
\operatorname{kl}(1-\delta,\delta)\le S\kappa(r).
\tag{2}
\]

More sharply, its maximum error is at least

\[
B_S(r)=\Pr\{\operatorname{Bin}(S,r)<S/2\}
+\tfrac12\Pr\{\operatorname{Bin}(S,r)=S/2\}>0.
\tag{3}
\]

**Proof.** Every transcript, even an infinite transcript, is obtained by a θ-independent randomized kernel applied to V=(V_1,…,V_S): θ→V→H. Data processing and independence give (1). Applying data processing to the decision event gives (2). Observing V perfectly is more informative than any extraction transcript. Its equal-prior Bayes decision is majority vote, with a fair tie, yielding (3). Sign symmetry makes that decision's two conditional errors equal, so this is also the minimax error for the perfectly observed reports. It bounds the average and maximum risk of extraction procedures, not the error of every procedure at each individual θ. Heterogeneous known roots instead give the overlap bound ½Σ_v min(P_+(v),P_−(v)) and weighted voting. ∎

**Scope and novelty.** This is a standard data-processing/testing consequence. The original note already contains its one-persistent-error special case in §9. It is a useful validity boundary, not a new flagship theorem. Giving the learner all z_g, p, q and perfect extraction cannot defeat it. The old k_min condition therefore does not establish feasible arbitrary-δ factual recovery when root supply is finite.

## 3. Proposition 2: learning extraction can succeed while factual learning saturates

Suppose both formats are sampled infinitely often on a fixed root–fact pair, with a_m≥1/2. Conditional strong laws give

\[
\bar Y_m\to V(2a_m-1),\qquad
\widehat a_m=\frac{1+|\bar Y_m|}{2}\to a_m\quad\text{a.s.}
\tag{4}
\]

For disjoint pairs of same-format extractions,

\[
Y_{m,1}Y_{m,2}=E_{m,1}E_{m,2},\qquad
\mathbb E[Y_{m,1}Y_{m,2}]=(2a_m-1)^2.
\tag{5}
\]

Thus p>q permits consistent format identification from repeats without factual labels, while Proposition 1 still bounds factual recovery. A positive accuracy orientation is essential: allowing a_m<1/2 leaves a_m versus 1−a_m ambiguous. Persistent extraction errors invalidate (4)–(5). Agreement here measures fidelity to the latent report **under this model**, not truthfulness or empirically established LLM correctness.

For one extraction per fresh root, only the effective means

\[
\widetilde a_m=\tfrac12+(2r-1)(a_m-\tfrac12)
\tag{6}
\]

are observed. Separate source/extractor rates are then genuinely nonidentifiable without additional structure: (r,p,q)=(.75,.9,.7) and (.9,.75,.625) both produce effective (.7,.6). Finite-root factual saturation is a different issue: distinct truth distributions can be identifiable yet still overlap with positive Bayes error in one finite-root experiment.

## 4. Proposition 3: fresh-root activation is a first-order cost

With unlimited iid roots, any uniformly δ-correct procedure with finite expected cost satisfies, under each θ,

\[
\mathbb E_\theta N\ge
\frac{\operatorname{kl}(1-\delta,\delta)}{\kappa(r)},
\qquad
\mathbb E_\theta C\ge
\frac{c\operatorname{kl}(1-\delta,\delta)}{\kappa(r)}.
\tag{7}
\]

**Proof.** If E N is infinite the root-count bound is immediate (and positive c makes expected cost infinite); otherwise use the following argument. Augment the observed experiment by revealing each newly activated report in a record hidden from the actual policy. The action kernels remain those of the original policy, and extraction kernels are identical under both truths given reports. The augmented log likelihood ratio is the sum of activated report log likelihood ratios. Activation occurs before seeing that independent root. Bounded root increments and finite E N give expected sum κ(r)E N, by stopped-sum conditioning or truncation. The observed transcript has no larger KL; binary decision data processing finishes (7). This argument justifies the random-root-count bound; substituting a random S into (1) without it would be insufficient. ∎

A common lower bound c_min>0 and common root KL upper bound yield the analogous heterogeneous bound. A once-per-task setup fee is O(1), but infinitely many imperfect independent roots require Ω(log(1/δ)) activations. The distinction changes when r→1, access cost vanishes, side information reveals truth, or one activation is amortized over a growing number of facts. No exact optimal coefficient is asserted by (7).

## 5. Proposition 4: exact coefficient in a restricted completed-block class

Assume K: fixed known r,a∈(1/2,1). Before each fresh root, select k≥1; take all k same-format extractions; discard the root permanently. Stop only at completed-block boundaries. Next k may adapt to earlier completed blocks. Within-root stopping and revisits are excluded by the policy-class definition.

If s of the k responses are positive, put

\[
f_k(s)=a^s(1-a)^{k-s},\quad g_k(s)=(1-a)^s a^{k-s},
\]
\[
P_{+,k}(s)=\binom{k}{s}[r f_k(s)+(1-r)g_k(s)],
\quad
P_{-,k}(s)=\binom{k}{s}[(1-r)f_k(s)+r g_k(s)].
\]

Define D_k=KL(P_{+,k}||P_{−,k}). Then

\[
\boxed{
\inf_{\pi\in\Pi_{\rm block,\delta}}
\mathbb E_\theta C_\pi
=K_c(a)\log(1/\delta)+O(1),\qquad
K_c(a)=\min_{k\ge1}\frac{c+k\ell}{D_k}.}
\tag{8}
\]

The O(1) is for fixed r,a,c,ℓ, as δ↓0. It does not assert uniformity over those parameters.

**Proof.** D_1=κ(ra+(1−r)(1−a))>0. Adding an observation gives D_{k+1}>D_k: after every finite history, the posterior probabilities of V under the two truths differ strictly and the next extraction channel is informative. Also D_k≤κ(r). As k→∞, the sample mean identifies V almost surely; the block likelihood ratio converges to the root likelihood ratio. It is bounded between (1−r)/r and r/(1−r), so dominated convergence gives D_k↑κ(r). Therefore D_k/(c+kℓ) tends to zero, and its positive maximum I* occurs at finite k*.

For any allowed policy, the stopped KL chain rule gives E_θΣ_b D_{k_b}≤I*E_θ C. Uniform correctness implies E_θ C≥kl(1−δ,δ)/I*. For the upper bound, repeat k* and run the symmetric SPRT at ±R, R=log(1/δ). Likelihood-ratio martingales give both errors ≤δ. The iid block increments have positive drift D_{k*} under +, bounded magnitude by logit(r), and finite expected stopping time (a bounded-increment concentration bound supplies a summable tail). Wald's identity and bounded overshoot give

\[
\mathbb E_+C\le\frac{c+k_*\ell}{D_{k_*}}[R+\operatorname{logit}(r)].
\]

The negative truth is symmetric. The lower bound differs from R/I* by o(1), proving (8). ∎

Two structural consequences are also rigorous:

**Pairwise crossover.** For k>1,
\[
k\text{ beats }1
\iff c(D_k-D_1)>\ell(kD_1-D_k).
\tag{9}
\]
This needs no unproved concavity/subadditivity of D_k. It is a comparison of completed-block information rates, not a state-dependent optimal stopping rule.

**Monotone extraction depth with access cost.** For c_1<c_2, any minimizing depths obey k_1≤k_2. Write the objective as c/D_k+kℓ/D_k. Optimality at c_1 and c_2 gives
\[
(c_2-c_1)(1/D_{k_2}-1/D_{k_1})\le0.
\]
Strict increase of D_k yields the result. Ties at an individual c are allowed. This is a model-specific structural consequence of a standard lower-envelope argument.

**What this does not prove.** No optimum for unrestricted root revisits, unknown p/q, root-dependent query costs, or group-shared activation. No inheritance of the original smallest-sharing-group formula. The KL/SPRT framework is standard sequential design, and equation (8) alone has insufficient novelty.

## 6. Exact local decision; a missing-state counterexample

At any history H in K, define m=E[θ|H], h_i=E[θV_i|H], s=2a−1, t=2r−1. Stop-now Bayes error is L_0=(1−|m|)/2. After exactly one further query and terminal Bayes decoding,

\[
L_i=\frac{1-\max\{|m|,s|h_i|\}}2,
\qquad
L_{\rm new}=\frac{1-\max\{|m|,st\}}2.
\tag{10}
\]

**Proof.** The signed joint mass for answer y is
P(θ=+,Y=y|H)−P(θ=−,Y=y|H)=(m+ys h_i)/2.
Sum its absolute value over y and use (|x+y|+|x−y|)/2=max(|x|,|y|). For a fresh root E[θV_new|H]=t. ∎

For the stated one-step loss error+λ·cost, new beats repeat iff L_i−L_new>λc, with stopping also checked. It is not a multi-step or fixed-confidence rule.

Let r=4/5,a=7/10, λℓ=.01, λc=.02. Both roots have two answers:

| History | Root 1 | Root 2 | P(θ=+|H) | E[θV_1|H] | Stop loss | Repeat loss | New loss | Best action class |
|---|---|---|---:|---:|---:|---:|---:|---|
| H1 | +,− | +,− | 1/2 | 3/5 | .5 | .39 | .41 | repeat |
| H2 | +,+ | −,− | 1/2 | 1323/3485 | .5 | .4340746 | .41 | new |

All entries follow from exact rational posterior calculations. Repeating either old root is symmetric, so uniqueness refers to the repeat-versus-new-versus-stop action **class**, not to one root identity. Both histories have positive probability. They have identical truth posterior and counts; the provenance posterior differs. Thus truth uncertainty plus root query counts is not a sufficient state for even this one-step decision.

For finite budgets, use the joint posterior over θ and reports (plus unknown format/rate variables when applicable). The Bellman recursion is

\[
F_B(\pi)=\min\left\{L_0(\pi),\;
\min_{u:\,c(u)\le B}\sum_yP_\pi(y|u)F_{B-c(u)}(\pi^{u,y})\right\}.
\tag{11}
\]

The exact checks use the equivalent sufficient root-count state for known channels, with each root's positive and negative counts retained separately. A full θ posterior by itself is insufficient. The recursion is standard; it is a reference solver for tiny instances, not a scalable new method.

## 7. Proposition 5: expensive independent evidence can erase a relative format premium without sharing

This is a further structural exploration. **Changed assumptions:** one fact; known r∈(1/2,1), known 1/2≤q<p<1; unknown z∈{A,B}; unlimited iid roots; known c>0 and ℓ>0. There is no cross-fact sharing, offline calibration, or direct type-question action in this experiment. Available actions are acquisition, extraction, and stopping. Let T_u(c,δ;θ,z) be the infimum expected **total cost** among policies correct for both truths and both formats, and T_o the corresponding type-informed oracle optimum. Both may revisit roots. Then

\[
\boxed{
\lim_{c\to\infty}\limsup_{\delta\downarrow0}
\frac{T_u(c,\delta;\theta,z)}{T_o(c,\delta;\theta,z)}=1.}
\tag{12}
\]

**Proof.** Consider a feasible policy taking k queries of each format at every fresh root, retaining only their total positive count S. Conditional on V=+, its count distribution is
\[
f_k=\operatorname{Bin}(k,p)*\operatorname{Bin}(k,q),
\]
which is invariant to swapping z. Conditional on V=− it is the reflection f_k(2k−s). Mix these with weights r and 1−r under the two truths and call their KL \(\bar D_k\). It is positive, at most κ(r), and tends to κ(r): the fraction S/(2k) tends to (p+q)/2>1/2 when V=+, and its complement when V=−. Hence S consistently identifies V, and bounded log likelihood ratios again give KL convergence.

A symmetric SPRT on these z-invariant independent blocks is correct for both θ,z without learning z. For every fixed k,
\[
T_u\le\frac{c+2k\ell}{\bar D_k}[R+\operatorname{logit}(r)].
\]
Proposition 3 applies to all oracle policies, including revisits:
\[
T_o\ge c\operatorname{kl}(1-\delta,\delta)/\kappa(r).
\]
Also T_u≥T_o since the oracle can ignore its extra information. First let δ↓0 for fixed c,k, then let c→∞. The ratio's limsup is at most κ(r)/\(\bar D_k\). Let k→∞ to obtain 1, which matches the lower bound. ∎

**Interpretation and limits.** Learning the preferred format can become negligible relative to expensive independent evidence acquisition, even for a singleton. This is a different mechanism from amortizing format learning over a large sharing group. It is an ordered two-limit **relative** statement; it does not say that the fixed-c logarithmic premium is zero, that the additive premium vanishes, or that knowing p,q is cost-free in the original experiment. It remains valid for q=1/2 because balanced extraction is informative. It does not establish the continuous-unknown-p/q version. The balanced policy itself is a strong simple baseline: if it suffices, an elaborate format learner is unnecessary.

**Novelty status: REVISE.** The argument is complete under these assumptions and has received a separate same-family check. The literature audit establishes close ancestors but not originality of this precise interaction. This is the most interesting additional structural result to investigate, not a confirmed paper contribution. Its proof uses standard saturation and block-testing tools.

## 8. Analytical checks and degenerate cases

`exact_checks.py` performs no random-world sampling or model inference. `ANALYTICAL_CHECKS.json` retains exact rational Bayes risks, a 162-case comparison of independent latent enumeration with (10), eight exact report-floor checks, and 12 tiny budget/reference comparisons. KL examples use 80-digit Decimal calculations; they are not directed interval certificates.

At r=.8,a=.7,ℓ=1, selected completed-block depths for c=0,1,3,10,50 are respectively 1,3,5,9,18. These are numerical evaluations of (8), not a theorem that depth always takes these values outside this fixture. The universal bound D_k≤κ(r) excludes depths beyond the computed range for these examples, subject to the stated numerical comparison.

At c=1,B=9, the exact finite-budget Bayes errors are .27299048 for the Bellman optimum, .323456 for fresh-root-only querying, and .2756216 for one-root-only querying. This is a small controlled exact example, not empirical agent performance or a tuned benchmark.

For r=.8,a=.9, 51 one-root repeats have Bayes error approximately .20000000000012, versus .0001198849 from 51 independent-root single extractions. This comparison counts responses and excludes access cost; equations (8)–(12) handle the cost tradeoff.

Degenerate checks:

- r=1/2: no factual information, regardless of extraction quality.
- r=1: persistent source error disappears; D_k=kκ(a), so the finite-root obstruction and finite optimal-depth argument no longer apply.
- a=1: the first read reveals V, and repeats add no information.
- a=1/2: no report information; one-format block testing is impossible.
- ℓ=0: infinitely deep extraction may have a limiting optimum unattained at finite k.
- p=q: preferred format is unidentifiable and immaterial; original strict-gap assumptions fail.
- Correlated root errors, unanchored adversarial orientation, or extra truth-bearing metadata: rederive the model; none is silently covered.
- Replacing θ with V recovers an extraction task but changes the scientific objective. Original extraction calibration cannot silently become source-truth calibration.

For an exact coefficient reduction through (6), also match the **induced alternative parameter domain**. For example, known r and original upper bound a≤1−η imply an effective upper endpoint ½+(2r−1)(½−η). Reusing the unchanged, larger original alternative domain may yield a conservative valid procedure, but does not establish equality of optimal coefficients for the restricted experiment.

## 9. What remains unsolved

The important open problem is the fixed-c acquisition-versus-revisit frontier with unknown continuous p,q and shared z_g, including finite calibration. To promote it, one needs a new stopped hierarchical likelihood, a joint information lower bound, a matching feasible policy, and a precise statement about the sharing structure. An arbitrary POMDP Bellman equation or plugging effective accuracy into the old Γ formula does not solve those obligations. Current results support a modest Web boundary extension and a separate candidate research direction, not a wholesale replacement of the existing theory.
