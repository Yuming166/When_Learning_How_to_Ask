# T1d nonuniform allocation and robustness

Read FINAL_DECISION.md first. The eight requested Markdown deliverables plus FINAL_RECEIPT.json are in this directory. T1D_PROTOCOL.md and POLICY_SEMANTICS_AND_SOURCE_AUDIT.md predate scientific entropy; the remaining reports are produced by the precommitted analyzer/renderer. No training or confirmation occurred.

SOURCE_MANIFEST.json covers all local Python (including copied T1c wrappers and complete dependencies, tests and postprocessing), fixed documents and numerical runtime fingerprints. HISTORICAL_INPUTS.json verifies frozen T1a/T1b/T1c public receipts without rewriting T1c's missing-wrapper record. Artifacts/private and literal engineering fixture records stay git-ignored; final receipt binds their hashes only. Existing reserved seeds were never opened.

RESULTS.json, PAIRED_OUTCOMES.json, STRATIFIED_RESULTS.json, MECHANISM_DIAGNOSTICS.json, RUNTIME.json and VALIDATION.json retain full denominators, all budgets/arms, negative cases and scope. Do not treat fixed-budget guesses as certified answers. The proposed confirmation document, if present, is a proposal with zero execution authorization.

The single scientific runner refuses artifacts overwrite or retry. Recomputing analysis/reports does not generate worlds: `python audit/analyze.py` then `python audit/render.py`; source integrity must remain unchanged and final receipt must be regenerated. Do not delete artifacts to rerun a new scientific batch. The branch is isolated; public allow-list is staged without commit/push/merge.

中文结果解释见[RESEARCH_INTERPRETATION.md](RESEARCH_INTERPRETATION.md)。A2阳性子命题的窄确认提案见[MECHANISM_CONFIRMATION_PROTOCOL_PROPOSAL.md](MECHANISM_CONFIRMATION_PROTOCOL_PROPOSAL.md)，仅提案、不执行。该文字补充在结果后完成，源协议与门槛保持不变。

## Requested deliverables

- [T1D_PROTOCOL.md](T1D_PROTOCOL.md)
- [POLICY_SEMANTICS_AND_SOURCE_AUDIT.md](POLICY_SEMANTICS_AND_SOURCE_AUDIT.md)
- [NONUNIFORM_ALLOCATION_ABLATION.md](NONUNIFORM_ALLOCATION_ABLATION.md)
- [CROSS_BUDGET_EVALUATION.md](CROSS_BUDGET_EVALUATION.md)
- [PAIRED_STATISTICAL_REPORT.md](PAIRED_STATISTICAL_REPORT.md)
- [COMPUTATIONAL_COST.md](COMPUTATIONAL_COST.md)
- [WWW_CONTRIBUTION_ASSESSMENT.md](WWW_CONTRIBUTION_ASSESSMENT.md)
- [FINAL_DECISION.md](FINAL_DECISION.md)
- [FINAL_RECEIPT.json](FINAL_RECEIPT.json)
