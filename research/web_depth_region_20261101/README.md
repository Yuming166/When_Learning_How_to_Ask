# Explicit depth-mixing region

2026-11-01. New, isolated theory extension; previous artifacts are read-only.

Start with [the Chinese report](RESEARCH_REPORT_CN.md) or [the full proof](REGION_THEOREM.md). The result holds on an explicit five-dimensional parameter box, with alpha in [0.95,1.20] and c/ell in [0.5,1.5].

## Reproduce the mathematical certificate

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 research/web_depth_region_20261101/certify_region.py
```

Only the Python standard library is required. The script recomputes 950 continuous-domain interval bounds, checks all 27 fixed-depth format compositions, and verifies the region inequalities with exact rational arithmetic. It writes only this stage's REGION_CERTIFICATE.json. It imports hash-bound, read-only arithmetic helpers from the two preceding theory stages. The JSON decimal fields are display approximations; pass/fail uses exact inequalities.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 research/web_depth_region_20261101/verify_artifacts.py
```

This checks unchanged historical files, output hashes, certificate/code binding, and local links; it does not repeat mathematical computation. It requires the sealed RECEIPT.json.

## Optional figure

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES='' /storage/gaoym/miniforge3/bin/python research/web_depth_region_20261101/plot_region.py
```

Requires NumPy and Matplotlib. The figure plots closed-form certified lower bounds inside the proven rectangle. Its plotting mesh is not the proof, and the colors do not estimate exact optimal costs. PNG/PDF metadata omit creation timestamps where supported.

## Files and scientific boundary

- REGION_THEOREM.md: self-contained model, theorem, proof, and scope.
- REGION_CERTIFICATE.json / certify_region.py: mathematical certificate and producer.
- paper_region.tex: short English insertion, not an entire submission.
- depth_region.pdf / depth_region.png / plot_region.py: certified-region illustration.
- PROOF_AUDIT.md: bounded same-family mathematical review; not external or formal proof verification.
- INPUT_HASHES.json: 68 preserved historical files.
- RECEIPT.json / verify_artifacts.py: sealed output set and checks.

No source/model service, empirical benchmark, training, large parameter search, or external publication is involved. Theorems concern pointwise asymptotic online-cost coefficients with known source reliability r and unknown extraction rates p,q. Finite-budget performance and real Web assumptions require separate validation.
