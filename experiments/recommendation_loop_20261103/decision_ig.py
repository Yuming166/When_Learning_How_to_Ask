"""Greedy information about the best catalogue item, with joint rate inference.

This is a numerical allocation baseline, not a stopping rule or certificate.
The discrete theta/type prior is enumerated exactly; the continuous uniform
rate prior is approximated by Gauss--Legendre quadrature on an ordered triangle.
Only the public schema and observed task replies are accepted.
"""
from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from functools import lru_cache
from numbers import Integral, Real

import numpy as np


def _integer(value, name, lower, upper=None):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    value = int(value)
    if value < lower or (upper is not None and value > upper):
        raise ValueError(f"{name} is outside the supported range")
    return value


def _rational(value, name):
    """Interpret decimal inputs as decimals, avoiding binary-float tie tests."""
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite rational number")
    if isinstance(value, Fraction):
        return value
    if not isinstance(value, (str, Integral, Real)):
        raise ValueError(f"{name} must be a finite rational number")
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite rational number") from exc


def _public_design(public):
    if not isinstance(public, Mapping):
        raise ValueError("public must be a mapping")
    required = {"d", "groups", "catalogue"}
    if not required <= set(public) or set(public) - required - {"eta"}:
        raise ValueError("public accepts only d, groups, eta, and catalogue")
    d = _integer(public["d"], "d", 1, 6)
    try:
        groups = tuple(_integer(g, "group membership", 0, 1)
                       for g in public["groups"])
    except TypeError as exc:
        raise ValueError("groups must be a length-d membership vector") from exc
    if len(groups) != d or set(groups) != set(range(max(groups, default=-1) + 1)):
        raise ValueError("groups must use contiguous IDs 0..G-1 and cover d coordinates")
    eta_input = public.get("eta", "1/100")
    if not isinstance(eta_input, str):
        raise ValueError("eta must be a rational string")
    eta = _rational(eta_input, "eta")
    if not 0 < eta < Fraction(1, 2) or not 0 < float(eta) < .5:
        raise ValueError("eta must be representable and strictly between 0 and 1/2")
    catalogue = public["catalogue"]
    if not isinstance(catalogue, Mapping) or set(catalogue) != {"offsets", "slopes"}:
        raise ValueError("catalogue accepts exactly offsets and slopes")
    try:
        offsets = tuple(_rational(v, "catalogue offset") for v in catalogue["offsets"])
        slopes = tuple(tuple(_rational(v, "catalogue slope") for v in row)
                       for row in catalogue["slopes"])
    except TypeError as exc:
        raise ValueError("catalogue offsets/slopes must be sequences") from exc
    if not offsets or len(slopes) != len(offsets) or any(len(row) != d for row in slopes):
        raise ValueError("catalogue must have one length-d slope row per offset")
    winners = []
    for mask in range(1 << d):
        signs = tuple(-1 if (mask >> j) & 1 else 1 for j in range(d))
        utilities = [b + sum(v * s for v, s in zip(row, signs))
                     for b, row in zip(offsets, slopes)]
        best = max(utilities)
        tied = [i for i, utility in enumerate(utilities) if utility == best]
        if len(tied) != 1:
            raise ValueError(f"catalogue has tied best items {tied} at theta mask {mask}")
        winners.append(tied[0])
    return d, groups, eta, len(offsets), np.asarray(winners, dtype=np.int64)


@lru_cache(maxsize=16)
def _design(d, groups, eta, order):
    """Immutable likelihood table, shared across independent posterior objects."""
    g_count = max(groups) + 1
    theta_count, type_count = 1 << d, 1 << g_count
    x, w = np.polynomial.legendre.leggauss(order)
    u, w = (x + 1) / 2, w / 2
    s, t = np.meshgrid(u, u, indexing="ij")
    length = .5 - float(eta)
    p = (.5 + length * s).ravel()
    q = (.5 + length * s * t).ravel()
    # dp dq = length * (p-.5) ds dt. Dividing by triangle area
    # length**2 / 2 gives the normalized density factor 2*s.
    node_weights = (2 * s * w[:, None] * w[None, :]).ravel()
    node_weights /= node_weights.sum()
    theta_masks = np.arange(theta_count, dtype=np.int64)
    type_masks = np.arange(type_count, dtype=np.int64)
    likelihood = np.empty((2 * d, theta_count * type_count * order**2))
    for action in range(2 * d):
        j, fmt = divmod(action, 2)
        better = ((type_masks >> groups[j]) & 1) == fmt
        reliability = np.where(better[:, None], p[None, :], q[None, :])
        negative = ((theta_masks >> j) & 1).astype(bool)
        likelihood[action] = np.where(negative[:, None, None],
                                      1 - reliability[None, :, :],
                                      reliability[None, :, :]).ravel()
    if not np.all((likelihood > 0) & (likelihood < 1)):
        raise ValueError("quadrature rates cannot be represented strictly inside (0, 1)")
    prior = np.tile(node_weights, theta_count * type_count) / (theta_count * type_count)
    log_positive, log_negative = np.log(likelihood), np.log1p(-likelihood)
    arrays = (likelihood, prior, log_positive, log_negative, p, q, node_weights)
    for array in arrays:
        array.setflags(write=False)
    return arrays


def _entropy(probability):
    probability = np.asarray(probability, dtype=float)
    tolerance = 128 * np.finfo(float).eps
    if np.any((probability < -tolerance) | (probability > 1 + tolerance)):
        raise FloatingPointError("invalid probability in entropy computation")
    probability = np.clip(probability, 0, 1)
    out = np.zeros_like(probability)
    positive = probability > 0
    out[positive] = -probability[positive] * np.log(probability[positive])
    return np.sum(out, axis=-1)


def _bernoulli_kl(mean, delta):
    """KL(Ber(mean+delta), Ber(mean)), avoiding a spurious small-score floor."""
    mean = np.broadcast_to(mean, delta.shape)
    small = np.abs(delta) < 1e-3 * np.minimum(mean, 1 - mean)
    value = np.zeros_like(delta)
    # The omitted terms are tiny relative to delta**2 in this local region.
    for n in range(2, 9):
        value[small] += delta[small]**n / (n * (n - 1)) * (
            (-1)**n / mean[small]**(n - 1) + 1 / (1 - mean[small])**(n - 1))
    outside = ~small
    if np.any(outside):
        probability = np.clip(mean[outside] + delta[outside], 0, 1)
        other = 1 - probability
        terms = np.zeros_like(probability)
        positive = probability > 0
        terms[positive] = probability[positive] * np.log(probability[positive] / mean[outside][positive])
        positive = other > 0
        terms[positive] += other[positive] * np.log(other[positive] / (1 - mean[outside][positive]))
        value[outside] = terms
    # At the branch boundary a negative value beyond roundoff signals a bug.
    if np.any(value < -128 * np.finfo(float).eps):
        raise FloatingPointError("negative Bernoulli KL beyond floating-point tolerance")
    return np.maximum(value, 0)


class QuadratureDecisionIG:
    """Expected next-reply information in nats about the best affine item.

    ``groups[j]`` is the zero-based group ID. Theta mask bit 1 means a negative
    preference; reply 1 means a positive preference. Type mask bit g gives the
    better format in group g. ``target='theta'`` is an optional diagnostic
    comparator; the recommendation baseline uses the default ``target='item'``.
    """

    def __init__(self, public, order=6, *, target="item"):
        self.d, self.groups, self.eta, self.item_count, self._winners = _public_design(public)
        self.order = _integer(order, "quadrature order", 1)
        if target not in {"item", "theta"}:
            raise ValueError("target must be 'item' or 'theta'")
        self.target = target
        self.group_count = max(self.groups) + 1
        self.theta_count, self.type_count = 1 << self.d, 1 << self.group_count
        (self._positive, prior, self._log_positive, self._log_negative,
         self._p, self._q, self._node_weights) = _design(
             self.d, self.groups, self.eta, self.order)
        self._weights = prior.copy()
        self._log_weights = np.log(prior)
        self._counts = np.zeros((2 * self.d, 2), dtype=np.int64)
        self._observations = 0
        self._log_evidence = 0.
        self._score_cache = None

    def observe(self, action_int, answer_int):
        """Condition on every observed task reply, including forced actions."""
        action = _integer(action_int, "action", 0, 2 * self.d - 1)
        answer = _integer(answer_int, "answer", 0, 1)
        increment = self._log_positive[action] if answer else self._log_negative[action]
        updated = self._log_weights + increment
        largest = float(updated.max())
        normalizer = largest + float(np.log(np.exp(updated - largest).sum()))
        self._log_weights = updated - normalizer
        self._weights = np.exp(self._log_weights)
        self._log_evidence += normalizer
        self._counts[action, answer] += 1
        self._observations += 1
        self._score_cache = None

    def _summary(self):
        if self._score_cache is not None:
            return self._score_cache
        weights = self._weights.reshape(self.theta_count, self.type_count * self.order**2)
        theta_probability = weights.sum(axis=1)
        normalizer = float(theta_probability.sum())
        theta_probability /= normalizer
        by_theta = np.einsum("atn,tn->at", self._positive.reshape(2 * self.d, self.theta_count, -1),
                             weights, optimize=False) / normalizer
        item_probability = np.bincount(self._winners, weights=theta_probability,
                                       minlength=self.item_count)
        if self.target == "item":
            probability = item_probability
            joint_positive = np.stack([np.bincount(self._winners, weights=row,
                                                   minlength=self.item_count) for row in by_theta])
        else:
            probability, joint_positive = theta_probability, by_theta
        target_normalizer = float(probability.sum())
        probability = probability / target_normalizer
        joint_positive = joint_positive / target_normalizer
        if self.target == "item":
            item_probability = probability
        else:
            theta_probability = probability
        # Remove zero-mass classes before division (some catalogue items never win).
        active = probability > 0
        mass, joint_positive = probability[active], joint_positive[:, active]
        conditional_positive = np.clip(joint_positive / mass[None, :], 0, 1)
        predictive_positive = np.clip(joint_positive.sum(axis=1), 0, 1)
        if np.any((predictive_positive <= 0) | (predictive_positive >= 1)):
            raise FloatingPointError("posterior predictive lost both outcomes numerically")
        # Pairwise differences preserve the modal-class deviation when its
        # conditional probability and the mean round to the same float.
        delta = np.einsum("aij,j->ai", conditional_positive[:, :, None] -
                          conditional_positive[:, None, :], mass, optimize=False)
        information = (_bernoulli_kl(predictive_positive[:, None], delta) * mass[None, :]).sum(axis=1)
        joint_negative = np.maximum(mass[None, :] - joint_positive, 0)
        answer_probability = np.column_stack((1 - predictive_positive, predictive_positive))
        posterior_entropies = np.column_stack((
            _entropy(joint_negative / answer_probability[:, 0, None]),
            _entropy(joint_positive / answer_probability[:, 1, None])))
        entropy = float(_entropy(mass))
        expected_entropy = np.sum(answer_probability * posterior_entropies, axis=1)
        self._score_cache = {"scores": information, "theta_probability": theta_probability,
                             "item_probability": item_probability,
                             "target_probability": probability,
                             "answer_probability": answer_probability,
                             "posterior_entropies": posterior_entropies,
                             "entropy": entropy, "expected_entropy": expected_entropy}
        return self._score_cache

    def scores(self):
        """Return one greedy expected entropy reduction for each action 2*j+fmt."""
        return self._summary()["scores"].copy()

    def diagnostics(self):
        """Return JSON-serializable numerical diagnostics, never certification."""
        summary = self._summary()
        weights = self._weights.reshape(self.theta_count, self.type_count, self.order**2)
        node_probability = weights.sum(axis=(0, 1))
        scores = summary["scores"]
        tolerance = 64 * np.finfo(float).eps * max(1., float(scores.max()))
        return {
            "allocation_rule": "greedy_expected_information_about_best_item" if self.target == "item"
                               else "greedy_expected_information_about_full_theta_diagnostic",
            "target": self.target, "units": "nats",
            "inference": "Gauss_Legendre_quadrature_approximate_continuous_joint_posterior",
            "discrete_enumeration": "complete_uniform_theta_and_type_prior",
            "rate_prior": "continuous_uniform_on_1/2<q<p<1-eta",
            "quadrature_order": self.order, "quadrature_nodes": self.order**2,
            "joint_states": int(self._weights.size), "observations": self._observations,
            "task_counts": self._counts.tolist(), "posterior_mass": float(self._weights.sum()),
            "theta_probability": summary["theta_probability"].tolist(),
            "item_probability": summary["item_probability"].tolist(),
            "type_probability": weights.sum(axis=(0, 2)).tolist(),
            "target_probability": summary["target_probability"].tolist(),
            "posterior_mean_p": float(node_probability @ self._p),
            "posterior_mean_q": float(node_probability @ self._q),
            "posterior_means_used_for_likelihood": False,
            "posterior_predictive": summary["answer_probability"].tolist(),
            "target_entropy": summary["entropy"],
            "entropy_after_answer": summary["posterior_entropies"].tolist(),
            "expected_entropy_after_answer": summary["expected_entropy"].tolist(),
            "information_scores": scores.tolist(),
            "entropy_subtraction_max_abs_difference": float(np.max(np.abs(
                summary["entropy"] - summary["expected_entropy"] - scores))),
            "score_tie_tolerance": tolerance,
            "maximizers_within_float_tolerance": np.flatnonzero(scores.max() - scores <= tolerance).tolist(),
            "score_tie_handling": "scores_only; caller_controls_action_tie_breaking",
            "catalogue_tie_handling": "reject_exact_rational_best_item_ties_at_any_theta",
            "log_transcript_evidence": float(self._log_evidence),
            "stopping_rule": None, "posterior_certification": False,
            "numerical_error_certificate": False,
        }
