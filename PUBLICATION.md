# Public research snapshot — 2026-11-01

This release collects existing theory, methodology source, protocols, tests, reports, mathematical certificates, and selected small aggregate results from isolated local worktrees. It preserves the original repository history and V5 PDF. It does not execute or extend scientific experiments.

## Included and excluded

The source manifest lists each exported file, original checkout alias/path, original SHA-256 and published SHA-256. The explicit export allow-list includes Python, Markdown, JSON configuration/certificates/selected aggregates, CSV summaries, LaTeX, figures and requirements files. Downloaded inputs, raw trajectories/model responses, private seed/reproduction records, model weights, dependencies, caches, logs, third-party full-page bodies and synthetic corpus/hidden-label dumps are excluded. The exclusion ledger records reasons; it contains file names, not excluded contents.

Historical results and negative findings are retained. Some large per-path diagnostics are excluded even though their public reports are included. Raw-data audit claims in those reports refer to the original producing environment, not to a new audit performed from this subset.

## Two different kinds of hash record

1. `publication/SOURCE_MANIFEST.json` binds the actual exported source subset and lists the original source hashes.
2. Historical `freeze`, `receipt`, `SOURCE_SNAPSHOT`, `INPUT_HASHES` and `MANIFEST.sha256` files are retained as original provenance. They can refer to omitted/private files, original absolute paths, and original code bytes. They are not rewritten to manufacture a complete historical rerun from the public subset.

Six runtime source files replace eleven workstation-specific dependency paths with repository-relative paths. `publication/PORTABILITY_CHANGES.json` records every before/after expression and both hashes. These edits do not change acquisition policies, posterior formulas, losses, parameter grids, splits, likelihoods, or scientific results. Strict historical runners may reject the adapted release against their original source freeze; that is expected. Use a new explicitly declared experiment and separate output paths for any future run, rather than impersonating a historical replay.

## What is reproducible here

- Read the theory statements, full derivations, exact certificates and certificate-producing code.
- Run core environment/method unit and engineering checks without private seeds, external inference or training.
- Inspect all method versions and their development decisions, including unsuccessful LoRA/residual-policy attempts.
- Generate synthetic controlled inputs using the included generators if separately choosing a new experiment.

Exact reproduction of historical aggregate statistics needs the locally retained private seeds and excluded raw records. Trained-policy inference also requires the omitted checkpoints; training requires optional dependencies and separately acquired model files. We do not substitute new seeds, new runs or zero-valued costs for missing historical artifacts.

The public check command validates source integrity, syntax, JSON and selected deterministic/technical contracts. Passing it does not prove novelty, real-Web validity, asymptotic optimality of approximate policies, or the completeness of historical experiments.

## Local-only provenance notes

Some historical Markdown and JSON retain absolute producing paths. Follow the relative root README/method navigation for public entry points; historical local paths identify provenance rather than a public download location. Input receipts are preserved without changing their meaning. Files newly created for publication, dependency-path changes and new technical checks are distinguished from scientific artifacts.

No new project license is invented by this export. Third-party datasets, models, and web pages remain subject to their own terms and are not redistributed as downloaded corpora here.
