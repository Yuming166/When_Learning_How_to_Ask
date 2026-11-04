# Shared reliability in a general recommendation catalogue

Date: 2026-11-03. Scope: analytic structural results at `alpha=0`, with bounded
CPU checks and separately scoped assistant derivations. Not external expert
review, formal proof-assistant verification or literature-priority certification.
The published manuscript and historical results are unchanged.

## 1. Model retained and scope added

Use exactly the previous binary-coordinate channel: fixed unknown
`theta in {−1,+1}^d`, known partition `S_1,...,S_G`, arbitrary fixed unknown
better formats `z_g`, and common unknown rates `1/2<=q<p<=1−eta`. Every query
has unit cost; responses are fresh and conditionally independent. The oracle
knows only `z`, not the signs or rates. There are no direct type-report actions.
Both labelled reference streams have `M_delta=o(log(1/delta))`, so `alpha=0`;
this does not require that there are literally no reference observations.

The output is the unique best item in any known finite affine catalogue,
`f(theta)=argmax_i(b_i+v_i^T theta)`, on the full sign cube. The results below
also hold for any fixed finite-output decision map. Fix the true sign vector.
Write `H` for its nonempty family of minimal decision-changing flip sets.
Constant decision maps have online coefficient zero and are excluded below.

All results concern the leading online coefficients `K` and `K_or` of the
previous continuous information program. Its ideal tracking interpretation
and actual-error numerical contract remain as stated in the previous note;
the present scripts do not implement an online policy. No new finite-budget
algorithm or natural-user reliability claim is made.

Let `D` be Bernoulli KL and `h` binary entropy. Define

\[
 B_p=D(p,1/2),\quad
 \psi_p(s)=h(\max\{1/2,p-(2p-1)s\})-h(p),\quad
 \rho=\max_{w\in\Delta_d}\min_{F\in H}w(F).
 \tag{1}
\]

The existing oracle theorem gives `K_or=1/psi_p(rho)` and says that every
oracle-optimal allocation uses only the true good formats. These facts, rather
than any assumption that an unknown-type optimum is good-only, are used below.
The flip-cover LP and fractional certificate interpretation are established
objects; we do not claim to introduce them.

## 2. Exact general equality criterion with the rates eliminated

For good-format probability weights `w`, a flip set `F`, and group subset `A`,
put

\[
 W_A=\sum_{g\in A}w(S_g),\qquad
 T_A=\sum_{g\in A}w(F\cap S_g),\qquad t=w(F),
\]

\[
 E_p(w;F,A)=W_A\psi_p(T_A/W_A)
 +(1-W_A)\psi_p((t-T_A)/(1-W_A)).
 \tag{2}
\]

An empty block contributes zero. This is the continuous perspective convention
at zero group mass. Define

\[
 J_p(w)=\min_{F\in H,\ A\subseteq[G]} E_p(w;F,A).
 \tag{3}
\]

**Theorem 1 (general catalogue, zero or positive reliability premium).**
For any nonconstant decision map and any allowed `q<p`,

\[
 \boxed{\quad K=K_{\rm or}
 \iff \exists w\in\Delta_d:\ J_p(w)\ge\psi_p(\rho).\quad}
 \tag{4}
\]

The right side is a finite convex feasibility test: each term (2) is concave
in `w`, so its superlevel set is convex. It contains no unknown candidate rates,
no allocation variables for the other format, and no `q`. Consequently the
**zero-versus-positive boundary is independent of q at alpha=0**, although the
size of a positive premium can depend on q.

**Proof of the rate elimination.** A group with total sampled mass `W` and
flip fraction `s` contributes, at its assigned candidate rate `x>=1/2`,

\[
 W L_p(s,x),\qquad L_p(s,x)=(1-s)D(p,x)+sD(p,1-x).
\]

Its fitted mean is `max(1/2,p-(2p-1)s)`, giving minimum `W psi_p(s)`. The fit
never exceeds `p`, so the upper rate bound is respected. A candidate type
assignment partitions groups between two common rates. Once a partition is
chosen, each pool is fitted independently; swapping the two pools respects
the ordering of the common rates. Thus minimizing all allowed candidate type
assignments and rates gives exactly (2)--(3). Equal fitted rates are allowed
in the closure, as in the original infimum.

By the oracle theorem, any allocation attaining the oracle cost in the
unknown-type problem must itself be a good-only oracle optimum. At total cost
`1/psi_p(rho)`, its feasibility is precisely (4). Conversely any witness in
(4), scaled to that cost, is feasible for the full unknown-type program, so
the lower oracle bound is attained. Compactness excludes a limiting equality
without an allocation attaining it: intersect nonnegative allocations with a
bounded total-cost sublevel; all information constraints are closed. This
also makes failure of (4) a **strict** cost gap. `square`

For clarity, `1/max_w J_p(w)` is the optimum when querying only true good
formats is imposed. Outside equality, it need not equal `K`: an unknown-type
optimum can use both formats. Our full continuous diagnostics retain both.

### Checking a proposed allocation uses only sorted group cuts

For a fixed `F,w`, sort used groups by
`s_g=w(F intersect S_g)/w(S_g)`. Only prefixes in this order are needed in (2).
Indeed, for `u>v`,

\[
 \frac{\partial}{\partial s}[L_p(s,u)-L_p(s,v)]
 =(2p-1)[\operatorname{logit}(u)-\operatorname{logit}(v)]>0.
\]

At fixed rates, the cheaper assignment therefore divides groups at a threshold
in `s_g`. Reassigning an optimal fit in this way and refitting cannot increase
the objective, so some sorted prefix attains the global minimum. Tied fractions
and equal fitted rates permit an entire tied block on either side.

Once group and flip masses are supplied, (3) can be evaluated in
`O(|H| G log G)` arithmetic operations. From coordinate weights and explicitly
listed edges, including mass preprocessing gives
`O(d + sum_{F in H}|F| + |H| G log G)`. This does **not** make the entire
catalogue problem polynomial: the flip family can be exponentially large, and
the sorting order depends on `w`. The fixed convex formulation still has a
constraint for every group subset; the prefix result is a separation/evaluation
tool, not a claim of only `G+1` globally fixed constraints. Ordered clustering
itself is an established tool, not the novelty claim.

## 3. The unsaturated region: the geometry of oracle allocations matters

Suppose `rho<1/2` and define the oracle polytope

\[
 \mathcal W=\{w\in\Delta_d:w(F)\ge\rho\ \forall F\in H\}.
 \tag{5}
\]

It is the complete set of normalized oracle-optimal coordinate allocations in
this region. For `w in W`, call `F` binding when `w(F)=rho`.

**Theorem 2 (binding balance and the dimension of the oracle face).**
If `w` witnesses equality in (4), then for every used group and every binding
flip set,

\[
 \boxed{\quad w(F\cap S_g)=\rho\,w(S_g).\quad} \tag{6}
\]

Let `L` be the number of groups with positive `w` mass, and let `face(w)` be the
minimal face of `W` containing `w`. Then

\[
 \boxed{\quad L-1\le\dim\operatorname{face}(w)\le\dim\mathcal W.\quad}
 \tag{7}
\]

In particular, **if the oracle coordinate allocation `w*` is unique**,

\[
 \boxed{\quad K=K_{\rm or}
 \iff \operatorname{supp}(w^*)\subseteq S_g
 \text{ for some }g.\quad} \tag{8}
\]

**Proof.** A witness of (4) belongs to `W`: the unsplit alternative gives
`J_p(w)<=min_F psi_p(w(F))`, and strict increase below `rho<1/2` forces every
coverage to be at least `rho`. On a binding set the pooled flip fraction is
`rho<1/2`. Isolate any
used group and pool all others. If its fraction differs from `rho`, strict
Jensen inequality for `psi_p` gives information strictly below `psi_p(rho)`.
The inequality remains strict when one pool is in the flat part: its chord to
a different pool lies strictly below the function at an interior average below
one-half. This proves (6). Conversely (6) makes every split of that binding set
attain exactly `psi_p(rho)`.

For each used group define `v_g=w|S_g/w(S_g)`. Its difference `d_g=v_g-w` has
zero sum, is supported on `supp(w)`, and preserves every binding equality by
(6). For sufficiently small positive and negative steps, it also preserves all
slack inequalities and nonnegative coordinates. Thus `d_g` lies in the tangent
space of `face(w)`. The vectors `v_g` have disjoint supports. Their differences
span dimension `L-1`: their sole linear relation is proportional to
`sum_g w(S_g)d_g=0`. This proves (7). A unique oracle point has dimension zero,
so its support must be in one group. Conversely a good-only allocation inside
one group has information `psi_p(w(F))` for each wrong decision, irrespective
of which candidate rate that group uses, and attains oracle cost. `square`

An arbitrary oracle vertex cannot furnish a multi-group equality witness. In
some catalogues equality requires an interior mixture of oracle-optimal
allocations; picking an arbitrary oracle LP vertex can lose that property.
This is an allocation-selection consequence, not a tested online algorithm.

### Why the nonbinding alternatives cannot be omitted

Condition (6) settles every binding set, but (4) must still be checked on all
nonbinding sets. A six-coordinate counterexample has groups
`A={a1,a2,a3}`, `B={b1,b2,b3}` and

\[
 H=\{\{a_i,b_i\}:i=1,2,3\}\cup\{A,B\}.
 \tag{9}
\]

Its cover value is `rho=1/3`. Uniform weights balance all three binding pairs
perfectly, while either nonbinding row has information `B_p/2<psi_p(1/3)`.
This failure holds at every oracle allocation: pairs exhaust the coordinate
mass and force pair coverage `1/3`; balance forces each used group uniform;
the two row informations are `lambda B_p` and `(1-lambda)B_p`, one at most
`B_p/2`. A single used group misses the opposite row entirely. Thus the full
problem has strictly positive premium. This is a failure of the proposed
binding-only criterion, not merely of one convenient weight vector.

## 4. A true three-item catalogue beyond cardinality thresholds

Take six preferences and

\[
\begin{aligned}
 U_0&=0,\\
 U_1&=-6\theta_1-4\theta_2-4\theta_3-2\theta_4-2\theta_5,\\
 U_2&=-1-2\theta_2-2\theta_3-4\theta_4-4\theta_5-8\theta_6.
\end{aligned}\tag{10}
\]

On the full 64-state sign cube there are no ties; utilities have different
residues modulo four. Winner counts are `(20,21,23)`. Every coordinate can
change the recommendation. At the all-positive state, item 0 wins and

\[
 H=\{12,13,234,235,145,236,46,56\},
 \quad\rho=5/13,\quad w^*=(3,2,2,1,1,4)/13.
 \tag{11}
\]

Here `12` means `{1,2}`, not an integer index. The first five alternatives
switch to item 1 and the last three to item 2. Both competitors contribute
necessary overlapping flip sets of different cardinalities.

In this order the exact dual distribution is
`(2/13,2/13,3/26,3/26,1/13,0,5/26,5/26)`. It gives every coordinate inclusion
load `5/13`. The primal covers every listed set by at least `5/13`. The
dual-positive incidence equations have rank six and force exactly `w*`;
hence the oracle allocation is unique. These are rational identities, not
claims inferred from a floating solver. By (8), the premium is zero **iff all
six coordinates share a group**. In particular the split `(123,456)` has a
strictly positive premium for every allowed `p,q` at `alpha=0`.

This is not an isolated catalogue point. Its exact minimum winner gap over the
full cube is one. If every item's parameter perturbation satisfies
`|Delta b_i|+sum_j|Delta v_ij|<1/2`, every winner is unchanged: each pairwise
winner margin loses less than one. Thus the decision geometry, winner counts
and conclusions persist on an explicit open parameter neighborhood. This
stability preserves the decision map; it is not a new weighted-catalogue
characterization by itself.

At `p=.8,q=.6`, full continuous-program diagnostics give

| Partition | Unknown-format coefficient | Type-only oracle coefficient |
|---|---:|---:|
| all six together | 5.46065866 | 5.46065866 |
| (123,456) | 9.21964892 | 5.46065866 |

These multiply `log(1/delta)`. They are not finite-budget savings, recommendation
accuracy or certified floating intervals. The second optimizer uses both
formats; the calculation did not artificially restrict it to good queries.

The separate catalogue note also contains unequal-weight two-item controls.
One unsaturated example is `U_1-U_0=5 theta1+4 theta2+2 theta3+theta4-7`, with
`H={1,2,34}`, `rho=1/3`. It has zero premium exactly when one group contains
coordinates 1, 2 and at least one of 3 or 4. Its decision geometry is not an
equal-cardinality threshold.

## 5. A rate-dependent boundary in one fixed catalogue

General catalogue geometry does not admit a `p`-independent extension of the
old threshold rule. For `k>=3`, use two groups of size `k`,

\[
 H_k=\{\{a_i,b_i\}:i=1,\ldots,k\}\cup\{A,B\}.
 \tag{12}
\]

Every coordinate is globally relevant. The exact cover value is `1/k`, while
the restricted cover value of **either group is zero** (it misses the opposite
row). Nonetheless:

**Theorem 3 (explicit reliability-rate transition).**

\[
 \boxed{\quad K=K_{\rm or}
 \iff \psi_p(1/k)\le B_p/2.\quad} \tag{13}
\]

**Proof.** Uniform coordinate weights give information `psi_p(1/k)` on pairs
and `B_p/2` on rows, proving sufficiency. At any oracle optimum each disjoint
pair has coverage `1/k`. An equality witness must use both groups and obey
(6), forcing `w_ai=lambda/k`, `w_bi=(1-lambda)/k`. Its row informations are
`lambda B_p` and `(1-lambda)B_p`, so their minimum cannot exceed `B_p/2`.
This proves necessity. The exact set of equality group mixtures, when it
exists, is `lambda in [psi_p(1/k)/B_p,1-psi_p(1/k)/B_p]`. `square`

For `k=7`, the ratio `psi_p(1/7)/B_p` is strictly increasing in `p` and crosses
one-half exactly once. To prove this, put `e=2p-1`, `a=5/7` and

\[
 J(e)=\log2-h((1+e)/2)
     =\sum_{n\ge1}\frac{e^{2n}}{2n(2n-1)}.
\]

The ratio equals `1-J(ae)/J(e)`. The second quotient is a weighted average of
the strictly decreasing sequence `a^(2n)`, with weights proportional to
`e^(2n)/[2n(2n-1)]`. Increasing `e` strictly tilts the weights to larger `n`;
equivalently its derivative in `log e` is the strictly negative covariance
of `a^(2n)` and `2n`. The endpoint limits are `24/49<1/2` and
`h(1/7)/log2>1/2`. The latter can also be replaced by the exact upper-bracket
sign check below, so no numerical endpoint judgement is needed for existence.

Exact rational log-series enclosures establish

\[
 0.73489<p_*<0.73490.
 \tag{14}
\]

An 80-digit decimal computation gives `p*=0.734893622116569...` (the digits are
an approximation; (14) is the certified bracket). For example fix `q=.55` and
`eta=.01`: the *same* user state, partition and catalogue have zero premium
throughout `p in [.6,.7]` and strict positive premium throughout `p in [.8,.9]`.
This concerns overhead **relative to the rate-matched oracle**, not a claim
that better answers make absolute query costs rise. It does not give an
explicit uniform lower bound on the positive cost ratio over that interval.

### These antichains are genuine affine catalogues

For any finite nonempty antichain `H` of nonempty coordinate subsets, let
`x_j=(1-theta_j)/2`, set `U_0=0`, and create
one item per `F in H` with

\[
 U_F=\sum_{j\in F}x_j-|F|+\epsilon_F,
 \qquad 0<\epsilon_F<1/4,
 \tag{15}
\]

where all `epsilon_F` are distinct. An item is positive exactly when all of its
coordinates are flipped. Incomplete sets have score at most `-1+epsilon_F`.
Distinct fractional offsets make all items' utilities different whenever
their integer parts agree. Thus the winner is unique everywhere. At the
all-positive state baseline 0 wins and the minimal flip family is exactly `H`.
At the state flipping precisely `F`, its corresponding item wins uniquely
because the antichain prevents any other edge being fully flipped. Therefore
all `|H|+1` items can win; none is a dominated padding item.

For `k=7`, (12) requires 14 preferences and 10 items. No model-generated labels
or hand-specified response probabilities in language prompts are involved.
The construction is a deterministic analytic catalogue, not a real dataset.

## 6. What cannot be compressed to a group statistic

The condition `max_g rho_g=rho` is sufficient for equality below saturation,
but not necessary: (12)--(13) can give equality even though every `rho_g=0`.
Even the entire tuple `(rho,rho_1,...,rho_G)` is insufficient at fixed `p`.

Use `k=8,p=3/4` and compare (12) with the same pair edges but rows replaced
by `{a1,a2}` and `{b1,b2}`. Both have `d=16`, group sizes `(8,8)`, global
`rho=1/8`, and restricted values `(0,0)`. The complete rows have zero premium:
`psi_p(1/8)<B_p/2`, with exact integer certificate
`2^40*3^6 < 11^11*5^5`. In the short-row catalogue, binding balance forces
within-group uniformity; oracle feasibility forces group masses one-half.
A short row then has information `psi_p(1/4)/2<psi_p(1/8)` by strict concavity,
so its premium is strictly positive. Both antichains have affine realizations
by (15). Thus full decision-flip geometry, not these summaries alone, is
needed in a general characterization.

## 7. Contribution and remaining boundaries

Relative to the previous note, the additions are the all-catalogue entropy
criterion, the unsaturated oracle-face dimension restriction and unique-oracle
corollary, a nonuniform genuine three-item application, and a fixed-catalogue
rate transition that rules out a `p`-free general group-size rule. The old
saturated group-certificate theorem remains valid and is recovered by (4).

The generic information program, fractional certificates, convex perspectives
and ordered clustering are prior mathematical tools. The intended contribution
is their structural consequence for unknown group-shared query formats, not
their invention. A bounded literature comparison cannot certify priority.

Positive-calibration general catalogues remain open; (4)--(14) must not be
applied to `alpha>0`. The channel still assumes fixed preferences, known groups,
common symmetric rates and fresh independent observations. Direct self-report,
natural language equivalence, persistent user errors and real recommendation
performance are not established here. Actual method comparisons must retain
the same decision target, observations, costs and stopping opportunity.
