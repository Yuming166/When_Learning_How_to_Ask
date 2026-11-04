# Recommendation-aware greedy information baseline

`QuadratureDecisionIG(public, order=6)` in `decision_ig.py` selects measurements
using expected information about the **best catalogue item**, rather than the
entire preference vector. It consumes public catalogue/group data and every
observed task reply. It does not consume true signs, types, rates, a true item,
calibration, or a hidden simulator object. Extra public or catalogue keys are
rejected. This module makes no model, API, training, GPU, or network calls.

## Interface and conventions

```python
from decision_ig import QuadratureDecisionIG

public = {
    "d": 3,
    "groups": [0, 1, 1],
    "eta": "1/100",  # optional; this is the default
    "catalogue": {
        "offsets": [0, 0],
        "slopes": [[0, 0, 0], [1, 1, 1]],
    },
}
planner = QuadratureDecisionIG(public)
scores = planner.scores()       # numpy array of length 2*d; units: nats
planner.observe(2 * 1 + 0, 1)  # coordinate 1, format 0, positive raw answer
diagnostic = planner.diagnostics()  # JSON-serializable
```

`groups` is a length-`d` membership vector using contiguous IDs `0..G-1`.
The supported bounded cases have `1 <= d <= 6` and `1 <= G <= 2`.
Theta mask bit `j=1` means negative preference, so mask 0 is all positive.
Raw answer 1 means positive preference. Type mask bit `g` is the better format
`z_g`. Action `2*j+fmt` asks coordinate `j` in format `fmt`. The item utility is
`offsets[i] + slopes[i] @ theta`, with signs in `{-1,+1}`.

The constructor checks all sign vectors using exact rational utility arithmetic.
An exact best-item tie at any sign vector is rejected. Numeric catalogue values
are interpreted through their decimal strings; rational strings such as `1/3`
are accepted. Score ties are returned honestly as ties: the module returns all
scores and reports maximizers within a stated floating-point tolerance. The
caller supplies any deterministic or randomized action tie rule.

## Joint inference and decision objective

The prior is uniform independently over all `2**d` theta masks and `2**G` type
masks. Rates have the continuous uniform prior on the ordered triangle
`1/2 < q < p < 1-eta`. Gauss--Legendre nodes `(s,t)` on `(0,1)^2` map to

```
L = 1/2 - eta
p = 1/2 + L*s
q = 1/2 + L*s*t
dp*dq = L*(p-1/2) ds*dt
```

The triangle area is `L**2/2`; therefore normalized node weights are
`2*s*weight(s)*weight(t)`, not uniform node weights. Order 6 uses **36 rate
nodes**, shared across all discrete states. All discrete states and rate nodes
retain their joint likelihood under the entire observed transcript. Updates
use log weights; reported posterior rate means are diagnostics and are never
substituted into a likelihood.

For item `F=f(theta)` and next answer `Y_a`, the score is
`I(F;Y_a | history) = H(F | history) - E[H(F | history,Y_a)]`.
Likelihood-weighted answer mass is first summed over types and rate nodes,
then over sign states with the same best item. The implementation evaluates
the equivalent weighted Bernoulli KL expression, using a local series to
reduce cancellation for very small information gains. It reports the entropy
subtraction discrepancy. An optional `target="theta"` constructor argument
is a diagnostic full-preference comparator; the item baseline uses the default.

## Common stopping and approximation limits

There is no stopping, forced-exploration schedule, or certification in this
module. The experiment runner must pass **every** task answer to `observe`,
including forced tasks, and apply the same independent certified GLR gate to
all allocation arms. Posterior concentration, a modal item, or a tiny entropy
must never replace that gate.

This is explicitly a **quadrature approximation of the continuous posterior**,
with exact enumeration only of the discrete support. A finite quadrature
posterior is not the exact continuous posterior. There is no quadrature error
certificate, posterior error certificate, or stopping-time optimality claim.
Very long histories can concentrate between quadrature nodes or underflow
negligible state masses. Floating-point scores and near-ties are numerical
allocation outputs, not certificates. The shared design cache contains only
immutable public likelihood tables; posterior arrays are independent per run.

## Deterministic checks

Run from the repository root:

```sh
python -m unittest discover -s experiments/recommendation_loop_20261103 -p test_decision_ig.py -v
```

Checks cover normalized triangle moments, reply prediction normalization,
nonnegative entropy/information, item-vs-theta targeting, no-history symmetry,
bit/reply conventions, independent batch-vs-incremental likelihood, hidden-key
rejection, exact utility tie rejection, a concentrated numerical posterior,
and order-4/order-8 sensitivity on one fixed short transcript. The sensitivity
check is a deterministic numerical fixture, not statistical efficacy evidence
and not a rule for selecting quadrature order from pilot results.

On the six-reply sensitivity fixture, order 4 and order 8 differ by approximately
`4.71113e-6` nats in the largest action score. The likelihood-only item marginal
agrees to floating precision; the next-answer integrand can have degree eight
in `s`, beyond order 4's polynomial exactness through degree seven. The test
uses an explicit `1e-4`-nat sensitivity tolerance rather than incorrectly
asserting roundoff agreement. This is no bound on other transcripts, and the
default remains order 6 regardless of pilot outcomes.

## Local verification and runtime receipt

All 11 deterministic unit tests passed (`0.051` seconds for the recorded test
run). A separate fixed 2,000-reply transcript, without a simulator or hidden
rates, exercised `scores()` followed by `observe()` at every step for
`d=6`, membership `[0,0,0,1,1,1]`, and order 6. This is 9,216 joint states.
Recorded process CPU time on the current host was `1.48310` seconds total,
approximately `0.74155` milliseconds per score/update pair; cold construction
was `0.16181` seconds and cached construction `0.00191` seconds. These timings
are host/fixture-specific. The raw positive-reply table occupied 884,736 bytes
(log-likelihood tables are additional). The final entropy subtraction
discrepancy was `1.48e-16` nats. Two planners shared immutable public tables
while keeping independent posterior arrays.
