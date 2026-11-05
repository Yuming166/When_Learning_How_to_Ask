# Myntra closed-loop method development v0.1

## Research question and status

This bounded development experiment asks whether decision-aware selection among
six exact, field-level preference questions can reduce early recommendation
errors or regret relative to fixed-order elicitation and generic profile
information gain, under the existing synthetic Myntra user model.

It is an implementation and mechanism pilot. The reference user answers exactly
and deterministically. It does not test unknown answer reliability, shared
query-format types, natural-language behavior, the original KL reliability
learner, or human shopping behavior. All 12 existing synthetic profiles and all
24 profile-menu cases are retained; no case is selected by its outcome.

## Data and isolation

- Use the already frozen 471-record Myntra catalogue and its v0.1 development
  split. Only the existing 48 development menu items may be evaluated.
- Use the existing 12 synthetic profiles, six menus, and 24 profile-menu cases.
- Generate a separate prior bank of 2,048 profiles per catalogue pool with the
  same documented profile generator but a new frozen seed root. The query
  policies receive this prior bank, the public menu, and only answers actually
  returned by the ReferenceUser. They do not receive evaluation profiles,
  reference outcomes, or utility-by-product labels.
- A field question costs one elicitation unit and returns that field's score
  map. The wash-care question also returns the allowed care set; the fabric
  question also returns excluded fabric labels. The threshold is one separate
  question. The six units have equal interaction cost in this controlled
  protocol; response-token costs are not modeled.
- Whole-profile disclosure is reported only as a strong shortcut: one dialogue
  turn but six information units. It is not compared with six atomic questions
  as if they had equal information content.

## Compared policies

All policies use the same exact ReferenceUser, six legal actions, cost, prior
draws, recommendation rule, and evaluator.

1. `fixed_order`: ask the five fields in the source-defined order, then the
   purchase threshold.
2. `profile_ig`: choose the unanswered field with maximum entropy of its
   possible answer under the synthetic prior. Since answers are exact, this is
   mutual information with the full latent profile for that question.
3. `decision_set_ig`: choose the question with greatest mutual information
   between its answer and the reference-optimal answer set (all tied best items,
   or `NO_BUY`).
4. `decision_value`: choose the question with greatest expected increase in
   Bayes probability of returning an answer in the reference-optimal set.

After each budget from zero through six, all policies use the same posterior
decision rule: return the product or `NO_BUY` with the highest estimated
probability of being valid under the synthetic prior. Ties prefer `NO_BUY`,
then the lexicographically first product ID. No hidden evaluator is used for
query selection or this decision.

## Outcomes and analysis

Primary outcome: fraction of 24 cases where the final action is a valid
maximizer, or correctly returns `NO_BUY`, at each elicitation budget. Also
report purchase-case recall, no-buy specificity, hard-constraint violation,
score regret, and exact query/unit counts. Regret is zero for `NO_BUY` when the
reference says `NO_BUY`; for a purchase, it is the maximum attainable score
above the threshold minus the score above threshold of a valid recommended
maximizer, with zero reward for an invalid recommendation.

Report all 24 paired cases and profile-cluster means over 12 profiles (the two
menus for one profile remain a cluster). This is a development panel: report
descriptive values only, without significance claims or population confidence
intervals. The Monte Carlo posterior uses the frozen 2,048-profile prior bank;
all methods share it.

## Smoke, freeze, and stop rules

1. Reconstruct the existing v0.1 prepared data into this experiment's ignored
   `artifacts/` directory without modifying the source worktree.
2. Run unit checks and a two-case smoke test. The smoke test must complete all
   six policies, preserve no-buy as an action, and show that six exact answers
   recover a valid terminal recommendation.
3. Freeze this protocol, code, config, source code/data hashes, and prior seed
   before the 24-case run.
4. Run the full bounded panel once. Do not tune policies, query costs, profiles,
   menus, or outcomes from its results. Retain failures and the full denominator.

Stop without interpreting efficacy if a source hash changes, an evaluation
profile reaches the policy outside the user-answer channel, a private reference
enters a policy, or full disclosure fails to reproduce the deterministic
evaluator. No model/API/GPU calls, training, extra profile search, or new menu
construction are part of this protocol.
