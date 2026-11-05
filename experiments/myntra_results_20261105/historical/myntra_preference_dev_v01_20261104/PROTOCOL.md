# Myntra preference development v0.1

## Material Passport

2026-11-04. User authorized development from the 471 core-complete catalogue
items. Source: 4ff3ce1; isolated worktree. Preserve all historical tracked files.
This stage builds a controlled preference environment, a private user/public
recommender boundary and a tiny local-model diagnostic. It is not a human study,
method ranking, training run or a natural-reliability confirmation.

Use only development-split products for menus, profile vocabularies, prompts
and reference episodes. The input adapter scans the 471 catalogue records to
filter their existing split flags; 78 validation and 55 test records remain
untransmitted and unevaluated. Do not change their original split assignments.

## Fixed construction

Three pools: Women/Kurtas, Men/Kurtas, Women/Dresses. Hash-order the development
products within each pool and take two disjoint menus of eight; no resampling
for persona feasibility, preference diversity, positive performance or buy rate.
Create four independently seeded synthetic profiles per pool (12 total).
Each is evaluated on both menus (24 development cases).

Private profile semantics:

- Hard constraints: a nonempty subset of acceptable seller-recommended care
  labels, and zero or one excluded fabric category label. No medical allergy,
  fibre-percentage or exclusive physical care permission is implied.
- Soft preferences: per-field categorical scores. One favourite label receives
  +2 times an importance of 1 or 2, one different label receives -1 times that
  importance, and all other known labels receive 0. Five fields are additive.
- Fixed purchase threshold drawn independently from {0,3,6,9}. Buy only when a
  feasible item's score is STRICTLY ABOVE the threshold. Equality means do not
  buy. If buying, any score-maximizing feasible item is valid; ties are retained.
- A feasible product can be less preferred, or the best available product can
  still fail the purchase threshold. Neither forces a purchase. Retain profiles
  with no feasible product and profiles with feasible but unappealing products.

Numerical scores are an explicit controlled preference contract for diagnostic
evaluation, not a claim of human utility realism. Source labels do not measure
collar height, visual salience, texture or subjective appeal. Do not invent them.
Profiles do not include budget, fit or other undisclosed tastes. No correctness
probabilities or optimal question type are injected into model instructions.

Reference outputs are computed separately by Python and an in-memory SQLite
evaluator. They never enter the recommender's public view or Qwen requests.
PublicAgent receives only menu attributes and actual disclosed answers. Its
preference completion status is separate from the user's NO_BUY decision.
Two lossless question schedules (ask-all and six-field disclosure) test wiring
against a deterministic reference user, not query efficiency superiority. They
communicate different amounts per turn and do not instantiate atomic iid p/q.

## Local Qwen diagnostic, at most 16 generation attempts

Use the already running endpoint only, actual served ID Qwen3.6-35B-A3B.
No paid APIs, service changes, other models, training or prompt search. One
request at a time; 45s each; 900s overall; no retries. Record transport failures,
invalid outputs and unattempted dependent jobs. Stop after this diagnostic.

Profiles P00 and P08 are fixed before inspecting their outcomes. Each gets:

1. Four independent menu choices: original; exact same prompt with new seed;
   reversed item order; permuted option IDs with original order.
2. Two equivalent care-set inquiries A/B, same labels and answer encoding.
3. One whole-profile disclosure (an explicit strong shortcut control).
4. One genuinely chained final choice: actual disclosure reply -> public
   recommender computes recommendation -> simulated user receives that
   recommendation and may buy a different maximizer or buy nothing. If the
   disclosure is unusable, skip this dependent call without replacement.

No gold choice, acceptance set, utility-by-product table or reference result is
sent to Qwen. The private profile is given to the simulated user, not the public
recommender. Choice calls use 256 output tokens, care calls 128, disclosure
1400; temperature .5, top_p .9, thinking disabled, seeds frozen per job.

Strict JSON parser may unwrap one complete JSON Markdown fence, as in the prior
transport protocol. It never extracts JSON from prose, repairs contents or
retries. Require normal stop, expected model ID, legal option IDs, correct key
types and no duplicate care labels. Report fenced outputs independently.

## Analysis and freeze

Before inference freeze code, protocol, config, system prompt, profiles, public
menus, jobs, independent request templates and private references by hash.
Dependent request construction is frozen as code and saved before its POST.
All choices retain full planned/attempted/valid denominators. Measure agreement
with fixed constructed preferences, selected hard violations, selected utility
regret, correct no-purchase with/without feasible goods, repeated/order/ID
consistency, care disclosure and whole-profile disclosure. No tie is scored
wrong merely because another equally preferred item was chosen.

Sixteen calls from two profiles cannot establish format reliability sharing,
human fidelity, iid errors, superiority to IG or a robust simulator. Report
missing outcome coverage, including if the fixed smoke profiles do not cover
both purchase and no-purchase. Do not add profiles to manufacture that coverage.
No significance tests or population intervals are appropriate for this smoke.

The entire 12-profile construction remains DEVELOPMENT. Future simulator or
method confirmation requires new profiles and a separate frozen protocol.
