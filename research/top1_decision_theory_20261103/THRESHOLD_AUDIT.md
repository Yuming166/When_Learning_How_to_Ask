# Independent audit of the threshold top-1 conjecture

Date: 2026-11-03.

Status: **SOLVED for the nonconstant threshold task, conditional only on the
standard identification of the leading coefficient with its information
allocation program.** The proposed oracle formula and both proposed
zero-premium conditions are correct for an integer threshold
`1 <= t <= d`. The allocation geometry and equality conditions below are
proved directly. The general controlled-sensing lower bound and tracking
achievability framework are background ingredients, not a new contribution.

Literal boundary warning: if `t <= 0`, recommendation 1 is correct at every
state and the true coefficient is zero. The displayed conjectured positive
coefficient would then be false. We assume the intended nonconstant task
`1 <= t <= d` throughout. A true state with `b >= t` automatically excludes
`t > d`.

Only `Theory_Note.md` was read as mathematical source. No other worker note,
model call, API call, or GPU computation was used. The original manuscript was
not modified. This file is an independent mathematical audit.

## 1. Decision alternatives and the information objective

Write `P={j: theta_j=+1}`, `|P|=b`, and

\[
h=t-1,\qquad r=b-h=b-t+1,\qquad x=r/b,\qquad s=2p-1>0.
\]

Let `N=P^c`. A decision-changing alternative has at most `h` positive signs.
For any fixed alternative channel levels and types, deleting a sign reversal
weakly reduces the divergence, because

\[
D(a,1-v)-D(a,v)=(2a-1)\log\frac v{1-v}\ge0
\quad(a,v\ge1/2).
\]

Consequently the least-favorable sign alternatives can be restricted to
exactly `r` reversed coordinates in `P`, with no reversed coordinate in `N`.
Indeed, an alternative reversing `A subset P` and `B subset N` must satisfy
`|A|-|B| >= r`; choose any `r` coordinates in `A`, and delete every other
reversal. Negative-coordinate query actions are **retained**: they supply
ordinary calibration divergence against these reduced alternatives.

Normalize online query counts by their total cost. For a normalized allocation
`w`, let its minimum decision-changing KL rate be `I(w)`. The information
coefficient is

\[
K=1/\sup_w I(w).
\]

An oracle allocation is defined identically with the types fixed under the
alternative as well as under the truth. The `alpha=0` offline streams contribute
no first-order information. We use the closed alternative channel domain,
including equal levels, as in the source note; infima over the original strict
domain have the same values by continuity.

Define the capped function on `[0,1]`

Here `D` is Bernoulli KL, `H` is binary entropy, and
`ell(v)=log(v/(1-v))`, with natural logarithms.

\[
f_p(a)=
\begin{cases}
H(p-sa)-H(p),&0\le a\le1/2,\\
B_p,&1/2\le a\le1,
\end{cases}
\qquad B_p=D(p,1/2)=\log2-H(p).
\]

It is increasing and strictly concave below `1/2`, and constant thereafter.
In particular it is concave on its entire domain. Its elementary projection
identity is

\[
\inf_{v\ge1/2}\{D(p,v)+as\ell(v)\}=f_p(a),
\qquad v_*(a)=\max\{1/2,p-sa\}.
\tag{1}
\]

All displayed fitted values are at most `p <= 1-eta`, so the upper channel bound
never obstructs these constructions.

## 2. Oracle formula and why bad-format actions cannot help

Set

\[
u_*=\max\{1/2,p-sx\},\qquad v_*=\min\{q,u_*\},
\qquad A=f_p(x).
\]

Average, uniformly, over all alternatives reversing an `r`-subset of `P`, at
this one fixed alternative pair `(u_*,v_*)`. The average divergence coefficient
of a good-format query on a positive coordinate is

\[
D(p,u_*)+xs\ell(u_*)=A.
\]

For `x<1/2`, a good-format query on a negative coordinate has coefficient
`D(p,u_*)<A`. A bad-format query on a positive coordinate has coefficient

\[
B=D(q,v_*)+x(2q-1)\ell(v_*)<A.
\tag{2}
\]

To prove the strict inequality, if `u_* <= q`, put
`F_x(a,u)=D(a,u)+x(2a-1)ell(u)`. For `a >= q >= u_*>1/2`,

\[
\partial_a F_x(a,u_*)=\ell(a)-(1-2x)\ell(u_*)>0,
\]

so `F_x(q,u_*)<F_x(p,u_*)`. If `u_*>q`, then

\[
B=x(2q-1)\ell(q)
< D(p,u_*)+x(2p-1)\ell(u_*)=A.
\]

A bad-format query on a negative coordinate has a coefficient at most `B`.
For `x>=1/2`, the same supporting alternative has `u_*=v_*=1/2`; every good
query has coefficient `B_p`, whereas every bad query has coefficient
`B_q<B_p`.

Since the minimum over alternatives is bounded by this average, every
unit-cost oracle allocation has information at most `A`. Uniform good-format
sampling on `P`, with zero weight elsewhere, attains `A` by (1). Therefore

\[
\boxed{K_{\rm or}=\frac1{f_p(r/b)}
=\frac1{\psi_p(\min\{r/b,1/2\})}.}
\]

The strict bad-format inequality proves a stronger fact: **every oracle-optimal
allocation gives zero first-order weight to every true bad-format action**,
including in the saturated regime. Thus admitting both query formats does not
improve the proposed oracle value. It is not necessary to assume them away.

## 3. The complete oracle optimal set

### 3.1 Unsaturated regime: `r/b < 1/2`

The strict supporting inequalities exclude every negative-coordinate action
and every bad-format action. The remaining normalized good-format weights
`w_j`, `j in P`, sum to one. At the fixed `u_*>1/2`, the divergence for an
alternative `A subset P`, `|A|=r`, is

\[
D(p,u_*)+s\ell(u_*)\sum_{j\in A}w_j.
\]

Its average is `f_p(r/b)`. Optimality forces every `r`-subset sum to equal its
average `r/b`. Because `1<=r<b`, exchanging one member of an `r`-subset with
one outside it proves that all `w_j` are equal. Hence the oracle optimizer is
unique:

\[
w_j=1/b\quad(j\in P),\qquad w_j=0\quad(j\in N),
\]

all on the true good formats.

### 3.2 Saturated regime: `r/b >= 1/2`

All oracle-optimal allocations still use only true good formats. They need not
sample all positive coordinates and can sample negative coordinates. For
arbitrary nonnegative weights on all coordinates with total one, put
`w(A)=sum_{j in A}w_j`. Their exact oracle information is

\[
I_{\rm or}(w)=\min_{A\subseteq P,\ |A|=r}f_p(w(A)).
\]

Therefore the complete oracle optimal set is

\[
\boxed{\mathcal W_{\rm or}
=\{w\ge0:\ \sum_jw_j=1,\quad
\min_{A\subseteq P,\ |A|=r}w(A)\ge1/2\}.}
\tag{3}
\]

At the boundary `r/b=1/2`, (3) again forces uniform weights on `P` and zero
negative weight, so the optimizer is unique there. Nonuniqueness can occur
strictly above the boundary. For example, when `t=1`, (3) merely requires total
positive weight at least `1/2`; the remaining weight may query negatives.

This distinction is essential: an argument that imports oracle uniqueness
throughout the saturated regime is invalid, even though the conjecture itself
survives.

## 4. Unknown types: the unsaturated equality criterion

An unknown-type policy can be simulated by the oracle, so `K>=K_or`. If equality
holds, its information allocation must be the unique oracle optimizer from
Section 3.1. Thus only the uniform good-format weights on `P` need be checked.

If all of `P` lies in one group, every sampled action receives the same fitted
alternative reliability, either `u` or `v`. For any `r`-subset reversal the
infimum is exactly `f_p(r/b)`, by (1), regardless of that group's alternative
type. Hence equality holds.

Conversely, suppose positive coordinates occupy at least two groups. Choose a
group containing `k` positives with `0<k<b`. There is an `r`-subset `A` such that
its positive-flip fraction `a_1=|A intersect S_g|/k` differs from the global
fraction `x=r/b`: an exchange between a positive in this group and a positive
outside it changes the group fraction, so not every `r`-subset can have the
same fraction. The complement's fraction `a_2` satisfies

\[
\frac{k}{b}a_1+\left(1-\frac{k}{b}\right)a_2=x<1/2,
\qquad a_1\ne a_2.
\]

Assign one alternative type to this group and the other to every remaining
group. Choose which type is reversed so that the larger of
`max(1/2,p-sa_1)` and `max(1/2,p-sa_2)` is the alternative high reliability.
This makes the order constraint valid and gives information

\[
\frac{k}{b}f_p(a_1)+\left(1-\frac{k}{b}\right)f_p(a_2)
<f_p(x).
\]

The Jensen inequality is strict because the weighted mean is below `1/2` and
the two arguments differ; the function has strictly negative curvature on
every nonempty subinterval below `1/2`. The oracle allocation is infeasible
at its oracle cost. Thus

\[
\boxed{r/b<1/2:\quad K=K_{\rm or}
\iff P\text{ is contained in a single sharing group}.}
\]

Negative calibration cannot rescue equality here: it is excluded by the
strict oracle supporting inequality, rather than deleted from the action set.

## 5. Unknown types: complete saturated equality geometry

Let `w` be a normalized oracle-optimal allocation in (3). In group `g`, define

\[
A_g=\sum_{j\in P\cap S_g}w_j,\qquad
N_g=\sum_{j\in N\cap S_g}w_j,\qquad W_g=A_g+N_g.
\]

Here `A_g` denotes positive weight and `N_g` negative weight in the given
group `S_g`. Let `T_h(g)` be the sum of the largest `min(h,k_g^+)`
positive-coordinate weights in that group, where `k_g^+=|P intersect S_g|`.
For `h=0`, set `T_0(g)=0`.

An alternative reverses all but `h` of the positive coordinates. Hence its
smallest possible reversed weight inside this group is exactly

\[
\min_{A\subseteq P,\ |A|=r}\sum_{j\in A\cap S_g}w_j
=A_g-T_h(g).
\tag{4}
\]

There are always enough outside positives to complete an omitted set of size
`h`, so (4) is exact, including `k_g^+<h`.

**Claim.** The normalized allocation remains optimal with unknown types if and
only if

\[
\boxed{A_g-2T_h(g)\ge N_g\quad\text{for every group }g.}
\tag{5}
\]

For sufficiency, (4)--(5) say that, under every relevant alternative, at least
half the sampled weight of each group is on reversed coordinates. Whichever
groups use alternative reliability `u`, their aggregate reversed fraction is
at least one-half; the same holds for groups using `v`. Each aggregate is
minimized at `1/2`, giving total information `B_p`. These values obey the
ordering constraint. Thus every unknown-type alternative has rate at least
`B_p`.

For necessity, suppose one positive-weight group has reversed weight
`F_g<W_g/2` for some relevant alternative. By oracle feasibility, total reversed
weight is at least one-half; the complement therefore has reversed fraction
strictly above one-half. Give this group alternative reliability

\[
u=p-sF_g/W_g>1/2
\]

and give every other group alternative reliability `v=1/2`. This is a valid
unknown-type pattern with `u>=v`. Its rate is

\[
W_g f_p(F_g/W_g)+(1-W_g)B_p<B_p.
\]

It violates optimal-cost feasibility. Equations (4)--(5) follow.

Unlike a uniqueness argument, (5) explicitly allows negative-coordinate
calibration whenever a group has enough positive-weight slack.

## 6. Cardinality criterion and why negative calibration does not change it

For any positive-weight group satisfying (5), its positive weight is nonzero.
If `h=0`, it must therefore contain at least one positive coordinate, and the
condition becomes simply `A_g>=N_g`.

If `h>=1` and a group contains `k` positive coordinates, `k<=h` is impossible:
then `T_h=A_g>0`. For `k>h`, the largest-`h` sum satisfies

\[
T_h(g)\ge\frac hk A_g.
\]

Combining this with (5) gives

\[
A_g\left(1-\frac{2h}{k}\right)\ge N_g\ge0,
\]

so `k>=2h` is necessary. Since a unit allocation has some positive-weight
group, equality requires a group containing at least `max(1,2h)` positives.

Conversely, if one group contains `k>=max(1,2h)` positives, put uniform
good-format weight on those `k` positives and zero elsewhere. Every relevant
alternative leaves at most `h` of them unreversed, so its reversed fraction is
at least `(k-h)/k>=1/2`. The allocation satisfies (5) and attains `B_p` with
unknown types. Therefore

\[
\boxed{r/b\ge1/2:\quad K=K_{\rm or}
\iff \exists g:\ |P\cap S_g|\ge\max\{1,2(t-1)\}.}
\]

At `k=2h>0`, (5) forces zero negative weight and equal positive weights within
that used group. For `k>2h`, negative weights may be feasible, but they consume
the slack `A_g-2T_h(g)` and cannot make a smaller group feasible. This is the
precise reason extra negative coordinates do not invalidate the cardinality
criterion.

For a concrete admissible negative-calibration example, take `t=2`, `b=3`, and
one group containing all three positives and one negative. Give total weight
`3/4` uniformly to the positives and `1/4` to the negative, using only true good
formats. Then `h=1`, `S=3/4`, `T_h=1/4`, `N=1/4`, so (5) holds with equality.
Every wrong-decision alternative reverses two positive coordinates, of weight
`1/2`. This allocation attains the oracle rate `B_p` despite querying a negative
coordinate at first order. It demonstrates the failure of a uniqueness claim,
without refuting the proposed equality criterion.

## 7. Strict premium when the criterion fails

At fixed finite `d` and fixed true `p>q`, the normalized action simplex is
compact and the alternative set is compact after closure. The infimum-KL rate
is continuous in the allocation, and positive at some allocation. Thus maxima
are attained. If neither applicable equality criterion holds, the proofs above
exclude every oracle-optimal allocation from the unknown-type feasible optimal
set. Consequently

\[
\sup_w I(w)<\sup_w I_{\rm or}(w),\qquad K>K_{\rm or}.
\]

This is a strictly positive first-order information gap, not merely failure of
one chosen allocation. Under the standard pointwise tracking/GLR
identification of these programs with stopping costs, it gives a strictly
positive coefficient of `log(1/delta)` in the online-cost premium.

## 8. Scope of the result

The structural result is independent of the numerical value of `q`, except that
`q<p` is needed for strict domination of bad-format weight at an oracle optimum.
It uses fresh independent responses, globally common unknown levels,
`alpha=0`, equal action costs, and no direct-type action. It does not establish
finite-budget behavior, uniformity as `p-q` tends to zero, growing-dimension
asymptotics, or an extension to constant-decision thresholds.

The generic change-of-measure lower bound, likelihood-ratio error control, and
allocation tracking are standard. The content proved here is the task-specific
oracle allocation geometry, its nonuniqueness boundary, and the exact sharing
criterion for this threshold decision.

## 9. Separate extension: finite `alpha>0`

This section leaves all `alpha=0` conclusions above unchanged. Let
`n=b`, `r=n-t+1`, and `k_g=|P intersect S_g|`. Define
`k_min^+=min{k_g:k_g>0}`. The same fresh-response, equal-cost model is used,
with no direct-type action.

**Result: the proposed finite-alpha zero-premium criterion is correct.** One
auxiliary uniqueness statement needs a correction: `u_*>1/2` implies a unique
uniform oracle allocation only when `r<n`. When `r=n` and `n>1`, the oracle
can distribute its positive-coordinate weight arbitrarily. This does not
invalidate the zero-premium criterion: `r=n` always has a strict premium at
every finite positive `alpha`.

### 9.1 Oracle value and all optimal-support restrictions

Put

\[
F_{n,r}(p,u)=rD(p,1-u)+(n-r)D(p,u)
=nD(p,u)+r(2p-1)\ell(u),
\]

and let `a>0` be the root

\[
\inf_{u\ge v\ge1/2}
\{\alpha[D(p,u)+D(q,v)]+aF_{n,r}(p,u)\}=1.
\tag{6}
\]

The root is unique: the left side is zero at `a=0`, is continuous, and increases
by at least `r B_p` times any positive increment of `a`. It tends to infinity.
The unique fitted parameter pair is obtained by first setting

\[
u_0=\max\left\{\frac12,
\frac{\alpha p+a[np-r(2p-1)]}{\alpha+na}\right\}.
\]

If `u_0>=q`, then `(u_*,v_*)=(u_0,q)`. Otherwise

\[
u_*=v_*=\max\left\{\frac12,
\frac{\alpha(p+q)+a[np-r(2p-1)]}{2\alpha+na}\right\}.
\tag{7}
\]

In every case `u_*<p` and `v_*=min(q,u_*)`. The strict inequality follows, for
example, because the derivative in `u` at `(p,q)` of the positive online term
is strictly positive.

Use the same uniform mixture over `r`-subset sign alternatives as in Section 2,
now at `(u_*,v_*)`, and retain the fixed offline contribution. Write `x=r/n` and

\[
A=D(p,u_*)+x(2p-1)\ell(u_*),\qquad
B=D(q,v_*)+x(2q-1)\ell(v_*).
\]

The proof of `A>B` in Section 2 works for every `0<x<=1`, not only `x<1/2`:
if `u_*<=q`, the derivative
`ell(c)-(1-2x)ell(u_*)` is positive on a set of positive length between `q` and
`p`; if `u_*>q`, use `B=x(2q-1)ell(q)<A`. At `u_*=1/2` this reduces to
`B_q<B_p`. Good-format negative-coordinate queries have coefficient
`D(p,u_*)<=A`, with equality only when `u_*=1/2`.

Since the offline contribution plus `na A` equals one, this supporting
alternative mixture proves

\[
\boxed{K_{\rm or}=na.}
\tag{8}
\]

It also proves that every oracle optimizer has zero true bad-format weight.
If `u_*>1/2`, every optimizer has zero negative-coordinate weight. For `r<n`,
the equal-`r`-subset-sum argument forces good-format count `a` on every member
of `P`, giving uniqueness. For `r=n`, every member of `P` is reversed under the
only minimal decision-changing sign alternative; any good-format allocation
on `P` with total `na` gives exactly the same oracle objective. Thus the
unqualified uniqueness claim is false in this endpoint case.

When `u_*=1/2`, negative-coordinate weight may occur at oracle optimality.
It is not discarded in the argument below.

### 9.2 Pooling, including `u_*=1/2`, always gives a strict premium

Suppose `u_*<=q`, so `v_*=u_*`. Consider any oracle-optimal allocation. By the
support restrictions just proved, it uses only true good formats. Its
divergence at the supporting pair and the relevant sign alternatives equals
one: for `u_*=1/2`, all selected actions have the same online divergence; for
`u_*>1/2,r<n`, the allocation is uniform on `P`; and for `r=n`, every selected
positive coordinate is reversed.

Reverse the types of **all groups** and use alternative levels
`(u,v)=(p,u_*)`. Every queried true good format now has fitted reliability
`v=u_*`, so all online divergences stay identical. The low offline stream also
has identical divergence. The high offline contribution is reduced from
`alpha D(p,u_*)` to zero. Hence this unknown-type alternative has information

\[
1-\alpha D(p,u_*)<1.
\tag{9}
\]

The parameter pair is valid because `u_*<p`. This proves a strict gap for every
oracle-optimal allocation in the pooling regime, including all allocations
with negative-coordinate weight when `u_*=1/2`.

### 9.3 A sharing group with `k_g<=r` also forces a strict premium

It remains to consider `u_*>q`, where `v_*=q`. First let `r<n`; the oracle
allocation is uniquely uniform good-format count `a` on `P`.

If a positive-containing group has `k<=r`, choose the reversed-positive set to
contain all its `k` positive coordinates, and fill the remaining `r-k`
coordinates outside the group. Reverse this group's type only and keep the
alternative levels `(u_*,q)`. Relative to the oracle supporting alternative,
the divergence changes by

\[
ak[D(p,1-q)-D(p,1-u_*)]<0.
\tag{10}
\]

The derivative of `D(p,1-v)` in `v>=1/2` is positive, and `q<u_*`, proving the
strict inequality. Thus `k_min^+<=r` implies a strict gap.

If `r=n`, all positives are reversed and oracle allocations on them may be
nonuniform. Choose any group carrying positive query weight `W>0`; reverse its
type at the same alternative levels. The change is
`W[D(p,1-q)-D(p,1-u_*)]<0`. Therefore every oracle optimizer fails, and `r=n`
also has a strict gap. This covers the uniqueness exception without assuming
uniformity.

### 9.4 Exact reduction when every positive-containing group has `k_g>r`

Here `r<n`. Initially assume `u_*>1/2`, so the only candidate equality
allocation is the uniform oracle allocation. For a set `J` of reversed-type
groups, let `k` be its number of positive coordinates. For a minimal
decision-changing positive-flip set, let `f` be the number of flipped positives
inside `J`. At any fixed `u>=v`, the online divergence is

\[
a\{(n-k)D(p,u)+kD(p,v)
 +(r-f)(2p-1)\ell(u)+f(2p-1)\ell(v)\}.
\tag{11}
\]

It is nonincreasing in `f`, because its slope is
`a(2p-1)[ell(v)-ell(u)]<=0`. The same ordering survives the infimum over
`u,v`. Thus the worst feasible overlap is `f=min(k,r)`.

If `J` contains any positives, then `k>=k_min^+>r`, so every flip can be put
inside `J` and `f=r`. The full objective becomes

\[
[\alpha+a(n-k)]D(p,u)
+\alpha D(q,v)+aF_{k,r}(p,v).
\]

It is minimized by `u=p`, since the minimizing `v` below is at most `p`.
Therefore its exact value is

\[
\Gamma_{k,r}
=\inf_{v\ge1/2}\{\alpha D(q,v)
+a[rD(p,1-v)+(k-r)D(p,v)]\},
\tag{12}
\]

with fitted level

\[
\boxed{v_{k,r}=\max\left\{\frac12,
\frac{\alpha q+a[r+(k-2r)p]}{\alpha+ka}\right\}.}
\tag{13}
\]

The fitted level does not exceed `p`, so `u=p` is feasible, including the
original upper bound `1-eta`. Increasing `k` adds the nonnegative term
`aD(p,v)` before minimization. Thus `Gamma_{k,r}` is nondecreasing in `k`.
The smallest positive `k` realized by a reversed-type group set is exactly
`k_min^+`. Group sets with `k=0` have the original oracle information one.
Consequently

\[
\boxed{k_{\min}^+>r:\quad K=K_{\rm or}
\iff\Gamma_{k_{\min}^+,r}\ge1.}
\tag{14}
\]

No negative-coordinate query appears in this equality check because their
absence was proved necessary at oracle optimality when `u_*>1/2`.

For completeness, if `u_*<=q`, choosing `v=u_*` in `Gamma_{n,r}` gives

\[
\Gamma_{n,r}\le1-\alpha D(p,u_*)<1.
\]

Monotonicity then gives `Gamma_{k_min^+,r}<1` whenever `k_min^+>r`. Thus (14)
also correctly rejects pooling and `u_*=1/2`; it does not require assuming
away their possible oracle nonuniqueness.

### 9.5 Consolidated finite-alpha statement

For every fixed finite `alpha>0`, the proposed criterion can be written without
a separate boundary case:

\[
\boxed{
K=K_{\rm or}
\iff
k_{\min}^+>r\quad\text{and}\quad
\Gamma_{k_{\min}^+,r}\ge1,
\qquad K_{\rm or}=na.
}
\tag{15}
\]

Here (12)--(13) are evaluated only when `k_min^+>r`. In particular, every
pooling case `u_*<=q`, every `u_*=1/2` case, and every `r=n` case has a strict
premium. Compactness of the fixed-cost action simplex and continuity of the
finite-alpha information function turn exclusion of every oracle optimizer
into a strictly positive value gap, as in Section 7.

The correction to oracle uniqueness is substantive but harmless for (15).
For example, take `n=r=2`, `p=3/4`, `q=1/2`, and any finite
`alpha>1/(2B_p)`. The oracle root has `u_*>1/2`: at total good count `T=alpha`,
the constrained fitted level first reaches `1/2`, and the objective there is
`2alpha B_p>1`, so the root has `T<alpha`. Nevertheless placing all `T` queries
on the first positive coordinate or on the second gives the same oracle
value. Both allocations have a strict unknown-type premium by Section 9.3.

This extension used only analytic arguments. No model calls, numerical
optimization, or additional worker files were used.
