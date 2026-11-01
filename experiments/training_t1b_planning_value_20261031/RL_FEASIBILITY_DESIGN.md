# Residual Actor-Critic feasibility design

## Material Passport

仅设计，尚未执行；本文件不授权训练。T1b结果决定是否值得后续T2，任何GO也不是已训练RL成功。旧Qwen-LoRA、旧MLP、新NQA与本残差RL是不同实验，负结果和协议均保留。

## 策略与优化目标

保留冻结联合后验、AnalyticReuse和独立严格停止器，网络只选择KL/IG/TYPE/TASK四个宏动作；强制轮屏蔽策略选择。共享组/事实编码和置换不变池化适合不同合法组大小；采用轻量Actor-Critic，不调用语言模型。最初不学习rate posterior或STOP，也不输出所有查询比例。

有限预算终局reward仅为1{完整joint-theta解码猜测正确}，固定B下没有额外查询惩罚。训练评测器在episode结束后才能给reward；真实参数/真值可计算reward，绝不能成为策略feature或中间正确性信号。若将来允许提前停止/变动总预算，需另行固定成本约束与目标，不能混用N/R和固定预算准确率。

先用无reward shaping的终局目标。若稀疏reward确实阻碍学习，可研究time-indexed potential F_t=gamma Phi_(t+1)(s')−Phi_t(s)，设终局Phi_B=0，使折扣累积shaping只差与动作无关的初始势常数；应在固定B、gamma和状态定义下逐项验证。每步熵下降不能直接当等价reward。PPO或其他Actor-Critic只是候选优化器，没有已安装/已运行的训练后端或超参数结果。

## 合法状态

原完整观察账本在iid模型下支撑belief与clock的Markov描述；网络采用摘要则是信息压缩，不自动仍为充分Markov状态。候选摘要包含：

- 公共d、分组、eta、已知s、R、M、B、t和剩余预算；
- p/q后验均值、方差、协方差及联合theta MAP概率/熵；
- 每事实theta边际不确定性、两格式任务count/强制count；
- 每组大小、z边际不确定性、type购买数及回答计数；
- 当前KL权重、candidate动作身份、虚拟cumulative与actual欠额、距离下一更新/forced轮。

统计只来自当前可见历史。四个宏可能映射到同一个物理动作；训练接口按固定canonical规则屏蔽重复宏，不能把重合标签当不同决策效果。未知真实p/q/z/theta、reward、评分和seed不得进入。尤其禁止直接把本轮评测JSON中的整段estimation_history作为输入：父评测器事后追加的p_error/q_error/type_errors/theta_errors属于标签，必须用schema白名单排除。world/episode/source ID、role索引、未来回答也排除。

## 训练和独立开发划分（未执行的资源提案）

如果T1b达到GO，再冻结一个有界T2：最多4096个train worlds、512个validation worlds、512个新的independent development worlds，世界之间不共享潜在响应流或校准样本；按world而非trajectory state拆分。train可多轮策略更新，但验证/开发不能用于拟合或在线reward shaping。所有来源为新Exact开发namespace，既有T1b世界只作已用的开发证据，不能改名独立验证，更不能读保留的最终benchmark holdout或Phase3确认seed。

候选训练配置p=.70/.80/.90，q=.50/.60/.65且q<p，分组[1,3]/[2,2]/[4]，alpha0/1/3，B24/32/64，R16、s=.8、eta=.05。世界数是未来上限，不是本轮已生成数据。独立OOD预先固定未见率(.77,.53)/(.88,.66)，分组[1,1]/[3]/[1,2]（d2/3,G<=2）、alpha2/6、预算20/48/96、已知s=.65/.90，分别测单因素和联合变化。只有接口支持不构成泛化效果。

主架构/训练停止只用train+validation；评测世界结果不能触发再训练后继续沿用同一“独立”标签。所有预处理/scaler只拟合训练集，预算/clock合法但不能借编号泄漏实例。

## 必要基线与资源账本

至少比较冻结AnalyticReuse、Fused-Info、Fused-D-RRC-Type、Fresh-IG、Task-Only、Type-Then-Task、Fixed-KL-IG、同目标Recovery1和Lookahead2；全部同一允许观察、公共预算、forced schedule、decoder和证书。若策略改变更新clock，必须有相同clock的无训练对照。若二步规划已足够快且效果最好，RL需证明额外收益或更低总计算，不能只胜未经T1a加速的旧teacher。

未来训练采集总上限4096*64=262144 online actions，验证/开发按最大B96保守计额外最多98304，总online上限360448；训练、基准KL、后验、优化器更新、奖励计算、验证/开发均计入CPU和获取成本。暂拟无GPU、最多8 CPU-hours/2小时wall（最多4核）、峰值内存上限4GiB、1个主模型与1个必要消融；不是现在可消耗资源。未授权大规模调参、并行候选搜索、Qwen或paid API。包含训练成本后再算部署N个episode的盈亏平衡，不只计网络forward。

## 统计可靠性和边界

固定预算猜测不具原风险保证；严格回答仍需完整count的原certify_stop。任何只依合法过去信息的RL选择可符合原anytime错误认证证明的predictability要求，但不会自动获得几乎必然完成、有限期望停止时间或渐近最优查询复杂度。

原forced blocks继续执行。**残差宏覆盖原tracker选出的动作后，原diagnostics中O(sqrt(t))欠额bound不能直接继承**；保留这些字段只供账本核对。没有证明新的allocation满足原Theorem1的tracking/consistency/vanishing-error前提。若未来研究固定置信RL，需要单独证明或实测其完成率/截尾行为，不能用网络置信或熵替代证书。

Exact的iid已知s模型条件不能直接迁移Mechanism/Natural；需要对那些通道另做模型有效性与经验可靠性评价。不能将一个固定先验下的训练成功当真实语言Agent有效。

## T1b之后的选择

若T1b收益只来自Recovery1同目标贪心、Fresh-IG更新频率或简单type日程，优先采用无训练方案，不启动RL。若LA2带来稳定额外恢复增益，但开销显著，则残差Actor-Critic有可验证目标：在保持该收益的同时减少多步树计算，或学习更远期类型购买。若T1b缺乏清楚信号，REVISE/NO-GO意味着停在当前有界证据，不自动扩大预算或开始PPO。
