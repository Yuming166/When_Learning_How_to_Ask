"""Observable plug-in information geometry and an exact fresh-rate warm solver.

``radial_cost`` separates every nonempty subset of fact flips, every group-type
flip, and continuous ordered alternative rates. Calibration alpha=M/R is fixed
while the online allocation is scaled. ``build_cuts`` is only a finite-cut lower
bound for training; it is not an exact information objective or a certificate.
All computations are float64 numerical calculations, not interval certificates.
No experiments, model calls, or fitting run on import.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, linprog

from . import bootstrap  # noqa: F401 -- only installs frozen import paths
from phase2a.coefficients import (
    alternatives as group_alternatives,
    coefficients_at,
    inner,
    kl,
)


OBSERVABLE_KEYS = frozenset({
    "schema", "d", "groups", "eta", "known_s", "counts", "forced_counts",
    "type_report_counts", "calibration", "R", "online", "online_cap",
    "remaining", "estimate", "action_mask",
})
ESTIMATE_KEYS = frozenset({"p", "q", "theta_prob", "z_prob", "z"})


@dataclass
class _Geometry:
    d: int
    groups: tuple
    eta: float
    p: float
    q: float
    alpha: float
    legal: np.ndarray
    means: np.ndarray
    required: np.ndarray
    high: np.ndarray
    type_coefficients: np.ndarray
    fact_masks: np.ndarray
    type_masks: np.ndarray

    @property
    def G(self):
        return len(self.groups)

    @property
    def A(self):
        return 2 * self.d + self.G

    def coefficients(self, u, v):
        """One independently chosen (u,v) per discrete alternative."""
        u = np.broadcast_to(np.asarray(u, dtype=float), (len(self.high),))
        v = np.broadcast_to(np.asarray(v, dtype=float), (len(self.high),))
        candidate = np.where(self.high, u[:, None], v[:, None])
        # Complementing the reference mean gives D(r,1-x)=D(1-r,x).
        tasks = np.maximum(0., kl(self.required, candidate))
        return np.concatenate([tasks, self.type_coefficients], axis=1)

    def fit(self, allocation):
        task = allocation[:2 * self.d]
        high_weight = self.high * task[None, :]
        low_weight = (~self.high) * task[None, :]
        nu = self.alpha + high_weight.sum(axis=1)
        nv = self.alpha + low_weight.sum(axis=1)
        su = self.alpha * self.p + (high_weight * self.required).sum(axis=1)
        sv = self.alpha * self.q + (low_weight * self.required).sum(axis=1)
        u = np.full(len(nu), 1 - self.eta)
        v = np.full(len(nv), .5)
        np.divide(su, nu, out=u, where=nu > 0)
        np.divide(sv, nv, out=v, where=nv > 0)
        u = np.clip(u, .5, 1 - self.eta)
        v = np.clip(v, .5, 1 - self.eta)
        violation = u < v
        pooled = np.divide(su + sv, nu + nv, out=np.full_like(su, .5), where=(nu + nv) > 0)
        pooled = np.clip(pooled, .5, 1 - self.eta)
        u = np.where(violation, pooled, u)
        v = np.where(violation, pooled, v)
        coefficients = self.coefficients(u, v)
        offsets = self.alpha * (np.maximum(0., kl(self.p, u)) + np.maximum(0., kl(self.q, v)))
        values = offsets + coefficients @ allocation
        return values, u, v, coefficients, offsets

    def unreachable(self, weights):
        """Detect finite asymptotes <=1 exactly by the positive-weight support.

        Zero online KL requires every observed Bernoulli mean to agree exactly
        with its alternative rate and every observed swapped type to agree.
        The remaining calibration loss is minimized over that zero-KL face.
        This catches missing fact coverage and calibration-only finite limits;
        it does not mistake a very small positive weight for a zero weight.
        """
        support = weights[:2 * self.d] > 0
        for i, high in enumerate(self.high):
            if np.any((self.type_coefficients[i] > 0) & (weights[2 * self.d:] > 0)):
                continue
            fixed = []
            possible = True
            for selector in (high, ~high):
                rr = self.required[i, support & selector]
                if len(rr) == 0:
                    fixed.append(None)
                elif np.any(rr != rr[0]) or not .5 <= rr[0] <= 1 - self.eta:
                    possible = False
                    break
                else:
                    fixed.append(float(rr[0]))
            if not possible:
                continue
            u, v = fixed
            if u is not None and v is not None and u < v:
                continue
            if u is None:
                u = max(self.p, v) if v is not None else self.p
            if v is None:
                v = min(self.q, u)
            limit = self.alpha * (kl(self.p, u) + kl(self.q, v))
            if limit <= 1:
                return True
        return False


def _geometry(state):
    if not isinstance(state, dict) or set(state) != OBSERVABLE_KEYS:
        raise ValueError("information accepts exactly the t2 observable-state fields")
    if state["schema"] != "t2_observable_v1":
        raise ValueError("unsupported observable schema")
    d = state["d"]
    if isinstance(d, bool) or not isinstance(d, (int, np.integer)) or not 1 <= d <= 4:
        raise ValueError("information geometry is bounded to 1<=d<=4")
    groups = tuple(tuple(mm) for mm in state["groups"])
    G = len(groups)
    if not 1 <= G <= 2 or any(not mm for mm in groups):
        raise ValueError("one or two nonempty groups required")
    members = [j for mm in groups for j in mm]
    if any(isinstance(j, bool) or not isinstance(j, (int, np.integer)) for j in members):
        raise ValueError("group members must be integer fact indices")
    if sorted(members) != list(range(d)):
        raise ValueError("groups must partition all facts")
    for name, shape in (("counts", (d, 2, 2)), ("forced_counts", (d, 2, 2)),
                        ("type_report_counts", (G, 2))):
        count = np.asarray(state[name])
        if count.shape != shape or count.dtype.kind not in "iu" or np.any(count < 0):
            raise ValueError("observable count arrays must contain nonnegative integers")
    if np.any(np.asarray(state["forced_counts"]) > np.asarray(state["counts"])):
        raise ValueError("forced counts cannot exceed total counts")
    if any(not isinstance(state[k], (int, np.integer)) or isinstance(state[k], bool)
           for k in ("online", "online_cap", "remaining")):
        raise ValueError("observable budgets must be integers")
    observed = int(np.asarray(state["counts"]).sum() + np.asarray(state["type_report_counts"]).sum())
    if not 0 <= state["online"] <= state["online_cap"] or state["remaining"] != state["online_cap"] - state["online"] or observed != state["online"]:
        raise ValueError("observable time, counts, and remaining budget disagree")
    eta = float(state["eta"])
    estimate = state["estimate"]
    if set(estimate) != ESTIMATE_KEYS:
        raise ValueError("only public posterior point estimates and marginals are accepted")
    p, q = float(estimate["p"]), float(estimate["q"])
    if not 0 < eta < .5 or not .5 <= q < p <= 1 - eta:
        raise ValueError("require ordered finite plug-in rates .5<=q<p<=1-eta")
    z = np.asarray(estimate["z"])
    if z.shape != (G,) or np.any((z != 0) & (z != 1)):
        raise ValueError("estimated group modes must be binary")
    z = z.astype(int)
    for name, length in (("theta_prob", d), ("z_prob", G)):
        values = np.asarray(estimate[name], dtype=float)
        if values.shape != (length,) or np.any(~np.isfinite(values)) or np.any((values < 0) | (values > 1)):
            raise ValueError("invalid observable posterior marginal")
    calibration = state["calibration"]
    if set(calibration) != {"high", "low"}:
        raise ValueError("labelled high and low calibration summaries required")
    totals = []
    for stream in ("high", "low"):
        item = calibration[stream]
        if set(item) != {"successes", "total"}:
            raise ValueError("calibration accepts successes and total only")
        success, total = item["successes"], item["total"]
        if not all(isinstance(x, (int, np.integer)) and not isinstance(x, bool) for x in (success, total)):
            raise ValueError("calibration counts must be integers")
        if not 0 <= success <= total:
            raise ValueError("invalid calibration counts")
        totals.append(total)
    R = float(state["R"])
    if totals[0] != totals[1] or not math.isfinite(R) or R <= 0:
        raise ValueError("equal calibration totals and positive finite R required")
    raw_legal = np.asarray(state["action_mask"])
    if raw_legal.shape != (2 * d + G,) or np.any((raw_legal != 0) & (raw_legal != 1)):
        raise ValueError("action_mask must have 2d+G boolean entries")
    legal = raw_legal.astype(bool)
    if not np.any(legal):
        raise ValueError("at least one legal action required")
    accuracy = state["known_s"]
    if accuracy is None:
        if np.any(legal[2 * d:]):
            raise ValueError("type actions require known finite type accuracies")
        if np.any(np.asarray(state["type_report_counts"])):
            raise ValueError("type reports require known finite type accuracies")
        kappa = np.zeros(G)
    else:
        accuracy = np.asarray(accuracy, dtype=float)
        if accuracy.shape != (G,) or np.any(~np.isfinite(accuracy)) or np.any((accuracy <= .5) | (accuracy >= 1)):
            raise ValueError("known_s must contain G finite accuracies in (.5,1)")
        kappa = kl(accuracy, 1 - accuracy)
    membership = np.empty(d, dtype=int)
    for g, mm in enumerate(groups):
        membership[list(mm)] = g
    fact_masks = np.repeat(np.arange(1, 2 ** d), 2 ** G)
    type_masks = np.tile(np.arange(2 ** G), 2 ** d - 1)
    flips = (fact_masks[:, None] >> np.arange(d)[None, :]) & 1
    type_flips = (type_masks[:, None] >> np.arange(G)[None, :]) & 1
    task_group = np.repeat(membership, 2)
    physical_mode = np.tile(np.arange(2), d)
    true_high = physical_mode == z[task_group]
    means = np.where(true_high, p, q)
    required = np.where(np.repeat(flips, 2, axis=1), 1 - means, means)
    high = physical_mode[None, :] == (z[task_group][None, :] ^ type_flips[:, task_group])
    return _Geometry(int(d), groups, eta, p, q, totals[0] / R, legal, means,
                     required, high, type_flips * kappa[None, :], fact_masks, type_masks)


def _allocation(geometry, allocation, normalized=False):
    x = np.asarray(allocation, dtype=float)
    if x.shape != (geometry.A,) or np.any(~np.isfinite(x)) or np.any(x < 0):
        raise ValueError("allocation must contain 2d+G finite nonnegative entries")
    if np.any(x[~geometry.legal] != 0):
        raise ValueError("illegal actions must receive exactly zero mass")
    if normalized and not math.isclose(float(x.sum()), 1., rel_tol=0., abs_tol=1e-8):
        raise ValueError("radial direction must sum to one")
    return x


def min_information(state, allocation):
    """Exact analytic separation at arbitrary online allocations, with fixed M/R.

    'Exact' describes the continuous ordered optimization, not floating-point
    certification. This function uses point estimates, not posterior integration.
    """
    geometry = _geometry(state)
    x = _allocation(geometry, allocation)
    values, u, v, coefficients, offsets = geometry.fit(x)
    i = int(np.argmin(values))
    return {
        "value": float(values[i]), "minimum_information": float(values[i]),
        "u": float(u[i]), "v": float(v[i]),
        "fact_mask": int(geometry.fact_masks[i]), "type_mask": int(geometry.type_masks[i]),
        "gradient": coefficients[i].tolist(), "offset": float(offsets[i]),
        "alpha": geometry.alpha, "alternative_count": len(values),
    }


def _radial(geometry, weights, rtol):
    if geometry.unreachable(weights):
        return math.inf
    def residual(t):
        return float(np.min(geometry.fit(weights * t)[0])) - 1.
    upper = 1.
    while residual(upper) < 0:
        if upper >= np.finfo(float).max / 4:
            raise FloatingPointError("finite radial root exceeds float64 range")
        upper *= 2
    return float(brentq(residual, 0., upper, xtol=1e-11, rtol=rtol, maxiter=200))


def radial_cost(state, weights, *, rtol=1e-10):
    """Return inf{t: min_alt I(t*w; alpha)>=1}, or infinity if unreachable.

    For alpha>0 this is generally NOT 1/min_information(state,w). Allocation
    weights are distributions over the physical, interleaved task/type actions.
    """
    if not math.isfinite(rtol) or rtol < 4 * np.finfo(float).eps:
        raise ValueError("radial root tolerance is below float64 resolution")
    geometry = _geometry(state)
    weights = _allocation(geometry, weights, normalized=True)
    return _radial(geometry, weights, rtol)


def build_cuts(state, teacher_weights, teacher_K):
    """Build <=6*(2**d-1)*2**G observable finite alternative constraints.

    C_i x + b_i >= 1, where b_i=alpha*calibration_KL. Four base rate pairs
    are augmented with exact adversaries at teacher and legal-uniform radial
    allocations. This finite relaxation gives a radial-cost lower bound only.
    Returned lists are JSON-compatible; no private parameters are inspected.
    """
    geometry = _geometry(state)
    teacher = _allocation(geometry, teacher_weights, normalized=True)
    teacher_K = float(teacher_K)
    if not math.isfinite(teacher_K) or teacher_K <= 0:
        raise ValueError("teacher coefficient must be finite and positive")
    uniform = geometry.legal.astype(float) / geometry.legal.sum()
    uniform_K = _radial(geometry, uniform, 1e-9)
    reference_pairs = [(geometry.p, geometry.q), (.5, .5),
                       (geometry.p, geometry.p), (1 - geometry.eta, .5)]
    blocks = []
    N = len(geometry.fact_masks)
    for u, v in reference_pairs:
        blocks.append((np.full(N, u), np.full(N, v), "base"))
    for weights, K, label in ((teacher, teacher_K, "teacher"),
                              (uniform, uniform_K if math.isfinite(uniform_K) else teacher_K, "uniform")):
        _, u, v, _, _ = geometry.fit(weights * K)
        blocks.append((u, v, label))
    rows, offsets, descriptions, seen = [], [], [], set()
    for us, vs, label in blocks:
        coefficients = geometry.coefficients(us, vs)
        bb = geometry.alpha * (np.maximum(0., kl(geometry.p, us)) + np.maximum(0., kl(geometry.q, vs)))
        for i, (u, v) in enumerate(zip(us, vs)):
            key = (int(geometry.fact_masks[i]), int(geometry.type_masks[i]), float(u), float(v))
            if key in seen:
                continue
            seen.add(key)
            rows.append(coefficients[i].tolist())
            offsets.append(float(bb[i]))
            descriptions.append({"fact_mask": key[0], "type_mask": key[1], "u": key[2], "v": key[3], "source": label})
    return {
        "cut_coefficients": rows, "cut_offsets": offsets,
        "action_mask": geometry.legal.tolist(),
        "legal_actions": np.flatnonzero(geometry.legal).tolist(),
        "alternatives": descriptions, "alpha": geometry.alpha,
        "teacher_K": teacher_K, "uniform_K": uniform_K if math.isfinite(uniform_K) else None,
        "scope": "finite-cut radial lower-bound surrogate; continuous KL; not an exact objective or certificate",
    }


def finite_cut_radial_cost(cuts, weights):
    """Evaluate the finite-cut lower bound, preserving genuine infinity."""
    C = np.asarray(cuts["cut_coefficients"], dtype=float)
    b = np.asarray(cuts["cut_offsets"], dtype=float)
    w = np.asarray(weights, dtype=float)
    if C.ndim != 2 or b.shape != (len(C),) or w.shape != (C.shape[1],):
        raise ValueError("invalid finite-cut shapes")
    if np.any(~np.isfinite(C)) or np.any(C < 0) or np.any(~np.isfinite(b)) or np.any(b < 0):
        raise ValueError("invalid finite-cut KL coefficients")
    if np.any(~np.isfinite(w)) or np.any(w < 0) or not math.isclose(float(w.sum()), 1., abs_tol=1e-8):
        raise ValueError("finite-cut direction must be a probability vector")
    if "action_mask" in cuts and np.any(w[~np.asarray(cuts["action_mask"], dtype=bool)] != 0):
        raise ValueError("illegal action mass")
    need, denominator = np.maximum(0., 1 - b), C @ w
    ratio = np.zeros_like(need)
    ratio[(need > 0) & (denominator == 0)] = math.inf
    np.divide(need, denominator, out=ratio, where=denominator > 0)
    return float(np.max(ratio, initial=0.))


class WarmSolver:
    """Fresh coefficient LPs reusing only valid adversarial (u,v) locations.

    No p/q rounding, coefficient cache, solved-allocation reuse, or rate grid is
    used. Every new call recomputes all KL rows and continuous separation at its
    exact inputs. The bounded cache contains locations for the last structure.
    As in the frozen solver, G<=2 and its symmetric within-group reduction are
    required. General asymmetric weights are handled by radial_cost instead.
    """
    def __init__(self, max_cached_cuts=256):
        if not isinstance(max_cached_cuts, int) or max_cached_cuts < 0:
            raise ValueError("max_cached_cuts must be a nonnegative integer")
        self.max_cached_cuts = max_cached_cuts
        self._locations = []
        self._partition = None
        self.calls = 0

    def solve(self, partition, p, q, alpha, type_accuracy=None, eta=.05,
              tolerance=2e-7, max_iterations=200):
        partition = tuple(partition)
        G = len(partition)
        if not 1 <= G <= 2 or any(not isinstance(k, (int, np.integer)) or isinstance(k, bool) or k < 1 for k in partition):
            raise ValueError("one or two positive integer group sizes required")
        if not 0 < eta < .5 or not .5 <= q < p <= 1 - eta or not math.isfinite(alpha) or alpha < 0:
            raise ValueError("invalid ordered allocation inputs")
        if not math.isfinite(tolerance) or tolerance <= 0 or not isinstance(max_iterations, int) or max_iterations < 1:
            raise ValueError("invalid solver controls")
        if type_accuracy is None:
            s, kappa = None, None
        else:
            s = np.asarray([type_accuracy] * G if np.isscalar(type_accuracy) else type_accuracy, dtype=float)
            if s.shape != (G,) or np.any(~np.isfinite(s)) or np.any((s <= .5) | (s >= 1)):
                raise ValueError("finite known type accuracies required")
            kappa = kl(s, 1 - s)
        objective = np.asarray(list(partition) * 2 + ([1] * G if kappa is not None else []), dtype=float)
        rows, rhs, locations, seen = [], [], [], set()
        alts = group_alternatives(G)
        def add(mask, h, u, v):
            key = (int(mask), int(h), float(u), float(v))
            if key in seen:
                return False
            seen.add(key)
            locations.append(key)
            rows.append(coefficients_at(partition, p, q, mask, h, u, v, kappa))
            rhs.append(1 - alpha * (kl(p, u) + kl(q, v)))
            return True
        for mask, h in alts:
            for u, v in ((p, q), (.5, .5), (p, p), (1 - eta, .5)):
                add(mask, h, u, v)
        warm_cuts = 0
        if self._partition == partition:
            for mask, h, u, v in self._locations:
                if .5 <= v <= u <= 1 - eta:
                    warm_cuts += int(add(mask, h, u, v))
        initial_cuts = len(rows)
        history = []
        for iteration in range(max_iterations):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Unrecognized options detected")
                lp = linprog(objective, A_ub=-np.asarray(rows), b_ub=-np.asarray(rhs), bounds=(0, None), method="highs",
                             options={"threads": 1, "primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9})
            if not lp.success:
                raise RuntimeError("Warm allocation LP failed: " + lp.message)
            x, lower = np.maximum(lp.x, 0.), float(lp.fun)
            fits = [inner(partition, p, q, alpha, x, mask, h, kappa, eta) for mask, h in alts]
            worst = min(fit["value"] for fit in fits)
            history.append({"iteration": iteration + 1, "lower_bound": lower,
                            "minimum_information": worst, "cuts": len(rows)})
            if worst >= 1 - tolerance:
                break
            added = sum(add(mask, h, fit["u"], fit["v"]) for (mask, h), fit in zip(alts, fits)
                        if fit["value"] < 1 - tolerance)
            if added == 0:
                raise RuntimeError("Warm cutting plane stalled before feasibility")
        else:
            raise RuntimeError("Warm allocation solver iteration cap")
        def minimum(scale):
            return min(inner(partition, p, q, alpha, x * scale, m, h, kappa, eta)["value"] for m, h in alts)
        high = 1.
        while minimum(high) < 1 + 1e-9:
            high *= 1.001
            if not math.isfinite(high):
                raise FloatingPointError("warm radial feasibility repair overflow")
        low = 1.
        for _ in range(35):
            mid = (low + high) / 2
            if minimum(mid) >= 1 + 1e-9:
                high = mid
            else:
                low = mid
        feasible = x * high
        upper = float(objective @ feasible)
        final = [inner(partition, p, q, alpha, feasible, m, h, kappa, eta)["value"] for m, h in alts]
        gap = (upper - lower) / max(1., upper)
        # These are the same numerical acceptance limits used by the frozen
        # aligned planner, with the caller's requested separation tolerance.
        gap_limit = max(5 * tolerance, 5e-8)
        if not math.isfinite(gap) or not -5e-8 <= gap <= gap_limit or min(final) < 1 - 1e-7:
            raise RuntimeError("warm solve failed numerical gap/feasibility acceptance")
        self._partition = partition
        self._locations = locations[-self.max_cached_cuts:] if self.max_cached_cuts else []
        self.calls += 1
        return {
            "partition": list(partition), "p": p, "q": q, "alpha": alpha,
            "type_accuracy": None if s is None else s.tolist(),
            "K": upper, "lower_bound": lower, "upper_bound": upper,
            "relative_gap": gap, "a": feasible[:G].tolist(), "b": feasible[G:2 * G].tolist(),
            "c": feasible[2 * G:].tolist() if kappa is not None else [0.] * G,
            "minimum_information": min(final), "constraints": final,
            "iterations": len(history), "cuts": len(rows), "history": history,
            "scope": "Exact semi-infinite formulation; floating analytic separation and LP bounds, not interval certification.",
            "warm_diagnostics": {"warm_cuts": warm_cuts, "initial_cuts": initial_cuts,
                                 "cached_locations": len(self._locations), "solve_calls": self.calls,
                                 "reused_rate_or_coefficient_results": False,
                                 "exact_fresh_inputs": True, "rounded_keys": False,
                                 "accepted_gap_limit": gap_limit},
        }
