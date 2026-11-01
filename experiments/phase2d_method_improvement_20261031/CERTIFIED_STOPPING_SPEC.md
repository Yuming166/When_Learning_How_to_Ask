# Certified Stopping Prototype: bounded numerical contract

Date: 2026-10-31. Scope: Phase2d P0, `d <= 4`, without new model calls or
confirmation-seed use. This document specifies the new module
[`phase2d/certified.py`](phase2d/certified.py). Historical implementations
remain unchanged.

The gate gives a conservative numerical implication under an explicit
arithmetic and model contract. It is not a proof-assistant-verified program,
a new asymptotic-optimality theorem, or an empirical verification of a tiny
error probability. High precision by itself is not its justification.

## Interface and decisions

```python
certify_stop(
    counts, groups, calibration=None, type_answers=None,
    type_accuracy=None, R=None, eta=.05, candidate_theta=None,
    precisions=(50, 80, 120), *, include_profiles=False,
)
```

`counts[j][m][y]` contains nonnegative integer raw-answer counts, with shape
`(d,2,2)`. Python integer-index-compatible scalar types, including NumPy
integer scalars, are accepted; integral-looking floats and Python booleans
are rejected. `groups` is a partition of all targets or a contiguous
zero-based membership vector. `calibration` contains exactly two labelled,
equally long bit sequences, `high` and `low`. `type_answers` contains one
bit sequence per group. Known per-group accuracies must be supplied when
reports are present. The signature accepts no true theta, true types, true
levels, seed, oracle state, or evaluation feedback.

`R > 0` means the exact real quantity `log(1/delta)` supplied to the gate;
no exponential conversion is performed. Constants may be integers, Python
floats, Decimal values, or Fractions. Floats mean their exact stored binary
values; Decimal and Fraction values mean their exact represented rational
values. This applies to `eta`, `R`, and each type accuracy. In particular,
the rate upper endpoint is **`1 - Fraction.from_float(eta)`**, not
`Fraction.from_float(1 - eta)`. No decimal-intent reconstruction occurs.

If `candidate_theta` is supplied, only that sign vector is tested, while
every competing sign and every group-type vector remain in the maximization.
If omitted, the largest profile lower endpoint selects the candidate, with
the first lexicographic state resolving equal lower endpoints. No assumption
that an externally supplied candidate is correct is needed for acceptance.

The JSON-serializable return value includes:

| Field | Meaning |
| --- | --- |
| `status` | `certified`, `rejected`, or `undetermined` |
| `certified`, `interval_certified` | Both true only for a rigorous crossing under this contract |
| `decision` | `stop` or `continue_or_abstain` |
| `theta`, `candidate_theta` | The tested candidate; null after arithmetic failure |
| `candidate_loglik_lower/upper` | Enclosure of its profiled log likelihood |
| `wrong_loglik_lower/upper` | Enclosure of the maximum over all other signs and types |
| `gap_lower/upper`, `beta_lower/upper` | Outward interval endpoints, as strings |
| `lower_witness` | A type vector and exact rational rate fit supporting the candidate lower bound |
| `precision`, `precision_attempts` | Used precision and every attempted crossing decision |
| `operation_counts`, `timings_seconds` | Arithmetic work counts and measured elapsed time |
| `exact_input_parameters` | Rational strings recording input interpretation and exact domain endpoint |
| `profiles` | Optional complete per-sign interval table and lower witnesses |

Accept **only** when `gap_lower > beta_upper`. If
`gap_upper <= beta_lower`, return `rejected`, meaning this candidate's
strict crossing is excluded at this transcript. Otherwise increase precision
according to the supplied finite schedule; remaining overlap is
`undetermined`. Both negative outcomes require continued sampling or
abstention. A deadline decoder's error is outside this gate's certificate.
Malformed/unsupported inputs raise `ValueError`. Caught arithmetic failures
return `undetermined` with null endpoints and no certificate.

## Exact continuous maximization

For a candidate sign vector theta and type vector z, a task answer matching
theta is a success. Format `z[group(j)]` is assigned to the high channel;
the other format is assigned to the low channel. Labelled reference successes
are added to their corresponding channels independently of theta and z.
Let their exact aggregate counts be `(a,n)` and `(b,m)`. Then

\[
\ell(\theta,z,p,q)=a\log p+(n-a)\log(1-p)
 +b\log q+(m-b)\log(1-q)+\ell_{\rm type}(z),
\]

where `ell_type` is the sum of the observed type-report match/mismatch log
probabilities, using the supplied known accuracies. This is the likelihood
of the ordered observations; state-independent binomial coefficients are
unnecessary.

Set `U = 1 - eta`, exactly. The maximization domain is
`1/2 <= q <= p <= U`. For positive channel weights, clip the empirical means
`a/n` and `b/m` separately to `[1/2,U]`. If their order is feasible, these
maximize the sum of the two one-dimensional concave objectives. If order
is violated, the order constraint is active: on `p=q`, the objective is the
single binomial log likelihood with counts `(a+b,n+m)`, giving the clipped
pooled mean `(a+b)/(n+m)` for both coordinates. Concavity establishes the
global maximum. All comparisons and divisions here use Fractions.

If only the low channel is observed, fit q and set p=q. If only the high
channel is observed, fit p and set q=1/2. If neither is observed, choose
p=q=1/2. These are maximizing representatives, including nonunique cases.
The likelihood is continuous on the compact domain because eta is positive.
Its closed-domain maximum also equals the supremum on the corresponding
dense strict-order domain. In particular, a wrong-sign maximum on p=q must
not be discarded.

Enumerate all `2^d * 2^G <= 256` joint states. Exact analytic profiling means
the upper bound covers **all continuous rates**, not just a numerical grid,
optimizer output, or finite collection of rate candidates.

## Outward arithmetic argument

Three explicit Decimal contexts are created per attempted precision: downward
(`ROUND_FLOOR`), upward (`ROUND_CEILING`), and nearest (`ROUND_HALF_EVEN`).
They have explicit exponent limits, flags, and traps. Endpoint operations
never use the ambient Decimal context; in particular, no global unary plus
or minus is used to transform an endpoint.

For a positive rational `x=a/b`, Decimal construction from the integer
numerator and denominator is exact. Directed division gives `x_lo <= x <= x_hi`.
Python documents `ln` as correctly rounded to nearest even. A one-neighbor
expansion of the rounded logarithm therefore gives

\[
\operatorname{nextMinus}(\operatorname{ln}_{\rm RN}(x_{lo}))
\le \log x \le
\operatorname{nextPlus}(\operatorname{ln}_{\rm RN}(x_{hi})).
\]

This follows from log monotonicity and correctly rounded nearest evaluation;
merely setting a directed context for `ln` would not suffice. The exact
special case log(1)=0 avoids an unnecessary neighbor expansion. The needed
library contracts are documented in
[Decimal.ln](https://docs.python.org/3/library/decimal.html#decimal.Decimal.ln),
[Decimal.next_minus/next_plus](https://docs.python.org/3/library/decimal.html#decimal.Decimal.next_minus),
and [rounding modes](https://docs.python.org/3/library/decimal.html#rounding-modes).
[Fraction construction](https://docs.python.org/3/library/fractions.html#fractions.Fraction)
documents exact conversion of the represented float value.

Every likelihood term has a nonnegative integer weight. Multiply its lower
endpoint downward and upper endpoint upward; add lower endpoints downward
and upper endpoints upward. This encloses each joint-state maximum computed
above. Taking maxima preserves enclosure: if every `L_i <= f_i <= U_i`,
then `max_i L_i <= max_i f_i <= max_i U_i`.

Write the candidate profile enclosure as `[A_lo,A_hi]` and the maximum over
all other signs/types as `[B_lo,B_hi]`. Directed subtraction gives

\[
g_{lo}=\operatorname{RD}(A_{lo}-B_{hi})
\le F(\theta_c)-\max_{\theta\ne\theta_c}F(\theta)
\le\operatorname{RU}(A_{hi}-B_{lo})=g_{hi}.
\]

Independently enclose the complete boundary

\[
\beta=R+2\log(M+1)+\sum_{j,m}\log(N_{jm}+1)
              +\sum_g\log(K_g+1).
\]

The two labelled reference streams each have length M; task counts and type
counts are recomputed from the supplied full transcript. Empty streams
contribute log(1)=0. The threshold is enclosed using the same rational-log
construction and directed addition, including a directed rational enclosure
of R. Thus `g_lo > beta_hi` implies the exact GLR exceeds the exact boundary.
Strict comparison is a deliberate conservative choice; exact equality need
not be accepted.

## Numerical walkthrough: preserved false-crossing counterexample

The Phase2c raw counterexample supplies one target, no references/type
reports, an empty second format, and `n = 1_000_000_000_152` positive answers
on the first format. Let `eta=.125` and supply the Python float
`R=559615787992.8533`, whose exact rational value is
`2292186267618727/4096`. The best positive-sign likelihood is `(7/8)^n`;
the best opposite-sign likelihood is `(1/2)^n`. Therefore

\[
g=n\log(7/4),\qquad \beta=R+\log(n+1).
\]

At 50 decimal digits the gate returns:

```text
gap_lower  = 559615788020.48428603707274884000164556616210307121
gap_upper  = 559615788020.48428603707274884000164556616210307127
beta_lower = 559615788020.48429260045654820820419295621356435021
beta_upper = 559615788020.48429260045654820820419295621356435022
```

The outward residual lies between
`-0.00000656338379936820254739005146127901` and
`-0.00000656338379936820254739005146127894`. The new result is `rejected`.
The unchanged historical float implementation accepts this transcript even
with its additional heuristic guard. This static large-count example is
a numerical counterexample, not an observed risk violation in an experiment.

## Validation and trust boundary

[`tests/test_certified.py`](tests/test_certified.py) contains 13 deterministic
tests. Tiny fixtures independently maximize **exact rational products of
integer powers** over a finite rational set containing all analytic extrema;
this is a test oracle, not the production upper-bound construction. A second
independent check encloses logarithms with the rational series

\[
\log x=2\sum_{k=0}^{N-1}\frac{t^{2k+1}}{2k+1}+r_N,
\quad t=(x-1)/(x+1),\quad
0\le r_N\le\frac{2t^{2N+1}}{(2N+1)(1-t^2)},
\]

after exact power-of-two scaling into `[1,2)`. The exact log(2) contribution
uses the same series, with the appropriate endpoint reversal for negative
scaling exponents. Other tests cover pooling, clipping, zero-weight cases,
all 256 d=4 states, arbitrary wrong candidates, the binary-float endpoint
distinction, the old false acceptance, precision escalation, null-endpoint
arithmetic failures, and hostile ambient Decimal precision/traps. A 150-digit
calculation is an additional cross-check, never the enclosure proof.

The implementation is bounded to d<=4, total observations <=2^50, rational
constant numerator/denominator lengths <=4096 bits, and one to six strictly
increasing precisions in `[16,512]`. Decimal constants also have preconversion
size limits. Inputs must be finite sequences. These are supported-input
limits, not a general denial-of-service defense for malicious Python objects.
No unsupported size silently falls back to floating-point certification.

The module uses only the standard library. Import it before filesystem
confinement; the call itself performs no imports, file or network access,
sampling, or model operations. The local verification environment was
CPython 3.13.13 with libmpdec 4.0.0. The trusted base includes correct Python
integer/Fraction arithmetic, the stated CPython/libmpdec Decimal contracts,
the hand-derived analytic maximization and model specification, and faithful
transcript aggregation. Runtime/hardware/library faults and implementation
proof-assistant verification are outside this guarantee.

The model-level anytime error argument additionally requires the original
correctly specified independent observation streams, predictable adaptive
sampling, fixed known accuracies, and a risk setting fixed before observing
the offline data. It is unconditional over those offline observations;
restarting the claim after a favorable realized calibration is unsupported.
Under those assumptions, the conservative event is a subset of the exact
GLR crossing event and inherits its wrong-certified-output bound. The gate
does not establish eventual stopping, expected-cost finiteness, an optimal
cost coefficient, or a guarantee for uncertified endpoint decisions. See
[`STOPPING_PROOF_AUDIT.md`](STOPPING_PROOF_AUDIT.md) for the separately derived
model-level argument and adversarial implementation review.

Reproduce the deterministic module checks from the repository root:

```bash
PYTHONPATH=experiments/phase2d_method_improvement_20261031 python -m unittest discover -s experiments/phase2d_method_improvement_20261031/tests -p test_certified.py -v
```
