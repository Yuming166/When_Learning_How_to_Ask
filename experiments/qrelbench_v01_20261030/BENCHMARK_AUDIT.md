# QRelBench v0.1 benchmark audit

## Material Passport

Scope: requested synthetic benchmark construction, code/semantic/statistical validation, independent local review, bounded CPU development. Theory source: repository `Theory_Note.md` (unchanged). Previous Phase01/UserBench/Phase1c reports read and retained. User authorization explicitly excludes Qwen, paid APIs, training, Phase 2 and confirmation. Separate reviewer is a same-family Codex agent, not an independent external expert or cross-model replication.

## Decision

**GO for a theory-controlled benchmark prototype and the bounded built-in-policy CPU pilot, after recorded tests/review and source/seed freeze.** This is not a GO finding for naturally occurring shared reliability, general adversarial-agent security, confirmatory evaluation or an adaptive method's superiority. Those claims remain unsupported.

## Assumption-by-assumption contract

|Requirement|Construction/evidence|Boundary|
|---|---|---|
|Independent unknown binary facts|One separately keyed Bernoulli(.5) bit per private Product/Offer record; no exact-balance filter, no shared records or cross-record rules|θ are sampled for evaluation; each realized episode is a fixed unknown vector|
|Known partition, hidden z|Requested five partitions; independent hidden type coin per source group|Sharing is planted, not discovered|
|Same proposition A/B|Same canonical predicate, record and 1/0 mapping; only rendering differs; independent predicate tests|No claim about an LLM interpreting the wording|
|Global unknown rates|Base p=.85,q=.60; only evaluator reads true rates; known eta=.05, same rate domain across groups|No algorithm is given true p/q; calibration estimates remain noisy|
|Fresh independent errors|Distinct HMAC domains for each target/format/count, type reports and high/low references|Standard reproducible pseudorandom simulation, not a proof of literal independence conditional on fixed seed; numeric sampling precision is 53 bits|
|Finite calibration|Labelled high/low correctness bit streams, same observations for paired policies, cached on repeated access|An explicit theoretical information resource, not ordinary unlabelled past dialogue|
|Optional types|Known s=.8, independent fresh reports; s=1 is a separate control|A simulated reporting channel, not measured self-report reliability|
|Oracle fairness|Only extra observation is z; same calibration, unknown rates, decoder and online cap|No true answers or free p/q|
|Public/private boundary|Spawned learner, JSON method allow-list; source/seed/truth/reward withheld; Landlock denies handled new file operations/TCP; parent non-dumpable|Stat metadata and existing FDs remain; trusted single-thread bootstrap; not general kernel/UDP/DoS sandbox|
|Reward access|submit returns acknowledgement, ends episode; scoring only in evaluator|No in-episode reward-based adaptation|
|Randomness isolation|Real development key freshly generated privately and commitment-bound before run; no usable config seed|Preknown/released seeds cannot be treated as secret; future confirmation needs independent unreleased seed|
|Split isolation|Distinct split domains and reserved ranges; main runner permits development only|No train/test evaluation run; structural tests are not held-out efficacy evaluation|
|Cost fairness|Online cap counts all task and type actions; exploration charged; offline separately logged|No free warmup or unequal-budget accuracy ranking|

## Provenance and semantics

Reference [Product](https://schema.org/Product), [Offer](https://schema.org/Offer), [availability](https://schema.org/availability), [shippingRate](https://schema.org/shippingRate), [merchantReturnDays](https://schema.org/merchantReturnDays). Source version/access and mappings are recorded in `SCHEMA_PROVENANCE.json`. Availability uses explicit InStock/OutOfStock; price uses a USD public threshold; shipping uses MonetaryAmount; return days includes MerchantReturnFiniteReturnWindow category. These are minimal fictional records inspired by the schema, not a validated merchant feed or scraped external dataset.

Private generation seeds, split/index, record witnesses, truth/type values and source types are retained only in privileged reproduction outputs. Ordinary public provenance includes generator version and schema reference, not reconstruction seeds. Both formats are checked against the same independently evaluated record predicate.

## Independent audit and prefreeze corrections

Read the hash-bound `audit/INDEPENDENT_REVIEW.md` for the full source-level review and independently executed probes. Findings were corrected **before any main pilot**, with failed probes and their dispositions retained:

1. Raw agreement totals rewarded extra sampling: replaced by smoothed agreement rates with pair denominators.
2. Coordinate marginal modes could be suboptimal for exact vector recovery: replaced by common groupwise joint MAP over <=2^16 signs, marginalizing z. Independent small-instance enumeration checks it.
3. A public fixed seed permitted full fact/future-stream reconstruction: replaced by freshly sampled evaluator-only development entropy and commitment; file-read route additionally blocked by confined worker. Future train/test keys must be independent of released development keys.
4. Full-word float division could round a random number to 1 and break perfect types: replaced by exact 53-bit [0,1) endpoints; deterministic endpoint regression retained.
5. Alternate CLI config could bypass a default-only freeze: selected config content now must match the frozen hash and its SHA is recorded.
6. Reviewer initial allow-list omitted the newly public known rate-domain bounds: stale test corrected after verifying it carried no realized rates. This is recorded as a reviewer assertion failure, not hidden implementation evidence.

Own generated/property/unit tests and separate reviewer CPU checks cover semantics, split/reproduction, public payloads, lifecycle/costs, fresh-error statistics, negative controls, exact decoder fixtures, fixed-confidence finite-state recursion, actual spawned IPC and file/TCP denial. These finite statistics can expose bugs but do not prove universal independence or human/LLM validity. Source stability and final audit hashes are bound before the main run.

## Fixed-confidence mathematical scope

Let X=2Y−1. Under the intended fresh channel, conditional E[X]>=0 for positive θ and <=0 for negative θ, even after predictable target/format choices. The one-sided exponential supermartingale bounds a wrong crossing at a target's nth observation by delta/[2*d*n*(n+1)]. Summing all n/targets gives <=delta/2, hence <=delta. A separate reviewer derived the adaptive-subsequence argument using truncated optional stopping and Fatou; no assumption of a random θ prior is needed for this certificate.

This certifies already frozen signs; it does not guarantee every policy terminates, especially q=.5. Uncertified outputs are censored diagnostics. It is not the joint continuous-rate GLR or achievability construction from Theory_Note §4, and no optimal cost coefficient is claimed. Information-optimal allocation is deliberately deferred; only small decoder/certificate mathematics has been checked.

## Reporting gates and integrity

Main pilot uses one frozen development plan, <=1,451,520 online actions and a 300-second cap. Every episode, failure, timeout, no-gap case and censor is retained. There is no accuracy-based rerun, seed search, profile selection or post-result method tuning. Statistical analysis is descriptive: episode-level Wilson intervals and paired bootstrap, no success requirement.

`PILOT_REPORT.md` distinguishes planted assumptions, executed observations, untested empirical hypotheses and prohibited conclusions. `VALIDATION.json`/`FINAL_RECEIPT.json` bind actual results and verify historical file hashes. Passing construction tests does not reverse previous negative Qwen findings. No confirmatory sample, natural-channel pilot or advanced adaptive method is included.

## Executed development receipt

The frozen run completed all **3,108 / 3,108** policy-episodes, **1,027,579** online actions in **273.45 seconds**, no retries and no experimental model calls. The 17 own tests and 10 independent check groups passed before freeze. Post-run validation reproduced eight existing trajectories exactly (all seven fixed-budget policies plus one Oracle confidence case), including full transcript hashes; replay used 1,239 additional CPU actions on already existing streams, not new scientific samples. All 131 hashed historical artifacts remain unchanged.

At online budget256, Repeat-and-Compare reached 91.7–100% exact recovery across the five partitions; RR reached 83.3–87.5%, while ETC reached 54.2–75.0%. These are 24-episode development cells. Only one of the five Repeat-and-Compare vs RR paired 95% intervals has a strictly positive lower endpoint; no familywise confirmatory claim is made. This is evidence that a cheap consistency baseline is a serious competitor under planted iid sharing, not evidence that a future complex allocator is necessary or superior.

Of 238 confidence trajectories satisfying the certificate's assumptions, 83 were censored and none had an incorrect issued certificate. Small n and repeated paired profiles do not empirically validate a delta guarantee. Outside-model controls produced incorrect certificates in 13/14 trajectories, illustrating why persistent errors and below-chance channels cannot inherit the theorem's assumptions. Full denominators and all costs remain in the episode table.

Post-run static scope note: the successful run has complete action accounting. On an exception, the execution receipt's aggregate counters cover completed, persisted episodes; the last interrupted episode could have additional actions without a completed record. Failed runs therefore require explicit incomplete-cost reporting, not use of that aggregate as a complete bill. Crash recovery and arbitrary hostile-agent deployment are not certified by this v0.1 pilot. No source was changed after freeze to alter the successful results.
