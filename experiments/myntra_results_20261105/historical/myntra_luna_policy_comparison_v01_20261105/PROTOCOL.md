# Luna customer response-bank comparison of four Myntra query policies

## Objective and scope

Compare the frozen `fixed_order`, `profile_ig`, `decision_set_ig`, and
`decision_value` query policies when the customer answers with Codex CLI's
requested `gpt-6-luna` model. This is an exploratory integration diagnostic,
not independent confirmation and not evidence about human shopping behavior.

The eight existing development-only personas are retained exactly: two each
from BUY_UNIQUE, BUY_TIED, NO_BUY_FEASIBLE, and NO_BUY_INFEASIBLE. They were
selected for mechanism coverage, not sampled to represent shoppers. The prior
Luna simulator failed its predeclared BUY_TIED behavior screen (9/12 correct);
that result remains unchanged and bounds interpretation of this comparison.
No validation/test products or new personas are used.

## Paired response-bank design

For each of the eight personas, ask one field-specific question for each of the
six frozen elicitation actions, in two fresh independent Codex CLI sessions.
This yields 8 x 6 x 2 = 96 planned Luna calls. Every call resets dialogue
history, uses the same frozen persona contract, and asks for only one field.
The customer prompt does not receive the menu recommendation, policy name,
other answers, hidden reference decision, or other query responses.

The resulting answer for a persona/action/replicate is revealed only if a
policy asks that action. All four policies share the same answer bank within a
replicate, so the comparison is paired and does not give any policy a more
favorable Luna draw. The two response-bank replicates are repeated measurements
of the same eight personas, not additional independent users. The method
policies and posterior recommender are unchanged from the deterministic
closed-loop implementation; only the user-answer source changes.

Primary endpoint: exact valid recommendation at budget 5 against the
deterministic hidden persona evaluator. Report all budgets 0-6, failed/malformed
answers, field-level exact match to the persona, hard-constraint violations,
purchase/no-buy errors, and paired method differences. Budget 6 is a terminal
information check, not an efficiency advantage. Report profile-clustered
descriptive uncertainty only; do not claim population-level significance.

No final Luna purchase-choice call is added. That would introduce a second
simulated decision layer; this experiment isolates query allocation and scores
recommendations against the frozen profile semantics. The recommender remains
a deterministic Python policy, not a language-model agent.

## Isolation, execution, and stop rules

Hidden profiles are sent only to the simulated customer and the evaluator.
The policy receives only the public menu, its frozen prior bank, and valid
answers to questions it actually selected. Invalid responses are retained,
consume the requested interaction, and stop that policy's information path;
no retry, repair, or selective exclusion is allowed. The denominator remains
all eight profiles x two response banks.

Before model calls, freeze source inputs, prompts, code, configuration, and
hashes. Run a 12-call smoke slice using the first frozen profile across both
response-bank replicates. If the model route fails, stop and preserve all
attempts. If it succeeds, run the remaining 84 calls with at most four
concurrent invocations. There are no automatic retries. Save raw final text,
CLI event streams, stderr, usage events, prompt hashes, parse outcomes, and
latencies. A reported model mismatch is retained and flagged; never substitute
another model.

## Claim limits

The prior readiness check showed imperfect behavior in one decision stratum.
The current experiment uses only eight purposively selected personas, a
structured exact-score elicitation interface, and a Codex CLI model alias whose
served backend identity and sampling controls are not independently attested.
Results can show whether the four policies can be integrated under this
simulated response process. They cannot establish that Decision Value is
superior for people, that Luna is a validated human simulator, or that the
policy generalizes to other catalogs.
