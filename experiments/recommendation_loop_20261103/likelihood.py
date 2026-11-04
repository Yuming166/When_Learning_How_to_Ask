"""Public-data-only joint likelihood for a bounded recommendation experiment.

The floating point fits in this module are for allocation and screening only.
Use ``CertifiedDecisionGate`` for every authorized stopping decision.
"""

from __future__ import annotations

from decimal import Decimal, DecimalException
from fractions import Fraction
from operator import index

import numpy as np


MAX_DIMENSION = 6
MAX_GROUPS = 2
MAX_TOTAL_OBSERVATIONS = 2**50
MAX_CONSTANT_BITS = 4096


def _integer(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must contain integers, not booleans")
    try:
        return int(index(value))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain integers") from exc


def _sequence(value, name):
    if isinstance(value, (str, bytes, dict)):
        raise ValueError(f"{name} must be a finite sequence")
    try:
        return tuple(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite sequence") from exc


def _rational(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite rational constant")
    if isinstance(value, str) and len(value) > 2500:
        raise ValueError(f"{name} exceeds bounded constant scope")
    try:
        if isinstance(value, (float, np.floating)):
            result = Fraction.from_float(float(value))
        elif isinstance(value, Decimal):
            if (not value.is_finite() or abs(value.adjusted()) > 1233
                    or len(value.as_tuple().digits) > 1234):
                raise ValueError(f"{name} exceeds bounded constant scope")
            result = Fraction(value)
        elif isinstance(value, str):
            # Reject huge decimal exponents before Fraction constructs integers.
            if "/" in value:
                parts = value.strip().split("/")
                if len(parts) != 2 or any(len(part.strip().lstrip("+-")) > 1234 for part in parts):
                    raise ValueError(f"{name} exceeds bounded constant scope")
                result = Fraction(value)
            else:
                decimal = Decimal(value)
                if (not decimal.is_finite() or abs(decimal.adjusted()) > 1233
                        or len(decimal.as_tuple().digits) > 1234):
                    raise ValueError(f"{name} exceeds bounded constant scope")
                result = Fraction(decimal)
        elif isinstance(value, Fraction):
            result = value
        else:
            result = Fraction(_integer(value, name))
    except (TypeError, ValueError, ZeroDivisionError, OverflowError, DecimalException) as exc:
        raise ValueError(f"{name} must be a finite rational constant") from exc
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_CONSTANT_BITS:
        raise ValueError(f"{name} exceeds {MAX_CONSTANT_BITS}-bit constant scope")
    return result


class JointLikelihood:
    """Enumerate every sign/type state and fit the continuous ordered channel.

    Public keys are exactly d, groups, eta, catalogue. Groups is a contiguous
    zero-based membership vector; catalogue has exactly offsets and slopes,
    defining utility[i] = offsets[i] + slopes[i] dot theta. Every cube vertex
    must have one unique maximizing item. An item is its zero-based row index.
    A theta-mask bit of 1 means theta[j] = -1; a type-mask bit is the better
    format z[g]. Raw answer 1 is positive. There are no labelled calibration
    streams or type-report actions in this observation model.
    """

    def __init__(self, public):
        if not isinstance(public, dict) or set(public) != {"d", "groups", "eta", "catalogue"}:
            raise ValueError("public must contain exactly d, groups, eta, catalogue")
        self.d = _integer(public["d"], "d")
        if not 1 <= self.d <= MAX_DIMENSION:
            raise ValueError(f"d must be in [1,{MAX_DIMENSION}]")
        self.groups = tuple(_integer(v, "groups") for v in _sequence(public["groups"], "groups"))
        if len(self.groups) != self.d:
            raise ValueError("groups must have length d")
        labels = set(self.groups)
        self.G = len(labels)
        if not 1 <= self.G <= MAX_GROUPS or labels != set(range(self.G)):
            raise ValueError("groups must have contiguous zero-based labels and 1 <= G <= 2")
        if not isinstance(public["eta"], str):
            raise ValueError("eta must be an exact rational string, for example '1/100'")
        self.eta = _rational(public["eta"], "eta")
        if not 0 < self.eta < Fraction(1, 2):
            raise ValueError("eta must be in (0,1/2)")
        self.upper = 1 - self.eta
        catalogue = public["catalogue"]
        if not isinstance(catalogue, dict) or set(catalogue) != {"offsets", "slopes"}:
            raise ValueError("catalogue must contain exactly offsets and slopes")
        self.offsets = tuple(_rational(v, "offsets") for v in _sequence(catalogue["offsets"], "offsets"))
        self.slopes = tuple(tuple(_rational(v, "slopes") for v in _sequence(row, "slopes"))
                            for row in _sequence(catalogue["slopes"], "slopes"))
        self.n_items = len(self.offsets)
        if not self.n_items or len(self.slopes) != self.n_items or any(len(row) != self.d for row in self.slopes):
            raise ValueError("catalogue must have nonempty offsets and slopes of shape (items,d)")
        self.theta_masks = np.arange(2**self.d, dtype=np.int64)
        self.theta_bits = (self.theta_masks[:, None] >> np.arange(self.d)) & 1
        self.theta_signs = 1 - 2 * self.theta_bits
        self.z_masks = np.arange(2**self.G, dtype=np.int64)
        self.z_bits = (self.z_masks[:, None] >> np.arange(self.G)) & 1
        # Exact rational utility comparisons establish the recommendation classes.
        winners = []
        for theta in self.theta_signs:
            values = [offset + sum(slope * int(sign) for slope, sign in zip(row, theta))
                      for offset, row in zip(self.offsets, self.slopes)]
            best = max(values)
            if values.count(best) != 1:
                raise ValueError("catalogue must have a unique winner at every full-cube theta")
            winners.append(values.index(best))
        self.winner_by_theta = np.asarray(winners, dtype=np.int64)
        # First occurrence uses the same deterministic theta-mask tie order as estimate.
        self.items = tuple(dict.fromkeys(winners))
        self.high_mask = (np.arange(2)[None, None, :]
                          == self.z_bits[:, self.groups, None]).astype(np.int64)
        for array in (self.theta_masks, self.theta_bits, self.theta_signs, self.z_masks,
                      self.z_bits, self.winner_by_theta, self.high_mask):
            array.setflags(write=False)

    def validate_counts(self, counts):
        """Reject coercion, floats, booleans, negatives, overflow and wrong shape."""
        try:
            # Object conversion retains bool/float types in mixed Python lists.
            array = np.asarray(counts, dtype=object)
        except (TypeError, ValueError) as exc:
            raise ValueError("counts must have shape (d,2,2)") from exc
        if array.shape != (self.d, 2, 2):
            raise ValueError("counts must have shape (d,2,2)")
        parsed = [_integer(v, "counts") for v in array.flat]
        if any(v < 0 for v in parsed):
            raise ValueError("counts must be nonnegative")
        if sum(parsed) > MAX_TOTAL_OBSERVATIONS:
            raise ValueError("total observations exceed bounded scope")
        return np.asarray(parsed, dtype=np.int64).reshape(self.d, 2, 2)

    def validate_candidate(self, candidate_item):
        if candidate_item is None:
            return None
        item = _integer(candidate_item, "candidate_item")
        if item not in self.items:
            raise ValueError("candidate_item must win at some full-cube theta")
        return item

    def _sufficient_statistics(self, data):
        """Integer arrays (theta,z), never approximate count aggregation."""
        positive, negative = data[:, :, 1], data[:, :, 0]
        success = np.where(self.theta_bits[:, :, None] == 0, positive, negative)
        high_s = np.einsum("tja,zja->tz", success, self.high_mask, dtype=np.int64)
        high_n = np.einsum("ja,zja->z", data.sum(axis=2), self.high_mask, dtype=np.int64)
        high_n = np.broadcast_to(high_n, high_s.shape)
        low_s = success.sum(axis=(1, 2))[:, None] - high_s
        low_n = int(data.sum()) - high_n
        return high_s, high_n, low_s, low_n

    def best_table(self, counts):
        """Floating fits and likelihoods for ALL states; never a stop certificate."""
        data = self.validate_counts(counts)
        hs, hn, ls, ln = self._sufficient_statistics(data)
        upper = float(self.upper)
        p = np.divide(hs, hn, out=np.full(hs.shape, .5), where=hn != 0)
        q = np.divide(ls, ln, out=np.full(ls.shape, .5), where=ln != 0)
        p, q = np.clip(p, .5, upper), np.clip(q, .5, upper)
        pooled = (hn != 0) & (ln != 0) & (p < q)
        rate = np.divide(hs + ls, hn + ln, out=np.full(hs.shape, .5), where=(hn + ln) != 0)
        p[pooled] = q[pooled] = np.clip(rate[pooled], .5, upper)
        p = np.where(hn == 0, q, p)
        # Complementary rates remain stable if a rational upper bound rounds to 1.
        eta_float = float(self.eta)
        if eta_float == 0:
            raise ValueError("eta is below floating policy scope; exact gate remains available")
        p_fail, q_fail = np.maximum(eta_float, 1 - p), np.maximum(eta_float, 1 - q)
        loglik = (hs * np.log1p(-p_fail) + (hn - hs) * np.log(p_fail)
                  + ls * np.log1p(-q_fail) + (ln - ls) * np.log(q_fail))
        return {"p": p, "q": q, "loglik": loglik,
                "high_successes": hs, "high_totals": hn,
                "low_successes": ls, "low_totals": ln}

    # Convenient spelling for external policy code.
    besttable = best_table

    def estimate(self, counts):
        table = self.best_table(counts)
        theta, z = np.unravel_index(int(np.argmax(table["loglik"])), table["loglik"].shape)
        return {"theta_mask": int(theta), "z_mask": int(z),
                "p": float(table["p"][theta, z]), "q": float(table["q"][theta, z]),
                "item": int(self.winner_by_theta[theta])}

    def decision_gap(self, counts, candidate_item=None):
        """Difference between best same-item and best different-item profiles.

        The threshold is deliberately absent. Values here only screen when to
        invoke exact certification and must never authorize an output.
        """
        candidate = self.validate_candidate(candidate_item)
        table = self.best_table(counts)
        profile = table["loglik"].max(axis=1)
        class_loglik = {int(item): float(profile[self.winner_by_theta == item].max()) for item in self.items}
        if candidate is None:
            candidate = int(self.winner_by_theta[int(np.argmax(profile))])
        alternatives = [value for item, value in class_loglik.items() if item != candidate]
        wrong = max(alternatives) if alternatives else float("-inf")
        return {"item": candidate, "gap": class_loglik[candidate] - wrong,
                "candidate_loglik": class_loglik[candidate], "alternative_loglik": wrong,
                "class_loglik": class_loglik, "certified": False}
