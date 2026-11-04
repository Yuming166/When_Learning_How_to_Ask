"""Protocol properties that prevent pairing, truth-interface and scope drift."""
import json
from pathlib import Path
import unittest

import run as harness


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).parent / "config.json").read_text())
        self.worlds = harness.make_worlds(self.config)

    def test_complete_predeclared_denominator_and_public_truth_separation(self):
        self.assertEqual(len(self.worlds), 48)
        self.assertEqual(len(self.worlds) * len(self.config["arms"]), 144)
        self.assertEqual(len({w["id"] for w in self.worlds}), 48)
        for world in self.worlds:
            self.assertEqual(set(world["public"]), {"d", "groups", "eta", "catalogue"})
            self.assertTrue(all(value == 0 for value in world["private"]["types"]))
            self.assertEqual(world["private"]["theta"], [1] * world["public"]["d"])
            expected = 1 if world["catalogue_name"] == "weighted5" else 0
            self.assertEqual(world["private"]["winner"], expected)

    def test_pairing_changes_only_partition_and_risk_not_response_tapes(self):
        for name in ("weighted5", "genuine6"):
            for replicate in self.config["replicate_indices"]:
                rows = [w for w in self.worlds if w["catalogue_name"] == name and w["replicate"] == replicate]
                self.assertEqual(len(rows), 4)
                self.assertEqual(len({w["private"]["response_seed"] for w in rows}), 1)
                self.assertEqual(len({json.dumps(w["public"]["catalogue"], sort_keys=True) for w in rows}), 1)
        self.assertEqual(len({w["private"]["response_seed"] for w in self.worlds}), 12)
        weighted = [c for c in self.config["cells"] if c["catalogue_name"] == "weighted5"]
        self.assertEqual(sorted(weighted[0]["groups"].count(g) for g in set(weighted[0]["groups"])), [2, 3])
        self.assertEqual(sorted(weighted[1]["groups"].count(g) for g in set(weighted[1]["groups"])), [2, 3])

    def test_smoke_uses_disjoint_tapes_and_all_frozen_model_sources_are_named(self):
        smoke = harness.make_worlds(self.config, smoke=True)
        self.assertFalse({w["private"]["response_seed"] for w in smoke} &
                         {w["private"]["response_seed"] for w in self.worlds})
        self.assertIn("experiments/recommendation_loop_20261103/relative_ig.py", harness.DEPENDENCIES)
        self.assertIn("experiments/recommendation_loop_20261103/decision_ig.py", harness.DEPENDENCIES)
        self.assertIn("experiments/recommendation_loop_20261103/certification.py", harness.DEPENDENCIES)
        self.assertEqual(self.config["workers"], 2)
        self.assertEqual(self.config["max_queries"], 2500)


if __name__ == "__main__":
    unittest.main()
