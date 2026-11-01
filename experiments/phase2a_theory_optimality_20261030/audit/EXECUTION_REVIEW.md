# Independent Phase 2a execution, privacy, and fairness review

## Material Passport

- Review mode: source audit plus bounded deterministic CPU probes.
- Inputs: the user's attached Phase 2a request; `Theory_Note.md`; raw Phase 2a and reused QRelBench source. No peer review report was used as an initial or subsequent input.
- Authority: write only this review and `audit/independent_policy_checks.py`; do not edit implementation/history or run the main pilot, models, APIs, or GPUs.
- Review independence: a separately dispatched agent inspected the raw source in a shared filesystem while implementation continued. No external or cross-model review was performed. This is not independent execution of a main benchmark.
- Final source gate: **GO FOR ONE BOUNDED DEVELOPMENT RUN** under the frozen config/protocol and the source hashes below. No blocking privacy, action-class fairness, interrupted-cost, or censoring defect was found in the inspected paths. This gate does not certify the theory, exact asymptotic optimality of the implemented tracker, rigorous float64 stopping error control, or main-run outcomes.

## Findings requiring explicit claim limits

1. **The implemented tracker is a development variant.** Theory Note lines 200–213 specify a forced-only sign/oriented-mean estimator projected to a vanishing grid and randomized exploitation. `tracking.py` uses three alternating likelihood updates, assists estimation with labelled calibration and known-accuracy type reports, imposes a vanishing continuous gap floor, updates targets every 32 actions, and follows deterministic cumulative deficits. All inputs are observable and these choices are plausible, but the note's exact proof cannot simply be attached to this implementation. `policy.py` explicitly records this limit.
2. **A numerically verified coefficient solver is not a verified optimal policy.** The planner's fixed `2e-6` allocation tolerance, finite stopping checks, float64 likelihood comparisons, and unproved implementation-specific estimator/tracking bounds prevent this audit from certifying exact asymptotic coefficient attainment. Retain theoretical `K`, actual online costs, censoring, and planner runtime separately.
3. **Forced exploration has visible finite-budget cost.** In an isolated static-target fixture with d=16, 64 of the first 256 actions were forced task observations; each of the 32 task streams had two. At t=4096 the total was 256 and each stream had eight. The O(sqrt(t)) schedule has the right development scaling; this is not evidence that it improves finite-budget recovery.
4. **Theorem 3 shortcut diagnostic was corrected during review.** The initial source recorded `Gamma` as `minimum_information`. The real worst information at the oracle allocation is `min(1,Gamma)`. The tested current source reports the corrected value; a direct alternative-constraint evaluation gave 0.9999999999999977 while the recorded value was 1.0.

## Learner-only source assessment

- `InformationTracking` accepts public metadata and labelled calibration only. It reads task counts from raw returned bits, plus noisy direct type reports. No generator, private episode, seed, records, true p/q, true signs, or true types are imported or passed into it.
- Forced observations are stored separately from full task counts. The estimator uses forced task observations; the stopping/endpoint likelihood uses full task counts and all type reports. Poisoning nonforced counts in a deterministic fixture left the estimate unchanged.
- Targets are normalized over the same 2d task actions and G optional direct type actions. Per-coordinate `a_g/K` and `b_g/K`, and per-group `c_g/K`, have the correct cost interpretation. Every forced action is still a paid online task action.
- `Direct Type Query` and `Information Tracking` have the same known-s type-question channel and unit online action cost. The Direct baseline chooses to ask once per group; Information Tracking may ask repeatedly. The oracle is told types only and otherwise profiles unknown rates/signs using the same calibration.
- All six policies use one common `endpoint_mle` decoder at fixed-budget endpoints. This removes the prior M=0 decoding ambiguity: zero calibration is handled by joint continuous profiling, with no fixed default reliability substituted into the final decoder.
- `profile_glr` exhaustively profiles signs/types and analytically profiles the ordered continuous Bernoulli means. It is limited to d<=8 for sequential checks. `endpoint_mle` allows d<=16,G<=2 for endpoint decoding and returns no certificate fields. No d=16 sequential-runtime claim follows from the endpoint extension.
- "Exact" means the mathematical enumeration/profile problem. Arithmetic is float64; `interval_certified=False`. The learner applies an extra comparison margin, but this is not a rigorous rounding enclosure or a newly proved statistical error guarantee.

## Bounded probe receipt

`audit/independent_policy_checks.py` contains deterministic count/transcript fixtures; it does not generate an episode, read private evaluator input, or run a main experiment.

| Probe | Outcome |
| --- | --- |
| Forced-count estimator at empirical p=.85,q=.60, mixed signs/types, M=0 and M=100 | Exact fixture signs/types/rates recovered; nonforced-count poisoning changed nothing |
| Forced exploration/tracking mechanics, d=2,8,16, t<=4096 | Each stream reached the sqrt(t) threshold up to one observation; forced counts differed by at most one |
| M=0 common endpoint and joint GLR, d=2 | Both selected [1,0], p_hat=.90,q_hat=.60; endpoint had no stopping fields |
| Empty M=0 data | Deterministic [0,0] tie, gap=0, no certificate |
| Six-policy scripted integration, d=4, M=0, B=8, snapshots 4/8 | Every policy used eight online actions and the common endpoint decoder; Direct used six task plus two type actions |
| Capped fixed-confidence scripted integration | Eight paid actions, incomplete, no certificate |
| Corrected shortcut minimum | Recorded 1.0 matched independent full-constraint minimum to float precision |
| Evaluator fake-RPC success, worker-error, and timeout paths | All retained task=1,type=1,offline=4 after the same paid calls; capped final stayed censored; snapshot reply was acknowledgement only |

A separate one-shot local kernel probe imported the numerical backend, called `warmup_lp()`, then applied the reused `confine_worker()`. It returned Landlock ABI 4, `no_new_privileges=True`, and `single_thread_bootstrap=True`. A new open of the public Theory Note and a loopback TCP connection were both denied with errno 13. This verifies those local denial mechanisms; inherited descriptors, metadata operations, and general kernel isolation are outside that check.

## Runner and plan assessment

- `runner.py` creates learners only with `multiprocessing.get_context('spawn')`, passing a pipe and a policy name. The seed is read into an evaluator-local variable after commitment verification and is neither a worker argument nor a public job field. No private seed file was opened for this audit.
- The worker imports reviewed source and warms a public toy LP before confinement; no private episode is created in that bootstrap. Landlock setup refuses unsupported kernels or multithreaded bootstrap. No unconfined fallback exists. The evaluator calls `protect_evaluator()` before private state is constructed/read.
- Public jobs contain protocol, cap, confidence/planning delta, endpoint/check schedule, and update frequency. They omit rates, private index, scenario, seed, signs, and group types. Reset supplies known partition, labelled-calibration size, rate-domain boundary, and known type accuracy; only the declared oracle gets true types.
- Evaluator snapshots compare reported task counts with independently retained raw replies. Truth-based correctness and estimation errors are calculated only in the evaluator, written to results, and never returned to the learner. The snapshot response is exactly an acknowledgement.
- Cost increments are captured in a `finally` block after every environment call. Thus interrupted-job costs remain in the final execution receipt, independently of whether a completed trajectory row was written. The fake-RPC probe separately checked worker-error and timeout exits after the same charged calls.
- The runner refuses existing output destinations and changed source/config/protocol/dependency/audit commitments. It records retries=0, confirmation=False, model_calls=0, the current failed job, planned trajectories, completed trajectory count, and costs including partial work.
- The current config yields **132 jobs per policy, 792 trajectories, 626,688 maximum online actions, and 3,696 endpoint decodes**. These fit the 650,000-action, 3,700-decode, and 900-second declared caps. The caps bound execution; they do not promise the whole pilot will finish in 900 seconds. There are 528 fixed-budget and 264 fixed-confidence trajectories.
- All main jobs are explicitly development. The planned rates cover .85/.60 plus .75/.60 and .60/.55. Theoretical alpha values 0,1,2,3,5,10 are handled by the separate phase-map source; development trajectories use alpha 0/3 and R 4/16/64. M=ceil(alpha R) is integral here, so effective alpha equals the configured value.
- The main-policy action budget is shared across task and direct-type calls. Every snapshot reports task/type/offline/total costs. Full acquisition cost adds 2M to online cost; offline samples are not silently treated as free when that total is reported.
- Raw `tests/test_integration.py` separately specifies six actual spawned/confined workers, M=0 snapshots, and evaluator count checks. Its existing execution was not rerun by this reviewer; the independent probes above cover different deterministic failure and estimator paths.

## Analysis and post-run integrity assessment

- `analyze.py` refuses incomplete execution and checks the trajectory count against both planned and finished denominators, the planned number of fixed-budget snapshots, and task/type/offline totals against the execution receipt. A failed or timed-out pilot therefore remains a partial run; complete comparisons are not constructed from survivors.
- Completion curves use the stricter learner `complete` flag. Wrong certification incidence is divided by every trajectory in the cell. Censored trajectories enter `mean(min(online,B))`; completed cost quantiles are separately labelled conditional. q=1/2 iid is retained as in-model; persistent and asymmetric channels are explicitly out-of-model.
- Full per-cell Wilson intervals and paired exploratory bootstrap summaries are separated from pooled descriptive confidence figures. The latter explicitly label 12 paths arising from only two reused profile indices. There is no multiplicity correction or strong superiority/convergence claim.
- Theory K and observed restricted online cost/R occupy separate columns. The report explicitly explains that censoring can move restricted cost below K. It distinguishes coefficient validation from policy optimality, float64 threshold crossing from rigorous interval control, and controlled channels from natural-language reliability.
- `PROTOCOL.md` freezes the development choices, single-thread limits, all denominators, no automatic retries, explicit negative controls, private seed handling, and the stop after this one development batch. Larger follow-up and natural-language/confirmation experiments remain outside this gate.
- `integrity.py` was source-inspected only. It verifies frozen artifacts, complete planned policy/job identities, cost identities, stored-truth scores, snapshot endpoints, censoring and stopping margins, then replays selected existing trajectories excluding timing fields. This reviewer did not call it, read private reproduction files, read seed bytes, or execute a replay. Its score-check comment now accurately distinguishes stored deterministic-evaluator truth from selected replay, which regenerates catalog truth. The frozen generator/evaluator and existing-trajectory replay remain the applicable checks; this is not a new independent semantic truth audit.
- A numerical kernel/bootstrap failure is correctly a failed run, with no unconfined fallback or automatic retry. The independent standalone probe passed with BLAS/OpenMP constrained to one thread. Main-run readiness still requires the executor to preserve that documented environment.

## Source bindings for the current learner review

Paths below are relative to the Phase 2a root unless prefixed `../qrelbench_v01_20261030/` or `../../`.

| Source | SHA-256 |
| --- | --- |
| `../../Theory_Note.md` | `66d89b9131fcb29f10a5007166f80a85e9f9de47b463acda9e28f01e062038ef` |
| `phase2a/coefficients.py` | `a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f` |
| `phase2a/tracking.py` | `d44b33df07fe80d517ea0488c570a8bf8cfa09ed16285baefd6a447a7d297474` |
| `phase2a/glr.py` | `7ed182834957d09546e855468fc14082d894bb54308f3ef728d591d1e4a330f6` |
| `phase2a/policy.py` | `68d75f51a71ee90f7ffc19b11e82f19563b5280533ab3bbae1fda6d70ce90a91` |
| `phase2a/bootstrap.py` | `21bc25d7c0c22c40605a9df0a858602fb78084588900b2d5cb2d865ff2060881` |
| `phase2a/runner.py` | `cfc3eafa11fe1d7e0c927733ef54f00554fddbcd9f734c032fe8ea0d2aee3f3a` |
| `phase2a/analyze.py` | `de3f7367129562d7641b7851c2c7410868b795e3385e2dacec1ed52f632262ca` |
| `phase2a/integrity.py` | `ee7120e91b54620b65bd1a6e7407cff0fbb435108893237bea641e08e95c01e5` |
| `phase2a/phase_map.py` | `2e1a799286b63ad8c3edceecdcc7cb092a9bd4b7e450d7d0ba90c179c2241d57` |
| `config.json` | `3bcfa08d9fcffcd790b889345687550394f43b0db792a1f7ac7bf1db972d4c24` |
| `PROTOCOL.md` | `bae829e594a420f3f4d31037416e86c9404721fbc261f11f343c17bf52cfec8b` |
| `tests/test_integration.py` | `9c8ab303141657d96231c6d3d14eb4e34dff159ff4d8922271a1e83ab1f3e8f8` |
| `tests/test_analysis.py` | `c6959124e02beb7c90411c3a5cde0c3dc36f9f222c342c08120c96a117919d43` |
| `audit/independent_policy_checks.py` | `efaee8228b3c885acdb4dff52911ca9eee924fa0d725290cf868b44802c88d4c` |
| `../qrelbench_v01_20261030/qrelbench/data.py` | `3a19293c307d7576d895d3a332e037b3f43dc0cf37db6db1f45255d1c472247e` |
| `../qrelbench_v01_20261030/qrelbench/environment.py` | `8bb13e388b83cb2e0d85cdac80af73eca3a6229ba0fc17b61597b4b32c6e5c2c` |
| `../qrelbench_v01_20261030/qrelbench/randomness.py` | `c83448bf784126519ed8f5df0164910409dc76a7a5dc84521e21c620a054d2be` |
| `../qrelbench_v01_20261030/qrelbench/policies.py` | `ade516e5db0d54eb6414a9402ea2ec69e019b6eff1225ffcbf0e8260e8130fe1` |
| `../qrelbench_v01_20261030/qrelbench/rpc.py` | `603ab85272d9a2da405efc2562643460288740538537f54edc0112bdac376fe9` |
| `../qrelbench_v01_20261030/qrelbench/security.py` | `bf1a9763d91d4a38a118560dc34eeed22c45ebc49bff7662f0c3d03e86e79002` |

The review must be refreshed for changed source bytes. This table binds an inspection and bounded probes; it is not an optimality, privacy-against-arbitrary-code, or statistical correctness certificate.
