# T2 evaluation

Manual review subsequently concluded **REVISE**; see FINAL_DECISION.md for the decision and condition-specific failures. The automatic analyzer's manual-review status below is preserved. Its legacy "Exact" radial wording means full-alternative numerical evaluation in the observable plug-in model, not exact arithmetic, true-parameter/oracle regret, or stopping-time regret; see ANALYSIS_SCOPE.md.

Final decision: **manual review required**. This report does not automatically declare GO.

Observed 858/858 planned path records; main applicable paths 792; variable-d applicable paths 60. Status counts: {"completed": 852, "not_applicable": 6}. Fixed-budget cells observed 1704/1704 (main 1584, variable-d 120).

Offline records: 1536/1536; statuses {"completed": 1338, "not_applicable": 198}.

The main matched teacher is **Fused-Original**. Native-Fused-Original is a separate native-scheduler reference. Warm-KL is retained as the warm-start optimization baseline. T1-MLP is the frozen original comparator; T2-MLP uses the same legal posterior features as the new structural models.

All cap abstentions are included in online and total-acquisition restricted costs. These costs are not means over successful paths and are not uncensored mean stopping times. Failed pairs make the paired estimate unavailable instead of being silently removed.

Repeated risks and snapshots are clustered by whole world. Main pooled comparisons contain 24 world clusters, not 72 independent worlds; each stratum has six worlds. Offline metrics average the six snapshots within a world before comparing worlds. Every infinity remains in the radial mean and bootstrap distribution. Matched-d4 offline tables keep the T1 comparator on a common state set.

95% percentile world-cluster bootstrap descriptive range; not a calibrated confidence or noninferiority interval. paired world-clustered descriptive sensitivity; fixed heterogeneous condition grid; no calibrated population noninferiority

## Main paired engineering readouts

Each entry is point [descriptive bootstrap lower, upper]. The engineering target is online query ratio at most 1.05 and inclusive estimator/planner/inference speedup at least 2. A point estimate alone is insufficient. Both candidate and matched teacher must certify every applicable path correctly, with zero abstentions, before the strict flags can all pass. Passing flags still requires manual interpretation.

| Method | Pairs / clusters | Online restricted ratio | Total acquisition ratio | Inclusive compute speedup | All strict flags |
| --- | --- | --- | --- | --- | --- |
| Aligned | 72/72 / 24 | 1.21 [1.06, 1.37] | 1.18 [1.05, 1.32] | 0.807 [0.703, 0.937] | False |
| D-RRC-NoType | 72/72 / 24 | 1.45 [1.28, 1.64] | 1.39 [1.24, 1.55] | 487 [402, 559] | False |
| D-RRC-Type | 72/72 / 24 | 1.23 [1.15, 1.31] | 1.2 [1.13, 1.27] | 376 [311, 430] | False |
| DeepSets-Info | 72/72 / 24 | 1.04 [1.02, 1.06] | 1.03 [1.01, 1.05] | 20.2 [17, 22.8] | False |
| DeepSets-KL | 72/72 / 24 | 1.04 [1.01, 1.07] | 1.03 [1.01, 1.06] | 20.3 [16.9, 22.8] | False |
| Fused-Info | 72/72 / 24 | 0.961 [0.95, 0.973] | 0.967 [0.957, 0.978] | 3.6 [3.07, 3.99] | False |
| Native-Fused-Original | 72/72 / 24 | 0.991 [0.986, 0.995] | 0.993 [0.989, 0.996] | 0.751 [0.632, 0.848] | False |
| T1-MLP | 72/72 / 24 | 2.03 [1.69, 2.47] | 1.88 [1.59, 2.23] | 70 [55.1, 83.5] | False |
| T2-MLP | 72/72 / 24 | 1.6 [1.21, 2.08] | 1.52 [1.19, 1.9] | 13.3 [9.62, 17.7] | False |
| Warm-KL | 72/72 / 24 | 1 [1, 1] | 1 [1, 1] | 0.678 [0.653, 0.709] | False |

## Per-stratum and risk path denominators

| Stratum | R | Method | Complete / applicable | N/A | Certified | Wrong cert. | Abstain | Mean online restricted | Mean total acquisition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eval_id | 16 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 944 | 987 |
| eval_id | 16 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1.3e+03 | 1.34e+03 |
| eval_id | 16 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.11e+03 | 1.16e+03 |
| eval_id | 16 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 736 | 779 |
| eval_id | 16 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 699 | 741 |
| eval_id | 16 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 592 | 635 |
| eval_id | 16 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 635 | 677 |
| eval_id | 16 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 629 | 672 |
| eval_id | 16 | T1-MLP | 6/6 | 0 | 5 | 0 | 1 | 1.57e+03 | 1.61e+03 |
| eval_id | 16 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 677 | 720 |
| eval_id | 16 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 635 | 677 |
| eval_id | 64 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 1.45e+03 | 1.62e+03 |
| eval_id | 64 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1.97e+03 | 2.14e+03 |
| eval_id | 64 | D-RRC-Type | 6/6 | 0 | 5 | 0 | 1 | 1.85e+03 | 2.02e+03 |
| eval_id | 64 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 1.3e+03 | 1.47e+03 |
| eval_id | 64 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 1.23e+03 | 1.4e+03 |
| eval_id | 64 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 1.13e+03 | 1.3e+03 |
| eval_id | 64 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.18e+03 | 1.35e+03 |
| eval_id | 64 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.18e+03 | 1.35e+03 |
| eval_id | 64 | T1-MLP | 6/6 | 0 | 5 | 0 | 1 | 2.28e+03 | 2.45e+03 |
| eval_id | 64 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 1.24e+03 | 1.41e+03 |
| eval_id | 64 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 1.18e+03 | 1.35e+03 |
| eval_id | 256 | Aligned | 6/6 | 0 | 5 | 0 | 1 | 3.07e+03 | 3.75e+03 |
| eval_id | 256 | D-RRC-NoType | 6/6 | 0 | 5 | 0 | 1 | 3.86e+03 | 4.54e+03 |
| eval_id | 256 | D-RRC-Type | 6/6 | 0 | 5 | 0 | 1 | 3.3e+03 | 3.98e+03 |
| eval_id | 256 | DeepSets-Info | 6/6 | 0 | 5 | 0 | 1 | 3.04e+03 | 3.72e+03 |
| eval_id | 256 | DeepSets-KL | 6/6 | 0 | 5 | 0 | 1 | 3.14e+03 | 3.82e+03 |
| eval_id | 256 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 2.91e+03 | 3.59e+03 |
| eval_id | 256 | Fused-Original | 6/6 | 0 | 5 | 0 | 1 | 3.02e+03 | 3.7e+03 |
| eval_id | 256 | Native-Fused-Original | 6/6 | 0 | 5 | 0 | 1 | 3.01e+03 | 3.69e+03 |
| eval_id | 256 | T1-MLP | 6/6 | 0 | 3 | 0 | 3 | 3.89e+03 | 4.58e+03 |
| eval_id | 256 | T2-MLP | 6/6 | 0 | 5 | 0 | 1 | 3.11e+03 | 3.8e+03 |
| eval_id | 256 | Warm-KL | 6/6 | 0 | 5 | 0 | 1 | 3.02e+03 | 3.7e+03 |
| eval_ood_calibration | 16 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 1.38e+03 | 1.39e+03 |
| eval_ood_calibration | 16 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1.11e+03 | 1.13e+03 |
| eval_ood_calibration | 16 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 987 | 1e+03 |
| eval_ood_calibration | 16 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 667 | 683 |
| eval_ood_calibration | 16 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 640 | 656 |
| eval_ood_calibration | 16 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 619 | 635 |
| eval_ood_calibration | 16 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 629 | 645 |
| eval_ood_calibration | 16 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 608 | 624 |
| eval_ood_calibration | 16 | T1-MLP | 6/6 | 0 | 5 | 0 | 1 | 1.5e+03 | 1.51e+03 |
| eval_ood_calibration | 16 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 672 | 688 |
| eval_ood_calibration | 16 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 629 | 645 |
| eval_ood_calibration | 64 | Aligned | 6/6 | 0 | 5 | 0 | 1 | 1.85e+03 | 1.91e+03 |
| eval_ood_calibration | 64 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 2.09e+03 | 2.15e+03 |
| eval_ood_calibration | 64 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.42e+03 | 1.49e+03 |
| eval_ood_calibration | 64 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 1.16e+03 | 1.23e+03 |
| eval_ood_calibration | 64 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 1.16e+03 | 1.23e+03 |
| eval_ood_calibration | 64 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 1.1e+03 | 1.17e+03 |
| eval_ood_calibration | 64 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.1e+03 | 1.17e+03 |
| eval_ood_calibration | 64 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.11e+03 | 1.17e+03 |
| eval_ood_calibration | 64 | T1-MLP | 6/6 | 0 | 5 | 0 | 1 | 2.15e+03 | 2.21e+03 |
| eval_ood_calibration | 64 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 1.25e+03 | 1.32e+03 |
| eval_ood_calibration | 64 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 1.1e+03 | 1.17e+03 |
| eval_ood_calibration | 256 | Aligned | 6/6 | 0 | 5 | 0 | 1 | 3.28e+03 | 3.54e+03 |
| eval_ood_calibration | 256 | D-RRC-NoType | 6/6 | 0 | 4 | 0 | 2 | 3.98e+03 | 4.24e+03 |
| eval_ood_calibration | 256 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 3.4e+03 | 3.65e+03 |
| eval_ood_calibration | 256 | DeepSets-Info | 6/6 | 0 | 5 | 0 | 1 | 3.15e+03 | 3.4e+03 |
| eval_ood_calibration | 256 | DeepSets-KL | 6/6 | 0 | 5 | 0 | 1 | 3.22e+03 | 3.47e+03 |
| eval_ood_calibration | 256 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 2.97e+03 | 3.22e+03 |
| eval_ood_calibration | 256 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 3.05e+03 | 3.31e+03 |
| eval_ood_calibration | 256 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 3.04e+03 | 3.3e+03 |
| eval_ood_calibration | 256 | T1-MLP | 6/6 | 0 | 3 | 0 | 3 | 4.36e+03 | 4.61e+03 |
| eval_ood_calibration | 256 | T2-MLP | 6/6 | 0 | 5 | 0 | 1 | 3.35e+03 | 3.61e+03 |
| eval_ood_calibration | 256 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 3.05e+03 | 3.31e+03 |
| eval_ood_parameters | 16 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 368 | 411 |
| eval_ood_parameters | 16 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 469 | 512 |
| eval_ood_parameters | 16 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 443 | 485 |
| eval_ood_parameters | 16 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 384 | 427 |
| eval_ood_parameters | 16 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 363 | 405 |
| eval_ood_parameters | 16 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 357 | 400 |
| eval_ood_parameters | 16 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 363 | 405 |
| eval_ood_parameters | 16 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 336 | 379 |
| eval_ood_parameters | 16 | T1-MLP | 6/6 | 0 | 6 | 0 | 0 | 475 | 517 |
| eval_ood_parameters | 16 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 363 | 405 |
| eval_ood_parameters | 16 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 363 | 405 |
| eval_ood_parameters | 64 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 699 | 869 |
| eval_ood_parameters | 64 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1e+03 | 1.17e+03 |
| eval_ood_parameters | 64 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 715 | 885 |
| eval_ood_parameters | 64 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 699 | 869 |
| eval_ood_parameters | 64 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 672 | 843 |
| eval_ood_parameters | 64 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 645 | 816 |
| eval_ood_parameters | 64 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 683 | 853 |
| eval_ood_parameters | 64 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 667 | 837 |
| eval_ood_parameters | 64 | T1-MLP | 6/6 | 0 | 6 | 0 | 0 | 1.2e+03 | 1.37e+03 |
| eval_ood_parameters | 64 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 725 | 896 |
| eval_ood_parameters | 64 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 683 | 853 |
| eval_ood_parameters | 256 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 1.74e+03 | 2.42e+03 |
| eval_ood_parameters | 256 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 2.86e+03 | 3.54e+03 |
| eval_ood_parameters | 256 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.98e+03 | 2.67e+03 |
| eval_ood_parameters | 256 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 1.74e+03 | 2.43e+03 |
| eval_ood_parameters | 256 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 1.89e+03 | 2.58e+03 |
| eval_ood_parameters | 256 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 1.65e+03 | 2.33e+03 |
| eval_ood_parameters | 256 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.7e+03 | 2.38e+03 |
| eval_ood_parameters | 256 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.69e+03 | 2.37e+03 |
| eval_ood_parameters | 256 | T1-MLP | 6/6 | 0 | 4 | 0 | 2 | 3.24e+03 | 3.93e+03 |
| eval_ood_parameters | 256 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 2e+03 | 2.68e+03 |
| eval_ood_parameters | 256 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 1.7e+03 | 2.38e+03 |
| eval_ood_partition | 16 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 1.41e+03 | 1.46e+03 |
| eval_ood_partition | 16 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1.43e+03 | 1.47e+03 |
| eval_ood_partition | 16 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.45e+03 | 1.49e+03 |
| eval_ood_partition | 16 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 827 | 869 |
| eval_ood_partition | 16 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 773 | 816 |
| eval_ood_partition | 16 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 677 | 720 |
| eval_ood_partition | 16 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 768 | 811 |
| eval_ood_partition | 16 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 752 | 795 |
| eval_ood_partition | 16 | T1-MLP | 6/6 | 0 | 2 | 0 | 4 | 4.33e+03 | 4.37e+03 |
| eval_ood_partition | 16 | T2-MLP | 6/6 | 0 | 2 | 0 | 4 | 4.6e+03 | 4.64e+03 |
| eval_ood_partition | 16 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 768 | 811 |
| eval_ood_partition | 64 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 1.97e+03 | 2.14e+03 |
| eval_ood_partition | 64 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 2.14e+03 | 2.31e+03 |
| eval_ood_partition | 64 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.74e+03 | 1.91e+03 |
| eval_ood_partition | 64 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 1.46e+03 | 1.63e+03 |
| eval_ood_partition | 64 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 1.33e+03 | 1.5e+03 |
| eval_ood_partition | 64 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 1.26e+03 | 1.43e+03 |
| eval_ood_partition | 64 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.34e+03 | 1.51e+03 |
| eval_ood_partition | 64 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 1.31e+03 | 1.48e+03 |
| eval_ood_partition | 64 | T1-MLP | 6/6 | 0 | 2 | 0 | 4 | 5.07e+03 | 5.24e+03 |
| eval_ood_partition | 64 | T2-MLP | 6/6 | 0 | 2 | 0 | 4 | 5.23e+03 | 5.4e+03 |
| eval_ood_partition | 64 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 1.34e+03 | 1.51e+03 |
| eval_ood_partition | 256 | Aligned | 6/6 | 0 | 4 | 0 | 2 | 3.41e+03 | 4.09e+03 |
| eval_ood_partition | 256 | D-RRC-NoType | 6/6 | 0 | 4 | 0 | 2 | 3.74e+03 | 4.43e+03 |
| eval_ood_partition | 256 | D-RRC-Type | 6/6 | 0 | 4 | 0 | 2 | 3.58e+03 | 4.26e+03 |
| eval_ood_partition | 256 | DeepSets-Info | 6/6 | 0 | 4 | 0 | 2 | 3.42e+03 | 4.1e+03 |
| eval_ood_partition | 256 | DeepSets-KL | 6/6 | 0 | 4 | 0 | 2 | 3.4e+03 | 4.08e+03 |
| eval_ood_partition | 256 | Fused-Info | 6/6 | 0 | 5 | 0 | 1 | 3.25e+03 | 3.94e+03 |
| eval_ood_partition | 256 | Fused-Original | 6/6 | 0 | 4 | 0 | 2 | 3.39e+03 | 4.07e+03 |
| eval_ood_partition | 256 | Native-Fused-Original | 6/6 | 0 | 4 | 0 | 2 | 3.38e+03 | 4.06e+03 |
| eval_ood_partition | 256 | T1-MLP | 6/6 | 0 | 0 | 0 | 6 | 6.14e+03 | 6.83e+03 |
| eval_ood_partition | 256 | T2-MLP | 6/6 | 0 | 1 | 0 | 5 | 5.4e+03 | 6.08e+03 |
| eval_ood_partition | 256 | Warm-KL | 6/6 | 0 | 4 | 0 | 2 | 3.39e+03 | 4.07e+03 |
| eval_variable | 64 | Aligned | 6/6 | 0 | 6 | 0 | 0 | 976 | 1.15e+03 |
| eval_variable | 64 | D-RRC-NoType | 6/6 | 0 | 6 | 0 | 0 | 1.29e+03 | 1.46e+03 |
| eval_variable | 64 | D-RRC-Type | 6/6 | 0 | 6 | 0 | 0 | 1.01e+03 | 1.18e+03 |
| eval_variable | 64 | DeepSets-Info | 6/6 | 0 | 6 | 0 | 0 | 805 | 976 |
| eval_variable | 64 | DeepSets-KL | 6/6 | 0 | 6 | 0 | 0 | 800 | 971 |
| eval_variable | 64 | Fused-Info | 6/6 | 0 | 6 | 0 | 0 | 768 | 939 |
| eval_variable | 64 | Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 763 | 933 |
| eval_variable | 64 | Native-Fused-Original | 6/6 | 0 | 6 | 0 | 0 | 757 | 928 |
| eval_variable | 64 | T1-MLP | 0/0 | 6 | 0 | 0 | 0 | unavailable | unavailable |
| eval_variable | 64 | T2-MLP | 6/6 | 0 | 6 | 0 | 0 | 811 | 981 |
| eval_variable | 64 | Warm-KL | 6/6 | 0 | 6 | 0 | 0 | 757 | 928 |

## Fixed-budget exact recovery and ceiling flags

Exact rate uses the full expected applicable denominator only when every planned readout exists. The table retains missing-readout counts; expected-denominator exact yield and observed fractions are separate JSON fields. An early certified path is absorbed with its actual acquisition cost. A ceiling flag means all observed planned readouts in that cell are exact; it is descriptive, not a generalization guarantee.

| Stratum | R | Method | Budget | Exact / expected | Observed | Missing | Exact rate | Absorbed | Ceiling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eval_id | 16 | Aligned | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | Aligned | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_id | 16 | D-RRC-Type | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 16 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | DeepSets-Info | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | DeepSets-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | DeepSets-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | DeepSets-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | Fused-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 16 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | Native-Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | Native-Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | T1-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | T2-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 16 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 16 | Warm-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | Aligned | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | Aligned | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_id | 64 | D-RRC-Type | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 64 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 64 | DeepSets-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | DeepSets-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | DeepSets-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | Fused-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 64 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | Native-Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | Native-Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | T1-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | T2-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 64 | T2-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 64 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 64 | Warm-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | Aligned | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | Aligned | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_id | 256 | D-RRC-Type | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | DeepSets-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | DeepSets-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | DeepSets-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | Fused-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | Native-Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | Native-Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_id | 256 | T1-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | T2-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | T2-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_id | 256 | Warm-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_id | 256 | Warm-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | Aligned | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 16 | D-RRC-NoType | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 16 | D-RRC-Type | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 16 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 16 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | DeepSets-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | DeepSets-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | DeepSets-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | Fused-Info | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 16 | Fused-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | Fused-Original | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_calibration | 16 | Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | Native-Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | Native-Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | T1-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | T1-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 16 | T2-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 16 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 16 | Warm-KL | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_calibration | 16 | Warm-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | Aligned | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 64 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | D-RRC-NoType | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 64 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | D-RRC-Type | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 64 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | DeepSets-Info | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | DeepSets-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | DeepSets-KL | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | DeepSets-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | Fused-Info | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | Fused-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | Fused-Original | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | Native-Fused-Original | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_calibration | 64 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 64 | T1-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | T2-MLP | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 64 | Warm-KL | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 64 | Warm-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | Aligned | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | D-RRC-NoType | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | D-RRC-Type | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 256 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | DeepSets-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | DeepSets-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | DeepSets-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | Fused-Info | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 256 | Fused-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_calibration | 256 | Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | Native-Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_calibration | 256 | T1-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | T2-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_calibration | 256 | Warm-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_calibration | 256 | Warm-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 16 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | D-RRC-NoType | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 16 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | D-RRC-Type | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 16 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | DeepSets-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_parameters | 16 | DeepSets-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | DeepSets-KL | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_parameters | 16 | DeepSets-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Fused-Info | 32 | 1/6 | 6 | 0 | 0.167 | 0 | False |
| eval_ood_parameters | 16 | Fused-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 16 | Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Native-Fused-Original | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 16 | T1-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 16 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 16 | Warm-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 16 | Warm-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 64 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | D-RRC-NoType | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 64 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | D-RRC-Type | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 64 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 64 | DeepSets-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | DeepSets-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 64 | DeepSets-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | Fused-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_parameters | 64 | Fused-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 64 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 64 | Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | Native-Fused-Original | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 64 | T1-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 64 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 64 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 64 | Warm-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 256 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | D-RRC-NoType | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 256 | D-RRC-NoType | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | D-RRC-Type | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_parameters | 256 | D-RRC-Type | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | DeepSets-Info | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 256 | DeepSets-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | DeepSets-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_parameters | 256 | DeepSets-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Fused-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_parameters | 256 | Fused-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 256 | Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Native-Fused-Original | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 256 | T1-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 256 | T2-MLP | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_parameters | 256 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_parameters | 256 | Warm-KL | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_ood_partition | 16 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 16 | Aligned | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | D-RRC-NoType | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | D-RRC-Type | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | D-RRC-Type | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | DeepSets-Info | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | DeepSets-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | DeepSets-KL | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 16 | DeepSets-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Fused-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_partition | 16 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Native-Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 16 | Native-Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | T1-MLP | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | T2-MLP | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 16 | Warm-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 64 | Aligned | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | D-RRC-NoType | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | D-RRC-Type | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 64 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 64 | DeepSets-Info | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | DeepSets-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | DeepSets-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | DeepSets-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Fused-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_partition | 64 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Native-Fused-Original | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Native-Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | T1-MLP | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | T2-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | T2-MLP | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Warm-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 64 | Warm-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 256 | Aligned | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | D-RRC-NoType | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | D-RRC-NoType | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | D-RRC-Type | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 256 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 256 | DeepSets-Info | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | DeepSets-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | DeepSets-KL | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | DeepSets-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | Fused-Info | 32 | 2/6 | 6 | 0 | 0.333 | 0 | False |
| eval_ood_partition | 256 | Fused-Info | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | Fused-Original | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 256 | Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | Native-Fused-Original | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_ood_partition | 256 | Native-Fused-Original | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | T1-MLP | 32 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | T1-MLP | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_ood_partition | 256 | T2-MLP | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 256 | T2-MLP | 64 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 256 | Warm-KL | 32 | 3/6 | 6 | 0 | 0.5 | 0 | False |
| eval_ood_partition | 256 | Warm-KL | 64 | 4/6 | 6 | 0 | 0.667 | 0 | False |
| eval_variable | 64 | Aligned | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Aligned | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | D-RRC-NoType | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | D-RRC-NoType | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | D-RRC-Type | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | D-RRC-Type | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | DeepSets-Info | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | DeepSets-Info | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | DeepSets-KL | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | DeepSets-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Fused-Info | 32 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | Fused-Info | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | Fused-Original | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Fused-Original | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Native-Fused-Original | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Native-Fused-Original | 64 | 6/6 | 6 | 0 | 1 | 0 | True |
| eval_variable | 64 | T1-MLP | 32 | 0/0 | 0 | 0 | unavailable | 0 | False |
| eval_variable | 64 | T1-MLP | 64 | 0/0 | 0 | 0 | unavailable | 0 | False |
| eval_variable | 64 | T2-MLP | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | T2-MLP | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Warm-KL | 32 | 5/6 | 6 | 0 | 0.833 | 0 | False |
| eval_variable | 64 | Warm-KL | 64 | 5/6 | 6 | 0 | 0.833 | 0 | False |

## Exact offline allocation quality

| Scope | Split | Model | States / planned | N/A | Worlds | Infinite radial states | L1 | Forward KL | Exact relative radial regret | Inference seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_applicable | id_test | DeepSets-Info | 96/96 | 0 | 16 | 0 | 0.134 [0.0708, 0.216] | 0.0764 [0.0221, 0.174] | 0.0821 [0.0502, 0.115] | 0.00109 [0.00107, 0.00113] |
| all_applicable | id_test | DeepSets-KL | 96/96 | 0 | 16 | 0 | 0.122 [0.065, 0.203] | 0.062 [0.0161, 0.144] | 0.0961 [0.059, 0.142] | 0.00108 [0.00107, 0.00109] |
| all_applicable | id_test | T1-MLP | 30/96 | 66 | 5 | 0 | 0.846 [0.493, 1.2] | 1.43 [0.568, 2.66] | 3.73 [1.08, 7.9] | 0.000778 [0.000537, 0.00125] |
| all_applicable | id_test | T2-MLP | 96/96 | 0 | 16 | 0 | 0.122 [0.076, 0.181] | 0.0343 [0.0124, 0.0701] | 0.109 [0.0758, 0.146] | 0.000811 [0.000779, 0.000855] |
| all_applicable | ood_calibration | DeepSets-Info | 96/96 | 0 | 16 | 0 | 0.118 [0.072, 0.171] | 0.0505 [0.0209, 0.0981] | 0.0732 [0.045, 0.103] | 0.00106 [0.00105, 0.00107] |
| all_applicable | ood_calibration | DeepSets-KL | 96/96 | 0 | 16 | 0 | 0.108 [0.0673, 0.158] | 0.0422 [0.0155, 0.0849] | 0.0955 [0.055, 0.147] | 0.00106 [0.00105, 0.00107] |
| all_applicable | ood_calibration | T1-MLP | 30/96 | 66 | 5 | 0 | 0.606 [0.38, 0.811] | 0.567 [0.344, 0.756] | 1.11 [0.618, 1.52] | 0.000518 [0.000515, 0.000521] |
| all_applicable | ood_calibration | T2-MLP | 96/96 | 0 | 16 | 0 | 0.102 [0.068, 0.143] | 0.024 [0.0119, 0.0397] | 0.091 [0.0611, 0.127] | 0.000789 [0.000772, 0.00081] |
| all_applicable | ood_parameters | DeepSets-Info | 96/96 | 0 | 16 | 0 | 0.0735 [0.0533, 0.0952] | 0.0188 [0.0141, 0.0241] | 0.0545 [0.0377, 0.0725] | 0.00106 [0.00106, 0.00107] |
| all_applicable | ood_parameters | DeepSets-KL | 96/96 | 0 | 16 | 0 | 0.0915 [0.0674, 0.116] | 0.0222 [0.0157, 0.029] | 0.0993 [0.0658, 0.134] | 0.00107 [0.00106, 0.00109] |
| all_applicable | ood_parameters | T1-MLP | 30/96 | 66 | 5 | 0 | 0.609 [0.402, 0.911] | 0.582 [0.341, 0.923] | 1.74 [0.613, 2.95] | 0.00053 [0.00052, 0.000536] |
| all_applicable | ood_parameters | T2-MLP | 96/96 | 0 | 16 | 0 | 0.103 [0.0769, 0.128] | 0.0219 [0.0142, 0.03] | 0.107 [0.0726, 0.144] | 0.000778 [0.000769, 0.000788] |
| all_applicable | ood_partition | DeepSets-Info | 96/96 | 0 | 16 | 0 | 0.135 [0.105, 0.166] | 0.0373 [0.0256, 0.0506] | 0.0929 [0.0743, 0.112] | 0.0011 [0.00109, 0.00111] |
| all_applicable | ood_partition | DeepSets-KL | 96/96 | 0 | 16 | 0 | 0.12 [0.0947, 0.15] | 0.034 [0.0223, 0.0491] | 0.116 [0.0979, 0.134] | 0.0011 [0.00109, 0.0011] |
| all_applicable | ood_partition | T1-MLP | 96/96 | 0 | 16 | 0 | 0.774 [0.681, 0.871] | 0.771 [0.602, 0.958] | 3.67 [1.9, 6.07] | 0.000526 [0.000522, 0.000532] |
| all_applicable | ood_partition | T2-MLP | 96/96 | 0 | 16 | 0 | 0.284 [0.211, 0.361] | 0.398 [0.215, 0.605] | 8.79 [3.75, 14.4] | 0.000792 [0.000782, 0.000806] |
| matched_d4 | id_test | DeepSets-Info | 30/30 | 0 | 5 | 0 | 0.0743 [0.0258, 0.139] | 0.0216 [0.0121, 0.0352] | 0.0658 [0.016, 0.123] | 0.00114 [0.00109, 0.00124] |
| matched_d4 | id_test | DeepSets-KL | 30/30 | 0 | 5 | 0 | 0.0595 [0.0294, 0.093] | 0.0123 [0.00562, 0.019] | 0.081 [0.0297, 0.157] | 0.00109 [0.00107, 0.0011] |
| matched_d4 | id_test | T1-MLP | 30/30 | 0 | 5 | 0 | 0.846 [0.493, 1.2] | 1.43 [0.568, 2.66] | 3.73 [1.08, 7.9] | 0.000778 [0.000537, 0.00125] |
| matched_d4 | id_test | T2-MLP | 30/30 | 0 | 5 | 0 | 0.0654 [0.0389, 0.0947] | 0.00669 [0.00279, 0.0116] | 0.084 [0.0439, 0.134] | 0.000793 [0.000784, 0.000801] |
| matched_d4 | ood_calibration | DeepSets-Info | 30/30 | 0 | 5 | 0 | 0.0788 [0.0258, 0.147] | 0.0221 [0.00899, 0.0374] | 0.0503 [0.0153, 0.101] | 0.00107 [0.00106, 0.00108] |
| matched_d4 | ood_calibration | DeepSets-KL | 30/30 | 0 | 5 | 0 | 0.07 [0.0254, 0.127] | 0.016 [0.00415, 0.0338] | 0.0939 [0.0244, 0.207] | 0.00108 [0.00106, 0.00109] |
| matched_d4 | ood_calibration | T1-MLP | 30/30 | 0 | 5 | 0 | 0.606 [0.38, 0.811] | 0.567 [0.344, 0.756] | 1.11 [0.618, 1.52] | 0.000518 [0.000515, 0.000521] |
| matched_d4 | ood_calibration | T2-MLP | 30/30 | 0 | 5 | 0 | 0.0772 [0.0424, 0.117] | 0.012 [0.00267, 0.0252] | 0.106 [0.0506, 0.182] | 0.000826 [0.000789, 0.000864] |
| matched_d4 | ood_parameters | DeepSets-Info | 30/30 | 0 | 5 | 0 | 0.0516 [0.0247, 0.0791] | 0.0131 [0.00948, 0.0168] | 0.0328 [0.0139, 0.0533] | 0.00108 [0.00106, 0.00109] |
| matched_d4 | ood_parameters | DeepSets-KL | 30/30 | 0 | 5 | 0 | 0.0694 [0.0259, 0.121] | 0.0135 [0.00468, 0.0262] | 0.109 [0.023, 0.195] | 0.00109 [0.00107, 0.00111] |
| matched_d4 | ood_parameters | T1-MLP | 30/30 | 0 | 5 | 0 | 0.609 [0.402, 0.911] | 0.582 [0.341, 0.923] | 1.74 [0.613, 2.95] | 0.00053 [0.00052, 0.000536] |
| matched_d4 | ood_parameters | T2-MLP | 30/30 | 0 | 5 | 0 | 0.0826 [0.04, 0.126] | 0.0132 [0.00305, 0.0244] | 0.121 [0.0434, 0.222] | 0.000794 [0.000785, 0.000811] |
| matched_d4 | ood_partition | DeepSets-Info | 96/96 | 0 | 16 | 0 | 0.135 [0.105, 0.166] | 0.0373 [0.0256, 0.0506] | 0.0929 [0.0743, 0.112] | 0.0011 [0.00109, 0.00111] |
| matched_d4 | ood_partition | DeepSets-KL | 96/96 | 0 | 16 | 0 | 0.12 [0.0947, 0.15] | 0.034 [0.0223, 0.0491] | 0.116 [0.0979, 0.134] | 0.0011 [0.00109, 0.0011] |
| matched_d4 | ood_partition | T1-MLP | 96/96 | 0 | 16 | 0 | 0.774 [0.681, 0.871] | 0.771 [0.602, 0.958] | 3.67 [1.9, 6.07] | 0.000526 [0.000522, 0.000532] |
| matched_d4 | ood_partition | T2-MLP | 96/96 | 0 | 16 | 0 | 0.284 [0.211, 0.361] | 0.398 [0.215, 0.605] | 8.79 [3.75, 14.4] | 0.000792 [0.000782, 0.000806] |

The information-training loss used finite cuts; this offline table uses the separate exact radial evaluator. The experiment supports only this simulator, frozen condition grid, models, and budget. No novelty, human-dialogue, or population noninferiority claim is made.
