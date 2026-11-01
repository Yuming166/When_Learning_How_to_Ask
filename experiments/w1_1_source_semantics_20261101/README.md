# W1.1 — Source Semantics and Provenance Repair

[中文报告](REPORT_ZH.md) · [全量 casebook](CASEBOOK.md) ·
[人工审阅包](human_review/README.md) · [来源图](PROVENANCE_GRAPH.md)

This is a development audit over the exact frozen W1 corpus. It does not modify
W1 or authorize a model run. New claims/pages/model calls/Y observations are zero.

Inputs and contracts:

- `SCOPE.json`, `SCHEMA.md`: scope, five semantic states, access missingness,
  attributed statement unit and independent-review gate.
- `PARENT_RECEIPT.json`: all 78 parent file hashes plus the parent manifest hash.
- `claims.json`: hand-authored typed normalization preserving the original targets.
- `drafts/semantics_*.json`: canonical authored statement records and exact short
  spans, each source under 20 quoted words; these are provisional AI annotations.
- `quarantine_diagnosis.json`: schema limitations and remaining insufficiencies
  are separate, overlapping reasons; no schema-only binary admission.

Derived outputs:

- `pages.json`, `page_semantics.csv`: all 54 claim×field rows, 50 real URL rows.
- `statement_index.json/csv`: 47 exact-span record pointers, attribution, polarity,
  context, source locator and hash. Quotes are stored only in canonical drafts.
- `provenance_graph.json`, `provenance_edges.csv`, `dependency_pairs.json/csv`:
  separate document identity, representation, statement and material-family views.
- `natural_error_feasibility.json`: fixed-corpus correction-related leads only.
- `human_review/`: two prepared packets and genuinely blank human forms, PENDING.
- `CONTROLLED_CORRUPTION_PROPOSAL.md`, `THEORY_HANDOFF.md`: proposed design and
  modelling boundaries; no edited documents or new theorem claimed.
- `SUMMARY.json`, `CHECKS.json`, `VALIDITY_REVIEW.md`, `MANIFEST.sha256`: counts,
  reproducibility checks, AI validity review and final file hashes.

Offline rebuild and verification (no network/model clients):

```bash
cd /home/gaoym/When_Learning_How_to_Ask/experiments/w1_1_source_semantics_20261101
PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/miniforge3/bin/python build.py
sha256sum --quiet -c MANIFEST.sha256
```

The build validates original-claim identity, all parent hashes, full annotation
coverage, exact short-span occurrence, graph references and zero approved binary
records. It preserves authored semantic decisions; it does not determine their
correctness or convert machine review into a human signature. BeautifulSoup4 is
used only to inspect already-saved HTML metadata; Python and package versions
remain recorded in the parent `RUNTIME.json`.

`V_current` in W1 meant the nonarchive-URL representation returned in that audit,
possibly from a browser cache. W1.1 uses version-aware semantic records and never
fills historical observations from those representations. Publication, modification,
event applicability, requested archive timestamp and actual acquired snapshot
time are distinct. No crawler timestamp is turned into a fabricated event date.

A new directory containing richer records does not change the original two W1
candidates or ten quarantines. P021 now has a conservative full-target attribution
summary; that is an explicitly post-W1 schema decision, pending human adjudication.
