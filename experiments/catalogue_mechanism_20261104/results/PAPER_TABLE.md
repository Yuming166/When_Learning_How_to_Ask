# Compact complete-denominator paper table

Every entry uses six paired response seeds. Means are restricted query costs; F marks a failed KL path charged the full 2,500 cap. IG and round robin certify all six paths in every row.

| Catalogue / partition | R | KL mean (certified) | Repaired IG mean | Round robin mean | IG minus KL [paired 95% CI] |
|---|---:|---:|---:|---:|---|
| weighted5_zero | 3 | 182.33 (6/6) | 224.67 | 533.33 | +42.33 [+2.67, +84.00] |
| weighted5_zero | 9 | 227.67 (6/6) | 295.17 | 581.33 | +67.50 [+23.67, +122.50] |
| weighted5_positive | 3 | 222.00 (6/6) | 235.00 | 449.67 | +13.00 [-4.00, +32.00] |
| weighted5_positive | 9 | 258.17 (6/6) | 267.17 | 534.33 | +9.00 [-16.67, +39.50] |
| genuine6_zero | 3 | 232.17 (6/6) | 189.83 | 443.50 | -42.33 [-65.00, -18.00] |
| genuine6_zero | 9 | 264.00 (6/6) | 216.67 | 536.17 | -47.33 [-73.33, -20.50] |
| genuine6_positive | 3 | 694.83 F (5/6) | 308.83 | 513.17 | -386.00 [-1110.83, +2.50] |
| genuine6_positive | 9 | 758.67 F (5/6) | 382.33 | 588.33 | -376.33 [-1086.67, +2.00] |

Positive IG-minus-KL favors KL. Intervals resample response tapes conditional on fixed catalogue/profile anchors; six seeds do not establish broad generalization.

Total: 144 planned paths; 142 certified, two numerical KL allocator failures, zero capped, zero wrong certified. The failures occur at the same seed and t=213 in the genuine6/split cell for R=3 and R=9. They are one paired numerical failure event observed at both risk settings, not two independent failure mechanisms.

Exact asymptotic coefficient statements and empirical restricted query counts are different quantities. No known-type empirical oracle is included.
