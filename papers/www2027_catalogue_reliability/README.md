# Reliable recommendation: catalogue geometry and decision value

Updated 2026-11-05. **Four-page anonymous author-review draft; not submitted.**
The pre-bridge paper is preserved byte-for-byte in `history/pre_bridge_20261104/`.

- [Current PDF](main.pdf), [LaTeX](main.tex), [Chinese completion report](OVERNIGHT_REPORT_ZH.md).
- [Claim/evidence map](OUTLINE_AND_CLAIMS.md), [writing and scientific review](WRITING_REVIEW_ZH.md).
- [Bridge experiment](../../experiments/decision_value_bridge_20261105/INTERPRETATION.md): 264 paths, 257 certificates, seven preserved KL numerical failures. Plain one-step DV **does not beat decision-IG** and matches RR stopping costs on all 66 paired worlds.
- [Analytic bridge](../../research/decision_value_bridge_20261105/BRIDGE_PROPOSITIONS.md): standard VOI identities, allocation-independent safety, exact within-channel myopia example with an explicit open neighborhood.
- [Bounded novelty audit](../../research/decision_value_bridge_20261105/NOVELTY_AUDIT.md): the DV principle and generic myopia are established; no first/optimal/universal-superiority claim.
- [Fashion evidence](../../experiments/fashion_evidence_snapshot_20261105/README.md): six historical panels, full budgets 0–6, paired outcome replay, strong held-out caveats and one explicit parser-diagnosis correction.
- [Full-budget figure](../../experiments/fashion_evidence_snapshot_20261105/results/full_budget_curves.pdf).

The structural contribution is the exact catalogue–sharing zero-premium
criterion. The methodological contribution is an implementation, paired
connection and limitation analysis. It is **not** a newly invented VOI principle
or an asymptotically optimal DV algorithm. The fashion adapter and the theorem
have different response spaces and correctness targets.

## Build

```sh
python -B papers/www2027_catalogue_reliability/build.py --tectonic /path/to/tectonic
```

This regenerates both tables from the released analysis and reconstructable
outcome summaries. `RESULTS_SOURCE.json` binds inputs; `BUILD_RECEIPT.json` records
compiler, hashes and checks. The local Tectonic 0.15.0 bundle contains acmart
2022/02/19 v1.83. The official current template still needs to be used for the
submission build. No font-size or page-margin overrides are used. The paper
includes references within its four pages. Author review remains necessary;
assistant checks are not external peer review or proof-assistant verification.

## Reproduce without new data or model calls

From the repository root:

```sh
python -B research/catalogue_paper_mainline_20261104/check_structure.py
python -B research/decision_value_bridge_20261105/exact_bridge_certificates.py
python -B experiments/decision_value_bridge_20261105/replay_release.py
python -B experiments/decision_value_bridge_20261105/test_protocol.py
python -B experiments/decision_value_bridge_20261105/analyze.py --mode main
python -B experiments/fashion_evidence_snapshot_20261105/analyze.py
python -B experiments/fashion_evidence_snapshot_20261105/plot_curves.py
```

The bridge archive contains every synthetic engineering/main history. Full
adaptive replay is possible from this public checkout. Fashion records support
outcome/statistical replay; they do not reconstruct all product/profile/prompt
inputs. The byte-identical fashion policy source is included as a reference,
with this limitation explicit. Raw marketplace data and model event streams
are not republished. No new model calls or training were performed in this
revision; historical Luna experiments are labeled as such.

The repository is a public research record. Prepare the submission artifact
according to the venue's current anonymity rules; do not label a public GitHub
link as anonymous. Nothing here constitutes conference submission.
