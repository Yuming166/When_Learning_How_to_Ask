# Exact affine-catalogue examples at zero calibration

Date: 2026-11-03. Scope: explicit deterministic constructions and exact
fractional-cover witnesses; bounded CPU diagnostics for the existing continuous
information program. No inference, training, API, or network calls. No novelty
claim. The state space in each example is the full sign cube, not a restricted
set selected to make the geometry convenient.

Throughout, the fixed state is `theta*=(+1,...,+1)`, calibration is `alpha=0`,
the original query groups form a known fixed partition, and `1/2<=q<p<1`.
The unknown types are otherwise unrestricted. Utilities are
`U_i(theta)=b_i+v_i^T theta`. All statements of zero or positive premium concern
the asymptotic online coefficient `K_f-K_or,f`. They do not assert finite-budget
savings. The numerical illustration fixes `p=4/5,q=3/5`.

## 1A. Unequal-weight two-item example below saturation

Use four coordinates and the integer catalogue proposed during the parent
derivation:

| Item | b | v1 | v2 | v3 | v4 |
|---|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | -7 | 5 | 4 | 2 | 1 |

The utility difference is odd at every sign vector, so the winner is unique
at all 16 states. The exact winner counts are `(13,3)`. At `theta*`, item 1
wins with utility 5, and

\[
 \mathcal H_{2u}=\{1,2,34\},\qquad \rho_{2u}=1/3.
\]

These three disjoint sets must each receive at least `rho` of unit mass,
so `rho<=1/3`. Weights `(1/3,1/3,1/3,0)` attain the bound; dual weights
`(1/3,1/3,1/3)` give coordinate load `1/3` everywhere. The entire normalized
oracle face is

\[
 w_1=w_2=1/3,\qquad w_3+w_4=1/3,\qquad w_3,w_4\ge0.
\]

All four coordinates are globally relevant. Starting at `theta*`, flipping
1 or 2 changes item 1 to item 0. Starting at the state with only 4 flipped,
flipping 3 changes the winner; interchanging 3 and 4 gives its witness for
coordinate 4. Thus an unused coordinate in one optimal allocation is not a
globally irrelevant coordinate.

At zero calibration the premium is zero **if and only if one sharing group
contains coordinates 1 and 2 and at least one of 3 and 4**. If such a group
exists, choose an oracle-face weight supported there; the one sampled group
has the same minimum `psi_p(1/3)` for preserved or reversed candidate type.

For necessity, every equality allocation must be good-only and on the
displayed oracle face. If 1 and 2 are in distinct groups, the group containing
1 has positive mass strictly below one; set `F=1` has positive flip fraction
in that group and zero in its complement. Fitting the two blocks separately
strictly lowers information below `psi_p(1/3)`, by the strict concavity
argument proved explicitly in Section 2. If 1 and 2 share a group but neither
3 nor 4 is in it, that group's mass is `2/3` and the same argument applies.
Compactness then gives a strict cost gap.

In particular, `(123,4)` has **zero premium**, whereas `(12,34)` has a
**strictly positive premium**. For the latter, against `F=1`, use opposite
candidate types and fit the groups at `(v,u)=(1/2,p)`. Every oracle allocation
then has per-unit-mass information `(2/3)B_p<psi_p(1/3)`. The oracle
coefficient is `1/psi_p(1/3)`, not `1/B_p`.

## 1B. Unequal-weight two-item control above saturation

Use five coordinates and the integer catalogue

| Item | b | v1 | v2 | v3 | v4 | v5 |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 3 | 2 | 2 | 1 | 1 |

`U_1` is an odd integer at every sign vector, so the winner is unique at all
32 states. The exact winner counts are `(16,16)`. At `theta*`, item 1 wins.
Writing `12` for `{1,2}`, the minimal decision-changing flip family is

\[
 \mathcal H_2=\{12,13,234,235,145\}.
\]

Indeed, a flip changes the winner exactly when the flipped weight is at least
5. The minimal sets have different cardinalities; this is a weighted decision
map rather than the equal-weight threshold family of Theorem C. In particular,
neither a positive rescaling nor a coordinate permutation produces the
all-`r`-subsets geometry at this state.

All coordinates are globally relevant. In the following table, first flip
the listed set `F` from `theta*`, then flip coordinate `j`; the winner changes
from 1 to 0.

| j | F before flipping j |
|---:|---|
| 1 | 2 |
| 2 | 1 |
| 3 | 1 |
| 4 | 23 |
| 5 | 23 |

### Exact fractional cover

The primal weight and a dual distribution, in the displayed order of
`H_2`, are

\[
 w=\tfrac19(3,2,2,1,1),\qquad
 \lambda=\tfrac19(1,1,2,2,3).
\]

Every set has `w(F)=5/9`, and every coordinate has dual inclusion load `5/9`.
Both vectors are nonnegative and sum to one. For any coordinate distribution
`w'`,

\[
 \min_F w'(F)\le\sum_F\lambda_F w'(F)
 =\sum_j w'_j\Pr_\lambda(j\in F)=5/9.
\]

Hence the exact value is `rho_2=5/9`, with no floating-point premise.
Theorem A gives `K_or,2=1/B_p`, where `B_p=D(p,1/2)`.

### Same group sizes, different premium

For partition `S=(12,345)`, the restricted cover values are
`rho_{2,12}=1/2` and `rho_{2,345}=0`. On `12`, weights `(1/2,1/2)` give
coverage at least `1/2`; the disjoint requirements from `13` and `235`
give the matching upper bound. On `345`, set `12` is missed entirely.
Theorem B therefore proves **zero premium**.

For partition `S=(14,235)`, the values are `0` and `1/3`. Group `14` misses
`235`. Within `235`, requirements from `12`, `13`, and `145` reduce to
the three distinct singleton coordinates 2, 3, and 5. Equal weights attain
`1/3`, and their sum gives the upper bound. Theorem B proves a **strictly
positive premium**. Both partitions have group sizes `(2,3)`; a group-size
summary cannot distinguish them.

The zero-premium partition may also be refined to `(12,3,4,5)`: the globally
relevant singleton groups do not destroy its group certificate.

## 2. A genuine three-item catalogue with asymmetric overlapping demands

Use six coordinates and the integer catalogue

| Item | b | v1 | v2 | v3 | v4 | v5 | v6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | -6 | -4 | -4 | -2 | -2 | 0 |
| 2 | -1 | 0 | -2 | -2 | -4 | -4 | -8 |

The three utilities have distinct residues modulo 4: `0`, `2`, and `3`.
Thus there are no pairwise ties at any of the 64 states. The exact winner
counts are `(20,21,23)`: every item wins many states. In particular, item 2
is an actual competitor rather than an appended dominated item. At `theta*`,
the utilities are `(0,-18,-21)`, and item 0 wins.

With `x_j=1{j in F}`, the competitors' utilities after flipping `F` are

\[
\begin{aligned}
 U_1(\theta^F)&=-18+4(3x_1+2x_2+2x_3+x_4+x_5),\\
 U_2(\theta^F)&=-21+4(x_2+x_3+2x_4+2x_5+4x_6).
\end{aligned}
\]

Competitor 1 first exceeds item 0 on the five sets
`12,13,234,235,145`. Competitor 2 first exceeds item 0 on
`2345,236,46,56`; `2345` contains the already decision-changing sets
`234` and `235` and is removed when taking the global minimal family.
Consequently

\[
 \mathcal H_3=
 \{\underbrace{12,13,234,235,145}_{\text{item 1 wins}},
   \underbrace{236,46,56}_{\text{item 2 wins}}\}.
\]

The labels in the braces are the actual winners at those flipped states.
For example, `12` has utilities `(0,2,-17)`, whereas `46` has
`(0,-14,3)`. Both competitors contribute necessary minimal alternatives.
Their boundaries have different coordinate weights and overlapping
coordinate sets. The resulting certificate family mixes pairs and triples
and has nonuniform optimal sampling weights; it is not the old uniform
threshold geometry with an extra item attached.

Every coordinate is globally relevant. In this table, the pre-flip winner is
0; after flipping `j` it becomes the indicated competitor.

| j | F before flipping j | New winner |
|---:|---|---:|
| 1 | 2 | 1 |
| 2 | 1 | 1 |
| 3 | 1 | 1 |
| 4 | 23 | 1 |
| 5 | 23 | 1 |
| 6 | 23 | 2 |

### Exact fractional cover and its unique optimizer

In the displayed order of `H_3`, use

\[
\begin{aligned}
 w^*&=\tfrac1{13}(3,2,2,1,1,4),\\
 \lambda&=(2/13,2/13,3/26,3/26,1/13,0,5/26,5/26).
\end{aligned}
\]

The primal set coverages are
`(5,5,5,5,5,8,5,5)/13`. The dual vector sums to one and gives every
coordinate load `5/13`. The same primal-dual argument proves the exact value

\[
 \boxed{\rho_3=5/13<1/2,\qquad
 K_{\rm or,3}=1/\psi_p(5/13).}
\]

The optimum `w*` is unique. Every dual-positive set must be tight at any
optimum. Write `(a,b,c,d,e,f)` for its coordinate weights and
`r=5/13`. The tight pair equations imply `b=c` and `d=e`.
The tight triples give `2b+d=r` and `a+2d=r`, while `a+b=r`.
Thus `b=2d`, `d=r/5`, `a=3r/5`, and the tight set `46` gives `f=4r/5`.
These are precisely `(3,2,2,1,1,4)/13`. All six coordinates have positive
optimal mass. The active incidence equations have exact rank six, also
checked by rational elimination in the companion script.

### Exact premium boundary for this catalogue

At `alpha=0`, **the premium is zero if and only if all six coordinates
belong to one sharing group**. Theorem B is not being used here, because
`rho_3<1/2`.

Sufficiency is direct: with one group, put good-format coordinate mass
`K_or,3 w*` on the group. Whether the candidate type is preserved or
reversed, its sampled good stream is fitted by one rate at least one-half;
its minimum information is `K_or,3 psi_p(w*(F))>=1`.

For necessity, equality of online coefficients would require a good-only
oracle optimizer by Theorem A. Its normalized weights must be the unique
`w*`. Suppose a nonempty group is a proper subset `S` of the six
coordinates, and put `t=w*(S) in (0,1)`. There exists an active flip set `F`
such that the within-block flip fractions

\[
 s_1=\frac{w^*(F\cap S)}t,\qquad
 s_2=\frac{w^*(F\cap S^c)}{1-t}
\]

are different. Otherwise every active set would cover exactly `rho_3` of
the normalized restriction `w*|S/t`; the full-rank active equations would
force this restriction to equal the everywhere-positive `w*`, which is
impossible on a proper subset.

Assign `S` and its complement opposite candidate types so that the block
with the smaller flip fraction uses `u`, and the other uses `v`. This is an
allowed group-type reversal pattern even when the complement contains
several groups. Fit each block at
`max(1/2,p-(2p-1)s_i)`. Their order satisfies `u>=v`, so the fit is allowed.
The information per unit total good-format mass is

\[
 t\psi_p(s_1)+(1-t)\psi_p(s_2)
 <\psi_p(t s_1+(1-t)s_2)=\psi_p(5/13).
\]

The inequality is strict: the average is below one-half, the fractions
differ, and `psi_p` is strictly concave below one-half and constant after it.
Hence the unique oracle-cost allocation violates a valid alternative.
Continuity and the compact fixed-cost allocation simplex rule out an
approaching sequence at oracle cost, proving a strict coefficient gap.
This is an analytic exclusion argument for the full continuous program,
not a conclusion inferred from an optimizer's floating output.

A concrete fixed positive-premium partition is `S=(123,456)`. For the active
set `F=12`, the two block masses are `7/13,6/13`, and flip fractions are
`5/7,0`. Reversing the first group and fitting `(u,v)=(p,1/2)` leaves only
`(7/13)B_p` information per unit mass. This is strictly below
`psi_p(5/13)`. At `p=4/5`, the oracle-cost allocation has information
approximately `0.56673795` against this one allowed alternative.

## 3. Bounded continuous-program diagnostics

The following outputs use the existing `DecisionProgram` inner isotonic
Bernoulli fit and cutting-plane outer LP, after replacing its threshold flip
family by the explicit catalogue family. All type-reversal patterns are
included. Every returned inner optimum is also checked independently with
SLSQP. The two reported cost columns are floating diagnostics, **not formally
certified lower/upper intervals**. Exact zero/positive claims above come from
the analytic arguments.

| Catalogue and fixed partition | Oracle coefficient | Outer LP cost | Repaired feasible-cost diagnostic | Outer iterations |
|---|---:|---:|---:|---:|
| Two items below saturation, `(123,4)` | 5.79343249 | 5.79343249 | 5.79343249 | 4 |
| Two items below saturation, `(12,34)` | 5.79343249 | 9.55361162 | 9.55361164 | 26 |
| Two items above saturation, `(12,345)` | 5.18820857 | 5.18820857 | 5.18820858 | 22 |
| Two items above saturation, `(14,235)` | 5.18820857 | 5.73020642 | 5.73020642 | 5 |
| Three items, `(123456)` | 5.46065866 | 5.46065866 | 5.46065866 | 4 |
| Three items, `(123,456)` | 5.46065866 | 9.21964890 | 9.21964892 | 39 |

Parameters are `p=.8,q=.6,alpha=0`. Maximum absolute discrepancies between
analytic and independent numerical inner fits were respectively
`5.1e-12,5.7e-14,6.7e-16,1.4e-13,6.7e-15,3.6e-13`. The largest pre-repair information
deficit was below `1.9e-9`. The three-item positive case uses some other-format
mass in its computed optimum; its larger cost is not being computed by
restricting the unknown-type learner to good formats.

Reproduce the exact cube, relevance, cover, rank, and restricted-cover checks:

```bash
python research/general_catalogue_theory_20261103/catalogue_examples_search.py
```

Add `--continuous` to rerun the six continuous-program diagnostics. The
script visits only the explicitly specified 16-, 32-, and 64-state cubes; it does
not perform a large catalogue search. It prints its outputs and does not
write result files.
