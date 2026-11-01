# T2 computational cost

Final manual assessment is **REVISE**, documented in FINAL_DECISION.md. The automatic tables below remain the frozen analyzer's output. Speedups describe the recorded CPU policy paths; they do not establish a whole-project amortization advantage.

The target speedup is the ratio of sums of **estimation + planning + inference** seconds for the matched Fused-Original teacher and each candidate. It includes Fused estimation. Gate, stopping GLR, evaluation-only score GLR, environment, wall and CPU are reported separately. Wall speedup is an additional measured quantity and includes their realized overhead. Summed component timers are not asserted to partition wall time exactly.

All ratios use complete planned pairs, including cap abstentions; no successful-path-only compute average is used. Risk repetitions stay inside the same world during resampling. 95% percentile world-cluster bootstrap descriptive range; not a calibrated confidence or noninferiority interval.

## Matched paired compute

| Method | Pairs | World clusters | Inclusive compute speedup | Wall speedup |
| --- | --- | --- | --- | --- |
| Aligned | 72/72 | 24 | 0.807 [0.703, 0.937] | 0.808 [0.705, 0.938] |
| D-RRC-NoType | 72/72 | 24 | 487 [402, 559] | 20.3 [16.6, 23.5] |
| D-RRC-Type | 72/72 | 24 | 376 [311, 430] | 22.7 [18.2, 26.5] |
| DeepSets-Info | 72/72 | 24 | 20.2 [17, 22.8] | 11.9 [9.75, 13.6] |
| DeepSets-KL | 72/72 | 24 | 20.3 [16.9, 22.8] | 11.9 [9.69, 13.6] |
| Fused-Info | 72/72 | 24 | 3.6 [3.07, 3.99] | 3.31 [2.82, 3.69] |
| Native-Fused-Original | 72/72 | 24 | 0.751 [0.632, 0.848] | 0.757 [0.641, 0.852] |
| T1-MLP | 72/72 | 24 | 70 [55.1, 83.5] | 12.2 [9.63, 14.6] |
| T2-MLP | 72/72 | 24 | 13.3 [9.62, 17.7] | 7.89 [5.78, 10.4] |
| Warm-KL | 72/72 | 24 | 0.678 [0.653, 0.709] | 0.686 [0.662, 0.716] |

## Per-stratum, risk and method timing totals

| Stratum | R | Method | Complete / applicable | estimation | planning | inference | glr | score_glr | gate | environment | wall | cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eval_id | 16 | Aligned | 6/6 | 0.0214 | 15.5 | 0 | 0.0805 | 0 | 0.0815 | 0.177 | 16.1 | 16.1 |
| eval_id | 16 | D-RRC-NoType | 6/6 | 0.0291 | 0.00347 | 0 | 0.107 | 0 | 0.0757 | 0.237 | 0.808 | 0.808 |
| eval_id | 16 | D-RRC-Type | 6/6 | 0.0248 | 0.0159 | 0 | 0.0924 | 0 | 0.0799 | 0.203 | 0.72 | 0.719 |
| eval_id | 16 | DeepSets-Info | 6/6 | 0.418 | 0 | 0.158 | 0.0618 | 0 | 0.0851 | 0.137 | 1.07 | 1.07 |
| eval_id | 16 | DeepSets-KL | 6/6 | 0.389 | 0 | 0.149 | 0.0585 | 0 | 0.0867 | 0.131 | 1.01 | 1.01 |
| eval_id | 16 | Fused-Info | 6/6 | 0.333 | 2.55 | 0 | 0.0494 | 0 | 0.0748 | 0.109 | 3.27 | 3.27 |
| eval_id | 16 | Fused-Original | 6/6 | 0.315 | 9.45 | 0 | 0.0535 | 0 | 0.0841 | 0.119 | 10.2 | 10.2 |
| eval_id | 16 | Native-Fused-Original | 6/6 | 0.616 | 18.9 | 0 | 0.0544 | 0 | 0.0833 | 0.123 | 20 | 20 |
| eval_id | 16 | T1-MLP | 6/6 | 0.0413 | 0 | 0.141 | 0.134 | 0 | 0.0903 | 0.291 | 1.15 | 1.15 |
| eval_id | 16 | T2-MLP | 6/6 | 0.372 | 0 | 0.106 | 0.0563 | 0 | 0.0839 | 0.127 | 0.933 | 0.933 |
| eval_id | 16 | Warm-KL | 6/6 | 0.348 | 13.4 | 0 | 0.0529 | 0 | 0.0838 | 0.119 | 14.2 | 14.2 |
| eval_id | 64 | Aligned | 6/6 | 0.032 | 23.2 | 0 | 0.124 | 0 | 0.0937 | 0.273 | 24.2 | 24.2 |
| eval_id | 64 | D-RRC-NoType | 6/6 | 0.0433 | 0.0051 | 0 | 0.165 | 0 | 0.0859 | 0.361 | 1.2 | 1.2 |
| eval_id | 64 | D-RRC-Type | 6/6 | 0.0403 | 0.0261 | 0 | 0.157 | 0 | 0.0916 | 0.338 | 1.16 | 1.16 |
| eval_id | 64 | DeepSets-Info | 6/6 | 0.767 | 0 | 0.273 | 0.112 | 0 | 0.0997 | 0.244 | 1.86 | 1.86 |
| eval_id | 64 | DeepSets-KL | 6/6 | 0.704 | 0 | 0.258 | 0.105 | 0 | 0.0961 | 0.234 | 1.74 | 1.74 |
| eval_id | 64 | Fused-Info | 6/6 | 0.61 | 4.82 | 0 | 0.0963 | 0 | 0.101 | 0.214 | 6.16 | 6.15 |
| eval_id | 64 | Fused-Original | 6/6 | 0.612 | 17.6 | 0 | 0.1 | 0 | 0.0985 | 0.223 | 18.9 | 18.9 |
| eval_id | 64 | Native-Fused-Original | 6/6 | 1.01 | 26.9 | 0 | 0.102 | 0 | 0.0985 | 0.23 | 28.7 | 28.7 |
| eval_id | 64 | T1-MLP | 6/6 | 0.0637 | 0 | 0.201 | 0.2 | 0 | 0.1 | 0.424 | 1.65 | 1.65 |
| eval_id | 64 | T2-MLP | 6/6 | 0.7 | 0 | 0.196 | 0.105 | 0 | 0.096 | 0.234 | 1.68 | 1.68 |
| eval_id | 64 | Warm-KL | 6/6 | 0.665 | 26.1 | 0 | 0.1 | 0 | 0.0966 | 0.225 | 27.5 | 27.5 |
| eval_id | 256 | Aligned | 6/6 | 0.0664 | 41.8 | 0 | 0.272 | 0 | 0.11 | 0.593 | 43.7 | 43.7 |
| eval_id | 256 | D-RRC-NoType | 6/6 | 0.0842 | 0.00994 | 0 | 0.335 | 0 | 0.0909 | 0.73 | 2.32 | 2.32 |
| eval_id | 256 | D-RRC-Type | 6/6 | 0.0703 | 0.0428 | 0 | 0.293 | 0 | 0.111 | 0.623 | 2.05 | 2.05 |
| eval_id | 256 | DeepSets-Info | 6/6 | 1.84 | 0 | 0.637 | 0.271 | 0 | 0.109 | 0.588 | 4.31 | 4.31 |
| eval_id | 256 | DeepSets-KL | 6/6 | 1.9 | 0 | 0.66 | 0.276 | 0 | 0.108 | 0.605 | 4.45 | 4.45 |
| eval_id | 256 | Fused-Info | 6/6 | 1.71 | 13 | 0 | 0.257 | 0 | 0.107 | 0.56 | 16.5 | 16.5 |
| eval_id | 256 | Fused-Original | 6/6 | 1.66 | 42.6 | 0 | 0.269 | 0 | 0.107 | 0.587 | 46.1 | 46.1 |
| eval_id | 256 | Native-Fused-Original | 6/6 | 1.61 | 44.2 | 0 | 0.268 | 0 | 0.106 | 0.582 | 47.6 | 47.6 |
| eval_id | 256 | T1-MLP | 6/6 | 0.133 | 0 | 0.347 | 0.358 | 0 | 0.118 | 0.749 | 2.85 | 2.85 |
| eval_id | 256 | T2-MLP | 6/6 | 1.87 | 0 | 0.481 | 0.274 | 0 | 0.115 | 0.602 | 4.23 | 4.23 |
| eval_id | 256 | Warm-KL | 6/6 | 1.79 | 65.9 | 0 | 0.266 | 0 | 0.107 | 0.584 | 69.6 | 69.5 |
| eval_ood_calibration | 16 | Aligned | 6/6 | 0.0305 | 25.2 | 0 | 0.119 | 0 | 0.0751 | 0.251 | 26.1 | 26.1 |
| eval_ood_calibration | 16 | D-RRC-NoType | 6/6 | 0.0241 | 0.00276 | 0 | 0.0906 | 0 | 0.0688 | 0.198 | 0.729 | 0.729 |
| eval_ood_calibration | 16 | D-RRC-Type | 6/6 | 0.0211 | 0.016 | 0 | 0.081 | 0 | 0.081 | 0.176 | 0.642 | 0.642 |
| eval_ood_calibration | 16 | DeepSets-Info | 6/6 | 0.335 | 0 | 0.141 | 0.055 | 0 | 0.0769 | 0.123 | 0.915 | 0.915 |
| eval_ood_calibration | 16 | DeepSets-KL | 6/6 | 0.319 | 0 | 0.134 | 0.0525 | 0 | 0.0724 | 0.118 | 0.872 | 0.872 |
| eval_ood_calibration | 16 | Fused-Info | 6/6 | 0.28 | 2.34 | 0 | 0.0502 | 0 | 0.117 | 0.112 | 3.07 | 3.07 |
| eval_ood_calibration | 16 | Fused-Original | 6/6 | 0.283 | 7.91 | 0 | 0.0518 | 0 | 0.0746 | 0.116 | 8.6 | 8.6 |
| eval_ood_calibration | 16 | Native-Fused-Original | 6/6 | 0.573 | 16.6 | 0 | 0.0509 | 0 | 0.0745 | 0.116 | 17.6 | 17.6 |
| eval_ood_calibration | 16 | T1-MLP | 6/6 | 0.0397 | 0 | 0.129 | 0.133 | 0 | 0.0815 | 0.273 | 1.08 | 1.08 |
| eval_ood_calibration | 16 | T2-MLP | 6/6 | 0.341 | 0 | 0.103 | 0.0548 | 0 | 0.0729 | 0.123 | 0.879 | 0.879 |
| eval_ood_calibration | 16 | Warm-KL | 6/6 | 0.311 | 11.1 | 0 | 0.0514 | 0 | 0.0756 | 0.116 | 11.8 | 11.8 |
| eval_ood_calibration | 64 | Aligned | 6/6 | 0.0409 | 29.7 | 0 | 0.158 | 0 | 0.0886 | 0.344 | 30.8 | 30.8 |
| eval_ood_calibration | 64 | D-RRC-NoType | 6/6 | 0.0459 | 0.00535 | 0 | 0.169 | 0 | 0.0773 | 0.374 | 1.23 | 1.23 |
| eval_ood_calibration | 64 | D-RRC-Type | 6/6 | 0.0304 | 0.023 | 0 | 0.116 | 0 | 0.0883 | 0.259 | 0.912 | 0.912 |
| eval_ood_calibration | 64 | DeepSets-Info | 6/6 | 0.61 | 0 | 0.244 | 0.0963 | 0 | 0.0941 | 0.218 | 1.59 | 1.59 |
| eval_ood_calibration | 64 | DeepSets-KL | 6/6 | 0.61 | 0 | 0.309 | 0.0953 | 0 | 0.0866 | 0.216 | 1.64 | 1.64 |
| eval_ood_calibration | 64 | Fused-Info | 6/6 | 0.518 | 4.34 | 0 | 0.0902 | 0 | 0.082 | 0.203 | 5.53 | 5.53 |
| eval_ood_calibration | 64 | Fused-Original | 6/6 | 0.522 | 13.6 | 0 | 0.0911 | 0 | 0.0823 | 0.205 | 14.8 | 14.8 |
| eval_ood_calibration | 64 | Native-Fused-Original | 6/6 | 0.839 | 23 | 0 | 0.0921 | 0 | 0.083 | 0.211 | 24.5 | 24.5 |
| eval_ood_calibration | 64 | T1-MLP | 6/6 | 0.0593 | 0 | 0.188 | 0.194 | 0 | 0.101 | 0.396 | 1.56 | 1.56 |
| eval_ood_calibration | 64 | T2-MLP | 6/6 | 0.678 | 0 | 0.195 | 0.103 | 0 | 0.0869 | 0.233 | 1.65 | 1.65 |
| eval_ood_calibration | 64 | Warm-KL | 6/6 | 0.567 | 20.5 | 0 | 0.0906 | 0 | 0.0815 | 0.206 | 21.7 | 21.7 |
| eval_ood_calibration | 256 | Aligned | 6/6 | 0.0733 | 52 | 0 | 0.295 | 0 | 0.102 | 0.626 | 54.1 | 54.1 |
| eval_ood_calibration | 256 | D-RRC-NoType | 6/6 | 0.0882 | 0.0101 | 0 | 0.343 | 0 | 0.0857 | 0.737 | 2.39 | 2.39 |
| eval_ood_calibration | 256 | D-RRC-Type | 6/6 | 0.0737 | 0.0574 | 0 | 0.307 | 0 | 0.108 | 0.63 | 2.2 | 2.2 |
| eval_ood_calibration | 256 | DeepSets-Info | 6/6 | 1.87 | 0 | 0.711 | 0.282 | 0 | 0.105 | 0.597 | 4.5 | 4.5 |
| eval_ood_calibration | 256 | DeepSets-KL | 6/6 | 1.92 | 0 | 0.735 | 0.288 | 0 | 0.0992 | 0.615 | 4.61 | 4.61 |
| eval_ood_calibration | 256 | Fused-Info | 6/6 | 1.56 | 12.8 | 0 | 0.261 | 0 | 0.0959 | 0.558 | 16.1 | 16.1 |
| eval_ood_calibration | 256 | Fused-Original | 6/6 | 1.62 | 45.6 | 0 | 0.272 | 0 | 0.104 | 0.583 | 49.1 | 49.1 |
| eval_ood_calibration | 256 | Native-Fused-Original | 6/6 | 1.61 | 46.6 | 0 | 0.273 | 0 | 0.106 | 0.581 | 50.1 | 50.1 |
| eval_ood_calibration | 256 | T1-MLP | 6/6 | 0.141 | 0 | 0.394 | 0.416 | 0 | 0.128 | 0.812 | 3.18 | 3.18 |
| eval_ood_calibration | 256 | T2-MLP | 6/6 | 1.99 | 0 | 0.548 | 0.297 | 0 | 0.107 | 0.638 | 4.57 | 4.57 |
| eval_ood_calibration | 256 | Warm-KL | 6/6 | 1.76 | 72.9 | 0 | 0.27 | 0 | 0.101 | 0.581 | 76.6 | 76.5 |
| eval_ood_parameters | 16 | Aligned | 6/6 | 0.00863 | 6.74 | 0 | 0.0333 | 0 | 0.0819 | 0.0725 | 7.04 | 7.04 |
| eval_ood_parameters | 16 | D-RRC-NoType | 6/6 | 0.0109 | 0.00125 | 0 | 0.041 | 0 | 0.0705 | 0.0902 | 0.345 | 0.345 |
| eval_ood_parameters | 16 | D-RRC-Type | 6/6 | 0.00995 | 0.00702 | 0 | 0.0384 | 0 | 0.0856 | 0.0839 | 0.347 | 0.347 |
| eval_ood_parameters | 16 | DeepSets-Info | 6/6 | 0.188 | 0 | 0.0913 | 0.0343 | 0 | 0.0841 | 0.0764 | 0.586 | 0.586 |
| eval_ood_parameters | 16 | DeepSets-KL | 6/6 | 0.193 | 0 | 0.0915 | 0.0344 | 0 | 0.0991 | 0.0755 | 0.603 | 0.603 |
| eval_ood_parameters | 16 | Fused-Info | 6/6 | 0.157 | 1.43 | 0 | 0.0314 | 0 | 0.084 | 0.0705 | 1.87 | 1.87 |
| eval_ood_parameters | 16 | Fused-Original | 6/6 | 0.161 | 5.81 | 0 | 0.0325 | 0 | 0.0822 | 0.0716 | 6.26 | 6.26 |
| eval_ood_parameters | 16 | Native-Fused-Original | 6/6 | 0.44 | 15.6 | 0 | 0.0311 | 0 | 0.0812 | 0.0714 | 16.4 | 16.4 |
| eval_ood_parameters | 16 | T1-MLP | 6/6 | 0.0133 | 0 | 0.0451 | 0.0422 | 0 | 0.085 | 0.0921 | 0.416 | 0.416 |
| eval_ood_parameters | 16 | T2-MLP | 6/6 | 0.176 | 0 | 0.0617 | 0.0321 | 0 | 0.0864 | 0.0718 | 0.532 | 0.532 |
| eval_ood_parameters | 16 | Warm-KL | 6/6 | 0.179 | 7 | 0 | 0.0326 | 0 | 0.0816 | 0.0736 | 7.48 | 7.47 |
| eval_ood_parameters | 64 | Aligned | 6/6 | 0.016 | 11.3 | 0 | 0.0629 | 0 | 0.0913 | 0.141 | 11.8 | 11.8 |
| eval_ood_parameters | 64 | D-RRC-NoType | 6/6 | 0.0231 | 0.0026 | 0 | 0.0877 | 0 | 0.0808 | 0.194 | 0.672 | 0.672 |
| eval_ood_parameters | 64 | D-RRC-Type | 6/6 | 0.0162 | 0.0109 | 0 | 0.0628 | 0 | 0.0958 | 0.14 | 0.528 | 0.528 |
| eval_ood_parameters | 64 | DeepSets-Info | 6/6 | 0.36 | 0 | 0.165 | 0.0621 | 0 | 0.0909 | 0.141 | 1.03 | 1.03 |
| eval_ood_parameters | 64 | DeepSets-KL | 6/6 | 0.341 | 0 | 0.157 | 0.0596 | 0 | 0.1 | 0.135 | 0.989 | 0.989 |
| eval_ood_parameters | 64 | Fused-Info | 6/6 | 0.299 | 2.58 | 0 | 0.0568 | 0 | 0.094 | 0.129 | 3.34 | 3.34 |
| eval_ood_parameters | 64 | Fused-Original | 6/6 | 0.328 | 10.1 | 0 | 0.0625 | 0 | 0.0951 | 0.138 | 10.9 | 10.9 |
| eval_ood_parameters | 64 | Native-Fused-Original | 6/6 | 0.678 | 20.4 | 0 | 0.0615 | 0 | 0.0954 | 0.141 | 21.6 | 21.6 |
| eval_ood_parameters | 64 | T1-MLP | 6/6 | 0.0361 | 0 | 0.114 | 0.11 | 0 | 0.106 | 0.234 | 0.961 | 0.961 |
| eval_ood_parameters | 64 | T2-MLP | 6/6 | 0.379 | 0 | 0.123 | 0.0643 | 0 | 0.0956 | 0.146 | 1.02 | 1.02 |
| eval_ood_parameters | 64 | Warm-KL | 6/6 | 0.345 | 13.3 | 0 | 0.0603 | 0 | 0.0955 | 0.137 | 14.2 | 14.2 |
| eval_ood_parameters | 256 | Aligned | 6/6 | 0.039 | 28.1 | 0 | 0.165 | 0 | 0.103 | 0.36 | 29.3 | 29.3 |
| eval_ood_parameters | 256 | D-RRC-NoType | 6/6 | 0.0653 | 0.00737 | 0 | 0.264 | 0 | 0.0827 | 0.559 | 1.8 | 1.8 |
| eval_ood_parameters | 256 | D-RRC-Type | 6/6 | 0.0442 | 0.0333 | 0 | 0.189 | 0 | 0.11 | 0.397 | 1.34 | 1.34 |
| eval_ood_parameters | 256 | DeepSets-Info | 6/6 | 1.03 | 0 | 0.465 | 0.165 | 0 | 0.106 | 0.361 | 2.65 | 2.65 |
| eval_ood_parameters | 256 | DeepSets-KL | 6/6 | 1.17 | 0 | 0.492 | 0.177 | 0 | 0.11 | 0.39 | 2.9 | 2.9 |
| eval_ood_parameters | 256 | Fused-Info | 6/6 | 0.888 | 7.09 | 0 | 0.155 | 0 | 0.106 | 0.337 | 9.05 | 9.05 |
| eval_ood_parameters | 256 | Fused-Original | 6/6 | 0.913 | 25.5 | 0 | 0.16 | 0 | 0.101 | 0.353 | 27.5 | 27.5 |
| eval_ood_parameters | 256 | Native-Fused-Original | 6/6 | 1.26 | 37 | 0 | 0.162 | 0 | 0.103 | 0.355 | 39.4 | 39.4 |
| eval_ood_parameters | 256 | T1-MLP | 6/6 | 0.135 | 0 | 0.3 | 0.334 | 0 | 0.127 | 0.643 | 2.53 | 2.53 |
| eval_ood_parameters | 256 | T2-MLP | 6/6 | 1.26 | 0 | 0.336 | 0.186 | 0 | 0.114 | 0.409 | 2.9 | 2.9 |
| eval_ood_parameters | 256 | Warm-KL | 6/6 | 1.01 | 37.8 | 0 | 0.161 | 0 | 0.1 | 0.352 | 39.9 | 39.9 |
| eval_ood_partition | 16 | Aligned | 6/6 | 0.0334 | 32.4 | 0 | 0.126 | 0 | 0.11 | 0.269 | 33.3 | 33.3 |
| eval_ood_partition | 16 | D-RRC-NoType | 6/6 | 0.0347 | 0.0037 | 0 | 0.13 | 0 | 0.101 | 0.272 | 0.962 | 0.962 |
| eval_ood_partition | 16 | D-RRC-Type | 6/6 | 0.036 | 0.0263 | 0 | 0.133 | 0 | 0.105 | 0.275 | 1 | 1 |
| eval_ood_partition | 16 | DeepSets-Info | 6/6 | 0.528 | 0 | 0.195 | 0.0748 | 0 | 0.109 | 0.159 | 1.31 | 1.31 |
| eval_ood_partition | 16 | DeepSets-KL | 6/6 | 0.491 | 0 | 0.184 | 0.0693 | 0 | 0.11 | 0.149 | 1.23 | 1.23 |
| eval_ood_partition | 16 | Fused-Info | 6/6 | 0.391 | 3.35 | 0 | 0.0609 | 0 | 0.11 | 0.129 | 4.23 | 4.23 |
| eval_ood_partition | 16 | Fused-Original | 6/6 | 0.457 | 18.2 | 0 | 0.0703 | 0 | 0.113 | 0.148 | 19.2 | 19.2 |
| eval_ood_partition | 16 | Native-Fused-Original | 6/6 | 0.853 | 35.1 | 0 | 0.0701 | 0 | 0.109 | 0.15 | 36.6 | 36.6 |
| eval_ood_partition | 16 | T1-MLP | 6/6 | 0.122 | 0 | 0.405 | 0.407 | 0 | 0.119 | 0.828 | 3.22 | 3.22 |
| eval_ood_partition | 16 | T2-MLP | 6/6 | 3.44 | 0 | 0.778 | 0.433 | 0 | 0.114 | 0.878 | 7.04 | 7.04 |
| eval_ood_partition | 16 | Warm-KL | 6/6 | 0.492 | 25.4 | 0 | 0.0697 | 0 | 0.112 | 0.149 | 26.4 | 26.4 |
| eval_ood_partition | 64 | Aligned | 6/6 | 0.047 | 46 | 0 | 0.18 | 0 | 0.136 | 0.383 | 47.4 | 47.4 |
| eval_ood_partition | 64 | D-RRC-NoType | 6/6 | 0.0495 | 0.0055 | 0 | 0.184 | 0 | 0.12 | 0.398 | 1.36 | 1.36 |
| eval_ood_partition | 64 | D-RRC-Type | 6/6 | 0.0404 | 0.0299 | 0 | 0.154 | 0 | 0.139 | 0.328 | 1.19 | 1.19 |
| eval_ood_partition | 64 | DeepSets-Info | 6/6 | 0.982 | 0 | 0.336 | 0.132 | 0 | 0.139 | 0.284 | 2.3 | 2.3 |
| eval_ood_partition | 64 | DeepSets-KL | 6/6 | 0.882 | 0 | 0.305 | 0.118 | 0 | 0.143 | 0.259 | 2.1 | 2.1 |
| eval_ood_partition | 64 | Fused-Info | 6/6 | 0.771 | 6.42 | 0 | 0.112 | 0 | 0.133 | 0.24 | 8.03 | 8.02 |
| eval_ood_partition | 64 | Fused-Original | 6/6 | 0.837 | 30.5 | 0 | 0.122 | 0 | 0.134 | 0.261 | 32.2 | 32.2 |
| eval_ood_partition | 64 | Native-Fused-Original | 6/6 | 1.23 | 45.8 | 0 | 0.122 | 0 | 0.124 | 0.262 | 47.9 | 47.9 |
| eval_ood_partition | 64 | T1-MLP | 6/6 | 0.151 | 0 | 0.452 | 0.472 | 0 | 0.136 | 0.951 | 3.67 | 3.67 |
| eval_ood_partition | 64 | T2-MLP | 6/6 | 3.93 | 0 | 0.83 | 0.478 | 0 | 0.122 | 0.984 | 7.88 | 7.88 |
| eval_ood_partition | 64 | Warm-KL | 6/6 | 0.892 | 44.7 | 0 | 0.12 | 0 | 0.131 | 0.26 | 46.5 | 46.5 |
| eval_ood_partition | 256 | Aligned | 6/6 | 0.0812 | 81.2 | 0 | 0.327 | 0 | 0.143 | 0.674 | 83.5 | 83.5 |
| eval_ood_partition | 256 | D-RRC-NoType | 6/6 | 0.0875 | 0.00952 | 0 | 0.344 | 0 | 0.127 | 0.72 | 2.37 | 2.37 |
| eval_ood_partition | 256 | D-RRC-Type | 6/6 | 0.0863 | 0.0635 | 0 | 0.347 | 0 | 0.157 | 0.69 | 2.38 | 2.38 |
| eval_ood_partition | 256 | DeepSets-Info | 6/6 | 2.56 | 0 | 0.8 | 0.331 | 0 | 0.149 | 0.676 | 5.55 | 5.55 |
| eval_ood_partition | 256 | DeepSets-KL | 6/6 | 2.48 | 0 | 0.792 | 0.323 | 0 | 0.155 | 0.67 | 5.44 | 5.44 |
| eval_ood_partition | 256 | Fused-Info | 6/6 | 2.19 | 17.9 | 0 | 0.359 | 0 | 0.146 | 0.634 | 22.2 | 22.2 |
| eval_ood_partition | 256 | Fused-Original | 6/6 | 2.32 | 80.8 | 0 | 0.33 | 0 | 0.148 | 0.675 | 85.3 | 85.3 |
| eval_ood_partition | 256 | Native-Fused-Original | 6/6 | 2.24 | 80.2 | 0 | 0.331 | 0 | 0.15 | 0.674 | 84.6 | 84.6 |
| eval_ood_partition | 256 | T1-MLP | 6/6 | 0.254 | 0 | 0.629 | 0.636 | 0 | 0.182 | 1.17 | 4.72 | 4.72 |
| eval_ood_partition | 256 | T2-MLP | 6/6 | 4.06 | 0 | 1.01 | 0.533 | 0 | 0.145 | 1.04 | 8.41 | 8.41 |
| eval_ood_partition | 256 | Warm-KL | 6/6 | 2.46 | 119 | 0 | 0.322 | 0 | 0.143 | 0.667 | 124 | 124 |
| eval_variable | 64 | Aligned | 6/6 | 0.021 | 16.2 | 0 | 0.0797 | 0 | 0.0446 | 0.183 | 16.8 | 16.8 |
| eval_variable | 64 | D-RRC-NoType | 6/6 | 0.0277 | 0.00321 | 0 | 0.101 | 0 | 0.0375 | 0.233 | 0.746 | 0.746 |
| eval_variable | 64 | D-RRC-Type | 6/6 | 0.0212 | 0.0134 | 0 | 0.0801 | 0 | 0.0452 | 0.184 | 0.613 | 0.613 |
| eval_variable | 64 | DeepSets-Info | 6/6 | 0.225 | 0 | 0.163 | 0.0649 | 0 | 0.0467 | 0.152 | 0.873 | 0.873 |
| eval_variable | 64 | DeepSets-KL | 6/6 | 0.224 | 0 | 0.162 | 0.0643 | 0 | 0.0482 | 0.152 | 0.87 | 0.87 |
| eval_variable | 64 | Fused-Info | 6/6 | 0.185 | 1.27 | 0 | 0.062 | 0 | 0.0457 | 0.145 | 1.92 | 1.92 |
| eval_variable | 64 | Fused-Original | 6/6 | 0.178 | 10.9 | 0 | 0.0619 | 0 | 0.0473 | 0.144 | 11.5 | 11.5 |
| eval_variable | 64 | Native-Fused-Original | 6/6 | 0.35 | 21.2 | 0 | 0.0619 | 0 | 0.0492 | 0.149 | 22 | 22 |
| eval_variable | 64 | T1-MLP | 0/0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| eval_variable | 64 | T2-MLP | 6/6 | 0.229 | 0 | 0.119 | 0.0653 | 0 | 0.0502 | 0.153 | 0.84 | 0.84 |
| eval_variable | 64 | Warm-KL | 6/6 | 0.208 | 14.1 | 0 | 0.0607 | 0 | 0.0437 | 0.144 | 14.8 | 14.8 |

## Preparation and training accounting

| Stage | Scope | Outer wall seconds | CPU seconds | CPU scope | Status |
| --- | --- | --- | --- | --- | --- |
| Preparation incl. data/labels and budget development | outer_total | 473 | 473 | current process | completed |
| Three-fit training total | outer_total | 21.1 | 21.1 | current process | completed |
| Evaluation outer process/pool | outer_total | 1.01e+03 | 14.1 | parent process only; excludes worker CPU | completed |
| deepsets_info | component_of_training_total_do_not_add_again | 11.1 | 11.1 | current process | recorded |
| deepsets_kl | component_of_training_total_do_not_add_again | 4.78 | 4.78 | current process | recorded |
| mlp | component_of_training_total_do_not_add_again | 4.51 | 4.51 | current process | recorded |
| data | component_of_preparation_total_do_not_add_again | 465 | unavailable | not separately measured | completed |
| budget_development | component_of_preparation_total_do_not_add_again | 5.3 | unavailable | not separately measured | frozen |

Raw preparation, training and evaluation execution receipts are preserved in `artifacts/analysis/execution_receipts.json`. They remain separate from policy-time speedups: teacher-label construction and network fitting are not free. Outer wall/CPU totals must not be added to their nested substage totals a second time. No break-even or amortized advantage is claimed without a declared deployment denominator.

```json
{
  "evaluation_execution": {
    "expected_applicable_paths": 852,
    "expected_nonapplicable_paths": 6,
    "external_api_calls": 0,
    "failed_paths": 0,
    "gpu_jobs": 0,
    "not_applicable_paths": 6,
    "offline_records": 1536,
    "outer_parent_cpu_seconds": 14.064821187,
    "outer_wall_seconds": 1007.3733561639674,
    "parent_model_load_wall_seconds": 1.3776218621060252,
    "path_records": 858,
    "qwen_calls": 0,
    "scientific_retries": 0,
    "status": "completed",
    "world_risk_jobs": 78
  },
  "preparation_execution": {
    "budget_development": {
      "independent_worlds": 18,
      "new_search_after_freeze": false,
      "readout_budgets": [
        32,
        64
      ],
      "rule": "nearest teacher pooled exact recovery to each target; distinct ascending budgets, ties smaller; if same choose remaining nearest to second target; use no student outcomes",
      "status": "frozen",
      "student_predictions_used": 0,
      "teacher_only_accuracy_curve": {
        "128": 0.9444444444444444,
        "16": 0.2222222222222222,
        "32": 0.6111111111111112,
        "48": 0.6666666666666666,
        "64": 0.8333333333333334,
        "96": 0.9444444444444444
      },
      "test_results_used": 0,
      "wall_seconds": 5.29890820896253
    },
    "data": {
      "generation_scope": "fresh development only",
      "online_actions": 360448,
      "splits": {
        "id_test": [
          "a072cfcd798acd70b938b28d",
          "df29013ea2c30da7edee55c6",
          "c9dac7d602cd4cd8c3058615",
          "b64e41f843c83769ea302c3d",
          "f8125341f7c9b66fc060e917",
          "145b378b607bd8ecb8352668",
          "5e33521977b01f252b4e95e4",
          "5105450b823fde7b72ad0edd",
          "78eb8260e776bbd7254c7969",
          "42c91704890dc9331e9c7e98",
          "7a3d891faace581c098f3778",
          "4aeed6b60d8c80497e07197f",
          "a3b730adbd5f582499bf9f6d",
          "05d3bb3ccf9966b05b647816",
          "02d0b0d00aa42715819da449",
          "0316a75c434c569672078add"
        ],
        "ood_calibration": [
          "1b916dabf21c5d450d0646d2",
          "6bc8b553a4873172eaeeb461",
          "82ff7da03e3f7684cf850837",
          "f1ae83643b618bc0c61b974c",
          "59cb0fd3554b945d9068fc7e",
          "5aa082917fef10749f574748",
          "f7dde07ec4f8ae2f5e83e4cc",
          "b2e190f87fa490ef4091b7c9",
          "de4a93854af5891401b3f798",
          "e2d83fee53226087f9b5445b",
          "f3bad6bae1e775ad18846cfb",
          "9bd3da2b5229809a41668dfa",
          "ba310b449fedcb95c39cd1e9",
          "b97a925e3f7c92fc27f92ff6",
          "0ce78842508af5f0fa6eab3f",
          "ce08d0616fe18cd100a803ff"
        ],
        "ood_parameters": [
          "2d7d23edbea8f8616a0d4533",
          "86cb4a297a315e390b0f4bdb",
          "c5b8262b4367de65f1924d69",
          "5583ea339d565b217dcaccb2",
          "f38f92f98d1feb8fd5055f78",
          "677b2be1c76f55e00b35254c",
          "c5d5d1b019878212ac4ea694",
          "8f613a17f98fbdb0bbb88801",
          "2a4e159dbc837c25234ba063",
          "0259051b3e93b27eaef9b5f0",
          "f08d48b0041fad5e80a38672",
          "d4c2b398e95746d4daa29e8e",
          "cfdc4dba3383f272d3569e58",
          "94c49dc2ce212cafd8b2156d",
          "1b3e0aca45893729f14f4e05",
          "f2700fa9493bd3ae01ca23d1"
        ],
        "ood_partition": [
          "ccd92cb89d1c301a0a9e9cb3",
          "52cf7764c17d6de609a89719",
          "de1d15be0084a11f85b2bbcb",
          "5bf1bfb2b6b327b27b2a421a",
          "94362ce5d84aad8914438ac4",
          "329230372a244ef60ce9670d",
          "20490b507660d16a6dbe4aec",
          "6fbf8b5ae7bdc3f78569c9f6",
          "dedc58f7df3209879c70ed09",
          "35245eeca20e215447a0f144",
          "8c8719af6a7092a189cc3436",
          "1bfaf0c7cd06c99a2509194b",
          "d4f289debd9c87aee2604f6c",
          "563d8724451b4b03f1d8c2c0",
          "452d90ea2cb2620d9f21f9b5",
          "af7ce582d15eb01bf26af194"
        ],
        "train": [
          "52223ed4897d1384e706580a",
          "43e9a91572bb2a02f1048bd6",
          "b92fdba253478fb931f59137",
          "958c588c9189f94253c9236d",
          "fbd1b013c0d2d68be767cd44",
          "f0e3335c016a03857c459076",
          "e1635358012538c6367fec82",
          "4edf2937d3271d8cd5504579",
          "e1e1f5d26316750de19f4f3d",
          "a388a08ad2cf052ff993571f",
          "d4bf3fb63e6e88298a797117",
          "a6fa1a3f9765851c8d3550fa",
          "851f79bafad58ec7b0af5c08",
          "87a05b1d26434ea711b23ac3",
          "d5f795955d23abcbaf745c8a",
          "9ddbd7679d7ade1e8a8bd48f",
          "8573f2aed04c01459c85984b",
          "cb55f218e2e6e44217c46d98",
          "1ffca2c4abdf264cd9a8f1ca",
          "c154c7481027e197e10eb6b9",
          "73f3b192fad2b148b6d16b7f",
          "c6b05535b947d776129bc058",
          "34aba6c4186696f9825bfce9",
          "0bc3d707372ed6d1b0dcefc3",
          "a397ed30a49ff3a7103b5e8b",
          "ef94ce191e0888272ecfcc53",
          "0bd4fe9211cd49100cc0b0ea",
          "a1d555ce4e1c4b7cb9127d34",
          "828f156874b438260035cf9b",
          "7caaa73adac485f484e7710c",
          "cd524c35e31da35f34658540",
          "9c87f1f9fab1bbbc9413ed96",
          "b2b13cc682dab23be0f37d69",
          "8bef00e88009921b9af6f071",
          "b7a388c308bd886592829b11",
          "7ac82907bbe368385cb4f560",
          "53da5662984f604441fa7c34",
          "ad947d7effda54d90f0eb838",
          "6e21437ff66d40a702787702",
          "246284360902df85965ce351",
          "70f30c0c9d4af5ecccc43f3e",
          "ab543e1951b5aabcff865d0b",
          "7f4f0d86bf2b247fdedb78f2",
          "795ae39c438c53d73687a490",
          "26ae3a81e6923ef45c6631cc",
          "14f460fd02494285c6dd6c87",
          "081f703ab0ac5c3950ec52e0",
          "be50bad5b002a36d6d6b3c19",
          "d8ce72e245d90a2eff7917d4",
          "53053f9ddca28f7fff4df7af",
          "393d146f421a172a3ace0aae",
          "f41772ca98acc5f44a9ef831",
          "d6282dfd1c820c32c1afe0ec",
          "e3620f8955699a99d6b58a26",
          "725a0c0075e8ceb9eaad8d63",
          "63f6ed62d76d95601b5322f5",
          "e23883f36cd95b7c38560689",
          "80e5e7789196cc6dbb621b65",
          "c71decbaf74ad0b9eedeb2bd",
          "dad5437df4547346f0954d40",
          "1d8a633bc445b04d7b087bcf",
          "fb3c29a63a05bba0b9a04e1c",
          "50e4f1e326bd9c069f3ce117",
          "f4fe966339ed0909157f4864",
          "eb81727e3a04560144bbe73a",
          "ebec083e9f40ac78ffac7b8c",
          "3ed1a09810ca152f2f74e2f3",
          "42ee4ab16118d59093420fc0",
          "6869835e3f45dd3ced5a2e20",
          "96e84dd9bd612eb5baf5dd5a",
          "5b9a14c2851e0bf533373107",
          "0fd6f1b9d8021893a5d43a32",
          "0d3a7d06c2d28df2bd1f8f95",
          "6126f01a1d87e2317e5efc56",
          "4642f8f517b65d297e72e34f",
          "7bb44c79308cf7fa4fe18caf",
          "bb283a64c1165ed316fa4d3d",
          "9090a3b163fe77007759fe8c",
          "e5f2c6dd39b414e66a7b9ec9",
          "d1d94f7d37329368c648c54b",
          "cea07d78029432c2a22a163b",
          "061da08edbb231e900bf0777",
          "d0d12b929f9cf1dc5cfbca4c",
          "1f072aff4bd93383dda518b7",
          "bcac04c5b6a2427aa636e1ab",
          "8d61abdcdacc0ebb60576108",
          "f512020238db4a0b39acd5db",
          "ee5d7131cf7e3c4a73b29ff2",
          "6aa02dff0f3db79ee13ebae4",
          "fe4ec8b11bb7191ded52e720",
          "5d4b05b60fa989ed4fec59af",
          "cbe773fb3ba28beed5c71b92",
          "9ad31270a60b093439498ad3",
          "5d4099628242f11ab7bee5f4",
          "3489152c0d8ee96ee88dc637",
          "988391390c7f068a17cfce05",
          "b5ba131ccceebeb58b672f51",
          "2d164f52901a3036b70becbb",
          "125845f373366b55a601c78e",
          "e05a2e2442adfa9ff040d8d8",
          "539164a598cbdf4b8bd45d9e",
          "a91d2d46bd153c7579648f12",
          "4271dd25f40566679035bb20",
          "af62825fe4f270d79b0ad0ca",
          "d4c3b5fde9480e6ab6bd791f",
          "996c4751805fb83d2b1891b5",
          "697234229c2416009b2e48d4",
          "af582f7dd2a1babee77c8aed",
          "3f081ef9e306f01d2fa44f6f",
          "6d84c782c5d401fbf0355b21",
          "0cc4c976e114441d51455335",
          "f2c075eac9f8f5f978c20bef",
          "23034a30551d7f6d60939260",
          "5b02a9ceb2a6dcf95b359f46",
          "ff47471471e910cc5e6762d4",
          "a50111c995ae5482eb2856a7",
          "d500f1b71e70ca3fd8631a1c",
          "2176452255bfe55c9070fcfc",
          "c7cb594eb61821c881f5175c",
          "8e7102fced6d22a4a1e91d2f",
          "87783ec9634b537dfbd75af7",
          "553b3fd40947b0f103fdd400",
          "93fbb3c764a7bf12cbf800b5",
          "65e766f428fd037e98fff0d8",
          "326a7ab6f6b476f5f41fcaab",
          "f5fd90f7d455b14558c5cc59",
          "66f10cc28622bbeaff8e1a80",
          "36afa2782a923a5170d68e29",
          "473b8cb2cf7e9b029a1a1e29",
          "7854534421c5215828bcb4c0",
          "227d7074f4d0ae18960b3a64",
          "25318c3be327227948d49323",
          "e6c9c99fa9912cd2f1954ef6",
          "c8892e940935fd7f1830597f",
          "6d24c6bcae1d612982e93a89",
          "950ce00ae1981f7652c71500",
          "0383bf2e720dad9e35b4d7eb",
          "0c616a80302ca1c08135541f",
          "0defd9dfbfc269df0c387f33",
          "e3375aee17f9d04302af2def",
          "e5aca6c81ab2e240a3d152ed",
          "1c0d8d7ddc4238dfc4f12ef3",
          "28ce730f6c29e6d005c7b608",
          "1b50d5e9101ddf16968c73da",
          "d061bdb580f7a11fd13ab736",
          "b433eddbb78191f37447e4ba",
          "dc7f46bdecd0662a0d2a671d",
          "40b6d6ac7fbfca45e788a76c",
          "28d5bad94d3d66caeb3402d6",
          "17afa5da26079076487ee069",
          "18a00b11e2ed5a3fb46e58dd",
          "52069a1c8fb7794c2d6fd30a",
          "97bc17c821c288973952ca66",
          "85f38bca672171029782c959",
          "1486d56979ad384f8439ad87",
          "da35ac545ea2e90ce05a7840",
          "c73ae13bdc191dc48ca3a8bb",
          "63b4a0827c3f926c6b21013b",
          "6c1563aa59c421170622b5bc",
          "968199ad891f7e39ea3bc176",
          "178f1e5f4352ec513e05dcfa",
          "fd09f54f23ba65936dd6c2cc",
          "ccda79d844892565fe95bc11",
          "94842e15068328a998c4fd8f",
          "8058e8289562c22878c46ec3",
          "ef0d536d19733ec1060bcb5b",
          "a81cd49c662b37bc11c28215",
          "3ba2395ee7eab584387b06d3",
          "f5ef5c746192b941e878fc07",
          "7fd5a598b1e8f7fec7f3e6c2",
          "ded96ab6fcb6892846324a21",
          "218d8de6bdbe5e3985d42e43",
          "4a2a4f9dd1736b7859910677",
          "e2398de48b8435e46db3ec6d",
          "d651852502ae8148c3f72bd0",
          "2e305c097904bccb6369c7db",
          "7ec33e4511f0b59f5f66e8dd",
          "c7a257cdc4505495f7e07a61",
          "8752b0d8b20397c4918a0c8d",
          "95f64b49450ff8565c443d28",
          "4cb04cfdbbd1d198135dd7e6",
          "0d85803ccbab267bf3a8883b",
          "61429111cbf79480977cc180",
          "7fd5b4047ecf1771e43a7b00",
          "5e33d3d0fe3d37269ac0a4ac",
          "ce2ce1395f9b0d91c1f5f688",
          "8e1bb408d94cbd25c5415ec3",
          "40482a1bb4bf42d8f32f4228",
          "2161466752788f9f7dea158a",
          "950bb4e33ad138bef7faa94e",
          "b34e31ebe33342cbb9ce2153",
          "9d73402b74c0e451d30cc541",
          "ca8cb242bf5d2060cfa3d6b9",
          "9cf99551238f8d0dc3098fa2",
          "854c1f762bb8a9c3703a0c5c",
          "1eb134b681e17cba5d52d39e",
          "8b65f6c5d267eee8f420cd52",
          "022b55ef8548abfd85b8a7bd",
          "8c5264a0d5f8e6bd010fc73c",
          "29c5d7c7f5019151c6aaf977",
          "2af31225f09a3b0c1ffb7d05",
          "29ffb226d5df3fcd92a6f5b5",
          "2272f51e4e2883a37830b683",
          "11840b5b8c8aa0163295821f",
          "2cd960c659a188a20c421f11",
          "e6d730f4e01bc41c950c1257",
          "a5d0a6c6783c22fdd8140baa",
          "03af824bd472db3a1913ad60",
          "abc21f55c9a5cbafdebeb21b",
          "8d3b4aa6af665032ef1814c4",
          "4896cee6bbd6c33fe1bc7503",
          "8724e54acfd7f30f1d485ff9",
          "c575eb75a99d0e50bf22d657",
          "1635d8cf5eff3f852777faea",
          "f517fc0442f14f4f817dd9c9",
          "34605bd9e88b1d04be687964",
          "947868b557af7e1f4673bf98",
          "5f1a3a88693bcbdeceb1f4d8",
          "8981fee2553c9dc9006c4405",
          "13936c1fdf6388220aaf4926",
          "78d671fceb394a389eedf9f4",
          "bc576dde8e90378ba20c3d7d",
          "03b8dd0b9b18121e80b03f2b",
          "897baeef51986e0e1f64a34e",
          "34f474e4a3d26c7364bad6f8",
          "b2e9fd342a5acc61c9024721",
          "e6ecfa1f7bc71395c5753aaf",
          "78f0542d4cb8b5acb2f647c9",
          "b3e180bf7b39a7b712d2af17",
          "9749393ea0a9be7e10809cd3",
          "20fe841986d0c487de1bb43e",
          "4f2503d1d42041f131f6c037",
          "27a8259465c6e16c5496c3c9",
          "87d99c52bdf8792ddf98e0b2",
          "dd855a5e062ff809cc6d9d68",
          "1c67ed09227b842ed902ba77",
          "f20582d45abfb5f774d857be",
          "4369ead7e3b7a8b602080909",
          "e7dfa63d745fa5ba98825f4e",
          "5f40734167ce9695bfe0cf96",
          "f58660a92cde28f39dd685f4",
          "2c5a8fb1c5640c6f83356515",
          "0005d0bc31750ca6fd41daad",
          "e35d39d717799fc965b5406f",
          "9a35afb63462835edb766159",
          "153f8d0d3b68f12050fea824",
          "4a25242b941af5b3bea4cee2",
          "5beaa2e7b59aab09c80a3a16",
          "23e13520de5b8a08ae303079",
          "87f3e551efa93992e5d96188",
          "323fa866f792c1efacb2ef44",
          "b533f097362c03cc103dbd52",
          "8332c1147b1f2485a3bedf9d",
          "6311fc7b77c034e99764825b",
          "a86bf9295e49096afdc4eb53",
          "0a45646cd62689407a960113"
        ],
        "validation": [
          "3ab86adc1cf5809981b916e9",
          "d401103d89846cc89423783c",
          "5be7082d7530c0ccaa7e992e",
          "3e48a552c813c6fef8023ac5",
          "4750e4595df200ad32f966a2",
          "2758ec32495b4d940f5801d9",
          "8c0695fa36d4aa62c73001a3",
          "f9910e7345c5228ca2426167",
          "212ae145d6f34ff2b52aad5c",
          "64dadd7f033ce50ef772dbad",
          "4b4f07befb68fcf68513b882",
          "168a5b7df46fabc6145494d6",
          "cfa8c7da202ccb74d2f4958a",
          "d3f3646b6037fc5cacb21404",
          "3562135a7c85ae2c97da635f",
          "a10f83fb19f5f802d457da20",
          "8790cf6ff49683f265c0ed99",
          "162167a2b83b8ec44dbcd08d",
          "702e38abad6481cf0e865398",
          "43922f1311d534f9503c00cb",
          "9fb0ca99605b59b816639fd7",
          "a70859a53b5d2026ce66f0ad",
          "bf13b25b59e82a323529af6c",
          "9d0efff0a81ba1fff0063cd6",
          "29623020579edea4ca41f253",
          "29999c372ca66f4c23007ab6",
          "60e3a3184bf26dc0e1ff1af2",
          "fc6c4827bd036a9f5c671e6e",
          "7cb5cf654365f98a9d26f01e",
          "e40649e2bae0ea0713fecaf1",
          "db6faa4ec00be63e9edc47e1",
          "4f0374a8502c289d4ac2966b"
        ]
      },
      "state_counts": {
        "id_test": 96,
        "ood_calibration": 96,
        "ood_parameters": 96,
        "ood_partition": 96,
        "train": 1536,
        "validation": 192
      },
      "status": "completed",
      "total_states": 2112,
      "total_worlds": 352,
      "unique_offline_observations": 100976,
      "wall_seconds": 464.7827464840375,
      "world_counts": {
        "id_test": 16,
        "ood_calibration": 16,
        "ood_parameters": 16,
        "ood_partition": 16,
        "train": 256,
        "validation": 32
      }
    },
    "data_audit": {
      "complete_world_split_disjoint": true,
      "cuts_rows_checked": 1536,
      "hidden_values_in_student_inputs": false,
      "rows_checked": 2112,
      "scope": "Source-backed legal-input and shape/data audit; no human/Natural validity or asymptotic proof.",
      "status": "PASS",
      "strict_nested_student_whitelist": true,
      "teacher_targets_observable_only": true,
      "wall_seconds": 0.8933167299255729
    },
    "gpu_jobs": 0,
    "model_api_calls": 0,
    "outer_cpu_seconds": 472.63214801900006,
    "outer_wall_seconds": 472.68680270342156,
    "preparation_engineering_restarts": 1,
    "prior_diagnostic_replay_actions": 516,
    "prior_failed_world_original_cost_unknown": true,
    "prior_known_smoke_actions": 128,
    "same_committed_world_plan": true,
    "scientific_fit_retries": 0,
    "smoke": {
      "gpu_jobs": 0,
      "model_api_calls": 0,
      "optimizer_updates": 0,
      "scope": "random-initialized neural forward only; interface check, not trained policy evidence",
      "status": "passed",
      "wall_seconds": 0.3342971676029265,
      "worlds": [
        {
          "costs": {
            "offline": 0,
            "task": 57,
            "type": 7
          },
          "gate_certified": false,
          "online": 64,
          "weights_valid": true,
          "world_id": "15d30027bc937169999aaed8"
        },
        {
          "costs": {
            "offline": 0,
            "task": 52,
            "type": 12
          },
          "gate_certified": false,
          "online": 64,
          "weights_valid": true,
          "world_id": "f23240117b5465262629aca9"
        }
      ]
    },
    "status": "completed"
  },
  "training_execution": {
    "data_loading_wall_seconds": 0.7280707592144608,
    "gpu_jobs": 0,
    "models": {
      "deepsets_info": {
        "checkpoint_sha256": "6b94ace8e4cd2c494222aab43c2d999ddc695ddbdaa4e5d18356a8b7013d7f00",
        "inner_receipt": {
          "batch_size": 64,
          "checkpoint_count": 1,
          "deterministic_algorithms": true,
          "device": "cpu",
          "elapsed_seconds": 10.395080952905118,
          "feature_version": "t2_observable_features_v1",
          "final_batch": {
            "finite_cut_positive_regret": 0.07633481919765472,
            "kl": 0.0507114939391613,
            "loss": 0.12704631686210632
          },
          "implementation_sha256": "6d38b8e05d24317c184ab0d920aea37fe583cb4a884aac5e6cb820b4f1603ba9",
          "information_regret_weight": 1.0,
          "information_surrogate": "finite-cut radial lower approximation with exact max subgradient",
          "initial_state_sha256": "23f1271bbc0b9bb708114b652b2341951bcdb2fb70950b73cafed705d1624b1b",
          "kind": "deepsets_info",
          "learning_rate": 0.001,
          "normalization": "fixed_observable_transforms",
          "objective": "KL(teacher||student) + relu(K_cut(student)/K_teacher-1)",
          "optimizer": "Adam",
          "parameter_count": 12899,
          "progress": [
            {
              "finite_cut_positive_regret": 0.9823871850967407,
              "kl": 0.6828049421310425,
              "loss": 1.6651921272277832,
              "step": 1
            },
            {
              "finite_cut_positive_regret": 0.6721671223640442,
              "kl": 0.6470968127250671,
              "loss": 1.3192639350891113,
              "step": 25
            },
            {
              "finite_cut_positive_regret": 0.6458441615104675,
              "kl": 0.5550264120101929,
              "loss": 1.2008705139160156,
              "step": 50
            },
            {
              "finite_cut_positive_regret": 0.27078455686569214,
              "kl": 0.2316497564315796,
              "loss": 0.5024343132972717,
              "step": 75
            },
            {
              "finite_cut_positive_regret": 0.18493632972240448,
              "kl": 0.09150489419698715,
              "loss": 0.27644121646881104,
              "step": 100
            },
            {
              "finite_cut_positive_regret": 0.14209036529064178,
              "kl": 0.0581536740064621,
              "loss": 0.20024403929710388,
              "step": 125
            },
            {
              "finite_cut_positive_regret": 0.1092362105846405,
              "kl": 0.05161341652274132,
              "loss": 0.16084963083267212,
              "step": 150
            },
            {
              "finite_cut_positive_regret": 0.08337040990591049,
              "kl": 0.0461462028324604,
              "loss": 0.1295166164636612,
              "step": 175
            },
            {
              "finite_cut_positive_regret": 0.08124183863401413,
              "kl": 0.04935389757156372,
              "loss": 0.13059574365615845,
              "step": 200
            },
            {
              "finite_cut_positive_regret": 0.08761657029390335,
              "kl": 0.037849266082048416,
              "loss": 0.12546584010124207,
              "step": 225
            },
            {
              "finite_cut_positive_regret": 0.08434682339429855,
              "kl": 0.035469114780426025,
              "loss": 0.11981593817472458,
              "step": 250
            },
            {
              "finite_cut_positive_regret": 0.06820331513881683,
              "kl": 0.04459015280008316,
              "loss": 0.1127934679389,
              "step": 275
            },
            {
              "finite_cut_positive_regret": 0.09130966663360596,
              "kl": 0.040033306926488876,
              "loss": 0.13134297728538513,
              "step": 300
            },
            {
              "finite_cut_positive_regret": 0.0979456827044487,
              "kl": 0.05214345082640648,
              "loss": 0.15008912980556488,
              "step": 325
            },
            {
              "finite_cut_positive_regret": 0.07877829670906067,
              "kl": 0.036430101841688156,
              "loss": 0.11520840227603912,
              "step": 350
            },
            {
              "finite_cut_positive_regret": 0.06844810396432877,
              "kl": 0.03555043041706085,
              "loss": 0.10399853438138962,
              "step": 375
            },
            {
              "finite_cut_positive_regret": 0.07633481919765472,
              "kl": 0.0507114939391613,
              "loss": 0.12704631686210632,
              "step": 400
            }
          ],
          "radial_denominator_floor": 1e-10,
          "seed": 731101,
          "selection": "none; final checkpoint only",
          "steps": 400,
          "torch_threads": 1,
          "torch_version": "2.6.0+cu124",
          "training_payload_sha256": "07a2f12d09461bed32144c67363786b9af567d2d0d26c3d29f9a2549692a42e6",
          "training_rows": 1536,
          "uses_hidden_parameters": false,
          "validation_used": false,
          "width": 32
        },
        "outer_cpu_seconds": 11.059857627000001,
        "outer_wall_seconds": 11.060162294656038
      },
      "deepsets_kl": {
        "checkpoint_sha256": "ea40326419d19e037b89cfc970d937b4c41cd71358934d1872560f96dd892422",
        "inner_receipt": {
          "batch_size": 64,
          "checkpoint_count": 1,
          "deterministic_algorithms": true,
          "device": "cpu",
          "elapsed_seconds": 4.301012752112001,
          "feature_version": "t2_observable_features_v1",
          "final_batch": {
            "finite_cut_positive_regret": 0.0,
            "kl": 0.04118245840072632,
            "loss": 0.04118245840072632
          },
          "implementation_sha256": "6d38b8e05d24317c184ab0d920aea37fe583cb4a884aac5e6cb820b4f1603ba9",
          "information_regret_weight": 0.0,
          "information_surrogate": "finite-cut radial lower approximation with exact max subgradient",
          "initial_state_sha256": "23f1271bbc0b9bb708114b652b2341951bcdb2fb70950b73cafed705d1624b1b",
          "kind": "deepsets_kl",
          "learning_rate": 0.001,
          "normalization": "fixed_observable_transforms",
          "objective": "KL(teacher||student)",
          "optimizer": "Adam",
          "parameter_count": 12899,
          "progress": [
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.6828049421310425,
              "loss": 0.6828049421310425,
              "step": 1
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.6080100536346436,
              "loss": 0.6080100536346436,
              "step": 25
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.4550062119960785,
              "loss": 0.4550062119960785,
              "step": 50
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.12458387017250061,
              "loss": 0.12458387017250061,
              "step": 75
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.08313938975334167,
              "loss": 0.08313938975334167,
              "step": 100
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.05713493004441261,
              "loss": 0.05713493004441261,
              "step": 125
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.053684595972299576,
              "loss": 0.053684595972299576,
              "step": 150
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.049727167934179306,
              "loss": 0.049727167934179306,
              "step": 175
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.05003975331783295,
              "loss": 0.05003975331783295,
              "step": 200
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.03203559294342995,
              "loss": 0.03203559294342995,
              "step": 225
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.031803544610738754,
              "loss": 0.031803544610738754,
              "step": 250
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.04330768063664436,
              "loss": 0.04330768063664436,
              "step": 275
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.039297815412282944,
              "loss": 0.039297815412282944,
              "step": 300
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.048607561737298965,
              "loss": 0.048607561737298965,
              "step": 325
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.03204663470387459,
              "loss": 0.03204663470387459,
              "step": 350
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.031125836074352264,
              "loss": 0.031125836074352264,
              "step": 375
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.04118245840072632,
              "loss": 0.04118245840072632,
              "step": 400
            }
          ],
          "radial_denominator_floor": 1e-10,
          "seed": 731101,
          "selection": "none; final checkpoint only",
          "steps": 400,
          "torch_threads": 1,
          "torch_version": "2.6.0+cu124",
          "training_payload_sha256": "139caf824341b274d6d9889a71d5166a0d19dde0186a016324ad56296e37a0cc",
          "training_rows": 1536,
          "uses_hidden_parameters": false,
          "validation_used": false,
          "width": 32
        },
        "outer_cpu_seconds": 4.783507060999999,
        "outer_wall_seconds": 4.7837437321431935
      },
      "mlp": {
        "checkpoint_sha256": "72ef2235b02c5b55c63214e58cd6e2d89e7a87971bde49b8420d931b3ac67730",
        "inner_receipt": {
          "batch_size": 64,
          "checkpoint_count": 1,
          "deterministic_algorithms": true,
          "device": "cpu",
          "elapsed_seconds": 3.1586560108698905,
          "feature_version": "t2_observable_features_v1",
          "final_batch": {
            "finite_cut_positive_regret": 0.0,
            "kl": 0.020240426063537598,
            "loss": 0.020240426063537598
          },
          "implementation_sha256": "6d38b8e05d24317c184ab0d920aea37fe583cb4a884aac5e6cb820b4f1603ba9",
          "information_regret_weight": 0.0,
          "information_surrogate": "finite-cut radial lower approximation with exact max subgradient",
          "initial_state_sha256": "c4de864ea905f675be0793496acbb8037e9f4acabfb9f3028e979f7be35d9879",
          "kind": "mlp",
          "learning_rate": 0.001,
          "normalization": "training_rows_only",
          "objective": "KL(teacher||student)",
          "optimizer": "Adam",
          "parameter_count": 4778,
          "progress": [
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.694568932056427,
              "loss": 0.694568932056427,
              "step": 1
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.6166149973869324,
              "loss": 0.6166149973869324,
              "step": 25
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.48200875520706177,
              "loss": 0.48200875520706177,
              "step": 50
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.27575045824050903,
              "loss": 0.27575045824050903,
              "step": 75
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.14498132467269897,
              "loss": 0.14498132467269897,
              "step": 100
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.09686417877674103,
              "loss": 0.09686417877674103,
              "step": 125
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.06442034244537354,
              "loss": 0.06442034244537354,
              "step": 150
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.03886139765381813,
              "loss": 0.03886139765381813,
              "step": 175
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.0326128825545311,
              "loss": 0.0326128825545311,
              "step": 200
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.02370697259902954,
              "loss": 0.02370697259902954,
              "step": 225
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.019338853657245636,
              "loss": 0.019338853657245636,
              "step": 250
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.024646418169140816,
              "loss": 0.024646418169140816,
              "step": 275
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.018449855968356133,
              "loss": 0.018449855968356133,
              "step": 300
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.020586416125297546,
              "loss": 0.020586416125297546,
              "step": 325
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.01786840707063675,
              "loss": 0.01786840707063675,
              "step": 350
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.013371825218200684,
              "loss": 0.013371825218200684,
              "step": 375
            },
            {
              "finite_cut_positive_regret": 0.0,
              "kl": 0.020240426063537598,
              "loss": 0.020240426063537598,
              "step": 400
            }
          ],
          "radial_denominator_floor": 1e-10,
          "seed": 731101,
          "selection": "none; final checkpoint only",
          "steps": 400,
          "torch_threads": 1,
          "torch_version": "2.6.0+cu124",
          "training_payload_sha256": "139caf824341b274d6d9889a71d5166a0d19dde0186a016324ad56296e37a0cc",
          "training_rows": 1536,
          "uses_hidden_parameters": false,
          "validation_used": false,
          "width": 32
        },
        "outer_cpu_seconds": 4.508064491999999,
        "outer_wall_seconds": 4.5112195941619575
      }
    },
    "outer_cpu_seconds": 21.082695242,
    "outer_wall_seconds": 21.0864048730582,
    "qwen_calls": 0,
    "scientific_retries": 0,
    "status": "completed"
  }
}
```

T1-MLP is the frozen historical reference, not an additional T2 fit. T2-MLP, DeepSets-KL and DeepSets-Info are the three new fixed final-checkpoint fits. Per-state inference latency is reported with the exact allocation-quality table and matched-d4 denominators in T2_EVALUATION.md.

## Final accounting qualifications and retained earlier costs

All acquisition below is simulator observation generation or per-policy charging, not Qwen/API/human queries. There were zero Qwen calls, paid-provider calls, GPU jobs, RL runs or confirmation runs in T2.

| Completed v02 stage | Online simulator actions / path charges | Offline observations / path charges | Meaning |
|---|---:|---:|---|
| Repeated technical smoke | 128 | 0 | Two interface worlds, not fitted-policy evidence |
| Teacher-data generation | 360,448 | 100,976 | One actual calibration sample set per data world; 352 worlds |
| Separate teacher-only budget development | 2,304 | 3,072 | 18 paths; costs retained although budget selection is outside final evaluation |
| Closed-loop evaluation | 1,504,320 | 209,824 | Sum across all 852 applicable policy paths; 1,358,062 task plus 146,258 type actions |

Evaluation offline charges deliberately count each comparator's calibration access. Paired methods and repeated R use coupled potential streams, so the sum of path charges is not a count of unique independently sampled offline observations. The offline allocation evaluation uses saved observable states and introduces no further user/environment observations.

Before v02 there were 128 known initial smoke actions and 516 known actions in one explicitly recorded technical diagnostic replay of the same committed world. The original interrupted world's actual prefix cost was not saved and remains **unknown**. Those known earlier charges are additional to v02; neither the replay's 516 actions nor zero may substitute for the unknown original prefix. The initial attempt and its receipt remain immutable. Accordingly, there is no complete known total-project acquisition or runtime figure.

Completed v02 outer stage wall timers are preparation **472.686803 s**, three fits **21.086405 s**, evaluation **1,007.373356 s**, analysis **7.105815 s**. Preparation/fitting CPU are 472.632148/21.082695 s. Evaluation's 14.064821 s CPU is **parent only**, excluding the two worker processes. Worker cold model-load wall/CPU seconds are 1.373261/1.363064 and 1.419149/1.413873; parent cold model loading is 1.377622 s wall. Per-path wall/CPU and individual computation, GLR, certification and environment components are in the tables/raw records above.

Outer timers start after module imports and initial freeze verification. They are not complete interpreter start-to-exit or full-project accounting. Individual model fitting, data generation, budget development and path components nest inside their corresponding outer totals; do not add them a second time. Parent CPU plus recorded path CPU is also not asserted to account for all worker startup, serialization and process-management CPU. No GPU kernel or energy accounting applies.

Two workers and single-thread numerical kernels were fixed. Timings measure this host/software workload and are descriptive; they are not a randomized hardware benchmark. Per-state neural inference excludes already-computed posterior estimation, whereas the headline inclusive online speedup includes estimation, planning and inference. Cold loading, teacher-data construction, fitting, analysis, scientific review and the earlier failed attempt are not included in that online speedup. No deployment break-even denominator was predeclared, so no net amortized training-cost advantage is claimed.
