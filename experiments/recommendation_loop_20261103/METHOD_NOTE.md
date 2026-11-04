# Observable recommendation elicitation: method and theorem boundary

Date: 2026-11-03. This is a controlled implementation note, not a revision of
the historical manuscript or a proof of a new allocation theorem.

## Decision target

The public catalogue defines affine utilities

\[
U_i(\theta)=b_i+\sum_{j=1}^d a_{ij}\theta_j,
\qquad i^*(\theta)=\arg\max_i U_i(\theta).
\]

The target is the unique best item, rather than every sign in the user profile.
Two profiles that recommend the same item belong to the same terminal class.
The public catalogue must have a unique winner at every binary profile.

An action asks preference coordinate \(j\) in format \(m\in\{0,1\}\).
Known groups share an unknown better format \(z_g\). Conditional on the fixed
latent state, fresh replies are independent, with correctness probability
\(p\) for \(m=z_{g(j)}\) and \(q\) otherwise. Policies do not know
\(\theta,z,p,q\). There are no calibration or direct-type actions in this
first implementation. All task actions cost one.

## Loop

1. **Infer.** Enumerate the bounded binary preference/type states and fit the
   two continuous rates on the ordered closure
   \(1/2\le q\le p\le1-\eta\). Pool the empirical rates if their ordering
   reverses. This is a joint all-data MLE, not a posterior. Sign-mask bit one
   means a negative sign; raw reply one means a positive sign.
2. **Allocate toward the decision.** At the fitted sign state, enumerate
   inclusion-minimal sign flips whose catalogue winner differs. The numerical
   information program protects against these decision alternatives, every
   type reversal and continuously re-fitted alternative rates. Map the
   oriented allocation through the fitted group types. Its query weights are
   an approximate float solution at logged fixed tolerance.
3. **Track and explore.** Track cumulative allocation deficits. At
   \(t=2d n^2+s\), \(0\le s<2d\), force action \(s\). Update targets at
   \(t+\max(2d,\lceil\sqrt{t+1}\rceil)\). When the fitted gap is at most
   \(10^{-8}\), use and log a uniform two-format target. No hidden rate is
   substituted for an unidentified fit. A failed planner is a recorded failure.
4. **Certify the recommendation.** Maximize the likelihood over every profile
   and type producing each item, then over the continuous rates. Use rational
   MLEs and outward log intervals to test the strict decision gap against
   \(R+\sum_{j,m}\log(N_{jm}+1)\). Only an interval-confirmed pass permits
   output. Otherwise continue, or report uncertified at the cap.

A cheap common screen requests exact checking near the threshold, with
additional checks every 50 answers and at the cap. The screen never certifies.
The implemented stopping time can be later than the earliest ideal GLR crossing.

## Fair comparisons

All arms share observations, action costs, the recommendation certificate and
the screening/checkpoint schedule. The joint D-RRC adaptation and both KL
allocators share the estimator, forced schedule, update cadence and tracker.
Profile KL changes only the allocation alternative family to singleton
wrong-profile flips; it still uses recommendation stopping. This is an
allocation-goal ablation, not a profile-versus-decision stopping ablation.

The strong IG baseline greedily maximizes information about the best item,
using a full joint preference/type/rate posterior approximated by order-six
Gauss–Legendre quadrature. Uniform sign/type priors and a uniform ordered-rate
prior are explicit in `IG_NOTE.md`. It updates after every answer. The final
comparison uses its scale-invariant repaired tie rule; `policies.py` retains
the frozen historical pilot rule. IG and KL differ in both inference and
allocation, so their contrast does not isolate the allocation objective alone.

## What carries over from theory

The decision alternatives come from the general-catalogue derivation in
`research/general_catalogue_theory_20261103/GENERAL_THEOREM.md`. With no labelled
calibration, this loop explores its \(\alpha=0\) regime. The certificate's
anytime model error bound is \(e^{-R}\); its argument and numerical arithmetic
contract are stated in `GATE_NOTE.md`. For \(R=3\) the bound is about 0.049787.

The certificate is independent of whether the allocation is efficient. Its
validity assumes the fixed iid two-rate channel and correct public state space.
All-data MLE, fixed optimization tolerance, finite quadrature, finite update
cadence and delayed checking do not establish the old forced-only expected-time
theorem or a new asymptotically optimal implementation. The pilot does not
measure an asymptotic slope. No posterior threshold is used as a certificate.

## Scope and present result

The implementation is explicitly bounded to \(d\le6,G\le2\), with
\(\eta=1/100\) for planning. It is a programmatic adaptive policy, without a
language-model conversation. It validates a recommendation-oriented observable
loop. The current eight-world development comparison does **not** establish
Decision KL superiority over repaired Decision IG; the latter uses slightly
fewer queries and less CPU in this sample. Keep both allocators as candidates.
