"""Scientific contract checks, independent evaluator checks, and parser/leakage checks."""
import copy
import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from design import ROOT, contrast_decision, decision, make_dataset, parse_answer, validate
from analyze import observation_only_selector
from design import sha, write_json, write_jsonl


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((ROOT / "config.json").read_text())

    def test_generation_and_disjoint_seeds(self):
        outputs = {}
        for stage in ["smoke", "pilot"]:
            data, req, meta = make_dataset(self.cfg, stage)
            self.assertTrue(validate(data, req, self.cfg, stage)["pass"])
            self.assertEqual((data, req, meta), make_dataset(self.cfg, stage))
            outputs[stage] = {r["seed"] for r in req}
            for r in req:
                if r["kind"] == "metadata":
                    self.assertNotIn("Private decision policy", r["prompt"])
                    self.assertNotIn("Signed weights", r["prompt"])
                    self.assertNotIn("strict priority order", r["prompt"])
        self.assertFalse(outputs["smoke"] & outputs["pilot"])

    def test_semantic_metamorphic(self):
        rng = random.Random(664831)
        checked = 0
        for _ in range(10000):
            p = {"kind": rng.choice(["weighted_sum", "lexicographic"]),
                 "weights": [rng.randint(-7, 7) for _ in range(4)],
                 "priority": rng.sample(list(range(4)), 4), "directions": [rng.choice([-1, 1]) for _ in range(4)]}
            options = [[rng.randint(-12, 12) for _ in range(4)] for _ in range(2)]
            try:
                d = decision(p, options)
            except ValueError:
                with self.assertRaises(ValueError): contrast_decision(p, options)
                continue
            self.assertEqual(d, contrast_decision(p, options))
            self.assertEqual(1 - d, decision(p, options[::-1]))
            shift = [rng.randint(-10, 10) for _ in range(4)]
            shifted = [[x + s for x, s in zip(o, shift)] for o in options]
            self.assertEqual(d, decision(p, shifted))
            checked += 1
        self.assertGreater(checked, 9900)

    def test_parser_fail_closed(self):
        for text in ["0", "1", " 0\n"]:
            self.assertIsNotNone(parse_answer(text))
        for text in ["Option 0", "0.", "1 because", "01", "<think>0</think>1", "", "2"]:
            self.assertIsNone(parse_answer(text))

    def test_selector_rejects_truth_and_uses_only_prefix(self):
        rows = [{"profile_id": "p", "group_index": 0, "preference_index": j,
                 "format": f, "replicate": r, "answer": (0 if f == "A" else r % 2)}
                for j in range(4) for f in ["A", "B"] for r in range(8)]
        result = observation_only_selector(rows)
        changed = copy.deepcopy(rows)
        for r in changed:
            if r["preference_index"] >= 2 or r["replicate"] >= 4:
                r["answer"] = None
        self.assertEqual(result, observation_only_selector(changed))
        self.assertEqual(result[("p", 0)], 0)
        changed[0]["theta"] = 0
        with self.assertRaises(ValueError): observation_only_selector(changed)

    def test_analysis_full_denominator_and_incomplete_gate(self):
        # Explicit fabricated unit-test fixture, confined to a temporary directory.
        # This is never used as Qwen evidence or written into experiment runs/.
        import analyze
        data, requests, _ = make_dataset(self.cfg, "pilot")
        truth = {r["preference_id"]: r["theta"] for r in data}
        with tempfile.TemporaryDirectory(prefix="lha_unit_fixture_") as tmp:
            root = Path(tmp)
            (root / "data/pilot").mkdir(parents=True)
            (root / "runs/pilot").mkdir(parents=True)
            cfg = {**self.cfg, "bootstrap_resamples": 100}
            write_json(root / "config.json", cfg)
            write_json(root / "freeze.json", {"unit_test_fixture": True})
            freeze_sha = sha((root / "freeze.json").read_bytes())
            write_jsonl(root / "data/pilot/private_truth.jsonl", data)
            write_jsonl(root / "data/pilot/requests.jsonl", requests)
            fake = []
            for r in requests[:-1]:
                answer = r["option_order"].index(truth[r["preference_id"]]) if r["kind"] == "task" else 0
                fake.append({**r, "status": "valid", "raw_output": str(answer), "parsed_answer": answer,
                             "freeze_sha256": freeze_sha})
            write_jsonl(root / "runs/pilot/raw.jsonl", fake)
            with patch.object(analyze, "ROOT", root), patch("sys.argv", ["analyze.py", "pilot"]), patch("builtins.print"):
                analyze.main()
            result = json.loads((root / "runs/pilot/analysis.json").read_text())
            self.assertEqual(result["decision"], "INCOMPLETE_NO_SCIENTIFIC_DECISION")
            self.assertEqual(result["coverage"]["planned"], 3264)
            self.assertEqual(result["coverage"]["attempted"], 3263)
            scored = (root / "runs/pilot/scored.jsonl").read_text().splitlines()
            self.assertEqual(len(scored), 3264)


if __name__ == "__main__":
    unittest.main()
