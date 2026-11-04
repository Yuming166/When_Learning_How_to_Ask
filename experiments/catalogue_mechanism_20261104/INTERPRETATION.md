# Post-run interpretation, with negative findings retained

The bounded frozen run completed all 144 planned trajectories. There were 142
certified outputs, zero observed wrong certified outputs, zero caps, and two
numerical KL allocation failures. All 142 successful histories replayed and
their terminal interval certificates were independently recomputed. Both failed
histories match their saved count totals and remain in the denominator.
There were 71 passing cross-R history-prefix pairs and one paired failure case.

The run used 50,262 main-run Bernoulli replies and 140.8 aggregate CPU seconds.
It used two pinned single-thread CPU workers, no external models, no APIs, no
GPU and no training. The separate engineering stages made 768 query requests;
their nested engineering prefixes are excluded from effectiveness statistics.

The complete compact eight-row comparison is in
[`results/PAPER_TABLE.md`](results/PAPER_TABLE.md). Full seed vectors, per-cell
statistics, matched contrasts and runtime summaries are in the frozen-generated
[`results/analysis.json`](results/analysis.json). The 19.7 MB raw artifact set
is retained locally, ignored by git, and covered by
[`results/RAW_MANIFEST.json`](results/RAW_MANIFEST.json).

The clearest controlled sharing diagnostic is the genuine three-item catalogue.
Under repaired IG, splitting the shared group increases mean certified query
cost by 119.0 at R=3 (paired tape-bootstrap 95% interval [92.33,143.33]) and
165.67 at R=9 ([143.50,187.50]). Round robin also has positive contrasts.
These are finite costs under two public partitions of the same catalogue,
true state, true coordinate-wise channel and paired response tapes. They are
not measurements of an unknown-type versus known-type oracle premium.

The weighted five-coordinate catalogue is an important counterweight. Its
same-size partitions have exactly different asymptotic premium classifications,
yet finite partition contrasts are not uniformly positive: IG's interval covers
zero at both R settings and round robin is faster under the positive-premium
partition. Thus these short finite experiments cannot be presented as proving
the exact coefficient classification or a policy-independent partition ranking.
The analytic geometry result and the finite empirical illustration must remain
separate statements.

The existing KL allocator also does not dominate the repaired IG policy. In the
weighted zero-premium cell it saves 42.33 queries at R=3 ([2.67,84.00]) and 67.50
at R=9 ([23.67,122.50]). It is worse than IG on the genuine three-item shared
cell and suffers numerical failures on its split cell. The preregistered pooled
failure-as-cap comparisons favor IG in point estimate; their intervals do not
establish a pooled difference. These results support reporting a theory-led
paper with a controlled mechanism illustration, not a broadly superior method.

Both KL failures occur at the same response seed, after 213 replies, for R=3
and R=9. The histories and counts are identical. A read-only recomputation from
saved counts gives the current fitted state theta-mask=0, type-mask=0, item=0,
p=53/66, q=19/27. The previous successful allocation update was at t=198.
The frozen source completed an allocation solve and then rejected its normalized
action weights at the final guard: nonfinite values, negative values, or a sum
outside tolerance trigger this error. The failed weight vector was not appended
to the raw log, so the specific violated component cannot be recovered from
the saved record. No allocation re-solve, numerical repair, retry, additional
answers or replacement was performed. The two paths receive cost 2,500 in the
restricted-cost metric; 2,500 is not their completed stopping time.
[`results/failure_context.json`](results/failure_context.json) preserves the
tracebacks, counts-derived fitted context and previous successful update.

All type bits were zero to isolate sharing from channel changes. A policy that
always selects format A would be a trivial strong alternative in these fixed
controlled states. The run therefore does not establish natural unknown-format
discovery, Web-user validity, or superiority against every simple baseline.
The only profiles are two all-positive theory anchors; six response tapes per
catalogue support uncertainty about conditional response noise, not new user or
catalogue generalization. Zero observed errors are not an empirical estimate of
the model's exp(-R) certification guarantee.
