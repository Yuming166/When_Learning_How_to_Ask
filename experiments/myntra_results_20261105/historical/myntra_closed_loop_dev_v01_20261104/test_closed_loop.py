import json
import unittest
from pathlib import Path

import engine


class ClosedLoopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("/home/gaoym/When_Learning_How_to_Ask_myntra_preference_dev_20261104")
        cls.env = engine.load_environment(cls.source)
        cls.prepared = engine.HERE / "artifacts/prepared"
        if not cls.prepared.exists():
            cls.env.prepare(cls.prepared)
        cls.profiles = {x["profile_id"]: x for x in cls.env.rows(cls.prepared / "private/profiles.jsonl")}
        cls.menus = {x["menu_id"]: x for x in cls.env.rows(cls.prepared / "public/menus.jsonl")}
        cls.cases = cls.env.rows(cls.prepared / "public/cases.jsonl")
        vocabs = json.loads((cls.prepared / "public/vocabularies.json").read_text())
        cls.prior = engine.make_prior_profiles(cls.env, vocabs, 64)

    def test_policy_interface_has_no_actual_profile_argument(self):
        self.assertEqual(list(engine.PublicPolicy.__init__.__code__.co_varnames[:5]),
                         ["self", "env", "menu", "prior_profiles", "method"])

    def test_question_answer_merge_covers_all_private_fields(self):
        profile = self.profiles["P00"]
        user = self.env.ReferenceUser(profile)
        observed = self.env.private_preferences(profile)
        for action in engine.CONFIG["query_actions"]:
            answer = user.answer(action)
            observed = engine.merge_answer(observed, action, answer)
        self.assertEqual(observed, self.env.private_preferences(profile))

    def test_all_methods_recover_valid_action_after_six_exact_answers(self):
        case = next(c for c in self.cases if c["case_id"] == "P00__M00")
        profile = self.profiles["P00"]
        menu = self.menus[case["menu_id"]]
        for method in engine.CONFIG["methods"]:
            rows = engine.run_case(self.env, case, profile,
                                   self.prior[int(profile["pool_index"])], method, 6)
            self.assertEqual(len(rows), 7)
            self.assertTrue(rows[-1]["exact_decision_correct"], method)
            self.assertEqual(rows[-1]["elicitation_units"], 6)

    def test_adaptive_scores_are_nonnegative(self):
        case = next(c for c in self.cases if c["case_id"] == "P00__M00")
        profile = self.profiles["P00"]
        menu = self.menus[case["menu_id"]]
        for method in ["profile_ig", "decision_set_ig", "decision_value"]:
            policy = engine.PublicPolicy(self.env, menu,
                                         self.prior[int(profile["pool_index"])], method)
            for action in engine.CONFIG["query_actions"]:
                self.assertGreaterEqual(policy.score_query(action), 0.0)

    def test_fixed_order_and_ask_all_are_distinct_costs(self):
        case = next(c for c in self.cases if c["case_id"] == "P00__M00")
        profile = self.profiles["P00"]
        policy = engine.PublicPolicy(self.env, self.menus[case["menu_id"]],
                                     self.prior[int(profile["pool_index"])], "fixed_order")
        self.assertEqual([policy.next_action() for _ in range(1)], ["neckline"])
        row = engine.run_ask_all(self.env, case, profile)
        self.assertEqual((row["dialogue_turns"], row["elicitation_units"]), (1, 6))
        self.assertTrue(row["exact_decision_correct"])


if __name__ == "__main__":
    unittest.main()
