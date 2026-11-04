# Catalogue-mechanism validation

This isolated experiment uses the frozen recommendation loop and repaired IG
to test four predeclared theory-anchor cells with fresh paired response tapes.
It preserves all older experiment records and does not change the manuscript.

The scope is finite-query validation of catalogue/sharing mechanisms. There are
two all-positive constructed profiles, 12 independent response-tape clusters,
three policies, two risk settings, and 144 planned paths. All group types are
zero to hold the response channel fixed across partition changes. A fixed-A
strategy would be strong in these controlled states; this is not a nontrivial
natural reliability-discovery benchmark. See [PROTOCOL.md](PROTOCOL.md).

Source hashes, configuration, world construction, and analysis are recorded in
`FREEZE.json` before main outcomes. All policies use the same exact certification
and cap. Capped answers are never certified. No empirical oracle is synthesized.

From the worktree root, with `/storage/gaoym/miniforge3/bin/python`:

```sh
python -B -m unittest discover -s experiments/catalogue_mechanism_20261104 -p test_protocol.py -v
python -B experiments/catalogue_mechanism_20261104/run.py --mode smoke
python -B experiments/catalogue_mechanism_20261104/run.py --mode runtime_smoke
python -B experiments/catalogue_mechanism_20261104/analyze.py --mode smoke
python -B experiments/catalogue_mechanism_20261104/analyze.py --mode runtime_smoke
python -B experiments/catalogue_mechanism_20261104/run.py --mode freeze
python -B experiments/catalogue_mechanism_20261104/run.py --mode main
python -B experiments/catalogue_mechanism_20261104/analyze.py --mode main
```

The executable sets single-thread BLAS/OpenMP settings before NumPy imports and
uses at most two pinned CPU workers. Existing output namespaces are rejected;
there are no automatic retries or replacements. To reproduce an already-run
stage, use a separate checkout and preserve the original records.

Raw JSON histories, complete failures, counts, seeds, generation settings,
posterior diagnostics and runtimes stay under ignored `artifacts/`. The main
analysis saves `results/analysis.json`, `results/plot_data.csv`, a results report,
and PNG/PDF scientific figures. Full seed vectors and clustered bootstrap
intervals remain available. Post-run receipts and interpretation are separate
outputs so the pre-outcome analysis source stays frozen.

No Qwen/model/API calls, network requests, GPU work, model training, historical
validation reuse, or policy optimization are included.
