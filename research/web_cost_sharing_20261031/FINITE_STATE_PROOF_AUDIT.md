# Finite-state expected-cost achievability audit

Date: 2026-10-31. This is a direct mathematical derivation for `MODEL_AND_SCOPE.md`, using no simulation, training, or model calls. It is a delegated same-family proof audit, not a formal verification or a literature-priority claim. Historical and sealed artifacts were not edited.

## 1. Verdict and exact scope

**PASS for the fixed finite-action model:** the proposed information LP is both a lower bound and the exact leading expected-cost coefficient. Its alternatives need only have a different answer vector theta. Same-theta/different-z alternatives must **not** be added to that LP unless the task is changed to require recovering z as well.

Full-state estimation is nevertheless a convenient auxiliary device for achievability. Deterministic square-root exploration identifies theta and z at a summable error rate. Those sublinear exploration samples do not impose a first-order nuisance-identification constraint. A finite-state grouped likelihood-ratio stopping rule is uniformly correct independently of the allocation policy. Deterministic tracking and a summable stopping-time tail give the required expectation bound, rather than just almost-sure convergence.

The theorem is pointwise as delta tends to zero, with fixed d, partition, finite positive integer L_max, r, p, q, c, and ell. It assumes exact probability evaluation, exact LP solutions, and exact tracking arithmetic. There is no uniformity in growing action menus, vanishing p-q, r approaching one half, varying costs, or numerical solver errors.

## 2. Finite experiment notation

Let

\[
\mathcal H=\{-1,+1\}^d\times\{A,B\}^G,
\qquad h=(\theta,z),
\]

and let `ans(h)=theta`. An action e specifies a fact j and a nonzero pair `(n_A,n_B)` with total at most L_max. Let A be the number of actions. Its known cost is

\[
w_e=c+\ell(n_A+n_B),\qquad
0<w_{\min}\le w_e\le w_{\max}<\infty.
\]

One block is one round. Its outcome is the pair of positive counts, with finite alphabet \(\mathcal Y_e\). Given h and the chosen action e, a new independent root is drawn and the block has a fixed distribution \(P_h^e\). Conditional on the past, its law is still \(P_h^e\); it is not an old root being revisited.

Because \(r\in(1/2,1)\), \(1/2\le q<p<1\), and all block lengths are finite, every permitted count outcome has strictly positive probability under every state. Thus

\[
B=\max_{e,h,g,y\in\mathcal Y_e}
\left|\log\frac{P_h^e(y)}{P_g^e(y)}\right|<\infty,
\qquad D_e(h,g)=\operatorname{KL}(P_h^e\Vert P_g^e)
\]

are bounded. All likelihoods below condition on the chosen actions; predictable policy factors cancel in likelihood ratios.

### Full-state identifiability is supplied by the menu

For a one-read action on fact j in format m,

\[
\mathbb E_hY_{j,m}
=\theta_j(2r-1)(2a_{g(j),m}-1).
\]

The sum of the A and B means has sign theta_j because
\(p+q-1>0\). Once that sign is known, their unequal oriented magnitudes identify the preferred format. Since each group is nonempty and both one-read formats are available, every distinct pair h,g is separated by some action:

\[
\min_{h\ne g}\sum_eD_e(h,g)>0.
\tag{1}
\]

This remains true for q=1/2. The strict p>q and r>1/2 assumptions matter.

## 3. Information program and lower bound

For each true state h define

\[
K_h=\min_{x\ge0}\left\{\sum_ew_ex_e:
\sum_ex_eD_e(h,g)\ge1
\quad\forall g:\operatorname{ans}(g)\ne\operatorname{ans}(h)\right\}.
\tag{2}
\]

This program has a finite positive attained optimum. A sufficiently large uniform allocation is feasible by (1). Positive action costs make bounded objective sublevel sets compact, giving attainment. At least one wrong-answer constraint exists and has bounded coefficients, giving positivity.

Let a policy be uniformly delta-correct for theta and stop almost surely under every state. If its expected cost under h is infinite, the lower bound is immediate. Otherwise \(\mathbb E_h\tau<\infty\) because every block costs at least w_min. Stopped change of measure gives, for each wrong-answer state g,

\[
\sum_e\mathbb E_hN_e(\tau)D_e(h,g)
\ge b_\delta:=\operatorname{kl}(1-\delta,\delta).
\tag{3}
\]

The decision event is “output ans(h).” Its probability is at least 1-delta under h and at most delta under g. Under a same-answer state this event is correct under both states, so no such information inequality is forced.

Normalizing expected action counts by b_delta gives a feasible point of (2). Therefore

\[
\mathbb E_hC_\tau\ge K_h b_\delta,
\qquad
\liminf_{\delta\downarrow0}
\frac{\mathbb E_hC_\tau}{\log(1/\delta)}\ge K_h.
\tag{4}
\]

The likelihood chain rule is justified by bounded increments and finite expected block count. The block structure is essential: counts from within one persistent root cannot be treated as independent one-read actions.

## 4. A fully specified attaining policy

Choose once and for all a deterministic optimal solution \(x^*(h)\) of (2) for every state. For example, take the lexicographic minimum on its compact optimal face. Define

\[
n_h=\sum_ex_e^*(h)>0,\qquad
v_e(h)=x_e^*(h)/n_h,\qquad
\mu_h=\sum_ew_ev_e(h)=K_h/n_h.
\tag{5}
\]

Here n_h is the target **block-count coefficient**, whereas K_h is the target **cost coefficient**. Confusing these normalizations would give an incorrect cost proof.

### Forced exploration

Enumerate the A actions. For each integer k>=0, reserve rounds

\[
Ak^2+1,\ldots,Ak^2+A
\tag{6}
\]

and execute every action once in that block. These intervals are disjoint. Let F(t) be the total number of forced rounds by t. There are constants depending only on A such that

\[
F(t)\le C\sqrt t+C,
\]

and each action has at least \(c_0\sqrt t\) forced observations for all sufficiently large t.

Before a nonforced round, compute \(\widehat h\) as the maximum-likelihood state using only earlier forced observations, with deterministic ties. The estimator is defined using the full state h, although the requested output and stopping rule concern only theta.

### Deterministic cumulative-deficit tracking

Index exploitation rounds by s. Let \(u_s=v(\widehat h_s)\), define cumulative desired counts \(S_e(s)=\sum_{i\le s}u_{i,e}\), and let \(N_e^{\rm exp}(s-1)\) be past exploitation counts. Choose an action maximizing

\[
S_e(s)-N_e^{\rm exp}(s-1),
\tag{7}
\]

with deterministic ties. Forced rounds do not update these desired exploitation counts.

For arbitrary target sequences, the tracking discrepancy is uniformly bounded. To see this, let \(d_e=N_e^{\rm exp}-S_e\). Before choosing an action after adding u_s, the provisional discrepancies sum to -1. Select their minimum and add one to that coordinate. Inductively every resulting d_e is at most 1; their sum is zero, so every d_e is at least -(A-1). Consequently

\[
\|N^{\rm exp}(s)-S(s)\|_1\le C_A
\tag{8}
\]

for a finite constant, e.g. A squared. No randomized action selection or tracking concentration is needed.

### Grouped GLR stopping

For a theta vector define its profile likelihood

\[
L_t(\theta)=\max_z\prod_{i\le t}P_{(\theta,z)}^{e_i}(Y_i).
\]

Let \(\widehat\theta_t\) maximize it. Define

\[
H_{\rm wrong}=(2^d-1)2^G,
\quad R=\log(1/\delta),
\quad \beta_\delta=R+\log H_{\rm wrong}.
\tag{9}
\]

Stop at the first completed-block boundary where

\[
\log L_t(\widehat\theta_t)
-\max_{\vartheta\ne\widehat\theta_t}\log L_t(\vartheta)
\ge\beta_\delta,
\tag{10}
\]

and return that vector. Because the parameter set is finite, a constant union-Ville threshold is sufficient; no log(t) penalty or continuous-parameter mixture approximation is necessary.

All observations, including forced blocks, enter (10). Extend the same acquisition rule indefinitely for the analysis, disregarding the first stopping time.

## 5. Uniform correctness

Fix a true h. For every state g with a wrong answer, \(L_t(g)/L_t(h)\) is a nonnegative mean-one martingale under h, even under adaptive action selection. A wrong stop implies that one such g has likelihood at least \(e^{\beta_\delta}L_t(h)\): the competing-answer denominator contains the true state.

Ville's inequality and a union bound over H_wrong states give

\[
\Pr_h\{\text{stop with wrong theta}\}
\le H_{\rm wrong}e^{-\beta_\delta}=\delta.
\tag{11}
\]

The expected-time argument below ensures almost-sure stopping. This guarantee does not depend on whether the policy has accurately estimated z or found a useful allocation yet.

## 6. Estimation and allocation bounds

### Summable full-state estimation error

For a false state g, its forced-data log likelihood relative to h is a sum of independent bounded random variables with negative expectation. Each action is forced order sqrt(t) times; (1) bounds the total expected evidence away from zero by a constant times sqrt(t). There are only order sqrt(t) such observations. Hoeffding's inequality and a union over the finite state set therefore give

\[
\Pr_h(\widehat h_t\ne h)\le C e^{-c\sqrt t}
\tag{12}
\]

for sufficiently large t. Constants can be taken uniformly over the finite H, with the model parameters fixed.

Let B_bad(t) count exploitation rounds up to t whose estimate is not h. Under the infinitely continued policy,

\[
\mathbb E_h B_{\rm bad}(\infty)
\le\sum_{t\ge0}\Pr_h(\widehat h_t\ne h)<\infty.
\tag{13}
\]

This is useful for expected cost; almost-sure eventual correctness alone would not supply that bound.

### Allocation closeness with a summable tail

Combining (8) with the target construction gives the deterministic inequality

\[
\|N(t)-t v(h)\|_1
\le C_A+2F(t)+2B_{\rm bad}(t).
\tag{14}
\]

For every fixed a>0, choose a sufficiently small fixed gamma>0. If every exploitation estimate after floor(gamma t) is correct, B_bad(t)<=gamma t+O(1). A union bound using (12), together with F(t)=O(sqrt(t)), yields

\[
\Pr_h\{\|N(t)/t-v(h)\|_1>a\}
\le C t e^{-c\sqrt t}
\tag{15}
\]

for all sufficiently large t. Constants may depend on a and the fixed model. This argument does not assume one has permanently committed to an early type estimate.

## 7. Uniform likelihood margin and expected block count

For a wrong-answer state g, write

\[
\Lambda_t(h,g)=\log\frac{L_t(h)}{L_t(g)}
=\sum_eN_e(t)D_e(h,g)+M_t(g),
\tag{16}
\]

where M_t(g) is a bounded-increment martingale. Its increments have magnitude at most 2B. For every b>0, Azuma and a finite union bound give

\[
\Pr_h\{\max_{g:\,\operatorname{ans}(g)\ne\theta}
|M_t(g)|>bt\}\le C e^{-c_b t}.
\tag{17}
\]

Feasibility of x*(h) implies

\[
\min_{g:\,\operatorname{ans}(g)\ne\theta}
\sum_ev_e(h)D_e(h,g)\ge1/n_h.
\tag{18}
\]

Fix epsilon>0. At every horizon t>=(n_h+epsilon)R,

\[
t/n_h-R\ge
\frac{\epsilon}{n_h(n_h+\epsilon)}t=:\xi t.
\tag{19}
\]

Choose the allocation tolerance a in (15) with D_max*a<=xi/3, and the martingale tolerance b=xi/3. On the good events in (15) and (17), equations (16)--(19) imply

\[
\min_{g:\,\operatorname{ans}(g)\ne\theta}\Lambda_t(h,g)
\ge R+\xi t/3.
\tag{20}
\]

For sufficiently large t, this exceeds beta_delta. Since the true-answer profile is at least L_t(h), condition (10) must already have been met. Therefore there are finite constants C,c and a sufficiently small delta_0 such that

\[
\Pr_h\{\tau_\delta>t\}\le C t e^{-c\sqrt t}
\quad\text{for all }0<\delta<\delta_0,
\quad t\ge\lceil(n_h+\epsilon)R\rceil.
\tag{21}
\]

Summing the tail gives

\[
\mathbb E_h\tau_\delta
\le (n_h+\epsilon)R+o(1).
\tag{22}
\]

The exponentially decaying square-root tail is summable; its sum after a growing lower endpoint tends to zero. For every fixed delta outside the asymptotic range, the same argument starts at a sufficiently large finite t so that t/n_h exceeds the fixed boundary with linear slack. Thus the expected block count is finite for every delta, and the policy stops almost surely.

This proof establishes an expectation bound. Merely observing that empirical allocations converge would not establish (21) or (22).

## 8. From expected blocks to expected cost

It is insufficient to multiply (22) by the worst action cost: that would lose the optimal coefficient. Instead, from the tracking decomposition,

\[
|C_t-\mu_h t|
\le w_{\max}\{C_A+2F(t)+2B_{\rm bad}(t)\}.
\tag{23}
\]

This bound holds pathwise at the random stopping time as well. Equations (13), F(t)<=C sqrt(t)+C, and Jensen's inequality imply

\[
|\mathbb E_hC_{\tau_\delta}-\mu_h\mathbb E_h\tau_\delta|
\le C\sqrt{\mathbb E_h\tau_\delta}+C.
\tag{24}
\]

Using (22) and mu_h*n_h=K_h,

\[
\limsup_{\delta\downarrow0}
\frac{\mathbb E_hC_{\tau_\delta}}{R}
\le\mu_h(n_h+\epsilon)
=K_h+\mu_h\epsilon.
\]

Let epsilon tend to zero and combine with (4):

\[
\boxed{
\inf_{\pi\text{ uniformly delta-correct for theta}}
\mathbb E_hC_\pi
=K_h\log(1/\delta)+o(\log(1/\delta)).}
\tag{25}
\]

The explicitly constructed policy attains this at every h with the same uniform correctness requirement. Its acquisition rule uses the known finite experiment and delta only through its stopping threshold.

## 9. Oracle and nuisance interpretation

For the oracle, restrict the state space to the known type vector z and keep exactly the same action menu, block costs, and outcome laws. The same proof gives its LP, whose alternatives have only a different theta. Neither oracle nor learner sees source reports or factual truth.

Same-theta/different-z constraints are absent from (2) for a substantive reason: deciding the type is not the requested answer. The construction estimates it at a sublinear exploration cost to select an efficient allocation. It does not certify z at level delta. Adding delta-correct type recovery would be a different task and could raise the LP value.

The square-root forced schedule is sufficient precisely because all model parameters are fixed and full states are identifiable. If two distinct nuisance states were observationally equivalent under every action, one would need to quotient equivalent states or track compatible allocations rather than invoke (12) unchanged. The present menu and p>q avoid that issue.

## 10. Loopholes excluded and recommendation

- **Block law versus independent reads:** compute KL between the full two-count mixture distributions. Treating the within-root reads as independent conditional on theta changes the experiment and invalidates the coefficient.
- **Cost normalization:** normalize x* by its sum to select blocks, not by its weighted cost. Recover expected cost using (23)--(24).
- **Nonunique LP optima:** a deterministic optimal selection suffices because H is finite. There is no need to prove a continuously varying optimizer or choose a favorable tied oracle depth after the fact.
- **Profiled stopping:** maximize over nuisance separately for each candidate theta. A test that demands separation from all z alternatives solves a stronger task.
- **Expected-time guarantee:** retain the estimation tail, deterministic discrepancy bound, likelihood martingale concentration, and cost conversion. Almost-sure tracking alone is inadequate.
- **Finite precision:** the proof is idealized. A numerical allocation or likelihood implementation needs explicit feasibility/optimization and stopping certification safeguards; successful deterministic examples do not establish these guarantees.
- **Growing depth/cost regimes:** L_max, c, and ell are fixed in (25). Any outer limit in c or removal of the depth cap must be justified separately; this proof supplies no uniform interchange of limits.
- **Action history:** selected blocks must finish and use fresh roots. Early stopping inside a block, mixed responses selected after observing current-root data, revisits, and shared purchases across facts require a new action model.

**Evidence:** the finite-state model's exact identifiability and strictly positive bounded probabilities, together with the complete argument above.

**Inference:** the expected-cost LP can serve as a reliable foundation for the proposed oracle allocation and sharing-threshold analysis. Whether a proposed threshold is correct depends on its own allocation geometry; (25) does not establish a scalar threshold or resolve optimal-depth ties.

**Recommendation:** GO for the restricted finite-action theorem and its use as a proof foundation. Keep novelty claims separate: controlled-sensing likelihood bounds and optimal information allocation are standard ingredients; the potential contribution must be a further proved structural statement about source cost and format sharing.
