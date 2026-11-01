# W1 bounded validity review

Date: 2026-11-01 (client date). Reviewer: a second Codex agent in the same
agent family. This is an independent pass over the saved artifacts, **not human
signoff, cross-model validation, or independent adjudication of world truth**.
No network requests, model-service inference calls, training, or Methodology
experiments were performed for this review. Only this file was written.

## Decision

The frozen selection and complete access ledger are reproducible offline. The
audit can be reported as completed with **2/12 provisional cases for W2 review
and 10/12 quarantined**, after downgrading W1-11/P046 as below. These two cases
provide **2 nonreference page candidates**; neither establishes a natural wrong
nonreference page. Human signoffs remain **0**, observed Y values remain **0**,
and historical binary page stances remain **0**. This is an adaptation-feasibility
result, not evidence that source reliability or shared query reliability has
been established.

The reviewer inspected PROTOCOL.json, its freeze receipt, ACCESS_CLARIFICATION.md,
the selection/input receipts, audit.py, all three review files, relevant retained
browser extracts and text snapshots. Selection and snapshot checks below were
reimplemented in a read-only Python calculation rather than accepting the
implementation's own assertions.

## Material correction: W1-11 / Sports Illustrated

**Recommendation: set P046 V_current=null and page_candidate=false; quarantine
W1-11.** At review time, reviews_09_12.json originally assigned V_current=0 and
accepted this case. The parent acknowledged this correction and is responsible
for updating the consolidated artifacts.

Evidence: browser_09_12/sources1.json, SI lines 81–88; texts/P046.txt lines
114–120. The article attributes the positive numeric report to Radar, reports
the parties' denial, and says the revision reflects that denial. Reporting that
parties dispute a number does not itself establish either a publisher-endorsed
rejection of the number or its objective falsity. The payment remains
confidential. Coding this as a clean binary rejection would apply a looser
attribution rule than used for the debate transcript in W1-08.

Use a stance category such as `ATTRIBUTED_DENIAL_WITH_COMPETING_REPORT` or
`UNRESOLVED_ATTRIBUTED_STANCES`. Preserve the denial, original report, revision
notice and common upstream relationship as useful provenance evidence. Do not
infer the pre-revision stance, correction time, or archived content. The
fact-checker's reference label remains a qualified reference, not an observed
court record.

## Candidate boundary: W1-05 / WISN

Keeping P021 as a **provisional** full-claim candidate is defensible under the
frozen rule. Its editorial headline adopts the Wisconsin tourism-loss amount
and period; the interview supplies the year-over-year comparison and start
point. It is consequently stronger than a bare transcript whose publisher
merely attributes a speaker's assertion.

Evidence: browser_05_08/batch_01.json, WISN lines 57–70. This distinction should
be explained in the report, not reduced to a generic rule that every quotation
counts as publisher belief. Preserve the headline, speaker attribution,
comparison basis and relevant date together in any eventual reading stimulus.
The precise comparator occurs in attributed speech, so this remains an explicit
W2 semantic-adjudication item, not a resolved gold annotation.

The reference gives a qualified fact-check conclusion based on a named study
family. The primary study was not independently recalculated, and the
nonreference and fact-check pages share the same evidential upstream. Neither
the headline nor the two domains creates independent truth measurements.
The separately nominated WPR article concerns a different measurement window;
its null full-claim stance is appropriate.

## Candidate boundary: W1-06 / McSweeney's

P028 has a determinate **current-representation V=0** for the attribution claim:
the publication names the contemporary author and expressly identifies the
work as parody rather than an actual Fitzgerald letter. This direct statement
about the page's own authorship is stronger than inferring falsity merely from
a satire-domain reputation. Keep the disclaimer and byline with the fictional
letter; reading the letter alone would change the evidence.

Evidence: browser_05_08/batch_02.json, McSweeney's lines 16–35. The first-party
authorship note can corroborate the **qualified reference conclusion**, but
must not be called independently adjudicated objective truth. The factchecker
links the same primary publication, so the two are not independent evidential
roots. The inaccessible Facebook page cannot supply a verified wrong-source
observation or a directly verified copying edge. The note's addition date is
unknown; the visible article date does not date every later revision.

Thus W1-06 is a useful present-representation attribution-reading candidate,
not evidence of a naturally erroneous McSweeney's source, a historical source
error, or model reading reliability.

## Appropriate exclusions and residual limitations

- **W1-04/P014:** the saved Facebook metadata contains an assertion, but the
  visible post body and historical representation are unavailable. Keep its
  metadata stance as a separately labeled review lead, not a body-ready page or
  strict accepted case. Its reference's account of derivation from Mumbai Mirror
  is secondhand; do not promote that account into a directly verified edge.
- **W1-07:** an official report of different patients attending GPs does not
  resolve the frozen singular-office/plural-visitors claim. The ABC passage
  about Melbourne cannot be silently rebound to NSW. Quarantine is justified.
- **W1-08:** speaker-attributed debate text is not publisher endorsement; the
  homepage cannot inherit the specific factcheck article's stance. Retain the
  poll year, country aggregation and confidence metric qualification.
- **W1-10:** the target quote lacks the attribution whose falsity the dataset
  justification evaluates. Do not insert Stalin into the frozen claim or use
  an empty search interface to prove absence.
- **W1-12:** the inspected Treasury material supports definitions or a different
  time window, not the selected full ten-year monetary claim. No silent
  subclaim substitution is warranted.
- **Representation timing:** browser records include crawl ages such as “last
  year” and “8 months ago.” `V_current` should be glossed as the nonarchive-URL
  representation returned in this audit, not a guarantee of the live content
  on 2026-11-01. Preserve crawl metadata. All historical V values remain null.
- **No independent-root shortcut:** archive/current pairs, same-article URL
  aliases, repeated QA URLs and explicit upstream attributions are dependencies
  or duplicates. Unknown relationships remain unknown.

## Independently reproduced denominators and integrity checks

| Quantity | Result |
| --- | ---: |
| Training records | 3,068 |
| Supported label records | 849 |
| Nonempty Supported claims eligible under the protocol | 848 |
| Refuted label records / eligible nonempty claims | 1,742 / 1,742 |
| Total eligible binary-label claims | 2,590 |
| Selected claims | 12: 6 Supported, 6 Refuted |
| Unique inventory field values | 51 |
| Unique actual HTTP(S) URLs | 50 |
| Unique non-URL sentinel values | 1 (`Metadata`) |
| All URL-field occurrences | 82 |
| Actual HTTP(S) field occurrences | 73 |
| Sentinel occurrences / affected cases | 9 / 4 |
| Claim-by-inventory-value rows | 54 |
| Claim-by-real-page rows | 50 |
| Raw-access ledger records | 51, including the unrequested sentinel |
| Saved raw response bodies / extracted texts | 13 / 13 |
| Raw HTTP statuses | 200: 9; 403: 3; 404: 1; no status: 38 |
| Strict provisional W2 cases after SI downgrade | 2 / 12 |
| Quarantined cases after SI downgrade | 10 / 12 |
| Human signoffs / model observations Y | 0 / 0 |

The 38 no-status records include the sentinel, which was never a network
request. Saved bodies include error/challenge/navigation content: neither a
response body nor HTTP 200 is a semantic-evidence pass. The 50 real URLs are not
50 independent sources or 50 available article bodies.

The SHA-ranked selection, selected-record contents and order match independent
recomputation exactly. The protocol hash, selection-file hash, pinned README and
train-file hashes, access-ledger coverage, and all saved raw/text hashes pass.
The freeze receipt records the intended ordering but is a local receipt, not an
externally timestamped preregistration. ACCESS_CLARIFICATION.md correctly labels
the archive-unwrapping rule as a post-selection access clarification; it should
remain visible in the report's methods and limitations.

The source-error observation denominator is too restricted to estimate a natural
Web error rate. “No accepted wrong source” means no such case was established
under this audit, not that the Web sources are error-free. No Y-based confusion
matrix, extraction accuracy, repeat-response dependence, group transfer, or
agent-performance conclusion is supported at W1.
