# Focused literature check: the oracle's format and depth structure

Date: 2026-10-31. Scope: [SCOPE.md](SCOPE.md), retaining the preceding unknown-rate/finite-calibration model. Historical directories were read only. This pass rechecked exactly three primary sources selected from the earlier audits; it did not repeat a broad literature search, execute experiments, or certify the project's numerical outputs.

## Assessment

**Multiple actions in a composite-testing allocation and varying batch sizes under setup costs are established ideas. They do not, by themselves, settle whether this model's format-aware oracle needs mixed formats or multiple depths.** None of the three inspected sources states that specific structural result for persistent source reports, unknown ordered extraction rates, finite labelled calibration, and per-root setup costs. Precise priority remains unestablished; this bounded comparison cannot prove absence of an earlier result.

A certified strict separation in this model would be a useful structural counterexample: it would explain exactly why a known-rate oracle reduction does not survive unknown reliability. Its value is the identified failure mechanism and its consequences for the sharing theorem, not the generic observation that optimal allocations may have several support points. Conversely, a pure-good dominance theorem under the full unknown-rate family would be informative even though generic Blackwell arguments already exist.

The [preceding calibration audit](../web_unknown_calibration_20261031/CALIBRATION_NOVELTY_AUDIT.md) already establishes the citation boundaries for information lower bounds, Dirichlet stopping, offline information credits, and cost clocks. Those subjects are not reaudited here.

## Three verified primary-source comparisons

### 1. Composite testing already optimizes over distributions of actions

**Deshmukh, A., Bhashyam, S., & Veeravalli, V. V. (2019). _Sequential Controlled Sensing for Composite Multihypothesis Testing_. arXiv:1910.12697v1.** [Full primary text](https://arxiv.org/html/1910.12697v1).

**Verified result:** Lemma 1 and equations (18)–(19) optimize the worst-alternative KL over the probability simplex of controls. Proposition 1's continuity statement assumes a unique maximizing allocation. The observation laws belong to one-parameter exponential families, and the objective is expected sample count.

**Reading this pass:** §§II–III, including the parameter-set conditions, Lemma 1, Proposition 1 and its explicit uniqueness qualification.

**Implication:** A composite problem need not reduce to choosing the individually best control; a distribution of controls is already the standard design variable. This result does not guarantee a pure action. It also does not prove that any particular collection of controls requires mixing. This paper gives no persistent-source, extraction-format, or setup/depth structural theorem. Importing its attainability statement would additionally require checking its observation-family and geometry assumptions.

### 2. Setup cost and adaptive batch size already have an explicit optimality theory

**Novikov, A. (2023 revision). _Group sequential hypothesis tests with variable group sizes: optimal design and performance evaluation_. arXiv:2210.07203v2, 29 March 2023.** [Full primary text](https://arxiv.org/html/2210.07203v2).

**Verified result:** Two simple hypotheses, a finite menu of batch sizes, and a cost c(m) per batch. Equations (2.5)–(2.7) give optimal dynamic-programming rules; equation (3.5) chooses the next size from the likelihood ratio in the iid specialization. Section 4.2.1 explicitly uses fixed setup plus linear per-observation cost. Randomization among tied choices is discussed after (2.7).

**Reading this pass:** §§2.1–2.3, the iid specialization in §3.1, and the setup-cost example in §4.2.1.

**Implication:** Variable acquisition depth under setup costs is not a new decision structure. General §2 permits non-iid joint laws, so dependence alone is not an adequate distinction. However, the hypotheses are simple; the inspected results do not optimize against a continuum of unknown extraction rates or establish a persistent-root mixed-depth first-order separation. History-dependent finite-error batch sizes should not be conflated with an asymptotic allocation requiring positive mass on several depths.

### 3. Latent items, noisy channels, acquisition costs and calibration have a close contemporary precedent

**Ham, D. W., Zhao, X., Jasin, S., & Yang, F. (2026). _Human–AI-Powered Hypothesis Testing: Cost-Aware Selective AI Scoring and Sequential Human Escalation_. arXiv:2609.28859v1.** [Full primary text](https://arxiv.org/html/2609.28859v1).

**Verified result:** A purchased pool of latent binary-labelled items; at most one noisy AI query and one exact human query per item. Acquisition, AI and human costs are distinct. Lemma 4.7 and Proposition 4.8 characterize a report-dependent verification frontier, with randomization at a marginal report. Section 6 treats unknown AI channels using paired pilot data.

**Reading this pass:** §§3.1–3.3 and 4.2–4.4, especially the query restrictions and frontier; §6's calibration/error boundary was inspected in the preceding audit.

**Implication:** These ingredients are close enough that “latent information plus noisy AI plus cost” is not a sufficient novelty claim. The result is about selective exact-label escalation after a single AI report, not repeated noisy extraction of a persistent erroneous source report. Its unknown-channel pilot result also has the conditional/unconditional qualifications documented previously. No pure-good-versus-mixed extraction or multi-depth oracle theorem for the present model was found in the inspected statements.

## Distinguish the structural questions

The following are this audit's definitions and deductions, not additional claims attributed to those papers. Let all costs be first-order expected online-cost coefficients under the same known-format, unknown-rate oracle and the same calibration experiment.

| Quantity | Allowed actions | What a strict inequality would establish |
| --- | --- | --- |
| C_all | Every completed block, including both formats in one root | C_all < C_good disproves pure-good optimality |
| C_good | Only the known good format, with arbitrary allowed depths | C_good < min_L C_good,L shows that no globally fixed pure-good depth is optimal |
| C_good,L | Only pure-good blocks of fixed depth L | Supplies each restricted comparator, rather than one handpicked depth |

Always C_all <= C_good <= min_L C_good,L. The two strict separations answer different questions. A proof of the second does not show any use for the lower-accuracy format. A proof of the first does not require multiple depths.

A stronger depth comparison allows every format composition at each fixed depth. Write C_L for the oracle optimum using all actions with total depth L. A full-model feasible allocation with cost U < min_L LB_L, where LB_L bounds C_L below, excludes every single-depth allocation even if that allocation mixes formats. It proves that every globally optimal oracle allocation has at least two depths, provided an optimum exists. This conclusion can hold while pure-good optimality remains unresolved; a pure-good witness supplies the upper bound without needing to be globally optimal.

For multiple facts, “one depth suffices” is ambiguous. Restricting every fact to the same L is stronger than permitting a separate fixed L_j for each fact. A counterexample against the first does not automatically refute the second. State the comparator explicitly; a one-fact witness avoids that distinction. Mixing formats within a root, using different pure formats on different roots, and allocating across distinct facts must likewise remain distinguishable.

At a fixed total cost coefficient C and cost fractions w_a, feasibility has the generic form

\[
\alpha H(p,q;u,v)
+C\sum_a w_a\frac{D(P_s^a\Vert P_{s'}^a)}{b_a}\ge1
\quad\text{for every wrong-answer alternative }s'.
\]

An infimum of affine functions of w is concave. Its maximum can occur in the interior of the allocation simplex: different alternatives can favor different controls. That is general max–min design geometry. The model-specific task is to prove which alternatives actually bind for persistent-source laws and whether they force distinct depths or formats. A solver returning several nonzero weights is not such a proof; degeneracy or approximate ties can produce the same output.

## What a defensible counterexample needs

1. A feasible candidate allocation for the full continuous alternative family, with a certified upper bound U on its cost coefficient. Feasibility on a finite alternative grid alone is insufficient.
2. A valid lower bound for every member of the restricted comparison class. One explicit admissible alternative per fixed depth can provide a lower bound; it need not be that depth's exact least-favourable alternative. To exclude all pure-good mixtures, a lower bound must cover their entire allocation set.
3. Strict separation after numerical or analytic error bounds: for depth mixing, U < min_L LB_L; for format necessity, U < LB_good. Positive support weights without this separation establish neither claim.
4. The same r,p,q, parameter domain, calibration ratio, action costs and oracle knowledge on both sides. Known-rate and unknown-rate oracles are different comparators.

The existing rate-dependent garbling formula explains why an old proof cannot simply be reused: its flip probability depends on unknown p,q. That fact is weaker than a performance separation and does not establish a complete-experiment Blackwell comparison after calibration. It should remain a motivation for the structural analysis, not its conclusion.

## Consequences for the sharing theorem and positioning

A mixed-depth counterexample would invalidate a general reduction to one selected oracle depth. It would not, by itself, prove that no scalar smallest-group condition can exist. That stronger claim would require a separate result. The full oracle-optimal allocation set remains the correct object for the generic zero-premium feasibility condition; a further reduction may still be possible under additional assumptions.

An appropriate claim, if certified, is: “Even when the best extraction format is known, finite knowledge of extraction reliability can require combining source-reading depths to minimize first-order acquisition cost in this persistent-source model.” If only format necessity is certified, replace the statement with that result. Neither statement should be advertised as the discovery of multi-support optimal design in general.

This check supports a narrowly stated structural proposition or counterexample, with precise comparisons to the known-rate reduction. It neither dismisses that result as generic nor establishes its priority, empirical Web validity, or conference acceptance prospects.
