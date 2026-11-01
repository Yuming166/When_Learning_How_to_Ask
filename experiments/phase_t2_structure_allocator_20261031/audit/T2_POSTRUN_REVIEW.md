# T2 subsequent-stage source and evidence review

## Material Passport

Date: 2026-10-31. Independent native same-family source/evidence review; not cross-family review, manuscript peer review, formal verification, or independent scientific confirmation. The frozen T2_DESIGN_REVIEW.md remains unchanged. The reviewer reads public source, receipts and generated artifacts only, and executes no learner inference, fitting, scientific world/replay or test. Private seed/truth contents are not opened.

**Current status: pre-fit NOT READY; scientific assessment PENDING.** The preparation attempt failed before one teacher-data world completed. There is no completed dataset, training-cut archive, data audit or frozen budget selection on which to issue a pre-fit PASS. No effectiveness or neural-method NO-GO conclusion follows from this engineering failure.

## Preparation failure independently reconciled

The public preparation receipt and log both report `ValueError('Estimated probabilities')` in t2/core.py validate_state, reached through observed_state during collection of the first training world. The strict observable-state validation rejected a posterior marginal outside its accepted finite [0,1] domain. The actual offending value and current transcript were not persisted; an ulp-scale probability-summation overrun is plausible from the source but is **not confirmed by this receipt**. NaN, a larger domain error and the exact failure position cannot be ruled out from the saved failure message alone.

The teacher-data manifest records zero completed worlds, zero persisted states, and the failed world ID `52223ed4897d1384e706580a`. The train.jsonl file is independently confirmed empty (zero bytes). No train_cuts.npz, BUDGET_FREEZE.json, completed DATA_LEAKAGE_AUDIT.json, training directory or evaluation directory exists at this inspection. The counts of zero in the manifest describe completed persisted worlds, not zero physical acquisition: `failed_world_partial_cost_unknown=true` explicitly records the unpersisted current-world cost.

The two declared technical smoke worlds completed 64 actions each using a randomly initialized network with no optimizer updates. Their costs sum to 109 task plus 19 type actions, 128 total online and zero offline. Both strict gates returned not certified at the smoke endpoint; this was a plumbing check and is not a failed trained-policy experiment. The smoke receipt reports 0.3260066 seconds wall time; the complete failed preparation wrapper reports 1.8293544 seconds wall and 1.8253883 seconds CPU. These totals include the smoke and failed data attempt; the individual data-generation receipt reports 0.1539162 seconds. Known smoke costs must be retained alongside the explicitly unknown failed-world partial cost.

No scientific retry, model API call or GPU job is recorded. No learner was fitted, and no candidate held-out predictions or final budget selection exist. Preserve this attempt and its zero-complete-data denominator. Do not describe it as completed T2 training, as an allocation-performance comparison, or as evidence that the proposed neural architecture failed.

## Frozen integrity at failure

The reviewer independently rehashed all 19 generation-frozen local files and 60 read-only dependencies; every hash matches. The design audit therefore remains bound to the source actually attempted. This check reads dependency file bytes for integrity, not private seed/truth contents, and does not itself re-run any experiment.

| Artifact | SHA-256 |
|---|---|
| generation_freeze.json | 89c65e24f41f928f33dabf9c8378a687894e4ccf7991cd74917893d0ada2a2aa |
| artifacts/prepare_execution.json | e5cb911eaf7836db2a636e03df2f1704c49b57a8877a10db5cdc0f87d18e3c3c |
| artifacts/data/manifest.json | b45786d133d8fee11c5de104a4a866900d8dfb9a0482f3987086c9bf5afd4172 |
| artifacts/smoke.json | 3959119ad9c31fc47104f2ba88b0bff5a6e91b4e004a8f1d340e2c18f63f0f37 |
| artifacts/data/train.jsonl | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| logs/prepare.log | ffb75a9b9a5921419b1ce9c45db6b19a4bce5a178563f4b0d9176aba851c0ee6 |

## Remaining gate

The pre-fit decision remains NOT READY until a valid completed dataset, source-backed legal-input/label checks, independent teacher-only budget freeze and an explicit training freeze exist. Any engineering correction or continuation must preserve the failed frozen attempt and its provenance, distinguish a numerical interface repair from scientific policy selection, and retain the no-outcome-selection boundary. The current report does not approve an uninspected correction, silently replace the failed world, or waive a frozen stage gate.
