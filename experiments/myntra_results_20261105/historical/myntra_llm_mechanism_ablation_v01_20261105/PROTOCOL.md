# Critical adaptivity ablation under three recorded LLM customer channels

The user authorized the same critical mechanism ablation for Luna, DeepSeek
V4.1 Flash and GLM-5.3 after the Python analysis. Use their already collected
real LLM field responses. This is a post-hoc response-bank replay, not fresh
model sampling, natural multi-turn dialogue, or an independently held-out study.
The recommender remains the frozen Python implementation. No API calls or
training are needed or executed in this experiment.

## Fixed sample and source integrity

Each deployment has the same 48 synthetic development profiles, 35 fixed menus,
280 profile-menu cases, and 288 unique field-response records. The three models
share these users; they are not 840 independent customer observations. Do not
extend this result to the 736-case Python panel. Preserve every original record,
including failed transport, invalid outputs, and valid-but-unfaithful answers.
Verify the source freezes, snapshot the records and four original policy traces,
and bind their hashes before any new static-order replay. Keep original files.
Source model identities and decoding/transport differences remain as documented
in the original experiments; model aliases/server strings are not weight audits.

## Sole component intervention

Full decision_value is compared with decision_value_initial_order. For each
public menu and identical 2,048-draw development-only pool prior, compute the
original six DV question scores with empty observations, sort by descending
score with the original exact tie rule, and freeze the order. After every valid
answer, the static control still performs the original observe/posterior/predict
updates. Initial scores/order must match the previous Python ablation for these
same menus. Both variants share a model's exact stored responses; questions,
parsers, preferences, priors and evaluation do not change.

The original update overwrites observed fields in every prior draw; do not
replace it with answer filtering. The hidden true profile is used only by the
ReferenceUser fidelity diagnostic and the separate evaluator, never to repair
responses or select questions. Cache only predict results by the full public
menu/observed-answer state under identical frozen code/prior; never cache stop
flags, costs or whole trajectories by observed state alone.

## Inherited failure semantics and invariants

An attempted field question costs one unit even when the response is invalid or
missing. The first failure permanently stops elicitation; later budget-ceiling
rows continue recommending from the last valid observed state. Preserve failed
paths in all 280-case denominators, including cases where the fallback happens
to be correct. Record actual costs, failure action and path completeness.
Revalidate valid records with the original parser; never promote or repair an
invalid record. Valid-but-wrong preferences are consumed as returned.

Reconstruct every historical full-DV observation/prediction using that model's
bank and its stored adaptive query path. Require all original path/metric fields
to match exactly. Do not re-search the historical adaptive question path.
The two variants must have identical budget0 and budget1 rows (apart from method
labels); same initial question; legal, nonrepeated attempts and valid-history
prefixes. Two complete six-field paths must end in the same recommendation,
but need not be correct when the LLM answer is unfaithful. Failed paths need not
agree at budget6. For complete exact answer banks, the static trace must match
the corresponding deterministic Python static-control metrics and questions.

## Statistics frozen before new replay

Primary comparison is full DV minus static initial-order DV at budget5,
reported separately for each deployment. Budgets3 and4 are auxiliary displays;
retain the complete0-6 curves. Use equal cases for the primary estimate and
equal profiles as sensitivity. No universal-profile improvement gate.

Generate 10,000 paired bootstrap draws using the fixed config seed. Within each
pool_index x cohort stratum, resample entire profiles and keep every associated
menu. Use the SAME sampled profile multiplicities for the three models, so the
joint model comparisons preserve their dependence. There are48 clusters and12
strata, not840 independent cases. Report linear-percentile pointwise95% CIs;
max-absolute-deviation simultaneous95% bands across3 model contrasts at budget5
and across3 models x7 budgets, separately for both weightings.

Secondary failure-excluding diagnostic: use the pre-defined intersection of
profiles with all six stored fields valid in all three models; report its full
denominator, both method curves, and bank/action agreement. Never substitute it
for the primary280-case estimates. Its CIs are descriptive and do not share the
full-sample simultaneous-coverage claim. Report per-model fidelity, stopped
paths, actual question costs, regret, hard violations, and case/profile wins.

All intervals condition on the fixed menus, prior, and single realized response
bank. They do not include model resampling uncertainty, human variability,
catalogue generalization or historical selection. A positive result supports
the critical intervention under these three structured response channels.

## Execution and completion

Run only in this new directory, freeze code/config/protocol/test/input hashes,
run once, retain partial evidence on failure, and do not change variants after
outcomes. Verify every case-method-budget-model key, all historical DV replays,
source preservation, independent result review and output hashes before final
reporting. Offline analysis is reproducible without model access.
