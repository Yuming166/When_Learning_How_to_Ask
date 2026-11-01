# Independent public-log post-run review

## Material Passport and decision

- Scope: read-only review of public execution/trajectory/snapshot logs, analysis JSON, the English pilot report, Chinese research decision, public validation receipt, and frozen hashes. Write only this new file.
- Independence: a separately dispatched same-family agent recomputed the summaries using inline standard-library Python, without importing the experiment's runner, analysis, or integrity implementations.
- Restrictions observed: no seed/private reproduction files were opened; no experiment, replay, model, API, or GPU call was executed; no frozen audit, implementation, historical file, or report was edited.
- **Decision: PASS for the completed bounded development result and its current reporting. No material reporting blocker found. Stop this phase; independent confirmation and asymptotic-optimality claims remain unauthorized/unestablished.**
- This audit checks consistency of public logs and reports. Public `exact`/`correct_facts` values inherit the trusted evaluator's correctness judgement. Public snapshot rows do not retain raw count arrays, so this review does not independently reconstruct task answers or catalog truth. The separate evaluator/validation/replay receipt has that scope.

## Full denominators and acquisition costs

All 792 expected policy/job identities were reconstructed directly from the frozen config and compared as multisets with the trajectory log: no missing or duplicated trajectory. Each of the six policies has 132 trajectories. The 528 fixed-budget trajectories each have all seven planned endpoints, giving 3,696 budget snapshots. There are 264 fixed-confidence trajectories and 13,157 total snapshots, including sequential checks.

| Item | Independently recomputed main-batch value |
| --- | ---: |
| Task actions | 283,825 |
| Direct type actions | 2,719 |
| Online actions | 286,544 |
| Offline calibration observations | 26,208 |
| Total acquisition, online + offline | 312,752 |
| Recorded main wall time | 400.95296326000243 seconds |

Every trajectory satisfies online=task+type, offline=2M, total acquisition=online+offline, and online<=cap. These sums agree exactly with `execution.json`, `facts.json`, and the public validation receipt. The run completed all planned trajectories, with error=null, retries=0, and reported model calls=0/confirmation=false. The main action count is below the frozen 626,688 maximum and 650,000 hard action cap; endpoint count and wall time fit the frozen limits.

The validation receipt separately reports 2,720 replayed online actions and zero replayed offline observations for eight existing trajectories. They are excluded from the main-batch efficacy denominators. Main plus those recorded replays totals 315,472 acquisition actions/observations. Earlier smoke/preflight work is separately scoped; this is not a claim to have reconstructed every prior-session CPU operation.

## Analysis consistency

Independent recomputation matched all **504 fixed-budget cells**, **138 confidence cells**, and **420 paired comparison means and paired sample counts**. Fixed-budget exact-recovery fractions, mean task/type/total costs, all cell Wilson intervals, all completion-curve points, wrong-certification fractions, restricted means, and conditional completed-cost quantiles agree with the saved analysis JSON.

For every fixed-confidence trajectory, the public `complete` flag agrees with the strict numerical stopping margin. An incomplete trajectory ends at its declared cap and remains censored. Wrong-certification incidence uses completed-and-incorrect divided by all trajectories in the cell, rather than only completions. All paths remain in mean min(T,B); completed-cost quantiles are explicitly conditional. Oracle known-type flags occur only for the Oracle policy. All recorded workers report the reviewed single-threaded Landlock bootstrap.

Planner, endpoint-decoding, and GLR CPU totals match the trajectory sums: 118.83264775108546, 191.3862549723126, and 10.362945245578885 seconds. The 1,148 tracker allocation updates also match the public histories. These computational costs remain distinct from query counts.

## Independently checked headline results

At d=16,B=256, RR and RRC recover 8/8 in every primary partition/alpha cell. Tracking recovers 7/8 for [1,15], [2,14], and [16], and 8/8 for [4,12] and [8,8], for both alpha=0 and alpha=3. The reports correctly retain this negative finite-budget comparison. The ten cells reuse eight profile indices; they are not 80 independent profiles.

At the predeclared medium-rate B=256 setting (.75,.60), Tracking and RRC each recover 1/4, while Direct and Oracle each recover 4/4; RR and ETC recover 0/4. At the weak (.60,.55) setting, all six policies, including Oracle, recover 0/4. The Chinese report accurately describes this floor effect and does not infer method ranking from it.

The primary d=4 fixed-confidence summaries below are descriptive averages across six partition/alpha configurations. **Each policy/R has 12 paths but only two independent profile indices.** RR, RRC, Tracking, and Oracle complete all those paths; ETC and Direct each complete 8/12 at every R, with four capped paths retained in restricted costs.

| R | RR mean min(T,2048) | RRC | Tracking | Oracle |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 314.6667 | 282.6667 | 253.3333 | 104.0000 |
| 16 | 465.3333 | 416.0000 | 329.3333 | 156.0000 |
| 64 | 952.0000 | 850.6667 | 610.6667 | 364.0000 |

The reported R=64 observation, Tracking 610.7 versus RRC 850.7, is numerically correct. Its exploratory label and two-profile caveat are necessary and present. It supplies no significance, generalization, superiority, or coefficient-convergence conclusion.

## Censoring and negative controls

| Scope/scenario | All trajectories | Completed | Censored | Wrong completed certificates / all |
| --- | ---: | ---: | ---: | ---: |
| All in-model confidence runs | 240 | 209 | 31 | 0/240 |
| q=.5 iid boundary subset | 12 | 9 | 3 | 0/12 |
| Label-asymmetric control | 12 | 10 | 2 | 10/12 |
| Persistent-error control | 12 | 11 | 1 | 3/12 |
| All out-of-model controls | 24 | 21 | 3 | 13/24 |

The in-model aggregate includes the q=.5 boundary and d=6/d=8 technical probes. The reports correctly classify q=.5 as in-model and the latter two channels as outside the iid symmetric model. No capped path is counted as a successful certificate. Zero observed in-model errors is not an empirical verification of tiny delta-correctness; out-of-model errors are not counterexamples to the original model theorem.

## Theory and claim limits

The Chinese headline values agree with the saved theoretical coefficient artifact: critical alpha for [8,8] is 2.0431602469281347. At alpha=3 with known-s=.8 type actions, [4,12] has K=14.56163829340373 versus oracle K=14.275193658449814, a 2.0065901858% premium. [8,8] has K=14.275193672923091, numerically equal to the oracle at the stated solver precision. These were checked against the saved coefficient artifact; no new optimizer was run for this review.

Both final reports preserve the required boundaries: theoretical coefficients differ from observed restricted cost; the d=16 phase transition is not empirically verified; no asymptotic convergence or proved optimal implementation is claimed; the actual tracker remains an implementation variant of the original achievability construction; float64 GLR arithmetic has no rigorous interval rounding certificate; d=16 receives terminal decoding only; historical v0.1 accuracy is not directly comparable under the changed decoder/calibration; no real-LLM reliability or confirmation claim is made.

The public validation receipt records eight exact existing-trajectory replays and 176 unchanged historical receipt-bound files. This reviewer checked that receipt's consistency with the public main totals, but did not independently reexecute replays or re-audit those 176 historical files. Frozen source/config/test hashes (16 entries), frozen audit hashes (7 entries), and reused v0.1 source hashes (10 entries) were independently rehashed and matched their commitments.

## Public artifact bindings

| Artifact | SHA-256 |
| --- | --- |
| `config.json` | `3bcfa08d9fcffcd790b889345687550394f43b0db792a1f7ac7bf1db972d4c24` |
| `PROTOCOL.md` | `bae829e594a420f3f4d31037416e86c9404721fbc261f11f343c17bf52cfec8b` |
| `freeze.json` | `d95bcb0dc8263e7fc74d5529c0803e94a999d26db76a95da2e03b243f0c4b368` |
| `artifacts/run/execution.json` | `024ec70df20e3ab8bce51c66ca4457c92eeae90fd475a7ac5c60aeef4891fd07` |
| `artifacts/run/trajectories.jsonl` | `11fda7dc3f9270236ab4c04cd15673cec195545033c131fb850c309ee69d38d1` |
| `artifacts/run/snapshots.jsonl` | `8defa2b0132f6d94731bcaa55316c16b8ee41debe3e2205427260b58f7a075d2` |
| `artifacts/analysis/facts.json` | `98afe782e82c1de14bc91a4bad53042e731ca9966fc87f8ade97a5ecf7f8c6ae` |
| `artifacts/analysis/budget.json` | `691deeb32d7532fd3ea26b0e2ecefa2c2abc45b6221893fd396405b71d9a9ec1` |
| `artifacts/analysis/confidence.json` | `bcc791bc24c2d1025a0408960337a7a433778302647aa5055b6fecfa4ef8aa3a` |
| `artifacts/analysis/paired.json` | `6dc5220801edd01ac41a85eeff17c8a1b1a4d6625b4c28aab9d3a720f938b29a` |
| `artifacts/theory/phase_map.json` | `e84ddf202c6ff1635c9dd9951cd148abea1aad0c9e61fa09c2bbb4ea5605310d` |
| `PILOT_REPORT.md` | `8e2444d6a0177907c5b9248ffcf47d487b88adf895d4974b2a443de28c06e410` |
| `RESEARCH_DECISION_CN.md` | `a76280e6398a707b2fbcff3e1a166bba06437e92820ed50f3111b71d9aacb906` |
| `VALIDATION.json` | `5168ad86e7f447c982f3ec53a23a92823581c614a47ad9d05975fec38cb015bf` |
