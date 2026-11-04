# Frozen paired Decision Value bridge, 2026-11-05

This is a bounded instantiation of standard one-step value of information for
0–1 recommendation loss, not an invention of VOI. Main outcomes are not inspected
until source freeze. Engineering-only seed labels are disjoint from main labels.
No model calls, training, empirical oracle, retries, replacement, tuning or
outcome-dependent expansion are permitted.

## Target and implementation

Decision Value is E_y[max_i P(i wins | h,a,y)] - max_i P(i wins | h).
Enumerate exactly the same theta/type states as repaired IG and use exactly the
same order-6 Gauss–Legendre rate quadrature and sequential log posterior update.
This is exact for that discrete quadrature model up to floating arithmetic, not
an exact continuous posterior. Evaluate the equivalent nonnegative expression
sum_y max_i[P(i,y|h,a)-P(i_current,y|h,a)] to avoid subtracting two near-one totals.
Compute each reply joint mass directly, without subtracting a tiny residual.
Use relative 64*epsilon score ties, least observed count, then smallest index.
When no reply can change the MAP item, all gains are exactly zero; the same
least-count fallback applies. This myopic plateau is a substantive method
limitation, not a reason to insert entropy or tune a hybrid after outcomes.

All arms share unchanged forced exploration and exact Fraction/Decimal GLR
stopping. Screen each reply; exact check at gap >= beta-1, each 50th reply, or
cap. Beta = R + sum_action log(N+1). Only strict outward-bound certification
stops. Risk exp(-R) follows the inherited iid channel model; posterior MAP,
floating crossings, caps, and fixed-budget guesses are never certificates.
Neither one-step DV nor this finite-tolerance KL implementation has a new
asymptotic optimality proof. Prior/quadrature scores do not supply the guarantee.

## Design fixed before outcomes

Four unchanged catalogue/partition anchor cells from the 2026-11-04 experiment:
weighted5_zero, weighted5_positive, genuine6_zero, genuine6_positive. All-positive
theta, p=4/5, q=3/5, eta=1/100, M=0. All-A group types. Six fresh response seeds
per catalogue; R=3 and 9; four arms: decision_value, decision_kl, repaired
decision_ig, round_robin. Main anchor denominator: 192 trajectories.

A separate prespecified R=9 type audit has three cells and six seeds/four arms:
weighted5_zero all-B types [1,1]; weighted5_positive mixed [0,1];
genuine6_positive mixed [1,0]. Denominator 72; total 264. This audit checks limited
type reversal/mixing, not arbitrary users or new preference profiles. Premium
labels describe original theory anchors; no new known-type comparison is run.

Every related run shares SHA256-derived action-indexed per-pull uniform tapes
within its catalogue/response-seed cluster, including partition, type, risk and
arm. Thus there are 12 response-tape clusters conditional on two constructed
catalogues, not 264 independent profiles. Seeds and exact groups are config.json.
Cap 2500 per path; maximum total 660000 main replies. No oracle baseline.
Use six CPU workers pinned to separate available CPUs, one BLAS/OpenMP thread
each. Smoke uses 28 paths capped at 24 replies; runtime smoke uses one split
three-item cell/four arms at 160 replies. Smoke is excluded from efficacy.

## Fixed-budget secondary outcomes

Budgets 25,50,100,200 are evaluated along the same stopped paths. If a path has
already certified, carry forward its certified item explicitly. Otherwise
recommend the MAP item from the same Q6 joint posterior for every allocator;
ties use smallest item index. This common readout prevents evaluator choice
from favoring DV/IG over KL/RR. Report correctness, certified coverage, carried
forward counts and unavailable failures separately. Failures before a budget
are unavailable and count as unsuccessful in complete-denominator accuracy.
Uncertified recommendations are guesses and do not inherit exp(-R) guarantees.

## Analysis and verification

Primary cost: certified query count, assigning 2500 to every cap or failure.
Retain all per-seed costs, status, errors, caps, failure/postprocessing records,
runtimes, and selected zero-gain counts. Per-cell and paired baseline-minus-DV
comparisons for each risk, including win/tie/loss. Pool anchor cells with equal
catalogue and partition weight; pool audits with equal catalogue weight and
then equal cells within catalogue (clearly separate from anchor results).
Bootstrap 10000 resamples of six seeds within each catalogue, reusing draws
across all arms, partitions, risks and related type runs. Percentile 95% intervals
are conditional on these fixed anchors and imprecise with six seeds. Fixed-budget
accuracy contrasts use the same cluster bootstrap. No significance-driven
selection and no broad superiority presumption.

Verify raw replies against tapes, forced actions, counts, check schedule, exact
terminal certificates, and cross-R prefix consistency. Replay full adaptive
policies against every retained history. Check DV scores against explicit
posterior-branch enumeration at reachable and arbitrary beliefs; compare the
2500-observation posterior against count-reconstructed log likelihood. Preserve
all raw outputs and a SHA256 manifest. Historical dependencies are imported and
hashed without modification; commands and provenance paths remain repo-relative.

Original constraints remain: two all-positive constructed profiles, small fixed
catalogues, at most two groups, iid constant rates and known sharing partition.
Type audit does not eliminate those limitations. Finite partition contrasts do
not estimate the asymptotic unknown-type minus known-type premium.
