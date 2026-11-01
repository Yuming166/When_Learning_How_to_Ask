# T3 computational and acquisition cost

## Material Passport

CPU-only NumPy neural training; no PyTorch dependency, GPU, language model or API. All actual-world acquisition and posterior-predictive simulation costs are separate ledgers.

Executed actual-world paths: **4488**. Online actions: **162048** (task 153917, type 8131); offline observations 199296; total acquisition **361344**. TRAIN/DEV collection and DEV evaluation are included, not discarded as free preparation. Fixed-budget arms have identical online and total acquisition cost per paired world. No equal-reliability query saving was measured.

Measured scientific CPU through TEST: **1018.31s**; sum of measured stage wall times **323.24s**. Four parallel evaluator lanes are capped; workerCPU is the appropriate additive policy comparison and wall time is not a single-thread speedup. The aggregate includes measured coordinator/reaped descendant CPU after each stage entry, including label generation and subprocess setup; excludes initial coordinator imports, human preparation/reporting and unrelated sessions.

Nine fixed MLP fits (1857 parameters each) consumed 1.873s CPU. Selected Joint / WorstFact B32 workerCPU ratio: **2.580**. Full labels and component CPU are in COMPUTATIONAL_COST.json and RESULTS.json. Feature/candidate construction includes an AnalyticReuse proposal; a cheap neural forward pass is not an end-to-end speedup. No break-even benefit is claimed when online deployment itself is slower.

Component timers posterior/target/controller are the primary breakdown. feature_and_candidates and network_inference are SUBCOMPONENTS of controller, not extra exclusive CPU; legacy planner timers also overlap. Do not sum overlapping components. Aggregate process/descendant CPU is the complete measured scientific ledger.

train: 192 states from48 worlds; 160128 simulated continuation queries; 86.97s measured label-function CPU, 22.36s wall. These internal simulations are not online observation purchases; their computational cost is counted.

development: 96 states from24 worlds; 77504 simulated continuation queries; 43.63s measured label-function CPU, 11.60s wall. These internal simulations are not online observation purchases; their computational cost is counted.

Terminal certified outputs: 0/4488; normal non-certifications: 4488; infrastructure failures 0; incomplete planned paths 0. Gate reason counts are in VALIDATION.json. Numerical exceptions would be execution failures, distinct from a conservative gate refusing certification. Full-budget non-certification is censoring only for certified-stopping time; it is not a missing fixed-budget recovery outcome.
