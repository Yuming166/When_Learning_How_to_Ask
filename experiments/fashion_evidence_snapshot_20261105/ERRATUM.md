# Correction to the historical Luna 48-profile report

The archived report says that the sole invalid answer, `A-P10__r1__pattern`,
contained out-of-vocabulary `dyed` and `yoke design` labels. That diagnosis was
incorrect: both labels occur in the supplied profile. The raw answer encoded
all numeric scores as JSON strings (for example `"4"` rather than `4`), and the
frozen validator returned `score_domain`. No coercion or retry was performed.

The original report remains archived verbatim for provenance. This correction
changes the explanation only: 288 calls, 287 valid answers, one invalid answer,
all method outcomes, full denominators and confidence intervals are unchanged.
The revised manuscript uses the corrected diagnosis. Raw profiles, prompts and
model event streams remain local and are not included in this outcome release.
