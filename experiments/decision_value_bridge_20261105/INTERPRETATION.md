# Post-run interpretation and estimand clarification

This note was written after the frozen run. It changes neither the protocol,
implementation nor primary analysis. `posthoc_summary.py` only derives
clarifications from retained results and packages raw synthetic evidence.

## Decision

**NO_GO for a finite-query Decision Value improvement claim on these anchors.**
The correctly instantiated one-step 0–1 decision-value policy has the same
certified query count as round robin on all 66 matched paths. Its complete
(action, answer) trajectory matches round robin on 46/66 paths; the two policies
are not claimed identical. Of 30,936 nonforced DV decisions, 30,864 (99.77%) have
exactly zero one-step value and invoke the prespecified least-count fallback.
The 72 nonzero decisions do not imply a visible certified-cost improvement here.
This is evidence of a myopic plateau on these constructed beliefs, not a
universal theorem that Decision Value equals round robin.

Repaired IG uses fewer queries than DV in all 11 cell/risk means. Pooled IG-minus-DV
contrasts are -238.00 [-278.17,-198.17] at anchor R3; -268.13
[-303.79,-236.29] at anchor R9; and -279.50 [-343.54,-220.79] in the R9 type audit.
Intervals are conditional paired catalogue-seed bootstrap intervals, not user
population intervals or guarantees of superiority beyond the fixed anchors.

## Complete denominator and implementation failures

264 attempted: 257 certified, 0 capped, 7 failed, 0 incorrect certificates.
All seven failures occurred in the inherited Decision-KL allocator with
`ArithmeticError: invalid allocation weights`. Three anchor catalogue-seed-cell
paths failed at both risk settings; one all-B audit path failed at R9. These
are correlated failures and remain in all 264 denominators with cost 2500 each.
No solver repair, retry, replacement or post-failure continuation was performed.
All 66 DV, 66 IG and 66 RR paths certified; KL certified 59/66.

The positive anchor KL-minus-DV mean is not evidence that DV beats a correctly
running KL allocator: these means include the prescribed failure penalty, and
both KL/DV interval comparisons include zero. A successful-only table would
change the estimand and selectively remove observed failures. We do not use it
as primary evidence.

## Accuracy estimands

`fixed_budget_aggregates` gives raw complete-denominator counts: the audit has
12 weighted5 cases and 6 genuine6 cases per arm/risk/budget, so its raw accuracy
weights catalogues 2/3 and 1/3. `fixed_budget_comparisons` gives the prespecified
standardized contrast: weight each catalogue 1/2, then each cell equally within
catalogue. Therefore subtracting two audit raw accuracies need not reproduce
the standardized accuracy contrast. Anchor raw and standardized weights agree.

`results/posthoc_clarification.json` explicitly provides both raw and standardized
accuracy for every arm, risk, track and budget. The standardized values merely
make the frozen comparison estimand readable; they introduce no new run,
selection, hypothesis, resample or interval. Complete-denominator unavailable
failure outcomes count as unsuccessful; their availability remains recorded.

## Numerical and scientific boundary

DV and IG use the identical uniform discrete prior over all theta/type states
and uniform continuous prior over the ordered rate triangle, approximated by
36 Gauss–Legendre nodes (order6 × order6), with log posterior updates. No
posterior-mean rate is inserted into the likelihood. DV's decision target is the
best catalogue item. Its algebraic score is exact for the discretized belief in
real arithmetic; floating calculations and continuous quadrature error are not
certified. Tests of count reconstruction and explicit reply conditioning
validate implementation, not continuous-posterior approximation accuracy.

The inherited outward-bound exact continuous GLR gate supplies the model-based
certificate. It is independent of the approximate posterior, and it does not
prove DV asymptotic optimality, posterior calibration, earliest possible
stopping, or a new general VOI principle. One-step value can be zero when
multiple future replies would still be valuable. No outcome-driven multistep or
entropy hybrid was added.

The type audit removes the exclusive all-A restriction only for three fixed
configurations. Two all-positive preference profiles, known partitions, tiny
catalogues, at most two groups, iid rates, and six seeds per catalogue remain.
The no-oracle experiment does not estimate an unknown-versus-known-type premium.

## Replay and packaging

All 264 retained histories pass full adaptive-policy replay; all terminal
certificates are independently rechecked; 93 nonfailed cross-R pairs pass prefix
checks. Three failed cross-R comparisons are retained as failures and excluded
from prefix-success claims. Every raw reply is checked against its action/pull
uniform tape; counts, forced actions and exact-check schedule are checked.
The main run contains 110,808 actual replies and 311.41 summed CPU seconds.

`FREEZE.json` preserves eight local source hashes, ten dependency hashes, world
hash and the 264-path denominator. `RECEIPT.json` hashes raw main JSON and analysis.
`results/paired_outcomes.csv` preserves all 264 outcome rows including failures.
`results/synthetic_raw_replay.tar.gz` is an optional compressed archive of every
raw engineering/main JSON file; its checksum is in `results/archive_receipt.json`.
Its paths are relative to this experiment directory. To inspect an archive in a
fresh experiment folder, extract there; the original runner intentionally
refuses to overwrite existing stage directories. Full fresh simulation requires
preserving the source hashes and running in a fresh output checkout.
