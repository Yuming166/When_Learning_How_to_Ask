# W1.1 representation contract (development, not a relabelled W1)

The W1 corpus and decisions are read-only. W1.1 records richer information about
the same observations. A schema repair is not a new truth adjudication or an
increase in the original two W2 candidates.

## Claim and time

`C_j = (entity, relation, value, event_time, geography, units, qualifiers)`.
Preserve the exact original claim, dataset reference label and source index.
`normalization_status` distinguishes an explicit proposition from missing
scope or a missing predicate. Clarifications inferred from evidence must be
labelled `contextual_interpretation`, not silently inserted into the target.
Alternative subclaims are diagnostic only; they are not replacement test items.

Separate event time / statement applicability interval, first publication,
update notice, requested archive timestamp, actually acquired archive snapshot,
local acquisition time and source-relative evaluation time. A later publication
can accurately discuss an earlier event. An archive timestamp encoded in a URL
does not establish an acquired snapshot or the timing of a correction. Browser
crawl ages remain verbatim metadata, not invented exact dates.

## Page semantics and missingness

| Semantic label | Condition, relative to the same scoped proposition |
|---|---|
| ASSERT_SUPPORT | Page narrator/editorial framing directly adopts the proposition |
| ASSERT_REFUTE | Page narrator/editorial framing directly rejects the proposition |
| ATTRIBUTED_ONLY | Relevant stance is attributed to another speaker without adoption |
| MIXED | Conflicting claims, attributions or unresolved qualifications coexist |
| NOT_ADDRESSED | Inspected content provides no determinate statement on the full target; retain partial/other claims separately |

Unavailable/uninspected pages have `semantic_label=null` and a separate access
state. Missingness is never NOT_ADDRESSED, false, or negative evidence. A title-only
shell cannot stand in for a read article body. Metadata-only assertions have their
own channel; the body remains unobserved. Reference factcheck articles retain
evaluator-only roles even when their stance is clear.

Each statement records its proposition, polarity, attributed speaker, narrative
adoption, exact short span and locator. Store each quote once; summaries refer to
statement IDs and locators. A page summary can be MIXED while its individual
statements have clear, different speakers. Reporting a denial is not verifying
the negation of the denied world fact. A satire disclaimer can directly reject
authorship without making the fictional narrative an erroneous factual report.

For social posts, distinguish the account author who asserts a claim from the
hosting platform; platform non-endorsement does not erase the author's assertion.
P014 is excluded from body-ready data because only metadata was acquired, not
because Facebook must endorse its user's claim. Where a record has an explicit
proposition and signed polarity, preserve both; a negative polarity must never
be dropped when displaying the proposition. A prose summary that already says
what was denied must not be negated a second time.

Comparability has separate entity / relation / value / event time / geography /
unit / qualifier results. FULL, PARTIAL, MISMATCH and UNRESOLVED are distinct.
Exact page-reference comparison requires FULL and a directly asserted stance,
plus genuine independent adjudication. All human reviews here are PENDING, so
the approved binary subset remains empty even for the two provisional candidates.

## Provenance

Keep URL resources, document identities, observed representations, statement
nodes and named upstream evidence nodes distinct. A representation is version-
specific. Exact archive wrapping identifies a nominated original document, not
equal content across times. Explicit citation, quotation, reported copying,
observed alias, and common named upstream are different edge types.

Use two graph views:

1. Nominated document-identity groups merge exact current/archive address pairs
   and explicitly evidenced aliases. They are bookkeeping, not evidence counts.
2. Claim-relative statement lineage groups join only observed shared material
   (e.g. the same reported number or the same joint denial). Their connectedness
   is not an assertion that different lineages are statistically independent.

A citation never merges every statement on two pages. If a page combines a
positive report with a denial, preserve both lineage memberships. A named study
series may establish shared upstream provenance without identifying the exact
weekly data release. Secondhand or inaccessible copying edges remain unverified.
All remaining pairwise independence is UNKNOWN_DEPENDENCE. Do not count graph
components, domains, URLs or unmatched roots as independent measurements.

## Scientific gates

- W1 remains 2 provisional cases, 10 quarantined; negative evidence is retained.
- W1.1 semantic usefulness is reported separately from binary-subset eligibility.
- AI annotations and a second AI review are not human signoffs or cross-model evidence.
- Natural source error requires an attributable erroneous assertion, matched
  proposition/version, qualified independent reference and review. A corrected
  article alone need not reveal its prior version or establish objective error.
- Controlled corruption is a separate proposed simulated track; no edited pages
  or model observations are generated in this task.
- All Y values are unobserved. No model, agent, training or Method experiment runs.
