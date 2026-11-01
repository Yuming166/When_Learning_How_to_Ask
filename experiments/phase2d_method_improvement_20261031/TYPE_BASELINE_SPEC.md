# Frozen Phase 2d task/type ablation specification

This specification freezes four allocation rules before the Phase 2d development batch. It changes no historical experiment, benchmark, model, estimator, or reference data. The new D-RRC-Type rule is a deliberately competitive, continually updated, non-joint-optimization baseline. It is not asserted to be the strongest possible type-enabled baseline.

## Four arms and implementation boundary

| Sampler | Task allocation family | Paid type allocation | Implementation |
|---|---|---|---|
| Aligned-Full | Frozen joint information allocation | Frozen joint allocation | Literal alias of Phase 2b `TheoryAlignedTracking` |
| Aligned-NoType | Same frozen information allocation with type actions unavailable | Exactly zero, `c_g=0` | Only constructor overridden; copied planning public input has `type_accuracy=None` |
| D-RRC-NoType | Uniform coordinates, current estimated good format | Exactly zero | Literal alias of Phase 2c `DecayingRepeatAndCompare` |
| D-RRC-Type | Uniform coordinates, current estimated good format | Public-structure guard, otherwise ongoing uncertainty/workload rule below | Only `_update` overridden |

All classes inherit the identical frozen `_estimate`, `_forced_index`, `next`, `observe`, and `diagnostics` methods. `Aligned-Full` and `D-RRC-NoType` are the actual historical classes, not rewritten versions. `Aligned-NoType` also inherits the exact frozen optimizer update, numerical checks, retries, telemetry, and failure behavior. Removing the type action columns does **not** tell the optimizer or external decoder the unknown group types.

The original environment public specification is not mutated. Aligned-NoType's local planning copy removes type action availability; the shared external stopping/decoding procedure must still receive the original public specification and profile all unknown group types, including in both no-type arms. An empty type-report history contributes no type evidence; it does not mean that the true group type is known.

```python
from phase2d.strategies import SAMPLERS, construct_sampler

policy = construct_sampler(name, public, calibration, planning_R)
action = policy.next(range(public["d"]))
policy.observe(action, result)
```

Registry keys are exactly `Aligned-Full`, `Aligned-NoType`, `D-RRC-NoType`, and `D-RRC-Type`. Unknown names raise an error.

## Shared estimation, exploration, and observation control

All four arms use the same forced-task-only estimator of theta, group type z, p, and q, including its deterministic ordered grid and tie rules. Calibration bit values, nonforced task responses, and direct type reports cannot modify those estimates. D-RRC-Type's auxiliary calculations described below can change the allocation between tasks and type reports; **they cannot override the preferred format used for task exploitation**. In particular, a confident type report opposing the forced estimate does not switch task exploitation to the report's format.

The common constructor retains only public dimensions/group membership, the rate-domain upper margin, known type accuracies when available, reference-stream length M, and `planning_R`. True labels, generating rates/types, private seeds, optimizer-oracle outputs, masks selected by an evaluator, and evaluator feedback are not inputs. The common external decoder retains both labelled reference streams; the policy only retains their length, with `alpha=M/planning_R`.

For L=2d, forced square blocks occur at completed times `t=L*n*n+s`, `0<=s<L`, and force task stream s. Both task formats continue to receive forced observations. Targets start uniformly over task streams, updates first occur after L actions, and later updates occur at `u_next=u+ceil(sqrt(u+1))`. Targets are held between updates. The identical largest-cumulative-deficit tracker selects nonforced actions; no arm makes an irreversible format commitment.

For all arms, raw task counts and raw type reports remain available to the same external likelihood calculation and terminal decoder. A strategy makes no stopping decision. Each task action and each type action costs one online query; the 2M offline reference observations are accounted for separately.

Identical forced-observation fixtures imply identical allocation estimates. A paired world/stream construction does not by itself imply identical forced observations after different action trajectories; the runner must record its pairing convention rather than claim estimator equality path by path.

## Predeclared D-RRC-Type rule

**Public-structure-aware guard, frozen before any development seed:** if `G==1` and `reference_count==0`, call the literal frozen D-RRC `_update`. Every coordinate receives `1/d` on the unchanged forced-estimated good format, and every type/other-format target is zero. This guard depends only on the public partition and reference-stream length. It does not inspect p/q, labels, observed outcomes, an evaluator score, or a joint optimizer. The forced estimator and its ongoing updates remain active.

The model-specific basis is [Theory_Note.md](../../Theory_Note.md), Theorem 2, Theorem 3 and its proof, and Corollary 3.1. Theorem 2 gives the unique uniform-good oracle allocation. Theorem 3's equality argument requires that allocation and zero first-order type-query counts. Corollary 3.1 establishes zero leading premium at alpha=0 exactly when G=1, for every admissible p>q and finite type-query KL. Thus this known public control does not need an imposed positive leading type budget. This strengthens the comparator before outcomes exist, and avoids manufacturing a leading-cost disadvantage on a structure where the ideal Aligned target is already uniform-good.

The guard does **not** claim type questions are useless at finite R, prove identical finite-sample performance to Aligned-Full, or apply to every model. The frozen floating Aligned solver can retain numerical residue; only D-RRC-Type versus the literal frozen D-RRC target/path has exact implementation equality under identical histories. The guard does not apply to one group with positive reference count or to multiple groups with no reference observations.

In every other public configuration, use the following unchanged full-threshold acquisition rule. At each scheduled update, obtain the unchanged forced-only estimate. Let `R=planning_R`, let G be the number of groups, and define

\[
B=R+\log(2d+2G),\qquad
\ell(r)=\log\frac{r}{1-r},\qquad
\kappa(r)=(2r-1)\ell(r).
\]

The projected p estimate is strictly greater than 1/2, so its kappa is positive. The q estimate may equal 1/2, in which case its log odds are exactly zero. These scalar expressions do not call the joint information optimizer, search over group masks, or optimize allocation coefficients.

For coordinate j, use all observed task responses to form the auxiliary signed task-evidence proxy

\[
S_j=\sum_{m\in\{A,B\}}
(N_{jm1}-N_{jm0})\ell(\widehat r_{jm}),
\quad
\widehat r_{jm}=
\begin{cases}
\widehat p,&m=\widehat z_{g(j)},\\
\widehat q,&m\ne\widehat z_{g(j)}.
\end{cases}
\]

Its remaining-task-work proxy is

\[
W_j=\frac{(B-|S_j|)_+}{\kappa(\widehat p)},
\qquad W=\sum_j W_j.
\]

For group g, the public known type accuracy is s_g, and its observed report counts are T_gA and T_gB. Define

\[
L_g=(T_{gB}-T_{gA})\ell(s_g),\qquad
V_g=\frac{(B-|L_g|)_+}{\kappa(s_g)},
\qquad V=\sum_g V_g.
\]

Outside the structural guard, when type actions are unavailable, every V_g is zero. With type actions available, B remains the **full** R-scale target for every group throughout execution. It is not shrunk when a coordinate's fixed-p/q task proxy becomes large: that proxy can become saturated before the common unknown-nuisance GLR can stop. Conflicting type reports can reduce the absolute report LLR, restore a deficit, and resume type acquisition at a later update.

If V>0, set

\[
w_g^{\mathrm{type}}=\frac{V_g}{W+V},\qquad
w_{j,\widehat z_{g(j)}}=\frac{W}{d(W+V)},\qquad
w_{j,1-\widehat z_{g(j)}}=0.
\]

If V=0, use the exact frozen D-RRC target: `1/d` for each coordinate's estimated good format and zero other/type mass. This fallback also covers W=V=0. If W=0 and V>0, every nonforced target is a type action until type deficits clear or later observations change the target. Forced task exploration always continues.

The rule therefore neither limits each group to one type call nor imposes an arbitrary tiny type fraction. It may allocate more than half the target mass to type actions. Group selection depends on observable report uncertainty and known report accuracy. Group sizes and all coordinates' unresolved task workloads determine the task/type balance through W; task coordinates themselves remain uniform. No optimized group selection, oracle label, fitted development parameter, or post-result threshold adjustment is introduced.

The LLRs, B, W, and V are **allocation proxies, not certified stopping statistics**. In particular, the task LLR substitutes estimated rates and types; it does not integrate or profile their uncertainty. The known-s report LLR concerns a group's label, not full-vector recovery. The common GLR and any separately audited stopping certificate remain the only stopping procedures used by the runner.

This conservative rule can overpurchase type reports, especially in large sharing groups, low-quality type channels, or settings where tasks already resolve group type well. It intentionally keeps a full R-scale acquisition option available rather than suppressing type acquisition because a task proxy appeared resolved. These disadvantages must remain visible in results; the rule is not retrospectively tuned to win or lose.

## Supported contrasts and claim limits

`Aligned-Full` versus `Aligned-NoType` measures allowing paid type actions within the same frozen joint allocation family. The no-type optimizer must reallocate its task effort after type actions are removed, so this includes the resulting task allocation response.

`D-RRC-Type` versus `D-RRC-NoType` measures adding this declared active type-acquisition schedule to uniform-coordinate, estimated-good-format D-RRC. The direction of task exploitation remains controlled by the common estimator; buying types changes the number and timing of task queries as well as adding reports to the common decoder.

`Aligned-NoType` versus `D-RRC-NoType` measures the two task allocation rules with no paid type actions. `Aligned-Full` versus `D-RRC-Type` measures the full joint allocation rule against this simple type-enabled comparator under the same public information and costs.

Thus this is a 2x2 table of strategy family and type treatment with **family-specific type schedules**. It does not isolate one universal scheduler-independent type main effect. A difference-in-differences interaction is descriptive of these four declared policies; it does not prove that the mathematical optimizer alone caused a gain, establish superiority over every type-enabled baseline, or identify a pure task-coordinate-reweighting effect. Finite development outcomes also do not establish asymptotic optimality or finite-risk correctness.

## Telemetry and deterministic validation

D-RRC-Type logs the shared estimate, forced counts, target weights, auxiliary threshold, signed task and type LLRs, per-coordinate/group task workloads, per-group type deficits/drifts/workloads, total workloads, type mass, update times, and measured update CPU/wall time. In the structural-guard branch it retains the exact frozen D-RRC telemetry and adds the explicit guard name and its leading-coefficient-only scope; no auxiliary acquisition calculation is performed there. It emits no fabricated coefficient, solver bound, solver residual, or optimization certificate. Its general direct report summation costs O(d+G+number of stored type reports) per scheduled update; the guard uses frozen D-RRC's O(d+G) update, and tracking retains the frozen O(d+G) work per action.

The local deterministic suite covers:

- literal frozen class identity, actual Aligned-Full behavior under identical histories, and exact inherited estimator/sampler methods for all four arms;
- actual no-type coefficient solves with unavailable type actions, c_g=0, and no mutation of environment public inputs;
- absence of type actions on 1,000-action fixtures for each no-type arm;
- identical forced-only estimates despite changed type/nonforced histories, poison reference values, and irrelevant private metadata;
- auxiliary type-report uncertainty, renewed conflict, known report accuracy, current R, and coordinate/group task-work changes;
- preservation of forced-estimated task orientation even when reports strongly oppose it;
- the W=0,V>0 all-type target and the V=0 exact-D fallback;
- an 800-action deterministic public-guard fixture matching frozen D-RRC's actions, observations, estimates, targets, cumulative tracking and cadence exactly, with the joint optimizer patched to raise;
- verification that both public guard conditions are necessary, and fixed one-group/zero-reference coefficient fixtures consistent with the theorem (not a substitute for its proof);
- a 1,600-action deterministic D-RRC-Type fixture with the actual joint solver patched to raise, multiple acquired reports per group, continued updates, exact cadence, count conservation, and inherited forced-count/tracking bounds;
- factual telemetry, an explicit arm registry, and failure on unknown names.

Run from this Phase 2d directory:

```bash
python -m unittest discover -s tests -p test_strategies.py -v
```

Implementation receipt after the preseed public-structure guard: **15/15 tests passed in 0.976 seconds**. The earlier unguarded contract suite passed 12/12 in 0.771 seconds; it consumed no development seed or world. These fixtures are deterministic contract tests, not benchmark worlds, development episodes, or independent confirmation. They establish neither efficiency nor a certified error probability. No experimental seed, model call, API call, GPU job, new benchmark, acceleration arm, robustness pilot, or confirmation data was used by this implementation task.
