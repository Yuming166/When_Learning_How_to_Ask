# 一手相关文献核验记录

日期：2026-10-31。用途：支持 `WWW_SHORT_OUTLINE.md` 的准确定位；只读公开文献，不上传本地未发表材料。以下是针对性的强相关来源审查，不是系统综述或全面优先权认证。不借搜索摘要证明某文“没有”某项结果；对全文访问不足之处明确降级。

## S1. Controlled sensing：简单假设与一般先验背景

Sirin Nitinawarat, George K. Atia, Venugopal V. Veeravalli. **Controlled Sensing for Multihypothesis Testing**. IEEE Transactions on Automatic Control, 58(10), 2013.

- 一手入口：[arXiv:1205.0858](https://arxiv.org/abs/1205.0858)；[作者原始 PDF](https://vvv.ece.illinois.edu/papers/journal/niti-atia-veer-tac-2013.pdf)。核验摘要和作者 PDF 首页。
- 可支持：controlled observations 下的 sequential multihypothesis test 和一阶渐近最优性早已存在；原文也考虑 hard risk constraints。
- 不支持：本项目首创主动选择高信息动作、先估计再查询，或似然停止。
- 本文差异属于具体未知通道和共享结构；不能用 S1 的一般框架直接替代 finite-calibration 期望尾界。

## S2. Composite controlled sensing：最直接的理论定位

Aditya Deshmukh, Srikrishna Bhashyam, Venugopal V. Veeravalli. **Sequential Controlled Sensing for Composite Multihypothesis Testing**. 核验版本 arXiv:1910.12697v1，2019；期刊版信息仅作来源线索，本提纲论断以该具体原文为准。

- 一手全文：[arXiv HTML](https://arxiv.org/html/1910.12697)；[PDF](https://arxiv.org/pdf/1910.12697)。读 §II model、§III lower bound、Proposition 1、§IV Theorems 1–3、控制策略与证明组织。
- 可支持：finite controls、单参数指数族、composite hypothesis sets、KL 信息率及期望停止时间渐近上界。
- 精确限制：§II hypotheses 为有限个互不相交相对开凸集合之并，并有 separation 假设；Proposition 1 后显式假设最大化解唯一，再使用连续 optimizer。**不是**一个无条件涵盖所有非唯一优化器与边界点的现成定理。
- 本项目须单独处理：共享 `p,q` 所诱导的可行参数结构、当前两条 finite calibration streams、非唯一最优集的累计跟踪和对所有较晚 horizons 的联合 tail。
- 最高风险错误：把“原文有 expected stopping theorem”误写成“本项目 executable Python 已由原文保证”。

## S3. Best-arm identification：tracking 技术归属

Aurélien Garivier, Emilie Kaufmann. **Optimal Best Arm Identification with Fixed Confidence**. COLT 2016, PMLR 49:998–1027.

- 一手入口：[PMLR record](https://proceedings.mlr.press/v49/garivier16a.html)；[PDF](https://proceedings.mlr.press/v49/garivier16a.pdf)。读 lower bound、C/D-Tracking、Theorem 14、Appendix B（尤其 Lemmas 15/17）及 Appendix D 的期望分析。
- 可支持：固定置信 BAI 的信息复杂度、最优比例 tracking 与 Chernoff stopping、强制探索和期望复杂度分析均为已有方法。
- 精确限制：Theorem 14 的假设和其 error control theorem 要结合使用；不能把某个 threshold 的经验更快当作其理论保证。
- 本项目应归属技术：estimated information allocation、累计目标跟踪、vanishing exploration、GLR 主框架。新增点应在结构性解析结果及该模型的充分条件。

## S4. Structured pure exploration：比只引用标准 BAI 更强的先行框架

Rémy Degenne, Wouter M. Koolen, Pierre Ménard. **Non-Asymptotic Pure Exploration by Solving Games**. NeurIPS 2019.

- 一手入口：[官方 proceedings record](https://papers.neurips.cc/paper_files/paper/2019/hash/8d1de7457fa769ece8d93a13a59c8552-Abstract.html)；[官方 PDF](https://proceedings.neurips.cc/paper/2019/file/8d1de7457fa769ece8d93a13a59c8552-Paper.pdf)。读 §§1–2 的环境集合 `M`、有限答案集及正确答案函数、GLRT/saddle-point 框架与 assumptions。
- 可支持：一般指数族 structured pure exploration 不限于“挑一个均值最高臂”；其信息优化、GLRT、optimism、tracking 和计算/样本折中已有系统研究。
- 本项目与之关系是**特殊共享通道模型的显式结构求解**，不能泛称“已有方法不能利用共享结构”。
- 核验限制：其一般 framework 不自动等于本项目 finite labelled calibration 的现成充分条件；如要宣称完全包含或严格超越，需要另给模型嵌入与假设逐项核对。

## S5. Offline-data BAI：校准信息不是全新的困难

Shubhada Agrawal, Sandeep Juneja, Karthikeyan Shanmugam, Arun Sai Suggala. **Optimal Best-Arm Identification in Bandits with Access to Offline Data**. arXiv:2306.09048v1，2023。保留为 preprint，不臆造已发表会议。

- 一手全文：[arXiv HTML](https://arxiv.org/html/2306.09048)；[PDF](https://arxiv.org/pdf/2306.09048)。读 §2 的模型、P1、Theorem 2.1，§3 及 Appendix B.2。
- 可支持：离线样本来自同一 bandit instance；offline policy 可未知；correctness 对 offline+online 联合随机性定义；lower bound 的 KL 约束含离线计数；tracking 型方法匹配特定渐近复杂度。
- Appendix B.2 明确区分对每个离线 realization 都成立的 conditional δ-correctness；不能把 unconditional guarantee 描述为逐离线样本的保证。
- 本项目差异：两条校准流标识高低通道水平，而不是当前每个 task action 的已知标签样本；未知 `θ,z` 以及 partition 使备择结构不同。
- 不写“本文首次将 offline data 与 fixed-confidence active learning 结合”。

## S6. Adaptive crowdsourcing：最直接的问题动机

Ittai Abraham, Omar Alonso, Vasilis Kandylas, Aleksandrs Slivkins. **Adaptive Crowdsourcing Algorithms for the Bandit Survey Problem**. COLT 2013, PMLR 30:882–910.

- 一手入口：[PMLR record](https://proceedings.mlr.press/v30/Abraham13.html)；[PDF](https://proceedings.mlr.press/v30/Abraham13.pdf)。读 §§1–2，尤其 PDF 第 2 页的 single microtask 边界与第 3 页 response-distribution model。
- 可支持：crowd quality 未知，算法自适应选 crowd、获取独立回答、选择停止时刻并输出聚合答案；源选择与答案聚合并非新问题。
- 精确区别：该文明确聚焦单 microtask，并将跨 microtask 潜在质量关系的学习分开。本项目研究多个坐标上的共同未知可靠度、分组共享格式及 exact zero-premium boundary。
- 不写“众包文献都需要已知工人可靠度”。

## S7. Adaptive task assignment：不能遗漏多任务异质性

Chien-Ju Ho, Shahin Jabbari, Jennifer Wortman Vaughan. **Adaptive Task Assignment for Crowdsourced Classification**. ICML 2013, PMLR 28(1):534–542.

- 一手入口：[PMLR official record](https://proceedings.mlr.press/v28/ho13.html)。本轮核验原始摘要与书目信息；未对全文 theorem assumptions 作逐项审计。
- 可支持的保守陈述：异质分类任务的 task assignment 与 label inference 已被共同研究，原文给出 online primal-dual 的自适应分配方法。
- 不能支持的负面断言：该文从未使用某种共享/校准结构，或不可能有更强样本保证。本轮不作此类断言。

## S8. Preference elicitation：效用和 rationality 联合估计

Taku Yamagata, Tobias Oberkofler, Timo Kaufmann, Viktor Bengs, Eyke Hüllermeier, Raúl Santos-Rodríguez. **Relatively Rational: Learning Utilities and Rationalities Jointly from Pairwise Preferences**. ICML 2024 Workshop on Models of Human Feedback for AI Alignment；不是 ICML main-track 论文。

- 一手来源：[作者机构原始研究记录与摘要](https://research-information.bris.ac.uk/en/publications/relatively-rational-learning-utilities-and-rationalities-jointly-/)；[OpenReview 原始 PDF](https://openreview.net/pdf?id=N9o8afNUfr)。搜索服务返回原始 PDF 的标题、作者与摘要；本轮直接打开 OpenReview 遇 browser verification，故不声称已完整审阅其 theorem/experiments。
- 可支持：在共享效用下使用 Boltzmann rational model 联合估计 labeller rationalities 与 utilities，已有将偏好与反馈可靠程度一起估计的研究。
- 本项目建模差异：固定二元符号、两个 accuracy levels、组共享 preferred format 和固定置信全向量恢复；这不等于经验上更真实或更有效。
- 不支持：该论文没有最优性理论、没有有限样本结果、没有 calibration，或本文首创联合学习。若最终 related work 需要这些更强比较，必须再取可读全文核验。

## 后续检索线索（不作为已核验定理引用）

TIFR 2025 原始研讨会摘要 [STCS Symposium 2025](https://www.tcs.tifr.res.in/~symposium/stcs-25.html) 中 Agniv Bandyopadhyay 关于 offline-data BAI 的报告，提到 offline-sufficiency boundary 附近 GLR sample complexity 的 noise 限制。这里仅保存为**需要追踪完整原稿的研究线索**，不把摘要当作本项目证明或反例。它提醒我们，正在线信息余量和 finite-calibration uniform tail 不能从标准 tracking 结论自动继承。

## 写作裁决

可用：*We solve an explicit shared-unknown-channel information problem and characterize its zero-premium sharing boundary, building on established controlled-sensing and pure-exploration machinery.*

不可用：“首个未知可靠度询问算法”“首次联合偏好与可靠度学习”“tracking 本身是本文创新”“offline information 未被先前研究”“现有所有方法不能共享信息”。当前来源只支持精确模型与结构结果的候选贡献，不支持全面优先权或真实交互有效性主张。
