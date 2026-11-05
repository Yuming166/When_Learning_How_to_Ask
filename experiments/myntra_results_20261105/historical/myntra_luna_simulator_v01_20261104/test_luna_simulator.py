import json
import unittest

import luna_simulator as l


class LunaSimulatorProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = l.rows(l.PRIVATE / "jobs.jsonl")
        cls.cases = {x["case_id"]: x for x in l.rows(l.PRIVATE / "selected_cases.jsonl")}
        cls.profiles = {x["profile_id"]: x for x in l.rows(l.PRIVATE / "profiles.jsonl")}
        cls.menus = {x["menu_id"]: x for x in l.rows(l.PUBLIC / "menus.jsonl")}
        cls.templates = l.read(l.PRIVATE / "prompt_templates.json")
        cls.vocabularies = l.read(l.PUBLIC / "vocabularies.json")

    def test_full_planned_denominators_and_strata(self):
        self.assertEqual(len(self.jobs), 72)
        self.assertEqual(len(self.cases), 8)
        self.assertEqual(len(self.profiles), 8)
        counts = {s: sum(c["stratum"] == s for c in self.cases.values())
                  for s in ["BUY_UNIQUE", "BUY_TIED", "NO_BUY_FEASIBLE", "NO_BUY_INFEASIBLE"]}
        self.assertEqual(counts, {s: 2 for s in counts})
        for c in self.cases:
            self.assertEqual(sum(j["case_id"] == c for j in self.jobs), 9)

    def test_independent_base_repeats_are_byte_identical_and_gold_is_hidden(self):
        for case_id, case in self.cases.items():
            prompt_texts = [self.templates[f"{case_id}__base_{i}"]["prompt"] for i in range(1, 4)]
            self.assertEqual(prompt_texts[0], prompt_texts[1])
            self.assertEqual(prompt_texts[1], prompt_texts[2])
            self.assertNotIn(json.dumps(case["reference"], ensure_ascii=False), prompt_texts[0])
        self.assertEqual(l.read(l.INPUT / "SOURCE_RECEIPT.json")["reserved_products_included"], False)

    def test_views_preserve_same_menu_and_change_only_presentation(self):
        for case_id, case in self.cases.items():
            base = self.templates[f"{case_id}__base_1"]["prompt"]
            reverse = self.templates[f"{case_id}__reverse"]["prompt"]
            alias = self.templates[f"{case_id}__alias"]["prompt"]
            self.assertNotEqual(base, reverse)
            self.assertNotEqual(base, alias)
            menu = self.menus[case["menu_id"]]
            self.assertEqual({x["product_id"] for x in l.transport.shown_options(menu)},
                             {x["product_id"] for x in l.transport.shown_options(menu, "reverse")})
            self.assertEqual({x["product_id"] for x in l.transport.shown_options(menu)},
                             {x["product_id"] for x in l.transport.shown_options(menu, "alias")})

    def test_strict_parser_and_duplicate_key_rejection(self):
        job = next(j for j in self.jobs if j["kind"] == "choice")
        menu = self.menus[job["menu_id"]]
        shown = l.transport.shown_options(menu, job.get("view", "base"))
        good = json.dumps({"decision": "NO_BUY", "selected_id": None})
        self.assertTrue(l.parse_luna("choice", good, shown, {})["value"]["decision"] == "NO_BUY")
        with self.assertRaises(ValueError):
            l.parse_luna("choice", "Answer: " + good, shown, {})
        with self.assertRaises(ValueError):
            l.parse_luna("choice", '{"decision":"NO_BUY","decision":"BUY","selected_id":null}', shown, {})

    def test_dialogue_includes_actual_disclosure_and_public_recommendation(self):
        job = next(j for j in self.jobs if j["kind"] == "dialogue_choice")
        profile = self.profiles[job["profile_id"]]
        menu = self.menus[job["menu_id"]]
        disclosure = json.dumps(l.ref.private_preferences(profile), ensure_ascii=False)
        value = l.ref.private_preferences(profile)
        agent = l.ref.PublicAgent(menu, self.vocabularies[str(menu["pool_index"])], "ask_all")
        agent.observe("ASK_ALL", value)
        recommendation = agent.finish()
        messages = l.messages_for(job, profile, menu, disclosure, recommendation)
        self.assertEqual(messages[2]["content"], disclosure)
        prompt = l.prompt_from_messages(messages)
        self.assertIn(disclosure, prompt)
        self.assertIn("推荐系统依据你刚才的披露", prompt)
        self.assertNotIn(json.dumps(self.cases[job["case_id"]]["reference"], ensure_ascii=False), prompt)


if __name__ == "__main__":
    unittest.main()
