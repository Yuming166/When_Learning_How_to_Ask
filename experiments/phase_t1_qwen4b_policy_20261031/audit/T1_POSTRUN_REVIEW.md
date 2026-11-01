# Phase T1 independent final review

Final status: **PASS for bounded execution, accounting and claim integrity; NO-GO for promoting the current LoRA configuration as a query-efficiency improvement.** All planned public evidence is complete. The intermediate pending entries below preserve the sequence of outcome access; the final reconciliation at the end supersedes them. This review is independent native same-family source/evidence inspection, not cross-family review or formal verification. The design, data and analysis audits remain immutable. The reviewer executes no model calls, training, scientific worlds or replays and reads no private seed/truth files.

## Interpretation limit recorded before held-out outcomes

The frozen system prompt specifies the observable-state interface, ten integer-percentage action slots, sum100, legal-action masks and JSON-only formatting. It does **not** explain the probabilistic environment, the objective of recovering the full hidden fact vector, the meaning of unknown shared high/low reliabilities and group types, or the mathematical information-allocation objective. Re-reading `t1/core.py` and `t1/qwen.py` confirms that BaseQwen and LoRA receive exactly this same prefix and serialized state; their inference difference is adapter disablement versus enablement, with identical greedy decoding and output validation.

This is a valid supervised policy-distillation design. Labels can teach the desired state-to-allocation mapping even though the task's statistical objective is not specified in natural language. However, **BaseQwen is an identical-contract initialization control, not an objective-aware or prompt-optimized zero-shot LLM baseline.** It lacks task information that the student can infer through1,024 labeled training examples. A LoRA improvement over BaseQwen can demonstrate learning under this fixed interface, including output-format compliance and teacher imitation; it cannot by itself establish superiority over a well-instructed pretrained Qwen, that weight training was necessary, or that the LLM learned a generally useful reliability model.

Retain all invalid outputs and uniform-legal fallbacks in the main denominators. Report format validity alongside allocation quality and closed-loop behavior so a validity gain is not silently equated with improved adaptive allocation. Any valid-output-only diagnostic would be selected by model behavior and must remain supplementary; it cannot replace the full-denominator comparison. The frozen matched teacher and MLP remain the substantive controls for practical distillation quality and computational value. A GO decision cannot rest only on beating this BaseQwen control. Conversely, an observed cheaper MLP matching or outperforming LoRA would still be relevant evidence against the practical need for this LLM configuration, regardless of the weak zero-shot-control interpretation.

This limitation does not invalidate or block the already authorized bounded fit/evaluation. No prompt edit, replacement baseline, extra training, evaluation rerun or new world is introduced. It is documented before viewing held-out model outcomes to avoid a result-driven reinterpretation.

Verified frozen source identities for this interpretation:

- `t1/core.py`: `a7b682c48bb25d7593af1fc5a2703741b04cac8b4d45624450b31e3e6c2b8cac`
- `t1/qwen.py`: `4882a87544a7be0c74944a471372b4b819089c6bd962d78922a8f1d8d8d42af6`

## Public postrun reconciliation

### Completed fitting receipts independently checked

SFT completed exactly128 optimizer steps and1,024 microbatches in1,820.090869 seconds, including12.436991 seconds loading and the post-epoch validation/save work. The reviewer verified all128 consecutive step records and microbatch counts8,16,...,1024, finite losses/gradient norms and monotone recorded elapsed times. Averaging the128 block losses reproduces the reported example-mean loss0.2492416006834901. Supervised target-token counts are28,093 for training and3,516 for validation and agree with the pre-training token audit. Validation token cross-entropy is0.20777942341369862; the saved checkpoint is final-only, with no selection on this diagnostic. Peak allocated memory is10,705,712,640 bytes; peak reserved memory is17,439,916,032 bytes.

MLP completed all200 fixed full-batch updates on1,024 states in4.118491 seconds. Its200 saved loss values are finite; the final post-update train forward-KL loss is0.05908285453915596. This loss is not numerically comparable to Qwen's token cross-entropy objective. The source uses train-only normalization and no validation checkpoint selection; the receipt contains the fixed9,290-parameter architecture.

The reviewer directly parsed the public safetensors files using CPU byte/array reads, without instantiating a model or running inference. Both the technical smoke adapter and final adapter have496 finite FP32 tensors, all text-language LoRA only, totaling16,232,448 parameters. All248 LoRA-B tensors are zero in the smoke artifact and nonzero in the final artifact, independently corroborating that the final adapter was actually updated. Final adapter SHA-256 is `723d013a0319b5eb99b0d94a20cf7fa1a60eb64e00430257f774f7f2dcc29940`; smoke adapter SHA-256 is `7fefa1337b94d853b6808806b94b4f50cdd93af56751b5bacf9b822922568f1e`.

All generation commitments (10 files/49 dependencies), training commitments (31 files/49 dependencies) and analysis commitments (three files) still match at this intermediate audit. Their SHA-256 values are respectively `1b2db2e2d867f15ea49a090a72d3013f3eb63be9f0f57a3133d37c2a6a373309`, `222d250bf688a1b7b3f9d6f739a40d00d1465ecf253eb238500a7c232c850e2d`, and `7fc8180d91a27d5fc12d14149415e1d3f9031da042464a2a7e01c8271bb19587`. This is an intermediate check, not yet the final preservation receipt.

### Intermediate evaluation inspection — no comparative verdict

At the first public-record inspection, evaluation was still `started`. The reviewer checked170 complete offline records (120 MLP and50 BaseQwen; zero LoRA records yet). Every record binds to its prespecified held-out world and one of the five declared states; saved state and teacher target match the original frozen data row. All recorded allocation L1 and smoothed forward-KL metrics were independently recomputed, and all available Qwen raw strings were reparsed to confirm validity, masks, weights and fallback handling. No incomplete JSON tail was present in that snapshot. These are schema/accounting checks of a growing file, not a performance comparison or a complete-call reconciliation.

**Empirical verdict remains PENDING.** The final review still requires all360 offline predictions,189 paths and336 main readouts (or explicit full missing/failure denominators), final call/cost/latency receipts, world-paired vectors, strict terminal certificates and abstentions, final source/history preservation evidence, analysis outputs and the proposed research decision. No partial BaseQwen result is used to predict or preselect the final comparison.

### Complete offline evidence — frozen parser, all120 states per method

The complete360-record file was inspected before reviewing a parent-authored comparison. Each method has the exact same120 declared states: five positions within each of24 held-out worlds, eight worlds in each stratum. Every saved state and teacher allocation binds to the frozen data row; every `(method,row_id)` is unique. All240 Qwen raw strings were independently reparsed against the original contract. All allocation weights respect the legal-action mask and sum to one after the specified fallback. No invalid row is discarded.

The reviewer independently recalculated allocation L1 and smoothed forward KL to numerical tolerance. Plug-in information was independently reconstructed by enumerating all15 wrong fact vectors and all group-type configurations, aggregating the weighted oriented Bernoulli successes, and maximizing over the continuous triangle using the unconstrained candidate plus its three edges `q=.5`, `p=1−eta`, and `p=q`. This calculation includes the calibration intensity and type-report term. All360 saved student/teacher information values and relative deficits agree; maximum absolute discrepancy is3.78e−15. This numerical cross-check validates the reported diagnostic computation; it is not an independent proof or a truth-based information estimate.

Each table entry first averages the five states within each world, then averages the eight world means in its stratum. Equal cluster sizes make these means equal to the40-state means, but paired comparisons retain the world as the unit. Lower L1, KL and deficit are preferable. Deficit is the observable plug-in diagnostic, not a recovery probability or certificate.

| Stratum | Method | Valid / fallback | L1 | Smoothed forward KL | Relative information deficit |
| --- | --- | ---: | ---: | ---: | ---: |
| ID | MLP | 40 / 0 | 0.359244 | 0.285283 | 0.218193 |
| ID | BaseQwen | 0 / 40 | 0.991869 | 0.671133 | 0.417264 |
| ID | LoRA | 28 / 12 | 0.972884 | 6.157121 | 0.496423 |
| OOD parameters | MLP | 40 / 0 | 0.346842 | 0.250511 | 0.276003 |
| OOD parameters | BaseQwen | 2 / 38 | 1.031017 | 1.095084 | 0.488536 |
| OOD parameters | LoRA | 28 / 12 | 1.209343 | 8.090437 | 0.618815 |
| OOD partition | MLP | 40 / 0 | 0.645569 | 0.631991 | 0.666123 |
| OOD partition | BaseQwen | 2 / 38 | 0.855750 | 0.529185 | 0.423886 |
| OOD partition | LoRA | 11 / 29 | 0.911706 | 2.452361 | 0.485512 |
| Pooled24 worlds | MLP | 120 / 0 | 0.450552 | 0.389262 | 0.386773 |
| Pooled24 worlds | BaseQwen | 4 / 116 | 0.959545 | 0.765134 | 0.443228 |
| Pooled24 worlds | LoRA | 67 / 53 | 1.031311 | 5.566640 | 0.533583 |

The saved `offline_summary.json` agrees with these independent full-denominator calculations. Mean measured prediction-wrapper wall times are0.000526s for MLP,3.664758s for BaseQwen and5.601233s for LoRA; these are observed implementation costs under the recorded backend, not architecture-intrinsic latency guarantees. Shared model loading is outside these per-call means.

LoRA raises exact-contract validity from4/120 to67/120, yet the frozen-parser pooled imitation errors and information deficit are worse than BaseQwen's predominantly uniform fallback. BaseQwen's result must therefore be described as mostly uniform-legal fallback behavior, not successful adaptive zero-shot allocation. MLP has lower world-mean L1 than LoRA in all24 worlds, and lower mean KL in all three strata. It does **not** dominate every diagnostic: its OOD-partition information deficit0.666123 is worse than LoRA0.485512 and BaseQwen0.423886. Teacher-distance and plug-in information rankings are distinct; neither settles the pending closed-loop comparison.

Raw offline file SHA-256: `ca9b830169a73c47e9097945018c1810a4bc063723e862e43c9015ca3efeac52`; summary SHA-256: `9849e73dd96027b73cdd79a1a9774856d880c0e24a98d64bc277374c89cec74f`. The completed training report was also checked: its numerical training receipts agree, it separates token CE from allocation quality, and it retains the BaseQwen interpretation limit above. Its hash at this inspection is `f12aadea0cfc81d060993b1ab6ea478d457287cb36a63de0c3064353a579498b`.

### Parser sensitivity boundary recorded while main evaluation continues

Independent inspection of every raw offline array shows that **all53 invalid LoRA outputs are ten legal, correctly masked integer percentages summing to99**. They fail only the frozen sum100 check. BaseQwen has111 non-100 sums and five sum100 masked violations as saved first-error categories; inspecting every condition reveals38 total masked violations,33 overlapping the sum failures. Any sum-only relaxation must preserve all38 masked rejections.

A supplementary analysis of these already saved strings may normalize any positive raw integer sum while retaining every other validation rule and the same uniform fallback. It must use all120 states/model and world-paired aggregation, preserve MLP, and be explicitly labeled **post-hoc parser sensitivity**. It does not change the frozen primary parser, source, data, main trajectories or research denominator. It requires no model inference or new world. Its result can diagnose an interface penalty in offline imitation, but cannot estimate how an altered parser would change later states, queries, recovery or strict stopping in a counterfactual closed-loop run. It cannot replace the primary result or be described as a preregistered improvement.

**Final empirical verdict remains PENDING** until the189 public paths,336 main readouts and complete accounting/certification/preservation receipts are available.

### Completed post-hoc parser sensitivity independently checked

The reviewer inspected the diagnostic source and report and independently reparsed/recomputed all360 rows without invoking that script, a model, or an environment. All72 method/world means and48 descriptive paired vectors agree; the largest independently recalculated metric discrepancy is3.56e−15. Source bindings match. Rehashing the complete generation, training and analysis commitments again finds no changes, so the diagnostic has not altered the frozen primary experiment.

| Method | Frozen valid /120 | Relaxed valid /120 | L1 frozen → relaxed | KL frozen → relaxed |
| --- | ---: | ---: | ---: | ---: |
| MLP | 120 | 120 | 0.450552 → 0.450552 | 0.389262 → 0.389262 |
| BaseQwen | 4 | 82 | 0.959545 → 1.017756 | 0.765134 → 0.977269 |
| LoRA | 67 | 120 | 1.031311 → 0.999698 | 5.566640 → 7.825043 |

All38 raw BaseQwen mask violations correctly retain fallback after the sum rule is relaxed. All53 LoRA sum99 outputs become legal under this diagnostic. LoRA's pooled L1 improves slightly, while its smoothed KL worsens; MLP remains substantially better on both pooled imitation metrics. Thus the frozen validity penalty is real, but this particular post-hoc normalization does not turn the recorded offline results into a broad successful-distillation finding. Nothing here establishes a normalized policy's closed-loop recovery, costs or stopping behavior.

Diagnostic source SHA-256: `d7f980136650524dde3e75e0d7dd561a1854a42362c06b6d8224d513008a81b1`; artifact SHA-256: `4c1ef5aa736635619dab13db34eb31043f82f7ce2b3cab090ae9f8f884c8347d`. The report explicitly records outcome-informed selection, full denominators, zero new calls/worlds/labels, fixed primary results and the unmeasured closed-loop counterfactual. This scoped supplementary analysis **passes** inspection; the overall empirical verdict remains pending.

### Additional final-interpretation constraints

Fixed-budget recovery may reach a ceiling in this small, favorable grid. Identical observed successes would establish no observed benefit at those readouts, not equivalence, noninferiority, equal sample complexity or equal behavior at smaller budgets. The original256/512 readouts and24-world plan must remain unchanged after seeing any ceiling.

Measured Qwen latency is conditional on the actual local reference-kernel Transformers implementation, BF16 base and unmerged FP32 LoRA adapters. It is a meaningful cost of this executed pilot, but cannot be treated as the best achievable serving latency of Qwen or LoRA generally. The identical-interface, incompletely explained BaseQwen task remains a limited initialization control throughout the final comparison.

## Final completed-run reconciliation

### Coverage, observable boundary and execution records — PASS

The final files contain exactly360 offline predictions,168 primary paths,21 diagnostic paths and336 primary readouts. All189 path identities equal the predeclared method/world/phase Cartesian products, without duplicates, replacements, missing paths or failed paths. All seven primary methods cover the same24 worlds; the diagnostic uses only the three predeclared reused worlds. The completed evaluation receipt records zero retries and zero external model API calls.

The reviewer algebraically reconstructed all104,576 recorded evaluation actions from the public transcripts. Every action, response count, forced-response count, type-response sequence, calibration charge, prediction-boundary state and snapshot prefix matches its saved path. All prediction inputs have exactly the canonical observable allowlist, cap2048 and correct remaining count; evaluator identity, truth and rewards are absent. Every matched policy updates at8+128k. Reconstructing cumulative allocation deficits from the saved target weights reproduces every chosen action, including the frozen square exploration schedule and first-index tie rule; DNoType never purchases a type report. All overlapping same-world/action/stream-position observations agree across methods and the reused diagnostics. This checks the recorded coupling without generating any observation or reading private truth.

All252 closed-loop Qwen raw predictions were independently checked against the frozen parser and legal-action masks. All107,042 durable event entries agree with the complete path records, including every action, prediction, snapshot and final path event. The independent count calculation reconciles final costs and prefixes;256/512 are not added as separate trajectories.

Recovery correctness is taken from the trusted evaluator's public score/snapshot fields and its inspected scoring code. This reviewer deliberately does not read private truth to re-score episodes. The counts, guesses, terminal score fields and public correctness fields are internally consistent; this audit does not claim a separate truth oracle.

### Fixed-budget results and descriptive analysis — PASS, no demonstrated gain

All seven methods recover the entire vector in all eight worlds of every stratum at both256 and512 online actions:24/24 per method per readout. All56 saved recovery-pair vectors are exactly zero, and the frozen bootstrap returns[0,0] for those observed vectors. Such a degenerate resampling result at a ceiling is **not** a population guarantee, equivalence test or noninferiority result. It supplies no evidence that LoRA saves queries at either prespecified readout.

Main-path allocation and computation remain quite different despite that shared outcome:

| Method | Main policy updates | Main fallbacks | Task queries | Type queries | Main inference wall seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| NativeAligned | 960 | 0 | 11,142 | 1,146 | 83.668915 |
| AlignedBlock128 | 96 | 0 | 11,227 | 1,061 | 8.558699 |
| DNoTypeBlock128 | 96 | 0 | 12,288 | 0 | 0.031934 |
| DTypeBlock128 | 96 | 0 | 9,217 | 3,071 | 0.037619 |
| MLP | 96 | 0 | 11,018 | 1,270 | 0.055606 |
| BaseQwen | 96 | 96 | 10,240 | 2,048 | 361.603358 |
| LoRA | 96 | 29 | 11,367 | 921 | 534.138106 |

Each method additionally pays1,536 offline reference observations across its24 paths. These are the same1,536 world-specific reference observations reused across methods, so per-policy charging and unique generated observations must remain distinct. NativeAligned's960 updates versus96 matched updates also makes its compute difference a cadence comparison, not a pure distillation comparison. In the main closed loop, BaseQwen is entirely uniform-legal fallback; LoRA has67 valid updates out of96.

The reviewer independently reconciled all56 primary summaries,56 primary paired records,12 offline summaries,48 offline paired vectors and their frozen4,000-resample intervals, all seven diagnostic summaries, and all seven computational cost rows. Offline resampling was reconstructed from seed731032 with five-state world means and eight worlds per stratum; pooled resampling preserves eight draws within each stratum. Saved values agree within numerical tolerance. The fixed heterogeneous grid and exploratory, unadjusted interpretation remain as declared before outcomes.

### Strict stopping diagnostics — accounting PASS, limited negative evidence for LoRA

The three columns below follow the predeclared ID, OOD-parameter and OOD-partition world order. Every diagnostic usesR16, cap2048, checks every128 actions, andM=0, so no offline cost is omitted here. A dagger means cap abstention, not a certified output.

| Method | ID online actions | OOD-parameter actions | OOD-partition actions | Certified /3 | Cap abstentions /3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| NativeAligned | 384 | 768 | 640 | 3 | 0 |
| AlignedBlock128 | 384 | 384 | 768 | 3 | 0 |
| DNoTypeBlock128 | 384 | 384 | 896 | 3 | 0 |
| DTypeBlock128 | 384 | 384 | 1,920 | 3 | 0 |
| MLP | 640 | 512 | 2,048 | 3 | 0 |
| BaseQwen | 1,152 | 640 | 1,408 | 3 | 0 |
| LoRA | 384 | 2,048† | 2,048† | 1 | 2 |

The reviewer checked all145 retained gate records:126 rejected checkpoints and19 certified terminal checkpoints. Every certificate's candidate equals the contemporaneous guess; task/type/calibration totals match the reconstructed prefix; lower/upper bounds are ordered; gap endpoints conservatively subtract candidate and wrong-profile endpoints; and every certified decision satisfies the strict `gap_lower > beta_upper` condition. Every rejected checkpoint satisfies `gap_upper <= beta_lower`. The threshold expression was independently recalculated asR plus twice the log reference-count factor and the log task/type count factors, and lies within its saved bounds. Snapshot certificates and gate histories agree exactly. Certification occurs once per successful path and immediately terminates that path. The two abstentions reach2048 with no prior certificate and expose no strictly certified output.

All19 certified outputs are correct according to the trusted evaluator. Both LoRA abstention paths also have correct terminal scoring guesses, but those guesses remain uncertified and cannot be counted as certified recoveries. MLP certifies at exactly2048 on its last diagnostic, so that path is correctly a success rather than an abstention. LoRA's average1,493.33 online actions includes both cap paths; calling it the mean cost among successful outputs would be wrong.

These records support only a three-world, reused diagnostic comparison. They do not estimate a tiny error probability, prove termination or establish a general ranking. The inherited strict gate's model-level error guarantee remains conditional on the previously audited mathematical model and exact-arithmetic/Decimal contracts, with risk fixed before data, arbitrary predictable allocation and the allowedd≤4 domain. It concerns erroneous certified outputs per trajectory, including calibration randomness in the joint model; it does not certify sampler optimality, efficiency, termination, the fixed-budget guesses, or an experiment-wide error bound for all21 paths. A learned allocation policy does not inherit the teacher's asymptotic optimality from SFT. This review checks saved certificate structure and frozen-source provenance; higher precision agreement is not substituted for the prior interval argument.

### Complete costs and preservation — PASS within stated provenance

The call counter, final receipt and primitive predictions all agree on492 Qwen calls:240 offline,192 primary and60 diagnostic, with241 BaseQwen and251 LoRA calls. The hard ceiling is600; charged-but-unrecorded calls are zero. BaseQwen has237 fallbacks across all241 calls; LoRA has82 across251. Training/validation forwards and the two zero-update technical backward smokes are distinct from these policy-generation counts.

Evaluation uses86,016 primary and18,560 diagnostic online actions, totaling104,576 =94,158 task +10,418 type. Per-path offline charges total10,752, giving115,328 charged evaluation acquisitions. The data-generation stage separately consumed185,088 online actions and15,360 unique offline observations. Evaluation introduces1,536 world-unique reference observations; the diagnostics introduce no additional unique reference stream. These quantities are not interchanged or silently combined into a claimed sample-efficiency improvement.

Completed evaluation wall time is2,425.450353s, including one shared12.534666s resident-model load; process CPU is2,428.185883s and peak allocated memory9,357,278,208 bytes. Together with the previously reconciled data generation, SFT and MLP fitting stages, recorded scientific-stage wall times sum to4,385.770258s. This is not total project elapsed time. The final cost report additionally preserves36.904184s for the two technical smokes and2.412306s for CPU analysis/plotting, and explicitly leaves unmetered setup, tests and hash audits outside that sum. There is no direct GPU-kernel-time or energy measurement. All per-method call counts, tokens, inference wall/CPU totals, median/P95 latencies and task/type/offline cost totals agree with raw records.

Final preservation provenance is explicit. The reviewer independently rehashed all407 public files bound by the eight historical receipts and verified the eight receipt identities. Fourteen historical private seed/truth/reproduction files were deliberately not opened; their unchanged status is supported by the parent's `PRESERVATION.json` hash audit, which reports421/421 historical files. All three T1 freeze commitments and their49 historical source/theory dependencies independently match; the design, data and analysis review files remain unchanged. The reviewer independently streamed and hashed all14 public base-checkpoint files,9,342,907,469 bytes, confirming the original checkpoint remains unchanged without loading a model. The resource-release receipt reports the pilot GPU freed and the existing inference service retained. No old confirmation protocol was executed by this review.

### Final claim review and disposition

`TRAINING_REPORT.md`, `QUERY_POLICY_EVALUATION.md`, `COMPUTATIONAL_COST.md` and `FINAL_DECISION.md` agree with the independently reconstructed evidence. They retain full denominators, all two LoRA cap abstentions, the weak-objective BaseQwen initialization control, the post-hoc nature of parser normalization, the backend-specific latency, the fixed-budget ceiling and the limited held-out conditions. The historical(.85,.60) condition is held out relative to this training split but is an interpolation and not a previously unseen research setting. No natural-language/Web transfer, larger dimension, calibrated population interval, strong zero-shot comparison or inherited sampler-optimality claim is established.

**FINAL POSTRUN VERDICT: PASS for execution/data-accounting/report integrity; NO-GO for promoting this frozen LoRA configuration as an established method enhancement.** The training ran and changed the intended adapter, but its full-denominator offline imitation is inferior to the cheap MLP, fixed-budget recovery is uninformative at the ceiling, the limited stopping diagnostic has two LoRA abstentions, and measured computation adds substantial cost. This does not prove that LLM policy training cannot work, or authorize further fitting, prompt changes, new worlds, RL or confirmation runs. MLP's cheaper and better imitation alone also does not establish it as a replacement for the matched teacher. Preserving this bounded negative pilot is the supported research outcome.

This is a native same-family independent source/evidence review with access to public records; it is neither cross-family external review nor formal verification. No unresolved material issue was found in the completed public evidence. The parent's final all-output receipt is intentionally written after this review becomes immutable; that later packaging step is not an additional scientific result.

Final reviewed identities (SHA-256):

- Raw paths: `313280315adcdb571ef36b4fa3f6781a82223845690b56bc57dc3c7dc22d0c15`
- Evaluation receipt: `b3f466fe48c4b7b5c12f85c034c109b54bf61ba5b8ac09da0d021026cabc416f`
- Call budget: `f165f6edf3ff726e7ea812c6d9033ff6e657a7e5bba5337b58ecdb705701f718`
- Preservation receipt: `dff98664325c3370bc875f1ba81910c264916aa2bd225de629ca8be9fab161e9`
- Complete coverage: `1790cf51647a18fc3bf8fdabb2161ad5dcba9a5fe472203e0c8d44d4190ae142`
- Primary summary: `1b0ab77058d064a1563d79fe971108c40c95b730975cdd12aa0420602fed1f12`
- Offline paired results: `c19dcb2bff52909c0724b57978df7e052a6f47853c11482962405987e003400b`
- Diagnostic summary: `d00606f7b13f3f3a09c81a9a897e425b138560c6574f755a5bb9e42ccae47349`
- Computational costs: `8a135d85b1f6c37b66da0fed25c4ee3f027e1a6cf1354129a9d15e2e4d5349b4`
- Final decision report: `5cf5632ba8608955a2c10566b909ec493c609ab1392fafee2805c70c6e3b961f`
- Evaluation report: `dc9868018a3d4d01c62429fb3c5674895637706020231232815eb790c604f4c2`
- Cost report: `f07898d09459ad89bedca7850af38306f7936e401d41a3dd3379e0aaf6a47a83`
