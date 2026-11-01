# Phase 2d P0 — joint task/type ablation and certified stopping

This separate development branch/directory preserves the original Phase2c strategy, records and unexecuted confirmation protocol. The user selected only the2x2ablation and certified stopping work. No acceleration, uncertainty-aware pilot, model calls, training or confirmation is included.

Read PHASE2D_PROTOCOL.md before the results. The four policy definitions and public structural control are in TYPE_BASELINE_SPEC.md. CERTIFIED_STOPPING_SPEC.md specifies exact rational profiling and outward Decimal likelihood/beta intervals; STOPPING_PROOF_AUDIT.md supplies the independent derivation, rational-series checks and guarantee limits. ABLATION_REPORT.md and ESTIMATION_DIAGNOSTICS.md are generated from the completed development batch. CERTIFIED_STOPPING_REPORT.md and METHOD_VERSION_DECISION.md give the post-ablation numerical and version judgments.

The main acquisition batch deliberately uses the common historical floating stopping rule to isolate the requested sampling ablation. A separate audit encloses completed endpoints from both Phase2c and Phase2d, tests the old false crossing, and replays selected existing worlds through the integrated strict gate. Scoring-only cap guesses are distinct from certified answers. Certificates cover wrong certified outputs under the stated model/arithmetic contracts; they do not prove arbitrary samplers eventually stop or the float optimizer is asymptotically exact.

From this directory, use thread settings before Python import:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python audit/stopping_independent_checks.py
```

Execution order is one-time `python -m phase2d.freeze`, `python -m phase2d.runner`, `python -m phase2d.integrity`, `python -m phase2d.analyze`, then `python -m phase2d.certificate_audit`, with the same thread settings. Freeze requires the recorded pre-seed source review. Seed/output files cannot be replaced or silently overwritten; do not restart an existing batch. Partial observations, failed identities and acquisition charges are retained if infrastructure fails, without interpreting missing terminal costs as cap censoring.

For exact reproduction use an isolated sibling copy with the same historical dependencies, source/config/freeze and private development seed; remove only that copy's generated run/analysis/certification directories and generated receipts/reports before following the recorded order. Do not generate a new seed and call it a replay. Preserve dependency/runtime versions from RUNTIME.json. Private seed/reproduction files stay evaluator-only and are excluded from accidental staging.

VALIDATION.json checks all new observations, action permissions, paired costs, schedules, final floating GLRs and353older receipt-bound files. CERTIFICATION_VALIDATION.json and artifacts/certification retain endpoint enclosures, the rejected historical counterexample, complete existing-path replay records, extra acquisition costs and gate timing. FINAL_RECEIPT.json binds final artifacts. No scientific/confirmation world is added by deterministic endpoint checks or replay.
