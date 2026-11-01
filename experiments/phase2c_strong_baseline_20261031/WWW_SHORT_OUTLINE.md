# WWW Short 四页论文提纲：共享未知询问可靠性的信息复杂度

日期：2026-10-31。状态：**理论驱动写作提纲；Phase 2c 对抗证明审查与已验证开发结果已合并；独立确认 FROZEN_NOT_EXECUTED。**

本提纲只读取原始理论、Phase 2a/2b 已验证记录、Phase 2c 公开报告/验证结果及公开一手文献，不产生轨迹、种子、模型调用或新系数。历史记录保持原样。按 `research-paper-writing` 的段落职责、主张—证据对齐和五维审稿检查组织。四页是用户给定的写作目标，**不是对 WWW 2027 官方篇幅、参考文献豁免或附录政策的已核实陈述**；排版前另核对当届官方要求。下表暂将参考文献也放进四页，以免预设其不计页数。

## 1. 一句话故事与贡献次序

**核心问题：当多个待恢复二元偏好共享一个未知的可靠询问格式，同时高低可靠度也未知时，学习“怎样问”何时增加一阶在线成本，何时可由共享信息完全吸收？**

建议主标题：**Learning How to Ask: Information Complexity under Shared Unknown Reliability**。

突出结构定理的备选：**When Does Learning How to Ask Have Zero Leading Cost?**

研究对象是明确的随机通道模型。Web 关联动机可使用交互式偏好获取、众包和反馈采集；这些是问题背景，不是本项目已经验证的用户场景。不要用自然 LLM 对话图或人体用户图暗示已有实证。

贡献按以下顺序写：

1. **共享未知通道的联合信息复杂度。** 对已知 sharing partition、共同未知 `p,q` 以及 `M/R→α` 的有限校准，给出联合 KL 约束及降维。精确数学下界及代数降维在本轮审查中为 **PASS**；理想策略达到下界为 **CONDITIONAL**。共同参数使跨组备择耦合，不能把已知通道的分组系数相加。
2. **最小共享组的零一阶溢价充要条件。** `K_{S,α}=K_or,α ⇔ Γ_{k_min}(α)≥1` 作为系数恒等式为 **PASS**；最小组决定是否为零，完整分组仍可决定正溢价的大小。解释为最优期望成本之差还需条件可达性。这是最值得占正文篇幅的结构结论。
3. **有条件的信息跟踪构造与受控验证。** 采用已有的估计、强制探索、信息分配和 GLR 范式，清楚列出理想优化 oracle、可预测可测选择和统一检查条件，并通过同估计器、同探索、同停止规则的 D-RRC 比较检验“联合分配是否带来额外价值”。已验证开发批次在 R=1024 的 `[1,3]` 两个 α 下节省在线查询约 52.6%–55.8%，在零溢价 `[4],α=0` 对照完全相同；`[4],α=3` 有小 R 反转。分配对照也包含是否购买 paid type information 的选择；并非固定已购信息后的纯 task reweighting。这是开发证据，不是独立确认。

本轮 [PROOF_AUDIT.md](PROOF_AUDIT.md) 的 verdict 不等于外部认证：它是分离的 native same-family 审查，标注 **NOT_CALIBRATED**，没有外部专家、跨模型或形式化验证。下界和结构恒等式是主要数学贡献；控制实验是第三项证据，不预设优势。

次要理论洞察：两个在线成本都随校准量下降，但两者的差可以非单调；只作为存在性例子，版面不足首先移出正文。直接类型问题、已知答案校准问题和真实自报的区别可用一句限制说明，不挤占核心定理。

## 2. 四页分配与段落职责

|页|建议英文标题及局部篇幅|段落职责与必须出现的内容|
|---|---|---|
|1|Title/Abstract（0.22 页）；**1 Introduction and Context**（0.35）；**2 Model**（0.43）|开篇提出“可靠性未知+格式共享”的联合难点；界定已有 tracking 方法；列三项贡献；用一个极简组共享示意图和符号表说明隐藏状态、可见信息及成本。|
|2|**3 Joint Information Complexity**（0.60）；**4 The Smallest Sharing Group** 开始（0.40）|定义联合信息程序；给出 transcript change-of-measure 下界、单偏好翻转降维、连续参数解析 profile 的证明骨架；给出 oracle 标量方程和唯一分配；展示零溢价判据。|
|3|Section 4 的证明与推论（0.40）；**5 Information Tracking and Its Conditions**（0.40）；结构图/可选校准洞察（0.20）|用 oracle 分配可行性解释 `k_min`；给出 `α=0 ⇔ 单一共享组` 推论；列理想策略六个条件、有限校准尾界的关键一步及机器实现边界；结构图占优，非单调例子为备选。|
|4|**6 Controlled Development Evaluation**（0.60）；**7 Limitations and Conclusion**（0.10）；References（0.30）|以 Aligned vs D-RRC 为主比较，分 premium strata；用四单元 R=1024 表与完整 R 曲线保留收益、相同结果及小 R 反转；报告删失、成本和计算代价；独立确认仍留空位。若 0.30 页不足容纳关键文献，先缩背景而非删最强相关工作。|

建议正文只保留两个主视觉对象：理论结构图和受控比较图；算法用短伪代码/流程行，避免第三个大图占掉假设和证据边界。完整证明位置及补充材料提交方式必须在官方政策核实后决定；不能假设 short 审稿人一定能查阅任意长附录。

## 3. 摘要与引言的可用句子（按职责列出，非完整正文）

- **Opening / 问题**：*Reliable elicitation requires learning both the target answers and which query format to trust.*
- **Model / 明确范围**：*We study binary answers with an unknown group-shared preferred format, common unknown reliability levels, and two labelled calibration streams whose lengths scale with log(1/δ).*
- **Contribution 1 / 当前可写**：*We derive a joint information lower bound and an explicit reduction of its decision-relevant alternatives.* “exact leading complexity”只有在条件化上界与审查状态一起给出时使用。
- **Contribution 2 / 当前可写为程序层面的数学结论**：*We characterize exactly when the information-program premium over a type-revealed oracle is zero: the criterion depends on the smallest sharing group.* 若写成最优期望成本之差，紧邻说明理想可达性条件。
- **Algorithm / 条件句**：*Under explicit real-arithmetic estimation and allocation-oracle conditions, predictable measurable choices, and uniform tracking and stopping-check conditions, an information-tracking policy attains the lower-bound coefficient.* 本轮审查支持该 **CONDITIONAL** 表述；不能省略条件写成可执行程序的 unconditional guarantee。
- **Evidence / 已验证开发证据**：*In controlled Bernoulli development experiments, Aligned reduced restricted online cost by 52.6–55.8% relative to estimator-controlled D-RRC in the two [1,3] cases at R=1024, matched the zero-premium control, and exhibited finite-risk reversals in the calibrated one-group case.* 紧邻标注每单元八个独立世界、包含 type acquisition 的对照范围；不用一句“outperforms”抹掉小 R 负结果。
- **Limitation / 必需**：*The finite-precision implementation has no exact risk or asymptotic-optimality certificate, and the experiments do not establish effectiveness in natural-language interaction.* 理论附注可说明存在远超开发尺度的 guard 反例；摘要不需塞入该输入的数值。

引言反向提纲：P1 问题和共享机制 → P2 为什么未知共同通道使备择跨组耦合 → P3 最强文献已经解决了什么、本文求解何种特殊结构 → P4 三项贡献及证据边界。每段第一句说明段落消息，避免把“同估计器基线还没比较”包装成一个新算法动机。

## 4. 模型、定理和理想算法的最小可复现信息

### 4.1 Model：必须在第一张结果图之前定义

- `d` 个固定未知符号 `θ_j∈{−1,+1}`；已知 partition `S=(S_1,…,S_G)`，`k_g=|S_g|`；每组未知 preferred format `z_g∈{1,2}`。
- 一次 task action `(j,m)` 返回全新独立二元回答；正确概率在 `m=z_g` 时为 `p`，否则为 `q`。共同未知 `.5≤q<p≤1−η`，已知 `η>0`。
- 离线两条**带高/低可靠度身份标签的**参考流，各 `M` 个观测；不揭示当前 `θ,z`。`R=log(1/δ)`，`M/R→α<∞`，离线共 `2M`。不把普通历史聊天自动解释成该校准资源。
- 可选 type action：以**已知** `s_g∈(.5,1)` 返回组类型，`κ_g=kl(s_g,1−s_g)`；每次也算一个在线动作。Phase 2b 的数值参考使用 `s=.8`；task-only 和 task+type 的 `K` 不可混用。
- `τ` 是在线动作数；主目标全符号恢复，风险概率对离线与在线随机性共同计算，并在模型域内 uniform δ-correct。渐近效率是固定 `d,p,q,S` 下 pointwise 结论，不是随维数或 gap 变化的 uniform rate。
- oracle **仅知 z**，仍未知 `θ,p,q`，获得同样校准数据。总获取成本单列 `τ+2M`。预算 `B` 处删失时报告 `min(τ,B)`，不把它标为 `Eτ`。

### 4.2 Theorem A：先给确切下界，再给条件上界

正文可先用一般式减少符号负担：

\[
K_{S,\alpha}=\min_{x\ge0}\left\{\mathbf1^\top x:
\inf_{h':\theta'\ne\theta}\left[\alpha D_0(h,h')+\sum_e x_eD(P_h^e,P_{h'}^e)\right]\ge1\right\}.
\]

`D_0=kl(p,u)+kl(q,v)`；`e` 包括允许的 task/type actions，`x_e` 是每 `R` 单位的在线次数。下一段给出同组置换对称化后的 `a_g,b_g,c_g`，并指向原始 `I_{J,h}` 公式；不要只展示一个泛型优化式而省掉真正的结构求解。

证明骨架：停止 transcript KL → 错误符号备择必须获得 `kl(1−δ,δ)` → 同组对称化 → 对 `r,x≥.5` 的 `kl(r,1−x)−kl(r,x)=(2r−1)log(x/(1−x))≥0` → 每种类型翻转模式只需保留一个符号翻转 → `G·2^G` 约束。内层是两变量加权 Bernoulli isotonic projection，可解析求解；这一事实不等于整个外层数值优化已经区间认证。

**层级 A，下界，PASS**：`liminf E_h τ/R ≥ K_{S,α}`，明列 uniform δ-correct 策略类和 a.s. stopping；有限期望时停止 KL identity 由有界 log likelihoods 支持，期望无穷时下界直接成立。单翻转降维和连续参数解析 inner projection 也在本轮审查中为 PASS。

**层级 B，条件可达性，CONDITIONAL**：存在满足下述完整理想契约的策略时，`E_h τ/R→K_{S,α}`。本轮审查没有找到 repaired ideal argument 的反例，支持 finite-calibration uniform tail 修补；但期望上界仍以实际 oracle 误差、可预测可测选择和统一更新/检查条件为前提。全文使用“exact information lower bound + conditional ideal achievability”，不借 Theorem 1 的原始标题认证 executable Python。

### 4.3 Theorem B：oracle 与最小组判据

定义 `D(r,x)=kl(r,x)`，`F_k(r,x)=D(r,1−x)+(k−1)D(r,x)`，并用标量根确定 `a_α`：

\[
\inf_{.5\le v\le u\le1-\eta}
\{\alpha[D(p,u)+D(q,v)]+a_\alpha F_d(p,u)\}=1,
\qquad K_{or,\alpha}=d a_\alpha.
\]

oracle 的唯一信息最优 task allocation：每个坐标只问好格式、次数系数为 `a_α`。本轮审查中标量系数及唯一性为 **PASS（数学程序）**；其有限预算逐步动作不必与该一阶目标完全相同。然后定义

\[
w_k=\max\left\{\tfrac12,
\frac{\alpha q+a_\alpha[1+(k-2)p]}{\alpha+ka_\alpha}\right\},\quad
\Gamma_k(\alpha)=\alpha D(q,w_k)+a_\alpha F_k(p,w_k).
\]

核心盒式结论（**PASS 作为系数恒等式；CONDITIONAL 作为期望成本恒等式**）：

\[
\boxed{K_{S,\alpha}=K_{or,\alpha}\iff\Gamma_{k_{min}}(\alpha)\ge1.}
\]

证明信息：在唯一 oracle allocation 上检验未知类型约束；若备择翻转总共 `l` 个坐标所在组的类型且符号翻转在其中，其最难信息为 `Γ_l`；`Γ_l` 随 `l` 不减，故最小非空翻转组支配零边界。有限信息 type actions 不能以零额外成本修复不满足的约束。

优先保留的推论：`α=0` 时零溢价当且仅当 `G=1`。`α>0` 时不能据 `G=1` 直接断言零溢价；`[4],α=3` 是当前开发配置中的正溢价点。

### 4.4 Algorithm：不把已有 tracking 当新贡献

用一行流程：**balanced O(√t) forced samples → forced-only response estimator → joint KL target → cumulative deficit tracking → common joint GLR**。

把“理想策略”条件集中成一个小框，替代散落的免责声明：

1. 每个 task stream 的 forced count 至少 `c√t−C`，总强制次数 `O(√t)`；
2. 估计器使用被允许的可观测信息，固定正 gap 下具有 `exp(−c√t)` 集中，投影网格确定性趋细；
3. 每次更新使用 `α_δ=M_δ/R`，而非 `M_δ/t`；每个接受的优化输出对**完整连续备择集**满足实际误差契约，例如 `x_t≥0`、`I_est(x_t)≥1−e(t)`、`cost(x_t)≤K_est+e(t)`，其中 `e(t)→0` 的模量不依赖 δ；若允许失败，另证明足以控制期望尾部的失败/恢复策略；
4. 每个动作、估计、optimizer representative 和 tie rule 均对可见过去及公开输入可测、可预测；可在每个有限网格点预先固定确定性 optimizer representative，无需唯一/连续 optimizer。更新年龄 `O(√t)`，累计目标在**每一轮**累加，实际次数与该目标偏差 `O(√t)`；这些常数在固定真参数邻域内对小 δ 统一；
5. joint GLR 精确比较或保守包围完整连续似然，使用包含两条离线流的原边界；uncapped mathematical stopping 持续检查，所有后续 horizons 的最大检查间隔统一为 `o(R)`，而非只在某一个 horizon 成立；
6. 固定真参数下局部最优集稳定、正在线信息余量和关于所有 `t≥(K+ε)R` 的可求和尾界成立。

有限校准证明必须点明：固定 `δ` 的离线坏事件不会随后续 `t` 自己消失；需联合离线和在线 log-likelihood increments 控制尾概率，再求和得到期望界。本轮审查对该 concentration 步骤在理想 allocation event 下判 **PASS**，对由 uniform tail 及 uniform checks 推至期望上界判 **CONDITIONAL**。`a.s.` allocation convergence 或逐 δ 的 pointwise optimizer convergence 不能直接替代该步骤。

**机器实现：GAP，而且已有具体 arithmetic counterexample。** 审查给出合法静态 count 输入：`d=1,η=1/8`、无 calibration/type、单格式约 `10^12` 个同向回答，仍小于源码的 `2^50` 总观测上限；在 `R≈5.596×10^11` 时，浮点 `gap−β` 约 `+1.2207×10^−4`、超过 heuristic guard，而高精度按该 binary64 R 的确切值计算约 `−6.5634×10^−6`。这反驳 guard 是保守 enclosure，**没有证明实际错误概率超过 δ，也没有证明任何 R=16–1024 开发端点判错**。正文限制段可用一句概述，完整数值与复现指向审查文件。

其余实现缺口也独立保留：固定 optimizer/LP/feasibility floors 不证明实际误差趋零；GLR 拒绝总观测大于 `2^50`，网格最终受 float resolution 限制，planner exceptions 没有数学定义的恢复策略，累计浮点目标也未包围舍入误差。Phase 2b 的 5,082 次更新均仍位于请求容差 `1e−4` 平台；其观测不能声称实际误差已经趋零。这些缺口限制 executable theorem，不否定诚实标注的有限精度受控实验。

## 5. 最强相关工作及精确差异

完整一手来源、阅读位置与核验限制见 [RELATED_WORK_SOURCES.md](audit/RELATED_WORK_SOURCES.md)。正文合并为三个紧凑主题，保留五条线的覆盖。

|线索与优先引用|已经存在的结果；本项目可主张的具体差异|
|---|---|
|Controlled sensing：Nitinawarat–Atia–Veeravalli；Deshmukh–Bhashyam–Veeravalli|前者已有 controlled multihypothesis 的一阶最优策略；后者处理 composite hypotheses 的未知指数族参数及期望停止时间。本文不首创“未知参数+主动询问+渐近最优”；应突出共享 `p,q`、带标签有限校准和 partition 结构的显式求解。后者特定版本的唯一 optimizer 假设不能直接为本文非唯一最优集作证。 [简单假设原文](https://arxiv.org/abs/1205.0858)，[复合假设原文](https://arxiv.org/html/1910.12697)。|
|Best-arm / structured pure exploration：Garivier–Kaufmann；Degenne–Koolen–Ménard|Track-and-Stop、强制探索、累计分配跟踪与 GLR 是已有技术；一般 structured exponential-family pure-exploration answer maps 也已有框架。本文价值应是可解释的联合复杂度及精确 sharing boundary，而不是把二元回答命名成新型 bandit。 [COLT 2016](https://proceedings.mlr.press/v49/garivier16a.html)，[NeurIPS 2019](https://papers.neurips.cc/paper_files/paper/2019/hash/8d1de7457fa769ece8d93a13a59c8552-Abstract.html)。|
|Offline-data BAI：Agrawal et al.|已有将离线计数加入 KL lower bound 的 online sample complexity，以及对离线/在线共同随机性的 correctness；不能把“加入校准信息”本身作新颖点。本文离线数据只标识两种可靠度，不透露当前符号或组格式；结构性问题是信息能否通过共享抵消 type-unknown premium。 [原文 §2、Appendix B.2](https://arxiv.org/html/2306.09048)。|
|Adaptive crowdsourcing：Abraham et al.；Ho–Jabbari–Vaughan|未知 crowd quality 下选择信息源与停止、异质任务自适应分配和标签推断都已有研究。Abraham 的单 microtask 设定明确分开跨任务 quality 学习；此处可精确说明跨坐标的共享格式及共同连续通道参数。不要泛称众包“假设可靠度已知”。 [Bandit Survey](https://proceedings.mlr.press/v30/Abraham13.pdf)，[Adaptive Task Assignment](https://proceedings.mlr.press/v28/ho13.html)。|
|Preference elicitation：Yamagata et al.|偏好效用和不同标注者 rationality 联合估计已有工作；本文不首创“偏好与可靠性同时学习”。其 Boltzmann utility/rationality 模型与本文两个 accuracy levels、组共享格式不同；当前核验只支持这一建模区别，不支持声称该文没有某个最优性定理。 [作者机构原始记录](https://research-information.bris.ac.uk/en/publications/relatively-rational-learning-utilities-and-rationalities-jointly-/)。|

可用 novelty 句：*Our contribution is the explicit shared-channel information program and its smallest-group zero-premium characterization; the tracking and likelihood-ratio machinery builds on established controlled-sensing and pure-exploration methods.*

这是一轮有针对性的来源核验，不是穷尽优先权审计。不要在标题、摘要或引言使用未经额外检索支持的 “first” 或 “previous work cannot”。

## 6. 实验叙事、现有结果与不得越过的空位

**主问题**：在相同 forced-only estimator、decaying exploration、离线信息、terminal decoder、GLR、检查时刻、动作计费及配对响应世界下，联合信息分配比简单 exploitation rule 多带来什么？

五个方法：Aligned、D-RRC、既有 constant-exploration RRC、Round-Robin、Format-Only Oracle。主比较只用 Aligned vs D-RRC；旧 RRC 用于说明为何原先差距不足以识别 allocation 的额外价值。按已冻结 [DECAYING_BASELINE_SPEC.md](DECAYING_BASELINE_SPEC.md)，D-RRC 保留共同估计器、探索、更新和 tracker，只在 exploitation 时对每坐标当前较好格式赋 `1/d`，type-action target 为零，不做 KL solve、不永久承诺。以下结果只来自已验证的公开开发报告。

**受控差异的精确含义**：两个策略拥有相同信息来源和动作可用性，取得的响应与购买的 type reports 可以不同；Aligned 的收益若存在，包含**是否/如何购买已知准确率 s=.8 的付费类型信息**以及如何在任务格式间分配。不能把该对照称为“在相同已购信息下只优化 task allocation”，也不能归因为“只改变数学 solver”。两者 allocation estimators 都只读 forced task responses；calibration bits 与已购 type reports 进入共同 GLR。相同潜在响应流不保证实际路径上的 forced estimates 完全相同。该已知可靠度 type-report 资源不是未经验证的人类自报接口。

**分层不能只按 partition 名称。** 当前 `d=4,p=.85,q=.60,s=.8`、允许 task+type 动作的系数如下，来自 Phase 2b 已验证 `coefficients.json`；表中为浮点数值近似，零等价依据结构定理而非舍入：

|Partition|α|K(task+type)|K_oracle|理论 strata|
|---|---:|---:|---:|---|
|[1,3]|0|5.7702202494|4.8106540845|positive premium|
|[1,3]|3|5.2007082146|4.1019698261|positive premium|
|[4]|0|4.8106540893|4.8106540845|zero premium（数学上相等，数值有舍入差）|
|[4]|3|4.2536324629|4.1019698261|positive premium；不可与上一行合称 zero-premium partition|

任务-only `K` 在 `[1,3]` 下分别为 `7.3327838999`、`6.7619924236`，不是上述 Aligned 可用 type actions 时的同一个基准。任何新图必须把 action set 标清。

**只允许作为历史探索证据的数字**：Phase 2b 有 64 个独立世界、320 条策略轨迹，每个 partition×α×R 单元 `n=4`；总在线 `1,038,656`，策略视角离线 `326,400`（去重后的配对世界离线 `65,280`），299 完成、21 删失。Aligned 完成 `63/64`、删失 1 条；已完成错误认证为 0，不能验证极小 `δ`。主批次 wall `723.75s`，Aligned planner `405.42s`；成本降低与计算开销分开写。

R=1024 四单元的 Aligned `mean min(T,B)/R` 为 `6.6875,6.3046875,5.2578125,4.953125`；对应高于 `K` 约 `15.9%,21.2%,9.3%,16.4%`，相对旧 RRC 在线成本低约 `45.1%,43.4%,30.6%,25.8%`。这些描述全部是 **Phase 2b exploratory**，不是对 D-RRC 的结果或渐近最优证明。不同 R 使用不同独立世界，曲线点不是同世界纵向收敛轨迹。

**Phase 2c 已验证开发分母**：128 个独立世界，16 个 partition×α×R 单元、每单元 8 个世界，五方法共 640 条轨迹；在线 `1,925,008`（task `1,894,181`，paid type `30,827`），逐策略计费离线 `652,800`，去重的独立世界实际离线 `130,560`，策略总获取成本 `2,577,808`。637 完成、3 删失、错误认证 `0/640`；其中 Aligned `127/128` 完成、1 删失，D-RRC `126/128` 完成、2 删失。三条删失均在 `[1,3],α=3,R=64`；所有世界按 `min(T,B)` 纳入。零观测错误不验证 `exp(−R)` 风险。

验证依据：[BASELINE_COMPARISON.md](BASELINE_COMPARISON.md)、[COST_GAP_DIAGNOSTICS.md](COST_GAP_DIAGNOSTICS.md)、[VALIDATION.json](VALIDATION.json)、[facts.json](artifacts/analysis/facts.json)。验证器重算 640 个最终 GLR，全部身份、计费、删失和配对检查通过，历史 295 个文件保持一致；既有世界重放是完整性检查，不新增独立科学样本。

**四页正文首选结果表：R=1024，八个独立世界/行，所有路径均完成。** `N/R` 在此仍按预先定义的 restricted-cost estimand 报告；表内差为逐世界配对 `A−D` 的均值，区间为未多重校正的探索性 world bootstrap 95% 区间。

|Partition|α|溢价层|Aligned N/R|D-RRC N/R|配对差 A−D /R [95% 区间]|相对 D-RRC 节省|
|---|---:|---|---:|---:|---|---:|
|[1,3]|0|positive|7.02734|14.82422|−7.7969 [−8.6484, −6.7188]|52.60%|
|[1,3]|3|positive|6.47656|14.64063|−8.1641 [−8.6523, −7.7617]|55.76%|
|[4]|0|zero|5.203125|5.203125|0.0000 [0.0000, 0.0000]|0.00%|
|[4]|3|positive|4.80078|4.98047|−0.1797 [−0.2305, −0.1328]|3.61%|

**所有 R 的方向及负结果必须随图呈现。** `[1,3]` 两个 α 在 R=16 的差区间均跨零，在 R=64、256、1024 的开发区间均低于零。零溢价 `[4],α=0` 在全部四个 R 的已观察配对路径完全相同；这不证明所有未来世界方差为零。正溢价 `[4],α=3` 在 R=16 为 `A−D=+2.1250 [1.0000,3.3750]`、R=64 为 `+0.3750 [0.1875,0.5625]`，即 Aligned 更贵；R=256 为 `+0.1016 [−0.0469,0.2891]`，方向不确定；到 R=1024 才出现上表的小幅节省。因此正溢价不是有限 R 胜出的充分条件，不能宣称 universal superiority。不同 R 使用不同独立世界，不能把曲线当同一个世界的收敛轨迹。

**有限 R 与 K 的差距**：R=1024 的四单元 `N/(KR)−1` 为 `21.79%,24.53%,8.16%,12.86%`；末次 `θ/z` 错误均为零，但连续 rate 估计、轨迹早期错误和分配偏离仍存在。此时强制比例为 `3.39%–4.09%`，`β/R=1.0420–1.0710`，实际分配在 K 处的信息缺口 `3.04%–11.39%`、末次目标的信息缺口 `0–9.69%`，tracking `L1/t=0.0277–0.0378`。信息缺口是 `max(0,1−I(α,Kw))`，不依赖任意选定的真 optimizer 距离；另存的 L1 距离只到一个指定真最优解，而非到整个非唯一最优集。这些相关诊断不能相加为因果成本贡献。

**查询节省伴随显著计算代价**：主批次 wall `1412.99s`，worker CPU 合计 `1097.87s`、evaluator CPU `381.46s`；planner wall/CPU `762.87/762.84s`，GLR wall/CPU `95.06/95.10s`。按策略统计的采样+规划+GLR wall：Aligned `837.63s`，D-RRC `211.61s`；对应 worker CPU `790.69s` 与 `128.27s`。不把 query-efficiency 当作 wall-time 优越。此次所有更新仍只达到最小请求容差 `1e−4`；记录的最大数值相对 gap 约 `1.11×10^−4`，不是严格误差 enclosure，也不证明无限期误差消失。

**当前可写的结论**：已观察到包含 paid-type acquisition choice 的分配规则在两组 `[1,3]` 的较大 R 情形有幅度较大的开发成本优势，零溢价对照相同，而单组校准情形出现有限 R 负结果。特异性仍是待确认的经验问题：不能由一层显著、一层不显著推导“收益只发生于正溢价”。

**独立确认结果空位保留**：`[CONFIRMATION_PRIMARY_RESULT — FROZEN_NOT_EXECUTED]`、`[CONFIRMATION_ZERO_CONTROL_RESULT — FROZEN_NOT_EXECUTED]`。已冻结 [CONFIRMATORY_PROTOCOL.md](CONFIRMATORY_PROTOCOL.md) 计划 R=1024、α=0：positive `[1,3]` 165 个独立世界、zero `[4]` 24 个独立世界；样本量由开发配对 SD 的预定膨胀规则规划，不是已取得样本。未产生确认 seed、world 或结果，不画确认点，也不填成功结论。数学审查仍为 exact lower/coefficient PASS、ideal expected-time CONDITIONAL、executable arithmetic GAP。

## 7. 图规格与可直接采用的图注

### Figure 1：结构定理图（优先正文；现有结果可用）

来源：Phase 2a `artifacts/theory/phase_map.json`、`phase_map.pdf` 和 `THEORY_PHASE_MAP.md`；对应 `FINAL_RECEIPT.json` 保留独立优化/备择核验。现图已查看。左图 `d=16,p=.85,q=.60`，横轴 `α`、纵轴 `Γ_{k_min}`，水平线 1；右图用同一动作集的 `K−K_oracle`。允许直接复用已验证数据排版，不在此阶段新增参数网格或重新求系数。

Caption：*Smallest-group criterion for zero leading online-cost premium. Left: Γ for the displayed sharing partitions; the threshold is Γ=1. Right: the joint-program premium with noisy type actions (s=0.8). These are numerical evaluations of theoretical coefficients, not finite-budget recovery measurements. Offline acquisition contributes an additional 2α to total cost normalized by R.*

制作要求：现图左侧阈值对应 `[8,8]` 的 `α≈2.04316`，不是 d=4 开发实验的经验转折；右图的 `~1e−8` 不当正溢价。“相变”一词只指系数等价边界，不能暗示有限样本性能有突变。正文应保留 partition 标签，不能仅给 `k_min` 而把正溢价大小也说成只由它决定。

### Figure 2A：历史有限 R 图（仅作历史/补充，必须明标 Phase 2b）

来源：Phase 2b `artifacts/analysis/summary.json`、`coefficients.json`、`paired.json`、`online_cost_convergence.pdf`、`VALIDATION.json`。现图已查看。四 panel 对应四个 partition×α，横轴 `R∈{16,64,256,1024}`，纵轴 `mean min(T,B)/R`；显示所有点、censor 标记、`n=4` 与对应 action set 的 `K`。为四页可只展示 Aligned、旧 RRC 和 Oracle，完整五方法表保留可访问记录；切勿把删去的曲线描述成未比较。

Caption：*Exploratory Phase 2b online query costs in controlled Bernoulli worlds. Each point averages four independent worlds paired across policies; distinct R values use distinct worlds. Costs are restricted at the declared cap, and censored cells are marked. Reference lines are information-program coefficients. The plot does not compare Aligned with D-RRC or establish convergence of expected stopping time.*

数值 `9.3%–21.2%` 和 `25.8%–45.1%` 只可作为该图的历史 R=1024 描述，不能放在摘要中代替主比较。

### Figure 2B：已验证 Phase 2c 主比较图（正文优先）

来源为 [BASELINE_COMPARISON.md](BASELINE_COMPARISON.md) 对应的 `artifacts/analysis/online_cost_comparison.{png,pdf}`、`total_cost_comparison.{png,pdf}` 与已验证 JSON；本轮提纲不新跑模型或重算系数。两个层次：每 cell 的 paired cost ratio/difference 和相应完成/删失分母；以 zero-premium `[4],α=0` 单独标识，其他三个为 positive-premium。保持全部 16 个预设 cell，包括 `[4],α=3` 的 R=16/64 负结果及 R=256 不确定结果，不只显示 R=1024。一个小表同时放 online、offline、total acquisition 和 CPU/wall，避免 query gain 隐去优化代价。

Caption：*Aligned versus estimator-controlled D-RRC in a bounded Bernoulli development study. The policies share exploration, estimation, calibration, decoding and stopping rules; their allocation contrast includes whether to purchase available type reports. There are 128 independent worlds across 16 cells, eight per cell, paired across policies. Costs use min(T,B)/R and exploratory world-bootstrap 95% intervals without multiplicity correction. At [1,3], α=3, R=64, Aligned has one capped path and D-RRC has two; all are retained. The calibrated one-group case shows reversals at smaller R. No independent confirmation samples were used.*

不能复用 Figure 2A 的旧 RRC 点当 D-RRC；正文应直接使用 Phase 2c 已验证数据对应的图。确认结果仍为空，冻结的 165+24 世界方案不得出现在任何“已执行样本量”或结果曲线上。

### 可选 Figure S：非单调 calibration premium（让位于核心证据）

只在原始 `numerical_bounds.json` / `certify_example.py` 及对应 receipt 核验后使用 Theory Note §7 的 `d=1,p=.75,q=.60` 既有例子；本提纲未重新执行其证书。图注必须写 *An existence example, not a universal shape theorem*。若四页已满，仅保留一句“the difference need not be monotone”和文献/证明指针。

## 8. 主张—证据映射（投稿前必须随最新审查重核）

|Claim / 候选英文主张|Evidence / 精确依据|Status 与措辞上限|
|---|---|---|
|*The joint program gives an information lower bound under shared unknown reliability.*|原 `Theory_Note.md` §2；本轮 `PROOF_AUDIT.md` 的 stopped KL、对称化和单翻转裁决|**PASS，精确数学下界**，限于明示随机通道和策略域；数值 checks 辅助，不替代证明。|
|*The oracle information allocation uses only the good format and has coefficient d aα.*|原 Note §5；本轮 audit 的 scalar/uniqueness 裁决，包括 d=2,α=0 边界论证|**PASS，数学程序结论**。不是有限样本每一步必须只问好格式。|
|*The smallest group determines whether the leading premium is zero.*|原 Note §6；本轮 audit 的 oracle feasibility、Γ_l 单调和 zero type cost 裁决|**PASS 作为系数恒等式；CONDITIONAL 作为期望成本恒等式**；不能扩展到正溢价大小。|
|*An ideal strategy matches K.*|Phase 2b addendum；本轮 audit 的实际误差契约、可预测可测选择、positive online margin、联合 calibration tail 和 uniform checks|**CONDITIONAL**。无新的 ideal-math counterexample；仍须保留完整条件，不能推出 Python theorem。|
|*The Python program is asymptotically optimal / has exact δ correctness.*|本轮 audit 的 guard 静态输入反例、fixed numerical floors、2^50 cap 和异常行为|**GAP；该 executable claim 不可写**。反例否定保守 enclosure，不证明实际风险超过 δ 或有限开发端点错误。|
|*Observed Phase 2b normalized restricted cost moves toward K over tested R.*|Phase 2b `summary.json`、`VALIDATION.json`、`FINAL_RECEIPT.json`；四独立世界/点，删失保留|**SUPPORTED，探索性有限 R 描述**；无截断 `Eτ/R` 极限未建立。|
|*Aligned improves over the old RRC at R=1024 in the four Phase 2b cells.*|Phase 2b 原始 summary 的受限均值和全部配对记录|**SUPPORTED，历史开发描述**；不识别 joint allocation 相对 consistent policy 的独立价值。|
|*At R=1024, Aligned reduces restricted cost against D-RRC in the two [1,3] cases and matches the zero-premium control.*|本轮 `BASELINE_COMPARISON.md`、`VALIDATION.json`、`facts.json`；每 cell 八个独立世界|**SUPPORTED，已验证开发证据**：节省 52.60%/55.76%，零溢价观察路径相同；完整 acquisition/allocation rule 对照，不单独识别纯 task reweighting，不是独立确认。|
|*Positive premium guarantees a finite-R gain / Aligned universally beats D-RRC.*|`[4],α=3` 在 R=16/64 更贵、R=256 不确定、R=1024 小幅节省；`[1,3]` 的 R=16 区间跨零|**REFUTED AS A UNIVERSAL DEVELOPMENT CLAIM**。逐 cell 写方向，不能只挑最大 R。|
|*The gain is confirmed to be specific to positive-premium settings.*|独立确认 positive/zero 方案为 165/24 世界，但 seed、world 和结果均未生成|**NEEDS CONFIRMATION**；保留确认空位，不由开发层间显著性差异推出特异性。|
|*Residual finite-R excess is explained additively by exploration, estimation, allocation and stopping overhead.*|`COST_GAP_DIAGNOSTICS.md` 的 forced fraction、rate errors、信息缺口、β/R 和 tracking diagnostics|**UNSUPPORTED AS CAUSAL DECOMPOSITION**。可分别描述活跃机制；没有冻结干预来识别可加因果贡献。|
|*More calibration can increase and then decrease the premium.*|原 Note §7 的存在性例子及保留的有理区间证书|**SECONDARY / 证书未在本提纲重跑**。不是普遍形状结论，也不表示总成本下降。|
|*The method improves natural LLM interactions or human outcomes.*|无符合共享 iid 模型的自然交互有效性验证|**UNSUPPORTED**。背景动机可以保留，效果主张删去。|

## 9. 五维审稿问题与当前回答

|维度|审稿人最强问题|当前回答与写作动作|
|---|---|---|
|Contribution|这是否只是 generic controlled sensing / structured bandit 加一个模型？|**needs revision**：一般 lower bound 和 tracking 并非新；必须把联合共享未知通道、oracle 唯一性、`k_min` 充要条件及校准边界写成可独立检查的显式结果，并在一手文献中继续核验优先权。|
|Writing clarity|读者能否区分全符号风险、type oracle、online coefficient、总获取成本与受限均值？|**pass with defined terminology**：首次出现即定义；每个图注标动作集、offline `2M`、删失和 evidence 层级。全篇用相同 `R,α,K,K_or,k_min`；若不写 type action 分支则同步换掉相关系数。|
|Experimental strength|比 constant-exploration RRC 快是否只是其探索负担过大？|**bounded development evidence**：共享估计器/探索/停止的 D-RRC 已比较；R=1024 两个 `[1,3]` 点节省约一半，零溢价路径相同，单组校准小 R 反转。区间 n=8、未多重校正；独立确认仍未执行，收益也包含 paid-type 购买选择。|
|Evaluation completeness|正/零溢价分层、runtime、误差认证、删失、未停止路径是否完整？|**pass for scoped development reporting**：全 16 cell 和 640 轨迹纳入，637 完成/3 删失，所有最终 GLR 重算；`[4],α=3` 正溢价；报告计算开销。`β/R`、estimation 和 allocation diagnostics 不组成因果分解；自然 LLM 外推及 exact executable risk 仍无证据。|
|Method design soundness|期望界是否只证明 a.s. 收敛？finite calibration 和 floating optimizer 是否被掩盖？|**conditional / executable gap explicit**：联合 tail 修补在理想事件下通过；可测选择、实际 δ-uniform oracle 误差和对所有后续时刻统一的 uncapped checks 保留。远尺度 guard 反例与有限机器限制阻止 exact executable theorem，不能拿零错误数补足。|

投稿前编辑检查：删除未填空位、核对三项贡献优先级、核对每个数字的历史阶段与完整分母、核对 conditional 字样紧邻上界、保留 D-RRC 的负/不确定结果、核对 WWW 官方 short 页数与补充材料政策。**当前可写的是理论结构与开发诊断论文提纲；目前不可写成“强基线优势已确认”“机器实现渐近最优”或“自然 LLM 有效”。**

## 10. 本提纲读取的本地证据

- 原始理论：[Theory_Note.md](../../Theory_Note.md)；含 §2 联合程序、§5 oracle、§6 最小组、§7 非单调例子。
- Phase 2b：[PROOF_ADDENDUM.md](../phase2b_alignment_20261031/PROOF_ADDENDUM.md)、[ALIGNMENT_MATRIX.md](../phase2b_alignment_20261031/ALIGNMENT_MATRIX.md)、[PILOT_REPORT.md](../phase2b_alignment_20261031/PILOT_REPORT.md)、[VALIDATION.json](../phase2b_alignment_20261031/VALIDATION.json)、[FINAL_RECEIPT.json](../phase2b_alignment_20261031/FINAL_RECEIPT.json)、公开分析 JSON/图。未读取 private seed 文件。
- Phase 2a：[PILOT_REPORT.md](../phase2a_theory_optimality_20261030/PILOT_REPORT.md)、[THEORY_PHASE_MAP.md](../phase2a_theory_optimality_20261030/THEORY_PHASE_MAP.md)、[FINAL_RECEIPT.json](../phase2a_theory_optimality_20261030/FINAL_RECEIPT.json)、phase-map 数据与图。
- Phase 2b 可观测采样器源文件用于核对 forced-only estimator 与数值契约；不启动运行。
- 本轮 [PROOF_AUDIT.md](PROOF_AUDIT.md) 已读取并合并，另读取已冻结 [DECAYING_BASELINE_SPEC.md](DECAYING_BASELINE_SPEC.md) 与 [PHASE2C_PROTOCOL.md](PHASE2C_PROTOCOL.md) 核对 paid-type acquisition 的对照范围；未编辑 proof/source/freeze，未读取任何 private/main seed。
- 本轮开发证据：[BASELINE_COMPARISON.md](BASELINE_COMPARISON.md)、[COST_GAP_DIAGNOSTICS.md](COST_GAP_DIAGNOSTICS.md)、[VALIDATION.json](VALIDATION.json)、[facts.json](artifacts/analysis/facts.json) 已用于填入开发结果；[CONFIRMATORY_PROTOCOL.md](CONFIRMATORY_PROTOCOL.md) 只核对冻结状态与计划样本量。独立确认结果空位保留，状态仍为 FROZEN_NOT_EXECUTED。
