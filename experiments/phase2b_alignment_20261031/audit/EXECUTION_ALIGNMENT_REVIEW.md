# Phase 2b execution and alignment review

## Material Passport

- Scope: independent source/protocol review and bounded public fixtures. Read raw Theory Note, historical implementation, current request, and the new source as it becomes available; do not use peer reports as input.
- Write authority: this file and `audit/execution_checks.py` only. No main batch, private seed reads, external calls, old-source edits, or historical-artifact edits.
- Final source gate: **GO FOR THE SINGLE FROZEN 320-TRAJECTORY DEVELOPMENT DIAGNOSTIC**, under the inspected numerical/protocol limits. No blocking hidden-parameter, action-class, log-risk, budget, interrupted-cost, or censoring defect was found in the inspected paths. This is not approval of a theorem, exact machine optimality, or empirical convergence. The independent mathematical gate remains separately owned.

## Theory-to-historical-code correspondence

The raw reference is Theory Note Sections 4.2–4.3, lines 200–246. Source agreement alone does not close the expected-stopping-time proof, which is a separate mathematical task.

| Requirement in the note | Historical Phase 2a implementation | Audit implication |
| --- | --- | --- |
| Deterministic O(sqrt(t)) forced exploration, with each task stream at least c sqrt(t) observations | Separate forced counts and threshold .5 sqrt((t+1)/d) | Same scaling for fixed d; maintain explicit forced observations rather than total adaptively selected counts |
| Sign from the two forced empirical means | Same sign-of-sum rule | Agrees, including deterministic zero tie handling |
| Type from group-oriented forced empirical means; average good/other rates | Three alternating likelihood iterations with calibration and type-report assistance | Observable but a different estimator; cannot attach the stated forced-only estimator proof without justification |
| Deterministic increasingly fine interior grid | Continuous vanishing gap floor | Consistency may be plausible, but it is not the specified grid construction |
| Information program at current estimate and alpha=M/R | Fixed 32-action updates and tolerance 2e-6 | Finite lag and fixed numerical accuracy require separate treatment; a nonvanishing tolerance does not prove exact K attainment |
| Exploitation samples from normalized optimal action counts | Deterministic cumulative-deficit selection | An alternative tracking construction; randomized-policy martingale proof is not automatically a proof of this code |
| Every observation enters continuous joint stopping likelihood | Full task/type/calibration data used for stopping | Preserve this part; forced-only estimation does not mean discarding exploitation data from the GLR |

The new sampler should expose these differences explicitly, including a vanishing optimization tolerance, any exact cache key/update rule, the grid sequence, forced-count bounds, and its independent algorithm RNG. The same GLR and calibration must be used across the five policies, with only Oracle receiving true types.

## Budget and runtime design

The original provisional grid of three partitions, two alpha values, four R values, eight profiles per cell, and five policies would create 960 trajectories. With cap=max(4096,64R), its worst-case online count is 21,626,880 and offline acquisition count is 979,200. A 16-action GLR cadence would permit 1,351,680 checks. That is materially larger than the prior bounded batch, before sampler planning costs.

The root's reduced, preseed diagnostic proposal is defensible: d=4, partitions [1,3] and [4], alpha=0/3, R=16/64/256/1024, four fresh independent worlds per cell, policy-only pairing, five policies. This is 320 trajectories over 64 independent worlds. Dropping the intermediate [2,2] partition must be described as runtime-limited structural coverage, not as evidence about that partition.

For cap=max(2048,24R), the caps are 2048,2048,6144,24576. The worst-case online action total is 2,785,280 and offline count is 326,400. A common check interval max(16,ceil(sqrt(R))) gives 16,16,16,32 and at most 112,640 GLR checks. Check delay/R tends to zero. The 1200-second limit is a hard bound, not a promise the full batch will complete. Interleave policy runs by cell/world so a wall timeout does not leave a whole policy arm unattempted due solely to policy order.

The cap is a diagnostic resource choice, not a completion guarantee. In all prior primary cells at R=64, Direct completed 8/12 and was censored 4/12 at cap=32R; completed Direct paths reached 25.25R. Thus a large-R cap of 24R can retain substantial Direct censoring. Report completion, wrong certificates/all, conditional completed costs, and E[min(T,B)]/R. Do not call a restricted mean E[T]/R. Do not enlarge the cap, retry, or discard cells after observing new outcomes.

No prior winning cell was selected for the budget recommendation: the full primary Phase 2a cells at R=16 and 64 were inspected, including Direct censoring. The old R=64 completed N/R ranges were RR 11.75–18.75, RRC 9–20.5, Direct 5.75–25.25, Oracle 5–6, and the old tracker 6.75–13. These are only two historical independent profiles and do not predict the aligned sampler's completion distribution.

## Log-risk requirement

At R=1024, float64 `exp(-R)` is zero. Public jobs and allocation alpha must carry R directly. The GLR boundary must be R plus the original streamwise logarithmic correction, without constructing/clamping a float delta. `log_glr.py` has been source-inspected: it uses the read-only likelihood/profile routine with a benign representable delta, then reconstructs beta directly from R and all reference/task/type stream counts. The likelihood profiles are independent of the dummy delta. The underlying arithmetic remains float64, not rigorous interval certification.

## New sampler source assessment

- `TheoryAlignedTracking` copies only public d/partition/domain/type-accuracy metadata and the reference-stream lengths. It does not retain a public-state object or calibration bit values. A guarded fixture raised on every attempted calibration-bit/hidden-field read; construction and estimation succeeded without such reads. Changing all nonforced counts and contradicting all acquired type reports left the forced-only estimate unchanged.
- The sign/orientation/group-type/mean-rate estimator now follows the raw Section 4.2 construction. The empirical fixture recovered signs [0,1,1,0], types [1,0], raw p=.85 and raw q=.60. Only public metadata and deterministic task-count fixtures were used, not a generated benchmark world.
- Projection is onto an explicit ordered grid with q_index<p_index. Its mesh is (.5-eta)/ceil(sqrt(t+1)), apart from the minimum initial grid size. Tie rules and upper endpoints are deterministic. No fixed true gap is supplied.
- Exploration uses square blocks, L=2d: at times L*n^2,...,L*n^2+L-1, force each task stream once. Per-stream counts differ by at most one and scale as sqrt(t/L); total forced counts are bounded by sqrt(L*t)+L. This is a different finite constant from Phase 2a, and actual forced counts/costs must remain visible.
- This implementation deliberately retains deterministic cumulative-deficit allocation rather than randomized exploitation. Its recorded pathwise discrepancy is bounded above by 1+F and below by -(E-1)(1+F), with F forced actions. Such a separately justified deterministic extension can replace allocation-randomization concentration, but it is not a literal transcription of the note's randomized action draw. No algorithm RNG exists, so algorithm-RNG/channel-RNG coupling is absent; do not claim an independently seeded random action selector was tested.
- Replanning lag is ceil(sqrt(t+1)), hence o(t). Requested optimizer tolerance min(1e-4,1/(t+1)) vanishes. Nevertheless accepted relative-gap floor 5e-8, accepted information residual 1e-7, and inherited LP/radial/cut-deduplication floors remain fixed numerical limits. The class exposes these limits and fails rather than falling back to another sampling policy if logged numerical checks are not attained. It remains a finite-precision alignment variant, not an exact asymptotic implementation certified by tests.
- Every actual task/type answer remains in full counts/reports for the common continuous GLR. Forced-only estimation does not discard paid exploitation observations from stopping. All targets must remain active, matching joint sign recovery.

## Runner, fairness, and interrupted work

- Public jobs contain exactly R, online cap, check interval, and milestones. They omit p/q, truth, types, private index, scenario, and seed. Source imports for the aligned selector lead only to public numerical dependencies, not a generator/evaluator.
- Every cell/R/replicate gets a globally unique private world index: 64 distinct worlds across 16 cells with four profiles per cell. Only the five policies share a world. R order rotates across replicate and policy order rotates within each world. This removes Phase 2a's cross-cell profile reuse and avoids whole-arm starvation from a policy-major wall timeout.
- Each worker is spawned with a pipe and policy name, warms a public toy LP, then applies the reused single-threaded Landlock confinement before receiving a job. The evaluator is protected before the sealed seed is read. No private seed argument or new source path reaches a worker.
- Direct and Aligned share the same available known-s=.8 type-query channel and unit type-action cost. Oracle receives true types only; all samplers share the exact same GLR/calibration and log-risk boundary. The numerical margin is 1e-8*(1+log1p(online+2M)); it is sublinear in the R-scale horizon but supplies no interval guarantee.
- Snapshot counts and type reports are compared with independently retained evaluator replies. Correctness and estimate errors are calculated only after receipt in the evaluator; the learner receives acknowledgement only. Final public rows retain already-observed calibration, task counts and type reports, allowing later blind GLR recomputation without private truth.
- A bounded fake-RPC fixture separately exercised normal capped submission, worker error, and timeout. All three retained task=1,type=1,offline=4 after the same paid calls. The normal fixture remained censored; the snapshot reply was acknowledgement-only. The fixture replaced episode/environment generation and did not use a real/private world or seed.
- The runner refuses existing output, verifies source/config/audit/dependency/seed commitments, records the current failed job, and accounts for environment-cost increments in a `finally` block. It has no unconfined fallback or main-run automatic retry. The seed's fresh independent draw is executor-owned provenance. The protocol explicitly fixes `secrets.token_hex(32)` after all gates, private directory/file permissions, and public file-hash commitment. This audit inspected that public procedure; it did not open secret bytes or independently certify an unseen entropy draw.

## Final analysis, integrity, and claim scope

- Analysis refuses incomplete execution and verifies every planned policy/world identity and complete-run task/type/offline totals. Cell-wise resampling uses four independent worlds; paired differences are within-world and within-cell across policies only. No pairing is invented across independently generated R/cell worlds.
- The main statistic includes all capped trajectories and is explicitly restricted online cost/R. Completion/wrong-certificate fractions use all paths; completed-cost distributions are conditional. Censoring is marked on the cost plots. Total acquisition/R is separately drawn by adding 2M/R. Small-n bootstrap intervals are exploratory, with no multiplicity-adjusted superiority or confirmation claim.
- Population min-KL at actual unsymmetrized action counts uses true types exclusively in evaluator-side analysis after execution; it cannot choose a query. It is labelled an information-allocation diagnostic, not the empirical GLR or a correctness certificate. The source tests include an unobserved-coordinate diagnostic, which correctly has zero information.
- Planning and GLR wall/CPU fields are now recorded separately from query counts. Baseline rows have their own frozen-sampler `sampling_scope` rather than being mislabeled as the aligned extension. The independent fake-RPC fixture was refreshed for this telemetry addition and still passed.
- Source-inspected `integrity.py` checks frozen dependencies, all planned identities, full task/type/offline counts, stopping/censoring margins, pairing of episode/calibration, and final likelihood recomputation. True types are used in likelihood recomputation only for the declared Oracle. Its selected higher-R existing-world replay is separated from new scientific observations and records replay costs separately. This reviewer did not execute integrity/replay or read its private inputs.
- The protocol freezes all structural endpoints, cap/check rules, numerical floors, independent-world design, fresh-seed procedure, analysis, hard limits, and stop after this batch. The actual execution is capped and may submit explicitly censored guesses; it is not the unbounded ideal policy appearing in an expected-time theorem. Any claim about that ideal policy needs the separate proof, and any empirical claim must retain the finite-R/n4/truncation/float64 limits.
- `preflight_tests_3.log` reports 15 tests passed, including actual confined workers at R=16 and R=1024, empty/small calibration, and numerical/scheduling tests. This reviewer inspected the raw test source and the public completion log, rather than rerunning that existing suite. Independent probes in `audit/execution_checks.py` separately passed guarded calibration/metadata access, forced-only estimator invariance, finite log-risk profiling, resource arithmetic, globally distinct plan indices, and normal/worker-error/timeout cost retention. No main experiment was run by this reviewer.

## Source bindings

Relative paths are from the Phase2b root. The table binds source inspection and the bounded fixture receipts above; any changed source requires a refresh. It supplies no theorem or interval-arithmetic certificate.

| Source | SHA-256 |
| --- | --- |
| `phase2b/__init__.py` | `864525342ea24eb43904595f26a2aad937ef41a34f7658c498ac8e96062e0a4b` |
| `phase2b/aligned.py` | `67bdf86cbd21a81bde81fde981b9c00308f35d2f911af766fbd28939ae5b4ab0` |
| `phase2b/analyze.py` | `cc6908f48f64fc16dbd0217446ee2927188a8196156f4400a786177593c152c2` |
| `phase2b/bootstrap.py` | `13d26affd870793e8e32579906551bc328fa55f95e5b6dae947f08cb4b0a034b` |
| `phase2b/integrity.py` | `0d64e95258509477e6aa1323fd022325586d0b2084fd91a10300f8077ae0ffc8` |
| `phase2b/log_glr.py` | `2e24081b34fa2b783b85fe5d6d73a3e52574e5466f0fe1eb88ca0513de1233ba` |
| `phase2b/policy.py` | `ad1ffc3c65492b5ecd98e4689486a3516d5ea7563537f98f61ea3385dc89c22e` |
| `phase2b/runner.py` | `21e95303ba9bb93d22a708be8c55a3bf487c99401f3c4289ff45090785062368` |
| `tests/test_aligned.py` | `8299aafbccfbf22a130b9fff9b18b5dac16a9d7a22999f324f8d48fb45654e51` |
| `tests/test_analysis.py` | `49b7f6b627e77f09c9d2abfe47625c79643860194b7bf8ba0428bc4cee9c3ce3` |
| `tests/test_integration.py` | `4e74cecae0b1d6cc2e7aa9c1f1d619a173f548dbf0b11339738782b52d28c03c` |
| `tests/test_log_glr.py` | `381a7657eccca995e0fe13b172d41f45ef11dabbaa8dd7d732de26052c51056d` |
| `config.json` | `145a431b4672437d59c51e21ad6ac56d0a095ae34526546ffcb8c503433f864b` |
| `PROTOCOL.md` | `77fbb9bc32d88370f7ab6d2f02ea9e31b53daf734c28b26fa90ee284ffb49e65` |
| `audit/execution_checks.py` | `40e6a12b9a6c3c6675522a9739aad64a5c01fecdd4c3b8071508104428430897` |
| `../../Theory_Note.md` | `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef` |
| `../phase2a_theory_optimality_20261030/phase2a/tracking.py` | `d44b33df07fe80d517ea0488c570a8bf8cfa09ed16285baefd6a447a7d297474` |
| `../phase2a_theory_optimality_20261030/phase2a/coefficients.py` | `a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f` |
| `../phase2a_theory_optimality_20261030/phase2a/glr.py` | `7ed182834957d09546e855468fc14082d894bb54308f3ef728d591d1e4a330f6` |
| `../qrelbench_v01_20261030/qrelbench/security.py` | `bf1a9763d91d4a38a118560dc34eeed22c45ebc49bff7662f0c3d03e86e79002` |
| `../qrelbench_v01_20261030/qrelbench/data.py` | `3a19293c307d7576d895d3a332e037b3f43dc0cf37db6db1f45255d1c472247e` |
| `../qrelbench_v01_20261030/qrelbench/environment.py` | `8bb13e388b83cb2e0d85cdac80af73eca3a6229ba0fc17b61597b4b32c6e5c2c` |
| `../qrelbench_v01_20261030/qrelbench/policies.py` | `ade516e5db0d54eb6414a9402ea2ec69e019b6eff1225ffcbf0e8260e8130fe1` |
| `../qrelbench_v01_20261030/qrelbench/rpc.py` | `603ab85272d9a2da405efc2562643460288740538537f54edc0112bdac376fe9` |
| `../qrelbench_v01_20261030/qrelbench/randomness.py` | `c83448bf784126519ed8f5df0164910409dc76a7a5dc84521e21c620a054d2be` |
