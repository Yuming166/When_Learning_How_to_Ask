# Perfect-source mechanism control

2026-11-01. New isolated theory stage. The completed task is the first recommended mechanism control, not a new empirical experiment.

Read [the Chinese report](RESEARCH_REPORT_CN.md) or [the complete proof](PERFECT_SOURCE_THEOREM.md). The general analytic result is K=(ell+c/N)T for both learner and format-aware oracle when r=1 is known under all alternatives. With c>0, all optimal allocations use only maximal depth. The original sharing criterion is recovered exactly.

## Reproduce bounded checks

From the repository root, using the standard library only:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 research/web_perfect_source_control_20261101/check_identities.py
PYTHONDONTWRITEBYTECODE=1 python3 research/web_perfect_source_control_20261101/verify_artifacts.py
```

The first command checks pointwise count-likelihood factorization, exact expected coefficients in the KL identity, preservation of read totals, and the exact cost difference. It covers truth/type changes, boundary alternatives, q=1/2, c=0, and N=1. It imports the existing full source-mixture law at r=1 and reuses the sealed imperfect-source depth certificate as provenance. It does not rerun the historical 950-cell certificate or infer a universal theorem from finite examples.

The second command checks historical input hashes, sealed output hashes, source bindings, and local links. It does not repeat the mathematical proof.

## Outputs and scope

- PERFECT_SOURCE_THEOREM.md: analytic theorem, complete allocation proof, endpoint expected-cost extension, sharing and mechanism consequences.
- RESEARCH_REPORT_CN.md: interpretation and limitations.
- paper_control.tex: insertable LaTeX, not a standalone compiled manuscript.
- check_identities.py / IDENTITY_CHECKS.json: deterministic rational diagnostics.
- PROOF_AUDIT.md: bounded same-family read audit; no formal or external verification.
- INPUT_HASHES.json: 81 preserved historical files.
- RECEIPT.json / verify_artifacts.py: sealed outputs and integrity check.

No model inference services, GPU jobs, training, numerical optimization, stochastic worlds, or publication actions. The result is pointwise asymptotic, with a fixed finite completed-block menu and known perfect source reliability. No real-Web validity claim is added.
