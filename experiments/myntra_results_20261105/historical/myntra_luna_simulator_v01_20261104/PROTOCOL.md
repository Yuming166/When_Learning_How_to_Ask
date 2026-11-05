# Luna as simulated Myntra customer: bounded development diagnostic

## Execution correction

Revision v0.1.1 fixes a prompt-log directory initialization error found before
the first model request. The failed preflight produced zero model calls and is
preserved separately. No prompt, profile, menu, metric, or stopping rule
changed; a second frozen manifest records the corrected executable.

## Objective and scope

Test whether the Codex CLI model alias `gpt-6-luna` can follow the same fixed
synthetic customer contract used in the Qwen coverage diagnostic. The target
is simulator feasibility, not a recommendation-method comparison or a claim
about human shopping behavior. This is development-only.

## Frozen source material

Reuse the eight development-only profile/menu cases selected before the Qwen
diagnostic by its four reference strata: BUY_UNIQUE, BUY_TIED,
NO_BUY_FEASIBLE, and NO_BUY_INFEASIBLE (two cases each, distinct profiles).
These are mechanism-coverage cases, not a representative sample. No validation
or test products are included. The selected cases and profiles are copied into
this experiment's artifacts and hashed before inference. Private references
are used only by the post-hoc evaluator; the Luna prompt receives the fixed
persona contract, that profile, and public menu information.

## Planned observations

There are nine planned jobs per case (72 total attempts maximum): three fresh,
identical base-choice prompts; one reversed menu; one aliased-option menu; two
care questions; one full-profile disclosure; and one final choice after the
actual Luna disclosure is passed to the deterministic public recommender.
Each Codex invocation is an independent ephemeral session. Repeated base
answers are fresh invocations, not seeded samples. The dialogue job is skipped
if the disclosure is invalid, and is still retained in its planned denominator.

The profile prompt, user text, and fixed menu labels remain as in the Qwen
diagnostic. Since Codex CLI does not expose the Qwen endpoint's temperature,
top-p, seed, or raw chat-completions protocol, this is a model-access-path
comparison, not an exact controlled model comparison. The runner requests
`gpt-6-luna`, records Codex CLI events and version, and does not claim a
separately attested backend model ID. No JSON output schema is imposed by the
CLI; the strict parser treats extra prose, malformed JSON, and invalid options
as failures.

## Isolation and execution limits

No training, paid API, reserved data, retries, prompt search, or method ranking.
Each invocation runs ephemeral in an empty scratch directory with the
read-only CLI sandbox and user configuration disabled; the request explicitly
forbids tool use. At most two concurrent invocations are allowed. Each has a
120-second limit; total wall-clock budget is 3,600 seconds. Two consecutive
CLI/process failures stop remaining requests. All attempts, skipped dependent
jobs, raw CLI events, final text, and parse errors are retained. No model
output will be edited or regenerated.

## Scoring and fixed readiness screen

All planned denominators are retained. Report validity, profile-rule action
accuracy, buy/no-buy decision accuracy, exact item choice, hard-constraint
violations, care disclosure, full disclosure, post-recommendation choice, and
repeat stability. Any highest-scoring tied item is accepted by the evaluator.
The public recommendation is computed only from the actual Luna disclosure;
hidden preferences are never supplied to it.

The simulator advances only to later method-integration development if all
predefined screens pass: at least 95% valid outputs; at least 90% action
accuracy within every four-case stratum denominator (12 planned choices per
stratum, including dialogue); at least 90% care disclosure; at least 90% full
disclosure; and zero hard violations among valid BUY actions. These small
development screens are not statistical certification. Passing them would
not demonstrate a method advantage. Failure means REVISE/NO-GO for this
simulator interface, with no prompt tuning on these cases.

No population confidence intervals or significance tests are reported: there
are only eight purposefully selected profiles, and repeated answers are
within-profile observations. The Qwen run is included as a historical paired
diagnostic reference, with its distinct endpoint controls and sampling
settings stated explicitly.
