import copy
import json
import unittest

import environment as e


def fixture():
    a = dict(zip(e.FIELDS, ["v-neck", "long sleeves", "cotton", "machine wash", "printed"]))
    b = dict(zip(e.FIELDS, ["round neck", "short sleeves", "polyester", "hand wash", "solid"]))
    items = [{"product_id": "100", "attributes": a}, {"product_id": "101", "attributes": b}]
    vocab = {f: sorted({a[f], b[f]}) for f in e.FIELDS}
    scores = {f: {v: int(v == a[f]) for v in vocab[f]} for f in e.FIELDS}
    profile = {"profile_id": "fixture", "hard": {"allowed_care_labels": e.CARE[:], "excluded_fabric_labels": []},
               "soft": {"scores": scores}, "purchase_threshold": 4}
    return items, vocab, profile


class EnvironmentTest(unittest.TestCase):
    def test_feasible_does_not_force_purchase(self):
        items, _, p = fixture()
        p["purchase_threshold"] = 8
        r = e.evaluate_python(items, p)
        self.assertEqual(r["feasible_ids"], ["100", "101"])
        self.assertEqual(r["relative_favorite_ids"], ["100"])
        self.assertEqual(r["decision"], "NO_BUY")
        self.assertEqual(r["valid_purchase_ids"], [])

    def test_threshold_equality_is_no_purchase(self):
        items, _, p = fixture()
        p["purchase_threshold"] = 5
        self.assertEqual(e.evaluate_python(items, p)["decision"], "NO_BUY")
        self.assertEqual(e.evaluate_sql(items, p)["decision"], "NO_BUY")

    def test_buying_selects_a_feasible_maximizer(self):
        items, _, p = fixture()
        r = e.evaluate_python(items, p)
        self.assertEqual(r["valid_purchase_ids"], ["100"])
        self.assertFalse(e.score_decision({"decision": "BUY", "selected_id": "101"}, r))

    def test_all_tied_maximizers_are_valid(self):
        items, _, p = fixture()
        p["soft"]["scores"] = {f: {v: 0 for v in m} for f, m in p["soft"]["scores"].items()}
        p["purchase_threshold"] = -1
        r = e.evaluate_python(items, p)
        self.assertEqual(r["valid_purchase_ids"], ["100", "101"])
        for pid in ["100", "101"]:
            self.assertTrue(e.score_decision({"decision": "BUY", "selected_id": pid}, r))

    def test_no_feasible_item_is_retained(self):
        items, _, p = fixture()
        p["hard"]["allowed_care_labels"] = ["dry clean"]
        r = e.evaluate_python(items, p)
        self.assertEqual(r["decision"], "NO_BUY")
        self.assertEqual(r["no_buy_reason"], "NO_FEASIBLE_ITEM")

    def test_multiple_acceptable_care_labels(self):
        items, _, p = fixture()
        p["hard"]["allowed_care_labels"] = ["machine wash", "hand wash"]
        self.assertEqual(e.evaluate_python(items, p)["feasible_ids"], ["100", "101"])

    def test_hard_exclusion_overrides_high_soft_score(self):
        items, _, p = fixture()
        p["hard"]["excluded_fabric_labels"] = ["cotton"]
        self.assertEqual(e.evaluate_python(items, p)["relative_favorite_ids"], ["101"])

    def test_missing_soft_label_is_not_silently_zero(self):
        items, _, p = fixture()
        del p["soft"]["scores"]["fabric"]["cotton"]
        with self.assertRaises(KeyError):
            e.evaluate_python(items, p)

    def test_sql_agreement_for_thresholds_hard_filters_and_ties(self):
        items, _, p = fixture()
        for care in [["machine wash"], ["hand wash"], ["dry clean"], e.CARE]:
            for excluded in [[], ["cotton"], ["polyester"]]:
                for threshold in [-1, 0, 4, 5, 8]:
                    q = copy.deepcopy(p)
                    q["hard"] = {"allowed_care_labels": care, "excluded_fabric_labels": excluded}
                    q["purchase_threshold"] = threshold
                    self.assertEqual(e.evaluate_python(items, q), e.evaluate_sql(items, q))

    def test_insufficient_agent_knowledge_is_not_no_buy(self):
        items, vocab, _ = fixture()
        agent = e.PublicAgent({"items": items}, vocab)
        self.assertEqual(agent.finish(), {"status": "INSUFFICIENT_PREFERENCES", "decision": None, "selected_id": None})

    def test_lossless_ask_all_closes_loop(self):
        items, vocab, p = fixture()
        agent = e.PublicAgent({"items": items}, vocab, "ask_all")
        user = e.ReferenceUser(p)
        action = agent.next_action()
        agent.observe(action, user.answer(action))
        self.assertIsNone(agent.next_action())
        self.assertEqual(agent.finish()["selected_id"], "100")

    def test_fieldwise_closes_loop_and_keeps_no_buy(self):
        items, vocab, p = fixture()
        p["purchase_threshold"] = 8
        agent = e.PublicAgent({"items": items}, vocab)
        user = e.ReferenceUser(p)
        while (action := agent.next_action()) is not None:
            agent.observe(action, user.answer(action))
        self.assertEqual(len(agent.history), 6)
        self.assertEqual(agent.finish()["decision"], "NO_BUY")

    def test_agent_uses_disclosed_not_actual_preferences(self):
        items, vocab, actual = fixture()
        stated = copy.deepcopy(actual)
        stated["purchase_threshold"] = 999
        agent = e.PublicAgent({"items": items}, vocab, "ask_all")
        agent.observe("ASK_ALL", e.private_preferences(stated))
        self.assertEqual(agent.finish()["decision"], "NO_BUY")
        self.assertEqual(e.evaluate_python(items, actual)["decision"], "BUY")

    def test_boolean_is_not_numeric_threshold_or_score(self):
        _, vocab, p = fixture()
        bad = e.private_preferences(p)
        bad["purchase_threshold"] = True
        with self.assertRaises(ValueError):
            e.validate_disclosure(bad, vocab)
        bad = e.private_preferences(p)
        bad["soft"]["scores"]["fabric"]["cotton"] = True
        with self.assertRaises(ValueError):
            e.validate_disclosure(bad, vocab)

    def test_incomplete_disclosure_fails(self):
        _, vocab, p = fixture()
        bad = e.private_preferences(p)
        del bad["soft"]["scores"]["neckline"]["v-neck"]
        with self.assertRaises(ValueError):
            e.validate_disclosure(bad, vocab)

    def test_duplicate_care_and_unknown_fabric_fail(self):
        _, vocab, p = fixture()
        bad = e.private_preferences(p)
        bad["hard"]["allowed_care_labels"] = ["machine wash", "machine wash"]
        with self.assertRaises(ValueError):
            e.validate_disclosure(bad, vocab)
        bad = e.private_preferences(p)
        bad["hard"]["excluded_fabric_labels"] = ["unreported fibre"]
        with self.assertRaises(ValueError):
            e.validate_disclosure(bad, vocab)

    def test_reference_user_cannot_be_mutated_through_answers(self):
        _, _, p = fixture()
        user = e.ReferenceUser(p)
        answer = user.answer("ASK_ALL")
        answer["purchase_threshold"] = 999
        self.assertEqual(user.answer("ASK_ALL")["purchase_threshold"], 4)

    def test_profile_generation_ignores_menu_order(self):
        _, vocab, _ = fixture()
        cfg = e.read(e.BASE / "config.json")
        a = e.generate_profiles(vocab, 0, cfg)
        z = e.generate_profiles(dict(reversed(list(vocab.items()))), 0, cfg)
        self.assertEqual(a, z)


if __name__ == "__main__":
    unittest.main()
