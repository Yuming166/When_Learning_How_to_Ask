# Myntra Structured Catalogue v0.1

## Material Passport

Constructed 2026-11-04 for reliable preference elicitation research. Derived,
local catalogue of seller-reported attributes from Gssmc/myntra_dataset. No
human preference records, LLM labels, inferred garment facts, images, training
or recommendation outcomes were added. Automated source-fidelity verification
does not constitute human semantic validation.

## Contents and unit of analysis

- Original CSV: 15,000 logical data records, including 14,000 entirely empty
  records and 1,000 nonempty SKU/size records. No invalid product IDs.
- All-products registry: 959 source product IDs. Forty-one IDs have two variant
  records. Different IDs are retained even when their texts are identical.
- Strict catalogue: 471 adult single-garment products with complete singleton
  source labels for neckline, sleeve length, fabric, wash care and pattern, one
  reported price and no disagreements detected by the stated limited guards.
- Six homogeneous gender/category pools: Women/Kurtas 214; Men/Kurtas 154;
  Women/Dresses 67; Women/Tops 21; Women/Tunics 8; Women/Kurtis 7.
- 18,991 source specification claims, covering 126 distinct source keys. All
  claims have exact source-record, column, fragment and character-span binding.

Kurtas account for 368/471 strict products. This is a narrow, Indian-market,
historical catalogue, not a representative sample of fashion or shoppers.

## Acquisition and provenance

Source repository: https://huggingface.co/datasets/Gssmc/myntra_dataset

Pinned revision: `e3037c0e7aba89376ac8ea24f69b416d9d0335cb`.

File: `marketing_sample_for_myntra_com-ecommerce__20190601_20190831__15k_data.csv`.

Bytes: 1,938,089. SHA256:
`d8091d2ec14ed95dc887994ce216679069391488fe32905873cbe13bff45ab58`.

Reused verified bytes from the preceding read-only check, without new network
requests. Source crawl timestamps are in 2019; prices, sizes, inventory and
availability are historical source records, not current shopping offers.
Currency is absent from this source and stays null. No images or product URLs
are supplied in this particular CSV, despite other Myntra versions having them.

The uploader's MIT metadata is recorded, not treated as independent proof of
rights to redistribute marketplace content. Raw and derived records remain
local/ignored; Git contains the constructor, documents, schemas and aggregates.

## Cleaning and selection

All raw cells are retained in `variants.jsonl`. Explicit `key : value` fragments
are recovered from the inventory/specifications/final unnamed columns. In 502
SKU records, specifications occupy the inventory column; recovered attributes
are retained while the unknown stock count becomes null. This is a documented
field-recovery operation, not invented inventory or a rewrite of source bytes.

HTML entities, Unicode, case, whitespace and dash typography are normalized.
No garment meaning is inferred from absent fields. Multiple claims are kept;
conflicting values do not acquire an arbitrary winning label. Top/Bottom/
Dupatta Fabric remain component-scoped fields. Pattern and Print or Pattern
Type remain separate axes. Cotton, Pure Cotton and Cotton Blend stay distinct.

Strict selection, applied before any model experiment:

| Sequential gate | Remaining products |
|---|---:|
| All source product IDs, valid identity and taxonomy | 959 |
| Adult single-garment category listed in config.json | 525 |
| No explicit component count other than 1 | 504 |
| Five core attributes present and singleton | 495 |
| One valid positive historical source price | 495 |
| No detected core source-label disagreement | 471 |
| No unparsed specification fragment | 471 |

The last exclusion step isolates 24 products with potential source-field
disagreement. It does not establish that either seller statement is false or
that two different care recommendations are physically incompatible. Across
all eligible-category records, guards report 12 care, 8 material, 4 neckline and
3 sleeve disagreements; flags can overlap and include records excluded earlier.

Seventy-one strict products do not report Number of Components; their category
names indicate single-garment categories, but physical component count remains
unverified. Missing component counts are explicitly flagged.

## Splits and reuse

Default hash buckets are 70/15/15, not an exact-size stratified allocation.
Explicit product variants always stay together. Different product IDs linked
by exact normalized brand+title or brand+description also stay together. There
are 937 leakage groups across the 959 IDs; 18 groups contain multiple IDs, and
the largest contains four. These are conservative split links, not a claim of
physical garment identity.

| Split | All product IDs | Strict products |
|---|---:|---:|
| development | 670 | 338 |
| validation_reserved | 157 | 78 |
| test_reserved | 132 | 55 |

All source metadata was available during catalogue construction. Reserved sets
contain no model outcomes and must not be used to tune simulator prompts or
query strategies. Their existence is not an independently completed
confirmatory evaluation. Small pools may have no members in a reserved split.
Image duplicates, semantic near-duplicates and cross-dataset training overlap
have not been assessed.

## Attribute semantics

`status=reported` means a single normalized seller label with source evidence;
`unknown` means no source claim; `ambiguous` means multiple distinct labels.
Unknown and ambiguous values are null in the flat CSV. Interpret them using the
associated status column. Consult JSONL for all values and provenance.

Examples of valid and invalid interpretations:

- `Wash Care=Hand Wash` supports "the seller recommends hand washing". It does
  not prove machine washing or dry cleaning is forbidden.
- `Fabric=Cotton` supports that category label. It does not establish 100%
  cotton, exact composition, absence of polyester or personal comfort.
- `Neck=Mandarin Collar` identifies a reported category, not collar height,
  visual salience, fit on a person or subjective attractiveness.
- Recorded sizes are source variant labels, not full measurements or current
  stock. `size_fit` often describes the model wearing a size, not garment size.
- A missing closure label does not imply the garment has no closure.

For a deterministic downstream task, explicit-label constraints such as "only
consider items whose seller explicitly lists Machine Wash" can be evaluated.
A physical constraint such as "must not contain any polyester" remains unknown
without sufficient composition evidence. Do not silently substitute one for
the other to obtain complete binary labels.

## Intended and unsupported uses

Suitable now: catalogue adapters, source-label reading checks, interpretable
candidate pools, and future **constructed** preference simulations with fixed
personas and a no-purchase option. No-purchase is a legitimate user decision;
it is distinct from a recommender lacking enough evidence to certify an answer.

Not established: human shopping realism, recovered real customer preferences,
purchase ground truth, natural group-shared query reliability, conditional iid
errors, calibrated confidence, method superiority or a complete benchmark.
Factual cards deliberately omit promotional prose and do not contain utilities,
hard-constraint labels, acceptable-item sets or purchase decisions. Those would
need a separate, frozen simulator protocol and evaluation.

## Reproducibility

Python standard library only. See REPRODUCE.md. Source hash, configuration and
protocol are fixed. All 24 generated files reproduce byte-for-byte with network
socket creation disabled. See results/VERIFICATION.json and results/REPLAY.json.
Twenty-nine semantic failure-mode tests pass. Verification checks source spans,
IDs, unknown handling, splits, CSV parity and hashes; it is not visual inspection
or an independent judgement of garment truth.
