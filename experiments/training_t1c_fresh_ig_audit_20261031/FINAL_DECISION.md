# T1c — Final research decision

**Fresh-IG实用候选：GO（预注册开发门槛）；RL训练：NO-GO_TRAINING_ADDED_VALUE_UNESTABLISHED。本轮已经停止，不自动追加确认、RL设计实验或训练。**

## Evidence scope

本报告来自一个有界、独立的新development批次。没有确认世界、Qwen调用、神经训练、RL更新、PPO或Actor–Critic；没有改写T1a/T1b/T2历史结果、基准生成器或Natural。预先规定B32为主预算，B16/B64为结构/辅助预算。96个世界各重复所有预算和策略，不能把288个预算读数或3456条路径当作独立世界。

协议、配置、依赖、测试和输入快照在新开发entropy生成前已有哈希绑定；runner误用旧目录名，漏列六个本地t1c模块。原freeze未被补写，模块没有在运行后改动；事后hash和早于启动的mtime只能提供支持证据，不能补成预先的完整源码承诺。见[PROVENANCE_DEVIATION.json](PROVENANCE_DEVIATION.json)。本批仍是开发证据。

## Primary result

B32新96世界：Lite完整恢复79/96，原KL-Block 68/96，KL-Fresh 69/96。Lite−KL-Block=+11.46pp [+4.17pp, +19.79pp]；Lite−KL-Fresh=+10.42pp [+3.12pp, +17.71pp]。旧T1b的+9.375pp仅为历史开发信号，本批独立结果完整保留，不能择优合并。


|预定Fresh候选门槛|实际|
|---|---|
|相对KL-Block点差>=3pp且区间下界>0|+11.46pp [+4.17pp, +19.79pp]|
|相对KL-Fresh点差>=0且区间下界>=0|+10.42pp [+3.12pp, +17.71pp]|
|全部预算完成、无非法路径|True|


## What has and has not been established


|问题|本轮证据与边界|
|---|---|
|统计估计|共同终局NLL/Brier/pq误差已报告；不同查询历史的后验质量不等于一个新估计器更好。|
|有限预算信息获取|Lite−原KL +11.46pp [+4.17pp, +19.79pp]；Lite−fresh KL +10.42pp [+3.12pp, +17.71pp]。仅此网格开发结果。|
|纯刷新解释|KL刷新 +1.04pp [-4.17pp, +6.25pp]；原IG刷新 +7.29pp [+0.00pp, +14.58pp]。不由策略名字推断。|
|信息准则解释|共同tracker的fresh IG−KL +9.38pp [+3.12pp, +16.67pp]；同target空间 +2.08pp [-5.21pp, +9.38pp]。|
|在线/总获取成本|每条固定B路径的总在线与预购校准成本相同；不能从恢复率直接声称节省到达同一可靠度的查询。|
|计算时间|B32 Lite CPU 10.391s；KL-Block 14.934s；KL-Fresh 41.656s。这是worker轨迹计时，父CPU单列。|
|认证停止|全部3456条终局证书0、错误证书0；3456条未认证。正常拒绝不能称数值失败或可靠停止成功。|
|学习必要性|未训练任何策略；门槛逐项见RL_ADDED_VALUE_ASSESSMENT，不把事后oracle或特征关联当部署收益。|


具体归因结论：原KL不是每32步更新；把KL改成每步后仍只有69/96，Fresh-IG优势并非仅由该clock假设解释。相同tracker下fresh单事实IG为78/96；把IG也约束到组内均匀target后降为71/96，对fresh KL的差区间跨零。因此支持有限预算下这一完整实用分配规则的开发价值，尚不支持“IG数学目标本身普遍更优”。

终局theta信念NLL/Brier改善，但p的平均绝对误差没有改善；并非全面的可靠性估计突破。Lite相对原sqrt KL的完整worker CPU比约1.44×，相对每步KL约4.01×；原KL对照上未达到2×完整路径加速。类型熵二分的低熵bin为0/96；廉价Belief-Gated在B32也为79/96、逐世界成败相同，且计算更贵。没有建立需由RL利用的稳定额外收益。

## Research disposition

保留AnalyticReuse作为冻结理论驱动KL基线，保留Fresh-IG-Lite作为本轮被明确审计的有限预算候选；是否推进由上方门槛结论决定，不能自动解释为确认授权。原Fused-Info、tracked IG、直接IG及组均匀IG分别报告，不能互相替名。

对WWW材料，本轮可提供带完整分母和限制的有限预算开发附录/机制分析。它不支持加入“训练带来收益”的贡献，也不证明KL渐近理论错误。没有真实语言环境迁移证据；不把Exact上的数值结果写成Natural Agent有效性。

源码hash漏列是保留的审计缺陷，不能把这批称为完整源码预承诺确认。协议中的设计、阈值和预算没有随结果修改；不因该记录缺陷重抽有利世界。旧T1a/T1b全public receipts及只读T2输入已再次核验。

全部六项交付及机器可读配对/成本/验证凭据均在本目录。没有开启下一阶段。

区间为预定12个单元内、以世界为单位的20000次配对bootstrap百分位区间，seed42017。每单元仅8世界，是固定网格开发不确定性；未作多重比较校正，不宣称总体显著性、确认性发现或普遍优越性。各预算沿用同一批世界；指标和比较不能当独立证据相加。

所有策略始终购买至B，使用同一个order32数值积分联合后验和完整theta向量joint-MAP最终猜测。目标后验不是精确连续后验。末尾另行调用冻结Fraction/Decimal严格gate，覆盖全部task/type/calibration；其范围限于原iid、已知s及已审计算术/模型假设。固定预算恢复率不是认证正确率，不证明delta-correctness、固定置信成本或渐近最优。
