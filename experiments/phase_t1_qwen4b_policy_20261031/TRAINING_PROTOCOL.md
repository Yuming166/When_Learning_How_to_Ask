# Phase T1 — Qwen3.5-4B Query Policy Pilot v0.1

## Material Passport

Date 2026-10-31 Asia/Shanghai; source is the user's attached Phase T1 task and frozen QRelBench-Exact/Aligned code. This is an explicitly authorized, isolated exploratory training branch. No original theory, Phase2c/2d, concurrent method/benchmark work or confirmation artifact may be modified. Complete one bounded pilot and stop with GO / REVISE / NO-GO. No RL/GRPO, hyperparameter search, paid service, external data upload or 35B use.

## Question and limits

Can a rank8 LoRA Qwen policy imitate the observable KL teacher allocation, transfer to T1-held-out conditions, and provide practical value compared with a small MLP? Distillation does not imply improvement over the teacher. QRelBench-Exact samples a specified iid channel; these experiments cannot establish natural-language/human reliability structure. Held-out (.85,.60) is interpolation and was used in earlier research, although it is absent from T1 training.

## Resource and technical gate

Read-only local checkpoint `/storage/lianjh/modelzoos/Qwen/Qwen3.5-4B`; record hashes and observed class. One currently free RTX4090 (initial candidate GPU3) only; inspect immediately before allocation, use an exclusive task-local lock, never terminate or reconfigure another process. Existing service GPU6 remains untouched. Existing Transformers5.17.0 / torch2.6.0+cu124 environment is reused read-only; PEFT0.21.2 and Accelerate1.15.0 reside only in this experiment's `.deps`. ms-swift is not installed; this pilot uses native Transformers+PEFT, not an unverified ms-swift recipe. Freeze all visual weights; select LoRA only on text-language attention/MLP projections. Preserve pretrained weights and save adapter separately.

First run a synthetic technical forward/backward and adapter save/load smoke test, with no scientific optimizer update. Audit data leakage and resources before the scientific SFT run. A failed technical test is retained and can be corrected with a documented implementation revision; no silent retry of a scientific training run. Hard smoke limit600s, scientific SFT limit3600s, evaluation limit3600s. A limit stops only this task's own process, retains partial records and produces an incomplete result.

Technical refinement before data generation: retain the first short70-token smoke, then test a synthetic1024-token masked-prefix batch with zero optimizer steps. PEFT adapters remain FP32 by default on the frozen BF16 base; this mixed precision is recorded explicitly. CUBLAS_WORKSPACE_CONFIG=:4096:8 is set for subsequent GPU execution. Greedy evaluation is deterministic in decoding settings; hardware/kernel arithmetic is not claimed bitwise reproducible.

## Legal policy state and teacher

Student input is a strict allowlisted summary of d=4, known group membership and rate domain, known type-report accuracy, all task response counts, forced-only response counts, type-report counts, labelled calibration success/total counts, confidence target R, elapsed count, public acquisition cap and remaining cap. No seed/world identity, hidden answer/type/rates, reward, evaluation result, teacher-derived estimate or optimizer label is present in the input. Target labels are separate ten-action allocation weights. Type actions for an absent second group are masked.

Teacher labels call the frozen Aligned allocation update on observable counts only, retaining its forced-only estimator, ordered grid and numerical feasibility checks. They are numerical targets, not certified mathematical optima. All learners retain balanced square-block forced exploration and cumulative-deficit scheduling. Matched policies update at t=8+128k; native frozen Aligned is an additional original-cadence reference. Initial eight actions force one observation per task/form. For Qwen the target is a JSON array of ten integer percentages with sum100, largest-remainder quantization; retain float weights and quantify rounding. Parse strictly; invalid output or nonzero masked mass is logged and uses uniform over legal actions, never teacher fallback. Deterministic greedy decoding, no thinking, max64 generated tokens, no sampling. MLP uses the same legal information and predicts float masked-softmax weights; its absence of percentage quantization is explicit.

## Data and splits, frozen before new seed

96 entirely new T1 development worlds, 16 decision states per world at t=8+128k, k=0..15, public cap2048: 64 train worlds/1024 states, and 8 worlds/128 states each for validation, ID test, held-out-parameter test, held-out-partition test. All states from a world stay together. Train rates are (.80,.55),(.90,.65), partitions [4]/[1,3], alpha0/1, R64/256, known s=.8 and eta=.05. Held-out parameters are (.85,.60); held-out partition [2,2] uses training rates. Conditions are deterministically balanced within each split. Private generating specs/seeds stay evaluator-only and outside model datasets.

Offline allocation evaluation uses all24 test worlds, five prespecified positions k=[0,3,6,9,15] each, 120 states per model. Training/validation/test observations are not used to tune templates or a search. One fixed prompt, one LoRA run, and one MLP configuration. Validation loss is a diagnostic; no test-dependent checkpoint or candidate selection.

## One bounded training run

Qwen post-trained checkpoint, BF16, LoRA rank8/alpha16/dropout0, text projections only, gradient checkpointing, max sequence1024, batch1, accumulation8, AdamW lr2e-4/weight_decay0, one epoch1024 examples/128 optimizer steps, fixed seed731031, gradient clip1. Completion-only causal-language-model cross entropy on the percentage JSON; prompts are masked. No packing or silent truncation. Record exact tokens, parameter names/counts, losses, gradient norms, memory, wall/CPU and loading times. Save final adapter without merging the base. Compute validation loss after the epoch; do not pick a checkpoint from test results.

MLP: same legal state feature function, train-only normalization, 69→64→64→10 ReLU masked softmax, Adam1e-3, fullbatch soft-label forward KL, fixed200 epochs/120seconds, seed731031, no validation selection or search. CPU training/inference cost and parameter count recorded. Continuous float teacher targets are used, so compare Qwen rounding loss separately.

## Closed-loop evaluation and controls

24 ADDITIONAL new worlds, disjoint from all96 state-data worlds: eight ID, eight held-out-parameter, eight held-out-partition. Primary R64 and alpha0/1 balance. Public cap2048 everywhere. Observe full-vector recovery at intermediate fixed-budget readouts256/512; these are evaluator readouts, not policy-known deadlines. This choice does not establish deadline-conditioned optimization. Use the same potential response streams within world across methods.

Seven policies: original frozen native-cadence Aligned; matched Aligned-Block128; D-RRC-NoType-Block128; active D-RRC-Type-Block128; MLP; base Qwen; LoRA Qwen. Only native Aligned retains native cadence; the other six share block128, forced exploration/tracking, known information, iid response environment and common exact-profile GLR decoding. This separates cadence from distillation effects. Fixed-budget guesses are not certified answers. Reference observations count toward total acquisition; separate their unique generation from per-policy accounting.

Small fixed-confidence diagnostic: first declared evaluation world of each stratum, same existing potential worlds, R16 (outside training R values), cap2048, checks every128. All policies use the independent Phase2d strict stopping gate with all unknown signs/types. Stop only on interval-certified crossing; at cap retain abstention and a separate scoring-only guess. These three reused worlds are diagnostics, not additional independent effectiveness evidence. No claim of eventual stopping, learner optimality or unconditional certified termination. Report false certified outputs/all, abstentions/all, cost and CPU for every declared path.

The first world of each stratum is selected by the deterministic public plan, before responses. All three have alpha0/M0 in that plan; changing R64→R16 therefore retains zero references. More generally this diagnostic code retains a world's original M rather than silently redrawing calibration for the new R. The three-world diagnostic does not cover all parameter/partition/calibration cells.

Qwen inference hard allowance600 requests shared across base+LoRA, including120-state offline comparison,24-world closed-loop comparison,three-world diagnostic and technical checks. Main expected requests240+192, diagnostic at most96, allowing a small technical margin. Single resident local model may switch adapter under a serialized interface; never change another service. Record cache/backend, cold-load and warmed inference cost separately. Stop visibly if budget or deadline is exhausted, retain all missing/failed denominators.

## Measurements and decision

All declared states/worlds retained. Report allocation L1/forwardKL, output validity/fallback, teacher rounding and information-deficit diagnostics; exact full-vector recovery, task/type/total acquisition, completion/abstention, wall/CPU/GPU/latency and model tokens. An information-deficit proxy using estimated state is distinct from evaluator-only true-parameter information; neither is a policy input. Uncertainty uses complete worlds as clusters, paired methods and exploratory95% intervals, no multiplicity-adjusted or confirmatory claim from eight worlds/stratum. Do not treat repeated states as independent samples.

GO only for further independent exploration if training improves policy behavior over the untrained model and offers an advantage not already obtained more cheaply by MLP, while audit/technical gates pass. REVISE for limited imitation, validity/generalization/cost tradeoffs or incomplete execution. NO-GO for LLM necessity if MLP matches/beats it with much lower cost. This is a bounded research disposition, not a paper-acceptance prediction. Freeze outcome interpretation and retain negative results, no post-hoc data selection.

Required outputs: `TRAINING_PROTOCOL.md`, `DATA_LEAKAGE_AUDIT.md`, `TRAINING_REPORT.md`, `QUERY_POLICY_EVALUATION.md`, `COMPUTATIONAL_COST.md`, `FINAL_DECISION.md`, configs, raw records, reproducibility instructions and final hash receipt. Independent native roles supply design/leakage/postrun checks; same-family reviews are not cross-model or formal verification. Stop at this pilot; any expansion needs a separate research decision.
