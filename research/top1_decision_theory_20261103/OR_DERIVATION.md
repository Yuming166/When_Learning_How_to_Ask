# OR top-1 decision: an exact one-bit reduction and a state-dependent boundary

Scoped independent derivation, 2026-11-03. This note does not modify the existing manuscript. It uses fresh iid binary answers and the common, unknown reliability levels in `Theory_Note.md`. No model/API/GPU call or new simulation was used. All claims below exclude direct type-report actions. The generic decision-alternative information program is an established ingredient; the structural reduction below is the result being derived.

## 1. Two recommendations whose winner is OR

Give two items utilities

\[
U_1(\theta)=d-1+\sum_{j=1}^d\theta_j,
\qquad U_0(\theta)=0.
\]

Their difference is \(-1\) when every sign is negative and at least \(+1\) otherwise. Thus there are no ties, and the top-1 recommendation is

\[
f_{\rm OR}(\theta)=\mathbf 1\{\exists j:\theta_j=+1\}.
\]

The learner must recommend the correct item uniformly over all signs, types and admissible common rates. It need not recover the signs. The oracle is told only the current types, receives the same labelled offline streams, and still does not know \(p,q\). Fix \(p>q\ge1/2\), \(p\le1-\eta\), and \(M_\delta/\log(1/\delta)\to\alpha<\infty\).

Write

\[
D(r,x)=\operatorname{kl}(r,x),\quad
\mathcal D=\{(u,v):1/2\le v\le u\le1-\eta\},
\quad
\Psi_\alpha(u,v)=\alpha[D(p,u)+D(q,v)].
\]

The closure \(u=v\) is used only in taking infima, as in the original model. Every closed-domain alternative needed below can be approximated by admissible strict alternatives. Counts are normalized by \(R_\delta=\log(1/\delta)\).

## 2. Define the genuine unknown-rate one-bit problems

For one true sign, let \(a,b\) be the normalized good/other-format counts, with “good” naming the true channel for analysis only. Define

\[
\begin{aligned}
C_\alpha(a,b)
&=\inf_{(u,v)\in\mathcal D}
\{\Psi_\alpha(u,v)+aD(p,1-u)+bD(q,1-v)\},\\
S_\alpha(a,b)
&=\inf_{(u,v)\in\mathcal D}
\{\Psi_\alpha(u,v)+aD(p,1-v)+bD(q,1-u)\}.
\end{aligned}
\]

The first alternative preserves the type; the second exchanges it. In particular, neither expression treats the true rates as known. Set

\[
K_{1,\alpha}=\min_{a,b\ge0}
\{a+b:C_\alpha(a,b)\ge1,\ S_\alpha(a,b)\ge1\},
\]

\[
K^{\rm or}_{1,\alpha}=\min_{a,b\ge0}
\{a+b:C_\alpha(a,b)\ge1\}.
\]

These are information coefficients, before invoking an asymptotic attainability theorem. Their feasible sets are closed; a sufficiently large two-format allocation is feasible, so their finite minima are attained.

## 3. Exact positive-OR reduction, for every finite alpha

**Theorem 1.** At any true sign vector containing at least one positive sign, for every known sharing partition,

\[
\boxed{
K_{{\rm OR},\alpha}(\theta,\mathcal S)=K_{1,\alpha},
\qquad
K^{\rm or}_{{\rm OR},\alpha}(\theta,\mathcal S)=K^{\rm or}_{1,\alpha}.
}
\]

Thus the coefficients do not depend on the number of coordinates, the number of positive coordinates, or the group sizes at a positive-OR instance.

**Proof.** Let \(P=\{j:\theta_j=+1\}\ne\varnothing\), and write the task counts as \(a_j,b_j\), according to the true good and other format in the coordinate's group. A wrong recommendation has the unique sign vector \(\theta'=(-1,\ldots,-1)\). Thus precisely the coordinates in \(P\) must change sign. Define the total counts

\[
A=\sum_j a_j,\qquad B=\sum_j b_j.
\]

For \(r,x\ge1/2\),

\[
D(r,1-x)-D(r,x)=(2r-1)\log\frac{x}{1-x}\ge0. \tag{1}
\]

First consider the wrong-recommendation alternative that preserves *every* group type. At fixed \((u,v)\), its divergence is

\[
\Psi_\alpha(u,v)
+\sum_{j\in P}[a_jD(p,1-u)+b_jD(q,1-v)]
+\sum_{j\notin P}[a_jD(p,u)+b_jD(q,v)].
\]

By (1), this is at most

\[
\Psi_\alpha(u,v)+AD(p,1-u)+BD(q,1-v).
\]

Consequently any feasible OR allocation must satisfy \(C_\alpha(A,B)\ge1\). Now choose the wrong-recommendation alternative that exchanges *every* group type. The same argument, with \(u,v\) interchanged in task terms, implies \(S_\alpha(A,B)\ge1\). Hence every feasible OR allocation has cost at least \(K_{1,\alpha}\). The oracle argument uses just the first alternative, giving the oracle lower bound.

Conversely, choose any true positive coordinate \(j_+\). Allocate the one-bit optimal \((a,b)\) entirely to its two formats and allocate zero first-order counts to every other coordinate. Every wrong recommendation flips \(\theta_{j_+}\). Its information is exactly the preserved-type or exchanged-type one-bit information, according to the alternative type of the group containing \(j_+\). The other group types have no task observations to influence. The same offline penalty is used. Therefore this allocation is feasible for OR and has the one-bit cost. The oracle construction uses its one-bit allocation in the same coordinate. This proves both equalities. \(\square\)

The proof does not replace the shared unknown rates by a known-channel calculation. The global sharing of \(u,v\), including the offline contribution, is retained in both inequalities.

## 4. No offline information at first order: zero premium for every partition

Let \(B_p=D(p,1/2)>0\). At \(\alpha=0\), the closed alternative \(u=v=1/2\) gives every allocation at most

\[
aB_p+bD(q,1/2)\le(a+b)B_p
\]

information per one-bit decision. Thus the cost is at least \(1/B_p\), even for the oracle. Sampling only the true good format of one positive coordinate gives at least \(aB_p\) against every wrong-recommendation alternative because its probability of answering that true sign is at most \(1/2\). Choosing \(a=1/B_p\) attains the lower bound. Therefore

\[
\boxed{
\theta\text{ has a positive sign},\quad\alpha=0:
\qquad K_{{\rm OR},0}=K^{\rm or}_{{\rm OR},0}
=\frac1{D(p,1/2)}.
}
\]

The true \(q\) drops out of this coefficient, but \(q\) is still unknown and remains a nuisance parameter of the statistical model. “\(\alpha=0\)” permits a sublogarithmic amount of offline data; it does not mean that the learner knows the rates without cost.

This is a counterexample to extending the full-recovery statement “zero calibration implies zero type premium iff there is one sharing group” to arbitrary top-1 decisions. An OR-positive instance has zero premium with any number of singleton groups.

## 5. Any positive calibration ratio creates a strict positive-OR premium

This statement is about every fixed finite \(\alpha>0\), not about a finite-sample monotonicity claim.

**Lemma 2 (one-bit oracle).** Let \(a_\alpha>0\) be the unique root

\[
\inf_{(u,v)\in\mathcal D}
\{\Psi_\alpha(u,v)+a_\alpha D(p,1-u)\}=1. \tag{2}
\]

The oracle optimum is uniquely \((a,b)=(a_\alpha,0)\).

**Proof.** The left side of (2) is zero at \(a=0\), continuous, and increases by at least \((a'-a)B_p\) when \(a'\ge a\), so its positive root exists and is unique. A minimizing pair at the root can be chosen with

\[
1/2\le u_*\le p,\qquad v_*=\min(q,u_*).
\]

The formula for \(v_*\) minimizes its offline KL; decreasing \(u>p\) decreases both relevant terms, establishing \(u_*\le p\). Let

\[
L_p=D(p,1-u_*),\qquad L_q=D(q,1-v_*).
\]

Then \(L_p>L_q\). If \(u_*\le q\), the two second arguments coincide and \(r\mapsto D(r,1-u_*)\) is strictly increasing between \(q\) and \(p\). If \(u_*>q\), use \(v_*=q\), the monotonicity in \(u\), and the same monotonicity in \(r\). Evaluating any competing allocation at this fixed minimizing pair gives

\[
C_\alpha(a,b)
\le \Psi_\alpha(u_*,v_*)+(a+b)L_p-b(L_p-L_q).
\]

If \(a+b\le a_\alpha\), this is strictly below one unless \((a,b)=(a_\alpha,0)\). \(\square\)

**Theorem 3.** For every \(\alpha>0\), every positive-OR true state and every partition,

\[
\boxed{K_{{\rm OR},\alpha}>K^{\rm or}_{{\rm OR},\alpha}.}
\]

**Proof.** Consider the unique one-bit oracle allocation in Lemma 2 and its minimizing pair \((u_*,v_*)\). For the exchanged-type one-bit alternative choose alternative rates \((u,v)=(p,v_*)\). This is admissible because \(v_*\le q<p\). Its information is

\[
\alpha D(q,v_*)+a_\alpha D(p,1-v_*).
\]

Subtract this from the oracle information in (2), which equals one. The difference is

\[
\alpha D(p,u_*)
+a_\alpha\{D(p,1-u_*)-D(p,1-v_*)\}. \tag{3}
\]

Both terms are nonnegative. If \(u_*>v_*\), the second is strictly positive since \(p>1/2\). If \(u_*=v_*\), then \(u_*\le q<p\), so the first is strictly positive because \(\alpha>0\). Thus the oracle allocation fails the exchanged-type information constraint. Since the unknown-type feasible set is closed and its finite optimum is attained, equality of optimum values would contradict the uniqueness in Lemma 2. Apply Theorem 1. \(\square\)

Combining Sections 4 and 5 yields the particularly simple, state-specific boundary

\[
\boxed{
\theta\text{ has a positive sign},\ \alpha<\infty:
\quad K_{{\rm OR},\alpha}=K^{\rm or}_{{\rm OR},\alpha}
\ \Longleftrightarrow\ \alpha=0.
}
\]

The availability of labelled calibration can make knowing the type valuable: the oracle can use the calibration to trust its known good format, while the unrevealed-type learner must also rule out a format exchange.

## 6. Requested concrete instance: p = .8, q = .6

Choose the model's fixed upper-bound constant with \(0<\eta\le1/5\), so this instance is admissible.

Define the exact constants

\[
P=D(4/5,1/2),\quad Q=D(3/5,1/2),\quad E=D(3/5,1/5).
\]

For any positive-OR state and any partition, at \(\alpha=0\) both coefficients are exactly \(1/P\).

For a positive calibration ratio in the range

\[
0<\alpha\le\frac1{(7/3)P+Q},
\]

the oracle's minimizing rates in (2) are \(u=v=1/2\), and

\[
a_\alpha=\frac{1-\alpha(P+Q)}P.
\]

Indeed the corner optimality condition is \(a_\alpha\ge(4/3)\alpha\), equivalent to the displayed range. In particular \(\alpha=1\) is in the range. For example, the elementary inequality \(D(r,1/2)\le(2r-1)^2\) implies \((7/3)P+Q<.88<1\).

For every unknown-type allocation, two fixed alternative choices imply

\[
Pa+Qb\ge1-\alpha(P+Q),\qquad
Pa+Eb\ge1-\alpha Q.
\]

These respectively use \(u=v=1/2\) with preserved type, and \(u=p,v=1/2\) with exchanged type. Here \(E>P>Q\). Taking nonnegative linear weights that make both count coefficients equal one gives the explicit strict lower bound

\[
\boxed{
K_{{\rm OR},\alpha}
\ge a_\alpha+\alpha\frac{P-Q}{E-Q}
>a_\alpha=K^{\rm or}_{{\rm OR},\alpha}.
}
\]

This is an analytic certificate, not a nonlinear-optimizer estimate. It need not be the exact unknown-type coefficient. At \(\alpha=1\), the gap lower bound is the positive exact log expression \((P-Q)/(E-Q)\). For a purely algebraic check that \(E>P\),

\[
5(E-P)=\log(84375/32768)>0.
\]

## 7. Negative-OR states retain the full-recovery boundary

**Theorem 4.** At \(\theta=(-1,\ldots,-1)\), the OR decision information problem is exactly the original full-sign-recovery information problem at the same state, for both oracle and unknown types, for every \(\alpha\) and partition.

**Proof.** At this true state, “a different full sign vector” and “a different OR winner” specify exactly the same set of alternative sign vectors: all vectors with at least one positive sign. Both problems retain every alternative rate pair and every alternative type vector. Thus their change-of-measure constraints, query costs and information programs are identical. Equivalently, the one-positive alternatives already give the original full-recovery constraints; additional positive sign changes only add nonnegative KL by (1). \(\square\)

Consequently the original smallest-sharing-group theorem applies at the negative-OR state. In particular, under its proved-program/attainability premises, at \(\alpha=0\)

\[
K_{{\rm OR},0}=K^{\rm or}_{{\rm OR},0}
\quad\Longleftrightarrow\quad G=1
\qquad(\theta\equiv-1).
\]

For a fixed partition with \(G>1\), the same OR recommendation task therefore has zero premium at every positive-OR state and strictly positive premium at its all-negative state, when \(\alpha=0\). A criterion based only on the partition cannot describe arbitrary top-1 decision instances.

## 8. What same-winner and irrelevant coordinates do in this example

At a positive-OR state, a negative coordinate remains unchanged under the unique wrong-winner sign vector. Its observations can supply calibration terms such as \(D(p,u)\), but Theorem 1 proves that allowing any number of such coordinates cannot lower the optimal leading coefficient below the one-positive-coordinate strategy. Likewise, additional positive coordinates give no reduction in this coefficient.

The same conclusion extends if one adds sign coordinates of zero utility weight, using the same channel model and arbitrary sharing groups. To prove the lower bound, choose wrong-winner alternatives that leave these nuisance signs unchanged and preserve or exchange all group types. Their information is bounded above by the same aggregate one-bit expressions, by (1). Sampling a true positive utility-bearing coordinate still attains the upper bound. Thus these nuisance coordinates can carry information about rates or types without improving the optimum in this OR-positive example.

This is a scoped negative result. It does not establish that irrelevant coordinates are useless for every top-1 utility map, nor that calibration observations have zero KL. In general threshold decisions, a coordinate unchanged under one wrong-winner alternative can still contribute type-calibration information against that alternative.

## 9. Known-rate control: sharing cannot remove the positive-OR premium

This subsection is a distinct control in which \(p,q\) really are supplied to the learner; it is not substituted for the unknown-rate results above. The reduction of Theorem 1 also holds in this control, by fixing \((u,v)=(p,q)\) and omitting the offline term.

The oracle coefficient is \(1/A\), where \(A=D(p,1-p)\), and its one-bit allocation uniquely uses the good format. The exchanged-type information at that allocation is \(D(p,1-q)/A<1\). Hence the positive-OR premium is strictly positive for every partition, including a single arbitrarily large sharing group.

There is an elementary closed form when \(q=1/2\). Put

\[
A=D(p,1-p),\quad B=D(p,1/2),\quad C=D(1/2,p).
\]

The preserved/exchanged type constraints reduce to

\[
Aa\ge1,\qquad Ba+Cb\ge1.
\]

Since \(C>B\), their minimum cost is

\[
\boxed{
K^{\rm known}_{{\rm OR},+}
=\frac1A+\frac{1-B/A}{C},
\qquad
K^{\rm known,or}_{{\rm OR},+}=\frac1A.
}
\]

This is independent of the number of positive coordinates and the sharing partition. It is the original one-coordinate known-rate formula, now derived as an exact reduction of a nontrivial top-1 task.

## 10. Achievability status and claim boundary

The equality proofs above are exact statements about information programs, with explicit lower and upper allocation constructions. Converting their coefficients into

\[
\inf_{\pi\ {\rm uniformly}\ \delta{\rm-correct}}
\mathbb E_h\tau_\pi
=K(h)\log(1/\delta)+o(\log(1/\delta))
\]

requires a valid uniformly correct decision stopping rule and the corresponding expected-cost attainability argument. Under the compact Bernoulli model, fixed dimensions and fixed pointwise gaps, these are the same controlled-sensing/likelihood ingredients used in the original note. This derivation does not claim a new general attainability theorem or a uniform result as gaps vanish.

The positive-OR upper bound also has a direct reduction route, conditional only on valid one-bit procedures. Use \(o(R_\delta)\) preliminary fresh observations of every format to order candidate coordinates, with a probability \(1-e^{-c\sqrt{R_\delta}}\) of placing a true positive first at any fixed positive-OR state. Test candidates using uniformly correct one-bit sign procedures at error level \(\delta/d\), returning positive as soon as a test finds one, and returning negative only when all tests find negative. Candidate tests use fresh task observations; the preliminary selection must not be a permanent unverified sign commitment. The labelled offline sample is shared, and the one-bit anytime error events can be union-bounded over all coordinates. Selection can be based only on preliminary task observations, independently of the offline sample and fresh tests. If each one-bit procedure has the claimed pointwise expected \(O(R_\delta)\) cost, the exceptional candidate-order event contributes \(o(R_\delta)\), and the leading expected cost at a positive-OR state is exactly the one-bit coefficient. Finite \(d\) changes \(\log(1/\delta)\) by only \(O(1)\) through \(\delta/d\).

The negative-OR equality of asymptotic costs additionally uses attainability of the original full-recovery coefficient: a full-recovery policy gives an OR policy, and the identical alternative set gives the matching lower bound.

Direct type reports, heterogeneous report reliabilities, persistent response errors, growing dimension, finite-budget gains and general weighted-threshold nuisance-coordinate benefits are outside the results established here. No statement in this note certifies scientific priority or paper readiness.
