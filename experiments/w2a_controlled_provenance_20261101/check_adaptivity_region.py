#!/usr/bin/env python3
"""Offline exact check for ADAPTIVITY_REGION_PROOF.md; prints JSON, writes nothing.

Replays the frozen policy with explicit latent reports and reading draws.
Independently enumerates all static allocations, including unused budgets.
Does not import engine.py, policy_audit.py, or independent_checks.py.
The continuous-region proof uses coupling and a common action menu, not corners.
"""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from math import prod
from pathlib import Path


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def encoded(x):
    return {"fraction": str(x), "float": float(x)}


def allocations(cap=8, minimum=1):
    """All nondecreasing positive depths, each activation bundled with a read."""
    yield ()
    for depth in range(minimum, cap):
        for tail in allocations(cap - depth - 1, depth):
            yield (depth,) + tail


def static_risk(depths, r, a):
    """Fully enumerate theta, root reports and raw answer histories."""
    owner = tuple(i for i, depth in enumerate(depths) for _ in range(depth))
    masses = defaultdict(lambda: [F(0), F(0)])
    for theta in (0, 1):
        for reports in product((0, 1), repeat=len(depths)):
            base = F(1, 2) * prod(r if v == theta else 1-r for v in reports)
            for answers in product((0, 1), repeat=len(owner)):
                weight = base * prod(
                    a if answer == reports[i] else 1-a
                    for answer, i in zip(answers, owner))
                masses[answers][theta] += weight
    require(sum(sum(pair) for pair in masses.values()) == 1,
            "static law failed normalization")
    return sum(min(pair) for pair in masses.values())


def node_key(state, remaining):
    return tuple(tuple(pair) for pair in state), remaining


def advance(state, root, answer):
    out = list(state)
    if root == len(state):
        out.append((answer, 1-answer))
    else:
        ones, zeros = out[root]
        out[root] = (ones+answer, zeros+1-answer)
    return tuple(out)


def freeze_policy(document):
    require(document["terminal_decoder"] ==
            "center-parameter Bayes sign, fair tie; held fixed under perturbation",
            "unexpected terminal-decoder rule")
    r0, a0 = F(document["r_center"]), F(document["a_center"])
    require((r0, a0, document["budget"], document["nominal_activation_cost"]) ==
            (F(3, 4), F(4, 5), 8, 1), "center changed")
    nodes = {
        node_key(row["ordered_root_counts"], row["remaining"]): row
        for row in document["nodes"]
    }
    require(len(nodes) == len(document["nodes"]) == 37, "node count/duplicate")

    @lru_cache(None)
    def frozen_one_probability(state):
        # Output randomization probability frozen at CENTER, never the test r,a.
        likelihood = []
        for theta in (0, 1):
            root_one = r0 if theta else 1-r0
            likelihood.append(F(1, 2) * prod(
                root_one * a0**ones * (1-a0)**zeros
                + (1-root_one) * (1-a0)**ones * a0**zeros
                for ones, zeros in state))
        if likelihood[1] > likelihood[0]:
            return F(1)
        if likelihood[1] < likelihood[0]:
            return F(0)
        return F(1, 2)

    reachable = set()
    queue = [((), 8)]
    while queue:
        key = queue.pop()
        if key in reachable:
            continue
        reachable.add(key)
        require(key in nodes, "missing child in frozen policy")
        state, remaining = key
        row = nodes[key]
        coins = len(state) + sum(sum(pair) for pair in state)
        require(coins <= 8 and remaining == 8-coins,
                "nominal budget not tied to root/read counts")
        if row["action"] == "STOP":
            require(row["action_cost"] == 0 and row["transitions"] == [],
                    "invalid STOP record")
            frozen_one_probability(state)
            continue
        root = row["root_index"]
        new = row["action"] == "NEW_ROOT"
        require(row["action"] in ("NEW_ROOT", "READ_EXISTING_ROOT"),
                "unsupported action")
        require((root == len(state)) if new else (0 <= root < len(state)),
                "root indexing invalid")
        cost = 2 if new else 1
        require(row["action_cost"] == cost and remaining >= cost,
                "action cost mismatch")
        expected_children = {
            (answer, advance(state, root, answer), remaining-cost)
            for answer in (0, 1)
        }
        actual_children = {
            (item["answer"], tuple(tuple(p) for p in item["next_root_counts"]),
             item["next_remaining"])
            for item in row["transitions"]
        }
        require(expected_children == actual_children, "child table mismatch")
        queue.extend((child, rem) for _, child, rem in expected_children)
    require(reachable == set(nodes), "unreachable/extra frozen nodes")

    def evaluate(r, a):
        @lru_cache(None)
        def walk(state, reports, remaining, theta):
            row = nodes[(state, remaining)]
            if row["action"] == "STOP":
                q = frozen_one_probability(state)
                return q if theta == 0 else 1-q
            root = row["root_index"]
            if row["action"] == "NEW_ROOT":
                result = F(0)
                for report in (0, 1):
                    p_root = r if report == theta else 1-r
                    for answer in (0, 1):
                        p_read = a if answer == report else 1-a
                        result += p_root * p_read * walk(
                            advance(state, root, answer), reports+(report,),
                            remaining-2, theta)
                return result
            report = reports[root]
            return sum(
                (a if answer == report else 1-a) * walk(
                    advance(state, root, answer), reports, remaining-1, theta)
                for answer in (0, 1))
        return sum(walk((), (), 8, theta) for theta in (0, 1)) / 2

    return evaluate, len(nodes)


def main():
    experiment_dir = Path(__file__).resolve().parent
    policy_path = experiment_dir / "center_policy.json"
    original_policy_bytes = policy_path.read_bytes()
    policy_doc = json.loads(original_policy_bytes)
    evaluate, node_count = freeze_policy(policy_doc)
    designs = tuple(allocations())
    require(len(designs) == len(set(designs)) == 22,
            "static design class changed")
    require(all(sum(ds)+len(ds) <= 8 for ds in designs),
            "infeasible static design")

    # Exact action-menu endpoint check. Analytical proof covers every pair;
    # n<=10,m<=n suffices to include the first forbidden boundary for this test.
    menu_checks = 0
    for gamma in (F(4, 5), F(1)):
        for n in range(11):
            for m in range(n+1):
                if (m == 0) != (n == 0):
                    continue
                require((n+gamma*m <= 8) == (m+n <= 8),
                        "menu mismatch at activation-cost endpoint")
                menu_checks += 1
    require(F(5)+F(4, 5)*4 == F(41, 5),
            "first forbidden trajectory cost mismatch")
    require(F(5)+F(3, 4)*4 == 8,
            "lower endpoint counterexample mismatch")

    r0, a0, epsilon = F(3, 4), F(4, 5), F(1, 4000)
    adaptive = evaluate(r0, a0)
    static_values = [(static_risk(ds, r0, a0), ds) for ds in designs]
    best_static = min(value for value, _ in static_values)
    winners = [ds for value, ds in static_values if value == best_static]
    require(adaptive == F(24899, 100000), "center policy replay mismatch")
    require(best_static == F(25871, 100000), "center static optimum mismatch")
    require((1, 2, 2) in winners, "claimed static witness absent")
    central_gap = best_static-adaptive
    require(central_gap == F(243, 25000), "center gap mismatch")
    region_gap = central_gap-16*epsilon
    require(region_gap == F(143, 25000) and region_gap > 0,
            "analytic margin arithmetic mismatch")

    corners = []
    for dr, da in product((-epsilon, epsilon), repeat=2):
        r, a = r0+dr, a0+da
        frozen_risk = evaluate(r, a)
        static_opt = min(static_risk(ds, r, a) for ds in designs)
        require(abs(frozen_risk-adaptive) <= 8*epsilon,
                "policy perturbation sanity check failed")
        require(abs(static_opt-best_static) <= 8*epsilon,
                "static-infimum perturbation sanity check failed")
        require(static_opt-frozen_risk >= region_gap,
                "corner gap below analytic certificate")
        corners.append({
            "r": str(r), "a": str(a), "frozen_policy_risk": encoded(frozen_risk),
            "reoptimized_static_risk": encoded(static_opt),
            "gap": encoded(static_opt-frozen_risk),
        })
    require(policy_path.read_bytes() == original_policy_bytes,
            "policy changed during read-only replay")
    print(json.dumps({
        "status": "PASS",
        "check_id": "W2a-fixed-adaptive-policy-region-v1",
        "policy_sha256": sha256(original_policy_bytes).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "reachable_frozen_policy_nodes": node_count,
        "static_allocations_including_empty_and_unused_budget": len(designs),
        "center_frozen_policy_risk": encoded(adaptive),
        "center_best_static_risk": encoded(best_static),
        "center_static_minimizers": winners,
        "center_gap": encoded(central_gap),
        "epsilon": str(epsilon),
        "analytic_full_region_margin": encoded(region_gap),
        "action_menu_endpoint_checks": menu_checks,
        "corner_sanity_checks": corners,
        "corners_are_not_the_region_proof": True,
        "policy_actions_and_decoder_reoptimized": False,
        "static_decoder_allowed_to_reoptimize": True,
        "center_global_adaptive_optimality_reproved_here": False,
        "center_optimality_needed_for_separation": False,
        "continuous_region_proof": "ADAPTIVITY_REGION_PROOF.md: common finite menu, adaptive coupling, uniform Lipschitz infimum bound.",
        "network_calls": 0, "model_service_calls": 0,
        "existing_files_modified": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

