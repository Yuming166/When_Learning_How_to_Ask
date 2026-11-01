# T3 learnability audit

## Material Passport

Frozen historical inputs plus new TRAIN-only posterior simulations; no old private data or confirmation seeds opened.

Historical B32 WorstFact recovered 80/96; the requested-family **hindsight** oracle recovered 87/96 (headroom 7.292pp). This is a ceiling for full-policy selection, not a deployable action improvement. All14 frozen policies and T1b's four-macro interface were audited. See HISTORICAL_LEARNABILITY.json for all paired wins/losses and first-free observable associations.

New TRAIN feasibility gate: **PASS**. 192 repeated states from48 independent training worlds; candidate disagreement 1.000; mean posterior-rollout Q range 0.03265. Observable correlations: `{"remaining_budget": 0.1538163169394729, "mean_fact_entropy": 0.1493700453992064, "mean_type_entropy": 0.14159412660427184, "joint_map_probability": -0.1850182232388347, "posterior_rate_gap": -0.10609074544735628}`. These are exploratory associations with noisy numerical-model labels, not proof of heldout predictability. The weak gate authorizes only the one planned fit. Final learnability is assessed by independent TEST behavior below.

## Post-result qualification

The exploratory gate passed, but heldout decisions did not establish a material gain. A POSTHOC diagnostic using existing stored common-random-number samples found train/DEV split-half residual correlations0.085/0.117 and mean residual standard errors0.0268/0.0282. This diagnostic did not change weights, selection, thresholds or rollouts. See LABEL_NOISE_DIAGNOSTIC.json and RESEARCH_INTERPRETATION_CN.md. Weak-gate passage must not be described as demonstrated learnability.
