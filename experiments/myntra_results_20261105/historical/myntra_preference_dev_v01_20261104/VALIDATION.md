# Interpretation boundaries

## Material Passport

Development diagnostic: 12 constructed profiles / 24 offline cases; two fixed
profiles / 16 local-model calls. No population inference or method comparison.

| Interpretation risk | Audit treatment |
|---|---|
| Technical validity vs semantic validity | Parser success is separate from fixed-profile correctness; neither validates human realism |
| Ground-truth leakage | Private references stay evaluator-side; actual disclosures alone enter PublicAgent |
| Hidden selection | Hash menus/profiles and P00/P08 fixed before outcomes; no replacement |
| Denominator bias | 16 planned, 16 attempted, 16 valid; all failures retained |
| Repeated observations as independent users | Ten choice calls are repetitions/history of two profiles; no iid or population intervals |
| Insufficient outcome coverage | Both model-tested cases should not buy; buy-positive capability is unknown |
| Agreement mistaken for truth | Order/alias consistency and reference correctness reported separately |
| Wrong target utility | Selecting the highest-score item can still violate the purchase threshold |
| Relative effects vs causal improvement | No comparison to prior VOGUE accuracy: dataset, task and evaluator changed |
| Presentation vs sampling randomness | Views use different seeds; one wrong reversed-view answer does not establish a causal order effect |
| Baseline/cost fairness | Full disclosure is retained; its information per turn differs from fieldwise and atomic binary queries |
| Generalization or optimality overclaim | No human simulation validation, natural p/q sharing, theoretical attainment or superiority to IG established |

The utility rule is a deliberate controlled assumption. Unknown physical facts
remain unmodeled; we do not invent them to force item-level binary answers.
Future mechanism-coverage sampling must be labelled as such and frozen before
new responses. No p-values, significance claims or confirmatory conclusions
are reported for this smoke test.
