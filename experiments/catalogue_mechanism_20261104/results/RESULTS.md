# Controlled catalogue-mechanism validation

144 frozen trajectories; 142 certified; 0 capped; 2 failed; 0 wrong certified.

| Cell | R | Arm | Certified | Capped | Failed | Mean restricted queries | 95% tape-bootstrap interval |
|---|---:|---|---:|---:|---:|---:|---|
| weighted5_zero | 3 | decision_kl | 6/6 | 0 | 0 | 182.33 | [136.83, 233.83] |
| weighted5_zero | 3 | decision_ig | 6/6 | 0 | 0 | 224.67 | [144.00, 310.83] |
| weighted5_zero | 3 | round_robin | 6/6 | 0 | 0 | 533.33 | [441.33, 625.33] |
| weighted5_zero | 9 | decision_kl | 6/6 | 0 | 0 | 227.67 | [183.17, 269.00] |
| weighted5_zero | 9 | decision_ig | 6/6 | 0 | 0 | 295.17 | [219.33, 392.00] |
| weighted5_zero | 9 | round_robin | 6/6 | 0 | 0 | 581.33 | [490.83, 671.00] |
| weighted5_positive | 3 | decision_kl | 6/6 | 0 | 0 | 222.00 | [192.50, 259.50] |
| weighted5_positive | 3 | decision_ig | 6/6 | 0 | 0 | 235.00 | [210.50, 265.00] |
| weighted5_positive | 3 | round_robin | 6/6 | 0 | 0 | 449.67 | [389.83, 522.00] |
| weighted5_positive | 9 | decision_kl | 6/6 | 0 | 0 | 258.17 | [220.67, 298.00] |
| weighted5_positive | 9 | decision_ig | 6/6 | 0 | 0 | 267.17 | [237.17, 302.00] |
| weighted5_positive | 9 | round_robin | 6/6 | 0 | 0 | 534.33 | [453.50, 615.50] |
| genuine6_zero | 3 | decision_kl | 6/6 | 0 | 0 | 232.17 | [184.00, 268.67] |
| genuine6_zero | 3 | decision_ig | 6/6 | 0 | 0 | 189.83 | [153.83, 223.67] |
| genuine6_zero | 3 | round_robin | 6/6 | 0 | 0 | 443.50 | [357.83, 505.83] |
| genuine6_zero | 9 | decision_kl | 6/6 | 0 | 0 | 264.00 | [210.00, 304.00] |
| genuine6_zero | 9 | decision_ig | 6/6 | 0 | 0 | 216.67 | [174.83, 257.33] |
| genuine6_zero | 9 | round_robin | 6/6 | 0 | 0 | 536.17 | [447.00, 613.06] |
| genuine6_positive | 3 | decision_kl | 5/6 | 0 | 1 | 694.83 | [273.00, 1435.83] |
| genuine6_positive | 3 | decision_ig | 6/6 | 0 | 0 | 308.83 | [254.33, 358.33] |
| genuine6_positive | 3 | round_robin | 6/6 | 0 | 0 | 513.17 | [418.00, 585.00] |
| genuine6_positive | 9 | decision_kl | 5/6 | 0 | 1 | 758.67 | [345.67, 1465.29] |
| genuine6_positive | 9 | decision_ig | 6/6 | 0 | 0 | 382.33 | [322.17, 439.33] |
| genuine6_positive | 9 | round_robin | 6/6 | 0 | 0 | 588.33 | [490.50, 668.83] |

Restricted query cost assigns the full cap to noncertified and failed paths; these are not completed stopping times.

## Matched partition contrasts

Positive-premium minus zero-premium cost on the same response tapes:

| Catalogue | R | Arm | Mean difference | 95% interval |
|---|---:|---|---:|---|
| weighted5 | 3 | decision_kl | 39.67 | [-3.83, 75.83] |
| weighted5 | 3 | decision_ig | 10.33 | [-67.50, 69.83] |
| weighted5 | 3 | round_robin | -83.67 | [-140.50, -31.67] |
| weighted5 | 9 | decision_kl | 30.50 | [-8.50, 69.50] |
| weighted5 | 9 | decision_ig | -28.00 | [-117.83, 35.00] |
| weighted5 | 9 | round_robin | -47.00 | [-67.50, -25.00] |
| genuine6 | 3 | decision_kl | 462.67 | [74.33, 1185.17] |
| genuine6 | 3 | decision_ig | 119.00 | [92.33, 143.33] |
| genuine6 | 3 | round_robin | 69.67 | [46.50, 100.33] |
| genuine6 | 9 | decision_kl | 494.67 | [127.17, 1189.17] |
| genuine6 | 9 | decision_ig | 165.67 | [143.50, 187.50] |
| genuine6 | 9 | round_robin | 52.17 | [26.33, 75.00] |

## Paired policy comparisons

Positive values favor KL. Pooling weights both catalogues and their partitions equally.

| R | Baseline | Mean baseline minus KL | 95% clustered interval |
|---:|---|---:|---|
| 3 | decision_ig | -93.25 | [-280.08, 10.13] |
| 3 | round_robin | 152.08 | [-16.71, 252.42] |
| 9 | decision_ig | -86.79 | [-271.21, 17.58] |
| 9 | round_robin | 182.92 | [23.25, 280.25] |

## Interpretation limits

Only two fixed all-positive theory-anchor profiles were tested. Bootstrap uncertainty concerns iid response tapes conditional on these anchors. Six seeds per catalogue provide limited uncertainty resolution.
Every group has true better format A. This isolates sharing structure, but a fixed-A baseline would be a trivial strong alternative in these particular controlled states. The benchmark does not establish natural latent reliability discovery or broad method superiority.
The zero/positive label describes an asymptotic unknown-type versus known-type coefficient premium. No empirical known-type oracle was run; a finite positive-minus-zero partition contrast is a mechanism diagnostic, not a direct estimator or proof of that premium.
The KL allocator uses finite-tolerance continuous optimization and IG uses order-6 quadrature. Common delayed exact stopping certifies individual decisions under the iid channel; it does not establish algorithmic optimality, SOTA performance, human realism, or an earliest stopping time.
Raw answers, complete failures, paired seed vectors, interval methods, and runtimes are retained. No path was replaced, retried, filtered, or used to tune a method.
