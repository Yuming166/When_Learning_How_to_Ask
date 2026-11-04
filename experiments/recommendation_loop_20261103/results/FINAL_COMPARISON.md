# Final development comparison, including baseline repair

Primary: 40 trajectories on eight worlds. Repair: eight additional trajectories on the SAME worlds.
Four constructed profile clusters; half the worlds are theory anchors. No confirmation sample.

| Arm | Certified | Capped / failed / wrong certified | Mean queries | Policy CPU seconds | Total CPU seconds |
|---|---:|---:|---:|---:|---:|
| round_robin | 8/8 | 0 / 0 / 0 | 542.000 | 0.0084 | 0.5224 |
| joint_dr_rc | 8/8 | 0 / 0 / 0 | 341.375 | 0.0175 | 0.4335 |
| decision_ig_relative_repair | 8/8 | 0 / 0 / 0 | 237.500 | 0.1323 | 0.3889 |
| profile_kl | 8/8 | 0 / 0 / 0 | 353.125 | 1.2691 | 1.6387 |
| decision_kl | 8/8 | 0 / 0 / 0 | 243.000 | 1.2896 | 1.5938 |

All paths certified, so restricted query cost equals observed stopping time in this table.
The original IG mean was 397.875; its absolute tie threshold was numerically unsuitable.
Only its tie rule was repaired; the original records and all Decision KL results remain unchanged.

| World | RR | Joint D-RRC | IG original | IG repaired | Profile KL | Decision KL |
|---|---:|---:|---:|---:|---:|---:|
| weighted_two__anchor_all_positive__partition0 | 422 | 221 | 63 | 63 | 221 | 64 |
| weighted_two__anchor_all_positive__partition1 | 453 | 346 | 294 | 302 | 361 | 327 |
| weighted_two__seeded_independent__partition0 | 336 | 157 | 136 | 136 | 157 | 145 |
| weighted_two__seeded_independent__partition1 | 263 | 188 | 111 | 111 | 148 | 89 |
| asymmetric_three__anchor_all_positive__partition0 | 351 | 214 | 366 | 213 | 209 | 253 |
| asymmetric_three__anchor_all_positive__partition1 | 444 | 440 | 480 | 351 | 520 | 322 |
| asymmetric_three__seeded_independent__partition0 | 988 | 528 | 988 | 250 | 528 | 252 |
| asymmetric_three__seeded_independent__partition1 | 1079 | 637 | 745 | 474 | 681 | 492 |

Decision KL vs repaired IG: 2 lower-cost / 0 tied / 6 higher-cost worlds;
mean cost 243 vs 237.5, i.e. Decision KL uses 2.32% more queries descriptively.
Both catalogue strata also have a higher Decision KL mean than repaired IG.
No universal ranking, real-user validity, asymptotic efficiency or empirical risk guarantee is established.
