"""Recompute all historical accuracy curves from outcome-only paired records."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = ["fixed_order", "profile_ig", "decision_set_ig", "decision_value"]


def main():
    manifest = json.loads((HERE / "SOURCE_MANIFEST.json").read_text())
    output = {}
    for label, source in manifest["exports"].items():
        path = HERE / source["trace"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
        rows = [json.loads(x) for x in gzip.decompress(path.read_bytes()).splitlines()]
        assert len(rows) == source["rows"]
        groups = collections.defaultdict(list)
        seen = set()
        for row in rows:
            key = (row["case_id"], row.get("panel_id"), row.get("replicate"), row["method"], row["budget"])
            assert key not in seen, (label, key)
            seen.add(key)
            if row["method"] in METHODS and isinstance(row["budget"], int) and 0 <= row["budget"] <= 6:
                groups[(row["method"], row["budget"])].append(row)
        curves = {}
        for method in METHODS:
            curves[method] = {}
            for budget in range(7):
                group = groups[(method, budget)]
                correct = sum(x["exact_decision_correct"] for x in group)
                curves[method][str(budget)] = {"correct": correct, "n": len(group), "accuracy": correct / len(group)}
        output[label] = {"unique_profiles": len({r["profile_id"] for r in rows}), "curves": curves}
    path = HERE / "results/RECOMPUTED.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    for label, d in output.items():
        print(label, d["unique_profiles"], {m: d["curves"][m]["5"] for m in METHODS})


if __name__ == "__main__":
    main()
