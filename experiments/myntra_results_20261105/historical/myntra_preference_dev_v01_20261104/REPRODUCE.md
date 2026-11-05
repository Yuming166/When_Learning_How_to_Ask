# Reproduction and interfaces

## Material Passport

Python standard library only; existing local inference service for the frozen
16-call run. Zero-call verification is the default way to inspect the result.
Raw catalogue, personas, prompts and model records are ignored in Git.

From this experiment directory, with the current local artifacts present:

```bash
python verify_records.py
```

This verifies source bindings, public/private isolation, the 16-attempt ledger,
actual disclosure history, model IDs and response hashes; then denies networking
and replays seven input files, deterministic reference episodes and analysis.
It never generates another model response. Historical-file verification needs
this worktree's inherited source files and PRESERVATION_BASE.json.

Semantic and parser tests:

```bash
python -m unittest discover -s . -p 'test_*.py'
```

Prepare a fresh offline copy without replacing the frozen inputs:

```bash
python environment.py prepare --prepared artifacts/my_offline_prepared
python environment.py offline --prepared artifacts/my_offline_prepared
```

This reuses the pinned input catalogue at artifacts/input/catalogue_strict.jsonl.
On a fresh checkout, reconstruct the prior myntra_catalogue_v01_20261104 dataset
following its REPRODUCE.md, and copy only its final catalogue_strict.jsonl to
this input path. Required SHA256 is in config.json and results/SOURCE.json.
Do not substitute another Myntra revision or silently regenerate split labels.

Public interface:

```python
agent = PublicAgent(public_menu, public_vocabulary, strategy="fieldwise")
action = agent.next_action()
agent.observe(action, actual_user_answer)
result = agent.finish()
```

PublicAgent has no private-profile/evaluator path. An incomplete disclosure
returns status=INSUFFICIENT_PREFERENCES with decision=null. A completed state may
return decision=NO_BUY. These are different states. The reference user is only
a deterministic software test double, never a claimed Qwen observation.

The recorded two-turn model sequence is whole-profile inquiry -> actual Qwen
reply -> PublicAgent recommendation -> Qwen final choice. PublicAgent is the
transparent full-disclosure baseline, not the original KL/IG strategy, an LLM
recommender, or a trained policy. Fieldwise questions transmit categorical score
maps and cannot be cost-compared as if they were atomic binary observations.

The collector CLI has prepare/freeze/run modes, but the existing frozen run
refuses re-execution because artifacts/qwen_smoke already exists. No automatic
retry, resume, profile replacement, second model or prompt search is provided.
A new observational experiment needs a new directory/protocol and bounded call
plan. Do not delete records to bypass this guard.

All planned/attempted/valid denominators remain in results/QWEN_SMOKE.json.
Protocol and configuration hash freeze: RULES_FREEZE.json. Pre-inference code,
prompts and input hashes: RUN_FREEZE.json. Source/record verifier was added
after sampling, and does not change the pre-frozen evaluation definitions.
