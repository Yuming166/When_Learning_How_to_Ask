# T3 cross-budget and heldout-regime evaluation

## Material Passport

Primary B32 uses192 worlds. Each secondary budget uses the same prespecified48-world subset,12 per panel; these overlap B32 worlds and cannot be counted as additional independent worlds. Budgets are separate completed trajectories.

| Budget | WorstFact | Fresh-IG | FixedType | Task-only | Type-only | Joint |
| --- | --- | --- | --- | --- | --- | --- |
| 16 | 17/48 | 17/48 | 18/48 | 17/48 | 18/48 | 18/48 |
| 32 | 151/192 | 155/192 | 157/192 | 151/192 | 148/192 | 154/192 |
| 48 | 43/48 | 42/48 | 45/48 | 42/48 | 43/48 | 43/48 |
| 64 | 48/48 | 47/48 | 46/48 | 47/48 | 47/48 | 47/48 |

B32 selected Joint minus WorstFact by panel:

| Panel | Worlds | Delta(pp) | Paired95% |
| --- | --- | --- | --- |
| ID | 48 | +8.33 | [0.0, 18.75] |
| OOD-rate | 48 | +2.08 | [-4.17, 10.42] |
| OOD-partition | 48 | +0.00 | [0.0, 0.0] |
| OOD-calibration | 48 | -4.17 | [-12.5, 4.17] |

Unseen rates, d3/group partitions and alpha1 are held out of both neural fitting and DEV selection. Training only atB32 tests budget transfer at16/48/64. Most d4 B16 trajectories consist entirely of forced queries, so allocation policies cannot differ there. OOD confidence intervals remain wide; a small observed deficit is not a formal no-harm guarantee. Mechanism/Natural/Web validity is untested.
