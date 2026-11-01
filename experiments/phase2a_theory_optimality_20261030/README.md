# QRelBench Phase 2a

Controlled numerical and CPU-only development work. Start with [PILOT_REPORT.md](PILOT_REPORT.md), [THEORY_PHASE_MAP.md](THEORY_PHASE_MAP.md), and [PROTOCOL.md](PROTOCOL.md). No natural-language reliability, superiority, empirical asymptotic convergence, or rigorous floating-point GLR certification is established here.

The read-only dependency is ../qrelbench_v01_20261030. Python3, NumPy, SciPy, Matplotlib and a Linux kernel supporting Landlock are required. Set numerical backend threads to1:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -m unittest discover -s tests -v
python3 -m phase2a.phase_map
```

The frozen main run uses python3 -m phase2a.runner and analysis uses python3 -m phase2a.analyze. The runner refuses changed hashes, overwritten output, and non-development configuration. It requires the sealed local seed file whose commitment appears in freeze.json. Keep that seed and private reproduction files private. No public seed determinism is claimed. A rerun is a separate explicitly authorized development execution and must use a new output path; these instructions do not authorize launching one automatically.

The run contains792 trajectories and3696 nested fixed-budget snapshots. Check artifacts/run/execution.json before interpreting any output. Failed/partial execution must be reported with its missing jobs and action accounting; analysis fails closed on incomplete runs. Endpoint and sequential GLR calculations are distinct. All source, audit, execution, plotting and historical-preservation receipts are retained locally.

Separate same-family reviewer evidence is in audit/COEFFICIENT_REVIEW.md, audit/GLR_AUDIT.md, and audit/EXECUTION_REVIEW.md. Private state is excluded from release via .gitignore. No Git publication or model calls are part of this stage.
