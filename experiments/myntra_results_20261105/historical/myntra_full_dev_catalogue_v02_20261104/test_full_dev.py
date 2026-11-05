#!/usr/bin/env python3
"""Construction tests for full development-catalogue coverage."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_full_dev as run


class FullDevelopmentCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy, cls.env = run.load_engine()
        cls.all_rows, cls.development, cls.reserved = run.audit_source(cls.env)
        cls.menus, cls.vocab, cls.provenance = run.build_menus(cls.env, cls.development)

    def test_source_scope_and_all_core_fields(self):
        self.assertEqual(len(self.all_rows), 471)
        self.assertEqual((len(self.development), len(self.reserved)), (338, 133))
        self.assertTrue(all(row["split"] == "development" for row in self.development))
        self.assertTrue(all(row["split"] != "development" for row in self.reserved))
        self.assertTrue(all(row["attributes"][field]["status"] == "reported"
                            for row in self.development for field in run.FIELDS))

    def test_full_development_item_coverage_exactly_once(self):
        ids = [item["product_id"] for menu in self.menus for item in menu["items"]]
        expected = {row["product_id"] for row in self.development}
        self.assertEqual(len(ids), 338)
        self.assertEqual(len(set(ids)), 338)
        self.assertEqual(set(ids), expected)
        self.assertEqual(len(self.menus), 35)

    def test_leakage_families_are_not_split_across_menus(self):
        owner = {}
        for menu_id, record in self.provenance.items():
            for group in record["leakage_group_ids"]:
                self.assertNotIn(group, owner)
                owner[group] = menu_id
        self.assertEqual(len(owner), 326)

    def test_menu_sizes_and_attribute_vocabularies(self):
        sizes = sorted(len(menu["items"]) for menu in self.menus)
        self.assertEqual(sizes.count(10), 30)
        self.assertEqual(sizes.count(9), 1)
        self.assertEqual(sizes.count(8), 3)
        self.assertEqual(sizes.count(5), 1)
        for pool, vocab in self.vocab.items():
            self.assertEqual(set(vocab), set(run.FIELDS))
            self.assertTrue(all(len(values) >= 2 for values in vocab.values()), pool)
        for menu in self.menus:
            for item in menu["items"]:
                self.assertEqual(set(item), {"product_id", "attributes"})
                self.assertEqual(set(item["attributes"]), set(run.FIELDS))

    def test_two_fresh_cohorts_and_independent_prior_seed(self):
        a = run.generate_profiles(self.env, self.vocab, "A", run.CONFIG["user_cohorts"]["A"], 4)
        b = run.generate_profiles(self.env, self.vocab, "B", run.CONFIG["user_cohorts"]["B"], 4)
        prior = run.generate_profiles(self.env, self.vocab, "C", run.CONFIG["prior_seed_root"], 8)
        self.assertEqual((len(a), len(b), len(prior)), (24, 24, 48))
        self.assertEqual(len({x["profile_id"] for x in a + b}), 48)
        self.assertTrue(any(self.env.private_preferences(a[i]) != self.env.private_preferences(b[i]) for i in range(24)))
        self.assertNotEqual(run.CONFIG["prior_seed_root"], run.CONFIG["user_cohorts"]["A"])
        self.assertNotEqual(run.CONFIG["prior_seed_root"], run.CONFIG["user_cohorts"]["B"])

    def test_independent_evaluators_agree_for_each_profile_and_menu(self):
        profile = run.generate_profiles(self.env, self.vocab, "A", run.CONFIG["user_cohorts"]["A"], 4)[0]
        for menu in [m for m in self.menus if m["pool_index"] == profile["pool_index"]]:
            self.assertEqual(self.env.evaluate_python(menu["items"], profile),
                             self.env.evaluate_sql(menu["items"], profile), menu["menu_id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
