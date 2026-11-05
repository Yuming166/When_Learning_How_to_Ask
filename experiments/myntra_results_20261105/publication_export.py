"""Build an explicit, provenance-bound public subset without editing source runs."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import shutil

SOURCE_NAMES = [
    "myntra_catalogue_v01_20261104", "myntra_preference_dev_v01_20261104",
    "myntra_closed_loop_dev_v01_20261104", "myntra_closed_loop_robustness_v01_20261104",
    "myntra_full_dev_catalogue_v01_20261104", "myntra_full_dev_catalogue_v02_20261104",
    "myntra_heldout_confirmation_v01_20261104", "myntra_luna_simulator_v01_20261104",
    "myntra_luna_policy_comparison_v01_20261105", "myntra_luna_48profile_policy_v01_20261105",
    "myntra_deepseek_48profile_policy_v01_20261105", "myntra_deepseek_48profile_policy_v02_20261105",
    "myntra_glm53_48profile_policy_v01_20261105", "myntra_glm53_48profile_policy_v02_20261105",
    "myntra_python_mechanism_ablation_v01_20261105", "myntra_llm_mechanism_ablation_v01_20261105",
]
PY = "myntra_python_mechanism_ablation_v01_20261105"
LLM = "myntra_llm_mechanism_ablation_v01_20261105"
MODEL_SOURCES = {"luna": "myntra_luna_48profile_policy_v01_20261105",
                 "deepseek": "myntra_deepseek_48profile_policy_v02_20261105",
                 "glm": "myntra_glm53_48profile_policy_v02_20261105"}
FIELDS = ["split", "model", "case_id", "profile_id", "pool_index", "user_cohort", "gender", "category", "method", "budget",
          "exact_decision_correct", "purchase_recall_case", "no_buy_correct_case", "false_purchase_case", "hard_constraint_violation",
          "score_regret", "normalized_score_regret", "elicitation_units", "dialogue_turns", "answer_path_complete",
          "query_sequence", "valid_query_sequence", "failed_query_action", "selected_action_code"]
BOOLEAN_FIELDS = ["exact_decision_correct", "purchase_recall_case", "no_buy_correct_case", "false_purchase_case", "hard_constraint_violation", "answer_path_complete"]


def read(p):
    return json.loads(Path(p).read_text())


def rows(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def extract_function(path, name):
    source = path.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    return "".join(source.splitlines(keepends=True)[node.lineno-1:node.end_lineno]) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    source, target = args.source.resolve(), args.destination.resolve()
    target.mkdir(parents=True, exist_ok=False)
    entries, derived = [], []

    def copy_file(src, rel):
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        entries.append({"path": str(rel), "source_path": str(src), "source_sha256": digest(src), "published_sha256": digest(dest)})

    for name in SOURCE_NAMES:
        base = source / "experiments" / name
        for p in sorted(base.iterdir()):
            if p.is_file() and p.suffix in {".py", ".md", ".json", ".txt"}:
                copy_file(p, Path("historical") / name / p.name)
        result_dir = base / "results"
        if result_dir.is_dir():
            for p in sorted(result_dir.iterdir()):
                if p.is_file() and p.suffix in {".json", ".csv", ".png", ".pdf", ".md"}:
                    copy_file(p, Path("historical") / name / "results" / p.name)
    for filename in ("engine.py", "environment.py", "config.json"):
        copy_file(source / "experiments" / MODEL_SOURCES["glm"] / filename, Path("code") / filename)
    copy_file(source / "experiments" / MODEL_SOURCES["glm"] / "replay.py", Path("code/legacy_replay.py"))
    copy_file(source / "experiments" / PY / "config.json", Path("python_config.json"))
    copy_file(source / "experiments" / LLM / "config.json", Path("llm_config.json"))
    copy_file(source / "experiments" / LLM / "PREPARED.json", Path("llm_panel_metadata.json"))

    # Whitelist-derived evaluation records: no catalogue, preference maps, content,
    # target sets, URLs or provider identifiers are copied into these CSV files.
    python_rows = rows(source / "experiments" / PY / "results/PAIRED_CASES.jsonl")
    llm_rows = []
    for model, name in MODEL_SOURCES.items():
        for r in rows(source / "experiments" / name / "results/PAIRED_POLICY_TRACES.jsonl"):
            llm_rows.append({**r, "model": model})
    llm_rows += [r for r in rows(source / "experiments" / LLM / "results/PAIRED_CASES.jsonl") if r["method"] == "decision_value_initial_order"]
    cases = {c["case_id"]: c for c in rows(source / "experiments" / LLM / "artifacts/input/cases.jsonl")}
    for kind, source_rows in (("python", python_rows), ("llm", llm_rows)):
        p = target / "records" / f"{kind}.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        seen = set()
        with p.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for raw in source_rows:
                c = cases[raw["case_id"]] if kind == "llm" else raw
                row = {k: raw.get(k, c.get(k, "")) for k in FIELDS}
                row["split"] = raw.get("split", "development")
                row["model"] = raw.get("model", "python")
                row["answer_path_complete"] = raw.get("answer_path_complete", True)
                for k in BOOLEAN_FIELDS:
                    row[k] = int(bool(row[k]))
                row["query_sequence"] = ";".join(raw["query_sequence"])
                row["valid_query_sequence"] = ";".join(raw.get("valid_query_sequence", raw["query_sequence"]))
                row["failed_query_action"] = raw.get("failed_query_action") or ""
                action = raw["selected_action"]
                row["selected_action_code"] = "NO_BUY" if action == "NO_BUY" else "ITEM_" + hashlib.sha256((raw["case_id"] + "|" + action).encode()).hexdigest()[:16]
                key = tuple(row[k] for k in ("split", "model", "case_id", "method", "budget"))
                if key in seen:
                    raise RuntimeError("Duplicate exported evaluation key")
                seen.add(key)
                writer.writerow(row)
        expected = 25760 if kind == "python" else 29400
        if len(seen) != expected:
            raise RuntimeError(f"Unexpected {kind} export denominator")
        derived.append({"path": str(p.relative_to(target)), "rows": len(seen), "published_sha256": digest(p),
                        "transformation": "explicit numerical-field whitelist; original outcomes preserved; case-local item hashes"})

    py_stats = source / "experiments" / PY / "ablation_statistics.py"
    llm_stats = source / "experiments" / LLM / "analysis.py"
    replay_source = source / "experiments" / LLM / "experiment.py"
    extractions = [
        ("statistics_python.py", py_stats, ["cluster_arrays", "bootstrap", "method_curves"], "from __future__ import annotations\nimport collections\nimport hashlib\nimport numpy as np\n"),
        ("statistics_llm.py", llm_stats, ["joint_bootstrap", "curves", "diagnostics"], "from __future__ import annotations\nimport collections\nimport hashlib\nfrom types import SimpleNamespace\nimport numpy as np\nex = SimpleNamespace(STATIC='decision_value_initial_order')\n"),
        ("policy_replay.py", replay_source, ["initial_rank", "predict_cached", "replay_path"],
         "from __future__ import annotations\nimport json\nimport sys\nfrom pathlib import Path\nHERE = Path(__file__).resolve().parent\nsys.path.insert(0, str(HERE/'code'))\nimport engine\nimport environment as ref\nimport legacy_replay\nCFG = json.loads((HERE/'llm_config.json').read_text())\nSTATIC = 'decision_value_initial_order'\n"),
    ]
    for rel, original, functions, header in extractions:
        body = header + "\n" + "\n\n".join(extract_function(original, name) for name in functions)
        p = target / rel
        p.write_text(body)
        derived.append({"path": rel, "source_path": str(original), "source_sha256": digest(original),
                        "published_sha256": digest(p), "transformation": "byte-identical extracted function bodies with public relative-path import wrapper",
                        "functions": functions})

    # The original current toy tests are reused, replacing only the private input
    # coverage test with tests of the published numerical projection.
    original_tests = source / "experiments" / LLM / "test_ablation.py"
    parsed = ast.parse(original_tests.read_text())
    replay_class = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == "ReplayTests")
    methods = [n for n in replay_class.body if isinstance(n, ast.FunctionDef) and n.name != "test_source_coverage_and_shared_profile_identity"]
    source_lines = original_tests.read_text().splitlines(keepends=True)
    replay_body = "class ReplayTests(unittest.TestCase):\n" + "\n".join("".join(source_lines[n.lineno-1:n.end_lineno]) for n in methods)
    content = "import copy\nimport random\nimport unittest\nimport policy_replay as ex\nimport statistics_llm as analysis\nfrom reproduce import load_records, check_coverage\n\n"
    content += "\n\n".join(extract_function(original_tests, n) for n in ("fixture", "bank_for", "legacy"))
    content += "\n\n" + replay_body + "\n\n" + extract_function(original_tests, "stats_fixture") + "\n\n" + extract_function(original_tests, "JointStatisticsTests")
    content += '''

class PublicRecordTests(unittest.TestCase):
    def test_exact_key_coverage_and_known_primary_counts(self):
        py, llm = load_records('python'), load_records('llm')
        self.assertEqual(check_coverage(py, llm)['python_rows'], 25760)
        expected = {'luna': (265,225), 'deepseek': (259,221), 'glm': (255,215)}
        for model, values in expected.items():
            actual = tuple(sum(r['exact_decision_correct'] for r in llm if r['model']==model and r['method']==method and r['budget']==5) for method in ('decision_value','decision_value_initial_order'))
            self.assertEqual(actual, values)

    def test_projection_has_no_model_text_or_catalogue_fields(self):
        forbidden = {'content','reasoning_content','attributes','scores','hard','soft','api_key','response_id','reference_target_set'}
        for kind in ('python','llm'):
            records = load_records(kind)
            self.assertTrue(all(not (set(row) & forbidden) for row in records))


if __name__ == '__main__':
    unittest.main(verbosity=2)
'''
    (target / "test_public_release.py").write_text(content)
    derived.append({"path": "test_public_release.py", "source_path": str(original_tests), "source_sha256": digest(original_tests),
                    "published_sha256": digest(target / "test_public_release.py"),
                    "transformation": "reuse 8 original toy tests unchanged; replace private-bank coverage with 2 public-projection tests"})
    copy_file(Path(__file__).resolve(), Path("publication_export.py"))
    write(target / "SOURCE_MANIFEST.json", {"scope": "explicit source/report subset plus derived numerical evaluation projection",
          "source_files": entries, "derived_files": derived,
          "original_freezes_are_historical_provenance_not_public_completeness_receipts": True})
    write(target / "EXCLUSIONS.json", {"excluded": [
        {"class": "raw and derived merchandise catalogue, attributes, source pages and images", "reason": "existing dataset-card redistribution boundary; keep local"},
        {"class": "private preference/profile banks, priors, evaluator references and request prompts", "reason": "not needed for numerical-statistics reproduction; full strategy replay needs separately supplied inputs"},
        {"class": "raw model responses, reasoning streams, CLI session events, HTTP headers, errors and provider IDs", "reason": "no raw session or provider material in the public projection"},
        {"class": "raw paired JSONL trajectories", "reason": "publish only an allow-listed numerical CSV projection; omit product IDs/target sets and response content"},
        {"class": "credentials, caches, environments, downloads and runtime logs", "reason": "outside publication scope"}],
        "positive_and_negative_outcomes_retained": True,
        "earlier_failed_screens_and_partial_transport_runs_retained_in_historical_aggregates": True})
    print(json.dumps({"copied_source_files": len(entries), "derived_files": len(derived), "destination": str(target)}))


if __name__ == "__main__":
    main()
