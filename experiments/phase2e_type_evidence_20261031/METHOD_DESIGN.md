# Type-Evidence-Fused Adaptive Information Elicitation

## Material Passport

Phase 2e, 2026-10-31. Development implementation in the isolated
`phase2e_type_evidence_fusion` branch/worktree. Historical model and proof
assumptions are those of Theory_Note.md and Phase 2b PROOF_ADDENDUM.md;
SOURCE_SNAPSHOT.json binds the Phase 2a–2d sources and audits used here.

The candidate repairs the split between the allocation estimator and the
stopping likelihood: task responses, noisy type reports, labelled offline
reference observations and the known partition now inform a single reliability
posterior. The stopping decision still profiles the complete continuous model.
No posterior probability is used as a stopping certificate.

For target j in group g, let theta_j,z_g be bits. Format m has correctness
r_gm=p if m=z_g and q otherwise, with .5<=q<p<=1-eta. A task answer matches
theta_j with probability r_gm. A type report matches z_g with known s_g in
(.5,1). The two reference streams have probabilities p and q. All observations
are conditionally independent fresh samples, and their availability/cost is
part of the public Exact contract. Natural dialogue does not inherit this model.

The model likelihood is

\[
L(\theta,z,p,q)=p^{H_s}(1-p)^{H_n-H_s}
 q^{L_s}(1-q)^{L_n-L_s}
 \prod_g s_g^{C_g(z_g)}(1-s_g)^{K_g-C_g(z_g)}.
\]

Here H/L counts pool task matches to the candidate theta under the candidate
z, together with the corresponding labelled reference stream. C counts type
reports matching the candidate z. No binomial coefficient is needed for an
ordered observation transcript. Predictable policy probabilities cancel when
conditioning on the realized transcript; sampling observations adaptively does
not justify treating their empirical correctness as known.

We use uniform independent priors on theta and z, and constant density on the
ordered rate triangle. This is an explicit modeling choice, not an estimate of
the world-generating prior over p,q. Stage 1 implements rational exact posterior
integration on small instances. Stage 2 uses numerical quadrature and exhaustively
marginalizes the discrete states. A separately labeled empirical-Bayes plug-in
holds rates fixed at a joint profile MLE; it is not exact posterior inference.

Fused-Original supplies posterior mean rates and marginal-MAP group types to
the original information-allocation solver. Fused-Info instead uses the expected
information a paid next response carries about the joint answer theta, so a type
query is valued through its answer-relevant dependence. Both retain the original
forced exploration, update cadence and cumulative tracking. Both use the same
all-observation conservative stopping gate. These are numerical finite-horizon
candidates, without a new asymptotic optimality claim.

The pre-outcome DEVELOPMENT_PROTOCOL.md fixes nine arms, 32 fresh Exact worlds,
R=16/256, alpha=0/3 and [1,3]/[4] partitions, with no efficacy selection or tuning.
Evidence fusion is also measured on a common observed tape independently of
policy changes. Type-disabled arms separate the availability of purchased type
reports from the task-allocation comparison; interactions remain explicit.

Tracking information-optimal proportions and controlled sensing are established
ideas: [Garivier and Kaufmann, COLT 2016](https://proceedings.mlr.press/v49/garivier16a.html)
and [Deshmukh et al., composite controlled sensing](https://arxiv.org/abs/1910.12697).
These sources do not prove optimality of this new posterior/greedy allocation.
No broad novelty or WWW acceptance claim is made.

The entropy/information objective is also related to established Bayesian
active learning, e.g. [Houlsby et al.](https://arxiv.org/abs/1112.5745).
The finite model-specific fusion and diagnostic package should be evaluated
on its actual evidence; renaming an information-gain criterion is not a new
general theory contribution.
