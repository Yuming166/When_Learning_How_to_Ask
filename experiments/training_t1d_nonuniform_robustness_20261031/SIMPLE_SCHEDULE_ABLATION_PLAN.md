# Separately frozen small schedule ablation

## Material Passport

Approved T1d scope; no training, tuning or future-phase execution. Frozen before development entropy, same roster/budgets/costs as the main comparison.

One simple alternative only: WorstFact-MI. At each free round compute the current common joint posterior, choose fact j maximizing binary marginal entropy (1e-12 stable lowest-index ties), then choose the task OR type action with maximal I(theta_j;Y_a) (same score tie rule). Forced actions remain unchanged. This avoids handicapping uncertainty sampling by excluding type questions. No temperature, learned weights, threshold sweep or budget-specific tuning.

Two mechanism controls: IG-Uniform-FixedType and IG-Fact-FixedType. At the first G free rounds purchase groups0..G-1 once, then use task-only dense joint-theta IG with respective granularity. The API remains identical. These controls address type-purchase coupling, not a proposed deployable optimum.

Report all budgets, outcomes and negative cases. Primary comparisons with Lite and fixed-type granularity are fixed now; no replacing this alternative after results. No additional simple rule is selected or fitted using the roster.
