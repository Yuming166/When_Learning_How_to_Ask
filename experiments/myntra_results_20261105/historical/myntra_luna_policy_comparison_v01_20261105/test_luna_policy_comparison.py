import json
import unittest

import engine
import luna_policy_comparison as exp


class LunaPolicyComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = {p["profile_id"]: p for p in exp.read_rows(exp.PRIVATE / "profiles.jsonl")}
        cls.cases = exp.read_rows(exp.PRIVATE / "selected_cases.jsonl")
        cls.menus = {m["menu_id"]: m for m in exp.read_rows(exp.PUBLIC / "menus.jsonl")}
        cls.vocabs = exp.read(exp.PUBLIC / "vocabularies.json")
        cls.env = engine.load_environment(exp.WORKTREE)
        cls.priors = exp.read_rows(exp.PRIVATE / "prior_profiles.jsonl")

    def test_input_inventory_and_strata_are_frozen(self):
        self.assertEqual(len(self.cases), 8)
        self.assertEqual(len(self.profiles), 8)
        self.assertEqual(len(exp.read_rows(exp.PRIVATE / "jobs.jsonl")), 96)
        self.assertEqual(len({c["stratum"] for c in self.cases}), 4)
        self.assertEqual(len(self.priors), 6144)

    def test_query_specific_field_answers_parse(self):
        profile = self.profiles["D32"]
        vocab = self.vocabs[str(profile["pool_index"])]
        for action in exp.CFG["query_actions"]:
            answer = exp.ref.ReferenceUser(profile).answer(action)
            parsed = exp.parse_field_answer(
                action, json.dumps(answer), vocab,
                exp.read(exp.LEGACY / "config.json")["purchase_thresholds"],
            )
            self.assertEqual(parsed, answer)

    def test_duplicate_keys_and_invalid_fields_fail_closed(self):
        profile = self.profiles["D32"]
        vocab = self.vocabs[str(profile["pool_index"])]
        with self.assertRaises(ValueError):
            exp.parse_field_answer("purchase_threshold", '{"purchase_threshold":0,"purchase_threshold":3}',
                                   vocab, [0, 3, 6, 9])
        with self.assertRaises(ValueError):
            exp.parse_field_answer("neckline", '{"field":"fabric","scores":{}}', vocab, [0, 3, 6, 9])

    def test_selected_menus_are_supported_by_their_mapped_prior_pools(self):
        for case_row in self.cases:
            menu = self.menus[case_row["menu_id"]]
            prior = next(p for p in self.priors if p["pool_index"] == case_row["prior_pool_index"])
            support = prior["soft"]["scores"]
            for item in menu["items"]:
                for field, value in item["attributes"].items():
                    self.assertIn(value, support[field], (case_row["case_id"], field, value))

    def test_all_four_policies_recover_reference_when_answers_are_exact(self):
        case_row = self.cases[0]
        profile = self.profiles[case_row["profile_id"]]
        menu = self.menus[case_row["menu_id"]]
        prior = [p for p in self.priors if p["pool_index"] == case_row["prior_pool_index"]]
        for method in exp.CFG["methods"]:
            policy = engine.PublicPolicy(self.env, menu, prior, method)
            user = exp.ref.ReferenceUser(profile)
            for _ in range(6):
                action = policy.next_action()
                self.assertIsNotNone(action)
                policy.observe(action, user.answer(action))
            action, _ = policy.predict()
            metrics = engine.episode_metrics(self.env, menu["items"], profile, action)
            self.assertTrue(metrics["exact_decision_correct"], (case_row["case_id"], method))

    def test_same_question_prompt_is_paired_across_response_replicates(self):
        prompts = {r["job_id"]: r for r in exp.read_rows(exp.PROMPTS / "requests.jsonl")}
        for case in self.cases:
            for action in exp.CFG["query_actions"]:
                left = prompts[f"{case['case_id']}__r1__{action}"]
                right = prompts[f"{case['case_id']}__r2__{action}"]
                self.assertEqual(left["prompt_sha256"], right["prompt_sha256"])
        public_cases = exp.read_rows(exp.PUBLIC / "cases.jsonl")
        self.assertTrue(all(set(row) == {"case_id", "profile_id", "menu_id"} for row in public_cases))


if __name__ == "__main__":
    unittest.main()
