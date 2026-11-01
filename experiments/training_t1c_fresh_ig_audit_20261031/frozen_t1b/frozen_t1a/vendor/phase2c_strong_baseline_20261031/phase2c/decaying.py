"""Primary shared-estimator decaying-exploration Repeat-and-Compare baseline.

Only the exploitation-target update differs from frozen Phase 2b Aligned.
This version estimates formats through the same forced-response estimator;
it is not an additional repeated-answer-agreement variant.
"""

import math
import time

import numpy as np

# Bootstrap must establish the read-only historical import paths first.
from .bootstrap import P2B  # noqa: F401
from phase2b.aligned import TheoryAlignedTracking


class DecayingRepeatAndCompare(TheoryAlignedTracking):
    """D-RRC: equal coordinate mass on each currently estimated better format.

    The inherited constructor is (public, calibration, planning_R). Forced
    observations, estimation/grid, square-block exploration, cumulative
    tracking, update cadence, pending-action checks, and storage are unchanged.
    Known type actions remain available, but this simple rule assigns them
    zero mass. No joint KL optimizer or true parameter is consulted.
    """

    def _update(self):
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        estimate = self._estimate()
        weights = np.zeros(self.E)
        for g, members in enumerate(self.groups):
            for j in members:
                weights[2 * j + estimate["z"][g]] = 1 / self.d
        self.weights = weights
        self.last_update = self.t
        # Frozen Phase 2b bundles the cadence into _update; reproduce that
        # exact integer formula while replacing its KL allocation step only.
        step = math.isqrt(self.t + 1)
        step += int(step * step < self.t + 1)
        self.next_update = self.t + max(1, step)
        wall_seconds, cpu_seconds = time.perf_counter() - wall_start, time.process_time() - cpu_start
        self.planner_seconds += wall_seconds
        self.planner_cpu_seconds += cpu_seconds
        self.last_estimate = {
            **estimate,
            "online": self.t,
            "alpha_effective": self.alpha,
            "weights": self.weights.tolist(),
            "allocation_rule": "uniform_coordinates_current_estimated_better_format",
            "paid_type_target_mass": 0.,
            "update_seconds": wall_seconds,
            "update_cpu_seconds": cpu_seconds,
            "next_update": self.next_update,
            "arithmetic_scope": "float64_simple_target_no_KL_optimization",
        }
        self.estimates.append(self.last_estimate)
