# T2 structured allocator — bounded development

Read T2_PROTOCOL.md and audit/CONTINUATION.json first. This is an isolated local experiment on branch training/structure_allocator_t2. Frozen T1 remains NO-GO; Phase2e remains REVISE. No Qwen, GPU, RL, new benchmark, paid provider or confirmation run is part of this phase.

The initial implementation attempt is preserved in the sibling phase_t2_structure_allocator_20261031 directory, including its failed preparation, public numerical diagnosis and FINAL_ATTEMPT_RECEIPT.json. v02 makes one guarded marginal-roundoff repair. It reuses that attempt's committed master seed and world plan, rather than drawing replacement worlds. Earlier failed-prefix cost remains unknown and must not be replaced by the diagnostic replay cost.

The source dependencies are read-only historical packages in the Phase2e worktree and the frozen T1 MLP in the training_t1 worktree. generation_freeze/training_freeze/analysis_freeze.json bind exact source bytes and absolute dependency locations. audit/HISTORY_BEFORE.json also binds historical results and the initial failed attempt. Source model descriptions are in audit/NEURAL_DESIGN.md and audit/INFORMATION_OBJECTIVE.md. T1_FAILURE_AUDIT.md separates observed problems from untested causal explanations.

Use `/storage/gaoym/wcl_v100_venv/bin/python` for preparation, fitting and evaluation. Set PYTHONDONTWRITEBYTECODE=1, OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and CUDA_VISIBLE_DEVICES='' before import. No installation into this environment is required. Analysis and its plotting tests use `/storage/gaoym/miniforge3/bin/python` with NumPy/Matplotlib; the training interpreter lacks Matplotlib. The preserved combined-environment probe failed for this known package separation; both intended test suites are recorded separately.

Actual stage commands, run once in this experiment directory after their source/data audit gates:

```sh
/storage/gaoym/wcl_v100_venv/bin/python -u -m t2.prepare
/storage/gaoym/wcl_v100_venv/bin/python -u -m t2.run fit
/storage/gaoym/wcl_v100_venv/bin/python -u -m t2.run evaluate
/storage/gaoym/miniforge3/bin/python -m t2.analyze
```

The launch receipts/logs record the actual hard timeouts. Every stage refuses pre-existing output, so these commands must not be rerun in this directory. For reproduction use an isolated copy, keep the same source/dependency bindings and private master seed, and create fresh output locations in that copy. The continuation seed source is an explicit private local dependency; reproduce from the retained seed rather than silently drawing a new one. A new seed changes the experiment. Model weights are stored separately from source; all training uses final-only checkpoints without selection.

Canonical student data is only row.state. Identity/split/teacher labels/cuts are separate supervised/evaluator metadata. The finite cuts depend on the observable estimated model, never true generating rates. All private directories are evaluator provenance and may not be passed to predictors or published. No adversarial plugin isolation or human/Natural validity is claimed.

The public plan enumerates all expected paths and offline rows, including unsupported T1-MLP dimensions. The two fixed budgets are evaluator readouts under public cap6144, not early deadlines supplied to a model. Strict outputs and scoring-only guesses are separate. Completed-path records include every action; progress journals preserve partial paid prefixes before expensive operations. Failed/missing/censored paths remain in the declared denominator.

T2_TRAINING_REPORT.md, T2_EVALUATION.md, COMPUTATIONAL_COST.md and FINAL_DECISION.md record the final result. Figures and complete paired/world vectors are under artifacts/analysis. A final receipt binds source, outputs, private provenance commitments, weights, reports and logs; integrity is not proof of effectiveness or asymptotic optimality.
