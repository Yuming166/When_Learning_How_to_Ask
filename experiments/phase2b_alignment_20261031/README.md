# Phase2b: proof alignment and cost convergence

Start with PILOT_REPORT.md, PROOF_ADDENDUM.md and ALIGNMENT_MATRIX.md. All historical source and results are read-only dependencies. This stage produces a mathematical policy argument plus a bounded finite-precision diagnostic; it does not establish that the executable is exactly asymptotically optimal.

Requirements: Python3,NumPy,SciPy,Matplotlib,Linux x86_64 with LandlockABI>=4. Run checks with explicit single-thread numerical settings:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -m unittest discover -s tests -v
```

The once-authorized main command is python3 -m phase2b.runner. It requires frozen hashes and a sealed evaluator seed, refuses existing output, and does not retry. Analysis is python3 -m phase2b.analyze. Integrity and selected existing-world replay use python3 -m phase2b.integrity. Reproduction should use an isolated copy/output; these instructions do not authorize restarting the main batch. Seed bytes and private reproduction data remain private; release excludes them via .gitignore.

All risks are represented as R=log(1/delta), so R1024 does not underflow. Only fixed-confidence d4 experiments run here; shared GLR, reference data, instances, online budgets and type-query costs are matched across methods. Four independent worlds/cell give exploratory uncertainty. Censored means are E[min(T,B)] estimates, never unqualified E[T]. Code/config/proof/audit provenance and final receipts are local artifacts; no GitHub publication, model/API/GPU use or Phase3 confirmation is included.
