## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: Phase 0 audit
- Origin Date: 2026-10-30
- Verification Status: source inspected; historical statistics unverified
- Version Label: phase01_v1

# Phase 0 research and environment audit

## Repository and V5 evidence

Cloned `https://github.com/Yuming166/When_Learning_How_to_Ask` at commit `3186587a5eb1aa4abc02c43d2ebb1e5f2ce050c3`. The original tree contains README.md, Theory_Note.md (31,711 bytes), and a two-page V5 Chinese brief (110,231 bytes). No original experiment scripts, datasets, item-level outputs, sample counts per reported percentage, uncertainty records, decoding settings or numerical certificate files are in the original tree. New work lives solely in `experiments/phase01_20261030/` on an isolated branch. Historical files and original remote refs are preserved.

| Historical statement | What can be checked now | Standing |
|---|---|---|
| Synthetic 23.67 / 14.00 / 48.33% eight-preference exact accuracy | Present in the brief; it explicitly sets .75/.50 Bernoulli rates | Reported, not reproduced |
| Qwen transfer 73.22 -> 93.05% | Present; described as average per-answer probability, based on Qwen answer probabilities | Reported, not direct independent generation evidence |
| Adaptive 82.37, RR 83.36, Direct 88.72, Oracle 89.72% | Present; total 32-query task, direct question counted | Reported; Adaptive does not beat RR or Direct |
| 10,800 synthetic trajectories and 24 development + 24 new cards per scenario | Stated in brief; underlying records absent | Not independently countable |
| Theory numerical checks / coefficient files | Named in note but files absent | Not reproduced |

The brief does not reveal enough to verify whether every Qwen trajectory used fresh generation rather than a cached probability model, or whether source information was equally available across formats. It explicitly uses source identification (text rules versus already computed results) and notes persistent errors in dialogues. These are risks to investigate, not established misconduct or a diagnosis of the missing code. Do not relabel cached-probability simulations as fresh Qwen conversations.

## Theory-to-pilot contract

The note studies fixed binary signs, a known partition, shared good-format identities, globally common unknown p,q with 1/2 <= q < p <= 1-eta, fresh responses, and explicitly labelled offline reference streams. The oracle knows z only and shares the same reference data. Theorems concern pointwise leading query cost as delta -> 0, not short-budget accuracy. The note explicitly states its proofs have not received independent review.

| Theoretical condition | Pilot status |
|---|---|
| Known groups, binary decisions | Built into deterministic construction |
| Group-shared better format | Empirical hypothesis, not a generator input |
| Common unknown p,q across groups/items | Unverified and likely approximate; heterogeneity reported |
| Both formats >= chance | Not guaranteed; must inspect actual correctness |
| Fresh independent observations | Fresh RNG seeds and contexts/cache per call; systematic item errors remain possible |
| Labelled high/low offline reference streams | Not supplied; diagnostic calibration labels are audit-only and not that assumption |
| Known direct-report reliability s_g | Not supplied; self-report reliability is measured, never presumed known |
| Uniform delta-correct recovery / asymptotic optimum | Outside Phase 1; no theorem validation from finite accuracies |

Important boundaries already stated in the note: with no external calibration (alpha=0), zero leading premium requires full sharing G=1; do not add independent single-group coefficients when p,q are globally unknown. A perfect type question removes the leading premium at cost at most G. Known-answer checks are not automatically equivalent to type queries. The exact information program, likelihood stopping rule and theory numerical claims remain separate from this behavioral pilot. No proof audit or novelty certification has been completed.

## Live environment

Host: cloud82. Local resource snapshot: 56 CPU threads, ~503 GiB RAM, ~143 GiB free on /home volume; GPU 0–2 V100 32GB idle, GPU 3–5 RTX4090 ~23GB idle, GPU6 RTX4090 serving an existing process (~20GB used). Snapshot can drift; check before allocation. Do not stop or reconfigure another service.

Live `/v1/models` checks, bypassing external proxies:

- 10.63.0.88:31519: **Qwen3.6-35B-A3B**, vLLM, model root Qwen3.6-35B-A3B-FP8, max_model_len 262144. No generation sent.
- cloud82 localhost:31519: **Hy-MT2-7B**, vLLM, translation model, max_model_len 65536. Not a substitute for Qwen.
- No existing 4B listener identified on 82. Local checkpoint `/storage/lianjh/modelzoos/Qwen/Qwen3.5-4B` and installed environment `/storage/gaoym/wcl_v100_venv/bin/python` are available. Actual torch 2.6.0+cu124, transformers 5.17.0; Qwen3_5ForConditionalGeneration import and CUDA availability checked. No installation/download needed.

Use existing local checkpoint in a separate offline inference process on idle GPU3, float32/TF32 disabled/SDPA, sequential fresh requests. This is explicitly a new experimental inference process using cached weights, not the prior vLLM deployment. Checkpoint/tokenizer hashes and actual model class/parameter count are recorded at runtime. Do not infer historical V5 decoding or model identity from this new backend. 35B max concurrency/remote GPU resource and decoding defaults remain **unverified**, since 35B generation is outside scope. Local source suggests service support for 32 sequences on the translation server only; that is not a Qwen budget.

## Implementation and execution plan

1. Deterministic source-equivalent preference cards; held-out wording and preferences; construction/metamorphic/leakage checks.
2. Freeze source, protocol, seeds and both datasets before any smoke sampling.
3. Run 80-generation technical smoke. Gate only on execution, identity and parsing, never on a favorable format gap.
4. If technical gate passes, run 3,264-generation bounded development pilot. No profile filtering, retries, hidden labels to selector, or format/template search.
5. Analyze with profile-cluster bootstrap, shuffled groups, all six required baselines and audit-only oracle references. Return full denominators, failures, data/setting hashes and GO / REVISE / NO-GO. Stop before Phase 2 or further model calls.

## Time and submission

Official dates checked at https://www2027.thewebconf.org/important-dates/: short-paper abstract 9 November 2026, paper 16 November 2026, end of day AoE. Thus “about 10 days” matches the abstract checkpoint, not the paper deadline. Do not make deadline-dependent scientific claims or skip an independent confirmation split to meet that checkpoint.
