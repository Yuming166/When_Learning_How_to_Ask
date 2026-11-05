# Python mechanism ablation on the pooled fixed benchmark

The user authorized this experiment after inspecting the existing full-policy
results. This is a post-hoc component analysis, not a new untouched confirmation.
The following design and code are frozen before generating any new static-order
outcomes. Original experiments and their conclusions are preserved.

## Cases and information boundary

Use exactly the existing 280 development, 264 validation_reserved, and 192
test_reserved profile-menu cases (736 cases, 288 profiles, 54 menus, 471 items).
Keep each case's original menu, hidden preferences, reference decision, and
development-only 2,048-draw-per-pool prior. Do not merge menus, regenerate users,
extend vocabularies, fit priors, or exclude cases based on results. Held-out
unseen attributes retain their frozen neutral-zero utility convention.

The policy receives only a public menu, its independent prior, and answers to
questions already asked. The ReferenceUser and hidden-reference evaluator are
separate from question selection. The existing posterior operation overwrites
observed fields in every prior draw; it is deliberately left unchanged.

## Component contrast

Treatment: existing adaptive decision_value. Reuse its immutable complete traces
and independently replay every stored observation and prediction with the
original policy implementation. Objective controls fixed_order, profile_ig,
decision_set_ig are reused with independently recomputed ground-truth metrics.

New control decision_value_initial_order: before seeing any answer, compute the
original decision_value score for all six questions and sort descending, with
the original exact-score/action-order tie break. Ask in that fixed order.
Continue the original observe, posterior, and predict operations after every
answer; only next-question adaptation is removed. Initial orders may be cached
per split/menu because all users of that menu share the identical prior.
Order caching and trajectory-state reuse are exact deterministic memoization,
not new samples or additional observations. Neither policy receives more than
the declared question budget. Equal question counts do not imply equal compute.

Required invariants: matching first question; per-case identical recommendations
at budgets 0 and 1; six distinct legal questions by budget 6; both terminal
recommendations identical and correct; static order invariant across users of
the same menu; frozen original traces and inputs unchanged. Accuracy is not
assumed monotonic across budgets. No model calls, training, retries, or
outcome-guided variant changes.

## Analysis fixed before new outcomes

Primary component contrast: adaptive DV minus initial-order DV at budget 5.
Secondary existing objective comparison: DV minus Decision-Set IG. Budgets 3 and
4 are auxiliary displays; retain all budgets 0-6 and all five methods.

Primary estimand weights the 736 cases equally. Also report equal-profile
averages, split-specific and pool-specific results, case and profile wins/ties/
losses, selected-action differences, and query-prefix differences. Retain false
purchases, hard violations, and regret. No majority-profile or all-subgroup
positivity gate is imposed for the mean-effect question.

Use 10,000 paired bootstrap draws with the seed in config.json. Resample entire
profiles within (original split, pool_index, user_cohort), keeping all menus for
each selected profile. This gives 32 strata for the pooled data. Report linear
interpolated percentile pointwise 95% intervals. Also report the max-absolute
deviation simultaneous 95% band over 2 contrasts x 7 budgets, separately for
case weighting and profile weighting. These bands do not adjust historical
method/benchmark/analysis selection. Split/pool intervals are pointwise
descriptive intervals. Menus and strata are held fixed; uncertainty covers the
synthetic profile generator, not people, arbitrary catalogues, or simulator
validity. Full-policy performance observed before this freeze stays disclosed.

## Preservation and completion

Snapshot exact input files; verify both upstream freezes. Hash-bind source
inputs, original outputs, code, this protocol, config, and preflight test receipt
before run. Run once into a new directory and retain partial evidence on any
failure. Do not overwrite run evidence. Before final reporting, verify coverage,
all reference replays, component invariants, upstream preservation hashes, and
all output hashes. Analysis can be reproduced offline from saved traces.
