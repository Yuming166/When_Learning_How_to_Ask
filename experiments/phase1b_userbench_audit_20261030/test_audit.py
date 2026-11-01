import json
import unittest
from pathlib import Path

from audit_userbench import ROOT, exclusive_labels, public_observation


class ScientificBoundaries(unittest.TestCase):
    def test_unspecified_preference_does_not_become_negative(self):
        unknown = {"dimensions": ["flight"], "flight": {"preferences": [
            ["flight", "service", "prefer business class", "more space", "annotation"]]}}
        self.assertEqual(exclusive_labels(unknown), [])

    def test_explicit_conflicting_preferences_not_coerced_to_binary(self):
        conflict = {"dimensions": ["flight"], "flight": {"preferences": [
            ["flight", "path", "prefer direct flight"], ["flight", "path", "prefer one-stop layover flight"]]}}
        self.assertEqual(exclusive_labels(conflict), [])

    def test_hidden_observation_and_rewards_are_not_agent_inputs(self):
        observation = {"feedback": "Which destination?", "step_count": 2,
                       "task_description": "SECRET_TRUE_PREFERENCE", "last_reward": .2,
                       "remaining_preferences": 4, "elicitation_ratio": .5,
                       "info": {"preferences_summary": "SECRET_TRUE_PREFERENCE"}}
        public = public_observation(observation)
        self.assertEqual(public, {"feedback": "Which destination?", "step_count": 2})
        self.assertNotIn("SECRET", json.dumps(public))
        with self.assertRaises(ValueError): public_observation({"feedback": 7, "step_count": 0})

    def test_live_source_probe_and_official_split_receipt(self):
        data = json.loads((ROOT / "audit_summary.json").read_text())
        self.assertEqual(data["model_calls"], 0)
        self.assertEqual(data["scenario_count"], sum(data["official_splits"].values()))
        self.assertEqual(data["scenario_id_overlap"], 0)
        probe = data["reset_leakage_probe"]
        self.assertTrue(probe["task_description_equals_full_private_scenario"])
        self.assertGreater(probe["private_summary_count"], 0)
        self.assertEqual(probe["public_projection_keys"], ["feedback", "step_count"])

    def test_preview_truth_source_and_private_public_separation(self):
        public = [json.loads(x) for x in (ROOT / "preview_public.jsonl").read_text().splitlines()]
        private = [json.loads(x) for x in (ROOT / "preview_private.jsonl").read_text().splitlines()]
        self.assertEqual(len(public), len(private))
        for p, s in zip(public, private):
            self.assertNotIn("source_scenario_id", p)
            self.assertNotIn("private_card", p)
            self.assertNotIn("ground_truth_digit", p)
            self.assertEqual(p["profile_id"], s["profile_id"])
            active = {x["preference"] for x in s["private_card"] if x["aspect"] == p["group"]}
            expected = s["semantic_alternatives"][s["source_theta"]]
            other = s["semantic_alternatives"][1 - s["source_theta"]]
            self.assertIn(expected, active)
            self.assertNotIn(other, active)
            self.assertEqual(p["options"][s["ground_truth_digit"]], expected.removeprefix("prefer "))


if __name__ == "__main__":
    unittest.main()
