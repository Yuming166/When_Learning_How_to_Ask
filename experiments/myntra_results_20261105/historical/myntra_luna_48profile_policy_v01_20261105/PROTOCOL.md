# Luna 48-profile policy comparison v0.1

## Research question

On the same 48-profile, 35-menu development panel used by the deterministic Myntra closed-loop evaluation, do four frozen query strategies behave differently when each structured preference answer is supplied by a fresh Luna session? The primary descriptive comparison is Decision Value versus Decision-Set IG at budget 5. No method is presumed superior.

## Frozen panel

- 48 existing synthetic development profiles, eight per six gender/category pools.
- All 35 frozen development menus and all 280 profile-menu cases. Validation-reserved and test-reserved products are excluded.
- The 48 profiles and development menu panel already participated in deterministic method development; this is an exploratory model-simulation transfer check, not independent confirmation.
- Six fields per profile, one independent call per field: 288 planned calls. Each profile-field answer is shared across all menus for that profile and all four paired methods, preventing strategies from receiving different simulated customers.
- Every model call resets dialogue history and presents the same fixed profile plus one field-specific question. The recommender is the frozen deterministic Python policy, not an LLM agent. Luna does not make the final product choice.
- The baseline prior contains 2,048 synthetic profiles per product pool (12,288 total). These are algorithmic prior draws, not evaluation users.

## Outcomes

Evaluate exact valid-recommendation rate at budgets 0–6 using the existing deterministic hidden-profile evaluator. A recommendation is correct when it returns NO_BUY for a hidden NO_BUY case, or a hidden valid purchase product for a BUY case. Also report regret, hard-constraint violations, query cost, per-pool and per-profile results, response validity, exact field match, and agreement with the already-recorded deterministic reference.

Paired differences use profile-cluster bootstrap stratified by pool and user cohort. The point estimate is over the 280 frozen profile-menu cases; the resampling unit is the unique profile. With 48 profiles this remains a development-panel estimate, not a human-population claim.

## Integrity and execution

Preserve the existing 8-profile Luna experiment unchanged. Freeze code, inputs, prompt hashes, source hashes, model alias, and CLI version before calls. Run a six-call smoke (one full profile response bank); require no transport or identity mismatch and verify all four policy paths replay without exception before the remaining 282 calls. Invalid/failed responses remain in the denominator; no retries or prompt tuning. Execute independent fresh Codex CLI sessions with concurrency 8, timeout 120 seconds, and a one-hour wall budget. Stop on three consecutive transport failures or reported model mismatch.

The prior Luna behavior screen reached 9/12 on BUY_TIED and failed its acceptance gate. This experiment retains that negative result. Exact field answering under a supplied hidden profile does not establish natural customer behavior, human preference validity, or superiority on a held-out cohort. The deterministic benchmark has already shown a development advantage, but this model-simulation panel reuses those same profiles and menus and must not be represented as independent evidence.
