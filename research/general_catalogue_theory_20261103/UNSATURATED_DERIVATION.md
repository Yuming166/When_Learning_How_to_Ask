# General unsaturated zero-premium boundary at zero calibration

Date: 2026-11-03. Status: bounded mathematical derivation, with exact-arithmetic
checks of two scalar examples. No model/API/network/training calls. This file
extends the model and Theorems A/B in
`research/top1_decision_theory_20261103/THEORY_RESULTS.md`; it does not alter the
historical theory note or the manuscript. It is not an external mathematical
review or a proof-assistant certificate.

The entropy-cut characterization and counterexample family below were derived
independently in this subtask. The local-face dimension corollary in Section 5
was proposed by the parent and then checked here; that section is not a blind
independent discovery claim.

## 1. Scope, quantifiers, and the boundary being characterized

Fix a true state, its arbitrary nonempty finite minimal wrong-decision flip
family `H`, and the original known partition `S_1,...,S_G` of all `d` task
coordinates. All original task coordinates and both query forms remain
available actions. The oracle knows the type vector `z` only: the common
rates `p,q` remain unknown. Assume

\[
 \alpha=0,\qquad \tfrac12\le q<p\le1-\eta<1,
 \qquad
 0<\rho:=\max_{w\in\Delta_d}\min_{F\in H}w(F)<\tfrac12.
 \tag{1}
\]

Correctness is uniform over the original state domain, as in the source
model. The criterion below concerns equality of the pointwise asymptotic
information coefficients at this true state. It does not weaken the uniform
correctness requirement. Type alternatives remain unrestricted across groups,
and both candidate rates remain shared across groups.

Write natural-log binary entropy as `H_b`, put `c=2p-1`, and define

\[
 B_p=\log2-H_b(p),\qquad
 \psi_p(s)=H_b(\max\{\tfrac12,p-cs\})-H_b(p),\quad 0\le s\le1.
 \tag{2}
\]

Theorem A gives

\[
 K_{\mathrm{or}}=1/\psi_p(\rho),\qquad
 \mathcal W_\rho=
 \{w\in\Delta_d:w(F)\ge\rho\text{ for every }F\in H\}.
 \tag{3}
\]

Every oracle optimum uses only the true good forms. Its normalized coordinate
weights lie exactly in `W_rho`. Because `rho<1/2`, every such weight has at
least one binding set `F` with `w(F)=rho`. The questions here are when an
oracle optimum can also tolerate unknown formats and whether that boundary
has a simpler combinatorial description.

The conclusions are:

* An exact criterion uses only the fractional-cover optimum face and explicit
  entropy cuts of group flip fractions. It removes all candidate-rate
  minimization and the exponentially many type patterns from evaluation of
  any proposed weight.
* Every binding flip set must have exactly the same flipped fraction `rho`
  in every used group. For nonbinding sets, extra information can compensate
  for imbalance; binding balance alone is insufficient.
* A zero-premium allocation using `L` groups requires an oracle face of
  dimension at least `L-1`. In particular, a unique oracle optimum has zero
  premium exactly when its support lies in one sharing group.
* In general, concentrating an optimal certificate in one group is sufficient
  but not necessary. The zero/positive boundary can genuinely depend on `p`
  for the same flip family, partition, `q`, and rate cap. Thus a purely
  `H`/partition-only iff criterion cannot cover this entire unsaturated model.

## 2. Exact reduction to two pooled group entropies

Fix normalized good-only weights `w`. For a wrong-decision set `F`, define

\[
 W_g=w(S_g),\quad Z_g=w(F\cap S_g),\quad
 s_g=Z_g/W_g\quad(W_g>0),\quad s=w(F).
 \tag{4}
\]

Zero-mass groups remain in the state/action domain; their ratio is simply not
needed in this expression. For `A` a subset of groups, let

\[
 t_A=\sum_{g\in A}W_g,\qquad x_A=\sum_{g\in A}Z_g.
\]

Use the continuous endpoint convention for

\[
 E_{F,A}(w)=
 t_A\psi_p(x_A/t_A)
 +(1-t_A)\psi_p((s-x_A)/(1-t_A));
 \tag{5}
\]

thus `E=psi_p(s)` when `t_A` is zero or one. Define

\[
 h_p(w)=\min_{F\in H}\min_{A\subseteq[G]}E_{F,A}(w).
 \tag{6}
\]

**Lemma 1 (exact pure-good information).** The normalized unknown-format
information of `w` is exactly `h_p(w)`.

**Proof.** A true good observation has true-sign success rate `p`. If a
candidate rate `r>=1/2` is assigned to a group, its normalized contribution is

\[
 W_g\{(1-s_g)D(p,r)+s_gD(p,1-r)\}.
 \tag{7}
\]

For a pool of total mass `t` and flip fraction `a`, the minimizer is

\[
 r(a)=\max\{\tfrac12,p-ca\},
 \qquad
 \inf_r t\{(1-a)D(p,r)+aD(p,1-r)\}=t\psi_p(a).
 \tag{8}
\]

The unconstrained weighted mean is `p-ca`; clamping at `1/2` proves this by
differentiating Bernoulli cross entropy. The upper cap never binds because
`r(a)<=p<=1-eta`.

For any candidate type pattern, the groups are assigned to two pools sharing
the rates `u,v`. Dropping their order gives the sum in (5), hence a lower
bound on the information for that pattern. Conversely, fit each of any two
pools independently using (8). Assign the larger fitted rate to `u` and the
smaller to `v`, and use the permitted type pattern that makes those
assignments. Both orientations are allowed because the type vector has no
cross-group restrictions. The independent two-pool fit is therefore attained
by some allowed pattern. Taking all patterns and all `F` proves (6). The
values `u=v` are understood in the same closed-domain infimum convention as
the source information program. `square`

This reduction does not fit each group at an independent rate. There are
exactly two fitted rates; this distinction matters when `G>2`.

**Lemma 2 (only sorted cuts are needed).** For each fixed `F,w`, sort its
positive-mass groups so that

\[
 s_{g_1}\le\cdots\le s_{g_m}.
\]

Then

\[
 \min_{A\subseteq[G]}E_{F,A}(w)
 =\min_{0\le k\le m}E_{F,\{g_1,\ldots,g_k\}}(w).
 \tag{9}
\]

**Proof.** For fixed ordered rates `u>=v`, the difference between assigning a
group of fraction `a` to `u` rather than to `v`, divided by its mass, is

\[
 D(p,u)-D(p,v)
 +ca\{\operatorname{logit}(u)-\operatorname{logit}(v)\}.
 \tag{10}
\]

It is nondecreasing in `a`. Therefore an optimal assignment at fixed rates
assigns `u` to a prefix of the sorted fractions. At a tie, one may assign all
tied groups the same way: their contributions are equal at the optimizing
rates. Refitting that prefix cannot raise the objective. Compactness of the
rate interval gives an optimizer, so a sorted-prefix assignment attains the
global minimum. Conversely, every prefix is an allowed assignment, and its
two independent fitted rates have the correct order because its mean flip
fraction is no larger than the complement's. This proves (9). `square`

Thus a fixed proposed `w` can be checked in `O(|H| G log G)` arithmetic plus
entropy evaluations, rather than enumeration of `2^G` type patterns and
two-dimensional rate optimization. This is an evaluation claim, not a claim
that globally finding the required weight is a linear program.

## 3. A necessary and sufficient slack-versus-imbalance criterion

For each `F,w`, define its oracle slack and its largest two-pool concavity
loss:

\[
 L_F(w)=\psi_p(w(F))-\psi_p(\rho),
 \qquad
 \Delta_F(w)=\psi_p(w(F))-
       \min_A E_{F,A}(w).
 \tag{11}
\]

Concavity gives `Delta_F>=0`. For an oracle-optimal weight, `L_F>=0`.

**Theorem 1 (general unsaturated zero-premium boundary).** Under (1), the
following are equivalent:

1. `K=K_or`.
2. There is `w in W_rho` such that

   \[
    \Delta_F(w)\le L_F(w)\quad\text{for every }F\in H.
    \tag{12}
   \]

3. There is `w in W_rho` satisfying these explicit structural conditions:
   for every binding `F` with `w(F)=rho`,

   \[
    w(F\cap S_g)=\rho w(S_g)
    \quad\text{for every used group }g;
    \tag{13}
   \]

   and, for every nonbinding `F`, each sorted prefix from Lemma 2 satisfies

   \[
    t\psi_p(x/t)+(1-t)\psi_p((w(F)-x)/(1-t))
      \ge\psi_p(\rho).
    \tag{14}
   \]

The criterion has no `q` dependence, provided `1/2<=q<p`. The full unknown
coefficient need not be `q` independent.

**Proof.** At total cost `K_or`, any feasible unknown-format allocation is
also oracle feasible and optimal. Theorem A therefore forces it to use only
good forms, with normalized weight in `W_rho`. Lemma 1 shows that scaling
such a weight by `K_or` is unknown-format feasible exactly when

\[
 h_p(w)\ge\psi_p(\rho).
 \tag{15}
\]

Using (11), this is (12). Conversely, (12) gives a feasible allocation at the
oracle cost; the oracle lower bound then gives equality. These reductions
use all original alternatives and actions, rather than deleting nonsupport
coordinates or the other form.

For a binding `F`, Jensen's inequality gives

\[
 E_{F,A}(w)\le\psi_p(\rho).
\]

If two nonzero pools have different fractions with mean `rho<1/2`, the
inequality is strict. Indeed, their interval contains a nonempty interval
strictly below `1/2`, on which `psi_p` is strictly concave. The flat portion
above `1/2` cannot restore equality. Isolating any one used group proves
that all its fractions must equal `rho`; this is (13). Conversely, (13)
makes every pool fraction equal `rho`, so all binding-set inequalities hold
with equality. For nonbinding sets, Lemma 2 gives precisely (14).

Finally, there is no nonattainment loophole when this criterion fails. The
original allocation information functions are continuous infima over a
compact rate domain and finitely many discrete alternatives; their feasible
set is closed. An all-coordinate allocation is strictly informative because
every nonempty wrong flip set changes at least one true good observation
from success probability `p>1/2` to at most `1/2`. Thus a finite feasible
cost exists, and a minimizing sequence has a convergent subsequence in a
bounded nonnegative cost simplex. An optimum is attained. If no witness in
(12) exists, equality is impossible and `K>K_or` strictly. `square`

This is more explicit than requiring feasibility in the original unknown
program: it gives a known fractional-cover face, linear balancing equations
on its binding sets, and finitely many explicit entropy cuts on the remaining
sets. It also explains why retaining only the binding sets loses information:
slack sets can have an unequal two-rate fit that falls below the binding
level.

## 4. Useful special cases and limits of a one-group rule

Define the restricted fractional-cover value

\[
 \rho_g=\max_{v\in\Delta(S_g)}\min_{F\in H}v(F).
 \tag{16}
\]

Always `rho_g<=rho`. If some `rho_g=rho`, put an optimal certificate entirely
in that group. All wrong decisions then have normalized information at least
`psi_p(rho)` even when the group's rate label changes. Hence

\[
 \max_g\rho_g=\rho\quad\Longrightarrow\quad K=K_{\mathrm{or}}.
 \tag{17}
\]

The converse is false in general; Section 6 supplies a counterexample with
every coordinate relevant.

There is, however, an exact useful sufficient hypothesis for the converse.
If every `F in H` is binding at every `w in W_rho`, then (13) implies that
every used group's normalized restriction has mass exactly `rho` on every
`F`. Any one of those restrictions proves `rho_g=rho`. Under this additional
fully-binding hypothesis,

\[
 K=K_{\mathrm{or}}
 \quad\Longleftrightarrow\quad\max_g\rho_g=\rho.
 \tag{18}
\]

More locally, a zero-premium witness at which all `F` bind already implies
the right-hand side. The source threshold result belongs to a still stronger
unique-weight special case: in its unsaturated regime, all supporters have
the unique uniform oracle weight, so they must lie in one group.

## 5. A checked face-dimension obstruction

For `w in W_rho`, let `M(w)` be its minimal face in that polytope. Explicitly,
it preserves every zero coordinate of `w` and every binding equality
`v(F)=rho` at `w`.

**Corollary 2 (number of used groups).** If `w` is a zero-premium witness
using `L` groups, then

\[
 L-1\le\dim M(w)\le\dim\mathcal W_\rho.
 \tag{19}
\]

In particular, a zero-premium witness that is an oracle vertex is supported
in one group. If the oracle optimum is unique, with weight `w*`, then

\[
 K=K_{\mathrm{or}}
 \quad\Longleftrightarrow\quad
 \operatorname{supp}(w^*)\subseteq S_g\text{ for some }g.
 \tag{20}
\]

**Proof.** For each used group, write

\[
 v_g=w|_{S_g}/W_g,\qquad d_g=v_g-w.
\]

Equation (13) implies `d_g(F)=0` for every binding `F`. The direction also
has zero sum and vanishes at every zero coordinate of `w`. Since there are
finitely many nonbinding inequalities, small perturbations `w+t d_g` for
both positive and negative `t` preserve them and nonnegativity. Thus `d_g`
lies in the tangent space of `M(w)`.

The `v_g` are linearly independent because their nonempty supports are
disjoint, and `w=sum_g W_g v_g`. If `sum_g a_g d_g=0` and `A=sum_g a_g`,
linear independence gives `a_g=A W_g` for every `g`. The only dependence
among the `L` directions is consequently proportional to
`sum_g W_g d_g=0`; their span has dimension `L-1`. This proves (19).

A vertex has zero-dimensional minimal face, so it uses one group. In the
unique-optimum case this proves necessity in (20); concentration in one group
gives sufficiency by the same argument as (17). `square`

The dimension bound is necessary, not sufficient: balanced oracle faces can
still fail on nonbinding wrong decisions.

## 6. An explicit affine-catalogue counterexample family

Choose integers `k>=3`, `l>=2`. There are exactly two groups,

\[
 S_g=\{(g,i,r):1\le i\le k,\ 1\le r\le l\},\quad g=1,2.
\]

The minimal wrong-decision family consists of the following `k+2l` sets:

\[
 R_i=\{(g,i,r):g=1,2,\ 1\le r\le l\},\quad 1\le i\le k,
 \tag{21}
\]

\[
 A_r=S_2\cup\{(1,i,r):1\le i\le k\},\qquad
 B_r=S_1\cup\{(2,i,r):1\le i\le k\},\quad 1\le r\le l.
 \tag{22}
\]

This is an antichain. No row contains a set from (22), because those sets
contain the other whole group and `k>=2`. No set in (22) contains a row,
because it contains only one coordinate from the restricted group's row and
`l>=2`. Sets within or across the two displayed families do not contain one
another either.

Every coordinate is globally relevant, and this is a genuine affine
catalogue example. To realize any such antichain with a unique winner at
every sign vector, take true `theta=all +`, set `x_j=(1-theta_j)/2`, and use
the affine utilities

\[
 U_0(\theta)=0,\qquad
 U_F(\theta)=\sum_{j\in F}x_j-|F|+\epsilon_F,
 \quad F\in H,
 \tag{23}
\]

where the `epsilon_F` are distinct numbers in `(0,1/4)`. An incomplete set
has utility below zero; a completed set has utility `epsilon_F`. Thus item
zero wins exactly when no minimal set has been completed. Otherwise the
completed set with largest `epsilon_F` wins uniquely. At the true state the
minimal wrong-decision flip sets are exactly `H`. Each coordinate belongs
to a row edge, and toggling it after flipping the rest of that edge changes
the decision, so there are no dummy coordinates. The catalogue has only
`k+2l+1` items.

**Proposition 3 (exact boundary for this family).**

\[
 \rho=1/k,\qquad \rho_1=\rho_2=1/\max\{k,l\},
 \tag{24}
\]

and

\[
 \boxed{
 K=K_{\mathrm{or}}
 \quad\Longleftrightarrow\quad
 \tfrac12\{\psi_p(1/l)+B_p\}\ge\psi_p(1/k).
 }
 \tag{25}
\]

**Proof.** The rows partition all coordinates, so every weight has some row
of mass at most `1/k`. Uniform weight gives every row mass `1/k`, and each
set in (22) mass `(1+1/l)/2>1/k`, proving the first part of (24). On one
restricted group, rows and its own column sets are two partitions with `k`
and `l` parts. Their respective averaging upper bounds are `1/k` and `1/l`;
uniform weight attains their minimum. This proves the restricted values.

For each fixed wrong alternative, information is linear in the original
good-only weights before rate minimization. Infima preserve concavity, so
`h_p(w)` is concave. Therefore `{w:h_p(w)>=psi_p(rho)}` is convex. The
hypergraph, partition, and this feasible set are invariant under simultaneous
row permutations, independent column permutations in the two groups, and
the swap of the two groups. These symmetries act transitively on all
coordinates. If a zero-premium witness exists, averaging its orbit produces
the uniform weight, which is still feasible. Conversely, feasibility of the
uniform weight is already a witness.

For uniform weight, every row has flip fraction `1/k` in each group, so its
unknown information is exactly `psi_p(1/k)`. Each `A_r` or `B_r` has group
fractions `1/l` and `1`. Pooling them gives `B_p`, whereas separating them
gives `[psi_p(1/l)+B_p]/2`, no larger than `B_p`. Thus uniform weight is
feasible at the oracle level exactly under (25). `square`

### 6.1 A mixed-group zero-premium allocation with no one-group certificate

Take `(k,l)=(4,5)`. Then `rho=1/4`, while each `rho_g=1/5<rho`.
Nevertheless (25) holds strictly for every `1/2<p<1`.

For an analytic proof, set `c=2p-1` and define the difference in (25) by

\[
 E_{k,l}(c)=
 \tfrac12H_b(\tfrac12+c(\tfrac12-1/l))
 +\tfrac12H_b(\tfrac12)
 -H_b(\tfrac12+c(\tfrac12-1/k)).
 \tag{26}
\]

For `(4,5)`,

\[
 E'_{4,5}(c)
 =-\tfrac3{10}\operatorname{atanh}(3c/5)
  +\tfrac12\operatorname{atanh}(c/2).
\]

Convexity of `atanh` and `atanh(0)=0` give
`atanh(3c/5)<=c atanh(3/5)=c log2`, while
`atanh(c/2)>=c/2`. Hence

\[
 E'_{4,5}(c)\ge
 c\{\tfrac14-\tfrac3{10}\log2\}>0.
\]

The last inequality follows, for example, from `log2<3/4`. Since
`E_{4,5}(0)=0`, the difference is strictly positive for `c>0`. This disproves
the conjecture that zero premium always requires an oracle-optimal
certificate supported in one group.

### 6.2 Binding-set balance is not sufficient

Take `(k,l)=(3,5)`. Under uniform weight, all binding rows have exactly
fraction `rho=1/3` flipped in each group. The remaining sets have slack:
their total mass is `3/5>1/3`. Nevertheless (25) fails strictly for every
`1/2<p<1`, so no zero-premium weight exists at all.

Indeed,

\[
 E'_{3,5}(c)
 =-\tfrac3{10}\operatorname{atanh}(3c/5)
  +\tfrac13\operatorname{atanh}(c/3).
\]

Use `atanh(3c/5)>=3c/5` and
`atanh(c/3)<=c atanh(1/3)=c log2/2`. Then

\[
 E'_{3,5}(c)\le
 c\{-\tfrac9{50}+\tfrac16\log2\}<0,
\]

where even `log2<1` suffices. Since the difference is zero at `c=0`, it is
strictly negative for `c>0`. The uniform binding rows satisfy all the
balancing equations but the slack alternatives fail the entropy barrier.
The symmetry proof rules out repairing this failure with a different oracle
weight. This disproves the conjecture that binding-set balance alone is a
sufficient general criterion.

### 6.3 The boundary genuinely depends on the true better-form rate

Take `(k,l)=(5,13)`. The same fixed `H` and partition have zero premium at
`p=3/5` and positive premium at `p=99/100`. One may fix the same
`q=11/20` and `eta=1/200` in both instances; both rate pairs obey the stated
domain. The true type vector can be any fixed vector in both instances.

The rate dependence can first be seen without decimals. Expanding (26) at
zero gives

\[
 E_{5,13}(c)=\frac{17}{16900}c^2+O(c^4)>0
 \quad\text{for sufficiently small positive }c.
 \tag{27}
\]

At the continuous endpoint `c=1`,

\[
 130E_{5,13}(1)
 =153\log2+65\log13-60\log3-130\log5<0,
 \tag{28}
\]

because the exact integer inequality

\[
 2^{153}13^{65}<3^{60}5^{130}
\]

holds. Thus negativity already occurs strictly below the excluded `p=1`
endpoint. The two concrete interior rates above were checked with rational
log-series enclosures:

| True `p` | Rigorous interval for `E_{5,13}(2p-1)` | Consequence |
|---|---|---|
| `3/5` | `(0.000023044577, 0.000023044578)` | zero premium |
| `99/100` | `(-0.016171227789, -0.016171227788)` | strict premium |

Consequently no criterion that depends only on `H` and the partition, and
does not inspect `p`, can be both necessary and sufficient throughout the
general unsaturated regime. This does not rule out useful purely
combinatorial sufficient conditions such as (17), or exact conditions under
unique/full-binding oracle geometry.

## 7. Exact-arithmetic receipt for the two concrete rate signs

The following bounded standard-library computation was run once. It uses
`Fraction` arithmetic and 80 terms of

\[
 \log x=2\sum_{i=0}^{N-1}\frac{z^{2i+1}}{2i+1}+R_N,
 \quad z=(x-1)/(x+1),
 \quad0\le R_N\le\frac{2z^{2N+1}}{(2N+1)(1-z^2)},
\]

after reducing `x` into `[1,2]`. This validates the signs, rather than
assuming that ordinary floating-point output establishes them.

```python
from fractions import Fraction as Q
from math import floor, ceil

def ln_unit_bounds(x, n=80):
    assert Q(1) <= x <= Q(2)
    z = (x - 1) / (x + 1)
    s = sum((2*z**(2*i+1)/Q(2*i+1) for i in range(n)), Q(0))
    tail = 2*z**(2*n+1)/(Q(2*n+1)*(1-z*z))
    return s, s + tail

L2, U2 = ln_unit_bounds(Q(2))

def ln_bounds(x):
    if x < 1:
        lo, hi = ln_bounds(1/x)
        return -hi, -lo
    power = 0
    while x > 2:
        x /= 2
        power += 1
    lo, hi = ln_unit_bounds(x)
    return lo + power*L2, hi + power*U2

def entropy_bounds(x):
    lx, ux = ln_bounds(x)
    ly, uy = ln_bounds(1-x)
    return -x*ux-(1-x)*uy, -x*lx-(1-x)*ly

def difference_bounds(k, l, p):
    c = 2*p - 1
    a = Q(1,2) + c*(Q(1,2)-Q(1,l))
    b = Q(1,2) + c*(Q(1,2)-Q(1,k))
    la, ua = entropy_bounds(a)
    lb, ub = entropy_bounds(b)
    return (la+L2)/2-ub, (ua+U2)/2-lb

for p in [Q(3,5), Q(99,100)]:
    lo, hi = difference_bounds(5, 13, p)
    scale = 10**12
    print(p, floor(lo*scale), ceil(hi*scale), lo > 0 or hi < 0)
print(2**153 * 13**65 < 3**60 * 5**130)
```

Observed exact output, with interval endpoints scaled by `10^12`:

```text
3/5      23044577       23044578       True
99/100  -16171227789   -16171227788    True
True
```

## 8. Claim limits

This file supplies the pointwise zero-premium equality boundary at
`alpha=0, 0<rho<1/2`. It does not give a closed formula for the positive
unknown-format optimum, extend the criterion to `alpha>0`, remove the
two-global-rate or unrestricted-type assumptions, establish a novelty claim,
or make a model/agent effectiveness claim. General affine catalogues can
realize the counterexamples with unique winners and every coordinate
relevant. All task actions remain available in every theorem and example.
