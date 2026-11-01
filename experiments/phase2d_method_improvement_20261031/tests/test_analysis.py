"""Deterministic analysis fixtures; no data generation or scientific run."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from phase2d.analyze import (CONTRASTS, TIME_KEYS, analyze_rows, bootstrap_interval,
                            contrast_vectors, coverage, validate_coverage)
from phase2d.policy import POLICIES
from phase2d.runner import jobs
from phase2d.report import write_reports


def fixtures():
    cfg = json.loads((ROOT / "config.json").read_text())
    rows = []
    for job in jobs(cfg):
        for policy_number, policy in enumerate(POLICIES):
            censored = job["replicate"] == 0
            online = job["online_cap"] if censored else 32 + 16 * policy_number + 16 * job["replicate"]
            paid_types = 0 if policy.endswith("NoType") else 8
            costs = {"task": online - paid_types, "type": paid_types, "offline": 2 * job["M"]}
            history = [{"online": 8, "theta_errors": 1, "type_errors": 1, "p_error": -.2, "q_error": .1},
                       {"online": 16, "theta_errors": 2 if censored else 0, "type_errors": 0, "p_error": .1, "q_error": -.3}]
            rows.append({**job, "policy": policy, "online": online, "costs": costs,
                         "total_acquisition": sum(costs.values()), "complete": not censored, "censored": censored,
                         "exact": job["replicate"] not in (0, 1), "estimation_history": history,
                         "forced_tasks": 8, "fit": {"beta": job["R"] + 4},
                         "tracking_diagnostics": {"actual_minus_target": [0.] * (8 + len(job["partition"]))},
                         **{key: .1 * (1 + policy_number) for key in TIME_KEYS}})
    refs = [{"partition": part, "alpha": alpha, "K_no_type": 3., "K_with_type": 2., "K_oracle": 1.,
             "premium_regime": "positive"} for part in cfg["partitions"] for alpha in cfg["alphas"]]
    receipt = {"status": "completed", "costs_including_partial": {key: sum(r["costs"][key] for r in rows) for key in ("task", "type", "offline")},
               "seconds": 1., "evaluator_cpu_seconds": .1, "retries": 0}
    return rows, cfg, receipt, refs


class TestAnalysis(unittest.TestCase):
    def test_exact_expected_world_and_policy_coverage(self):
        rows, cfg, _, _ = fixtures()
        result = validate_coverage(rows, cfg)
        self.assertEqual((result["planned_worlds"], result["planned_trajectories"]), (64, 256))
        self.assertTrue(result["exact"])
        for broken in (rows[:-1], rows + [deepcopy(rows[0])]):
            with self.assertRaises(ValueError):
                validate_coverage(broken, cfg)
        broken = deepcopy(rows)
        broken[0]["R"] += 1
        self.assertFalse(coverage(broken, cfg)["exact"])
        with self.assertRaises(ValueError):
            validate_coverage(broken, cfg)

    def test_contrast_direction_pairing_and_interaction_identity(self):
        indices = [10, 11, 12, 13]
        values = {"Aligned-Full": [10, 20, 30, 40], "Aligned-NoType": [20, 50, 40, 70],
                  "D-RRC-Type": [30, 50, 70, 80], "D-RRC-NoType": [50, 100, 100, 120]}
        by_policy = {p: {i: {"online": v} for i, v in reversed(list(zip(indices, values[p])))} for p in POLICIES}
        vectors = contrast_vectors(by_policy, indices, 10)
        np.testing.assert_array_equal(vectors["task_without_type"], [3, 5, 6, 5])
        np.testing.assert_array_equal(vectors["remaining_type_enabled_advantage"], [2, 3, 4, 4])
        np.testing.assert_array_equal(vectors["interaction"], vectors["kl_type_benefit"] - vectors["simple_type_benefit"])
        np.testing.assert_array_equal(vectors["interaction"], vectors["remaining_type_enabled_advantage"] - vectors["task_without_type"])
        draws = np.random.default_rng(763401).integers(0, 4, size=(4000, 4))
        joint = {name: vector[draws].mean(axis=1) for name, vector in vectors.items()}
        np.testing.assert_allclose(joint["interaction"], joint["kl_type_benefit"] - joint["simple_type_benefit"], atol=1e-15)
        self.assertEqual(bootstrap_interval(vectors["interaction"], draws), np.quantile(joint["interaction"], [.025, .975]).tolist())

    def test_censoring_wrong_outputs_and_diagnostics_keep_full_denominators(self):
        rows, cfg, receipt, refs = fixtures()
        result = analyze_rows(rows, cfg, receipt, refs)
        self.assertEqual((len(result["summary"]), len(result["paired"]), len(result["diagnostics"])), (64, 80, 256))
        summary = result["summary"][0]
        matching = [r for r in rows if all(r[key] == summary[key] for key in ("partition", "alpha", "R", "policy"))]
        self.assertEqual((summary["n"], summary["completed"], summary["censored"], summary["wrong_certificates"]), (4, 3, 1, 1))
        self.assertEqual(summary["wrong_terminal_guesses"], 2)
        self.assertEqual(summary["wrong_fraction_all"], .25)
        self.assertEqual(summary["mean_restricted_online_over_R"], np.mean([r["online"] / r["R"] for r in matching]))
        self.assertNotEqual(summary["mean_restricted_online_over_R"], np.mean([r["online"] / r["R"] for r in matching if r["complete"]]))
        censored_diagnostics = [r for r in result["diagnostics"] if r["censored"]]
        self.assertEqual(len(censored_diagnostics), 64)
        self.assertTrue(all(r["last_theta_errors"] == 2 for r in censored_diagnostics))
        self.assertTrue(all(len(r["history_errors"]) == 2 for r in result["diagnostics"]))
        self.assertEqual(result["facts"]["charged_policy_offline_observations"],
                         4 * result["facts"]["unique_world_offline_observations"])
        self.assertEqual(result["facts"]["wrong_certificates"], 64)
        self.assertEqual(result["facts"]["trajectories"], 256)
        self.assertTrue(all(r["n_pairs"] == 4 for r in result["paired"]))

    def test_incomplete_and_short_censored_records_fail_closed(self):
        rows, cfg, receipt, refs = fixtures()
        failed = deepcopy(receipt)
        failed["status"] = "failed"
        with self.assertRaises(ValueError):
            analyze_rows(rows, cfg, failed, refs)
        short = deepcopy(rows)
        short[0]["online"] -= 1
        with self.assertRaisesRegex(ValueError, "Infrastructure truncation"):
            analyze_rows(short, cfg, receipt, refs)
        with self.assertRaises(ValueError):
            analyze_rows([r for r in rows if r["complete"]], cfg, receipt, refs)

    def test_report_labels_floating_scope_and_full_denominators(self):
        rows, cfg, receipt, refs = fixtures()
        result = analyze_rows(rows, cfg, receipt, refs)
        with tempfile.TemporaryDirectory(prefix="phase2d-analysis-contract-") as directory:
            write_reports(result, cfg, directory)
            ablation = (Path(directory) / "ABLATION_REPORT.md").read_text()
            diagnostics = (Path(directory) / "ESTIMATION_DIAGNOSTICS.md").read_text()
            self.assertIn("旧浮点停止规则", ablation)
            self.assertIn("64/256", ablation)
            self.assertIn("逐世界有序对比向量", ablation)
            self.assertIn("未按完成状态筛选", ablation)
            self.assertIn("相同路径/成本是构造结果", ablation)
            self.assertIn("不宣称其与浮点 Aligned-Full 逐位相同", ablation)
            self.assertIn("全部四策略", diagnostics)
            self.assertIn("不构成可相加的因果成本解释", diagnostics)


if __name__ == "__main__":
    unittest.main()
