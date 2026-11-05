import json
import unittest
from pathlib import Path

import luna_48_policy_comparison as run


class Luna48ProfileTests(unittest.TestCase):
    def test_frozen_input_inventory(self):
        profiles = run.read_rows(run.PRIVATE / "profiles.jsonl")
        menus = run.read_rows(run.PUBLIC / "menus.jsonl")
        cases = run.read_rows(run.PRIVATE / "selected_cases.jsonl")
        jobs = run.read_rows(run.PRIVATE / "jobs.jsonl")
        self.assertEqual(len(profiles), 48)
        self.assertEqual(len({p["profile_id"] for p in profiles}), 48)
        self.assertEqual(len(menus), 35)
        self.assertEqual(len(cases), 280)
        self.assertEqual(len(jobs), 288)
        self.assertEqual(len({j["job_id"] for j in jobs}), 288)
        self.assertEqual(len({p["profile_id"] for p in profiles if p["pool_index"] == 0}), 8)

    def test_all_profile_fields_have_well_formed_templates(self):
        profiles = {p["profile_id"]: p for p in run.read_rows(run.PRIVATE / "profiles.jsonl")}
        vocab = run.read(run.PUBLIC / "vocabularies.json")
        prompts = {p["job_id"]: p for p in run.read_rows(run.PROMPTS / "requests.jsonl")}
        jobs = run.read_rows(run.PRIVATE / "jobs.jsonl")
        self.assertEqual(len(prompts), len(jobs))
        for job in jobs:
            profile = profiles[job["profile_id"]]
            expected = run.ref.ReferenceUser(profile).answer(job["query_action"])
            parsed = run.parse_field_answer(
                job["query_action"], json.dumps(expected, ensure_ascii=False),
                vocab[str(profile["pool_index"])], run.read(run.LEGACY / "config.json")["purchase_thresholds"])
            self.assertEqual(run.canonical(parsed), run.canonical(expected))
            self.assertEqual(prompts[job["job_id"]]["prompt_sha256"],
                             run.hashlib.sha256(prompts[job["job_id"]]["prompt"].encode()).hexdigest())

    def test_smoke_replay_accepts_multiple_history_entries(self):
        profiles = {p["profile_id"]: p for p in run.read_rows(run.PRIVATE / "profiles.jsonl")}
        menus = {m["menu_id"]: m for m in run.read_rows(run.PUBLIC / "menus.jsonl")}
        vocab = run.read(run.PUBLIC / "vocabularies.json")
        priors = run.read_rows(run.PRIVATE / "prior_profiles.jsonl")
        case_row = next(c for c in run.read_rows(run.PRIVATE / "selected_cases.jsonl")
                        if c["profile_id"] == run.CFG["smoke_profile_id"])
        profile = profiles[case_row["profile_id"]]
        bank = {}
        for action in run.CFG["query_actions"]:
            answer = run.ref.ReferenceUser(profile).answer(action)
            bank[(action, 1)] = {"valid": True, "parsed": {"value": answer},
                                 "exact_profile_match": True}
        prior = [p for p in priors if p["pool_index"] == profile["pool_index"]]
        case = {**case_row, "public_menu": menus[case_row["menu_id"]]}
        for method in run.CFG["methods"]:
            trace = run._case_trace(run.engine.load_environment(run.WORKTREE), case, profile,
                                    prior, method, 1, bank, vocab[str(profile["pool_index"])],
                                    run.read(run.LEGACY / "config.json")["purchase_thresholds"])
            self.assertEqual(len(trace), 7)
            self.assertTrue(all(row["answer_path_complete"] for row in trace))
            self.assertTrue(trace[-1]["exact_decision_correct"])


if __name__ == "__main__":
    unittest.main()
