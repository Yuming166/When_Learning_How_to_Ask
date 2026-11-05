"""Independent edge-case checks before generating any new panel outcomes."""
from __future__ import annotations

import copy
import random
import sys
import unittest

import experiment as exp
import ablation_statistics as stats


def toy_fixture(env):
    attributes = {"neckline": ["round", "v"], "sleeve_length": ["short", "long"],
                  "fabric": ["cotton", "silk"], "wash_care": ["machine wash", "dry clean"],
                  "pattern": ["solid", "print"]}
    menu = {"menu_id": "toy", "items": [{"product_id": pid,
            "attributes": {f: v[j] for f, v in attributes.items()}} for j, pid in enumerate(("A", "B"))]}
    rng = random.Random(19)
    priors = []
    for i in range(16):
        priors.append({"hard": {"allowed_care_labels": attributes["wash_care"][:], "excluded_fabric_labels": []},
            "soft": {"scores": {f: {v: rng.choice([0, 1, 3, 5]) for v in values} for f, values in attributes.items()}},
            "purchase_threshold": rng.choice([4, 8, 12, 18])})
    return menu, priors


class ComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine, cls.envs = exp.load_policy_environment()
        cls.env = cls.envs["development"]

    def test_exact_ties_preserve_original_action_order(self):
        menu, priors = toy_fixture(self.env)
        rank = exp.initial_order(self.engine, self.env, menu, [priors[0]] * 3)
        self.assertTrue(all(v == 0 for v in rank["scores"].values()))
        self.assertEqual(rank["order"], exp.CFG["query_actions"])

    def test_initial_ranking_agrees_with_original_dv_first_action(self):
        menu, priors = toy_fixture(self.env)
        rank = exp.initial_order(self.engine, self.env, menu, priors)
        original = self.engine.PublicPolicy(self.env, menu, priors, "decision_value")
        self.assertEqual(rank["order"][0], original.next_action())
        self.assertEqual(set(rank["order"]), set(exp.CFG["query_actions"]))
        self.assertEqual(len(rank["order"]), 6)

    def test_frozen_questions_still_update_recommendation(self):
        menu, priors = toy_fixture(self.env)
        rank = exp.initial_order(self.engine, self.env, menu, priors)
        p = self.engine.PublicPolicy(self.env, menu, priors, "decision_value")
        original_action = p.predict()[0]
        chosen = "B" if original_action == "A" else "A"
        preferred = next(i for i in menu["items"] if i["product_id"] == chosen)
        truth = copy.deepcopy(priors[0])
        truth["purchase_threshold"] = 1
        for field, scores in truth["soft"]["scores"].items():
            for value in scores:
                scores[value] = 5 if value == preferred["attributes"][field] else 0
        user = self.env.ReferenceUser(truth)
        frozen = rank["order"][:]
        for question in frozen:
            p.observe(question, user.answer(question))
        self.assertEqual(rank["order"], frozen)
        self.assertEqual(p.predict()[0], chosen)
        self.assertNotEqual(p.predict()[0], original_action)
        self.assertEqual([h["action"] for h in p.history], frozen)

    def test_heldout_oov_retains_neutral_zero_and_sql_agrees(self):
        menu, priors = toy_fixture(self.env)
        menu["items"][0]["attributes"]["pattern"] = "__unseen__"
        env = self.envs["test_reserved"]
        py = env.evaluate_python(menu["items"], priors[0])
        self.assertEqual(py, env.evaluate_sql(menu["items"], priors[0]))
        expected = sum(priors[0]["soft"]["scores"][f].get(v, 0) for f, v in menu["items"][0]["attributes"].items())
        self.assertEqual(py["scores_by_product"]["A"], expected)

    def test_prediction_cache_separates_states_menus_and_splits(self):
        class FakePolicy:
            known = {}
            calls = 0

            def predict(self):
                self.calls += 1
                return (str(self.calls), 1.0)
        p, memo = FakePolicy(), {}
        first = exp.cached_predict(p, "development", "m1", memo, self.engine)
        self.assertEqual(first, exp.cached_predict(p, "development", "m1", memo, self.engine))
        p.known = {"a": {"scores": {"x": 1}}}
        second = exp.cached_predict(p, "development", "m1", memo, self.engine)
        third = exp.cached_predict(p, "test_reserved", "m1", memo, self.engine)
        fourth = exp.cached_predict(p, "test_reserved", "m2", memo, self.engine)
        self.assertEqual(len({first, second, third, fourth}), 4)

    def test_full_input_denominators_and_existing_prior_snapshot(self):
        data = exp.load_data()
        self.assertEqual(len(data["cases"]), 736)
        self.assertEqual(len(data["profiles"]), 288)
        self.assertEqual(len(data["menus"]), 54)
        self.assertEqual(len(data["historical"]), 20608)
        self.assertEqual(exp.sha(exp.INPUT / "prior_profiles.jsonl"),
                         exp.sha(exp.DEV / "artifacts/prepared/private/prior_profiles.jsonl"))
        strata = {(c["split"], c["pool_index"], c["user_cohort"]) for c in data["cases"]}
        self.assertEqual(len(strata), 32)


def statistical_fixture(ties=False):
    rr = []
    for cid, pid in (("c1", "p1"), ("c2", "p1"), ("c3", "p2")):
        for method in ("decision_value", exp.CFG["new_method"], "decision_set_ig"):
            for b in range(7):
                correct = True if ties else ((pid == "p1") == (method == "decision_value"))
                rr.append({"split": "toy", "case_id": cid, "profile_id": pid, "pool_index": 0,
                           "user_cohort": "A", "method": method, "budget": b,
                           "exact_decision_correct": correct})
    return rr


class StatisticsTests(unittest.TestCase):
    def test_case_and_profile_weighting_are_distinct(self):
        result = stats.bootstrap(statistical_fixture(), {**exp.CFG, "bootstrap_repetitions": 100}, "toy")
        entry = result["contrasts"]["adaptivity"]["budgets"]["5"]
        self.assertAlmostEqual(entry["case_equal"]["difference"], 1 / 3)
        self.assertEqual(entry["profile_equal"]["difference"], 0)
        self.assertEqual(result["profiles"], 2)
        self.assertEqual(result["cases"], 3)
        self.assertEqual(entry["profile_net_wins_ties_losses"], [1, 0, 1])

    def test_all_ties_remain_zero_and_bootstrap_is_reproducible(self):
        config = {**exp.CFG, "bootstrap_repetitions": 100}
        a = stats.bootstrap(statistical_fixture(True), config, "toy")
        b = stats.bootstrap(statistical_fixture(True), config, "toy")
        self.assertEqual(a, b)
        for entry in a["contrasts"]["adaptivity"]["budgets"].values():
            for weighting in ("case_equal", "profile_equal"):
                self.assertEqual(entry[weighting]["pointwise_95_ci"], [0, 0])
                self.assertEqual(entry[weighting]["simultaneous_14_contrast_95_band"], [0, 0])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "scope": "toy mechanism/OOV/cache/cluster edge cases and input coverage; no new panel outcomes"}
    path = exp.HERE / "TEST_RECEIPT.json"
    if path.exists() and (exp.HERE / "FROZEN.json").exists():
        if exp.read(path) != receipt:
            raise RuntimeError("Frozen test receipt differs; preserve prior evidence")
    else:
        exp.dump(path, receipt)
    sys.exit(0 if result.wasSuccessful() else 1)
