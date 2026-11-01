# Phase2b — Proof-to-Code Alignment and Cost Convergence Audit

## Material Passport

Date2026-10-31. This is a CPU-only development protocol, frozen before the new private seed or main-run trajectories exist. Scope follows the user's Phase2b attachment: expected-time proof, code correspondence, and a small fixed-confidence cost diagnostic. No model/API/GPU calls, training, fixed-budget benchmark expansion, Phase3 confirmation, or post-outcome strategy tuning is authorized. All previous artifacts and Theory_Note.md remain unchanged.

## P0 gate and mathematical scope

Keep PROOF_ADDENDUM.md, ALIGNMENT_MATRIX.md, and independent audit/THEOREM1_REVIEW.md. Resolve the finite-calibration uniform-tail argument using a single centered offline+online transcript martingale at deviation proportional to t, then a compact alternative net and a delta-uniform tail sum. Explain local allocation continuity, nonunique convex normalized optimizer set, positive online information, and uniformity of estimator/oracle/update moduli. Mark the resulting ideal-policy theorem separately from the actual float64 program.

The new sampler uses forced-only means exactly in the estimator construction: sign of two-format means minus one, group type by larger oriented mean, coordinate-average p/q, and nearest ordered grid with mesh(.5-eta)/ceil(sqrt(t+1)). Calibration values and direct-type answers do not assist this allocation estimator; all such answers still enter the common GLR. Calibration length sets alpha=M/R. Rates/signs/types/seed/correctness and evaluation feedback never enter the selector.

Force task stream s at completed t=(2d)n^2+s,0<=s<2d. On every round add the current target to cumulative weights; on nonforced rounds select the largest cumulative deficit. Explicit O(sqrt(t)) discrepancy supplies an extension to the original randomized sampler, not a literal transcription. Update at u_next=u+ceil(sqrt(u+1)). Request epsilon_u=min(1e-4,1/(u+1)), log actual solver bounds/gaps, and fail closed if the bounded numerical contract is unattained. One tighter INNER solve is allowed and logged; it does not restart any trajectory or main experiment.

The backend has fixed floating tolerances and finite iteration limits. A fixed accepted gap floor5e-8 and information residual1e-7 remain visible alongside actual attained values. No inference that requested epsilon alone gives certified vanishing actual error. The real-arithmetic reference proof does not certify this executable program's exact leading coefficient or machine error probability.

## P1/P2 preselected design

All true generating parameters are evaluator-only. d=4,p=.85,q=.60,eta=.05,s=.8. Partitions[1,3] and[4], alpha0/3, R=16,64,256,1024, four globally independent worlds per cell. These endpoints were chosen before new seeds to bound runtime and contrast smallest versus full sharing; omitted[2,2] receives no conclusion. There are16cells and64independent worlds. Each cell/R/replicate has a different episode index; pairing is across policies only. No previous world, outcome, profile, or seed is reused for scientific observations.

Five policies: frozen Round-Robin, Repeat-and-Compare, Direct Type Query, Format-Only Oracle, and new Aligned Tracking. Oracle knows z only, not p/q/theta. Known-s type calls cost one online action, just like task calls. All methods get the SAME2M offline reference observations in a paired world, with M=ceil(alpha R) PER STREAM. Total acquisition adds2M separately; the online coefficient K does not include that sunk resource.

Carry R directly. Never compute exp(-R) to represent the GLR risk atR1024, clamp it to a representable delta, or substitute a different nominal risk. The read-only exact mathematical profile solver is reused; beta is rebuilt as R+2log(M+1)+sum_task log(N+1)+sum_type log(N+1). All methods check every max(16,ceil(sqrt(R))) actions, plus the cap. The check gap/R vanishes. Stop only if gap-beta>1e-8*(1+log1p(online+2M)); this guard is o(R), but is not rigorous interval arithmetic. Profile likelihood uses all observed samples, no grid approximation. d=4 only; no sequential d16 GLR.

Each trajectory cap is max(2048,24R):2048,2048,6144,24576. Keep every censored/failed trajectory and action cost. The Direct sampler can permanently choose a weak form; this cap need not permit completion. Its restricted cost must never be called E[T].

Plan:320trajectories, at most2,785,280 online actions and326,400 offline observations charged across all policy comparisons. Hard caps:2,800,000online actions,1200wall seconds, numerical backends one thread. Five spawned/confined workers are kept idle except for the one current trajectory; policies are interleaved within every world with a cyclic rotation, so a timeout is not caused to omit an entire last-listed arm. World/R ordering is predetermined and interleaved by replicate. No automatic retries, overwrite, cap extensions or second tuning batch. Technical fixtures and selected exact replays are identified separately and excluded from the main study denominators.

## Analysis frozen before outcomes

Primary statistic is the all-world restricted mean online/R with cell-wise n4 exploratory bootstrap intervals(4000resamples,fixed analysis seed). Report the exact completed/censored/error denominators. When no world in a cell is censored, this equals the observed mean stopping cost/R, but four samples cannot prove convergence in expectation. When any censoring occurs, E[T]/R is unidentified above this restricted lower bound; do not impute unobserved tails or use completed-only means. Completion/wrong-certification curves versus query budget, conditional completed-cost distributions, and E[min(T,B)] remain separate.

The full predefined R curve is reported for every cell/policy. Compare to theoretical K_task_only, K_tasks+known-type, and K_format-only-oracle as appropriate, computed post-run by evaluator-side analysis. No hidden coefficient/parameter is sent back to choose a query. Draw total-acquisition/R separately, shifting online by2alpha. Bootstrap paired differences within a world are exploratory, without multiplicity adjustment; no general superiority, delta-correctness from zero errors, or empirical proof of an asymptotic limit.

Diagnosis retains actual forced fractions, estimator sign/type/rate error, grid mesh, update count/lag, requested/attained solver error and fixed floors, threshold/R, and min population KL/R at realized unsymmetrized counts. Population KL uses true group types only after execution; never feeds the selector. Planning and GLR wall/CPU timings are separate from query acquisition cost. No fixed-budget accuracy comparison is pooled into this fixed-confidence analysis.

If any required source audit, smoke fixture, seed commitment or runtime contract fails, retain exact error/partial logs and do not produce a complete-comparison report. A crashed main batch is not silently rerun. A completed run must have all320 planned identities and complete cost reconciliation before analysis.

## Reproducibility and stop

Draw a FRESH256-bit evaluator seed with secrets.token_hex(32), after all gates. Keep it in a mode700directory, mode600file; record generation procedure and only its file-hash commitment publicly. Spawn without seed arguments, apply Landlock before public input, and protect evaluator memory. Learners receive only public R/cap/check/milestones, public problem metadata, actually acquired answers/calibration/type reports, and ACK-only snapshot replies. They receive no audit/truth fields.

Hash-bind new code/tests/config/protocol/proof/audits and read-only v0.1/Phase2a source. Preserve all earlier receipt files before/after. Validate public count/cost/GLR coverage, selected exact existing-trajectory replays, and claims. Separate same-family reviewers are not external or cross-model certification. After the single bounded diagnostic and full report including failures or negative trends, STOP. No independent confirmation seed is drawn or used.
