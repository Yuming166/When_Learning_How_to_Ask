# Decision certificates and the cost of learning how to ask

Date: 2026-11-03. Status: analytic derivations under the stated model, with
separately scoped same-family derivation/review and bounded deterministic
checks. Not external peer review, a formal proof-assistant certificate, or a
completed novelty assessment. The published manuscript is unchanged.

## 1. Model and what actually changes

Keep `Theory_Note.md`'s fixed binary preferences, known partition
`S=(S_1,...,S_G)`, arbitrary fixed unknown types `z_g`, and globally unknown
levels `1/2<=q<p<=1-eta`. No prior distribution or cross-group restrictions on
`z` are imposed. A unit-cost query `(j,m)` returns a fresh binary answer with
accuracy `p` for the group's better form and `q` for its other form. Conditional
on the state, all task and reference observations are independent. The two
labelled reference streams each contain `M_delta` observations; let
`R=log(1/delta)` and `M_delta/R -> alpha<infinity`.

Instead of recovering every preference, return

\[
 f(\theta)=\arg\max_{i\in\mathcal C}(b_i+v_i^\top\theta).
\]

The catalogue is finite and known, with a unique winner at every allowed sign
vector. Correctness is uniform over the same original state domain and
includes calibration randomness. The oracle learns `z` only, not `p,q` or
`theta`, and receives the same reference streams. Dedicated type questions,
whole-profile disclosures, unequal task costs, persistent errors and unknown
groups are absent here. Total acquisition cost remains `2M_delta+E tau`.

For a true state, let `theta^F` flip exactly the coordinates in `F`, and define

\[
 \mathcal H_f(\theta)=\min_{\subseteq}
 \{F\subseteq[d]:f(\theta^F)\ne f(\theta)\}.
\]

This is the family of minimal decision-changing flip sets. It is a standard
certificate/sensitive-block construction, not a newly invented object. The
full-preference problem has every singleton as a minimal flip set. A general
recommendation need not.

If the catalogue has the same winner at every state, the decision is constant
and both optimal online coefficients are zero: no task query is needed. All subsequent
positive-coefficient results assume `H_f(theta)` is nonempty, equivalently
that the decision map is nonconstant on the allowed sign space.

## 2. Decision information program and a correct stopping target

Orient forms by the true type for analysis only, with good/other counts
`a_j,b_j`. This orientation is not given to a query algorithm. For a reversed
type set `J`, let `x_g=u,y_g=v` when `g notin J`, and `x_g=v,y_g=u` otherwise.
For a flip set `F`, define

\[
 I_{F,J}(a,b)=\inf_{1/2\le v\le u\le1-\eta}
 \left\{\alpha[D(p,u)+D(q,v)]
 +\sum_j\left[a_jD(p,x_{g(j)}^{[j\in F]})
              +b_jD(q,y_{g(j)}^{[j\in F]})\right]\right\},
\]

where `x^0=x`, `x^1=1-x`, and `D` is Bernoulli KL. Set

\[
 K_f=\min_{a,b\ge0}\left\{\sum_j(a_j+b_j):
 I_{F,J}(a,b)\ge1\quad\forall F\in\mathcal H_f,\ J\subseteq[G]\right\}.
 \tag{1}
\]

The oracle coefficient restricts `J` to the empty set. For candidate rates at
least one-half,

\[
 D(r,1-x)-D(r,x)=(2r-1)\log\frac{x}{1-x}\ge0.
 \tag{2}
\]

Every wrong recommendation contains a minimal wrong-decision flip set, and
deleting other flips can only reduce information. Thus (1) accounts for every
wrong recommendation, including ones requiring several simultaneous flips.
The single-flip reduction from full recovery cannot simply be reused.

**Framework proposition.** Under the original ideal real-arithmetic,
vanishing-actual-error tracking contract, fixed dimension and fixed true
nonzero gaps,

\[
 \inf_{\pi\;\mathrm{uniformly}\;\delta\mathrm{-correct}}
 E_h\tau_\pi=K_f R+o(R).
 \tag{3}
\]

This is a specialization of established controlled sensing / structured pure
exploration. The contribution sought below is the structure of (1), not the
generic framework.

**Proof details for the specialization.** Stopped-transcript KL is
`M_delta[D(p,u)+D(q,v)]` plus expected action counts times their KLs. The event
of returning the true item gives the usual `kl(1-delta,delta)` lower bound for
every wrong-item alternative. For attainment, the original forced-only
estimator identifies the finite signs/types and the common rates, with error
tails exponential in `sqrt(t)`. Track approximate solutions of (1) with actual
errors vanishing uniformly in `delta`, using cumulative-target discrepancy
`O(sqrt(t))` and update ages `O(sqrt(t))`.

The positive-online-margin step survives the changed goal. For any minimal
wrong-decision `F`, the same-type alternative at the true rates forces

\[
 \sum_{j\in F}[a_jD(p,1-p)+b_jD(q,1-q)]\ge1.
\]

Every candidate wrong decision has flipped observations with probability of
the true sign at most `1/2`. Therefore its online information is bounded below
by a fixed positive multiple of the displayed quantity; omit the zero-over-zero
`q=1/2` term. Local continuity and compact optimizer-set tracking follow from
the all-task strict-feasibility repair direction, as in the original addendum.
Jointly center the offline and online likelihood increments, use a compact rate
net and the forced-sample concentration event. For fixed `epsilon>0`, this gives

\[
 \Pr_h(\tau>t)\le Ct^A e^{-c\sqrt t},\quad
 t\ge(K_f+\epsilon)R,
\]

uniformly over sufficiently small `delta`. Its sum is `o(R)`. This proof uses
the repaired joint concentration argument, not a permanently conditioned
good-calibration event. Fixed numerical tolerances do not establish (3) for a
particular implementation.

### A decision-level GLR

Let

\[
 \Lambda_t(i)=\sup_{h:f(\theta)=i}L_t(h),\qquad
 \widehat i_t\in\arg\max_i\Lambda_t(i).
\]

Stop when

\[
 \log\Lambda_t(\widehat i_t)-\max_{i\ne\widehat i_t}\log\Lambda_t(i)
 \ge R+2\log(M_\delta+1)+\sum_{e\;\mathrm{online}}\log(N_e(t)+1).
 \tag{4}
\]

A saturated Beta-mixture likelihood ratio initialized before calibration
proves the anytime `delta` error bound exactly as for full recovery: on a wrong
output, the true likelihood belongs to a competing item class.

On the same coupled observation path and threshold, the decision GLR gap is
at least the full-profile GLR gap. The numerator is the same global maximum;
the competing-item set excludes same-item alternative profiles. Consequently

\[
 \tau_{\mathrm{decision}}\le\tau_{\mathrm{profile}}
 \tag{5}
\]

pathwise for fixed query actions up to stopping. This does not assert a strict
improvement on every history, or optimality of any specific question allocator.

## 3. General oracle geometry when alpha=0

For `0<=s<=1`, put

\[
 B_p=D(p,1/2),\qquad
 \psi_p(s)=H(\max\{1/2,p-(2p-1)s\})-H(p).
\]

The function is strictly increasing and concave below `1/2`, then constant at
`B_p`. It is the exact minimum of
`(1-s)D(p,u)+sD(p,1-u)` over candidate `u>=1/2`. Define

\[
 \rho_f=\max_{w\in\Delta_d}\min_{F\in\mathcal H_f}w(F).
\]

For Boolean decisions, `1/rho_f` is the established fractional certificate
complexity at the instance. No priority claim is made for this combinatorial
quantity.

**Theorem A (unknown-rate oracle formula).** At `alpha=0`,

\[
 \boxed{K_{\mathrm{or},f}=1/\psi_p(\rho_f).}
 \tag{6}
\]

Every oracle optimum uses only true good formats. Its complete normalized
coordinate optimal set consists of weights with

\[
 \min_{F\in\mathcal H_f}w(F)\ge\min\{\rho_f,1/2\}.
 \tag{7}
\]

**Proof.** Let `lambda=(2q-1)/(2p-1)<1`. A binary symmetric channel with that
contraction maps `p` to `q` and a candidate `u` to
`v=1/2+lambda(u-1/2)<=u`, including their sign complements. Data processing
therefore bounds every other-form divergence by the corresponding good-form
divergence at `(u,v)`. Aggregate both query formats' weights coordinatewise.
For their least covered `F`, choose
`u=max(1/2,p-(2p-1)w(F))`. The mixed allocation's information is no larger than
`psi_p(w(F))<=psi_p(rho_f)`. Good-only sampling at a maximizing weight vector
attains this value. If any bad-format weight were positive in an optimum,
the displayed BSC contraction would be strict at the minimizing `u<p`,
contradicting optimality. The capped function then gives (7). `square`

For a separately labelled known-rate control, the oracle coefficient is
`1/[D(p,1-p)rho_f]`. It must not replace (6) in an information-matched comparison.

**Theorem B (group certificates in the saturated regime).** If
`rho_f>=1/2`, define the restricted cover value

\[
 \rho_{f,g}=\max_{w\in\Delta(S_g)}\min_{F\in\mathcal H_f}w(F).
\]

Then

\[
 \boxed{K_f=K_{\mathrm{or},f}
 \iff\max_g\rho_{f,g}\ge1/2.}
 \tag{8}
\]

**Proof.** Equality requires a good-only oracle optimum, with total cost
`1/B_p`. If some used group has less than half of its weight flipped by some
wrong decision, fit that group at
`u=p-(2p-1)w(F intersect S_g)/w(S_g)>1/2`, and every other group at `v=1/2`.
An allowed type-reversal pattern realizes these two assignments and makes its
total information strictly less than `B_p`. Thus each used group's normalized
weights must itself cover every decision-changing set by at least half. There
must be a group with `rho_{f,g}>=1/2`. Conversely, put all weight in such a
group. Every wrong decision reverses at least half that group's sampled mass,
whichever candidate rate its type uses; its information is minimized at
`1/2` and equals `B_p`. `square`

This replaces a global group-size statistic by a decision-specific group
certificate. Outside the stated saturated regime, (8) is not claimed.

## 4. A complete threshold-catalogue theorem at alpha=0

Use two candidate items with known utility difference

\[
 U_1(\theta)-U_0(\theta)=\sum_{j=1}^d\theta_j+d-2t+1,
 \qquad 1\le t\le d.
 \tag{9}
\]

The first item wins iff at least `t` preferences are positive, with no ties.
For either true winner, define its supporting index set `P` and effective
threshold `tau` as follows:

| Winner | P | tau |
|---|---|---|
| 1 | positive coordinates | t |
| 0 | negative coordinates | d-t+1 |

Let `n=|P|`, `r=n-tau+1`, and `k_g=|P intersect S_g|`. A recommendation changes
only after some `r` supporting coordinates reverse. The minimal flip family
contains every `r`-subset of `P`. Unselected coordinates and groups remain
available query actions throughout the proof.

**Theorem C (threshold recommendation boundary).** At `alpha=0`,

\[
 K_{\mathrm{or}}=\frac1{\psi_p(r/n)},\qquad
 \boxed{K=K_{\mathrm{or}}
 \iff \max_g k_g\ge\min\{n,\max\{1,2(\tau-1)\}\}.}
 \tag{10}
\]

**Proof.** The fractional cover value of all `r`-subsets of `P` is `r/n`,
attained uniformly on `P`; use Theorem A. If `r/n<1/2`, oracle optimality
strictly excludes nonsupporting coordinates and forces equal good-format
weights on `P`, by exchanging members of `r`-subsets. If `P` occupies two
groups, some `r`-subset has different flip fractions in the two groups.
Fit them separately at their clamped empirical means, assigning their types
to respect `u>=v`. Strict concavity of `psi_p` below one-half gives strictly
less information than the oracle. Thus all `n` supporters must share a group;
that condition also suffices.

If `r/n>=1/2`, Theorem B applies. For a group containing `k` supporters,
uniform weights there have least flipped fraction
`max(0,k-(tau-1))/k`; no other weights can improve this minimum, by averaging
over omitted supporter subsets. It reaches one-half iff
`k>=max(1,2(tau-1))`. This proves (10), including the equality boundary. Nonsupporting
coordinate weights can be oracle-optimal in the saturated regime, but cannot
make a smaller group meet the condition. `square`

The minimum is a threshold on the **largest supporting group**, not the
smallest original group. The full-preference theorem is recovered when
`P=[d]` and `r=1`. More generally, `r=1` recovers the full-recovery subproblem
on supporting coordinates with their induced partition, rather than the
entire original profile.

## 5. Positive calibration: an exact active-group boundary

Let `alpha>0` be fixed and finite. Define

\[
 F_{n,r}(p,u)=rD(p,1-u)+(n-r)D(p,u).
\]

Let `a>0` be the unique root

\[
 \inf_{1/2\le v\le u\le1-\eta}
 \{\alpha[D(p,u)+D(q,v)]+aF_{n,r}(p,u)\}=1.
 \tag{11}
\]

For `k>=r` put

\[
 v_{k,r}=\max\left\{\tfrac12,
 \frac{\alpha q+a[r+(k-2r)p]}{\alpha+ka}\right\},\qquad
 \Gamma_{k,r}=\alpha D(q,v_{k,r})+aF_{k,r}(p,v_{k,r}).
 \tag{12}
\]

Ignore zero intersections only when defining
`k_min^+=min{k_g:k_g>0}`; the original query actions are not deleted.

**Theorem D (finite-calibration threshold).** For (9),

\[
 K_{\mathrm{or}}=na,
 \qquad
 \boxed{K=K_{\mathrm{or}}
 \iff k_{\min}^+>r\ \text{and}\ \Gamma_{k_{\min}^+,r}\ge1.}
 \tag{13}
\]

Thus the finite-calibration threshold depends on supporters and the number of
preference reversals needed to change the recommendation. It is not a formula
in the smallest original sharing group.

**Proof.** Average oracle alternatives over all `r`-subsets of `P` at a
minimizing pair `(u*,v*)` in (11). The supporting coefficient of a good-format
query on `P` is `F_{n,r}(p,u*)/n`. Every bad-format coefficient is strictly
smaller: `u*<=p`, `v*=min(q,u*)`, and the derivative in the true rate of
`D(s,u*)+(r/n)(2s-1)logit(u*)` is positive between `q` and `p` when `u*<=q`;
when `u*>q`, monotonicity yields the same strict comparison. Nonsupporting
good-format coefficients are strictly smaller unless `u*=1/2`.
This proves the oracle value in (11) and excludes every bad-format optimum.

If `u*=v*<=q`, reverse every group's type, keep `v=u*`, and set `u=p`.
Every sampled good-form likelihood is unchanged, while calibration KL falls
by `alpha D(p,u*)>0`. Hence no oracle optimum is feasible with unknown types.
This includes `u*=1/2`, even when nonsupporting coordinates can be optimal.

Otherwise `u*>q`. If `r<n`, every oracle optimum is uniquely uniform on `P`:
nonsupporters are excluded, and equality of every binding `r`-subset sum
forces equal weights. When `r=n`, any good-only allocation on `P` can be
optimal; reversing a used group strictly reduces its flipped-sign information
from `D(p,1-u*)` to `D(p,1-q)`, so all such allocations still fail.

For `r<n`, if a group has `1<=k<=r` supporters, choose a wrong decision that
flips all of them and reverse that group's type. The same strict reduction
violates optimal-cost feasibility. If all nonempty supporting groups have
`k>r`, consider an arbitrary reversed-group set containing `k` supporters and
an alternative flipping `f` of those `k`. Moving a flip from the unreversed
set into the reversed set changes KL by
`a(2p-1)[logit(v)-logit(u)]<=0`. The worst case therefore puts all `r` flips
inside the reversed set. All other coordinates are unchanged and fit at
`u=p`; the remaining information is exactly `Gamma_{k,r}`. These values are
nondecreasing in `k`, since each added supporter adds `aD(p,v)>=0`.
The least nonempty reversed set has size `k_min^+`, proving (13). In the
excluded pooling case, `Gamma_{n,r}<1`, so (13) cannot accidentally certify
equality there. Closed feasible sublevels and exclusion of every oracle
optimizer give a strict cost gap when the criterion fails. `square`

The `alpha=0` and `alpha>0` criteria must be stated separately. The coefficients
are continuous in calibration, but equality versus a strictly positive gap
can change immediately at zero; this is not a discontinuity in total cost.

## 6. Explicit consequences and controls

### 6.1 A singleton group need not create a recommendation premium

Take majority among five preferences, all positive. Then `n=5,tau=3,r=3`.
At `alpha=0`, Theorem C requires a group of at least four supporters.
Partition `(4,1)` has zero premium; `(3,2)` has a strictly positive one.
All five preferences are globally relevant to this catalogue. This is not
obtained by adding a dummy coordinate to a one-bit decision.

At `p=.8,q=.6`, numerical coefficients are approximately

| Partition | Unknown type | Type-only oracle |
|---|---:|---:|
| (4,1) | 5.18821 | 5.18821 |
| (3,2) | 5.73021 | 5.18821 |

These multiply `log(1/delta)` and are not finite-budget accuracy or savings.

### 6.2 Positive-OR has a particularly sharp calibration boundary

For `t=1` and at least one positive preference, every finite-calibration
decision program reduces exactly to the single-bit program. Aggregating all
good/other counts and testing the all-type-preserved and all-type-reversed
alternatives proves the lower bound using (2); concentrating on one positive
coordinate proves the upper bound. Therefore, for every partition,

\[
 K_{\mathrm{OR},0}=K^{\mathrm{or}}_{\mathrm{OR},0}=1/B_p,
 \qquad
 K_{\mathrm{OR},\alpha}>K^{\mathrm{or}}_{\mathrm{OR},\alpha}
 \quad(\alpha>0).
 \tag{14}
\]

At the all-negative OR state, minimal wrong decisions are singleton flips, so
the full-recovery information problem returns. The same catalogue can thus
have different reliability-sharing requirements at different user profiles.
See `OR_DERIVATION.md` for the full finite-alpha proof.

### 6.3 Quantified strict premium, not just a numerical gap

For majority-3 at `theta=(+,+,+)`, singleton groups, `alpha=0`, `p=4/5,q=3/5`,
let `A,B` be total good/other counts, `B_p=D(p,1/2)`, `B_q=D(q,1/2)` and
`W=D(q,1-p)`. Necessary constraints from `(u,v)=(1/2,1/2)` and the average of
the three pair-flip / matching type-flip alternatives at `(u,v)=(p,1/2)` are

\[
 B_p A+B_q B\ge1,\qquad
 \frac23B_p A+\frac{2W+B_q}{3}B\ge1.
\]

Their two-variable LP dual gives

\[
 \frac{K}{K_{\mathrm{or}}}
 \ge1+\frac{B_p-B_q}{2W-B_q}>1.23.
 \tag{15}
\]

The dual weights are positive at these rational parameters. Exact rational
log-series enclosures establish the last inequality; see
`exact_certificates.json`. The numerical optimum ratio is larger; (15) is a
proved lower bound, not an exact optimum claim.

### 6.4 The catalogue is not an isolated equal-weight point

Perturb (9) to utility difference `b+sum_j a_j theta_j`. If

\[
 |b-(d-2t+1)|+\sum_j|a_j-1|<1,
 \tag{16}
\]

every sign vector has exactly the same unique winner as before: the original
utility difference is an odd integer with absolute value at least one, and
the perturbation is uniformly smaller than one. All the information programs
and structural conclusions above are unchanged on this nonempty open
catalogue-parameter region. The rate conditions also cover their stated
nondegenerate range. This does not extend an alpha=0 statement to an open
calibration interval; (14) explicitly rules that shortcut out.

### 6.5 A useful failed mechanism

Under this equal-cost symmetric global-rate model, coordinates absent from
every minimal decision-changing set cannot strictly improve the optimal
first-order coefficient as calibration probes. Transfer their good/other
mass to a critical coordinate in the same group when available. For an empty
critical group, match its alternative type to that of the recipient group.
Equation (2) makes every transferred observation at least as informative,
while preserving cost and the labelled calibration penalty.

Such coordinates may carry positive mass in a nonunique optimum, but they are
not essential to achieving its cost. This is different from being outside one
particular chosen certificate. Cheap special probes, heterogeneous channels
or constraints on the type vector could change the conclusion, and are not
assumed here. See `INDEPENDENT_DERIVATION.md`.

## 7. What this establishes for the paper

The new candidate contribution is the decision-specific reliability boundary,
especially (10) and (13), its certificate explanation, and the change from
full-profile stopping to (4). They are not statements present in the original
full-recovery Theorems 1--3. Generic identification, fractional certificates
and tracking remain attributed prior machinery. The task is a restricted
two-item recommendation model, not a general catalogue ranking theorem.

Any subsequent method comparison must give every baseline the same top-1 goal,
decision-level stopping opportunity, observations and costs. Saving queries
relative to a baseline forced to reconstruct every preference is a comparison
of different tasks, not evidence of superiority over strong recommendation
baselines.

No natural-user or LLM reliability model has been validated. There are no new
model responses, online agent trajectories or method-effectiveness claims.
The shared symmetric channel, fixed preferences, known grouping and labelled
calibration remain substantial assumptions. Novelty beyond the bounded
primary-source comparison and external mathematical review remain open.
