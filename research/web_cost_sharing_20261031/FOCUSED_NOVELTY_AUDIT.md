# Focused novelty audit: source cost and shared query formats

Date searched: 2026-10-31. Scope: [MODEL_AND_SCOPE.md](MODEL_AND_SCOPE.md). This is a bounded primary-source comparison, not an exhaustive priority search, a proof certificate, or a recommendation about acceptance probability. No experiments or model calls were performed. The sealed `web_native_theory_20261031` files were only read.

## Assessment

**The generic cost-weighted information program is established theory. The proposed explicit sharing threshold remains a candidate model-specific contribution whose precise priority is unestablished.** The inspected sources do not directly state the particular condition

\[
\max_{L\in\mathcal M(c)}
\frac{V_L+(k_{\min}-1)U_L}{A_L}\geq1,
\qquad
\mathcal M(c)=\operatorname*{argmax}_{1\leq L\leq L_{\max}}
\frac{A_L}{c+\ell L}.
\]

Here, for a pure-format block of depth \(L\), let \(P_{+,a}^{(L)}=r\,\mathrm{Bin}(L,a)+(1-r)\,\mathrm{Bin}(L,1-a)\), and let \(P_{-,a}^{(L)}\) be its reflection. The quantities are \(A_L=D(P_{+,p}^{(L)}\Vert P_{-,p}^{(L)})\), \(U_L=D(P_{+,p}^{(L)}\Vert P_{+,q}^{(L)})\), and \(V_L=D(P_{+,p}^{(L)}\Vert P_{-,q}^{(L)})\). Thus \(k_{\min}\) counts facts sharing a format, while \(L\) counts repeated extractions from one root.

This negative search observation does not establish that the condition is new. Its strongest possible value is a closed-form answer to a narrow question: when can optimal reading depth substitute for sharing a reusable unknown format across multiple facts? It should be positioned as a structural extension of the current theory, conditional on a complete proof, rather than a new general framework for cost-aware information acquisition.

The distinctions below matter more than the terminology “Web source” or “agent.”

1. A completed block from a fresh root is one action with a known finite-alphabet law under each state \(s=(\theta,z)\). Integrating out the persistent binary report incorporates all within-block dependence. With fixed \(L_{\max}\), this reduction removes the growing-state obstacle present in unrestricted revisiting problems.
2. The output is \(\theta\), not the complete state \((\theta,z)\). Competing states with the same answer are nuisance states, and requiring their exclusion can artificially increase the characteristic cost.
3. The benchmark knows \(z\) and therefore removes nuisance alternatives. This differs from the “oracle” in several controlled-sensing papers, which uses the true state to choose allocations but still has to discriminate it against the original alternative set.
4. Choosing one convenient tied oracle optimizer cannot prove necessity. The entire oracle-optimal allocation set must be considered. Handling nonunique allocations is itself established; the possible contribution is the exact reduction of that set to the stated scalar condition in this model.

## Search method and reading boundary

The search began with the supplied arXiv identifiers and the prior twelve-paper map. Additional searches targeted controlled/composite testing with costs, nuisance parameters, clustered/repeated measurements with acquisition costs, nonunique pure-exploration allocations, and structured cost-aware exploration. Representative exact queries were:

- `"sequential hypothesis testing" "nuisance" "costs"`
- `"controlled sensing" "composite" "cost"`
- `"sequential" "testing" "random effects" "cost" hypothesis`
- `"sequential design" "cluster" "sampling cost" hypothesis testing`
- `optimal allocation repeated measurements cluster sampling cost random effects information`
- `"pure exploration" "cost" "structured" "oracle"`
- `"Cost-Aware Exploration for Structured Bandits"`
- `"group sequential" "variable group sizes" sampling cost Novikov`

Search-engine results were discovery aids. Substantive comparisons below use author manuscripts, publisher/proceedings texts, or explicitly identified author abstracts. Preprints were included because the user specifically requested recent theory comparisons. Unrelated clinical trial, regression, and statistical-contract papers were screened out; none supplies negative evidence about originality. This is not a PRISMA review, and no invented database-wide counts are reported.

The corpus is intentionally concentrated on mathematical methods. Geographical coverage is inapplicable to this theory question. Eight substantive comparisons follow, plus one unresolved-access lead. Originality, correctness of every cited proof, retraction status, and publication acceptance were not certified. Semantic Scholar/OpenAlex/Crossref metadata enrichment was not performed; author/title/arXiv-version matching was used to avoid counting versions twice.

## Closest primary sources

### 1. Cost-aware testing explicitly contains the generic KL program

**Vershinin, G., Cohen, A., & Gurewitz, O. (2026). _On Cost-Aware Designs for Sequential Hypothesis Testing_. arXiv:2512.19067v3.** [Versioned full text](https://arxiv.org/html/2512.19067v3); [version history](https://arxiv.org/abs/2512.19067).

**Verified model/result:** Finite hypotheses and actions; known action-dependent laws; conditionally independent samples; positive costs and finite likelihood-ratio second moments. The fixed-cost analysis minimizes expected cost under an average-error constraint. Corollary 1 and Proposition 1 give the max–min KL-per-cost criterion and its linear-programming transformation. Theorems 2–3 state asymptotic optimality of cost-aware Chernoff/NJ1 procedures. Random-cost/preemption extensions are outside the present comparison.

**Reading:** §§II–IV, including Theorem 1, Corollary 1, Proposition 1 and Theorem 2 proof. Latest version verified as 24 September 2026; initial submission was December 2025. Preprint status only. Full proof correctness was not independently certified.

**Implication:** Do not claim the cost-normalized LP or adapting Chernoff allocation to unequal costs as new. A block-as-action reduction is available. Their average-error/full-state formulation still requires adaptation to this project's uniform error and answer-class objective; citing the theorem alone does not prove the proposed iff.

### 2. Cost-normalized controlled sensing predates the recent paper

**Nitinawarat, S., & Veeravalli, V. V. (2015). _Controlled Sensing for Sequential Multihypothesis Testing with Controlled Markovian Observations and Non-Uniform Control Cost_. Sequential Analysis, 34(1), 1–24.** [Full manuscript v2](https://arxiv.org/pdf/1310.1844v2); [publisher record](https://www.tandfonline.com/doi/abs/10.1080/07474946.2014.961864).

**Verified model/result:** Finite hypotheses, controls and observed states; known positive controlled transition kernels and positive action costs. Equation (5.1) optimizes stationary KL information divided by expected control cost. Theorem 5.1 gives asymptotic lower and matching upper bounds. Example 5.1 explicitly shows costs changing the optimal control mixture.

**Reading:** Model and §§4–5 previously inspected; §5.1, Theorem 5.1 and Example 5.1 reread here. Manuscript v2 is dated June 2014; the journal article is 2015.

**Implication:** Neither adding costs nor showing that costs alter an optimal sensing action is new. The specific group-sharing threshold is not stated in the inspected result. For the current finite-block problem, the simpler independent-action formulation is more natural than introducing a controlled Markov state.

### 3. Composite testing is the relevant answer-versus-state ancestor

**Deshmukh, A., Bhashyam, S., & Veeravalli, V. V. (2019). _Sequential Controlled Sensing for Composite Multihypothesis Testing_. arXiv:1910.12697v1.** [Full text](https://arxiv.org/html/1910.12697v1); [metadata](https://arxiv.org/abs/1910.12697).

**Verified model/result:** Finite controls, each with a one-parameter exponential-family observation law; disjoint composite hypothesis sets satisfying geometric assumptions. Lemma 1 minimizes over states outside the correct hypothesis set. GLR stopping and forced-exploration tracking attain the sample-count lower bound. Proposition 1's continuity argument explicitly assumes a unique maximizing allocation.

**Reading:** §§II–V, especially equations (17)–(22), (28), (32)–(42), Proposition 1 and its uniqueness qualification. Theorem statements and relevant proof structure were inspected, not every appendix step. Only the 2019 preprint version is relied upon.

**Implication:** Recovering an answer without identifying every nuisance parameter is established. This paper cannot be invoked unchanged for arbitrary binomial-mixture blocks or tied optimal depths. A finite-state proof here can be simpler, but must supply its own cost conversion, stopping guarantee, and expected-cost argument.

### 4. Nonunique oracle allocations already have a careful theory

**Degenne, R., & Koolen, W. M. (2019). _Pure Exploration with Multiple Correct Answers_. NeurIPS 32.** [Proceedings full text](https://proceedings.neurips.cc/paper/2019/file/60cb558c40e4f18479664069d9642d5a-Paper.pdf).

**Verified model/result:** Structured bandit parameter sets within one-dimensional canonical exponential families, with a finite answer space. Theorem 4 studies set-valued oracle allocations; Proposition 5 establishes convexity for a fixed answer. Theorem 7 gives asymptotic optimality of C-tracking for single-answer problems even with nonunique allocations. The paper explains why D-tracking may fail to track a convex optimal set.

**Reading:** §§1–4, including model definitions, Theorem 4, Proposition 5, Lemma 6, Theorem 7 and Remark 8. The full supplement was not proof-audited. OpenReview access hit a browser challenge; the official proceedings PDF was accessible.

**Implication:** Treating ties correctly is a required technical obligation, not a new concept. The proposed maximization over all oracle-optimal depths could still be a useful specialized simplification. Multiple optimal allocations should not be confused with multiple correct answers: this project's requested truth vector is unique.

### 5. Setup cost plus variable block size is established sequential design

**Novikov, A. (2023 preprint revision). _Group sequential hypothesis tests with variable group sizes: optimal design and performance evaluation_. arXiv:2210.07203v2.** [Versioned full text](https://arxiv.org/html/2210.07203v2); [history](https://arxiv.org/abs/2210.07203).

**Verified model/result:** Two simple hypotheses; a finite menu of batch sizes selected from previous observations; batch cost \(c(m)\), including setup costs. Dynamic programming characterizes optimal truncated and limiting plans; the i.i.d. case admits likelihood-ratio-based rules and numerical evaluation.

**Reading:** Introduction, §§2.1–2.3 and 3.1, plus the numerical recursion in §4.1. The v1 title differs; this entry uses v2. Publisher DOI retrieval failed, so the verified preprint is the substantive citation.

**Implication:** “Pay setup, then choose how many measurements to take” is not a new decision structure. The present persistent latent report changes the block law, and shared unknown formats introduce composite alternatives absent from the inspected model. Those changes must yield the specific threshold rather than merely another batch-cost dynamic program. Here “group” means an observation batch, not a sharing group of facts.

### 6. Cluster acquisition versus within-cluster depth has older precedents

**List, J. A., Sadoff, S., & Wagner, M. (2011). _So you want to run an experiment, now what? Some simple rules of thumb for optimal experimental design_. Experimental Economics.** [Author-hosted publisher PDF](https://rady.ucsd.edu/_files/faculty-research/sadoff/List_Sadoff_Wagner_Optimal_Sample_Design_Experimental_Economics_2011.pdf).

**Verified model/result:** The cluster-design calculation separates within- and between-cluster variation and charges a fixed cost per new cluster plus a cost per subject. Equation (10) shows the optimal cluster size increasing with the square root of the setup-to-subject cost ratio, adjusted by the variance ratio. The authors explicitly present this as a compilation of earlier design results, not original derivations.

**Reading:** Introduction and cluster-design subsection, especially PDF pp.12–14 and equation (10).

**Implication:** The qualitative claim that expensive independent units encourage more observations per unit is old. This is an adjacent design precedent, not evidence that the current binary nuisance-format iff is already known. It concerns fixed-budget precision/power, not simultaneous truth recovery with uniformly vanishing error. The original priority of the cluster formula was not traced here.

### 7. The Web-specific two-layer reliability abstraction is established

**Dong, X. L., et al. (2015). _Knowledge-Based Trust: Estimating the Trustworthiness of Web Sources_. PVLDB, 8(9), 938–949.** [Publisher full text](https://www.vldb.org/pvldb/vol8/p938-dong.pdf).

**Verified model/result:** Latent fact truth and page-provided claims are separated from extraction errors. The model distinguishes source accuracy from extractor recall/false-positive behavior. Source and extractor hierarchies pool statistical strength across sparse groups.

**Reading:** §§2.3–3.2, equations (5)–(9), §4 and limitations were inspected in the preceding audit; the publisher PDF was retrieved again here. This pass did not redo the empirical audit.

**Implication:** Persistent source content, noisy extraction and group-shared reliability are credible Web abstractions but are not independently novel. The missing result in this predecessor is the specific sequential cost/sharing characterization, not the existence of two error layers. This model also does not validate the assumed independent-root structure of actual websites.

### 8. A recent human–AI theory already combines latent items, acquisition costs and optimal verification

**Ham, D. W., Zhao, X., Jasin, S., & Yang, F. (2026). _Human–AI-Powered Hypothesis Testing: Cost-Aware Selective AI Scoring and Sequential Human Escalation_. arXiv:2609.28859v1.** [Full text](https://arxiv.org/html/2609.28859v1).

**Verified model/result:** Binary latent item labels distinguish two population proportions. A fixed pool is purchased in advance; each item admits one noisy finite-valued AI report and one exact human label. Theorem 4.10 gives an information/cost lower bound; Theorem 5.3 states first-order optimality of SCALE. Section 6 studies unknown AI-output laws using paired AI–human pilot data, including charging pilot cost.

**Reading:** §3, §4.4, §5.3 and §6.3; theorem statements, assumptions and selected derivations. No independent full-proof audit. Verified as a September 2026 preprint.

**Implication:** Cost-optimal information acquisition with latent items and noisy AI is already a close contemporary topic. This paper has exact-label verification and growing paired calibration; the present model has neither. It does not state the current depth/shared-format condition. Do not suggest that this project's general information/cost motivation alone separates it from recent AI-assisted inference theory.

### Additional lead with incomplete access

**Liu, X., Qin, C., & You, W. _Cost-Aware Exploration for Structured Bandits_.** The [author's current research page](https://cnyouwei.github.io/) identifies it as work being prepared for submission to Operations Research. Its abstract discusses optimal posterior-error decay per spent budget, structured exponential families, and a cost-aware policy analyzed through differential inclusions.

The indexed PDF URL returned 404 when opened. The search-indexed first page has a different author order from the current website; the current version is unresolved. Only the author-hosted abstract is verified here. This is a relevant lead, not a certified theorem comparison or evidence of publication. Posterior-error exponents should not be equated automatically with uniform fixed-confidence expected-cost optimality.

## Generic consequence versus the specialized iff

The following is this audit's mathematical interpretation of the proposed model, not a theorem attributed to a source.

Let \(P_s^a\) denote the distribution of a completed block and let \(b_a=c+\ell L_a\). The standard information lower-bound program has the form

\[
K_u(s)=\min_{x\geq0}\sum_a b_ax_a,
\quad
\sum_a x_a D(P_s^a\Vert P_{s'}^a)\geq1
\quad\text{for every }s'\text{ with }\theta'\neq\theta.
\]

The corresponding known-\(z\) oracle program retains only alternatives compatible with that known value. Once matching achievability and attainment are established, equality of the two costs is equivalent to **some oracle-optimal allocation satisfying all additional nuisance-alternative constraints**. This feasibility-on-the-optimal-set statement follows directly from nested feasible sets. It is not a standalone new principle.

The substantive specialization would have to establish all of the following:

- **Oracle support:** Pure good-format blocks characterize the relevant oracle-optimal allocations. Any claim of strict dominance must handle mixed blocks and equality cases, rather than excluding them by definition.
- **Depth ties:** All depths in \(\mathcal M(c)\) remain available. Prove why mixtures of tied depths cannot rescue a case in which every listed scalar ratio is below one, and why one qualifying depth suffices. This is stronger than checking a numerically chosen optimizer.
- **Hard alternatives:** Reduce every truth/type alternative to the expression involving \(A_L,U_L,V_L\). Same-answer type changes alone are not terminal error events, but type changes combined with truth errors are.
- **Smallest group:** Show why the common parameters, identical action menus and separate per-fact root purchases make \(k_{\min}\) sufficient. The same simplification need not survive heterogeneous source qualities, costs, or joint source purchases.
- **Attainment:** Give a uniformly valid stopping rule and a matching expected-cost result without importing uniqueness assumptions or silently requiring full-state recovery.

No inspected source supplies this entire reduction or its particular scalar expression. Conversely, obtaining it by explicit evaluation of a classical characteristic program is compatible with a useful model-specific contribution; the use of established tools alone does not settle novelty either way.

## What the cost interpretation may legitimately say

Under a successful proof, the notable mechanism would be that deeper extraction has two different information effects: truth-flip information is capped by the persistent root, while information distinguishing extraction channels can continue increasing. Optimizing depth for source cost can therefore change whether a truth-optimal allocation also supplies enough nuisance discrimination. This connects source acquisition cost to a sharing requirement, rather than merely reporting that an optimal allocation changes with price.

The quantifiers must remain visible:

- Fixed finite \(L_{\max}\) does not allow arbitrary depth. Increasing \(c\) can favor the cap without making the threshold attainable.
- A large-cap/high-cost existence result is separate from the fixed-cap iff. It needs an explicit order or joint choice of limits; it is not a uniform finite-budget guarantee.
- For a singleton, the displayed condition is \(V_L/A_L\geq1\). Divergence of \(U_L\) alone is insufficient unless an additional proved relation such as \(V_L\geq U_L\) is invoked.
- The truth-information cap compares hypotheses with the same extraction channel. It does not cap KL against a different channel; treating these quantities identically would obscure the mechanism.
- A no-premium result concerns the leading coefficient of expected cost. It does not say every algorithm works, all finite-error costs coincide, or the format must be explicitly estimated.
- These statements retain known \(r,p,q\), fresh independent roots, fixed completed blocks, no revisits and no direct-type/calibration queries. They do not resolve the original unknown-level model or establish these assumptions for real Web data.

## Recommendation for the current paper

**Conditional GO as a restricted theoretical extension; REVISE as the main novelty claim or a Web-general optimality claim.** If the full iff and its attainment proof survive review, it is more informative than the preceding double-limit balanced-block proposition: it can identify a finite-cost, finite-menu boundary and explain when sharing is or is not needed. That makes it a reasonable proposition/corollary in the current theory narrative, with a compact illustrative calculation and full assumptions in an appendix.

The paper should attribute the general KL/cost and composite-testing machinery explicitly, then emphasize the specialized criterion and its mechanism. Strong wording such as “first cost-aware Web acquisition theory,” “first treatment of persistent extraction errors,” “first handling of optimal-depth ties,” or “expensive sources always remove the learning penalty” is unsupported. The present audit neither found an exact predecessor nor established absence of one. A publication-level originality claim still requires focused checking of the unresolved structured-cost lead and the closest invariant/composite-design results, followed by comparison against the final proved statement rather than a broad problem description.
