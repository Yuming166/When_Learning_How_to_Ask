# Integration interface

## Material Passport

Isolated method package `experiments/phase2e_type_evidence_20261031/phase2e`.
Historical Exact and Phase 2a–2d copies are pinned by SOURCE_SNAPSHOT.json;
validated v0.2.1 public fixtures/compiler copies by FIXTURE_SNAPSHOT.json.
No files were written in the independently developed v0.2.x directories.

Construct a sampler with `construct_sampler(name, public, calibration, R)`.
The learner receives public d, groups[g].targets, rate_domain.eta, known finite
per-group type_accuracy and real high/low calibration bits. The complete set of
targets remains active. Call `next(set(range(d)))`, then `observe(action,result)`
for exactly that pending action. Actions are `('query',j,'A'|'B')` or
`('type',g)`. Task results are normalized binary `{'answer':0|1}`; type results
are `{'format':'A'|'B'}`. The sampler does not receive truth, true rates/types,
seeds, private records, scores or an environment object, and does not stop itself.

The external fixed-confidence driver computes the full continuous profile GLR
at the existing check cadence. A float crossing is only a prefilter for
`phase2d.certified.certify_stop(counts,groups,calibration,type_answers,s,R,eta,
candidate_theta=...)`. Only `certified=True` authorizes a strict output.
At cap an unaccepted path has `strictly_certified_output=null`; the required
`submit` call is a separately scored terminal guess. R stays in log-risk form.

Exact environment methods are unchanged: reset, get_calibration, query,
ask_type, submit. The unchanged generator/environment provide shared potential
response streams and calibration within each world. Spawned JSON-only workers
run after LP/quadrature bootstrap under the existing Landlock file/network
boundary; evaluator is non-dumpable. No live model/provider code is imported.
This is the original controlled built-in learner boundary, not a new general
sandbox for adversarial plugins.

`validate_exact` rejects unknown type accuracy, missing iid bounded-rate domain,
invalid calibration and d>4. Natural/semantic interfaces that declare
`type_accuracy='unknown'` or no assumed bounded iid domain are unsupported by
this certified method version. Empty real reference streams (M=0) are supported;
missing reference availability is not converted to fabricated samples.

Existing public v0.2.1 independent/dependent fixtures are used only to test
compiler A/B normalization and interface rejection. Their 96 target propositions
produce 768 encoded-bit checks plus invalid-answer cases. No private fixture
key, new natural instance or provider call is needed. An invalid natural answer
remains missing; it cannot be inserted as a 0/1 task observation in this model.
B's option digit must be normalized through its declared answer mapping.

To reproduce locally, from the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONPATH=experiments/phase2e_type_evidence_20261031 \
python -m unittest discover -s experiments/phase2e_type_evidence_20261031/tests -v
```

The acquisition runner refuses an existing artifacts directory and has no
confirmation or retry launcher. Existing raw development output can be audited
without resampling. A new scientific run requires a new output directory and
an explicitly labeled development revision, not deletion of the current results.
The eight requested documents, code, source snapshots, raw output and receipt
are reviewable locally; no merge, publication or cross-session integration has
been performed.
