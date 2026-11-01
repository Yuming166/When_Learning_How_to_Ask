# D-RRC: primary shared-estimator decaying-exploration baseline

This is the primary estimator-controlled Decaying-Exploration Repeat-and-Compare (D-RRC) baseline requested for Phase 2c. It learns formats with the **same forced-only sign/orientation estimator as Aligned**, rather than introducing a separate repeated-answer-agreement estimator. No optional agreement variant is implemented.

The scientific comparison is the information-allocation action rule under the same estimation, exploration, tracking, information availability, and stopping framework. The baseline is not tuned to underperform Aligned, and no performance outcome is built into the rule.

## Interface and implementation boundary

```python
from phase2c.decaying import DecayingRepeatAndCompare

policy = DecayingRepeatAndCompare(public, calibration, planning_R)
action = policy.next(set(range(public['d'])))
policy.observe(action, result)
```

`DecayingRepeatAndCompare` subclasses the frozen Phase 2b `TheoryAlignedTracking`. It overrides **only `_update`**. Its constructor, forced-only estimator/grid, forced schedule, cumulative target tracking, `next`, `observe`, and diagnostics are inherited unchanged. Phase 2c bootstrap establishes the read-only historical import paths before the frozen class is imported. Neither earlier code nor earlier data are modified.

Public action/answer conventions remain unchanged: task actions are `('query', j, 'A'/'B')` with a raw 0/1 answer; type actions, when available, are `('type',g)` with an A/B report. Full-vector recovery requires every target to remain active. Calibration streams have equally long labelled high/low reference observations. `planning_R` carries log(1/delta) directly; `alpha_effective=M/planning_R` remains logged without exponentiation or underflow.

No hidden signs, current types, generating rates, private seeds, or evaluation feedback are accepted as policy inputs. The inherited constructor retains only dimensions/partition, public rate domain, known type accuracy, and calibration length. It does not retain reference bit values or unrelated public metadata.

## Fixed exploitation rule

At each scheduled update, the inherited estimator returns current estimated group formats z_hat. Set

\[
w_{j,m}(t)=\begin{cases}1/d,&m=\widehat z_{g(j)}(t),\\0,&m\ne\widehat z_{g(j)}(t),\end{cases}
\qquad w_g^{\rm type}(t)=0.
\]

Thus every coordinate has equal exploitation mass, its current estimated better format receives that mass, and all other formats/type actions receive zero target mass. There is no KL solve, plug-in information-ratio optimization, permanent commitment, outcome-selected override, or dependence on the true parameter.

These are cumulative **allocation targets**. The inherited tracker can select a currently zero-target stream to settle deficits from an earlier target, and designated forced exploration continues to query both formats. The rule does not forbid either task format.

## Shared estimator, exploration, tracking, and cadence

The forced-only estimator computes empirical response means from `forced` observations, estimates theta from the sign of the two-format mean sum minus one, orients means by that estimate, chooses each group's higher oriented mean, and averages good/other means to raw p/q. It projects onto the same deterministic increasingly fine ordered grid `.5<=q<p<=1-eta`, including the q=.5 and p=1-eta outer boundaries. Equality ties use the same frozen deterministic convention. Calibration values, direct type reports, and nonforced task answers do not assist this allocation estimator in either policy.

Let L=2d. At completed times `t=L*n*n+s`, `0<=s<L`, force task stream s. The frozen pathwise bounds are

\[
\lfloor\sqrt{t/L}\rfloor\le F_e(t)\le\lfloor\sqrt{t/L}\rfloor+1,
\qquad F(t)\le\sqrt{Lt}+L.
\]

For E=2d+G available slots and C(t) the cumulative targets, the same largest-deficit tracker gives, in exact arithmetic,

\[
-(E-1)(1+F(t))\le N_e(t)-C_e(t)\le1+F(t).
\]

Thus exploration proportion and tracking discrepancy divided by t vanish. These local schedule/tracking facts are inherited from Phase 2b; float64 cumulative sums are not interval-enclosed.

Updates begin after L completed actions, then occur at `u_next=u+ceil(sqrt(u+1))`. Frozen `_update` bundles this cadence with allocation planning, so the override repeats precisely that integer formula after substituting the simple target. Targets are held between updates. Update age is O(sqrt(t)), the last update divided by t tends to one, and updates continue throughout execution. The first L actions are forced, so the inherited initial uniform-two-format target does not introduce an initial permanent commitment.

## Information, actions, stopping, and cost fairness

Aligned and D-RRC receive the same public action availability, offline reference information, known type-report accuracies, and risk level. D-RRC's simple rule chooses **zero paid type calls**. Aligned may allocate mass to paid type actions or to other-format task actions. This choice is part of the allocation-rule comparison; a measured advantage cannot automatically be attributed solely to task-coordinate reweighting or solely to the mathematical optimizer.

All raw task answers remain in `counts`; all type reports, if present, remain in the inherited `types` storage; both labelled calibration streams go to the same external full-likelihood GLR/terminal decoder. The policy itself does not implement or adjust stopping. Each task/type action costs one online query. Offline observations number 2M, and total acquisition cost adds that separately.

Identical forced-observation fixtures produce identical estimates and update times for both policies. This is a controlled implementation statement. Under different actual action trajectories, a paired random-stream design need not make every forced observation or estimate identical; pairing/provenance must be recorded by the harness.

The complete allocation rule is predeclared and independent of development results. In particular, for one sharing group with alpha=0, the ideal good-format-only uniform target can coincide with Aligned's ideal optimal target. No perturbation is added to manufacture a win. Positive/zero-premium labels must follow the audited coefficient at the specific partition and alpha; `[4]` is not silently treated as zero-premium for every alpha.

## Telemetry and computation

Every update logs estimated theta/z, raw and grid p/q, grid mesh and indices, forced counts, alpha, target weights, update time, next update time, CPU seconds and wall seconds. `planner_seconds` and `planner_cpu_seconds` remain compatible inherited counters, but for D-RRC they measure estimator/simple-target update cost. Per-update timing fields are accurately named `update_seconds` and `update_cpu_seconds`.

No fabricated `estimated_K`, optimization lower/upper bound, solver residual, solver tolerance, or `solver_seconds` is emitted. A numerical information coefficient for this simple rule, if desired, belongs to the offline evaluator and must be labelled as such.

Each target update costs O(d+G) after the shared estimator. Regular tracking also costs O(d+G), with O(sqrt(t)) updates. This reduces optimization CPU by construction, but establishes no sample-efficiency or wall-time superiority. Query cost and measured computation must remain separate outcomes.

## Deterministic validation scope

The unit suite checks:

- only `_update` is overridden, with the inherited public constructor and all sampling/observation methods unchanged;
- identical forced fixtures yield identical estimates, alpha and update cadence;
- every coordinate receives 1/d on its current estimated better format, with zero other/type target mass;
- patching the actual frozen KL solver to raise still permits a complete deterministic 5,000-step path;
- every prefix of that path satisfies the forced-count and tracking discrepancy bounds, while updates continue;
- changed forced observations can reverse the preferred format without permanent commitment;
- calibration-value inspection is blocked by a poison sequence, and excluded metadata/type/nonforced observations cannot influence the estimate;
- telemetry contains factual update costs and no fabricated optimization quantities;
- a supplied good-only uniform Aligned target can coincide exactly with D-RRC, including the intended one-group/alpha-zero control.

The 5,000-step fixture is noiseless deterministic functional input, not a new statistical world, development episode, or effectiveness experiment. Unit tests do not certify delta-correctness, asymptotic optimality, or baseline superiority. No main experiment, private seed, model call, paid API, or confirmation sample is consumed by this implementation task.

Run from the Phase 2c directory:

```bash
python -m unittest discover -s tests -p test_decaying.py -v
```

With the real parent-owned bootstrap, **8/8 tests passed in 0.406 seconds**. An earlier explicitly stubbed import-path preflight also passed 8/8 in 0.361 seconds; it did not replace the real import integration check. No failing D-RRC checks were observed. The full 5,000-step test patched the frozen KL solver to raise on any call, and it was never invoked.

Source hashes after validation and before development execution:

```text
phase2c/decaying.py
29049fd2c08c130ee102be66193e0fbe7f52ab03d8a8f571727ae2513c64853a
tests/test_decaying.py
dfc6ed48f245e7fdcc92ddfadfcea0e7db3748f26722797dfa5f12e3fcd27225
read-only phase2b/aligned.py
67bdf86cbd21a81bde81fde981b9c00308f35d2f911af766fbd28939ae5b4ab0
```

These local deterministic receipts do not constitute execution approval for a statistical batch. The parent task separately reviews and freezes the common runner, pairing, cost limits, stopping rule, and development namespace before its one authorized bounded batch.
