# GLM-5.3 customer-family transfer on the fixed Myntra panel

This experiment collects exactly one independent GLM answer for each of the original 48 profiles × six fields. Four frozen deterministic recommendation policies share those answers. All 280 original profile-menu cases remain in every budget cell.

Read `PROTOCOL.md` for the fixed deployment and scientific claim limits. Results are written to `results/REPORT_ZH.md` and include Luna, DeepSeek and GLM comparisons, full denominators and a clearly secondary common-valid subset.

Zero-call verification and offline analysis:

```bash
python experiment.py verify
python experiment.py analyze
```

The initial authorized collection uses `python experiment.py run`. The collector reads the API key from `DASHSCOPE_API_KEY` or hidden terminal input, never saves it, and refuses repeated runs. Transport is pooled requests.Session, serial SSE, no retries and no redirects. Stream content is scored only after a complete finish and [DONE]; reasoning deltas are excluded from final-answer parsing.

Offline mocked tests:

```bash
python -m unittest -v test_experiment.py
```

This is a reused development panel with supplied structured profiles. It does not establish natural user behavior or broad agent-family generalization.
