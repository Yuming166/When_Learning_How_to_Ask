# W1.1 bounded AI validity review

Date: 2026-11-01 (client date). Reviewer: a second Codex agent from the same
agent family. This is an additional AI evidence/representation audit, not human
signoff, cross-model validation, or independent adjudication of world truth.
The review used only the saved W1 and W1.1 artifacts. No new page requests,
model-service calls, training, or Methodology experiments were performed. Only
this review file was written by the reviewer; corrections described below were
made by the parent agent in W1.1.

## Outcome

**PASS for a development-stage semantic/provenance audit, after two verified
representation fixes.** No remaining finding requires changing the fixed W1
case decisions or increasing the approved binary subset. Human review remains
PENDING, approved binary pages remain **0**, verified natural-source errors
remain **0**, and all Y values remain unobserved.

This pass concerns traceability and conservative representation. It does not
certify every semantic interpretation, factual reference, source relationship,
or temporal qualification as ground truth. The two human review packets are
prepared but unsigned.

## Issues found and fixed during this review

1. **Polarity was lost from the consolidated statement index.** The initial
   statement_index JSON/CSV copied the base proposition but omitted the signed
   polarity from the second draft. For example, `11-P043-S1` described the
   payment report as true in its base proposition even though the source draft
   encoded polarity -1. `11-P046-S2` had the same problem for the parties'
   denial. Reading those index entries alone could reverse their meaning.
   The parent added `proposition_polarity` and `polarity_contract` to JSON/CSV.
   I checked all 47 index records against their draft pointers and the CSV:
   original polarity is now preserved. Summary-only records are not blindly
   negated again. This fixes the loss while retaining the original utterance
   proposition and speaker attribution.
2. **The graph omitted four observed representations with no relevant
   statement.** The initial graph created a representation only for pages with
   extracted statements, omitting P007, P027, P036 and P041. Those pages were
   actually inspected and labeled NOT_ADDRESSED. The parent added their
   representation nodes. The graph now has **26 observed representations**:
   24 with body-level semantic labels, one metadata-only representation, and
   one header-only representation. The latter two do not become readable
   article bodies or eligible binary pages.

Both fixes were re-read and checked after the parent rebuilt the outputs. They
change W1.1's completeness, not W1's historical acceptance decisions.

## Semantic boundaries checked

- **Missingness is separate from NOT_ADDRESSED.** The 26 unobserved body labels
  among the 50 real URL records remain null. Error pages, access challenges,
  unavailable archives, login gates and P040's header-only extraction are not
  coded as negative or unaddressed evidence. The 11 NOT_ADDRESSED labels refer
  to inspected generic interfaces, partial evidence, or different scoped
  propositions. Their relevant subclaims remain separately represented.
- **P021/WISN:** ATTRIBUTED_ONLY for the full target is a defensible conservative
  W1.1 interpretation. Its headline adopts the approximate amount and start
  period; the full comparator and details occur in the named interview
  speaker's answer. P021-S1 and P021-S2 preserve this distinction instead of
  silently composing an independently verified publisher assertion. The
  transcript/dataset wording difference is also retained. This is a stricter
  post-W1 representation, not a retrospective change to W1's two provisional
  review candidates. Human adjudication of adoption and scope is still needed.
- **P028/McSweeney's:** the byline and explicit authorship disclaimer support
  ASSERT_REFUTE for the actual-authorship claim. The fictional narrator is not
  treated as a factual assertion by the publisher, a contrary independent
  source, or a naturally erroneous page. First-party authorship evidence
  supports a qualified reference conclusion; it does not supply independent
  human adjudication or establish when the disclaimer was added.
- **SI/Radar:** P042, P046 and P048 appropriately remain MIXED. The reported
  amount and joint denial have separate speakers, adoption states, and material
  lineages. Reporting a denial is not proving the negation of the payment fact.
  The reference factchecker can assert a qualified rejection while the actual
  confidential amount remains unknown. No pre-update text is reconstructed.
- **P014 metadata:** the assertion is retained in its own metadata channel;
  body_semantic_label and overall semantic_label remain null. This lead does
  not become a body-reading candidate.
- **Scope:** the NSW/other-state distinction, singular office versus separate
  GP visits, first versus only, missing Stalin attribution, and infrastructure
  measurement-window mismatch remain explicit. No diagnostic subclaim replaces
  the original selected target.

## Time and provenance boundaries checked

The records distinguish claim applicability, page publication, self-reported
modification time, requested archive timestamp, acquisition time and unknown
historical content. Dates supplied by reference context are marked as such.
Later publication alone is not used as a mismatch rule. SI/Radar HTML timestamps
are retained as metadata, not proof of the time when the denial was added.
All acquired-archive snapshot times and historical semantic labels remain null.
The nonarchive representation is the saved W1 tool result, not a guarantee of
live page content on the audit date.

The 40 nominated document groups perform address/alias bookkeeping. They do
not merge contents across time or constitute 40 independent observations. The
seven material-lineage groups retain differing evidential strengths, including
named study families, unfetched upstream material and directly shared reports.
They are not seven statistically independent roots. Radar and SI participate
in separate amount-report and joint-denial lineages; citation does not collapse
their entire pages into one statement. Login-target mismatches and the
unverified www/non-www identity remain unresolved instead of being merged.

The added same-claim dependency table has **104 pairs**, all marked statistical
independence NOT_ESTABLISHED. The graph's independent-root count remains null.
Known material reuse, common named origin and unknown dependence must continue
to be reported separately; neither the pair table nor a graph component count
identifies a generative independence partition.

## Independently checked counts and integrity

| Check | Result |
| --- | ---: |
| Original claims, train indices, exact claim text/hashes and labels preserved | 12 / 12 |
| W1 files matching the parent receipt | 78 / 78 |
| W1 MANIFEST hash matching the parent receipt | PASS |
| Claim-by-inventory-value records | 54 |
| Real URL records / Metadata case rows | 50 / 4 |
| Real-URL body labels unobserved | 26 |
| NOT_ADDRESSED / ASSERT_REFUTE / ATTRIBUTED_ONLY | 11 / 5 / 2 |
| ASSERT_SUPPORT / MIXED | 3 / 3 |
| Body-level semantic observations | 24 |
| Observed representation nodes after the fix | 26 |
| Statement records with source-bound short-span checks | 47 / 47 |
| Nominated document groups / material-lineage groups | 40 / 7 |
| Same-claim dependency pairs; independence not established | 104 / 104 |
| Original W1 provisional cases / quarantines retained | 2 / 10 |
| W1.1 nonreference direct-assertion candidate before human review | 1 (P028) |
| Signed human reviews / approved binary pages / observed Y | 0 / 0 / 0 |

For the short spans, I additionally checked each span against its specifically
nominated page section and cited line interval (or the named HTML metadata
field), not merely against any occurrence in a multi-page receipt. All 47
passed whitespace-normalized matching; evidence-file hashes also matched.
This verifies quoted-text location, not semantic correctness. The normal build
check's file-wide containment test should not itself be described as full
locator or semantic validation.

All 12 claim objects and all 54 page records retain null Y and false approved
binary flags. The two human forms have null reviewer identity, human status,
reading attestation, judgments, date and signature, with status PENDING and
model_run_authorization=false. No human identity or signature has been supplied
by an AI agent.

The natural-error outcome remains NO_GO within this fixed corpus; it is not a
claim that naturally erroneous Web sources do not exist. The controlled-
corruption document is design-only. Human source review, a separately frozen
reading target/protocol, and a separate execution decision are still required
before any model observations or empirical reliability claims.
