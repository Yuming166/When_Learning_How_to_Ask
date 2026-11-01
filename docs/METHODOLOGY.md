# Methodology implementation map

The primary implemented acquisition stack is QRelBench-Exact → joint inference/information allocation → a separate stopping rule. The natural-language interfaces and Web provenance model are distinct observation environments; their assumptions and result claims are not merged.

## Core stages

| Stage | Main implementation | Documents |
|---|---|---|
| Controlled environment and RPC boundary | [qrelbench](../experiments/qrelbench_v01_20261030/qrelbench) | [Protocol](../experiments/qrelbench_v01_20261030/PROTOCOL.md) |
| Unknown-rate coefficients and likelihood | [phase2a](../experiments/phase2a_theory_optimality_20261030/phase2a) | [Theory map](../experiments/phase2a_theory_optimality_20261030/THEORY_PHASE_MAP.md) |
| Information-aligned tracking | [phase2b](../experiments/phase2b_alignment_20261031/phase2b) | [Proof addendum](../experiments/phase2b_alignment_20261031/PROOF_ADDENDUM.md) |
| Strong decaying baseline | [phase2c](../experiments/phase2c_strong_baseline_20261031/phase2c) | [Baseline spec](../experiments/phase2c_strong_baseline_20261031/DECAYING_BASELINE_SPEC.md) |
| Type-action ablation and certified stop | [phase2d](../experiments/phase2d_method_improvement_20261031/phase2d) | [Stopping spec](../experiments/phase2d_method_improvement_20261031/CERTIFIED_STOPPING_SPEC.md), [version decision](../experiments/phase2d_method_improvement_20261031/METHOD_VERSION_DECISION.md) |
| Full evidence fusion and information policy | [phase2e](../experiments/phase2e_type_evidence_20261031/phase2e) | [Design](../experiments/phase2e_type_evidence_20261031/METHOD_DESIGN.md), [joint estimator](../experiments/phase2e_type_evidence_20261031/JOINT_ESTIMATOR.md), [final decision](../experiments/phase2e_type_evidence_20261031/FINAL_RESEARCH_DECISION.md) |

Phase2e is the latest bounded core-method development, with final status **REVISE**, not a confirmed default or an executable asymptotic-optimality result. Its quadrature posterior is distinguished from its exact small-instance reference. Greedy information gain does not by itself imply optimal stopping cost. All task, calibration and noisy type evidence must enter the correct likelihood. Endpoint certificates and query-cost efficiency are different claims.

## Learned policies and optimized controls

| Stage | Scope and retained decision |
|---|---|
| [T0](../experiments/training_t0_nqa_20261031/README.md) | Feasibility, state/action contracts and teacher/student protocol |
| [T1](../experiments/phase_t1_qwen4b_policy_20261031/FINAL_DECISION.md) | Qwen3.5-4B LoRA and MLP; current Qwen configuration NO-GO |
| [T1a](../experiments/training_t1a_solver_gate_20261031/README.md) | Numerical/solver baselines; frozen dependencies included as source |
| [T1b](../experiments/training_t1b_planning_value_20261031/README.md) | Finite-budget planning and belief-state interfaces |
| [T1c](../experiments/training_t1c_fresh_ig_audit_20261031/README.md) | Fresh-information and objective controls |
| [T1d](../experiments/training_t1d_nonuniform_robustness_20261031/FINAL_DECISION.md) | Nonuniform allocation and robustness controls |
| [T2 failed initial attempt](../experiments/phase_t2_structure_allocator_20261031/ATTEMPT_STATUS.md) | Retained preparation failure; not silently replaced |
| [T2 v02](../experiments/phase_t2_structure_allocator_v02_20261031/FINAL_DECISION.md) | DeepSets amortization; computational/query-cost tradeoff; REVISE |
| [T2b](../experiments/phase_t2b_failure_hybrid_20261031/FINAL_DECISION.md) | AnalyticReuse, risk/periodic hybrids and complete CPU accounting |
| [T3](../experiments/training_t3_outcome_residual_20261031/T3_FINAL_DECISION.md) | Outcome-aligned residual-policy pilot; NO-GO for current WWW enhancement |

These are preserved research implementations, not an instruction to train them. T1/T2 need optional PyTorch/transformers/PEFT components and omitted model/checkpoint files; consult their original requirements/protocol/runtime records. No new training dependencies are installed by the core checks. T3's NumPy contract tests can be requested separately:

```bash
python scripts/run_public_checks.py --stage training_t3_outcome_residual_20261031
```

A supported public test target only exercises existing engineering fixtures. It does not open a held-out scientific test split, run a confirmation batch, or reproduce a historical trained model without its weights.

## Reproduction boundaries

Published code resolves core sibling packages relative to the repository. Six training runtime files have documented import-path repairs. Frozen source copies remain identifiable in stage/vendor directories; their original scientific receipts are not reissued as if the path repair had been part of the original run.

Private seeds, training rows, raw answers/trajectories, weights and downloaded datasets remain outside this release. See [PUBLICATION.md](../PUBLICATION.md) before invoking any freeze/runner/evaluation command. A new seed or fresh run is a new experiment, not a historical replay.
