# Catalogue reliability paper: outline and evidence contract

Date: 2026-11-04. Author-review draft; not submitted.

## Paper question

When does learning an initially unknown reliable question format add a positive
first-order interaction cost to identifying the best item in a known catalogue?

The Web challenge is the interaction burden of cold-start recommendation in an
online catalogue. Catalogue-dependent decision requirements and the transfer of
query reliability must be treated together. Merely applying generic active
learning to a Web dataset is not the contribution.

## Four-page argument

1. A shopping assistant needs reliable preference evidence, but need not recover
   every preference. Which uncertainties matter depends on competing items.
2. Define a fixed binary-preference, two-format, shared-rate observation model.
   Compare with an oracle knowing only the better formats, retaining unknown
   rates. No calibration, type-report, preference-disclosure or persistent-error
   actions are included in this manuscript.
3. The general KL characteristic is established pure-exploration machinery.
   Reduce the new structural question to minimal decision-changing flip sets.
4. Prove an exact entropy-cut criterion for zero premium. Explain the unique
   oracle-allocation corollary and show that equal group sizes can have different
   premiums in an explicit affine catalogue.
5. Instantiate joint inference, decision-directed KL allocation and an anytime
   certified stopping rule. Separate ideal tracking's asymptotic contract from
   the finite-tolerance implementation actually evaluated.
6. Validate the stated mechanism on predetermined controlled catalogues with
   fresh response tapes. Retain repaired decision-information-gain and uniform
   scheduling; report all trajectories and no algorithm-superiority claim.

## Claims and evidence

| Claim | Evidence | Limit |
|---|---|---|
| Query reliability has an exact zero/positive information-cost boundary determined jointly by the flip family and sharing partition | GENERAL_THEOREM.md, THEORY_AUDIT.md, proof in manuscript | Fixed finite decision map; two common symmetric iid response rates; known groups; zero logarithmic calibration |
| The boundary is independent of the worse rate q | Rate elimination in the main theorem | Premium magnitude and finite-sample performance may depend on q |
| For rho<1/2 and unique oracle weights, equality iff their support lies in one group | Binding-balance and tangent-space proof | Not claimed for saturated rho or nonunique oracle weights |
| Group sizes alone cannot decide equality for top-item recommendation | Exact weighted5 catalogue, matched (2,3) partitions | Constructive theorem example, not a population study |
| Stopping controls wrong recommendations under arbitrary adaptive allocation | Saturated Beta-mixture/Ville proof; exact rational MLE/outward log gate | Model-dependent error control; caps mean abstention |
| A concrete recommendation loop can execute the theory's observation interface | Frozen-source runner, independent tapes, replay records | Numerical allocation/IG integration not asymptotically or globally error certified |
| A new allocation algorithm universally beats IG | NOT CLAIMED | Existing strong-IG negative comparisons retained |
| Natural-language users or LLM simulators satisfy the model | NOT CLAIMED | No human data or model calls in this work |

## Method module sketch

`public catalogue/groups + observed answers -> joint likelihood -> candidate item
and KL allocation -> next fresh answer -> joint likelihood -> exact item GLR
certificate or continue/abstain`.

Inference retains uncertainty in preferences, formats and rates. Allocation
distinguishes wrong recommendations rather than every wrong profile. The gate
alone grants the correctness guarantee; a floating allocation score never does.

## Boundaries inherited from historical work

The original smallest-group theorem concerns full profile recovery. It is
background, not the new top-item theorem. Finite positive calibration,
provenance-dependent Web evidence and training are separate research lines.
The latest fixed-budget certification frontier is a diagnostic and is not used
as a fixed-confidence cost result. This document does not alter any historical
manuscript, theory note, frozen algorithm or experiment record.
