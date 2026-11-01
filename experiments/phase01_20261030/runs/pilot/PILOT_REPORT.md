## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-10-30
- Verification Status: ANALYZED
- Version Label: phase01_v1

# Pilot Report

**Decision: REVISE_OR_NO_GO.**

Coverage: 3264/3264 attempted; 3264 valid. Invalid/error/unattempted task outputs score zero.

## Held-out reliability (not equal-cost agent performance)

| Strategy | Accuracy | Profile bootstrap 95% interval |
|---|---:|---:|
| Fixed_A | 49.74% | [44.53, 54.69] |
| Fixed_B | 55.21% | [50.26, 60.42] |
| Round_Robin | 54.17% | [49.74, 58.59] |
| LOPO_Global_Format_Audit_Reference | 55.21% | [50.26, 60.42] |
| Observation_Only_Agreement | 52.08% | [47.66, 55.99] |
| Labelled_Calibration_Oracle | 53.12% | [47.66, 57.81] |
| Hindsight_Oracle_Reference | 63.80% | [61.20, 66.93] |
| Direct_Type_Query | 51.82% | [46.88, 56.77] |
| Public_Metadata_Predictor | 52.08% | [46.88, 56.77] |
| Shuffled_Group_Audit_Control | 51.24% | [47.28, 54.59] |

## Prespecified discovery gates

Intervals below use Bonferroni 99% marginal intervals for five primary endpoints (95% family coverage target).
Profile bootstrap remains approximate with 24 clusters.

| Endpoint | Estimate | Interval | Pass |
|---|---:|---:|---|
| replicated_gap_product | 0.0047 | [-0.0046, 0.0151] | False |
| labelled_transfer_minus_shuffled | 0.0188 | [-0.0177, 0.0569] | False |
| agreement_minus_global_reference | -0.0312 | [-0.1120, 0.0443] | False |
| agreement_minus_direct | 0.0026 | [-0.0807, 0.0781] | False |
| agreement_minus_metadata | 0.0000 | [-0.0807, 0.0807] | False |

## Interpretation boundaries

Both preferences and paraphrases are held out in the transfer analysis. The observation-only selector receives no correct answers or policy cards. Labelled-calibration and hindsight oracles are audit references. Hindsight chooses on the evaluation observations and is optimistically biased. Direct and metadata format reports have two independent prompt variants; variant 0 is prespecified primary. Tied held-out group labels are explicitly retained.

There is no Phase 2 agent, training, 35B generation, confirmation set, or human study in this run. These 24 profiles are development data. Failure of the conservative discovery gate does not refute the mathematical theorems. The heterogeneous utility/priority tasks do not automatically satisfy common p,q or the iid channel model.

## Statistical fallacy scan (11/11 assessed)

| Risk | Disposition |
|---|---|
| Simpson | Aggregate and every group gap retained in group_diagnostics.jsonl. |
| Ecological | Inference limited to simulated profiles; no human/individual generalization. |
| Berkson | No performance-based profile filtering. |
| Collider | No outcome-conditioned adjustment or subgroup selection. |
| Base rate | Binary answer mapping balanced; all invalid/missing counts retained. |
| Regression to mean | Discovery and validation use distinct observations and preferences. |
| Survivorship | Full planned denominators; incomplete collection blocks scientific decision. |
| Look-elsewhere | Five primary endpoints and all baselines retained, including negative outcomes. |
| Forking paths | Protocol/source/data hashes frozen before smoke; no adaptive template search. |
| Causality | No mechanism/causal attribution from the observed gaps. |
| Reverse causality | All selectors use prespecified prefix or independent reports. |

See analysis.json for type-report counts, repeated-error audit, costs and all gates; failure_examples.jsonl contains the first 12 failures in request-ID order.
