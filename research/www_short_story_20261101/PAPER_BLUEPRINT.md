# 四页候选论文骨架与 motivation 草案

日期：2026-11-01。状态：写作蓝图，**不是已排版的四页投稿稿**。本文件选择 Story D，原始共享理论稿保持独立。本轮英文段落是忠实于现有证据的可编辑草案；未生成摘要或完整论文，不涉及作者/提交决定。

## 1. 先固定消息与紧凑提纲

工作标题：**When Fixed Reading Depth Fails: Web Evidence Acquisition with Finite Calibration**。

主消息：在完成来源块模型中，持久来源错误与有限校准的未知抽取可靠率可以使任何固定读取深度严格次优，即使最佳提问形式已知。

紧凑提纲：

1. Web系统需要同时决定获取多少独立来源、每源读取多少次。
2. 采用已有的来源/抽取两层错误表示，明确当前研究的是带成本的证据获取。
3. 用相同未知参数、参考数据和费用定义 oracle 与固定深度强基线。
4. 给出信息系数、连续域严格分离及非退化参数区域。
5. 用已知率与完美来源控制解释结构改变，并说明原理论的恢复关系。
6. 给出受限策略类、窄区域、校准假设和无自然Web验证等限制。

## 2. 四页预算

官方限制为4页，含参考文献和可选附录；第一页必须明确 Web 和 track 关联。[官方要求](https://www2027.thewebconf.org/research-track-papers/)

| 内容 | 目标页数 | 必须保留 |
|---|---:|---|
| Title / Abstract | .20 | 一个问题、一个主定理、模型范围；此轮不写摘要 |
| Introduction and Context | .60 | 具体Web决策；承接已有分层/来源选择研究；核心结构发现 |
| Model and Information Cost | .50 | θ,V,Y；已知r与z；未知p,q；两条参考流；完成块与费用 |
| Fixed-Depth Separation | .80 | 一信息系数命题＋一主定理；所有固定深度全部组合；区域与成本含义 |
| Proof Outline | .65 | 正确成本/似然；统一可行见证；全连续备择覆盖；受限下界与扰动 |
| Mechanism Controls and Certificate Table | .40 | 三种信息条件的深度结构；一小表/一紧凑图；明确计算辅助性质 |
| Limitations and Conclusion | .15 | 受控模型、策略类、校准与来源假设、非经验结果 |
| References | .70 | 直接近邻优先，不能为省页删除最相似结果 |
| **合计** | **4.00** | 实际排版后重新分配，不能当已满足篇幅 |

关键证明必须在正文有自洽的逻辑。长证明和代码可另备复现材料，但不能假设 short 的附录不计页数，也不能把审稿人必须接受的核心推导完全放到正文外。若可达性证明无法交代，应降低论文主张或重新分配篇幅，而非保留“全局最优期望成本”口号。

## 3. 引言英文草案与段落职责

### P1 — Opening / Web决策

**A Web evidence system must decide both which sources to acquire and how deeply to read them.** After locating a report, it can spend additional effort extracting that report or pay to obtain another source. These actions address different uncertainties when a source can consistently state a false claim. We study the cost of recovering a binary fact under this distinction, with a prescribed error probability.

角色：先提出具体决策和指标，不宣称已有实际系统表现已被测量。段落自己的论断是本文建模动机。

### P2 — Context / 承接已有研究

**Separating source errors from extraction errors is essential to defining the evidence being acquired.** Prior work distinguishes factual errors in Web sources from errors introduced by extractors, and accounts for dependence caused by copying. [Knowledge-Based Trust](https://www.vldb.org/pvldb/vol8/p938-dong.pdf), [source dependence](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf). We adopt this distinction and ask how finite knowledge of extraction reliability changes the optimal allocation between new sources and repeated extraction. This is an acquisition-design question beyond interpreting an additional answer as a fresh independent report.

角色：明确哪些部件已有、我们具体研究什么。末句只区分观测模型，不声称现有全部方法都使用错误独立性假设。

### P3 — Challenge / 有限校准

**Unknown extraction reliability changes which alternatives an acquisition strategy must rule out.** We consider independent persistent source reports with known source accuracy, two extraction formats, and two labelled reference streams of size proportional to log(1/δ). The better format is revealed to our oracle, while its two accuracy levels remain unknown. Even under this favorable information, a strategy must distinguish an incorrect fact together with alternative extraction rates, rather than test only a truth reversal at a fixed channel.

角色：落到本文真正的复合备择困难；不把z已知与p,q已知混同。主定理本身不要求先解决未知z学习。

### P4 — Finding / 核心贡献

**Finite calibration can make every fixed source-reading depth strictly suboptimal.** Within a completed-block model, we certify an explicit parameter region in which every optimal first-order allocation uses at least two depths. The comparison includes every format composition at each fixed depth. Across this region, the optimal asymptotic online-cost coefficient is at least 4.85% smaller than that of every fixed-depth design. The separation is established by a continuous-domain, computer-assisted certificate, rather than a grid comparison.

角色：定理及强比较对象。4.85%是系数相对差，不能替换成准确率、有限预算成本或包含参考数据的总成本。

### P5 — Explanation and scope / 因素移除及边界

**The change in depth structure is explained by complementary model controls.** With perfect sources, the information coefficient reduces to that of independent answers times ℓ+c/N, and maximal depth suffices. With known extraction rates, the completed-block model admits a fixed-depth optimum. Our result concerns a fixed finite block menu with no within-block decisions or revisits; it neither asserts optimality for unrestricted browsing agents nor establishes these assumptions empirically for natural Web pages.

角色：解释而非堆新贡献。已知率的一般表述是“存在单深度最优”，不能宣称所有最优分配都只有一个深度。

### 中文连贯版 motivation

Web证据获取需要同时决定获取哪些来源、对每个来源读取多少次。来源陈述可能持续错误，读取器也可能误解陈述，因此反复提问、读取转载和寻找独立证据具有不同的信息价值。我们的目标是在明确的错误率要求下，研究这种区别如何改变获取成本。

本文采用已有的来源错误与抽取错误分层，集中考察有限校准带来的结构变化。即使系统已经知道哪种读取形式更可靠，只是不知道具体可靠率，最优分配仍可能无法简化成给所有来源使用同一读取深度。我们给出一个明确参数区域内的严格证明，并通过完美来源和已知抽取率两个控制，解释这种变化为什么与来源错误和可靠性不确定性相联系。

这段是受控理论 motivation，不添加“现实普遍符合”“我们在真实网页上验证”等句子。

## 4. 正文定理怎样压缩

### 定义与信息命题

令 h=(θ,z,p,q)，e=(j,n_A,n_B)，P_h^e 为完整块计数分布，w_e=c+ℓ(n_A+n_B)。参考数据针对报告抽取成功率，D_0=kl(p,u)+kl(q,v)。定义

\[
K(h,\alpha)=\min_{x\ge0}\sum_e w_ex_e,
\quad
\alpha D_0(h,h')+\sum_e x_eD(P_h^e\Vert P_{h'}^e)\ge1
\quad\forall h':\theta'\ne\theta.
\]

最优系数对理想完成块策略具有 E C*=K log(1/δ)+o(log(1/δ)) 的解释。正文的短证明至少说明：联合转录KL、完整类别似然的时间一致检验、强制探索与最优集合跟踪、正在线信息余量及成本时钟尾界。不能用“直接套标准定理”掩盖共同未知率、离线随机性和不同块成本。

对于主定理，z已知，备择限制为z'=z，仍对连续u,v取约束；K_L只允许总深度L，但允许该深度全部格式组成和随机分配。

### 主定理建议表述

For d=1, Lmax=6 and η=1/40, consider the known-format oracle with unknown extraction rates. For every instance satisfying

\[
|r-.6|\le1/40000,\quad |q-.6|\le1/40000,\quad |p-.95|\le1/40000,
\quad\alpha\in[.95,1.20],\quad c/\ell\in[.5,1.5],
\]

we have

\[
K_{\rm or}\le16c+18\ell,
\quad \min_{1\le L\le6}K_L\ge16c+18\ell+15\ell/7.
\]

Thus every optimal first-order allocation uses at least two distinct depths, with a relative online-cost-coefficient saving of at least5/103 against each fixed depth.

来源率r在每个实例内已知；参数盒跨实例比较，不是未知r的定理。

### 证明骨架

1. 纯优见证x_(1,0)=14、x_(2,0)=2，给成本上界。
2. 参考流弱率可精确profile为min(q,u)；950个严格有理区间覆盖完整连续备择域。
3. 对深度1与深度≥2分别给合法备择及对偶下界；全部27种格式组成被覆盖。
4. 对α、c/ℓ和三个真实率给统一余量/扰动界，得到区域。
5. 正费用、有限菜单和闭约束保证最优分配存在，严格排除所有单深度支撑。

现有证书与扰动界已经完成。接下来需要的是可读的解释和篇幅压缩，不是重新搜索有利参数。

## 5. 核心结果表与图

首选图：[theory_story.pdf](theory_story.pdf)，展示θ、V、Y和三种深度结构。它是概念图，非拟合、实测或新证书。

首选表：三个机制控制（参见理论全表§4），中心与区域区分清楚。若需数值列，中心现有界为32.947798…≤K_or≤34、每种固定深度≥41.3；这些是上下界，不能标成全部精确最优值。中心17.68%和整个盒4.85%均是各自口径的保守差。

W2a默认不进核心结果表：它已知通道、允许重访、固定硬预算、比较Bayes风险，与主定理的有限校准期望成本不是同一实验。若放一句补充，应同时写清差异和15/81严格优势、66/81平局的完整分母。

固定深度与静态设计不是同义词。主定理不排除预先安排多种深度；不能把它写成“自适应超过全部非自适应”。

原Method开发结果不作为本模型的实验。它仍可服务原共享理论稿，需独立确认和数值/最优性边界。

## 6. 五维自审与反向提纲

| 维度 | 自审判断 | 行动 |
|---|---|---|
| Contribution | 有模型内结构结果；优先权尚不确定 | 核查“未知率导致强制混合”而非泛泛分层新颖性；保留REVISE |
| Writing clarity | P1决策→P2证据单位→P3困难→P4结论→P5控制，逻辑可闭合 | 统一reading depth、source report、extraction reliability和online-cost coefficient |
| Experimental strength | 计算辅助数学证据足够支撑限定定理；无自然LLM证据 | 不包装成benchmark排名；准确说明连续域认证而非格点检验 |
| Evaluation completeness | 固定深度强对手与全部格式组合保留；负结果可列 | W2a若出现就给完整分母；不将不同模型放一张性能榜 |
| Method design soundness | 理想策略与完整块类别似然有既有证明 | 正文说明计算契约，不给实际近似优化器追加渐近最优性 |

反向提纲的每个段落都应映射到主消息。若一个段落只能介绍共享组、训练或复杂Agent而无法解释当前深度分离，应优先移出四页。

逐项主张检查见[CLAIM_EVIDENCE.csv](CLAIM_EVIDENCE.csv)。当前英文草案中数学结论均有既有证据，广义现实动机以研究设置表述；“首次”“真实Web有效”“通用Agent最优”均未进入草案。

## 7. 最小剩余工作

1. 用现有证书写出可自洽的短证明，尤其说明两类危险备择为何对深度有不同信息效率；不要声称已知全部紧约束。
2. 在ACM两栏中实际排版并检查4页限制；篇幅不够就删W2a和次要共享推论，不删主定理前提与最近邻。
3. 对最终初稿做一次针对贡献重合、Web必要性、证明充分性的审阅；这是未来动作，本轮无新独立审稿结论。

这三项完成后再判断是否值得额外模型桥接。本文作为受控理论研究不预设必须添加Qwen实验，也不要求重新启动人工事实标注。
