# Phase 2c — strong baseline and pre-confirmation freeze

Start with [RESEARCH_DECISION_CN.md](RESEARCH_DECISION_CN.md) for the five requested judgments. Read `BASELINE_COMPARISON.md` for efficacy, `COST_GAP_DIAGNOSTICS.md` for finite-R diagnostics, `PROOF_AUDIT.md` for theorem/code limits, and `CONFIRMATORY_PROTOCOL.md` for the unexecuted next stage. `WWW_SHORT_OUTLINE.md` organizes the four-page paper. The immutable development design is `PHASE2C_PROTOCOL.md`; D-RRC's definition is `DECAYING_BASELINE_SPEC.md`.

Dependencies are the sibling frozen QRelBench v0.1, Phase2a and Phase2b Python packages, plus Python3/NumPy/SciPy/Matplotlib and Linux Landlock support. Exact versions and launch environment are in `RUNTIME.json`. No model service is required.

Commands from this directory use `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` before Python starts:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python audit/adversarial_math_checks.py
```

The already completed development batch is preserved. `phase2c.freeze` and `phase2c.runner` refuse to replace its seed/output; do not run them to restart this directory. For exact reproduction, make an isolated sibling copy, retain the original source/config/freeze/private development seed, remove only that copy's `artifacts/run`, `artifacts/analysis`, and generated final reports, and run `python -m phase2c.runner`, then `python -m phase2c.analyze` and `python -m phase2c.integrity` there with the same thread environment. Never change existing historical artifacts. Numerical/library differences may prevent bit-identical reproduction; source and version hashes must be reported.

`phase2c.integrity` checks all295 prior receipt-bound files, current source/config/audits/seed/dependencies, paired costs and observations, every final GLR, forced/tracking schedules, then exactly replays selected **existing** development paths. It adds no independent worlds. Local private seed and reproduction files are available to this workspace's owner and excluded from accidental Git staging; never print them or send them to policy workers. The final receipt includes their hashes, not their contents.

Per-trajectory rows retain raw counts, calibration bits, type reports, full estimate/optimizer history, worker CPU/wall, and transcript hash. Snapshot replies to workers are acknowledgement only. Evaluator truth/provenance and trace prefixes stay in private reproduction records. Censored paths remain in all cost denominators. Technical fixtures, existing-world replay, and main scientific costs are reported separately.

There is no confirmation runner, generated confirmation seed, model call, RL, training or publication step here. The next decision is about the frozen numerical-policy confirmation, not a certificate of executable asymptotic optimality.
