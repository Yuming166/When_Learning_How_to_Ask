# Catalogue robustness: Python and GPT-6 Luna

This addition retains the existing repository files. It supplies two matched tables on Myntra and Amazon, with Fixed order, Profile IG, Decision-set IG and one-step decision value at 3, 4 and 5 questions.

- `tables/table1_python.tex` and `.csv`: pure Python truthful-answer simulation. The companion chat reran the frozen protocol; its per-menu results match the saved run exactly.
- `tables/table2_luna.tex` and `.csv`: new GPT-6 Luna structured customer answer banks, replayed under exactly the same menus, prior, acceptance rule, inference, policies and ties.
- `reproduction/`: finite input catalogue fields, menus, frozen protocols, complete results, literal model replies and offline replay code.
- `paper/`: the source-only short-paper revision, with the two tables and robustness wording. Its theory, numbered equations and binary-channel experiment are unchanged. The PDF supplied before this addition is the preceding compiled version.
- `archive/nine_preference_research_records.tar.gz`: lossless earlier nine-preference research records, including the development search, confirmation, unsuccessful settings, sensitivity checks and independent audits. Historical paths identify the producing environment.

## Matched setup and results

Each source uses 576 menus of 16 products and all 64 binary preference profiles, weighted by the same frozen prior. The six questions concern sleeve length, pattern, neckline, fabric, wash care and budget. Dataset-specific labels and price cutoffs come from each development pool. Correctness means selecting an acceptable item, or selecting NO_BUY when no item is acceptable.

The Luna collection used eight fresh customer-only agent sessions requested as `gpt-6-luna`, reasoning `low`, with no parent conversation: four batches of sixteen profiles per source. A model supplies six A/B answers per shopper. Only the selected answer is revealed to the recommendation policy during replay. No products, policy names, scoring rules or outcomes appear in the customer cards. This is a structured answer-bank experiment, not a claim about natural multi-turn shopping behavior.

All 768 field answers agree with the prescribed cards. Consequently the two tables have identical values; their equality is an observed result, not a copied substitute for model calls. One infrastructure attempt failed before producing any response and was retried once. All eight completed responses are retained without correction.

| Dataset | Questions | Fixed order | Profile IG | Set IG | One-step DV |
|---|---:|---:|---:|---:|---:|
| Myntra | 3 | 68.06 | 69.79 | 76.43 | 84.89 |
| Myntra | 4 | 80.39 | 82.00 | 87.40 | 91.80 |
| Myntra | 5 | 95.02 | 94.45 | 95.53 | 97.45 |
| Amazon | 3 | 79.20 | 70.84 | 79.59 | 82.05 |
| Amazon | 4 | 85.43 | 80.50 | 85.89 | 88.17 |
| Amazon | 5 | 96.61 | 88.34 | 94.52 | 97.81 |

Values are acceptable-decision accuracy in percent. DV has the highest mean accuracy in these six fixed comparisons. The ordering among the three baselines varies. These runs condition on constructed preferences and previously available catalogue pools; the original split membership is retained.

## Offline reproduction

From the repository root, with Python 3, NumPy, pandas and requests installed:

```sh
python experiments/catalogue_robustness_20261105/reproduction/reproduce_tables.py
```

Add `--quick` for three menus per setting. The entry point reads bundled inputs and saved replies and makes no network or model requests. Full replay has been checked on all 576 menus in each included setting with zero difference from the recorded outputs. A separately implemented posterior-subset check of the new Luna replay agrees within 5.6e-16.

The source collector `reproduction/luna/luna_table2.py` retains its original local collection paths as provenance. Use the portable entry point above for replay. Confidence intervals in the results condition on fixed products, synthetic profiles and the observed answer banks; they resample menus within seed.

## Earlier work kept separate

The original 48-profile Luna study is preserved in `reproduction/luna/historical_luna_provenance.json`, traced to repository commit `6a7e00626147ab64a3ca74d8c542262680747adb`. It has 280 development cases and DV accuracies 72.1%, 87.1% and 94.6% at three, four and five questions. Its original protocol differs from this matched six-field check. Its single parser failure and the repository erratum are retained.

The nine-preference study and Qwen/Gemma interface checks remain in the accompanying records. All results, including weaker comparisons and task-selection history, keep their original interpretation. No existing repository file is replaced by this addition.
