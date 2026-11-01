# Joint task–type allocation

## Material Passport

Implementation: phase2e/strategies.py and estimator.information_scores.
All policies make predictable choices using only public inputs and observed
responses. Costs are one per task or type response; offline cost is reported too.

Fused-Original changes only the estimator used by the original semi-infinite
KL allocation solver. At the same update times it substitutes posterior means
p,q and marginal MAP z, and tracks the original expanded a_g,b_g,c_g weights.
The partition, alpha=M/R, available actions, tolerance schedule and numerical
solver floors remain the frozen ones. This provides an estimator-only
intervention within the original allocation architecture, although the changed
estimate naturally changes the resulting action trajectory.

Fused-Info uses a simpler decision-information criterion. For a possible action
a and next binary outcome Y_a, define

\[
I_t(a)=I(\Theta;Y_a\mid\mathcal D_t)
=\sum_\vartheta\pi_t(\vartheta)
 D_{\rm Ber}(\mu_{a,\vartheta},\mu_a),\quad
\mu_{a,\vartheta}=E[P(Y_a=1|\vartheta,Z,p,q)\mid\vartheta,\mathcal D_t].
\]

All theta states and correlated type/rate uncertainty are included. At each
original update, choose argmax I_t(a)/cost(a), with fixed action-order ties,
and set that action's target mass to one. The inherited cumulative tracker
and forced task blocks implement the targets until the next update. It is a
batch-updated greedy information policy, not exact one-step updating per query.
Type-disabled versions exclude those actions but retain unknown types in inference
and in the stopping likelihood.

A type response depends on z, but helps only when z and theta have become
posterior dependent. Initially, without task data, theta and z are independent,
so pure type uncertainty alone does not imply positive answer information.
After task evidence, a type report can break format/sign ambiguity. When task
responses already settle the useful type distinction, its information about
theta shrinks. Thus uncertainty and purchase timing are endogenous, rather than
allocating R-level type certainty independently of task evidence. This explains
the criterion; whether the timing saves acquisition cost is an empirical question.

The KL expression is evaluated in log space. An entropy difference would lose
the information of rare wrong-answer states at R=256. For each theta, compute
its predictive deviation as sum_phi pi(phi)(mu_theta-mu_phi); this preserves a
modal deviation proportional to rare-state mass. A sixth-order local KL series
avoids first-order cancellation for tiny deviations. General nonlocal KL uses
SciPy rel_entr. This is a numerical stabilization, with no numerical certification.
A test with 500 task observations checks that no spurious fixed information
floor dominates the rare alternative. None of this arithmetic controls stopping.

Fused-D-RRC-Type replaces only the frozen D-RRC-Type estimator. Its workload
threshold, uniform-coordinate exploitation and public single-group/zero-reference
guard are unchanged. This is an essential same-estimator simple comparator.
The guard makes no claim that finite-R type queries are useless.

The no-type pair contrasts information allocation with the original solver
without direct type purchasing. The full/no-type contrasts within each allocator
measure the value of enabling that allocator to buy type evidence. Their
interaction is reported rather than assigning all full-arm differences to timing.
This design does not identify a pure timing effect holding the task trajectory
fixed, nor does it establish that any complexity is worthwhile universally.

No expected-stopping optimality theorem is supplied. Posterior entropy reduction
is not the same objective as the frequentist GLR threshold, and a myopic policy
can trade away important future learning. The forced schedule ensures observable
exploration within the bounded run; it does not repair the missing infinite-time
estimator, numerical-oracle or allocation-optimality proof conditions.

For a type query, conditional on the observed past, Theta -> z_g -> Y_type is
a Markov chain. Therefore its exact information obeys

\[
0\le I(\Theta;Y_g\mid\mathcal D)
\le I(z_g;Y_g\mid\mathcal D)
=h((1-s_g)+(2s_g-1)\pi_g)-h(s_g),
\]

where pi_g=P(z_g=1|D) and h is binary entropy in nats. This upper bound vanishes
as pi_g tends to zero or one. Independence of Theta and z_g makes the left side
zero even at pi_g=1/2. This supplies a model-level reason to consider both type
uncertainty and its coupling to the answer, rather than type entropy alone.
Maximizing the exact criterion is optimal for the next-step expected posterior
entropy reduction; that limited assertion does not imply optimal stopping cost.
The implementation uses approximate integrals and delayed target updates.

Information-gain query selection is established Bayesian experimental-design
methodology; see [Houlsby et al., Bayesian Active Learning for Classification
and Preference Learning](https://arxiv.org/abs/1112.5745). That work studies
predictive-entropy information objectives in a different model. Here the design
choice is to target only the answer vector while marginalizing nuisance
reliability/type uncertainty. This bounded implementation is not a claim of
novelty for information gain itself or a completed literature-priority audit.
