# GLM-5.3 direct-transport continuation

## Material Passport

This is a post-failure transport continuation within the user's authorized 288-field GLM family test. The original complete research protocol is preserved in `artifacts/reference/INITIAL_GLM_PROTOCOL.md`; inputs, prompts, model, inference parameters, methods, scoring, all budgets and claim limits remain unchanged. The original run and its frozen files remain untouched in adjacent v01.

## Preserved failure evidence

The initial six distinct A-P00 requests produced one complete valid GLM answer and five transport failures: two ReadTimeout, one ProxyError and two SSLError, with no service response available for the failed calls. The initial smoke gate stopped all 282 remaining requests. A credential-free HEAD check to the same provider hostname failed through the environment proxy but succeeded using direct HTTPS. This supports changing the transport route; it does not establish the ultimate cause of every failed request.

Carry all six original attempts and records into the combined ledger, including all five failures. Do not repeat any of those six jobs. Make exactly the 282 never-attempted GLM requests, including six A-P01 smoke fields before the remaining 276. Maximum combined unique attempts is 288, retries zero. Failed/unattempted records and all affected cases stay in the main denominators. Never fill a missing GLM answer with another model's answer.

## Direct transport contract

Keep the exact endpoint https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1/chat/completions, the same credential, glm-5.3 alias, serialized prompts, stream=true, temperature=1, top_p=1, enable_thinking=true, reasoning_effort=high, max_tokens=8192 and include_usage=true. Each field has a fresh one-message history. Only route and connection scheduling change.

Disable environment proxies on this API client (`Session.trust_env=false`) and use one pooled Session per worker thread, concurrency 4, 0.5-second per-worker dispatch delay, max_retries=0, redirects disabled, connect timeout 30 seconds, read timeout 120 seconds and the original one-hour continuation dispatch deadline. Retain the same stop rules. Session settings are local to this experiment; system proxy variables are not changed. Record the route change and post-failure status in the final report.

## Guard and reporting corrections before new calls

Read-only review found the original decoder accepted zero response IDs despite the protocol's identity requirement. The one accepted original stream has exactly one nonempty ID and matches its stored content/hash. Before additional calls, strengthen the new decoder to require exactly one nonempty response ID; no original response is reclassified or discarded. Retain the original source snapshot and finding.

Also distinguish unattempted records from actual transport failures in the new reporting classifier. Neither correction changes the policy engine, parser, deterministic replay, original scored observations or main endpoint. Freeze these corrections, the original failed run and all new continuation code before new calls.

## Analysis and claim boundary

The frozen same-panel bootstrap, all 280 cases, exact deterministic cache rule and three-deployment common-valid supplementary subset remain as in the original protocol. Report complete banks, failures, actual unique attempts and original/continuation raw response locations. This remains a third-deployment structured fixed-profile check with post-failure transport adaptation, not a clean preregistered transport run, independent held-out experiment, weights-only model comparison, or broad natural/human-agent generalization.
