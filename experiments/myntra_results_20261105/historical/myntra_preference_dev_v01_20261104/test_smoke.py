import json
import unittest

import environment as e
import qwen_smoke as q
from test_environment import fixture


class SmokeTest(unittest.TestCase):
    def setUp(self):
        items, self.vocab, self.profile = fixture()
        self.menu = {"items": items, "gender": "Women", "category": "Kurtas"}
        self.shown = q.shown_options(self.menu)
        self.cfg = e.read(e.BASE / "config.json")

    def parse(self, kind, text, **kw):
        return q.parse_reply(kind, text, kw.get("finish", "stop"), kw.get("model", self.cfg["expected_model"]),
                             self.shown, self.vocab, self.cfg)

    def test_nonpurchase_needs_no_item_even_if_feasible(self):
        self.assertEqual(self.parse("choice", '{"decision":"NO_BUY","selected_id":null}')["value"]["selected_id"], None)

    def test_buy_requires_current_id(self):
        for x in [None, "unknown", 0, ["C00"]]:
            with self.assertRaises(ValueError):
                self.parse("choice", json.dumps({"decision": "BUY", "selected_id": x}))

    def test_no_buy_with_selected_item_rejected(self):
        with self.assertRaises(ValueError):
            self.parse("choice", '{"decision":"NO_BUY","selected_id":"C00"}')

    def test_one_complete_json_fence_supported(self):
        p = self.parse("choice", '```json\n{"decision":"BUY","selected_id":"C00"}\n```')
        self.assertTrue(p["fenced"])

    def test_prose_extraction_not_allowed(self):
        with self.assertRaises(ValueError):
            self.parse("choice", 'Here is my answer: {"decision":"NO_BUY","selected_id":null}')

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            self.parse("choice", '{"decision":"BUY","decision":"NO_BUY","selected_id":null}')

    def test_nonstop_or_model_drift_invalid(self):
        for kw in [{"finish": "length"}, {"model": "different-model"}]:
            with self.assertRaises(ValueError):
                self.parse("choice", '{"decision":"NO_BUY","selected_id":null}', **kw)

    def test_care_multiple_choices_permitted(self):
        self.assertEqual(len(self.parse("care", '{"allowed_care_labels":["hand wash","dry clean"]}')["value"]["allowed_care_labels"]), 2)

    def test_care_invalid_values_or_duplicates_not_repaired(self):
        for values in [[], ["hand wash", "hand wash"], ["gentle cycle"], [True]]:
            with self.assertRaises(ValueError):
                self.parse("care", json.dumps({"allowed_care_labels": values}))

    def test_disclosure_schema_without_gold_validation(self):
        stated = e.private_preferences(self.profile)
        stated["purchase_threshold"] = 999
        self.assertEqual(self.parse("disclosure", json.dumps(stated))["value"]["purchase_threshold"], 999)

    def test_reverse_changes_only_order(self):
        self.assertEqual(q.shown_options(self.menu, "reverse"), list(reversed(self.shown)))

    def test_alias_preserves_features_and_bijection(self):
        alias = q.shown_options(self.menu, "alias")
        self.assertEqual([x["attributes"] for x in alias], [x["attributes"] for x in self.shown])
        self.assertEqual({x["option_id"] for x in alias}, {x["option_id"] for x in self.shown})
        self.assertNotEqual(alias[0]["option_id"], self.shown[0]["option_id"])

    def test_repeat_messages_identical(self):
        a = q.independent_messages(self.profile, self.menu, {"kind": "choice", "view": "base"})
        z = q.independent_messages(self.profile, self.menu, {"kind": "choice", "view": "repeat"})
        self.assertEqual(a, z)

    def test_care_frames_use_identical_answer_encoding(self):
        a = q.independent_messages(self.profile, self.menu, {"kind": "care", "frame": "A"})
        z = q.independent_messages(self.profile, self.menu, {"kind": "care", "frame": "B"})
        self.assertEqual(a[0], z[0])
        self.assertTrue(a[1]["content"].endswith(q.CARE_SCHEMA))
        self.assertTrue(z[1]["content"].endswith(q.CARE_SCHEMA))

    def test_prompt_does_not_contain_product_reference_tables(self):
        messages = q.independent_messages(self.profile, self.menu, {"kind": "choice", "view": "base"})
        text = json.dumps(messages)
        for key in ["scores_by_product", "valid_purchase_ids", "feasible_ids", "reference_decision"]:
            self.assertNotIn(key, text)


if __name__ == "__main__":
    unittest.main()
