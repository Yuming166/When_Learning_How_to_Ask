# Web-theory handoff: representation precedes source-report inference

This is a modelling handoff based on W1.1, not a theorem or natural-reliability
measurement. W1.1 changes neither the original theory nor its frozen proofs.

For a scoped proposition C_j, distinguish the unobserved world truth θ_j from
the dataset reference label, written tilde-θ_j when its independent support is
incomplete. Root reports V_rj, webpage content D_ij, and extraction Y_ijm are
different objects. A webpage often has multiple parents:

\[
\theta_j\;\longrightarrow\;\{V_{rj}:r\in\mathrm{Pa}(i,j)\}
\;\longrightarrow\;D_{ij}^{(v)}\;\longrightarrow\;Y_{ijm}.
\]

Here v identifies the inspected representation/version. C_j, attribution,
editorial framing, event time, version, and provenance observations must be
conditioned on or explicitly included. D is a structured collection of
statements, not a single binary number. A denial can be a report about a prior
report; it does not automatically equal −θ. Satire is a different discourse
mode, not a Bernoulli truth error.

Three choices are necessary before a new information-complexity result:

1. **Target and observation:** decide whether Y extracts a speaker's report,
   publisher commitment, a dispute structure, or world truth. These are different
   statistical experiments. The input should retain the same attribution and
   disclaimer context across reading formats.
2. **Origin and acquisition:** define a root at the claim/statement level,
   specify how root errors are generated, and state what evidence can establish
   shared lineage. A connected citation graph is not a generative independence
   partition. Known shared statements can be deduplicated; unmatched components
   remain dependence-unknown. Visiting a new URL does not necessarily acquire a
   new root, and real root acquisition cost is unmeasured here.
3. **Identifiability:** specify which of θ, V, D and provenance are observed or
   calibrated, how missing/mixed cases are sampled, and whether page metadata or
   selection supplies additional information. Do not assume a θ-independent
   channel from V to the transcript without justifying that restriction.

The existing source-saturation argument in
`research/web_native_theory_20261031/WEB_THEORY_RESULTS.md` assumes an independent
root model and a θ-independent observation kernel conditional on the root
reports. It can guide a restricted model, but W1.1 does not validate those
assumptions. The cost/depth results in `web_cost_sharing_20261031` additionally
fix the acquisition/block policy and independence conditions. Rich D, unknown
lineage, page revisions and selective access do not inherit their coefficients,
stopping guarantees, or asymptotic optimality automatically.

Useful empirical motivation from the fixed corpus is narrower: one report can
be re-expressed by several pages; one page can contain competing lineages; and
missing scope can make apparent conflicts concern different propositions.
The only binary subset that could eventually support the old model must pass
attribution, comparability and independent review gates. Its approved size is
currently zero. No extraction or format-transfer observation exists.
