## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run / discovery design
- Origin Date: 2026-10-30
- Verification Status: protocol, not empirical evidence
- Version Label: phase01_v1

# Frozen Phase 0/1 protocol

## Questions and stopping point

Q1: Do semantically equivalent whole-option and attribute-contrast questions exhibit natural reliability differences?
Q2: Does a group's difference predict new preferences under new phrasing?
Q3: Can an answer-only selector exploit sharing beyond fixed, alternating, direct self-report and public-metadata choices?
The authorized endpoint is a development pilot report. No complete adaptive agent, training, paid APIs, 35B generation, automatic follow-up calls, or confirmation experiment.

## Task and information boundary

Each independently seeded profile has two known groups of four binary choices in web-facing domains (shopping, feeds, booking, cloud services). Each group has a private signed additive-utility or lexicographic policy, sampled independently of its public domain. Four independent option pairs follow that policy. Canonical preference bits are independent fair draws, implemented by swapping options after constructing a non-tied pair. No profile is filtered by model performance. Within-group labels are not forced to balance, to avoid a known label-total shortcut.

The response model sees its private policy and both options. The elicitor sees group membership, domain/attribute metadata, questions, and canonicalized answers, but no private policy or labels. The public metadata predictor sees only public domain, attributes, group size and query descriptions. The direct type report sees the private policy and the same query descriptions. Neither report gets measured reliability or response feedback. A difference of private policy representation is an environment variable, never a prescribed good format or error probability.

Format A asks to assess complete options individually. Format B asks to compare attribute differences. Both request the same preferred-option digit, share byte-identical policy/options, and preserve identical evidence ordering and option mapping within paired repetitions. Two paraphrases per format are fixed in source. Character-length differences are checked and token-length differences logged. Deterministic absolute-utility and difference evaluators must agree; option swaps must complement answers; common attribute shifts must preserve answers. These checks certify construction, not the model's interpretation or absence of all linguistic confounds. This is policy-grounded preference simulation, not evidence about real people.

## Samples and model contract

Smoke: 2 independent profiles, 8 preferences each, 2 formats, 2 independent generations = 64 task responses, plus 8 direct and 8 metadata reports = 80 generations.
Pilot: 24 new development profiles, 8 preferences, 2 formats, 8 independent generations = 3,072 task responses, plus 96 direct and 96 metadata reports = 3,264 generations. Total cap: 3,344. Every generation uses a fresh context/cache and distinct recorded seed. No resampling from a probability cache. No injected p/q. No retry of failed requests. No continuation of a truncated output. All unsuccessful outputs remain in denominators.

Initial service audit found only 35B at 10.63.0.88:31519 and Hy-MT2-7B on cloud82:31519. Therefore use the already cached Qwen3.5-4B checkpoint with the installed Transformers runtime, offline, one idle physical GPU (3), float32, SDPA, TF32 off, one independent request at a time. This is a distinct local inference backend, not an assertion that the old API deployment still exists. Record actual model class, package versions, checkpoint/tokenizer hashes, dtype, GPU, settings and serialized prompt hashes. No downloads or deployment changes. API backend is supplied for a future verified 4B endpoint and refuses model substitution.

Temperature .7, top-p .95, top-k disabled, thinking disabled, maximum 12 new tokens, seed per request. Parse only a stopped output whose stripped text is exactly 0 or 1. Smoke gate checks construction, model identity, complete transport, and at least 95% parse yield in each request kind; correctness is not a gate. Three infrastructure failures stop collection without retry; 5,400-second wall limit per stage. A process timeout wrapper also covers stalled generation. An incomplete pilot cannot produce GO/NO-GO scientific evidence.

## Independence and evaluation splits

Repetitions 0–3 use paraphrase 0; repetitions 4–7 use paraphrase 1. Within each half, option order alternates, giving balanced response digits conditional on every true preference. Primary transfer uses only preferences 0–1, repetitions 0–3 for selection, and preferences 2–3, repetitions 4–7 for evaluation. Thus neither evaluation preferences nor evaluation paraphrase is reused to label/calibrate a format. Group gap stability across all preferences and independent halves is a separate descriptive diagnostic.

The label-free agreement selector consumes an allow-listed answer projection and compares unbiased pairwise signed-answer agreement across the first two preferences (4 responses/format/preference). Ties select A. It is a simple discovery probe, not the theory's information-optimal policy; systematic wrong answers can fool it. Audit-only labelled-calibration selection receives true labels for the prefix and is evaluated on different preferences/phrasing. A leave-one-profile-out global-format audit reference uses only other profiles' prefix correctness. Those references are explicitly unavailable as online policies under the information boundary.

Direct and metadata reports each use two independent phrasings and counterbalanced format-digit mapping. Variant 0 is the primary choice, variant 1 a wording check. Do not choose the better variant after outcomes. Type-choice accuracy uses held-out non-tie group labels and reports ties/invalids and all 48 groups. The finite-data group label is noisy and is not a known theoretical z_g.

## Baselines, controls, costs

Report Fixed A, Fixed B, Round-Robin (two held-out repetitions from each format), Direct Type Query, Public Metadata Predictor, observation-only agreement, the LOPO global audit reference, labelled-calibration oracle reference, and hindsight oracle reference. Hindsight picks the best format on evaluation outcomes; its score is optimistic and only descriptive. Accuracy measures held-out single-response reliability, not eight-preference exact accuracy or an equal-total-query-cost adaptive-agent comparison. State all prefix/type-query costs separately; no cost-free self-report claim.

Negative control: 499 seeded shuffles of group membership within each profile, separately permuting the four calibration preferences and the four evaluation preferences into two pseudo-groups with two of each. Keep all answers and labels unchanged. Apply the same labelled-calibration selection and evaluate transfer; report every profile, never select favorable shuffles. Shared global gaps can survive shuffling; the real-minus-shuffled contrast isolates the additional group value.

## Statistics and prespecified development decision

Resample profiles with their entire groups, preferences, formats and repetitions, 10,000 bootstrap draws, fixed seed. Do not treat 3,072 responses as 3,072 independent experimental units. Baseline intervals are descriptive 95% percentile intervals. For five primary endpoints use Bonferroni marginal 99% intervals (approximate family 95% coverage; 24 clusters remains limited).

The five primary quantities are (1) product of independent-half group gaps; (2) labelled transfer minus shuffled transfer; (3) observation-only selector minus LOPO global reference; (4) observation-only minus direct; (5) observation-only minus metadata. A conservative `GO_TO_PHASE2_DESIGN` requires complete collection, >=95% valid yield, lower interval >0 for (1), and lower interval >.02 for (2)–(5). All other complete results are `REVISE_OR_NO_GO`, not a theorem refutation. These thresholds are a resource-allocation screen, not an assertion of statistical power or a necessary condition for every possible future algorithm. A positive labelled transfer with weak agreement is structural evidence with an open learning problem, not proof that no algorithm can work. Never optimize on or recycle these profiles as confirmation.

## Reporting limits

Retain raw outputs, invalids, unattempted counts, cell-level all-wrong/same-answer behavior, group gaps, direct/metadata mistakes, deterministic first-12 failure examples, and both positive and negative gates. Answer agreement is not correctness. Fresh seeded contexts do not eliminate item-specific systematic error. No iid/common-channel claim follows from aggregate accuracies; verify those assumptions separately before using theoretical constants. No cross-model robustness statement until a frozen independently authorized replication exists. No human-behavior or asymptotic-optimality claim from this development pilot.
