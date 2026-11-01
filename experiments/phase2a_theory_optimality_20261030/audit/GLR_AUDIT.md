# Joint GLR and endpoint-MLE audit

Task D is implemented for bounded development. The small-d stopping implementation exhaustively profiles every discrete candidate and analytically maximizes the continuous binomial likelihood. It does not provide an interval-arithmetic certificate or an empirical validation of delta-correctness.

## Interfaces and observation conventions

```python
profile_glr(counts, groups, calibration=None, type_answers=None,
            type_accuracy=None, delta=.05, eta=.05, oracle_types=None)

endpoint_mle(counts, groups, calibration=None, type_answers=None,
             type_accuracy=None, eta=.05, oracle_types=None,
             *, include_profiles=False)
```

- `counts[j,m,y]` is a nonnegative integer count, with format `m=0/1` and raw answer `y=0/1`. Theta and group type estimates also use `0/1`; the theory's signs correspond to `2*theta-1`.
- `groups` primarily takes a partition such as `[[0,1],[2,3]]`. A contiguous group-membership vector such as `[0,0,1,1]` is also accepted.
- `calibration={'high': [...bits...], 'low': [...bits...]}` contains the two labelled independent reference streams. Equal length `M` is required. Missing calibration means both streams are empty.
- `type_answers[g]` contains raw `0/1` reports of type, with known independent `type_accuracy[g]` strictly between one half and one. Accuracy is never estimated from these reports. Empty type streams are valid.
- `oracle_types` fixes only current types. Signs and both continuous levels remain unknown and are still profiled. Numeric `0/1` types are required; no ambiguous A/B conversion occurs.
- Inputs above are observations or known public experimental parameters. The interfaces accept no latent true signs, true types (outside the explicit Oracle argument), or true generating rates.

The GLR returns best theta/types/rates, best *different-theta* competitor and its types/rates, both log likelihoods, gap, beta, a float64 boundary-crossing flag `certified`, `interval_certified=False`, exhaustive-search scope, stream counts, the per-theta profiles, and component timings. Ties choose the first lexicographic candidate. `certified` is a computational threshold result within the reported floating-point scope; it is not a statement that arithmetic rounding has been rigorously enclosed.

## Exact optimization problem and numerical limits

For fixed candidate theta and types, a task observation is a success when its raw answer equals that candidate theta. Task successes and failures are aggregated into candidate good/low blocks, and the labelled reference successes/failures enter their respective blocks. The two fitted rates maximize

\[
S_p\log p+(N_p-S_p)\log(1-p)
+S_q\log q+(N_q-S_q)\log(1-q)
\]

over the closure `0.5 <= q <= p <= 1-eta`. Separately clipped empirical rates are optimal when ordered. If both blocks have positive weight and violate the order, their successes and weights are pooled and the common rate is clipped. This follows from concavity and the active-order boundary; there is no continuous grid or local numerical optimizer in production.

An unobserved low block is represented by `q=.5`. An unobserved high block is represented by `p=q`. When both are empty, `p=q=.5`. These deterministic choices are maximum-likelihood representatives, and need not be consistent estimators of unobserved levels. Known-accuracy type-report likelihoods add a type-dependent constant before profiling each theta over all type vectors.

For `profile_glr`, every one of `2^d` theta vectors and `2^G` allowed types is enumerated, with the hard cap `d<=8`. The maximum number of joint candidates is 65,536, including singleton groups. Oracle types leave one type candidate. The best competing *theta profile* is used, rather than the second-best joint state, because different types can share the same theta.

The stopping boundary is exactly the stated streamwise correction:

\[
\beta=\log(1/\delta)+2\log(M+1)
+\sum_{j,m}\log(N_{jm}+1)+\sum_g\log(N_g^{\rm type}+1).
\]

Zero-count streams contribute zero. Labelled reference observations are not counted as online queries. Full ordered-observation likelihoods are used; adding state-independent binomial coefficients would not change the GLR.

Arithmetic is float64, with no rational or interval enclosure. Counts are integral and total observations are capped at `2^50`, so the aggregated count arithmetic remains within the exact-integer range of float64; logarithms, fitted ratios, and likelihood subtraction are still floating-point approximations. A near-zero gap or near-boundary crossing therefore has no rigorous rounding guarantee. Enumerating all states and analytically solving the continuous maximum removes search approximation, but does not eliminate arithmetic rounding. Runtime is bounded through the explicit dimensions/state count, not through a guaranteed wall-clock deadline.

The separate `endpoint_mle` extension permits `d<=16,G<=2`, at most 262,144 joint candidates. It shares the same exhaustive likelihood maximization, and returns no gap, boundary, or certificate fields. It is a common fixed-budget endpoint decoder, including when `M=0`; it has no d=16 repeated-stopping or error-rate claim. Full theta profiles are omitted by default and available only through `include_profiles=True`. Binary candidate arrays are generated by vectorized bit shifts, cached by dimension, and read-only; they retain exactly the original lexicographic enumeration.

## Independent checks and reproducible receipts

Commands, run from the Phase 2a directory:

```bash
python -m unittest discover -s tests -p test_glr.py -v
python audit/glr_checks.py
```

The unit suite passed **11/11 tests** in 2.866 seconds after candidate caching, using Python 3.13.13, NumPy 2.5.3 and SciPy 1.18.1. Checks cover zero observations, zero calibration, labelled calibration only, type-only observations, sign-profile ties, pooled rates, unobserved rate blocks, fixed Oracle types, exact streamwise beta, actual boundary crossing, input rejection, the complete d=8 singleton-group search, and the separate bounded d=16 endpoint API. Repeated endpoint estimates and full small-d profiles remain identical with the candidate cache.

The independent scalar implementation uses nested Python enumeration, evaluates raw answer probabilities, and checks all feasible interior/edge stationary points and triangle corners. A second checker enumerates the same discrete states but maximizes the raw-observation likelihood with SciPy SLSQP, independently of the production aggregate/isotonic helper. The table gives maximum error over *every theta profile*, not just the selected optimum.

| d | G | Joint states checked | Scalar maximum absolute error | SciPy maximum absolute error | Maximum SciPy feasibility residual | SciPy non-success statuses |
|---|---|---:|---:|---:|---:|---:|
| 4 | 2 | 64 | 1.066e-14 | 9.795e-12 | 2.246e-13 | 0 |
| 6 | 2 | 256 | 1.421e-14 | 7.326e-12 | 9.215e-14 | 0 |
| 8 | 2 | 1,024 | 2.132e-14 | 1.157e-11 | 8.876e-13 | 0 |

Thus 1,344 continuous state optimizations were independently checked. Tolerances are numerical checks, not exact arithmetic proofs. The independent optimizer's statuses and constraint residuals are emitted by `audit/glr_checks.py`; non-success statuses would remain present in its output.

Five local timing samples per small-d setting gave these medians:

| d | G | Joint states | Median seconds |
|---|---|---:|---:|
| 4 | 2 | 64 | 0.000414 |
| 6 | 2 | 256 | 0.000442 |
| 8 | 2 | 1,024 | 0.000588 |
| 8 | 8 | 65,536 | 0.008729 |

Before candidate caching, one d=16,G=2 endpoint decode took 0.155 seconds; a second audit execution took 0.150 seconds and an isolated fresh-process endpoint took 0.177 seconds. After caching, a cold call took 0.0896 seconds, and five warm calls took 0.0934, 0.0987, 0.0981, 0.0838 and 0.0788 seconds (median 0.0934 seconds). Theta, types, rates and maximized likelihood were identical across these warm calls. These are host observations, with no guaranteed wall-clock bound or d=16 sequential-stopping claim. The isolated process reached 88,308 KiB peak resident memory. Combined-check `getrusage` peaks varied from 131,880 KiB to 2,483,956 KiB, without an established cause; no measured memory-upper-bound claim is made. The checker now emits Linux `/proc/self/status` VmRSS/VmHWM alongside `getrusage` for transparent follow-up.

A single bounded d=4,G=2 round-robin smoke path used seed 49304, fresh Bernoulli answers, generating p=.85/q=.60, empty reference streams, delta=.05, checks every 16 online queries, and a cap of 1,024. The first float64 boundary crossing occurred at **t=352**, with gap **34.3834855782** and beta **33.4490321917**, returning the correct `[0,1,0,1]`. This only exercises the implemented stopping behavior. One correct path is not evidence that an error probability is below delta.

## Preserved failing check and claim boundaries

The first unit-suite execution was 9/10 passing. `test_membership_vector_and_sign_flip_equivariance` initially asserted that the chosen lexicographic MLE itself transforms under flipping one answer coordinate. The d=4 case actually had two tied theta profiles, indices 11 and 15, both with log likelihood -17.72468971503388. A coordinate flip can change which tied state is lexicographically first, so the assertion was too strong. The corrected check compares every permuted likelihood profile, retains deterministic tie handling, and checks the unchanged gap. No GLR arithmetic or tie selection was changed to force this test to pass.

The implementation verifies the likelihood optimization and threshold transcription. It does not independently prove Theorem 1 or the mixture-martingale argument, establish delta-correctness empirically, certify floating-point rounding, support d=16 sequential stopping, or compare algorithm effectiveness. No model/API/GPU calls or confirmation experiments were used for these checks.

Source hashes at the executed check:

```text
phase2a/glr.py   7ed182834957d09546e855468fc14082d894bb54308f3ef728d591d1e4a330f6
tests/test_glr.py e12f9f3e86a973d5e1708deeb3a1005a42c26c0d184a5a5c3c9fcae34c0fec00
```

`audit/glr_checks.py` recomputes hashes and prints fresh evidence, without mutating result files.
