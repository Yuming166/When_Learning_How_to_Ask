# T2b deployment cost analysis

Manual final assessment: **REVISE**, see FINAL_DECISION.md. The frozen primary numerical scenarios below charge historical synthetic-data preparation and fitting CPU. Separately disclosed training acquisition counts and timer qualifications follow at the end.

成本判断依赖每次反馈与 CPU 的相对价格；这里不编造货币单价，也不把组件 wall 加速当成全流程 CPU 加速。

C_total = c_query N + c_CPU T_CPU + C_train/M。配对差值除以 c_CPU 后为 lambda DeltaN + DeltaCPU + T_known/M，其中 lambda=c_query/c_CPU（CPU 秒等价/观测），M 为未来部署次数。

N 使用总获取，DeltaCPU 使用完整 path CPU；同一世界/R 的校准成本相同而在差值中抵销。下面是固定开发网格的点估计情景，不是价格预测、置信边界或外推收益保证。

历史已知 preparation CPU=472.632148019s；单次拟合 {'DeepSets-KL': 4.783507060999999, 'DeepSets-Info': 11.059857627000001}。

三种训练摊销情景：sunk_training=0（已发生且复用）；fit_only=对应单模型 CPU 拟合；known_construction_plus_fit=将整次已知共享 preparation 全额分配给该模型，再加其拟合。hybrid/periodic 使用 DeepSets-KL 成本，纯基线为零；不把无训练阶段说成整个部署无需训练。

历史初次失败 world 的原始前缀成本未知；上述是已知部分阶段 CPU，不是完整项目成本。没有把未知项填为零。它们也不包括人工、原开发评估/调参、能耗或 GPU 价格。

## 每次部署的观测与完整 CPU 差值

|方法|参考|完整配对|Delta获取|Delta CPU s|
|---|---|---|---|---|
|AnalyticReuse|Fused-Info|True|30.667|-0.559|
|DeepSets-Info|AnalyticReuse|True|92.444|-0.500|
|DeepSets-Info|Fused-Info|True|123.111|-1.059|
|DeepSets-KL|AnalyticReuse|True|79.111|-0.505|
|DeepSets-KL|Fused-Info|True|109.778|-1.065|
|Fused-Info|AnalyticReuse|True|-30.667|0.559|
|Fused-Original-Cold|AnalyticReuse|True|1.333|3.339|
|Fused-Original-Cold|Fused-Info|True|32.000|2.780|
|Hybrid-Risk-Info|AnalyticReuse|True|95.111|-0.382|
|Hybrid-Risk-Info|Fused-Info|True|125.778|-0.941|
|Hybrid-Risk-Reuse|AnalyticReuse|True|71.556|-0.429|
|Hybrid-Risk-Reuse|Fused-Info|True|102.222|-0.988|
|Periodic-Info|AnalyticReuse|True|-4.889|-0.224|
|Periodic-Info|Fused-Info|True|25.778|-0.783|

## M=1000 的 break-even 情景

lambda 小于/大于阈值的方向见区域列；阈值单位为 CPU 秒等价/观测。等号是持平，不属于严格节省。全部 M=1/100/1000/10000 情景保留在 deployment_scenarios.json。

|方法|参考|训练情景|每部署训练 CPU s|lambda 阈值|节省区域|
|---|---|---|---|---|---|
|AnalyticReuse|Fused-Info|sunk_training|0.000|0.018233|0 <= lambda < threshold|
|AnalyticReuse|Fused-Info|fit_only|0.000|0.018233|0 <= lambda < threshold|
|AnalyticReuse|Fused-Info|known_construction_plus_fit|0.000|0.018233|0 <= lambda < threshold|
|DeepSets-Info|AnalyticReuse|sunk_training|0.000|0.005405|0 <= lambda < threshold|
|DeepSets-Info|AnalyticReuse|fit_only|0.011|0.005286|0 <= lambda < threshold|
|DeepSets-Info|AnalyticReuse|known_construction_plus_fit|0.484|0.000173|0 <= lambda < threshold|
|DeepSets-Info|Fused-Info|sunk_training|0.000|0.008601|0 <= lambda < threshold|
|DeepSets-Info|Fused-Info|fit_only|0.011|0.008511|0 <= lambda < threshold|
|DeepSets-Info|Fused-Info|known_construction_plus_fit|0.484|0.004672|0 <= lambda < threshold|
|DeepSets-KL|AnalyticReuse|sunk_training|0.000|0.006389|0 <= lambda < threshold|
|DeepSets-KL|AnalyticReuse|fit_only|0.005|0.006329|0 <= lambda < threshold|
|DeepSets-KL|AnalyticReuse|known_construction_plus_fit|0.477|0.000354|0 <= lambda < threshold|
|DeepSets-KL|Fused-Info|sunk_training|0.000|0.009698|0 <= lambda < threshold|
|DeepSets-KL|Fused-Info|fit_only|0.005|0.009654|0 <= lambda < threshold|
|DeepSets-KL|Fused-Info|known_construction_plus_fit|0.477|0.005349|0 <= lambda < threshold|
|Fused-Info|AnalyticReuse|sunk_training|0.000|0.018233|lambda > threshold|
|Fused-Info|AnalyticReuse|fit_only|0.000|0.018233|lambda > threshold|
|Fused-Info|AnalyticReuse|known_construction_plus_fit|0.000|0.018233|lambda > threshold|
|Fused-Original-Cold|AnalyticReuse|sunk_training|0.000|NA|none for nonnegative lambda|
|Fused-Original-Cold|AnalyticReuse|fit_only|0.000|NA|none for nonnegative lambda|
|Fused-Original-Cold|AnalyticReuse|known_construction_plus_fit|0.000|NA|none for nonnegative lambda|
|Fused-Original-Cold|Fused-Info|sunk_training|0.000|NA|none for nonnegative lambda|
|Fused-Original-Cold|Fused-Info|fit_only|0.000|NA|none for nonnegative lambda|
|Fused-Original-Cold|Fused-Info|known_construction_plus_fit|0.000|NA|none for nonnegative lambda|
|Hybrid-Risk-Info|AnalyticReuse|sunk_training|0.000|0.004018|0 <= lambda < threshold|
|Hybrid-Risk-Info|AnalyticReuse|fit_only|0.005|0.003968|0 <= lambda < threshold|
|Hybrid-Risk-Info|AnalyticReuse|known_construction_plus_fit|0.477|NA|none for nonnegative lambda|
|Hybrid-Risk-Info|Fused-Info|sunk_training|0.000|0.007484|0 <= lambda < threshold|
|Hybrid-Risk-Info|Fused-Info|fit_only|0.005|0.007446|0 <= lambda < threshold|
|Hybrid-Risk-Info|Fused-Info|known_construction_plus_fit|0.477|0.003688|0 <= lambda < threshold|
|Hybrid-Risk-Reuse|AnalyticReuse|sunk_training|0.000|0.005992|0 <= lambda < threshold|
|Hybrid-Risk-Reuse|AnalyticReuse|fit_only|0.005|0.005925|0 <= lambda < threshold|
|Hybrid-Risk-Reuse|AnalyticReuse|known_construction_plus_fit|0.477|NA|none for nonnegative lambda|
|Hybrid-Risk-Reuse|Fused-Info|sunk_training|0.000|0.009664|0 <= lambda < threshold|
|Hybrid-Risk-Reuse|Fused-Info|fit_only|0.005|0.009617|0 <= lambda < threshold|
|Hybrid-Risk-Reuse|Fused-Info|known_construction_plus_fit|0.477|0.004994|0 <= lambda < threshold|
|Periodic-Info|AnalyticReuse|sunk_training|0.000|NA|all nonnegative lambda|
|Periodic-Info|AnalyticReuse|fit_only|0.005|NA|all nonnegative lambda|
|Periodic-Info|AnalyticReuse|known_construction_plus_fit|0.477|0.051919|lambda > threshold|
|Periodic-Info|Fused-Info|sunk_training|0.000|0.030365|0 <= lambda < threshold|
|Periodic-Info|Fused-Info|fit_only|0.005|0.030180|0 <= lambda < threshold|
|Periodic-Info|Fused-Info|known_construction_plus_fit|0.477|0.011845|0 <= lambda < threshold|

## Controller 嵌套计算分项（主池与变维度全部路径）

|方法|分项完整|条件回退次数/决策数|neural wall/CPU s|risk wall/CPU s|baseline/fallback wall/CPU s|controller 外壳 wall s|
|---|---|---|---|---|---|---|
|AnalyticReuse|True|0/3508|0.000/0.000|0.000/0.000|43.788/43.785|44.684|
|DeepSets-Info|True|0/3724|4.367/4.369|0.000/0.000|0.000/0.000|5.312|
|DeepSets-KL|True|0/3699|4.357/4.359|0.000/0.000|0.000/0.000|5.293|
|Fused-Info|True|0/3443|0.000/0.000|0.000/0.000|83.104/83.101|84.066|
|Fused-Original-Cold|True|0/3511|0.000/0.000|0.000/0.000|292.501/292.487|293.361|
|Hybrid-Risk-Info|True|329/3733|4.361/4.363|0.960/0.964|7.815/7.815|14.073|
|Hybrid-Risk-Reuse|True|323/3677|4.287/4.289|0.945/0.949|5.161/5.161|11.312|
|Periodic-Info|True|907/3504|4.119/4.121|0.000/0.000|21.856/21.857|26.870|

纯基线的计算也记在 baseline/fallback 分项；条件回退次数只表示 hybrid/periodic 的实际切换。缺失分项显示 NA，不填零。

## 测量范围与完整执行账本

完整 path CPU/wall 包含估计、planner/controller、神经推理、风险指标、fallback、GLR、gate 与环境；模型冷加载/worker 启动在 driver 账本另列。本轮 inference 仅含神经计算；风险、fallback 和 controller 包装余量计入 planning。controller 自身分项是嵌套诊断，不能额外加到 path 总数。

break-even 默认已加载长期服务。未来若每批部署重新初始化，应在截距额外加入差分冷初始化 CPU/M；共享加载两个模型的 worker 成本未武断归给某一方法。保存的 driver/worker 加载收据供独立配置计算，不能将其默认当成未来为零。wall 并行总时与子进程 CPU 总和不是同一计量。

执行收据见 artifacts/analysis/execution_receipts.json；本报告不把嵌套阶段耗时相加为完整项目总耗时。

本轮 execution 收据（原样保留在 JSON，不含模型/真实答案数据）：

```json
{
  "confirmation_worlds": 0,
  "expected_paths": 624,
  "external_api_calls": 0,
  "failed_paths": 0,
  "gpu_jobs": 0,
  "new_training_updates": 0,
  "offline_path_charges": 153344,
  "online_actions": 921568,
  "outer_parent_cpu_seconds": 5.6904913709999985,
  "outer_wall_seconds": 340.9967087493278,
  "path_records": 624,
  "qwen_calls": 0,
  "scientific_retries": 0,
  "status": "completed",
  "worker_count": 2
}
```

## Final scope qualifications

Frozen POLICY_ALIGNMENT_AUDIT.md describes the evaluator's enclosing pre-reclassification inference timer. The final path wrapper reclassifies neural forward time as inference and every risk/fallback/normalization/wrapper remainder as planning. Their sum preserves the original enclosing controller cost. Most detailed component timers are wall seconds; controller_accounting.cpu and full-path cpu are separate CPU measurements. Components are nested, not additional costs.

Full-path CPU/wall includes controller construction, estimation, all forwards even when discarded on fallback, risk, fallback, tracking, GLR, strict gate, environment and progress journals. The outer worker/model startup and final parent serialization remain outside each path; no claim of complete project/service CPU accounting follows. Worker model-load receipts are retained separately below, not allocated arbitrarily to one method. Main methods run in deterministic rotated order on two single-thread CPU workers. No randomized hardware or energy benchmark is claimed.

T2 training data construction used 360,448 online and100,976 unique offline synthetic observations (461,424 total). Completed historical preparation including smoke and budget selection used466,928 observations/path charges. Their simulated generation CPU is already included in the preparation charge; no paid API/human feedback was acquired. If a future application must recollect paid training feedback, additionally charge lambda*N_train/M; this is a conditional accounting formula, not evidence of Natural/human effectiveness. audit/TRAINING_ACQUISITION_COST_SCOPE.json binds these counts.

The original T2 failed attempt additionally has128 known smoke actions and516 known technical diagnostic replay actions, while its original interrupted prefix remains unknown. Replayed costs do not replace that unknown. The current T2b study incurred no scientific rerun, new training, GPU, RL, provider call or confirmation. Its technical smoke used1,280 online+1,280 offline path charges; main evaluation used921,568 online+153,344 offline charges, all recorded including caps. These are simulator/per-policy counts and methods/R share potential streams, so they are not unique independent observations.

The complete main wrapper ran340.996709s wall and5.690491s parentCPU (workerCPU excluded), smoke2.563834s wall/2.559288s CPU, analysis7.225622s wall/7.224044s CPU. Stages begin after imports/initial source/history verification; per-path subtotals cannot be added again to outer wall totals. Testing, source review and known/unknown prior attempts are not all covered by these stage clocks. There is no complete total-project cost or net amortized benefit claim.

| Worker model load | Wall seconds | CPU seconds |
|---|---:|---:|
| 1 | 1.321096 | 1.312346 |
| 2 | 1.366109 | 1.358641 |
