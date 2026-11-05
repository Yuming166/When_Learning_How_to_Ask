# DeepSeek V4.1 Flash customer-response replication v0.1

## Material Passport

- Mode: authorized code experiment; simulation, not a human study.
- User authorized this model, the supplied Qianwen Beijing endpoint, uploading the same synthetic customer questions, and completion of the same-data comparison on 2026-11-05.
- Primary comparison: Decision Value minus Decision-Set IG at budget 5. Budgets 3 and 4 are also requested descriptive comparisons; retain all budgets 0–6 and all four policies.
- New calls: exactly 48 profiles × 6 fields = 288; no purchase-choice calls, training, new profiles, reserved products, prompt search, or response retries.

## Fixed inputs and differences

Copy every Luna input byte-for-byte: 48 existing synthetic development profiles, 35 menus, 280 profile-menu cases, 12,288 prior draws, 288 serialized prompts. Copy the policy engine and environment unchanged. Extract the existing parser and replay function without editing their function bodies. Bind all code, inputs, original results, and response-bank cache by SHA-256 before any call.

Send each original serialized prompt as the content of one user message, with fresh history for every field. The customer sees its complete fixed profile but only answers the requested field. The deterministic recommender receives only fields actually elicited. The same answer bank is shared across all menus and policies. The user-supplied image example is transport guidance; no image is added to this text-only panel.

Provider: Qianwen / Alibaba Cloud Model Studio, not direct DeepSeek transport. Base URL: `https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1`; requested alias: `deepseek-v4.1-flash`. Freeze temperature=1, top_p=1, enable_thinking=true, reasoning_effort=high (documented defaults made explicit), max_tokens=8192, stream=false. The output cap and API transport differ from Luna's Codex CLI, whose backend identity and decoding parameters were unavailable. Accept the requested model alias or the documented `deepseek-v4.1-flash-1017` response alias, record the actual string, and never claim independent weight attestation. A model response using a different alias stops the queue.

## Execution

Use standard-library HTTPS POST, concurrency 8, a 120-second request timeout and a one-hour global dispatch deadline. No SDK retries. A six-call A-P00 smoke is included in the 288-call total; require no transport/model-identity error and successful four-policy replay before dispatching the other 282 calls. Failed or invalid answers remain in the inventory and case denominators, with the same original stop/fallback rule. No response repair, retry, or prompt tuning. Stop further dispatch on authentication/billing/contract errors, model mismatch, or three consecutive transport failures; already in-flight calls finish and remain recorded. Record unattempted jobs separately. Credentials enter via environment or non-echoing terminal input, stay in process memory, and never enter request-body snapshots or reports.

## Offline replay and cache

For each profile compare the complete six-field effective answer bank with Luna's frozen bank: validity, parsed value, and exact-profile-match flag. A profile may reuse Luna's deterministic traces only if all six signatures match and every input/engine/parser/replay hash and case identity has been verified. This is exact deterministic memoization, independent of whether a policy wins. Recompute every case of any changed profile using the original replay function. Before full collection, independently replay the smoke profile's representative case and require byte-equivalent trace objects when cache-equivalent. If parity fails, stop rather than mix inconsistent traces. Report reused and recomputed cases and per-model output disagreements. Raw DeepSeek answers are still collected for all 288 jobs, irrespective of cache eligibility.

## Scoring and uncertainty

Use the same hidden deterministic evaluator: exact valid purchase recommendation or correct NO_BUY; report query units, regret, hard violations, failures, BUY/NO_BUY denominators, per-profile and per-pool results. Never use model answers as ground-truth preferences. Retain all 280 cases in each method-budget cell.

Replicate the original stratified profile-cluster bootstrap: 10,000 repetitions, seed 202611041955, the same 12 pool-by-cohort strata, and all menu cases carried with each selected profile. Match the recorded Luna differences and intervals before inference. Report descriptive 95% intervals, not a confirmatory hypothesis test; 48 profile clusters, not 280 independent users. Compare DeepSeek and Luna by paired cases as well as aggregate method scores.

## Claim limits

These development profiles/menus were already used for method development. This is a second model/API deployment check of structured fixed-profile answers, not independent held-out confirmation, an LLM recommendation agent, a validated customer simulator, or evidence of human shopping behavior. Luna's previous BUY_TIED behavior-screen failure remains unchanged; this experiment does not repeat that behavior screen for DeepSeek. Exact field copying or nearly identical policy scores may show protocol fidelity while adding little behavioral diversity. Provider/model/decoding differences are inseparable in this comparison.

## Documentation checked before calls

- https://help.aliyun.com/zh/model-studio/deepseek-api (thinking control, defaults and response protocol)
- https://help.aliyun.com/zh/model-studio/deepseek-v4-1-flash (provider/model alias)

The user's explicit experiment and upload instruction takes priority over the generic ARS execute-only and no-upload defaults. No additional authorization gate is inferred.
