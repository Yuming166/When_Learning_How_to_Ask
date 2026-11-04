# Decision Value bridge results

264 trajectories: 257 certified, 0 capped, 7 failed, 0 wrong certified.

| Cell | R | Arm | Certified | Mean restricted queries | 95% conditional interval |
|---|---:|---|---:|---:|---|
| weighted5_zero | 3 | decision_value | 6/6 | 434.17 | [380.0, 493.3333333333333] |
| weighted5_zero | 3 | decision_kl | 5/6 | 589.33 | [180.66666666666666, 1367.5] |
| weighted5_zero | 3 | decision_ig | 6/6 | 186.33 | [147.5, 224.0] |
| weighted5_zero | 3 | round_robin | 6/6 | 434.17 | [380.0, 493.3333333333333] |
| weighted5_zero | 9 | decision_value | 6/6 | 560.67 | [498.5, 620.5] |
| weighted5_zero | 9 | decision_kl | 5/6 | 625.50 | [222.5, 1385.6666666666667] |
| weighted5_zero | 9 | decision_ig | 6/6 | 250.00 | [205.0, 295.3374999999999] |
| weighted5_zero | 9 | round_robin | 6/6 | 560.67 | [498.5, 620.5] |
| weighted5_positive | 3 | decision_value | 6/6 | 395.00 | [330.0, 452.6666666666667] |
| weighted5_positive | 3 | decision_kl | 5/6 | 595.33 | [171.83333333333334, 1367.5] |
| weighted5_positive | 3 | decision_ig | 6/6 | 240.67 | [181.66666666666666, 303.0] |
| weighted5_positive | 3 | round_robin | 6/6 | 395.00 | [330.0, 452.6666666666667] |
| weighted5_positive | 9 | decision_value | 6/6 | 483.67 | [416.3333333333333, 548.8333333333334] |
| weighted5_positive | 9 | decision_kl | 5/6 | 631.33 | [222.16666666666666, 1387.6666666666667] |
| weighted5_positive | 9 | decision_ig | 6/6 | 272.00 | [209.16666666666666, 341.3333333333333] |
| weighted5_positive | 9 | round_robin | 6/6 | 483.67 | [416.3333333333333, 548.8333333333334] |
| genuine6_zero | 3 | decision_value | 6/6 | 543.50 | [462.1666666666667, 620.5] |
| genuine6_zero | 3 | decision_kl | 6/6 | 257.50 | [199.33333333333334, 313.6666666666667] |
| genuine6_zero | 3 | decision_ig | 6/6 | 228.50 | [187.0, 270.8333333333333] |
| genuine6_zero | 3 | round_robin | 6/6 | 543.50 | [462.1666666666667, 620.5] |
| genuine6_zero | 9 | decision_value | 6/6 | 628.67 | [580.3333333333334, 691.0] |
| genuine6_zero | 9 | decision_kl | 6/6 | 290.17 | [232.16666666666666, 342.5] |
| genuine6_zero | 9 | decision_ig | 6/6 | 273.67 | [228.66666666666666, 314.5] |
| genuine6_zero | 9 | round_robin | 6/6 | 628.67 | [580.3333333333334, 691.0] |
| genuine6_positive | 3 | decision_value | 6/6 | 620.00 | [566.8333333333334, 687.0] |
| genuine6_positive | 3 | decision_kl | 5/6 | 840.17 | [473.1666666666667, 1510.8333333333333] |
| genuine6_positive | 3 | decision_ig | 6/6 | 385.17 | [326.6666666666667, 449.0166666666664] |
| genuine6_positive | 3 | round_robin | 6/6 | 620.00 | [566.8333333333334, 687.0] |
| genuine6_positive | 9 | decision_value | 6/6 | 698.83 | [658.8333333333334, 764.5] |
| genuine6_positive | 9 | decision_kl | 5/6 | 888.00 | [532.0, 1540.6666666666667] |
| genuine6_positive | 9 | decision_ig | 6/6 | 503.67 | [466.1666666666667, 538.0] |
| genuine6_positive | 9 | round_robin | 6/6 | 698.83 | [658.8333333333334, 764.5] |
| weighted5_zero_allB | 9 | decision_value | 6/6 | 536.33 | [420.3333333333333, 649.5] |
| weighted5_zero_allB | 9 | decision_kl | 5/6 | 542.50 | [132.83333333333334, 1331.5] |
| weighted5_zero_allB | 9 | decision_ig | 6/6 | 150.83 | [132.16666666666666, 175.5] |
| weighted5_zero_allB | 9 | round_robin | 6/6 | 536.33 | [420.3333333333333, 649.5] |
| weighted5_positive_mixed01 | 9 | decision_value | 6/6 | 448.67 | [372.5, 526.1666666666666] |
| weighted5_positive_mixed01 | 9 | decision_kl | 6/6 | 194.50 | [140.16666666666666, 264.6666666666667] |
| weighted5_positive_mixed01 | 9 | decision_ig | 6/6 | 215.17 | [142.66666666666666, 300.1666666666667] |
| weighted5_positive_mixed01 | 9 | round_robin | 6/6 | 448.67 | [372.5, 526.1666666666666] |
| genuine6_positive_mixed10 | 9 | decision_value | 6/6 | 703.67 | [595.6666666666666, 798.8333333333334] |
| genuine6_positive_mixed10 | 9 | decision_kl | 6/6 | 509.17 | [457.3333333333333, 574.5] |
| genuine6_positive_mixed10 | 9 | decision_ig | 6/6 | 454.17 | [414.8333333333333, 493.0] |
| genuine6_positive_mixed10 | 9 | round_robin | 6/6 | 703.67 | [595.6666666666666, 798.8333333333334] |

Positive cost contrasts favor DV. Anchor and type-audit outcomes remain separate; pooled values weight catalogues equally and cells equally within each catalogue.

| Track | R | Baseline | Baseline minus DV | 95% paired cluster interval |
|---|---:|---|---:|---|
| anchor | 3 | decision_kl | 72.42 | [-188.62604166666665, 353.9583333333333] |
| anchor | 3 | decision_ig | -238.00 | [-278.16666666666663, -198.165625] |
| anchor | 3 | round_robin | 0.00 | [0.0, 0.0] |
| anchor | 9 | decision_kl | 15.79 | [-253.21354166666666, 305.9604166666667] |
| anchor | 9 | decision_ig | -268.12 | [-303.7927083333333, -236.29166666666669] |
| anchor | 9 | round_robin | 0.00 | [0.0, 0.0] |
| type_audit | 9 | decision_kl | -159.25 | [-302.4614583333333, 42.334374999999994] |
| type_audit | 9 | decision_ig | -279.50 | [-343.5427083333333, -220.78958333333335] |
| type_audit | 9 | round_robin | 0.00 | [0.0, 0.0] |

## Fixed-budget common posterior-MAP readout

These are complete-denominator counts. Uncertified guesses are not certificates; certified outputs are carried forward.

| Track | R | Budget | Arm | Correct/attempted | Certified | Carried |
|---|---:|---:|---|---:|---:|---:|
| anchor | 3 | 25 | decision_value | 22/24 | 0 | 0 |
| anchor | 3 | 25 | decision_kl | 21/24 | 0 | 0 |
| anchor | 3 | 25 | decision_ig | 22/24 | 0 | 0 |
| anchor | 3 | 25 | round_robin | 22/24 | 0 | 0 |
| anchor | 3 | 50 | decision_value | 24/24 | 0 | 0 |
| anchor | 3 | 50 | decision_kl | 24/24 | 0 | 0 |
| anchor | 3 | 50 | decision_ig | 24/24 | 0 | 0 |
| anchor | 3 | 50 | round_robin | 24/24 | 0 | 0 |
| anchor | 3 | 100 | decision_value | 24/24 | 0 | 0 |
| anchor | 3 | 100 | decision_kl | 22/24 | 0 | 0 |
| anchor | 3 | 100 | decision_ig | 24/24 | 0 | 0 |
| anchor | 3 | 100 | round_robin | 24/24 | 0 | 0 |
| anchor | 3 | 200 | decision_value | 24/24 | 0 | 0 |
| anchor | 3 | 200 | decision_kl | 22/24 | 7 | 7 |
| anchor | 3 | 200 | decision_ig | 24/24 | 10 | 10 |
| anchor | 3 | 200 | round_robin | 24/24 | 0 | 0 |
| anchor | 9 | 25 | decision_value | 22/24 | 0 | 0 |
| anchor | 9 | 25 | decision_kl | 21/24 | 0 | 0 |
| anchor | 9 | 25 | decision_ig | 22/24 | 0 | 0 |
| anchor | 9 | 25 | round_robin | 22/24 | 0 | 0 |
| anchor | 9 | 50 | decision_value | 24/24 | 0 | 0 |
| anchor | 9 | 50 | decision_kl | 24/24 | 0 | 0 |
| anchor | 9 | 50 | decision_ig | 24/24 | 0 | 0 |
| anchor | 9 | 50 | round_robin | 24/24 | 0 | 0 |
| anchor | 9 | 100 | decision_value | 24/24 | 0 | 0 |
| anchor | 9 | 100 | decision_kl | 22/24 | 0 | 0 |
| anchor | 9 | 100 | decision_ig | 24/24 | 0 | 0 |
| anchor | 9 | 100 | round_robin | 24/24 | 0 | 0 |
| anchor | 9 | 200 | decision_value | 24/24 | 0 | 0 |
| anchor | 9 | 200 | decision_kl | 22/24 | 3 | 3 |
| anchor | 9 | 200 | decision_ig | 24/24 | 4 | 4 |
| anchor | 9 | 200 | round_robin | 24/24 | 0 | 0 |
| type_audit | 9 | 25 | decision_value | 17/18 | 0 | 0 |
| type_audit | 9 | 25 | decision_kl | 18/18 | 0 | 0 |
| type_audit | 9 | 25 | decision_ig | 17/18 | 0 | 0 |
| type_audit | 9 | 25 | round_robin | 17/18 | 0 | 0 |
| type_audit | 9 | 50 | decision_value | 17/18 | 0 | 0 |
| type_audit | 9 | 50 | decision_kl | 18/18 | 0 | 0 |
| type_audit | 9 | 50 | decision_ig | 18/18 | 0 | 0 |
| type_audit | 9 | 50 | round_robin | 17/18 | 0 | 0 |
| type_audit | 9 | 100 | decision_value | 18/18 | 0 | 0 |
| type_audit | 9 | 100 | decision_kl | 18/18 | 0 | 0 |
| type_audit | 9 | 100 | decision_ig | 18/18 | 1 | 1 |
| type_audit | 9 | 100 | round_robin | 18/18 | 0 | 0 |
| type_audit | 9 | 200 | decision_value | 18/18 | 0 | 0 |
| type_audit | 9 | 200 | decision_kl | 17/18 | 8 | 8 |
| type_audit | 9 | 200 | decision_ig | 18/18 | 9 | 9 |
| type_audit | 9 | 200 | round_robin | 18/18 | 0 | 0 |

## Limits

Decision Value is a one-step VOI instantiation with Q6 approximate joint belief, not a new VOI principle or an asymptotically optimal allocator. Exact GLR certification is inherited and independent of posterior scoring. Six seeds per fixed catalogue give limited uncertainty resolution; there are 12 response-tape clusters, not 264 independent users. Two all-positive constructed preference profiles, at most two groups, known partitions and iid rates remain substantial constraints. Type reversal/mixing is a bounded audit. No empirical oracle or unknown-versus-known-type premium is estimated. Full vectors, adaptive replay, failures, zero-gain counts, fixed-budget records and runtimes are retained in analysis.json.
