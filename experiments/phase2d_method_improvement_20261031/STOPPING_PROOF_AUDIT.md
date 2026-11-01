# Independent adversarial audit of CertifiedStopping

Date: 2026-10-31. Final gate verdict: **PASS within the stated model and
arithmetic contract**. No blocking proof or implementation gap was found.
The guarantee remains conditional on correct caller setup and the standard
Python Fraction/Decimal contracts, as detailed below; it is not a
proof-assistant-verified theorem or a claim of eventual stopping.

## Material passport and independence

This audit independently derives the stopping requirement from the raw
`Theory_Note.md` Sections 1, 3, and 4, Phase2a `glr.py` and `coefficients.py`,
Phase2b `log_glr.py`, and the explicit floating-point counterexample in
Phase2c `audit/adversarial_math_checks.py`. The derivation below was completed
before reading any new gate specification or another gate agent's answer.
No approving Phase2c proof review was read. This is a separate native agent
with the parent's task description, not a cross-model or formally verified
proof. The implementation had not yet been created at initial derivation.

No worlds, model calls, random seeds, training, package installation, or
experimental episodes are authorized by this audit. Deterministic arithmetic
and adversarial input checks are in scope.

## 1. Exact event that must be certified

For the observed full transcript, put

\[
F_t(\vartheta)=\max_{z\in\{0,1\}^G}
\max_{1/2\le q\le p\le U}\ell_t(\vartheta,z,p,q),
\qquad U=1-\eta.
\]

All reference, task, and paid type observations enter this same likelihood.
For any proposed candidate \(c\in\{0,1\}^d\), it is sufficient to construct

\[
A_c\le F_t(c),\qquad
B_c\ge\max_{\vartheta\ne c}F_t(\vartheta),\qquad
C_t\ge R+\sum_e\log(N_e(t)+1)
\]

and accept **only** if a downward-rounded evaluation of \(A_c-B_c\) is
at least \(C_t\). Equivalently one may compare a downward residual with zero.
These inequalities, not numerical agreement at multiple precisions, are the
proof obligation. A candidate's feasible joint value already suffices for
\(A_c\); computing its exact profiled maximum is optional. Every wrong sign
and every allowed type assignment must be covered by \(B_c\).

The candidate may come from a floating-point heuristic or any history-based
selection. No correctness assumption about that selection is needed. Since
\(R>0\), successful certification itself implies that its exact profile is
larger than every wrong-sign profile. An approximate candidate or overlapping
intervals may delay stopping but must never authorize a fallback crossing.

## 2. Continuous profiling, including omitted-weight cases

For a fixed pair \((\vartheta,z)\), aggregate exact integer successes and
totals \((a,n)\) on the candidate's high channel and \((b,m)\) on its low
channel. Reference successes are labelled independently of \(\vartheta,z\).
The part depending on the levels is

\[
f(p,q)=a\log p+(n-a)\log(1-p)
       +b\log q+(m-b)\log(1-q).
\]

For two positive weights, separately clip \(a/n,b/m\) to \([1/2,U]\).
If their order is feasible, these are the constrained maximizers. Otherwise
the order constraint is active and both coordinates equal the clipped
pooled mean \((a+b)/(n+m)\). The pooled expression follows by restricting
the strictly concave objective to \(p=q\); concavity and the active order
constraint establish global, rather than local, optimality.

If \(n=0<m\), fit \(q\) and choose any feasible \(p\ge q\), for example
\(p=q\). If \(m=0<n\), fit \(p\) and choose \(q=1/2\). If both totals are
zero, \(p=q=1/2\) is valid. The unconstrained, clipped, pooled and empty
cases are all rational when \(U\) is rational.

An independent exact check is available: the feasible triangle has vertices
\((1/2,1/2),(U,1/2),(U,U)\). At a proposed optimum \(x\), calculate the
rational gradient \(\nabla f(x)\) and verify
\(\nabla f(x)\cdot(v-x)\le0\) at all three vertices. Concavity then proves
optimality on the entire continuous domain. This test does not rely on the
same pooling implementation or a grid.

The closed domain includes \(p=q\), especially \(p=q=1/2\). The true model
retains \(p>q\). The strict domain is dense in the closed triangle and the
finite-data log likelihood is continuous because \(0<\eta<1/2\). Thus the
closed maximum equals the strict-domain supremum. Excluding the diagonal
would risk understating a competing supremum.

## 3. Arithmetic contract

The intended real input is the exact represented input. For a supplied
binary float, use its exact integer ratio for \(\eta,s_g,R\). In particular,
compute \(1-\eta\) and \(1-s_g\) **after** rational conversion. The rounded
binary expression `1 - eta` is generally a different domain endpoint.
Define the stated risk as \(\delta=\exp(-R)\) for this exact value of \(R\);
there is no need to evaluate the exponential. If instead a user supplies a
target \(\delta\), its conversion to \(R\) requires its own conservative
rounding proof.

Convert a positive rational argument to Decimal using a lower and upper
directed division, obtaining \(x_-\le x\le x_+\). Monotonicity of log and
correctly rounded nearest evaluation give the enclosure

\[
\operatorname{nextMinus}(\operatorname{ln}(x_-))
\le\log x\le
\operatorname{nextPlus}(\operatorname{ln}(x_+)).
\]

Python documents `Decimal.ln` as correctly rounded with `ROUND_HALF_EVEN`;
the neighboring representable values are defined by `next_minus` and
`next_plus`. Thus setting a directed context alone does not make `ln` a
directed operation. The one-neighbor expansion is essential in this
construction. This is a library-contract assumption, not a claim of a
machine-checked implementation proof. Source:
[Python 3.13 Decimal documentation](https://docs.python.org/3.13/library/decimal.html#decimal.Decimal.ln).

Multiplication by nonnegative integer counts and all sums must preserve
directed lower/upper endpoints. Maximum over finitely many lower endpoints
is a lower bound on the maximum; maximum over upper endpoints is an upper
bound. The final subtraction needs downward rounding. Use fresh explicit
contexts so ambient precision, rounding, exponent limits or traps cannot
silently change certificate semantics. Reject nonfinite/invalid results.
Any precision or count limit must decline certification, never substitute
an unchecked float result. Store endpoint strings without a subsequent
float conversion if they are intended as auditable enclosures.

## 4. Why the old model-level anytime guarantee transfers

Fix a true model state \(h\). In a saturated model put an independent
uniform Beta prior on the raw Bernoulli parameter of every stream, including
the two labelled references, all \(2d\) task streams, and every available
paid type stream. For stream \(e\) with total \(n\) and successes \(k\),
the ordered-sequence mixture likelihood is

\[
Q_e=\frac{1}{(n+1)\binom nk},\qquad
\sup_\mu L_e(\mu)\le(n+1)Q_e.
\]

Consequently the full model supremum is bounded by
\(Q_t\prod_e(N_e+1)\). Under predictable adaptive sampling, action kernels
cancel in the likelihood ratio. The process \(Q_t/L_t(h)\) is a
nonnegative mean-one martingale when started **before the offline samples**.
Known type accuracy does not invalidate saturation; its stream likelihood
is simply bounded by the unrestricted Bernoulli likelihood. Empty streams
contribute \(\log1=0\).

On a wrong certified output, \(h\) belongs to the competing-sign set. The
certified inequality therefore implies

\[
\frac{Q_t}{L_t(h)}\ge e^R=1/\delta.
\]

Ville's inequality proves
\(\Pr_h(\exists t:\text{wrong certified output at }t)\le\delta\), uniformly
in each allowed fixed true \(h\). The sampling rule may be any predictable
history-based rule, and checking only a subset of times preserves the bound.
Randomized sampling is included by conditioning on independent internal
randomness or including it in the filtration.

Required setup: \(R,\eta\), partition, known type accuracies, stream identities
and their likelihood model are fixed before offline sampling; the complete
count correction is recomputed at each inspection. Offline sample size is
the prescribed finite size, with the two streams counted separately. The
claim averages over offline observations. A per-realized-calibration
conditional guarantee does not follow by restarting Ville after observing
the calibration data. Choosing \(R\) after favorable calibration outcomes
also does not inherit the stated fixed-risk proof.

This theorem controls wrong **certified** output. Arbitrary predictable
samplers can fail to obtain information and never stop. Almost-sure stopping,
finite expected cost, an asymptotic coefficient, and errors from an
uncertified deadline decoder each require separate claims and assumptions.
The numerical gate's \(d\le4\) restriction is a computational scope limit;
it must be enforced, not silently replaced by incomplete enumeration.

## 5. Adversarial implementation review

Reviewed source: `phase2d/certified.py`, SHA-256
`162fe61943bdebf2b297cdca914a734e9b0befcf66939c800a00a9a35820130c`.
The derivation in Sections 1–4 was written first. The implementation review
and independent tests were completed without reading another gate agent's
answer or the new implementation specification.

| Obligation | Observed implementation | Finding |
|---|---|---|
| Exact inputs and complements | `_rational`, lines 58–79; `_ordered_mle`, line 111; `_states`, lines 259–264 | PASS: stored binary values are exact, complements are rational |
| Continuous supremum | `_ordered_mle`, lines 109–119 | PASS: clipping, pooling, both single-empty cases and both-empty case |
| All wrong signs and all types | `_states`, lines 248–266; competitor maximum, lines 317–319 | PASS: complete enumeration; no single-flip reduction is assumed for observed likelihoods |
| Joint data model | `_states`, lines 247–264 | PASS: independent labelled references, candidate-oriented task answers, known-accuracy paid type answers |
| Interval logarithms | `_Intervals`, lines 125–180 | PASS: exact integer Decimal construction, directed rational division, nearest log with neighboring endpoint expansion, directed sums/products/subtraction |
| Threshold | lines 294–296 and 320 | PASS: exact R, two reference corrections, every task stream and paid type stream |
| Candidate selection | lines 308–319 | PASS: supplied candidate or maximum lower endpoint; competitors exclude only that sign, not a joint state |
| Stop event | lines 325–329 | PASS: strict `gap_lower > beta_upper` is conservative relative to the theorem's non-strict boundary |
| Failure behavior | lines 333–345 | PASS: overlaps require continuation/abstention; arithmetic failure discards prior endpoints; no floating fallback |
| Declared scope | `_validate`, lines 183–241 | PASS: d at most 4, at most 256 joint states, bounded counts/constants/precision, malformed data rejected |

There are caller obligations that this stateless function cannot verify:
fixed R and channel constants before offline observations, genuine labelled
independent references, the stated fresh-response model, correct known type
accuracy, and complete counts. The returned `theta` is also present on a
rejected/undetermined attempt; a consumer must stop only when `certified`
is true. Runtime resource errors outside the caught arithmetic errors can
abort a call; they do not establish a certificate and must not be converted
by a wrapper into an answer with the certified risk claim.

The implementation has no oracle-type input and always enumerates every
type vector. That is conservative and matches this prototype's requested
scope. A future restricted-type version needs a separate check that the
true type is included in its supplied restriction.

## 6. Deterministic independent evidence

Command, from the repository root:

```sh
python experiments/phase2d_method_improvement_20261031/audit/stopping_independent_checks.py
```

Executed successfully on Python 3.13.13, libmpdec 4.0.0. Last observed runtime
was approximately 0.83 seconds. The script reports the source hash above.

| Check | Observed result |
|---|---|
| Exact rational gradient at all feasible-triangle vertices | 2,352 MLE cases passed, including all weights 0 through 6 and three upper endpoints |
| Log intervals checked against a separate rational series remainder | 27 cases passed at 16, 50 and 80 decimal digits |
| Full likelihood reconstruction from stream probabilities | 5 fixtures / 28 sign profiles passed; includes d=4, G=4, 256 joint states, finite calibration and paid type data |
| Candidate, wrong-sign, gap and complete threshold intervals | Every fixture passed independent rational containment |
| Old floating false crossing | Rejected; rational remainder proves the exact residual is negative |
| Candidate supplied independently | Correct candidate certified; wrong candidate not certified |
| Ambient Decimal context altered | Identical certificate endpoints and decision |
| Malformed and out-of-scope input | 21 inputs rejected |
| Precision overlap and refinement | At 16 digits returned undetermined; 80-digit refinement certified a residual independently proved positive |
| Injected arithmetic failure after an overlapping attempt | Returned undetermined and discarded earlier candidate/endpoints |

The logarithm reference reduces a positive rational to \(2^k y\),
\(1\le y\le2\), and uses

\[
\log y=2\sum_{j=0}^{N-1}\frac{t^{2j+1}}{2j+1}+\rho_N,
\quad t=\frac{y-1}{y+1},\quad
0\le\rho_N\le\frac{2t^{2N+1}}{(2N+1)(1-t^2)}.
\]

All operations, including the bound, use exact Fractions. The reference does
not call `Decimal.ln` or a binary logarithm. For each checked target enclosure,
its lower endpoint lies below the reference lower bound and its upper endpoint
lies above the reference upper bound. Thus the check establishes containment
through a mathematical remainder bound instead of numerical agreement.
The mathematical reasoning in Sections 1–4 supplies the general argument;
the finite test set is regression evidence, not exhaustive proof over all
integer counts or all supported inputs.

For the historical counterexample, \(n=1000000000152\), \(\eta=1/8\),
and the exact stored \(R=2292186267618727/4096\). Its exact residual is
\(n\log(7/4)-R-\log(n+1)<0\). The new gate rejects this input.

All checks use synthetic static count arrays and deterministic arithmetic:
**0 experimental episodes, 0 acquired offline observations, 0 online
actions, 0 random seeds, 0 model/API calls**.
