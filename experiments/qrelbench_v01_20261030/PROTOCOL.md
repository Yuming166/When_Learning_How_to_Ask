# QRelBench v0.1 frozen development protocol

## Material Passport

Artifact: benchmark construction and CPU development pilot. Authority: user-provided QRelBench v0.1 task. No LLM/API/GPU calls, training, Phase 2, or confirmation. Historical Phase01, UserBench and Phase1c remain immutable. The protocol and all package/tests/config bytes are hashed before the main pilot. Preflight changes/failures are retained; no post-confirmation fixes are possible because confirmation is not executed.

## Source, facts and information boundary

Fictional private Product/Offer catalogs, Schema.org concepts only; not scraped real products. Each of 16 independent Bernoulli(.5) facts has its own record. No forced balance. Four predicates: explicit availability, price <= public threshold, shipping charge ==0, return days >= public threshold. Public IDs/kinds/thresholds use separate pseudorandom domains from truths/types. A/B refer to the exact same canonical proposition and truth-to-answer mapping. The response channel uses verified database truth and supplied format, not an LLM or linguistic parser.

Known partitions: [1,15], [2,14], [4,12], [8,8], [16]. Hidden source types sampled independently of facts/metadata. Global p=.85,q=.60 for the base experiment; p/q hidden from policies. Known eta=.05 bounds rates away from one. Independent correctness draws per (target,format,count), independent high/low labelled reference streams and independent type reports s=.80. HMAC substreams implement reproducible pseudorandomness; the actual development seed is newly sampled into a mode-0600 evaluator-only file and only its SHA commitment enters the public freeze. The config contains no usable seed; future train/test evaluation must use independently generated secrets, not a derivation of any released development seed. Independence is a model/construction assumption, not proved by finite autocorrelation tests. Across strategies and grouping/budget comparisons, common random numbers pair the same independent catalogs and streams. The built-in policy object is rebuilt per episode and retains no observations across jobs.

Learner uses a spawned process, JSON-whitelisted reset/query/ask_type/get_calibration/submit only. Private objects are never sent. Before any job, Linux Landlock ABI>=4 denies handled new file reads/writes/creation/execution and TCP bind/connect; stat/exists metadata is not covered; existing pipe FDs remain usable. Trusted evaluator is non-dumpable to block child process-memory reads. Bootstrap must be single-threaded. Missing confinement fails closed. This addresses readable config/seed reconstruction, but is not a general kernel, UDP or denial-of-service sandbox; no arbitrary unreviewed plugin or attacker code is executed. Reproduction manifests are private artifacts. Source/config values in research documentation are not a grant to hardcode unknown channel parameters into strategies.

reset may occur once per server episode, cannot choose seed; get_calibration caches the same finite data and charges once; submit is terminal and returns acknowledgement only. Score is evaluator-only and RPC-inaccessible. Ordinary client receives no oracle types; Oracle gets z and nothing else extra.

## Policies and decoding

Seven strategies: Fixed A/B; per-target alternating Round-Robin; ETC (two targets/group, or one for singleton, each AABB, then commit); Repeat-and-Compare (alternate complete balanced AABB target sweeps with repeated selected-format sweeps); one Direct Type Query/group then commit; format-only Oracle. Consistency choice uses smoothed agreement rates with pair denominators, not accumulated counts. Every exploration/type action consumes online budget; no free warmup. Tie rule is public deterministic group-index alternation.

Fixed-budget decoding is identical across strategies: estimate p/q from high/low reference success bits with add-one smoothing, project to .5<=q<=p<1, enumerate <=2^16 joint signs per group while marginalizing z and incorporating known-s type reports. This is exact for the plug-in rate posterior used, not a full posterior over uncertain continuous rates. Oracle prior fixes z only. Independent brute-force checks validate the decoder. No information-optimal query allocation is implemented.

## Fixed-budget protocol

Budgets 64,128,256 online actions including tasks plus type queries. 24 development episodes per partition/budget/policy. Finite calibration M=64 each, separately charge 128 offline observations to all strategies. Endpoint returns all 16 predictions; primary score is exact vector recovery. Wilson intervals on episode success; paired bootstrap (5,000, seed2026103017) vs RR uses the same episode IDs. Exploratory only, no positive-performance gate.

## Fixed-confidence protocol

Delta .10,.05,.01; 2 development episodes per partition/delta/policy; cap4096 online actions. M=ceil(64 log(1/delta)) per offline stream. For target j at n observations, let S=sum(2Y-1); certify if |S|>sqrt(2n log(2*d*n*(n+1)/delta)). Keep certified signs fixed. The conditional one-sided Hoeffding argument and sum_n1/[n(n+1)]=1 bound any wrong certificate by <=delta/2, hence <=delta, in the intended channel domain even with predictable adaptive choices. This is a conservative safety certificate, not the original GLR or an optimal allocation. It does not assure termination when only noninformative channels are sampled.

All uncertified cases remain censored, with cap cost and diagnostic guesses explicitly separated. Report completion, any certificate error, full restricted mean min(T,cap), online task/type/offline/total acquisition costs. Do not report completed-only mean as E[T], do not claim observed n=2 validates delta calibration, do not fit asymptotic coefficients.

## Negative controls

Each control: eight fixed-budget episodes B128 and one confidence episode delta.10 cap4096, seven policies, default [8,8] except no-sharing [1]*16. Equal informative p=q=.725; equal chance p=q=.5; true singleton groups; perfect type s=1; label-asymmetric correctness r for theta1 and 1-r for theta0; persistent correctness one draw per item/format forever. Label-asymmetric/persistent violate certificate assumptions and errors are retained and labelled. Equal-chance may never finish. No gaps, profiles or methods discarded based on scores.

## Limits and gate

3,108 total planned strategy-episodes; maximum 1,451,520 online actions; one worker at a time, one BLAS thread, 300-second hard pilot timeout, no retries/overwrites. Main pilot only after own tests and independent source/CPU audit pass; actual config content must match the frozen hash. Every failure produces an execution receipt and retained data. This is a bounded CPU development run, not a confirmatory benchmark sweep.

GO means technically valid theory-controlled benchmark for further review; not natural reliability GO or method superiority. REVISE on data/interface/cost/mathematical defects; stop without pilot if unresolved. After tests, audit and bounded pilot, stop and report. No natural-channel discovery or larger runs without new decision.
