"""Observable forced-only estimates and bounded-error deterministic tracking.

This is a numerical proof-to-code alignment variant, not an exact-arithmetic
implementation of an asymptotic theorem. The coefficient implementation is
imported read-only from Phase 2a. Its fixed internal numerical floors remain
visible in every planning record.
"""

from __future__ import annotations

import math
import time

import numpy as np

from phase2a.coefficients import solve_allocation


def ordered_grid_projection(raw_p: float, raw_q: float, t: int, eta: float = .05):
    """Nearest Euclidean ordered grid point, with deterministic half-up ties.

    Grid rates are .5 + (1-eta-.5)*i/n for i=0,...,n, n=ceil(sqrt(t+1)).
    Require q_index < p_index. When separately nearest indices violate that
    condition, the nearest feasible pair is adjacent and is found by rounding
    (raw_q_index+raw_p_index-1)/2. No response or calibration values are used
    to choose the grid itself.
    """
    if t < 0 or not 0 < eta < .5 or not all(math.isfinite(x) for x in (raw_p, raw_q)):
        raise ValueError("invalid grid projection inputs")
    root = math.isqrt(t + 1)
    n = max(2, root + int(root * root < t + 1))
    span = .5 - eta
    a, b = (raw_q - .5) * n / span, (raw_p - .5) * n / span
    round_half_up = lambda x: math.floor(x + .5)
    q_index = min(n - 1, max(0, round_half_up(a)))
    p_index = min(n, max(1, round_half_up(b)))
    if q_index >= p_index:
        q_index = min(n - 1, max(0, round_half_up((a + b - 1) / 2)))
        p_index = q_index + 1
    # Use explicit endpoints: (span*n)/n can round above span even though the
    # exact grid endpoint equals the public upper bound.
    q = .5 if q_index == 0 else .5 + span * (q_index / n)
    p = 1 - eta if p_index == n else .5 + span * (p_index / n)
    if not .5 <= q < p <= 1 - eta:
        raise FloatingPointError("ordered grid exceeds the available floating-point resolution")
    return {
        "p": p, "q": q, "grid_size": n, "grid_mesh": span / n,
        "p_grid_index": p_index, "q_grid_index": q_index,
    }


class TheoryAlignedTracking:
    """Joint-sign recovery sampler with next(active)/observe(action,result).

    Public input follows QRelBench: d, groups[g]['targets'], rate_domain.eta,
    and optionally known type_accuracy. No private seed, true signs/types, or
    generating rates are accepted or inspected. Calibration bit values and
    direct type reports never enter the forced-only allocation estimator.

    ``planning_R`` is log(1/delta), avoiding exp(-R) underflow. All task and type
    observations remain in counts/types for the common external GLR. This class
    makes no stopping decision. Full target activity is required.
    """

    def __init__(self, public, calibration, planning_R: float):
        self.d = int(public["d"])
        if self.d < 1 or self.d != public["d"]:
            raise ValueError("public d must be a positive integer")
        self.groups = tuple(tuple(int(j) for j in group["targets"]) for group in public["groups"])
        self.G = len(self.groups)
        if not 1 <= self.G <= 2 or any(not group for group in self.groups):
            raise ValueError("the read-only coefficient solver supports one or two nonempty groups")
        if sorted(j for group in self.groups for j in group) != list(range(self.d)):
            raise ValueError("public groups must partition all targets exactly once")
        self.eta = float(public["rate_domain"]["eta"])
        if not 0 < self.eta < .5:
            raise ValueError("eta must be in (0,1/2)")
        supplied_accuracy = public.get("type_accuracy")
        self.type_accuracy = None if supplied_accuracy is None else tuple(float(x) for x in supplied_accuracy)
        if self.type_accuracy is not None and (
            len(self.type_accuracy) != self.G or any(not .5 < x < 1 for x in self.type_accuracy)
        ):
            raise ValueError("known finite type accuracies must lie in (1/2,1)")
        if not math.isfinite(planning_R) or planning_R <= 0:
            raise ValueError("planning_R must be finite and positive")
        self.planning_R = float(planning_R)
        if set(calibration) != {"high", "low"} or len(calibration["high"]) != len(calibration["low"]):
            raise ValueError("two equally long labelled reference streams are required")
        # Deliberately retain lengths only. Reference values cannot assist the
        # Section 4.2 forced-only estimator through this object.
        self.reference_count = len(calibration["high"])
        self.alpha = self.reference_count / self.planning_R
        self.L = 2 * self.d
        self.E = self.L + self.G
        self.counts = np.zeros((self.d, 2, 2), dtype=np.int64)
        self.forced = np.zeros_like(self.counts)
        self.types = [[] for _ in range(self.G)]
        self.weights = np.r_[np.full(self.L, 1 / self.L), np.zeros(self.G)]
        self.cumulative = np.zeros(self.E)
        self.t = 0
        self.next_update = self.L
        self.last_update = None
        self.estimates = []
        self.planning_failures = []
        self.last_estimate = None
        self.planner_seconds = 0.
        self.planner_cpu_seconds = 0.
        self.last_forced = False
        self._pending = None

    def _forced_index(self):
        """Square blocks at completed times L*n^2,...,L*n^2+L-1."""
        n = math.isqrt(self.t // self.L)
        offset = self.t - self.L * n * n
        return int(offset) if offset < self.L else None

    def _estimate(self):
        n = self.forced.sum(axis=2)
        if np.any(n == 0):
            raise RuntimeError("all task streams need an initial forced observation")
        means = self.forced[:, :, 1] / n
        theta = (means.sum(axis=1) > 1).astype(np.int8)
        oriented = np.where(theta[:, None] == 1, means, 1 - means)
        z = np.zeros(self.G, dtype=np.int8)
        for g, members in enumerate(self.groups):
            group_means = oriented[list(members)].mean(axis=0)
            z[g] = int(group_means[1] > group_means[0])
        good = [float(oriented[j, z[g]]) for g, members in enumerate(self.groups) for j in members]
        low = [float(oriented[j, 1 - z[g]]) for g, members in enumerate(self.groups) for j in members]
        raw_p, raw_q = math.fsum(good) / self.d, math.fsum(low) / self.d
        projection = ordered_grid_projection(raw_p, raw_q, self.t, self.eta)
        return {
            "theta": theta.tolist(), "z": z.tolist(), "raw_p": raw_p, "raw_q": raw_q,
            **projection, "forced_tasks": int(n.sum()), "forced_task_counts": n.tolist(),
            "estimator_inputs": "forced_task_observations_only",
            "sign_tie": 0, "type_tie": 0,
        }

    @staticmethod
    def requested_tolerance(t):
        return min(1e-4, 1 / (t + 1))

    def _update(self):
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        estimate = self._estimate()
        epsilon = self.requested_tolerance(self.t)
        requested_gap = 5 * epsilon
        numerical_gap_floor = 5e-8
        effective_gap = max(requested_gap, numerical_gap_floor)
        attempts = []
        allocation = None
        try:
            for attempt in range(2):
                fit = solve_allocation(
                    [len(group) for group in self.groups], estimate["p"], estimate["q"],
                    self.alpha, self.type_accuracy, self.eta,
                    tolerance=epsilon * (0.1 ** attempt), max_iterations=200,
                )
                attempts.append({
                    "requested_separation_tolerance": epsilon * (0.1 ** attempt),
                    "relative_gap": float(fit["relative_gap"]),
                    "lower_bound": float(fit["lower_bound"]),
                    "upper_bound": float(fit["upper_bound"]),
                    "minimum_information": float(fit["minimum_information"]),
                    "iterations": int(fit["iterations"]), "cuts": int(fit["cuts"]),
                })
                if (math.isfinite(fit["relative_gap"]) and -numerical_gap_floor <= fit["relative_gap"] <= effective_gap
                        and fit["minimum_information"] >= 1 - 1e-7):
                    allocation = fit
                    break
            if allocation is None:
                raise RuntimeError("allocation failed its logged numerical gap/feasibility checks")
            weights = np.zeros(self.E)
            for g, members in enumerate(self.groups):
                for j in members:
                    weights[2 * j + estimate["z"][g]] = allocation["a"][g] / allocation["K"]
                    weights[2 * j + 1 - estimate["z"][g]] = allocation["b"][g] / allocation["K"]
                weights[self.L + g] = allocation["c"][g] / allocation["K"]
            if np.any(~np.isfinite(weights)) or np.any(weights < 0) or abs(weights.sum() - 1) > 1e-7:
                raise RuntimeError("allocation does not expand into a valid action distribution")
            if self.type_accuracy is None and np.any(weights[self.L:] > 0):
                raise RuntimeError("allocation contains unavailable type actions")
            # Correct floating summation drift only; no statistical smoothing,
            # forced minimum mass, or ad hoc allocation shortcut is introduced.
            self.weights = weights / weights.sum()
        except Exception as exc:
            self.planning_failures.append({"online": self.t, "estimate": estimate,
                                           "attempts": attempts, "error": type(exc).__name__ + ": " + str(exc)})
            raise
        finally:
            wall_seconds, cpu_seconds = time.perf_counter() - wall_start, time.process_time() - cpu_start
            self.planner_seconds += wall_seconds
            self.planner_cpu_seconds += cpu_seconds
        self.last_update = self.t
        step = math.isqrt(self.t + 1)
        step += int(step * step < self.t + 1)
        self.next_update = self.t + max(1, step)
        self.last_estimate = {
            **estimate, "online": self.t, "alpha_effective": self.alpha,
            "weights": self.weights.tolist(), "estimated_K": float(allocation["K"]),
            "allocation_a": allocation["a"], "allocation_b": allocation["b"], "allocation_c": allocation["c"],
            "requested_tolerance": epsilon, "requested_relative_gap": requested_gap,
            "effective_numerical_relative_gap": effective_gap,
            "numerical_gap_floor": numerical_gap_floor,
            "numerical_floor_active": requested_gap < numerical_gap_floor,
            "solver_relative_gap": float(allocation["relative_gap"]),
            "lower_bound": float(allocation["lower_bound"]), "upper_bound": float(allocation["upper_bound"]),
            "minimum_information": float(allocation["minimum_information"]),
            "solver_attempts": attempts, "solver_seconds": wall_seconds,
            "solver_cpu_seconds": cpu_seconds, "next_update": self.next_update,
            "arithmetic_scope": "float64_LP_and_analytic_separation_not_interval_certified",
            "solver_fixed_floors": {"LP_primal_dual": 1e-9, "radial_information_pad": 1e-9,
                                    "cut_deduplication_decimal_places": 13,
                                    "accepted_information_evaluation_residual": 1e-7},
        }
        self.estimates.append(self.last_estimate)

    def _actual_counts(self):
        return np.r_[self.counts.sum(axis=2).reshape(-1), [len(x) for x in self.types]]

    def next(self, active):
        if self._pending is not None:
            raise RuntimeError("observe the pending action before requesting another action")
        if set(active) != set(range(self.d)):
            raise ValueError("theory-aligned joint recovery requires all targets active")
        if self.t >= self.next_update:
            self._update()
        self.cumulative += self.weights
        index = self._forced_index()
        self.last_forced = index is not None
        if index is None:
            index = int(np.argmax(self.cumulative - self._actual_counts()))
        if index < self.L:
            action = ("query", index // 2, "AB"[index % 2])
        else:
            action = ("type", index - self.L)
        self._pending = action
        return action

    def observe(self, action, result):
        if self._pending is None or tuple(action) != self._pending:
            raise ValueError("observation must match the single pending action")
        if action[0] == "type":
            reported = result["format"]
            if reported not in ("A", "B"):
                raise ValueError("type report must use public format A or B")
            self.types[action[1]].append("AB".index(reported))
        else:
            answer = result["answer"]
            if answer not in (0, 1):
                raise ValueError("task answer must be 0 or 1")
            j, fmt = action[1], "AB".index(action[2])
            self.counts[j, fmt, int(answer)] += 1
            if self.last_forced:
                self.forced[j, fmt, int(answer)] += 1
        self.t += 1
        self._pending = None

    def diagnostics(self):
        actual_minus_target = self._actual_counts() - self.cumulative
        forced_total = int(self.forced.sum())
        return {
            "online": self.t, "forced_tasks": forced_total,
            "forced_task_counts": self.forced.sum(axis=2).tolist(),
            "forced_total_upper_bound": math.sqrt(self.L * self.t) + self.L,
            "actual_minus_target": actual_minus_target.tolist(),
            "tracking_upper_bound": 1 + forced_total,
            "tracking_lower_bound": -(self.E - 1) * (1 + forced_total),
            "last_update": self.last_update, "next_update": self.next_update,
            "last_update_ratio": None if self.last_update is None or self.t == 0 else self.last_update / self.t,
            "planner_seconds": self.planner_seconds, "planner_cpu_seconds": self.planner_cpu_seconds,
            "numerical_scope": "finite_precision_alignment_variant_not_an_exact_asymptotic_implementation",
        }
