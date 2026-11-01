# Phase T1 analysis review before held-out evaluation

Review type: independent native same-family source and research-validity review. No held-out model outcome, private seed/truth file, model call, training, scientific world generation or replay is used for this review. The frozen design/data audits remain unchanged.

## Review history: initial CONDITIONAL, resolved by the final PASS below

The inspected analysis correctly defines 360 offline predictions (three methods ×24 worlds ×five positions), 189 closed-loop paths (seven methods ×24 main worlds plus seven ×three reused diagnostic worlds), and336 primary readouts (seven ×24 ×two budgets). It rejects duplicate or unplanned records and validates world/stratum/readout binding. Missing paths, states and failed paths remain explicit; a partially observed world does not become a four-state substitute for a five-state offline mean. Missing paired outcomes suppress paired means and intervals rather than selecting complete cases. Incomplete coverage suppresses comparison figures and creates an incomplete report.

Offline metrics average the five predetermined states within each world first, then give each of eight worlds in a stratum equal weight. Paired vectors subtract the same world under two methods. Primary recovery similarly uses eight paired binary world outcomes; the256/512 readouts are two prefixes of each path, not independent trajectories. Missing recovery outcomes retain identification bounds with denominator8. Invalid-output fallbacks remain outcomes and expenses. Negative plug-in information deficits are retained rather than clipped into apparent success.

The code retains saved teacher percentage labels, so it does not silently redefine the previously disclosed near-tied rounding case. The information deficit is an observable-state floating-point diagnostic, distinct from latent true-parameter information and a stopping certificate. Native Aligned remains separate from the matched block128 teacher. A difference involving native cadence cannot be attributed solely to distillation.

The three-world strict-stop diagnostic has a denominator3 for every method and separately counts wrong certified outputs, cap abstentions, failures and missing paths. It provides no independent replication or empirical verification of a tiny nominal risk. Cost totals use each path's final acquisition count once, rather than summing cumulative256/512 prefixes. Calibration has separate unique-world generation and per-policy charges. Shared resident-model load is counted once and is already included in evaluation wall time; SFT loading is already in training wall time. Stage-wall sums are explicitly not elapsed pipeline time when stages overlap. Warm inference latency alone does not imply end-to-end efficiency, and GPU kernel seconds are honestly unmeasured.

The following focused source revisions were requested before a final PASS:

1. State explicitly that the fixed, heterogeneous eight-world condition grids make ordinary world-resampling percentile intervals descriptive sensitivity summaries, not calibrated population confidence intervals. Keep4000 resamples and seed731032 fixed, with no multiplicity-adjusted claim.
2. Do not label evaluation COMPLETE when charged Qwen requests exceed recorded predictions; require exact reconciliation and the600-call ceiling for complete evaluation. Preserve positive differences on incomplete runs.
3. Check that a diagnostic completion has a true terminal strict certificate and matching certified output; validate cap abstention semantics, rather than treating a standalone `complete` boolean as a certificate.
4. Recheck both training and analysis freezes at analysis entry, not only before evaluation, so post-evaluation source/data drift is rejected.

## Final source verification

### FINAL PRE-EVALUATION ANALYSIS VERDICT: PASS

All four requested changes were inspected in the final source. The structured analysis protocol and rendered report explicitly classify the intervals as descriptive paired-world resampling sensitivity on fixed heterogeneous grids, not calibrated population confidence intervals. The declared seed731032 and4,000 resamples are fixed. The additional `all_24_worlds` display reuses the same24 worlds; pooled resampling draws eight worlds within each of the three strata, maintaining their equal representation. It neither creates extra samples nor removes the within-stratum heterogeneity limitation. Pooled recovery uses denominator24, while each component stratum uses denominator8.

Complete coverage now additionally requires charged Qwen calls to equal retained prediction/path calls and lie within0..600. Undercharging fails the accounting audit; overcharging or a positive unrecorded difference prevents COMPLETE and figures. Incomplete records preserve the difference rather than manufacturing a prediction. The terminal diagnostic validator checks boolean completion/abstention semantics, exactly one terminal certified crossing, matching path/snapshot/certificate candidates, finite decimal interval endpoints with `gap_lower > beta_upper`, and equality with the final retained gate-history entry. A completed uncertified diagnostic must reach cap2048; fixed-budget paths cannot claim certified output. This validates the retained certificate's consistency under the previously audited gate implementation; it does not replace its arithmetic proof or independently rerun the gate.

Analysis entry verifies both `training_freeze.json` and `analysis_freeze.json` before reading results or creating analysis artifacts. It refuses an existing output directory. Failure keeps an explicit audit-failed receipt and prevents a valid complete-comparison report. Analysis wall/CPU and Python/NumPy/Matplotlib versions are recorded separately from model computation. The developer's CPU plot smoke produced both planned plot concepts in PNG/PDF from handwritten fixtures; it used no scientific outcomes.

The reviewer independently executed **14/14 final deterministic analysis tests, PASS in0.672 seconds**. They use hand-assigned scores and mocked receipt structures, not generated worlds, trained models or private inputs. The tests independently check known paired vectors and resampling quantiles, averaging before world resampling, incomplete-state/pair suppression, missing-world identification bounds, all denominators, retained invalid fallbacks and negative deficits, duplicate/unplanned rejection, cost deduplication, charged-call discrepancies, strict endpoint/candidate/history rejection, cap-abstention consistency, pooled24 reuse, and incomplete-report/figure suppression.

At this verdict, the held-out evaluation artifact directory did not exist. The reviewer read no held-out model outcome. All31 training-frozen files and49 historical dependencies were rehashed and still match; the immutable design and data audits are among those commitments.

| Reviewed commitment | SHA-256 |
| --- | --- |
| `t1/analyze.py` | `74cb36c97cd5ccf72b5d822ce6bb9f75a1326295b07b9a02570681d61c82bb24` |
| `tests/test_analysis.py` | `971d8569838e56664cd4082d408b2a38cfe61eaa7502aa0cb9f9c7108f043ec1` |
| `training_freeze.json` | `222d250bf688a1b7b3f9d6f739a40d00d1465ecf253eb238500a7c232c850e2d` |

The parent may now bind these analysis files and this review in the separate analysis freeze before held-out evaluation. Leave this review immutable afterward. Approval is limited to the inspected aggregation/reporting code; it does not predetermine GO/REVISE/NO-GO, establish LLM necessity, or authorize population, asymptotic, natural-language or web-reliability claims. The final audit must still reconcile actual public records, all failures/abstentions, cost and latency, frozen hashes, and the proposed conclusions.
