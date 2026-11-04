# Decision-value bridge: statements, proofs, and limits

Date: 2026-11-05. Scope: analytic bridge for the original shared-format channel.
This note does not alter the paper, experiment runner, historical outcomes, or
original premium theorem. No live model calls. The rational certificates are
reproducible with `python research/decision_value_bridge_20261105/exact_bridge_certificates.py`.

## 1. One decision problem must be fixed before allocating queries

Write h=(theta,z,p,q) and let pi_t be a probability distribution on the original
parameter space, updated by its conditional iid binary likelihood. A finite
rate grid is a computational belief approximation, not a replacement of the
continuous-parameter theorem or a claim of exact continuous posterior inference.
The original theorem has a **singleton** target f(theta): the unique catalogue
winner. Let D be its finite answer space and define

    V(pi)=max_{a in D} P_pi(f(theta)=a),   R(pi)=1-V(pi).

For query e=(j,m), let P_pi(y|e)=integral P_h(y|e) pi(dh), and let pi^{e,y}
be its Bayes update. Define

    DV_pi(e) = sum_y P_pi(y|e) V(pi^{e,y}) - V(pi)
             = R(pi) - E[R(pi^{e,Y})].                         (1)

This is standard myopic expected value of sample information under 0-1 decision
loss. It is not expected utility regret reduction for the catalogue utilities.
The probability of the best item and expected utility of the selected item
are different decision objectives. Query costs are unit in the theorem;
subtracting a monetary query cost requires a specified common utility scale.

For acceptable-answer sets A(h), replace V by

    V_A(pi)=max_a P_pi(a in A(h)).                            (2)

Acceptance events can overlap, so these probabilities need not sum to one.
Do not arbitrarily normalize them or substitute the posterior of a selected
representative winner. A practical NO_BUY output belongs in A(h) only under an
explicit preference/utility rule. It is distinct from ABSTAIN, which signifies
that no answer is certified before a resource cap. An outside option can stay
within the singleton theorem when it is a fixed affine catalogue item and all
states still have unique winners. Epsilon-optimal or multiple acceptable items
change the target and do not automatically inherit the premium boundary;
Degenne and Koolen (2019) specifically study multiple-answer complications.

## 2. Standard one-step identities

**Proposition 1 (nonnegativity and zero criterion).** For finite D and the
binary reply channel, DV_pi(e)>=0. It is zero if and only if the positive-mass
reply branches have at least one common maximizing answer:

    intersection_{y:P_pi(y|e)>0} argmax_a P_pi(f(theta)=a | e,y)
    is nonempty.                                           (3)

This also holds with the membership probabilities in (2).

**Proof.** Put v_y(a)=P_pi(f(theta)=a | e,y). For a prior maximizing answer a*,

    DV_pi(e)=sum_y P_pi(y|e) [max_a v_y(a)-v_y(a*)].

Every term is nonnegative. Equality requires that a* maximize every
positive-mass branch. Conversely a common branch maximizer also maximizes
their average and makes the displayed difference zero. QED.

This is a finite-action Bayes decision identity, not a new theorem about
reliability. It explains how substantial posterior movement, including learning
z,p,q, can have zero immediate effect on recommendation success.

## 3. Certification transfers; efficiency does not

**Proposition 2 (allocation-independent singleton safety).** Under the original
fixed-state iid channel, use any predictable allocation, including exact DV,
approximate/grid DV, randomized ties, or DV combined with forced exploration.
Let ell_t(i)=sup_{h:f(theta)=i} log L_t(h). Emit i only when

    ell_t(i)-max_{j!=i} ell_t(j)
      > log(1/delta) + sum_e log(N_e(t)+1).                  (4)

If the maximizations and inequality are verified conservatively, then for every
allowed true h, P_h(ever emit an incorrect i)<=delta. Approximate allocation
does not weaken this bound. Approximate unvalidated gate optimization can.

**Proof.** For each action integrate an unrestricted Bernoulli parameter against
Beta(1,1), giving a product mixture likelihood Q_t. Its saturated likelihood
satisfies sup_r L_t(r)<=Q_t product_e(N_e(t)+1), including under adaptive
sampling since the predictable policy factors cancel in likelihood ratios.
At any wrong output the true likelihood is in a competing class. Equation (4)
therefore implies Q_t/L_t(h)>1/delta. This ratio is a nonnegative mean-one
martingale under h; Ville's inequality finishes the proof. QED.

This restates the existing gate argument. It is **not** asymptotic optimality
of DV, an expected stopping-time bound, or termination. A zero DV value is not
a frequentist certificate. At a cap, return ABSTAIN if (4) is unresolved.
The original equality K=K_or concerns a best achievable information coefficient;
a practical DV policy is not proved to achieve either coefficient. Forced
exploration by itself does not turn this proposition into optimal tracking.

For set-valued acceptance, a compatible extension would certify action a by
comparing the overall model likelihood with the supremum over states where
a is unacceptable. The same mixture proof can apply to that precisely defined
gate, but (4), its current code, and the singleton premium theorem should not
be silently relabelled as that extension.

## 4. Explicit myopia inside the unchanged channel

**Proposition 3 (zero one-step value, positive two-step format learning).**
Use d=2, one sharing group S={1,2}, U_+=theta_1 and U_-=-theta_1. The winner
is unique on the full cube. Coordinate 2 is an auxiliary preference that does
not affect this catalogue decision; the general theorem permits it. Its query
is an ordinary noisy preference query, not a direct type report or externally
labelled reference observation. Set eta=.05 and an independent belief

    P(theta_1=+)=77/100, P(theta_2=+)=99/100,
    P(z=0)=1/2,
    P((p,q)=(9/10,3/5))=P((p,q)=(22/25,31/50))=1/2.

Both signs, both types, and both rate pairs have positive probability. For
both formats the marginal target accuracy is 3/4. Because 77/100>3/4,
theta_1=+ remains the posterior winner after either reply to either target
query. A query about theta_2 leaves theta_1 independent and unchanged.
Thus **all four available queries have DV exactly zero**.

Now query (2,0). After reply + query (1,0); after reply - query (1,1).
Finally recommend the sign returned by this target query. Exact enumeration
of the 16 hidden states gives

| First reply | Probability | Chosen target format | Conditional final success |
|---|---:|---:|---:|
| + | 149/200 | 0 | 72257/93125 |
| - | 51/200 | 1 | 52639/63750 |

Both final success probabilities exceed 77/100; the stated terminal decision
is Bayes-optimal on each target reply branch. Total success is

    197153/250000 = .788612,
    improvement = 4653/250000 = .018612 > 0.                (5)

The auxiliary query has positive information about the common format and
changes the best follow-up format even though its immediate DV is zero.
This proves complementarity, not superiority of IG or a two-step policy.
Boutilier et al. (2003, Section 2) already explain the generic failure of
myopic EVOI for individually valueless but jointly useful queries. The new
content here is an explicit checkable instantiation under this paper's channel.

### Explicit open neighborhood

Parameterize the product belief by a=P(theta_1=+), b=P(theta_2=+),
c=P(z=0), w=P(rate pair 1), and p_1,q_1,p_2,q_2. Perturb **each** of these
eight scalars by less than epsilon=1/1000 from the displayed values; retain
the same independent construction and catalogue. All states stay supported,
and both rate pairs remain in the allowed ordered interior.

Couple the four prior Bernoulli draws and each binary response. A one-query
joint state/transcript law changes by total variation at most 5 epsilon;
a two-query adaptive transcript changes by at most 6 epsilon. In the baseline,
the minimum unnormalized difference
P(theta_1=+,Y=y)-P(theta_1=-,Y=y) over all four one-query choices and both
replies is 1/50. Perturbation changes each difference by at most 10 epsilon,
so the same plus answer still maximizes every branch: all DV remain zero.
The fixed two-step terminal policy has success at least .788612-6 epsilon,
while current success is at most .77+epsilon. Its improvement remains at least

    .018612-7 epsilon = .011612 > 0.

Thus this is not a tie or point-prior artifact. The claim concerns an admissible
belief, **not** a posterior proved reachable from the experiment's uniform prior.
The two-point rate belief is exact for this construction. Continuous beliefs
concentrated near these pairs also preserve the strict inequalities by coupling;
we do not claim that a particular continuous prior reaches this configuration.

## 5. Strict IG versus DV reversal, with explicit limitations

Keep the catalogue, group, type prior and uncertain rate pairs of Proposition 3,
but set P(theta_1=+)=7/10 and P(theta_2=+)=1/2. Let e_1=(1,0), e_2=(2,0).
For full-state joint information gain I(h;Y|e),

    IG(e_2)-IG(e_1)=log(2)-h(3/5)>0,
    DV(e_1)=1/20>0=DV(e_2).                               (6)

Indeed both actions have the same expected conditional reply entropy, while
their positive-reply probabilities are respectively 3/5 and 1/2. A target query
raises expected winner success from .7 to .75; the auxiliary query leaves it
at .7. The strict inequalities persist on an open neighborhood by continuity
(all reply probabilities are interior). Winner regions also persist under
sufficiently small perturbations of the catalogue coefficients.

This is a reversal against **joint-state IG**, not against decision-label IG,
which assigns the independent auxiliary query zero information here. It uses
an auxiliary decision-irrelevant coordinate and must not be sold as an
all-coordinates-relevant example or as an empirical performance prediction.
No numerical superiority follows; Proposition 3 itself warns against assuming
that immediate decision value captures all useful reliability learning.

## 6. Safe manuscript framing

The structural contribution remains the exact shared-reliability premium
boundary. The method is a standard one-step Bayes-risk acquisition rule
instantiated with joint preference/format/rate inference and the existing
frequentist gate. The propositions make its decision objective and failure
mode explicit. A meaningful empirical comparison shares likelihood, prior,
queries, budget, tie handling and certificate with IG, and changes only the
acquisition score. Any advantage is restricted to those evaluated conditions.
