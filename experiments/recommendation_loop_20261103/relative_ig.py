"""Separate post-hoc IG tie repair; the original policy remains frozen.

The quadrature posterior, order, forced schedule, observation handling, and
other allocation arms are inherited unchanged. Positive information scores
are compared with relative tolerance 64*machine_epsilon*abs(maximum_score),
with no absolute tolerance floor. Counts break ties, then action index.
"""
from __future__ import annotations

import numpy as np

from policies import ObservablePolicy, forced_action


class RelativeIGPolicy(ObservablePolicy):
    """Change only non-forced ``decision_ig`` action tie handling."""

    def next(self):
        if self.name != "decision_ig":
            return super().next()
        if self.pending is not None:
            raise RuntimeError("observe pending action first")

        # Keep the original policy's state bookkeeping and force rule.
        self.cumulative += self.weights
        forced = forced_action(self.t, self.d)
        details = {"forced": forced is not None, "update_count": len(self.updates)}
        if forced is not None:
            action = forced
            details["rule"] = "forced_exploration"
        else:
            scores = np.asarray(self.posterior.scores(), dtype=float)
            if scores.shape != (2 * self.d,) or np.any(~np.isfinite(scores)):
                raise ArithmeticError("invalid information-gain scores")
            best = float(scores.max())
            tolerance = 64 * np.finfo(float).eps * abs(best)
            ties = np.flatnonzero(scores >= best - tolerance)
            actual = self.counts.sum(axis=2).reshape(-1)
            # For exactly all-zero scores tolerance is zero and every action
            # ties, so this also gives the requested least-count fallback.
            action = int(ties[np.argmin(actual[ties])])
            details.update(
                rule="quadrature_decision_information_gain",
                selected_gain=float(scores[action]),
                maximum_gain=best,
                gain_tie_rule="relative_64_machine_epsilon_no_absolute_floor",
                gain_tie_tolerance=float(tolerance),
            )
        self.pending = int(action)
        self.last_choice = details
        return int(action)
