# Adversarial geometry of good-only allocations at alpha = 0

Date: 2026-11-03. Scope: an independent mathematical cross-check of the model
and Theorems A/B in `research/top1_decision_theory_20261103/THEORY_RESULTS.md`.
No peer notes, network, model calls, or training were used. This note derives
finite-dimensional identities and explicit counterexamples; it is not external
peer review or a proof-assistant certificate. The initial reduction and the
three-column counterexample below were derived before receiving the parent's
candidate eight-column transition. Section 5 records that candidate-informed
follow-up separately. AI-assisted mathematical analysis was used.

## 1. Exact reduction for an arbitrary good-only allocation

Write `H` for the nonempty minimal flip antichain, put

\[
c=2p-1>0,\qquad B_p=\log 2-H(p),\qquad
\psi_p(s)=H(\max\{1/2,p-cs\})-H(p),
\]

and let `w` be a probability vector on coordinates, assigning all its mass to
their true good forms. For a fixed flip set `F`, define

\[
W_g=w(S_g),\quad T_g=w(F\cap S_g),\quad
s_g=T_g/W_g\quad(W_g>0),\qquad t=w(F).
\]

Zero-mass groups can be discarded. For a group using candidate rate `x`, its
normalized KL contribution is

\[
L_p(s,x)=(1-s)D(p,x)+sD(p,1-x)
       =-r(s)\log x-(1-r(s))\log(1-x)-H(p),
\quad r(s)=p-cs.
\]

Thus its minimizing rate over `[1/2,1-eta]` is
`x*=max(1/2,r(s))`; it lies below `p`, so the upper bound does not bind. The
minimum is precisely `psi_p(s)`.

For a subset `A` of the used groups, abbreviate
`W_A=sum_{g in A} W_g`, `T_A=sum_{g in A} T_g`. Since the type alternative
can assign each group either of two rates and can swap the labels of those
two rates, the ordering `u>=v` causes no restriction on the unordered split.
Consequently the exact reduced unknown-type information for `F` is

\[
\boxed{\quad
\mathcal I_F(w)=\min_{A\subseteq G_+}
 \left\{
 W_A\psi_p(T_A/W_A)
 +(1-W_A)\psi_p((t-T_A)/(1-W_A))
 \right\}.\quad} \tag{G1}
\]

The contribution of an empty block is zero. The allocation's full reduced
information is `min_{F in H} I_F(w)`. An allocation with total cost `C` has
information `C` times this quantity. Neither `q` nor the original true types
enter (G1); there are no other-form observations or reference observations in
this reduction. The closure allowing equal candidate rates is the same one
used in the source information program.

There is also an exact ordered version. Sort used groups by increasing `s_g`.
It suffices to consider the `|G_+|+1` prefix cuts in that order. Indeed, for
fixed `u>v`,

\[
\frac{\partial}{\partial s}
[L_p(s,u)-L_p(s,v)]
=c\log\frac{u(1-v)}{v(1-u)}>0.
\]

At those rates, assigning each group to its cheaper rate therefore sends a
prefix of the sorted fractions to `u` and the suffix to `v`. Reassigning and
then refitting cannot increase the objective. Ties and equal rates allow an
entire tied block to go to either side. Hence minimizing all prefix-cut entropy
expressions gives exactly (G1), not a relaxation.

## 2. Oracle equality in the unsaturated regime

Let

\[
\rho=\max_{w\in\Delta_d}\min_{F\in H}w(F)<1/2,
\qquad \Gamma=\psi_p(\rho).
\]

By Theorem A, equality of the unknown-type and oracle coefficients requires
a good-only oracle-optimal allocation. Its normalized weights satisfy
`min_F w(F)=rho`. By homogeneity and (G1), the following is an exact necessary
and sufficient criterion:

\[
K=K_{\rm or}
\quad\Longleftrightarrow\quad
\exists w\in\Delta_d:\quad
\min_{F\in H}w(F)=\rho,
\quad
W_A\psi_p(T_A/W_A)+(1-W_A)\psi_p((w(F)-T_A)/(1-W_A))
\ge\Gamma
\quad\forall F\in H,\ A\subseteq G_+.
\tag{G2}
\]

Only sorted prefix cuts are needed for each `F`. This finite entropy criterion
is useful even though it is not a formula in a single group statistic.

An important necessary condition follows by inspecting every globally binding
flip set, namely each `F` with `w(F)=rho`:

\[
\boxed{\qquad s_g=\rho\quad\text{for every used group }g.\qquad} \tag{G3}
\]

To prove necessity, isolate any group whose fraction differs from `rho` and
put all other groups in the other block. The two block fractions differ and
their weighted mean is `rho<1/2`. Strict Jensen inequality for `psi_p` then
makes (G1) strictly smaller than `psi_p(rho)`. Here strict Jensen still holds
if one block lies in the constant part: `psi_p` is strictly concave below
one-half, and a chord with an endpoint above one-half is strictly below the
function at every interior point below one-half. Conversely, for a fixed
binding `F`, (G3) makes every split have information exactly `Gamma`.

Thus (G3) completely resolves the binding flip sets. It does not resolve the
nonbinding flip sets. Their pooled coverage can exceed `rho` while separating
groups into two candidate rates lowers their information below `Gamma`.

## 3. A strict counterexample to checking only binding sets

Take two groups

\[
A=\{a_1,a_2,a_3\},\qquad B=\{b_1,b_2,b_3\},
\]

and the antichain

\[
H=\{\{a_i,b_i\}:i=1,2,3\}\cup\{A,B\}.
\tag{G4}
\]

The three pairs are disjoint, so `rho<=1/3`. Uniform coordinate weights attain
`rho=1/3`: pair masses are `1/3`, and row masses are `1/2`. Every globally
binding pair has fraction `1/3` in both groups. Therefore all binding sets
satisfy (G3), exactly.

The row `A`, however, has fractions `(1,0)`. Formula (G1) gives

\[
\mathcal I_A(w)=\mathcal I_B(w)=B_p/2
<\psi_p(1/3),
\]

because concavity and `psi_p(0)=0`, `psi_p(1/2)=B_p` imply
`psi_p(1/3)>=2B_p/3>B_p/2`.

This is also a global strict-inequality example, not merely a bad choice of
oracle-optimal weights. At any oracle optimum, every pair must have mass
`1/3`, since the pairs partition all coordinates. A single used group cannot
be oracle optimal because it misses the opposite row. If equality held, (G3)
would force each of the two groups' normalized weights to be uniform. Writing
`lambda=w(A)`, the row informations would then be `lambda B_p` and
`(1-lambda)B_p`. Their minimum is at most `B_p/2<Gamma`, a contradiction.
Hence `K>K_or` for every `p>1/2` allowed by the model.

The antichain is realizable by a finite affine catalogue with a unique winner
at every sign vector. More generally, for any antichain `H`, take the true sign
vector to be all `+1`, a baseline item with utility zero, and for each `F in H`
an item with utility

\[
U_F(\theta)=1+\varepsilon_F-|F|-\sum_{j\in F}\theta_j,
\qquad 0<\varepsilon_F<1/4,
\]

where the `epsilon_F` are distinct. At the sign vector flipping `B`, that item
has utility `1+epsilon_F-2|F\setminus B|`, which is positive exactly when
`F subseteq B`. Distinct offsets preclude all utility ties. The baseline's
minimal decision-changing flip sets are exactly `H`. Thus (G4) is compatible
with the affine-catalogue formulation as well as an arbitrary decision map.

## 4. Restricted group cover values do not characterize equality

The condition `max_g rho_g=rho` is sufficient: choose a single group's optimal
weights, which makes (G1) identical to the oracle problem. It is not necessary.
In fact even the entire tuple `(rho,rho_1,...,rho_G)`, with fixed `p`, fixed
dimension, and fixed group sizes, does not determine equality outside
saturation.

Here is an explicit pair with `p=3/4`, two groups of eight coordinates each,
and pair edges `P_i={a_i,b_i}`, `i=1,...,8`.

* `H_plus = {P_1,...,P_8,A,B}`, with `A` and `B` the two full groups.
* `H_minus = {P_1,...,P_8,{a_1,a_2},{b_1,b_2}}`.

Both antichains have `rho=1/8`: disjoint pairs give the upper bound, and uniform
weights attain it. Both have `rho_A=rho_B=0`, since each contains an edge wholly
inside the opposite group.

For `H_plus`, uniform weights have pair information `psi_p(1/8)` and row
information `B_p/2`. At `p=3/4`,

\[
\psi_p(1/8)=0.0587512299364368
<B_p/2=0.0654060179705685.
\]

The inequality also has an exact integer certificate: it is equivalent to
`2^40 3^6 < 11^11 5^5`. Thus `K_plus=K_or` despite both restricted group values
being zero.

For `H_minus`, equality would again force uniform normalized weights within
each group by applying (G3) to the eight pairs. Oracle feasibility of the two
short rows forces `lambda=w(A)=1/2`. The short row information is then

\[
\tfrac12\psi_p(1/4)<\psi_p(1/8),
\]

by strict concavity on `[0,1/4]`. Thus `K_minus>K_or`; this last conclusion holds
for every `p>1/2`. These two examples have identical global and restricted
fractional cover values, but opposite equality conclusions at the same `p`.

## 5. Candidate-informed follow-up: k columns and a rate transition

After the blind reduction and (G4) were reported, the parent supplied the
candidate generalization

\[
H_k=\{\{a_i,b_i\}:i=1,\ldots,k\}\cup\{A,B\},\qquad k\ge3.
\]

The candidate is correct:

\[
\boxed{\qquad K=K_{\rm or}
\iff \psi_p(1/k)\le B_p/2.\qquad} \tag{G5}
\]

Indeed, `rho=1/k`. Uniform weights yield pair information `psi_p(1/k)` and row
information `B_p/2`, proving sufficiency. Necessity follows exactly as in
Section 3: equality forces group-uniform weights, whose smaller row information
is at most `B_p/2`. This proves the equality boundary but does not assert a
closed form for the unknown-type coefficient in the strict-inequality region.

There is a genuine finite-`p` transition. Put `e=2p-1`, `a=1-2/k`, and

\[
J(e)=\log2-H((1+e)/2)
=\sum_{n=1}^\infty\frac{e^{2n}}{2n(2n-1)}.
\]

Then `psi_p(1/k)/B_p = 1-J(ae)/J(e)`. For `0<a<1`, the latter ratio is strictly
increasing in `p`: `J(ae)/J(e)` is a weighted average of the strictly decreasing
sequence `a^(2n)`, and increasing `e` strictly tilts its positive weights toward
larger `n`. Equivalently, differentiating with respect to `log e` gives the
strictly negative covariance of `a^(2n)` with `2n`. Hence

\[
\lim_{p\downarrow1/2}\frac{\psi_p(1/k)}{B_p}
=\frac4k\left(1-\frac1k\right),\qquad
\lim_{p\uparrow1}\frac{\psi_p(1/k)}{B_p}
=\frac{H(1/k)}{\log2}.
\tag{G6}
\]

For `k=8`, these limits are `7/16<1/2` and
`H(1/8)/log2=0.5435644431995964>1/2`, respectively. The second strict inequality
is equivalent to `2^20>7^7`. Thus a unique crossing exists, numerically

\[
p_*=0.957590839865981.
\]

Equality holds for `1/2<p<=p_*`, and strict inequality for `p>p_*`, intersected
with the original allowed interval `p<=1-eta`. If that interval ends before
the crossing, there is no transition inside that particular model domain.

Bounded deterministic checks for `3<=k<=10` give:

| k | behavior on 1/2 < p < 1 |
|---|---|
| 3,4,5,6 | strict inequality throughout |
| 7 | equality up to 0.734893622116569, then strict inequality |
| 8 | equality up to 0.957590839865981, then strict inequality |
| 9 | equality up to 0.999043621743438, then strict inequality |
| 10 | equality throughout |

The qualitative classification follows from (G6) and monotonicity; the decimal
crossings are numerical approximations (80-digit decimal arithmetic was used
for the root calculations). The companion standard-library script
reproduces these numbers, checks the exact integer inequalities, and compares
the exhaustive partition formula to its sorted-prefix reduction on bounded
deterministic fixtures. These checks support arithmetic and implementation;
the preceding arguments establish the claims.

## 6. Claim boundary

The reduction applies to good-only weights at `alpha=0`; it is used for an
exact equality test because Theorem A forces good-only sampling at any shared
optimum. It does not prove that a strict-gap unknown-type optimum must itself
be good-only, and it supplies no unknown-type optimum outside the equality
boundary. Unsaturated equality depends on the full flip geometry and the rate
`p`; a restricted fractional cover statistic alone cannot replace the entropy
conditions in (G2).
