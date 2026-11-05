# Reproduction

The experiment binds to the exact v0.1 Myntra source environment and the
471-record catalogue SHA256 in `FREEZE.json`. That source worktree must contain
its ignored `artifacts/input/catalogue_strict.jsonl`; no substitute catalogue
revision is accepted.

The full run refuses to overwrite results. For a clean reproduction copy:

```bash
python -B experiments/myntra_closed_loop_dev_v01_20261104/prepare_reproduction.py \
  --destination /tmp/myntra-closed-loop-reproduction
python -B -m unittest discover \
  -s /tmp/myntra-closed-loop-reproduction -p 'test_*.py' -v
python -B /tmp/myntra-closed-loop-reproduction/run.py --stage smoke \
  --source-worktree /home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104
python -B /tmp/myntra-closed-loop-reproduction/run.py --stage full \
  --source-worktree /home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104
python -B /tmp/myntra-closed-loop-reproduction/verify_results.py
```

The test stage and smoke run are local and make no inference calls. The full
stage computes 24 cases against the frozen 2,048-profile-per-pool Monte Carlo
prior. All user profiles, prior samples, prepared catalogue subsets, and raw
paired episode traces are created under ignored `artifacts/` or `results/` in
the reproduction copy; only summary outputs need to be shared. CPU time may
vary; the deterministic outputs should match under the same Python version and
source hashes.
