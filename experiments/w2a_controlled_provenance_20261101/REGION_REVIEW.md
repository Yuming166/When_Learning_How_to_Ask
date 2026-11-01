# Review of the fixed-policy adaptivity region

Date: 2026-11-01. Scope: ADAPTIVITY_REGION_PROOF.md,
check_adaptivity_region.py, center_policy.json and the corresponding policy
receipt. This is an additional AI mathematical/code review, not human review or
cross-model evidence. No network/model calls or full-grid reruns were made.
Only this file was added; the four previous independent-audit files were
hash-compared before and after the read-only check and remain unchanged.

## Verdict

**PASS under the stated constructed model and per-trajectory hard budget.**
The argument proves that one frozen observation-adapted policy, including its
terminal decoder, has an absolute error advantage of at least
**143/25000 = 0.00572** over every permitted static allocation/decoder throughout

\[
|r-3/4|\le 1/4000,\qquad |a-4/5|\le1/4000,
\qquad c/\ell\in[4/5,1],\qquad B=8\ell.
\]

No material proof gap or required correction was found. The result is a
computation-assisted, stable finite-budget separation. It does not establish
that the frozen policy remains adaptively optimal at every nearby parameter,
that the bound is tight, or that the model describes natural Web observations.

## Main reasoning checks

1. **The cost-feasible class really is constant.** Every useful nonempty path
   has integers 1≤m≤n. If m+n≤8, then n+γm≤8 for γ≤1. Conversely,
   n+γm≥n+(4/5)m=(9/10)(n+m)+(1/10)(n−m). Thus m+n≥9 implies cost at least
   8.1, violating the hard cap. Empty paths are handled separately. Nonnegative
   action costs also make every prefix feasible. This establishes equality of
   complete feasible action trees and static allocations, not merely feasibility
   of the chosen policy. At γ=3/4, (m,n)=(4,5) becomes newly feasible; the proof
   correctly declines to cross that boundary without another argument.

2. **The adaptive coupling needs at most eight perturbed bits.** A new root
   consumes one source-correctness bit and its read consumes one extraction bit;
   a reread consumes only a fresh extraction bit. Before the first mismatch,
   shared theta and algorithm randomness produce the same history and action in
   both systems. Each newly exposed uniform variable is independent of the past,
   so its conditional mismatch probability is at most ε, even though the next
   type of bit is chosen adaptively. The common path exposes at most m+n≤8 bits.
   A conditional union bound therefore gives total mismatch probability ≤8ε.
   The proof does not incorrectly assume that selected observations remain
   unconditionally independent. Persistent extraction errors or correlated
   roots require a different generative argument.

3. **The output rule is frozen as required.** The policy actions, stopping
   choices and center-parameter terminal Bayes sign are held fixed. A center
   tie uses an independent fair coin shared between the coupled executions.
   These algorithm random variables have no changing parameter and add no ε
   term. No channel mismatch means identical error indicators, giving the
   8ε risk bound. The checker computes the terminal sign with r0,a0 while
   replaying channel transitions with the perturbed r,a; it does not reuse
   center transition probabilities for the changed model.

4. **Static opponents may reoptimize.** The cost argument supplies one common
   static strategy class. The 8ε bound applies uniformly to each fixed member,
   including its allocation, randomization and terminal decision map. Taking
   the infimum after applying that bound gives the claimed bound on the optimal
   static value. A different optimizer can be selected at each parameter point;
   no step silently fixes the center static optimizer or decoder. Parameter-aware
   choices can be viewed as selecting a member of this common class before
   observations. Randomized allocations are convex mixtures of feasible fixed
   allocations, and randomized decoders cannot improve on pointwise Bayes risk.
   Exchangeability then justifies the 22 nondecreasing depth allocations,
   including empty and unused-budget designs. For a fixed feasible allocation,
   early stopping can be simulated by ignoring later observations.

5. **The final bound and units are correct.** The center separation is
   243/25000. Subtracting 8ε for the fixed adaptive policy and 8ε for the
   reoptimized static value yields 143/25000 at ε=1/4000. No additional fee
   perturbation term is necessary because the feasible class is unchanged and
   the objective is error under a hard budget, not error plus monetary loss.
   The guarantee is 0.572 percentage points of absolute error, not a 0.572%
   relative reduction. The parameter box has positive volume and its channels
   are strictly between chance and perfection.

## Code and certificate checks

The 37 nodes in center_policy.json exactly match the reachable policy retained
in the previous independent rational expectations. Their `remaining` field is
the center bookkeeping quantity 8−m−n; using it at another cost ratio is
legitimate because the allowable action tree is unchanged. It is not asserted
to be the actual monetary remainder when γ<1.

I read the checker and ran its packaged read-only replay once. It returned PASS:
37 closed reachable states, 22 static allocations, 112 endpoint integer-pair
checks, center policy risk 24899/100000, center optimal static risk
25871/100000, and margin 143/25000. The checker explicitly enumerates latent
reports and ordered answers and computes a reoptimized static decoder at each
tested corner. These corner tests are implementation sanity checks; the proof
of the whole continuum is the common-menu/coupling/infimum argument above.

Checked policy SHA256:
`78266efc5e4a9124ae45964b6713a889b05c79a7b5a553f596fd5b3f0d2c665c`.

Checked region-checker SHA256:
`411393c54525beb335f127c3374b7f2eaa9d1618bd26da263d90fbeaee9e2b80`.

## Claim boundaries to preserve

The center expected cost 6.3612 is a descriptive policy statistic. The theorem
compares policies satisfying **cost≤8 on every trajectory**. It does not show
that this adaptive policy beats every static design constrained only by expected
cost≤6.3612 or expected cost≤8; those are different optimization classes.

The proof requires independent constructed roots, iid reading noise conditional
on each persistent root report, a fixed symmetric prior, declared provenance,
the stated action costs and no extra factual information from copy identity.
It assumes no calibrated learned channel or natural independent-root evidence.
Center global adaptive optimality is unnecessary for the separation: feasibility
and its certified risk suffice against the certified static lower bound.

The region was derived after observing the frozen-grid witness. Its status is
development-stage theory, not a preregistered confirmation experiment. The
standard coupling and infimum-Lipschitz steps are sound but are not themselves
new general mathematical tools. Broader novelty and applicability claims remain
separate from this validity review.
