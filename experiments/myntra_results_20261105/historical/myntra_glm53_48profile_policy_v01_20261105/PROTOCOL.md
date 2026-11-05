# GLM-5.3 same-panel customer-family transfer v0.1

## Material Passport

The user explicitly requested execution using glm-5.3 and the supplied Qianwen Beijing API on 2026-11-05, to extend the customer-model-family transfer test. Authorization covers sending the same synthetic fixed-profile prompts to this endpoint. This is a code simulation experiment, not a human study. The generic ARS no-upload/execute-only defaults do not override that authorization.

## Frozen research comparison

Copy the exact Luna input bytes: 48 synthetic development profiles, 35 development menus, 280 profile-menu cases, 12,288 independent prior profiles and 288 serialized customer prompts. All validation/test-reserved products remain excluded. The four Python query strategies, deterministic evaluator, parser, query costs, budgets 0–6 and tie-breaking stay unchanged. Primary comparison: Decision Value minus Decision-Set IG at budget 5; also report budgets 3 and 4 requested in this conversation. All 280 cases remain in each method-budget cell, including failed-response paths and NO_BUY cases.

Each new GLM session receives exactly one original serialized prompt as one user message and answers one field. All menus and four strategies share the same profile-field response. No final purchase-choice model call, natural dialogue rollout, new profile, tuning, training, held-out evaluation or API call to another model is added. Exactly 288 planned GLM requests, one per profile-field, zero retries.

## Deployment contract

Use the exact requested alias `glm-5.3`, at `https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1/chat/completions` through Qianwen / Alibaba Cloud Model Studio. Accept only `glm-5.3` as a reported stream model. This is the provider-reported alias, not independent model-weight attestation. GLM and DeepSeek family names distinguish nominal model deployments; they do not supply a random sample of models or prove independent training.

Freeze temperature=1, top_p=1, enable_thinking=true, reasoning_effort=high, max_tokens=8192 (integer), stream=true and include_usage=true. High and top_p=1 are chosen to align the previous DeepSeek configuration; GLM's documented defaults are top_p=0.95 and max reasoning. Do not silently call these identical defaults. The endpoint supports high. Luna's backend/decoding configuration cannot be fully matched. Deployment and inference-setting differences remain confounded with model identity.

Use one pooled requests.Session, concurrency 1 and a 0.5-second dispatch interval, based on the previously stable transport. Connect timeout 15 seconds, per-request/stream timeout 120 seconds, one-hour global dispatch deadline, no automatic HTTP retries or redirect forwarding. Six A-P00 field requests form the initial smoke and count within the 288. Require successful transport/identity and the unchanged four-policy replay check before the remaining 282. On authentication/billing/contract failure, model mismatch or three consecutive transport/protocol failures, stop new dispatch. Preserve all failed and unattempted jobs separately. Do not resample or repair invalid answers.

Require well-formed SSE frames, one consistent allowed model and response identity, a terminal finish reason and [DONE]. Concatenate only content deltas into the answer; reasoning_content is never used for parsing or scoring. Retain the raw stream locally and token usage if reported. Truncation, malformed/incomplete streams, wrong model, tool calls and schema violations fail closed; do not accept a parseable JSON fragment from an incomplete stream. Keys enter via environment or hidden terminal input and remain out of artifacts.

## Offline analysis

Before inference, verify original Luna and DeepSeek frozen hashes, exact source/input identity, and reproduce all 28 Luna counts plus 21 paired bootstrap comparisons. The original stratified profile bootstrap uses 48 unique clusters, 12 pool/cohort strata, 10,000 draws and seed 202611041955; carry all of a profile's menu cases together. Intervals are descriptive, not a claim about independent human users or a preregistered population hypothesis test.

Use the same exact deterministic memoization rule: only reuse Luna policy traces when the complete six-field effective bank matches in validity, parsed values and exact-profile-match flags and all inputs/functions are identical. Recompute every case of changed profiles. This never replaces any of the 288 actual GLM request attempts. Before full collection, independently replay the smoke case and require exact trace parity if its bank is cache-equivalent.

Report GLM vs all four policies, GLM/Luna/DeepSeek full-denominator scores, field validity and fidelity, complete-bank counts, per-profile/pool outcomes, failures, regret, constraint violations, query costs and paired differences. Preserve DeepSeek's 10 TLS failures and post-failure transport continuation when comparing full panels. Additionally describe the intersection of profiles with complete valid banks across all three models, explicitly as a failure-excluding secondary subset, not the primary endpoint. Never select a response or subset based on method success.

## Claim boundary

This panel already participated in method development. It tests structured disclosure of a supplied fixed preference profile under a third specified customer deployment. The recommender is deterministic Python, not a model-driven recommender agent. High field fidelity or matching scores need not imply behavioral diversity. The result cannot establish natural multi-round agent transfer, human preference validity, independent held-out confirmation, broad robustness across all model families, or weights-only causality. The previous Luna BUY_TIED behavior-screen failure remains unchanged; no GLM purchase-behavior validation is implied.

## Official provider documentation checked

- https://help.aliyun.com/zh/model-studio/glm
- https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions/

Only model/content transport and analysis implementation are adapted. No source experiment or prior result is modified.
