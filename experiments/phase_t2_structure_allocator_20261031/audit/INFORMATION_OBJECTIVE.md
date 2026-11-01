# T2 observable information objective

The implementation is `t2/information.py`. Its only state input is the exact
`t2_observable_v1` allow-list. It does not access a world, private seed, generating
rate, true fact, true group type, evaluator, model, or held-out label.

For each observable plug-in pair `p,q`, estimated group mode `z`, and legal
allocation `x`, it enumerates every nonempty fact-flip subset and every group-type
flip mask. The bounded domain is `1 <= d <= 4`, `1 <= G <= 2`. Alternative rates
range continuously over `0.5 <= v <= u <= 1-eta`; there is no rate grid.

For an alternative `(S,m,u,v)`, the information is

`I(x) = alpha * [D(p||u) + D(q||v)] + sum_a x[a] * C[a]`,

where `alpha = calibration.high.total / R`; the high and low totals must agree.
Task coefficients compare the observable estimated reference mean to the
alternative mean, complemented exactly when that fact is flipped. Type
coefficients are `D(s_g || 1-s_g)` exactly when group `g` is swapped. Physical
action order is `(fact 0, mode 0), (fact 0, mode 1), ...`, followed by group type
actions. All observations influence the supplied estimate upstream; already paid
online observations are not added as a second information offset here.

Complementing a flipped reference mean converts its KL term into an ordinary
weighted Bernoulli fit. The two independent weighted binomial fits are clipped
to the public rate interval and pooled if their order is violated. This solves
the inner continuous problem analytically, including zero-weight channels.

`radial_cost(state,w)` returns the first nonnegative `t` for which the minimum
over all alternatives of `I(t*w)` reaches one. Alpha remains fixed throughout the
monotone scalar root. Thus `1/min_information(state,w)` is generally incorrect
when alpha is positive; it agrees in the homogeneous alpha-zero case. Directions
with an alternative whose information can never reach one return infinity.
The support check does not replace small positive action weights by zero.

`build_cuts(state,teacher_weights,teacher_K)` exports JSON-compatible
`cut_coefficients` and `cut_offsets`. It uses four base rate pairs plus the exact
continuous minimizing rates at teacher and legal-uniform radial allocations.
It stores at most `6*(2**d-1)*2**G` constraints, hence at most 360 in scope. The
offset of each constraint is alpha times its calibration KL, not a scaled online
coefficient. Exact duplicate constraint locations are omitted.

For the fixed finite constraints, the radial lower bound is

`K_cut(w) = max_i max(0,1-b_i)/(C_i @ w)`.

Zero requirement with zero denominator is zero; positive requirement with zero
denominator is infinity. Every retained constraint is an actual alternative, so
`K_cut(w) <= K_exact(w)`. Consequently its positive-part relative regret against
the same teacher coefficient is a lower bound on positive-part exact relative
regret. A denominator floor in training makes this bound more optimistic. The
finite-cut training loss is explicitly an approximation and can miss harmful
directions. Held-out checks must use `radial_cost`, not report the surrogate as
an exact objective or guaranteed regret certificate.

`WarmSolver.solve` uses the frozen symmetric within-group allocation formulation
and frozen analytic separation functions. It reuses only adversarial `(u,v)`
locations from its previous compatible group-size structure. Every KL row,
calibration right-hand side, LP, separation check, and radial repair is recomputed
at the exact fresh `p,q,alpha,s,eta`. There is no rounded rate key or cached answer.
The location cache is bounded, and locations outside a changed rate domain are
discarded. General asymmetric allocations are evaluated by `radial_cost`.

The warm solver retains the frozen LP primal/dual tolerance `1e-9` and repaired
information target `1+1e-9`, and checks the frozen planner acceptance limits:
minimum information at least `1-1e-7`, relative gap in
`[-5e-8, max(5*tolerance,5e-8)]`. Returned bounds are floating numerical bounds,
not interval-arithmetic certificates. The caller may request a tighter rerun.

Validation uses default Python with single-thread BLAS/OpenMP and standard
`unittest` because pytest is absent. The mathematical fixtures test independent
continuous minimization, all-subset teacher consistency, relabeling invariance,
fixed-alpha nonhomogeneity, infinity preservation, envelope and surrogate finite
differences, finite-cut lower bounds, exact fresh-rate warm/cold consistency, and
observable/bounded-input rejection. They generate no scientific worlds or model
outputs and make no effectiveness or speedup claim.
