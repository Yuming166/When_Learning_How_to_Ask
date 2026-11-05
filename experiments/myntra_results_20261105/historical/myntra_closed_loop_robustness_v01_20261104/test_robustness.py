#!/usr/bin/env python3
"""Protocol and data-generation checks; no model calls."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_robustness as run


class RobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = run.load_module("test_frozen_engine", run.PRIMARY / "engine.py")
        cls.env = cls.policy.load_environment(run.SOURCE)

    def test_four_distinct_seed_roots(self):
        roots = list(run.CONFIG["cohorts"].values()) + list(run.CONFIG["prior_seeds"].values())
        self.assertEqual(len(roots), len(set(roots)))

    def test_independent_cohorts_keep_all_profiles(self):
        a = run.make_cohort(self.env, "A")
        b = run.make_cohort(self.env, "B")
        self.assertEqual((len(a), len(b)), (12, 12))
        self.assertEqual({p["pool_index"] for p in a}, {0, 1, 2})
        self.assertEqual({p["pool_index"] for p in b}, {0, 1, 2})
        by_local = {p["profile_id"].split("-", 1)[1]: p for p in a}
        by_local_b = {p["profile_id"].split("-", 1)[1]: p for p in b}
        self.assertEqual(set(by_local), set(by_local_b))
        self.assertTrue(any(self.env.private_preferences(by_local[k]) != self.env.private_preferences(by_local_b[k]) for k in by_local))

    def test_prior_banks_are_independent_and_counted(self):
        a = run.make_prior(self.env, "A", 32)
        b = run.make_prior(self.env, "B", 32)
        self.assertEqual({pool: len(rows) for pool, rows in a.items()}, {0: 32, 1: 32, 2: 32})
        self.assertEqual({pool: len(rows) for pool, rows in b.items()}, {0: 32, 1: 32, 2: 32})
        self.assertNotEqual(self.env.private_preferences(a[0][0]), self.env.private_preferences(b[0][0]))

    def test_smoke_case_ids_map_to_frozen_menus(self):
        menus = run.frozen_menus(self.policy)
        cases = run.cases_for(run.make_cohort(self.env, "A"), menus, set(run.CONFIG["smoke_case_ids"]))
        self.assertEqual(len(cases), 2)
        self.assertEqual({case[0] for case in cases}, set(run.CONFIG["smoke_case_ids"]))

    def test_source_catalogue_is_frozen(self):
        source = run.SOURCE_EXP / "artifacts/input/catalogue_strict.jsonl"
        self.assertEqual(run.sha256(source), run.CONFIG["source_catalogue_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
