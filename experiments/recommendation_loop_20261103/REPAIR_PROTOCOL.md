# Numerical baseline repair, separate from the frozen primary pilot

This is a post-hoc correctness repair, not an independent confirmation or a
replacement of the original 40 trajectories. All original source hashes and
records remain unchanged.

The primary policy wrapper treated scores within `1e-14` as ties. Retained
prefix inspection found information gains far below this absolute scale, with
meaningful unequal rankings. This could turn the IG baseline into least-count
cycling. A 36-prefix numerical audit found six action changes between absolute
and relative ties. Q6 and Q14 relative-tie choices agreed at these 36 retained
prefixes; this is a limited numerical diagnostic, not an integration-error bound.

Repair only the action tie comparison: use `64*machine_epsilon*abs(max_score)`;
exactly zero scores permit least-count ties. Keep quadrature order 6, model,
priors, forced schedule, certified gate, risk, cap, public worlds and paired
action-indexed streams unchanged. Do not change Decision KL or its results.

After the scale-invariance regression tests, hash-freeze the repair source and
run exactly eight repaired IG trajectories, one per original development world.
No seed/parameter search or retries. All failures/caps remain in the denominator.
These are additional controlled Bernoulli observations, not Qwen/API calls.
Report the original and repaired baseline side by side, and compare the repaired
baseline to the original frozen Decision KL results without claiming a new
independent test. Stop after this numerical repair.
