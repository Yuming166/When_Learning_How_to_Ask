# T1：Qwen4B 查询策略训练报告

## Material Passport

2026-10-31，独立开发分支 training/qwen4b_policy_t1。当前状态：**单次 LoRA 科学训练已完成；独立策略效果评测另见评测报告。** 训练完成不代表查询效果改善。

## 已完成的训练前检查

- 本地 Qwen3.5-4B，实际模型类 Qwen3_5ForConditionalGeneration，含 LoRA 总参数 4,555,497,984，可训练 LoRA 参数 16,232,448。
- 冻结 BF16 基座及视觉模块；PEFT LoRA 适配器为 FP32，混合精度记录明确。
- 短70-token 与满1024-token 两次技术反向传播均通过，均为零优化更新；保存的适配器张量读取后逐项一致。它们是两次技术 forward/backward，不是零计算，也不是两次策略生成。
- 长 smoke 峰值 allocated 12,415,349,760 bytes，reserved 13,274,972,160 bytes；使用一张空闲4090，保留现有 GPU6 推理服务。
- 96 个新开发世界、1536 个教师状态；训练64世界/1024状态，验证及三种测试各8世界/128状态。学生消息严格白名单，无隐藏答案、真实可靠率、隐藏组类型、身份或评分。
- 完整模板的序列长度362–417tokens，未截断。损失仅覆盖百分比分配答案，prompt 全部 -100。两项有限状态碰撞/浮点量化边界在 DATA_LEAKAGE_AUDIT.md 中保留说明，没有改数据或重跑。

## 已冻结的拟合

一次 LoRA SFT：rank8，alpha16，dropout0，单卡batch1，累积8，lr2e-4，梯度裁剪1，1epoch/1024微批次/128优化更新。训练使用连续教师分配量化成的整数百分比 JSON 作为目标；验证仅诊断，无测试或验证检查点选择。保存 adapter，不合并基座。

一次 MLP：69→64→64→10，9,290 参数，训练集归一化，连续教师软目标前向 KL。已完成 200 个固定epoch，用时 4.118s，CPU 3.760s，训练KL=0.059083。该KL与Qwen的token交叉熵不可直接比较。

原生 Transformers 后端缺少 causal-conv1d/flash-linear-attention 加速内核，实际走参考实现；训练保留了这个执行条件。种子固定，但 SDPA 反向内核没有逐位确定性保证，不把固定种子称作逐位复现证明。

## 最终训练结果

单次运行完整完成：1024 个微批次、128 次优化更新，0 次重跑。训练样本等权 token-CE 均值 0.249242，按目标token加权均值 0.251807；验证目标token加权CE 0.207779，共 3516 个验证目标token。训练目标token总数 28093。CE包含JSON标点及格式token，不是分配误差或恢复准确率。

运行墙钟 1820.091s（30.33分钟），进程CPU 1822.348s；峰值 allocated 10,705,712,640 bytes（10.706GB），reserved 17,439,916,032 bytes（17.440GB）。墙钟包含模型加载/分词/训练/验证及保存；不把加载时间再次相加。

最终 adapter 位于 artifacts/adapters/final，496 个保存张量均为语言模块 LoRA；248 个 LoRA-B 张量全部从零初始化变成非零，确认实际发生权重训练。基座未保存或合并。完整计数、梯度与阶段损失见 artifacts/training/steps.jsonl 和 execution.json；核验见 audit/ADAPTER_VERIFICATION.json。

## 质量解释

LoRA 的目标是模仿冻结教师在可观测状态下的分配，不能从训练/验证CE推断其超过教师或更节省查询。MLP使用连续分配KL，Qwen使用百分比JSON的token-CE，二者损失不可直接排名。共同的离线分配误差、无效输出、固定预算恢复率及计算成本见 QUERY_POLICY_EVALUATION.md、COMPUTATIONAL_COST.md，最终研究判断见 FINAL_DECISION.md。

未微调 Qwen 是相同输入契约的初始化对照；冻结prompt没有完整说明环境的数学目标，因此不把它称为经过充分任务提示设计的强零样本基线。LoRA相对它的收益可能包含格式遵循和标签映射学习；不能据此证明训练优于强提示或训练是必要的。MLP和教师是判断实际价值的重要对照。

## 完整评测后的结论

全部预定评测完成，无重试或额外拟合。格式合规率改善，但汇总离线模仿误差未改善；固定预算结果出现全方法天花板，三世界停止诊断中LoRA两次上限弃权。当前配置的技术完成与研究NO-GO分开记录，详见FINAL_DECISION.md。没有基于这些结果继续训练或改动策略。
