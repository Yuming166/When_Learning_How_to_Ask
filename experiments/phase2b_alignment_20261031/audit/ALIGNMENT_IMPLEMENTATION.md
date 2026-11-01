# Theory-aligned sampler: contract, pathwise bounds, and numerical limits

`phase2b/aligned.py` implements a new observable-data alignment variant. It leaves every Phase 2a artifact unchanged. The raw `Theory_Note.md` Sections 1–4 were read before implementation; no new independent mathematical report was consumed for this implementation. Root and implementation agent explicitly agreed on deterministic cumulative tracking, square-block forced exploration, delayed square-root updates, and the logged tolerance schedule before code was committed to this directory.

The resulting code is **not** an exact arithmetic implementation of an asymptotic theorem, and passing these tests does not close expected-time achievability. Its auditable differences and fixed numerical floors remain part of the claim boundary.

## Public interface

```python
from phase2b.aligned import TheoryAlignedTracking

policy = TheoryAlignedTracking(public, calibration, planning_R=1024)
action = policy.next(set(range(public['d'])))
policy.observe(action, result)
```

`planning_R` is the logarithmic risk level `log(1/delta)` itself, so R=1024 does not require constructing an underflowing `exp(-1024)`. The calibration ratio is exactly `len(calibration['high'])/planning_R`, with equally long labelled high/low streams required.

`public` contributes only d, the known partition `groups[g]['targets']`, public eta, and optional known finite type accuracies. The sampler retains normalized copies of those fields and the calibration length. It does not retain or read calibration answer values, generating rates, true signs/types, private random seeds, or other public metadata. A supplied Oracle-format field is ignored. No RNG is used.

Task actions are `('query',j,'A'/'B')` and responses provide `result['answer']` in 0/1. Optional type actions are `('type',g)` and reports provide `result['format']` as A/B. All task observations enter `counts[j,m,y]`, all type reports enter `types[g]`, and only designated forced task observations enter `forced[j,m,y]`. Those full counts and reports remain available for the common external GLR; this sampler makes no stopping decision.

The current contract recovers the complete vector and requires every target to remain active. It rejects partial active sets, repeated `next` calls without an intervening observation, mismatched actions, invalid responses, unsupported group counts, and invalid public domains. The read-only coefficient solver supports G<=2. Type actions are omitted from planning when no known `type_accuracy` is supplied.

## Correspondence to Section 4.2

| Requirement | Concrete implementation | Scope |
|---|---|---|
| Forced observations in every task stream | Deterministic square blocks below | Explicit pathwise lower/upper count bounds |
| Estimator uses forced observations only | Means from `forced`, no reference/type/nonforced answers | Tested by changing all excluded inputs |
| Sign from sum of two means minus one | `theta[j] = int(mu[j,0]+mu[j,1] > 1)` | Equality chooses theta=0 |
| Group type from higher oriented mean | Equal-coordinate mean in each format after candidate sign orientation | Equality chooses format A/0 |
| Average estimated high/low reliability | Average the corresponding oriented probabilities across coordinates | Raw values logged before projection |
| Vanishing deterministic interior grid | Ordered grid with n=ceil(sqrt(t+1)), including both outer boundaries | Strict p>q; grid is only for allocation estimates |
| Original continuous KL allocation problem | Read-only Phase 2a `solve_allocation` with all original alternatives | No Gamma shortcut or fixed-level substitution |
| Allocation optimization accuracy improves | Requested epsilon_t=min(1e-4,1/(t+1)) | Actual floating upper/lower gap and floors separately logged |
| Continued adaptation | Update times u_next=u+ceil(sqrt(u+1)) | Last update divided by current time tends to one |
| Track normalized allocation | Largest cumulative deficit, with only predetermined forced overrides | Deterministic O(sqrt(t)) discrepancy bound below |

At update time, let forced empirical response means be mu_jm. Define theta as above, then orient each coordinate's mean by using mu for theta=1 and 1-mu for theta=0. Each group selects the format with the larger average of those oriented means. Raw p/q are the coordinate averages of the selected good/other means. Direct type reports and labelled calibration do not resolve ties or otherwise assist this estimator.

The grid is `r_i=.5+(.5-eta)*i/n`, i=0,...,n, with q_index<p_index and n=max(2,ceil(sqrt(t+1))). It contains q=.5 and p=1-eta. The nearest Euclidean grid point is found by separately rounding the raw indices when ordered, or by choosing the nearest adjacent pair when the order is violated. Rounding ties use a deterministic half-up rule. Its mesh tends to zero, and projection error vanishes at every fixed admissible true p>q. Grid projection is not used by the GLR, which still profiles continuous rates.

## Forced-exploration pathwise bound

Let L=2d be the number of task streams and t the number of completed online actions. For n=0,1,..., designate completed times

\[
t=Ln^2+s,\qquad s=0,\ldots,L-1
\]

as forced actions for task stream s. All other times use tracking. These blocks are disjoint. In particular, the first L actions provide one forced observation in every task stream before the first allocation update.

For m=floor(sqrt(t/L)), every stream has completed epochs 0,...,m-1 and can have at most one more forced observation. Consequently, for every completed prefix,

\[
\lfloor\sqrt{t/L}\rfloor\le F_e(t)\le\lfloor\sqrt{t/L}\rfloor+1,
\qquad
F(t)=\sum_eF_e(t)\le\sqrt{Lt}+L.
\]

Thus each task stream obtains at least sqrt(t/L)-1 forced observations, and the total forced fraction vanishes. These statements count all online actions, including type questions. They are deterministic and do not require any response assumptions.

## Deterministic tracking substitution

Let E=2d+G, let w_s be the predictable normalized allocation held for online action s, and set C_e(t)=sum_{s<=t}w_{s,e}. At a nonforced step the implementation chooses an action maximizing C_e(t)-N_e(t-1). Equivalently, it chooses the minimum of the pre-action actual-minus-target vector A=N-C.

In exact real arithmetic that pre-action vector sums to -1. Its selected coordinate is therefore at most zero, and adding the selected observation leaves that coordinate at most one. Every unselected coordinate decreases by its nonnegative target mass. A forced override can increase the maximum actual-minus-target discrepancy by at most one. Induction gives

\[
\max_e[N_e(t)-C_e(t)]\le1+F(t).
\]

Because the completed-prefix discrepancies sum to zero, their minimum is at least -(E-1)(1+F(t)). Hence

\[
-(E-1)(1+F(t))\le N_e(t)-C_e(t)\le1+F(t),
\]

and the discrepancy divided by t is O(t^(-1/2)) for fixed d,G. This holds for arbitrarily varying predictable targets, including changes caused by observed data. It replaces the randomized allocation-concentration step with a concrete pathwise discrepancy condition; it does not by itself prove optimizer stability or the expected stopping-time bound. Float64 cumulative addition still has rounding error, so the implementation is not an interval-certified realization of this exact-arithmetic bound.

The target cumulative sum includes forced rounds. Since forced rounds are O(sqrt(t)), this convention and an exploitation-only cumulative sum differ by a vanishing fraction.

## Delayed optimization and tolerance contract

Updates start after L observations. If the latest update occurred at u, the next is scheduled at u+ceil(sqrt(u+1)). Between updates, the previous target is held. For completed t between successive updates,

\[
0\le t-u\le\lceil\sqrt{u+1}\rceil\le\sqrt{t+1}+1,
\]

so u/t tends to one. There are O(sqrt(t)) updates: within a square-time band [m^2,(m+1)^2), each update advances at least m steps. Regular per-action bookkeeping is O(d+G), while an update invokes the original solver in 2G or 3G variables with G*2^G continuous alternative constraints, using analytic separation. Fixed G<=2 keeps the alternative family bounded. This is an operation-count characterization, not a guaranteed wall-clock bound.

Every solve requests separation tolerance epsilon_t=min(1e-4,1/(t+1)). It logs the numerical lower/upper cost bounds and their relative gap. The accepted relative gap is at most max(5*epsilon_t,5e-8); when the 5e-8 acceptance floor exceeds the requested vanishing target, `numerical_floor_active=True` is explicit. A tighter retry is allowed once. If the numerical bound is still unattained, or information/weights fail their checks, the policy records a planning failure and raises; there is no silent alternate sampling method.

The read-only Phase 2a solver additionally has fixed 1e-9 LP feasibility tolerances, a 1e-9 radial information pad, 13-decimal cut deduplication, and finite iteration limits. This wrapper allows 200 cutting-plane iterations per attempt and an information-evaluation residual of 1e-7. These floors and the attained gap are recorded at every successful update. The returned primal bounds are floating numerical readouts, not interval-certified optimization bounds. The vanishing requested epsilon alone cannot justify calling this finite implementation asymptotically exact.

Each estimate record includes raw and projected rates, estimated signs/types, forced counts, grid mesh/indices, alpha, expanded action weights, a/b/c allocation, estimated K, requested and attained numerical bounds, fixed floors, update times, CPU time, and wall time. `diagnostics()` also exposes cumulative tracking discrepancies and forced-count bounds. Truth-based estimator errors must be evaluated separately by the experiment harness; no true state is passed into the sampler.

## Executed bounded checks

Run from the Phase 2b directory:

```bash
python -m unittest discover -s tests -p test_aligned.py -v
```

**9/9 tests passed in 0.738 seconds.** The tests include:

- 2,501 completed-prefix checks of the exact forced schedule and lower/upper count bounds;
- 5,000 adversarial changing-allocation steps with forced overrides and both pathwise discrepancy inequalities;
- a direct forced-only estimator hand calculation, invariant under calibration bit flips, direct type-answer changes, nonforced-count changes, and unused Oracle/true-rate metadata;
- independent exhaustive ordered-grid projection checks for multiple grid sizes and raw rates, plus all boundary projections over t=0,...,4096;
- delayed update cadence, a vanishing requested tolerance, and update telemetry;
- real read-only continuous-KL solver smoke checks at boundary rates and weak separation;
- fail-closed behavior when the requested numerical bound is unattained, and explicit reporting when the fixed acceptance floor exceeds the requested target;
- invalid input, pending-action, and all-targets-active contracts.

The two real solver smoke checks use d=2, singleton groups, alpha=0, R=1024, and a forced observation fixture at t=4000. They are numerical functional checks rather than generated trajectories or effectiveness estimates.

| Raw p/q | Grid p/q | Grid mesh | Estimated K | Numerical relative gap | Minimum evaluated information | CPU seconds |
|---|---|---:|---:|---:|---:|---:|
| .95 / .50 | .95 / .50 | .00703125 | 3.2242492147 | 9.2445e-5 | 1.0000000010 | .141 |
| .80 / .79 | .80234375 / .78828125 | .00703125 | 5.3528857496 | 4.1019e-5 | 1.0000000010 | .152 |

The second row makes the finite grid distortion visible: weak raw separation need not be preserved exactly at finite t. The mesh vanishes with t; these two checks do not establish a uniform guarantee as p-q vanishes.

## Preserved failure and limits

The first seven-test execution had six passes and one error. The delayed-update test encountered `FloatingPointError` because computing the upper grid endpoint as `.5+(span*n)/n` could round above .95, first reproducible at t=144 for raw p=q=1. The correction represents the outer endpoints explicitly and computes interior ratios before multiplying by the span. A regression checks every t through 4096. This was an implementation arithmetic error, not an optimizer or theorem counterexample.

The discrepancy, schedule and projection arguments above are local proof-to-code facts. They do not close Theorem 1's uniform tail, optimizer stability, finite-calibration, or expected-time achievability obligations. Fixed iteration/numerical floors and finite-precision cumulative sums remain material limitations. No main run, model/API/GPU call, independent confirmation experiment, or empirical convergence claim was made by this implementation task.

Source hashes at the executed checks:

```text
phase2b/aligned.py
67bdf86cbd21a81bde81fde981b9c00308f35d2f911af766fbd28939ae5b4ab0
tests/test_aligned.py
8299aafbccfbf22a130b9fff9b18b5dac16a9d7a22999f324f8d48fb45654e51
read-only phase2a/coefficients.py
a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f
```
