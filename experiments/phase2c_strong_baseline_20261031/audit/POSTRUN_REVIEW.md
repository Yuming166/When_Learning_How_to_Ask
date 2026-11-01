# Phase 2c post-run execution and analysis review

2026-10-31. Bounded read-only review of the completed development batch, public commitments, raw trajectory rows, analysis artifacts and generated reports. The reviewer did not run a new scientific world, open or hash the private seed/reproduction file, rerun the main batch, change a frozen file, or consume confirmation data. Ground-truth format orientation for diagnostic recomputation was taken from existing post-run Format-Only Oracle fit outputs.

**Artifact-consistency verdict: PASS. Research-readiness verdict: GO for independent confirmation of the scoped numerical restricted-cost hypothesis, subject to a separate resource/execution gate; no automatic launch.** This is not confirmed effectiveness. Results support a development advantage in selected positive-premium settings and retain clear finite-R losses, censoring, computation costs and numerical limitations.

## Commitments, denominators, and costs

The persisted pre-seed source commitment hashes to the value linked in `freeze.json`; its fields are preserved in the final freeze. Every frozen source/config/protocol file and frozen audit hash matched at review. The private seed commitment was checked by the trusted integrity task, as recorded in `VALIDATION.json`; this reviewer deliberately did not open or hash that private file.

Raw rows contain **640 unique policy/world identities**, 128 per policy, representing 128 independently indexed development worlds and 16 cells with eight worlds each. All row-level task/type/offline totals match the execution receipt and analysis facts exactly:

| Quantity | Verified value |
|---|---:|
| Main trajectories / independent worlds | 640 / 128 |
| Completed / censored / observed wrong certificates | 637 / 3 / 0 |
| Main task queries | 1,894,181 |
| Main paid type queries | 30,827 |
| Main online actions | 1,925,008 |
| Per-policy charged offline observations | 652,800 |
| Unique-world offline reference observations | 130,560 |
| Main total charged acquisition | 2,577,808 |
| Main elapsed wall seconds | 1,412.986 |
| Main retries / model calls / confirmation worlds | 0 / 0 / 0 |

Observed main work remained below the frozen online allowance and 1800-second work deadline. The five policies share reference samples within each world; 652,800 is the sum of compared policy acquisition charges, not a claim of that many independent reference observations. Independent statistical units number 128, not 640.

`VALIDATION.json` reports all 640 terminal GLRs recomputed, 295 historical files unchanged, pairing/count/cost/censoring/forced/tracking checks passed, and six exact existing-path replays matching records and transcript hashes after timing removal. Validation took 42.954 wall seconds; its existing-path replays took 40.615 wall seconds and charged 55,365 task + 923 type + 384 offline observations. Those are replay computation/acquisition costs, not additional independent scientific worlds or a second development batch. Technical preflight costs remain separately recorded from the main batch.

## Primary comparison recomputed from raw rows

Every one of the 16 Aligned-minus-D-RRC paired difference vectors and cell means matched `paired.json` exactly, with eight pairs retained per cell. The R=1024 values below were independently reconstructed from the raw costs before comparison with the analysis outputs:

| Partition | alpha | Premium | Aligned mean cost/R | D-RRC mean cost/R | Mean (A-D)/R | Relative restricted-cost reduction |
|---|---:|---|---:|---:|---:|---:|
| [1,3] | 0 | positive | 7.027344 | 14.824219 | -7.796875 | 52.60% |
| [1,3] | 3 | positive | 6.476563 | 14.640625 | -8.164063 | 55.76% |
| [4] | 0 | zero | 5.203125 | 5.203125 | 0 | 0% |
| [4] | 3 | positive | 4.800781 | 4.980469 | -0.179688 | 3.61% |

All these R=1024 primary paths completed within their cap. The estimand remains the prespecified restricted cost, and the eight-pair bootstrap intervals are exploratory and not multiplicity-adjusted confirmation.

The full [4], alpha=0 control has **32/32 existing worlds across all four R values with identical Aligned/D-RRC online cost, task counts and transcript hashes**. No performance gap was manufactured in the configuration where their ideal uniform-good targets can coincide. This observed identity is not a proof of zero difference or variance for every possible future numerical trajectory.

Positive premium is not sufficient for a finite-R advantage. For [4], alpha=3, the retained Aligned-minus-D-RRC mean differences are:

| R | Mean (A-D)/R | Exploratory paired 95% bootstrap interval |
|---:|---:|---|
| 16 | +2.125000 | [1.0000, 3.3750] |
| 64 | +0.375000 | [0.1875, 0.5625] |
| 256 | +0.101563 | [-0.0469, 0.2891] |
| 1024 | -0.179688 | [-0.2305, -0.1328] |

Thus Aligned loses in observed mean at R=16,64,256 in that positive-premium setting. The two [1,3], R=16 mean advantages also have exploratory intervals crossing zero. Within this limited grid, nonzero large-R gains occur in positive-premium cells and the zero-premium control ties. This is a necessary-looking empirical pattern on these configurations, **not** a universal necessity theorem or a sufficient condition for finite-budget superiority.

All 30,827 paid type actions were purchased by Aligned; D-RRC purchased none. The action set and offline information were equally available, but the scientific contrast includes this purchase decision. It does not identify a pure task-reweighting effect holding purchased type information fixed.

## All three censored paths retained

All censoring occurs in [1,3], alpha=3, R=64, with a common cap of 2048:

| World index | Policy | Online cost | GLR gap | beta | Correct terminal guess? |
|---:|---|---:|---:|---:|---|
| 310503 | D-RRC | 2048 | 15.12815 | 110.69259 | yes |
| 310503 | Aligned Tracking | 2048 | 12.84032 | 120.12354 | yes |
| 310507 | D-RRC | 2048 | 27.93873 | 115.74714 | yes |

These are three censored trajectories, not two and not certified successes. The paired cell includes the two capped values for world 310503 and the capped D-RRC value for world 310507; no completed-only primary filter is used.

At world 310503, Aligned's last forced-only estimator has one type error despite a correct sign estimate and 401 paid type reports; its target estimator intentionally ignores those reports under the shared frozen definition. D-RRC's last estimator has one sign and one type error, even though its separate full-likelihood terminal guess is correct. World 310507 D-RRC has a last type error. Estimator correctness, decoder guesses and passing the stopping boundary therefore remain distinct observations.

The Aligned censored path has population information/R about .4982 versus beta/R about 1.8769; its estimated model's numerical solver gap is small while its true-parameter information deficit at K is large. This is a retained example where solving the estimated information program accurately does not repair a finite-sample type-estimation error.

## Population information and remaining gap to K

All **128 Aligned** trajectory diagnostics for last-target information at K, empirical-allocation information at K and actual-count population KL/R were recomputed from existing rows and Oracle-format outputs. Every recomputed readout matched the stored artifact exactly. These recomputations check artifact scaling/indexing/orientation; the earlier separate 60-state SciPy check supplies an independent numerical formulation check. Neither is a proof of the general theorem.

At R=1024 the mean Aligned excess over its true task+type coefficient K is approximately 21.79%,24.53%,8.16%,12.86% in the four table configurations. The corresponding diagnostic ranges are:

- Forced fraction: about 3.39%–4.09%.
- Final beta/R: about 1.0420–1.0710.
- Empirical allocation information deficit at K: about 3.04%–11.39%.
- Last-target information deficit at K: 0%–9.69%.
- Last theta/type error counts: zero on all 32 Aligned R=1024 paths; earlier errors and lower-R failures remain in the histories.

These are concurrent diagnostic readouts. They do not add to a causal explanation of the observed excess cost, and an L1 distance to one chosen optimizer is not a distance to the full nonunique optimal set. The report preserves both distinctions. Forced exploration, evolving estimates/grid, target tracking and the enlarged stopping boundary remain plausible finite-R mechanisms, not separately identified causal cost shares.

There were 10,149 Aligned updates, with maximum Aligned online cost 9536. **Every requested solver tolerance was still exactly 1e-4**, and the largest actual numerical relative gap was 1.11346e-4. No numerical-floor activation occurred. Thus this batch supplies no observation of the requested schedule leaving its initial plateau, no evidence of infinite-horizon vanishing optimization error, and no interval-certified executable GLR guarantee.

Aligned used 790.69 worker CPU seconds versus D-RRC's 128.27; the main batch's target/planning CPU summed to 762.84 seconds. The observed online-query savings cannot be called a computation-time improvement. CPU, wall time, query cost and charged acquisition remain separate quantities.

## Confirmation sample size, decisions, and readiness

`confirmation_plan.json` applies the design rule fixed before development outcomes. The positive [1,3], alpha=0, R=1024 cell has paired SD 1.5171085; multiplying by 1.5 gives 2.2756628. Using the **prespecified effect -0.5**, not the observed -7.796875, the one-sided noncentral-t planning calculation gives:

\[
\operatorname{power}(164)=.7987491<.8,
\qquad \operatorname{power}(165)=.8011617\ge.8.
\]

The independently recomputed smallest admissible integer is therefore **165 positive-premium worlds**. The zero control's observed SD is zero, so the fixed minimum rule supplies **24 zero-premium worlds**. This is 189 future worlds and 378 two-policy trajectories, with the correctly calculated hard online ceiling

\[
(165+24)\times2\times24576=9,289,728.
\]

This resource budget is conservative relative to using the much larger observed mean effect without SD inflation. It is **not a guaranteed conservative power design** under unknown tail behavior: SD comes from only eight development pairs, the 1.5 inflation is a planning choice rather than a confidence upper bound, and t/noncentral-t calculations remain model-based approximations. The displayed zero-control power 1.0000 is the plug-in zero-variance model output, not demonstrated true 100% power or a variance-zero theorem. The minimum 24 and explicit zero-SD caveat are retained.

The nominal two-claim family allocation remains internally consistent: positive superiority uses a one-sided 97.5% paired t upper bound; zero equivalence uses TOST at per-test .025, or containment of a two-sided 95% paired t interval in +/-0.25. Bonferroni family error <=.05 is conditional on the stated interval assumptions, not a distribution-free finite-sample certificate. Prespecified restricted-cost censoring, >5% censoring interpretation guard, wrong-certificate guard, incomplete-infrastructure rule, unfavorable and inconclusive outcomes are preserved.

The nine-million-action future ceiling exceeds this development batch's planned maximum and requires its own explicit resource/wall allowance and source/protocol freeze. None is inherited as permission to launch. Confirmation can test the frozen numerical policy's synthetic restricted-cost hypothesis; it cannot certify exp(-1024) executable correctness, asymptotic optimality, natural-LLM reliability sharing, human benefit, or universal baseline superiority.

The project receives **GO to prepare the specified independent numerical-policy confirmation**, with resource/execution feasibility checked before any new seed. The present status remains `FROZEN_NOT_EXECUTED`, with zero confirmation worlds consumed. No further run, cap change, seed generation or automatic Phase 3 is authorized by this review.

The theory verdict remains distinct: the bounded adversarial proof audit gives **PASS** for the mathematical information lower bound and checked coefficient identities, **CONDITIONAL** for ideal real-arithmetic expected-time achievability under its stated oracle/predictability/uniformity premises, and **GAP** for strict floating-program risk and infinite-horizon optimality. Its arithmetic counterexample defeats a global enclosure interpretation of the current guard; it does not show that an observed main endpoint was wrong or that the main error probability exceeded delta. Independent confirmation cannot fill that proof/finite-arithmetic GAP. The five-question `RESEARCH_DECISION_CN.md` was also checked against the raw/analysis values and retains these scopes and all three censored identities.

## Reviewed artifact provenance

```text
freeze.json
ae8337cd300e07f69460854b04473b04fece4bf455726098e8eaf2b996e15509
artifacts/preseed_source_commitment.json
eaef8622014ed57c8ef1b3891ae62e9a3d92b48ed250a95e69d8fc54c9c336ae
artifacts/run/execution.json
bd1a089439d7213569fc8d828bb08c8d8aac71201815065f88d4d8c303316ccb
VALIDATION.json
9a1ef967facb4cafe962715fd45e438cac03ac0a38b6ac2644e7bb4e50114adc
artifacts/analysis/facts.json
d902956f2945f6bee9aee17bc6234fceacfbb26ba08758fd6b80b57779b1f122
artifacts/analysis/paired.json
f12655791b9a2ff875bfbd3f8ef88343503683b64305267671ee4c1bf1b8ef5d
artifacts/analysis/diagnostics.json
eefc59b4ce50904f1ce331ba5f6888b63c102eb7415ac83f8a21fced4d7a41b6
artifacts/analysis/confirmation_plan.json
4431e8d20a1ceb39f1ae2b448490136f18b0229acb20e4e29196b0143b85a972
```

This review adds only `audit/POSTRUN_REVIEW.md`; all frozen source, protocols, previous reviews and experimental artifacts remain unchanged.
