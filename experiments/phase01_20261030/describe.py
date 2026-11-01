"""Post-collection descriptive companion. No new tests, selection or primary gates."""
import json
from design import ROOT, read_jsonl, write_json


def main():
    out = ROOT / "runs/pilot"
    rows = read_jsonl(out / "scored.jsonl")
    groups = read_jsonl(out / "group_diagnostics.jsonl")
    private = {r["preference_id"]: r for r in read_jsonl(ROOT / "data/pilot/private_truth.jsonl")}
    summary = {"scope": "Post-collection descriptive companion; no new hypothesis tests or changed primary gates",
               "by_format": {}, "by_private_policy_kind_audit_only": {}}
    for fmt in ["A", "B"]:
        rr = [r for r in rows if r["kind"] == "task" and r["format"] == fmt]
        summary["by_format"][fmt] = {"correct": sum(r["correct"] for r in rr), "total": len(rr),
                                     "accuracy": sum(r["correct"] for r in rr) / len(rr)}
    for kind in ["weighted_sum", "lexicographic"]:
        rr = [r for r in rows if r["kind"] == "task" and private[r["preference_id"]]["policy"]["kind"] == kind]
        summary["by_private_policy_kind_audit_only"][kind] = {
            "groups": len({r["group_id"] for r in rr}), "correct": sum(r["correct"] for r in rr),
            "total": len(rr), "accuracy": sum(r["correct"] for r in rr) / len(rr)}
    non_tie = [r for r in groups if r["calibration_gap_B_minus_A"] != 0 and r["heldout_gap_B_minus_A"] != 0]
    summary["transfer_direction"] = {
        "same_direction": sum((r["calibration_gap_B_minus_A"] > 0) == (r["heldout_gap_B_minus_A"] > 0) for r in non_tie),
        "non_tie_both": len(non_tie), "all_groups": 48,
        "calibration_ties": sum(r["calibration_gap_B_minus_A"] == 0 for r in groups),
        "heldout_ties": sum(r["heldout_gap_B_minus_A"] == 0 for r in groups)}
    paired = {}
    for r in rows:
        if r["kind"] == "task":
            paired.setdefault((r["preference_id"], r["replicate"]), {})[r["format"]] = r
    lengths = [v["B"]["input_tokens"] - v["A"]["input_tokens"] for v in paired.values()]
    summary["format_order_and_length"] = {
        "paired_evidence_equal": all(v["A"]["evidence_sha256"] == v["B"]["evidence_sha256"] for v in paired.values()),
        "token_gap_B_minus_A_min": min(lengths), "token_gap_B_minus_A_max": max(lengths),
        "output_digit_counts": {str(k): sum(r["kind"] == "task" and r["parsed_answer"] == k for r in rows) for k in [0, 1]}}
    write_json(out / "descriptive_companion.json", summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
