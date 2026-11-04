# Frozen catalogue-mechanism validation protocol

Date: 2026-11-04. This document and the executable analysis are frozen before
main-run outcomes. Engineering smoke runs use separate response seeds, remain
preserved, and are excluded from efficacy statistics.

The purpose is to examine finite-query behavior on two independently derived
catalogue geometries and their known sharing partitions. The experiment can
show a finite manifestation or a negative diagnostic. It does not prove an
asymptotic theorem or establish broad method superiority.

## Four theory-derived cells

All preferences are positive. Utilities are affine and evaluated exactly when
constructing the public catalogue. Calibration M=0.

| Cell | Public catalogue | Known groups, 1-based | Theoretical premium |
|---|---|---|---|
| weighted5_zero | U0=0, U1=3θ1+2θ2+2θ3+θ4+θ5 | (12,345) | zero |
| weighted5_positive | same catalogue | (14,235) | strictly positive |
| genuine6_zero | U0=0; U1=(-6,-4,-4,-2,-2,0)·θ; U2=-1+(0,-2,-2,-4,-4,-8)·θ | (123456) | zero |
| genuine6_positive | same catalogue | (123,456) | strictly positive |

These are the explicit constructions in `CATALOGUE_EXAMPLES.md`. The weighted
pair has matched group sizes (2,3); the genuine three-item catalogue has all
three items winning somewhere on the full cube. Only its all-positive item-0
state is empirically tested here.

True rates are p=4/5, q=3/5; eta=1/100. Every group has true better format A
(type bit zero). Keeping the same better format at every coordinate isolates
sharing from a change in the response channel under partition changes. The
selection policies do not receive types, rates, theta, seeds, or winners.
Nevertheless a fixed-A strategy would be a trivial strong alternative in these
particular controlled states. This study is not a realistic hidden-reliability
discovery benchmark, and it cannot support that claim.

## Sampling and complete denominator

Six new seed indices 0–5 are fixed for each catalogue. Stable SHA256-derived
action-indexed uniform tapes are shared across partitions, risks and all arms
within each catalogue/seed pair. Different catalogue/seed pairs have independent
streams. Thus there are 12 independent response-tape clusters conditional on
two fixed constructed profiles, not 48 independent users.

Risks R=3 and R=9 correspond to model bounds exp(-R). With four cells, six seeds,
two risks and three arms, the denominator is 144 trajectories. Cap=2,500 replies
per trajectory, at most 360,000 main-run Bernoulli observations. Each requested
answer is a fresh independent Bernoulli draw conditional on the fixed channel.
No Qwen, paid API, GPU, training, or natural-user simulation is used.

## Frozen policies and common certification

Arms are the existing `decision_kl`, repaired `decision_ig`, and `round_robin`.
The original implementation is imported without editing. A process-local
factory selects the frozen `RelativeIGPolicy`, which repairs only IG's numeric
tie handling and delegates other arms unchanged. IG retains Q6 quadrature.
The KL allocation retains tolerance 1e-6, maxiter150, all-data joint MLE,
unidentified-rate uniform fallback, forced schedule, and update cadence.

All arms use the same exact recommendation-level gate. At each reply, compute
the floating GLR gap and beta=R+sum_action log(N_action+1). Run the exact gate if
gap>=beta-1, at every 50th reply, or at the cap. Stop only when the outward-bound
Fraction/Decimal gate certifies. A terminal guess, posterior agreement, capped
path or floating crossing is never called certified. Common delayed checks do
not claim earliest ideal-GLR stopping.

At most two worker processes run, each pinned to one CPU and using single
BLAS/OpenMP threads. Policy, gate, total CPU and wall times are retained.
No trajectory replacement, retry, adaptive seed expansion, parameter tuning,
or outcome-dependent exclusion is allowed.

## Predeclared analysis

Primary finite cost is certified query count; every noncertified/failed path
receives the full 2,500 cap in restricted-cost comparisons. Certification,
errors, caps, failures and postprocessing failures remain separate counts.
This cost for censored paths is not their completed stopping time.

For every cell/risk/arm retain the six seed costs and mean. Policy comparisons
retain paired baseline-minus-KL vectors and win/tie/loss counts. Partition
contrasts retain paired positive-minus-zero vectors for each catalogue/risk/arm.
Pooled policy contrasts weight the two catalogue anchors and two partitions
equally. Bootstrap 10,000 resamples of six response-seed indices within each
catalogue; reuse each resample jointly across arms/partitions/risks. Report
percentile 95% intervals without claims of asymptotic precision from six seeds.
The two catalogues and profiles are fixed; intervals do not cover profile,
catalogue, model-family, or human generalization.

Verify every raw answer against its action-indexed tape, forced actions, count
totals, exact-check schedule, terminal certificates and true terminal item.
Verify R=3 histories are prefixes of R=9 histories. Preserve infrastructure and
mid-run failures; partial failure histories are explicitly labeled rather than
certified by a replay receipt. Record a hash manifest of all raw outputs.

Theoretical coefficient comparisons remain separate from these empirical
policies. No empirical oracle is reported without a fair known-type estimator
and stopping rule. In particular, positive-minus-zero partition cost is not a
direct estimator of the unknown-type minus known-type asymptotic premium.
No SOTA, implementation-level asymptotic optimality, or natural Web-user claim
will be inferred from this bounded mechanism experiment.

## Engineering checks before freezing

Twelve four-cell/three-arm paths at 24 replies completed without failures.
A separate genuine6/split prefix of 160 replies per arm completed without
failures. Both stages use engineering-only seeds and may share their own prefix;
they are excluded from main statistics. The 160-reply CPU totals were KL1.596 s,
IG0.243 s, RR0.104 s. Linear full-cap extrapolation is about 24 CPU-minutes,
or 12 wall-minutes on two cores; this is a feasibility estimate, not a deadline.
No policy, seed or scientific parameter was selected from smoke performance.
