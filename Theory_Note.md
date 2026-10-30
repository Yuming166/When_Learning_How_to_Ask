# Learning How to Ask: Calibration Information and the Smallest Sharing Group

Research note derived on 29 October 2026. This is a new derivation built on the user's binary-preference model. It is not an independently reviewed or accepted paper. No independent Astra xhigh agent was successfully invoked in this session. Numerical checks are reported separately from proofs.

## 1. Model and the information comparison

There are \(d\) unknown fixed signs \(\theta_j\in\{-1,+1\}\). A known partition \(\mathcal S=(S_1,\ldots,S_G)\) has sizes \(k_g\). Group \(g\) has an unknown preferred question format \(z_g\in\{1,2\}\). A task query \((j,m)\) returns a fresh binary answer with

\[
\Pr(Y=\theta_j\mid j,m)=\begin{cases}p,&m=z_{g(j)},\\q,&m\ne z_{g(j)}.\end{cases}
\]

Both reliability levels are unknown. They are common across groups. Fix a known \(0<\eta<1/2\) and use the parameter domain

\[
1/2\le q<p\le1-\eta.
\]

The upper bound away from one is a technical bounded-likelihood assumption. There is no known lower bound on \(p-q\), and no positive lower bound on \(p-1/2\). All asymptotic claims are pointwise at a fixed true parameter with \(p>q\); they are not gap-uniform minimax statements. The closure, including \(p=q=1/2\), is used when minimizing over alternatives.

Before the task, the learner receives two labelled reference streams, each containing \(M_\delta\) independent observations:

\[
X_{p,i}\sim\operatorname{Bern}(p),\qquad X_{q,i}\sim\operatorname{Bern}(q).
\]

The stream identities are known from the reference experiment. These observations estimate the high and low reliability levels; they do not disclose any current \(z_g\) or any current \(\theta_j\). This is an explicit information assumption. Arbitrary unlabelled past conversations are not automatically equivalent to these reference streams. There are \(2M_\delta\) offline observations in total.

Write

\[
R_\delta=\log(1/\delta),\qquad M_\delta/R_\delta\longrightarrow\alpha\in[0,\infty).
\]

All task queries count toward the online stopping time \(\tau\). Offline observations are treated as an already acquired resource. Report total acquisition cost separately as \(2M_\delta+\mathbb E\tau\) when that is the relevant objective.

A policy must stop almost surely and recover the entire sign vector with probability at least \(1-\delta\), uniformly over the parameter domain and all signs/types. Probability includes randomness in the offline sample. The guarantee is not a conditional guarantee for every realized offline data set.

The oracle is told the current type vector \(z\), and nothing more. It receives the same offline observations and remains ignorant of \(p,q,\theta\).

### Optional direct type questions

One may also allow a type question in group \(g\): it reports \(z_g\) correctly with known probability \(s_g\in(1/2,1)\), independently of previous observations. Its cost is one query and its distinguishing information is

\[
\kappa_g=\operatorname{kl}(s_g,1-s_g).
\]

This action is optional; set its count to zero when it is not available. A self-report whose reliability has not been established does not satisfy the known-\(s_g\) assumption. Perfect type reports are treated separately in Section 8.

## 2. Exact information program for an arbitrary known partition

Let \(D(r,x)=\operatorname{kl}(r,x)\), and let

\[
\ell(x)=\log\frac{x}{1-x},\qquad
F_k(r,x)=D(r,1-x)+(k-1)D(r,x).
\]

Orient each response by its true sign for the mathematical analysis, and relabel each group's true good format as the first format. This transformation is used only in the proof. The algorithm does not receive the true signs or types.

Let \(a_g,b_g\) be normalized online task counts **per coordinate** in group \(g\), for the good and other format. Let \(c_g\) be the normalized number of direct type questions for group \(g\). Counts are measured in units of \(R_\delta\).

For a subset \(J\subseteq\{1,\ldots,G\}\) of groups whose type is reversed under an alternative, define

\[
x_g^J(u,v)=\begin{cases}u,&g\notin J,\\v,&g\in J,\end{cases}\qquad
y_g^J(u,v)=\begin{cases}v,&g\notin J,\\u,&g\in J.\end{cases}
\]

For each group \(h\) containing one reversed preference, define

\[
\begin{aligned}
\mathcal I_{J,h}(a,b,c;\alpha)
=\inf_{1/2\le v\le u\le1-\eta}\Bigg\{
&\alpha[D(p,u)+D(q,v)]\\
&+\sum_g k_g\big[a_gD(p,x_g^J)+b_gD(q,y_g^J)\big]\\
&+a_h(2p-1)\ell(x_h^J)+b_h(2q-1)\ell(y_h^J)\\
&+\sum_{g\in J}\kappa_gc_g\Bigg\}.
\end{aligned}
\]

Define the convex optimization problem

\[
\boxed{
K_{\mathcal S,\alpha}
=\min_{a,b,c\ge0}
\left\{\sum_g k_g(a_g+b_g)+\sum_gc_g:
\mathcal I_{J,h}\ge1\quad\forall J,h\right\}.
}
\]

If direct type questions are absent, omit \(c\). There are \(G2^G\) information constraints. Each constraint is the superlevel set of a concave function, because its left side is an infimum of affine functions of the counts. This is a convex problem, despite the inner minimization.

**Theorem 1 (exact leading online cost).** Under the stated model, for every fixed true parameter,

\[
\inf_{\pi\text{ uniformly }\delta\text{-correct}}\mathbb E\tau_\pi
=K_{\mathcal S,\alpha}R_\delta+o(R_\delta).
\]

An explicit exploration-and-information-allocation policy with the stopping rule in Section 4 attains the coefficient. The result allows continuous unknown \(p,q\); plugging estimates into the original known-channel stopping boundary is not the construction used here.

### Proof of the lower bound and the reduction

For any alternative requiring a different sign vector, the stopped transcript KL divergence is

\[
M_\delta[D(p,u)+D(q,v)]+\sum_e\mathbb E N_e(\tau)D(P_h^e,P_{h'}^e).
\]

Adaptive action probabilities cancel in the likelihood ratio. Data processing applied to the event of outputting the true sign vector implies that this expression is at least

\[
\operatorname{kl}(1-\delta,\delta).
\]

Averaging an allocation over permutations within each group preserves all alternative constraints and the cost. Consequently an optimal information allocation can use common per-coordinate counts \(a_g,b_g\) within a group.

For \(r,x\ge1/2\),

\[
D(r,1-x)-D(r,x)=(2r-1)\ell(x)\ge0.
\]

For any fixed alternative type pattern and alternative levels, reversing additional preference signs only increases the divergence. It therefore suffices to consider precisely one reversed sign, in each possible group. This gives \(\mathcal I_{J,h}\).

Divide the change-of-measure inequalities by \(R_\delta\). If normalized expected costs are bounded, take a convergent subsequence of the normalized counts. Since \(M_\delta/R_\delta\to\alpha\) and \(\operatorname{kl}(1-\delta,\delta)/R_\delta\to1\), its limit is feasible for the displayed program. If the costs are unbounded the lower bound is immediate. This proves the liminf bound.

The original known-level sum of separate group coefficients must not be reused here. Changing the common unknown \(p,q\) changes the answer distribution in every group. The displayed joint program accounts for that coupling.

## 3. The inner minimization has an exact elementary solution

Every inner objective is a sum of weighted Bernoulli divergences. After complementing the true mean for the one reversed coordinate, it has the form

\[
C-W_u[\bar r_u\log u+(1-\bar r_u)\log(1-u)]
-W_v[\bar r_v\log v+(1-\bar r_v)\log(1-v)],
\]

up to a constant independent of \(u,v\).

Set each unconstrained fitted mean to its weighted average, and impose \(u\ge v\ge1/2\). First take \(u_0=\max(1/2,\bar r_u)\), \(v_0=\max(1/2,\bar r_v)\). If \(u_0\ge v_0\), use them. If \(u_0<v_0\), pool the two weighted means:

\[
u=v=\max\left\{\frac12,\frac{W_u\bar r_u+W_v\bar r_v}{W_u+W_v}\right\}.
\]

All means being averaged are among \(p,q,1-p,1-q\), so the fitted values do not exceed \(p\le1-\eta\). Zero-weight cases simply leave the unobserved parameter free subject to the order restriction. The code implements those cases explicitly.

This is the exact weighted Bernoulli isotonic projection, not a grid approximation. Strict convexity in each positively weighted parameter and the first-order conditions prove the claim.

For equal-size groups with a common type-question accuracy, symmetry across groups further allows common \(a,b,c\). The constraints are indexed only by the number of reversed groups and whether the reversed preference lies inside that set. There are \(2G\) constraints and two or three allocation variables. Thus the common equal-partition simulations do not require an optimization over exponentially many allocation variables.

## 4. A valid stopping rule and a matching policy

### 4.1 Uniform error control with unknown levels

Use the full joint likelihood of the offline observations and all online observations. For a candidate sign vector \(\vartheta\), let

\[
L_t(\vartheta)=\sup_{z,p,q}L_t(\vartheta,z,p,q).
\]

Let \(\widehat\theta_t\) maximize this quantity. Stop when

\[
\log L_t(\widehat\theta_t)-\max_{\vartheta\ne\widehat\theta_t}\log L_t(\vartheta)
\ge \beta(t,\delta),
\]

where

\[
\boxed{\beta(t,\delta)=\log(1/\delta)+\sum_{e\in\mathcal E_{\rm all}}\log(N_e(t)+1).}
\]

The stream set includes the two offline reference streams, the \(2d\) task-query streams, and any allowed group type-question streams. Each offline count is \(M_\delta\). All logarithms are natural.

**Lemma 1 (anytime error bound).** For any predictable adaptive sampling policy, the probability of stopping and returning an incorrect sign vector is at most \(\delta\).

**Proof.** Introduce a saturated model with an independent unrestricted Bernoulli parameter for every stream. Integrate each parameter against a uniform Beta prior. If a stream has \(n\) observations and \(s\) successes, its integrated likelihood is

\[
Q_e=B(s+1,n-s+1)=\frac1{(n+1)\binom ns}.
\]

Its maximum likelihood obeys \(\sup_\mu L_e(\mu)\le(n+1)Q_e\), since \(\binom ns\sup_\mu L_e(\mu)\le1\). Therefore

\[
\sup_{\theta,z,p,q}L_t\le Q_t\prod_e(N_e(t)+1).
\]

Under the true state, \(Q_t/L_t(h)\) is a nonnegative mean-one likelihood-ratio martingale, including the initial offline sampling period. Predictable adaptive choices preserve this property. On an incorrect stopping event, the likelihood of the true state lies in the competing-sign denominator, so the stopping inequality implies \(Q_t/L_t(h)\ge1/\delta\). Ville's inequality gives the result. No finite union bound over a continuous parameter space is needed. \(\square\)

### 4.2 Allocation policy

Use a deterministic forced-exploration schedule that gives every task-query stream at least \(c\sqrt t\) exploration observations by time \(t\), using \(O(\sqrt t)\) total forced observations for fixed \(d\). The remaining rounds use the information-optimal allocation at the current parameter estimate.

For a fully specified consistent estimator, use only the forced observations. Let \(\widehat\mu_{jm}\) be the empirical probability of answer \(+1\). Estimate the sign by the sign of \(\widehat\mu_{j1}+\widehat\mu_{j2}-1\). Orient the two empirical response probabilities using that estimated sign. For each group, choose the format with the higher mean oriented probability as its type. Average the oriented good/other probabilities to estimate \(p,q\). Project these estimates onto a deterministic increasingly fine grid within \(1/2\le q<p\le1-\eta\), whose mesh tends to zero. This grid is used only to define the allocation estimate. The stopping likelihood is over the full continuous model.

For every fixed true parameter and every fixed estimation tolerance, Hoeffding bounds and the positive fixed gaps give

\[
\Pr(\widehat z_t\ne z\text{ or }\|\widehat r_t-r\|>\varepsilon)
\le C_\varepsilon e^{-c_\varepsilon\sqrt t}
\]

for sufficiently large \(t\). Sign estimation has the same bound because \(p+q-1>0\).

At an exploitation round, solve the information program at the estimated parameters with \(\alpha_\delta=M_\delta/R_\delta\). Expand the per-coordinate optimizer into action counts \(n_e^*\), and sample action \(e\) with probability \(n_e^*/\sum_f n_f^*\). All observations, including forced observations and type questions, enter the stopping likelihood. This is a single ongoing policy; no permanent commitment to an early type estimate is made.

### 4.3 Expected-cost achievability

Here are the details needed beyond almost-sure consistency.

For any fixed true parameter, the information program has finite positive value: uniform sampling of task queries separates every wrong sign vector, and an alternative that changes only one sign at the true levels forces a positive task-query allocation on that coordinate. Uniformly increasing all task-query counts yields strict feasibility locally. The inner KL functions are continuous on the compact alternative-level domain. These facts give local boundedness of optimizers, continuity of the optimal value, and upper hemicontinuity of the optimal set. A unique optimizer is unnecessary: the normalized true optimal set is convex because all its members have the same total cost.

The exploration estimator is exponentially accurate in \(\sqrt t\), and the forced fraction vanishes. On a high-probability event, after a small initial fraction of a horizon \(t\), every exploitation allocation is arbitrarily close to the true normalized optimal set. Martingale concentration controls realized allocation counts around their predictable sums. Their Cesaro average is consequently close to some true normalized optimizer.

At every true optimal allocation, each wrong-sign alternative receives a strictly positive amount of online information. Indeed, a same-type alternative at the true levels that reverses coordinate \(j\) imposes

\[
a_{g(j)}D(p,1-p)+b_{g(j)}D(q,1-q)\ge1.
\]

A flipped-sign observation under any admissible alternative has probability at most \(1/2\) of the true sign. Its divergence is at least \(D(p,1/2)\) or \(D(q,1/2)\). Thus, uniformly over the compact true optimal set and all wrong-sign alternatives, normalized online information is bounded below by a positive constant. This point rules out a problematic zero-online-information alternative that would rely solely on a tight offline constraint.

At \(t=K_{\mathcal S,\alpha}R_\delta\), expected information from the target online allocation and the offline sample is at least \(R_\delta\) against every wrong-sign alternative. At \(t=(K_{\mathcal S,\alpha}+\varepsilon)R_\delta\), it exceeds that value by a positive multiple of \(R_\delta\). The boundary overhead is \(O(\log R_\delta)\) because \(M_\delta=O(R_\delta)\).

To control the full likelihood uniformly over alternatives, cover their two-dimensional level domain by a mesh of size \((M_\delta+t)^{-2}\). Bounded log-likelihood derivatives give a vanishing interpolation error; the net has polynomial size. Azuma/Hoeffding bounds for the finite sign/type set and this net, combined with the exploration-estimation bound, yield constants depending on the fixed true parameter and \(\varepsilon\) such that, for all sufficiently small \(\delta\),

\[
\Pr\!\left(\tau>t\right)\le C t^C e^{-c\sqrt t},
\qquad t\ge(K_{\mathcal S,\alpha}+\varepsilon)R_\delta.
\]

The offline observations are independent; at these horizons \(M_\delta=O(t)\), so their concentration errors fit the same bound. Summing the tail gives

\[
\mathbb E\tau\le(K_{\mathcal S,\alpha}+\varepsilon)R_\delta+o(R_\delta).
\]

Then let \(\varepsilon\downarrow0\). The same tail proves finite expectation and almost-sure stopping. Together with the lower bound, this completes Theorem 1.

This argument establishes the leading coefficient. It does not establish optimized finite-budget constants or a uniform bound when \(d\) grows or \(p-q\) vanishes.

## 5. The oracle reduces to one scalar equation

For a task of total size \(d\), define

\[
S_{d,\alpha}(a)=\inf_{1/2\le v\le u\le1-\eta}
\{\alpha[D(p,u)+D(q,v)]+aF_d(p,u)\}.
\]

Let \(a_\alpha\) be the unique positive root of \(S_{d,\alpha}(a)=1\).

**Theorem 2 (oracle allocation).** The oracle coefficient is

\[
\boxed{K_{\mathrm{or},\alpha}=d a_\alpha.}
\]

Its unique information-optimal task allocation gives every coordinate \(a_\alpha R_\delta\) good-format queries and zero first-order other-format queries. Type questions are unnecessary when the type is known.

**Proof.** Once types are known, arbitrary coordinate permutations are symmetries. The symmetric oracle information problem has objective \(d(a+b)\) and constraint

\[
\inf_{u\ge v\ge1/2}\{\alpha[D(p,u)+D(q,v)]+aF_d(p,u)+bF_d(q,v)\}\ge1.
\]

At \((a_\alpha,0)\), choose a minimizing pair \((u_*,v_*)\). Necessarily \(u_*\le p\) and \(v_*=\min(q,u_*)\). Put \(A=F_d(p,u_*)\), \(B=F_d(q,v_*)\). Then \(A>B\).

If \(u_*\le q\), both arguments equal \(u_*\), and

\[
\frac{\partial F_d(r,u_*)}{\partial r}
=d\ell(r)-(d-2)\ell(u_*)
=2\ell(u_*)+d[\ell(r)-\ell(u_*)]
\]

is positive on a set of positive length between \(q\) and \(p\). If \(u_*>q\), use

\[
F_d(p,u_*)=dD(p,u_*)+(2p-1)\ell(u_*)>D(q,1-q)=B.
\]

Evaluating the information constraint at this fixed minimizing pair gives a supporting affine upper bound. Any \(a+b\le a_\alpha\) with \(b>0\) has information strictly less than one. Thus \(b=0\) is necessary at the optimal cost. Since symmetrization preserves the average bad-format count, all individual bad-format counts must also vanish.

The good-format counts must be equal. Otherwise, choose a coordinate with less than the average count. Evaluating its reversed-sign constraint at the symmetric minimizing pair decreases its information strictly whenever \(u_*>1/2\). The remaining boundary case for unequal allocations is \(d=2,\alpha=0,u_*=1/2\); the derivative with respect to \(u\) is then negative for the under-sampled coordinate, so moving \(u\) slightly above one-half makes its information strictly less than one. For \(d=1\) there is no unequal allocation. This proves uniqueness.

Finally, \(S_{d,\alpha}(0)=0\), it increases strictly with \(a\), and it tends to infinity, because \(\inf_x F_d(p,x)>0\). Hence its root exists and is unique. \(\square\)

For computation, set

\[
u_0=\max\left\{\frac12,\frac{\alpha p+a[1+(d-2)p]}{\alpha+da}\right\}.
\]

If \(u_0\ge q\), take \((u,v)=(u_0,q)\). Otherwise take

\[
u=v=\max\left\{\frac12,\frac{\alpha(p+q)+a[1+(d-2)p]}{2\alpha+da}\right\}.
\]

A one-dimensional root search then computes \(a_\alpha\).

## 6. The smallest-sharing-group theorem

Let \(k_{\min}=\min_g k_g\), and define

\[
w_k=\max\left\{\frac12,
\frac{\alpha q+a_\alpha[1+(k-2)p]}{\alpha+ka_\alpha}\right\},
\qquad
\Gamma_k(\alpha)=\alpha D(q,w_k)+a_\alpha F_k(p,w_k).
\]

**Theorem 3 (necessary and sufficient zero-premium criterion).** For any known partition and any available direct type questions with finite \(\kappa_g\),

\[
\boxed{
K_{\mathcal S,\alpha}=K_{\mathrm{or},\alpha}
\quad\Longleftrightarrow\quad
\Gamma_{k_{\min}}(\alpha)\ge1.
}
\]

If the inequality fails, the difference of optimal expected online costs has a strictly positive leading coefficient:

\[
T_\delta^*-T_{\delta,\mathrm{or}}^*
=(K_{\mathcal S,\alpha}-d a_\alpha)R_\delta+o(R_\delta).
\]

The smallest group decides whether the premium is zero. The entire partition can still affect the size of a positive premium.

**Proof.** The oracle's optimal task allocation is unique. Equality of costs requires exactly that allocation and zero first-order type-query counts. Check whether it is feasible without revealing the types.

Suppose the alternative reverses the types of groups containing \(l\) coordinates in total, and reverses a preference inside that set. The non-reversed groups are fitted exactly by \(u=p\). The remaining minimization is

\[
\inf_{v\ge1/2}\{\alpha D(q,v)+a_\alpha F_l(p,v)\}=\Gamma_l(\alpha).
\]

Its optimizer is \(w_l\le p\), so the order constraint is satisfied. Since \(F_{l+1}(p,v)=F_l(p,v)+D(p,v)\), this value is nondecreasing in \(l\). The smallest possible nonempty set is one group of size \(k_{\min}\).

If the reversed preference lies outside the reversed-type set, a minimizing pair can be chosen with \(1/2\le v\le u\le p\). For every non-reversed preference in a reversed-type group, \(D(p,v)\ge D(p,u)\). Replacing these terms by \(D(p,u)\) reduces the objective to the oracle constraint. These alternatives therefore have information at least one. The unchanged-type alternative also has information exactly one.

The worst information at the oracle allocation is consequently \(\min\{1,\Gamma_{k_{\min}}\}\). The equivalence follows. Attainment of the convex program and uniqueness of the oracle allocation imply a strictly positive gap when that allocation is infeasible. Finite-information type questions have positive cost; equality cannot allocate a positive count to them. \(\square\)

### Corollary 3.1: no external calibration

Define

\[
r_d=\max\{1/2,p-(2p-1)/d\},\qquad I_d(p)=F_d(p,r_d).
\]

At \(\alpha=0\),

\[
a_0=1/I_d(p),\qquad
\Gamma_k(0)=I_k(p)/I_d(p).
\]

The sequence \(I_d(p)\) is strictly increasing. Indeed, \(I_1=D(p,1/2)\), \(I_2=2D(p,1/2)\), and for \(d\ge2\),

\[
I_d(p)=d[H(p-(2p-1)/d)-H(p)].
\]

Strict concavity of binary entropy shows that this expression increases strictly with \(d\), and its limit is \(D(p,1-p)\).

Therefore

\[
\boxed{\alpha=0:\quad K_{\mathcal S,0}=K_{\mathrm{or},0}
\quad\Longleftrightarrow\quad G=1.}
\]

When all preferences share one type,

\[
\boxed{K_{\{1,\ldots,d\},0}=K_{\mathrm{or},0}=d/I_d(p).}
\]

With multiple groups and globally shared unknown levels, the premium is strictly positive. The equality stated in the earlier research record for a single group must not be generalized by adding single-group coefficients.

### Corollary 3.2: recovery of the known-level result

As \(\alpha\to\infty\) in the coefficient functions,

\[
a_\alpha\to1/D(p,1-p),\qquad
\Gamma_k(\alpha)\to
\frac{D(p,1-q)+(k-1)D(p,q)}{D(p,1-p)}.
\]

The old sharing threshold is recovered exactly. This is a limit of the coefficient functions; it does not silently assert an arbitrary simultaneous limit with super-exponentially growing offline data.

The convergence follows because the offline KL penalty forces bounded-cost minimizing alternatives toward \((p,q)\). A strictly enlarged known-level allocation gives the reverse approximation.

### Corollary 3.3: pooling and calibration

Coarsening a partition, when the merged groups share the same actual type, removes alternative type patterns. It cannot increase \(K_{\mathcal S,\alpha}\). Coefficients are invariant to true format labels, so this compares the structural partition costs. The oracle coefficient depends on total \(d\), not the partition.

Both \(K_{\mathcal S,\alpha}\) and \(K_{\mathrm{or},\alpha}\) are nonincreasing in \(\alpha\), because increasing the offline information adds a nonnegative term to every alternative constraint. Their difference need not be monotone.

## 7. More calibration can first increase the value of knowing the type

This claim is an existence result, not a universal inverted-U theorem.

Take one preference, \(p=0.75,q=0.60\), and no direct type questions. The executed coefficient calculations give:

| Per-stream calibration ratio \(\alpha\) | Unknown type | Type revealed, rates unknown | Premium |
|---:|---:|---:|---:|
| 0 | 7.64456 | 7.64456 | 0 |
| 1 | 7.31811 | 6.49063 | 0.82748 |
| 5 | 6.01234 | 3.03315 | 2.97919 |
| 20 | 4.23382 | 2.04143 | 2.19239 |
| 100 | 3.85342 | 1.86143 | 1.99198 |
| Known-level limit | 3.76690 | 1.82048 | 1.94642 |

Every entry is a coefficient multiplying \(\log(1/\delta)\), not a finite-budget success rate. Both online costs decrease, while their difference increases and then decreases.

The nonmonotonicity can also be certified without trusting the nonlinear optimizer. At \(\alpha=5\), choose the fixed swapped-type alternative levels \(u=0.651466,v=1/2\). Every feasible unknown-type allocation satisfies

\[
aD(0.75,1/2)+bD(0.60,1-u)
\ge1-5[D(0.75,u)+D(0.60,1/2)].
\]

Consequently its total count is greater than \(6.01233\). For the oracle, \(a=3.034,b=0\) has minimized information greater than \(1.00018\), and hence is feasible. Thus the premium at \(\alpha=5\) exceeds \(2.978\). Its known-level limit is below \(1.947\), while at zero calibration it is exactly zero. These strict inequalities prove the existence of a nonmonotone premium. The supporting optimization bounds are retained in `numerical_bounds.json`. In addition, `certify_example.py` verifies the strict inequalities with exact rational interval arithmetic: it encloses each logarithm using a 60-term atanh series and an explicit geometric remainder. The certified premium lower bound at alpha=5 is 2.9783358779, and a certified upper bound on the known-level limiting premium is 1.9464235468. The rational checks establish these inequalities without relying on a nonlinear optimizer; they do not independently verify the general theorems.

Interpretation: without reference data, even the type-revealed system must learn how strongly to trust the good-format answers. Reference data removes much of that burden. An unknown-type system must still decide which format the known reliability pattern belongs to. Sufficient sharing can remove that remaining difficulty.

## 8. What dedicated calibration can and cannot do

### 8.1 A perfect type question removes the leading premium

If each \(z_g\) can be learned without error using one online query, then

\[
0\le T_\delta^*-T_{\delta,\mathrm{or}}^*\le G.
\]

Ask those \(G\) questions and then implement the oracle policy. The upper bound counts those questions. No logarithmic premium survives. Therefore an empirical task with nearly trivial source identification requires the direct-source baseline; it cannot be used to argue that a large calibration premium is unavoidable.

### 8.2 Known-answer checks are asymptotically dominated under this model

Suppose a calibration check uses the same response channel and format but asks about a known sign. For every alternative, its information is \(D(r,x)\). Spread its count uniformly across ordinary task coordinates in the same group. Coordinates whose signs are unchanged contribute exactly \(D(r,x)\); a reversed sign contributes \(D(r,1-x)\ge D(r,x)\). This preserves total cost and weakly increases information against every decision-relevant alternative.

Thus such known-answer checks do not improve the leading coefficient. This is an asymptotic information statement within the non-adversarial binary-channel model. It does not imply that calibration questions are useless at short budgets, or that a direct question about \(z_g\) is equivalent to a known-answer check.

### 8.3 A closed form with a noisy direct type question

For one group of size \(k\), known levels, \(q=1/2\), and a type-question KL value \(\kappa\), write

\[
A=D(p,1-p),\quad B=D(p,1/2),\quad C=D(1/2,p).
\]

The exact coefficient is

\[
\boxed{K_k(\kappa)=\frac{k}{A}
+\frac{(1-kB/A)_+}{\max\{C,\kappa\}}.}
\]

The information constraints are \(Aa\ge1\) and \(kBa+kCb+\kappa c\ge1\), with cost \(k(a+b)+c\). Since \(C>B\), take the minimum good-format count \(a=1/A\), then meet the remaining type-discrimination deficit using whichever of other-format task queries and direct type questions has greater information per cost. This proves the formula. For unknown levels, the joint convex program remains the correct allocation rule.

## 9. Persistent errors are a distinct model boundary

If an item-specific latent variable \(U\) is drawn once with \(1/2\le r<1\) and \(\Pr(U=1)=r\), and every repetition returns \(Y_t=\theta U\), repetitions after the first are deterministic functions of the first answer. They add no information about \(\theta\). With a symmetric prior on \(\theta\), the Bayes error remains \(1-r\) for every number of repetitions.

This elementary boundary is why the main theory assumes fresh observations. Fresh-context language-model sampling under a fixed cache is legitimately iid conditional on the cached problem. A history-dependent dialogue, a persistent interpretation error, and task-to-task heterogeneity are different environments. The experiment must distinguish them rather than describing all cached trajectories as real dialogues.

## 10. Executed numerical evidence

`verification.json` records:

- 400 analytic inner projections compared with a separate constrained numerical optimizer; maximum absolute objective difference about \(2.1\times10^{-10}\).
- 50 two-variable oracle optimizations checked against the scalar oracle formula; maximum difference below \(1.7\times10^{-7}\).
- 1,560 full preference-flip alternatives over 200 type/allocation cases checked against the one-flip reduction; maximum difference about \(2.3\times10^{-15}\).
- 60 arbitrary-partition checks of the smallest-group criterion; maximum difference below \(5.6\times10^{-15}\).
- 20 no-calibration closed-form checks; maximum difference below \(4.4\times10^{-7}\).

There are 32 executed coefficient settings in `coefficient_results.csv`. For \(d=8,p=.75,q=.5,\alpha=0\), the coefficients for equal group sizes \(1,2,4,8\) are approximately \(60.4785,30.4120,19.0215,17.0209\), while the common type-revealed oracle coefficient is \(17.0209\).

A separate controlled simulation executes 16,000 one-preference trajectories at \(p=.75,q=.6,\alpha=0\). Both algorithms profile unknown reliability levels over the enlarged closure with upper bound one; the mixture error proof still applies, and the interior-instance leading coefficient is unchanged. The unknown-type algorithm uses vanishing exploration and estimated-format selection; the oracle is told only the good format. At \(R=10,30,100,300\), their normalized mean costs are respectively

\[
(17.084,11.661,8.957,8.210)\quad\text{and}\quad
(10.903,9.029,8.104,7.834).
\]

The common predicted limit is \(7.64456\). No run hit the declared cap. These finite-horizon results are consistent with convergence but do not numerically prove the asymptotic statement. Observing no errors at tiny nominal tolerances does not validate a tiny error probability; the stopping guarantee comes from Lemma 1. No new language-model experiment was run in this session.

## 11. Contribution boundary and independent review status

The mathematical ingredients of controlled sensing, change of measure, likelihood-ratio stopping, and tracking information-optimal allocations are established. Related primary sources include:

1. Abraham, Alonso, Kandylas and Slivkins (COLT 2013), *Adaptive Crowdsourcing Algorithms for the Bandit Survey Problem*.
2. Garivier and Kaufmann (COLT 2016), *Optimal Best Arm Identification with Fixed Confidence*.
3. Deshmukh, Bhashyam and Veeravalli (Sequential Analysis 2021), *Sequential Controlled Sensing for Composite Multihypothesis Testing*.
4. Agrawal, Juneja, Shanmugam and Suggala (2023), *Optimal Best-Arm Identification in Bandits with Access to Offline Data*, arXiv:2306.09048.
5. Yamagata et al. (ICML 2024 Workshop on Models of Human Feedback for AI Alignment), *Relatively Rational: Learning Utilities and Rationalities Jointly from Pairwise Preferences*.

The candidate structural contribution here is the explicit finite-calibration, common-unknown-channel analysis for sharing partitions, especially the smallest-group criterion, the no-calibration full-sharing boundary, the nonmonotone value-of-type example, and the calibration-action distinctions. This note does not establish priority over every existing paper or guarantee conference acceptance.

An independent review should concentrate on the joint shared-parameter lower bound, the oracle uniqueness argument, the smallest-group reduction, and expected-cost achievability with \(M_\delta\asymp\log(1/\delta)\). The current session produced no independently verified Astra xhigh approval.
