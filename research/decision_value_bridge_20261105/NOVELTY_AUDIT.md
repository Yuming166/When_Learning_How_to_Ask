# Bounded novelty audit: joint-belief decision value

Date: 2026-11-05. Decision: **useful method instantiation; not a new VOI
principle or new generic safety theorem**. The main theoretical contribution
remains the exact zero/positive reliability-premium boundary. The finite-budget
DV loop can make the decision objective explicit, but does not inherit the
information program's asymptotic efficiency.

This is a targeted primary-source check, not a systematic review or priority
certification. Queries used bibliographic metadata only. No manuscript or
private data was uploaded. Local paper/theorem/proof companion were read.

## Verified nearby work and exact distinctions

| Source and checked locator | Established content | Consequence for this revision |
|---|---|---|
| Boutilier, Zemel, Marlin (2003), *Active Collaborative Filtering*, UAI, pp. 98–106; author-hosted PDF, Section 2, Eq. (2), PDF p. 3 | Myopic EVOI selects a query by expected improvement in optimal posterior recommendation value. The same section explicitly discusses pairs of queries that are jointly useful while individually ineffective. | DV under winner 0-1 loss is a specialization of this established decision-theoretic template. The within-channel myopia example is an explicit model instance, not discovery of myopic complementarity. Their main value is expected recommendation rating; ours is probability of selecting the unique winner. |
| Degenne and Koolen (2019), *Pure Exploration with Multiple Correct Answers*, NeurIPS 32; proceedings PDF, Sections 1–2 | Multiple acceptable answers alter pure-exploration geometry and can remove convexity properties used in singleton Track-and-Stop arguments. | An acceptable-item/NO_BUY application requires its own answer correspondence and invalid-action alternatives. Merely citing this paper does not extend the singleton catalogue theorem or prove optimality of DV. |
| Donmez, Carbonell, Schneider (2009), *Efficiently Learning the Accuracy of Labeling Sources for Selective Sampling*, KDD, pp. 259–268; author PDF, abstract/introduction | Jointly learning label-source accuracy and selecting informative labels with unknown source reliability already has direct precedent. | Neither unknown reliability nor learning task labels and source quality together is a standalone novelty claim. The present distinction is the specified shared-format channel and catalogue-dependent premium characterization. |
| Filstroff et al. (2024), *Targeted Active Learning for Bayesian Decision-Making*, TMLR; published PDF title page/abstract; 2021 arXiv predecessor | Acquisition targets information gain about the posterior optimal decision. | Decision-directed acquisition is established. Their stated objective is decision-label IG, which differs from the expected increase in the largest posterior success probability. The simple reversal proved here is against joint-state IG, not automatically against their criterion. |
| Krause and Guestrin (2009), *Optimal Value of Information in Graphical Models*, JAIR 35:557–591; author-submitted arXiv record and journal reference | Observation selection and conditional observation plans are established VOI problems, including sensor settings and substantial computational barriers. | Multi-step lookahead is not conceptually new. Our enumerated small-channel counterexample does not establish a tractable general optimal policy or a greedy approximation guarantee. |

Primary sources:

1. [Boutilier et al., author-hosted full paper](https://www.cs.toronto.edu/kr/papers/acf.pdf); [author publication record confirming venue/pages](https://research.google/pubs/active-collaborative-filtering/).
2. [Degenne and Koolen, NeurIPS proceedings](https://papers.neurips.cc/paper_files/paper/2019/hash/60cb558c40e4f18479664069d9642d5a-Abstract.html); [full paper](https://papers.neurips.cc/paper_files/paper/2019/file/60cb558c40e4f18479664069d9642d5a-Paper.pdf).
3. [Donmez et al., author-hosted full paper](https://www.cs.cmu.edu/~schneide/rsp767-donmez.pdf); [CMU publication record and bibliographic entry](https://publications.ri.cmu.edu/efficiently-learning-the-accuracy-of-labeling-sources-for-selective-sampling).
4. [Filstroff et al., published TMLR PDF](https://openreview.net/pdf?id=KxPjuiMgmm); [author-submitted preprint](https://arxiv.org/abs/2106.04193).
5. [Krause and Guestrin, author-submitted record with 2009 journal metadata](https://arxiv.org/abs/1401.3474).

## Claim decisions

**Supportable framing.** We instantiate myopic decision value using a joint
belief over preferences and shared response reliability, while retaining a
policy-independent frequentist recommendation gate. We establish exact
within-model examples of IG/DV disagreement and of the myopic rule ignoring
useful shared-format learning. These examples expose what the acquisition
objective does and does not optimize. The structural premium theorem explains
which decision geometry permits cost-free format uncertainty at first order;
it does not certify the DV allocator's efficiency.

**Do not claim:** first decision-aware recommendation elicitation; first joint
learning of preferences and reliability; first observation that entropy can
misalign with decisions; novel nonnegative VOI; novel policy-independent gate;
DV asymptotic optimality; termination from a zero/nonzero DV test; multiple-answer
premium characterization; superiority established by a constructed reversal.

The bridge is conceptually coherent without pretending that (1) the original
continuous frequentist coefficient, (2) the finite-prior Bayes acquisition
objective, and (3) the gate are the same theorem. Report each separately.

## Verification receipt and remaining gaps

- Full-text passages were checked for the most direct EVOI and multiple-answer
  precedents. Other comparison rows are limited to the stated primary-source
  abstract/introduction or publication metadata; no uninspected theorem is cited.
- Semantic Scholar metadata requests for all five sources returned HTTP 429.
  `SOURCE_METADATA_CHECK.json` retains the unavailable status. Verification
  therefore used the primary records listed above; no S2 verification is claimed.
- DOI resolution for the KDD and JAIR candidates was inaccessible through the
  browser. The supplied BibTeX omits the KDD DOI rather than upgrading a secondary
  record. The JAIR DOI is retained because the author-submitted journal record
  explicitly supplies it; resolver verification remains unavailable.
- The OpenReview discussion URL printed in the TMLR PDF was inaccessible. Use
  the accessible published PDF URL; its title page verifies the June 2024 status.
- No global literature priority, independent expert proof review, or formal
  proof-assistant verification is claimed.
- The exact belief examples are not proved reachable from the experimental
  uniform prior. The auxiliary coordinate is decision-irrelevant in the chosen
  catalogue. These limitations must travel with the examples.
- The explicit perturbation neighborhood preserves the admissible product-prior
  family. It does not establish an all-priors or all-catalogues performance result.

Ready-to-use verified bibliography entries are in `verified_references.bib`.
