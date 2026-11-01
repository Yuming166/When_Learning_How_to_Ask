# Theorem 1: Expected-time achievability for `Theory_Note.md`

**Source:** `C:\Users\22797\Downloads\Theory_Note.md`, dated 29 October 2026, Theorem 1 and Sections 1–4. Source SHA-256: `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef`.

**说明。** 本文对应原笔记中“各组共享未知准确率 \(p,q\)，并有离线校准样本”的 Theorem 1，展开其 expected-time achievability 证明。所有结论均针对固定维度、固定真实参数及有限 \(\alpha\)。这份文件可作为原笔记第 4.3 节的证明附件。

## 1. Statement

Use the model, partition \(\mathcal S\), and optional type questions from the source note. The fixed true state is

\[
h=(\theta,z,p,q),\qquad \tfrac12\le q<p\le1-\eta,
\quad 0<\eta<\tfrac12.
\]

Let \(R=\log(1/\delta)\), where \(0<\delta<1/2\). Each of the two labelled offline streams contains a deterministic number \(M_\delta\) of independent observations. Assume

\[
\alpha_\delta=M_\delta/R\longrightarrow\alpha\in[0,\infty).
\]

Write \(K=K_{\mathcal S,\alpha}(p,q)\) for the information-program value in Theorem 1 of the source note.

**Achievability claim.** The ongoing exploration-and-allocation policy specified below, with the stopping rule in Section 4.1 of the source note, is uniformly \(\delta\)-correct. It has finite expected stopping time at every admissible instance for every \(\delta\), and

\[
\boxed{\displaystyle
\limsup_{\delta\downarrow0}
\frac{\mathbb E_h\tau_\delta}{\log(1/\delta)}\le K.}
\tag{1}
\]

Together with the lower bound in Section 2 of the source note, this gives its exact leading coefficient. The proof covers \(q=1/2\), \(\alpha=0\), and nonunique optimal allocations.

## 2. Action notation and the information program

Let \(\mathcal A\) be the finite set of online actions: the \(2d\) task streams and any available group type questions. Set \(m=|\mathcal A|\). Encode each observation as a Bernoulli variable, and write \(\mu_e(h)\) for its mean on stream \(e\).

For an alternative \(h'=(\theta',z',u,v)\), define

\[
D_e(h,h')=\operatorname{kl}(\mu_e(h),\mu_e(h')),
\qquad
D_0(h,h')=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]

Take alternatives over the compact set

\[
\mathcal H_{\ne\theta}
=\{(\theta',z',u,v):\theta'\ne\theta,
\ \tfrac12\le v\le u\le1-\eta\}.
\]

The closure gives the same likelihood suprema and information infima as the original strict domain. For online count vectors \(x\ge0\), put

\[
J_h(x,h')=\sum_{e\in\mathcal A}x_eD_e(h,h').
\]

Let \(\mathcal X\) require equal per-coordinate counts within each group for each of its two formats; type-question counts are unrestricted nonnegative coordinates. This is a closed convex cone. The symmetrization and one-sign-flip reduction in Section 2 of the source note give the equivalent program

\[
K(h,a)=\min_{x\in\mathcal X}
\left\{\|x\|_1:
aD_0(h,h')+J_h(x,h')\ge1
\quad\forall h'\in\mathcal H_{\ne\theta}\right\}.
\tag{2}
\]

Here \(a\ge0\) denotes an offline information ratio, and \(K=K(h,\alpha)\). The good-format and other-format components of \(x\) are precisely the \(a_g,b_g\) of the note, repeated over the coordinates of group \(g\).

All possible stream means, including those of fixed-reliability type questions, lie in \([b,1-b]\) for some fixed \(b>0\). Consequently, on the stated parameter domains there are finite constants

\[
D_* =\sup_{e,h'}D_e(h,h'),\qquad
A_* =\sup_{h'}D_0(h,h'),\qquad
L_* =\sup_{e,h'}|\operatorname{logit}\mu_e(h)
                         -\operatorname{logit}\mu_e(h')|.
\tag{3}
\]

The last supremum includes both offline streams. The constants may depend on the fixed instance, partition, and available type-question reliabilities.

## 3. Two allocation facts

### 3.1 Local continuity of the optimal value and optimal set

Let \(y\in\mathcal X\) allocate one observation to every task stream and zero to type questions. Every wrong-sign alternative flips some coordinate \(j\). Its probability of the true sign on the true good-format stream of \(j\) is at most \(1/2\). Therefore

\[
J_h(y,h')\ge B_p:=\operatorname{kl}(p,1/2)>0
\quad\forall h'\in\mathcal H_{\ne\theta}.
\tag{4}
\]

Thus \(y/B_p\) is feasible in (2), and adding any positive multiple of \(y\) gives strict slack. The separation in (4) remains bounded away from zero in a neighborhood of the true levels.

For a lower bound, use an alternative at the true levels with the same types and only coordinate \(j\) reversed. Define

\[
A_r=\operatorname{kl}(r,1-r).
\]

Every feasible \(x\) must satisfy, for each \(j\),

\[
x_{j,z_{g(j)}}A_p+x_{j,3-z_{g(j)}}A_q\ge1.
\tag{5}
\]

Since \(A_p\ge A_q\), summing (5) gives

\[
0<d/A_p\le K(h,a)\le2d/B_p<\infty.
\tag{6}
\]

These bounds are locally uniform in the true levels. Existence of an optimizer follows by restricting the closed feasible set to a bounded objective sublevel set.

We now justify the continuity used by the allocation policy. Fix the discrete labels, and let \((h_n,a_n)\to(h,\alpha)\). On every bounded count set, the left sides of the constraints in (2) converge uniformly over the compact alternative set. For a true optimizer \(x\), let \(\omega_n\to0\) bound the resulting maximum constraint deficit at \((h_n,a_n)\). By (4),

\[
x+\frac{\omega_n}{B_{p,n}}y
\]

is feasible for the nearby program, where \(B_{p,n}=\operatorname{kl}(p_n,1/2)\) stays positive. This proves \(\limsup_n K(h_n,a_n)\le K(h,\alpha)\). Nearby optimizers are bounded by (6); every convergent subsequence has a feasible limit at the true parameters, so the reverse liminf inequality holds. Every such limit is optimal.

Let

\[
\mathcal W=
\{x/K:x\text{ is optimal in (2) at }(h,\alpha)\}.
\tag{7}
\]

This is a nonempty compact convex subset of the action simplex: the feasible set is convex and every optimizer has the same total count \(K\). The preceding argument implies the following precise stability property. For every \(\rho>0\), sufficiently accurate levels, correct discrete labels, and an offline ratio sufficiently close to \(\alpha\) ensure that **every** normalized optimal allocation lies within \(\rho\) of \(\mathcal W\) in \(\ell_1\) distance. No continuity of a chosen optimizer is required.

### 3.2 Every feasible allocation supplies positive online information

Define

\[
\chi=
\min_{r\in\{p,q\}:r>1/2}
\frac{\operatorname{kl}(r,1/2)}{\operatorname{kl}(r,1-r)}>0.
\tag{8}
\]

If \(q=1/2\), its numerator and denominator both vanish; it is omitted from this minimum. The set always contains \(p\).

Consider any wrong-sign alternative and a coordinate \(j\) that it flips. On each format of this coordinate, the alternative probability of the true sign is at most \(1/2\). Since \(\operatorname{kl}(r,x)\) is minimized over \(x\le1/2\) at \(x=1/2\) when \(r\ge1/2\), (5) implies

\[
\begin{aligned}
J_h(x,h')
&\ge x_{j,z_{g(j)}}\operatorname{kl}(p,1/2)
   +x_{j,3-z_{g(j)}}\operatorname{kl}(q,1/2)\\
&\ge\chi\left(x_{j,z_{g(j)}}A_p
             +x_{j,3-z_{g(j)}}A_q\right)
\ge\chi.
\end{aligned}
\tag{9}
\]

In particular, with \(\lambda_0=\chi/K>0\), every \(w\in\mathcal W\) satisfies

\[
\alpha D_0(h,h')+KJ_h(w,h')\ge1,
\qquad J_h(w,h')\ge\lambda_0
\quad\forall h'\in\mathcal H_{\ne\theta}.
\tag{10}
\]

The second inequality gives a strict information margin when the online horizon exceeds \(KR\), even for alternatives whose constraint in (2) is tight.

## 4. The policy and its uniform error guarantee

The policy uses the estimator and allocation program in Section 4.2 of the source note. The following choices make its exploration schedule explicit.

Enumerate the \(L=2d\) task streams. For every integer \(k\ge0\), use rounds

\[
Lk^2+1,\ldots,Lk^2+L
\]

to sample each task stream once. These blocks are disjoint. Each task stream receives at least \(c\sqrt t\) forced observations by time \(t\) for all sufficiently large \(t\), and the total number \(F(t)\) of forced rounds is \(O(\sqrt t)\).

Before each other round \(s\), use only earlier forced observations to estimate the signs, group formats, and common levels as in the note. Fix a sequence of finite grids in the strict domain whose covering radii over the compact closure tend to zero as \(s\to\infty\). Project the levels onto the round-\(s\) grid, choosing a nearest grid point and breaking ties deterministically. Choose any fixed measurable optimal-solution rule for (2), evaluated at the estimates and \(a=\alpha_\delta\). Sample from its normalized action counts. The stopping likelihood uses the full continuous parameter domain and all observed data.

Let \(\mathcal F_s\) include the offline data and the first \(s\) online observations. All action probabilities are \(\mathcal F_{s-1}\)-measurable. For analysis, extend the same sampling rule past the first stopping time.

At each online time, profile the likelihood over the nuisance parameters for each sign vector and apply the note's stopping boundary

\[
\beta(t,\delta)
=R+2\log(M_\delta+1)
    +\sum_{e\in\mathcal A}\log(N_e(t)+1).
\tag{11}
\]

To verify error control, integrate an unrestricted Bernoulli mean on each stream against a uniform prior, producing likelihood \(Q_t\). For a stream with \(n\) observations and \(s\) successes,

\[
\sup_{\mu\in[0,1]}\mu^s(1-\mu)^{n-s}
\le(n+1)B(s+1,n-s+1).
\]

The full model likelihood is bounded by the product of these saturated maxima. A wrong stop therefore implies \(Q_t/L_t(h)\ge1/\delta\). Including the initial offline sampling period, this ratio is a nonnegative mean-one martingale: the predictable action probabilities cancel in each likelihood ratio. Ville's inequality gives error probability at most \(\delta\), uniformly over the full model. The stopping-time bounds below establish finite expectation and hence almost-sure termination.

## 5. A uniform bound for realized allocation counts

For any fixed parameter tolerance \(\zeta>0\), the forced-data estimator satisfies

\[
\mathbb P_h\{\widehat\theta_s\ne\theta
\text{ or }\widehat z_s\ne z
\text{ or }\|\widehat r_s-r\|>\zeta\}
\le C_\zeta e^{-c_\zeta\sqrt s}
\tag{12}
\]

for sufficiently large \(s\), with constants independent of \(\delta\). Indeed, each empirical task mean has at least \(c\sqrt s\) fresh observations. Hoeffding's inequality controls all of them. The sign estimator is separated from zero by \(p+q-1>0\); conditional on correct signs, each group-format comparison is separated by \(p-q>0\). Averaging estimates the levels, and a nearest-point grid projection adds an error tending to zero. This reasoning also applies when \(q=1/2\) or \(p=1-\eta\).

Fix a small number \(a>0\). We claim that, for all sufficiently small \(\delta\) and all sufficiently large horizons \(t\),

\[
\mathbb P_h\left\{
\inf_{w\in\mathcal W}\|N(t)/t-w\|_1>a\right\}
\le C t e^{-c\sqrt t}.
\tag{13}
\]

Here and below, constants may depend on \(a\) and the true instance, but are uniform over these \(t,\delta\).

To prove (13), choose small fixed \(\gamma,\rho>0\). By Section 3.1, there is an estimation tolerance such that every exploitation distribution is within \(\rho\) of \(\mathcal W\) once the estimates meet that tolerance and \(\alpha_\delta\) is sufficiently close to \(\alpha\). Apply (12) at all rounds between \(\lfloor\gamma t\rfloor\) and \(t\). The probability of any failure is at most

\[
C t e^{-c\sqrt{\gamma t}}.
\tag{14}
\]

Let \(\pi_s\) be the predictable action distribution at round \(s\), including a unit vector on forced rounds. On the complementary event, approximate each late exploitation distribution by a point of \(\mathcal W\). Approximate the earlier and forced distributions by any point of \(\mathcal W\), at \(\ell_1\) cost at most two each. Convexity of \(\mathcal W\) then gives

\[
\inf_{w\in\mathcal W}
\left\|\frac1t\sum_{s=1}^t\pi_s-w\right\|_1
\le\rho+2\gamma+2F(t)/t+O(1/t).
\tag{15}
\]

For each action, \(N_e(t)-\sum_{s\le t}\pi_{s,e}\) is a martingale with bounded increments. Azuma's inequality and a union bound give

\[
\mathbb P_h\left\{
\left\|N(t)-\sum_{s=1}^t\pi_s\right\|_1>\rho t
\right\}\le C e^{-c_\rho t}.
\tag{16}
\]

Choose \(\rho,\gamma\) so that \(2\rho+2\gamma<a\), and use \(F(t)/t\to0\). Equations (14)–(16) prove (13). They allow the optimal allocation to jump between different optimizers at every round.

## 6. A linear information margin beyond the design horizon

Fix \(\varepsilon>0\), and consider every integer

\[
t\ge(K+\varepsilon)R.
\]

Set \(b_\varepsilon=\varepsilon/(K+\varepsilon)>0\). For every \(w\in\mathcal W\), (10) implies, uniformly over wrong-sign alternatives,

\[
\begin{aligned}
M_\delta D_0(h,h')+tJ_h(w,h')
&\ge R+(t-KR)\lambda_0
       -|\alpha_\delta-\alpha|RA_*\\
&\ge R+\lambda_0 b_\varepsilon t
       -|\alpha_\delta-\alpha|RA_*.
\end{aligned}
\tag{17}
\]

Choose the allocation tolerance \(a\) in (13) so that
\(D_*a\le\lambda_0b_\varepsilon/4\). For sufficiently small \(\delta\), also

\[
|\alpha_\delta-\alpha|A_* /(K+\varepsilon)
\le\lambda_0b_\varepsilon/4.
\]

On the event in (13) where the allocation error is at most \(a\), equations (3) and (17) give

\[
\boxed{\displaystyle
\inf_{h'\in\mathcal H_{\ne\theta}}
\left\{M_\delta D_0(h,h')+
       \sum_e N_e(t)D_e(h,h')\right\}
\ge R+c_0t,}
\qquad c_0=\lambda_0b_\varepsilon/2>0.
\tag{18}
\]

This inequality retains the offline term and holds at all later horizons. A rate of convergence for \(\alpha_\delta\to\alpha\) is unnecessary.

## 7. Uniform likelihood concentration over the continuous alternatives

For each stream, let \(S_e(t)\) be its success count and set

\[
Z_e(t)=S_e(t)-N_e(t)\mu_e(h).
\]

For the two offline streams use their fixed count \(N_e=M_\delta\). The Bernoulli log-likelihood identity gives, for every alternative simultaneously,

\[
\begin{aligned}
\log\frac{L_t(h)}{L_t(h')}
={}&M_\delta D_0(h,h')+
       \sum_{e\in\mathcal A}N_e(t)D_e(h,h')\\
&+\sum_{e\in\mathcal A\cup\{p\text{-ref},q\text{-ref}\}}
Z_e(t)\bigl[\operatorname{logit}\mu_e(h)
             -\operatorname{logit}\mu_e(h')\bigr].
\end{aligned}
\tag{19}
\]

Thus the supremum of the absolute centered likelihood error over all alternatives is at most

\[
L_*\sum_e|Z_e(t)|.
\tag{20}
\]

For each online stream, \(Z_e(t)\) is a martingale sum of \(t\) bounded increments. Each offline residual is a sum of \(M_\delta\) independent centered bounded variables. At the horizons under consideration,

\[
M_\delta/t\le\alpha_\delta/(K+\varepsilon)
\]

is uniformly bounded for sufficiently small \(\delta\). Azuma/Hoeffding bounds, followed by a union bound over the fixed number of streams, therefore give

\[
\mathbb P_h\left\{L_*\sum_e|Z_e(t)|>c_0t/2\right\}
\le C e^{-ct}.
\tag{21}
\]

An offline stream with \(M_\delta=0\) has zero residual. The bound applies to all continuous alternatives through the exact identity (19); no parameter mesh is needed.

Combining (13), (18), and (21), except on an event of probability at most \(Ct e^{-c\sqrt t}\),

\[
\inf_{h'\in\mathcal H_{\ne\theta}}
\log\frac{L_t(h)}{L_t(h')}
\ge R+c_0t/2.
\tag{22}
\]

The profiled likelihood for the true sign vector is at least \(L_t(h)\). Equation (22) therefore gives the same lower bound for its profile-likelihood gap over all wrong sign vectors.

## 8. Summing the stopping-time tail

Since \(M_\delta\le Ct\) at these horizons, the boundary overhead in (11) satisfies

\[
\beta(t,\delta)-R
\le2\log(Ct+1)+m\log(t+1)=O(\log t),
\tag{23}
\]

uniformly for sufficiently small \(\delta\). For all sufficiently large \(t\), this is smaller than \(c_0t/2\). Hence (22) implies that the rule has stopped by \(t\). There exist constants \(C,c>0\) and \(\delta_0>0\), depending on the fixed instance and \(\varepsilon\), such that

\[
\boxed{\displaystyle
\mathbb P_h(\tau_\delta>t)\le Ct e^{-c\sqrt t}
\quad\text{for every }0<\delta<\delta_0,
\quad t\ge\lceil(K+\varepsilon)R\rceil.}
\tag{24}
\]

To pass to expected time, put \(T=\lceil(K+\varepsilon)R\rceil\) and use the tail-sum formula:

\[
\mathbb E_h\tau_\delta
\le T+C\sum_{t=T}^{\infty}t e^{-c\sqrt t}.
\tag{25}
\]

For large \(T\), the summand is decreasing. The substitution \(u=\sqrt x\) gives

\[
\int_T^\infty x e^{-c\sqrt x}\,dx
=2e^{-c\sqrt T}
\left(\frac{T^{3/2}}c+\frac{3T}{c^2}
      +\frac{6\sqrt T}{c^3}+\frac6{c^4}\right).
\tag{26}
\]

Consequently the sum in (25) is \(o(1)\), and

\[
\limsup_{\delta\downarrow0}
\frac{\mathbb E_h\tau_\delta}{R}\le K+\varepsilon.
\]

Letting \(\varepsilon\downarrow0\) proves (1).

For completeness, finite expectation also holds at each fixed \(\delta\) outside the asymptotic range. Redo Sections 3–7 with \(a=\alpha_\delta\) as the fixed reference ratio and its optimal value \(K_\delta\). The allocation policy uses exactly that ratio, so no ratio-approximation error appears. At all sufficiently large horizons \(t\ge(K_\delta+1)R\), the same reasoning gives a summable bound \(Ct e^{-c\sqrt t}\), with constants now allowed to depend on this fixed \(\delta\). Equation (25), with a larger finite starting horizon if needed, proves \(\mathbb E_h\tau_\delta<\infty\).

This completes the expected-time achievability proof. \(\square\)

## 9. What the expansion adds to Section 4.3

The upper-bound claim in the source note holds. The proof above expands its compressed steps and makes two corrections explicit: at the design horizon, the information lower bound is \(R-|\alpha_\delta-\alpha|RA_*\), and finite expectation for each fixed \(\delta\) requires the final fixed-ratio argument in Section 8. Four facts carry the proof:

1. Uniform task sampling gives local strict feasibility, which establishes stability of the full optimal set, including boundary true parameters.
2. The single-coordinate constraints give the explicit positive online-information constant in (8)–(10).
3. The offline and online terms together yield the margin in (18), uniformly over every horizon beyond \((K+\varepsilon)R\).
4. The finite-stream identity (19) gives uniform likelihood concentration, and the summable tail (24) proves the expectation bound.

This proves the leading-order statement \(KR+o(R)\). An explicit power-law remainder would additionally require quantitative control of optimal-allocation stability and of \(\alpha_\delta-\alpha\).
