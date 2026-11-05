# Record conventions

## Material Passport

v0.1; source-claim catalogue; no model-produced or human preference labels.
Machine-readable product schema: schemas/product.schema.json, JSON Schema
2020-12. The executable verifier is standard-library-only; no JSON Schema
package is required. It checks source bindings and cross-record invariants
beyond structural schema validation.

`products_all.jsonl` and `catalogue_strict.jsonl`: one object per product ID.

| Field | Meaning |
|---|---|
| product_id | Literal source ID string; not an independently verified physical identity |
| title / brand / gender / domain / category | Source metadata, not newly generated names |
| attributes.<field>.status | reported / unknown / ambiguous |
| attributes.<field>.value | Single normalized value, else null |
| attributes.<field>.reported_values | All distinct normalized labels, including unresolved alternatives |
| attributes.<field>.source_labels | Literal source labels with only display whitespace trimmed |
| attributes.<field>.evidence_ids | Join to source_claims.jsonl |
| all_specification_claims | Keys present; complete claim values remain in source_claims.jsonl |
| variant_ids / source_records | Full joins to variants.jsonl |
| source_price | Historical numeric strings, min/max, currency=null |
| size_labels | Historical source variant labels; not size measurements |
| source_descriptions / source_care_material_texts | Preserved seller text |
| source_dominant_material_labels | Separate source labels; no composition inference |
| image_urls | Empty in this source version |
| split / leakage_group_id | Group-reserved allocation, not an experiment outcome |
| quality | Gate results, exclusions, limited detected discordances, claim limits |

`variants.jsonl`: one nonempty source record, including raw_cells in the exact
24-column order, raw_fields, logical source_record, source_record_id, literal
variant_id, timestamp, size, price, stock label and recovered specification
columns. A specification in inventory means the stock number is unknown.

`source_claims.jsonl`: one explicit key/value pair. evidence_id is
`r<record>c<column-index>p<pipe-segment-index>`. Column index is zero-based;
source_record includes the header as record 1. Embedded CSV newlines do not
increment this logical record number. span=[start,end] indexes Python Unicode
characters in that original cell, with an exclusive end. fragment is exactly
the cell substring. Normalized keys/values do not replace the source text.

`factual_cards.jsonl`: product_id, split, leakage_group_id, five literal facts,
their evidence IDs, source price, recorded sizes and neutral Chinese card text.
No promotional language, purchase target, utility, user identity, acceptable
set, model answer or correctness label is added. Actual attractiveness and
physical attribute intensity remain unmeasured.

CSV uses UTF-8 with BOM for common spreadsheet tools. Non-scalar sizes,
variants and exclusion lists are JSON strings in `_json` columns. Prices are
decimal strings in JSON. CSV blank values must be interpreted using status
columns. Pattern and print_pattern_type are separate, and component fabric
fields never silently populate the whole-garment fabric field.
