# W2a independent numerical and validity review

Date: 2026-11-01. Reviewer: another Codex agent using only local files and CPU
calculations. This is an independently implemented verifier and AI code/evidence
review, not human review or cross-model evidence. Constructed truth is checked by
deterministic rules; completing this controlled track does not depend on a human
signoff. No new Web requests, external-model calls, training, or Methodology
experiments were performed by the reviewer.

## Result

**PASS within the explicitly constructed, known-channel, finite-budget model.**
The independently implemented rational calculations agree with the tested
floating-point calculations. The two reported strict advantages over the
stronger, arbitrary-static-allocation baseline have exact rational witnesses.
The central small-budget negative results, perfect/chance-channel boundaries,
and persistent-extraction violation remain intact. This result does not establish
natural Web reliability, real extraction quality, unknown-channel learning,
empirical root acquisition cost, or unrestricted asymptotic optimality.

The four reviewer-owned files are independent_checks.py,
INDEPENDENT_EXPECTATIONS.json, INDEPENDENT_CHECKS.json, and this document. W1,
W1.1, the parent engine, generator and report were not modified by this reviewer.

## What was independently calculated

The reference uses Fraction arithmetic. Its Bellman state preserves roots in
creation order; it never sorts/canonicalizes roots and does not call the parent's
transition, likelihood, or value helpers. It integrates hypothetical theta and
source reports to compute a posterior, but never supplies realized theta or V
to a policy. Available actions are stop, reread an existing root for one cost
unit, or activate a fresh root and read once for c+1 units.

A separate latent enumeration sums over theta, all root reports, and every
ordered response history. This cross-checks the reference count-likelihood
formula rather than merely repeating the parent closed-form formula. Explicit
page schedules are also mapped to declared roots before latent enumeration.
Repeating one page and reading different copies assigned to that same root have
identical **complete joint laws**, not merely equal terminal accuracy.

| Verification | Count / result |
| --- | ---: |
| Parent float values versus independent rational values | 461 comparisons, all pass |
| Largest absolute discrepancy | 3.3306690738754696e-16 |
| Declared comparison tolerance | 2e-12 absolute |
| Fixed-design latent-sum versus count-law comparisons, total reads 0–6 | 64 |
| Reference perfect/chance/persistent-error boundary identities | 264 |
| Complete page-copy joint-law checks, reads 1–6 | 6 |
| Central witness reachable conditional policy values | 37 |
| Confidence-diagnostic field checks, including null zero-coverage cases | 150 |
| Frozen law configurations present and exactly checked | 80 / 80 |
| Frozen cost configurations present; budget/accounting checks | 81 / 81 |
| W1 / W1.1 receipt files retaining content hashes | 78 / 31 |

The 461 numerical comparisons include the numerical confidence fields; the 150
confidence checks additionally include null-valued fields when acceptance has
zero probability. These counts should not be added as disjoint experiment
denominators. All 81 cost-grid DP values were **not** independently recomputed:
the rational DP checks cover the stated small, boundary and two witness cases.
The full grid remains the parent's exhaustive floating-state calculation, with
the corresponding scope and tolerance disclosed.

## Exact witnesses and retained negative results

At r=3/4 and a=4/5, same-root error for n=1,…,6 is
0.35, 0.35, 0.302, 0.302, 0.27896, 0.27896. Fresh-root error is
0.35, 0.35, 0.28175, 0.28175, 0.235169375, 0.235169375. The same-root and
fresh-root joint laws already differ at n=2 even though their Bayes errors tie.
The independently enumerated DP is no better than the best fixed completed
depth at every central budget B≤6 with c∈{0,1}. This negative result is retained.

For the stronger baseline, the reference enumerates **all within-budget static
depth allocations**, including allocations leaving budget unused. This differs
from the parent's full-spending partition reduction and independently checks
that reduction at the two witnesses.

| Parameters | Best arbitrary static allocation | Exact DP risk | Exact gain over static |
| --- | --- | --- | --- |
| r=3/4, a=4/5, c=1, B=8 | (1,2,2): 25871/100000 = 0.25871 | 24899/100000 = 0.24899 | 243/25000 = 0.00972 |
| r=9/10, a=4/5, c=1, B=12 | (3,3,3): 43158943/488281250 = 0.088389515264 | 35735359/488281250 = 0.073186015232 | 3711792/244140625 = 0.015203500032 |

The reference evaluates 353 ordered Bellman states for the first witness and
8,997 for the second. It examines 22 and 77 static allocations respectively
when unused-budget allocations are included. These counts differ from the
canonical parent solver by construction, without changing values.

The first witness's 37-node reachable policy is retained in
INDEPENDENT_EXPECTATIONS.json. One optimal policy opens two roots first. At the
next decision, agreement leads to rereading an existing root, whereas disagreement
leads to opening a third root. Subsequent decisions and stopping depend only on
observed counts and remaining budget. The stored tree is one optimal realization;
ties do not imply a unique action sequence.

At the first witness, the equal-depth baseline's error is 0.266672, so its larger
gap of 0.017682 must not be called the gain over every nonadaptive design. The
arbitrary-depth baseline reduces that gap to the certified 0.00972. The parent
recorded this baseline strengthening in amendment A1 and preserved the initial
run. These two witnesses were selected for additional verification after the
grid results were available; they are not a newly frozen confirmation sample.

## Information and cost fairness

Code inspection finds the same equiprobable binary-truth prior, known r/a, and
correct generative-law Bayes decoder in all accuracy comparisons. The fixed
mixed-depth baseline integrates complete root-specific count likelihoods; it
does not pool votes while ignoring dependence. Its optimization over known-law
expected risk is allowed design information, not access to a realized answer.

BudgetSolver reads parameters and observed count states only. Neither it nor
run_exact imports evaluator gold, corpus roots, seeds, or realized truth/report
records. The selector-visible fixture manifests also exclude those hidden fields
under their declared interface. This is an interface and code-path separation,
not an adversarial operating-system security guarantee.

Root activation cost is charged once per activated constructed root. Reading
another copy of that root does not activate a new root. The common read cost is
one. The base model charges no additional page-opening overhead, explicitly an
idealization. Baselines and DP share the same budget cap, and unused budget or
early stopping are permitted. None obtains a free realized report from an
oracle. The known root grouping and independent-root supply are assumptions of
the constructed experiment, not discoveries about real pages.

The URL-iid rule is confined to the confidence diagnostic. It does not replace
the proper decoder in the accuracy comparison. In the symmetric one-root case,
its answer sign can agree with the correct Bayes decision while its confidence
is badly inflated; therefore this experiment supports a calibration failure,
not an artificial accuracy failure for a deliberately weak baseline.

## Boundaries and corrections checked

- r=1 removes persistent source error; arbitrary regrouping of the same total
  number of iid reads has the same informational law.
- a=1 reveals a root report exactly; rereading that same root cannot eliminate
  its source error. Fresh independent roots can still add evidence.
- r=1/2 or a=1/2 yields Bayes error 1/2 under the specified model.
- A persistent reading-error bit per root violates the main iid-reading
  assumption. At the central parameters, repeated-root error stays 0.35 for
  every tested repeat count, rather than decreasing toward the source floor
  0.25. This is retained as a violation control, not silently fitted to the main
  channel.
- The reviewer identified zero-probability count histories in the confidence
  helper as a possible 0/0 boundary failure. The parent added an evidence-mass
  guard. Independent confidence checks now include perfect and chance
  boundaries and pass after the fix. The main central diagnostic was unaffected.

The rendered corpus and numerical law experiment have different jobs. The
1,152 HTML files are deterministic controlled semantic fixtures, including
mixed/attributed/unaddressed wrappers. They are **not 1,152 model calls or 1,152
measured extraction trials**. In particular, a NOT_ADDRESSED fixture cannot
simply be treated as an observed atomic V report. Numerical risks here come
from the stipulated atomic root-report channel; no Y was extracted from these
HTML files. The generator's separate DOM/text checks establish construction
consistency, not natural-language reader performance. Its balanced finite truth
fixture also does not establish an iid multi-fact population.

The source-error mechanism and probabilities are explicitly simulated. The
review preserves all these conditions rather than seeking a positive result by
changing labels, hiding ties, weakening decoding, or counting copies as fresh
evidence. A new experiment would be needed to make any claim about natural
source errors, uncertain provenance, learned reliability, or an actual model
reading these documents.

## Reproduction

From this directory, run `python3 independent_checks.py --write-expectations
--check-engine` after the parent outputs exist. This runs only local exact
calculations and read-only audits; it writes the two reviewer JSON outputs.
The checked engine, verifier and protocol hashes are recorded in
INDEPENDENT_CHECKS.json. The script does not modify any historical parent file.
