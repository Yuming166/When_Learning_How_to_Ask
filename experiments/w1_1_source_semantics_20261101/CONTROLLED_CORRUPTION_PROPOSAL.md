# Controlled source corruption — design only, not executed

**Decision: conditional design is feasible; construction and model execution are
not authorized or performed.** No current W1 candidate has genuine human signoff.
Do not call any future edited document a naturally occurring Web error.

The experimental target would be the cost of rereading one persistent report
versus acquiring a genuinely new, independently constructed report. Source
corruption is explicit manipulation; extraction accuracy remains measured from
actual answers rather than prescribed in prompts.

## Prerequisites and minimal unit

After a human validates a fact and its evidence/version, freeze a scoped binary
proposition and a self-contained evidence unit. W1-06 authorship is a possible
seed, subject to W2; it is not currently an approved gold seed. Preserve the
original source link and attribution in evaluator-side provenance.

Use a fictional, clearly labelled **simulated / Web-derived counterfactual**
wrapper. Operate on one explicit assertion field, not an unreviewed whole page.
Every transformation gets a character/token edit ledger, original and edited
hashes, target proposition, original reference, constructed report V, root ID,
page-copy ID and reason. Labels and the edit ledger stay evaluator-side. All
arms receive the same simulated-status disclosure; no arm gets a hidden cue
that identifies the corrupted report.

For authorship, for example, an eventual unit could assert the validated actual
author, and the corrupted unit could assert another author. These are proposed
manipulated units, not already generated pages. A counterfactual must remain
internally coherent: byline, explanatory note and relevant text cannot silently
contradict the manipulated field. If coherence requires removing decisive
context or changing what the question asks, reject the unit.

## Three acquisition conditions

| Condition | What changes | What remains persistent |
|---|---|---|
| Reread one source k times | Fresh extraction calls only | Same report, evidence, root, and page |
| Read k copies | Wrapper or URL/page-copy identifier | Same underlying report and root |
| Acquire a new root | Independent source-error draw by construction | Same target fact and evidence access contract |

The root-generation randomness is defined and logged before model answers;
copies reuse the same draw. Independent construction of error draws is a
simulation property, not a claim that real websites are independent. Correct
and corrupted source reports should be balanced across profiles/conditions
according to a frozen mechanism, without selecting only roots on which a model
makes mistakes. The true θ, source V and extracted Y are evaluated separately.

The model question must concern the source's attributable assertion, with the
same answer coding and evidence across formats. Validate same-root copies for
semantic equivalence and preserve invalid outputs. Repeated-call agreement is
not truth accuracy. Label a same-root/new-root cost as an assumed experimental
cost, not a measured Web acquisition price.

Any later pilot needs a separate frozen scope and authorization. This proposal
chooses no optimized policy, no winning corruption rate, no model-call budget,
and no claim of natural source reliability or human behaviour. W1.1 generates
zero edited pages and zero Y observations.
