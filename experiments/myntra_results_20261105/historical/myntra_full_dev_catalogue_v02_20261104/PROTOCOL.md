# Full development-catalogue robustness panel v0.2 (bounded parallel runner)

## Question

Does the frozen `decision_value` elicitation policy retain an advantage over
the stronger `decision_set_ig` baseline when tested across the full eligible
Myntra development catalogue, rather than the 48 products in six earlier
menus? Fixed-order and profile-IG policies remain secondary baselines.

This is a controlled finite-catalogue experiment with deterministic synthetic
users. It is not a human or LLM-agent experiment and does not validate the
original unknown shared-reliability theory.

## Data scope and construction

- Bind to the frozen 471-row source catalogue and use every record in its
  `development` split that has all five frozen core attributes. The current
  audit found 338 such development records across six gender/category pools.
- Keep all records in a `leakage_group_id` together in a single menu. This
  preserves every development product record while preventing a near-duplicate
  family from appearing in multiple menus. Validation-reserved and test-reserved
  records are never loaded into menus, profiles, priors, or evaluators.
- Create deterministic, outcome-blind menus within each category, using a
  target size of 10 and a frozen seed. Expected pool sizes are Men/Kurtas 11,
  Women/Dresses 5, Women/Kurtas 15, Women/Kurtis 1, Women/Tops 2, and
  Women/Tunics 1: 35 menus total. Actual size can vary when a leakage group
  contains multiple product records; record every menu size and item assignment.
- Generate two fresh user cohorts, four profiles per category in each cohort
  (48 profiles total). Generate one independent prior bank of 2,048 profiles
  per category. The same prior bank is used for paired methods and both user
  cohorts; no hidden evaluation profile or label is passed to a policy.
- Evaluate every profile against every menu in its category. No profile, menu,
  or result is filtered by outcome.

## Policies and outcomes

Reuse the original frozen implementation without changing query scores,
recommendation rules, tie-breaking, or costs: `fixed_order`, `profile_ig`,
`decision_set_ig`, and `decision_value`. Record budgets 0 through 6, plus the
whole-profile `ask_all` reference at one turn and six information units.

Primary comparison: exact valid-recommendation rate for `decision_value` versus
`decision_set_ig` at budget 5. Report fixed-order and profile-IG comparisons as
secondary. Also report purchase recall, NO_BUY specificity, false purchases,
hard-constraint violations, normalized regret, and results by category, menu
size, cohort, and profile cluster. Full disclosure must recover every reference
decision at budget 6.

Uncertainty is summarized with a 10,000-draw profile-cluster bootstrap,
stratified by cohort and category. Menus are the finite development-catalogue
census in this experiment, not a sample from a menu population. Intervals are
conditional on the synthetic profile generator; they do not support human-user
or cross-catalogue claims.

## Descriptive robustness gate

Report `CATALOGUE_ROBUST_ADVANTAGE_ESTABLISHED` only if the budget-5 paired
difference against `decision_set_ig` is positive overall, the stratified
profile-cluster bootstrap 95% lower bound is above zero, both independent user
cohorts have positive differences, at least 4 of 6 categories have positive
differences, and at least 24 of 48 profile clusters have positive differences.
Otherwise report `CATALOGUE_ROBUST_ADVANTAGE_NOT_ESTABLISHED` and retain all
negative and mixed effects. This gate is descriptive and does not correct for
method selection on earlier development experiments.

## Freeze, smoke, and run rules

Audit all category counts, attribute vocabularies, duplicate families, and
reserved-split separation. Build menus and profiles in this new experiment's
ignored preparation directory. Run tests and two smoke cases, including the
small five-item Kurtis category. Freeze protocol, code, source, previous result,
and generated input hashes before the full run. Run the full panel once using
the frozen eight-worker `spawn` process pool. Cases are independent; workers
return complete per-case records to the parent, which writes each case batch
exactly once in canonical case order. The runner checks the 29 distinct
method-budget records per case and verifies the persisted trace against the
in-memory trace. Do not tune from results, call models/APIs, train models, or
edit any earlier experiment. An interrupted full run is preserved as
incomplete; do not selectively resume or rerun in place.
