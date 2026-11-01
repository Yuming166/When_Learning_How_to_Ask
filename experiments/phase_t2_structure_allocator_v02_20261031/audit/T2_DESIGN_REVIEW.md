# T2 v02 bounded continuation design review

Date: 2026-10-31. Reviewer role: independent native same-family source/evidence auditor. This is not manuscript peer review, cross-family review, formal verification, or independent scientific confirmation. The reviewer reads public source and receipts, executes no scientific world/replay, model inference, fitting or test, and does not open private seed/truth contents. Writable scope for this review is this file only.

**Pre-generation verdict: PASS for one explicitly recorded engineering continuation, after the new generation freeze binds the reviewed source, protocol, continuation provenance and this report.** This verdict covers the same two technical smoke worlds, 352 teacher-data worlds and 18 teacher-only budget-development worlds from the already committed plan. The complete plan remains 402 distinct world identities, including the later 30 closed-loop worlds. It does not approve fitting before a completed public data/input audit, budget freeze and training freeze, or held-out evaluation before the analysis freeze. Scientific effectiveness and the final GO / REVISE / NO-GO decision remain pending.

## Prior audit and preserved failure

The original frozen [design review](/home/gaoym/When_Learning_How_to_Ask_training_t2/experiments/phase_t2_structure_allocator_20261031/audit/T2_DESIGN_REVIEW.md) supplies the unchanged source/design assessment, T1 failure evidence, Phase2e limitations and claim boundaries. The original [subsequent-stage review](/home/gaoym/When_Learning_How_to_Ask_training_t2/experiments/phase_t2_structure_allocator_20261031/audit/T2_POSTRUN_REVIEW.md) records the preparation failure and pre-fit NOT READY status. Neither report is changed or retroactively relabeled successful.

The initial attempt completed two 64-action technical smoke worlds but failed while collecting its first teacher-data world. It persisted zero complete teacher-data worlds and zero rows; no student was fitted and no student held-out outcome or budget selection was available for choosing this correction. The original failed-world partial acquisition cost was not saved and remains unknown.

The author's later public PREPARATION_FAILURE_DIAGNOSIS.json records one explicit technical replay of that same committed world. At online action 516, a posterior marginal was 1.0000000000000004, an overrun of approximately 4.44e-16; the minimum marginal was 6.157584296690793e-16. This supports the numerical-interface diagnosis that the earlier failure receipt alone could not establish. The reviewer inspected the public diagnostic, not its private seed, and did not reproduce the world.

The failed attempt is preserved under FINAL_ATTEMPT_RECEIPT.json. Earlier integrity inspection verified its 36 public bound files and receipt hash; the two private bound files were not opened by this reviewer. The new HISTORY_BEFORE.json reports PASS for 738 unique files: the prior 699 historical files plus the initial attempt's 38 bound files and its receipt. This count is a reviewed author-produced integrity receipt, not a claim that the reviewer independently inspected private contents.

## Inspected correction and continuation controls

The implementation differences are confined to t2/core.py, t2/data.py, t2/prepare.py and t2/integrity.py. The configuration is byte-identical to the initial attempt. The information, neural, evaluation and run logic retain the previously reviewed method and accounting contracts.

In observed_state, only copied theta_prob and z_prob marginals are adapted. Finite values within 1e-12 of [0,1] are clipped into that interval; larger overruns and nonfinite values raise an error. The strict observable-state validator remains unchanged. The raw Phase2e posterior probability fields, joint posterior, p/q estimates and group MAP types retain their original values. The frozen teacher implementation, coefficient solver and independent certification gate are unchanged. Adapter counts and maximum adjustment are retained as label-row metadata and are not added to the student input whitelist. This is a bounded numerical input repair, not evidence of exact posterior arithmetic.

The preparation caller reads the committed seed only after checking its recorded hash, retains the same namespace and configuration, and compares the regenerated public plan for exact equality with the original public plan before acquisition. It refuses an existing output directory. The history checker binds the initial failed receipt and its artifacts. The v02 protocol amendment explicitly overrides the original fresh-seed/zero-restart wording: one preparation engineering restart is recorded, with zero scientific fitting retries and no replacement world selection.

Cost provenance is explicit. The prior 128 smoke actions and 516 diagnostic-replay actions remain separate from v02's actual acquisition and compute. Re-executed smoke actions are charged again. The unknown original failed-world cost remains unknown and is not replaced by the replay's cost. A later report must not describe the overall engineering effort as zero retries or as having fully known acquisition cost. If v02 fails, the amended protocol requires preserving that failure and ending this round rather than continuing technical trials.

## Readiness evidence

The reviewer inspected the author-produced final logs: **42 generation/source-contract tests PASS in 2.383 seconds**, and **12 analysis tests PASS in 1.892 seconds**. The generation suite includes the bounded-marginal repair and rejection checks in addition to the previously reviewed core, information, neural and evaluation contracts. These tests were not run by the reviewer and establish neither allocation quality nor generalization.

The initial combined environment probe is preserved in logs/combined_environment_probe.log. Its two plotting errors came from absent Matplotlib in the training environment; the final suites use the explicitly recorded separate training and analysis interpreters. audit/ENVIRONMENT.json discloses this probe, no environment installation, one training CPU thread, zero Qwen calls and zero GPU jobs. The probe is not silently represented as a clean first test run or a scientific outcome.

At this review, the new artifacts directory does not exist. There are no v02 generated rows, labels, budget outcomes or student predictions available to this reviewer. This is therefore a source/provenance readiness decision only. After preparation completes, public rows, finite-cut archives, DATA_LEAKAGE_AUDIT, BUDGET_FREEZE and plan_public still require the separate pre-fit review.

## Boundaries retained

T1 remains a configuration-specific NO-GO; Phase2e remains REVISE, and Fused-Original is not a confirmed optimum. The coefficient solver supports G<=2 and the inherited certified gate d<=4. All-alternative fixed-alpha radial information diagnostics, finite-cut training approximations, observable-input restrictions, matched scheduling, charged posterior estimation, full failed/capped/inapplicable denominators and world-cluster descriptive uncertainty retain the original review's qualifications. No posterior clipping, successful preparation or synthetic test receipt establishes a neural optimum, stopping-time guarantee, population noninferiority, novelty or independent confirmation.

## Reviewed artifact hashes

These hashes were read before the new generation freeze; the freeze must also bind this report and all required source/dependency files.

| Artifact | SHA-256 |
|---|---|
| t2/core.py | 6bc68b26df262c8a26d038aadc73012b58ea5a028a628b847f6a9e596b9ecbdf |
| t2/data.py | bfa3811955b877af36761fa1930a2a9aa9d26b5c69f817f9137597bef2de241c |
| t2/prepare.py | 9d06f5316014d24c1bb9550c83323871b37053b99cde01be4debee18a83a6a21 |
| t2/integrity.py | 6fed69deab70a6e5109a9586bfc3dbbca96623d2fb9af86c4d68c6348dd57018 |
| T2_PROTOCOL.md | 7d30b161f7145c1bfcb1d9f9a6fc3420328328939acca102ba1afd320a615ad0 |
| config.json | d8d6cc701f1b468082714b7ed95272935fd4c23aa51034e78fe3103ad3f08e69 |
| audit/CONTINUATION.json | 496ef5836194575763d7c2fda3f5bded10efb25f078ecbfd4f12d27206d0c800 |
| logs/pre_generation_tests.log | 3fef9438f40966112d3ee042267895420e9e39968f80dd386de41defaa1f48c8 |
| logs/analysis_tests.log | 9be76d4b6af8f23caa258a70b64c5a8cfb5a6ed11c22b8269c41f0e08ba75a8a |
