# Phase T1 data leakage and pre-training audit

## FINAL PRE-TRAIN VERDICT: PASS

The generated data, legal-input boundary, fixed training callers, and evaluation interfaces pass this bounded exploratory pilot's pre-training audit. The single prespecified MLP fit and single prespecified LoRA fit may proceed after `training_freeze.json` binds this audit, data, source, configuration and historical dependencies. This is a research-validity/source review by an independent native same-family role, not cross-family verification, formal security isolation, or evidence that training will help. No training or evaluation execution receipt existed at this verdict.

The reviewer read the user authorization, source code, public manifests, public state/label rows, tokenization and technical receipts. The reviewer did not read any private development seed, raw latent truth/type file, or reserved confirmation instance; no scientific world, model/GPU call, training, or replay was executed by the reviewer. Private-file permission checks used metadata only. The earlier `audit/T1_DESIGN_REVIEW.md` remains unchanged after its generation commitment.

## Complete-world isolation and denominators

| Split | Independent worlds | Correlated states | Maximum total tokens | Maximum prompt tokens |
| --- | ---: | ---: | ---: | ---: |
| Train | 64 | 1,024 | 412 | 384 |
| Validation | 8 | 128 | 413 | 385 |
| ID test | 8 | 128 | 408 | 380 |
| Held-out parameters | 8 | 128 | 414 | 386 |
| Held-out partition | 8 | 128 | 417 | 388 |
| Total | 96 | 1,536 | 417 | 388 |

Independent reconstruction of the public manifest and source plans confirmed 96 distinct data-world identifiers, 24 additional disjoint evaluation-world identifiers, and 120 distinct episode indices. Data splitting uses complete worlds and distinct namespaced split/index stream keys. Every world contributes exactly 16 consecutive rows at t=8+128k, k=0,...,15; per-world row ranges cover their split exactly once. Each split-file hash and every 16-row world-content hash matches the manifest. All 96 private world files have mode 0600 under a 0700 directory; their contents were not opened.

Generation completed all 96 worlds in 136.110545 seconds, with **185,088 online observations and 15,360 unique offline calibration observations**, and no failed or replaced world in the completed manifest. These generation costs are separate from later policy acquisition and training compute. All states remain in their declared split. The 1,536 rows are not 1,536 independent statistical units.

Training covers the 16-condition factorial four times. Validation and ID state-test splits use complementary balanced eight-cell fractions. The parameter holdout (.85,.60) is interpolation and absent from T1 training, although present in earlier research. The [2,2] partition is absent from training. These holdouts do not establish extrapolation, combined parameter-and-partition shift, natural-language reliability, or broad task transfer.

One identical observable state occurs at t=8 in two distinct worlds: train row192 and validation row48. The world identifiers, split keys and indices differ. With eight binary initial observations, such collisions are possible and do not constitute shared-world leakage. No deduplication or outcome-based replacement was performed. It would be incorrect to claim disjoint *observable values* across splits; the required independence is in world generation and allocation of entire histories.

## All-row input and label inspection

For all 1,536 rows the reviewer checked the exact row-key contract; validated the state and its 69-dimensional feature representation; reconstructed the exact system/user/assistant messages; checked counts, cap2048, remaining allowance, public R/eta/s and declared group sizes; and verified fixed calibration counts and monotone within-world observation histories. Every 128-action interval has the required total increment. Forced counts match the square-block calendar on every task/form stream.

Only allowlisted observable state enters prompts or MLP features. The data rows also retain teacher estimates and labels as separate diagnostics/targets, but the policy adapters never pass those fields to students. In particular hidden p/q, true answer/type vectors, identifiers, seeds, split names, evaluator scores and rewards are not student inputs. The canonical-message equality audit prevents a clean state field from concealing a contaminated serialized prompt.

The reviewer independently reconstructed all forced-only sign/type estimates and ordered-grid rate projections from the legal forced observations. All agree with the saved teacher diagnostics. Every saved ten-action float target agrees with expansion of its recorded a/b/c allocation and coefficient; all numerical feasibility checks passed. Recorded minimum information is at least 1.000000001; maximum recorded relative solver gap is 0.00010798458409136703, within the frozen state-dependent acceptance tolerance. These are numerical solver checks, not interval-certified optimality claims. No new optimizer label was generated or selected during this audit.

All 1,536 integer labels are the direct largest-remainder rounding of their saved float target, with sum100 and zero masked mass. Mean float-to-percent L1 error is **0.012881247916123483**, maximum **0.04268970939586416**. A repeated normalization of the saved float vector changes a near-tied remainder for **train row420**: one percentage point switches between task slots1 and2. Direct rounding of the saved target reproduces the stored label; training uses that label, and offline evaluation receives saved teacher percentages. This finite-precision tie sensitivity is retained and disclosed. No data or frozen generator was modified, and no world was rerun.

## Tokenization, fitting and failure boundaries

The public tokenization receipt checks all five splits with the actual local tokenizer, exact canonical messages, a strict prompt/completion prefix, completion-only labels and no truncation or filtering. Maximum total length417 and prompt length388 are comfortably within the frozen training limit1024 and inference prompt limit960. Training has 371,572 prompt tokens and 28,093 supervised completion tokens; validation has 46,621 prompt and3,516 completion tokens. Test tokenization is a schema/length check with no model forward or checkpoint selection.

Source inspection confirms that SFT uses only 1,024 training rows, one deterministic shuffled pass, microbatch1/accumulation8, exactly128 optimizer updates, rank8/alpha16, and final adapter only. All prompt labels are -100. Only text-language LoRA tensors are trainable; the BF16 base and visual components remain frozen, with FP32 adapters explicitly reported. Validation is evaluated after the pass and does not select a checkpoint. Both technical smoke receipts are required; the 1,024-token smoke has zero optimizer updates and fits the selected device.

The MLP uses only legal-state features, train-only normalization, fixed69→64→64→10 architecture, 9,290 parameters, and200 full-batch updates under the fixed time limit. Its continuous targets/output differ from Qwen's integer-percentage targets, which is disclosed and measured via rounding diagnostics. Neither student sees test data during fitting. `run_mlp.py` and `train.py` verify frozen files **and historical dependencies**, require this PASS, and refuse scientific retries/overwrites. MLP started/progress/failure receipts and SFT started/per-step/failure receipts preserve incomplete runs. Training completion and empirical claims remain unverified until postrun evidence exists.

The inspected test receipt reports **25/25 PASS in5.541 seconds**: 11 core/data tests, 12 evaluation/MLP contract tests, and two actual-tokenizer completion-mask tests. The reviewer independently executed the final11 core/data tests (all passed in0.464 seconds) using only handwritten/mocked observations. The evaluation tests exercise strict-gate rejection despite a floating crossing, certified acceptance, cap abstention, invalid-output fallback, hard call limits, partial-path persistence, wholly missing-method denominators and hidden-field exclusion. No learner fitting was performed by these tests.

## Evaluation contract and limits

The fixed offline subset contains120 states: five declared positions in every one of24 state-test worlds. Main closed-loop evaluation uses24 additional worlds, seven policies and fixed256/512 intermediate readouts under public cap2048. Six matched policies share block128, forced square exploration, cumulative tracking and a common profile decoder; native Aligned retains its original cadence as a separately labeled reference. Same-world methods share potential observation streams. Tests are paired by complete world, not by individual state or query.

Base Qwen and LoRA share a serialized resident model, prompt, greedy decoding, length limit, parser and legal fallback; adapter enablement is the treatment. Every Qwen request is charged once before inference against the shared600-call ceiling. Planned calls are240 offline +192 main +at most96 diagnostic. Invalid outputs/transport failures retain raw/error records and uniform-legal fallback; no teacher fallback exists. Missing/failed paths remain in denominators. The runner flushes each offline prediction and each closed-loop prediction/action/snapshot/path event. A resource interruption stops the experiment visibly rather than granting extra calls or silently replacing worlds.

The three diagnostic worlds are fixed by the pre-seed public plan and all have M=0. They reuse existing evaluation worlds at predeclared R16 and cap2048, with all seven methods checked by the strict Phase2d certificate at128-action intervals. A floating crossing cannot authorize a stop. At the cap, abstention remains distinct from a scoring-only guess. Under the inherited iid-channel and arithmetic contracts, the certificate's error statement is per prespecified policy/world experiment and concerns wrong certified output; it is not a claim of termination, sample optimality, or a family-wide e^-16 bound over all21 diagnostic paths. Fixed-budget guesses carry no such certificate. Diagnostic reuse is not independent confirmation.

The final evaluation caller additionally requires a separate `analysis_freeze.json` before evaluation. Analysis implementation and outcome interpretation must remain bound to the frozen protocol and retain full missing denominators. This pre-training verdict does not certify an analysis file that has not yet been reviewed, or any future empirical GO decision. Teacher-policy offline histories also do not eliminate student-induced distribution shift in closed-loop operation.

## Commitments checked before fitting

The reviewer rehashed all **10 generation-frozen files and49 historical Python/theory dependencies** after generation; all still match. The public history receipt records421 previously frozen artifact files, including the353 earlier files and68 Phase2d files. This review independently checks the49 imported source/theory dependencies and inspects the history receipt; it does not read old private seed/truth artifacts to duplicate that421-file check.

| Artifact | SHA-256 |
| --- | --- |
| `generation_freeze.json` | `1b2db2e2d867f15ea49a090a72d3013f3eb63be9f0f57a3133d37c2a6a373309` |
| `artifacts/data/manifest.json` | `dec715b1dbcd58ea03c869af5f9799a064858446248ed35b148f57ccbacb17df` |
| `artifacts/data/train.jsonl` | `2a123831b71c08f80f868ab7b848f092bd79b870eec7d621eb13c6e9e979953e` |
| `artifacts/data/validation.jsonl` | `077c6a48c2340e74b1ab5ced45fb4424d953b914bc9864b26faf44458dbf1977` |
| `artifacts/data/id_test.jsonl` | `1c6725b5c7afd2bf3a2796ffdd1e37b30206cfdb743e2bfb6ba27925578b1d87` |
| `artifacts/data/ood_parameters.jsonl` | `642b411833574fbbcc777bc36250f6314c451c25d1c751567fcffa117762ebf2` |
| `artifacts/data/ood_partition.jsonl` | `f409009b45151b03372375bdf6fc2e7727fdc449f8c39c12ff43a732134b5379` |
| `audit/TOKENIZATION.json` | `4fcb2bcb45e68f92980b016ab5ca4f3e1c02d975d009b64cce7fab617a7dc2cd` |
| `t1/evaluate.py` | `8be16816d7cd83478f66da36f1a23d4048d519503fc849dfb08ce2aee584cfa7` |
| `t1/mlp.py` | `cfa65c895040c945b1361e3bca5be79e61e1ee97aae69f9a0c3333e30f351cb6` |
| `t1/qwen.py` | `4882a87544a7be0c74944a471372b4b819089c6bd962d78922a8f1d8d8d42af6` |
| `t1/train.py` | `cc0c18ddfab6a6f49cd8afd26d2a5a65563cd84be6d4d95cb76eb025f155e8d4` |
| `t1/run_mlp.py` | `17a1a5cb34097886787ec6fcd34655c316d428ff0cdc308fb7c3788d71962278` |
| `t1/run_evaluation.py` | `bf84358c511740230281f13b4191928ac840a629c4529515e2960fc4bf53aaa8` |
| `t1/token_audit.py` | `1fe5f26c4b48e0d037b07f7a125de28a53298304dcab2d5a0ebecf0ea31c5e7a` |

Leave this audit immutable once bound by the training freeze. All later results, limitations, discrepancies and the final GO/REVISE/NO-GO assessment belong in the postrun review and required reports. No prior theory, method, benchmark or confirmation artifact is changed by this approval.
