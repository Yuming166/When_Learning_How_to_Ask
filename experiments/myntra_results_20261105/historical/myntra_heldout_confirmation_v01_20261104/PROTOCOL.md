# Myntra held-out confirmation v0.1

## Research question and status

This is a frozen confirmation of the existing training-free decision-value query policy on the catalogue's reserved validation and test products. It compares the four existing policies under the same deterministic user simulator and reports every elicitation budget from 0 through 6. It does not train a model, call Qwen/Luna, simulate human behavior, or establish real-world recommendation quality.

The user asked to see multiple budgets and whether the proposed policy avoids losses. The primary historical anchor remains budget 5 versus Decision-Set IG. The complete 0-6 curve is co-reported against Fixed Order, Profile IG, and Decision-Set IG. A simultaneous cluster-bootstrap confidence band covers all 21 method-baseline-by-budget contrasts within each split. “No worse at every budget” is supported only if every simultaneous lower bound is at least zero; a favorable average or selected budget is insufficient. All point estimates and failures remain reported regardless of this gate.

## Data, split discipline, and profiles

- Use the original 471-product frozen catalogue and its unchanged split labels. Validation has 78 records and test has 55; every product and leakage group remains in its original split.
- Use all held-out products that have the five reported core attributes, in six predeclared gender/category pools. Construct disjoint menus with target size 10 while keeping each leakage group in one menu. Every eligible product appears exactly once in its split's menus.
- The policy receives only one public menu, the frozen development prior bank, and answers actually returned by the deterministic ReferenceUser. It never receives a held-out profile or evaluator reference.
- Reuse the 2,048-per-pool prior profiles generated only from development vocabularies and the previously frozen seed. Generate fresh held-out user profiles from those same development vocabularies, with 12 profiles per represented pool in each of two independent cohorts per split. Seed roots differ across cohorts and splits. No profile is selected or removed by its recommendation outcome.
- The pool-specific support audit finds these held-out values absent from the corresponding development vocabulary: validation—Women/Kurtas neckline `scoop neck` and fabrics `art silk`, `crepe`; Women/Kurtis fabric `pure silk`; Women/Tops neckline `keyhole neck`. Test—Women/Dresses fabric `modal`; Women/Kurtis pattern `yoke design`. To preserve the frozen development preference support, any item value absent from its pool's development vocabulary receives soft utility 0. It does not create an implicit preference or a new hard constraint. This is an explicit cold-start convention, not a claim about shoppers' tastes.
- Profile scores and hard constraints remain the controlled simulator contract from the development protocol. These are not measured human utilities. Exact answers are deterministic and reliable.

## Policies and interaction budget

Compare the unchanged policies: `fixed_order`, `profile_ig`, `decision_set_ig`, and `decision_value`. Each field question costs one unit; the six actions and their order are inherited unchanged from the frozen method implementation. After each budget, each policy uses the same prior-posterior recommendation rule and tie-breaking rule. Whole-profile disclosure is retained only as a separate six-information-unit, one-turn reference; it is not treated as an equal-information atomic query.

Primary anchor: exact decision accuracy at budget 5, `decision_value` versus `decision_set_ig`. Report every budget (0-6) against all three baselines, including purchase correctness, correct no-buy, false purchase, hard-constraint violations, and score regret where defined. Budget 6 is a terminal correctness check, not evidence of efficiency advantage.

## Analysis

The unit is a paired profile-menu case. For every budget, report numerator and denominator for each method and paired accuracy differences for `decision_value` against every baseline. Resample independent synthetic profile clusters, stratified by user cohort and catalogue category; all menus for a sampled profile travel together. Report pointwise 95% percentile intervals and simultaneous 95% bands using the 95th percentile of the maximum absolute bootstrap deviation over all 21 contrasts in a split. These intervals quantify only synthetic-profile Monte Carlo uncertainty conditional on the fixed held-out menus and preference generator; they do not quantify human, catalogue-sampling, or simulator uncertainty.

Also report split-specific and category-specific denominators, profile-level wins/losses/ties, menu coverage, all invalid or incomplete execution paths, and full-disclosure terminal replay checks. After the shared freeze, run validation and test concurrently using four workers each (eight total); analyze both only with the unchanged frozen code. Do not use validation results to modify policy, simulator, budget, menu construction, or test analysis. Any implementation failure stops the affected run; retain the failure and do not silently patch after seeing held-out outcomes.

## Freeze and stop rules

Before any held-out policy outcome is generated, freeze this protocol, configuration, code, development source catalogue, development-only prior bank, generated menus/profiles/references for both splits, and all hashes. Run only schema/evaluator agreement tests before the freeze; no held-out method scores may be inspected. Verify all frozen hashes before each split run. Run each split once and preserve partial outputs on interruption. The model-call and training counts must remain zero.

The result is a deterministic synthetic-user catalogue confirmation only. Even a positive curve cannot establish real-user or Web-wide superiority. A negative or mixed curve remains a valid result and must be reported without selecting a favorable budget after the fact.
