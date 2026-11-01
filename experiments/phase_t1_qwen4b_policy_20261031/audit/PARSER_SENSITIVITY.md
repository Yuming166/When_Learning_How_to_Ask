# POST-HOC parser sensitivity of existing T1 offline outputs

This outcome-informed diagnostic was requested after observing the frozen parser's failures. It does not replace the frozen primary results. All 120 states per method remain in every overall denominator; each stratum contains 40 states from eight worlds, with five fixed positions per world.

The diagnostic reparses each saved Qwen raw string. It retains the JSON array, length 10, integer range 0–100, nonnegativity, and complete action-mask checks. Only exact total 100 is relaxed to any positive total, followed by normalization. Every other failure keeps the same uniform legal fallback. MLP weights remain unchanged. Only continuous allocation L1 and the frozen smoothed forward KL are compared; no teacher percentage labels are regenerated or evaluated.

## All-state results

| Method | Strict valid / 120 | Diagnostic valid / 120 | L1 strict → diagnostic | KL strict → diagnostic |
| --- | ---: | ---: | ---: | ---: |
| MLP | 120 | 120 | 0.450552 → 0.450552 | 0.389262 → 0.389262 |
| BaseQwen | 4 | 82 | 0.959545 → 1.017756 | 0.765134 → 0.977269 |
| LoRA | 67 | 120 | 1.031311 → 0.999698 | 5.566640 → 7.825043 |

## Full raw-contract audit

- BaseQwen: 78 outputs recovered solely by sum normalization; 38 retain fallback. Raw mask violations: 38, including 33 simultaneous sum violations. Raw sum histogram: `{"100": 9, "140": 1, "150": 15, "151": 1, "157": 1, "160": 39, "172": 3, "180": 1, "196": 1, "200": 1, "220": 1, "228": 4, "234": 2, "296": 1, "300": 10, "332": 1, "350": 3, "410": 1, "500": 25}`.
- LoRA: 53 outputs recovered solely by sum normalization; 0 retain fallback. Raw mask violations: 0, including 0 simultaneous sum violations. Raw sum histogram: `{"99": 53, "100": 67}`.

Saved parser errors report only the first failed check. In particular, a sum error does not establish that the mask was correct. The diagnostic independently rechecks every raw mask position.

## Stratum results

| Stratum | Method | Strict → diagnostic valid / 40 | L1 strict → diagnostic | KL strict → diagnostic |
| --- | --- | ---: | ---: | ---: |
| id_test | MLP | 40 → 40 | 0.359244 → 0.359244 | 0.285283 → 0.285283 |
| id_test | BaseQwen | 0 → 20 | 0.991869 → 1.101330 | 0.671133 → 0.904909 |
| id_test | LoRA | 28 → 40 | 0.972884 → 0.906086 | 6.157121 → 7.323064 |
| ood_parameters | MLP | 40 → 40 | 0.346842 → 0.346842 | 0.250511 → 0.250511 |
| ood_parameters | BaseQwen | 2 → 22 | 1.031017 → 1.015378 | 1.095084 → 1.159317 |
| ood_parameters | LoRA | 28 → 40 | 1.209343 → 1.354835 | 8.090437 → 11.194214 |
| ood_partition | MLP | 40 → 40 | 0.645569 → 0.645569 | 0.631991 → 0.631991 |
| ood_partition | BaseQwen | 2 → 40 | 0.855750 → 0.936561 | 0.529185 → 0.867580 |
| ood_partition | LoRA | 11 → 40 | 0.911706 → 0.738175 | 2.452361 → 4.957851 |

The JSON artifact retains all 360 row-level records, 72 method/world means, and paired world vectors for BaseQwen−LoRA, MLP−LoRA, and BaseQwen−MLP, separately by stratum and overall. These are descriptive summaries of the fixed heterogeneous grid, with no new bootstrap or calibrated population interval.

## Interpretation and limits

This comparison separates sensitivity to the exact-sum interface rule from the allocation content in these saved outputs. It does not establish the performance of a normalized-output policy in closed loop: changing an early allocation would change later observations and prompts. Query cost, recovery accuracy, and certified stopping for that counterfactual policy are therefore unmeasured.

The initial BaseQwen prompt specified the legal input/output allocation interface but did not supply an objective-aware explanation of the teacher's KL design criterion or worked allocation examples. This limits conclusions about pretrained Qwen's best achievable planning ability. The saved base-model initialization and the trained adapter remain the actual comparisons; this diagnostic does not create a new objective-aware baseline or tune a prompt after outcomes.

The primary parser/policy, trained weights, experimental configuration, and report sources were not edited. No model inference, worlds, queries, private provenance, or new labels were used. A later proposal to normalize outputs would require a separate frozen evaluation and cannot inherit the current closed-loop claims.

## Reproduction and provenance

Run `PYTHONDONTWRITEBYTECODE=1 /storage/gaoym/wcl_v100_venv/bin/python audit/parser_sensitivity.py` from the T1 experiment directory. The script refuses to overwrite outputs. Input files and the diagnostic source are SHA-256 bound in the JSON artifact.

- [Complete diagnostic JSON](../artifacts/diagnostics/parser_sensitivity.json)
- [Diagnostic source](parser_sensitivity.py)
- Diagnostic JSON SHA-256: `4c1ef5aa736635619dab13db34eb31043f82f7ce2b3cab090ae9f8f884c8347d`
