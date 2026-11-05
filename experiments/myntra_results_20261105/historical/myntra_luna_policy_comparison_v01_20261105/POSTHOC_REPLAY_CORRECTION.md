# Post-hoc replay correction

The first deterministic analysis at `results/ANALYSIS.json` was invalid for strategy outcomes: it destructured `PublicPolicy.history` entries (which are dictionaries) as two-value iterables. The exception handler marked every second queried field as a failed path. The original outputs are preserved in `results/first_pass_invalid_due_to_replay_bug/`.

No model calls were repeated. The 96 raw model response records and the original inference runner remain unchanged. A separate post-hoc copy `posthoc_replay_corrected.py` changes exactly one loop to read `prior_entry["action"]` and `prior_entry["answer"]`, then replays policies deterministically from the frozen response bank. The pre-inference `FROZEN.json` remains intact and verifies the original experiment artifacts; the post-hoc correction script is not represented as pre-registered code.

Original analysis runner SHA-256: `d529357f96c3a732df7ebdd69c1aea5e512ebfd55de570b03fe49faf7dd6ecf9`
Post-hoc correction script SHA-256: `1ad21622162378c49db8c06824ab9297818cc40372841e9c78e7e6f585355c70`

This correction fixes a transparent software exception in the replay layer. It does not authorize changing prompts, policies, profiles, budgets, outcome rules, model responses, or retrying calls.
