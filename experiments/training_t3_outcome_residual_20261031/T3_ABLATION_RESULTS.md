# T3 ablation results

## Material Passport

One bounded development pilot; all192 TEST worlds are independent of TRAIN/DEV and were opened after weight hashes and DEV selection. These are heldout development tests, not independent confirmation.

DEV-selected Joint: **Learned-Joint-7102**. DEV-selected strongest frozen comparator: **IG-Fact-FixedType**. The other Joint seeds are reported regardless of TEST score.

| Policy | B32 full recovery | Rate | Mean type | Joint Brier | Joint NLL | Worker CPU(s) | Overrides |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WorstFact-MI | 151/192 | 78.65% | 1.11 | 0.3072 | 0.7478 | 14.26 | 0.0% |
| Fresh-IG-Lite | 155/192 | 80.73% | 1.10 | 0.2991 | 0.7194 | 14.76 | 0.0% |
| Belief-Gated | 156/192 | 81.25% | 1.08 | 0.2925 | 0.7077 | 32.91 | 0.0% |
| KL-AnalyticReuse | 133/192 | 69.27% | 1.90 | 0.4232 | 0.9539 | 21.38 | 0.0% |
| Fused-Info | 147/192 | 76.56% | 1.23 | 0.3369 | 0.7867 | 39.87 | 0.0% |
| Rule-Switch | 157/192 | 81.77% | 2.19 | 0.2803 | 0.7014 | 34.25 | 16.7% |
| IG-Fact-FixedType | 157/192 | 81.77% | 1.62 | 0.2772 | 0.6964 | 14.02 | 0.0% |
| Learned-Task-7102 | 151/192 | 78.65% | 1.09 | 0.3060 | 0.7444 | 36.80 | 0.6% |
| Learned-Type-7101 | 148/192 | 77.08% | 2.25 | 0.3313 | 0.7706 | 33.63 | 9.2% |
| Learned-Joint-7101 | 151/192 | 78.65% | 1.21 | 0.3174 | 0.7627 | 34.83 | 1.3% |
| Learned-Joint-7102 | 154/192 | 80.21% | 1.79 | 0.2942 | 0.7154 | 36.80 | 6.5% |
| Learned-Joint-7103 | 151/192 | 78.65% | 1.89 | 0.3026 | 0.7505 | 34.26 | 12.6% |

All arms have the same paid observation access, posterior approximation, forced clock, joint-MAP decoder, B32 online cost and per-world offline cost. Source routing does not change frozen baseline algorithms. Residual task/type masks hold the alternative task/type action fixed at each observed state; divergent future histories can change future purchase schedules.

| Selected Joint minus | Delta(pp) | Paired95% | Family7 interval | Wins | Losses |
| --- | --- | --- | --- | --- | --- |
| WorstFact-MI | +1.56 | [-2.08, 5.21] | [-3.12, 6.77] | 8 | 5 |
| Fresh-IG-Lite | -0.52 | [-4.69, 3.65] | [-5.73, 5.21] | 7 | 8 |
| Belief-Gated | -1.04 | [-4.17, 2.08] | [-5.21, 3.65] | 4 | 6 |
| KL-AnalyticReuse | +10.94 | [5.73, 16.67] | [3.65, 18.75] | 27 | 6 |
| Fused-Info | +3.65 | [-1.04, 8.85] | [-3.12, 10.42] | 16 | 9 |
| Rule-Switch | -1.56 | [-5.21, 2.08] | [-6.77, 3.28] | 5 | 8 |
| IG-Fact-FixedType | -1.56 | [-5.73, 2.6] | [-7.81, 4.17] | 8 | 11 |

Intervals resample complete worlds within four fixed panels; states and budgets are not independent replicates. Family7 adjustment applies to the seven prespecified reference contrasts. No policy is promoted based on TEST ranking. All training losses, DEV-label zero-residual comparators and all9 fit attempts are in TRAINING.json; good MSE does not establish improved decisions.

Paired secondary estimation errors and intervals (joint Brier/NLL, reliability-level absolute errors, fact/type errors) are in ESTIMATION_PAIRED.json. Negative differences favor Joint; these are exploratory and do not inherit the primary family correction.
