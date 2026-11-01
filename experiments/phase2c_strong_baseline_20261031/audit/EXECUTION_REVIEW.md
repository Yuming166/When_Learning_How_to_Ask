# Phase 2c execution review

Read-only pre-execution review, 2026-10-31. The reviewer implemented the D-RRC subclass but separately inspected the root runner, policy integration, configuration, protocol, inherited GLR, potential-response streams and observer boundary. This is a same-family implementation review, not independent external certification. No main/private seed was opened, generated or consumed, and no statistical episodes were run by this review.

**Runner source verdict: PASS WITH EXECUTION CONDITIONS. Analysis verdict: PASS (completed below).** One bounded development batch is supported under the conditions below; this is not permission for confirmation, retries, cap extension, or further data-dependent tuning.

## Reviewed correspondence

| Item | Finding | Verdict |
|---|---|---|
| D-RRC integration | Dispatch uses `DecayingRepeatAndCompare(public,cal,R)`; the subclass overrides only the target update and contains no KL solve | PASS |
| Shared estimator/schedule | Frozen forced-only estimator, grid, square-block forcing, cumulative tracking, observation methods and integer sqrt cadence remain inherited | PASS |
| Available information/actions | Same reset/calibration/known type accuracy and permitted task/type actions; D-RRC's own rule chooses zero type target mass | PASS, with action-rule scope retained |
| Shared terminal likelihood | Every policy uses the frozen continuous-profile `log_glr`, same reference observations, original streamwise beta and same numeric margin/check schedule | PASS as float64 computation, not interval certification |
| Oracle boundary | Only `Oracle Format` receives current true formats; p/q/theta remain unknown and profiled | PASS |
| Learner public job | Only R, online cap, check interval and milestones are serialized; true p/q, indices and private generation state remain evaluator-side | PASS |
| RPC observation audit | Evaluator independently counts task/type observations and costs; snapshots and final rows are compared against those counts | PASS |
| Feedback boundary | Truth-based estimate errors and exactness are added to evaluator logs; snapshot replies contain only `recorded=True`, submission only acknowledgement | PASS |
| PRF pairing | Same world key, per-(target,format,repetition) task stream, per-(group,repetition) type stream, and labelled reference streams are shared across policies | PASS |
| Across-world design | All partition/alpha/R/replicate indices are globally distinct; no pairing across cells is presented as additional independence | PASS for declared PRF world model |
| Caps/retries | Environment enforces each online cap; sum of all planned caps is below allowance; output-directory guard prevents overwrite/automatic rerun | PASS |
| Private worker boundary | Spawned workers, controlled JSON RPC, evaluator non-dumpability, and fail-closed Linux Landlock bootstrap are reused | CONDITIONAL on technical fixture and recorded thread environment |
| Timing | Per-worker trajectory CPU/wall, GLR CPU/wall, target-update CPU/wall, evaluator CPU and global elapsed wall are separate | PASS with interpretation below |
| Statistical analysis | Full paired denominators, restricted-cost estimand, evaluator-only information diagnostics and prespecified confirmation planning reviewed below | PASS for exploratory scope |

The pairing is shared potential responses, not identical realized trajectories or forced estimates. Each policy consumes a stream prefix according to its own adaptive actions. Calibration is identical within a world, and direct-type streams are domain-separated from task/reference streams. Private errors/rates are not returned in RPC replies.

## Static plan receipt

Only `jobs(config)` and public-job projection were evaluated; `make_episode` and the runner's `main` were not invoked.

| Quantity | Verified value |
|---|---:|
| Cells | 16 |
| Worlds per cell | 8 |
| Globally distinct worlds/indices | 128 |
| Policies per world | 5 |
| Planned trajectories | 640 |
| Maximum online actions | 5,570,560 |
| Online allowance | 5,600,000 |
| Unique-world reference observations | 130,560 |
| Per-policy charged reference observations | 652,800 |

All planned caps and milestones align with the common stopping-check schedule. The public job has exactly `R`, `check_every`, `milestones`, and `online_cap`. Indices are unique over the complete plan; each of the 16 cells has exactly eight worlds.

The two offline totals describe different denominators: unique world reference samples are shared across policies, while each compared policy's acquisition cost includes the full 2M resource. Reports should not call the five-times charged total a count of independent reference samples.

## Required conditions before starting the one batch

1. Run real spawned-worker technical fixtures for the new policy dispatch, common likelihood/stopping, acquisition accounting, and actual confinement before generating the main development seed. D-RRC's local real-bootstrap suite has already passed **8/8 in 0.406 seconds**, including a 5,000-step deterministic path with the frozen KL solver patched to raise and never called.
2. Set single-thread backend environment variables **before Python/NumPy import**, for example `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`, and retain the launch command/environment receipt. `limits.blas_threads=1` is declarative in the inspected runner; `confine_worker` checks the actual process thread count and fails closed, but does not itself configure the numerical backend.
3. Complete and review the analysis source before freezing source/config/protocol/audit/dependency hashes and drawing the development seed. Do not change frozen source or analysis after outcomes to rescue a result.
4. Preserve every completed, censored, failed, partially executed, and missing policy/world record. If the global work deadline stops the batch, report the batch incomplete and retain aggregate partial acquisition costs; do not silently analyze only available favorable pairs or automatically retry.
5. The 1800-second limit is an evaluator work deadline checked during RPC service. Worker termination, joining, log flushing, and receipt writing add cleanup overhead. Report actual elapsed time; do not describe the source as enforcing an exact 1800-second total-runtime upper bound.
6. Treat all GLR decisions and solver bounds as floating numerical calculations. Shared stopping code and the heuristic margin do not provide interval-certified executable delta-correctness. The protocol already preserves this limitation and the adversarial arithmetic issue.
7. Retain the scope of the primary contrast: Aligned versus D-RRC changes the entire allocation rule, including buying paid type information. Shared estimator definitions do not make purchased information or realized estimator paths identical.
8. Keep the no-overwrite/no-retry guard and the sealed development split. No confirmation seed, world or model call is authorized by this review.

Per-trajectory worker wall time includes RPC waiting and the evaluator's response service for that trajectory; worker CPU excludes evaluator CPU. Summing policy wall times and adding evaluator CPU is not a total resource measure. Planner counters mean numerical KL planning for Aligned and simple estimator/target updates for D-RRC; the baseline's factual per-update fields are `update_seconds`/`update_cpu_seconds`, with no fabricated K or solver residual.

## Source snapshot reviewed

```text
phase2c/runner.py
ad6754135b0e72292e115f081e566e983395211bdc6b3a6d2a433905793ddaa4
phase2c/policy.py
efb8f27b052779bbf867b920d4910a0e899186263b2e1e6f922dc1dce463e99e
phase2c/bootstrap.py
90c70cf44637c06ba285cf176276c9602a21e769687a8a29e33eb447c1ab1672
phase2c/decaying.py
29049fd2c08c130ee102be66193e0fbe7f52ab03d8a8f571727ae2513c64853a
config.json
dd0d17e939dca6db98e438af868cef39a8a80fb517458ba091482034744be42c
PHASE2C_PROTOCOL.md
6f0f519f974c0c7e200311a74c978c6fd9070e1901c1f915d6150de5a2762850
```

Any subsequent runner/config/protocol changes require a focused review of those changes before freeze. The following analysis review was completed before execution, without a main seed or main episodes.

## Completed pre-seed analysis and integrity review

`analyze.py` computes population information at a normalized target by setting online counts to K*w and the per-reference-stream count to alpha. This is the normalized information program, including nonuniform actual coordinate counts and optional type counts. True current types and generating rates occur only in the offline evaluator. They are not passed back to the learner.

The L1 diagnostic is explicitly distance to **one chosen optimizer**, not distance to the entire potentially nonunique optimal set. The separate population-information deficit at K checks the target's information rather than interpreting a different optimal allocation as inefficient. Estimated/empirical allocation, forced fraction, beta/R, observation/profile fluctuations, and solver residuals remain correlated diagnostics; the report does not add them as causal contributions.

An additional independent deterministic check enumerated all 15 nonempty sign-flip masks and all four type masks for d=4, partition [1,3], fractional task counts `[[1.25,0],[.5,2],[0,1],[3,.25]]`, type counts `[.5,1.25]`, true types `[1,0]`, p=.85, q=.60, M=.75, and known s=.8. Every one of the 60 continuous problems was optimized separately with SciPy SLSQP using directly evaluated Bernoulli KL. The minimum was 0.06536991508161161 versus 0.06536991508161062 from the production one-flip analytic routine: absolute difference **9.85e-16**, maximum feasibility residual **1.10e-14**, and zero non-success optimizer statuses. This is a bounded numerical cross-check, not a proof or a newly generated statistical episode.

The analysis rejects a partial batch or missing/duplicate policy/world identities before presenting a complete comparison. Every censored world contributes its cap to restricted cost, and paired differences use every world in each cell. Bootstrap sampling is over world-level values/differences, not individual answers or policies. All 16 cells remain in the reports; n=8 intervals are exploratory and explicitly unadjusted for multiple efficacy comparisons.

The future confirmation design fixes positive-premium [1,3], zero-premium [4], alpha=0, R=1024, the Aligned-minus-D-RRC restricted-cost difference, meaningful planning effect -0.5, and zero equivalence band +/-0.25 before development outcomes. Sample-size planning inflates development paired SD by 1.5, chooses an integer n in [24,512], and retains an insufficiency result if the heuristic power target is not attained. The t/noncentral-t power calculations are correctly labelled approximate planning models, including the observed-zero-SD case. No finite-sample power or coverage certificate is claimed.

Positive superiority uses a one-sided 97.5% paired t bound (claim alpha=.025). Zero equivalence uses TOST with per-test alpha=.025, equivalently containment of the two-sided 95% paired t interval inside the equivalence band. The two-claim Bonferroni family interpretation is nominal and conditional on the stated interval assumptions. Prespecified censoring, infrastructure failure, wrong-certificate, unfavorable and inconclusive rules remain explicit. No future seed/world is generated by planning, and no confirmation launcher is supplied.

The initially inspected analysis mapped private rows using a flat index, although private records store the index inside `job`. Root corrected that pre-seed static defect to `(r['policy'],r['job']['index'])`; the corrected analysis hash is recorded below. This correction used no experimental outcome.

`integrity.py` independently recomputes every terminal GLR, checks count/cost/stopping/pairing/forced-prefix/tracking contracts and historical hashes, and replays selected **already existing** trajectories. Replays are separate computation/acquisition receipts, not new independent worlds. After review, it also records validation wall/evaluator CPU and existing-replay wall/worker CPU separately from main-run timing.

The first reviewed `freeze.py` drew a seed before computing final source/audit/dependency hashes. Root corrected the order: it now computes those hashes and exclusively persists `artifacts/preseed_source_commitment.json` **before** `secrets.token_hex` or writing a private seed. Only then is the private seed commitment attached. The one-time no-replacement/no-retry guards remain. The reviewer inspected this source order but did not invoke it.

## Satisfied pre-seed receipts and final gate

- `preflight_tests_1.log`: **14/14 pass in 6.559 seconds**, including real spawned/confined workers for five policies and two 64-action technical fixtures each. These are 10 technical trajectories, 640 technical online actions and 30 charged offline observations, with no main scientific seed or main world consumed.
- `preflight_tests_2.log`: targeted analysis **4/4 pass in 0.516 seconds** after the private-index correction. The reviewer independently reran those four deterministic tests, passing in 0.533 seconds.
- `RUNTIME.json`: OpenBLAS, OMP and MKL thread variables are all 1, with the exact pre-import launch environment and work-deadline-plus-cleanup scope recorded.
- `audit/HISTORY_PRESERVATION_BEFORE.json`: **295 historical files verified**, theory hash retained, main seed absent, no confirmation worlds consumed.
- A final read-only check found the reviewed runner/policy/config/protocol hashes unchanged, and found no private main seed file, no main run directory, and no freeze file before this final review.

Additional reviewed source provenance:

```text
phase2c/analyze.py
39a2c64c22618446bb1cf52ad27c633f2a1cb4cd592d994c15908856a06d0882
phase2c/report.py
d2317038693316538e7d9125bbc93ab5cb6122344757f971e13f72a475b617dd
phase2c/integrity.py
11d4c62f32abd6e88ab875e0cc71d48eda5bcafada77fcb09c22ed5bdadbfa08
phase2c/freeze.py
21f31c178e94347ace3b9e50e795007daaa88518629a22cf0d03c503f626239f
tests/test_analysis.py
9b8d99e9da238cf17a7ded7dc2d1843fb1c97a4f16a4a95e5e7f9b701edecc81
RUNTIME.json
09a0e3894ac0f39ac381d051ba1377e3aebc2826475a125961c8ec377129ed9a
```

**FINAL PRE-SEED VERDICT: PASS**

The reviewed implementation, fixed plan, real technical isolation checks, numerical diagnostics, exploratory analysis and confirmation-planning scope support exactly one bounded development batch. The operational conditions above remain binding throughout execution. This verdict does not predict an Aligned advantage, certify floating-point delta-correctness/asymptotic optimality, permit confirmation, or authorize a retry after failure. Source/config/audit changes after this gate require renewed focused review before any seed or execution.
