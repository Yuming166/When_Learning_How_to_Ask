# Initial independent design audit: recommendation development loop

Date: 2026-11-03. Status: **appropriate for a bounded DEVELOPMENT pilot after the implementation gates below; no confirmation, method promotion, or optimality conclusion.** This is an independent assistant design pass within the same project. It is not external expert review, statistical certification, or a review of results.

## Material Passport and read boundary

- Task: audit the proposed recommendation policies, common stopping gate, controls, data boundary, pairing, and reporting before observing new outcomes.
- Authorized scope: local read-only source/design inspection and this report; CPU only; no network, APIs, models, training, generated test-world outcomes, or future result files.
- Material actually read: the four sources below. No main recommendation-loop implementation or new experimental result was available to this initial pass. A later code review must not be implied by this document.
- Planned design, as communicated by the owner: `p=4/5`, `q=3/5`, `eta=1/100`, `M=0`, exact `R=3`, online cap 2,000; five arms; two catalogues × two profiles (anchor plus seeded) × two partitions = eight paired worlds and 40 trajectories. These contain four profile clusters, not eight independent users or 40 independent samples.
- Current judgement: the model and common-certificate comparison can support a useful small mechanism pilot. Sample-efficiency findings will be descriptive and specific to these profiles, rates, catalogues, and finite cap.

Sources and SHA-256:

| Source | SHA-256 |
|---|---|
| `research/top1_decision_theory_20261103/THEORY_RESULTS.md`, especially §2 | `8c4e15564fe8c511c76e8ae78f84816f09d6d881f2e462565100385602271441` |
| `research/general_catalogue_theory_20261103/GENERAL_THEOREM.md` | `2177909547019acb357c79ccef631517537a5f55f8d6223e4d6fdaf27d638332` |
| `experiments/phase2c_strong_baseline_20261031/DECAYING_BASELINE_SPEC.md` | `38e52edc28946f8f87679763ad694539fe0e3cc3189af7d4fa69b450ba5ae8a9` |
| `experiments/phase2d_method_improvement_20261031/CERTIFIED_STOPPING_SPEC.md` | `33d90c9b128254e054a87fa99e54e678e66ff5f761c34a907c2ebafd3fb16ea0` |

## 1. Theory and implementation contracts must stay separate

The decision information program minimizes against **all minimal decision-changing flip sets and all alternative group-type assignments**, with continuous candidate rates `1/2 <= v <= u <= 1-eta`. A recommendation can require several simultaneous sign flips. Reusing only the singleton alternatives from full-profile recovery is invalid. Conversely, including all wrong profiles is valid but yields a different, full-profile allocation objective; that is a useful ablation rather than the proposed decision allocation.

The general-catalogue results are asymptotic statements at `alpha=0` and the fixed state in question. `M=0` fits that calibration regime. The zero/positive premium geometry, coefficient diagnostics, or oracle-optimal good-format allocations do not predict a finite-budget win at `R=3`. In particular, the unknown-type optimum may use both formats, even at `M=0`. A good-format-only restriction in the decision allocator would silently change the optimization problem. The type-only oracle knows `z`, not `p,q,theta`; no policy or unlabelled reference coefficient may receive true rates or formats.

The framework attainment argument in the top-1 note uses forced-only estimation and a vanishing-actual-error tracking contract. The proposed all-count joint MLE, fixed floating solver tolerances, finite quadrature, and finite cap are development adaptations. An exact stopping certificate does not prove their estimator tails, allocation convergence, coefficient optimality, eventual stopping, or finite expected cost. Call the implementation “estimated-state decision-KL allocation” and report its solve diagnostics; do not claim it implements the theorem's full attainment proof.

**Accepted owner change:** use raw continuous joint MLE, with no grid perturbation. Whenever fitted `p-q <= 1e-8`, every target-based arm (joint-MLE D-RRC adaptation, profile-KL, decision-KL) uses the same frozen uniform-over-both-formats fallback, with its reason logged. This makes the boundary behavior concrete. The threshold is an algorithm parameter, not an exact-identifiability theorem or a repair that converts the rates into an interior MLE. Large enough errors or failures in a KL solve need a separately frozen, logged fallback; they must not silently receive an arbitrary allocation.

## 2. The common decision certificate is the main correctness gate

For each item `i`, form its likelihood class by maximizing over **every** sign vector whose public catalogue winner is `i`, and over every group-type vector. Profile the continuous rates analytically using exact rational clipping/pooling, including the `p=q` boundary. Enclose each profile log likelihood, then each item maximum, with outward Decimal bounds. For any candidate item, the candidate class lower bound minus the maximum competing-item upper bound must strictly exceed the full threshold upper bound.

A single selected sign profile versus wrong-item alternatives can be conservative, but it is not the complete item-class GLR and need not have the claimed pathwise advantage over a profile gate. A floating MLE profile must not determine the set of item-class alternatives. All item classes, including profiles that share the current recommendation, need correct aggregation. A constant public decision map should return its unique item without querying; it must not be manufactured by deleting hard states from an otherwise nonconstant catalogue.

Here the threshold is exactly `3 + sum_e log(N_e+1)` because `M=0` and there are no type-report streams. Counts are all observed task counts, independent of whether they were forced or exploitative. A rate-domain endpoint derived from exact `eta=1/100` should be recorded as `99/100`; interpreting a Python float as its exact binary value is also coherent, but a different contract. Freeze and record the interpretation instead of mixing it between fitting, allocation, and certification.

**Accepted owner changes:** implement and test the `d=6` gate separately; aggregate all states by item exactly; attempt the same common gate after every action for all five arms. The historical Phase2d prototype explicitly supports `d<=4`; merely importing it or increasing a size check would not verify the extension. Shared/split `d=6` cases can remain numerically small, but each supported partition and total state count must be checked explicitly.

An unbounded floating prescreen may miss a true crossing. If used only as a speed shortcut, it must have a proven conservative exclusion bound or be disabled for the common per-action comparison. Otherwise different policies can acquire different stopping opportunities through a computational artifact. Arithmetic overlap, failure, or unsupported input gives continue/abstain, never a floating certificate. At the cap, an uncertified best guess remains an uncertified best guess.

The mathematical risk implication is for the specified fresh independent observation model, predictable action choices, fixed pre-observation risk setting, and the stated arithmetic trust base. `R=3` corresponds to `delta=exp(-3)`. Tiny empirical zero-error counts neither validate that risk level nor imply a stronger one. Grouping profiles by the public decision map does not relax the observation assumptions.

## 3. Controls and attribution

| Arm | Necessary interpretation and control |
|---|---|
| Round robin | Fixed public action order; the same unit acquisition cost, count interface, exact gate, and cap. State whether it has any target-update computation. |
| Joint-MLE D-RRC adaptation | Equal coordinate mass on the estimated better format, plus common forcing/tracking/fallback. The historical D-RRC uses forced-only estimates; this adaptation should not be named as an unchanged historical implementation. |
| Quadrature decision information gain | Greedy information about the **recommended item**, not full signs or types. Publish priors, rate triangle/weights, posterior normalization, predictive update, quadrature order, cadence, and tie rules. Integrated posterior inference and an MLE plug-in posterior are different arms. |
| Full-profile KL allocation | Same joint MLE, continuous rate domain, solver budget, forcing, tracker, update cadence, numerical safeguards, gate, and cost as decision-KL; only the alternative decision target changes. |
| Decision-KL allocation | Correct estimated-state minimal flip family, every alternative type assignment, both formats available, and a continuous-rate inner minimization. Record estimated objective, feasibility/separation diagnostics, and fallback frequency. |

The cleanest component contrast is profile-KL versus decision-KL under the shared implementation controls. D-RRC versus decision-KL also changes coordinate allocation and solve complexity. Quadrature decision-IG versus joint-MLE decision-KL changes inference and action objective together; it cannot identify the causal effect of either component on its own. Round robin is a simple reference, not an estimator-controlled ablation.

All policies must receive only observed counts and public structure: dimensions, partition, rate domain, catalogue, and declared risk/control constants. True signs, generating rates, current true formats, profile seed, outcome streams, true flip family, true oracle coefficients, and success feedback belong only to the harness/evaluator. No direct self-report or type-question action is allowed in this model. A useful negative check changes private metadata while keeping counts and public structure identical and requires identical actions/targets.

## 4. Exploration, target tracking, and planner accuracy

The communicated forced schedule uses `L=2d` and blocks `L*n^2,...,L*n^2+L-1`; the target update schedule is `t + max(L,ceil(sqrt(t+1)))`. Record these as the new common schedule. Check initialization, completed-time indexing, and the first block explicitly, as an off-by-one can omit an action or call the policy after stopping. Every task-format stream needs unbounded forced counts on an uncapped continuation; “exploration is sqrt(t)” alone does not establish per-stream coverage.

Target tracking must accumulate the actual target vectors over time. Tracking `t*w_current` after a target change is different and can erase previous deficits. Forced samples still enter actual counts; normalization and deficit bookkeeping must use the same convention across arms. The next action must be chosen from completed observations before its new answer is generated or retrieved.

For decision-KL, recompute the public decision map's flip family at the **estimated** sign vector; do not reuse the all-positive anchor's family once the estimate moves. A general catalogue can have different minimal families at different states. Checking the full wrong-item set instead is a valid small-state reference for validating the reduced family. Reducing type assignments using a result proved only for true-good-format allocations must not be used for the unrestricted two-format online problem.

Fixed solver tolerance, stale-target updates, and finite quadrature are acceptable for this development pilot if visibly labelled. Log failures, returned residuals, target normalization, chosen fallback, update time, and objective values. A solver success flag is not a continuous global bound. Claims of optimal coefficient or exact information gain need an additional actual-error argument. Quadrature refinement on deterministic count fixtures is a useful sensitivity diagnostic; high order or agreement at selected fixtures is not a uniform posterior-error certificate.

## 5. Leakage, profiles, pairing, and cache safety

Anchor profiles deliberately expose the theorem's mechanism. They should retain that label. Freeze the seeded-profile generator, seed list, catalogue coefficients, partitions, type assignments, cap, and all policy/numerical parameters before the one bounded run. Generate profiles without inspecting comparative outcomes. Retain seeded profiles even when they duplicate an anchor, are easy, or give an inconvenient geometry, unless a predeclared outcome-independent rule specifies otherwise. Do not replace worlds to rescue a result.

Validate catalogue uniqueness using public exact utilities on the entire sign cube. This is a mathematical catalogue check, not a new stochastic world outcome. For the genuine three-item catalogue, retain all three active classes and all six relevant coordinates. Do not use a relabelled threshold surrogate. Positive/zero premium labels must be state-specific and use the proper unknown-rate, type-only-oracle definition; the split label by itself is insufficient for an arbitrary seeded profile.

For a paired world, each public task action should have its own conditionally independent answer stream. Every arm reads the same action-indexed stream by its own count for that action. The kth call to one action must be independent of the kth call to another action. This preserves valid marginal experiments while inducing useful across-arm pairing. Different action trajectories need not receive identical forced samples or MLEs. The entire answer stream and seed remain unavailable to policies.

Within a catalogue/profile, shared and split partitions are related structural cases; the profile cluster is the natural descriptive grouping. With four profile clusters and only one seeded profile per catalogue, do not present bootstrap intervals or p-values as broad population evidence. A paired table of all eight worlds plus per-catalogue/profile summaries is more informative than a single pooled percentage.

Caches must preserve exact sufficient-statistic semantics. Include counts, partition, catalogue/decision-map identity, exact rate domain, risk constants when relevant, method, and numerical configuration in the appropriate keys. A gate cache cannot be keyed only by the selected MLE sign or item: the competing likelihoods and the threshold change with counts. Do not reuse mutable count buffers by reference. State aggregation may cache repeated channel-count likelihoods, but the gate threshold still uses the original task-stream counts.

An allocation cache must not import the hidden true-state geometry, a precomputed true coefficient, or another arm's posterior. Warm shared caches can also distort CPU comparisons through run order. Either isolate caches per arm/trajectory or report cold/warm behavior and order explicitly. Record hit/miss counts and cached computation time separately from acquisition cost; acceleration cannot be credited as fewer queries.

## 6. Censoring, failures, and the full denominator

Preserve one row for each of the 40 planned arm-world trajectories. Store separately: actions acquired, certified/uncertified status, certified item if present, optional terminal guess, true winner in evaluator-only fields, arithmetic status, cap status, policy/planner failure, and elapsed CPU/wall time. An arithmetic `undetermined` at an earlier prefix does not itself mean the whole trajectory failed if sampling continued and later certified. A final cap with no certificate remains uncensored with respect to observation count but **right-censored with respect to eventual stopping time**.

Report `min(tau,2000)` as capped/restricted acquisition cost. Do not report a cap as a completed stopping time, drop capped worlds, compute mean cost only among successful certificates, or compare only the subset where one arm succeeds. For each paired comparison retain the two certificate statuses next to the capped cost difference. A lower capped mean can coexist with poorer certification, and the design must show both. An early computational crash is a failure row, not cost zero and not a statistical cap.

Report certified-correct, certified-wrong, capped-uncertified, and computationally failed denominators separately, plus any uncertified terminal-guess errors. Keep query counts, forcing overhead, estimation/planning cost, gate cost, and total runtime distinct. A query-efficient policy can be CPU-expensive. Uniform time watchdogs, if necessary, should be declared before execution and their triggered paths retained; no arm gets an outcome-dependent retry.

## 7. Minimum implementation evidence before the bounded run

These checks use deterministic count fixtures or public catalogue calculations and do not require consuming new world outcomes:

1. Exact profiling fixtures cover separate means, order violation/pooling, missing channels, `p=q`, `q=1/2`, upper clipping, and exact endpoint semantics. Every supported `d=6` state/type combination is included in the coverage calculation.
2. Item-class aggregation agrees with an independently computed complete profile table. Same-item alternative profiles are excluded only from the competing-item maximum. Candidate selection remains safe under ties/interval overlap.
3. A constant decision catalogue, a full-profile decision map, and a nontrivial multiple-flip catalogue recover the intended gate/alternative behavior. Fixed-action transcript fixtures check the decision gap is at least the full-profile gap under the same threshold.
4. Hostile ambient Decimal settings, finite precision escalation, arithmetic failure, and overlapping intervals cannot produce a certificate. Every arm invokes the common gate after every completed action with the same exact inputs.
5. All target-based arms share joint estimates on identical counts, common near-equality fallback, forcing schedule, cadence, and cumulative tracking semantics. Counts/public inputs alone determine the next action; private metadata and evaluator feedback cannot affect it.
6. Decision-KL's minimal-family reduction agrees with enumeration of all wrong-item states on deterministic fixtures; profile-KL differs only in its intended alternative target. Both retain all alternative types and continuous rate profiling.
7. The runner freezes eight worlds and all 40 trajectory slots before outcomes; validates independent per-action stream construction without revealing streams to policies; and preserves caps/failures in its output schema. It must not silently reuse confirmation seeds or historical frozen result paths.

The initial design is suitable for the stated finite development exercise with these safeguards. Results can motivate a later revision or a separately authorized confirmation design. They cannot by themselves establish general recommendation effectiveness, natural-user reliability, a new allocation theorem, or a promoted main method.

## 8. Nonblind implementation review before pilot freeze

This appended pass inspects the owner's implementation and disclosed design changes. “Nonblind” means that the arm identities and their intended mechanisms are known; **no smoke or pilot outcomes were read**. The owner supplied a deterministic-suite receipt; this pass did not rerun that suite, invoke a runner, or generate any world or answer. Reviewed files: `policies.py`, `run_loop.py`, `PROTOCOL.md`, `config.json`, `likelihood.py`, `certification.py`, `decision_ig.py`, plus the imported `general_geometry.py` and `decision_information.py` allocation dependency chain. Static inspection is not independent numerical certification.

### Common screening amendment

The implemented common procedure screens after every answer and calls the exact interval gate when the floating decision gap is at least `beta-1`, every 50 answers, or at the cap. Only `checked_gate['certified']` stops. This is a valid conservative subsequence of exact certificate attempts under the same anytime mixture argument: the screen determines when to check and never authorizes an output. Fixed checkpoints limit neglect due to a floating false negative. The common rule can delay certification; it does not preserve earliest exact-GLR stopping or the earlier full-profile/decision stopping-time comparison as an implementation claim. This amendment supersedes this report's initial recommendation to attempt the exact gate after every answer. Screening counts and exact calls are logged separately.

### Consistent paths observed

- `JointLikelihood` validates the exact public schema, uses exact rational full-cube utility comparisons, enumerates all sign/type states, and returns a floating analytic continuous-rate fit for allocation/screening. The exact gate independently computes rational clipped/pooled MLEs and outward item-class maxima. The `d<=6,G<=2` scope is explicit; the old `d<=4` stopping function is not called. Its arithmetic primitives are imported instead. The float argmax is a numerical MLE estimate, not an exact-state-maximization certificate.
- All three target-based arms share the same all-count estimator, `p-q<=1e-8` fallback, forcing schedule, update cadence, and cumulative-deficit tracker. Raw fitted rates are passed to the planner; hidden generating rates do not fill its parameters. At fitted equality the simple D-RRC adaptation also receives the uniform-two-format fallback, as specified.
- Profile-KL uses singleton wrong-profile flips and decision-KL recomputes minimal wrong-item flips at the estimated sign state. Both call the same unrestricted two-format, all-type-pattern continuous information program, with the same tolerance and iteration budget. Both stop on the common recommendation gate. This is an allocation-target ablation; it does not compare full-profile stopping to recommendation stopping.
- The oriented planner allocation is mapped back through the estimated type mask. The per-policy cache key omits that mask correctly: it stores an oriented solution for the current flip family and fitted rates, then remaps it. Groups and rate domain are fixed within that object. The quadrature design cache stores immutable likelihood/prior arrays; each posterior has separate mutable weights.
- The harness reconstructs only `world['public']` for policy/gate construction. Private signs, types, rates, winner, and response seeds remain in the harness. Each action has a separately seeded stream; each arm consumes that action's own prefix count. No oracle state, future answer, success feedback, or direct type action enters the reviewed policy path.
- Solver nonconvergence raises and is recorded as failure rather than being relabelled convergence. Planner outputs remain explicitly float diagnostics. Caps and ordinary caught arm failures have separate statuses; failed arms do not receive zero restricted acquisition cost.

### Items to resolve before freeze

1. **Postprocessing can overwrite a valid certificate.** In the reviewed `run_loop.py`, terminal MLE and posterior diagnostics execute inside the main trajectory `try` after `status='CERTIFIED'` is set. If either diagnostic raises, the handler sets `FAILED_UNCERTIFIED` while retaining `certificate`, `certified_output`, and `certified_correct`. This creates contradictory rows and can remove a valid certificate from the main denominator. Catch diagnostic errors separately and retain the acquisition/certificate status; record a separate diagnostic failure. This is a reporting/denominator issue, not a route to an invalid certificate.
2. **One thread per worker is promised but not established by the reviewed runner.** NumPy/SciPy are imported without an internal thread limit, and no reviewed launcher establishes the limit before import. Two worker processes alone do not imply two CPU threads. Enforce or verify the declared limits and persist the effective runtime/thread settings. An external launcher can satisfy this item if its exact environment/command is part of the frozen receipt.
3. **An exceptional future can lose the full denominator.** The parent loop calls `future.result()` without handling process-level failure. A dead worker or serialization/infrastructure exception can abort summary generation and leave planned trajectories absent even though ordinary policy exceptions are caught. Predeclare all 40 slots and preserve returned, failed, and unreturned/infrastructure-failed slots without retries. Do not convert an unstarted slot to a statistical cap.
4. **Freeze the imported implementation, too.** The local policy imports `research/general_catalogue_theory_20261103/general_geometry.py`, which imports `research/top1_decision_theory_20261103/decision_information.py`; the new certificate imports `experiments/phase2d_method_improvement_20261031/phase2d/certified.py`. Freeze these dependencies in addition to local files/config/world hash. This pass did not read a future freeze manifest or assert that it already includes them.

### Limits that should remain visible

The quadrature baseline has a uniform joint sign/type prior and a continuous uniform rate prior approximated by order-six Gauss–Legendre quadrature. Its policy uses an absolute `1e-14` score tie tolerance and resolves ties by least-sampled action, then stream order. These are algorithm choices to freeze and disclose; posterior precision and greedy optimality are not certified. The profile-KL/decision-KL contrast has shared estimator/tracking controls; the quadrature-IG contrast changes both inference and allocation objective.

The configured catalogues are nonconstant. Although the gate itself supports constant decisions, the reviewed runner first checks after an answer and therefore would not return at zero queries for such a future catalogue; the protocol's zero-query statement is a gate capability, not a verified runner behavior. This does not affect the current eight-world design.

The observed private/public boundary and stopping paths are consistent with the intended pilot. Resolve the concrete failure-accounting/thread/freeze items above before declaring the code frozen. This pass provides no new outcome evidence and no claim of external expert certification.

## 9. Source-verified dispositions before freeze

The owner supplied corrections, and this follow-up inspected **only the revised `run_loop.py`**, SHA-256 `7854a033453370335a4ebeb69d528bda650cfbc2fe9dc68426685520ea9d860e`. No smoke/pilot artifacts, generated worlds, outcomes, or freeze manifest were read; no runner or stochastic test was executed. Earlier findings remain above as the review history.

- **Certificate retention: addressed in source.** Exceptions after a non-null stopping certificate now populate `postprocessing_failure` without replacing `CERTIFIED`, the certificate, output, or restricted query cost. This resolves the contradictory certified/failed row identified in §8. A diagnostic exception after an uncertified cap is still classified as `FAILED_UNCERTIFIED`; its acquired count remains available, while restricted cost is null. Preserve this distinction in reporting rather than interpreting every failure as an early acquisition failure.
- **CPU/thread scope: addressed for the intended fresh CLI execution.** `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` are set to one before NumPy and the numerical dependencies are imported. The process-pool initializer pins each worker to one CPU chosen from the first two currently allowed CPUs. Each trajectory records affinity and the three principal BLAS/OpenMP environment values. The source establishes the requested restriction; this pass did not execute it or measure an effective library thread count. The initializer permits both workers to select the same CPU, so no claim of distinct CPU placement or isolated wall-time measurement follows.
- **Exceptional-future denominator: addressed in source for handled submission/result exceptions.** The runner writes `planned_jobs.json` before submission; catches per-job submit exceptions and future-result exceptions; and collects explicit `FAILED_INFRASTRUCTURE_UNCERTIFIED` rows with unknown query counts represented by null. These rows contribute to the failure count and are neither retried nor converted to caps. The predeclared job list also survives an unhandled parent-process interruption; such an interruption still requires reporting any absent completions against that list.
- **Imported dependency binding: verification path added; manifest creation remains owner work.** Pilot startup now checks both local `source_sha256` entries and repository-relative `dependency_sha256` entries, followed by the generated-world hash. This is the required mechanism for the imported solver/arithmetic chain. The final manifest must include all three paths named in §8; its existence and entries were deliberately not inspected in this pre-freeze pass.

No unresolved source-level blocker from the four §8 items remains for the bounded pilot, conditional on the final dependency manifest being populated and the disclosed execution/reporting limits being retained. This is source inspection, not a new execution receipt, result endorsement, external expert review, or confirmation approval.
