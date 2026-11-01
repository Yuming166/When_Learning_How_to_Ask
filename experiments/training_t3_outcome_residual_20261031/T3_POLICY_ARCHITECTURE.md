# T3 policy architecture

## Material Passport

Frozen pre-execution design; actual fit and selected-weight receipts are TRAINING.json and DEV_SELECTION.json. Implementation is t3/core.py. No language model is trained or invoked.

Each free decision first obtains the frozen AnalyticReuse cumulative-deficit proposal on the current legal ledger. A fresh order32 joint belief supplies five proposals: original WorstFact-MI; original Fresh-IG-Lite; the current KL proposal; best joint-information type report; and a WorstFact task-only fallback. Duplicate physical actions are deduplicated. Forced rounds remain exactly the frozen clock and cannot be overridden. The extra fallback lets a type-only gate skip a type proposal without freely choosing a different fact. This extends the old T1b four-macro interface rather than silently treating its TYPE/TASK semantics as unchanged.

The scorer is a shared 40-32-16-1 tanh MLP. Each row describes one physical action with global belief/budget moments, group-local pooled fact uncertainty and counts, local fact/format uncertainty and counts, posterior joint/marginal information, one-step complete-recovery gain, predictive answer entropy and proposal-membership flags. No physical/group index, raw fictional text, environment/world ID, true labels or future response is encoded. Variable d and group sizes affect only row construction and symmetric pooling; fixed network weights handle variable row counts. No training target is a KL allocation vector.

A(s,a)=f_phi(x(s,a))-f_phi(x(s,a_base)); the base residual is exactly0. Select the largest allowed residual only if it exceeds the fixed .02 threshold; otherwise execute WorstFact-MI. All queries, including overrides, update the SAME paid observation ledger and virtual KL tracker. At deployment the trained scorer does not execute counterfactual rollouts. It still pays posterior and candidate-generation cost, including the KL optimizer; this pilot is an effectiveness test and does not assume a computation speedup.

Task-only: if WorstFact selects type, preserve it; otherwise allow candidate task actions only. Type-only: allow type candidates and the fixed WorstFact task proposal, preserving task identity. Joint: allow all proposals. Same training worlds/labels are used; each mask has its own3 independent parameter fits. The masks can alter later beliefs and hence later purchase timing, so they do not isolate an identical realized type schedule. Frozen fixed-type baselines provide a separate control.

The shared scorer is equivariant to physical-action row permutations and its pooled legal features respect fact/group relabeling away from proposal ties. The COMPLETE policy inherits index-based deterministic ties and the forced enumeration from frozen baselines; strict pathwise permutation equivariance at exact ties is NOT claimed. Symmetric deterministic unique-choice equivariance is generally impossible. Tests check scorer row equivariance and zero-residual physical equality, not an unsupported theorem about the entire candidate/tracking process.

The approximate posterior preserves joint theta/z/rate dependence; a noisy report is not treated as a revealed z. Shape-valid feature access does not itself prove semantic sufficiency or transfer. Model size, forward overhead, override fraction and failure modes are reported after the fixed pilot.
