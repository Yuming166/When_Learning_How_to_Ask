# Oracle structure with unknown extraction rates

This stage retains every assumption in `../web_unknown_calibration_20261031/MODEL_AND_SCOPE.md`: known source accuracy, unknown ordered extraction accuracies, finite calibration ratio, finite menu of completed independent source blocks, and online cost. The oracle knows group formats but not extraction levels or truths.

Questions, in order: (1) Must a cost-optimal oracle use only its good format? (2) Can one depth always suffice, or can mixing depths strictly improve its coefficient? (3) What does the answer permit us to conclude about a smallest-group sharing threshold?

Only deterministic calculations and mathematical proofs/certificates are authorized here. Finite alternative grids are discovery relaxations, not continuous optimization certificates. No empirical model calls or training, no changes to prior snapshots, no publication. `INPUT_HASHES.json` records historical inputs before this stage.

Initial bounded diagnostic: source accuracy in {.6,.8,.95}, extraction pairs {(.65,.5),(.8,.6),(.95,.6),(.95,.9)}, d in {1,2,4,8}, alpha in {0,.1,1,10}, setup cost in {0,1,10,100}, unit read cost, maximum depth 6, eta=.025. Alternative grid spacing .015 plus true rates and boundaries. Compare all actions, pure-good actions, and each fixed pure-good depth. This is a mathematical counterexample search with all diagnostic cases retained; it is not benchmark selection or confirmation. Any refinement must be recorded explicitly.

## Implementation clarification and post-discovery refinement

The implemented grid uses 33 evenly spaced points on [.5,.975], hence exact spacing .475/32=.01484375, augmented by p and q. It is approximately .015 as described above. The complete main scan has 768 configurations, two LPs per configuration, and all rows are retained in `DISCOVERY_GRID.json`.

After this scan identified depth-mixture candidates, the positive-setup-cost singleton fixture r=.6,p=.95,q=.6,d=1,alpha=1,c=1 was selected for an exact mathematical counterexample. At fixed parameters only, a 10,001-point one-dimensional diagnostic gave min information approximately 1.02997188 for the rational witness b1=14,b2=2, and located convenient alternatives for fixed-depth lower bounds. A further midpoint diagnostic checked the proposed Taylor bound. These exploratory values are superseded by, and not used as substitutes for, the exact continuous certificate. The certificate first verified depth necessity, then added the same-instance known-rate comparison and was rerun successfully. Its final proof checks all 27 actions and all continuous alternatives as specified in the theorem.

A separately delegated mathematical audit also made preliminary comparisons before obtaining its analytic boundary results. Those are not part of the retained 768-case scan; their available provenance and retention limits are recorded separately. They support no effectiveness or universal-optimality claim. The primary certificate, not any adaptive search frequency, establishes the counterexample.
