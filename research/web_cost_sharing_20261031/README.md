# Source-cost / sharing theory snapshot

Start with [the Chinese research report](RESEARCH_REPORT_CN.md), then [the theorem and proofs](THEORY_RESULTS.md).

This directory is separate from all historical experiments and from the sealed previous web_native_theory_20261031 snapshot. The scope is a fixed finite completed-block model with known reliability levels. It contains mathematical calculations and audits, not a new empirical benchmark.

## Contents

- MODEL_AND_SCOPE.md: assumptions fixed before the checks.
- THEORY_RESULTS.md: information program and matching coefficient, oracle face, exact smallest-group criterion, finite-cap cost implications, finite-confidence balanced bound.
- FINITE_STATE_PROOF_AUDIT.md: full uniform-correctness and expected-cost construction.
- ADVERSARIAL_AUDIT.md: independent structural proof, limitations, certified nonmonotonicity counterexample.
- FOCUSED_NOVELTY_AUDIT.md: primary-source comparison and reading limits.
- check_cost_sharing.py / CHECK_RESULTS.json: rational distribution checks, high-precision KL, full mixed-action LPs, illustrative cost intervals and bounds.
- certified_counterexample.py / certified_counterexample.json: exact Fraction interval certificate using bounded logarithm-series remainders.
- cost_sharing_examples.png / .pdf: mathematical illustration.
- RECEIPT.json: hashes, preserved-input verification, counts, software versions and scope.

## Reproduce

The main numerical script requires Python, NumPy, SciPy and Matplotlib. The interval certificate requires only Python's standard library. The checked environment used Python 3.13 with NumPy 2.5.3, SciPy 1.18.1 and Matplotlib 3.11.1; exact recorded versions are in the receipt.

From the repository root:

    PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' /storage/gaoym/miniforge3/bin/python research/web_cost_sharing_20261031/check_cost_sharing.py --plot

    PYTHONDONTWRITEBYTECODE=1 python research/web_cost_sharing_20261031/certified_counterexample.py

Both scripts write their results alongside themselves. To preserve this snapshot byte-for-byte, copy the directory elsewhere before rerunning. Matplotlib PDF creation metadata can change file hashes on an otherwise equivalent rerun. Figures and LP outputs are not interval-certified; the separately named exact certificate checks its assertions with rational interval endpoints.

No inference endpoint, credentials, model downloads, model calls, training, random benchmark worlds or GPU are needed. Illustrative fixtures are mathematical diagnostics chosen during theory development, not an empirical preregistration. The full LP checks are numerical corroboration of the written proof and include every wrong-answer nuisance alternative for each enumerated instance.

The review was by collaborators with shared context and the same model family. It is not blinded review, cross-model validation or machine formal verification.
