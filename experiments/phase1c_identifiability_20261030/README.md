# Phase 1c — Identifiability and Benchmark Feasibility Audit

Start with [REPORT_ZH.md](REPORT_ZH.md), [BENCHMARK_AUDIT_ZH.md](BENCHMARK_AUDIT_ZH.md), [IDENTIFIABILITY_NOTE_ZH.md](IDENTIFIABILITY_NOTE_ZH.md), [PROTOCOL.md](PROTOCOL.md), and the completed run's `run/REPORT_ZH.md`.

New isolated experiment directory; no previous artifact modified. Bernoulli exact tests and empirical discovery are separate. This is reliable information elicitation, with no human-behaviour or asymptotic-LLM claim.

## Reproduction

Python 3.13 standard library suffices for fetch, logic/data audits and exact enumeration. Analysis uses NumPy/Matplotlib. Offline inference uses the existing environment recorded in `config.json` and model identity receipt; no package or model installation is required. Full paths in config are local deployment details and can be changed only for a separate, explicitly recorded replication.

```bash
python3 fetch_sources.py
python3 fetch_contract.py
python3 logic_audit.py
python3 identifiability.py
python3 design.py
python3 dependency_audit.py
python3 -m unittest -v test_phase1c
```

Source acquisition extracts members using the supplied central directory indexes (under `source_indexes/`). Those indexes record official URLs, ZIP offsets, CRCs and sizes. `fetch_sources.py` refuses source overwrites; source receipts give hashes. Keep the supplied indexes/receipts alongside any archived run. Large sources and respondent prompts are ignored by Git.

The existing run is immutable and `collect.py` refuses reruns. Its `freeze.json` was written after preflight and before any model generation; collection checks source/data hashes before loading. Earlier preflight manifest is retained to document a position-balancing correction made before calls. All 192 requests are unique seeds, with 24 included as technical smoke. To inspect/recompute without new generations:

```bash
python3 analyze.py
```

To replicate inference, copy to a separate directory, explicitly authorize and record a new run, reconstruct data and a new source/data freeze, then use the frozen launch command. Do not delete this directory's `run/` to bypass the cap.

```bash
CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 TOKENIZERS_PARALLELISM=false \
  /storage/gaoym/wcl_v100_venv/bin/python collect.py
```

The user example said 384 calls, but 8 groups × 6 targets × 2 formats × 2 repeats = **192**. This run preserves those factors and caps itself at 192, with no retries or extra baseline generations. Selector replay costs differ and are reported; response correctness is not equal-budget recovery performance. Direct-type/public-metadata model probes and a 35B replication were not executed.

Source/data provenance, historical hashes, frozen protocol, raw outputs, scoring, failures, analysis JSON and plots are kept locally. `FINAL_RECEIPT.json` records final checksums; construction checks are not independent scientific validation.
