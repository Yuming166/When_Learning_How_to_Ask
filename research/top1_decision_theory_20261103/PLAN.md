# Decision-focused recommendation theory: bounded exploration

Date: 2026-11-03 (Asia/Shanghai). Base public commit: `cc3861b669b9e30e7a08834ed203f77fa4d86984`.

User-approved question: how does learning query reliability change when the goal is the best recommendation rather than the entire preference vector?

This directory is isolated from the published four-page draft. No model calls, training, user study, paid service or large benchmark is authorized or needed. Mathematical and deterministic CPU checks are permitted. This is exploratory theory development, not confirmation or a novelty certificate.

## Model retained

Keep the original binary coordinate/form observations, known partition, globally unknown high/low accuracies, finite labelled reference streams, and the oracle that knows only format types. Change the terminal decision to a unique best item in a known affine-utility catalogue. Do not replace the oracle by a known-rate oracle without separately labelling that control.

## Questions and initial controls

1. Derive decision-changing alternatives and their minimal flip sets. This is standard pure-exploration/certificate machinery, not automatically a novel result.
2. Test a one-coordinate-dominant catalogue and OR/AND catalogues. Retain a counterexample if the old smallest-group theorem fails.
3. Examine two-item threshold catalogues, including majority and states close to a decision boundary. Seek a closed structural equality criterion.
4. Compare fixed small instances at zero and positive calibration ratios. Report unknown-rate and known-rate controls separately.
5. Check whether irrelevant coordinates can be useful for reliability calibration. Do not remove their available actions by assumption.

## Deliverables and stop

Produce a proof note, executable continuous-information-program checks, bounded primary-source comparison, and a Chinese decision report. Preserve all failed guesses and distinguish an analytic coefficient theorem, its ideal-policy expected-time interpretation, and numerical optimization evidence. Do not modify or push the published paper during this exploratory step.
