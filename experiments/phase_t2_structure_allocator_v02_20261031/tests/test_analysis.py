"""Synthetic evidence only; no held-out files or models are opened."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from t2.analyze import (
    CoverageError, TIMINGS, OFFLINE_MODELS, aggregate, clustered_ratio,
    computational_report, evaluation_report, render_figures, validate_coverage,
    world_mean, execution_accounting, verify_analysis_freeze, analyze,
)


def fixture():
    methods = ["Fused-Original", "Native-Fused-Original", "T1-MLP", "T2-MLP", "DeepSets-KL", "DeepSets-Info", "Warm-KL"]
    config = {
        "evaluation": {"splits": ["id"], "worlds_per_split": 2, "risks": [16, 64, 256],
                       "extra_variable_worlds": 1, "extra_variable_R": 64, "methods": methods},
        "data": {"splits": ["id_test"], "test_worlds_per_split": 2, "snapshot_times": [4, 16, 32, 64, 256, 1024]},
        "analysis": {"bootstrap_resamples": 128, "bootstrap_seed": 731102, "scope": "synthetic fixture only"},
        "go_targets": {"query_ratio_upper": 1.05, "planning_speedup_lower": 2},
    }
    budgets = [8, 16]
    plan = {"expected_paths": [], "expected_offline": []}
    paths, offline = [], []
    for split, worlds, risks in (("eval_id", ["main-a", "main-b"], [16, 64, 256]),
                                ("eval_variable", ["variable-a"], [64])):
        for wi, world in enumerate(worlds):
            for R in risks:
                for method in methods:
                    identity = {"world_id": world, "split": split, "R": R, "method": method}
                    status = "not_applicable" if split == "eval_variable" and method == "T1-MLP" else "completed"
                    plan["expected_paths"].append({**identity, "status": status})
                    if status == "not_applicable":
                        paths.append({**identity, "status": status})
                        continue
                    online = 100*(wi+1)
                    compute = 10. if method == "Fused-Original" else 2.
                    timings = {key: .1 for key in TIMINGS}
                    timings.update(estimation=compute*.4, planning=compute*.5, inference=compute*.1, wall=compute+1, cpu=compute+1)
                    readings = [{"budget": b, "effective_online": min(online, b), "guess_exact": True,
                                 "costs": {"task": min(online, b), "type": 0, "offline": 2},
                                 "total_acquisition": min(online, b)+2, "absorbed": online <= b} for b in budgets]
                    paths.append({**identity, "status": status, "online": online,
                                  "costs": {"task": online, "type": 0, "offline": 2}, "total_acquisition": online+2,
                                  "certified": True, "certified_exact": True, "abstained": False,
                                  "final_guess_exact": True, "readouts": readings, "timings": timings})
    for wi, world in enumerate(("offline-a", "offline-b")):
        d = 4 if wi == 0 else 3
        for position in range(6):
            for model in OFFLINE_MODELS:
                status = "not_applicable" if d != 4 and model == "T1-MLP" else "completed"
                identity = {"world_id": world, "split": "id_test", "position": position, "model": model, "state_d": d, "status": status}
                plan["expected_offline"].append(identity.copy())
                row = identity.copy()
                if status == "completed":
                    row.update(allocation_l1=.1*(wi+1), forward_kl=.05*(wi+1), teacher_K=20.,
                               radial_cost=22., relative_regret=.1, radial_infinite=False, inference_wall_seconds=.002)
                offline.append(row)
    return paths, offline, plan, config, budgets


class AnalysisTests(unittest.TestCase):
    def test_exact_coverage_and_variable_dimension_exclusion(self):
        paths, offline, plan, config, budgets = fixture()
        result = aggregate(paths, offline, plan, config, budgets)
        coverage = result["coverage"]
        self.assertEqual(coverage["path_records_expected"], 49)
        self.assertEqual(coverage["main_applicable"], 42)
        self.assertEqual(coverage["variable_applicable"], 6)
        self.assertEqual(coverage["readout_cells_observed"], 96)
        self.assertEqual(coverage["offline_status_counts"], {"completed": 42, "not_applicable": 6})
        paired = next(r for r in result["paired_summary"] if r["method"] == "DeepSets-Info" and r["split"] == "main_pooled" and r["R"] == "pooled_R")
        self.assertEqual(paired["expected_pairs"], 6)
        self.assertEqual(paired["world_clusters"], 2)
        self.assertAlmostEqual(paired["inclusive_compute_speedup"]["point"], 5.)
        self.assertTrue(paired["all_engineering_flags_pass"])
        self.assertIn("manual_review", paired["decision"])
        json.dumps(result, allow_nan=False)

    def test_missing_duplicate_and_unexpected_keys_fail_closed(self):
        paths, offline, plan, config, budgets = fixture()
        for altered in (paths[:-1], paths + [deepcopy(paths[0])], paths + [{**paths[0], "world_id": "unexpected"}]):
            with self.assertRaises(CoverageError):
                validate_coverage(altered, offline, plan, config, budgets)
        with self.assertRaises(CoverageError):
            validate_coverage(paths, offline[:-1], plan, config, budgets)
        changed_plan = deepcopy(plan)
        changed_plan["expected_paths"] = changed_plan["expected_paths"][:-1]
        with self.assertRaises(CoverageError):
            validate_coverage(paths[:-1], offline, changed_plan, config, budgets)

    def test_missing_readout_and_cost_inconsistency_fail_closed(self):
        paths, offline, plan, config, budgets = fixture()
        for mutate in (lambda r: r["readouts"].pop(), lambda r: r.update(total_acquisition=999),
                       lambda r: r["readouts"][0].update(effective_online=7)):
            changed = deepcopy(paths)
            mutate(changed[0])
            with self.assertRaises(CoverageError):
                validate_coverage(changed, offline, plan, config, budgets)

    def test_failed_pair_preserves_denominator_and_disables_ratio(self):
        paths, offline, plan, config, budgets = fixture()
        index = next(i for i, row in enumerate(paths) if row["method"] == "DeepSets-Info")
        paths[index] = {key: paths[index][key] for key in ("world_id", "split", "R", "method")}
        paths[index].update(status="failed", readouts=[])
        result = aggregate(paths, offline, plan, config, budgets)
        paired = next(r for r in result["paired_summary"] if r["method"] == "DeepSets-Info" and r["split"] == "main_pooled" and r["R"] == "pooled_R")
        self.assertEqual(paired["expected_pairs"], 6)
        self.assertEqual(paired["complete_pairs"], 5)
        self.assertFalse(paired["paired_metrics_available"])
        self.assertNotIn("online_restricted_cost_ratio", paired)
        cell = next(r for r in result["fixed_budget_summary"] if r["method"] == "DeepSets-Info" and r["split"] == "eval_id" and r["R"] == 16 and r["budget"] == 8)
        self.assertEqual(cell["expected_applicable"], 2)
        self.assertEqual(cell["observed"], 1)
        self.assertIsNone(cell["exact_rate"])
        self.assertEqual(cell["exact_yield_expected"], .5)

    def test_abstention_cost_retained_and_strict_gate_fails(self):
        paths, offline, plan, config, budgets = fixture()
        row = next(r for r in paths if r["method"] == "DeepSets-Info")
        row.update(online=400, costs={"task": 400, "type": 0, "offline": 2}, total_acquisition=402,
                   certified=False, certified_exact=None, abstained=True, final_guess_exact=False)
        result = aggregate(paths, offline, plan, config, budgets)
        paired = next(r for r in result["paired_summary"] if r["method"] == "DeepSets-Info" and r["split"] == "main_pooled" and r["R"] == "pooled_R")
        self.assertAlmostEqual(paired["online_restricted_cost_ratio"]["point"], 1200/900)
        self.assertFalse(paired["all_engineering_flags_pass"])
        self.assertFalse(paired["engineering_flags"]["all_candidate_and_teacher_paths_certified_correctly_without_abstention"])

    def test_cluster_resampling_does_not_treat_repeated_risks_as_worlds(self):
        original = clustered_ratio(["a", "b", "c"], [1., 4., 9.], [2., 3., 4.], resamples=256)
        repeated = clustered_ratio([w for w in ("a", "b", "c") for _ in range(3)],
                                   [x for x in (1., 4., 9.) for _ in range(3)],
                                   [x for x in (2., 3., 4.) for _ in range(3)], resamples=256)
        self.assertEqual(original["point"], repeated["point"])
        self.assertEqual(original["descriptive_bootstrap_range"], repeated["descriptive_bootstrap_range"])
        self.assertEqual(repeated["world_clusters"], 3)
        self.assertEqual(repeated["paired_records"], 9)

    def test_offline_infinity_and_within_world_average_are_preserved(self):
        paths, offline, plan, config, budgets = fixture()
        for row in offline:
            if row["model"] == "DeepSets-Info" and row["world_id"] == "offline-a" and row["position"] == 0:
                row.update(radial_cost=None, relative_regret=None, radial_infinite=True)
        result = aggregate(paths, offline, plan, config, budgets)
        summary = next(r for r in result["offline_summary"] if r["model"] == "DeepSets-Info" and r["scope"] == "all_applicable")
        self.assertEqual(summary["completed_states"], 12)
        self.assertEqual(summary["world_clusters"], 2)
        self.assertEqual(summary["radial_infinite_states"], 1)
        self.assertTrue(summary["metrics"]["relative_regret"]["point"]["infinite"])
        self.assertIsNone(summary["metrics"]["relative_regret"]["point"]["value"])
        self.assertAlmostEqual(summary["metrics"]["allocation_l1"]["point"]["value"], .15)
        self.assertEqual(summary["metrics"]["relative_regret"]["infinite_worlds"], 1)
        json.dumps(result, allow_nan=False)
        infinity = world_mean([float("inf"), 1.], resamples=128, seed=731102)
        self.assertTrue(infinity["descriptive_bootstrap_range"][1]["infinite"])

    def test_radial_null_without_flag_and_zero_teacher_k_are_rejected(self):
        paths, offline, plan, config, budgets = fixture()
        for change in ({"radial_cost": None}, {"teacher_K": 0}, {"relative_regret": 100}):
            altered = deepcopy(offline)
            altered[0].update(change)
            with self.assertRaises(CoverageError):
                validate_coverage(paths, altered, plan, config, budgets)

    def test_reports_and_both_figure_formats_from_synthetic_data(self):
        paths, offline, plan, config, budgets = fixture()
        result = aggregate(paths, offline, plan, config, budgets)
        text = evaluation_report(result)
        self.assertIn("Warm-KL", text)
        self.assertIn("Native-Fused-Original", text)
        self.assertIn("restricted", text)
        self.assertIn("manual review required", text)
        self.assertIn("training", computational_report(result, {"training_execution": {"outer_wall_seconds": 12.}}))
        with tempfile.TemporaryDirectory(prefix="t2-analysis-unit-") as directory:
            outputs = render_figures(result, Path(directory))
            self.assertEqual(len(outputs), 4)
            self.assertEqual(sum(path.endswith(".pdf") for path in outputs), 2)
            self.assertTrue(all(Path(path).stat().st_size > 500 for path in outputs))

    def test_execution_accounting_does_not_add_nested_training_twice(self):
        rows = execution_accounting({"training_execution": {"status": "completed", "outer_wall_seconds": 12.,
                                    "outer_cpu_seconds": 11., "models": {"mlp": {"outer_wall_seconds": 3., "outer_cpu_seconds": 2.}}},
                                     "evaluation_execution": {"status": "completed", "outer_wall_seconds": 20., "outer_parent_cpu_seconds": 1.}})
        training = next(r for r in rows if r["stage"] == "Three-fit training total")
        self.assertEqual(training["outer_wall_seconds"], 12.)
        model = next(r for r in rows if r["stage"] == "mlp")
        self.assertIn("do_not_add_again", model["accounting_scope"])
        evaluation = next(r for r in rows if r["stage"] == "Evaluation outer process/pool")
        self.assertIn("excludes worker", evaluation["cpu_scope"])

    def test_analysis_freeze_hashes_source_before_results_are_opened(self):
        with tempfile.TemporaryDirectory(prefix="t2-analysis-freeze-unit-") as directory:
            root = Path(directory)
            with self.assertRaises(CoverageError):
                verify_analysis_freeze(root)
            files = {}
            for name in ("t2/analyze.py", "tests/test_analysis.py"):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic source\n")
                files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            (root/"analysis_freeze.json").write_text(json.dumps({"files": files, "dependencies": {}}))
            self.assertEqual(verify_analysis_freeze(root)["status"], "PASS")
            (root/"t2/analyze.py").write_text("modified\n")
            with self.assertRaises(CoverageError):
                verify_analysis_freeze(root)

    def test_launcher_retains_failure_receipt_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="t2-analysis-launch-unit-") as directory:
            root = Path(directory)
            with self.assertRaises(CoverageError):
                analyze(root)
            receipt_path = root/"artifacts/analysis/execution.json"
            original = receipt_path.read_text()
            receipt = json.loads(original)
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["model_calls"], 0)
            self.assertEqual(receipt["simulation_worlds"], 0)
            self.assertFalse(receipt["automatic_retry"])
            for key in ("python_version", "numpy_version", "matplotlib_version"):
                self.assertTrue(receipt[key])
            for key in ("outer_wall_seconds", "outer_cpu_seconds"):
                self.assertGreaterEqual(receipt[key], 0)
            with self.assertRaises(FileExistsError):
                analyze(root)
            self.assertEqual(receipt_path.read_text(), original)


if __name__ == "__main__":
    unittest.main()
