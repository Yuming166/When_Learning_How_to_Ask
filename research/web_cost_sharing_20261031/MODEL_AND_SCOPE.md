# Source cost and format sharing: fixed scope

Date: 2026-10-31. This is a new mathematical exploration, separate from the sealed `web_native_theory_20261031` snapshot and all prior experiments.

## Scientific question

Does the optimal depth of reading a persistent source, which depends on source activation cost, change the smallest sharing group needed to eliminate the first-order cost of an unknown query format?

The proposed threshold is a conjecture to prove or refute, not a desired experimental outcome. Finite exact enumeration may falsify statements but cannot replace proofs. No model calls, training, empirical benchmark worlds, or confirmation data are in scope.

## Minimal model

- Fixed d binary facts θ_j and a fixed known partition with sizes k_g.
- Unknown z_g in {A,B}. Known fixed source accuracy r in (1/2,1), and known extraction accuracies 1/2 <= q < p < 1. The known-level assumption is a deliberate restricted extension; it does not revise the original unknown-level theory.
- Every newly activated root serves exactly one fact. Its persistent report is V=θ_j B with P(B=+1)=r. Root errors are independent across acquisitions and facts. There is no purchase sharing across facts.
- At a block boundary, select a fact and a pair (n_A,n_B) of nonnegative integers, with 1 <= n_A+n_B <= L_max. L_max is finite and fixed before inference; all such pairs are available. The whole block is chosen before seeing its responses, completed, and the root is permanently discarded. Responses are independent conditional on V and use accuracy p for z_g, q otherwise.
- Both format-specific positive counts are observed. Balanced blocks and mixed-format blocks are allowed; the learner is not restricted to pure formats.
- A block costs c + ell*(n_A+n_B), with known c >= 0, ell > 0. All selected blocks are paid. Stop only at block boundaries. No within-block adaptation, early termination, revisits, offline calibration, or direct type queries in this model.
- Recover the whole θ vector, with error <= δ uniformly over every θ,z, and stop almost surely. Minimize expected total cost pointwise at each true state. The oracle only additionally knows z. Both have identical r,p,q, root access, block menu, and costs.

## Proof targets

1. Finite-c and finite-δ upper bound from balanced blocks versus the universal source-KL oracle lower bound, preserving the previous policy-class assumptions.
2. Finite-action block information LP and a matching achievable leading coefficient for θ recovery with nuisance z.
3. Oracle structure including strict dominance or exceptions for mixed-format blocks; optimal-depth ties must be retained.
4. If the oracle has one optimal depth L*, test the candidate Gamma_{k,L*}=[V_L*+(k-1)U_L*]/A_L* >= 1, where A is truth-flip KL at p, U is type-flip same-truth KL p-to-q, and V is type-plus-truth-flip KL p-to-q. Establish the precise iff claim or a counterexample.
5. Replace any uniqueness-dependent statement by a criterion over the entire oracle-optimal allocation set. Do not choose a convenient tied optimizer after the fact.
6. Determine what source cost can and cannot imply for the threshold. Any all-depth/unbounded-menu or large-cost result needs a separately stated argument; a finite depth cap may prevent threshold attainment.

## Checks and limits

Check q=1/2, r approaching 1/2 and 1, p approaching q, c=0, singleton/multiple groups, all sign/type alternatives, mixed blocks, and tied optimal depths. Do not assert monotonicity of the new threshold without proof. Treat known-level/noiseless-source reductions carefully; the original full unknown-level and finite-calibration theorem is not being claimed here.

Required outcome: a complete restricted-model result or a documented failure, a reproducible small deterministic check, a focused novelty comparison, and a clear recommendation about whether this belongs in the current paper.
