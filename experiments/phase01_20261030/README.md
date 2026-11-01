# Learning How to Ask — isolated Phase 0/1

Historical `Theory_Note.md` and V5 PDF remain untouched. Source checkout:
`3186587a5eb1aa4abc02c43d2ebb1e5f2ce050c3`; branch `phase01/reliability-discovery-20261030`.
No push or release is performed. See `reports/AUDIT.md` and `reports/PROTOCOL.md` before interpreting results.

## Reproduction

From this directory, using the existing system Python (NumPy, Matplotlib) for construction/analysis:

```bash
python3 -m unittest -v test_pipeline.py
python3 design.py smoke
python3 design.py pilot
python3 -c 'import time; from collect import hashes; from design import ROOT, write_json; write_json(ROOT / "freeze.json", {"files": hashes(), "frozen_unix_time": time.time()})'
```

Data generation refuses overwrite. The two stage seeds are disjoint. Freeze source and both datasets **before any generation**. The checked-in/generated manifest records the exact frozen bytes. A new run must use a fresh isolated directory and must not overwrite these development observations. Tests fabricate answers only inside a temporary unit-test directory, never in `runs/`.

The existing offline environment is `/storage/gaoym/wcl_v100_venv/bin/python`; the existing checkpoint is `/storage/lianjh/modelzoos/Qwen/Qwen3.5-4B`. Set GPU 3 explicitly and verify it is still idle immediately before launching:

```bash
CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 timeout 5500 /storage/gaoym/wcl_v100_venv/bin/python -u collect.py smoke > runs_smoke.log 2>&1
python3 analyze.py smoke
```

Inspect `runs/smoke/smoke_gate.json`. The collector independently enforces this gate and the frozen manifest:

```bash
CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 timeout 5500 /storage/gaoym/wcl_v100_venv/bin/python -u collect.py pilot > runs_pilot.log 2>&1
python3 analyze.py pilot
```

There is no automatic retry or stage chaining. Logs flush every response and progress prints every 16. Monitor PID/liveness and `runs/*/raw.jsonl`; stage deadline is 5,400 seconds plus a 5,500-second external hard timeout. Maximum 3,344 generations for smoke + pilot. Sampler never reads `private_truth.jsonl`. Raw records include complete prompts, seeds, outputs and identity bindings; `scored.jsonl` joins correctness after collection. Statistical selectors receive the label-free `selector_observations.jsonl` projection.

The optional API backend requires a genuinely served `Qwen3.5-4B` at an inspected local address. It checks `/models` and every returned model ID, refuses substitution, bypasses external HTTP proxies for local inference, and reads an optional `QWEN_API_KEY` only from the environment. Changing backend/config invalidates the old freeze and smoke gate and needs a new experiment directory. No keys are written to logs.

## Outputs

- `reports/AUDIT.md`, `reports/environment.json`, `reports/PROTOCOL.md`: provenance, actual service/resource inventory, task and analysis contract.
- `data/{smoke,pilot}/`: private deterministic truth, prompt requests, public metadata, construction checks.
- `freeze.json`: protocol/source/data SHA-256 and freeze time.
- `runs/{smoke,pilot}/`: actual model-file identities, raw and scored responses, denominators, execution receipts.
- `runs/pilot/PILOT_REPORT.md`, `analysis.json`, `group_diagnostics.jsonl`, `failure_examples.jsonl`, `discovery.png/pdf`: development results and claim limits.

No raw V5 implementation or V5 call records were present in the supplied repository at audit time. Its PDF percentages remain historical, not locally reproduced. This pipeline never uses the V5 outcomes to choose a successful task or method. The pilot is a falsifiable initial environment, and a negative result is a complete scientific output.

## Completed result

Smoke: 80/80 valid. Pilot: 3,264/3,264 valid, including all 3,072 task samples. No retries, unattempted samples, training or 35B generations. Frozen primary decision: `REVISE_OR_NO_GO`; no Phase 2 execution follows. Read `runs/pilot/REPORT_ZH.md` for the Chinese six-dimension report and `runs/pilot/PILOT_REPORT.md` / `analysis.json` for the frozen analysis. `describe.py` was added after collection solely to reproduce explicitly descriptive companion counts; it is outside the frozen primary test family and never changes selection/gates. Run it with `python3 describe.py`.
