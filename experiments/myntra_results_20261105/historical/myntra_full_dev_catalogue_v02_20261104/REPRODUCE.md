# Reproduction

This is a one-shot deterministic development experiment. Reproduce it in a fresh copy of this experiment directory; do not delete or overwrite the original run, freeze, or traces. The configured source worktree and its frozen catalogue must be available at the path recorded in `config.json`.

```bash
python -m unittest -v test_full_dev.py
python run_full_dev.py --prepare
python run_full_dev.py --smoke
python freeze_full_dev.py
python run_full_dev.py --full
python verify_full_dev_postrun.py
python analyze_pools_postrun.py
```

The full command launches eight independent `spawn` workers and one ordered parent writer. It does not call an LLM/API, train a model, or use the validation/test product records. `RUN_STARTED.json` prevents a second in-place full run; an interrupted run must be preserved as incomplete and reproduced in a new, separately identified experiment copy.

`verify_full_dev.py` is part of the frozen code, but its CLI omits a module-level `FROZEN` path and therefore fails when invoked directly. Use the included `verify_full_dev_postrun.py` wrapper, which supplies the local frozen-file path without modifying the frozen verifier. The wrapper validates existing receipts against the freeze, metrics, and trace hashes.

`analyze_pools_postrun.py` reports the frozen primary contrast separately for the six gender/category pools. It is an audit of the already frozen trace and does not alter the method, data, or primary results.
