"""Synthetic mathematical fixtures only; no worlds, seeds, training, or models."""
from copy import deepcopy
from functools import partial
import math
import unittest

import numpy as np
from scipy.optimize import minimize

from t2.information import (
    WarmSolver, build_cuts, finite_cut_radial_cost, min_information, radial_cost,
)
from phase2a.coefficients import kl, solve_allocation


def assert_close(actual, expected, rel=1e-7, abs=0.):
    assert math.isclose(actual, expected, rel_tol=rel, abs_tol=abs), (actual, expected)


def state_fixture(groups=((0, 1), (2,)), p=.82, q=.61, M=5, R=10., known_s=(.83, .76)):
    d, G = sum(map(len, groups)), len(groups)
    return {
        "schema": "t2_observable_v1", "d": d, "groups": [list(g) for g in groups],
        "eta": .05, "known_s": None if known_s is None else list(known_s[:G]),
        "counts": np.zeros((d, 2, 2), dtype=int).tolist(),
        "forced_counts": np.zeros((d, 2, 2), dtype=int).tolist(),
        "type_report_counts": np.zeros((G, 2), dtype=int).tolist(),
        "calibration": {"high": {"successes": M, "total": M},
                        "low": {"successes": M // 2, "total": M}},
        "R": R, "online": 0, "online_cap": 80, "remaining": 80,
        "estimate": {"p": p, "q": q, "theta_prob": [.7] * d,
                     "z_prob": [.2, .8][:G], "z": [0, 1][:G]},
        "action_mask": [1] * (2 * d) + [int(known_s is not None)] * G,
    }


def teacher(state, solver=solve_allocation):
    fit = solver([len(g) for g in state["groups"]], state["estimate"]["p"], state["estimate"]["q"],
                 state["calibration"]["high"]["total"] / state["R"], state["known_s"], tolerance=1e-8)
    w = np.zeros(len(state["action_mask"]))
    for g, group in enumerate(state["groups"]):
        z = state["estimate"]["z"][g]
        for j in group:
            w[2 * j + z] = fit["a"][g] / fit["K"]
            w[2 * j + 1 - z] = fit["b"][g] / fit["K"]
        w[2 * state["d"] + g] = fit["c"][g] / fit["K"]
    return fit, w / w.sum()


def test_asymmetric_separation_against_independent_continuous_minimization():
    state = state_fixture(groups=((0,), (1,)))
    x = np.array([1.6, .25, .42, 1.05, .2, .4])
    estimate = state["estimate"]
    d, G, alpha = state["d"], len(state["groups"]), .5
    membership = [next(g for g, members in enumerate(state["groups"]) if j in members) for j in range(d)]
    candidates = []
    for flips in range(1, 2 ** d):
        for types in range(2 ** G):
            def objective(uv):
                u, v = uv
                value = alpha * (kl(estimate["p"], u) + kl(estimate["q"], v))
                for j in range(d):
                    g = membership[j]
                    for mode in range(2):
                        r = estimate["p"] if mode == estimate["z"][g] else estimate["q"]
                        alt_z = estimate["z"][g] ^ ((types >> g) & 1)
                        alt_r = u if mode == alt_z else v
                        if (flips >> j) & 1:
                            alt_r = 1 - alt_r
                        value += x[2 * j + mode] * kl(r, alt_r)
                for g, s in enumerate(state["known_s"]):
                    value += x[2 * d + g] * ((types >> g) & 1) * kl(s, 1 - s)
                return value
            result = minimize(objective, [.75, .6], method="SLSQP", bounds=[(.5, .95)] * 2,
                              constraints=[{"type": "ineq", "fun": lambda uv: uv[0] - uv[1]}],
                              options={"ftol": 1e-12, "maxiter": 100})
            assert result.success
            candidates.append(result.fun)
    fit = min_information(state, x)
    assert fit["alternative_count"] == (2 ** d - 1) * 2 ** G
    assert_close(fit["value"], min(candidates), abs=2e-9)


def test_fixed_calibration_radial_is_not_information_reciprocal():
    state = state_fixture(groups=((0,), (1,)), M=30)
    w = np.array([.37, .13, .09, .27, .08, .06])
    K = radial_cost(state, w)
    assert math.isfinite(K)
    assert_close(min_information(state, K * w)["value"], 1., abs=1e-9)
    assert abs(K - 1 / min_information(state, w)["value"]) > .01
    state["calibration"] = {k: {"successes": 0, "total": 0} for k in ("high", "low")}
    assert_close(radial_cost(state, w), 1 / min_information(state, w)["value"], rel=1e-9)


def test_teacher_coefficient_consistent_with_all_subsets(groups, M, known_s):
    state = state_fixture(groups=groups, M=M, known_s=known_s)
    fit, w = teacher(state)
    assert_close(radial_cost(state, w), fit["K"], rel=5e-8)
    assert min_information(state, fit["K"] * w)["value"] >= 1 - 2e-9


def test_missing_fact_coverage_stays_infinite_and_mask_is_enforced():
    state = state_fixture(groups=((0,), (1,)))
    missing = np.array([.6, .2, 0., 0., .1, .1])
    assert math.isinf(radial_cost(state, missing))
    masked = state_fixture(groups=((0,),), known_s=None)
    with unittest.TestCase().assertRaisesRegex(ValueError, "illegal"):
        radial_cost(masked, [.5, 0., .5])
    assert math.isfinite(radial_cost(masked, [1., 0., 0.]))


def test_only_uninformative_low_channel_can_have_a_finite_calibration_limit():
    state = state_fixture(groups=((0,),), p=.8, q=.5, M=0)
    assert math.isinf(radial_cost(state, [0., 1., 0.]))
    # Positive M cannot identify a fact whose only sampled rate is one-half.
    state["calibration"] = {k: {"successes": 20, "total": 40} for k in ("high", "low")}
    assert math.isinf(radial_cost(state, [0., 1., 0.]))


def test_fact_group_and_channel_relabelling_invariance():
    state = state_fixture()
    w = np.array([.13, .08, .17, .06, .11, .22, .09, .14])
    original = radial_cost(state, w)
    # Swap two facts within a group and reorder the two groups.
    other = deepcopy(state)
    permutation = [1, 0, 2]  # new position -> previous fact
    other["groups"] = [[2], [0, 1]]
    other["known_s"] = state["known_s"][::-1]
    other["estimate"]["z"] = state["estimate"]["z"][::-1]
    other["estimate"]["z_prob"] = state["estimate"]["z_prob"][::-1]
    reordered = np.r_[w[:6].reshape(3, 2)[permutation].ravel(), w[6:][::-1]]
    assert_close(radial_cost(other, reordered), original, rel=1e-10)
    # Relabel the two physical channels in one group, including estimated z.
    other["estimate"]["z"][1] ^= 1
    reordered[:4] = reordered[:4].reshape(2, 2)[:, ::-1].ravel()
    assert_close(radial_cost(other, reordered), original, rel=1e-10)


def test_envelope_gradient_and_finite_cut_radial_bound():
    state = state_fixture(groups=((0,), (1,)))
    fit, tw = teacher(state)
    cuts = build_cuts(state, tw, fit["K"])
    assert len(cuts["cut_offsets"]) <= 6 * (2 ** state["d"] - 1) * 4
    assert np.asarray(cuts["cut_coefficients"]).shape[1] == 6
    assert cuts["alpha"] == .5
    assert_close(finite_cut_radial_cost(cuts, tw), fit["K"], rel=5e-8)
    directions = [np.full(6, 1 / 6), np.array([.37, .13, .09, .27, .08, .06]),
                  np.array([.01, .31, .3, .02, .25, .11])]
    for w in directions:
        assert finite_cut_radial_cost(cuts, w) <= radial_cost(state, w) * (1 + 2e-9)
    x = np.array([1.6, .25, .42, 1.05, .2, .4])
    direction = np.array([.2, -.1, -.3, .15, .1, -.05])
    analytic = np.asarray(min_information(state, x)["gradient"]) @ direction
    eps = 1e-5
    numerical = (min_information(state, x + eps * direction)["value"] -
                 min_information(state, x - eps * direction)["value"]) / (2 * eps)
    assert_close(analytic, numerical, abs=2e-8)


def test_cut_radial_derivative_matches_fixed_active_constraint():
    state = state_fixture(groups=((0,), (1,)))
    fit, tw = teacher(state)
    cuts = build_cuts(state, tw, fit["K"])
    C, b = np.asarray(cuts["cut_coefficients"]), np.asarray(cuts["cut_offsets"])
    w = np.array([.37, .13, .09, .27, .08, .06])
    direction = np.array([.2, -.1, -.3, .15, .1, -.05])
    need, denom = np.maximum(0., 1 - b), C @ w
    index = np.argmax(np.divide(need, denom, out=np.zeros_like(need), where=denom > 0))
    expected = -need[index] * (C[index] @ direction) / denom[index] ** 2
    eps = 1e-6
    derivative = (finite_cut_radial_cost(cuts, w + eps * direction) -
                  finite_cut_radial_cost(cuts, w - eps * direction)) / (2 * eps)
    assert_close(derivative, expected, rel=2e-6, abs=2e-6)


def test_warm_solver_recomputes_exact_fresh_rates_and_matches_cold():
    warm = WarmSolver(max_cached_cuts=128)
    previous = None
    for p, q, alpha, s in [(.82, .61, .5, [.83, .76]),
                            (.820000017, .610000023, .5, [.83, .76]),
                            (.84, .63, .8, [.8, .79])]:
        kwargs = dict(partition=(1, 2), p=p, q=q, alpha=alpha, type_accuracy=s,
                      tolerance=2e-8, max_iterations=200)
        current = warm.solve(**kwargs)
        cold = solve_allocation(**kwargs)
        assert current["p"] == p and current["q"] == q
        assert current["minimum_information"] >= 1 - 1e-7
        assert current["relative_gap"] <= 1e-7
        assert_close(current["K"], cold["K"], rel=5e-7)
        assert current["lower_bound"] <= cold["upper_bound"] * (1 + 1e-8)
        assert cold["lower_bound"] <= current["upper_bound"] * (1 + 1e-8)
        diagnostics = current["warm_diagnostics"]
        assert diagnostics["exact_fresh_inputs"] and not diagnostics["rounded_keys"]
        assert not diagnostics["reused_rate_or_coefficient_results"]
        if previous is not None:
            assert diagnostics["warm_cuts"] > 0
        previous = current


def test_observable_and_bounded_geometry_fails_closed(change):
    state = state_fixture()
    change(state)
    with unittest.TestCase().assertRaises(ValueError):
        radial_cost(state, np.full(8, 1 / 8))


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    parameterized = {"test_teacher_coefficient_consistent_with_all_subsets",
                     "test_observable_and_bounded_geometry_fails_closed"}
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and name not in parameterized:
            suite.addTest(unittest.FunctionTestCase(function))
    for case in [(((0, 1),), 0, None), (((0,), (1, 2)), 5, (.83, .76)),
                 (((0, 1), (2, 3)), 20, (.83, .76))]:
        function = partial(test_teacher_coefficient_consistent_with_all_subsets, *case)
        function.__name__ = "test_teacher_coefficient_consistent_with_all_subsets"
        suite.addTest(unittest.FunctionTestCase(function,
                                               description="teacher coefficient consistency " + str(case)))
    for change in [lambda x: x.update(private_seed=1), lambda x: x["estimate"].update(true_p=.8),
                   lambda x: x["calibration"]["low"].update(total=6), lambda x: x.update(d=5)]:
        function = partial(test_observable_and_bounded_geometry_fails_closed, change)
        function.__name__ = "test_observable_and_bounded_geometry_fails_closed"
        suite.addTest(unittest.FunctionTestCase(function,
                                               description="reject malformed or private state"))
    return suite


if __name__ == "__main__":
    unittest.main()
