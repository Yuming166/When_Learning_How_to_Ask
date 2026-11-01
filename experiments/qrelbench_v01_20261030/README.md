# QRelBench v0.1

A runnable, source-grounded **controlled** benchmark for reliable information elicitation. Private fictional catalogs use [Schema.org Product](https://schema.org/Product)/[Offer](https://schema.org/Offer) concepts. This package plants the theoretical response channel; it does not measure natural LLM or human reliability.

Read `BENCHMARK_AUDIT.md`, `PILOT_REPORT.md`, and `PROTOCOL.md` first. Historical experiment directories are immutable.

## Package and interfaces

- `qrelbench/data.py`: independent private facts/records, common proposition and two query renderings, source provenance.
- `environment.py`: trusted evaluator's `reset`, `query(j, format)`, `ask_type(group)`, `get_calibration`, `submit`; evaluation reward is private.
- `rpc.py`, `security.py`: spawned JSON-only learner and fail-closed Linux confinement. Ordinary policies receive no records, true parameters, seed, group types or correctness. Oracle receives types only.
- `policies.py`: seven budgeted baselines; normalized consistency estimates; conservative anytime confidence certificate.
- `decoder.py`: common joint exact-recovery MAP conditional on calibration-estimated rates, tested against independent brute force. No information-optimal allocation is implemented.
- `evaluate.py`, `analyze.py`: bounded CPU runner, all costs, censoring, paired descriptive analysis and plots.

## Environment and zero-call checks

Python >=3.10, NumPy and Matplotlib. No PyTorch, model weights, inference services or API keys. Existing environment has these dependencies. Property tests use deterministic generated cases and independent enumerations, without requiring Hypothesis/pytest. Linux x86_64 with Landlock ABI>=4 is required for learner execution; unsupported isolation fails closed.

```bash
cd /home/gaoym/When_Learning_How_to_Ask/experiments/qrelbench_v01_20261030
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 -B audit/reviewer_checks.py
```

Single-thread variables must be set **before** importing NumPy. The worker rejects multithreaded bootstrap. This is audited isolation for built-in policies, not a general-purpose hostile-code sandbox. Private files are not distributed to learner authors. A seed known before evaluation could reconstruct facts, so the real development seed is generated privately, not a constant in source/config. Its commitment binds the run. Publishing the development seed later does not authorize using it for training/evaluating on these same worlds; future train/test seeds must be newly and independently generated.

## Frozen CPU pilot

`configs/development.json` contains the scientific parameters, bounds and split namespace, but no usable seed. Only the trusted evaluator reads `artifacts/private/evaluator_seed.json`; its hash is in `freeze.json`. Existing run directories refuse overwrites/retries. This invocation has already been executed for the delivered pilot; do not rerun or expand it without a new research decision.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 -m qrelbench.evaluate
python3 -m qrelbench.analyze
```

Analysis can be recomputed without generating responses. To reproduce the exact observations, a privileged researcher uses the retained seed/config/source receipt in a separate authorized output directory. Copies using a new seed are new development runs, not exact reproductions. The requested stopping point is the completed small pilot; no confirmation or LLM run is included.

## Outputs

- `freeze.json`: pre-run source/config/test/protocol hashes plus private seed commitment.
- `artifacts/run/episodes.jsonl`: full policy-episode denominators, costs, exact scores, completion/censoring, transcript hashes and worker isolation receipts. This is evaluator output, never learner input.
- `artifacts/run/private/reproduction.jsonl`: privileged provenance/seed, catalog records/truth/types, counts, certificates and first 128 transcript events. Remaining observations are reproduced deterministically and bound by full transcript SHA; no claim that every full transcript is archived verbatim.
- `artifacts/run/execution.json`: actual counts, timeout/failure status, no retries, zero model calls.
- `artifacts/analysis/`: JSON/CSV summaries, paired development intervals and standalone PNG/PDF plots.
- `audit/INDEPENDENT_REVIEW.md`: separate-agent local source/CPU audit, failures/corrections and claim limits.
- `VALIDATION.json`, `FINAL_RECEIPT.json`: integrity, history preservation and reproducibility evidence.

Fixed-budget scores are full-vector exact recovery at equal task+type online budgets. Offline costs are separately charged equally. Fixed-confidence reports certificates **and censoring**, including the cap cost, and is not the original theory-optimal GLR. No asymptotic or real-world claim follows from this pilot.
