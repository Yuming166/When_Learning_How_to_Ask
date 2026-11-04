# Public replay, without collecting responses

These instructions were added after analysis; the eight frozen source files are
unchanged. Use Python with NumPy and SciPy (recorded environment: Python 3.13.13,
NumPy 2.5.3, SciPy 1.18.1). Matplotlib is needed only for legacy imports/plots.
No model credentials, network, GPU or training are required.

From a fresh checkout:

```sh
python -B experiments/decision_value_bridge_20261105/replay_release.py
python -B experiments/decision_value_bridge_20261105/test_protocol.py
python -B experiments/decision_value_bridge_20261105/analyze.py --mode main
```

The first command checks frozen sources/dependencies and the archive checksum,
then unpacks 310 JSON files (engineering smoke tests plus all main histories).
Existing byte-identical files are accepted; different files are never replaced.
The final command reconstructs every adaptive action/reply history and terminal
certificate and regenerates the complete analysis and manifest. It uses six CPU
workers with one numerical-library thread each. It does not generate new data.
The saved analysis includes measured original CPU times, not replay timings.

To rerun stochastic generation, use a separate fresh checkout, do not unpack the archive, and run `run.py --mode main`. It checks the frozen configuration and
refuses an existing main output directory. Do **not** rerun `--mode freeze` over
the released freeze. Rerunning data generation will change wall/CPU timings;
response/action/certificate evidence should be compared separately. Existing
failed KL paths are part of the frozen implementation, not missing jobs.

Read `INTERPRETATION.md` before treating these results as a method advantage.
The posthoc standardized-accuracy supplement distinguishes raw audit counts
from equal-catalogue paired contrasts; they are not interchangeable estimands.
