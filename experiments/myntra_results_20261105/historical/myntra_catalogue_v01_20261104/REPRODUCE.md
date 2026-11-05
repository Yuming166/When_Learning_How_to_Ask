# Reproduce the catalogue

## Material Passport

Python 3 standard library only; tested on Python 3.13.13. No models, GPUs,
credentials or paid services. Raw and derived records stay in ignored artifacts/.
Run commands from this experiment directory. Existing output directories are
never overwritten.

1. Obtain the pinned source bytes. On the current machine they are already in
   artifacts/source/. This command checks and reuses them without network:

```bash
python acquire_source.py
```

On a fresh machine this attempts one bounded (4MB) HTTPS download of the pinned
file, verifies SHA256, and retains partial bytes on failure. It does not retry,
fall back to another dataset, bypass TLS or execute an upstream script. A file
downloaded manually from the listed repository must have the exact config hash.

2. Run the semantic failure-mode tests:

```bash
python -m unittest discover -s . -p test_catalogue.py
```

3. Build into a NEW directory. The default output already exists on the current
   machine; use the explicit replay output below when inspecting this checkout:

```bash
python build_catalogue.py --output artifacts/my_replay
```

4. Independently check source fidelity and splits:

```bash
python verify_catalogue.py --output artifacts/my_replay --receipt artifacts/my_replay_verification.json
```

Default final catalogue: artifacts/catalogue_v01_final/. The earlier development
output artifacts/catalogue_v01/ is retained with its original constructor hash;
it predates the documented neckline word-form bug fix. See implementation
history. Use the final catalogue, not the initial development output.

Every generated file, including MANIFEST.json, is deterministic. A complete
offline replay has been compared byte-for-byte with the final output; its
network sockets were disabled. Receipt: results/REPLAY.json.

Do not edit config.json or PROTOCOL.md to increase yield. FREEZE.json protects
both, and an alternate --config cannot bypass its hash. A new selection rule
requires a new version. Constructor fixes must preserve earlier outputs and
document the reason. New code changes also require regenerated data and a new
manifest; the verifier checks the constructor identity.

results/ contains only aggregate summaries, hashes and receipts. No source or
derived catalogue rows are staged in Git. Future reserved-split performance
evaluation, simulator generation, Qwen calls or query-agent ranking are separate
tasks and are not launched by any script in this package.

The local ZIP contains source bytes, final records, schemas, code and documents;
it excludes the initial development output and the redundant offline replay.
To rebuild a local bundle without replacing the existing one:

```bash
python package_catalogue.py --output artifacts/my_catalogue_bundle.zip
```

Packaging verifies CRC and every member against its local bytes. It performs
no upload. Data rights and source limitations are described in DATASET_CARD.md.
