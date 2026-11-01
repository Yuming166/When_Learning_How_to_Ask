# Unknown extraction rates and finite calibration

Start with [the Chinese research report](RESEARCH_REPORT_CN.md) and [the theorem note](THEORY_RESULTS.md).

The experiment is fixed in MODEL_AND_SCOPE.md. Both older theory snapshots and all historical experiments remain unchanged. This directory contains mathematical proofs, two exact certificates, and explicitly labelled deterministic numerical relaxations. It is not a benchmark confirmation run or a deployed sequential learner.

## Files

- THEORY_RESULTS.md: exact continuous information coefficient, valid stopping, structural reductions, restricted scalar theorem and certified failures of the known-rate threshold.
- CONTINUOUS_COST_PROOF.md: complete expected-cost proof, including categorical observations and the cost-hitting-time argument.
- ORACLE_AND_THRESHOLD_AUDIT.md: independent structural proof and certificate audit.
- CALIBRATION_NOVELTY_AUDIT.md: primary-source comparisons and applicability limits.
- certify_threshold_failure.py / THRESHOLD_FAILURE_CERTIFICATE.json: all-action learner lower bound, continuous-domain oracle upper bound, known-rate criterion and inner nonconvexity.
- singleton_threshold_certificate.py / singleton_threshold_certificate.json: exact one-read example where the weaker unknown-rate oracle changes the equality conclusion.
- explore_calibration.py / GRID_DIAGNOSTIC.json: six fixed calibration ratios, finite-grid LP relaxations and heuristic pure-block witnesses. No continuous-optimality claim.
- plot_certificates.py / calibration_certificates.png / .pdf: floating-point illustrations of separately certified statements.
- RECEIPT.json: source hashes, preserved historical snapshots, verification scope and software versions.

## Reproduce

The two exact certificates need only Python's standard library. From the repository root:

    PYTHONDONTWRITEBYTECODE=1 python research/web_unknown_calibration_20261031/certify_threshold_failure.py

    PYTHONDONTWRITEBYTECODE=1 python research/web_unknown_calibration_20261031/singleton_threshold_certificate.py

For the optional numerical diagnostic and figure, use Python with NumPy, SciPy and Matplotlib:

    PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' /storage/gaoym/miniforge3/bin/python research/web_unknown_calibration_20261031/explore_calibration.py

    PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' /storage/gaoym/miniforge3/bin/python research/web_unknown_calibration_20261031/plot_certificates.py

Each script writes beside itself. Copy this directory elsewhere before rerunning to preserve the snapshot. Plot PDF timestamps can change hashes without changing the mathematical content.

## Evidence levels

Exact Fraction arithmetic and logarithm-series remainder bounds certify the finite inequalities. The continuous oracle upper bound additionally uses a proved global derivative bound across 900 covering cells, so it is not a claim based only on a grid of alternatives. Decimal strings are displays of bounds.

The six-ratio grid study has a different status: checking a finite subset of nuisance alternatives yields a relaxation. A local continuous search produces candidates, not certified global minima. The alpha=1 separation was subsequently certified by independent lower/upper bounds; grid equalities at other alpha values remain unconfirmed.

The written optimality theorem assumes ideal continuous likelihood profiles and exact allocation optimization. These scripts do not implement or certify that ongoing policy.

No inference service, credentials, models, training, GPU, external experimental API or randomly sampled benchmark world is needed. Reviews were by collaborators sharing context and model family, not blinded, cross-model or formal machine proof checking.
