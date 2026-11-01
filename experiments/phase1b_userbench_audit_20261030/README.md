# Phase 1b — UserBench suitability audit (2026-10-30)

Read [benchmark_selection_report.md](benchmark_selection_report.md) first. Result: conditional GO as a data source; REVISE for direct use as unknown binary query-reliability evidence. No experimental model calls were made. Frozen Phase 0/1 outputs remain untouched.

Upstream: https://github.com/SalesforceAIResearch/UserBench , pinned commit `80506d2ab484cab843e60a2401ff3e0290d05b87`.
Source clone: `/home/gaoym/userbench-source-20261030` (kept outside the research repository; not modified).

Only local dependency added for this audit: pyarrow 21.0.0 in `.deps/`, excluded from Git. The existing third-party Python 3.12 environment had an unreadable NumPy dependency; it was left unchanged. Reproduction with the system Python 3.13 and existing NumPy:

```bash
python3 -m pip install --no-deps --target .deps pyarrow==21.0.0
PYTHONPATH=.deps python3 audit_userbench.py > audit_execution.log 2>&1
python3 -m unittest -v test_audit.py
```

This script reads all JSON and Parquet, verifies pinned source and official split identities, extracts a narrow explicitly declared binary-contrast subset, and executes five isolated upstream reset methods through AST. It never imports upstream API clients, creates a full Gym environment, runs an Agent, or calls an LLM. Full Gym execution has not been tested; gymnasium is absent in the current audit interpreter.

Artifacts:

- `audit_summary.json`: counts, split reuse, coverage limits, structural option checks and exposed-state probe.
- `source_manifest.json`: pinned code/data provenance with SHA-256.
- `preference_catalog.jsonl`: all 82 preference definitions and their cue counts.
- `preview_public.jsonl`, `preview_private.jsonl`: eight TRAIN-only construction examples; public/private separation and deterministic gold. No collected answers, inferential results, or hidden reliability labels.
- `sources/userbench_emnlp2026.pdf` and `.txt`: official paper snapshot and text extraction.
- `sources/userbench_pdf_preflight.json`: structural preflight availability record. `pypdf` is absent; this sidecar is UNAVAILABLE, not a structural PASS. It does not certify page anchors.
- `benchmark_selection_report.md`: decision, theory mapping, unsafe native information fields, cost and direct-baseline caveats, and proposed bounded diagnostic.

The official paper reports 902 elicitation ways. This pinned release contains 901 distinct exact cue strings and 908 distinct preference/cue pairs; these definitions are kept separate. The adaptation preview is not claimed to be native UserBench performance, human evidence, or an established shared reliability structure.
