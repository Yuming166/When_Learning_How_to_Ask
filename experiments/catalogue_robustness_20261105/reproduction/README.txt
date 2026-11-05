Evidence accompanying the short-paper revision

reproduce_tables.py is the entry point. It uses the bundled product attributes,
menus, settings and saved model replies; it makes no network/model calls.
Run `python reproduce_tables.py` for all new menus, or add `--quick` for a small
consistency check. Dependencies: Python 3, NumPy, pandas and requests (the latter
two are imported by the shared collection modules).

experiment_inputs.json contains only the product fields and menus required to
recompute the new results. nine_preference_* retains the post-confirmation
3/4/5-question extension. common_field_* retains the fixed-protocol Myntra and
Amazon comparison. model_bank_* contains the model identities, frozen protocol,
unaltered local API responses and policy replay results. All completed answers
and failures are retained. The original API collection scripts are included for
audit; use reproduce_tables.py for offline replication from this package.

earlier_study_reported_results.json transcribes the supplied original paper's
pages 3-4. Its six-field and Luna results are reported evidence, not a rerun in
this revision. At budgets 3 and 4, that paper reports method differences; the
package does not invent the underlying absolute accuracies or new intervals.

Each new comparison is conditional on constructed preferences and the specified
catalogue. The common-field check fixes one protocol across two catalogue
sources, with attribute labels and prices derived separately from development
records. Model tests use reset structured answer banks from prescribed
profiles; their result concerns answer fidelity and policy replay, not natural
human preferences or unrestricted multi-turn customer behavior.

Full parameter descriptions and retained earlier results are in the optional
research appendix, compiled through ../full_version.tex. ../main.tex is the
four-page short-paper entry point.
