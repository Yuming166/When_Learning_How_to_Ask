# Historical fashion evaluation: auditable outcome snapshot

This release supports the revised manuscript without republishing marketplace
records, hidden synthetic profiles, prompts or model event streams. It introduces
no new model calls, policies, users or experiments. All six panels include the
full budget range 0--6 and all four query policies. The small Python panel has
repeated prior draws; Luna 8 has repeated answer banks; neither enlarges the
number of independent profile clusters.

Run `python experiments/fashion_evidence_snapshot_20261105/analyze.py` from the
repository root to reconstruct accuracy curves. Original summary metrics retain
their uncertainty estimates and scope; reconstruction does not re-certify their
bootstrap methods. SOURCE_MANIFEST.json binds exact source bytes and compressed
outcome records. The archived source reports preserve development status,
holdout results, numeric failures and negative simulator behavior findings.
Read ERRATUM.md for one corrected diagnosis of the Luna parser failure.

The development panel covers 338 products through 35 menus of 5--10 items,
not one simultaneous 338-item recommendation. Reserved panels cover 78 validation
and 55 test products. Preferences are synthetic in every panel. Luna provides
structured field answers, not observed human purchase choices. Luna 48 reuses
the development profiles and menus; it is not an independent confirmation.
The prior BUY_TIED behavior screen (9/12) failed its acceptance gate.

`fashion_engine_reference.py` is a byte-identical historical algorithm source
reference, not a standalone simulator. Its belief implementation replaces known
fields in prior draws; it must not be presented as a general exact Bayesian
update for correlated or noisy preferences. The new joint-reliability experiment
is separately implemented in `../decision_value_bridge_20261105/`.

To create the snapshot from the original local experiment tree:
`python experiments/fashion_evidence_snapshot_20261105/snapshot.py --source-root /path/to/original/worktree`.
