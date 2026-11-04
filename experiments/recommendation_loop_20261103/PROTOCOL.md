# Recommendation method loop: bounded development

Date: 2026-11-03. Parent commit `7207c63`. User authorized beginning the method
loop after the general-catalogue theory. This stage implements and tests that
loop in the controlled iid channel; no Qwen/API calls, training, human study,
large-scale search, confirmation evaluation or remote publication.

## Question and observable contract

Can a policy use only public catalogue/group definitions and observed replies
to estimate preferences/types/rates, choose questions aimed at the best item,
and stop only with a numerical likelihood certificate?

Public input has exactly `d,groups,eta,catalogue`; catalogue has offsets/slopes.
True signs, types, rates, seed, winner and correctness never enter a policy or
gate. An action is integer `2*j+format`; raw answer 1 means positive preference.
Mask bit j=1 represents a negative preference. All task actions cost one.
There are no type-report actions or labelled references in this first loop.

The joint estimator maximizes the continuous likelihood over signs/types and
`1/2<=q<=p<=1-eta` (closure). It is joint MLE, not a posterior. The information
gain baseline uses a separately labelled quadrature approximation to the
continuous joint posterior. Its posterior is not used for certified stopping.

## Predeclared arms and fairness

All arms receive identical public information, paired per-action iid response
streams, the same action set and costs, and **the same stopping procedure after
every answer**. Float likelihood screening requests an exact gate when the gap
is within one nat below its threshold; exact checks also occur every 50 answers
and at the cap, irrespective of screening. Only the exact interval gate can
stop. This can delay an otherwise valid certificate; it is not claimed to stop
at the earliest exact-GLR crossing. The screening/checkpoint rule is identical
for every arm and is frozen before any outcomes.

1. Round-Robin over all coordinate-format streams.
2. Joint-MLE D-RRC adaptation: equal coordinate mass on each estimated better
   format, with continuing forced exploration. This adapts the historical
   baseline's allocation rule; its all-data estimator is new and must not be
   called the untouched historical forced-only implementation.
3. Greedy information gain about the winning item, with full joint sign/type/
   rate quadrature and the same continuing forced exploration.
4. Full-profile KL allocation ablation, with the same joint MLE and tracking as
   arm 5 but singleton wrong-profile alternatives. It still uses the SAME
   recommendation stopping gate. This isolates allocation-goal alignment.
5. Decision KL allocation, using all minimal wrong-item flips at the estimated
   preference state, all group type reversals and the continuous rate fit.

For target-based arms 2,4,5, when fitted `p-q<=1e-8`, use a uniform two-format
target and log the reason; do not fabricate a reliability gap. Initial targets
are uniform. Forced blocks and update cadence are in config.json. Tracking
uses cumulative target deficits. Other than this explicit unidentified-state
fallback, failed or nonconvergent planning terminates and records that arm;
there are no retries or hidden fallback winners. All failures remain denominators.

The planner is a float diagnostic solver at fixed logged tolerance. All-data
joint MLE, finite quadrature and fixed optimization errors do not inherit the
old forced-only estimator's expected-time/asymptotic-optimality theorem.

## Certified decision gate

At every exact check, enumerate all bounded sign/type states and fit the
continuous rates exactly with Fraction arithmetic. Maximize likelihood WITHIN each item
class, then compare the best class to every different-item class. Outward
Decimal intervals must strictly separate the gap from

`R + sum_action log(N_action+1)`.

Use exact integer `R=3`, so the model risk bound is `exp(-3)`, approximately
0.049787, not exactly 0.05. This is the same saturated Beta-mixture bound as
the theory. The old d<=4 validated stopping function is not invoked outside
scope: the d<=6 extension has its own state construction and tests, reusing
only rational/interval primitives. Constant-public decisions may certify at
zero queries. Undetermined arithmetic never certifies. No terminal MAP/MLE
guess is promoted to a certificate.

The common screening rule was added before smoke or pilot outcomes after
deterministic runtime fixtures measured about 16--53 ms per six-dimensional
exact gate. Delaying certification preserves the mixture error guarantee on
the selected stopping subsequence, but does not certify numerical screening
accuracy or the earliest possible stopping time.

## Development worlds and budgets

Two fixed catalogues (unequal-weight two-item and genuine asymmetric three-item),
two profiles each (all-positive theory anchor plus one independently seeded
profile), and two partitions (all shared and split): eight paired worlds.
The four profile clusters are reused across partitions; these are not eight
independent users. All five arms: 40 trajectories, cap 2,000 each, at most
80,000 cheap Bernoulli observations. At most two CPU workers, one BLAS thread
each. No model-serving traffic or GPU allocation.

Seeded profiles/types are generated deterministically from the config seed
and stable hashed labels before any arm outcomes. Store them in a private-side
world record; policies receive only a freshly constructed public dictionary.
Responses use an action-indexed sequence of independent uniforms shared across
arms, so revisiting an action gives a fresh observation and paired policies use
the same nth observation of that action. This is a controlled Bernoulli model,
not empirical user simulation or a new natural benchmark.

Before the batch: deterministic unit/integration checks and a tiny smoke run;
then hash-freeze code/config/input worlds. Do not choose seeds, catalogues,
quadrature order, stopping thresholds or caps from observed winners. Preserve
initial smoke evidence and any implementation failure/correction separately.

## Reporting and stopping

For every trajectory retain raw actions/replies, forced status, all planner
updates, full final counts, certificate or abstention, wall/CPU cost, and any
failure. Report all 40 attempted trajectories, certified/capped/failed counts,
wrong certified outputs, and paired outcomes by world/cell. A cap contributes
`min(tau,2000)` to restricted cost, not a completed stopping time; incomplete
certification must be reported beside every cost comparison. No effectiveness
claim follows merely from a correct guess at the cap.

These are small, anchor-containing development samples. No significance claim,
universal superiority, empirical risk certification or real-user validity.
Success of this stage means the observable loop works with meaningful checks;
it does not require our allocator to beat every baseline. Stop after this
bounded stage, preserving negative findings and the frozen parent artifacts.
