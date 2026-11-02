# Claim-to-evidence map

Status: author-review draft, 2026-11-03. These are local source checks, not independent peer review or an exhaustive novelty search.

| Manuscript claim | Evidence | Scope |
|---|---|---|
| Question design matters in conversational recommendation | Kostric et al. (RecSys 2021), official publisher/author-hosted record in the bibliography | Motivation; does not establish our symmetric shared channel |
| Query selection is connected to recommendation quality | Guo and Sanner (AISTATS 2010) | Existing work explicitly acknowledged; no claim of first active preference elicitation |
| Reliability/utility learning is not a new general idea | Chen et al. (WSDM 2013); Yamagata et al. (ICML 2024 workshop) | Related but different models; workshop status retained |
| Optimal slate equals the preference vector | Proposition 1, direct proof in the manuscript | Positive additive weights, fixed independent slots, exactly two candidates per slot |
| Leading online cost is the joint KL program | Original `Theory_Note.md`, §§2–4; expected-time proof and Phase 2b repair | Fixed dimension, fixed nonzero gaps, finite calibration ratio; ideal policy with actual approximation errors vanishing |
| Information tracking is established machinery | Garivier and Kaufmann; Deshmukh et al.; Degenne et al. | The generic lower bound/tracking template is not claimed as new |
| Offline and online information must both enter the comparison | Model and lower-bound proof; Agrawal et al. as related offline-data identification | Our oracle knows current format types only; both sides have unknown reliability levels and identical calibration |
| Oracle allocation is unique and uses only the better form | `Theory_Note.md`, §§5–6, and Phase 2b proof addendum | Uniqueness is required for the zero-premium iff statement, not assumed for arbitrary tracking optimizers |
| Smallest-group condition is necessary and sufficient | `Theory_Note.md`, §§6–7; manuscript Theorem 4 (numbering depends on layout) | Zero versus positive leading premium, not that the positive gap depends only on the smallest group |
| With alpha=0 the premium vanishes iff G=1 | Entropy expression for I_k and strict increase; explicit k=1,2 handling | Zero logarithmic-scale calibration, not necessarily zero raw historical observations |
| Finite-information type questions do not change the equality boundary | Oracle uniqueness plus positive unit cost; original optional-type model | Known accuracy strictly below one; unknown accuracy or bulk disclosure is not covered |
| Perfect type reports remove the leading premium | At most G exact reports followed by oracle elicitation | Fixed G and unit-cost perfect reports; not a claim about real self-reports |
| Figure illustrates the boundary | `reproduce.py`, `boundary_values.csv`, `numerical_checks.json` | Formula evaluations, not model calls, finite-budget method rankings, or a general monotonicity theorem |
| Exploratory Qwen answers are interface-sensitive | `interface_diagnostic_summary.json`, hashes of two existing local analysis artifacts | 2 base worlds; 128 pilot generations; no human/generalization claim; raw records not exported |
| Natural reliability structure is not validated | Negative simulator audit retained; no positive claim in abstract or conclusion | No validation of human behavior, conditional independence, stable sharing, or real recommendation improvements |

## Source locations

- [Original theory](../../Theory_Note.md)
- [Expected-time details](../../research/original_expected_time_proof_20261031/EXPECTED_TIME_PROOF.md)
- [Proof addendum](../../experiments/phase2b_alignment_20261031/PROOF_ADDENDUM.md)
- [Proof-to-code audit](../../experiments/phase2c_strong_baseline_20261031/PROOF_AUDIT.md)
- [Method development decision](../../experiments/phase2e_type_evidence_20261031/FINAL_RESEARCH_DECISION.md)

## Bibliographic checks

All eight cited primary records were opened during drafting. Verified fields were retained; unchecked page ranges/DOIs were omitted. Deshmukh et al. and Agrawal et al. are cited as the verified arXiv versions, without inventing a later venue. Yamagata et al. is labelled as a workshop paper, not a main-track ICML publication. Official source URLs are recorded in `references.bib`.

No claim is made that previous work assumes universally known noise, that this is the first joint utility/reliability model, or that the general KL lower-bound construction is new. The intended structural novelty is the explicit smallest-sharing-group boundary in this particular unknown-channel, finite-calibration model. Priority and suitability for WWW remain author-review tasks.
