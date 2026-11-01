# T2b 冻结策略对齐审计

源代码与技术集成审计通过。此结论允许进入预先冻结的匹配开发评测，不代表神经或混合策略已通过查询非劣、认证或部署成本门槛。

审计范围是同模型家族、共享上下文的源代码/证据核查与固定可观测夹具验证；不是盲审、跨家族复核、形式化证明或独立科学确认。未读取私有种子、真实参数或答案文件，未采样开发/确认世界，未训练、调用模型服务或使用 GPU。T1a、T1b、T2 历史目录均只读。

## 可复用的精确接口

原接口为 `t1a.solvers.Solver('AnalyticReuse')(partition, p, q, alpha, type_accuracy=None, eta=.05, tolerance=2e-7, max_iterations=120)`。这里的“精确接口”指逐字复用被冻结实现，数值结果仍是浮点诊断。

新适配器在 [t2b/reuse.py](t2b/reuse.py)：

- `AnalyticReuseSolver().solve(...)` 与 `__call__(...)` 委托原接口；保留原计数器与 solver CPU 账本。
- `.target(observable_state)` 直接调用冻结的 `t2.core.teacher_target(state, solver=self)`；保留状态白名单、两次收紧容差尝试、可行性/缺口验收及物理动作展开。
- `.stats`、`.cpu`、`.last_fit`、`.diagnostics()` 可供主评测记录。失败向上传播，不进行隐性回退。

适配器仅以私有模块命名空间载入原 `t1a/solvers.py`，跳过其只用于添加 vendor 路径的 bootstrap。T2 原 bootstrap 先建立依赖路径，随后检查 solver 与实际载入的系数源码哈希。没有全局 monkeypatch、重复 vendor 覆盖、目标函数改动、额外平滑或权重下限。主冻结收据仍应绑定全部依赖；此适配器内的两个哈希不是完整环境冻结的替代品。

|对象|SHA-256|
|---|---|
|T1a 原 `t1a/solvers.py`|`89bcdc606e105c2c49c585ab960b94378ae05aa802a3addd4a531011e99a3160`|
|共同 `phase2a/coefficients.py`|`a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f`|

## 源码合同与差异

|维度|核查结果|匹配评测必须保持的条件|
|---|---|---|
|合法观察|Fused-Original、Fused-Info 的 `Fusion._estimate` 使用任务计数、付费 type 回答、标记校准和公开组；T2 学生状态是其严格白名单摘要|不把世界标识、生成种子、真实 theta/p/q/z、未来回答或正确性传给 planner。controller 自身使用的 GLR 只能来自已经支付的历史|
|后验|共同 `phase2e.estimator.posterior(..., order=32, plugin=False)`；枚举离散 theta/z，有序率域使用固定 Gauss–Legendre 近似|学生、KL 与 IG 使用同一观察前缀下的相同后验；不能把 order-32 近似称为精确贝叶斯积分|
|浮点适配|T2 `observed_state` 只对概率越界不超过 `1e-12` 的复制边际进行截断，原 fit 保留|复用原适配，不扩宽容差，不修改 p/q、原后验、solver 或 gate|
|KL 目标|T1a `Model`、`optimized` 保持原每组 a/b/type-c 成本与组备择信息约束；只向量化有序二项投影/行计算，并复用固定方向充分统计量|alpha 为每条参考流长度/R；径向修复保持校准项固定。AnalyticReuse 不读取缓存答案或 WarmStart 支持池|
|KL 验收|T2 `teacher_target` 与原 aligned 使用同一 t 依赖容差：`min(1e-4,1/(t+1))`；最多两次求解，relative gap 与 minimum information 同门槛|保留当前估计率下的 K、缺口与约束；它们不是未知真实率下的 oracle 成本，更不是停止证书|
|IG 目标|`FusedInformation._update` 对联合 theta 与下一回答的单位成本互信息取最大 log-score，产生 one-hot target|复用 `information_scores` 的完整 latent fit，不能仅凭 theta/z 边际重建 IG，也不能混同 KL 最小信息目标|
|动作与成本|共同物理动作是 `2*d` 个任务形式和 G 个付费 type；所有在线动作单位成本，校准两条流合计 `2*M`|保留 task/type/offline 分项，额外回退计算也计入成本|
|探索与跟踪|`TheoryAlignedTracking.next/observe` 使用平方块强制探索和累计目标欠额，固定 argmax tie|初始 `2*d`，随后统一每 32 次回答重规划。保留 cumulative、实际计数和 forced 前缀；切换 planner 不重置 tracker|
|认证停止|T2 每 32 次回答检查 log-GLR；原浮点越界预筛通过或到 cap 时调用同一严格 `certify_stop`|cap=6144，风险 R 相同；认证输出只由严格 gate 给出，学生/风险启发式不能认证。所有 cap 弃权保留|
|中途预算读数|T2 B=32/64 是固定置信轨迹上的评分读数；提前认证后吸收该答案|与已知有限 horizon 的 T1b 固定预算政策分开报告，不能合并两种目标或样本|

源位置（均为只读）：

- T1a `t1a/solvers.py:16`（信息模型）、`:83`（LP）、`:101`（优化与径向修复）、`:147`（原 solver 分支）。
- T1a `t1a/strategies.py:12`（只替换求解器）、`t1a/policy.py:29`（原闭环与 gate）。
- 共同 Phase2e `phase2e/estimator.py:47`（后验）、`:67`（互信息），`phase2e/strategies.py:10`（融合）、`:28`（IG）。
- 共同 Phase2b `phase2b/aligned.py:111`（初始状态）、`:129`（强制探索）、`:171`（容差与 KL 更新）、`:262`（累计目标跟踪）。
- 冻结 T2 `t2/core.py:16`（白名单）、`:49`（状态）、`:85`（展开）、`:101`（KL target）、`:113`（外部注入的匹配 scheduler）。
- 冻结 T2 `t2/evaluate.py:29`（cap/check/cadence）、`:76`（匹配基线 instrumentation）、`:275`（动作记录与检查）、`:300`（严格 gate 与预算读数）。

以上共同文件位于 `/home/gaoym/When_Learning_How_to_Ask_phase2e/experiments` 对应阶段目录。T1a 的 vendor、T1b 的 frozen_t1a/vendor 与 T2 实际使用目录之间，以下六个文件已逐字哈希核对一致：coefficients、aligned、log_glr、certified、estimator、strategies。结果如下，未仅依赖文件名判断相容性。

|共同文件|SHA-256|
|---|---|
|phase2a/coefficients.py|`a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f`|
|phase2b/aligned.py|`67bdf86cbd21a81bde81fde981b9c00308f35d2f911af766fbd28939ae5b4ab0`|
|phase2b/log_glr.py|`2e24081b34fa2b783b85fe5d6d73a3e52574e5466f0fe1eb88ca0513de1233ba`|
|phase2d/certified.py|`162fe61943bdebf2b297cdca914a734e9b0befcf66939c800a00a9a35820130c`|
|phase2e/estimator.py|`a161629bd83ea96e008f7e1ad3899b0fe9fd04023a97f12c78cc36bd199b56a7`|
|phase2e/strategies.py|`9b00e02cf8a6c7efd7129130566ea9ac6dba7a5a011ff8dca5dd5e8ace109f52`|

## T1b 的适用边界

T1b 确实复用同一后验、KL solver、探索与计数，但其 residual controller 可以在每次回答后计算新的 root belief 并覆盖 primitive action。Fresh-IG 是这种逐次重新决策规则，不等于 T2 每 32 步更新一次的 Fused-Info。两步前瞻与 Recovery-1 还使用完整向量终局 MAP utility、已知剩余预算和候选宏动作，目标不同于固定置信最早认证。

T1b `t1b/policy.py:24` 固定购买满 B 次，然后共同 joint-MAP 解码并做一次终局 gate；T2 使用每 32 次的 profile GLR 和可变提前停止。T1b `Belief.ig()` 的 direct KL 算法也不同于共同 `information_scores` 对极小信息使用 log-domain 的实现；不能不加说明地替换。T1b 的历史恢复数与 T2 的中途读数不可合并排名，T1b 的后验/预测内“exact”只针对有限 quadrature belief，不是连续率积分。

## 计时的可比较范围

T1a 报告 3.819× 是其同一次开发闭环中的完整 trajectory CPU 比值（worker 启动另记）；T2 报告约 20× 是 estimation + planning + inference 分量 wall 比值，排除了 GLR/gate/environment，也另有 cold load 与训练费用。因此两者不能相除或跨轮排名。

T2b 应在相同 roster、机器、线程限制、cadence、公共 cap 和 gate 下，分别保留完整 path CPU/wall、后验、规划、学生推理、风险判断、fallback、GLR、gate、环境与冷加载账本。嵌套分量不得重复相加。训练成本已经发生，但仍须报告部署摊销。共享世界的三个 R 是配对相关条件，以完整世界为聚类单位。

## 固定技术夹具验证

[tests/test_reuse.py](tests/test_reuse.py) 的 6 项测试通过，见 [logs/reuse_tests.log](logs/reuse_tests.log)，运行约 1.38 秒。没有抽样的科学世界、正确答案、模型权重或 provider 调用。

1. 原模块与系数来源相同，历史 vendor bootstrap 没有覆盖 T2 依赖。
2. 四个字面固定输入覆盖 `[4]`/`[1,3]`/`[2,2]`、alpha=0/.5/3 和 type 不可用情形：归一化 a/b/c 与原 solver 在绝对 `2e-11` 内相同，K 比值在小数 10 位内为 1，通过同一缺口/可行性界；无缓存命中或 fallback。
3. `target` 与冻结目标展开一致，输入状态不变，调用数等于记录的容差尝试数。
4. 额外私有字段在求解前拒绝，额外 solver 私有参数也拒绝。
5. 一个明确的非随机、动作专属二进制序列技术回放执行 128 次动作、4 次规划：与匹配 32 步的原 Fused-Original 在每步的动作、回答、forced 标志、权重、最终 task/type/校准成本、计数、type 回答和最终 GLR 完全一致（权重按浮点容差比较），严格 gate 的全部非计时输出相同。

首轮技术测试错误地比较了 gate 内实际 wall timers，导致一项失败；科学输出和动作已一致。只将 `timings_seconds` 排除后重跑 6 项全部通过，算法、夹具和验收容差未改变。这是测试合同修复，不是科研试验重试或样本替换。

夹具验证说明适配器正确接通现有数学与调度，不能证明所有浮点输入的分配唯一、无限轨迹逐字相同、正式查询非劣或旧定理的有限精度实现。T1a 自身观察到的旧世界轨迹相同保留为历史证据；T2b 的新世界必须如实记录任何 tie/数值差异、弃权与失败，不能强制沿用教师动作来制造身份一致。

## T2b 共同后验控制器的接线复核

另行检查了本轮根代理写入的 `t2b/controllers.py` 与 `t2b/evaluate.py`。所有方法由同一 `Scheduler` 执行；统一调用 `observed_state` 获得白名单 state 和从相同观察计算的 raw quadrature fit。额外的 raw fit 是合法观察所导出的离散假设/率网格后验，不是环境真值；只有无训练互信息计算读取它，冻结神经网络仍只接收 state。

`Controller.info` 与冻结 `FusedInformation._update` 逐项相同：对 `information_scores(fit, groups, known_s, True)` 做同样的有限检查，使用同样的 `np.argmax` tie，输出同样物理顺序的 one-hot target。重用同次后验避免重复估计，没有改变目标。`Fused-Original-Cold` 调用原 `teacher_target`，其估计率/类型、容差、两次尝试、验收和展开与冻结原 `_update` 同合同；将原 sqrt cadence 改为预定 32 是本轮匹配条件，不能把此基线称为原 native cadence 的逐字复现。

新 evaluator 将整个 controller 调用（包括其内部学生、风险判断、fallback、白名单检查等）计入父级 `inference` wall 字段。因此本轮该字段名称不表示纯神经 forward；比较 estimation + planning + inference 时覆盖全部 planner/controller 计算，controller 自身分项为其中的嵌套测量，不能再次相加。最终全轨迹 CPU/wall 还包含 GLR/gate/环境等。单条路径冷加载仍须由 driver 另外记账。
