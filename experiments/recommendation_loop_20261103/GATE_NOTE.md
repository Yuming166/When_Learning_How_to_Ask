# Recommendation likelihood and bounded certificate

This is a separately tested extension to `d <= 6`, `G <= 2`, with no labelled
calibration observations (`M=0`) and no type-report actions. It does not invoke
the historical `d <= 4` stopping function outside its validated scope. All work
here is CPU-only; it requires no model, network, training, or posterior grid.

## Public interface and conventions

`public` contains exactly `d`, `groups`, `eta`, and `catalogue`. `groups` is a
length-`d`, contiguous zero-based group-membership vector. `eta` is an exact
rational string (`"1/100"` in the pilot; `"1/20"` is also tested). The catalogue
contains exactly `offsets` and `slopes` and defines

```
utility_i(theta) = offsets[i] + sum_j slopes[i][j] * theta[j].
```

Every one of the `2**d` full-cube sign vectors must have a unique maximizing
item, checked using exact rational arithmetic. Item IDs are catalogue row
indices. Numeric float catalogue entries denote their exact stored binary
values. Rational strings, integers, `Fraction`, and finite `Decimal` constants
are also accepted. Extra public keys, including hidden truth/rate/type fields,
are rejected. The estimator consumes only public data and observation counts.

Counts have shape `(d,2,2)` and contain nonnegative integers; the final index is
the **raw answer bit**, with `1` meaning a positive sign. A theta-mask bit of
`1` means `theta[j] = -1`; mask zero is all positive. Consequently the success
count for a state is `counts[j,fmt,1-((theta_mask>>j)&1)]`. A type-mask bit is the
better format `z[g]`. Counts are bounded by a total of `2**50`; booleans,
integral-looking floats, negative values, overflow, and malformed shapes are
rejected. Public rational constants are bounded to 4096 bits.

`JointLikelihood(public)` exposes:

- `theta_signs`, `winner_by_theta`, `items`, `groups`, `d`, and `G`;
- `estimate(counts)`: `theta_mask`, `z_mask`, `p`, `q`, and `item`;
- `best_table(counts)` (alias `besttable`): floating likelihood/rate arrays of
  shape `(2**d,2**G)`, plus integer sufficient statistics;
- `decision_gap(counts,candidate_item=None)`: `item`, `gap`, candidate and
  alternative profile log likelihoods, and `class_loglik`. It always reports
  `certified=False` and has no threshold or stopping authority.

All theta and type states are enumerated. For each state the continuous channel
is maximized over the entire closure `1/2 <= q <= p <= 1-eta`. Weighted empirical
rates are clipped to this interval and pooled when their order is reversed.
Zero-weight rates are assigned a feasible deterministic maximizer. The policy
table uses vectorized integer sufficient statistics and floating likelihoods;
it is a plug-in MLE, not an exact posterior. Extremely small positive eta that
underflows floating arithmetic is excluded from `best_table` while remaining
available to the exact gate within its rational-constant scope.

`CertifiedDecisionGate(public,R=3,precisions=(50,80,120)).check(counts,
candidate_item=None)` returns a JSON-safe dictionary. `R` must be a positive
exact integer. `status` is `CERTIFIED`, `NOT_CERTIFIED`, or `UNDETERMINED`.
The output `item` is populated **only** for `CERTIFIED`; other outcomes require
continuation or abstention. `candidate_item` and profile bounds are diagnostics.
Endpoints are decimal strings, with both `threshold_*` and `beta_*` aliases.
The result records its dimension, group, observation, state, numerical, and
trust scope. The precision schedule has 1--6 increasing entries in `[16,512]`.
Arithmetic failure aborts certification; unresolved interval overlap returns
`UNDETERMINED`. Increasing precision may resolve earlier overlap.

## Recommendation-level likelihood and strict stopping rule

Write `b(theta)` for the exact public catalogue winner. The relevant classes are

```
L_i = max_{theta: b(theta)=i} max_z max_{1/2<=q<=p<=1-eta} log likelihood.
gap_i = L_i - max_{k!=i} L_k.
beta = R + sum_{j,fmt} log(N[j,fmt] + 1).
```

The profile within an item is a **maximum**, not a posterior sum. Every state
whose catalogue winner equals the candidate item belongs to the same side of
the comparison, even if its signs or types differ. Only other items are
alternatives. Certification requires `gap_lower > beta_upper`, a strict
outward-bounded comparison. A supplied candidate restricts the item under test,
without restricting any theta, type, or continuous fit within either side.
A catalogue with a constant winner on the full cube is vacuously certified;
its gap is represented by the string `"+Infinity"`.

The exact gate computes rational MLEs for every state and outward Decimal
likelihood intervals for every state before making the class comparison. It
reuses only `_ordered_mle` and `_Intervals` from the read-only file
`experiments/phase2d_method_improvement_20261031/phase2d/certified.py`, loaded
through `importlib`. Its SHA256 at implementation time is
`162fe61943bdebf2b297cdca914a734e9b0befcf66939c800a00a9a35820130c`.
The old validation, state construction, and `certify_stop` function are not
called by the new implementation. The original source remains an import-time
dependency. The gate does not use floating fits or discretized posterior mass
to authorize a stop.

## Mathematical validity boundary

The statistical statement is conditional on a fixed true sign/type state in
the public space, fixed true rates in the stated continuous domain, and raw
responses following the stated independent Bernoulli channel conditional on
the predictably selected action. A recommendation is the public utility winner,
not an external semantic label. Correlated respondent errors, model drift,
misspecified grouping/channel, future-answer access, or semantic benchmark
validity do not follow from this certificate.

For completeness, the threshold has a direct anytime argument. Let `L_*` be
the sequential likelihood under the fixed true channel and let `U_t` be the
product of independent uniform-Beta mixtures over the raw Bernoulli probability
of each task/format action. Under predictable action selection, `U_t/L_*` is a
nonnegative mean-one likelihood-ratio martingale. For every observed action
stream, its unrestricted Bernoulli maximum is at most `(N+1)` times its
uniform-mixture likelihood, since its maximized binomial probability is at most
one. Therefore the maximum over the whole structured channel is at most
`U_t * product_action(N_action+1)`. If a wrong item is certified, the alternative
class contains the true state, so the exact strict gap implies
`U_t/L_* > exp(R)`. Ville's inequality bounds the probability of any wrong
certified recommendation by `exp(-R)`. There is no extra union over theta,
types, items, or times in this argument. In particular `R=3` corresponds to
`exp(-3)`, approximately `0.0497871`, rather than exactly `0.05`.

The numerical implication is conditional on the analytic two-rate reduction,
Python exact integer/Fraction operations, and the documented correctly rounded
Decimal logarithm and directed arithmetic contracts. This is not verification
in a proof assistant. Tests check the implementation across the stated cases;
they do not exhaust all admissible counts or establish empirical effectiveness.

Any harness may use a floating gap to decide when to request exact checking.
Only `check(...)["status"] == "CERTIFIED"` authorizes output. Less frequent
checking can delay stopping, so this component does not promise the earliest
possible crossing, an optimal allocation, or an asymptotic allocation contract.

## Tests and reproducibility

Run from the repository root:

```
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s experiments/recommendation_loop_20261103 \
  -p test_likelihood_gate.py -v
```

All 16 tests passed in 1.56 seconds on the implementation host (NumPy 2.5.3,
SciPy 1.18.1). Coverage includes:

- 340 independently optimized SciPy raw-answer inner maxima over dimensions
  1, 2, 4, and 6, plus order pooling, upper clipping and empty streams;
- 16 comparisons with the original gate within `d <= 4`, using singleton
  recommendation classes and explicitly converted raw-bit orientation;
- the exact possible-history OR witness below and explicit exclusion of
  other theta states that produce the same item;
- a real precision boundary at `10**14` observations: precision 16 leaves
  gap `[35.19,35.27]` overlapping threshold approximately `35.23619130191665`,
  returns `UNDETERMINED` with no item, and precision 50 certifies;
- forced arithmetic failure, ambient Decimal context changes, malformed
  inputs, unused catalogue items, serialization, input immutability, the exact
  count bound, constant recommendations, and all 256 d=6/G=2 state fits.

The possible-history witness uses d=2, one group, eta=`1/20`, catalogue offsets
`[0,1]` and slopes `[[0,0],[1,1]]`. Item 1 wins whenever either sign is positive.
Twenty raw positive responses from action `(coordinate=0,format=0)` and no other
responses have gap `20*log(1.9)`, approximately `12.83707772344790`, exceeding
`3+log(21)`, approximately `6.04452243772342`. The recommendation gate certifies
item 1. A full-sign gate cannot certify because the second sign is unobserved;
the theta masks 0 and 2 have identical likelihood and the same item. This
history has positive probability under an admissible channel. It is a witness
of the stopping target distinction, not an estimate of typical savings.

A local runtime sample with random d=6/G=2 counts measured approximately
0.27 ms per floating `decision_gap` (500 calls) and 53 ms per exact `check`
(50 calls). These timings are host/input-specific. The exact search has up to
256 states and may evaluate many high-precision logarithms; using it after
every answer can dominate a cheap policy. The floating prefilter can reduce
that cost without acquiring stopping authority.
