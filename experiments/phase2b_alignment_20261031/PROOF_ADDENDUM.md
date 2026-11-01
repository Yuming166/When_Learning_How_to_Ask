# Theorem 1 expected-time addendum and code correspondence

## Material Passport

2026-10-31. Inputs: unchanged Theory_Note.md, Phase2a source, new forced-only sampler, independent mathematical review in audit/THEOREM1_REVIEW.md. This is a research proof with separate same-family review, not a formal proof-assistant or external-expert certificate. Historical theory and results are preserved. The full derivation, boundary cases and quantifiers are in the independent review; this addendum states the repaired argument and its executable limits.

## Precise ideal-policy claim

Fix finite d, a known partition, eta>0, known finite type accuracies, and a true .5<=q<p<=1-eta. Let R=log(1/delta), M/R->alpha<infinity. Use the original joint continuous coefficient K=K_{S,alpha}.

An ideal real-arithmetic policy attains E_h[tau]/R->K if it has: (i) deterministic forced counts F_e(t)>=c sqrt(t)-C and F(t)=O(sqrt(t)); (ii) the Section4.2 forced-only estimator on a deterministically vanishing ordered grid; (iii) allocations with ACTUAL feasibility and optimality errors bounded by a delta-independent e(t)->0; (iv) update ages O(sqrt(t)); (v) actual counts within O(sqrt(t)) of cumulative normalized allocation targets; and (vi) exact joint GLR stopping at the original boundary, checked with a gap o(R). All constants are pointwise in the fixed true parameter. No growing-d or vanishing-gap uniform claim is made.

The current implementation realizes explicit schedules/estimators and evaluates the required numerical diagnostics. Its fixed float64 floors do not certify premise(iii) on an infinite horizon, and its GLR is not interval-enclosed. Therefore this ideal-policy theorem is not an unconditional theorem about the executable Python program.

## 1. Local stability without unique optimizers

Write I_xi(x)=inf_{h':theta'!=theta}[alpha D_0(h')+J_{h'}(x)] and query cost c^T x, xi=(p,q,alpha). The alternatives are a fixed compact two-dimensional ordered triangle times a finite discrete set. The all-task direction v gives one query to each task stream. In a relative neighborhood with p'>=p_min>.5, every wrong sign incurs at least b=kl(p_min,.5)>0 from the changed coordinate's true good stream. Thus I_xi'(x+a v)>=I_xi'(x)+ab.

This produces a common feasible bounded-cost allocation, strict feasibility, and an arbitrarily small feasibility repair when xi changes. Positive query costs give compact sublevels. Uniform continuity of KL on the compact alternative domain yields continuity of I. Subsequences then prove K continuity and upper hemicontinuity of the compact optimizer set X*. The same argument handles actual feasibility/optimality errors tending to zero. It works at alpha=0,q=.5,p=1-eta in relative neighborhoods; no positive calibration or interior-q assumption is added.

All x in X* have the same positive cost K. Consequently W*={Tx/K:x in X*} is compact and convex, where T expands grouped counts to actions. Normalization is linear on this one cost hyperplane; no continuous or unique optimizer selection is needed.

## 2. A positive online margin

Put A_r=kl(r,1-r), B_r=kl(r,.5), and r*=min_{r in {p} union {q:q>.5}} B_r/A_r>0. For q=.5 omit its0/0 term. A same-type alternative at the true levels flipping coordinate j enforces a_g A_p+b_g A_q>=1. Hence a_g B_p+b_g B_q>=r*.

For any wrong-sign alternative the probability of the true sign at a flipped coordinate is at most .5, regardless of its candidate type/levels. Its online information under every normalized true optimizer is therefore at least mu=r*/K>0. This explicitly excludes an alternative relying entirely on a tight offline constraint.

## 3. Forced estimates, delayed updates, and deterministic tracking

Use L=2d task streams. At completed times t=L n^2+s,0<=s<L, force stream s. Then floor(sqrt(t/L))<=F_e(t)<=floor(sqrt(t/L))+1 and F(t)<=sqrt(Lt)+L. At updates compute forced-only raw means, sign from their sum minus one, group type by the larger oriented mean, coordinate-averaged high/low rates, and projection to the ordered grid of mesh(.5-eta)/ceil(sqrt(t+1)). The fixed gaps p+q-1 and p-q give probability <=C_a exp(-c_a sqrt(t)) of any discrete error or fixed level error>a.

Hold targets from u until u+ceil(sqrt(u+1)); their age is O(sqrt(t)). Let C(t)=sum_{s<=t}w_s include every round. On a nonforced round select argmax_e(C_e(t)-N_e(t-1)); forced rounds override that choice. With A=N-C, the selected nonforced pre-action value is the smallest component of A-w and is <=0. Its post-action value is <=1; unselected components do not increase. Each forced override raises the maximum by at most1. Therefore

\[
\max_e A_e(t)\le1+F(t),\quad
\min_e A_e(t)\ge-(|E|-1)(1+F(t)),\quad
\|A(t)\|_1\le2(|E|-1)(1+F(t)).
\]

This is a deterministic extension of the note's randomized allocation step. It is not asserted to be literal line-by-line implementation of that randomization. The bound is proved here for the exact cumulative-target convention in aligned.py.

On a high-probability event every target after rho*t is near W*. By convexity, their Cesaro mean is near W*, even when optimizers are nonunique and targets change discontinuously. Early rounds contribute at most2rho in L1; the tracking error contributes O(t^-1/2). A union bound over late update times gives a bad-event probability <=C t exp(-c sqrt(t)), with constants independent of delta. Grid, update, and actual solver-error moduli must be uniform in delta: pointwise accuracy only after exp(R) would not suffice at t~R.

## 4. Horizon-proportional drift and finite calibration

For a wrong alternative define the predictable compensator D_t=M D_0+sum_e N_e(t)d_e. For t>=(K+epsilon)R, feasibility, the online margin mu, local allocation closeness and M/R->alpha give

\[
D_t\ge R+(t-KR)\mu-o(t)\ge R+\gamma t
\]

for some gamma>0, uniformly over all wrong alternatives and all such t, once R is large. Explicitly choose the allocation L1 tolerance so D_max*a<=epsilon*mu/[4(K+epsilon)] and calibration-ratio error so |M/R-alpha|D_{0,max}<=epsilon*mu/4; then gamma=epsilon*mu/[2(K+epsilon)] works.

For fixed delta, an offline empirical-mean bad event generally has positive probability independent of t. Treating that as a permanently required good event cannot justify a tail decaying to zero for all later t. This is the missing uniformity detail in the historical sketch.

Instead concatenate the2M offline and t adaptive online centered log-likelihood increments. Probabilities are bounded away from0 and1, so the centered increments are bounded. For t>=(K+epsilon)R and small delta,2M+t<=C_0 t. Azuma at deviation gamma*t/4 gives exp(-c t), including offline fluctuations without conditioning them away. For each finite sign/type pattern cover the continuous rate triangle by a t^-2 mesh with O(t^4) points. Bounded log-likelihood derivatives give O(1/t) interpolation error; union bounds produce C t^4 exp(-c t).

The boundary correction is at most |E|log(t+1)+2log(M+1)=O(log t), uniformly over these horizons. It is smaller than the drift slack for every t>=(K+epsilon)R once R is large. Combining with the allocation event gives

\[
\Pr_h(\tau_\delta>t)\le C t^A e^{-c\sqrt t},\quad
R\ge R_0,\quad t\ge\lceil(K+\epsilon)R\rceil.
\]

The constants are independent of both delta and t. At a last checked time, an o(R) check gap is absorbed by a smaller internal epsilon. For fixed delta outside the asymptotic range the same online margin eventually dominates the fixed offline batch, yielding a summable tail after a delta-dependent threshold and finite expected stopping.

## 5. Tail summation and error control

Summing the uniform tail after T=ceil((K+epsilon)R) gives E tau<=T+C sum_{t>=T}t^A exp(-c sqrt(t)). The latter sum is bounded by a polynomial in sqrt(T) times exp(-c' sqrt(T)), hence o(R). Let epsilon decrease to0 after taking limsup. The source change-of-measure lower bound gives the matching liminf; closure alternatives follow by continuity from strict p>q alternatives.

The anytime error argument is separate: the saturated Beta-mixture likelihood ratio is initialized BEFORE the offline observations. Its mean is1 unconditionally over the offline sample; Ville therefore supplies the original delta bound for any predictable sampler. This is not a guarantee conditional on every offline data realization. A floating GLR without rigorous conservative enclosures does not automatically inherit that arithmetic guarantee.

## Literature context and provenance

The cumulative-proportion tracking argument is an established ingredient: [Garivier and Kaufmann, COLT2016, AppendixB and Theorem14](https://proceedings.mlr.press/v49/garivier16a.pdf) prove tracking and expected stopping-time results for best-arm identification. [Deshmukh, Bhashyam and Veeravalli, composite controlled sensing](https://arxiv.org/pdf/1910.12697) separately formulate expected-delay optimality. Those results motivate the proof organization; neither directly substitutes for the finite-calibration, shared-unknown-channel argument above. No novelty or priority audit is claimed here.
