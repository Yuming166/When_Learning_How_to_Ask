# Source acquisition cost and the smallest sharing group

Status: restricted-model mathematical result; not a claim about empirical Web or LLM performance. Date: 2026-10-31.

## 1. Scope and notation

Use exactly MODEL_AND_SCOPE.md. There are d fixed binary truths, a known partition with group sizes k_g, unknown shared format types z_g, and known constants
\[
1/2<r<1,\qquad 1/2\le q<p<1,\qquad c\ge0,\quad\ell>0.
\]
An independent source report V equals its fact's truth with probability r. All responses within that source share V; conditional on V their extraction errors are independent. A completed block chooses one fact and counts (n_A,n_B), with 1≤n_A+n_B≤L_max. Its cost is c+ell(n_A+n_B). Every mixed and balanced block is available. There is no within-block adaptation, revisiting, shared acquisition across facts, offline calibration, or direct type action. L_max is finite and fixed.

The output is the whole truth vector θ. Type z is a nuisance: outputting the correct type is not required. Error is bounded by δ uniformly over all states h=(θ,z); δ∈(0,1/2). Both learner and type-informed oracle have the same costs, known reliability levels, and block menu.

Write R=log(1/δ), b_δ=kl(1−δ,δ), and κ(r)=kl(r,1−r). All logarithms are natural. If C_u(h,δ) and C_o(h,δ) denote the infimum expected total costs among the respective uniformly correct policies, define their leading coefficients by their limits divided by R.

The known-level assumption is deliberate. It neither changes nor proves the original theory with unknown continuous p,q and finite calibration.

## 2. Block laws and information quantities

For a pure length-L block with extraction accuracy a, under positive truth the positive count distribution is
\[
P_{a,L}^{+}(s)=\binom Ls
\{r a^s(1-a)^{L-s}+(1-r)(1-a)^s a^{L-s}\}.
\]
Under negative truth, \(P_{a,L}^{-}(s)=P_{a,L}^{+}(L-s)\). Define
\[
A_L=D(P_{p,L}^{+}\Vert P_{p,L}^{-}),\quad
U_L=D(P_{p,L}^{+}\Vert P_{q,L}^{+}),\quad
V_L=D(P_{p,L}^{+}\Vert P_{q,L}^{-}).
\tag{1}
\]
For a mixed block, retain the positive count of each format separately. If a_A,a_B denote its two extraction rates and
\[
f(s_A,s_B)=\binom{n_A}{s_A}\binom{n_B}{s_B}
a_A^{s_A}(1-a_A)^{n_A-s_A}a_B^{s_B}(1-a_B)^{n_B-s_B},
\]
then its positive-truth law is \(rf(s_A,s_B)+(1-r)f(n_A-s_A,n_B-s_B)\). Within each format, order is conditionally exchangeable, so the two counts preserve the full block likelihood.

### Lemma 1: saturation, strict dominance, and type information

For every finite L:

1. \(0<A_L<A_{L+1}<\kappa(r)\), and \(A_L\to\kappa(r)\).
2. \(U_L>0\), \(V_L\ge U_L\), with strict inequality when q>1/2.
3. At a fixed depth, any block containing at least one bad-format response has strictly less truth-flip KL than the pure-good block.
4. \(U_L\to\infty\), and therefore \(V_L\to\infty\).

**Proof of 1.** The full truth-to-report-to-responses channel gives A_L≤κ(r). After any finite response history, both source signs still have positive posterior probability. Their posterior odds under the two truths differ by the nonunit prior-odds factor. Another p>1/2 response therefore has different conditional laws under the two truths, making the conditional KL increment strictly positive. The source sign is not perfectly identified at any finite L, making the data-processing inequality strict. As L grows, its empirical response mean identifies the source sign. The truth likelihood ratio is always between (1−r)/r and r/(1−r), so bounded convergence gives the limiting source KL κ(r).

**Proof of 2.** The positive-truth marginal response means are \(1/2+(2r-1)(a-1/2)\); p≠q implies different count laws, hence U_L>0. Also
\[
V_L-U_L
=\sum_s P_{p,L}^{+}(s)\log\frac{P_{q,L}^{+}(s)}{P_{q,L}^{-}(s)}.
\]
Pair s with L−s. For s>L/2, both \(P_{p,L}^{+}(s)-P_{p,L}^{+}(L-s)\) and the displayed log ratio are positive if q>1/2; the middle term is zero. At q=1/2 the q laws coincide and V_L=U_L.

**Proof of 3.** Start from L independent p-accuracy responses conditional on the persistent report. Each requested q-accuracy coordinate is obtained by independently flipping its p-accuracy response with probability
\[
\eta=\frac{p-q}{2p-1}\in(0,1/2].
\]
This is a truth-independent stochastic postprocessing. For any fixed values of the other coordinates, the original truth likelihood ratio changes strictly when this coordinate changes sign: the source likelihood ratio changes by a nonunit factor and the mixture likelihood ratio is strictly monotone in it. Since the flip channel has both transitions positive, equality in KL data processing is impossible. Retaining counts is sufficient both before and after the transformation, giving strict dominance for the observed laws.

**Proof of 4.** Set t=(p+q−1)/2 and consider the event E_L={|S/L−1/2|>t}. Under P_p^+ it has probability tending to one; under P_q^+ it tends to zero. More explicitly, with
\[
\epsilon_L=2\exp\{-L(p-q)^2/2\},
\]
Hoeffding's inequality gives P_p^+(E_L)≥1−ε_L and P_q^+(E_L)≤ε_L. Once ε_L<1/2, binary data processing yields
\[
U_L\ge \operatorname{kl}(1-\epsilon_L,\epsilon_L)\longrightarrow\infty.
\tag{2}
\]
The bound is loose but explicit. V_L≥U_L completes the proof. ∎

## 3. The finite-state information program

For a block action e and two states h,h', let \(D_e(h,h')=D(P_h^e\Vert P_{h'}^e)\) and \(w_e=c+\ell(n_A+n_B)>0\). Define
\[
K_h=\min_{x\ge0}\sum_e w_ex_e
\quad\text{such that}\quad
\sum_e x_eD_e(h,h')\ge1
\quad\text{for every }h'\text{ with }\theta'\ne\theta.
\tag{3}
\]
There is no constraint for a pure type change retaining the correct θ.

**Theorem 1 (optimal leading cost in the fixed-menu model).**
\[
\lim_{\delta\downarrow0}\frac{C_u(h,\delta)}{R}=K_h.
\tag{4}
\]
The oracle has the same program with alternatives restricted to z'=z. Both infima are over all adaptive policies selecting completed blocks in the fixed menu.

**Lower bound.** For any finite-expected-cost policy, the stopped adaptive likelihood chain rule gives
\[
\sum_e \mathbb E_hN_e(\tau)D_e(h,h')
=D(\mathcal L_h(\text{stopped transcript})\Vert
       \mathcal L_{h'}(\text{stopped transcript}))
\ge b_\delta
\]
for each wrong-answer h'. The last inequality follows by mapping the transcript to the event of outputting θ. Dividing expected block counts by b_δ gives a feasible point in (3), hence \(\mathbb E_h C_\tau\ge K_hb_\delta\). Infinite expected cost is already above this bound.

**Achievability.** The complete finite-state construction and expected-cost tail argument are in FINITE_STATE_PROOF_AUDIT.md. Its ingredients are:

- A deterministic selected optimal solution x*(h) for each of finitely many states, including a fixed choice when allocations tie.
- Sparse deterministic exploration of every action, with order sqrt(n) exploration pulls through block n. The one-read A and B actions distinguish all states because r>1/2 and p>q. Maximum-likelihood state errors have an exp(−const·sqrt(n)) bound.
- Bounded-discrepancy tracking of the selected normalized block allocation \(x^*(\widehat h)/\sum_e x_e^*(\widehat h)\) during exploitation.
- A likelihood-ratio stop against wrong-answer states only, at threshold \(\log(N_{\rm wrong}/\delta)\), where \(N_{\rm wrong}=(2^d-1)2^G\). A finite union of likelihood-ratio martingale bounds controls the error uniformly.
- Summable stopping tails and a separate accounting of the actual costs of tracked actions. This step is needed: multiplying the block count by the maximum action cost would not give K_h.

These give \(\mathbb E_h C_\tau=K_hR+o(R)\) with almost sure stopping. Exploration can estimate a nuisance that need not be certified at stopping. Exact finite-state mathematical optimizations are used here; no numerical implementation or rounded solver inherits the guarantee automatically. ∎

The LP, likelihood-ratio stopping, and cost-normalized information allocation are standard controlled-testing machinery. They are not claimed as the novel part of this note.

## 4. Oracle face and the exact sharing threshold

Define
\[
I(c)=\max_{1\le L\le L_{\max}}\frac{A_L}{c+\ell L},
\qquad
\mathcal M(c)=\arg\max_{1\le L\le L_{\max}}\frac{A_L}{c+\ell L},
\tag{5}
\]
and
\[
\Gamma_{k,L}=\frac{V_L+(k-1)U_L}{A_L},
\qquad k_{\min}=\min_gk_g.
\tag{6}
\]

**Lemma 2 (complete oracle-optimal face).** The oracle leading coefficient is
\[
K_o=\frac{d}{I(c)}.
\tag{7}
\]
Every oracle-optimal allocation uses only pure-good blocks with depth in M(c), and for each fact j its depth weights satisfy
\[
\sum_{L\in\mathcal M(c)}A_Lx_{j,L}=1.
\tag{8}
\]
Conversely every such allocation is oracle-optimal.

**Proof.** Compare the true state against the alternative flipping only fact j and keeping all types. Only blocks querying j contribute, so their truth KL must sum to at least one. Each action's truth KL is at most I(c) times its cost; by Lemma 1 this inequality is strict unless the block is pure-good at an oracle-optimal depth. Summing the d constraints yields cost≥d/I(c). Pure-good allocations satisfying (8) attain it, and any larger truth-changing alternative adds the corresponding nonnegative singleton contributions. Equality forces exactly the stated support and equalities. ∎

**Theorem 2 (cost-dependent smallest-sharing-group criterion).**
\[
\boxed{\quad
K_h=K_o
\quad\Longleftrightarrow\quad
\max_{L\in\mathcal M(c)}\Gamma_{k_{\min},L}\ge1 .
\quad}
\tag{9}
\]
If the inequality fails, K_h>K_o. At a unique optimal depth L*, the condition reduces to \(\Gamma_{k_{\min},L^*}\ge1\).

**Proof.** Relabel each truth and each group's formats so the true state is all positive with A good; this is a symmetry of the complete action menu. Since the unknown-type feasible set is a subset of the oracle feasible set, equality can occur precisely when some point of the oracle-optimal face is feasible for all wrong-answer type alternatives. Both programs attain their minima: costs are strictly positive and a finite feasible point exists.

On that face, consider an alternative flipping z_g and exactly one truth j in group g. Its information is
\[
\sum_{i\in g}\sum_L U_Lx_{i,L}
       +\sum_L(V_L-U_L)x_{j,L}.
\tag{10}
\]
If the type is not flipped, flipping any one truth contributes exactly one by (8). If the type is flipped, adding further truth flips adds nonnegative terms V_L−U_L. Type changes in other groups likewise add nonnegative information. Therefore, among all wrong-answer alternatives, it suffices in addition to the oracle constraints to impose (10)≥1 for each group and each j in it. This argument includes simultaneous truth and type changes in multiple groups.

Average any feasible point over permutations of facts within each group. Convexity preserves the oracle face and every constraint; each fact in group g now has the same depth weights x_{g,L}. Constraint (10) becomes
\[
\sum_{L\in\mathcal M(c)}[V_L+(k_g-1)U_L]x_{g,L}\ge1,
\qquad \sum_L A_Lx_{g,L}=1.
\]
With \(\lambda_{g,L}=A_Lx_{g,L}\), this is a convex combination
\[
\sum_L\lambda_{g,L}\Gamma_{k_g,L}\ge1,\qquad
\lambda_{g,L}\ge0,\quad\sum_L\lambda_{g,L}=1.
\tag{11}
\]
It is feasible iff \(\max_{L\in\mathcal M(c)}\Gamma_{k_g,L}\ge1\). As U_L>0, Γ is nondecreasing in group size for every L. Thus all groups satisfy the condition iff the smallest does. ∎

**Ties matter.** The theorem requires existence of a feasible allocation on the entire oracle face, not feasibility of an arbitrarily selected oracle optimizer. The maximum over M(c) is necessary. At a tie, both pure-depth allocations are cost-optimal but one can fail the unknown-type constraints while the other passes.

Equivalently, the integer sharing threshold is
\[
k_{\rm crit}(c)=
\min_{L\in\mathcal M(c)}
\max\left\{1,\ 1+\left\lceil\frac{A_L-V_L}{U_L}\right\rceil\right\}.
\tag{12}
\]
The result concerns equality of leading log(1/δ) cost coefficients. It does not say the two finite-δ costs coincide, or that their additive difference tends to zero.

## 5. What increasing source cost proves

### Proposition 3: larger source cost favors deeper oracle blocks

For fixed finite menu, oracle-optimal depth cannot move downward as c strictly increases. For i<j, A_j>A_i, and j is at least as efficient as i iff
\[
c(A_j-A_i)\ge\ell(A_i j-A_j i).
\tag{13}
\]
Once this comparison favors j, it continues to do so as c increases. In particular, if L_max>1, define
\[
c_{\rm cap}=
\max_{1\le L<L_{\max}}
\frac{\ell(A_L L_{\max}-A_{L_{\max}}L)}
     {A_{L_{\max}}-A_L}.
\tag{14}
\]
For c≥0 strictly greater than c_cap, L_max is the unique oracle-optimal depth. For L_max=1 it is always unique.

This does **not** establish that Γ_{k,L} is monotone in L. A counterexample is retained in ADVERSARIAL_AUDIT.md. Nor do we claim general monotonicity of the integer k_crit(c).

### Corollary 4: finite-cost elimination of the singleton premium is possible

For every fixed interior r and fixed p>q, there is a finite L_0 such that \(V_L\ge A_L\) for all L≥L_0, by \(A_L\le\kappa(r)\) and Lemma 1. Choose any finite cap L_max≥L_0 and then a fixed finite c strictly above (14). Theorem 2 gives
\[
K_h=K_o\quad\text{even if every group has size one}.
\tag{15}
\]
Both L_max and c are chosen independently of δ. This is a fixed-c equality of leading coefficients in the **completed-block policy class**, stronger in that respect than the preceding note's ordered double-limit result. It does not imply the same fixed-c equality for policies allowed to revisit or adapt within a source.

For a preassigned shallow cap, no such conclusion follows: high c selects that cap, so its Γ must still be checked. At L_max=1 and r=.8,p=.8,q=.6, the singleton Γ≈.430941 is independent of c; increasing acquisition cost never removes its leading premium within that menu.

In fact, if \(\Gamma_{k_{\min},L_{\max}}<1\) for a fixed cap, a positive **relative** premium persists as c→∞. To see this, divide all LP costs by c. The objectives converge to the number-of-blocks objective \(\sum_ex_e\), with weights \(1+\ell L_e/c\). A fixed feasible allocation bounds the optimum and therefore bounds \(\sum_ex_e\); alternatively, compare directly against an optimal unit-block-cost allocation. The optimal values converge to their unit-block-cost limits. At unit cost per block the oracle uniquely uses pure-good depth L_max, by strict increase of A_L and mixed-block dominance. The same oracle-face proof then gives a strictly larger unknown-type optimum when its Γ fails. Hence
\[
\lim_{c\to\infty}\frac{K_h(c)}{K_o(c)}>1
\quad\text{if }\Gamma_{k_{\min},L_{\max}}<1.
\tag{15a}
\]
This finite-cap statement is compatible with the previous note's no-cap ordered limit. The action menu, and the order in which its depth is allowed to grow, matter.

The corollary also explains the singular r→1 issue. At r=1, the source information does not saturate:
\[
A_L=L\,D(p\Vert1-p),\quad
U_L=L\,D(p\Vert q),\quad
V_L=L\,D(p\Vert1-q).
\tag{16}
\]
The resulting Γ is the original known-level ratio, independent of L. The present high-cost conclusion uses r<1 and need not hold uniformly as r approaches one. q=1/2 is included (V=U); p=q and r=1/2 are excluded boundary models.

## 6. A separate finite-cost, finite-confidence bound

The following bound concerns **one fact**, known r,p,q, and no direct type queries. It compares unknown-type and type-informed costs even in the larger class allowing source revisits, using a feasible balanced-block policy and a universal source-acquisition lower bound.

At every fresh source, take k reads of A and k of B and keep only the total positive count. Its law is invariant to swapping the type. Write its truth-flip KL as \(\overline D_k\). Conditional on V, its positive count is the convolution Bin(k,p)*Bin(k,q), or its reflection. Therefore \(0<\overline D_k\le\kappa(r)\) and \(\overline D_k\to\kappa(r)\).

A symmetric SPRT with thresholds ±R has error at most δ and a per-block log-likelihood increment bounded by b_r=log(r/(1−r)). Wald's identity gives the feasible cost bound
\[
C_u(c,\delta)\le
\frac{(c+2k\ell)(R+b_r)}{\overline D_k}.
\tag{17}
\]
Any oracle policy requires expected number of independent source acquisitions at least b_δ/κ(r), hence \(C_o(c,\delta)\ge cb_\delta/\kappa(r)\). Consequently, for c>0,
\[
1\le\frac{C_u(c,\delta)}{C_o(c,\delta)}
\le
\frac{\kappa(r)}{\overline D_k}
\left(1+\frac{2k\ell}{c}\right)
\frac{R+b_r}{b_\delta}.
\tag{18}
\]
For a finite menu require 2k≤L_max for this particular policy. In the unrestricted acquisition/revisit class there is no such restriction. This bound is valid without knowing the oracle's optimal policy and can be loose.

For a desired factor 1+ε, put \(F_\delta=\kappa(r)(R+b_r)/b_\delta\). If \((1+\epsilon)\overline D_k>F_\delta\), it suffices that
\[
c\ge
\frac{2k\ell F_\delta}
{(1+\epsilon)\overline D_k-F_\delta}.
\tag{19}
\]
If the denominator is nonpositive, this bound certifies no finite cost at that confidence level; it does not prove impossibility. As δ↓0, F_δ→κ(r), recovering a finite-c sufficient bound for the asymptotic ratio. No ordered-limit statement is silently converted into finite-confidence equality.

## 7. Scientific interpretation and limits

The mathematical mechanism is that repeated extraction from one imperfect source eventually yields little further information about truth, but can still reveal extraction reliability. Access cost changes how much of this within-source information an efficient policy acquires. Sharing across facts and learning during repeated source reads can therefore substitute for one another in the restricted model.

An appropriate Web interpretation is fact verification with persistent source claims, a fixed source-access cost, and a group-shared extraction or presentation mode. The model does not establish that actual websites or Qwen have these stochastic properties. It also assumes that distinct acquisitions provide independent root errors; copied pages cannot simply be counted as new roots.

The specialized threshold (9), its oracle-face treatment, and the finite-cost implication (15) are the candidate contribution. Generic information LPs, source saturation, controlled sensing, tracking, and handling optimizer ties have established ancestors. See FOCUSED_NOVELTY_AUDIT.md.

Still open: unknown continuous reliability levels with finite calibration; revisits and within-source adaptation; dependent or unknown provenance; a page purchase serving several facts; empirical validation; finite-sample algorithm superiority. The proof is human-readable mathematics checked by collaborators and deterministic calculations, not machine-verified formal mathematics.
