# T2b matched development comparison

## Material Passport

完整结论由 FINAL_DECISION.md 给出；此报告不自动宣布 GO。所有数字限于冻结开发 roster，未使用保留确认集。

路径覆盖 624/624；状态 {'completed': 624}；预算读数 1248/1248。

每个主世界的三个 R 一起重采样；主池中的 72 条配对记录来自 24 个世界，不能当成 72 个独立样本。所有区间均为固定异质网格的描述性世界聚类重采样范围，不是校准总体置信区间或正式非劣检验。

在线均值包含 cap 弃权，是 restricted capped acquisition cost；不是未截断期望停止时间。总获取还包括两条校准流。

|方法|路径|在线均值|总获取均值|正确认证|弃权|全路径 CPU 均值 s|全路径 wall 均值 s|
|---|---|---|---|---|---|---|---|
|Fused-Original-Cold|72/72|1504.444|1756.444|70/72|2|4.246|4.246|
|AnalyticReuse|72/72|1503.111|1755.111|70/72|2|0.907|0.907|
|Fused-Info|72/72|1472.444|1724.444|72/72|0|1.466|1.466|
|DeepSets-KL|72/72|1582.222|1834.222|69/72|3|0.402|0.402|
|DeepSets-Info|72/72|1595.556|1847.556|68/72|4|0.407|0.407|
|Hybrid-Risk-Info|72/72|1598.222|1850.222|68/72|4|0.525|0.525|
|Hybrid-Risk-Reuse|72/72|1574.667|1826.667|69/72|3|0.478|0.478|
|Periodic-Info|72/72|1498.222|1750.222|72/72|0|0.683|0.683|

## 配对参考：AnalyticReuse

|方法|在线成本比|总获取比|估计+规划+推理加速|全路径 CPU 加速|全路径 wall 加速|新增弃权对|原三门全过|
|---|---|---|---|---|---|---|---|
|DeepSets-Info|1.062 [1.027, 1.091]|1.053 [1.023, 1.079]|3.133 [2.873, 3.502]|2.227 [2.085, 2.407]|2.227 [2.085, 2.407]|2|False|
|DeepSets-KL|1.053 [1.027, 1.078]|1.045 [1.023, 1.068]|3.192 [2.949, 3.524]|2.259 [2.126, 2.416]|2.259 [2.126, 2.416]|1|False|
|Fused-Info|0.980 [0.962, 0.995]|0.983 [0.967, 0.996]|0.571 [0.518, 0.645]|0.619 [0.567, 0.690]|0.619 [0.567, 0.690]|0|False|
|Fused-Original-Cold|1.001 [1.000, 1.002]|1.001 [1.000, 1.002]|0.183 [0.157, 0.233]|0.214 [0.184, 0.270]|0.214 [0.184, 0.270]|0|False|
|Hybrid-Risk-Info|1.063 [1.030, 1.098]|1.054 [1.025, 1.083]|2.092 [1.846, 2.339]|1.728 [1.585, 1.868]|1.728 [1.586, 1.867]|2|False|
|Hybrid-Risk-Reuse|1.048 [1.021, 1.074]|1.041 [1.017, 1.064]|2.392 [2.044, 2.684]|1.897 [1.708, 2.050]|1.896 [1.707, 2.050]|1|False|
|Periodic-Info|0.997 [0.976, 1.014]|0.997 [0.980, 1.012]|1.427 [1.309, 1.590]|1.327 [1.238, 1.446]|1.327 [1.238, 1.446]|0|False|

## 配对参考：Fused-Info

|方法|在线成本比|总获取比|估计+规划+推理加速|全路径 CPU 加速|全路径 wall 加速|新增弃权对|原三门全过|
|---|---|---|---|---|---|---|---|
|AnalyticReuse|1.021 [1.005, 1.039]|1.018 [1.004, 1.034]|1.752 [1.550, 1.930]|1.616 [1.449, 1.762]|1.616 [1.449, 1.762]|2|False|
|DeepSets-Info|1.084 [1.056, 1.108]|1.071 [1.046, 1.094]|5.490 [5.314, 5.658]|3.600 [3.417, 3.742]|3.600 [3.417, 3.742]|4|False|
|DeepSets-KL|1.075 [1.045, 1.101]|1.064 [1.037, 1.088]|5.594 [5.330, 5.816]|3.651 [3.410, 3.839]|3.651 [3.410, 3.839]|3|False|
|Fused-Original-Cold|1.022 [1.006, 1.040]|1.019 [1.005, 1.035]|0.321 [0.292, 0.373]|0.345 [0.314, 0.402]|0.345 [0.314, 0.402]|2|False|
|Hybrid-Risk-Info|1.085 [1.059, 1.113]|1.073 [1.049, 1.097]|3.665 [3.102, 4.063]|2.794 [2.449, 3.037]|2.794 [2.449, 3.037]|4|False|
|Hybrid-Risk-Reuse|1.069 [1.039, 1.096]|1.059 [1.032, 1.084]|4.191 [3.373, 4.777]|3.066 [2.604, 3.401]|3.065 [2.604, 3.401]|3|False|
|Periodic-Info|1.018 [1.009, 1.026]|1.015 [1.007, 1.022]|2.500 [2.449, 2.544]|2.145 [2.079, 2.198]|2.145 [2.079, 2.198]|0|True|

## 条件结果与完整分母

下表保留每个 split/R 的全部适用路径；main/variable 分开。完整配对范围、失败状态、各字段向量见 artifacts/analysis/aggregate.json 与 paired_vectors.json。

|split|R|方法|完成/适用|在线均值|认证|弃权|失败|
|---|---|---|---|---|---|---|---|
|eval_id|16|AnalyticReuse|6/6|581.333|6|0|0|
|eval_id|16|DeepSets-Info|6/6|661.333|6|0|0|
|eval_id|16|DeepSets-KL|6/6|608.000|6|0|0|
|eval_id|16|Fused-Info|6/6|624.000|6|0|0|
|eval_id|16|Fused-Original-Cold|6/6|581.333|6|0|0|
|eval_id|16|Hybrid-Risk-Info|6/6|618.667|6|0|0|
|eval_id|16|Hybrid-Risk-Reuse|6/6|608.000|6|0|0|
|eval_id|16|Periodic-Info|6/6|602.667|6|0|0|
|eval_id|64|AnalyticReuse|6/6|1178.667|6|0|0|
|eval_id|64|DeepSets-Info|6/6|1232.000|6|0|0|
|eval_id|64|DeepSets-KL|6/6|1226.667|6|0|0|
|eval_id|64|Fused-Info|6/6|1130.667|6|0|0|
|eval_id|64|Fused-Original-Cold|6/6|1178.667|6|0|0|
|eval_id|64|Hybrid-Risk-Info|6/6|1232.000|6|0|0|
|eval_id|64|Hybrid-Risk-Reuse|6/6|1221.333|6|0|0|
|eval_id|64|Periodic-Info|6/6|1146.667|6|0|0|
|eval_id|256|AnalyticReuse|6/6|3045.333|6|0|0|
|eval_id|256|DeepSets-Info|6/6|3232.000|5|1|0|
|eval_id|256|DeepSets-KL|6/6|3194.667|6|0|0|
|eval_id|256|Fused-Info|6/6|2976.000|6|0|0|
|eval_id|256|Fused-Original-Cold|6/6|3045.333|6|0|0|
|eval_id|256|Hybrid-Risk-Info|6/6|3184.000|5|1|0|
|eval_id|256|Hybrid-Risk-Reuse|6/6|3168.000|6|0|0|
|eval_id|256|Periodic-Info|6/6|3040.000|6|0|0|
|eval_ood_calibration|16|AnalyticReuse|6/6|688.000|6|0|0|
|eval_ood_calibration|16|DeepSets-Info|6/6|736.000|6|0|0|
|eval_ood_calibration|16|DeepSets-KL|6/6|784.000|6|0|0|
|eval_ood_calibration|16|Fused-Info|6/6|677.333|6|0|0|
|eval_ood_calibration|16|Fused-Original-Cold|6/6|693.333|6|0|0|
|eval_ood_calibration|16|Hybrid-Risk-Info|6/6|778.667|6|0|0|
|eval_ood_calibration|16|Hybrid-Risk-Reuse|6/6|741.333|6|0|0|
|eval_ood_calibration|16|Periodic-Info|6/6|704.000|6|0|0|
|eval_ood_calibration|64|AnalyticReuse|6/6|1226.667|6|0|0|
|eval_ood_calibration|64|DeepSets-Info|6/6|1312.000|6|0|0|
|eval_ood_calibration|64|DeepSets-KL|6/6|1349.333|6|0|0|
|eval_ood_calibration|64|Fused-Info|6/6|1136.000|6|0|0|
|eval_ood_calibration|64|Fused-Original-Cold|6/6|1226.667|6|0|0|
|eval_ood_calibration|64|Hybrid-Risk-Info|6/6|1264.000|6|0|0|
|eval_ood_calibration|64|Hybrid-Risk-Reuse|6/6|1301.333|6|0|0|
|eval_ood_calibration|64|Periodic-Info|6/6|1168.000|6|0|0|
|eval_ood_calibration|256|AnalyticReuse|6/6|3205.333|5|1|0|
|eval_ood_calibration|256|DeepSets-Info|6/6|3242.667|5|1|0|
|eval_ood_calibration|256|DeepSets-KL|6/6|3232.000|5|1|0|
|eval_ood_calibration|256|Fused-Info|6/6|3034.667|6|0|0|
|eval_ood_calibration|256|Fused-Original-Cold|6/6|3205.333|5|1|0|
|eval_ood_calibration|256|Hybrid-Risk-Info|6/6|3221.333|5|1|0|
|eval_ood_calibration|256|Hybrid-Risk-Reuse|6/6|3296.000|5|1|0|
|eval_ood_calibration|256|Periodic-Info|6/6|3082.667|6|0|0|
|eval_ood_parameters|16|AnalyticReuse|6/6|357.333|6|0|0|
|eval_ood_parameters|16|DeepSets-Info|6/6|394.667|6|0|0|
|eval_ood_parameters|16|DeepSets-KL|6/6|362.667|6|0|0|
|eval_ood_parameters|16|Fused-Info|6/6|384.000|6|0|0|
|eval_ood_parameters|16|Fused-Original-Cold|6/6|357.333|6|0|0|
|eval_ood_parameters|16|Hybrid-Risk-Info|6/6|405.333|6|0|0|
|eval_ood_parameters|16|Hybrid-Risk-Reuse|6/6|357.333|6|0|0|
|eval_ood_parameters|16|Periodic-Info|6/6|410.667|6|0|0|
|eval_ood_parameters|64|AnalyticReuse|6/6|666.667|6|0|0|
|eval_ood_parameters|64|DeepSets-Info|6/6|714.667|6|0|0|
|eval_ood_parameters|64|DeepSets-KL|6/6|677.333|6|0|0|
|eval_ood_parameters|64|Fused-Info|6/6|650.667|6|0|0|
|eval_ood_parameters|64|Fused-Original-Cold|6/6|666.667|6|0|0|
|eval_ood_parameters|64|Hybrid-Risk-Info|6/6|725.333|6|0|0|
|eval_ood_parameters|64|Hybrid-Risk-Reuse|6/6|666.667|6|0|0|
|eval_ood_parameters|64|Periodic-Info|6/6|677.333|6|0|0|
|eval_ood_parameters|256|AnalyticReuse|6/6|1765.333|6|0|0|
|eval_ood_parameters|256|DeepSets-Info|6/6|1861.333|6|0|0|
|eval_ood_parameters|256|DeepSets-KL|6/6|1978.667|6|0|0|
|eval_ood_parameters|256|Fused-Info|6/6|1749.333|6|0|0|
|eval_ood_parameters|256|Fused-Original-Cold|6/6|1765.333|6|0|0|
|eval_ood_parameters|256|Hybrid-Risk-Info|6/6|2080.000|6|0|0|
|eval_ood_parameters|256|Hybrid-Risk-Reuse|6/6|2005.333|6|0|0|
|eval_ood_parameters|256|Periodic-Info|6/6|1770.667|6|0|0|
|eval_ood_partition|16|AnalyticReuse|6/6|709.333|6|0|0|
|eval_ood_partition|16|DeepSets-Info|6/6|832.000|6|0|0|
|eval_ood_partition|16|DeepSets-KL|6/6|746.667|6|0|0|
|eval_ood_partition|16|Fused-Info|6/6|746.667|6|0|0|
|eval_ood_partition|16|Fused-Original-Cold|6/6|714.667|6|0|0|
|eval_ood_partition|16|Hybrid-Risk-Info|6/6|805.333|6|0|0|
|eval_ood_partition|16|Hybrid-Risk-Reuse|6/6|741.333|6|0|0|
|eval_ood_partition|16|Periodic-Info|6/6|752.000|6|0|0|
|eval_ood_partition|64|AnalyticReuse|6/6|1344.000|6|0|0|
|eval_ood_partition|64|DeepSets-Info|6/6|1509.333|6|0|0|
|eval_ood_partition|64|DeepSets-KL|6/6|1370.667|6|0|0|
|eval_ood_partition|64|Fused-Info|6/6|1338.667|6|0|0|
|eval_ood_partition|64|Fused-Original-Cold|6/6|1349.333|6|0|0|
|eval_ood_partition|64|Hybrid-Risk-Info|6/6|1413.333|6|0|0|
|eval_ood_partition|64|Hybrid-Risk-Reuse|6/6|1365.333|6|0|0|
|eval_ood_partition|64|Periodic-Info|6/6|1354.667|6|0|0|
|eval_ood_partition|256|AnalyticReuse|6/6|3269.333|5|1|0|
|eval_ood_partition|256|DeepSets-Info|6/6|3418.667|4|2|0|
|eval_ood_partition|256|DeepSets-KL|6/6|3456.000|4|2|0|
|eval_ood_partition|256|Fused-Info|6/6|3221.333|6|0|0|
|eval_ood_partition|256|Fused-Original-Cold|6/6|3269.333|5|1|0|
|eval_ood_partition|256|Hybrid-Risk-Info|6/6|3450.667|4|2|0|
|eval_ood_partition|256|Hybrid-Risk-Reuse|6/6|3424.000|4|2|0|
|eval_ood_partition|256|Periodic-Info|6/6|3269.333|6|0|0|
|eval_variable|64|AnalyticReuse|6/6|672.000|6|0|0|
|eval_variable|64|DeepSets-Info|6/6|714.667|6|0|0|
|eval_variable|64|DeepSets-KL|6/6|741.333|6|0|0|
|eval_variable|64|Fused-Info|6/6|693.333|6|0|0|
|eval_variable|64|Fused-Original-Cold|6/6|672.000|6|0|0|
|eval_variable|64|Hybrid-Risk-Info|6/6|730.667|6|0|0|
|eval_variable|64|Hybrid-Risk-Reuse|6/6|714.667|6|0|0|
|eval_variable|64|Periodic-Info|6/6|709.333|6|0|0|

## 中途预算评分（独立于固定置信认证）

B=32/64 是同一固定置信轨迹的中途读数，公共 cap 仍为 6144；不是 T1b 已知剩余 horizon 的固定预算实验。提前认证后的读数使用吸收答案和实际已付成本。

|split|R|方法|B|正确/适用|缺失|吸收|有效在线均值|
|---|---|---|---|---|---|---|---|
|eval_id|16|AnalyticReuse|32|3/6|0|0|32.000|
|eval_id|16|AnalyticReuse|64|5/6|0|0|64.000|
|eval_id|16|DeepSets-Info|32|3/6|0|0|32.000|
|eval_id|16|DeepSets-Info|64|5/6|0|0|64.000|
|eval_id|16|DeepSets-KL|32|3/6|0|0|32.000|
|eval_id|16|DeepSets-KL|64|5/6|0|0|64.000|
|eval_id|16|Fused-Info|32|4/6|0|0|32.000|
|eval_id|16|Fused-Info|64|6/6|0|0|64.000|
|eval_id|16|Fused-Original-Cold|32|3/6|0|0|32.000|
|eval_id|16|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_id|16|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_id|16|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_id|16|Hybrid-Risk-Reuse|32|3/6|0|0|32.000|
|eval_id|16|Hybrid-Risk-Reuse|64|5/6|0|0|64.000|
|eval_id|16|Periodic-Info|32|4/6|0|0|32.000|
|eval_id|16|Periodic-Info|64|5/6|0|0|64.000|
|eval_id|64|AnalyticReuse|32|3/6|0|0|32.000|
|eval_id|64|AnalyticReuse|64|5/6|0|0|64.000|
|eval_id|64|DeepSets-Info|32|3/6|0|0|32.000|
|eval_id|64|DeepSets-Info|64|6/6|0|0|64.000|
|eval_id|64|DeepSets-KL|32|3/6|0|0|32.000|
|eval_id|64|DeepSets-KL|64|6/6|0|0|64.000|
|eval_id|64|Fused-Info|32|4/6|0|0|32.000|
|eval_id|64|Fused-Info|64|6/6|0|0|64.000|
|eval_id|64|Fused-Original-Cold|32|3/6|0|0|32.000|
|eval_id|64|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_id|64|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_id|64|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_id|64|Hybrid-Risk-Reuse|32|3/6|0|0|32.000|
|eval_id|64|Hybrid-Risk-Reuse|64|5/6|0|0|64.000|
|eval_id|64|Periodic-Info|32|4/6|0|0|32.000|
|eval_id|64|Periodic-Info|64|5/6|0|0|64.000|
|eval_id|256|AnalyticReuse|32|3/6|0|0|32.000|
|eval_id|256|AnalyticReuse|64|6/6|0|0|64.000|
|eval_id|256|DeepSets-Info|32|3/6|0|0|32.000|
|eval_id|256|DeepSets-Info|64|6/6|0|0|64.000|
|eval_id|256|DeepSets-KL|32|3/6|0|0|32.000|
|eval_id|256|DeepSets-KL|64|6/6|0|0|64.000|
|eval_id|256|Fused-Info|32|4/6|0|0|32.000|
|eval_id|256|Fused-Info|64|6/6|0|0|64.000|
|eval_id|256|Fused-Original-Cold|32|3/6|0|0|32.000|
|eval_id|256|Fused-Original-Cold|64|6/6|0|0|64.000|
|eval_id|256|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_id|256|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_id|256|Hybrid-Risk-Reuse|32|3/6|0|0|32.000|
|eval_id|256|Hybrid-Risk-Reuse|64|6/6|0|0|64.000|
|eval_id|256|Periodic-Info|32|4/6|0|0|32.000|
|eval_id|256|Periodic-Info|64|5/6|0|0|64.000|
|eval_ood_calibration|16|AnalyticReuse|32|4/6|0|0|32.000|
|eval_ood_calibration|16|AnalyticReuse|64|5/6|0|0|64.000|
|eval_ood_calibration|16|DeepSets-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|16|DeepSets-Info|64|5/6|0|0|64.000|
|eval_ood_calibration|16|DeepSets-KL|32|4/6|0|0|32.000|
|eval_ood_calibration|16|DeepSets-KL|64|5/6|0|0|64.000|
|eval_ood_calibration|16|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|16|Fused-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|16|Fused-Original-Cold|32|4/6|0|0|32.000|
|eval_ood_calibration|16|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_ood_calibration|16|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|16|Hybrid-Risk-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|16|Hybrid-Risk-Reuse|32|4/6|0|0|32.000|
|eval_ood_calibration|16|Hybrid-Risk-Reuse|64|5/6|0|0|64.000|
|eval_ood_calibration|16|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|16|Periodic-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|64|AnalyticReuse|32|5/6|0|0|32.000|
|eval_ood_calibration|64|AnalyticReuse|64|6/6|0|0|64.000|
|eval_ood_calibration|64|DeepSets-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|64|DeepSets-Info|64|5/6|0|0|64.000|
|eval_ood_calibration|64|DeepSets-KL|32|4/6|0|0|32.000|
|eval_ood_calibration|64|DeepSets-KL|64|6/6|0|0|64.000|
|eval_ood_calibration|64|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|64|Fused-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|64|Fused-Original-Cold|32|5/6|0|0|32.000|
|eval_ood_calibration|64|Fused-Original-Cold|64|6/6|0|0|64.000|
|eval_ood_calibration|64|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|64|Hybrid-Risk-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|64|Hybrid-Risk-Reuse|32|5/6|0|0|32.000|
|eval_ood_calibration|64|Hybrid-Risk-Reuse|64|6/6|0|0|64.000|
|eval_ood_calibration|64|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|64|Periodic-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|256|AnalyticReuse|32|4/6|0|0|32.000|
|eval_ood_calibration|256|AnalyticReuse|64|4/6|0|0|64.000|
|eval_ood_calibration|256|DeepSets-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|256|DeepSets-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|256|DeepSets-KL|32|4/6|0|0|32.000|
|eval_ood_calibration|256|DeepSets-KL|64|4/6|0|0|64.000|
|eval_ood_calibration|256|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|256|Fused-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|256|Fused-Original-Cold|32|4/6|0|0|32.000|
|eval_ood_calibration|256|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_ood_calibration|256|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|256|Hybrid-Risk-Info|64|4/6|0|0|64.000|
|eval_ood_calibration|256|Hybrid-Risk-Reuse|32|4/6|0|0|32.000|
|eval_ood_calibration|256|Hybrid-Risk-Reuse|64|4/6|0|0|64.000|
|eval_ood_calibration|256|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_calibration|256|Periodic-Info|64|4/6|0|0|64.000|
|eval_ood_parameters|16|AnalyticReuse|32|4/6|0|0|32.000|
|eval_ood_parameters|16|AnalyticReuse|64|5/6|0|0|64.000|
|eval_ood_parameters|16|DeepSets-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|16|DeepSets-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|16|DeepSets-KL|32|5/6|0|0|32.000|
|eval_ood_parameters|16|DeepSets-KL|64|6/6|0|0|64.000|
|eval_ood_parameters|16|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|16|Fused-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|16|Fused-Original-Cold|32|4/6|0|0|32.000|
|eval_ood_parameters|16|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_ood_parameters|16|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|16|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|16|Hybrid-Risk-Reuse|32|4/6|0|0|32.000|
|eval_ood_parameters|16|Hybrid-Risk-Reuse|64|5/6|0|0|64.000|
|eval_ood_parameters|16|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|16|Periodic-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|64|AnalyticReuse|32|6/6|0|0|32.000|
|eval_ood_parameters|64|AnalyticReuse|64|6/6|0|0|64.000|
|eval_ood_parameters|64|DeepSets-Info|32|5/6|0|0|32.000|
|eval_ood_parameters|64|DeepSets-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|64|DeepSets-KL|32|6/6|0|0|32.000|
|eval_ood_parameters|64|DeepSets-KL|64|5/6|0|0|64.000|
|eval_ood_parameters|64|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|64|Fused-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|64|Fused-Original-Cold|32|6/6|0|0|32.000|
|eval_ood_parameters|64|Fused-Original-Cold|64|6/6|0|0|64.000|
|eval_ood_parameters|64|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|64|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|64|Hybrid-Risk-Reuse|32|6/6|0|0|32.000|
|eval_ood_parameters|64|Hybrid-Risk-Reuse|64|6/6|0|0|64.000|
|eval_ood_parameters|64|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|64|Periodic-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|256|AnalyticReuse|32|6/6|0|0|32.000|
|eval_ood_parameters|256|AnalyticReuse|64|6/6|0|0|64.000|
|eval_ood_parameters|256|DeepSets-Info|32|5/6|0|0|32.000|
|eval_ood_parameters|256|DeepSets-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|256|DeepSets-KL|32|6/6|0|0|32.000|
|eval_ood_parameters|256|DeepSets-KL|64|6/6|0|0|64.000|
|eval_ood_parameters|256|Fused-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|256|Fused-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|256|Fused-Original-Cold|32|6/6|0|0|32.000|
|eval_ood_parameters|256|Fused-Original-Cold|64|6/6|0|0|64.000|
|eval_ood_parameters|256|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|256|Hybrid-Risk-Info|64|6/6|0|0|64.000|
|eval_ood_parameters|256|Hybrid-Risk-Reuse|32|6/6|0|0|32.000|
|eval_ood_parameters|256|Hybrid-Risk-Reuse|64|6/6|0|0|64.000|
|eval_ood_parameters|256|Periodic-Info|32|4/6|0|0|32.000|
|eval_ood_parameters|256|Periodic-Info|64|6/6|0|0|64.000|
|eval_ood_partition|16|AnalyticReuse|32|3/6|0|0|32.000|
|eval_ood_partition|16|AnalyticReuse|64|3/6|0|0|64.000|
|eval_ood_partition|16|DeepSets-Info|32|3/6|0|0|32.000|
|eval_ood_partition|16|DeepSets-Info|64|3/6|0|0|64.000|
|eval_ood_partition|16|DeepSets-KL|32|3/6|0|0|32.000|
|eval_ood_partition|16|DeepSets-KL|64|3/6|0|0|64.000|
|eval_ood_partition|16|Fused-Info|32|2/6|0|0|32.000|
|eval_ood_partition|16|Fused-Info|64|3/6|0|0|64.000|
|eval_ood_partition|16|Fused-Original-Cold|32|3/6|0|0|32.000|
|eval_ood_partition|16|Fused-Original-Cold|64|3/6|0|0|64.000|
|eval_ood_partition|16|Hybrid-Risk-Info|32|2/6|0|0|32.000|
|eval_ood_partition|16|Hybrid-Risk-Info|64|3/6|0|0|64.000|
|eval_ood_partition|16|Hybrid-Risk-Reuse|32|3/6|0|0|32.000|
|eval_ood_partition|16|Hybrid-Risk-Reuse|64|3/6|0|0|64.000|
|eval_ood_partition|16|Periodic-Info|32|2/6|0|0|32.000|
|eval_ood_partition|16|Periodic-Info|64|3/6|0|0|64.000|
|eval_ood_partition|64|AnalyticReuse|32|2/6|0|0|32.000|
|eval_ood_partition|64|AnalyticReuse|64|2/6|0|0|64.000|
|eval_ood_partition|64|DeepSets-Info|32|2/6|0|0|32.000|
|eval_ood_partition|64|DeepSets-Info|64|3/6|0|0|64.000|
|eval_ood_partition|64|DeepSets-KL|32|2/6|0|0|32.000|
|eval_ood_partition|64|DeepSets-KL|64|3/6|0|0|64.000|
|eval_ood_partition|64|Fused-Info|32|2/6|0|0|32.000|
|eval_ood_partition|64|Fused-Info|64|3/6|0|0|64.000|
|eval_ood_partition|64|Fused-Original-Cold|32|2/6|0|0|32.000|
|eval_ood_partition|64|Fused-Original-Cold|64|2/6|0|0|64.000|
|eval_ood_partition|64|Hybrid-Risk-Info|32|2/6|0|0|32.000|
|eval_ood_partition|64|Hybrid-Risk-Info|64|3/6|0|0|64.000|
|eval_ood_partition|64|Hybrid-Risk-Reuse|32|2/6|0|0|32.000|
|eval_ood_partition|64|Hybrid-Risk-Reuse|64|2/6|0|0|64.000|
|eval_ood_partition|64|Periodic-Info|32|2/6|0|0|32.000|
|eval_ood_partition|64|Periodic-Info|64|3/6|0|0|64.000|
|eval_ood_partition|256|AnalyticReuse|32|3/6|0|0|32.000|
|eval_ood_partition|256|AnalyticReuse|64|3/6|0|0|64.000|
|eval_ood_partition|256|DeepSets-Info|32|2/6|0|0|32.000|
|eval_ood_partition|256|DeepSets-Info|64|3/6|0|0|64.000|
|eval_ood_partition|256|DeepSets-KL|32|3/6|0|0|32.000|
|eval_ood_partition|256|DeepSets-KL|64|3/6|0|0|64.000|
|eval_ood_partition|256|Fused-Info|32|2/6|0|0|32.000|
|eval_ood_partition|256|Fused-Info|64|3/6|0|0|64.000|
|eval_ood_partition|256|Fused-Original-Cold|32|3/6|0|0|32.000|
|eval_ood_partition|256|Fused-Original-Cold|64|3/6|0|0|64.000|
|eval_ood_partition|256|Hybrid-Risk-Info|32|2/6|0|0|32.000|
|eval_ood_partition|256|Hybrid-Risk-Info|64|3/6|0|0|64.000|
|eval_ood_partition|256|Hybrid-Risk-Reuse|32|3/6|0|0|32.000|
|eval_ood_partition|256|Hybrid-Risk-Reuse|64|3/6|0|0|64.000|
|eval_ood_partition|256|Periodic-Info|32|2/6|0|0|32.000|
|eval_ood_partition|256|Periodic-Info|64|3/6|0|0|64.000|
|eval_variable|64|AnalyticReuse|32|5/6|0|0|32.000|
|eval_variable|64|AnalyticReuse|64|5/6|0|0|64.000|
|eval_variable|64|DeepSets-Info|32|5/6|0|0|32.000|
|eval_variable|64|DeepSets-Info|64|5/6|0|0|64.000|
|eval_variable|64|DeepSets-KL|32|5/6|0|0|32.000|
|eval_variable|64|DeepSets-KL|64|5/6|0|0|64.000|
|eval_variable|64|Fused-Info|32|4/6|0|0|32.000|
|eval_variable|64|Fused-Info|64|5/6|0|0|64.000|
|eval_variable|64|Fused-Original-Cold|32|5/6|0|0|32.000|
|eval_variable|64|Fused-Original-Cold|64|5/6|0|0|64.000|
|eval_variable|64|Hybrid-Risk-Info|32|4/6|0|0|32.000|
|eval_variable|64|Hybrid-Risk-Info|64|5/6|0|0|64.000|
|eval_variable|64|Hybrid-Risk-Reuse|32|5/6|0|0|32.000|
|eval_variable|64|Hybrid-Risk-Reuse|64|5/6|0|0|64.000|
|eval_variable|64|Periodic-Info|32|4/6|0|0|32.000|
|eval_variable|64|Periodic-Info|64|5/6|0|0|64.000|

## 验收与限制

原 T2 三门全部保留：在线成本比的描述性范围上界 ≤1.05；估计+规划+推理加速的描述性范围下界 ≥2；候选和参考的全部路径正确认证且无弃权。另列相对参考的新增弃权对、弃权总数及错证，不用净恢复数抵销新增失败。描述性门标记不等于总体非劣证明。

所有 controller 经过相同后验、cadence32、平方强制探索、累计目标跟踪和原严格 gate。风险启发式只改变 planner 选择，不给查询非劣或停止时间保证。所有 fallback 计算包含在 planner/controller 和完整 path 计时中。

置信停止、有限精度 planning 与 quadrature 近似均保留原限制；本轮没有模型训练、RL、Qwen 调用、Natural benchmark 或独立确认。
