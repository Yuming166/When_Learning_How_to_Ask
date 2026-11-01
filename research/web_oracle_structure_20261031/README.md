# Unknown-rate oracle structure

Start with [the Chinese research report](RESEARCH_REPORT_CN.md). The primary result is [strict necessity of depth mixing](DEPTH_MIXING_THEOREM.md), with an [exact continuous-domain certificate](DEPTH_MIXING_CERTIFICATE.json). [The format audit](ORACLE_STRUCTURE_AUDIT.md) proves pure-good boundary cases and a calibration-resource comparison. [The depth/sharing audit](DEPTH_STRUCTURE_AUDIT.md) proves the zero-calibration equivalence K_learner=K_oracle iff G=1, supplies conditional finite-calibration group criteria, and independently reads the depth certificate. [The literature check](STRUCTURE_LITERATURE.md) bounds novelty claims.

All assumptions remain those of `../web_unknown_calibration_20261031/MODEL_AND_SCOPE.md`. The historical snapshots and original theory are read only. No model calls, training, empirical confirmation or publication occurs in this stage.

## Reproduce the proof certificates

From the repository root, standard-library Python suffices:

```bash
PYTHONDONTWRITEBYTECODE=1 python research/web_oracle_structure_20261031/certify_depth_mixing.py
PYTHONDONTWRITEBYTECODE=1 python research/web_oracle_structure_20261031/certify_monotonicity_obstruction.py
PYTHONDONTWRITEBYTECODE=1 python research/web_oracle_structure_20261031/verify_artifacts.py
```

The depth verifier reads the previous stage's hash-bound `certify_threshold_failure.py` solely for rational probability and logarithm interval functions; importing it does not execute its experiment. Keep the prior snapshot in the checkout. All sign comparisons and interval bounds use exact fractions. Decimal strings are display approximations. These are readable computer-assisted proofs, not formal proof-assistant verification.

## Optional discovery and illustration

NumPy, SciPy, and Matplotlib are needed only here. The execution environment used Python 3.13.13, NumPy 2.5.3, SciPy 1.18.1, and Matplotlib 3.11.1. Constrain CPU thread use:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' python research/web_oracle_structure_20261031/discover_structure.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' python research/web_oracle_structure_20261031/plot_depth_mixing.py
```

The discovery script reads probability helpers from the previous stage without executing its main entry point. Its 768 configurations and all results are retained. Each solves two finite-grid LPs; no grid output is treated as a continuous certificate. The actual grid has 33 evenly spaced points on [.5,.975] (spacing .475/32), augmented by true p,q, rather than an exactly .015 grid. This implementation detail is recorded in the scope supplement.

`depth_mixing.pdf` is the export figure; its continuous curves are illustrative, while the displayed cost inequalities are from the exact certificate. `INPUT_HASHES.json` and `RECEIPT.json` bind historical integrity and final outputs. Reproducing the scripts overwrites only this stage's corresponding generated outputs.
