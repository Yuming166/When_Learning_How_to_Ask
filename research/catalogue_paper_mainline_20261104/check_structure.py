"""Exact bounded manuscript structure checks; Python standard library only.

No optimizer, random sampling, model, network, or historical-file writes.
Run: python -B research/catalogue_paper_mainline_20261104/check_structure.py
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CATALOGUES = {
    "weighted5": {
        "rows": [(0, 0, 0, 0, 0, 0), (0, 3, 2, 2, 1, 1)],
        "family": [(1, 2), (1, 3), (2, 3, 4), (2, 3, 5), (1, 4, 5)],
        "primal": [Q(3, 9), Q(2, 9), Q(2, 9), Q(1, 9), Q(1, 9)],
        "dual": [Q(1, 9), Q(1, 9), Q(2, 9), Q(2, 9), Q(3, 9)],
        "rho": Q(5, 9),
        "winner_counts": [16, 16],
    },
    "genuine6": {
        "rows": [(0, 0, 0, 0, 0, 0, 0),
                 (0, -6, -4, -4, -2, -2, 0),
                 (-1, 0, -2, -2, -4, -4, -8)],
        "family": [(1, 2), (1, 3), (2, 3, 4), (2, 3, 5),
                   (1, 4, 5), (2, 3, 6), (4, 6), (5, 6)],
        "primal": [Q(3, 13), Q(2, 13), Q(2, 13), Q(1, 13), Q(1, 13), Q(4, 13)],
        "dual": [Q(2, 13), Q(2, 13), Q(3, 26), Q(3, 26),
                 Q(1, 13), Q(0), Q(5, 26), Q(5, 26)],
        "rho": Q(5, 13),
        "winner_counts": [20, 21, 23],
    },
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def mask(indices):
    return sum(1 << (j - 1) for j in indices)


def indices(value, d):
    return [j + 1 for j in range(d) if value & (1 << j)]


def fractions(values):
    return [str(v) for v in values]


def cube_check(name, spec):
    rows = spec["rows"]
    d = len(rows[0]) - 1
    require(all(len(row) == d + 1 for row in rows), name + ": row lengths")
    winners, gaps = [], []
    for flipped in range(1 << d):
        signs = [-1 if flipped & (1 << j) else 1 for j in range(d)]
        values = [Q(row[0]) + sum(Q(v) * s for v, s in zip(row[1:], signs))
                  for row in rows]
        best = max(values)
        require(values.count(best) == 1, name + ": cube winner tie")
        winner = values.index(best)
        winners.append(winner)
        gaps.append(min(best - value for k, value in enumerate(values) if k != winner))
    counts = [winners.count(i) for i in range(len(rows))]
    require(counts == spec["winner_counts"], name + ": winner counts")
    require(all(counts), name + ": inactive catalogue item")
    wrong = [m for m in range(1, 1 << d) if winners[m] != winners[0]]
    minimal = [m for m in wrong if not any(n != m and n & m == n for n in wrong)]
    expected = [mask(edge) for edge in spec["family"]]
    require(minimal == expected, name + ": minimal wrong sets")
    relevance = []
    for j in range(d):
        witness = next((m for m in range(1 << d)
                        if winners[m] != winners[m ^ (1 << j)]), None)
        require(witness is not None, name + ": irrelevant coordinate")
        relevance.append({"coordinate": j + 1, "before_flips": indices(witness, d),
                          "before_winner": winners[witness],
                          "after_winner": winners[witness ^ (1 << j)]})
    return {"dimension": d, "cube_size": 1 << d, "unique_winners": True,
            "winner_counts": counts, "reference_winner": winners[0],
            "minimum_winner_gap": str(min(gaps)),
            "minimal_flip_sets": [indices(m, d) for m in minimal],
            "minimal_flip_winners": [winners[m] for m in minimal],
            "all_coordinates_relevant": True, "relevance_witnesses": relevance}


def exact_cover(spec, support=None, primal=None, dual=None, expected=None):
    d = len(spec["rows"][0]) - 1
    support = list(range(1, d + 1)) if support is None else list(support)
    primal = list(spec["primal"] if primal is None else primal)
    dual = list(spec["dual"] if dual is None else dual)
    expected = spec["rho"] if expected is None else expected
    family = spec["family"]
    require(len(primal) == d and len(dual) == len(family), "cover witness lengths")
    require(sum(primal) == sum(dual) == 1, "cover witness normalization")
    require(min(primal) >= 0 and min(dual) >= 0, "negative cover witness")
    require(all(primal[j - 1] == 0 for j in range(1, d + 1) if j not in support),
            "primal outside restricted support")
    coverages = [sum(primal[j - 1] for j in edge) for edge in family]
    loads = [sum(weight for edge, weight in zip(family, dual) if j in edge)
             for j in range(1, d + 1)]
    lower = min(coverages)
    upper = max(loads[j - 1] for j in support)
    require(lower == upper == expected, "primal/dual cover bounds differ")
    # For every supported distribution v, min_F v(F) <= sum_j v_j load_j <= upper.
    return {"support": support, "value": str(expected), "primal": fractions(primal),
            "dual": fractions(dual), "primal_coverages": fractions(coverages),
            "dual_coordinate_loads": fractions(loads),
            "exact_matching_primal_dual_bounds": True}


def exact_unique_cover(spec):
    """Dual-positive tight equations force the displayed weight, over Q."""
    d = len(spec["primal"])
    active = [edge for edge, weight in zip(spec["family"], spec["dual"]) if weight > 0]
    matrix = [[Q(int(j in edge)) for j in range(1, d + 1)] + [spec["rho"]]
              for edge in active]
    pivot_row, pivots = 0, []
    for column in range(d):
        found = next((r for r in range(pivot_row, len(matrix)) if matrix[r][column]), None)
        if found is None:
            continue
        matrix[pivot_row], matrix[found] = matrix[found], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [value / divisor for value in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r != pivot_row:
                factor = matrix[r][column]
                matrix[r] = [a - factor * b for a, b in zip(matrix[r], matrix[pivot_row])]
        pivots.append(column)
        pivot_row += 1
    require(pivot_row == d and pivots == list(range(d)), "active cover rank is not full")
    require(all(any(row[:d]) or row[-1] == 0 for row in matrix), "inconsistent active system")
    solution = [matrix[r][-1] for r in range(d)]
    require(solution == spec["primal"], "unique cover solution differs")
    require(all(value > 0 for value in solution), "cover is not full support")
    return {"dual_positive_edges": [list(edge) for edge in active],
            "exact_active_incidence_rank": pivot_row, "dimension": d,
            "unique_cover_weight": fractions(solution), "full_support": True,
            "proof": "Matching primal/dual bounds force every dual-positive edge tight; "
                     "the exact rank-d tight system has the unique displayed solution."}


def main(output=None):
    catalogue_records = {}
    for name, spec in CATALOGUES.items():
        record = cube_check(name, spec)
        record["global_cover"] = exact_cover(spec)
        catalogue_records[name] = record
    weighted = CATALOGUES["weighted5"]
    restricted = {
        "12": exact_cover(weighted, [1, 2],
                          [Q(1, 2), Q(1, 2), Q(0), Q(0), Q(0)],
                          [Q(0), Q(1, 2), Q(0), Q(1, 2), Q(0)], Q(1, 2)),
        "345": exact_cover(weighted, [3, 4, 5],
                           [Q(0), Q(0), Q(1), Q(0), Q(0)],
                           [Q(1), Q(0), Q(0), Q(0), Q(0)], Q(0)),
        "14": exact_cover(weighted, [1, 4],
                          [Q(1), Q(0), Q(0), Q(0), Q(0)],
                          [Q(0), Q(0), Q(0), Q(1), Q(0)], Q(0)),
        "235": exact_cover(weighted, [2, 3, 5],
                           [Q(0), Q(1, 3), Q(1, 3), Q(0), Q(1, 3)],
                           [Q(1, 3), Q(1, 3), Q(0), Q(0), Q(1, 3)], Q(1, 3)),
    }
    catalogue_records["weighted5"]["restricted_covers"] = restricted
    unique = exact_unique_cover(CATALOGUES["genuine6"])
    catalogue_records["genuine6"]["uniqueness"] = unique
    require(weighted["rho"] >= Q(1, 2), "weighted5 not saturated")
    require(CATALOGUES["genuine6"]["rho"] < Q(1, 2), "genuine6 not unsaturated")
    cells = []
    for groups, expected in [([[1, 2], [3, 4, 5]], "ZERO"),
                             ([[1, 4], [2, 3, 5]], "POSITIVE")]:
        values = [Q(restricted["".join(map(str, group))]["value"]) for group in groups]
        zero = max(values) >= Q(1, 2)
        require(("ZERO" if zero else "POSITIVE") == expected, "weighted cell boundary")
        cells.append({"catalogue": "weighted5", "groups": groups, "group_sizes": list(map(len, groups)),
                      "restricted_covers": fractions(values), "premium": expected,
                      "criterion": "saturated: some group restricted cover >= 1/2",
                      "structural_criterion_verified": True})
    for groups, expected in [([list(range(1, 7))], "ZERO"),
                             ([[1, 2, 3], [4, 5, 6]], "POSITIVE")]:
        support = {j + 1 for j, value in enumerate(CATALOGUES["genuine6"]["primal"]) if value}
        zero = any(support <= set(group) for group in groups)
        require(("ZERO" if zero else "POSITIVE") == expected, "genuine cell boundary")
        cells.append({"catalogue": "genuine6", "groups": groups, "group_sizes": list(map(len, groups)),
                      "premium": expected,
                      "criterion": "unsaturated unique cover: full positive support contained in one group",
                      "structural_criterion_verified": True})
    require(cells[0]["group_sizes"] == cells[1]["group_sizes"], "group-size control differs")
    # One explicit binding imbalance witnesses failure at the unique genuine6 optimum.
    w = CATALOGUES["genuine6"]["primal"]
    group, edge = {1, 2, 3}, {1, 2}
    mass = sum(w[j - 1] for j in group)
    flipped = sum(w[j - 1] for j in group & edge)
    required = CATALOGUES["genuine6"]["rho"] * mass
    require(sum(w[j - 1] for j in edge) == CATALOGUES["genuine6"]["rho"], "edge not binding")
    require(flipped != required, "split unexpectedly balances binding edge")
    report = {
        "status": "PASS", "date": "2026-11-04", "arithmetic": "Python int and fractions.Fraction only",
        "scope": "Four fixed manuscript cells; structural theorem conditions, not empirical method efficacy",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "historical_witness_source": "research/general_catalogue_theory_20261103/CATALOGUE_EXAMPLES.md",
        "catalogues": catalogue_records, "cells": cells,
        "genuine6_split_binding_imbalance": {"group": sorted(group), "binding_flip": sorted(edge),
            "group_mass": str(mass), "flipped_mass": str(flipped), "required_balanced_mass": str(required)},
        "claims": {"full_cube_unique_winners": True, "all_coordinates_relevant": True,
            "exact_minimal_flips": True, "matching_exact_cover_witnesses": True,
            "genuine6_unique_cover": True, "weighted5_restricted_covers": True,
            "four_theorem_conditions": True, "same_size_opposite_premiums": True},
        "not_performed": ["optimizer search", "entropy-prefix numerical comparisons", "statistical inference",
                          "response collection", "model/API/network/GPU calls", "finite-cost or efficiency certification"],
        "interpretation": "ZERO/POSITIVE conclusions invoke the audited catalogue premium theorems at alpha=0, "
                          "for any fixed allowed strict q<p; they are not floating coefficient estimates.",
    }
    destination = HERE / "STRUCTURE_CHECKS.json" if output is None else Path(output)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "catalogues": len(catalogue_records),
                      "cube_states": sum(r["cube_size"] for r in catalogue_records.values()),
                      "cells": len(cells), "output": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    main(parser.parse_args().output)
