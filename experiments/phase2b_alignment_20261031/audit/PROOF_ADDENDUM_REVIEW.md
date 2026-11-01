# Proof addendum scope review

2026-10-31. Separate same-family reviewer; this is a comparison with the previously committed independent derivation, not a second independent-model proof or an executable-code audit. Only the two new drafts below were read for this follow-up. No experiments, private seeds, code changes, or historical edits.

**Verdict: PASS FOR THE STATED CONDITIONAL IDEAL-POLICY CLAIM.** The addendum and correspondence matrix agree with the independent derivation. They preserve the distinction between a proved mathematical policy under explicit premises and the current floating implementation. No mathematical disagreement requiring a change was found within this scope.

## Hash-bound inputs

| Input | SHA256 |
|---|---|
| `PROOF_ADDENDUM.md` | `60d6197e4fe6bb35f5a015d42eaf9394b09eb14c8a77a6076647b65b779eb5e6` |
| `ALIGNMENT_MATRIX.md` | `364b64eec92952f5a985a3ba9b87e65b07444fe32d290e59a373194d40d311a7` |
| Independent `audit/THEOREM1_REVIEW.md` | `ac80995ab40ab3638492d091eb78354606747bdbd4044ebc8900b7797411ebba` |

This verdict binds these file contents; later substantive changes require another comparison.

## Assessed points

- [Ideal theorem and machine limits](../PROOF_ADDENDUM.md:7): actual feasibility and optimality errors must obey a delta-independent vanishing modulus. The text explicitly states that requested tolerances, fixed float64 floors, and an unenclosed GLR do not certify that premise or the original arithmetic error guarantee. The [matrix](../ALIGNMENT_MATRIX.md:12) preserves these limits. It does not promote logged numerical gaps into a proof of infinite-horizon accuracy.
- [Optimizer stability and online margin](../PROOF_ADDENDUM.md:15): the all-task separating direction, relative boundary neighborhoods, compact optimizer set, fixed-cost normalization, and explicit r*/K margin match the independent lemmas, including alpha=0, q=.5, and p=1-eta. No uniqueness assumption was silently introduced.
- [Tracking and updates](../PROOF_ADDENDUM.md:29): the all-round cumulative-target convention gives the stated O(sqrt(t)) count discrepancy under square-block forcing. Held O(sqrt(t)) updates and delta-uniform grid/oracle moduli are compatible with the Cesaro argument. This is a proved deterministic extension of the original randomized policy, as the drafts say.
- [Finite-calibration tail repair](../PROOF_ADDENDUM.md:45): the explicit calibration-ratio and allocation-error bounds give drift R+gamma*t uniformly over all wrong alternatives and all t>=(K+epsilon)R. Combining the 2M offline and t online centered log-likelihood increments at deviation proportional to t repairs the historical offline-event gap. The net/interpolation, uniform-in-delta constants, summation, and separate fixed-delta admissibility arguments agree with the independent review.
- [Stop-check delay](../ALIGNMENT_MATRIX.md:19): interpret “gap o(R)” as a bound on the **maximum per-run interval between checks, uniformly over every later horizon**. The stated fixed interval g_R=max(16,ceil(sqrt(R))) satisfies this condition. If t>=(K+epsilon)R, its last checked time s obeys s>=t-g_R>=(K+epsilon/2)R for large R. Also s/t->1 uniformly on those horizons. Applying the repaired bound with internal epsilon/2 therefore preserves the all-t tail and its expected-time conclusion. A statement about check gaps only near one selected horizon would be insufficient; the matrix's explicit fixed schedule avoids that ambiguity.

The drafts are suitable to freeze with this conditional scope visible. This review does not certify the new executable, numerical results, floating cumulative sums, solver rounding bounds, or external literature statements. In particular, it supplies no unconditional asymptotic-optimality or exact delta-correctness theorem for the Python program.
