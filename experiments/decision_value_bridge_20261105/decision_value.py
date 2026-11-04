"""One-step posterior Bayes decision value; allocation only, no stopping claim."""
from __future__ import annotations
import numpy as np
from decision_ig import QuadratureDecisionIG
from relative_ig import RelativeIGPolicy
from policies import forced_action

class QuadratureDecisionValue(QuadratureDecisionIG):
    def scores(self):
        # Same enumerated theta/type prior, Q6 rate nodes, and log posterior as IG.
        weights = self._weights.reshape(self.theta_count, -1)
        total = weights.sum()
        probability = np.bincount(self._winners, weights=weights.sum(axis=1), minlength=self.item_count) / total
        incumbent = int(np.argmax(probability))
        gains = np.zeros(2*self.d)
        for y in (0, 1):
            likelihood = self._positive if y else 1-self._positive
            by_theta = np.einsum('atn,tn->at', likelihood.reshape(2*self.d, self.theta_count, -1), weights, optimize=False) / total
            joint = np.stack([np.bincount(self._winners, weights=row, minlength=self.item_count) for row in by_theta])
            # sum_y max_k P(k,y) - max_k P(k) equals this expression.
            # Each branch contains an exactly zero incumbent contrast; if no
            # reply can change the MAP choice, gain is exactly zero, not a
            # spurious subtraction residual at the 1e-16 scale.
            gains += np.max(joint-joint[:, incumbent, None], axis=1)
        if np.any(~np.isfinite(gains)) or np.any(gains < 0):
            raise ArithmeticError('invalid decision value')
        return gains

    def diagnostics(self):
        result = super().diagnostics()
        result.update(allocation_rule='one_step_expected_increase_in_posterior_MAP_success',
                      units='probability_of_correct_recommendation',
                      information_score_units='nats',
                      decision_value_units='probability_of_correct_recommendation',
                      decision_value_scores=self.scores().tolist(),
                      decision_value_zero_rule='exact_zero_if_incumbent_maximizes_both_reply_joint_masses',
                      asymptotic_optimality_proved=False)
        return result

class BridgePolicy(RelativeIGPolicy):
    def __init__(self, name, public, **kwargs):
        super().__init__('decision_ig' if name == 'decision_value' else name, public, **kwargs)
        self.name = name
        if name == 'decision_value':
            self.posterior = QuadratureDecisionValue(public, order=kwargs.get('quadrature_order',6))

    def next(self):
        if self.name != 'decision_value':
            return super().next()
        if self.pending is not None:
            raise RuntimeError('observe pending action first')
        self.cumulative += self.weights
        mandatory = forced_action(self.t, self.d)
        details = {'forced': mandatory is not None, 'update_count': len(self.updates)}
        if mandatory is not None:
            action = mandatory
            details['rule'] = 'forced_exploration'
        else:
            scores = self.posterior.scores()
            best = float(scores.max())
            tolerance = 64*np.finfo(float).eps*abs(best)
            ties = np.flatnonzero(scores >= best-tolerance)
            counts = self.counts.sum(axis=2).reshape(-1)
            action = int(ties[np.argmin(counts[ties])])
            details.update(rule='quadrature_decision_value', selected_gain=float(scores[action]),
                           maximum_gain=best, gain_tie_tolerance=float(tolerance),
                           zero_gain_fallback=best == 0,
                           gain_tie_rule='relative_64_machine_epsilon_then_least_count_then_index')
        self.pending = int(action)
        self.last_choice = details
        return int(action)
