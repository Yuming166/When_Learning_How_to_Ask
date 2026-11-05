# DeepSeek V4.1 Flash customer response replication

Same 48 synthetic development profiles, 35 menus and 280 cases as the completed Luna panel. The original experiment is preserved. Protocol and configuration are frozen before collection.

Read `results/REPORT_ZH.md` for results and limitations. Read `PROTOCOL.md` for the exact comparison and deployment differences.

Completed-run verification, with zero network calls:

```bash
python experiment.py verify
```

Offline replay and analysis, also with zero network calls:

```bash
python experiment.py analyze
```

Collection command for the initial authorized run only:

```bash
python experiment.py run
```

This transport continuation carries forward all 24 initial attempts, including ten TLS failures, and calls only the 264 never-attempted jobs. The collector reads `DASHSCOPE_API_KEY` or asks through hidden terminal input. It refuses a second run if any continuation attempt exists. It sends the original text prompts to the configured Qianwen endpoint. No credential is saved. HTTPS uses a pooled requests.Session, concurrency 1, with no retries or redirects. Read the post-failure continuation disclosure in `PROTOCOL.md`.

The test suite uses mocked failures, never a live API:

```bash
python -m unittest -v test_experiment.py
```

All four strategies share each model's response bank. A frozen, exact cache rule avoids repeating deterministic computation for profiles whose entire effective answer bank equals Luna's. Every field is still actually collected from DeepSeek. All cases for a changed profile are replayed using the unchanged original policy and evaluator.

This is a structured fixed-profile answer check on an existing development panel. It does not validate a human simulator, natural multi-round purchase behavior, or independent held-out generalization.
