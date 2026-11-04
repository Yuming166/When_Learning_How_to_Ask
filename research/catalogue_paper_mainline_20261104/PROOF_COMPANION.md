# Compact proof of the catalogue premium boundary

Date: 2026-11-04. This companion restates and proves the structural result under
the audited local model. It changes no frozen theorem or executable policy.
It is not a priority claim or formal proof-assistant certificate.

## Definitions and theorem

Fix a nonconstant finite-output decision map `f` on the full sign cube, a true
profile theta, known groups `S_g`, and common true rates
`1/2 <= q < p <= 1-eta`. Let H contain the inclusion-minimal nonempty flip sets
that change f(theta). There are no direct type reports, all questions cost one,
and labelled calibration per stream is `o(log(1/delta))`. Write

\[
 \rho=\max_{w\in\Delta_d}\min_{F\in H}w(F),\qquad
 \psi(s)=h(\max\{1/2,p-(2p-1)s\})-h(p).
\]

For good-format weights w, a group subset A, and a wrong flip F, set

\[
 W=w(\cup_{g\in A}S_g),\quad
 T=w(F\cap\cup_{g\in A}S_g),\quad t=w(F),
\]

\[
 E_{F,A}(w)=W\psi(T/W)+(1-W)\psi((t-T)/(1-W)).
\]

A zero-mass pool contributes zero. Let K be the unknown-format information
coefficient and K_or the coefficient when only the true group format types
are disclosed. Then

\[
 K_{or}=1/\psi(\rho),\qquad
 K=K_{or}\iff\exists w\in\Delta_d:
     E_{F,A}(w)\ge\psi(\rho)\quad\forall F\in H,A\subseteq[G].
\]

The test is finite convex feasibility and its zero/positive outcome does not
depend on q. If `rho<1/2` and the max-cover optimizer `w*` is unique, equality
holds iff `supp(w*)` lies in one sharing group.

## Proof

**1. Only minimal wrong flips are needed.** For `r,x>=1/2`,

\[
 D(r,1-x)-D(r,x)=(2r-1)\log[x/(1-x)]\ge0.
\]

Every wrong flip set contains a minimal wrong subset, and its extra flips
only increase divergence at any fixed candidate types/rates. This remains
true after taking the candidate-rate infimum. The decision map itself need
not be monotone.

**2. Oracle formula and strict good-only necessity.** Let the total query mass
be C, and normalize total per-coordinate mass from both formats to w. Put
`s=min_F w(F)`. Feasibility implies `s>0`: otherwise a same-type true-rate
alternative flips an unqueried wrong set without changing any data. For a
least-covered F choose

\[
 u=\max\{1/2,p-(2p-1)s\},\quad
 \lambda={2q-1\over2p-1}\in[0,1),\quad
 v=1/2+\lambda(u-1/2).
\]

The binary symmetric channel with contraction lambda maps Bernoulli p to q
and Bernoulli u to v, also mapping their complements. Data processing bounds
each other-format divergence by its good-format counterpart at these candidate
rates. Since `s>0`, `u<p`; the compared input distributions differ both on
unchanged and flipped coordinates. The contraction has overlapping output
support (or is constant when lambda=0), so its KL inequality is strict. Thus
any positive other-format mass gives total information strictly less than
`C psi(s) <= C psi(rho)`. No oracle-optimal allocation can use it.

For good-only normalized weights, the exact oracle rate fit gives information
`min_F psi(w(F))`; maximizing this expression yields `psi(rho)`. Consequently
`K_or=1/psi(rho)` and every optimum is good-only. Below saturation, strict
increase of psi gives the complete coordinate optimizer set

\[
 \mathcal W=\{w\in\Delta_d:w(F)\ge\rho\quad\forall F\in H\}.
\]

For completeness, above saturation the optimizer condition is minimum cover
at least one half, not necessarily the maximum cover rho.

**3. Eliminate candidate rates at oracle cost.** In a pool with total sampled
mass W and flipped fraction s, candidate rate x contributes

\[
 W[(1-s)D(p,x)+sD(p,1-x)].
\]

Its minimum over `x>=1/2` is `W psi(s)`, attained in the closed domain at
`max(1/2,p-(2p-1)s) <= p <= 1-eta`. A candidate type pattern partitions groups
between two common-rate pools. For any partition, independently fit those two
pools; assign the larger fitted value to the high candidate rate and choose
the corresponding allowed type labels. Therefore minimization over all types
and ordered rates is exactly `min_A E_F,A(w)`. This uses two fitted rates,
not one per group.

Any unknown-format allocation of cost K_or is also oracle feasible, hence by
step 2 is good-only. At that cost it is feasible exactly when the displayed
entropy inequalities hold. Conversely a weight satisfying those inequalities,
scaled by K_or, is unknown-format feasible. This proves the iff criterion.
Closed constraints, finite feasible cost from all-task sampling, and compact
bounded cost sublevels ensure that the optimum is attained; infeasibility at
K_or therefore means `K>K_or`, rather than unattained equality.

The alternative closure including equal rates has the same infimum as strict
candidate rates: it is their closure, all relevant probabilities stay bounded
away from zero/one, and KL is continuous. True instances still require p>q.

**4. Unique-cover corollary.** Suppose rho<1/2 and w witnesses equality. The
unsplit pool shows `w in W`. If a binding F has `w(F)=rho`, every group split
has weighted mean flip fraction rho. Unequal nonempty pool fractions give
strict Jensen loss for psi: an interior part of their interval lies below
one half, where psi is strictly concave. Thus every used group obeys

\[
 w(F\cap S_g)=\rho w(S_g)
 \quad\text{for every binding }F.
\]

Let `v_g=w|S_g/w(S_g)` for each used group, and `d_g=v_g-w`. These directions
preserve normalization, all binding cover constraints, and every zero
coordinate of w. Small positive and negative steps preserve the finitely many
slack inequalities and positive coordinates. Hence they lie in the tangent
space of w's minimal face in W. The v_g have disjoint supports; their
differences span dimension L-1 when L groups are used, since their sole linear
dependence is `sum_g w(S_g)d_g=0`. Therefore

\[
 L-1\le\dim(face_{\mathcal W}(w)).
\]

If the cover optimizer is unique, this dimension is zero, so only one group
can be used. Conversely, a max-cover weight supported in one group faces only
one sampled candidate rate regardless of the type label; its wrong-decision
information is `psi(w(F))>=psi(rho)`. This proves sufficiency and the corollary.
`QED`.

## Framework interpretation and executable limit

Under the ideal forced-only, vanishing-actual-error tracking contract and
decision-class GLR stopping, the usual stopped-transcript lower bound and the
repaired summable-tail proof identify these as leading expected online costs.
For the decision specialization, the needed positive online margin follows
from same-type true-rate constraints on every minimal F and the ratios

\[
 \min_{r\in\{p,q\}:r>1/2}{D(r,1/2)\over D(r,1-r)}>0.
\]

Every wrong decision contains such an F and receives that positive margin.
This replacement is enough for local optimizer stability and the original
joint offline/online concentration proof. The practical fixed-tolerance,
all-task-MLE allocation has not established this stronger implementation
contract. Its conservative item-level stopping certificate can remain valid
without an asymptotic allocation-optimality claim.
