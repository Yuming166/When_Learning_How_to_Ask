# Myntra closed-loop robustness panel v0.1

## Question and claim boundary

This panel checks whether the development signal for `decision_value` at five
field questions persists under independently generated user profiles and
independent Monte Carlo prior banks, while holding the six catalog menus and
the deterministic ReferenceUser fixed. It does not test language-model or
human behavior, new products, unknown answer reliability, or the original
group-shared query-format theory. As the policy signal was observed in an
earlier development panel, this remains development robustness evidence rather
than independent confirmation.

## Frozen design

- Two cohorts of 12 profiles each, four per each of the three existing product
  pools, generated with the documented deterministic generator and independent
  seed roots A and B. Profiles are not filtered by outcomes.
- Two independent prior banks, each 2,048 profiles per pool, crossed with both
  user cohorts to form four panels. Menus and product records are exactly those
  in the frozen v0.1 development experiment (six menus, 24 menu/profile cases
  per panel). No new catalogue items are introduced.
- Four policies: `fixed_order`, `profile_ig`, `decision_set_ig`, and
  `decision_value`. Each is evaluated at budgets 0 through 6. The full-profile
  disclosure reference is also recorded as one turn and six information units.
- Primary endpoint: exact valid-recommendation rate at budget 5 for
  `decision_value` paired against `fixed_order` and `profile_ig`. `decision_set_ig`
  is secondary. Report all 24 cases per panel, unique-profile clusters, BUY / 
  NO_BUY denominators, and all error paths. Descriptive only; no p-values,
  confidence intervals, or population claims.
- Robustness gate, evaluated separately against each primary baseline:
  positive case-mean difference in at least 3 of 4 crossed panels, positive
  pooled mean after averaging menus and both prior banks within each of the 24
  unique profile clusters, and positive difference for at least 4 unique
  profile clusters. If any condition fails, report
  `ROBUST_ADVANTAGE_NOT_ESTABLISHED`.

## Information boundaries and controls

The recommendation policies receive only the public menu, prior draws, and
answers returned by the deterministic user. Evaluation profiles and labels are
used only by the runner to generate answers and score outcomes. All methods use
identical menus, profiles, prior bank within a panel, costs, action set, and
tie-breaking. Existing source files, frozen data, previous results, and logs
remain untouched. No model/API/GPU calls, training, parameter search, or
outcome-based stopping are allowed.

## Execution

Run unit tests and a two-case end-to-end smoke test using prior bank A. Freeze
the code, protocol, config, original experiment result and freeze, source
environment, and catalogue hashes before starting the full panel. Then execute
the complete 4 × 24 case panel once. Retain the complete paired traces and
verification receipt. A run failure is reported with its full denominator; do
not silently retry selected cases or reduce the planned design.
