# W2a controlled-provenance theoretical experiment

[中文报告](REPORT_ZH.md) · [基础证明](THEORY_RESULTS.md) ·
[稳定自适应分离](ADAPTIVITY_REGION_PROOF.md) · [独立数值审计](INDEPENDENT_REVIEW.md)

Completed without human signoff: deterministic fictional gold, controlled source
corruption, mathematical mechanism comparisons and finite-state calculations.
New Web requests, Qwen/other experiment-model calls, training and Method reruns: 0.
The two original natural-Web review candidates are not used as gold or promoted.

## Model and evidence boundaries

- `PROTOCOL.json`, `FREEZE_RECEIPT.json`: frozen scope, grids and both read-only parents.
- `AMENDMENTS.json`, `initial_run/`: transparently added stronger arbitrary-static
  depth-allocation baseline; unchanged grid, original run preserved.
- `generate_corpus.py`, `CORPUS_SPEC.md`, `corpus/`: 1,152 **simulated HTML files**,
  not model calls. Selector/reader/evaluator interfaces are distinct. Mixed or
  unaddressed pages do not have a forced binary publisher report.
- `engine.py`, `run_exact.py`: stipulated atomic root-report channel. No actual
  model reads the HTML in this experiment. Policies never consume realized gold.
- `THEORY_RESULTS.md`, `theory_certificates.json`, `verify_theory_certificates.py`:
  closed forms and exact finite checks, including cost-reversal intervals.
- `center_policy.json`, `policy_audit.py`, `POLICY_AUDIT.json`: 37-node frozen
  ordered-root policy, fixed decoder, forward risk/cost replay and perturbation checks.
- `ADAPTIVITY_REGION_PROOF.md`, `check_adaptivity_region.py`, `ADAPTIVITY_REGION_CHECK.json`:
  explicit nondegenerate region, coupling proof and independent finite certificate.
- `independent_checks.py`, `INDEPENDENT_EXPECTATIONS.json`, `INDEPENDENT_CHECKS.json`:
  Fraction reference using unsorted root states, full-history latent checks and
  exact certificates at the two strict-gain witnesses. Not human/cross-model evidence.

## Read-only verification

Use the existing saved inputs/seed, without regenerating or reinitializing:

```bash
cd /home/gaoym/When_Learning_How_to_Ask/experiments/w2a_controlled_provenance_20261101
PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/miniforge3/bin/python verify_artifacts.py
PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/miniforge3/bin/python check_adaptivity_region.py
```

For a complete replay of all main law risks and all finite-budget DP/static rows:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' \
  /storage/gaoym/miniforge3/bin/python verify_artifacts.py --recompute
```

This also verifies both parent manifests, corpus hashes and source metadata. It
does not write a new human attestation, change the corpus or call a model.

## Rebuild, in a copied directory

Python standard-library code suffices for theory, construction and numerical
work; Matplotlib and NumPy generate figures only. Exact runtime versions are in
`RUNTIME.json`. Keep `corpus/evaluator_only/seed.txt` to reproduce the same fixtures;
do not pass evaluator material or generator source to a policy.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 generate_corpus.py
PYTHONDONTWRITEBYTECODE=1 python3 verify_theory_certificates.py
PYTHONDONTWRITEBYTECODE=1 python3 run_exact.py
PYTHONDONTWRITEBYTECODE=1 python3 independent_checks.py --write-expectations --check-engine
PYTHONDONTWRITEBYTECODE=1 python3 policy_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 check_adaptivity_region.py
PYTHONDONTWRITEBYTECODE=1 python3 plot_results.py
```

Numeric outputs are deterministic; run logs contain elapsed times and are not
byte-reproducibility claims. Rebuilding refreshes check receipts. Verify the
sealed `MANIFEST.sha256` against the original artifact before a rebuild, rather
than treating refreshed logs/receipts as the same sealed delivery.

For the corpus alone, `generate_corpus.py --verify-only` is read-only. Do not
use `--initialize` for a rerun. The original retained-seed byte-rebuild result is
separately recorded in `CORPUS_REBUILD_CHECK.json`.

## Results and claims

- `law_grid.csv/json`: all 80 stipulated observation-law cases.
- `cost_grid.csv/json`: all 81 common-budget cases, including ties/no strict gain.
- `confidence_diagnostic.csv/json`: wrong URL-iid confidence; separate from accuracy baselines.
- `boundary_and_dependency_controls.csv/json`: perfect/chance channels and persistent reading errors.
- `EXACT_SUMMARY.json`: grid counts and strict-gain summaries.
- `mechanism_summary.png/pdf`, `adaptive_gain_grid.png/pdf`: standalone scientific figures.
- `analytic_curve_values.csv`: clearly labelled analytic illustration extensions, not new benchmark tuning.
- `FINAL_CHECKS.json`, `COMPLETION_RECEIPT.json`, `MANIFEST.sha256`: completion checks and hashes.

Finite-budget Bayes risk, fixed-confidence stopping, known channels, unknown
reliability learning, natural source errors and actual LLM extraction are different
claims. This package completes the controlled known-channel track only. It makes
no publication-priority claim and does not inherit earlier asymptotic theorems.
