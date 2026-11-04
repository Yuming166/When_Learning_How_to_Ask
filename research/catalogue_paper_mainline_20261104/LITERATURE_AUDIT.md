# Bounded primary-literature audit for the catalogue/reliability paper

## Material Passport

- Date: 2026-11-04, Asia/Shanghai.
- Purpose: locate direct overlap and bound the proposed contribution; this is
  a targeted audit, not a systematic review or an exhaustive novelty claim.
- Reviewer: delegated assistant, same inference family and shared project
  context. No human-read attestation, independent expert endorsement, or
  cross-model review is implied.
- Applied workflow: academic-research-suite, deep-research/source verification.
- External queries used public titles and generic topic phrases only. No
  unpublished proofs or manuscript content were uploaded. No model/API/GPU
  calls, experiment reruns, or changes to manuscript/frozen sources occurred.
- Full public CAPE PDF was downloaded for local text inspection after the web
  reader rejected its `application/octet-stream` content type. Primary PDF
  links below are the evidence sources, not an external generated summary.

## Assessment for the author

The defensible contribution is the **structural zero-versus-positive
query-format-ignorance premium**, determined jointly by decision-changing
preference sets and the given sharing partition, relative to an oracle that
knows formats but still does not know response rates. Its stated zero/sublog
calibration scope must match the proved theorem. This audit did not find that
specific characterization in the inspected passages. That is a bounded finding,
not proof that no prior paper contains it.

Do not claim novelty for catalogue-sensitive efficiency, Bayesian elicitation,
noisy preference learning, latent sharing, learning oracle reliability,
KL allocation, fractional certificates, or conversational style adaptation.
The two additional overlaps in §§7–8 are particularly useful for preventing an
overbroad introduction.

## 1. CAPE: closest recent system framing

**Read:** §2; §§3.1–3.2, equations (2)–(11), Algorithm 1; Appendix A setup and
comparison; Appendix B.1; Appendix E.1–E.2 and discussion of sequential
acquisition. [Primary proceedings](https://proceedings.mlr.press/v306/bose26a.html),
[PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/bose26a/bose26a.pdf).

CAPE learns population preference correlations offline, updates a latent-user
belief online, selects informative unqueried criteria, and predicts a complete
profile for a fixed downstream solver. Its evaluated budget is five questions;
criteria are not repeated. The latent variable represents the user, while
observation likelihoods come from the offline model. Appendix A compares
sparse-feedback RL learning and dense-profile learning; it is not a
fixed-confidence reliable-query premium theorem. The inspected formulation has
no alternative formats with an unknown group-shared better channel, nor the
proposed matched type-only oracle.

**Consequence:** use it to establish that structured Bayesian personalization
is already substantive prior work. Distinguish preference correlation from
shared uncertainty about measurement reliability. Do not describe our joint
inference decomposition as new merely because it avoids online retraining.

Metadata verified: `bose2026`, ICML 2026, PMLR 306, 9295–9321; all nine authors
are in the supplied BibTeX addition.

## 2. Di Noia et al.: catalogue geometry is established motivation

**Read:** §§2.3, 3.1–3.2, and §4's assumptions/strategy formulation, plus the
lower/upper-complexity claims. [Author preprint](https://arxiv.org/html/2111.05578v3),
[published record](https://doi.org/10.1016/j.ins.2022.07.169).

The model permits feature/item feedback, slot filling, relaxation and revision.
Its theoretical objective minimizes worst-case dialog turns; §4 explicitly
leaves a probabilistic setting for future work and assumes truthful coherence
with ideal acceptable items. It proves computational hardness and shows
catalogue characteristics influence strategy efficiency. This directly
precludes presenting catalogue-dependent recommendation complexity as our new
observation. The inspected model does not give the proposed noisy-channel
characteristic coefficient or format-ignorance equality boundary.

**Consequence:** state the different question explicitly: computational dialog
strategy complexity versus the statistical cost of an unknown observation
channel for a particular decision map.

Metadata verified: `dinoia2022`, *Information Sciences* 614 (2022), 325–347,
DOI `10.1016/j.ins.2022.07.169`.

## 3. Kostric–Balog–Gadiraju: motivation, not validation of our channel

**Read:** §§3.1–3.3 and the study-design/task description, not just the abstract.
[Primary author manuscript](https://arxiv.org/html/2504.13095v1).

The study contrasts high involvement, high considerateness and user-controlled
switching, with 30 participants performing scholarly recommendation tasks.
Styles differ in pacing, tone, initiative, questioning frequency and forms of
interaction. These are broad bundled interventions, not two semantically
matched binary measurements with identical evidence. The paper motivates
attention to how interaction is conducted; it does not establish our p/q
channel, iid replies, stable group types, or cross-preference reliability
sharing. Treating it as direct empirical evidence for those assumptions would
overstate its result.

Metadata verified: `kostric2025`, UMAP 2025; DOI
`10.1145/3699682.3728353`. The supplied entry omits an unverified page range.

## 4. Garivier–Kaufmann: credit the KL identification scaffold

**Read:** §2.1, Theorem 1 and its change-of-measure argument; §3 tracking;
§5.2 expected-time asymptotics. [Primary PDF](https://proceedings.mlr.press/v49/garivier16a.pdf),
[metadata](https://proceedings.mlr.press/v49/garivier16a.html).

The characteristic time is a max-allocation/min-alternative KL game; the
sampling proportions and Chernoff-style stopping are tied to that lower bound.
This is foundational machinery rather than a new contribution here. The
original setting identifies a highest-mean arm in a one-parameter family.
Our structural theorem concerns an item decision computed from a preference
vector with shared unknown format nuisance variables. Simply replacing the
alternative set by wrong-item states is not the entire claimed novelty.

Metadata: existing `garivier2016` is correct; COLT 2016, PMLR 49, 998–1027.

## 5. Guo–Sanner: recommendation-directed VOI and noise are not new

**Read:** §§2.1–2.3, the TrueSkill-style factor graph/noise treatment, and
query-selection discussion. [Primary PDF](https://proceedings.mlr.press/v9/guo10b/guo10b.pdf).

This work already uses additive multiattribute utilities, Bayesian beliefs,
pairwise comparison responses, approximate posterior updates, and VOI query
selection directed toward available high-utility items. Its noisy performance
model uses a fixed scale (`beta=1` in the described implementation). It does
not supply the proposed unknown-format/sharing-partition premium criterion in
the inspected sections. Cite it for established preference-elicitation and
decision-aware questioning, rather than claiming to introduce those ideas.

Metadata: existing `guo2010` is correct; AISTATS 2010, PMLR 9, 289–296.

## 6. Fractional sensitivity/certificates: explicit established connection

**Read:** Tal's Definitions 1.2–1.3, Theorem 2 and the stated LP-duality
connection; Kulkarni–Tal introduction/related-work LP formulations.
[Tal primary paper](https://web.vu.lt/mif/s.jukna/boolean/Tal2013.pdf),
[Kulkarni–Tal report](https://eccc.weizmann.ac.il/report/2013/168/),
[full revised text](https://eccc.weizmann.ac.il/report/2013/168/comment/1/download/).

Sensitive blocks and the dual fractional certificate cover are established
query-complexity objects. Tal explicitly identifies their local LP duality;
Kulkarni–Tal records `fbs(f,x)=FC(f,x)` and their relation to randomized
certificates. Thus minimizing a fractional hitting cover of decision-changing
sets is not itself new. Applying that geometry to a multi-item decision map
is a connection to credit; the additional unknown-channel constraints and
their exact equality boundary must do the novel work.

Metadata: `kulkarni2013` cites ECCC TR13-168 (2013), Raghav Kulkarni then Avishay
Tal. Tal's distinct ITCS 2013 paper has DOI `10.1145/2422436.2422485`, pages
441–454. Do not conflate those two 2013 papers. The author homepage lists a
2016 CJTCS journal version of the joint work; its publisher endpoint failed
here, so the supplied bibliography uses the verified 2013 report.

## 7. Additional direct theoretical overlap: unknown variances

**Read:** Jourdan–Degenne–Kaufmann §§2.1–2.3, especially Lemmas 3–4.
[Primary PDF](https://proceedings.mlr.press/v201/jourdan23a/jourdan23a.pdf),
[proceedings](https://proceedings.mlr.press/v201/jourdan23a.html).

Unknown nuisance noise already has a quantified asymptotic identification
premium. Their Gaussian model lets alternatives change variances as well as
means. Lemma 4 gives a strictly larger unknown-variance characteristic time
and an explicit ratio upper bound `d/log(1+d)` for its defined gap/noise
quantity. Consequently we must not claim to discover that learning nuisance
reliability can increase the leading coefficient. The distinction sought here
is the **structural zero-versus-positive boundary**, including nondegenerate
zero cases caused by decision/sharing geometry, with an oracle revealing only
format types rather than all noise parameters.

Metadata: `jourdan2023`, ALT 2023, PMLR 201, 776–849. The PMLR generated BibTeX
mistakenly swaps surname/given-name fields for authors two and three; the
addition correctly uses Degenne and Kaufmann from the primary PDF.

## 8. Additional direct mechanism overlap: proactive learning

**Read:** Yang–Carbonell §§1–2, the sequential-test formulations, and §6.
[Primary CMU report](https://www.cs.cmu.edu/~jgc/publication/PublicationPDF/Cost_Complexity_Of_Proactive_Learning_Via_A_Reduction_To_Realizable_Active_Learning.pdf).

Proactive learning already selects among multiple sources with unknown label
reliabilities/costs, repeatedly queries them, and derives PAC cost bounds.
Section 6 discusses improving later source selection using reliability learned
on previous examples. Its proved main samplers rely on costs without knowing
the noise rates. The inspected report does not characterize an exact
decision-map/sharing-partition zero-premium condition. Still, it blocks broad
claims that jointly learning labels and source reliability, or transferring
reliability experience between questions, is newly introduced here.

Metadata: `yang2009`, CMU-ML-09-113, November 2009. Some secondary indexes label
an uploaded copy 2012; use the date printed on the primary report.

## 9. Remaining novelty uncertainty and compact integration

The most important unresolved perimeter is structured pure exploration with
shared nuisance channels, noisy decision-tree/Boolean evaluation, adaptive
source selection/crowdsourcing, and joint utility/rationality identification.
The existing bibliography's `yamagata2024` is relevant to that last issue;
its OpenReview page hit a browser-verification wall during this bounded pass,
so no substantive comparison or absence claim is made for that source. Generic
searches did not settle the entire perimeter. Existing composite-testing and
offline-data references also need precise scope matching if used to support
attainment or calibration claims; this audit did not reread them fully.

In the short manuscript, prioritize direct overlap instead of adding a long
survey. The current draft already credits CAPE, catalogue complexity, noisy
VOI, fractional certificates, and KL games. One additional sentence can cover
the two important omissions:

> Unknown source reliability has been studied in proactive learning, and
> unknown noise parameters can increase fixed-confidence identification costs;
> our question is when recommendation structure removes the premium of
> learning the reliable format.

Use `yang2009,jourdan2023` there. This is a positioning inference from the
model comparisons above, not a statement that all adjacent literature was
exhausted. Preserve the matched oracle definition next to the new theorem.

Recommended claim boundary: an exact characterization **in this shared binary
channel model**, rather than the first theory of conversational recommendation
or the first method to learn how to ask. A new finite-tolerance implementation
can be valuable supporting methodology without a new sample-optimality claim.
Controlled negative method comparisons should remain visible. The present
literature audit neither establishes empirical superiority nor validates the
channel assumptions for Web users.

## Deliverables and access notes

`references-additions.bib` contains the six requested additions with keys
`bose2026,dinoia2022,kostric2025,kulkarni2013,jourdan2023,yang2009`.
Metadata for existing Guo/Garivier entries was checked without editing the
paper's bibliography. Only these two assigned auxiliary files were created.
Failed primary endpoint access is retained above rather than silently replaced
by a claim based on search summaries. No human-read declaration was created.
