# Decision Value bridge

Run from repository root:

```sh
python experiments/decision_value_bridge_20261105/test_protocol.py
python experiments/decision_value_bridge_20261105/run.py --mode smoke
python experiments/decision_value_bridge_20261105/analyze.py --mode smoke
python experiments/decision_value_bridge_20261105/run.py --mode runtime_smoke
python experiments/decision_value_bridge_20261105/analyze.py --mode runtime_smoke
python experiments/decision_value_bridge_20261105/run.py --mode freeze
python experiments/decision_value_bridge_20261105/run.py --mode main
python experiments/decision_value_bridge_20261105/analyze.py --mode main
```

Output folders are exclusive-create; an existing stage is never overwritten by
the runner. Reproduce execution in a fresh checkout/output directory after
verifying FREEZE.json. Main outcomes live in results/analysis.json and RESULTS.md;
raw artifacts retain every observation, policy decision and certificate.
