# Web-native theory: bounded primary-source novelty audit

**Date:** 2026-10-31. **Status:** research scoping; not an originality certificate, theorem verification, or publication recommendation. **Scope:** source provenance, persistent source errors, noisy extraction, reusable query-format reliability, activation costs, and sequential information acquisition. Twelve focal papers are inspected below. All novelty assessments are our inferences from the inspected passages.

## Main assessment

值得探索的方向是：**当网页内容本身可能错误、多个 URL 可能来自同一个信息源时，什么时候应继续换方式读取已有来源，什么时候必须付费寻找新的独立来源？** 这比把“用户偏好”改名为“网页事实”更实质地改变信息结构。

但现有文献已覆盖几个单独部件：复制依赖、来源与抽取的两层错误、跨网页/抽取模式共享可靠性、成本约束下的来源选择、相关噪声下的自适应测试、激活成本。下面的 P1–P12 给出具体证据。因此，“这些部件第一次出现在一个图里”不是足够的理论贡献。较有价值的目标是证明它们结合后，**独立来源数量、重复读取深度与学习查询形式的代价**之间出现什么不能由已有结果直接推出的边界。

Recommended claim strength now: **a motivated candidate problem with several established ancestors; the incremental theorem remains to be isolated and proved.** A focused search did not establish that the proposed joint model is absent from the literature.

## Search and verification method

The searches used bibliographic phrases and public mathematical topics only; no unpublished notes were uploaded. Sources were restricted for substantive claims to publisher proceedings, author/institution pages, and author-submitted arXiv manuscripts. Searches included:

- `Dong knowledge based trust extraction source errors`, `From Data Fusion to Knowledge Fusion`;
- `Integrating Conflicting Data source dependence`, `Less is More Selecting Sources Wisely for Integration`;
- `controlled Markov observations non-uniform control cost`, `active search switching actions`;
- `persistent classification noise repeated queries`, `budget optimal task allocation reliable crowdsourcing`;
- `Bayesian active learning noisy observations correlated costs`;
- `sequential testing sensor activation cost`, `Sequential Testing with Subadditive Costs`;
- `Search-R1`, `BrowseComp`, `Adaptive Generate-Rank-Verify`.

This is a targeted counter-overlap search, not a systematic review. References within papers provided additional leads. A search hit alone did not count as full-text reading. “Read” below means AI inspection of the listed passages, not a user-attested read mark. The twelve focal works were selected for proximity to the proposed mechanism, including negative evidence against broad novelty claims; source age is consequently concentrated in foundational work.

## Twelve focal papers

### P1. Copying and source dependence

**Dong, X. L., Berti-Équille, L., & Srivastava, D. (2009). Integrating Conflicting Data: The Role of Source Dependence. PVLDB, 2(1), 550–561.** [Publisher full text](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf).

- **Model/assumptions:** Conflicting static source values; Bayesian dependence inference. §3 assumes independent values across objects, independent copying relationships, and no copying cycles.
- **Result:** An iterative truth/dependence procedure discounts copied support and incorporates source accuracy.
- **Overlap:** Multiple agreeing URLs need not supply multiple independent observations; this is established motivation.
- **Remaining proof obligation:** Quantify the cost of adaptively acquiring fresh provenance roots versus rereading descendants, with an explicit error criterion. A known partition into exact-copy roots is a controlled special case, not a solution to general copy detection.
- **Coverage:** Abstract/introduction, §3 assumptions and dependence/vote equations, PDF pp. 1–4. No independent reproduction of experiments.

### P2. Extraction noise already changes data fusion

**Dong, X. L., Gabrilovich, E., Heitz, G., Horn, W., Murphy, K., Sun, S., & Zhang, W. (2014). From Data Fusion to Knowledge Fusion. PVLDB, 7(10), 881–892.** [Publisher full text](https://www.vldb.org/pvldb/vol7/p881-dong.pdf).

- **Model/assumptions:** Fact × source × extractor observations, with errors introduced by entity linkage and schema alignment; the study uses a static snapshot.
- **Result:** Adapts fusion procedures to extracted triples and studies probability calibration and failure modes. §3 retains extractor, URL, and extraction context as provenance.
- **Overlap:** Adding an extraction channel to source reliability is not a new Web abstraction by itself.
- **Remaining proof obligation:** A sequential allocation theorem must concern choices and costs not answered by batch fusion. Preserve the distinction between faithfully extracting a false page claim and extracting a true fact incorrectly.
- **Coverage:** Abstract, §§1–3.1, including provenance description. This audit does not certify every empirical claim.

### P3. Two error layers and grouped reliability

**Dong, X. L., et al. (2015). Knowledge-Based Trust: Estimating the Trustworthiness of Web Sources. PVLDB, 8(9), 938–949.** [Publisher full text](https://www.vldb.org/pvldb/vol8/p938-dong.pdf).

- **Model/assumptions:** Latent fact truth and latent page-provided claims, separate source accuracy and extractor recall/false-positive parameters; single-truth modeling.
- **Result:** §3 gives multilayer inference; §4 pools sparse source/extractor groups using website, predicate, page, and extraction-pattern hierarchies.
- **Overlap:** Both two-stage noise and group-shared extraction quality are direct predecessors. §5.4 explicitly leaves scalable copy detection as further work.
- **Remaining proof obligation:** Establish adaptive acquisition complexity and a nontrivial sharing-dependent price of unknown formats. Do not claim that hierarchical reliability sharing itself is new.
- **Coverage:** §§2.3–3.2, equations (5)–(9), §4, and §5.4 limitations; PDF pp. 3–4, 7, 11–12. Graphical-model factorization was read; no full proof audit.

### P4. Cost-aware source selection predates agentic search

**Dong, X. L., Saha, B., & Srivastava, D. (2012). Less is More: Selecting Sources Wisely for Integration. PVLDB, 6(2), 37–48.** [Publisher full text](https://www.vldb.org/pvldb/vol6/p37-dong.pdf).

- **Model/assumptions:** Select a source subset before integration. Gain depends on fusion accuracy; costs are additive in the main instantiation. Accuracy estimation assumes independent sources and homogeneous item error properties, using source-quality estimates.
- **Result:** Formalizes budget/quality and profit objectives, shows naive greedy selection can be poor, and proposes randomized selection.
- **Overlap:** Paying to acquire sources and deciding that some sources are not worth their cost are established problems.
- **Remaining proof obligation:** Distinguish online learning of unknown source/extractor parameters and stopping for truth recovery from offline subset-profit optimization.
- **Coverage:** Abstract, §1.4, §§2.1–2.2 and assumptions near PDF p. 4. Conference presentation was 2013; publication volume is dated 2012.

### P5. Unreliable workers and limits to adaptivity

**Karger, D. R., Oh, S., & Shah, D. (2014). Budget-Optimal Task Allocation for Reliable Crowdsourcing Systems. Operations Research, 62(1), 1–24.** [Publisher record](https://pubsonline.informs.org/doi/pdf/10.1287/opre.2013.1235); [author manuscript](https://arxiv.org/pdf/1110.3564).

- **Model/assumptions:** Binary tasks; each worker has one latent reliability shared across its batch; conditionally independent answers and equal task difficulty. Workers are fleeting and cannot be selected again after reliability is learned.
- **Result:** Nonadaptive task allocation/inference is order-optimal even against the considered adaptive class.
- **Overlap:** Shared unknown reliability does not automatically imply an adaptive advantage.
- **Remaining proof obligation:** Explain the reusable object: a source, extractor, domain, or query format that can be selected again. Show a separation under that model rather than importing one from transient workers.
- **Coverage:** Publisher abstract and manuscript introduction/model, pp. 1–4. The downloaded manuscript identifies arXiv v4 (2013), while its rendered title date is 2024; publication year comes from the publisher.

### P6. Persistent errors are an established learning model

**Jackson, J., Shamir, E., & Shwartzman, C. (1999). Learning with Queries Corrupted by Classification Noise. Discrete Applied Mathematics, 92(2–3), 157–175.** [Author institution record](https://cris.huji.ac.il/en/publications/learning-with-queries-corrupted-by-classification-noise/); [DOI](https://doi.org/10.1016/S0166-218X(99)00045-1).

- **Model/assumptions:** Persistent membership-query noise gives the same corrupted label on repeated queries to the same point. Independence is retained across appropriate distinct noise variables.
- **Result:** The abstract reports a noise-robust Harmonic Sieve for DNF under the uniform distribution.
- **Overlap:** Repetition not eliminating a fixed underlying error is an established distinction from fresh Bernoulli noise.
- **Remaining proof obligation:** Separate a persistent page claim from stochastic extraction of that claim, and analyze acquisition of new independent claims.
- **Coverage/access limit:** Institution-hosted abstract and bibliographic metadata only. Author PDF failed browser retrieval; publisher returned 403. No theorem constants or detailed proof claims are used from this work.

### P7. Bayesian design with correlated noise and unequal costs

**Golovin, D., Krause, A., & Ray, D. (2010). Near-Optimal Bayesian Active Learning with Noisy Observations. NeurIPS 23.** [Proceedings full text](https://proceedings.neurips.cc/paper/2010/file/1e6e0a04d20f50967c64dac2d639a577-Paper.pdf).

- **Model/assumptions:** Finite hypotheses/tests, known joint prior; noise can be correlated and tests have unequal costs. Noise is incorporated into latent outcome realizations.
- **Result:** EC² has a logarithmic competitive guarantee for equivalence-class determination; greedy information gain/decision value need not have comparable guarantees.
- **Overlap:** Correlated-noise adaptive testing is already covered at this level of generality.
- **Remaining proof obligation:** Unknown frequentist reliability and vanishing-error truth recovery require separate arguments. In the nonidentifiable case, §4 targets the decision made with all test outcomes, not guaranteed recovery of the true hypothesis.
- **Coverage:** §§1, 3–4, Theorems 3–4, PDF pp. 1, 4–6. Finite known-prior reduction does not automatically yield a tractable or sharp solution to an expanding-source model.

### P8. Controlled observations and costs already have KL-rate optimality

**Nitinawarat, S., & Veeravalli, V. V. (2015). Controlled Sensing for Sequential Multihypothesis Testing with Controlled Markovian Observations and Non-Uniform Control Cost. Sequential Analysis, 34(1), 1–24.** [Publisher metadata](https://www.tandfonline.com/doi/abs/10.1080/07474946.2014.961864); [full manuscript v2](https://arxiv.org/pdf/1310.1844v2).

- **Model/assumptions:** Finitely many hypotheses, actions, and observed states; known positive controlled transition probabilities; positive action costs.
- **Result:** §5 and Theorem 5.1 characterize optimal asymptotic cost using a stationary KL information-rate/expected-cost ratio.
- **Overlap:** Cost-normalized information allocation and Markov dependence alone are not new.
- **Remaining proof obligation:** Hidden persistent content, irreversible activation, expanding roots, or continuous nuisance parameters need a valid reduction or new analysis. A growing belief state is not automatically their finite observed Markov state.
- **Coverage:** §3 equation (3.1), §§4–5, Theorem 5.1, and appendix positivity-of-cost passage. No wholesale import of its risk definition into the proposed model.

### P9. Switching costs can disappear in first-order asymptotics

**Vaidhiyan, N. K., & Sundaresan, R. (2015). Active Search with a Cost for Switching Actions. Information Theory and Applications Workshop.** [Author manuscript and venue comment](https://arxiv.org/abs/1505.02358); [full text](https://arxiv.org/pdf/1505.02358).

- **Model/assumptions:** Finite actions/hypotheses; known action-conditioned observation laws; bounded switching costs with zero cost for remaining on an action; finite likelihood-ratio second moments and discrimination assumptions.
- **Result:** Sluggish Procedure A approaches the no-switching first-order cost as error and its switching parameter decrease.
- **Overlap:** A fixed setup/switch penalty need not change the leading asymptotic rate.
- **Remaining proof obligation:** Show why fresh-root activation must occur proportionally to required evidence, rather than being a bounded startup expense or avoidable switching. Fixed finite domains with one activation each may only contribute lower-order cost.
- **Coverage:** §II assumptions/cost model, Theorem 6 and discussion, PDF pp. 2–5. This audit uses the 2015 workshop manuscript, not a guessed later journal version.

### P10. Activation costs also have combinatorial testing theory

**Harris, B., Nagarajan, V., & Tan, R. (2025). Sequential Testing with Subadditive Costs. IPCO 2025, pp. 283–296.** [Official conference program](https://ipco25.cs.jhu.edu/program/); [full manuscript](https://arxiv.org/html/2501.18010v1).

- **Model/assumptions:** A finite series system; independent tests with known passing probabilities; testing reveals a component outcome. Costs may be subadditive, including machine activation and tree/routing structures.
- **Result:** A general oracle-dependent approximation and a machine-activation approximation are provided.
- **Overlap:** Paying once to enable a collection of tests is established theory.
- **Remaining proof obligation:** Our target would need uncertain extraction of persistent claims, unknown shared reliability, and a truth-recovery error constraint. The cited model stops upon a revealed failure or after checking every component; it is not noisy certification of a shared hidden truth.
- **Coverage:** §§1.1–1.2, cost definitions, and §2 truncation argument. The manuscript was inspected, not independently proof-checked.

### P11. Learned search policies are an empirical ancestor

**Jin, B., Zeng, H., Yue, Z., Yoon, J., Arık, S. Ö., Wang, D., Zamani, H., & Han, J. (2025). Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning.** [Inspected arXiv v3](https://arxiv.org/html/2503.09516v3); [COLM paper URL](https://openreview.net/pdf?id=Rwhi91ideu).

- **Model/assumptions:** RL trajectories interleave reasoning and retrieval, using final-answer reward and masking retrieved tokens from policy loss. The inspected experiments retrieve from a 2018 Wikipedia dump.
- **Result:** Empirical QA improvements, not a source-provenance or fixed-confidence optimality theorem.
- **Overlap:** Adaptive query wording/tool calling is already central to search agents.
- **Remaining proof obligation:** A Web-theory contribution should identify what evidence is genuinely new and when to stop; learning another search policy is not that theorem.
- **Coverage:** arXiv v3 §§3.1–3.4 and 4.3. OpenReview blocked direct access with a browser challenge; versions show different reported scores, so no effect size is pooled or quoted here.

### P12. Recent theory already separates acquisition and costly verification

**Dughmi, S., Haghifam, M., & Kalayci, Y. H. (2026). Adaptive Generate-Rank-Verify: Inference-Time Search with Costly Verification. arXiv:2605.17609v1.** [Primary full text](https://arxiv.org/html/2605.17609v1).

- **Model/assumptions:** Fresh generated candidates, cheap scores, paid verifier labels, and a positive probability of success. Correctness is defined by the verifier. The main guarantee assumes nondecreasing score-conditioned success.
- **Result:** ADAP has a constant-factor expected-cost guarantee against a distribution-aware optimum; the paper also studies structural lower bounds.
- **Overlap:** Unknown reliability relationships and separate acquisition/verification costs already motivate theoretical inference-time search.
- **Remaining proof obligation:** Distinguish finding one accepted candidate from recovering several truths without an authoritative verifier, especially with repeated views of one persistent source claim.
- **Coverage:** §§2–4, Theorem 4.2, §7 limitations. Publication status verified only as a preprint; this audit did not validate its full proof.

## What is standard, and where a new proof could lie

The following is a proposed mathematical diagnostic, not a theorem attributed to the cited papers.

Fix a binary fact θ and nuisance parameters. Let independent provenance root r contain a persistent binary claim U_r, with P(U_r = θ) = a_r, where 1/2 < a_r < 1. All subsequent extractions of descendants of root r are generated from U_r by the same conditional channel under both truth hypotheses. The extraction channel may depend on a fixed query-format parameter. Query actions may use observed history, but must not obtain other truth-bearing evidence.

For a **fixed finite set of roots**, the entire interaction transcript H is a randomized post-processing of their claims U. Consequently,

    KL(P_1^H || P_0^H) ≤ KL(P_1^U || P_0^U)
                         = Σ_r kl(a_r, 1 − a_r).

This is a direct data-processing calculation, not a novel general principle. Repeated stochastic extraction can recover page content more accurately while still failing to repair the page's factual error. With a prior assigning positive probability to both truths, overlapping root-claim distributions leave a positive Bayes error even after all fixed root claims are known perfectly. A theorem formalizing this elementary special case can serve as a lemma or counterexample, but is unlikely to carry the paper alone. Persistent-label noise and the truth/content/extraction separation already have close precedents in [P6](https://cris.huji.ac.il/en/publications/learning-with-queries-corrupted-by-classification-noise/) and [P3](https://www.vldb.org/pvldb/vol8/p938-dong.pdf).

For an adaptive number of fresh roots, obtaining an expected-root-count lower bound additionally requires the sequential likelihood chain rule and integrability/optional-stopping justification. It is not valid simply to substitute a random root count into the fixed-set inequality. Root-type selection, side information, and calibration outcomes must all appear in the likelihood model. Root independence also has to be assumed or established; different URLs do not establish it.

The potentially useful next target is a **joint acquisition frontier** with explicit competing actions:

1. acquire a new independent root, paying activation cost;
2. read an already acquired root again, paying extraction cost;
3. select a query/extraction format whose quality is unknown but shared across an observable group;
4. stop with a stated truth-recovery error guarantee.

To make a claim beyond the existing ancestors, prove at least one of the following, rather than treating the entire list as already feasible:

- A sharp acquisition-cost characterization showing when and how independent-root activation remains a leading-order expense, while deeper reading trades off against imperfect extraction.
- A lower/upper bound on the additional cost of learning group-shared formats **under the persistent-content model**. State what replaces the old smallest-group criterion, and why old Bernoulli action counts cannot just be reused.
- A separation between policies that treat agreeing pages/extractions as fresh evidence and a valid root-aware policy, evaluated on both error control and total cost. Showing that a deliberately misspecified independence baseline fails is diagnostic; it is not by itself a separation from strong dependency-aware methods.

These are research obligations, not verified novelty claims. General cost-aware design already has strong positive results in [P7](https://proceedings.neurips.cc/paper/2010/file/1e6e0a04d20f50967c64dac2d639a577-Paper.pdf), [P8](https://arxiv.org/pdf/1310.1844v2), and [P10](https://arxiv.org/html/2501.18010v1). The proof must identify precisely which assumptions prevent applying those results directly.

## Important distinctions for the eventual manuscript

| Distinction | Consequence for the candidate theory |
|---|---|
| URL versus provenance root | A URL is an access location. Exact copy families require a separate relation; ordinary domain grouping is insufficient. |
| Root persistence versus extraction randomness | Independent decoding calls do not imply independent factual evidence. |
| Correct page interpretation versus true external fact | Extraction accuracy can rise while factual error remains. |
| Unknown format versus unknown source credibility | These are different nuisance variables; one calibration set need not identify both. |
| Group sharing versus independent replication | Shared quality supports learning transfer, but does not make within-root observations independent. |
| One-time domain setup versus activation of every fresh root | The former may be O(1) for fixed domains; the latter can matter at leading order. |
| Switching cost versus activation cost | Returning to an already opened root may be free of activation cost even if switching still costs something. |
| Fixed-confidence versus fixed-budget performance | A finite-budget accuracy advantage does not certify the stopping guarantee or expected-cost optimum. |
| Verifier acceptance versus latent truth recovery | A final authoritative verifier removes an uncertainty that this project may specifically aim to model. |

The table is an analysis of modeling choices, not an empirical assertion about all websites or all LLMs.

## Boundaries and unresolved search coverage

- This audit verifies existence and the listed supporting passages. It is not a retraction-status audit or a complete bibliography. Publisher/author text was inspected; no Crossref/OpenAlex retraction API workflow was run.
- P6 has abstract-only semantic coverage. P11 uses a specifically identified preprint for substance because direct proceedings retrieval was blocked. These limitations must remain visible if those references become central to a theorem claim.
- Additional screened context included BrowseComp, a contemporary live-browsing benchmark, the classical Track-and-Stop literature, and newer heterogeneous-cost sequential-testing work. They were not needed to establish the overlaps above and are not counted among the twelve focal comparisons. No “complete through 2026” claim is made.
- Before asserting originality of an acquisition frontier, perform a dedicated second search on sequential experimental design with random effects, multi-stage sampling, costly cluster acquisition, hidden-state controlled sensing, and source selection with dependence. The present search does not rule out a direct result in those adjacent formulations.
- Relevance to WWW follows here from the explicitly modeled Web mechanisms; it is not an assessment of a current conference's acceptance probability or track policy.
- AI-assisted source search and comparison were used. No model/API training, data collection, experiment reruns, or modifications of historical research artifacts were performed by this bibliography task.

**Handoff:** keep the full theory exploration open, but make the immediate proof target narrower than “Web-aware adaptive querying.” The strongest candidate from this audit is the acquisition-versus-rereading problem under persistent source claims, followed by the cost of learning a reusable extraction format. A new theorem, not the names of the variables, must establish the advance.
