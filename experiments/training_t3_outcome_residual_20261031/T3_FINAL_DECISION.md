# T3 final research decision

## Material Passport

**NO-GO_FOR_WWW_ENHANCEMENT_THIS_PILOT**. Completed one authorized bounded pilot: 48 TRAIN,24 DEV,192 heldout TEST worlds;9 fixed lightweight neural fits with3 seeds per action mask. No Qwen, PPO, actor-critic escalation or confirmation was run.

The DEV-selected Joint recovered **154/192** atB32. WorstFact-MI recovered **151/192**; paired difference **+1.56pp**,95% interval **[-2.08, 5.21]**, wins/losses 8/5. The descriptively strongest TEST frozen reference was Rule-Switch, 157/192; difference -1.56pp. Its TEST ranking is descriptive and did not choose the model or primary comparator.

| Preregistered engineering/research gate | Result |
| --- | --- |
| at_least_5pp_vs_all_frozen | FAIL |
| positive_family7_paired_lower_vs_all | FAIL |
| no_observed_panel_deficit_worse_than_5pp | FAIL |
| joint_seed_range_at_most_5pp | PASS |
| no_joint_seed_below_WorstFact | PASS |
| worker_CPU_at_most_2x_WorstFact | FAIL |

Required five-part judgment:

1. **Statistical estimation:** selected Joint joint-Brier 0.2942, NLL 0.7154; WorstFact 0.3072/0.7478. These are allocation-induced descriptive changes using the same estimator, not a new estimator consistency theorem. Complete-recovery improvement must be judged by the paired intervals above.
2. **Online query cost:** no improvement demonstrated; every paired arm spends the same B. Higher fixed-budget accuracy, if any, would not establish equal-reliability savings.
3. **Total acquisition cost:** no improvement demonstrated; per world every arm spends B+2M, and training/DEV observations add development cost.
4. **Computation:** nine neural fits cost 1.873s CPU, but posterior-rollout labels and KL candidates dominate additional work. Selected Joint deploy workerCPU is 2.580x WorstFact; no overall speedup is assumed from network-forward timing alone.
5. **Certified stopping reliability:** unchanged gate, 0/4488 certified in this bounded run. Terminal likelihood includes all task/type/calibration observations. Non-certified fixed-budget guesses carry no delta-correctness claim; no improvement in general numerical certification or asymptotic optimality is established.

The training objective is terminal Bayesian recovery under frozen quadrature, not KL imitation. A single baseline state distribution, noisy K16 rollout labels and baseline-continuation/deployment mismatch limit one-step policy improvement. Exact simulation success cannot establish Natural/Web transfer or real source reliability. Preserve all seeds/checkpoints and negative findings. **Stop here: no automatic extra fitting, tuning or confirmation.** A future new experiment would need separate authorization and a new frozen protocol.

Chinese result interpretation: [RESEARCH_INTERPRETATION_CN.md](RESEARCH_INTERPRETATION_CN.md). Posthoc label diagnostics explain a possible limitation without changing this decision or launching more work.
