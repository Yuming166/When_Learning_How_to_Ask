# Cross-budget evaluation

## Material Passport

Bounded CPU development, run/validate inline. New independent roster96; four deadlines on each world are correlated. No RL, neural training, Qwen/model API or confirmation; no Natural/Web generator modification. Full source/dependency/protocol manifest precedes entropy. T1c missing-wrapper defect and old negative findings remain unchanged. This is source-bound descriptive analysis, not an independently rerun efficacy confirmation.


|Policy|B16 exact/n|B32 PRIMARY exact/n|B48 exact/n|B64 exact/n|B32 worker CPU/s|B32 type mean|
|---|---|---|---|---|---|---|
|KL-OriginalSolver|47/96|72/96|81/96|84/96|65.042|1.99|
|KL-AnalyticReuse|47/96|74/96|81/96|85/96|18.539|1.99|
|KL-Fresh|47/96|73/96|82/96|85/96|50.354|2.04|
|Fused-Info|47/96|74/96|87/96|91/96|23.639|1.10|
|IG-Uniform-Block|46/96|74/96|79/96|89/96|6.680|1.88|
|IG-Fact-Block|50/96|75/96|88/96|91/96|8.693|1.18|
|IG-Uniform-Fresh|46/96|73/96|82/96|91/96|18.101|1.68|
|IG-Fact-Fresh|49/96|78/96|89/96|90/96|18.579|0.93|
|IG-Uniform-Direct|49/96|75/96|80/96|88/96|13.585|1.04|
|Fresh-IG-Lite|50/96|77/96|88/96|92/96|11.312|0.88|
|Belief-Gated|50/96|78/96|87/96|93/96|23.919|0.88|
|WorstFact-MI|49/96|80/96|88/96|92/96|11.895|0.99|
|IG-Uniform-FixedType|47/96|70/96|87/96|90/96|11.316|1.62|
|IG-Fact-FixedType|50/96|82/96|92/96|95/96|12.617|1.62|


Each budget was actually run. Belief-Gated knows the deadline; it is not evaluated using a long-path midpoint. d4 B16 is all forced; d3 B16 has4 free rounds. The OOD-partition panel shifts BOTH group partition and fact count. No independent growing-d or general partition-transfer claim follows. Online cost is exactlyB, offline2ceil(alpha R), so higher recovery at equal cost is not a measured saving to equal reliability.

## panel strata


|Stratum|B|n|Lite exact|UniformDirect exact|Fused-Info exact|AnalyticReuse exact|Belief-Gated exact|WorstFact exact|Lite−uniform 95%|
|---|---|---|---|---|---|---|---|---|---|
|ID|16|24|7|7|7|7|7|7|+0.00pp [+0.00pp, +0.00pp]|
|ID|32|24|19|18|17|18|19|20|+4.17pp [-8.33pp, +16.67pp]|
|ID|48|24|23|21|22|21|22|23|+8.33pp [+0.00pp, +20.83pp]|
|ID|64|24|23|23|23|21|23|23|+0.00pp [+0.00pp, +0.00pp]|
|OOD-calibration|16|24|14|14|14|14|14|14|+0.00pp [+0.00pp, +0.00pp]|
|OOD-calibration|32|24|18|16|18|20|19|19|+8.33pp [+0.00pp, +20.83pp]|
|OOD-calibration|48|24|20|18|21|18|20|20|+8.33pp [+0.00pp, +20.83pp]|
|OOD-calibration|64|24|23|21|22|20|23|23|+8.33pp [+0.00pp, +20.83pp]|
|OOD-partition|16|24|19|18|16|16|19|18|+4.17pp [+0.00pp, +12.50pp]|
|OOD-partition|32|24|20|22|22|20|20|22|-8.33pp [-20.83pp, +0.00pp]|
|OOD-partition|48|24|23|23|23|23|23|23|+0.00pp [+0.00pp, +0.00pp]|
|OOD-partition|64|24|23|24|24|23|24|24|-4.17pp [-12.50pp, +0.00pp]|
|OOD-rate|16|24|10|10|10|10|10|10|+0.00pp [+0.00pp, +0.00pp]|
|OOD-rate|32|24|20|19|17|16|20|19|+4.17pp [-8.33pp, +16.67pp]|
|OOD-rate|48|24|22|18|21|19|22|22|+16.67pp [+4.17pp, +33.33pp]|
|OOD-rate|64|24|23|20|22|21|23|22|+12.50pp [+0.00pp, +25.00pp]|


## partition strata


|Stratum|B|n|Lite exact|UniformDirect exact|Fused-Info exact|AnalyticReuse exact|Belief-Gated exact|WorstFact exact|Lite−uniform 95%|
|---|---|---|---|---|---|---|---|---|---|
|(1, 2)|16|12|9|9|7|9|9|9|+0.00pp [+0.00pp, +0.00pp]|
|(1, 2)|32|12|10|11|12|10|10|12|-8.33pp [-25.00pp, +0.00pp]|
|(1, 2)|48|12|12|12|12|12|12|11|+0.00pp [+0.00pp, +0.00pp]|
|(1, 2)|64|12|12|12|12|12|12|12|+0.00pp [+0.00pp, +0.00pp]|
|(1, 3)|16|24|7|7|7|7|7|7|+0.00pp [+0.00pp, +0.00pp]|
|(1, 3)|32|24|17|18|16|19|17|16|-4.17pp [-16.67pp, +8.33pp]|
|(1, 3)|48|24|21|16|21|19|20|21|+20.83pp [+8.33pp, +37.50pp]|
|(1, 3)|64|24|23|19|22|20|23|22|+16.67pp [+4.17pp, +33.33pp]|
|(2, 2)|16|24|12|12|12|12|12|12|+0.00pp [+0.00pp, +0.00pp]|
|(2, 2)|32|24|20|17|17|18|21|21|+12.50pp [+0.00pp, +25.00pp]|
|(2, 2)|48|24|23|21|22|19|23|23|+8.33pp [+0.00pp, +20.83pp]|
|(2, 2)|64|24|24|23|23|21|24|24|+4.17pp [+0.00pp, +12.50pp]|
|(3,)|16|12|10|9|9|7|10|9|+8.33pp [+0.00pp, +25.00pp]|
|(3,)|32|12|10|11|10|10|10|10|-8.33pp [-25.00pp, +0.00pp]|
|(3,)|48|12|11|11|11|11|11|12|+0.00pp [+0.00pp, +0.00pp]|
|(3,)|64|12|11|12|12|11|12|12|-8.33pp [-25.00pp, +0.00pp]|
|(4,)|16|24|12|12|12|12|12|12|+0.00pp [+0.00pp, +0.00pp]|
|(4,)|32|24|20|18|19|17|20|21|+8.33pp [+0.00pp, +20.83pp]|
|(4,)|48|24|21|20|21|20|21|21|+4.17pp [+0.00pp, +12.50pp]|
|(4,)|64|24|22|22|22|21|22|22|+0.00pp [+0.00pp, +0.00pp]|


## rate strata


|Stratum|B|n|Lite exact|UniformDirect exact|Fused-Info exact|AnalyticReuse exact|Belief-Gated exact|WorstFact exact|Lite−uniform 95%|
|---|---|---|---|---|---|---|---|---|---|
|(0.72, 0.64)|16|12|4|4|4|4|4|4|+0.00pp [+0.00pp, +0.00pp]|
|(0.72, 0.64)|32|12|9|8|7|6|9|8|+8.33pp [-16.67pp, +33.33pp]|
|(0.72, 0.64)|48|12|10|7|9|8|10|10|+25.00pp [+0.00pp, +50.00pp]|
|(0.72, 0.64)|64|12|11|9|10|10|11|11|+16.67pp [+0.00pp, +41.67pp]|
|(0.75, 0.6)|16|36|17|17|17|16|17|17|+0.00pp [+0.00pp, +0.00pp]|
|(0.75, 0.6)|32|36|22|24|24|24|23|26|-5.56pp [-16.67pp, +5.56pp]|
|(0.75, 0.6)|48|36|31|28|30|27|30|32|+8.33pp [+0.00pp, +16.67pp]|
|(0.75, 0.6)|64|36|33|33|34|29|34|34|+0.00pp [-8.33pp, +8.33pp]|
|(0.85, 0.6)|16|36|23|22|20|21|23|22|+2.78pp [+0.00pp, +8.33pp]|
|(0.85, 0.6)|32|36|35|32|33|34|35|35|+8.33pp [+0.00pp, +16.67pp]|
|(0.85, 0.6)|48|36|35|34|36|35|35|34|+2.78pp [+0.00pp, +8.33pp]|
|(0.85, 0.6)|64|36|36|35|35|35|36|36|+2.78pp [+0.00pp, +8.33pp]|
|(0.9, 0.55)|16|12|6|6|6|6|6|6|+0.00pp [+0.00pp, +0.00pp]|
|(0.9, 0.55)|32|12|11|11|10|10|11|11|+0.00pp [+0.00pp, +0.00pp]|
|(0.9, 0.55)|48|12|12|11|12|11|12|12|+8.33pp [+0.00pp, +25.00pp]|
|(0.9, 0.55)|64|12|12|11|12|11|12|11|+8.33pp [+0.00pp, +25.00pp]|


## gap strata


|Stratum|B|n|Lite exact|UniformDirect exact|Fused-Info exact|AnalyticReuse exact|Belief-Gated exact|WorstFact exact|Lite−uniform 95%|
|---|---|---|---|---|---|---|---|---|---|
|0.08|16|12|4|4|4|4|4|4|+0.00pp [+0.00pp, +0.00pp]|
|0.08|32|12|9|8|7|6|9|8|+8.33pp [-16.67pp, +33.33pp]|
|0.08|48|12|10|7|9|8|10|10|+25.00pp [+0.00pp, +50.00pp]|
|0.08|64|12|11|9|10|10|11|11|+16.67pp [+0.00pp, +41.67pp]|
|0.15|16|36|17|17|17|16|17|17|+0.00pp [+0.00pp, +0.00pp]|
|0.15|32|36|22|24|24|24|23|26|-5.56pp [-16.67pp, +5.56pp]|
|0.15|48|36|31|28|30|27|30|32|+8.33pp [+0.00pp, +16.67pp]|
|0.15|64|36|33|33|34|29|34|34|+0.00pp [-8.33pp, +8.33pp]|
|0.25|16|36|23|22|20|21|23|22|+2.78pp [+0.00pp, +8.33pp]|
|0.25|32|36|35|32|33|34|35|35|+8.33pp [+0.00pp, +16.67pp]|
|0.25|48|36|35|34|36|35|35|34|+2.78pp [+0.00pp, +8.33pp]|
|0.25|64|36|36|35|35|35|36|36|+2.78pp [+0.00pp, +8.33pp]|
|0.35|16|12|6|6|6|6|6|6|+0.00pp [+0.00pp, +0.00pp]|
|0.35|32|12|11|11|10|10|11|11|+0.00pp [+0.00pp, +0.00pp]|
|0.35|48|12|12|11|12|11|12|12|+8.33pp [+0.00pp, +25.00pp]|
|0.35|64|12|12|11|12|11|12|11|+8.33pp [+0.00pp, +25.00pp]|


## alpha strata


|Stratum|B|n|Lite exact|UniformDirect exact|Fused-Info exact|AnalyticReuse exact|Belief-Gated exact|WorstFact exact|Lite−uniform 95%|
|---|---|---|---|---|---|---|---|---|---|
|0|16|36|17|16|16|15|17|17|+2.78pp [+0.00pp, +8.33pp]|
|0|32|36|31|29|27|23|31|31|+5.56pp [-5.56pp, +16.67pp]|
|0|48|36|35|32|33|32|35|35|+8.33pp [+0.00pp, +16.67pp]|
|0|64|36|35|34|36|33|36|35|+2.78pp [-5.56pp, +11.11pp]|
|1|16|24|14|14|14|14|14|14|+0.00pp [+0.00pp, +0.00pp]|
|1|32|24|18|16|18|20|19|19|+8.33pp [+0.00pp, +20.83pp]|
|1|48|24|20|18|21|18|20|20|+8.33pp [+0.00pp, +20.83pp]|
|1|64|24|23|21|22|20|23|23|+8.33pp [+0.00pp, +20.83pp]|
|3|16|36|19|19|17|18|19|18|+0.00pp [+0.00pp, +0.00pp]|
|3|32|36|28|30|29|31|28|30|-5.56pp [-13.89pp, +0.00pp]|
|3|48|36|33|30|33|31|32|33|+8.33pp [+0.00pp, +16.67pp]|
|3|64|36|34|33|33|32|34|34|+2.78pp [+0.00pp, +8.33pp]|


World-paired bootstrap20000 within four fixed panels, seed42031; cell-stratified sensitivity seed42032 reported separately. Raw95% intervals are developmental; five strong-reference comparisons also have99% Bonferroni-family descriptive intervals. No simultaneous claim for every secondary table. Small strata and a fixed heterogeneous grid limit coverage and external generalization. Same-world budgets/groups are correlated.

Fixed-budget guesses are NOT certified answers. Terminal audited iid/known-s Fraction/Decimal gate includes all task/type/calibration. Certified outputs=0; wrong certificates=0; confidence-censored/noncertified=5376. Planned paths=5376, observed=5376, unfinished=0, infrastructure failures=0; integrity checks passed=True. Gate rejection is distinct from numerical failure or unfinished budget execution. No delta-correctness, asymptotic optimality or real-language Agent claim.
