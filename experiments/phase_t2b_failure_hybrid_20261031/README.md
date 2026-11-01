# T2b: student failure attribution and hybrid rescue

Isolated branch training/failure_hybrid_t2b; frozen T1/T1a/T1b/T2 records stay unchanged. Read HYBRID_CONTROLLER_PROTOCOL.md and ANALYSIS_SCOPE.md for the full development protocol, limits and stop rules. No training, provider, Qwen, GPU, Natural, RL or confirmation run is part of this phase.

Historical packages/weights are read-only absolute local dependencies declared in t2b/bootstrap.py and generation_freeze.json. They are not silently replaced by current GitHub code. audit/HISTORY_BEFORE.json commits every receipt-bound input. t2b/reuse.py isolates the T1a solver namespace to avoid importing a competing historical vendor tree. New source is additive; the QRelBench model/generator/gate are unchanged.

The frozen source, controller rules, model bytes, complete deterministic condition roster and analysis precede creation of a new private master seed. artifacts/SEED_COMMITMENT.json binds that local private seed before any fresh world. Raw identities/seeds/truth never enter the prediction callback. The source-only same-family shared-context review and deterministic unit fixtures are not a blinded/cross-family or scientific confirmation.

## Reproduce locally

Training-compatible inference interpreter: /storage/gaoym/wcl_v100_venv/bin/python (Torch/NumPy/SciPy). Analysis and plotting interpreter: /storage/gaoym/miniforge3/bin/python (NumPy/Matplotlib). Set PYTHONDONTWRITEBYTECODE=1, OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, CUDA_VISIBLE_DEVICES='' before scientific imports. There is no fit command. The driver runs exactly two single-thread CPU workers with a hard timeout, retains per-action progress journals and never retries scientific jobs.

After the original audit/freeze, the once-only launch sequence is:

```sh
/storage/gaoym/wcl_v100_venv/bin/python -u -m t2b.run smoke
/storage/gaoym/wcl_v100_venv/bin/python -u -m t2b.run evaluate
/storage/gaoym/miniforge3/bin/python -m t2b.analyze
```

Do not rerun in the populated output directory. For exact reproduction, use an isolated copy, bind the same source/dependency bytes and saved private seed, remove only copied outputs in that isolated copy and create matching fresh output locations. Merely drawing another seed is a new development experiment. Hash verification deliberately fails if dependencies drift. Scripts refuse replacement of stage outputs.

Technical smoke separately compares the two same-input controller reference implementations to literal frozen baseline implementations; no fitted checkpoint is changed. Main observations are624 policy paths from new development worlds, with repeatedR/methods coupled inside30 distinct worlds. Two additional smoke worlds are excluded from scientific statistics. B32/64 are intermediate scoring-only readouts under cap6144, not certified outputs or deadline-optimized fixed-budget policies.

## Artifacts

POLICY_ALIGNMENT_AUDIT.md records source/numerical/control alignment. FAILURE_STATE_ATTRIBUTION.md audits saved T2 histories without new inference; its unavailable GLR history and causal limits remain explicit. HYBRID_CONTROLLER_PROTOCOL.md freezes methods/risk thresholds/roster. MATCHED_COMPARISON_RESULTS.md and DEPLOYMENT_COST_ANALYSIS.md give complete new-path denominators, costs, uncertainty and parameterized deployment tradeoffs. CONDITIONAL_TRAINING_PROPOSAL.md proposes only conditional future work; it authorizes no training. FINAL_DECISION.md provides the bounded scientific decision. FINAL_RECEIPT.json binds source, reports, raw outputs, models' dependency commitments and private provenance hashes.

Local provenance files under artifacts/private and historical private paths are not authorized for publication. Logs contain no service credentials. All statistical resampling and plotting is offline, with no model/environment queries. Missing/failed/cap paths remain visible; cached weights and historical unknown failed-prefix cost do not become free or known costs. Final scope is QRelBench-Exact development only, with no human/Natural, asymptotic optimality or novelty claim.
