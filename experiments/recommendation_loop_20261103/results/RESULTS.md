# Bounded recommendation-loop development results

40 trajectories; 8 paired worlds; 4 profile clusters. Four worlds are theory anchors.

| Arm | Certified | Capped | Failed | Wrong certified | Mean capped cost | Mean policy seconds |
|---|---:|---:|---:|---:|---:|---:|
| round_robin | 8/8 | 0 | 0 | 0 | 542.00 | 0.008 |
| joint_dr_rc | 8/8 | 0 | 0 | 0 | 341.38 | 0.017 |
| decision_ig | 8/8 | 0 | 0 | 0 | 397.88 | 0.268 |
| profile_kl | 8/8 | 0 | 0 | 0 | 353.12 | 1.269 |
| decision_kl | 8/8 | 0 | 0 | 0 | 243.00 | 1.290 |

Noncertified and failed trajectories receive the cap in this restricted-cost column; this is not their completed stopping time.

| World | RR | Joint D-RRC | Decision IG | Profile KL | Decision KL |
|---|---:|---:|---:|---:|---:|
| weighted_two__anchor_all_positive__partition0 | 422 | 221 | 63 | 221 | 64 |
| weighted_two__anchor_all_positive__partition1 | 453 | 346 | 294 | 361 | 327 |
| weighted_two__seeded_independent__partition0 | 336 | 157 | 136 | 157 | 145 |
| weighted_two__seeded_independent__partition1 | 263 | 188 | 111 | 148 | 89 |
| asymmetric_three__anchor_all_positive__partition0 | 351 | 214 | 366 | 209 | 253 |
| asymmetric_three__anchor_all_positive__partition1 | 444 | 440 | 480 | 520 | 322 |
| asymmetric_three__seeded_independent__partition0 | 988 | 528 | 988 | 528 | 252 |
| asymmetric_three__seeded_independent__partition1 | 1079 | 637 | 745 | 681 | 492 |

C=capped without certificate; F=failed. No trajectory was replaced.

All arms share the same screened/checkpoint interval gate, action set, iid channel and paired action-indexed streams.
The gate may certify later than the ideal earliest GLR crossing. Fixed-tolerance allocation and quadrature are not certified asymptotic-optimality implementations.
These results do not establish real-user reliability, universal superiority or a final method choice.
