# T2 v02 subsequent-stage public evidence review

Date: 2026-10-31. Bounded native same-family source/evidence/arithmetic audit within the shared session; not manuscript peer review, cross-family review, formal verification, or independent scientific confirmation. The parent supplied a preliminary offline summary before this arithmetic reconciliation, so this review is **not blinded**. "Independently reconciled" refers to separately reading and recalculating public records, not to an independent model family or confirmatory experiment. The generation design review remains frozen. This report reads public source and generated artifacts only, without private seed/truth contents, project-module execution, scientific worlds/replays, fitting, model inference or test execution.

**Final audit status: PASS for bounded source/provenance, coverage, public-arithmetic reconciliation and final interpretation consistency. Scientific recommendation: REVISE for the structured-neural T2 development claim, consistent with FINAL_DECISION.md; the declared GO target is not met.** Preparation, three fixed fits, offline/closed-loop evaluation and frozen analysis are complete. The pre-fit inspection preceded training, and the source-only analysis inspection preceded held-out predictions. DeepSets yields substantial measured computation savings, but its query-cost descriptive bounds exceed the frozen 5% tolerance and its certification yield is below the matched teacher. This audit neither authorizes additional experiments nor promotes historical conclusions.

## Completed public-data inspection

The reviewer independently parsed all 2,112 persisted rows across the 352 teacher-data worlds. Every actual world ID matches its planned split, and the six splits are disjoint. Each world has exactly the six planned positions at 2d,16,32,64,256,1024. Row dimensions, partitions, risk, behavior and calibration ratio match the public plan. Nested observable fields match the whitelist; count arrays are integer/nonnegative, forced counts are bounded by actual counts, counts increase across snapshots, calibration is constant within a world, and the online count and remaining 6144-cap budget reconcile. All teacher weights have the correct action dimension, are finite/nonnegative and sum to one; teacher K is finite and positive, and saved marginals are finite and within [0,1]. No discrepancy was found.

| Split | Complete worlds | Rows |
|---|---:|---:|
| Train | 256 | 1,536 |
| Validation | 32 | 192 |
| ID test | 16 | 96 |
| Parameter holdout | 16 | 96 |
| Partition holdout | 16 | 96 |
| Calibration holdout | 16 | 96 |
| Total | 352 | 2,112 |

The reviewer loaded all 3,072 public NPZ arrays with pickle disabled, without importing project modules. Each of 1,536 training rows has one coefficient matrix and one one-dimensional offset vector, with matching nonzero cut count and action width; all values are finite and nonnegative. There are 24–360 cuts per row. This verifies saved-array consistency, not exact regret or completeness of the continuous alternative set. The source still constructs the declared finite relaxation from observable estimates only.

The public row metadata include world/split/behavior/position, teacher labels, numerical solver diagnostics, label timing and the probability-adapter summary. Source inspection confirms that the feature encoder receives row['state'] through the strict whitelist, while the supervised targets and finite cuts enter the declared loss separately. The fitting caller loads only the train split; fresh-MLP normalization is fitted only on those training features. No validation checkpoint selection is present.

In the complete dataset, 247 label snapshots record adjustment of 485 marginals in total; the largest saved adjustment is 1.1191048088221578e-13, below the frozen 1e-12 tolerance. These counts concern saved label snapshots only, not every online posterior computation. They do not certify exact posterior arithmetic. The adapter metadata are outside the student state.

The regenerated public plan is independently compared with the initial failed attempt's public plan and is exactly equal. The fixed world identities and conditions have not been replaced in this continuation. Initial failure, one engineering restart, known prior smoke/replay acquisition and the unknown original interrupted-world cost retain the generation review's disclosure requirements.

## Budget selection independently reconciled

All 18 planned budget-development worlds have completed public Fused-Original records. Recomputing their saved exact-recovery readouts gives:

| Budget | Correct / 18 | Accuracy |
|---|---:|---:|
| 16 | 4 | 0.222222 |
| 32 | 11 | 0.611111 |
| 48 | 12 | 0.666667 |
| 64 | 15 | 0.833333 |
| 96 | 17 | 0.944444 |
| 128 | 17 | 0.944444 |

The frozen nearest-to-0.5 then nearest-to-0.8 distinct-budget rule independently yields **32 and 64**, matching BUDGET_FREEZE. The caller uses only these separate teacher paths; the receipt records zero student predictions and zero test results used. No fitted student exists at this inspection. Final held-out ceiling effects, if any, must be retained without another budget search. These readouts remain intermediate guesses from a strict trajectory, not policies optimized for a known early deadline.

## Preparation accounting and frozen integrity

Independently summing one calibration record per teacher-data world gives 100,976 unique offline observations; 352 complete 1,024-action histories give 360,448 online actions. Both match the completed data manifest. The two repeated smoke worlds again use 128 online actions and zero offline observations, with zero optimizer updates; their uncertified endpoints are interface checks, not trained-policy outcomes. Budget-development acquisition and its path timing are separately retained in its 18 public records.

The complete preparation wrapper reports 472.6868027 seconds wall time and 472.6321480 seconds CPU. DATA_LEAKAGE_AUDIT reports PASS for all 2,112 rows and 1,536 cut rows. The reviewer independently rehashed all 22 generation-bound local files and 60 read-only dependencies; every hash matches, and none required opening a private path. These checks do not replace final total-cost reconciliation or recover the initial attempt's unknown interrupted-world cost.

The public offline evaluation manifest correctly plans 384 rows for each new model. Frozen T1 MLP supports only 186 of its 384 planned states; the remaining 198 d=2/3 states are explicitly not applicable. Later comparisons must retain this differing support rather than substitute zero scores or call those rows failed inference. The main/extra closed-loop manifest retains its previously declared 852 applicable paths and six T1 not-applicable records.

## Pre-evaluation analysis-source review

The reviewer inspected t2/analyze.py, its synthetic test source and the author-produced log recording 12 tests PASS in 1.892 seconds. No analysis, test, model or scientific evaluation was executed by the reviewer. At this source inspection, artifacts/evaluation and artifacts/analysis were absent. The parent's three-fit completion report is not used here as evidence of held-out quality.

Coverage validation checks the public expected-key manifest against the frozen configuration before indexing outcomes. Missing, duplicate or unexpected keys fail closed. The resulting expected denominators are 858 path records, including six T1 not-applicable records, and 1,536 offline records, including 198 T1 not-applicable records. Completed paths require both frozen readouts; incomplete failed paths retain their missing readout counts. A failed candidate or matched-teacher path makes its affected paired summary unavailable, rather than producing a completed-pairs-only estimate. Unsupported T1 states do not become zero scores.

Ratios are ratios of sums. Before each of 4,000 bootstrap draws, all repeated R values are summed inside their original world; resampling therefore has 24 main world clusters or six per stratum, not 72 independent main worlds. Variable-d worlds remain separate. Offline metrics first average all six snapshots within each eligible world, then average across worlds. Infinite radial values remain infinite in the world means and bootstrap draws; the inverted-CDF quantile preserves infinite limits without filtering them out. The common d=4 offline table permits the frozen T1 comparator to be read on the same state support as the new models.

Completed uncertified paths retain their actual cap acquisition in restricted cost summaries. Costs are not reinterpreted as uncensored mean stopping times or successful-stop-only costs. Paired computation speedup is matched Fused-Original time divided by candidate time, using estimation + planning + inference on both sides. Source inspection of evaluator instrumentation confirms that the teacher's posterior-estimation time is counted and subtracted from its enclosing planner timer to avoid double charging, while each new student's posterior computation and feature/inference work are charged. GLR, certification, environment and whole-path wall/CPU remain separate quantities. Parent-pool CPU is labeled as excluding workers, and nested training/preparation subtotals are not added again to outer totals.

Engineering flags use the descriptive query-ratio range's upper limit <=1.05 and inclusive speedup range's lower limit >=2. They additionally require every compared candidate and matched-teacher path to certify correctly without abstention. The flags do not automatically produce GO. The source retains per-stratum/per-risk summaries, and final manual judgment must inspect those results and the declared small-world limitations, not only a pooled point estimate.

One reporting qualification was sent before outcomes: the current table/figure wording "Exact relative radial regret" denotes a full-alternative **numerical plug-in radial cost ratio relative to numerical teacher K**. It is not oracle regret, true-parameter information, an interval certificate or stopping-time regret; negative relative values are permitted. Final reporting must keep that distinction from the optimistic finite-cut training surrogate. No execution/statistical blocker was identified. Evaluation may proceed once the parent freezes the analysis source/tests, committed inputs and fitted model artifacts.

| Source evidence inspected before outcomes | SHA-256 |
|---|---|
| t2/analyze.py | e098f4f9c2a7f76704180617fd66c01f8216983d32b858eec5a146ee9c070335 |
| tests/test_analysis.py | cc97f589fe9bca81cb893a85e54d23f49e403bb21b13bcb80b87c5fc0ec6a573 |
| logs/analysis_tests.log | 9be76d4b6af8f23caa258a70b64c5a8cfb5a6ed11c22b8269c41f0e08ba75a8a |

## Fitting receipts and pre-outcome freeze reconciled

The public execution receipt records three CPU fits, each attempt 1, with 1,536 training rows, 400 updates, batch size 64, learning rate 0.001 and fixed seed 731101. Each retains one final checkpoint without validation selection. Each progress log contains 17 strictly ordered records from update 1 through 400. Both DeepSets fits have the same initial-state hash; MLP and DeepSets-KL share the same state/teacher-label payload hash, while DeepSets-Info additionally binds the finite cuts. The reviewer inspected receipts, progress and hashes without loading models or running inference.

| Model | Parameters | Whole-fit wall seconds | Whole-fit CPU seconds |
|---|---:|---:|---:|
| T2 MLP | 4,778 | 4.511220 | 4.508064 |
| DeepSets-KL | 12,899 | 4.783744 | 4.783507 |
| DeepSets-Info | 12,899 | 11.060162 | 11.059858 |

The enclosing three-fit stage reports 21.086405 seconds wall and 21.082695 seconds CPU, including 0.728071 seconds data loading. These outer totals include the model subtotals and must not be added to them again. Receipts record zero scientific retries, Qwen calls and GPU jobs.

All 20 analysis-frozen files and 60 read-only dependencies independently match their hashes, including the final model files, budget, public plan, training receipt, analysis source/tests and ANALYSIS_SCOPE.md. That pre-outcome scope document explicitly qualifies the legacy "Exact relative radial regret" label as a numerical observable plug-in ratio relative to numerical teacher K, preserves negative residuals/infinity/censoring, and rejects oracle/stopping-time interpretations. It also requires retaining stratum, variable-d and Warm-KL results. No private file was opened for this integrity check.

## Completed offline records independently reconciled

The public offline file has all 1,536 expected keys, with 1,338 completed records and 198 planned T1 not-applicable records. Every model's eligible world contains all six snapshots. Saved allocations are finite, nonnegative, correctly dimensioned and normalized. Recomputing every recorded L1, the declared 1e-8-smoothed forward KL, teacher-K identity and finite radial/teacher-K-minus-one arithmetic from the saved public weights/labels gives maximum discrepancy zero. The reviewer did not rerun a network or the continuous radial minimizer. No infinite radial state is recorded in this completed offline file.

The following means average six states inside each world and then average eligible worlds. "Radial excess" means K(student)/K(teacher)-1 in the frozen numerical plug-in diagnostic; these are point summaries, not confidence statements.

| Support | Model | Worlds / states | Mean L1 | Mean forward KL | Mean radial excess |
|---|---|---:|---:|---:|---:|
| All applicable | T2 MLP | 64 / 384 | 0.152600 | 0.119583 | 2.275148 |
| All applicable | DeepSets-KL | 64 / 384 | 0.110444 | 0.040093 | 0.101611 |
| All applicable | DeepSets-Info | 64 / 384 | 0.115122 | 0.045734 | 0.075647 |
| Matched d=4 | Frozen T1 MLP | 31 / 186 | 0.731810 | 0.814755 | 2.953732 |
| Matched d=4 | T2 MLP | 31 / 186 | 0.182740 | 0.210638 | 4.588801 |
| Matched d=4 | DeepSets-KL | 31 / 186 | 0.094207 | 0.024287 | 0.105425 |
| Matched d=4 | DeepSets-Info | 31 / 186 | 0.102636 | 0.028428 | 0.071935 |

T2 MLP's all-applicable radial means are 0.109215 on ID, 0.106804 on parameter holdout, 8.793615 on partition holdout and 0.090956 on calibration holdout. Its lower matched-d4 imitation error than frozen T1 does not imply lower radial cost: the matched radial mean is worse, with the partition holdout dominating its aggregate. This is a retained failure pattern, not evidence isolating one causal defect.

DeepSets-Info's radial mean is lower than DeepSets-KL in each of the four saved strata: 0.082096 versus 0.096137 on ID, 0.054477 versus 0.099262 on parameter holdout, 0.092860 versus 0.115579 on partition holdout, and 0.073155 versus 0.095465 on calibration holdout. Its L1/KL imitation means are higher. This supports a descriptive tradeoff between the two objectives on these states; it does not establish a closed-loop benefit, optimality or a population guarantee. The MLP/DeepSets comparison also changes parameter count, so the observed difference does not isolate structural equivariance as its sole cause.

Offline inference timing starts from saved observable states, including already computed posterior features. It is not the inclusive online estimation/planning/inference speedup used by the engineering target. Full closed-loop costs and uncertainty remain to be reviewed.

| Completed-stage artifact | SHA-256 |
|---|---|
| artifacts/training/execution.json | 54a26d82cc25a63f5e2cd17b59d40d79d0adbdabd0c6ffb197b7c8c8af369d8e |
| artifacts/evaluation/offline.jsonl | 84b5b63a3c2f46500f1a1116095d586e500b630e901d3f18bdfbd93a8a34eb73 |

## Final closed-loop coverage and arithmetic reconciliation

The reviewer made one bounded pass through public paths, checked the execution/analysis receipts and reports, and reconciled aggregate point estimates from saved scalar outcomes. No network, simulator, certification gate, continuous radial solver, test or bootstrap was rerun. All eight aggregate input-provenance hashes match their current public files.

There are exactly 858 planned path records: 792 main paths and 60 applicable variable-d paths completed, plus six planned T1 not-applicable records. There are zero execution failures and all 1,704 frozen readouts are present. The already reconciled offline denominator remains 1,536 records, with 1,338 applicable and 198 T1 not applicable. All 78 planned world-risk jobs completed.

All 852 applicable paths reconcile task/type counts with online cost and total acquisition. There are **779 certified correct paths, 73 cap abstentions and zero wrong certificates**. Every certified path has a positive recorded gate decision at its final online count. Every abstention occurs at 6,144 queries and has a null strict output and null certified-correctness field. Every readout has the correct min(T,B) acquisition and repeated calibration charge. No path certified before these readout budgets, so zero readouts were absorbed in this run. Raw records report no external/provider model calls, GPU calls or automatic retry.

For every paired summary scope, independently recomputed online-cost, total-acquisition, inclusive-compute and wall-time ratios of sums match the aggregate point values exactly. Pair counts and unique-world counts also match. The frozen bootstrap ranges were reviewed as published outputs of the previously inspected code; this audit does not call them independently recalibrated population confidence intervals.

## Final scientific interpretation

The main comparison contains 72 repeated-risk paths per method in 24 world clusters. Brackets below are the frozen descriptive whole-world resampling ranges. Certified counts use the full 72-path denominator; every remaining path is a cap abstention.

| Method | Online restricted cost / matched teacher | Inclusive computation speedup | Certified / 72 |
|---|---|---|---:|
| Fused-Original matched teacher | 1.000000 | 1.000000 | 69 |
| DeepSets-KL | 1.036738 [1.010977, 1.073270] | 20.279 [16.870, 22.838] | 68 |
| DeepSets-Info | 1.040621 [1.017640, 1.061307] | 20.218 [16.994, 22.786] | 68 |
| T2 MLP | 1.602748 [1.212866, 2.082833] | 13.256 [9.625, 17.731] | 57 |
| Frozen T1 MLP | 2.027479 [1.685498, 2.465009] | 70.031 [55.090, 83.534] | 46 |
| Fused-Info matched | 0.961171 [0.950050, 0.972981] | 3.596 [3.068, 3.990] | 71 |
| Warm-KL | 1.000000 [1.000000, 1.000000] | 0.678 [0.653, 0.709] | 69 |

Both DeepSets point query ratios are below 1.05, but both upper descriptive limits exceed 1.05. They have four caps each versus the teacher's three. The additional cap is in calibration holdout: 17/18 certify for each DeepSets model versus 18/18 for the matched teacher. ID certification is 17/18 for all three, parameter holdout 18/18 for all three, and partition holdout 16/18 for all three. This fails the declared query/yield conditions despite approximately 20-fold inclusive computation and 11.9-fold whole-path wall speedups. It supports REVISE, not a noninferiority or GO claim.

DeepSets-Info's lower offline radial mean does not establish a closed-loop improvement over DeepSets-KL. Main total online queries are 111,488 for Info and 111,072 for KL, with identical 68/72 certification. At budgets 32/64, Info recovers 41/72 and 62/72, KL 44/72 and 62/72, and the matched teacher 43/72 and 62/72. These are correlated intermediate-guess readouts, not independent confirmations or deadline-optimized policies. On partition holdout, KL's query ratio is 1.001942 while Info's is 1.038835; on parameter holdout, Info is lower (1.031128 versus 1.068093). The objective comparison therefore has an offline/closed-loop and stratum-dependent tradeoff.

The new MLP retains a material partition failure: its partition query ratio is 2.770874 [2.021053, 4.514803], and it certifies only 5/18 partition paths versus the teacher's 16/18. This is a configuration-specific NO-GO for promoting the new MLP as an effective substitute, not a diagnosis of one isolated mechanism. Neither its better imitation error than T1 nor its fast forward pass removes the failure.

All 60 applicable variable-d paths certify correctly. The six-world DeepSets query ratios are 1.048951 [0.968421, 1.120301] for KL and 1.055944 [0.989796, 1.105590] for Info, with inclusive speedups about 28.7 and 28.6. The checks establish execution on d=2/3 within the declared scope; they do not pass the query tolerance or justify broad dimension generalization. Frozen T1 remains not applicable.

The implemented Warm-KL does not explain away the neural timing gain: its main aggregate query ratio is exactly 1, but its inclusive speedup is 0.678, meaning it is slower than the matched teacher. Variable-d query ratio is 0.993007 and speedup 0.773644. This is a negative result for this particular warm-start implementation, not a claim that all exact-solver optimizations are ineffective.

Fused-Info is a strong competing baseline on these main worlds: lower restricted query cost, approximately 3.6-fold inclusive speedup, and one cap versus the teacher's three. It still has a cap, variable-d query uncertainty and per-stratum compute ranges that do not uniformly clear the targets. Its result limits the claim that neural allocation uniquely provides a useful cost tradeoff. It does not promote Phase2e from REVISE or establish optimality. D-RRC's larger computation speedups accompany substantially worse query ratios, and native Fused-Original remains separately identifiable from the matched teacher.

## Final runtime and acquisition accounting

| v02 stage | Charged online actions | Charged offline observations |
|---|---:|---:|
| Repeated technical smoke | 128 | 0 |
| Teacher-data generation | 360,448 | 100,976 |
| Budget development | 2,304 | 3,072 |
| Applicable closed-loop paths | 1,504,320 | 209,824 |
| Total | 1,867,200 | 313,872 |

These are stage/path acquisition charges, not a count of globally unique response values: common reference streams are charged again for each arm as declared. Offline student prediction reuses the saved teacher-data states and adds computation, not new acquisition. The prior failed attempt's 128 smoke actions and the 516-action diagnostic replay add 644 known actions separately; the initial failed world's unpersisted original acquisition remains unknown. Thus 2,181,716 is a known charged-action subtotal across the continuation and those prior known actions, **not a complete known total** for all engineering attempts.

The v02 evaluation wrapper reports 1,007.373356 seconds wall time and 14.064821 seconds parent CPU; the latter explicitly excludes worker CPU. The 852 recorded paths sum to 1,976.076936 seconds wall and 1,975.869060 seconds CPU, which cannot be read as elapsed batch time because two workers ran concurrently. Two separate worker-loading receipts total 2.792410 seconds wall and 2.776936 seconds CPU; parent model loading is 1.377622 seconds wall inside the evaluation wrapper. These component measures do not establish an exact partition of all process-startup/transport overhead.

Frozen analysis reports 7.105815 seconds wall and 7.105040 seconds CPU, zero model calls and zero simulated worlds. Preparation and training outer totals remain 472.686803 and 21.086405 seconds wall. Network-forward or inclusive allocation speedups do not include offline fitting as free work; whole-stage costs remain separate, and no amortized break-even claim is justified without a deployment count. The original unknown failed-world cost is not repaired by these complete v02 receipts.

| Final evidence artifact | SHA-256 |
|---|---|
| artifacts/evaluation/paths.jsonl | d8a3627c04a1ebc0513a2551b1629dda17d4c63dccf55571eed7fb18477245c2 |
| artifacts/evaluation/execution.json | 237513d31608c7efabf09b7c636f2bb44e1f380e59d66cb253a7e3caaa1e8061 |
| artifacts/analysis/aggregate.json | a0ad57312e88b8534685231e79c4ae35c12a37553589bc33df32d190208dd85c |
| artifacts/analysis/execution.json | 221c00b13bf3ee7346856b9f70ba12e574c23fbcfa991f51d8a94b30e3531152 |

## Final limits

The bounded execution and requested evidence review are complete. The pre-fit and pre-evaluation verdicts remain preserved in separate immutable receipts/freezes. T1 NO-GO, Phase2e REVISE, the finite-cut approximation, the limited d/G domain, the shared-context non-blinded audit scope and the small-world descriptive claim boundaries remain unchanged. Zero wrong certificates in this run is not a new family-wide risk theorem. Retained cap costs are restricted costs, not uncensored stopping-time means. No further fitting, budget selection, fresh worlds or independent confirmation is implied by the REVISE recommendation.

The reviewer subsequently read FINAL_DECISION.md, the final accounting addendum in COMPUTATIONAL_COST.md and the interpretation note in T2_EVALUATION.md. Their REVISE decision, stop boundary, full denominators, certification/cap distinction, Info-versus-KL limitations, separate T1 support, strong-baseline caveats, numerical radial qualification and earlier-retry/unknown-cost disclosures are consistent with this evidence review. The final decision appropriately permits bounded computational-tradeoff and negative-ablation evidence while rejecting proven query noninferiority, complete certification, optimality or confirmed main-method superiority. The cost addendum further clarifies that outer timers exclude imports/initial verification and that the host timings are not a randomized hardware benchmark.

No remaining material source, denominator, arithmetic or interpretation discrepancy was identified in this bounded review. Final historical-integrity verification and the all-output FINAL_RECEIPT are the parent's subsequent sealing step, not evidence already certified by this report. This audit is finalized; no further recalculation, experiments or edits are requested.

| Reviewed artifact | SHA-256 |
|---|---|
| artifacts/data/manifest.json | 820f24db08c1cccbdb24c9974104e77c84e653a98f46514bad0192270955d9f9 |
| artifacts/data/train_cuts.npz | 88bc1c9d6a14b8ef980f81c47e95e60fa958de052b8dccb941c3e311c706b9f7 |
| artifacts/plan_public.json | 9c4e7240fe04dab63830796fd00c5b9ae950800d0faa3be8ee26a15dc46db7e8 |
| artifacts/prepare_execution.json | 28f0d6978a0d045394391927bd2e399684712fd4eacbc5a260b6c3648c002b15 |
| artifacts/BUDGET_FREEZE.json | 5372e3ad191c21160e4c7a11b0e41a18bbd29dad68160bcae917ebfa2d62cee0 |
| audit/DATA_LEAKAGE_AUDIT.json | 4c7299743a1a5211a0dcc5919a4e8f78cc20c76bd171054ff39b39ad1d0bb580 |
