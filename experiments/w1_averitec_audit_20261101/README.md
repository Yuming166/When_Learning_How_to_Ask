# W1 AVeriTeC audit — data only

Read [REPORT_ZH.md](REPORT_ZH.md) for the outcome and [CASEBOOK.md](CASEBOOK.md)
for all 12 claims and 54 claim×field-value records (50 HTTP-page rows, 4 sentinel rows).

This directory is isolated from previous experiments. No model-service inference,
training, agent-policy experiment, Method/CRAG/M3 rerun, commit, or publication
was performed. AI-assisted annotation is not human signoff. The only authorized
stage was W1. W2 candidates are provisional; W3 is not authorized.

## Frozen inputs and reproduction

- `PROTOCOL.json` / `PROTOCOL_FREEZE.json`: rule written before this audit's train download.
- `inputs/UPSTREAM_RECEIPT.json`: exact upstream commit, download URLs and hashes.
- `inputs/train.json`: training split only; upstream CC BY-NC 4.0, see saved README.
- `selected_claims.json` / `SELECTION_RECEIPT.json`: 6 nonempty Supported + 6 Refuted;
  deterministic hash ranking, no replacement.
- `ACCESS_CLARIFICATION.md`: disclosed post-selection access-method clarification.

Offline reproduction from the saved artifacts, with no network or model calls:

```bash
cd /home/gaoym/When_Learning_How_to_Ask/experiments/w1_averitec_audit_20261101
PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/miniforge3/bin/python audit.py verify
PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/miniforge3/bin/python build_report.py
sha256sum -c MANIFEST.sha256
```

`build_report.py` normalizes supplied provisional annotations and checks coverage;
it does not automate semantic verification. Its list of readable representations
is an explicit audit input, not an accuracy score. The two W2 candidates must not
be used as a confirmation set.

Optional *fresh acquisition* can only be reproduced in a new copied directory:
`audit.py inventory`, then `audit.py capture`. Capture refuses to overwrite an
existing access log. This will fetch the nominated URLs again, so resulting page
bytes and availability can differ. Do not run it merely to validate this report.
Capture uses Python standard libraries, BeautifulSoup4, and `pdftotext` for PDF
responses; no model packages or credentials are required. Exact runtime versions
are in `RUNTIME.json`.

The archived train file is sufficient to reproduce selection; to replace a missing
input, use the pinned URL in `inputs/UPSTREAM_RECEIPT.json` and verify its SHA256.
No upstream executable scripts were run.

## Audit records

- `url_inventory.json`, `url_occurrences.json`: unique strings and every field occurrence.
- `access_log.jsonl`: one record per string; Metadata is skipped, never requested.
- `snapshots/`, `texts/`: raw HTTP responses and deterministic extracted text.
- `browser_*/`: exact retained browser-tool returns, including errors and crawler age.
- `browser_access_log.json`: all 40 browser-open records reconstructed from those returns.
- `reviews_*.json`: original scoped AI reviews, with parent corrections in `ADJUDICATION.json`.
- `case_annotations.json`, `page_annotations.json`, corresponding CSVs: normalized records.
- `provenance_relations.json`: typed observations and uncertainty, not independence labels.
- `SUMMARY.json`: all reported denominators and stopping status.
- `VALIDITY_REVIEW.md`: AI validity review; not human or cross-family verification.
- `MANIFEST.sha256`: hashes of final artifacts, excluding this manifest itself.

## Annotation contract

`theta_reference` preserves the dataset binary reference; `theta_status` qualifies
what was actually checked. `V_current` is a legacy field name for the inspected
nonarchive-URL representation; browser caches can be older than retrieval. It is
not a guaranteed live page and cannot populate `V_historical`.

Unknown/partial/mixed/quote-only/source-unavailable states remain `null`. No arbitrary
zero encoding is used: CSVs render null V as `UNKNOWN` and null Y as `UNOBSERVED`.
Evaluator-only factcheck pages and metadata-only leads are excluded from ordinary
body candidates. URL variants and archive/current pairs do not create independent
sources. All `Y` and `V_historical` fields are null; human signoffs are zero.
