# Primary-source comparison and limits of the novelty claim

Checked: 2026-11-03. This is a bounded comparison, not a systematic review,
priority certification or external novelty judgement. Public searches used
generic problem descriptions and bibliographic titles; no unpublished notes,
manuscript or experimental records were uploaded.

| Primary source | Relevant established content | Boundary for this work |
|---|---|---|
| [Degenne, Koolen and Menard, NeurIPS 2019, Non-Asymptotic Pure Exploration by Solving Games](https://papers.neurips.cc/paper_files/paper/2019/hash/8d1de7457fa769ece8d93a13a59c8552-Abstract.html) | General structured pure-exploration queries and information/game allocations | Replacing full-state alternatives by wrong-output alternatives is established machinery. No first general decision-information program claim. |
| [Fiez, Jain, Jamieson and Ratliff, NeurIPS 2019, Sequential Experimental Design for Transductive Linear Bandits](https://papers.neurips.cc/paper_files/paper/2019/hash/8ba6c657b03fc7c8dd4dff8e45defcd2-Abstract.html) | Best-item identification with measurement and recommendation sets that may differ; includes a recommender example | Learning only the best item rather than the entire utility vector is already a central objective. That change of target alone is not novelty. Their displayed channel is linear measurement with additive noise, rather than the particular unknown shared format channel here. |
| [Kulkarni and Tal, On Fractional Block Sensitivity, ECCC TR13-168, revision 1](https://eccc.weizmann.ac.il/report/2013/168/revision/1/download) | Minimal flipping blocks, fractional certificates, and their relation to randomized certificate complexity; Definition 2.1 | The flip-cover LP and its certificate interpretation are prior concepts. Our rho is reciprocal fractional certificate complexity for a Boolean output, not a newly introduced complexity measure. |
| [Gu, Li and Xu, Tight Bounds for Noisy Computation of High-Influence Functions, Connectivity, and Threshold, arXiv:2502.04632v2](https://arxiv.org/html/2502.04632v2) | Noisy Boolean queries, threshold computation, and sharp query bounds with fixed independent flip noise | No first noisy-threshold or first certificate-saving claim. Their threshold result has a different channel/information setting and worst-instance/growing-problem analysis; it does not directly supply the present pointwise group-type/calibration criterion. This distinction is not proof that all related work lacks such a result. |
| [Garivier and Kaufmann, COLT 2016](https://proceedings.mlr.press/v49/garivier16a.html) | Information allocations, tracking and expected stopping-time analysis | These tools are background. The original repaired expected-time addendum is still required for the shared-rate finite-calibration specialization. |

The bibliographic records and relevant passages for the first four sources
were opened in this turn. The original project already records the fifth
source and its use; this round does not claim a new full reading of it.

## What is the candidate new result?

Within the original project's observation model, the intended additions are:

1. The analytic unknown-rate oracle expression in terms of existing
   certificate geometry, together with a group-restricted certificate equality
   criterion in its stated regime.
2. The complete threshold-catalogue zero-premium rule at alpha=0, determined
   by the largest supporting group and decision flip distance.
3. The finite positive-calibration rule using only active groups and the
   number of simultaneous preference flips needed to change the item.
4. The resulting state-dependent changes and concrete counterexamples to
   transplanting the original full-recovery smallest-group rule.

These are new derivations relative to the original `Theory_Note.md`. Whether
they are new to the literature requires a wider comparison; none of the
sources inspected is claimed to establish a negative priority result by its
abstract alone. In particular, generic decision-level GLR stopping and the
advantage of not reconstructing every latent parameter should be attributed
as existing methodology, even when useful in this application.

## Web relevance and remaining empirical gap

The decision is a personalized choice between known catalogue items, and the
information cost is paid in elicitation interactions. This is closer to the
recommendation decision than the independent-slot equivalence in the first
draft. The model remains generic beyond the Web; Web importance must come
from the platform/user problem and eventual valid interface evidence, not a
claim that threshold functions themselves are Web-specific.

The explicit catalogue neighborhood in the theory note rules out an isolated
equal-weight construction. It does not validate natural users, the symmetric
channel, known groups, labelled reference streams or independent answers.
No new user simulator or real recommendation evaluation was executed.
