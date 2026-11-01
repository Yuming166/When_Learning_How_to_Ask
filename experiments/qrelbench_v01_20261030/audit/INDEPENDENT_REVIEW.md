# QRelBench v0.1 independent code audit

## Material Passport

- Review mode: independent local code and reproducibility validation.
- Inputs: the user's original pasted QRelBench request, repository `Theory_Note.md`, and the benchmark implementation itself. No peer review was used as the initial review input.
- Reviewer: a separate Codex agent in the same model family and shared workspace; no cross-model or external-service review.
- Allowed work: read-only implementation inspection and bounded CPU checks; only this report and `audit/reviewer_checks.py` are reviewer-authored.
- Status: **SOURCE REVIEW PASSED / SEED-AND-FREEZE BINDING PENDING**. The implementation was revised during review; all discovered functional defects and the public-seed issue have prefreeze dispositions recorded below.
- No LLM/API/GPU calls, package installation, main development pilot, training, or confirmatory experiments were executed by this reviewer.

## Decision and scope

**CONDITIONAL GO for the bounded CPU development pilot using the reviewed built-in policies**, subject to generation of a fresh evaluator-only development seed and matching final source/config/protocol/seed-commitment freeze. The endpoint, selected-config freeze, and public-seed issues have been corrected and rechecked. The ordinary API, separate process, and tested confinement layer are suitable for this scope. No general adversarial security or real-LLM claim is approved.

This is an implementation audit, not approval of `Theory_Note.md`'s general theorems or evidence of naturally occurring query reliability. The finite checks below can expose implementation defects; they do not prove statistical independence or real-world transfer.

## Findings and dispositions

### F1 — Raw consistency totals biased the adaptive format comparison: corrected before pilot

The initial `Strategy.estimate_format` compared raw agreement totals. Repeat-and-Compare deliberately acquires more repetitions from its selected format, so this comparison rewarded sampling frequency as well as consistency. The corrected implementation stores both completed pair counts and agreements and compares `(agree + 0.5)/(pairs + 1)` in `qrelbench/policies.py:20-34,60-65`.

The independent regression gives A 8 agreements from 10 pairs and B 2 from 2. Corrected selection is B. This check passes. This was a prefreeze code correction; there were no reviewed confirmatory outcomes to repair.

### F2 — Coordinate marginal modes were weaker than joint exact-recovery MAP: corrected before pilot

The initial common decoder returned coordinate marginal modes, which do not always maximize posterior probability of the entire vector. The reviewer independently enumerated all signs/types for a three-fact group at plug-in rates p=0.85, q=0.60 with counts:

```json
[[[5,1],[1,2]],[[2,0],[0,4]],[[1,2],[5,2]]]
```

The initial decoder returned `[0,1,0]`; joint MAP returned `[1,1,0]` with a log posterior advantage of 0.02384178261876002. The corrected `qrelbench/decoder.py:19-47` enumerates up to 2^16 sign assignments within a group and marginalizes its latent type. The independent fixture now returns `[1,1,0]`, matching enumeration with zero log deficit.

The rates remain estimates from finite offline calibration. This is joint MAP for that plug-in posterior, not a posterior integrating continuous rate uncertainty, a theorem-attaining information allocation, or a fixed-confidence certificate. It is applied commonly across fixed-budget baselines, including the format-only Oracle.

### F3 — Initial seed reconstruction corrected by confinement and sealed fresh-seed design

The normal transport is well separated: only protocol, online cap, and delta enter the job payload (`qrelbench/evaluate.py:62-68`); the parent retains the episode and environment. Only five allowed methods can be called (`:68,78-85`). The worker receives JSON bytes rather than the environment or a serialized private episode (`qrelbench/rpc.py:7-31`). `multiprocessing` explicitly uses `spawn` (`qrelbench/evaluate.py:114,121-122`).

The original unconstrained spawned probe received only public episode JSON, read the development config seed, searched four candidate public episode IDs, and reconstructed the full private truth vector exactly. The same key also determines future task/error draws (`qrelbench/data.py:45-55,76-86`; `qrelbench/randomness.py:7-25`). Mode 0700 on a directory alone does not isolate processes sharing a UID.

The implementer subsequently added `qrelbench/security.py:12-32`, invoked before the worker's first job by `rpc.py:25-30`, and evaluator non-dumpability in `evaluate.py:62-63`. The independent confined probe observed Landlock ABI4; both config and implementation reads were denied, both local TCP bind/connect attempts were denied, and the existing JSON pipe remained usable. All fourteen spawned-policy smoke episodes still passed.

However, a second probe **after confinement** hardcoded the then-published development seed, used the already loaded generator, and reconstructed the private vector again using only the public episode ID. Confinement cannot hide a constant already known to the policy author.

The final reviewed design corrects this too: `configs/development.json:3-4,83-85` has `master_seed:null` and specifies a sealed evaluator-only seed. `evaluate.py:109-112` loads a separate private development seed and requires its file bytes to match a pre-pilot commitment. Only the evaluator receives it; the job whitelist is unchanged. Evaluator non-dumpability is now set at `main` entry before config/seed reads or worker launch (`evaluate.py:101-105`), as well as in each job. The protocol requires a newly generated seed after review, private mode-0600 persistence, and independent future train/test secrets (`PROTOCOL.md:11`). The updated probe confirms the public config has no seed, and the old hardcoded seed cannot locate the episode generated from a distinct private test fixture. The reviewer did not inspect a real pilot seed, execute the main pilot, or claim to prove computational unguessability. Final entropy generation, private file permissions, and commitment binding remain an execution precondition.

`Path.exists()` continued to disclose filesystem metadata under confinement. Landlock ABI4's handled rights do not cover every possible filesystem/IPC action. Its policy applies to the calling thread and subsequent descendants; the final implementation now rejects a multithreaded bootstrap (`security.py:18-22`). The audit does not approve arbitrary code imported before confinement, UDP/Unix-socket exclusion, signal/DoS resistance, or general kernel sandboxing. These scope limits agree with the [Linux kernel Landlock documentation](https://docs.kernel.org/userspace-api/landlock.html), particularly its access-rights, inheritance, and compatibility sections.

### F4 — Float conversion could produce a uniform draw equal to 1: corrected before pilot

The reviewed `qrelbench/randomness.py:12-13` divided a full 64-bit integer by 2^64 using Python float. The maximum integer rounds to `1.0`, so `uniform(...) < 1.0` is false. Consequently a nominally perfect type report (`s=1`) is not perfect by construction for an upper-tail hash value (`qrelbench/environment.py:61-64`).

A bounded deterministic check patched only the hash result to all 0xff and observed `uniform == 1.0`. The explicit regression failed with `Uniform endpoint rounding violates perfect-type control`. The corrected `randomness.py:12-14` uses the top 53 bits divided by 2^53. The same regression now returns 0.9999999999999999 for the maximum and 0.0 for the minimum and passes. This was a prefreeze correction.

### F5 — Freeze checked the default config while CLI could select another: corrected before pilot

`qrelbench/evaluate.py:21-24` hashes the default `configs/development.json`, while `main` reads `args.config` (`:99-102`). A different config could therefore run under the default config's frozen receipt. This does not change the planned default invocation, but weakens the reproducibility contract of the runnable package.

The corrected `evaluate.py:105-108` reads the selected bytes and requires their SHA256 to equal the frozen config hash. Its SHA256 is included in the receipt (`:120-122`). This fixes the default/selected-config discrepancy for the normal, non-optimized Python invocation. As with the other assert-based checks, `python -O` is outside the audited invocation.

### R1 — One reviewer assertion was stale: corrected transparently

The first independent full-script execution had six passing check groups and one failing `interface_and_integrity_checks` assertion. The reviewer had allow-listed the earlier reset fields and had not yet included the newly added `rate_domain`. Inspection established that the field contains the public known eta and bounds, not the realized p/q. The allow-list was updated and now checks its exact content. The second full execution passed all seven then-registered groups on unchanged source hashes. This is a reviewer-test correction, not a suppressed implementation failure.

## Source-level conclusions

| Requirement | Audited evidence | Limit |
|---|---|---|
| Independent fact construction | Each j has a separately keyed truth bit and its own product/offer record (`data.py:54-74`); the four predicates are mechanically consistent. | Pseudorandom construction with a fixed seed, not literal independent randomness conditional on an already fixed seed. |
| Equivalent A/B semantics | Both formats render the exact same canonical claim with the same 1/0 meaning (`data.py:33-42,72-73`). | Semantics are validated as benchmark text/predicates, not by measuring LLM interpretations. |
| No deterministic cross-fact source dependence | Distinct records/IDs; no shared stock, return, price, shipping, or aggregate constraints (`data.py:54-74`). No exact within-group balancing. | This is a fictional procedural source. Group sharing is assigned, not discovered in external data. |
| Public/private API | Deep-copied public catalog excludes records/truth/types/key/provenance (`data.py:77-89`); reset adds known s, calibration size, known bounds, and Oracle-only types (`environment.py:36-43`). | File-read reconstruction is blocked; actual seed must be fresh, private, and commitment-bound before execution. This is not general adversarial certification. |
| Channel model | Shared p/q and per-group preferred format determine correctness; per-(j,m,count) draws are domain-separated (`environment.py:45-56`). | Cryptographic pseudorandom simulator; finite tests do not prove ideal iid. F4 endpoint correction passes. |
| Offline references | Labelled high/low streams use a separate domain; caching prevents repeated acquisition or cost inflation (`environment.py:66-72`). | These labelled correctness streams are an explicit information resource, not natural unlabelled history. |
| Lifecycle/costs/reward | No in-episode reset; common task+type cap; invalid requests do not charge; calibration charged once; post-submit queries rejected; submit returns receipt only; scoring stays server-side (`environment.py:28-86`). | Oracle deliberately receives group types; evaluator object itself must remain trusted. |
| Oracle fairness | Oracle differs in reset only by its type vector; same rates, reference streams, cap, decoder, and per-action channel. All direct type questions count online (`evaluate.py:61-66`; `policies.py:67-93`). | Type-known Oracle is a comparator, not a policy with extra free labels/rates. |
| Negative controls | p=q informative and chance, singleton groups, perfect type reports, asymmetric and persistent channel cases are distinct jobs (`evaluate.py:42-56`). | Asymmetric/persistent data violate the certificate assumptions and must remain marked invalid for theoretical confidence claims. |
| Partition isolation | Split is in the key derivation (`data.py:46-49`); job builder admits development only and bounded development indices (`evaluate.py:27-58`). | This verifies namespace separation, not a claim that every test of isolation is adversarially secure. No train/test experiment was run by reviewer. |
| Adaptive performance | Seven declared baselines use public observations; corrected repeat comparison and common joint MAP decoder are substantial baselines. | No information-optimal allocator is implemented here, so no theory-optimality or guaranteed adaptive win should be claimed. |

## Fixed-confidence interpretation

`policies.py:10-13,69-93` uses a conservative time-uniform majority boundary, not the continuous-rate likelihood stopping rule in `Theory_Note.md`. For a true positive fact, each fresh ±1 vote has conditional mean at least zero. Hoeffding's inequality bounds a wrong crossing at n by `delta / (2*d*n*(n+1))`; summing over n and facts is at most delta/2. The negative-fact argument is symmetric. Predictable choices between channels preserve the argument while correctness is at least 1/2 and fresh errors hold.

The code has a finite cap. It explicitly retains uncertified guesses and reports censoring. Completion-conditioned query counts must not be presented as unconditional expected stopping times. The chance control and policies that remain on a q=1/2 stream need not stop almost surely. This implementation therefore supports finite-cap certificate/censoring diagnostics, not a general implementation of the note's uniformly correct, almost-surely stopping, asymptotically optimal policy.

## Independently executed checks

Command: `python -B audit/reviewer_checks.py` from this benchmark root. No main pilot runner was called.

- 200 generated episodes, 3,200 propositions checked by separately written predicate logic; all four predicate kinds covered. Truth mean 0.495625; type mean 0.5225. The first four-fact group was unbalanced in 141/200 cases.
- Reproducible same-seed/catalog checks, partition-paired catalog identity, and distinct train/development/test episode namespaces.
- Public field allow-list, mutation isolation, invalid action validation, terminal behavior, task/type budget integrity, offline acquisition caching, reward-free submission, and Oracle-only public addition.
- 12,000 fresh task draws across both labels/formats; per-stream correctness matched 0.60/0.85 within declared 0.04 tolerance. Empirical means were 0.59833, 0.85133, 0.60467, 0.86867. Lag and between-stream covariance sanity checks passed.
- 3,000 direct type draws, 16,000 offline draws, 12,000 label-asymmetric draws, 3,000 chance-control draws, 80 persistent repetitions, and 20 perfect-type draws. These finite perfect draws do not discharge F4; the boundary regression is the relevant exact check.
- Corrected normalized-consistency fixture and exhaustive three-fact joint-MAP fixture.
- All seven policies, both protocols, in seven real spawned workers per full execution: 14 deliberately tiny episodes, each with 24 online actions and 16 offline observations, 336 online actions per execution (1,344 across the four full executions). All fixed-budget runs completed, all deliberately tiny fixed-confidence runs were correctly censored. Workers exited cleanly.
- The planned config generates 3,108 policy-episodes and an upper bound of 1,451,520 online actions; this reviewer did not execute that pilot.
- An additional spawned shared-filesystem reconstruction probe demonstrated F3 without printing the private vector.
- A deterministic patched-hash boundary probe demonstrated F4 and failed its regression before a fix; the corrected 53-bit construction passes both endpoints.
- A Landlock-confined probe verified denied file reads and TCP bind/connect while JSON IPC remained usable. It first demonstrated metadata visibility and successful reconstruction with a preknown public seed. After the sealed-seed redesign, the updated probe verified the public config contains no usable seed and the old known seed cannot reconstruct a private-seed fixture.
- Mocked unsupported OS, Landlock ABI3, and multiple bootstrap threads are each rejected without falling back to an unconfined worker.

After these source changes, a third complete script execution passed **9/9 registered check groups**, with no source changes during its 2.5523 seconds. It used `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit/reviewer_checks.py`.

After the sealed-seed and single-thread bootstrap changes, the fourth complete execution passed **10/10 groups**, with no source changes during its 2.4913 seconds, using the same bounded command. It hashes all package, test, config, and protocol files; no failure was suppressed. These reruns were prompted by substantive implementation changes.

No confidence/independence claim is inferred solely from these toleranced finite tests. No scientific effectiveness result is inferred from smoke runs.

## Final binding

The final source audit is **GO_SOURCE_AUDIT_BOUNDED_DEVELOPMENT_ONLY** for the snapshot below. All modified implementation paths were checked. The only change after the fourth full execution was `protect_evaluator()` at main entry; its position before all private reads and worker creation was independently inspected, and it calls the same function already exercised in all spawned smoke jobs. No further broad rerun was necessary for that one-line placement change.

`qrelbench/analyze.py:24-38,41-74` was source-reviewed: it retains all episodes in restricted mean/censoring summaries, checks complete output denominators, uses paired episode resampling, and separates out-of-model certificate errors. Its reporting explicitly limits finite-confidence and synthetic-reliability claims (`:100-124`). The reviewer did not execute the analysis against nonexistent pilot output.

The fresh private seed and public freeze do not yet exist at report finalization. Before execution the implementer must generate the seed once, persist it privately, and bind its commitment plus these exact source/config/protocol/test hashes and the final audit artifacts. The reviewer has not certified an unobserved entropy draw, file mode, freeze, or main-pilot result. This is the remaining execution precondition, not an unresolved code finding.

```text
qrelbench/__init__.py       ffdd656d12cc785818eda76d7c39134b82b4393c4b71ea4826343083657a0cbe
qrelbench/analyze.py        56638ba1236945f70d01287b895d8083eb15bb7059b562e4c66de8089889496b
qrelbench/data.py           3a19293c307d7576d895d3a332e037b3f43dc0cf37db6db1f45255d1c472247e
qrelbench/decoder.py        1aecbcf325ab66069bb31f075253f4bb8f13a3fad18d39e9a5494fbc7d14829e
qrelbench/environment.py    8bb13e388b83cb2e0d85cdac80af73eca3a6229ba0fc17b61597b4b32c6e5c2c
qrelbench/evaluate.py       ad482a692d7bcbbb1267cacf13c913f6481dff87b7f118d1ccefe76ccbf43ca6
qrelbench/policies.py       ade516e5db0d54eb6414a9402ea2ec69e019b6eff1225ffcbf0e8260e8130fe1
qrelbench/randomness.py     c83448bf784126519ed8f5df0164910409dc76a7a5dc84521e21c620a054d2be
qrelbench/rpc.py            603ab85272d9a2da405efc2562643460288740538537f54edc0112bdac376fe9
qrelbench/security.py       bf1a9763d91d4a38a118560dc34eeed22c45ebc49bff7662f0c3d03e86e79002
tests/test_core.py          7879461972d5343005fca8e8820c0fcf6f4faa1b1f11b7c07f2e0aaf1b6e8383
tests/test_rpc.py           e9bf5237a5e697d8d64bacd61443dc3cd17632edd5a907cd4019a0900b57a5c1
configs/development.json   de670bd10cfc66f967ae71f170d99162dcaf71fdf87de6737b2aa4eb7bc7f6ad
PROTOCOL.md                be48a46b33d5662a26a17ba483ef92949feadc41f5f21c182b5d38693dec33a1
```

Any implementation change invalidates reliance on this snapshot until the changed paths are checked. No external independent model, expert panel, theorem certification, or adversarial sandbox approval is implied.
