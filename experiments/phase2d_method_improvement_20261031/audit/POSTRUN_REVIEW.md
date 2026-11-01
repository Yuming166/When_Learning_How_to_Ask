# Independent post-run review

Status: **FINAL POST-RUN VERDICT: PASS for the declared bounded development, arithmetic audit and existing-world replay scope**. Main acquisition, frozen-source checks, independent raw public analysis reconstruction and final certificate/replay receipts passed. This is not independent confirmation of effectiveness. This reviewer generated no scientific worlds, drew no seeds, ran no replay, and read no private seed or truth files.

## Provenance and unchanged history

The 18 source/config/protocol hashes and 7 pre-seed audit hashes all match `freeze.json`. The complete pre-seed commitment matches both its hash and every shared freeze field. The original theory hash also matches. All 37 public historical Python dependencies were independently rehashed and matched. The before/after historical validation receipts agree exactly on 353 protected files; this reviewer relies on the evaluator receipt for protected private artifacts rather than reading them.

The three Phase2c confirmation-related artifacts remain byte-identical to the historical receipt: `CONFIRMATORY_PROTOCOL.md`, `PHASE2C_PROTOCOL.md`, and `artifacts/analysis/confirmation_plan.json`. The new bounded gate has not silently replaced the old protocol.

## Main batch and full denominators

The completed batch contains exactly 64 independent public world identities and 256 planned policy/world identities: 16 cells × 4 worlds × 4 policies. There are no missing, duplicate, failed or censored trajectories. Public task count arrays, type report lengths, paired calibration records and all charged costs were independently reconciled. Each cell-policy denominator is 4 and every contrast has 4 paired worlds. The failure log is empty.

|Policy|Task actions|Type actions|Completed|Censored|Evaluator-reported wrong terminal outputs|
|---|---:|---:|---:|---:|---:|
|Aligned-Full|127,300|14,348|64/64|0|0/64|
|Aligned-NoType|155,712|0|64/64|0|0/64|
|D-RRC-Type|122,755|33,261|64/64|0|0/64|
|D-RRC-NoType|235,440|0|64/64|0|0/64|

Total online actions are **688,816 = 641,207 task + 47,609 type**. Policy-accounted offline cost is **261,120**; unique shared reference observations are **65,280**. Total policy-accounted acquisition is **949,936**. The run used 1,103.295 seconds, below the 1,800-second deadline; its online total is below both the planned maximum 2,228,224 and hard allowance 2,250,000. Retries, model calls and confirmation worlds are all zero in the execution receipt.

The main run used the frozen legacy floating stopping rule. Every main row has `strict_certificate=None` and no strictly certified output. Evaluator integrity separately recomputed all 256 terminal floating GLRs. Scores quoted here are the public evaluator scores, not independently recomputed private labels.

## Independent exact reconstruction of every cell

The reviewer reconstructed all normalized costs from integer raw public counts using exact Fractions. All 64 policy means, 80 paired vectors, their 320 scalar differences and all contrast means match the persisted analysis exactly. The table contains mean online cost divided by R; all trajectories completed, so these also equal the observed restricted means.

|Partition|alpha|R|Aligned-Full|Aligned-NoType|D-RRC-Type|D-RRC-NoType|
|---|---:|---:|---:|---:|---:|---:|
|[1, 3]|0|16|38.5|32.0|46.5|43.25|
|[1, 3]|0|64|12.75|13.4375|11.625|22.5|
|[1, 3]|0|256|7.640625|8.84375|8.609375|15.8125|
|[1, 3]|0|1024|7.171875|8.1015625|7.8203125|15.4453125|
|[1, 3]|3|16|30.75|30.0|38.5|42.5|
|[1, 3]|3|64|13.5625|15.1875|14.75|26.0|
|[1, 3]|3|256|7.453125|9.25|8.140625|16.484375|
|[1, 3]|3|1024|6.203125|7.6484375|6.8984375|14.625|
|[4]|0|16|16.25|16.25|16.25|16.25|
|[4]|0|64|8.875|8.875|8.875|8.875|
|[4]|0|256|6.140625|6.140625|6.140625|6.140625|
|[4]|0|1024|5.1484375|5.1484375|5.1484375|5.1484375|
|[4]|3|16|19.25|18.75|20.25|18.25|
|[4]|3|64|8.4375|8.0625|9.1875|7.9375|
|[4]|3|256|6.078125|6.125|6.984375|6.203125|
|[4]|3|1024|4.8671875|5.1640625|6.078125|5.140625|

Contrast order below is C1 = D-NoType − Aligned-NoType; C2 = D-Type − Aligned-Full; C3 = Aligned-NoType − Aligned-Full; C4 = D-NoType − D-Type; I = C3 − C4. Positive C1–C4 favors the named policy change. Vectors are ordered by ascending public world index, with four entries per cell. These were reconstructed from raw rows before comparison to `paired.json`.

|Partition|alpha|R|World indices|C1 vector|C2 vector|C3 vector|C4 vector|I vector|
|---|---:|---:|---|---|---|---|---|---|
|[1, 3]|0|16|[410000, 410001, 410002, 410003]|[10.0, 14.0, 11.0, 10.0]|[-23.0, 7.0, 9.0, 39.0]|[-35.0, 1.0, 3.0, 5.0]|[-2.0, 8.0, 5.0, -24.0]|[-33.0, -7.0, -2.0, 29.0]|
|[1, 3]|0|64|[410100, 410101, 410102, 410103]|[10.5, 6.75, 10.75, 8.25]|[1.25, -2.25, -2.25, -1.25]|[2.75, 1.75, -3.5, 1.75]|[12.0, 10.75, 9.5, 11.25]|[-9.25, -9.0, -13.0, -9.5]|
|[1, 3]|0|256|[410200, 410201, 410202, 410203]|[7.5625, 8.75, 5.0, 6.5625]|[0.4375, 0.875, 1.3125, 1.25]|[0.8125, 0.9375, 1.5, 1.5625]|[7.9375, 8.8125, 5.1875, 6.875]|[-7.125, -7.875, -3.6875, -5.3125]|
|[1, 3]|0|1024|[410300, 410301, 410302, 410303]|[7.625, 7.5, 7.25, 7.0]|[1.125, 0.625, 1.3125, -0.46875]|[1.125, 1.40625, 1.5625, -0.375]|[7.625, 8.28125, 7.5, 7.09375]|[-6.5, -6.875, -5.9375, -7.46875]|
|[1, 3]|3|16|[410400, 410401, 410402, 410403]|[5.0, 17.0, 10.0, 18.0]|[-3.0, 25.0, 1.0, 8.0]|[-3.0, -3.0, 0.0, 3.0]|[5.0, -11.0, 9.0, 13.0]|[-8.0, 8.0, -9.0, -10.0]|
|[1, 3]|3|64|[410500, 410501, 410502, 410503]|[3.0, 16.75, 7.75, 15.75]|[-2.75, 5.25, 1.25, 1.0]|[0.5, -0.5, 6.25, 0.25]|[6.25, 11.0, 12.75, 15.0]|[-5.75, -11.5, -6.5, -14.75]|
|[1, 3]|3|256|[410600, 410601, 410602, 410603]|[5.3125, 6.5, 7.4375, 9.6875]|[1.125, -0.0625, 0.5625, 1.125]|[3.25, 1.5, 0.625, 1.8125]|[7.4375, 8.0625, 7.5, 10.375]|[-4.1875, -6.5625, -6.875, -8.5625]|
|[1, 3]|3|1024|[410700, 410701, 410702, 410703]|[7.09375, 6.625, 7.78125, 6.40625]|[1.15625, -0.09375, 0.75, 0.96875]|[1.90625, 0.5625, 1.0625, 2.25]|[7.84375, 7.28125, 8.09375, 7.6875]|[-5.9375, -6.71875, -7.03125, -5.4375]|
|[4]|0|16|[410800, 410801, 410802, 410803]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|
|[4]|0|64|[410900, 410901, 410902, 410903]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|
|[4]|0|256|[411000, 411001, 411002, 411003]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|
|[4]|0|1024|[411100, 411101, 411102, 411103]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0, 0.0, 0.0]|
|[4]|3|16|[411200, 411201, 411202, 411203]|[0.0, -1.0, 0.0, -1.0]|[0.0, 1.0, 2.0, 1.0]|[-1.0, 0.0, 0.0, -1.0]|[-1.0, -2.0, -2.0, -3.0]|[0.0, 2.0, 2.0, 2.0]|
|[4]|3|64|[411300, 411301, 411302, 411303]|[-0.25, 0.0, 0.0, -0.25]|[1.5, 1.75, -1.25, 1.0]|[0.0, 0.0, -1.25, -0.25]|[-1.75, -1.75, 0.0, -1.5]|[1.75, 1.75, -1.25, 1.25]|
|[4]|3|256|[411400, 411401, 411402, 411403]|[-0.125, 0.4375, 0.0, 0.0]|[0.5, 0.6875, 1.3125, 1.125]|[-0.3125, -0.0625, 0.5625, 0.0]|[-0.9375, -0.3125, -0.75, -1.125]|[0.625, 0.25, 1.3125, 1.125]|
|[4]|3|1024|[411500, 411501, 411502, 411503]|[-0.09375, 0.0, 0.03125, -0.03125]|[1.125, 1.03125, 1.5625, 1.125]|[0.28125, 0.40625, 0.28125, 0.21875]|[-0.9375, -0.625, -1.25, -0.9375]|[1.21875, 1.03125, 1.53125, 1.15625]|

The frozen bootstrap implementation was reviewed before the seed draw. It uses the same within-cell world resample indices for all arms and contrasts, 4,000 resamples and fixed analysis seed 763401. The reviewer did not draw another analysis seed or rerun the bootstrap. These percentile intervals are exploratory, unadjusted for multiple comparisons, and based on four independent worlds per cell.

## Evidence-bounded interpretation

In [1,3], the no-type task-allocation contrast is positive in all eight cells. At R=1024, its normalized mean differences are 7.34375 (alpha=0) and 6.9765625 (alpha=3). Relative reductions calculated from the respective cell mean costs are approximately 47.5% and 47.7%. These ratios of cell means are not mean within-world percentage reductions.

After adding the declared type-aware comparator, the remaining R=1024 mean differences are only 0.6484375 and 0.6953125, approximately 8.29% and 10.08% of the D-Type mean costs. The prespecified paired intervals are respectively [-0.0703125, 1.21875] and [0.171875, 1.0625]. The first crosses zero; the second is an exploratory four-world interval. Low-R outcomes are mixed, including a negative remaining-advantage mean in [1,3], alpha=0, R=64. Universal finite-R superiority is unsupported.

For [4], alpha=0, guarded D-Type and D-NoType action/observation/transcript hashes agree exactly. Their tie is imposed by the public-structure rule, not evidence that type questions never help at finite R. All four arms happened to have matching costs in these observed cells, which is a separate empirical statement. For [4], alpha=3, D-Type incurs a negative type-benefit contrast at every R: -2, -1.25, -0.78125 and -0.9375. Its full R-scale schedule can overbuy reports; comparisons against it do not establish the strongest possible baseline or pure task/type causal shares.

No observed error in 256 trajectories verifies exp(-R) error probabilities. Neither the ablation nor exact terminal arithmetic proves solver correctness, asymptotic expected-cost optimality, a.s. stopping for arbitrary samplers, or a guarantee conditional on each realized calibration sample.

## Certificate and replay review

All **765/765 declared completed terminal states** have valid stored crossing
certificates: 509 historical non-Oracle states and all 256 new states. All
used 50 decimal digits; rejected and undetermined counts are both zero for
these observed completed endpoints. Identity coverage was compared exactly
against both public raw trajectory files, rather than merely trusting the
aggregate receipt. Historical coverage is explicitly 509 completed out of
512 non-Oracle paths; the 3 old censored paths and 128 Oracle paths are outside
this prespecified terminal-certification set and remain in historical data.

For every certificate, the reviewer checked the returned candidate against
the corresponding original sign estimate, all task/type/reference counts,
total observations, exact stored R/eta/s interpretation, exact upper endpoint,
complete sign/type search sizes, feasible rational lower witness, and the
strict endpoint inequality using exact Fraction conversions of endpoint
strings. The smallest observed `gap_lower - beta_upper` is approximately
0.004302043958961873, still strictly positive. Every lower gap is also at most
the exact difference between the stored candidate lower and wrong-sign upper
endpoints, consistent with outward subtraction. The general validity of the
logarithm enclosures is supplied by the separately reviewed frozen arithmetic
implementation and rational-remainder regression; this post-run check did
not rerun 765 calls or replace that argument with precision agreement.

The static historical counterexample still has floating acceptance and new
gate status `rejected`, as required. Ordinary completed endpoints all passing
does not establish that the legacy numerical rule is universally safe.

The exact predeclared eight replay identities are present, without substitution:

|Mode|Policy|Existing index|R|Original online|Replay online|Extra actions|Gate calls|Trace hash unchanged|
|---|---|---:|---:|---:|---:|---:|---:|---|
|floating|Aligned-Full|410100|64|688|688|0|0|yes|
|floating|Aligned-NoType|410100|64|864|864|0|0|yes|
|floating|D-RRC-Type|410100|64|768|768|0|0|yes|
|floating|D-RRC-NoType|410100|64|1536|1536|0|0|yes|
|certified|Aligned-Full|410300|1024|6688|6688|0|1|yes|
|certified|Aligned-NoType|410300|1024|7840|7840|0|1|yes|
|certified|D-RRC-Type|410300|1024|7840|7840|0|1|yes|
|certified|D-RRC-NoType|410300|1024|15648|15648|0|1|yes|

The four floating replay records exactly match the original records after
removing timing fields. For all strict replays, the certified candidate,
submitted scoring candidate and reported output agree, the final gate time
equals the action count, and the complete current count arrays, type reports
and calibration match their original endpoints. Every strict replay passed
the exact endpoint inequality; none abstained or required extra actions.
This zero-delay observation concerns four preselected trajectories only.
The tested refusal/continued-sampling/cap-abstention logic remains necessary
even though it was not triggered by these four observed paths.

Replay action costs independently sum to **41,872 = 37,960 task + 3,912
type**, with zero offline observations charged on the selected alpha=0
worlds. This is below the separate 200,000-action ceiling. Replay wall time
is 71.626 seconds, below 300 seconds; the complete static-plus-replay audit
used 85.059 seconds. Static gate calls used approximately 11.874 seconds.
The replay receipt is completed with no error, and there are zero failure
rows. No failed replay or extra delay was hidden from the aggregate counts.
Main and replay operations remain separately accounted; reusing existing
worlds does not create new independent effectiveness samples.

Main sampling results remain legacy floating regardless of these endpoint
checks. Only the four strict replays actually executed the new gate online.
The narrow mathematical guarantee is that its accepted event implies the
original full-model boundary crossing under the stated arithmetic/model
contracts, and hence inherits the wrong-certified-output bound under those
contracts and fixed pre-offline risk. It is not a guarantee conditional on
every realized calibration, a claim of universal termination, or an
expected-cost/solver-optimality result.

## Method version disposition

The evidence supports preserving the frozen Aligned-Full sampler and treating the independently audited d<=4 certified gate as a separately versioned bounded implementation candidate. It does not justify rewriting the historical method, relabeling main-batch costs as certified-policy costs, or reusing Phase2c confirmation as confirmation of the changed executable rule. Any new confirmation needs its own explicit version/protocol and independent data, and none is executed by this review.

## Public artifacts checked

|Artifact|SHA-256|
|---|---|
|freeze.json|`d72940d83384c572132e4802cf054510add53a312e9507ae6707362110e3cedf`|
|artifacts/preseed_source_commitment.json|`3f26cf04e9cd2c4ee29c94e7757471ddce2167bb2a6932a9a5158e657e276a2b`|
|artifacts/run/execution.json|`da137a1ee2c1fa74b71daee7eb5a1ba126ce358918b36b208a2c1a677d534211`|
|artifacts/run/trajectories.jsonl|`8292381634ab9051097380418855f27668168aca2f8f7a02fbc38c6dff17adeb`|
|artifacts/run/failures.jsonl|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|
|artifacts/analysis/summary.json|`975a8fcdeeb70a36f3d3efbdd55ef7149c86f57e74da6c5154e1dbc63360e8ef`|
|artifacts/analysis/paired.json|`e3a3e7a7cfd5fcf28d0cfa08cbc7905a4c57feee5882434a16201aa29898632f`|
|artifacts/analysis/facts.json|`8436b039d66a7a41da970a5f48055de8247965fe556c7e4d5926d240c392c2ee`|
|VALIDATION.json|`24bc0f1642fd53e38d027e66f3b7e0246960df513b1945fcd7f480ec8fb35fae`|
|CERTIFICATION_VALIDATION.json|`f2c6f570dc0eca8077da9c78086cd0d9f9026a5b01565962d1297db9abd9636a`|
|artifacts/certification/terminal_enclosures.jsonl|`1bd3531dee3ea53b4f7bdfaf243df54d6ccd0cd028172fa31c589ae356eef680`|
|artifacts/certification/existing_replays.jsonl|`6f6bf87e7ca4d7f92b9589cfb07c238531e22dbdfd93122fa60096df3f70ad07`|
|artifacts/certification/counterexample.json|`55bf804bce296a3483610e85d1b3992a5cfc6f27bac339b66fab9d76b5587c52`|
