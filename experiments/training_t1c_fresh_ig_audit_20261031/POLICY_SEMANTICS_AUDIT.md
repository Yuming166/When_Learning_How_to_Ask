# Policy semantics audit before T1c

## Material Passport

只读审计T1a/T1b/T2 v02的冻结源码与结果。本报告在新世界抽样前完成，不重跑历史训练/科学评测，不读取旧私有seed。哈希见INPUT_SNAPSHOT。T2 v02的三次历史CPU拟合属于别的已完成实验，本轮没有调用它的训练/神经模块。

## 必须纠正的更新频率

T1a及T1b中的KL都在首次t=2d=8后按 t_next=t+ceil(sqrt(t+1)) 更新。B32的真实轨迹日志为 **8,11,15,19,24,29**。冻结Fused-Info也是相同clock；不是每32步。更新t表示已完成观察数，在下一查询前计算。

T2匹配臂才由evaluate.py `_instrument`覆盖为t_next=t+32：初次t8，随后40、72等，因此B32只有t8一次规划。Native-Fused-Original保留sqrt。用户提出的字面“每32步vs每步”无法把T1a直接放进32步格；T1c因此将实际sqrt作为主held-target水平，另外做真正的32步桥接。

## 精确定义

|策略|后验/目标刷新|信息目标|实际自由动作|类型与成本|终局语义|
|---|---|---|---|---|---|
|T1a AnalyticReuse|sqrt clock；每次完整fused后验32阶|连续备择KL成本规划|最大累计目标欠额|task/type均可，type含噪s=.8|原T1a为严格停止成本；T1b包装下为统一joint-MAP固定预算猜测|
|T1b Fused-Info|同sqrt clock|I(theta;Y)最大，one-hot target|累计目标欠额，可能追赶旧target|相同动作/观测/收费|T1b统一joint-MAP，预算末单独certificate|
|T1b Fresh-IG|每个非forced轮重算当前后验和IG；原KL骨架仍按sqrt更新但其候选被忽略|相同theta互信息，数值实现为dense概率矩|直接argmax当前IG，不执行原跟踪动作|相同动作/观测/收费|同T1b decoder和预算末gate|
|T2 matched Fused-Original|t8后每32轮，原fused后验|原KL目标；尚未采用本线T1a加速|累计目标欠额|相同task/type；M由R和该世界alpha决定|cap6144路径中的GLR最大似然预算读数，非给策略的短截止|
|T2 matched Fused-Info|同32轮匹配clock|同theta互信息one-hot|累计目标欠额|同T2可用观察|同GLR读数；早认证时吸收认证答案|

T1b Fresh-IG不仅改变刷新频率，还把跟踪执行改成直接选样，并使用等价数值IG的dense实现及1e-12稳定tie。冻结Info用log/KL稳定公式和numpy argmax。T1b单测验证有限状态上两种IG值一致，但在数值ties处不能宣称所有历史的逐位同轨。T1c专门留出same-backend直接执行桥与实用dense版本，避免混归因。

T1b中的Fresh-IG实际维护了未被执行的KL target，并计算其他未选macro候选；不是其最低可实现计算成本。T1c Fresh-IG-Lite只保留当前belief、dense IG、原forced动作和直接选样。6组工程流（3分组×有/无校准）各64次literal响应与T1b原Fresh-IG逐动作相同，且KL调用从非零降为0。这是有限接口/等价回归证据，不是全历史证明。

## 分配空间的额外混杂

KL求解器只表达组内事实均匀的task目标，IG可选单个事实one-hot。即使物理action space、后验、clock与executor相同，原2×2仍是两种完整分配规则的比较，不是固定target可行类后只改数学目标。T1c增加IG-Group两臂，以平均组内IG选择一个组格式的均匀目标，或单独type目标；其convex action simplex与KL归一化a/b/c空间一致。报告同时保留原规则和同target空间两套2×2，绝不把组内自适应收益误记成纯目标优势。

## 观察边界

上述fused策略均使用全部task counts、含噪type reports、真实labelled calibration及已知分组。theta/z在后验中枚举的是假设；不接收真实隐藏值。T1a/T1b受限worker只获得公共R、cap及原reset/calibration/query/type RPC，父进程持有真值/生成率/seed；评分误差仅在终局父评测器追加。Fresh-IG没有额外API、免费type查询或真实z。

T2采用可信内置回调边界而非本线Landlock隔离；其core.validate_state是严格schema，包含合法后验摘要和观察count，排除隐藏真值/率/seed。v02的1e-12边际roundoff保护仅用于学生接口；冻结FO/FI仍调用原fused估计。未发现这几个冻结基线读取隐藏评分来选动作的代码通路；这不是对任意第三方插件或全部运行环境的安全证明。

可用观察权限相同不等于每步及时使用：有意hold住posterior/target是cadence处理，而非给Fresh免费新增观测。所有task/type费用、2M校准费用需要逐臂相同计入。

## 历史结果不能直接合并

T1b：96个独立世界，固定p=.85/.75、q=.60、alpha0/3、R16，d4、三分组；B真正是episode截止；统一order32完整theta后验joint MAP decoder。全部2592固定预算猜测均未严格认证。

T2：24个主世界，每个R16/64/256相关重复，共72条/方法；ID/率留出/分组留出/alpha留出各6世界，参数网格不同。B32/64在teacher-only预算开发后冻结，是cap6144严格停止轨迹的中间GLR读数，不作为短截止输入；较早严格认证可以吸收。故43/72 vs35/72不是对T1b 71/96 vs80/96的同分布复现。不能把72相关R读数称72个独立世界，也不能由排序不同推断某方法被证伪。

## 旧96世界配对核查

|预算|Fresh独赢|KL独赢|都成功|都失败|Fresh−KL|分层配对bootstrap开发区间|
|---|---:|---:|---:|---:|---:|---|
|16|0|0|39|57|0pp|[0,0]pp|
|32|15|6|65|10|+9.375pp|[+1.042,+17.708]pp|
|64|8|0|84|4|+8.333pp|[+4.167,+13.542]pp|

B32的传统discordant-binomial双侧McNemar参考值为0.07835，B64为0.0078125。它要求公平且可交换的discordant signs；固定异质单元下弱总体零假设的校准未建立。分层bootstrap与该参考p值条件不同，不挑一个更有利的统计量宣布确认。B64是辅助预算，不能替代主B32。所有结果为后验开发审计，不是新独立确认；完整计算见HISTORICAL_PAIRED_AUDIT.json。
