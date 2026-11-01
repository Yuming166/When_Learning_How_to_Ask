# Focused novelty audit: unknown extraction rates and finite calibration

Date: 2026-10-31. Scope: [MODEL_AND_SCOPE.md](MODEL_AND_SCOPE.md). This is a bounded primary-source audit, not an exhaustive originality search or an independent certification of the project's proofs. Historical theory snapshots were read only. No model calls, empirical runs, or numerical experiments were performed for this audit.

## Assessment

**The general calibration-adjusted information program, mixture-based stopping argument, and cost-weighted allocation principle have close established ancestors. The promising contribution is a model-specific structural result about how unknown extraction rates change the source-cost/sharing tradeoff.** In particular, a proof or certified counterexample concerning the known-rate pure-good oracle and scalar sharing threshold would be more informative than presenting another generic KL optimization problem.

None of the inspected papers states the exact combination of persistent source blocks, shared unknown good formats, two labelled reference streams with size proportional to log(1/delta), and an oracle that knows only the shared formats. This is a bounded observation, not a priority claim. The collection of these ingredients alone is insufficient evidence of a new theorem.

The label “ancillary calibration” needs care: the reference observations do not depend on the current truths or group types, conditional on p,q, but they do depend on p,q. They are therefore not ancillary for the full unknown parameter. Their high/low stream labels are substantive information supplied by the model.

## Search and reading boundary

This pass reused the [previous cost/sharing audit](../web_cost_sharing_20261031/FOCUSED_NOVELTY_AUDIT.md) and its verified sources. Additional searching was restricted to multinomial mixture tests and fixed-confidence identification with offline data. Five closest sources are detailed below; one supporting general-GLR reference is identified separately. Author manuscripts and official proceedings/journal texts were inspected. Search snippets were not used as evidence for theorem scope. No exhaustive citation-network search, publication-status certification, or full proof audit was attempted.

### 1. Offline information already appears additively in optimal identification bounds

**Agrawal, S., Juneja, S., Shanmugam, K., & Suggala, A. S. (2023). _Optimal Best-Arm Identification in Bandits with Access to Offline Data_. arXiv:2306.09048v1.** [Versioned full text](https://arxiv.org/html/2306.09048v1); [metadata](https://arxiv.org/abs/2306.09048).

**Verified scope:** Independent arms in a single-parameter exponential family, one best arm, offline observations from the same instance, followed by adaptive online sampling. The offline quantity can depend on delta. Theorem 2.1 combines expected offline and online counts in the KL lower bound. Correctness averages over both stages. Appendix B.2 shows that correctness conditional on every offline realization imposes a purely online information lower bound. Theorem 3.1 supplies joint delta-correctness; Theorem 3.3 treats expected sample complexity with qualifications excluding critical offline-quantity windows.

**Reading:** §§2–3.1, Theorems 2.1, 3.1 and 3.3, and Appendix B.2 including its conditional change-of-measure argument. Only v1 is relied upon.

**Relevance/limit:** Calibration KL credits and the joint-versus-conditional distinction have a direct precedent. The paper does not supply the present shared-parameter categorical-mixture theorem, unequal-cost objective, or every-alpha expected-cost conclusion. Its best-arm pairwise reduction cannot be imported as a one-truth-flip reduction here.

### 2. Composite controlled testing already separates answers from nuisance states

**Deshmukh, A., Bhashyam, S., & Veeravalli, V. V. (2019). _Sequential Controlled Sensing for Composite Multihypothesis Testing_. arXiv:1910.12697v1.** [Full text](https://arxiv.org/html/1910.12697v1); [metadata](https://arxiv.org/abs/1910.12697).

**Verified scope:** Finite controls with one-parameter exponential-family observations and composite hypotheses satisfying separation/geometric conditions. Lemma 1 minimizes over parameters outside the correct hypothesis set, rather than requiring recovery of every nuisance parameter. GLR stopping and forced-exploration tracking achieve sample-count asymptotics under the stated assumptions. Proposition 1 explicitly assumes a unique maximizing allocation.

**Reading:** §§II–V and the relevant lower-bound, continuity, stopping and tracking statements were inspected in the preceding stage and reused here.

**Relevance/limit:** A truth vector can be an answer class containing many z,p,q states. That idea is established. The finite-alphabet mixture family here is not automatically a one-parameter exponential family for each control; shared p,q constraints, nonunique optimizers, unequal costs, and delta-dependent offline data require their own argument. A nuisance-parameter GLR is not itself a new methodology.

### 3. Dirichlet mixtures provide a direct categorical stopping ancestor

**Lindon, M., & Malek, A. (2022). _Anytime-Valid Inference For Multinomial Count Data_. NeurIPS 35.** [Official proceedings PDF](https://papers.nips.cc/paper_files/paper/2022/file/12f3bd5d2b7d93eadc1bf508a0872dc2-Paper-Conference.pdf); [author full text](https://arxiv.org/html/2011.03567).

**Verified scope:** Multinomial observations, a point null, and a Dirichlet-mixture alternative. The beta-function Bayes factor is a test martingale; Ville's inequality supplies time-uniform type-I error control, with confidence sequences obtained by inversion. Uniform Dirichlet parameters are an available choice.

**Reading:** Official PDF pp.1–4, especially §2, equation (3), Theorems 2.1–2.2 and the confidence-sequence construction. Full appendix proofs were not independently certified.

**Relevance/limit:** Treat each completed source block as one categorical outcome. A product of independently mixed action laws gives a convenient dominating predictive law, even if it ignores the physical shared-parameter constraints. Extending the product to predictably chosen actions and adding the two reference streams is a standard likelihood-ratio construction; it is not a verbatim theorem of this paper. The within-root Bernoulli-independence shortcut is unnecessary and invalid after marginalizing the persistent report.

### 4. Unequal sampling costs already lead to KL-per-cost allocation

**Vershinin, G., Cohen, A., & Gurewitz, O. (2026). _On Cost-Aware Designs for Sequential Hypothesis Testing_. arXiv:2512.19067v3, 24 September 2026.** [Versioned full text](https://arxiv.org/html/2512.19067v3); [version history](https://arxiv.org/abs/2512.19067).

**Verified scope:** Finite hypotheses/actions with known observation laws, positive costs, and likelihood-ratio moment assumptions. Corollary 1 and Proposition 1 express the max–min information-per-cost criterion and its LP reformulation. Theorem 2 gives a matching cost-aware sequential construction within its formulation.

**Reading:** §§II–IV, including Theorem 1, Corollary 1, Proposition 1 and the Theorem 2 proof, were inspected in the preceding stage. Preprint status only.

**Relevance/limit:** Charging c+ell L for a completed action does not create a new information-theoretic allocation principle. Continuous unknown rates, joint reference data, and an answer-class error criterion are substantive extensions to prove, not consequences of citing the finite-hypothesis result. Its state-informed allocation benchmark also differs from an oracle that removes type uncertainty while retaining rate uncertainty.

### 5. Unknown AI channels with a pilot are close, but error guarantees matter

**Ham, D. W., Zhao, X., Jasin, S., & Yang, F. (2026). _Human–AI-Powered Hypothesis Testing: Cost-Aware Selective AI Scoring and Sequential Human Escalation_. arXiv:2609.28859v1.** [Full text](https://arxiv.org/html/2609.28859v1).

**Verified scope:** Latent binary items, finite AI reports, exact human labels, acquisition costs, and two population hypotheses. Section 6 estimates unknown AI-report channels from a paired pilot. Theorem 6.1 controls nominal errors conditional on a good-pilot event; Corollary 6.2 adds the pilot-failure probability unconditionally. With their delta_m=m^-2, the displayed sublinear-in-log-error pilot schedule leaves an unconditional additive term much larger than exponentially small nominal test errors.

**Reading:** §§3, 4.4, 5.3 and 6.1–6.3; this pass additionally checked the pilot confidence radius, smoothing, Theorem 6.1, and Corollaries 6.2–6.5.

**Relevance/limit:** Unknown-channel cost-aware inference with calibration is already a close topic. Its stated good-pilot cost result should not be cited as the present exact uniform-delta unconditional theorem without addressing the failure budget. This is a scope distinction, not a claim that the paper is erroneous. Its human-labelled pilot/main-stage verifier also differs from this model's nuisance-only reference experiments.

**Supporting GLR/tracking reference.** Kaufmann and Koolen, _Mixture Martingales Revisited with Applications to Sequential Tests and Confidence Intervals_, JMLR 22(246), 2021: [official PDF](https://jmlr.org/papers/volume22/18-798/18-798.pdf). Section 4, Definition 14 and Propositions 15–16 link general answer-set GLRs, uniform error control and information lower bounds. Theorem 17 assumes unique, continuous optimal weights for its expected-time conclusion. The paper's one-dimensional exponential-family assumptions do not automatically encompass these categorical mixtures. Relevant statements were inspected, not every proof. For set-valued allocation tracking, the preceding audit separately verifies Degenne–Koolen's 2019 results; ties are an established technical issue.

## What the generic machinery gives in this model

The formulas in this section are this audit's specialization of standard change-of-measure and mixture arguments, not quotations or purported new general results. Let s=(theta,z,p,q), let a be any allowed completed block, let b_a=c+ell L_a, and write P_s^a for its full categorical law. For an alternative s'=(theta',z',u,v) with theta' different from theta, define

\[
H(p,q;u,v)=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]

The joint transcript KL is

\[
M_\delta H(p,q;u,v)
+\sum_a\mathbb E_s[N_a]\,D(P_s^a\Vert P_{s'}^a).
\]

Uniform delta-correctness bounds this below by kl(1-delta,delta). With R=log(1/delta), M/R tending to alpha, and x_a representing expected counts divided by R, the natural coefficient program is

\[
\begin{split}
\inf_{x\ge0}\quad &\sum_a b_a x_a,\\
\text{subject to}\quad
&\alpha H(p,q;u,v)+\sum_a x_a D(P_s^a\Vert P_{s'}^a)\ge1
\quad\text{for every wrong-answer alternative }s'.
\end{split}
\]

This is a **convex semi-infinite linear program in x**. For each fixed alternative the constraint is affine. The continuous inner search over u,v can nevertheless be nonconvex because P is a latent-source mixture. Convexity in allocations does not certify a local numerical minimizer over alternative parameters. Grids, local optimization and exact global certificates must remain distinguishable.

Calibration contributes once to the joint constraint. Duplicating this global credit for each fact or group would double-count observations. The known-z oracle keeps exactly the same unknown u,v and reference data, while restricting z'=z. Equality of the learner and oracle coefficients is equivalent, when optima are attained, to the existence of an oracle-optimal allocation feasible for the learner's additional alternatives. That optimal-set feasibility statement is generic nested-program geometry. An explicit reduction to a useful threshold would be the structural result.

Reference data have zero KL against alternatives with the same p,q and different truths. Thus no amount of this nuisance-only calibration can by itself resolve current truths. This differs from offline best-arm observations that can directly identify the answer. Also, alpha=0 includes diverging but sub-logarithmic M; it does not mean that no reference observations exist. The limit alpha to infinity is a separate coefficient limit, not the finite-alpha experiment.

## A standard full-categorical stopping construction

For action a=(j,n_A,n_B), let K_a=(n_A+1)(n_B+1), the number of possible pairs of positive counts. Take independent uniform Dirichlet mixtures on each action's K_a-category law, and independent Beta(1,1) mixtures on the two reference streams. Denote the resulting joint predictive likelihood by Q_t and the physical-model likelihood under s by L_s(t). Predictable action-selection probabilities are the same under both and cancel in their likelihood ratio.

Under each true s, Q_t/L_s(t) is a nonnegative likelihood-ratio martingale through the reference and online observations. After calibration it begins with a random value of expectation one; it must not be silently reset to one conditional on each reference record. The saturated categorical maximum likelihood obeys

\[
\frac{\sup L_{\mathrm{sat}}(t)}{Q_t}
\le (M_\delta+1)^2
\prod_a {N_a(t)+K_a-1\choose K_a-1}.
\]

Consequently a sufficient GLR threshold is

\[
\beta_t=\log(1/\delta)+2\log(M_\delta+1)
+\sum_a\log{N_a(t)+K_a-1\choose K_a-1}.
\]

Use the supremum physical likelihood in the numerator and the supremum over all states with a different truth vector in the denominator. On a wrong declaration the denominator contains the true state. Saturated domination and Ville's inequality then control the overall error by delta. With this single dominating mixture, an additional union bound over truth vectors is not necessary. All likelihoods include both reference streams.

This supplies a finite-delta validity route; it does not alone prove eventual stopping or optimal expected cost. With fixed finite action alphabets and sample counts of order R, the extra threshold is O(log R). Exploiting that fact still requires consistency, tracking and tail control under the actual acquisition-cost clock.

## Why the known-rate oracle argument cannot simply be reused

At known p,q, a p-accurate binary extraction can be independently flipped with probability

\[
t(p,q)=\frac{p-q}{2p-1}
\]

to produce a q-accurate extraction. This gives the known-rate Blackwell comparison between pure-good and mixed blocks of equal depth.

Across an unknown-rate parameter family this kernel depends on the state. More directly, hold theta,z,p fixed and vary q: a pure-good block has the same law, while a block containing low-format extractions generally changes its law. No single parameter-independent Markov kernel from that pure-good action can reproduce all those mixed-action laws. This is an action-experiment non-dominance argument over the full parameter family.

**The limitation is precise:** failure of that Blackwell proof does not itself prove that mixed blocks are necessary for optimal truth-only acquisition, nor does it establish dominance or non-dominance of the complete experiment including finite calibration. A strict cost separation needs a valid model-specific argument or certificate. In particular, “the oracle knows z” must not be silently replaced by “the oracle knows z,p,q.”

## Remaining proof obligations and defensible claims

1. **Continuous alternatives:** retain the whole constrained p,q closure, all type patterns and all mixed actions unless an exact reduction has been proved. A Bernoulli or one-truth-flip reduction from another problem is not a certificate here.
2. **Expected cost:** establish identification at each admissible true state, set-valued tracking when the optimizer is not unique, correct block-count versus cost-fraction conversion, and integrable stopping tails. Almost-sure convergence alone does not justify an expected-cost limit.
3. **Reference randomness:** include misleading calibration records in validity and expectation arguments. A pilot-good event with probability tending to one need not be adequate for a nominal delta error guarantee. Separately track any error budget allocated to pilot failure.
4. **No fixed gap:** assumptions permit p-q arbitrarily small. A pointwise asymptotic theorem at fixed p>q is distinct from a uniform rate theorem over that family. Equal-rate closure points used in infima should not silently become required identifiable true states.
5. **Structural novelty:** common unknown rates couple groups globally. The original smallest-group scalar formula, a pure-good oracle and a direct known-rate substitution all require fresh justification. A rigorous failure boundary would be a substantive result even if no replacement scalar formula exists.

Suggested claim level: “We characterize, within a fixed source-block model, how shared unknown extraction reliability and finite reference information change the optimal information allocation and the validity of the known-rate sharing criterion.” Use “characterize” only for the parts actually proved. Do not claim the first calibration-aware test, the first information-per-cost program, or a new general mixture-martingale method. The present audit establishes neither priority nor empirical validity for real Web sources.
