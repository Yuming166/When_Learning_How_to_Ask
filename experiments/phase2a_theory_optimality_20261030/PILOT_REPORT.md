# Phase 2a bounded development report

**Decision: mathematical/numerical implementation GO; empirical asymptotic optimality NOT ESTABLISHED.**

Completed 792 development trajectories, 286544 online actions, 26208 offline observations, and zero model calls. No independent confirmation set was generated.

## Theoretical coefficients and scope

See [THEORY_PHASE_MAP.md](THEORY_PHASE_MAP.md). The analytic critical alpha for [8,8] is 2.0431602469. The K solver uses the full joint continuous-rate program, without using the Gamma zero-premium shortcut. Independent SLSQP and full alternative enumeration checks are recorded in audit/COEFFICIENT_REVIEW.md. Float64 optimization bounds are numerical, not interval or rational proofs.

## Fixed-budget recovery

All six samplers use the same full-observation joint profile-MLE terminal decoder. Oracle knows group types only, and must still infer signs and rates. Every type query consumes one online action. Calibration is charged as 2M separately. These decoder and calibration settings differ from v0.1; do not compare historical accuracy percentages directly.

|Partition|alpha|n per policy|RR @256|RRC @256|ETC @256|Direct @256|Oracle @256|Tracking @256|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|[1, 15]|0|8|8/8|8/8|7/8|5/8|8/8|7/8|
|[1, 15]|3|8|8/8|8/8|7/8|5/8|8/8|7/8|
|[2, 14]|0|8|8/8|8/8|7/8|5/8|8/8|7/8|
|[2, 14]|3|8|8/8|8/8|7/8|5/8|8/8|7/8|
|[4, 12]|0|8|8/8|8/8|7/8|5/8|8/8|8/8|
|[4, 12]|3|8|8/8|8/8|7/8|5/8|8/8|8/8|
|[8, 8]|0|8|8/8|8/8|7/8|5/8|8/8|8/8|
|[8, 8]|3|8|8/8|8/8|7/8|5/8|8/8|8/8|
|[16]|0|8|8/8|8/8|8/8|8/8|8/8|7/8|
|[16]|3|8|8/8|8/8|8/8|8/8|8/8|7/8|

The full seven-budget curves and cell-wise Wilson intervals are in artifacts/analysis/budget.json and budget_curves.pdf. Paired episode bootstrap differences are exploratory (n=8 primary, n=4 rate coverage), with no multiplicity correction. Reused episode indices across partitions/alphas do not create independent profiles. No superiority claim is made.

## Confidence stopping and censoring

Under the iid model: 209/240 completed, 31 censored, 0 wrong certifications. Outside the iid model: 21/24 completed, 3 censored, 13 wrong certifications. q=1/2 remains in-model; persistent and label-asymmetric controls do not.

|R|Policy|Completed / all|Censored|Wrong certified / all|Mean min(T,2048)|
|---:|---|---:|---:|---:|---:|
|4|Round-Robin|12/12|0|0/12|314.7|
|4|Repeat-and-Compare|12/12|0|0/12|282.7|
|4|Explore-Then-Commit|8/12|4|0/12|852.0|
|4|Direct Type Query|8/12|4|0/12|820.0|
|4|Oracle Format|12/12|0|0/12|104.0|
|4|Information Tracking|12/12|0|0/12|253.3|
|16|Round-Robin|12/12|0|0/12|465.3|
|16|Repeat-and-Compare|12/12|0|0/12|416.0|
|16|Explore-Then-Commit|8/12|4|0/12|921.3|
|16|Direct Type Query|8/12|4|0/12|904.0|
|16|Oracle Format|12/12|0|0/12|156.0|
|16|Information Tracking|12/12|0|0/12|329.3|
|64|Round-Robin|12/12|0|0/12|952.0|
|64|Repeat-and-Compare|12/12|0|0/12|850.7|
|64|Explore-Then-Commit|8/12|4|0/12|1185.3|
|64|Direct Type Query|8/12|4|0/12|1172.0|
|64|Oracle Format|12/12|0|0/12|364.0|
|64|Information Tracking|12/12|0|0/12|610.7|

The primary confidence design has only two independent profile indices, reused across partitions and alpha. Confidence JSON retains every cell and negative control. The plots show completion, cumulative wrong certifications divided by all paths, restricted mean cost, and costs conditional on completion. Censored means are not E[T]. Zero observed errors cannot establish delta-correctness.

The GLR enumerates all discrete alternatives and profiles continuous rates analytically for d<=8. Its mathematical optimization is exact, its arithmetic is float64 with interval_certified=false. A numerical stopping margin does not supply a rigorous rounding certificate. d=16 receives only fixed-budget terminal decoding; no sequential d=16 GLR was run.

## Observable tracking and computation

Information Tracking made 1148 allocation updates. Planner time: 118.83s; endpoint decoding: 191.39s; GLR checks: 10.36s. Total run wall time: 400.95s.

The tracker estimates signs/types/rates using forced observations, offline calibration and actual type-query responses; it receives no true signs, group types, rates, private seed, correctness, or evaluation feedback. Its estimator projection, finite coordinate iterations, 32-action update frequency, fixed solver tolerance and deterministic deficit tracking are a precommitted development variant. The original asymptotic achievability proof has not been verified for this implementation.

|Scenario|R|alpha|Mean forced fraction (last update)|Mean sign errors|Mean type errors|Mean abs p error|Mean abs q error|
|---|---:|---:|---:|---:|---:|---:|---:|
|dimension_probe|4|3|0.1269|0.5000|0.0000|0.0545|0.0434|
|label_asymmetric|4|3|0.1379|3.5000|0.5000|0.0171|0.1135|
|persistent|4|3|0.2549|0.0000|0.0000|0.0833|0.1042|
|primary|4|0|0.2857|3.1250|0.2000|0.0595|0.0920|
|primary|4|3|0.2857|3.1750|0.1750|0.0508|0.0677|
|primary_glr|4|0|0.1640|0.0000|0.0000|0.0516|0.1372|
|primary_glr|4|3|0.1463|0.1667|0.0000|0.0675|0.0608|
|primary_glr|16|0|0.1326|0.0000|0.0000|0.0583|0.1125|
|primary_glr|16|3|0.1241|0.0000|0.0000|0.0373|0.0824|
|primary_glr|64|0|0.0926|0.0000|0.0000|0.0411|0.0853|
|primary_glr|64|3|0.0912|0.0000|0.0000|0.0308|0.0394|
|q_boundary|4|3|0.1365|0.5000|0.0000|0.0246|0.0960|
|rate_coverage|4|3|0.2857|6.5000|0.7500|0.0882|0.0647|

Forced observations are also usable task observations; the forced fraction is an allocation cost, not wasted samples. Error diagnostics remain evaluator-only. Raw update-level errors and CPU costs remain in trajectories.jsonl.

## Theory versus observed restricted cost

|Partition|alpha|R|K (tasks + types)|K_oracle|Tracking mean min(T,B)/R|Tracking completed / all|Oracle mean min(T,B)/R|
|---|---:|---:|---:|---:|---:|---:|---:|
|[1, 3]|0|4|5.77022|4.81065|90.000|2/2|22.000|
|[1, 3]|0|16|5.77022|4.81065|31.500|2/2|9.500|
|[1, 3]|0|64|5.77022|4.81065|12.750|2/2|5.875|
|[1, 3]|3|4|5.20071|4.10197|74.000|2/2|30.000|
|[1, 3]|3|16|5.20071|4.10197|23.500|2/2|10.000|
|[1, 3]|3|64|5.20071|4.10197|11.375|2/2|5.500|
|[2, 2]|0|4|5.65104|4.81065|58.000|2/2|22.000|
|[2, 2]|0|16|5.65104|4.81065|20.500|2/2|9.500|
|[2, 2]|0|64|5.65104|4.81065|9.375|2/2|5.875|
|[2, 2]|3|4|5.11342|4.10197|76.000|2/2|30.000|
|[2, 2]|3|16|5.11342|4.10197|21.000|2/2|10.000|
|[2, 2]|3|64|5.11342|4.10197|9.500|2/2|5.500|
|[4]|0|4|4.81065|4.81065|38.000|2/2|22.000|
|[4]|0|16|4.81065|4.81065|11.500|2/2|9.500|
|[4]|0|64|4.81065|4.81065|6.875|2/2|5.875|
|[4]|3|4|4.25363|4.10197|44.000|2/2|30.000|
|[4]|3|16|4.25363|4.10197|15.500|2/2|10.000|
|[4]|3|64|4.25363|4.10197|7.375|2/2|5.500|

K is an asymptotic ONLINE coefficient. The observed column is restricted cost divided by R; heavy censoring can move it below K and does not contradict the lower bound. Offline total 2M is separately charged. These bounded runs do not establish convergence to K, do not empirically verify the d=16 phase transition, and do not authorize confirmation or natural-language claims.

Source and math reviews use separate same-family Codex agents, not external human or cross-model theorem certification. All previous experimental artifacts are preserved.
