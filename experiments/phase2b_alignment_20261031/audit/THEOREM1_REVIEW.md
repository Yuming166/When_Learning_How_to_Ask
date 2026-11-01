# Independent Theorem 1 review: expected time and proof-to-code conditions

## Material Passport and verdict

- Date: 2026-10-31. Scope: the historical `Theory_Note.md`, especially Theorem 1 and Section 4.3. Source SHA256: `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef`.
- Provenance: a separate reviewer role in the same model family, with historical Phase 2a context. No new peer proof draft was read before deriving this report. This is not an independent-model review, human review, or machine-checked proof.
- Actions: source reading and mathematical derivation only. No private seeds, trajectory experiments, model/API/GPU calls, or historical file changes. No numerical script was needed.
- Verdict on the historical text: **the displayed expected-time tail is not sufficiently justified as written**. In particular, its sentence about offline concentration does not itself establish a bound uniform over all later t for a fixed delta. This is a proof gap, not a counterexample to the claimed coefficient.
- Verdict on the mathematical claim: **a complete repair is available under the explicit ideal policy conditions below**. The repair handles alpha=0, q=.5, p=1-eta, nonunique allocations, the stated delayed updates, and deterministic deficit tracking. It does not establish that a floating implementation with a fixed numerical error floor attains the exact limiting coefficient.

The source makes a pointwise claim at each fixed true p>q, with d, the partition, eta, and any finite known type-query accuracies fixed. Nothing below is uniform as p-q tends to zero, d grows, eta tends to zero, or a type-query accuracy tends to one. See the [model and pointwise qualification](../../../Theory_Note.md:13), [Theorem 1 statement](../../../Theory_Note.md:97), and [historical expected-time argument](../../../Theory_Note.md:215).

## 1. Exact statement that the repair supports

Let 0<delta<1/2, R=log(1/delta), M=M_delta, alpha_delta=M/R -> alpha<infinity. Let K=K_{S,alpha} at a fixed true state h=(theta,z,p,q), with .5<=q<p<=1-eta. Optional type reports have fixed known s_g in (.5,1). All observations are fresh and conditionally independent given their action streams, as in the [source model](../../../Theory_Note.md:7).

Assume the following operational conditions.

1. Every task stream receives deterministic forced observations F_e(t)>=c_F sqrt(t)-C_F. Total forced observations obey F(t)<=C'_F sqrt(t)+C''_F. The constants do not depend on delta.
2. The forced-only estimator of [Section 4.2](../../../Theory_Note.md:202), or an estimator with the same proved concentration property, is used. For every fixed accuracy a>0, its probability of a sign/type error or level error>a is at most C_a exp(-c_a sqrt(u)) at estimator time u. Its grid approximation error tends to zero under a deterministic modulus independent of delta.
3. At an update u the allocation oracle returns x>=0 whose constraint residual is at most e(u), and whose cost is at most K(estimated p,q,alpha_delta)+e(u), where e(u)->0. Relative optimality tolerances are also sufficient when they imply this local absolute bound. The bounds must be actual mathematical bounds, not merely requested stopping tolerances.
4. Updates are predictable, and the most recent update U(t) satisfies U(t)>=t-C sqrt(t+1)-C for all large t, uniformly in delta. Held targets use the same fixed alpha_delta throughout that run. The proposed rule u_next=u+ceil(sqrt(u+1)) satisfies this condition.
5. Each returned allocation is normalized by its actual total online cost, expanded to actual actions, and mapped using the estimated current types. Counts track the cumulative normalized targets with discrepancy o(t), uniformly in delta. The deterministic rule in Section 6 proves a stronger O(sqrt(t)) discrepancy for the stated candidate implementation.
6. The stopping statistic is the exact joint profile GLR of [Section 4.1](../../../Theory_Note.md:161), with all available streams in its boundary. Stopping is checked every round, or with a deterministic gap o(t), uniformly in delta. A conservative numerical certificate is sufficient for error control only if its inequalities are proved in the correct directions; a generic approximate GLR is not enough.

Then the policy is uniformly delta-correct, stops with finite expectation at every fixed admissible state, and

\[
\limsup_{\delta\downarrow0}\frac{\mathbb E_h\tau_\delta}{R}
\le K_{\mathcal S,\alpha}.
\]

Together with the source lower bound, this gives the asserted leading coefficient. Sections 2–9 prove the upper bound and specify the uniformity required for the expectation argument. This result is conditional on the listed policy properties; it is not a claim that each property has been verified for the executable code.

## 2. Local allocation stability, including all three boundary cases

Use the actual online action set E, of size m=2d or 2d+G. Let x denote the grouped count vector of the source program. Let T expand a grouped allocation into actual action counts, including one type count per group when allowed. Its cost is

\[
c^\top x=\boldsymbol 1^\top Tx.
\]

For a wrong-sign alternative h', define D_0(h')=D(p,u)+D(q,v), and let J_{h'}(x) be its online KL information at grouped counts x. The information constraints can be written

\[
I_\xi(x):=\inf_{h':\theta'\ne\theta}
\{\alpha D_0(h')+J_{h'}(x)\}\ge1,
\qquad \xi=(p,q,\alpha).
\]

Here the alternative set is a finite union, over signs and types, of the fixed compact triangle .5<=v<=u<=1-eta. It can equally be represented by the source's finite one-flip constraints. This representation follows from the [information program and reduction](../../../Theory_Note.md:71). The discussion below does not require uniqueness of any inner minimizer.

**Lemma 2.1: uniform separating direction.** There is a relative neighborhood V of the fixed true xi, and b>0, such that the allocation v giving one count to every task stream and zero to every type stream satisfies

\[
\inf_{h':\theta'\ne\theta}J_{h'}(v)\ge b,
\qquad \xi'\in V.
\]

**Proof.** Choose p_min>.5 below the true p and restrict nearby parameters to p'>=p_min. Any wrong-sign alternative reverses at least one coordinate j. At its true good-format task stream, the true probability of the true sign is p', whereas the alternative probability is at most .5, regardless of its type. That stream contributes at least D(p_min,.5)>0. Take b=D(p_min,.5). All other stream KL terms are nonnegative. The argument does not use alpha>0, q>.5, or p<1-eta. It therefore works at alpha=0, q=.5, and p=1-eta in relative neighborhoods of the stated parameter domain. QED.

For every nearby parameter and x>=0,

\[
I_{\xi'}(x+av)\ge I_{\xi'}(x)+ab,\quad a\ge0.
\]

Consequently v/b is uniformly feasible, and 2v/b has a strict constraint margin. This supplies the missing local Slater argument without relying on positive calibration information.

**Lemma 2.2: existence, continuity, and upper hemicontinuity.** The optimal value K(xi) is positive and continuous at the fixed state, the optimizer set X*(xi) is nonempty and compact, and optimizers at nearby xi' approach X*(xi).

**Proof.** The direction above gives a common finite upper bound on the cost. Positive query costs make every bounded-cost sublevel compact. Joint continuity of I_xi(x) follows from uniform continuity of the KL objective on the compact alternative domain, locally bounded x, and a finite number of discrete patterns.

For positivity, set A_r=D(r,1-r). An alternative with the same true types and levels, changing only coordinate j's sign, has no offline or type-query KL. It forces

\[
a_{g(j)}A_p+b_{g(j)}A_q\ge1.
\]

Since A_q<=A_p<infinity, summing over coordinates gives cost>=d/A_p>0. This also gives a uniform positive lower bound locally. Compactness then yields attainment.

For continuity from above, take x* optimal at xi, and let

\[
d_n=(1-I_{\xi_n}(x^*))_+\longrightarrow0.
\]

Then x*+(d_n/b)v is feasible at xi_n, so limsup K(xi_n)<=K(xi). For continuity from below, take nearby optimizers x_n. The common cost bound gives a convergent subsequence x_n->x. Joint continuity gives I_xi(x)>=1, and hence K(xi)<=c^T x=lim K(xi_n). This proves value continuity. The same subsequence argument shows that every optimizer cluster point is a true optimizer, which is precisely the required upper hemicontinuity on a common compact set. QED.

**Approximate-oracle extension.** The same proof applies to x_n satisfying I_{xi_n}(x_n)>=1-e_n and c^T x_n<=K(xi_n)+e_n with e_n->0. Any cluster point is feasible and has cost K(xi), so its distance to X*(xi) vanishes. This is the condition that links approximate computation to the theorem. A fixed e_n=e_0>0 does not provide this conclusion.

## 3. The normalized optimizer set is convex

The feasible set is convex because each information constraint is an infimum of affine functions of x and thus is concave in x. Therefore

\[
X^*=\{x\ge0:I_\xi(x)\ge1,\ c^\top x=K\}
\]

is compact and convex. Since K>0 is the same number for all members, the normalized actual-action set

\[
W^*=\{Tx/K:x\in X^*\}
\]

is a compact convex subset of the probability simplex. This verifies, rather than assumes, the normalization claim at [source line 219](../../../Theory_Note.md:219). Normalizing arbitrary allocations with different costs would not be a linear operation and would not justify this argument.

The approximate-oracle extension and positivity of the local cost imply that if the estimated discrete state is correct, estimated levels approach the true ones, alpha_delta approaches alpha, and e(u)->0, then the actual normalized target approaches W*. No unique optimizer or continuous tie-breaking rule is needed.

## 4. An explicit strictly positive online information margin

Let

\[
A_r=D(r,1-r),\qquad B_r=D(r,.5),\qquad
r_* =\min_{r\in\{p\}\cup\{q:q>.5\}}\frac{B_r}{A_r}>0.
\]

The q=.5 term is omitted because A_q=B_q=0. This is a boundary convention, not division by zero. The p term is always present because p>q>=.5. The assumed upper bound p<=1-eta ensures the denominators are finite.

The same-type/true-level alternative in Lemma 2.2 implies a_g A_p+b_g A_q>=1 for every group. Hence

\[
a_gB_p+b_gB_q\ge r_*.
\]

Every wrong-sign alternative reverses some coordinate j. At the true good and other task streams for j, its probabilities of the true sign are <=.5, so those streams contribute at least a_g B_p+b_g B_q. Type information and all other streams are nonnegative. Thus

\[
\inf_{x\in X^*,\ h':\theta'\ne\theta}J_{h'}(x)\ge r_*,
\qquad
\inf_{w\in W^*,\ h':\theta'\ne\theta}J_{h'}(w)
\ge\mu:=r_*/K>0.
\]

This proves the assertion at [source lines 223–229](../../../Theory_Note.md:223) with an explicit margin, including q=.5. Compactness alone would not be a proof without first ruling out a zero-information point. In fact the inequality holds for every feasible grouped x before normalization, not merely an optimizer.

## 5. Forced-only estimation, delayed updates, and Cesaro averaging

For any fixed admissible true parameter, sign recovery uses the positive gap p+q-1, and type recovery uses p-q. Coordinate empirical probabilities based only on forced observations obey Hoeffding bounds with at least c_F sqrt(u)-C_F samples. A finite union over streams therefore gives, for every fixed accuracy a>0,

\[
\Pr(\text{wrong discrete estimate or level error}>a)
\le C_a e^{-c_a\sqrt u}
\]

for all large u. Clipping/projection at q=.5 or p=1-eta preserves consistency when the grid approaches these boundaries. One must specify that the grid actually approximates the full relative domain. No positive q-.5 gap is needed.

For the held-update rule u_next=u+ceil(sqrt(u+1)), an estimate used at time s has age at most sqrt(s+1)+1. In particular U(s)>=s/2 for all sufficiently large s. A finite union over late update times gives, for each fixed rho>0,

\[
\Pr(\exists s\in[\rho t,t]:
\text{estimate used at s is outside a fixed good neighborhood})
\le C t e^{-c\sqrt t}.
\]

The constants may depend on rho and the true gaps. They do not depend on delta. Deterministic grid and allocation errors are small for all these late updates once t is large, and alpha_delta is in the needed neighborhood for all small delta. Lemmas 2–3 then put every late target within any prescribed a>0 of W*.

Let C(t)=sum_{s<=t}w_s be the cumulative actual-action targets, including forced rounds if that is the implementation convention. Since the simplex has L1 diameter 2 and W* is convex, on this event

\[
\operatorname{dist}_1(C(t)/t,W^*)\le2\rho+a.
\]

Choose a nearby point of W* for each late target and any fixed point of W* for the early targets; their average is in W*. This gives the displayed bound pathwise. It is the missing explicit justification for the [Cesaro assertion](../../../Theory_Note.md:221).

The original randomized sampler adds a martingale count-deviation term with exp(-ct) tails. The deterministic deficit rule below needs no action-randomization concentration. Estimation still has a stochastic error event.

**Uniformity qualification.** It is insufficient to show e_{delta,u}->0 separately for each fixed delta. For example an oracle could remain inaccurate until u=exp(R_delta) and become exact thereafter. That is pointwise convergence in u but gives no theorem at u proportional to R_delta. An error modulus e(u) independent of delta, such as min(1e-4,1/(u+1)), avoids this diagonal problem. The grid, update-age, and tracking bounds need the same uniform interpretation.

## 6. The communicated deterministic tracking variant

This section proves the protocol described to the reviewer. It is not an executable-code inspection.

Let L=2d. Force one query to each task stream in the block t=L n^2+s, 0<=s<L, for n=0,1,2,..., with harmless shifts for one-based indexing. Completed blocks give, up to fixed endpoint constants,

\[
F_e(t)\ge\sqrt{t/L}-1,\qquad
F(t)\le\sqrt{Lt}+L.
\]

Thus both the estimator rate and vanishing forced fraction required above hold with constants independent of delta.

At every round first set C(t)=C(t-1)+w_t. On an unforced round choose an action maximizing C_e(t)-N_e(t-1); on a forced round choose the prescribed task stream. Let A(t)=N(t)-C(t), so sum_e A_e(t)=0. Before the action, B=A(t-1)-w_t has sum -1.

On an unforced round the chosen action minimizes B, so B_chosen<=-1/m and its post-action value is B_chosen+1<1. All unchosen coordinates satisfy A_e(t)=A_e(t-1)-w_{t,e}<=A_e(t-1). A forced round can raise the maximum coordinate by at most one. Starting at zero therefore gives

\[
\max_e A_e(t)\le1+F(t),\qquad
\min_e A_e(t)\ge-(m-1)(1+F(t)),
\]

and, using sum A=0,

\[
\|N(t)-C(t)\|_1\le2(m-1)(1+F(t))=O(\sqrt t).
\]

This proof allows arbitrary predictable changing targets. It does not need the targets themselves to vary smoothly, and it covers type actions that are never forced. Normalizing by t and combining with Section 5 gives, for every fixed a>0, constants independent of delta such that

\[
\Pr\{\operatorname{dist}_1(N(t)/t,W^*)>a\}
\le C t e^{-c\sqrt t}
\]

for all sufficiently large t and sufficiently small delta. This is the allocation event used below.

Keeping a separate exploitation count and cumulative exploitation target would yield a bounded discrepancy before adding forced counts. That is also valid, but the proof above matches the communicated all-round-target convention directly.

## 7. Predictable information has a margin proportional to the full horizon

For a fixed wrong-sign alternative h', write its predictable log-likelihood-ratio drift as

\[
D_t(h')=M D_0(h')+\sum_e N_e(t)d_e(h').
\]

It is a random predictable compensator through the action counts, not an unconditional expected value conditional on a hand-picked allocation event. All stream divergences are bounded by some D_max<infinity, and D_0<=D_{0,max}<infinity.

Fix epsilon>0, set lambda=K+epsilon, and let t>=lambda R. On the allocation event, choose w in W* with ||N(t)/t-w||_1<=a. Feasibility and Section 4 give

\[
\begin{aligned}
D_t(h')
&\ge R\{\alpha D_0(h')+KJ_{h'}(w)\}
 +(t-KR)J_{h'}(w)
 -R|\alpha_\delta-\alpha|D_{0,\max}-tD_{\max}a\\
&\ge R+\frac{\epsilon\mu}{\lambda}t
 -\frac{|\alpha_\delta-\alpha|D_{0,\max}}{\lambda}t
 -D_{\max}at.
\end{aligned}
\]

Choose a so D_max a<=epsilon mu/(4lambda), and then delta small enough that |alpha_delta-alpha|D_{0,max}<=epsilon mu/4. Uniformly for **every** wrong-sign alternative and **every** t>=lambda R,

\[
D_t(h')\ge R+\gamma t,
\qquad\gamma=\epsilon\mu/(2\lambda)>0.
\]

This horizon-proportional slack is the important strengthening of the source's argument at the single time (K+epsilon)R. It remains useful for arbitrarily later horizons, where R is fixed but t grows.

## 8. Combined offline/online concentration: the repair

### 8.1 Why a separate fixed-tolerance offline event fails

For fixed delta and finite M>0, the event that an offline empirical mean differs from p by a fixed positive tolerance generally has positive probability that is constant in t. It therefore cannot be bounded for all later t by C t^a exp(-c sqrt(t)), which tends to zero. Conditioning permanently on that event being absent cannot justify summing a horizon-uniform tail.

This is the unresolved step in the historical sentence [“their concentration errors fit the same bound”](../../../Theory_Note.md:240) if it is interpreted as fixed-tolerance offline-mean concentration. The sentence can be repaired by the different argument below; it should not be presented as an already supplied derivation.

### 8.2 One martingale over the entire transcript

Let rho_0=min(eta,min_g(1-s_g))>0, omitting the type term if no type actions exist. All true and alternative Bernoulli probabilities lie in [rho_0,1-rho_0]. Set B=log((1-rho_0)/rho_0). Every observation log-likelihood-ratio increment is bounded in absolute value by B; its centered increment is bounded by 2B.

Process the 2M offline observations first, then the t online observations. For any fixed alternative h',

\[
Z_t(h')=\log\frac{L_t(h)}{L_t(h')}-D_t(h')
\]

is the sum of bounded martingale differences along this entire sequence. Online actions are predictable, so centering by their action-specific KL is valid. For the fixed-horizon argument, continue the prescribed sampler, forced schedule, estimator, and target updates while ignoring the stopping decision. This extension preserves the allocation estimates; it is not an arbitrary post-stopping action sequence.

For all small delta, M<=(alpha+1)R. For t>=lambda R,

\[
2M+t\le C_0t,\qquad C_0=1+2(\alpha+1)/\lambda.
\]

Applying Azuma at deviation gamma t/4 gives

\[
\Pr\{Z_t(h')\le-\gamma t/4\}
\le\exp\{-\gamma^2t/(128B^2C_0)\}.
\]

Thus the offline part does not need a t-dependent fixed-tolerance accuracy event. The relevant tolerance is proportional to t for the **combined centered sum**. When t is much larger than M, the fixed offline fluctuation is automatically small relative to this tolerance.

### 8.3 Uniformity over continuous alternatives and the stopping boundary

For each discrete wrong-sign/type pattern, cover the alternative triangle with an infinity-norm mesh of size t^-2. Its cardinality is O(t^4). The number of discrete patterns is fixed. Each observation log likelihood has derivative in its relevant level bounded by 1/rho_0, so replacing levels by a nearby mesh point changes the whole log likelihood by at most

\[
(2M+t)t^{-2}/\rho_0\le C_0/(\rho_0t).
\]

A union bound over the net therefore controls all centered likelihood ratios with failure probability C t^4 exp(-c t), and interpolation controls the full continuous alternative set. This proof uses the bounded upper probability assumption; it is not valid unchanged with eta=0 or perfect type reports.

The exact boundary satisfies

\[
\beta(t,\delta)-R
\le m\log(t+1)+2\log(M+1)=O(\log t)
\]

uniformly on these horizons. For all sufficiently large R, this is <=gamma t/4 **for every** t>=lambda R. One may use that log(t)/t decreases after a fixed constant. Combining the allocation event, the drift margin, concentration, and interpolation gives

\[
\inf_{h':\theta'\ne\theta}\log\frac{L_t(h)}{L_t(h')}
>\beta(t,\delta)
\]

except on an event with probability at most C t^A exp(-c sqrt(t)), where C,A,c do not depend on delta or t. Since the correct-sign profile likelihood is at least L_t(h), this condition makes the correct sign vector the unique winner and meets the exact GLR stopping rule.

Hence, for every fixed epsilon>0 there are R_0,C,A,c such that

\[
\boxed{\Pr_h(\tau_\delta>t)\le C t^A e^{-c\sqrt t},
\quad R\ge R_0,\quad t\ge\lceil(K+\epsilon)R\rceil.}
\]

All quantifiers in this display are necessary for the expectation conclusion. For non-every-round stopping checks with gap o(t), apply the proof at the last checked time and use a smaller internal epsilon, for example epsilon/2. A geometric stopping-check schedule can retain a nonvanishing multiplicative delay and is not covered by the exact leading-coefficient conclusion. Geometric **parameter updates** are a different matter: their estimates can still be consistent quickly enough. The communicated O(sqrt(t)) update gaps cause no difficulty.

## 9. Summing the tail, admissibility, and the lower bound

Put T=ceil((K+epsilon)R). The tail bound gives

\[
\mathbb E_h\tau_\delta
\le T+C\sum_{t\ge T}t^A e^{-c\sqrt t}.
\]

The sum is bounded by a constant times a polynomial in sqrt(T) times exp(-c' sqrt(T)). For example substitute u=sqrt(t) in the integral comparison, giving 2 integral_{sqrt(T)-1}^infinity u^{2A+1} exp(-cu) du; repeated integration by parts supplies the claimed polynomial bound. Consequently the tail sum is o(1), and in particular o(R). Therefore

\[
\limsup_{\delta\downarrow0}\mathbb E_h\tau_\delta/R\le K+\epsilon.
\]

Let epsilon decrease to zero after this bound. This proves the required limsup.

To ensure the policy is admissible also for delta values outside the asymptotic range, fix any delta, hence fix alpha_delta<infinity and M. Apply the same stability and online-margin arguments with that fixed alpha_delta. At large t its target has strictly positive online information rate, while the boundary is R+O(log t), and 2M+t=O(t). The same combined concentration yields a summable tail after a delta-dependent finite threshold. Thus the policy stops almost surely with finite expectation at every fixed admissible state and every fixed delta in the stated range. No delta-uniform constants are required for this last, fixed-delta admissibility statement.

The anytime error control is logically separate: the source's [saturated Beta-mixture likelihood argument](../../../Theory_Note.md:182) remains valid for predictable randomized or deterministic actions. Offline observations must be regarded as the initial segment of the martingale, so its mean-one initialization is before those observations. This gives unconditional error control over offline and online randomness, as the [model requires](../../../Theory_Note.md:37), rather than a guarantee conditional on every realized offline data set.

The [source change-of-measure lower bound](../../../Theory_Note.md:106) applies to any admissible policy. If expected cost is finite, bounded per-observation likelihood ratios justify the stopped KL decomposition. Dividing by R and taking bounded-count subsequences gives feasibility of the coefficient program; unbounded costs are immediate. Alternatives on the closure are obtained by continuity from admissible strict-level alternatives. Thus the liminf bound combines with the repaired limsup to give K R+o(R).

## 10. What is closed and what remains a code-level obstruction

| Question | Independent mathematical assessment |
|---|---|
| Stability at alpha=0 | Closed by the all-task separating direction; no positive offline Slater term is required. |
| q=.5 and p=1-eta | Closed in relative neighborhoods. The online ratio omits q's 0/0 term; p>.5 and eta>0 are essential. |
| Nonunique optimizer | Closed using compact convex X*, common K, and convex normalized W*. |
| Positive online margin | Closed explicitly by r*/K. |
| Uniform tail for all t>=(K+epsilon)R | Closed by combined offline/online martingale concentration at deviation proportional to t. A fixed-tolerance offline-good event is insufficient. |
| Tail summation to expected time | Closed once constants are uniform in delta; the tail remainder is polynomial times exp(-c sqrt(R)). |
| Held O(sqrt(t)) updates | Compatible with the proof and estimator concentration. |
| All-round cumulative deterministic deficits | Compatible; discrepancy <=2(m-1)(1+F(t)) in L1. |
| Vanishing approximate allocation error | Compatible if both actual feasibility and actual optimality errors obey a deterministic delta-uniform vanishing modulus. |
| Fixed or saturated float error floor | Does not establish the exact limiting coefficient. It can support bounded finite-prefix numerical statements or a separately quantified approximate coefficient. |
| Three fixed iterations of an unproved estimator | No consistency or concentration conclusion follows merely from iteration count. A proved estimator or a new proof is required. |
| Generic approximate GLR | No original anytime error guarantee follows without conservative bounds. |
| Actual current executable alignment | Not inspected by this report; conditions and communicated protocols above are not a source-code certification. |

The historical numerical solver itself explicitly describes its bounds as floating rather than interval certificates; see its [scope statement](../../phase2a_theory_optimality_20261030/phase2a/coefficients.py:1). Requesting e(u)=min(1e-4,1/(u+1)) is mathematically appropriate, but cannot make a fixed floating backend deliver arbitrarily small certified errors. This distinction should appear next to any theorem-to-code claim. A finite run can document all obtained residuals, gaps, and solver failures; it cannot establish an infinite-horizon vanishing-error property by extrapolation.

The report supports replacing the historical Section 4.3 sketch with the explicit lemmas above. It supports a theorem for the precisely stated ideal policy and a conditional alignment theorem for implementations that meet those properties. It does not support calling numerical convergence plots a proof, or calling the finite floating executable an already proved asymptotically optimal policy.
