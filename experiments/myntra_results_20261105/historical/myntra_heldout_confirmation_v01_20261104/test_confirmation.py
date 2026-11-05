"""Pre-freeze structural and evaluator tests; never run a held-out policy."""
from __future__ import annotations

import collections
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_confirmation as run


class HeldoutConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy, cls.env = run.DEV.load_engine()
        cls.env.evaluate_python = run.evaluate_python_oov
        cls.env.evaluate_sql = run.evaluate_sql_oov
        cls.source, cls.dev_vocab, cls.audit = run.audit_source(cls.env)

    def test_frozen_splits_and_product_families(self):
        self.assertEqual(self.audit["split_counts"], {
            "development": 338, "validation_reserved": 78, "test_reserved": 55})
        self.assertEqual(self.audit["cross_split_leakage_groups"], 0)
        for split in run.CONFIG["splits"]:
            menus, _, provenance = run.build_menus(self.source, split)
            ids = [item["product_id"] for menu in menus for item in menu["items"]]
            expected = {row["product_id"] for row in self.source if row["split"] == split}
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(set(ids), expected)
            owners = {}
            for menu_id, record in provenance.items():
                for group in record["leakage_group_ids"]:
                    self.assertNotIn(group, owners)
                    owners[group] = menu_id

    def test_oov_neutral_evaluator_matches_independent_sql(self):
        profile = self.env.generate_profiles(self.dev_vocab["0"], 0,
                    {**self.env.read(self.env.BASE / "config.json"),
                     "seed_root": "heldout-oov-evaluator-fixture", "profiles_per_pool": 1})[0]
        source_item = next(x for x in self.source if x["split"] == "development"
                           and x["gender"] == "Men" and x["category"] == "Kurtas")
        item = {"product_id": source_item["product_id"],
                "attributes": {field: source_item["attributes"][field]["value"] for field in run.FIELDS}}
        item["attributes"]["fabric"] = "__UNSEEN_FIXTURE_LABEL__"
        py = run.evaluate_python_oov([item], profile)
        sql = run.evaluate_sql_oov([item], profile)
        self.assertEqual(py, sql)
        expected = sum(profile["soft"]["scores"][field].get(item["attributes"][field], 0)
                       for field in run.FIELDS)
        self.assertEqual(py["scores_by_product"][item["product_id"]], expected)

    def test_reserved_attribute_support_is_audited_without_method_scores(self):
        self.assertFalse(self.audit["method_outcomes_computed"])
        expected = {
            "validation_reserved": {
                ("Women/Kurtas", "neckline"): ["scoop neck"],
                ("Women/Kurtas", "fabric"): ["art silk", "crepe"],
                ("Women/Kurtis", "fabric"): ["pure silk"],
                ("Women/Tops", "neckline"): ["keyhole neck"],
            },
            "test_reserved": {
                ("Women/Dresses", "fabric"): ["modal"],
                ("Women/Kurtis", "pattern"): ["yoke design"],
            },
        }
        for split in run.CONFIG["splits"]:
            observed = {}
            for pool, fields in self.audit["unseen_values_by_split_pool_field"][split].items():
                for field, values in fields.items():
                    if values:
                        observed[(pool, field)] = values
            self.assertEqual(observed, expected[split])

    def test_prepared_profiles_are_independent_and_development_supported(self):
        for split in run.CONFIG["splits"]:
            for cohort, seed in run.CONFIG["user_cohort_seed_roots"][split].items():
                self.assertNotEqual(seed, run.CONFIG["prior_seed_root"])
        self.assertEqual(run.CONFIG["budgets"], list(range(7)))
        self.assertEqual(run.CONFIG["primary_budget"], 5)
        self.assertEqual(run.CONFIG["model_calls"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
