# 候选 WWW 理论短文：贡献审计

日期：2026-11-01。审计类型：同一写作上下文内的证据整理与反重合比较；非独立盲审、系统综述、全文优先权排查或证明正确性再认证。公开查询使用一般学术主题和公开论文信息，未上传未发表理论文本到外部模型。

**结论：GO 写候选稿；原创性和投稿就绪度保持 REVISE。** 支撑候选贡献的是本模型中对全部固定深度的严格分离及机制恢复关系。单独的分层图、来源饱和、KL 配置和“多动作可能更好”均不足以作为主要新意。

## 1. 实质贡献与基础工具分开

| 内容 | 判断 | 建议表述 |
|---|---|---|
| θ→V→Y 分层 | 已有直接先例 | 采用来源事实错误与抽取错误的分层表示，引用 Knowledge-Based Trust |
| 同源复制不能当独立证据 | 已有直接先例 | 用于定义证据单位和说明适用范围 |
| 以 KL/费用为准则分配动作 | 已有一般理论 | 特化并证明所用模型的条件；不命名为新的通用原则 |
| 离线校准与在线信息共同进入下界 | 已有直接先例 | 明确共同未知参数、参考通道及无条件风险保证的差别 |
| 变批量与启动成本 | 已有直接先例 | “来源深度是一种带启动费的动作”不是新贡献 |
| 当前模型必须混合深度的严格区域定理 | **候选结构贡献** | 即使已知最佳形式，在指定未知率/有限校准模型内任何固定深度都严格次优 |
| 完美来源退化及已知率对照 | 机制支撑和精确连接 | 表明哪种模型条件改变了深度结构，不能扩成现实因果结论 |
| 原最小共享组 iff | 另一条候选结构贡献 | 可独立组织原研究故事；一般多读版尚未完成 |
| W2a 超过全静态类的有限分离 | 候选辅助结果，创新风险较高 | 在已知通道有限模型内给精确见证；不当作学习算法优越性 |

## 2. 十个最近邻/边界来源

以下是范围核查，不把“未在查阅段落见到”提升为“不存在”。来源页面本轮均已打开；范围较深的条目还承接2026-10-31的本地逐节审计。标注的本轮阅读范围不代表全文每个证明均已重验。

| ID / 一手来源 | 已经覆盖什么 | 与当前主定理的差别 / 风险 | 本轮范围 |
|---|---|---|---|
| P1 [Dong等，2009，Integrating Conflicting Data](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf) | 复制依赖改变真值融合 | provenance 本身不是新意；我们的主张是来源读取深度与未知抽取率 | 摘要与引言；之前审计含模型 |
| P2 [Dong等，2015，Knowledge-Based Trust](https://www.vldb.org/pvldb/vol8/p938-dong.pdf) | 区分来源错误、抽取错误，联合估计可靠性 | 三层变量和分层可靠性不可宣称首次提出；当前研究额外关心顺序获取的最优成本结构 | 摘要、引言；之前审计含两层模型 |
| P3 [Dong等，2012，Less is More](https://www.vldb.org/pvldb/vol6/p37-dong.pdf) | 来源质量与整合成本的权衡及来源子集选择 | “有成本地选来源”不新；尚需区分静态融合与未知率下的读取深度必要性 | 摘要与引言；之前审计含问题定义 |
| P4 [Golovin等，2010，Noisy Bayesian Active Learning](https://proceedings.neurips.cc/paper/2010/file/1e6e0a04d20f50967c64dac2d639a577-Paper.pdf) | 已知联合先验下，有相关噪声和不同测试费用的自适应设计 | 通用自适应/相关噪声不是新意；不能仅凭 W2a 的动态优于静态主张重大新理论 | 摘要；之前审计含EC²保证范围 |
| P5 [Deshmukh等，2019v1，Composite Controlled Sensing](https://arxiv.org/html/1910.12697v1) | 对连续备择优化动作分布、GLR和渐近采样复杂度 | 多支持动作是既有设计变量；本模型类别混合、共同参数、校准和费用需单独处理 | 模型、Lemma1及式18、唯一性条件；承接前次逐节审计 |
| P6 [Agrawal等，2023v1，Offline-data Best-Arm Identification](https://arxiv.org/html/2306.09048v1) | 离线与在线 KL 合并；风险对两阶段共同取概率 | 不能把校准信息项包装成新工具；当前离线数据只校准 nuisance 而非当前答案 | §2.1、Theorem2.1及风险定义；其余边界承接前审 |
| P7 [Novikov，2023v2，Variable Group Sizes](https://arxiv.org/html/2210.07203v2) | 两简单假设下变组大小，包含启动费＋逐观测费；通用部分允许非iid联合律 | 不能声称首次研究带启动费的动态深度；需突出未知率使一阶最优支撑发生具体变化 | §2.1、动态规划附近、§4.2.1费用例子 |
| P8 [Vershinin等，2026v3，Cost-Aware Sequential Testing](https://arxiv.org/html/2512.19067v3) | 有限已知假设/动作的最优信息费用权衡和构造 | 成本加权最优性不是新；当前复合连续未知率、校准和特定深度结构不同 | 模型、固定费用目标与成本分解；保证边界承接前审 |
| P9 [Ham等，2026v1，Human–AI-Powered Hypothesis Testing](https://arxiv.org/html/2609.28859v1) | 购入潜在项目、AI报告、精确人工核验、不同费用、未知通道pilot | 极近的成本与校准祖先；其每项目最多一次AI/一次人类查询与当前同一报告重复抽取不同 | 查询限制、Theorem5.3、§6开头；前审另核对pilot风险口径 |
| P10 [Jia等，2024v2，Noisy Optimal Decision Trees](https://arxiv.org/abs/2312.15357) | 噪声/持久结果下自适应决策树与排名问题 | 对 W2a 是应进一步深读的近邻；不能声称已排除其全部结果 | **仅元数据和摘要，完整模型重合仍未解决** |

这些材料支持缩窄主张，不构成原创性证书。所有论文对比都是我们基于所列范围的判断。

## 3. 最终可交付的三项 contribution

**C1 — 校准改变来源读取深度结构。** 在一事实、已知来源率、最佳格式已知、抽取率未知、两路有限有标签校准及完成块菜单下，证明一个明确参数区域内任何固定深度都严格次优。比较对象保留各深度的全部格式组合，没有用“全重读/全换新”弱基线替代。

**C2 — 严格机制对照和原理论恢复。** r=1 时成本恰为原信息复杂度乘以 ℓ+c/N；已知率时存在单深度最优。结合C1，说明来源错误与未知抽取率的交互能改变最优结构。控制属于不同信息条件，目的不是公平算法排名。

**C3 — 可复核的连续域分离。** 以统一可行分配上界、各固定深度全菜单下界、连续参数域区间证书和扰动界排除网格假象。作为证据和技术支撑，不宣称区间算法或连续性原理本身新。

C1是主要科学主张。C2解释，C3支撑。四页不足时优先压缩一般信息复杂度推导，不删除关键假设和最强固定深度对手。

必须额外区分：C1证明不同深度的混合必要，未证明观测自适应严格胜过全部预定混合设计。前者改变设计的支撑，后者比较动作对历史的依赖。这不是同一项贡献。

## 4. 证明可以怎样讲清楚

目前严格证书提供的是以下闭环：

1. 选择不同深度的可行一阶分配 x_(1,0)=14、x_(2,0)=2，成本 U=16c+18ℓ。
2. 对整个错误事实＋连续可靠率备择域认证其信息约束，而不是只检查网格点。
3. 对深度1，使用抽取率移至1/2的备择；对深度≥2，使用保持真实率但翻转事实的备择。分别得到适用于全部格式组合的下界。
4. 区间与导数界给出统一严格余量，因此从中心点扩到明确参数盒。

这说明浅读与深读可以对不同危险备择具有不同的相对信息效率。**尚未证明上述两类备择恰好构成最优设计的全部紧约束**，也未求出完整区域内的精确最优分配。

若要继续加强理论，最值得做的是从证书中提炼一个可读的结构充分条件：何时不同深度的信息向量/费用比使所有单深度失去可行性或最优性，并说明本模型何以满足。普通的“一个可行上界低于所有受限下界”只是证明模板，不单列为新的通用定理。

## 5. 拒稿风险与当前处置

| 风险问题 | 当前能回答什么 | 仍需做什么 |
|---|---|---|
| 这不就是一般复合检验的多动作设计吗？ | 工具属于已有体系；我们证明特定来源模型中单深度化简的失败，且有清楚控制 | 精简展示实际危险备择；排查最贴近的重复测量/变组大小结果，不能靠模型部件多声称新颖 |
| 为什么是 Web？ | 研究来源报告、重复抽取、独立证据获取与预算分配；第一页能具体定义决策 | 不泛称provenance learning；解释只覆盖语义限定的报告单位，非任意整页 |
| r已知、根独立、校准流带高低标签是否太理想？ | 这是给系统较充分信息后仍存在的分离；数学范围透明 | 限制必须显眼，不能由理论反推现实满足；未来验证不是当前证明的一部分 |
| 参数区域是否过窄？ | 证明正体积及明确校准/费用区间，排除孤立点 | 三个率半径仅2.5e−5；不可称覆盖广泛实际环境；可研究更大证书但不以拓盒代替科学解释 |
| 是否证明了完整 Agent 最优？ | 只证明完成块策略类的信息系数与理想构造 | 正文标题、模型、定理、图注都写清；W2a逐步策略是另一模型 |
| 有没有实际 Web / LLM 效果？ | 没有；W1未建立有效测量集，W2a风险来自规定概率律 | 作为纯理论短文定位；若后来做桥接，单列协议和有限经验主张 |
| 能否四页讲完？ | 以一主定理、两短控制和计算辅助证明骨架可尝试 | 需要实际排版检验；不可把核心证明全移到默认不计页数的附录 |

## 6. 审计决策

- **写作 GO**：已有足够的模型内结果组织候选稿。
- **理论完整度：主定理限定范围内已闭合**，本轮未发现需要补齐才能陈述该定理的前置结果；仍不是新一轮独立证明审阅。
- **新颖性 REVISE**：未找到所查段落直接覆盖强制深度混合区域，但尚未排尽最邻近结果或证明其非直接推论。
- **经验有效性未建立**：W1/W1.1/W2a均不能证明自然共享可靠性或真实读取独立性。
- **提交就绪度 REVISE**：还缺排版后的自洽初稿和针对这份最终稿的审阅；新增模型调用不是当前必要条件。

不要把“没有发现相同定理”改写成“首个”；也不要把本轮建议写作解读为已承诺投稿或预判录用。

## 7. 禁止的主张及可替代句

| 不受支持的句子 | 可用替代 |
|---|---|
| We introduce source/extraction error decomposition. | We adopt a source/extraction decomposition to study acquisition depth under finite calibration. |
| Our agent is asymptotically optimal on the Web. | An ideal policy attains the information coefficient within the specified completed-block model. |
| Adaptive querying improves accuracy by4.85%. | Allowing multiple depths reduces the asymptotic online-cost coefficient by at least4.85% relative to every fixed depth in the certified region. |
| The optimal policy uses exactly two good-format depths. | Every optimal first-order allocation uses at least two depths; a two-depth good-format allocation supplies a feasible upper bound. |
| Necessary depth mixing proves an adaptive agent beats every static design. | The depth theorem excludes single-depth designs; W2a studies a separate adaptivity-versus-all-static comparison. |
| Our benchmarks validate natural Web reliability. | Controlled calculations verify the claimed mechanism under the stated observation laws. |
| The smallest group controls all Web acquisition costs. | The smallest-group criterion is exact in the original model and selected Web boundaries; the general finite-calibration multi-read reduction remains open. |

原有新颖性审计：[Web基础](../web_native_theory_20261031/WEB_THEORY_NOVELTY_MAP.md)、[成本与共享](../web_cost_sharing_20261031/FOCUSED_NOVELTY_AUDIT.md)、[有限校准](../web_unknown_calibration_20261031/CALIBRATION_NOVELTY_AUDIT.md)、[Oracle结构](../web_oracle_structure_20261031/STRUCTURE_LITERATURE.md)。本文件补充最终故事的比较，不覆盖或改写这些历史判断。
