"""Joint GLR with exhaustive signs/types and continuous binomial profiling.

Conventions match the benchmark: ``counts[j, m, y]`` counts answers ``y`` in
{0, 1} to target j / format m in {0, 1}; theta and group types are also 0/1.
The likelihood is that of the observed ordered observations, with no binomial
coefficient. Those coefficients would be state independent and cancel anyway.

"Exact" describes enumeration and the analytic maximization problem, not
floating point arithmetic. No interval-arithmetic error certificate is claimed.
"certified" below means the theoretical boundary was crossed by this float64
implementation, subject to its explicitly reported numerical scope.
"""

from __future__ import annotations

from functools import lru_cache
from math import fsum, log
from time import perf_counter
from typing import Sequence

import numpy as np


MAX_DIMENSION = 8
MAX_ENDPOINT_DIMENSION = 16
MAX_ENDPOINT_GROUPS = 2
MAX_TOTAL_OBSERVATIONS = 2**50


@lru_cache(maxsize=MAX_ENDPOINT_DIMENSION + 1)
def _binary_vectors(length: int) -> np.ndarray:
    """Immutable lexicographic binary candidates, reusable across endpoints."""
    values = np.arange(2**length, dtype=np.uint32)[:, None]
    shifts = np.arange(length - 1, -1, -1, dtype=np.uint32)[None, :]
    candidates = ((values >> shifts) & 1).astype(np.int8)
    candidates.flags.writeable = False
    return candidates


def _bits(values, name: str) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim != 1 or np.any((arr != 0) & (arr != 1)):
        raise ValueError(f"{name} must be a one-dimensional sequence of 0/1 values")
    return arr.astype(np.int8)


def _memberships(groups, d: int) -> tuple[np.ndarray, int]:
    """Accept a partition, or a length-d vector of contiguous group indices."""
    raw = list(groups)
    if not raw:
        raise ValueError("groups must be a nonempty partition")
    if all(np.isscalar(g) for g in raw):
        if len(raw) != d or any(int(g) != g for g in raw):
            raise ValueError("membership indices must be integral and have length d")
        membership = np.asarray(raw, dtype=np.int64)
        labels = np.unique(membership)
        if not np.array_equal(labels, np.arange(len(labels))):
            raise ValueError("membership indices must be contiguous starting at zero")
        return membership, len(labels)
    membership = np.full(d, -1, dtype=np.int64)
    for g, members in enumerate(raw):
        members = list(members)
        if not members:
            raise ValueError("every group must contain at least one target")
        for j in members:
            if not np.isscalar(j) or int(j) != j or not 0 <= j < d:
                raise ValueError("group coordinates must be integral indices in [0,d)")
            j = int(j)
            if membership[j] != -1:
                raise ValueError("groups must contain every target exactly once")
            membership[j] = g
    if np.any(membership == -1):
        raise ValueError("groups must contain every target exactly once")
    return membership, len(raw)


def _binomial_mle(high_s, high_n, low_s, low_n, eta: float):
    """Weighted binomial isotonic MLE, including all zero-weight cases.

    If the two separately clipped empirical means violate p>=q, the two
    positive-weight blocks are pooled. An unobserved low parameter is set to
    1/2; an unobserved high parameter is set equal to the fitted low parameter.
    These are deterministic representatives of possibly nonunique MLEs.
    """
    high_s, high_n, low_s, low_n = np.broadcast_arrays(
        high_s, high_n, low_s, low_n
    )
    p = np.divide(high_s, high_n, out=np.full(high_s.shape, .5), where=high_n > 0)
    q = np.divide(low_s, low_n, out=np.full(low_s.shape, .5), where=low_n > 0)
    p = np.clip(p, .5, 1 - eta)
    q = np.clip(q, .5, 1 - eta)
    pool = (p < q) & (high_n > 0) & (low_n > 0)
    pooled = np.divide(
        high_s + low_s, high_n + low_n,
        out=np.full(high_s.shape, .5), where=high_n + low_n > 0,
    )
    pooled = np.clip(pooled, .5, 1 - eta)
    p = np.where(pool, pooled, p)
    q = np.where(pool, pooled, q)
    p = np.where(high_n == 0, q, p)
    value = (
        high_s * np.log(p) + (high_n - high_s) * np.log1p(-p)
        + low_s * np.log(q) + (low_n - low_s) * np.log1p(-q)
    )
    return p, q, value


def _profile_joint(
    counts,
    groups,
    calibration=None,
    type_answers=None,
    type_accuracy=None,
    delta: float = .05,
    eta: float = .05,
    oracle_types=None,
    *,
    _endpoint_only=False,
    _include_profiles=True,
) -> dict:
    """Profile the complete joint GLR of Theory_Note.md Sections 1, 3 and 4.

    Parameters
    ----------
    counts : nonnegative integer array, shape (d, 2, 2), 1 <= d <= 8
        Counts of raw 0/1 answers. No latent truth, levels, or types are used.
    groups : partition list of lists, or group-index vector of length d
        A partition uses zero-based target indices. A membership vector uses
        contiguous zero-based group labels.
    calibration : {'high': [0/1,...], 'low': [0/1,...]}, optional
        Labelled independent Bernoulli reference streams. Equal lengths M are
        required by the stated theorem and threshold. Defaults to both empty.
    type_answers : sequence of G sequences of 0/1 reports, optional
        Reports of group type, with their known, independent accuracies below.
    type_accuracy : sequence of G numbers in (1/2,1), optional
        Must be supplied when any type report is present. No accuracy is fit.
    oracle_types : length-G 0/1 sequence, optional
        Fixes only current types; levels and signs remain unknown and profiled.

    Returns a JSON-serializable dictionary. ``gap`` compares the best sign
    vector against the best *different sign vector*, each independently
    profiled over all allowed types and continuous levels. Ties use the first
    lexicographic candidate. A finite-precision threshold crossing is reported
    as ``certified``; ``interval_certified`` is always False. Exhaustive state
    enumeration is never silently replaced by a dimension-dependent heuristic.
    """
    started = perf_counter()
    if not np.isfinite(delta) or not 0 < delta < 1:
        raise ValueError("delta must be in (0,1)")
    if not np.isfinite(eta) or not 0 < eta < .5:
        raise ValueError("eta must be in (0,1/2)")
    data = np.asarray(counts)
    if data.ndim != 3 or data.shape[1:] != (2, 2):
        raise ValueError("counts must have shape (d,2,2)")
    d = data.shape[0]
    max_dimension = MAX_ENDPOINT_DIMENSION if _endpoint_only else MAX_DIMENSION
    if not 1 <= d <= max_dimension:
        raise ValueError(f"exact profile supports 1 <= d <= {max_dimension}; received d={d}")
    try:
        valid = np.all(np.isfinite(data)) and np.all(data >= 0) and np.all(data == np.floor(data))
    except TypeError as exc:
        raise ValueError("counts must contain nonnegative finite integers") from exc
    if not valid:
        raise ValueError("counts must contain nonnegative finite integers")
    total = sum(int(x) for x in data.flat)
    if total > MAX_TOTAL_OBSERVATIONS:
        raise ValueError("total observations exceed the stated float64 numerical scope")
    data = data.astype(np.float64)
    membership, group_count = _memberships(groups, d)
    if _endpoint_only and group_count > MAX_ENDPOINT_GROUPS:
        raise ValueError(f"endpoint_mle supports at most {MAX_ENDPOINT_GROUPS} groups")
    if calibration is None:
        calibration = {"high": [], "low": []}
    if set(calibration) != {"high", "low"}:
        raise ValueError("calibration must contain exactly high and low labelled streams")
    high = _bits(calibration["high"], "calibration.high")
    low = _bits(calibration["low"], "calibration.low")
    if len(high) != len(low):
        raise ValueError("the theorem requires equally long labelled reference streams")
    m = len(high)
    if type_answers is None:
        type_answers = [[] for _ in range(group_count)]
    if len(type_answers) != group_count:
        raise ValueError("type_answers must contain one report sequence per group")
    reports = [_bits(a, f"type_answers[{g}]") for g, a in enumerate(type_answers)]
    if type_accuracy is None:
        if any(len(a) for a in reports):
            raise ValueError("type reports require known per-group type_accuracy")
        accuracy = np.full(group_count, .75)  # immaterial for empty streams
    else:
        accuracy = np.asarray(type_accuracy, dtype=np.float64)
        if (accuracy.shape != (group_count,) or not np.all(np.isfinite(accuracy))
                or np.any(accuracy <= .5) or np.any(accuracy >= 1)):
            raise ValueError("type_accuracy must give G known values in (1/2,1)")
    total += 2 * m + sum(len(a) for a in reports)
    if total > MAX_TOTAL_OBSERVATIONS:
        raise ValueError("total observations exceed the stated float64 numerical scope")
    theta = _binary_vectors(d)
    if oracle_types is None:
        z = _binary_vectors(group_count)
    else:
        fixed_z = _bits(oracle_types, "oracle_types")
        if len(fixed_z) != group_count:
            raise ValueError("oracle_types must have length G")
        z = fixed_z[None, :]
    validated_at = perf_counter()

    # Each column is one complete type vector, each row one sign vector.
    # Success means matching that candidate sign, not matching latent truth.
    candidate_success = np.where(theta[:, :, None] == 1, data[None, :, :, 1], data[None, :, :, 0])
    good_format = z[:, membership]
    good_mask = (good_format[:, :, None] == np.arange(2)).reshape(len(z), 2 * d).astype(np.float64)
    stream_n = data.sum(axis=2).reshape(2 * d)
    candidate_success = candidate_success.reshape(len(theta), 2 * d)
    high_s = candidate_success @ good_mask.T + float(high.sum())
    low_s = candidate_success.sum(axis=1)[:, None] - high_s + float(high.sum()) + float(low.sum())
    high_n = stream_n @ good_mask.T + m
    low_n = stream_n.sum() + 2 * m - high_n
    p, q, joint = _binomial_mle(high_s, high_n, low_s, low_n, eta)
    type_loglikelihood = np.zeros(len(z))
    for g, answers in enumerate(reports):
        matches = np.sum(answers[None, :] == z[:, g, None], axis=1)
        type_loglikelihood += matches * log(accuracy[g]) + (len(answers) - matches) * log(1 - accuracy[g])
    joint += type_loglikelihood[None, :]
    profiled_at = perf_counter()

    best_z_indices = np.argmax(joint, axis=1)
    profile = joint[np.arange(len(theta)), best_z_indices]
    best = int(np.argmax(profile))
    competitors = profile.copy()
    competitors[best] = -np.inf
    second = int(np.argmax(competitors))
    best_z, second_z = int(best_z_indices[best]), int(best_z_indices[second])
    gap = max(0.0, float(profile[best] - profile[second]))
    task_n = data.sum(axis=2).astype(np.int64)
    # Use the full streamwise mixture correction, including zero-count streams.
    beta = fsum([
        -log(delta), 2 * log(m + 1),
        *(log(int(n) + 1) for n in task_n.flat),
        *(log(len(a) + 1) for a in reports),
    ])
    ended = perf_counter()
    result = {
        "theta": theta[best].tolist(),
        "z": z[best_z].tolist(),
        "p_hat": float(p[best, best_z]),
        "q_hat": float(q[best, best_z]),
        "log_likelihood": float(profile[best]),
        "alternative_theta": theta[second].tolist(),
        "alternative_z": z[second_z].tolist(),
        "alternative_p_hat": float(p[second, second_z]),
        "alternative_q_hat": float(q[second, second_z]),
        "alternative_log_likelihood": float(profile[second]),
        "gap": gap,
        "beta": beta,
        "certified": bool(gap >= beta),
        "interval_certified": False,
        "numerical_scope": {
            "discrete_search": "exhaustive_all_signs_and_allowed_types",
            "continuous_profile": "analytic_weighted_binomial_isotonic_pooling_and_clipping",
            "arithmetic": "float64_not_interval_certified",
            "candidate_domain": "0.5 <= q <= p <= 1-eta (closure)",
            "max_dimension": max_dimension,
            "max_total_observations": MAX_TOTAL_OBSERVATIONS,
            "near_boundary_warning": "gap>=beta is evaluated in float64; rigorous rounding enclosure absent",
        },
        "oracle_types_fixed": oracle_types is not None,
        "dimension": d,
        "groups": group_count,
        "sign_candidates": len(theta),
        "type_candidates": len(z),
        "joint_candidates": len(theta) * len(z),
        "reference_count_per_stream": m,
        "task_counts": task_n.tolist(),
        "type_counts": [len(a) for a in reports],
        "timings_seconds": {
            "validation_and_candidates": validated_at - started,
            "aggregation_and_profile": profiled_at - validated_at,
            "selection_and_threshold": ended - profiled_at,
            "total": ended - started,
        },
    }
    if _include_profiles:
        result["profile_log_likelihoods"] = profile.tolist()
    if _endpoint_only:
        # This API is an endpoint decoder, with no stopping certificate or
        # error-rate inference attached. Keep its return values unambiguous.
        for key in ("gap", "beta", "certified", "interval_certified",
                    "alternative_theta", "alternative_z", "alternative_p_hat",
                    "alternative_q_hat", "alternative_log_likelihood"):
            del result[key]
        result["numerical_scope"]["near_boundary_warning"] = "no stopping decision is made"
        result["numerical_scope"]["max_groups"] = MAX_ENDPOINT_GROUPS
        result["numerical_scope"]["max_joint_candidates"] = 2 ** (MAX_ENDPOINT_DIMENSION + MAX_ENDPOINT_GROUPS)
        result["purpose"] = "common_fixed_budget_profile_mle_endpoint_decoder"
    return result


def profile_glr(
    counts, groups, calibration=None, type_answers=None, type_accuracy=None,
    delta: float = .05, eta: float = .05, oracle_types=None,
) -> dict:
    """Joint GLR for d<=8, profiling every sign and permitted group type.

    ``counts[j,m,y]`` and all signs, formats, types and type reports use 0/1.
    ``groups`` is a partition list of lists or a contiguous membership vector.
    ``calibration`` holds equally long labelled ``high`` / ``low`` bit streams.
    ``type_accuracy`` gives the known independent report accuracy per group.
    ``oracle_types`` fixes only types, while signs and levels remain profiled.
    The closure 0.5<=q<=p<=1-eta is maximized analytically. ``certified`` means
    a float64 threshold crossing; ``interval_certified`` is always False.
    See the module documentation and GLR_AUDIT.md for the numerical limits.
    """
    return _profile_joint(counts, groups, calibration, type_answers, type_accuracy,
                          delta, eta, oracle_types)


def endpoint_mle(
    counts, groups, calibration=None, type_answers=None, type_accuracy=None,
    eta: float = .05, oracle_types=None,
    *, include_profiles: bool = False,
) -> dict:
    """Common exact-profile fixed-budget decoder for d<=16 and G<=2.

    Enumerates at most 262,144 joint states, with the same continuous analytic
    fit and data conventions as profile_glr. Intended for one decode per
    prespecified budget endpoint; returns no gap, boundary, or certificate.
    Binary candidate arrays are cached and immutable. Full per-theta profiles
    are omitted unless include_profiles=True. This extension makes no d=16
    sequential GLR/stopping-runtime claim.
    """
    return _profile_joint(counts, groups, calibration, type_answers, type_accuracy,
                          .05, eta, oracle_types, _endpoint_only=True,
                          _include_profiles=include_profiles)
