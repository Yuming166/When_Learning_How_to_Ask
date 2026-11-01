# Proof-to-code correspondence

## Material Passport

2026-10-31; Phase2b development. Read-only inputs: root Theory_Note.md, QRelBench v0.1, Phase2a. New code and independent review are kept here. Claims about ideal mathematical conditions and observations about float64 implementation are separate.

|Obligation|Phase2a gap|Phase2b implementation|Verification / remaining scope|
|---|---|---|---|
|Every task stream explored|Threshold forcing without a detailed proof receipt|aligned.py `_forced_index`: predetermined square blocks|Explicit prefix count and O(sqrt(t)) bounds, targeted tests|
|Proved estimator|Three coordinate iterations with calibration/type assistance|`_estimate`: forced means, sign sum, group oriented mean, averaged p/q|Excluded-input poisoning and hand calculation; Hoeffding argument in proof addendum|
|Deterministic vanishing grid|Continuous gap projection|`ordered_grid_projection`: nearest ordered finite grid, meshO(t^-1/2)|Exhaustive small-grid comparison and both endpoints tested|
|Actual allocation error tends0|Fixed requested tolerance|`_update`: requested epsilon=min(1e-4,1/(t+1)), actual gaps logged|Improves explicit contract; fixed backend/error floors still block infinite-horizon machine certification|
|No oracle rate/type leakage|Observable-only code already audited|Same boundary, estimator stores public dimensions/domain/type accuracy and M only|New source/RPC review; seed remains evaluator-only|
|Allocation tracking|Deterministic deficits, proof not supplied|Cumulative target tracking with forced overrides|Exact arithmetic discrepancy proof supplied; float accumulation not interval-enclosed|
|Delayed updates compatible|Every32 actions|u_next=u+ceil(sqrt(u+1))|LagO(sqrt(t)), explicit uniform schedule; original32 delay also asymptotically negligible given a proved estimator/oracle|
|Finite-calibration expected-time tail|Sketch did not justify offline fixed-tolerance event for all t|New combined transcript martingale argument|Full constants and pointwise boundaries in independent THEOREM1_REVIEW.md|
|Correct nominal risk at largeR|delta interface underflows atR1024|log_glr.py carriesR directly, rebuilds original beta|No clamping; profiles equal to old routine at representable risks|
|GLR arithmetic guarantee|Float64, non-interval|Same exact mathematical profile, float64 with o(R) guard|No rigorous rounding enclosure or empirical delta-correctness claim|
|Stop-check delay|Every16|max(16,ceil(sqrt(R)))|Gap/R tends0; same schedule for every policy|
|Independent evidence units|Only2 indices reused in primary confidence cells|64globally distinct worlds,4percell; policy-only pairing|Preseed index plan; uncertainty remains exploratory withn4|
|Censoring and cost fairness|Correct but tiny sample|All paths; same calibration/GLR/instances; task/type/offline explicit|Restricted means, conditional completion distribution and total acquisition separated|

The deterministic sampler is a proved tracking extension under the ideal oracle contract; it is not a literal transcription of the original randomized sampler. Both changes and limits remain visible next to theorem and experiment claims. New numerical convergence can support a finite-R diagnostic, never replace the ideal-policy proof or prove actual floating-point asymptotic exactness.
