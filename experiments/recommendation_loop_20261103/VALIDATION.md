## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-11-03
- Verification Status: ANALYZED; raw responses, policy actions and terminal certificates replayed
- Version Label: recommendation_loop_validation_v1

## Validation Report

Source: the frozen 40-trajectory pilot and separately frozen eight-trajectory
post-hoc IG repair. Overall confidence: **CAUTION for effectiveness inference**.
The observable implementation works on these controlled fixtures. This is not
a population-level superiority or equivalence result.

| Finding | Descriptive value | Interpretation boundary |
|---|---:|---|
| Decision KL vs Joint D-RRC | 243 vs 341.375 mean queries; 7/8 cheaper | Four constructed profile clusters; no population CI or test |
| Decision KL vs Profile KL allocation | 243 vs 353.125; 7/8 cheaper | Shared recommendation stopping; allocation-goal ablation only |
| Decision KL vs repaired Decision IG | 243 vs 237.5; 2/8 cheaper | No advantage over the strongest tested baseline established |
| Wrong certified recommendations | 0/40 primary; 0/8 repair | Does not empirically establish the analytic error bound |
| R=3 model guarantee | exp(-3)≈0.049787 | Conditional on the fixed iid channel and numerical contract |

No p-values, confidence intervals, standardized population effect sizes or
equivalence tests are reported. Raw differences and paired vectors are retained.
Treat each partition as a repeated constructed profile, not an independent user.

## Fallacy scan: 11/11 checked

| Type | Status | Assessment |
|---|---|---|
| Simpson's paradox | Checked | KL exceeds repaired IG cost overall and within each catalogue mean; no catalogue-level sign reversal for this contrast. Individual worlds remain visible. Other subgroup ranks can vary; no uniform ranking is claimed. |
| Ecological fallacy | Bounded | Eight environments are not eight independent users; no individual human inference from means. |
| Berkson's paradox / selection | CAUTION | Half the worlds are hand-constructed theory anchors; this is not a representative recommendation sample. No selection based on arm outcomes. |
| Collider bias | Not introduced in analysis | No conditioning on success, certificate speed, estimation quality or an outcome-dependent inclusion filter. All attempted paths remain. |
| Base-rate neglect | Bounded | No diagnostic precision claim or unobserved user preference prevalence; catalogue winner coverage is disclosed. |
| Regression to mean | Not a pre/post efficacy claim | The repaired IG is a numerical-rule intervention on all eight original worlds, not improvement of a selected worst subset. No regression-based explanation or new generalization evidence is inferred. |
| Survivorship bias | Checked | Main 40/40 and repair 8/8 reported. Caps/failures are predeclared statuses, retained and separately counted. Smoke runs remain separate. |
| Look-elsewhere effect | CAUTION | All five initial arms and the repair are shown; no significant-only reporting. No significance tests performed. Eight worlds cannot support a broad winner claim. |
| Garden of forking paths | CAUTION, disclosed | Main sources/config frozen before outcomes. IG tie repair and final synthesis are explicitly post-hoc; they reuse the development worlds and do not count as confirmation. |
| Correlation vs causation | Bounded | Profile/Decision KL share controls for a specific allocation contrast in the simulator; KL vs IG also changes inference and update behavior. No causal explanation for finite-sample differences or human behavior is claimed. |
| Reverse causality | Not the design | Actions precede fresh responses; no future answer or truth reaches selection. No observational directional-effect claim is made. |

## Numerical and reproducibility scope

There are 43 passing component/integration tests. All 48 retained efficacy-stage
histories have deterministic raw-answer replay, non-future policy-action replay
and terminal interval-certificate rechecking. The main and repair freezes remain
unchanged. This verifies recorded trajectories without collecting new answers.
It is **not** a fresh full experimental re-run, proof-assistant validation,
certified quadrature error bound or a cross-family review.

Only the zero-sample preparation path of `reproduce_in_copy.py` is exercised in
this turn. The optional fresh-directory end-to-end reproduction entry point is
provided, but its full 48 trajectories are not rerun here. Reproducibility verdict:
**PARTIALLY_REPRODUCIBLE**, with exact deterministic history replay checked and
fresh execution of the reproduction wrapper still unverified.

CPU logs are host-specific and include initialization/caching effects. Policy
and gate costs are separate in the machine-readable results. Query savings
relative to a simple arm do not imply lower CPU or total deployment cost.
