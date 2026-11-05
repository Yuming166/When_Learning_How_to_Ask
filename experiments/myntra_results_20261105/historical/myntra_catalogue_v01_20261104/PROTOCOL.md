# Myntra catalogue v0.1 construction protocol

## Material Passport

2026-11-04. User authorized a clean, regular catalogue from the approximately
1,000 nonempty Myntra records. This is retrospective source-data construction,
not a preregistered effectiveness experiment. Initial field counts and examples
were inspected before this protocol. No model outcomes are available or used.
Zero inference, training, image acquisition, new user profiles or human review.

Base: isolated worktree from fcb17cb. Preserve every pre-existing tracked file.
Reuse the already downloaded source, pinned by repository revision and SHA256.
No additional acquisition is needed. Upstream source rows and derived catalogue
records remain local and ignored; only code, configuration and aggregates are
committed. The uploader marks its repository MIT; original marketplace content
rights and provenance are not independently established by that metadata.

## Construction rules

1. Require the exact 24-column source header and source hash. Account for every
   logical CSV record: empty, parsed, or invalid. Do not replace the source file.
2. Recover key/value specification claims from the inventory, specifications and
   final unnamed column only when an explicit `key : value` is present. Keep
   the original column, record number, exact fragment and character span. Missing
   inventory stays missing; a recovered specification is not a stock count.
3. One variant per source record; merge variants by explicit product_id only.
   Preserve sizes, timestamps, prices and availability per variant. Do not
   invent dates, currency, measurements, images, compositions or product links.
4. Preserve all 959 expected product identities in an all-products registry,
   including irrelevant categories and problematic records. Retain every
   specification key, including component-scoped Top/Bottom/Dupatta Fabric.
   Do not flatten these fields into whole-garment Fabric.
5. Normalize HTML entities, Unicode, case, whitespace and dash typography only.
   Preserve physical distinctions: Cotton != Pure Cotton != Cotton Blend;
   Printed != Floral; garment length != sleeve length. Absent means unknown.
   Multiple values for the same field remain ambiguous, not an arbitrary winner.
6. Strict catalogue: use the ordered gates in config.json. Adult Men/Women,
   Clothing, one of the listed single-garment categories; no explicit number of
   components other than 1; complete singleton Neck/Sleeve Length/Fabric/Wash
   Care/Pattern; one valid positive source price; no detected core disagreement
   or unparsed specification fragment. Unreported component count is flagged.
   Keep all exclusions with overlapping reasons and the sequential funnel.
7. Cross-check only explicit descriptions and seller care/material fields.
   Limited deterministic guards: singleton conflicting sleeve/neck phrases,
   reported/denied care methods, disjoint recognized material families, and
   within-product conflicting core labels. These guards cannot certify all
   semantic agreement. Pattern and Print or Pattern Type remain separate axes;
   do not treat their different labels as automatic contradictions.
8. Form catalogue pools by source gender and exact source category. Do not mix
   shoes, homewares, sets, children's clothing and adult garments in one pool.
9. Reserve 70/15/15 hash buckets at leakage-group level. Link explicit product
   IDs and exact normalized brand+title or brand+description matches. These are
   conservative split links, not claims that different IDs are the same product.
   No variant or exact-text group crosses splits. Image-level and semantic near
   duplicates remain unchecked. No recommendation evaluation is run.

## Output semantics and limits

Produce all-product JSONL/CSV, variants, source claims, quality exclusions,
strict JSONL/CSV, factual cards, per-category pools, schema, split manifest,
coverage/distribution/funnel summaries and reproducibility hashes. Preserve
marketing text in raw/variant records but do not add it to factual cards.

The catalogue's facts are seller-reported claims, not independently verified
garment properties. A recommendation simulator must later separate hard
constraints, subjective appeal and purchase/no-purchase; this construction
creates none of those labels. It also provides no natural p/q, reliability
sharing, model fidelity, algorithm ranking or human-behaviour evidence.

The protocol/configuration are frozen before running the constructor. Fixing
implementation errors is permitted and must be described; changing a selection
rule requires a new protocol version and retained earlier outputs.
