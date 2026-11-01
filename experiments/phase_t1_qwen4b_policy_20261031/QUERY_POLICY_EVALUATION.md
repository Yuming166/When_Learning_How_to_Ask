# T1 query-policy evaluation

本轮是受控 iid 通道内的开发评测，独立单位为完整世界。离线使用 24 个数据测试世界，每世界五个预定状态；闭环使用另 24 个世界，每分层八个。所有声明的模型结果已记录。

离线先在每个世界内平均五个状态，再等权汇总。L1 和 forward KL 衡量模仿误差；信息缺口是由可观测估计量计算的浮点代理，不是隐藏真参数信息或停止证书。负缺口保留。Qwen 使用整数百分比分配，MLP 使用连续权重；量化误差单独保留。

百分比指标沿用数据生成时保存的 teacher_percent 标签，不从已序列化浮点权重重新生成；最大余数法在数值相同余数处保留生成时的顺序约定。

|分层|方法|状态/计划|无效回退/计划|L1|Forward KL|信息缺口|每次调用墙钟秒|
|---|---|---:|---:|---:|---:|---:|---:|
|id_test|MLP|40/40|0/40|0.3592|0.2853|0.2182|0.0005|
|id_test|BaseQwen|40/40|40/40|0.9919|0.6711|0.4173|3.7019|
|id_test|LoRA|40/40|12/40|0.9729|6.1571|0.4964|5.5605|
|ood_parameters|MLP|40/40|0/40|0.3468|0.2505|0.2760|0.0005|
|ood_parameters|BaseQwen|40/40|38/40|1.0310|1.0951|0.4885|3.7239|
|ood_parameters|LoRA|40/40|12/40|1.2093|8.0904|0.6188|5.5945|
|ood_partition|MLP|40/40|0/40|0.6456|0.6320|0.6661|0.0005|
|ood_partition|BaseQwen|40/40|38/40|0.8558|0.5292|0.4239|3.5685|
|ood_partition|LoRA|40/40|29/40|0.9117|2.4524|0.4855|5.6488|
|all_24_worlds|MLP|120/120|0/120|0.4506|0.3893|0.3868|0.0005|
|all_24_worlds|BaseQwen|120/120|116/120|0.9595|0.7651|0.4432|3.6648|
|all_24_worlds|LoRA|120/120|53/120|1.0313|5.5666|0.5336|5.6012|

配对改进为左方法减右方法的世界平均损失，正值支持右方法的较低损失。所有区间使用 4,000 次世界配对重采样，固定分析种子 731032；每分层 n=8，未经多重校正。八个世界来自固定且异质的条件组合，因此区间只表示描述性重采样敏感性，不是经过校准的总体置信区间。

all_24_worlds 汇总复用同一批世界，不增加样本；其重采样在每个分层内各抽八个世界，保持三层等额。

|分层|左−右|指标|均值差|描述性95%重采样范围|
|---|---|---|---:|---|
|id_test|BaseQwen−LoRA|allocation_l1|0.0190|[-0.20714833586052475, 0.25352393451604777]|
|id_test|BaseQwen−LoRA|forward_kl_epsilon_1e8|-5.4860|[-8.303605974231866, -2.6412784707421326]|
|id_test|BaseQwen−LoRA|plugin_relative_information_deficit|-0.0792|[-0.2401033206917518, 0.06513179385279558]|
|id_test|BaseQwen−MLP|allocation_l1|0.6326|[0.5123213319572265, 0.7667710304803946]|
|id_test|BaseQwen−MLP|forward_kl_epsilon_1e8|0.3859|[0.16654797426982637, 0.5561030605352675]|
|id_test|BaseQwen−MLP|plugin_relative_information_deficit|0.1991|[0.14215461766984605, 0.2644333056298584]|
|id_test|MLP−LoRA|allocation_l1|-0.6136|[-0.8591981045760514, -0.34984953837021887]|
|id_test|MLP−LoRA|forward_kl_epsilon_1e8|-5.8718|[-8.678897079656872, -3.027686871954548]|
|id_test|MLP−LoRA|plugin_relative_information_deficit|-0.2782|[-0.46486416964502236, -0.10567096872605479]|
|ood_parameters|BaseQwen−LoRA|allocation_l1|-0.1783|[-0.4732450299287795, 0.11842964541767428]|
|ood_parameters|BaseQwen−LoRA|forward_kl_epsilon_1e8|-6.9954|[-10.906433509930274, -3.1168526071715137]|
|ood_parameters|BaseQwen−LoRA|plugin_relative_information_deficit|-0.1303|[-0.27689432321951324, 0.03373477624817828]|
|ood_parameters|BaseQwen−MLP|allocation_l1|0.6842|[0.4197363737148755, 0.9202163212598891]|
|ood_parameters|BaseQwen−MLP|forward_kl_epsilon_1e8|0.8446|[0.16977541996504114, 1.8499374267690778]|
|ood_parameters|BaseQwen−MLP|plugin_relative_information_deficit|0.2125|[0.03867823054462983, 0.37166568512568227]|
|ood_parameters|MLP−LoRA|allocation_l1|-0.8625|[-1.28227996124677, -0.4653806629929727]|
|ood_parameters|MLP−LoRA|forward_kl_epsilon_1e8|-7.8399|[-11.99800049686137, -3.6726578693171064]|
|ood_parameters|MLP−LoRA|plugin_relative_information_deficit|-0.3428|[-0.5737416832253464, -0.10619288985409768]|
|ood_partition|BaseQwen−LoRA|allocation_l1|-0.0560|[-0.13108787619343754, 0.0013841024723883766]|
|ood_partition|BaseQwen−LoRA|forward_kl_epsilon_1e8|-1.9232|[-3.506641817151938, -0.6148473200670868]|
|ood_partition|BaseQwen−LoRA|plugin_relative_information_deficit|-0.0616|[-0.1267668741479574, -0.005302410407714633]|
|ood_partition|BaseQwen−MLP|allocation_l1|0.2102|[0.15542187145129943, 0.2619787525023422]|
|ood_partition|BaseQwen−MLP|forward_kl_epsilon_1e8|-0.1028|[-0.2195899454684008, 0.012134099496929132]|
|ood_partition|BaseQwen−MLP|plugin_relative_information_deficit|-0.2422|[-0.3016261501130245, -0.15659321354861117]|
|ood_partition|MLP−LoRA|allocation_l1|-0.2661|[-0.3700447093819728, -0.17989486321310816]|
|ood_partition|MLP−LoRA|forward_kl_epsilon_1e8|-1.8204|[-3.4492697804627013, -0.5245297988543873]|
|ood_partition|MLP−LoRA|plugin_relative_information_deficit|0.1806|[0.06174141066188596, 0.27863970366062685]|
|all_24_worlds|BaseQwen−LoRA|allocation_l1|-0.0718|[-0.19322363212834798, 0.05137502578016598]|
|all_24_worlds|BaseQwen−LoRA|forward_kl_epsilon_1e8|-4.8015|[-6.465909031349363, -3.1783562698416707]|
|all_24_worlds|BaseQwen−LoRA|plugin_relative_information_deficit|-0.0904|[-0.16468005569779734, -0.01611434692884437]|
|all_24_worlds|BaseQwen−MLP|allocation_l1|0.5090|[0.40460460533280324, 0.6015555331363261]|
|all_24_worlds|BaseQwen−MLP|forward_kl_epsilon_1e8|0.3759|[0.12263587840044114, 0.7135824417942569]|
|all_24_worlds|BaseQwen−MLP|plugin_relative_information_deficit|0.0565|[-0.011911476173529735, 0.11900044353967598]|
|all_24_worlds|MLP−LoRA|allocation_l1|-0.5808|[-0.741254881070756, -0.417513966045044]|
|all_24_worlds|MLP−LoRA|forward_kl_epsilon_1e8|-5.1774|[-6.938593306307421, -3.4525972075460154]|
|all_24_worlds|MLP−LoRA|plugin_relative_information_deficit|-0.1468|[-0.25039893697327315, -0.0397636117871386]|

闭环在公开上限 2048 下读取查询数 256/512 的完整向量恢复。256/512 是 evaluator 的中间读数，未作为更早截止时间输入策略。该表为固定预算猜测准确率，并非认证输出。原始 Aligned 保留其原生更新节奏，其余六策略统一为初始八次强制观察后每 128 步更新。

|分层|方法|预算|完整恢复/全部|任务合计|类型合计|离线合计|平均总获取|回退/已记录调用|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|eval_id|NativeAligned|256|8/8|1914|134|512|320.0|0/216|
|eval_id|NativeAligned|512|8/8|3787|309|512|576.0|0/320|
|eval_id|AlignedBlock128|256|8/8|1914|134|512|320.0|0/16|
|eval_id|AlignedBlock128|512|8/8|3843|253|512|576.0|0/32|
|eval_id|DNoTypeBlock128|256|8/8|2048|0|512|320.0|0/16|
|eval_id|DNoTypeBlock128|512|8/8|4096|0|512|576.0|0/32|
|eval_id|DTypeBlock128|256|8/8|1503|545|512|320.0|0/16|
|eval_id|DTypeBlock128|512|8/8|3150|946|512|576.0|0/32|
|eval_id|MLP|256|8/8|1903|145|512|320.0|0/16|
|eval_id|MLP|512|8/8|3834|262|512|576.0|0/32|
|eval_id|BaseQwen|256|8/8|1744|304|512|320.0|16/16|
|eval_id|BaseQwen|512|8/8|3472|624|512|576.0|32/32|
|eval_id|LoRA|256|8/8|1850|198|512|320.0|7/16|
|eval_id|LoRA|512|8/8|3686|410|512|576.0|13/32|
|eval_ood_parameters|NativeAligned|256|8/8|1910|138|512|320.0|0/216|
|eval_ood_parameters|NativeAligned|512|8/8|3821|275|512|576.0|0/320|
|eval_ood_parameters|AlignedBlock128|256|8/8|1978|70|512|320.0|0/16|
|eval_ood_parameters|AlignedBlock128|512|8/8|3921|175|512|576.0|0/32|
|eval_ood_parameters|DNoTypeBlock128|256|8/8|2048|0|512|320.0|0/16|
|eval_ood_parameters|DNoTypeBlock128|512|8/8|4096|0|512|576.0|0/32|
|eval_ood_parameters|DTypeBlock128|256|8/8|1482|566|512|320.0|0/16|
|eval_ood_parameters|DTypeBlock128|512|8/8|3269|827|512|576.0|0/32|
|eval_ood_parameters|MLP|256|8/8|1887|161|512|320.0|0/16|
|eval_ood_parameters|MLP|512|8/8|3796|300|512|576.0|0/32|
|eval_ood_parameters|BaseQwen|256|8/8|1744|304|512|320.0|16/16|
|eval_ood_parameters|BaseQwen|512|8/8|3472|624|512|576.0|32/32|
|eval_ood_parameters|LoRA|256|8/8|1865|183|512|320.0|6/16|
|eval_ood_parameters|LoRA|512|8/8|3699|397|512|576.0|12/32|
|eval_ood_partition|NativeAligned|256|8/8|1792|256|512|320.0|0/216|
|eval_ood_partition|NativeAligned|512|8/8|3534|562|512|576.0|0/320|
|eval_ood_partition|AlignedBlock128|256|8/8|1763|285|512|320.0|0/16|
|eval_ood_partition|AlignedBlock128|512|8/8|3463|633|512|576.0|0/32|
|eval_ood_partition|DNoTypeBlock128|256|8/8|2048|0|512|320.0|0/16|
|eval_ood_partition|DNoTypeBlock128|512|8/8|4096|0|512|576.0|0/32|
|eval_ood_partition|DTypeBlock128|256|8/8|1158|890|512|320.0|0/16|
|eval_ood_partition|DTypeBlock128|512|8/8|2798|1298|512|576.0|0/32|
|eval_ood_partition|MLP|256|8/8|1743|305|512|320.0|0/16|
|eval_ood_partition|MLP|512|8/8|3388|708|512|576.0|0/32|
|eval_ood_partition|BaseQwen|256|8/8|1664|384|512|320.0|16/16|
|eval_ood_partition|BaseQwen|512|8/8|3296|800|512|576.0|32/32|
|eval_ood_partition|LoRA|256|8/8|1989|59|512|320.0|2/16|
|eval_ood_partition|LoRA|512|8/8|3982|114|512|576.0|4/32|
|all_24_worlds|NativeAligned|256|24/24|5616|528|1536|320.0|0/648|
|all_24_worlds|NativeAligned|512|24/24|11142|1146|1536|576.0|0/960|
|all_24_worlds|AlignedBlock128|256|24/24|5655|489|1536|320.0|0/48|
|all_24_worlds|AlignedBlock128|512|24/24|11227|1061|1536|576.0|0/96|
|all_24_worlds|DNoTypeBlock128|256|24/24|6144|0|1536|320.0|0/48|
|all_24_worlds|DNoTypeBlock128|512|24/24|12288|0|1536|576.0|0/96|
|all_24_worlds|DTypeBlock128|256|24/24|4143|2001|1536|320.0|0/48|
|all_24_worlds|DTypeBlock128|512|24/24|9217|3071|1536|576.0|0/96|
|all_24_worlds|MLP|256|24/24|5533|611|1536|320.0|0/48|
|all_24_worlds|MLP|512|24/24|11018|1270|1536|576.0|0/96|
|all_24_worlds|BaseQwen|256|24/24|5152|992|1536|320.0|48/48|
|all_24_worlds|BaseQwen|512|24/24|10240|2048|1536|576.0|96/96|
|all_24_worlds|LoRA|256|24/24|5704|440|1536|320.0|15/48|
|all_24_worlds|LoRA|512|24/24|11367|921|1536|576.0|29/96|

闭环配对差及每世界向量保留于 primary_paired.json；方向为左减右的完整恢复率，统计单位仍为世界。Native 与 Block128 的差异包含更新节奏，不能归因于模型蒸馏。单组、零参考情形的 D-Type 公共结构判断可能使两个 D 基线构造性相同。

R16 的固定置信度诊断复用三个已声明闭环世界，未增加独立样本。只在独立严格门给出区间认证时停止；上限时弃权及评分猜测分开。此处 n=3，不能验证极小风险、渐近最优性或普遍终止。

|方法|认证/全部|错误认证/全部|上限弃权/全部|失败|平均在线成本|平均认证门墙钟秒|
|---|---:|---:|---:|---:|---:|---:|
|NativeAligned|3/3|0/3|0/3|0|597.3|0.0461|
|AlignedBlock128|3/3|0/3|0/3|0|512.0|0.0444|
|DNoTypeBlock128|3/3|0/3|0/3|0|554.7|0.0445|
|DTypeBlock128|3/3|0/3|0/3|0|896.0|0.0923|
|MLP|3/3|0/3|0/3|0|1066.7|0.1184|
|BaseQwen|3/3|0/3|0/3|0|1066.7|0.0874|
|LoRA|1/3|0/3|2/3|0|1493.3|0.2001|

训练外参数 (.85,.60) 位于 T1 训练参数范围内，是留出组合而非范围外推；该参数在既往研究出现过。结果限于合成通道，不能外推为自然语言、真实用户或 Web 查询能力。没有根据测试结果选择 checkpoint、提示词或更有利的分层。

图为 artifacts/analysis/accuracy_vs_budget.{png,pdf} 与 offline_quality_vs_inference_cost.{png,pdf}。推理延迟图仅显示已加载模型的调用成本；端到端数据生成、训练、加载及评测成本见 COMPUTATIONAL_COST.md。

## 最终解释核对补充

七种方法在两个预定预算均24/24完整恢复：这批固定预算结果存在天花板，不能建立训练收益、等效或非劣性。停止诊断仅三个复用世界；LoRA两次2048上限弃权保留在分母及成本中，不能仅对其一次成功报告平均停止成本。

未微调Qwen接收同一冻结输入与输出契约，但prompt没有完整说明环境数学目标，应解释为初始化对照，不能当作充分任务提示优化的强零样本基线。事后的归一化解析分析仅使用保存字符串，不修改主结果或闭环轨迹，详见audit/PARSER_SENSITIVITY.md。当前配置的研究判断及全部限制见FINAL_DECISION.md。
