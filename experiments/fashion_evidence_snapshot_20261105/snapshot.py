"""Export outcome-only historical evidence; no prompts, profiles or seller records."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = {
    "small_python": ("myntra_closed_loop_robustness_v01_20261104", "results/PAIRED_CASES.jsonl", "results/ROBUSTNESS_METRICS.json", "REPORT_ZH.md"),
    "development_python": ("myntra_full_dev_catalogue_v02_20261104", "results/PAIRED_CASES.jsonl", "results/CATALOGUE_METRICS.json", "REPORT_ZH.md"),
    "validation_python": ("myntra_heldout_confirmation_v01_20261104", "results/validation_reserved_PAIRED_CASES.jsonl", "results/ANALYSIS.json", "results/REPORT_ZH.md"),
    "test_python": ("myntra_heldout_confirmation_v01_20261104", "results/test_reserved_PAIRED_CASES.jsonl", "results/ANALYSIS.json", "results/REPORT_ZH.md"),
    "luna8": ("myntra_luna_policy_comparison_v01_20261105", "results/PAIRED_POLICY_TRACES.jsonl", "results/ANALYSIS.json", "results/REPORT_ZH.md"),
    "luna48": ("myntra_luna_48profile_policy_v01_20261105", "results/PAIRED_POLICY_TRACES.jsonl", "results/ANALYSIS.json", "results/REPORT_ZH.md"),
}
FIELDS = ["budget", "case_id", "profile_id", "menu_id", "method", "replicate", "prior_seed", "panel_id", "pool_index", "user_cohort", "stratum", "split", "exact_decision_correct", "answer_path_complete", "hard_constraint_violation", "false_purchase_case", "normalized_score_regret", "elicitation_units"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    manifest = {"purpose": "Historical outcome replay only; not new experiments", "source_files": {}, "exports": {}}
    for label, (folder, trace, metrics, report) in SOURCES.items():
        base = args.source_root / "experiments" / folder
        rows = []
        for line in (base / trace).read_text().splitlines():
            d = json.loads(line)
            rows.append({k: d[k] for k in FIELDS if k in d})
        payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
        dst = out / (label + "_outcomes.jsonl.gz")
        dst.write_bytes(gzip.compress(payload, mtime=0))
        for rel in [trace, metrics, report, "config.json"]:
            src = base / rel
            if src.exists():
                manifest["source_files"][f"experiments/{folder}/{rel}"] = sha(src)
        (out / (label + "_source_metrics.json")).write_bytes((base / metrics).read_bytes())
        # Reports remain exact archival bytes; ERRATUM.md supersedes one diagnosis.
        (out / (label + "_source_report.md")).write_bytes((base / report).read_bytes())
        manifest["exports"][label] = {"trace": str(dst.relative_to(HERE)), "rows": len(rows), "sha256": sha(dst)}
    source_engine = args.source_root / "experiments/myntra_luna_48profile_policy_v01_20261105/engine.py"
    (HERE / "fashion_engine_reference.py").write_bytes(source_engine.read_bytes())
    manifest["source_files"]["experiments/myntra_luna_48profile_policy_v01_20261105/engine.py"] = sha(source_engine)
    manifest["engine_note"] = "Archived source reference; its original config/environment are not bundled. Report replay is standalone via analyze.py."
    (HERE / "SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
