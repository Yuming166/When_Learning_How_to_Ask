"""Clustered discovery analysis. Audit labels never enter the observation-only selector."""
import argparse
import json
from collections import Counter

import numpy as np

from design import ROOT, parse_answer, read_jsonl, sha, write_json, write_jsonl


def observation_only_selector(rows):
    allowed = {"profile_id", "group_index", "preference_index", "format", "replicate", "answer"}
    counts = {}
    for r in rows:
        if set(r) != allowed:
            raise ValueError("Selector requires an explicit label-free observation projection")
        if r["preference_index"] >= 2 or r["replicate"] >= 4:
            continue
        key = (r["profile_id"], r["group_index"], r["preference_index"], r["format"])
        c = counts.setdefault(key, [0, 0])
        if r["answer"] is not None:
            c[r["answer"]] += 1
    result = {}
    for pid, gi, _, _ in counts:
        scores = []
        for fmt in ["A", "B"]:
            value = 0.
            for ji in range(2):
                n0, n1 = counts.get((pid, gi, ji, fmt), [0, 0])
                # Pairwise signed answer agreement, 4 planned responses; invalids contribute zero.
                value += ((n1 - n0)**2 - n0 - n1) / 12
            scores.append(value / 2)
        result[(pid, gi)] = int(scores[1] > scores[0])
    return result


def interval(values, draws, alpha=.05):
    samples = np.asarray(values)[draws].mean(axis=1)
    lo, hi = np.quantile(samples, [alpha / 2, 1 - alpha / 2])
    return {"mean": float(np.mean(values)), "low": float(lo), "high": float(hi)}


def selected(means, choices):
    return np.take_along_axis(means, choices[..., None], axis=-1)[..., 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["smoke", "pilot"])
    args = ap.parse_args()
    cfg = json.loads((ROOT / "config.json").read_text())
    out = ROOT / "runs" / args.stage
    requests = read_jsonl(ROOT / "data" / args.stage / "requests.jsonl")
    raw = read_jsonl(out / "raw.jsonl") if (out / "raw.jsonl").exists() else []
    private = read_jsonl(ROOT / "data" / args.stage / "private_truth.jsonl")
    truth = {r["preference_id"]: r["theta"] for r in private}
    lookup = {r["request_id"]: r for r in raw}
    assert len(lookup) == len(raw), "Duplicate response IDs"
    assert set(lookup) <= {r["request_id"] for r in requests}, "Unexpected request"
    frozen_hash = sha((ROOT / "freeze.json").read_bytes())
    assert all(r["freeze_sha256"] == frozen_hash for r in raw), "Mixed freezes"
    scored, projected = [], []
    for req in requests:
        r = lookup.get(req["request_id"], {**req, "status": "unattempted", "parsed_answer": None})
        answer = r.get("parsed_answer")
        if r["status"] == "valid":
            assert parse_answer(r["raw_output"]) == answer
        if r["kind"] == "task":
            canonical = r["option_order"][answer] if answer is not None else None
            scored.append({**r, "canonical_answer": canonical, "ground_truth": truth[r["preference_id"]],
                           "correct": canonical is not None and canonical == truth[r["preference_id"]]})
            projected.append({"profile_id": r["profile_id"], "group_index": r["group_index"],
                              "preference_index": r["preference_index"], "format": r["format"],
                              "replicate": r["replicate"], "answer": canonical})
        else:
            scored.append({**r, "chosen_format": r["format_order"][answer] if answer is not None else None})
    write_jsonl(out / "scored.jsonl", scored)
    write_jsonl(out / "selector_observations.jsonl", projected)
    counts = {kind: dict(Counter(r["status"] for r in scored if r["kind"] == kind))
              for kind in ["task", "direct", "metadata"]}
    coverage = {"planned": len(requests), "attempted": len(raw), "by_kind": counts,
                "valid": sum(r["status"] == "valid" for r in scored),
                "task_correct": sum(r.get("correct", False) for r in scored),
                "task_planned": sum(r["kind"] == "task" for r in scored)}
    if args.stage == "smoke":
        write_json(out / "analysis.json", {"coverage": coverage, "inference": "No scientific inference from smoke"})
        print(json.dumps(coverage)); return
    pids = sorted({r["profile_id"] for r in private})
    pi = {p: i for i, p in enumerate(pids)}
    n = len(pids)
    score = np.zeros((n, 2, 4, 2, 8))
    answer = np.full_like(score, np.nan)
    choices = {k: np.full((n, 2, 2), -1, dtype=int) for k in ["direct", "metadata"]}
    for r in scored:
        i, g = pi[r["profile_id"]], r["group_index"]
        if r["kind"] == "task":
            j, f, rep = r["preference_index"], int(r["format"] == "B"), r["replicate"]
            score[i, g, j, f, rep] = int(r["correct"])
            if r["canonical_answer"] is not None:
                answer[i, g, j, f, rep] = r["canonical_answer"]
        elif r["chosen_format"] is not None:
            choices[r["kind"]][i, g, r["template_index"]] = int(r["chosen_format"] == "B")
    # The primary transfer comparison holds out BOTH preferences and paraphrases.
    cal = score[:, :, :2, :, :4].mean(axis=(2, 4))
    test = score[:, :, 2:, :, 4:].mean(axis=(2, 4))
    half0 = score[:, :, :, :, :4].mean(axis=(2, 4))
    half1 = score[:, :, :, :, 4:].mean(axis=(2, 4))
    audited = (cal[..., 1] > cal[..., 0]).astype(int)
    observable = observation_only_selector(projected)
    agreement = np.array([[observable.get((p, g), 0) for g in range(2)] for p in pids])
    # Strong global-format audit reference: use other profiles' calibration labels only.
    global_choices = []
    for i in range(n):
        other = np.delete(cal, i, axis=0).mean(axis=(0, 1))
        global_choices.append(int(other[1] > other[0]))
    pooled = selected(test, np.repeat(np.array(global_choices)[:, None], 2, axis=1))
    fixed_a, fixed_b = test[..., 0], test[..., 1]
    # Alternating format at each response, with 2 held-out queries per format.
    rr = (score[:, :, 2:, 0, 4::2].mean(axis=(2, 3)) +
          score[:, :, 2:, 1, 5::2].mean(axis=(2, 3))) / 2
    strategies = {"Fixed_A": fixed_a, "Fixed_B": fixed_b, "Round_Robin": rr,
                  "LOPO_Global_Format_Audit_Reference": pooled,
                  "Observation_Only_Agreement": selected(test, agreement),
                  "Labelled_Calibration_Oracle": selected(test, audited),
                  "Hindsight_Oracle_Reference": test.max(axis=2)}
    for kind in ["direct", "metadata"]:
        primary = choices[kind][:, :, 0]
        value = selected(test, np.maximum(primary, 0))
        strategies["Direct_Type_Query" if kind == "direct" else "Public_Metadata_Predictor"] = np.where(primary >= 0, value, 0.)
    # Shuffle calibration and test preference memberships separately inside each profile.
    # This keeps 2 calibration and 2 held-out preferences per pseudo-group, without outcome selection.
    shuffle_rng = np.random.default_rng(935711)
    shuffled = np.zeros((499, n))
    for perm in range(len(shuffled)):
        for i in range(n):
            citems = score[i, :, :2, :, :4].mean(axis=-1).reshape(4, 2)
            titems = score[i, :, 2:, :, 4:].mean(axis=-1).reshape(4, 2)
            ci, ti = shuffle_rng.permutation(4), shuffle_rng.permutation(4)
            values = []
            for g in range(2):
                cm = citems[ci[2*g:2*g+2]].mean(axis=0)
                tm = titems[ti[2*g:2*g+2]].mean(axis=0)
                values.append(tm[int(cm[1] > cm[0])])
            shuffled[perm, i] = np.mean(values)
    strategies["Shuffled_Group_Audit_Control"] = shuffled.mean(axis=0)[:, None]
    rng = np.random.default_rng(cfg["bootstrap_seed"])
    draws = rng.integers(0, n, size=(cfg["bootstrap_resamples"], n))
    baseline_summary = {name: interval(values.mean(axis=1), draws) for name, values in strategies.items()}
    a = strategies["Observation_Only_Agreement"].mean(axis=1)
    endpoints = {
        "replicated_gap_product": ((half0[..., 1] - half0[..., 0]) * (half1[..., 1] - half1[..., 0])).mean(axis=1),
        "labelled_transfer_minus_shuffled": strategies["Labelled_Calibration_Oracle"].mean(axis=1) - shuffled.mean(axis=0),
        "agreement_minus_global_reference": a - pooled.mean(axis=1),
        "agreement_minus_direct": a - strategies["Direct_Type_Query"].mean(axis=1),
        "agreement_minus_metadata": a - strategies["Public_Metadata_Predictor"].mean(axis=1),
    }
    family = {name: interval(values, draws, alpha=.05/cfg["simultaneous_comparisons"])
              for name, values in endpoints.items()}
    # These are joint development gates, not an effectiveness claim or confirmatory p-values.
    gates = {name: value["low"] > (0 if name == "replicated_gap_product" else cfg["practical_gain"])
             for name, value in family.items()}
    complete = len(raw) == len(requests) and all(r["status"] != "error" for r in scored)
    valid_yield = coverage["valid"] / len(requests)
    decision = "GO_TO_PHASE2_DESIGN" if complete and valid_yield >= .95 and all(gates.values()) else "REVISE_OR_NO_GO"
    if not complete:
        decision = "INCOMPLETE_NO_SCIENTIFIC_DECISION"
    groups, hits = [], {}
    for i, p in enumerate(pids):
        for g in range(2):
            cg, tg = cal[i, g, 1] - cal[i, g, 0], test[i, g, 1] - test[i, g, 0]
            group_private = next(r for r in private if r["profile_id"] == p and r["group_index"] == g)
            groups.append({"profile_id": p, "group_index": g, "domain": group_private["domain"],
                           "private_policy_kind_audit_only": group_private["policy"]["kind"],
                           "calibration_gap_B_minus_A": float(cg), "heldout_gap_B_minus_A": float(tg),
                           "audited_choice": "AB"[audited[i, g]], "agreement_choice": "AB"[agreement[i, g]],
                           "heldout_tie": bool(tg == 0),
                           "direct_choice": None if choices["direct"][i,g,0] < 0 else "AB"[choices["direct"][i,g,0]],
                           "metadata_choice": None if choices["metadata"][i,g,0] < 0 else "AB"[choices["metadata"][i,g,0]]})
    testgap = test[..., 1] - test[..., 0]
    eligible = testgap != 0
    for kind in ["direct", "metadata"]:
        c = choices[kind][:, :, 0]
        hit = ((testgap > 0) == (c == 1)) & (c >= 0)
        hits[kind] = {"hits": int((hit & eligible).sum()), "non_tie_groups": int(eligible.sum()),
                      "ties": int((~eligible).sum()), "all_groups": int(eligible.size),
                      "invalid_primary": int((c < 0).sum()),
                      "paraphrase_agreement": float(((choices[kind][:,:,0] == choices[kind][:,:,1]) &
                                                       (choices[kind][:,:,0] >= 0)).mean())}
    no_gap = int((testgap == 0).sum())
    same_answer_cells = np.isfinite(answer).all(axis=-1) & (np.nanmax(answer, axis=-1) == np.nanmin(answer, axis=-1))
    all_wrong = (score.sum(axis=-1) == 0) & np.isfinite(answer).all(axis=-1)
    failures = [r for r in scored if r["kind"] == "task" and not r["correct"]]
    # Fixed first 12 by request ID; never cherry-pick failure examples.
    examples = sorted(failures, key=lambda r: r["request_id"])[:12]
    result = {"decision": decision, "coverage": coverage, "valid_yield": valid_yield,
              "baseline_heldout_single_response_accuracy": baseline_summary,
              "five_primary_endpoints_simultaneous_95_intervals": family, "gates": gates,
              "type_prediction": hits, "group_counts": {"total": int(eligible.size), "heldout_ties": no_gap,
                  "heldout_A_better": int((testgap < 0).sum()), "heldout_B_better": int((testgap > 0).sum())},
              "persistent_error_audit": {"preference_format_cells": int(same_answer_cells.size),
                  "all_8_same_canonical_answer": int(same_answer_cells.sum()), "all_8_valid_wrong": int(all_wrong.sum()),
                  "interpretation": "Item heterogeneity and repeated misinterpretation; not proof of temporal dependence"},
              "shuffle_control": {"permutations": 499, "seed": 935711, "mean": float(shuffled.mean()),
                  "permutation_mean_range": [float(shuffled.mean(axis=1).min()), float(shuffled.mean(axis=1).max())]},
              "scope": "Development discovery; no human, full-agent, fixed-budget superiority or asymptotic claims",
              "inference_unit": "24 independent profiles, resampled with all their groups/items/responses",
              "labelled_oracles": "Audit-only; labelled calibration uses different preferences and templates; hindsight is optimistically biased",
              "costs": {"main_response_samples": 3072, "direct_report_samples": 96, "metadata_samples": 96,
                        "selector_prefix": "2 preferences/group * 2 formats * 4 responses = 16 task queries/group",
                        "comparison": "Held-out response reliability only; no equal-total-cost agent comparison"}}
    write_json(out / "analysis.json", result)
    write_jsonl(out / "group_diagnostics.jsonl", groups)
    write_jsonl(out / "failure_examples.jsonl", examples)
    # Standard static plotting; no model or network dependency.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    names = list(baseline_summary)
    means = [baseline_summary[k]["mean"] for k in names]
    axes[0].barh(range(len(names)), means)
    axes[0].set_yticks(range(len(names)), [k.replace("_", " ") for k in names], fontsize=7)
    axes[0].set_xlim(0, 1); axes[0].set_xlabel("Held-out single-response accuracy (full denominator)")
    axes[1].scatter([g["calibration_gap_B_minus_A"] for g in groups], [g["heldout_gap_B_minus_A"] for g in groups], alpha=.7)
    axes[1].axhline(0, color="grey", linewidth=.7); axes[1].axvline(0, color="grey", linewidth=.7)
    axes[1].set_xlabel("Calibration gap: B - A (first preferences/template)")
    axes[1].set_ylabel("Held-out gap: B - A (new preferences/template)")
    fig.tight_layout()
    fig.savefig(out / "discovery.png", dpi=160); fig.savefig(out / "discovery.pdf"); plt.close(fig)
    report = ["## Material Passport", "", "- Origin Skill: academic-research-suite / experiment-agent",
              "- Origin Mode: validate", "- Origin Date: 2026-10-30", "- Verification Status: ANALYZED",
              "- Version Label: phase01_v1", "", "# Pilot Report", "", f"**Decision: {decision}.**", "",
              f"Coverage: {len(raw)}/{len(requests)} attempted; {coverage['valid']} valid. Invalid/error/unattempted task outputs score zero.", "",
              "## Held-out reliability (not equal-cost agent performance)", "",
              "| Strategy | Accuracy | Profile bootstrap 95% interval |", "|---|---:|---:|"]
    for name, v in baseline_summary.items():
        report.append(f"| {name} | {100*v['mean']:.2f}% | [{100*v['low']:.2f}, {100*v['high']:.2f}] |")
    report += ["", "## Prespecified discovery gates", "", "Intervals below use Bonferroni 99% marginal intervals for five primary endpoints (95% family coverage target).",
               "Profile bootstrap remains approximate with 24 clusters.", "", "| Endpoint | Estimate | Interval | Pass |", "|---|---:|---:|---|"]
    for name, v in family.items():
        report.append(f"| {name} | {v['mean']:.4f} | [{v['low']:.4f}, {v['high']:.4f}] | {gates[name]} |")
    report += ["", "## Interpretation boundaries", "",
               "Both preferences and paraphrases are held out in the transfer analysis. The observation-only selector receives no correct answers or policy cards. "
               "Labelled-calibration and hindsight oracles are audit references. Hindsight chooses on the evaluation observations and is optimistically biased. "
               "Direct and metadata format reports have two independent prompt variants; variant 0 is prespecified primary. Tied held-out group labels are explicitly retained.", "",
               "There is no Phase 2 agent, training, 35B generation, confirmation set, or human study in this run. "
               "These 24 profiles are development data. Failure of the conservative discovery gate does not refute the mathematical theorems. "
               "The heterogeneous utility/priority tasks do not automatically satisfy common p,q or the iid channel model.", "",
               "## Statistical fallacy scan (11/11 assessed)", "",
               "| Risk | Disposition |", "|---|---|",
               "| Simpson | Aggregate and every group gap retained in group_diagnostics.jsonl. |",
               "| Ecological | Inference limited to simulated profiles; no human/individual generalization. |",
               "| Berkson | No performance-based profile filtering. |",
               "| Collider | No outcome-conditioned adjustment or subgroup selection. |",
               "| Base rate | Binary answer mapping balanced; all invalid/missing counts retained. |",
               "| Regression to mean | Discovery and validation use distinct observations and preferences. |",
               "| Survivorship | Full planned denominators; incomplete collection blocks scientific decision. |",
               "| Look-elsewhere | Five primary endpoints and all baselines retained, including negative outcomes. |",
               "| Forking paths | Protocol/source/data hashes frozen before smoke; no adaptive template search. |",
               "| Causality | No mechanism/causal attribution from the observed gaps. |",
               "| Reverse causality | All selectors use prespecified prefix or independent reports. |", "",
               "See analysis.json for type-report counts, repeated-error audit, costs and all gates; failure_examples.jsonl contains the first 12 failures in request-ID order."]
    (out / "PILOT_REPORT.md").write_text("\n".join(report) + "\n")
    print(json.dumps({"decision": decision, "coverage": coverage, "gates": gates, "baseline": baseline_summary}))


if __name__ == "__main__":
    main()
