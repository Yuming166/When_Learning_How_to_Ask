# Phase 2e: bounded type/evidence fusion development

Status: **COMPLETE, REVISE**. New development only; no confirmation or model calls.
Branch: `phase2e_type_evidence_fusion`, isolated worktree rooted at
`/home/gaoym/When_Learning_How_to_Ask_phase2e`.

The eight requested deliverables are:

- [Method design](METHOD_DESIGN.md)
- [Joint estimator](JOINT_ESTIMATOR.md)
- [Allocation design](ALLOCATION_DESIGN.md)
- [Fair ablation report](FAIR_ABLATION_REPORT.md)
- [Certified evaluation](CERTIFIED_EVALUATION.md)
- [Computational cost](COMPUTATIONAL_COST_REPORT.md)
- [Integration interface](INTEGRATION_INTERFACE.md)
- [Final research decision](FINAL_RESEARCH_DECISION.md)

The pre-outcome [protocol](DEVELOPMENT_PROTOCOL.md), config.json, freeze.json,
SOURCE_SNAPSHOT.json and FIXTURE_SNAPSHOT.json identify the scientific run.
VALIDATION.json identifies the checks. The final receipt binds the artifacts.
All checks were performed in the producing context; this is not a claim of an
independent reviewer or formal verification.

Raw local outputs remain under artifacts/: trajectories.jsonl, snapshots.jsonl,
execution.json and analysis/. Evaluator-only reproduction/seed records remain
under artifacts/private/ with a protected directory. Generated data, caches and
logs are excluded from Git. Historical source, results and confirmation files were not edited;
read-only source/spec/audit and validation dependencies were snapshotted for reproducibility.
Historical source and artifact preservation checks are in audit/HISTORY_CHECK.json.

The runner refuses an existing output directory. Do not delete raw output to
rerun it. Report and numerical-analysis scripts read existing observations and
perform no acquisition. The frozen method files and protocol have not changed
after seed creation; later audit scripts are explicitly post-run analysis.

Main census:32 independent worlds,288 paths,287 strict certifications,
1 cap non-certification,0 wrong certified outputs,349056 online actions and
117504 policy-accounted offline observations. Shared unique offline samples:
13056. The exact model/scope restrictions are essential; Natural fixtures test
normalization and rejection only.
