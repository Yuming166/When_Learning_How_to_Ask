"""Estimator-controlled task/type allocation ablation.

Historical classes are imported read-only. Type uncertainty used by a new
allocation rule never enters the shared forced-only allocation estimator.
"""

import math
import time

import numpy as np

from .bootstrap import P2B, P2C  # noqa: F401
from phase2b.aligned import TheoryAlignedTracking
from phase2c.decaying import DecayingRepeatAndCompare


# Literal class aliases preserve all frozen behavior, including diagnostics.
AlignedFull = TheoryAlignedTracking
DRRCNoType = DecayingRepeatAndCompare


class AlignedNoType(TheoryAlignedTracking):
    """Frozen Aligned with type actions removed from its allocation problem.

    The external experiment still receives the original public specification
    and profiles unknown group types. This copied planning input changes only
    the optimizer's action availability: its returned c_g is exactly zero.
    """

    def __init__(self, public, calibration, planning_R):
        planning_public = dict(public)
        planning_public["type_accuracy"] = None
        super().__init__(planning_public, calibration, planning_R)


class DRRCType(DecayingRepeatAndCompare):
    """D-RRC with ongoing, workload-balanced type-certainty acquisition.

    Auxiliary task and type likelihood ratios govern allocation only. They
    never replace forced-only theta/z/p/q, and are not stopping certificates.
    This simple decoupled rule performs no joint information optimization.
    The public single-group/zero-reference control uses frozen D-RRC exactly.
    """

    def _update(self):
        if self.G == 1 and self.reference_count == 0:
            # Theory_Note Theorems 2/3 and Corollary 3.1: at alpha=0,
            # G=1 has the uniform-good oracle leading coefficient, with no
            # first-order type allocation, for every admissible p>q.
            # This public-structure guard is not a finite-R uselessness claim.
            super()._update()
            self.last_estimate.update({
                "allocation_rule": "public_structure_guard_exact_frozen_D_RRC",
                "public_structure_guard": "single_group_zero_reference_count",
                "type_acquisition_enabled": False,
                "guard_scope": "leading_coefficient_structure_not_finite_R_type_uselessness",
            })
            return
        wall_start, cpu_start = time.perf_counter(), time.process_time()
        estimate = self._estimate()
        threshold = self.planning_R + math.log(2 * self.d + 2 * self.G)
        p, q = estimate["p"], estimate["q"]
        logit_p = math.log(p / (1 - p))
        logit_q = math.log(q / (1 - q))
        sign_drift = (2 * p - 1) * logit_p
        # Projected p is strictly above 1/2. Numerical failure must remain
        # visible rather than being hidden by a parameter-dependent floor.
        if not math.isfinite(sign_drift) or sign_drift <= 0:
            raise FloatingPointError("nonpositive estimated task information")
        signed_task_evidence = np.zeros(self.d)
        task_workload = np.zeros(self.d)
        for g, members in enumerate(self.groups):
            preferred = estimate["z"][g]
            for j in members:
                balance = self.counts[j, :, 1] - self.counts[j, :, 0]
                signed_task_evidence[j] = (
                    int(balance[preferred]) * logit_p + int(balance[1 - preferred]) * logit_q
                )
                task_workload[j] = max(0., threshold - abs(signed_task_evidence[j])) / sign_drift

        type_llr = np.zeros(self.G)
        type_deficit = np.zeros(self.G)
        type_drift = np.zeros(self.G)
        type_workload = np.zeros(self.G)
        if self.type_accuracy is not None:
            for g, accuracy in enumerate(self.type_accuracy):
                log_odds = math.log(accuracy / (1 - accuracy))
                type_llr[g] = (2 * sum(self.types[g]) - len(self.types[g])) * log_odds
                type_drift[g] = (2 * accuracy - 1) * log_odds
                type_deficit[g] = max(0., threshold - abs(type_llr[g]))
                type_workload[g] = type_deficit[g] / type_drift[g]

        total_task_work = math.fsum(task_workload)
        total_type_work = math.fsum(type_workload)
        total_work = total_task_work + total_type_work
        if not math.isfinite(total_work):
            raise FloatingPointError("nonfinite estimated acquisition workload")
        weights = np.zeros(self.E)
        if total_work > 0:
            weights[self.L:] = type_workload / total_work
            task_mass = total_task_work / total_work
        else:
            task_mass = 1.
        for g, members in enumerate(self.groups):
            for j in members:
                weights[2 * j + estimate["z"][g]] = task_mass / self.d
        # When no type action is available, or all type deficits are zero,
        # this is exactly the frozen D-RRC target, including after W=0.
        if total_type_work == 0:
            weights[:] = 0.
            for g, members in enumerate(self.groups):
                for j in members:
                    weights[2 * j + estimate["z"][g]] = 1 / self.d
        if np.any(~np.isfinite(weights)) or np.any(weights < 0) or abs(weights.sum() - 1) > 1e-12:
            raise FloatingPointError("invalid workload-balanced allocation")
        self.weights = weights
        self.last_update = self.t
        step = math.isqrt(self.t + 1)
        step += int(step * step < self.t + 1)
        self.next_update = self.t + max(1, step)
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        self.planner_seconds += wall_seconds
        self.planner_cpu_seconds += cpu_seconds
        self.last_estimate = {
            **estimate,
            "online": self.t,
            "alpha_effective": self.alpha,
            "weights": self.weights.tolist(),
            "allocation_rule": "uniform_estimated_good_tasks_with_active_type_certainty",
            "public_structure_guard": None,
            "type_acquisition_enabled": self.type_accuracy is not None,
            "auxiliary_threshold": threshold,
            "auxiliary_task_signed_llr": signed_task_evidence.tolist(),
            "auxiliary_task_workload": task_workload.tolist(),
            "auxiliary_group_task_workload": [float(sum(task_workload[list(members)])) for members in self.groups],
            "auxiliary_type_signed_llr": type_llr.tolist(),
            "auxiliary_type_deficit": type_deficit.tolist(),
            "auxiliary_type_expected_llr_increment": type_drift.tolist(),
            "auxiliary_type_workload": type_workload.tolist(),
            "auxiliary_total_task_workload": total_task_work,
            "auxiliary_total_type_workload": total_type_work,
            "auxiliary_scope": "allocation_proxies_only_not_a_stopping_certificate",
            "paid_type_target_mass": float(weights[self.L:].sum()),
            "update_seconds": wall_seconds,
            "update_cpu_seconds": cpu_seconds,
            "next_update": self.next_update,
            "arithmetic_scope": "float64_simple_target_no_joint_information_optimization",
        }
        self.estimates.append(self.last_estimate)


SAMPLERS = {
    "Aligned-Full": AlignedFull,
    "Aligned-NoType": AlignedNoType,
    "D-RRC-NoType": DRRCNoType,
    "D-RRC-Type": DRRCType,
}


def construct_sampler(name, public, calibration, planning_R):
    """Construct a declared ablation arm; unknown names fail closed."""
    return SAMPLERS[name](public, calibration, planning_R)
