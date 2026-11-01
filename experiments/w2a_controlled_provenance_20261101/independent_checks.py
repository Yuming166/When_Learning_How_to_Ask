"""Independent exact-rational W2a verifier; no network or model clients.

The reference DP retains root creation order. It does not import the parent
engine, canonicalize/sort root states, or use realized theta/V in its actions.
Small fixed designs also have an independent explicit latent-variable sum.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from math import comb, prod
from pathlib import Path
import hashlib
import importlib.util

ROOT = Path(__file__).resolve().parent


def fraction(value):
    return value if isinstance(value, F) else F(str(value))


def encoded(value):
    value = fraction(value)
    return {"fraction": str(value), "float": float(value)}


def single_read_correctness(r, a):
    r, a = fraction(r), fraction(a)
    return r * a + (1 - r) * (1 - a)


def count_design_risk(depths, r=F(3, 4), a=F(4, 5)):
    """Exact Bayes error of fixed root depths, integrating latent root reports.

    No independence is asserted between answers from the same root. Each
    count's binomial multiplicity is included once, outside its likelihood.
    """
    r, a = fraction(r), fraction(a)
    depths = tuple(depths)
    if any(d < 1 for d in depths):
        raise ValueError("Every activated root must have at least one read")
    risk = F(0)
    for counts in product(*(range(d + 1) for d in depths)):
        masses = []
        multiplicity = prod(comb(d, k) for d, k in zip(depths, counts))
        for theta in (0, 1):
            mass = F(1, 2)
            for d, k in zip(depths, counts):
                root_one = r if theta else 1 - r
                mass *= (root_one * a**k * (1-a)**(d-k)
                         + (1-root_one) * (1-a)**k * a**(d-k))
            masses.append(mass)
        risk += multiplicity * min(masses)
    return risk


def latent_enumerated_risk(depths, r=F(3, 4), a=F(4, 5),
                           persistent_extraction=False):
    """Independent theta/V/Y enumeration of ordered raw response histories.

    With persistent_extraction=True, each root additionally draws one reading
    error bit, reused on all its reads. This deliberately violates the main
    conditional-independent extraction law.
    """
    r, a = fraction(r), fraction(a)
    depths = tuple(depths)
    roots = len(depths)
    history_masses = defaultdict(lambda: [F(0), F(0)])
    owner = tuple(i for i, depth in enumerate(depths) for _ in range(depth))
    for theta in (0, 1):
        for reports in product((0, 1), repeat=roots):
            source_mass = F(1, 2) * prod(r if v == theta else 1-r
                                       for v in reports)
            if persistent_extraction:
                for errors in product((0, 1), repeat=roots):
                    mass = source_mass * prod(a if not e else 1-a for e in errors)
                    history = tuple(reports[i] ^ errors[i] for i in owner)
                    history_masses[history][theta] += mass
            else:
                for history in product((0, 1), repeat=len(owner)):
                    mass = source_mass * prod(a if y == reports[i] else 1-a
                                               for y, i in zip(history, owner))
                    history_masses[history][theta] += mass
    assert sum(sum(m) for m in history_masses.values()) == 1
    return sum(min(m) for m in history_masses.values())


def unsorted_root_bellman(budget, activation_cost=0, r=F(3, 4), a=F(4, 5),
                          include_reachable_policy=False):
    """Minimum expected terminal error over all observation-adapted actions.

    State is the ordered tuple of (ones, zeros) for roots in creation order.
    Visiting a page copy is the same action as revisiting its root. Opening a
    fresh root and taking its first answer costs c+1. Existing-root reads cost
    1. Early stopping is available with the correct common posterior decoder.
    """
    r, a = fraction(r), fraction(a)
    if budget < 0 or activation_cost < 0:
        raise ValueError("Costs and budget must be nonnegative")
    choices = {}

    @lru_cache(None)
    def theta_masses(state):
        out = []
        for theta in (0, 1):
            mass = F(1, 2)
            root_one = r if theta else 1-r
            for ones, zeros in state:
                mass *= (root_one * a**ones * (1-a)**zeros
                         + (1-root_one) * (1-a)**ones * a**zeros)
            out.append(mass)
        return tuple(out)

    @lru_cache(None)
    def solve(state, remaining):
        masses = theta_masses(state)
        denominator = sum(masses)
        if not denominator:
            return F(0)  # impossible history, zero predictive mass
        best = min(masses) / denominator
        chosen = None
        actions = [(i, 1) for i in range(len(state))] if remaining >= 1 else []
        if remaining >= activation_cost + 1:
            actions.append((len(state), activation_cost + 1))
        for root, cost in actions:
            value = F(0)
            predictive_sum = F(0)
            for answer in (0, 1):
                next_state = list(state)
                if root == len(state):
                    next_state.append((answer, 1-answer))
                else:
                    ones, zeros = next_state[root]
                    next_state[root] = (ones+answer, zeros+1-answer)
                next_state = tuple(next_state)  # intentionally NEVER sorted
                prediction = sum(theta_masses(next_state)) / denominator
                predictive_sum += prediction
                value += prediction * solve(next_state, remaining-cost)
            assert predictive_sum == 1
            if value < best:
                best, chosen = value, (root, cost)
        choices[state, remaining] = chosen
        return best

    risk = solve((), budget)
    result = {"risk": risk, "states": solve.cache_info().currsize,
              "root_order": "creation_order_not_canonicalized"}
    if include_reachable_policy:
        queue = [((), budget)]
        visited, records = set(), []
        while queue:
            state, remaining = queue.pop(0)
            if (state, remaining) in visited:
                continue
            visited.add((state, remaining))
            choice = choices[state, remaining]
            record = {"ordered_root_counts": state, "remaining": remaining,
                      "optimal_conditional_risk": encoded(solve(state, remaining)),
                      "action": "STOP" if choice is None else
                          "NEW_ROOT" if choice[0] == len(state) else "READ_EXISTING_ROOT",
                      "root_index": None if choice is None else choice[0],
                      "action_cost": 0 if choice is None else choice[1],
                      "transitions": []}
            if choice is not None:
                root, cost = choice
                for answer in (0, 1):
                    nxt = list(state)
                    if root == len(state):
                        nxt.append((answer, 1-answer))
                    else:
                        ones, zeros = nxt[root]
                        nxt[root] = (ones+answer, zeros+1-answer)
                    nxt = tuple(nxt)
                    probability = sum(theta_masses(nxt))/sum(theta_masses(state))
                    if probability:
                        record['transitions'].append({"answer": answer,
                            "probability": encoded(probability), "next_root_counts": nxt,
                            "next_remaining": remaining-cost})
                        queue.append((nxt, remaining-cost))
            records.append(record)
        result['reachable_optimal_policy'] = records
    return result


def page_schedule_joint(page_sequence, declared_page_roots, r=F(3, 4), a=F(4, 5)):
    """Full theta/history law, enumerated via page IDs and their declared roots."""
    r, a = fraction(r), fraction(a)
    roots = list(dict.fromkeys(declared_page_roots[p] for p in page_sequence))
    positions = {root: i for i, root in enumerate(roots)}
    result = defaultdict(lambda: [F(0), F(0)])
    for theta in (0, 1):
        for reports in product((0, 1), repeat=len(roots)):
            pm = F(1, 2)*prod(r if v == theta else 1-r for v in reports)
            for answers in product((0, 1), repeat=len(page_sequence)):
                mass = pm
                for page, answer in zip(page_sequence, answers):
                    report = reports[positions[declared_page_roots[page]]]
                    mass *= a if answer == report else 1-a
                result[answers][theta] += mass
    assert sum(sum(m) for m in result.values()) == 1
    return dict(result)


def fixed_budget_risks(budget, cost, r=F(3, 4), a=F(4, 5)):
    repeat_depth = max(0, budget-cost)
    repeat = count_design_risk((repeat_depth,) if repeat_depth else (), r, a)
    fresh_count = budget // (cost+1)
    fresh = count_design_risk((1,)*fresh_count, r, a)
    candidates = []
    for depth in range(1, budget+1):
        roots = budget // (cost+depth)
        if roots:
            candidates.append((count_design_risk((depth,)*roots, r, a), depth, roots))
    best = min(candidates, default=(F(1, 2), None, 0))
    return {"repeat": repeat, "copies": repeat, "fresh": fresh,
            "best_fixed_completed_depth": best[0],
            "one_best_depth": best[1], "completed_roots": best[2]}


def compositions(total):
    if total == 0:
        yield ()
    else:
        for first in range(1, total+1):
            for tail in compositions(total-first):
                yield (first,)+tail


def exhaustive_static_risk(budget, cost, r, a):
    """All within-budget ordered compositions, deduplicated after construction.

    Unlike the parent enumerator, include allocations that leave budget unused.
    This independently checks its harmless-full-spending reduction.
    """
    allocations = {()}
    for reads in range(1, budget+1):
        for depths in compositions(reads):
            if reads+cost*len(depths) <= budget:
                allocations.add(tuple(sorted(depths)))
    values = [(count_design_risk(depths, r, a), sum(depths)+cost*len(depths), depths)
              for depths in allocations]
    risk, spent, depths = min(values)
    return {"risk": risk, "one_optimal_depths": depths, "spent": spent,
            "allocations_including_unspent": len(allocations)}


def exact_naive_confidence(n, r, a, delta=F(1, 20)):
    """Evaluate the wrong URL-iid confidence under the actual one-root law."""
    r, a = fraction(r), fraction(a)
    b = single_read_correctness(r, a)
    coverage = error_mass = confidence_mass = F(0)
    for ones in range(n+1):
        f, g = a**ones*(1-a)**(n-ones), (1-a)**ones*a**(n-ones)
        plus, minus = r*f+(1-r)*g, (1-r)*f+r*g
        evidence = F(comb(n, ones), 2)*(plus+minus)
        if not evidence:
            continue
        wrong_plus = b**ones*(1-b)**(n-ones)
        wrong_minus = (1-b)**ones*b**(n-ones)
        wrong_confidence = max(wrong_plus, wrong_minus)/(wrong_plus+wrong_minus)
        if wrong_confidence >= 1-delta:
            coverage += evidence
            error_mass += F(comb(n, ones), 2)*(minus if wrong_plus >= wrong_minus else plus)
            confidence_mass += evidence*wrong_confidence
    return {"naive_acceptance_probability": coverage,
            "actual_selective_error": error_mass/coverage if coverage else None,
            "mean_naive_confidence_when_accepted": confidence_mass/coverage if coverage else None,
            "correct_all_positive_confidence": (r*a**n+(1-r)*(1-a)**n)/(a**n+(1-a)**n),
            "naive_all_positive_confidence": b**n/(b**n+(1-b)**n)}


def check_saved_artifacts():
    """Read-only coverage, preservation and budget checks; no experiment rerun."""
    protocol = json.loads((ROOT/'PROTOCOL.json').read_text())
    freeze = json.loads((ROOT/'FREEZE_RECEIPT.json').read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest(ROOT/'PROTOCOL.json') == freeze['protocol_sha256']
    parents = {}
    for parent in freeze['parents']:
        path = ROOT.parent/parent['directory']
        assert digest(path/'MANIFEST.sha256') == parent['manifest_sha256']
        for entry in parent['files']:
            assert digest(path/entry['path']) == entry['sha256']
        parents[parent['directory']] = len(parent['files'])
    laws = json.loads((ROOT/'law_grid.json').read_text())
    costs = json.loads((ROOT/'cost_grid.json').read_text())
    law_expected = set(product(protocol['law_grid']['r'], protocol['law_grid']['a'],
                               protocol['law_grid']['reads']))
    cost_expected = set(product(protocol['cost_grid']['r'], protocol['cost_grid']['a'],
                                protocol['cost_grid']['root_activation_cost'],
                                protocol['cost_grid']['budget']))
    assert len(laws) == len(law_expected) == 80
    assert {(v['r'], v['a'], v['reads']) for v in laws} == law_expected
    assert len(costs) == len(cost_expected) == 81
    assert {(v['r'], v['a'], v['root_cost'], v['budget']) for v in costs} == cost_expected
    for row in costs:
        assert row['copies_risk'] == row['repeat_risk']
        assert row['repeat_spent'] <= row['budget']
        assert row['fresh_spent'] == row['fresh_roots']*(row['root_cost']+1) <= row['budget']
        assert row['best_fixed_spent'] == row['best_fixed_roots']*(row['root_cost']+row['best_fixed_depth']) <= row['budget']
        assert row['DP_risk'] <= row['best_static_risk']+2e-12 <= row['best_fixed_depth_risk']+4e-12
    forbidden = {'theta', 'V', 'V_root', 'source_correct', 'correctness', 'gold',
                 'edit_ledger', 'semantic_label', 'seed', 'truth_rule', 'statements', 'value'}
    visible_counts = {}
    for filename in ('manifest.jsonl', 'facts.jsonl'):
        rows = [json.loads(x) for x in (ROOT/'corpus/selector_visible'/filename).read_text().splitlines()]
        assert all(not (set(row)&forbidden) for row in rows)
        visible_counts[filename] = len(rows)
    assert visible_counts == {'manifest.jsonl': 1152, 'facts.jsonl': 192}
    return {"parent_content_hashes_preserved": parents,
            "frozen_law_rows_complete": len(laws), "frozen_cost_rows_complete": len(costs),
            "cost_accounting_and_static_ordering_checks": len(costs),
            "selector_visible_record_counts": visible_counts,
            "selector_hidden_fields_absent": True,
            "all_grid_DP_values_independently_recomputed": False,
            "scope": "All law rows checked exactly elsewhere; only stated small/boundary/witness DP cases independently recomputed."}


def make_expectations():
    r, a = F(3, 4), F(4, 5)
    rows = []
    for n in range(1, 7):
        rows.append({"reads": n,
                     "same_root": encoded(count_design_risk((n,), r, a)),
                     "fresh_roots": encoded(count_design_risk((1,)*n, r, a)),
                     "persistent_extraction_same_root": encoded(
                         latent_enumerated_risk((n,), r, a, True))})
    dp_rows = []
    for cost in (0, 1):
        for budget in range(0, 7):
            sol = unsorted_root_bellman(budget, cost, r, a)
            fixed = fixed_budget_risks(budget, cost, r, a)
            assert sol['risk'] <= min(fixed[k] for k in
                ('repeat', 'copies', 'fresh', 'best_fixed_completed_depth'))
            dp_rows.append({"budget": budget, "activation_cost": cost,
                "optimal_risk": encoded(sol['risk']), "ordered_states": sol['states'],
                "repeat_risk": encoded(fixed['repeat']),
                "fresh_risk": encoded(fixed['fresh']),
                "best_fixed_risk": encoded(fixed['best_fixed_completed_depth']),
                "one_best_fixed_depth": fixed['one_best_depth']})
    enum_checks = 0
    for n in range(0, 7):
        for depths in compositions(n):
            assert count_design_risk(depths, r, a) == latent_enumerated_risk(depths, r, a)
            enum_checks += 1
    boundary_checks = 0
    for n in range(1, 7):
        for depths in compositions(n):
            assert count_design_risk(depths, F(1), a) == count_design_risk((n,), F(1), a)
            assert count_design_risk(depths, F(1, 2), a) == F(1, 2)
            assert count_design_risk(depths, r, F(1, 2)) == F(1, 2)
            assert count_design_risk(depths, r, F(1)) == count_design_risk((1,)*len(depths), r, F(1))
            boundary_checks += 4
        assert count_design_risk((n,), r, F(1)) == 1-r
        assert latent_enumerated_risk((n,), r, a, True) == 1-single_read_correctness(r, a)
        boundary_checks += 2
    copy_checks = []
    for n in range(1, 7):
        repeated = ['page_0']*n
        copies = ['copy_'+str(i) for i in range(n)]
        repeat_law = page_schedule_joint(repeated, {'page_0':'root_0'}, r, a)
        copy_law = page_schedule_joint(copies, {p:'root_0' for p in copies}, r, a)
        fresh_law = page_schedule_joint(copies, {p:'root_'+p for p in copies}, r, a)
        assert repeat_law == copy_law
        if n >= 2:
            assert copy_law != fresh_law
        copy_checks.append({"reads": n, "same_root_full_joint_law_equal": True,
                            "fresh_joint_law_distinct": n >= 2,
                            "histories": len(copy_law), "repeat_activated_roots": 1,
                            "copy_activated_roots": 1, "fresh_activated_roots": n})
    witness = unsorted_root_bellman(8, 1, r, a, include_reachable_policy=True)
    fixed = fixed_budget_risks(8, 1, r, a)
    static = exhaustive_static_risk(8, 1, r, a)
    witness_record = {"r": str(r), "a": str(a), "budget": 8, "activation_cost": 1,
        "optimal_risk": encoded(witness['risk']),
        "best_fixed_risk": encoded(fixed['best_fixed_completed_depth']),
        "gain_over_best_fixed": encoded(fixed['best_fixed_completed_depth']-witness['risk']),
        "best_static_risk": encoded(static['risk']),
        "one_best_static_depths": static['one_optimal_depths'],
        "gain_over_best_static": encoded(static['risk']-witness['risk']),
        "all_static_candidates_including_unused_budget": static['allocations_including_unspent'],
        "ordered_states": witness['states'],
        "reachable_optimal_policy": witness['reachable_optimal_policy']}
    large = unsorted_root_bellman(12, 1, F(9, 10), a)
    large_static = exhaustive_static_risk(12, 1, F(9, 10), a)
    large_record = {"r": "9/10", "a": "4/5", "budget": 12, "activation_cost": 1,
        "optimal_risk": encoded(large['risk']), "best_static_risk": encoded(large_static['risk']),
        "one_best_static_depths": large_static['one_optimal_depths'],
        "gain_over_best_static": encoded(large_static['risk']-large['risk']),
        "ordered_states": large['states'],
        "all_static_candidates_including_unused_budget": large_static['allocations_including_unspent']}
    return {"status": "EXACT_RATIONAL_REFERENCE_READY",
            "main_r": str(r), "main_a": str(a), "read_cost": 1,
            "known_channel_common_bayes_decoder": True,
            "law_rows": rows, "finite_budget_rows": dp_rows,
            "independent_latent_sum_design_checks": enum_checks,
            "boundary_checks": boundary_checks,
            "page_assignment_copy_joint_checks": copy_checks,
            "frozen_grid_witness_checked_after_parent_result": witness_record,
            "amended_static_baseline_maximum_checked_after_parent_result": large_record,
            "human_signoffs": 0, "network_calls": 0, "model_service_calls": 0,
            "limits": "Constructed symbolic channels only; not a natural Web or model reliability measurement."}


def check_engine(expectations):
    """Compare the parent float implementation to the independently built law.

    The reference functions above never call the engine. Here it is imported
    only as the implementation under test, after exact values are computed.
    """
    engine_path = ROOT/'engine.py'
    spec = importlib.util.spec_from_file_location('w2a_engine_under_test', engine_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    comparisons = []

    def compare(kind, parameters, actual, exact):
        expected = float(exact)
        error = abs(actual-expected)
        row = {"kind": kind, "parameters": parameters, "actual": actual,
               "expected_fraction": str(exact), "absolute_error": error,
               "pass": error <= 2e-12}
        comparisons.append(row)
        assert row['pass'], row

    protocol = json.loads((ROOT/'PROTOCOL.json').read_text())
    for rf in protocol['law_grid']['r']:
        for af in protocol['law_grid']['a']:
            r, a = fraction(rf), fraction(af)
            b = single_read_correctness(r, a)
            for n in protocol['law_grid']['reads']:
                pars = {"r": rf, "a": af, "n": n}
                compare('repeat_frozen_law', pars, engine.repeat_risk(n, rf, af),
                        count_design_risk((n,), r, a))
                # Independent roots yield independent Bernoulli(b) answers.
                compare('fresh_frozen_law', pars, engine.fresh_risk(n, rf, af),
                        count_design_risk((n,), F(1), b))

    for rf, af in ((.75, .8), (1, .8), (.75, 1), (.5, .8), (.75, .5)):
        for roots in range(1, 7):
            for depth in range(1, 7):
                if roots*depth > 6:
                    continue
                compare('fixed_depth_complete_count_law',
                        {"r": rf, "a": af, "roots": roots, "depth": depth},
                        engine.fixed_depth_risk(roots, depth, rf, af),
                        count_design_risk((depth,)*roots, fraction(rf), fraction(af)))

    for row in expectations['finite_budget_rows']:
        budget, cost = row['budget'], row['activation_cost']
        got = engine.BudgetSolver(.75, .8, cost).initial(budget)
        compare('central_unsorted_fraction_dp',
                {"r": .75, "a": .8, "budget": budget, "cost": cost},
                got['risk'], F(row['optimal_risk']['fraction']))

    witness = expectations['frozen_grid_witness_checked_after_parent_result']
    solver = engine.BudgetSolver(.75, .8, 1)
    compare('frozen_grid_gain_witness_fraction_dp',
            {"r": .75, "a": .8, "budget": 8, "cost": 1},
            solver.initial(8)['risk'], F(witness['optimal_risk']['fraction']))
    for node in witness['reachable_optimal_policy']:
        state = tuple(tuple(pair) for pair in node['ordered_root_counts'])
        compare('witness_reachable_conditional_value',
                {"ordered_root_counts": state, "remaining": node['remaining']},
                solver.value(state, node['remaining']),
                F(node['optimal_conditional_risk']['fraction']))
    compare('center_best_static_including_unspent_reference',
            {"r": .75, "a": .8, "budget": 8, "cost": 1},
            engine.best_static_allocation(8, 1, .75, .8)['risk'],
            F(witness['best_static_risk']['fraction']))
    large = expectations['amended_static_baseline_maximum_checked_after_parent_result']
    compare('larger_frozen_grid_gain_witness_fraction_dp',
            {"r": .9, "a": .8, "budget": 12, "cost": 1},
            engine.BudgetSolver(.9, .8, 1).initial(12)['risk'],
            F(large['optimal_risk']['fraction']))
    compare('larger_best_static_including_unspent_reference',
            {"r": .9, "a": .8, "budget": 12, "cost": 1},
            engine.best_static_allocation(12, 1, .9, .8)['risk'],
            F(large['best_static_risk']['fraction']))

    for rf, af in ((1, .8), (.75, 1), (.5, .8), (.75, .5), (1, 1)):
        for cost in (0, 1):
            for budget in range(0, 5):
                exact = unsorted_root_bellman(budget, cost, fraction(rf), fraction(af))['risk']
                compare('boundary_unsorted_fraction_dp',
                        {"r": rf, "a": af, "budget": budget, "cost": cost},
                        engine.BudgetSolver(rf, af, cost).initial(budget)['risk'], exact)

    confidence_count = 0
    confidence_parameters = [(n, .75, .8) for n in range(1, 16)]
    confidence_parameters += [(n, rf, af) for n in (1, 3, 5)
                             for rf, af in ((1, .8), (.75, 1), (.5, .8), (.75, .5), (1, 1))]
    for n, rf, af in confidence_parameters:
        actual = engine.confidence_diagnostic(n, rf, af)
        expected = exact_naive_confidence(n, rf, af)
        for key, value in expected.items():
            if value is None:
                assert actual[key] is None
            else:
                compare('confidence_diagnostic_'+key,
                        {"r": rf, "a": af, "reads": n}, actual[key], value)
            confidence_count += 1
    artifact_checks = check_saved_artifacts()

    return {"status": "PASS", "reference": "Fractions; unsorted root-creation-order Bellman and explicit latent sums",
            "comparison_tolerance_absolute": 2e-12,
            "comparisons": comparisons, "comparison_count": len(comparisons),
            "max_absolute_error": max(row['absolute_error'] for row in comparisons),
            "latent_sum_cross_checks": expectations['independent_latent_sum_design_checks'],
            "reference_boundary_checks": expectations['boundary_checks'],
            "page_copy_complete_joint_law_checks": len(expectations['page_assignment_copy_joint_checks']),
            "witness_reachable_policy_nodes": len(witness['reachable_optimal_policy']),
            "confidence_metric_checks_including_zero_coverage": confidence_count,
            "artifact_checks": artifact_checks,
            "engine_sha256": hashlib.sha256(engine_path.read_bytes()).hexdigest(),
            "independent_verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256((ROOT/'PROTOCOL.json').read_bytes()).hexdigest(),
            "human_review": "NOT_PERFORMED_OR_REQUIRED_FOR_CONSTRUCTED_TRUTH",
            "external_model_calls": 0, "network_calls": 0,
            "scientific_boundary": "Symbolic controlled channel validation; no natural or model-extraction reliability claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-expectations', action='store_true')
    parser.add_argument('--check-engine', action='store_true')
    args = parser.parse_args()
    result = make_expectations()
    if args.write_expectations:
        (ROOT/'INDEPENDENT_EXPECTATIONS.json').write_text(
            json.dumps(result, indent=2)+'\n')
    if args.check_engine:
        checks = check_engine(result)
        (ROOT/'INDEPENDENT_CHECKS.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(json.dumps({k:v for k,v in checks.items() if k != 'comparisons'}, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
