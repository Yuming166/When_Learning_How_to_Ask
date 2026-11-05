"""Toy counterexamples for failure semantics and dependent-model bootstrap."""
import copy
import random
import sys
import unittest

import analysis
import experiment as ex


def fixture():
    vocab = {"neckline": ["round", "v"], "sleeve_length": ["short", "long"], "fabric": ["cotton", "silk"],
             "wash_care": ["machine wash", "dry clean"], "pattern": ["solid", "print"]}
    menu = {"menu_id": "toy", "items": [{"product_id": pid, "attributes": {f: v[i] for f, v in vocab.items()}}
                                          for i, pid in enumerate(("A", "B"))]}
    rng = random.Random(31)
    priors = [{"profile_id": f"p{i}", "hard": {"allowed_care_labels": vocab["wash_care"][:], "excluded_fabric_labels": []},
               "soft": {"scores": {f: {v: rng.choice([-2, -1, 0, 2, 4]) for v in values} for f, values in vocab.items()}},
               "purchase_threshold": rng.choice([0, 4, 8])} for i in range(12)]
    case = {"case_id": "toycase", "stratum": "toy", "menu_id": menu["menu_id"], "public_menu": menu}
    truth = copy.deepcopy(priors[0])
    return case, truth, priors, vocab


def bank_for(profile):
    user = ex.ref.ReferenceUser(profile)
    return {a: {"valid": True, "value": user.answer(a), "exact_profile_match": True} for a in ex.CFG["query_actions"]}


def legacy(case, profile, priors, vocab, bank):
    original_bank = {(a, 1): {"valid": r["valid"], "parsed": {"value": r["value"]},
                             "exact_profile_match": r["exact_profile_match"]} for a, r in bank.items()}
    return ex.legacy_replay._case_trace(ex.ref, case, profile, priors, "decision_value", 1, original_bank, vocab, [0, 4, 8])


class ReplayTests(unittest.TestCase):
    def test_full_dv_replay_matches_legacy_with_valid_answers(self):
        case, truth, prior, vocab = fixture()
        bank = bank_for(truth)
        rank = ex.initial_rank(case["public_menu"], prior)
        old = legacy(case, truth, prior, vocab, bank)
        self.assertEqual(ex.replay_path(case, truth, prior, bank, vocab, rank["order"], old), old)
        static = ex.replay_path(case, truth, prior, bank, vocab, rank["order"])
        self.assertEqual(static[6]["selected_action"], old[6]["selected_action"])
        self.assertTrue(static[6]["exact_decision_correct"])
        self.assertEqual(static[6]["query_sequence"], rank["order"])

    def test_failed_first_question_costs_one_and_fallback_can_be_correct(self):
        case, _, prior, vocab = fixture()
        rank = ex.initial_rank(case["public_menu"], prior)
        prediction = rank["initial_prediction"][0]
        truth = next(p for p in prior if ex.engine.episode_metrics(ex.ref, case["public_menu"]["items"], p, prediction)["exact_decision_correct"])
        bank = bank_for(truth)
        bank[rank["order"][0]]["valid"] = False
        old = legacy(case, truth, prior, vocab, bank)
        dynamic = ex.replay_path(case, truth, prior, bank, vocab, rank["order"], old)
        static = ex.replay_path(case, truth, prior, bank, vocab, rank["order"])
        for b in range(1, 7):
            self.assertEqual(static[b]["elicitation_units"], 1)
            self.assertEqual(static[b]["valid_query_sequence"], [])
            self.assertFalse(static[b]["answer_path_complete"])
            self.assertTrue(static[b]["exact_decision_correct"])
            self.assertEqual(dynamic[b]["selected_action"], static[b]["selected_action"])

    def test_later_failure_preserves_last_valid_state(self):
        case, truth, prior, vocab = fixture()
        rank = ex.initial_rank(case["public_menu"], prior)
        bank = bank_for(truth)
        bank[rank["order"][2]]["valid"] = False
        old = legacy(case, truth, prior, vocab, bank)
        self.assertEqual(ex.replay_path(case, truth, prior, bank, vocab, rank["order"], old), old)
        static = ex.replay_path(case, truth, prior, bank, vocab, rank["order"])
        for b in range(3, 7):
            self.assertEqual(static[b]["elicitation_units"], 3)
            self.assertEqual(static[b]["valid_query_sequence"], rank["order"][:2])
            self.assertEqual(static[b]["selected_action"], static[2]["selected_action"])

    def test_valid_but_unfaithful_answers_are_consumed_without_repair(self):
        case, truth, prior, vocab = fixture()
        truth["purchase_threshold"] = 0
        wrong = copy.deepcopy(truth)
        for field, values in vocab.items():
            truth["soft"]["scores"][field] = {values[0]: -2, values[1]: 4}
            wrong["soft"]["scores"][field] = {values[0]: 4, values[1]: -2}
        wrong["purchase_threshold"] = 0
        bank = bank_for(wrong)
        for r in bank.values():
            r["exact_profile_match"] = False
        rank = ex.initial_rank(case["public_menu"], prior)
        old = legacy(case, truth, prior, vocab, bank)
        static = ex.replay_path(case, truth, prior, bank, vocab, rank["order"])
        self.assertTrue(static[6]["answer_path_complete"])
        self.assertFalse(static[6]["exact_decision_correct"])
        self.assertEqual(static[6]["selected_action"], old[6]["selected_action"])
        self.assertEqual(static[6]["selected_action"], "A")

    def test_observation_exception_inherits_legacy_stop_rule(self):
        case, truth, prior, vocab = fixture()
        rank = ex.initial_rank(case["public_menu"], prior)
        bank = bank_for(truth)
        bank[rank["order"][0]]["value"] = {"invalid_schema": True}
        old = legacy(case, truth, prior, vocab, bank)
        self.assertEqual(ex.replay_path(case, truth, prior, bank, vocab, rank["order"], old), old)
        self.assertFalse(old[1]["answer_path_complete"])
        self.assertEqual(old[1]["valid_query_sequence"], [])

    def test_exact_ties_follow_original_question_order(self):
        case, truth, _, _ = fixture()
        rank = ex.initial_rank(case["public_menu"], [truth] * 3)
        self.assertTrue(all(score == 0 for score in rank["scores"].values()))
        self.assertEqual(rank["order"], ex.CFG["query_actions"])

    def test_source_coverage_and_shared_profile_identity(self):
        data = ex.load_data()
        self.assertEqual(len(data["cases"]), 280)
        self.assertEqual(len(data["profiles"]), 48)
        self.assertEqual(len({(c["pool_index"], c["user_cohort"]) for c in data["cases"]}), 12)
        for model in ex.CFG["models"]:
            self.assertEqual(len(data["banks"][model]), 288)
            self.assertEqual(len(data["historical"][model]), 7840)


def stats_fixture(ties=False):
    result = []
    for cid, pid in (("c1", "p1"), ("c2", "p1"), ("c3", "p2")):
        for model in ex.CFG["models"]:
            for method in ex.CFG["evaluated_methods"]:
                for b in range(7):
                    positive = (pid == "p1") != (model == "deepseek")
                    correct = True if ties else positive == (method == "decision_value")
                    result.append({"case_id": cid, "profile_id": pid, "model": model, "method": method,
                                   "budget": b, "pool_index": 0, "user_cohort": "A", "exact_decision_correct": correct})
    return result


class JointStatisticsTests(unittest.TestCase):
    def test_profile_weights_and_perfect_model_dependence(self):
        a = analysis.joint_bootstrap(stats_fixture(), {**ex.CFG, "bootstrap_repetitions": 257})
        first, opposite, identical = [a["models"][m]["5"] for m in ex.CFG["models"]]
        self.assertAlmostEqual(first["case_equal"]["difference"], 1 / 3)
        self.assertEqual(first["profile_equal"]["difference"], 0)
        self.assertEqual(first, identical)
        for weight in ("case_equal", "profile_equal"):
            lo, hi = first[weight]["pointwise_95_ci"]
            self.assertEqual(opposite[weight]["pointwise_95_ci"], [-hi, -lo])
            self.assertEqual(first[weight]["simultaneous_primary_three_models_95_band"], first[weight]["simultaneous_21_contrast_95_band"])

    def test_zero_differences_and_reproducibility(self):
        config = {**ex.CFG, "bootstrap_repetitions": 101}
        a = analysis.joint_bootstrap(stats_fixture(True), config)
        self.assertEqual(a, analysis.joint_bootstrap(stats_fixture(True), config))
        for model in ex.CFG["models"]:
            for b in range(7):
                for weight in ("case_equal", "profile_equal"):
                    self.assertEqual(a["models"][model][str(b)][weight]["pointwise_95_ci"], [0, 0])


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    receipt = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "scope": "legacy stop/fallback/unfaithful-answer counterexamples, exact ties, source coverage and dependent-model bootstrap"}
    path = ex.HERE / "TEST_RECEIPT.json"
    if path.exists() and (ex.HERE / "FROZEN.json").exists():
        if ex.read(path) != receipt:
            raise RuntimeError("Frozen test receipt mismatch")
    else:
        ex.dump(path, receipt)
    sys.exit(0 if result.wasSuccessful() else 1)
