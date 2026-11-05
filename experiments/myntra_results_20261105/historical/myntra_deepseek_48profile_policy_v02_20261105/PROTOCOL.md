# Transport-only continuation of the DeepSeek same-panel experiment

## Material Passport

The user's 2026-11-05 request authorizes completion of the same-data DeepSeek customer experiment. The initial run and its frozen files remain unchanged in the adjacent v01 directory. The full original protocol is preserved as `artifacts/reference/INITIAL_PROTOCOL.md` and still governs prompts, policies, scoring, budgets, failures, uncertainty, and claim limits.

## Observed transport failure and fixed continuation

The initial six-call smoke passed with exact Luna replay parity. The subsequent run stopped at its three-consecutive-transport-failure rule. It made 24 distinct attempts: 14 valid responses, 10 TLS `UNEXPECTED_EOF_WHILE_READING` failures, and 264 jobs not attempted. No HTTP status or model content was received for those ten failed connections. The cause is unresolved; it is not labeled a model-answer error.

This continuation changes only HTTPS connection handling and dispatch pressure: Python `requests.Session`, pooled connection reuse, concurrency 1, minimum interval 0.5 seconds, no HTTP-library retries or redirects, connect timeout 15 seconds and response timeout 120 seconds. Record the requests/urllib3 versions. Model endpoint, alias, prompt bytes, generation parameters and all research inputs remain exactly identical. A new A-P04 six-field transport smoke is a subset of the 264 never-attempted jobs, followed by its four-policy replay check and the remaining 258 never-attempted jobs. The global continuation dispatch deadline remains one hour.

Carry all 24 original attempts into the combined ledger and retain all 10 original failures as failures. Do not repeat any job that was already attempted, even if it failed. Thus there are at most 288 unique attempts across both phases, zero retries, and all 280 cases remain in each policy-budget denominator. Continue to distinguish transport failures, invalid answers, unattempted jobs, and scored case failures. All initial attempts/records/responses/receipts are snapshotted before this continuation and hash-bound. The new collector refuses a second run.

The adaptation is post-failure, not preregistered. It preserves the original failure evidence and does not turn the stopped initial run into a fully predeclared successful run. Report aggregate all-case results including transport failures; also report how many profiles have a complete valid response bank. Do not describe the combination as a clean model-only robustness result. Do not infer network reliability or human shopping behavior from it.

All scripts, source records, original and continuation contracts, immutable input copies and request bodies are frozen before any additional call. The statistical analyzer, parser, scoring and exact deterministic cache rule remain the same. No new model calls occur during offline analysis.
