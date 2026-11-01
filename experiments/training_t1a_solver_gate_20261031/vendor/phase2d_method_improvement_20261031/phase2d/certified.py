"""Bounded, conservative joint-GLR stopping under the stated Decimal contract.

No hidden truth/types/rates are inputs. All sign/type states are enumerated;
continuous likelihood maxima are fitted with exact rational arithmetic. See
CERTIFIED_STOPPING_SPEC.md for the arithmetic argument and its trust boundary.
Import this stdlib-only module before applying filesystem confinement. Calls
perform no file/network access, imports, sampling, or model operations.
"""

from __future__ import annotations

from decimal import (
    Clamped, Context, Decimal, DecimalException, DivisionByZero, FloatOperation,
    InvalidOperation, Overflow, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN,
    Subnormal, Underflow,
)
from fractions import Fraction
from itertools import product
from operator import index
from time import perf_counter


MAX_DIMENSION = 4
MAX_TOTAL_OBSERVATIONS = 2**50
MAX_CONSTANT_BITS = 4096
MAX_PRECISION = 512
HALF = Fraction(1, 2)
ONE = Fraction(1)
ZERO_DECIMAL = Decimal(0)


def _sequence(value, name):
    if isinstance(value, (str, bytes, dict)):
        raise ValueError(f"{name} must be a finite sequence")
    try:
        return list(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite sequence") from exc


def _integer(value, name):
    # Never silently round count data or accept an integral-looking float.
    if isinstance(value, bool):
        raise ValueError(f"{name} must contain integers, not booleans")
    try:
        return int(index(value))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain integers") from exc


def _bits(value, name):
    result = tuple(_integer(v, name) for v in _sequence(value, name))
    if any(v not in (0, 1) for v in result):
        raise ValueError(f"{name} must contain only integer 0/1 values")
    return result


def _rational(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite numeric constant")
    try:
        if isinstance(value, float):
            result = Fraction.from_float(value)
        elif isinstance(value, Decimal):
            # Bound conversion cost before constructing a possibly huge integer.
            if not value.is_finite() or abs(value.adjusted()) > 1233:
                raise ValueError(f"{name} is outside the bounded constant scope")
            if len(value.as_tuple().digits) > 1234:
                raise ValueError(f"{name} is outside the bounded constant scope")
            result = Fraction(value)
        elif isinstance(value, Fraction):
            result = value
        else:
            result = Fraction(_integer(value, name))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite int, float, Decimal, or Fraction") from exc
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_CONSTANT_BITS:
        raise ValueError(f"{name} exceeds {MAX_CONSTANT_BITS}-bit constant scope")
    return result


def _memberships(groups, d):
    raw = _sequence(groups, "groups")
    if not raw:
        raise ValueError("groups must be a nonempty partition or membership vector")
    try:
        labels = [_integer(v, "groups") for v in raw]
    except ValueError:
        labels = None
    if labels is not None:
        if len(labels) != d or set(labels) != set(range(len(set(labels)))):
            raise ValueError("membership vector must have length d and contiguous zero-based labels")
        return tuple(labels), len(set(labels))
    membership = [-1] * d
    for g, value in enumerate(raw):
        members = _sequence(value, "group members")
        if not members:
            raise ValueError("groups cannot be empty")
        for value in members:
            j = _integer(value, "group members")
            if not 0 <= j < d or membership[j] != -1:
                raise ValueError("groups must contain each target exactly once")
            membership[j] = g
    if -1 in membership:
        raise ValueError("groups must contain each target exactly once")
    return tuple(membership), len(raw)


def _ordered_mle(high_s, high_n, low_s, low_n, eta):
    """Exact maximizer on 1/2 <= q <= p <= 1-eta, including zero weights."""
    upper = ONE - eta
    clip = lambda value: max(HALF, min(upper, value))
    p = clip(Fraction(high_s, high_n)) if high_n else HALF
    q = clip(Fraction(low_s, low_n)) if low_n else HALF
    if high_n and low_n and p < q:
        p = q = clip(Fraction(high_s + low_s, high_n + low_n))
    if not high_n:
        p = q
    return p, q


class _Intervals:
    """All endpoint arithmetic uses explicit contexts, never ambient context."""

    def __init__(self, precision):
        options = dict(
            prec=precision, Emin=-999999, Emax=999999, capitals=1, clamp=0,
            flags=[], traps=[InvalidOperation, DivisionByZero, Overflow,
                             Underflow, Subnormal, Clamped, FloatOperation],
        )
        self.down = Context(rounding=ROUND_FLOOR, **options)
        self.up = Context(rounding=ROUND_CEILING, **options)
        self.nearest = Context(rounding=ROUND_HALF_EVEN, **options)
        self.logs = {}
        self.counts = {"rational_divisions": 0, "ln_evaluations": 0,
                       "directed_multiplications": 0, "directed_additions": 0,
                       "directed_subtractions": 0}

    def rational(self, value):
        numerator, denominator = Decimal(value.numerator), Decimal(value.denominator)
        self.counts["rational_divisions"] += 2
        return (self.down.divide(numerator, denominator),
                self.up.divide(numerator, denominator))

    def log(self, value):
        if value <= 0:
            raise ValueError("logarithm arguments must be positive")
        if value == ONE:
            return ZERO_DECIMAL, ZERO_DECIMAL
        if value not in self.logs:
            lo, hi = self.rational(value)
            # ln is correctly rounded HALF_EVEN, independently of context
            # rounding. Monotonicity plus a full neighbor step encloses it.
            lower = self.down.next_minus(self.nearest.ln(lo))
            upper = self.up.next_plus(self.nearest.ln(hi))
            self.counts["ln_evaluations"] += 2
            if not lower.is_finite() or not upper.is_finite() or lower > upper:
                raise ArithmeticError("nonfinite or reversed logarithm enclosure")
            self.logs[value] = lower, upper
        return self.logs[value]

    def add(self, left, right):
        self.counts["directed_additions"] += 2
        return self.down.add(left[0], right[0]), self.up.add(left[1], right[1])

    def subtract(self, left, right):
        self.counts["directed_subtractions"] += 2
        return self.down.subtract(left[0], right[1]), self.up.subtract(left[1], right[0])

    def weighted_logs(self, terms):
        result = ZERO_DECIMAL, ZERO_DECIMAL
        for weight, argument in terms:
            if not weight:
                continue
            lo, hi = self.log(argument)
            factor = Decimal(weight)  # exact conversion, even at low precision
            weighted = self.down.multiply(lo, factor), self.up.multiply(hi, factor)
            self.counts["directed_multiplications"] += 2
            result = self.add(result, weighted)
        return result


def _validate(counts, groups, calibration, type_answers, type_accuracy, R,
              eta, candidate_theta, precisions):
    rows = _sequence(counts, "counts")
    if not 1 <= len(rows) <= MAX_DIMENSION:
        raise ValueError(f"counts dimension must be in [1,{MAX_DIMENSION}]")
    data = []
    for row in rows:
        formats = _sequence(row, "counts")
        if len(formats) != 2:
            raise ValueError("counts must have shape (d,2,2)")
        parsed = []
        for stream in formats:
            pair = _sequence(stream, "counts")
            if len(pair) != 2:
                raise ValueError("counts must have shape (d,2,2)")
            pair = tuple(_integer(v, "counts") for v in pair)
            if any(v < 0 for v in pair):
                raise ValueError("counts must be nonnegative")
            parsed.append(pair)
        data.append(tuple(parsed))
    membership, group_count = _memberships(groups, len(data))
    if calibration is None:
        calibration = {"high": [], "low": []}
    if not isinstance(calibration, dict) or set(calibration) != {"high", "low"}:
        raise ValueError("calibration must contain exactly high and low streams")
    high, low = (_bits(calibration[k], f"calibration.{k}") for k in ("high", "low"))
    if len(high) != len(low):
        raise ValueError("the boundary requires equally long labelled reference streams")
    if type_answers is None:
        type_answers = [[] for _ in range(group_count)]
    reports = tuple(_bits(v, "type_answers") for v in _sequence(type_answers, "type_answers"))
    if len(reports) != group_count:
        raise ValueError("type_answers must have one sequence per group")
    if type_accuracy is None:
        if any(reports):
            raise ValueError("known type_accuracy is required when reports are present")
        accuracies = (Fraction(3, 4),) * group_count
    else:
        accuracies = tuple(_rational(v, "type_accuracy")
                           for v in _sequence(type_accuracy, "type_accuracy"))
        if len(accuracies) != group_count or any(not HALF < v < ONE for v in accuracies):
            raise ValueError("type_accuracy must contain G known values in (1/2,1)")
    risk, margin = _rational(R, "R"), _rational(eta, "eta")
    if risk <= 0 or not 0 < margin < HALF:
        raise ValueError("R must be positive and eta must be in (0,1/2)")
    task_counts = tuple(tuple(sum(pair) for pair in row) for row in data)
    total = sum(sum(row) for row in task_counts) + len(high) + len(low) + sum(map(len, reports))
    if total > MAX_TOTAL_OBSERVATIONS:
        raise ValueError("total observations exceed the bounded prototype scope")
    candidate = None if candidate_theta is None else _bits(candidate_theta, "candidate_theta")
    if candidate is not None and len(candidate) != len(data):
        raise ValueError("candidate_theta must have length d")
    precision_list = tuple(_integer(p, "precisions") for p in _sequence(precisions, "precisions"))
    if (not 1 <= len(precision_list) <= 6
            or any(not 16 <= p <= MAX_PRECISION for p in precision_list)
            or any(a >= b for a, b in zip(precision_list, precision_list[1:]))):
        raise ValueError("precisions must contain 1..6 strictly increasing integers in [16,512]")
    return (tuple(data), membership, high, low, reports, accuracies, risk,
            margin, candidate, precision_list, task_counts, total)


def _states(data, membership, high, low, reports, accuracies, eta):
    """Finite states, each carrying an exact continuous maximizer and log terms."""
    states = []
    m, high_cal_s, low_cal_s = len(high), sum(high), sum(low)
    for theta in product((0, 1), repeat=len(data)):
        rows = []
        for z in product((0, 1), repeat=len(reports)):
            hs, hn, ls, ln = high_cal_s, m, low_cal_s, m
            for j, row in enumerate(data):
                for fmt, pair in enumerate(row):
                    if fmt == z[membership[j]]:
                        hs, hn = hs + pair[theta[j]], hn + sum(pair)
                    else:
                        ls, ln = ls + pair[theta[j]], ln + sum(pair)
            p, q = _ordered_mle(hs, hn, ls, ln, eta)
            terms = [(hs, p), (hn - hs, ONE - p),
                     (ls, q), (ln - ls, ONE - q)]
            for g, answers in enumerate(reports):
                matches = sum(a == z[g] for a in answers)
                terms.extend(((matches, accuracies[g]),
                              (len(answers) - matches, ONE - accuracies[g])))
            rows.append({"z": z, "p": p, "q": q, "terms": tuple(terms)})
        states.append((theta, rows))
    return states


def certify_stop(counts, groups, calibration=None, type_answers=None,
                 type_accuracy=None, R=None, eta=.05, candidate_theta=None,
                 precisions=(50, 80, 120), *, include_profiles=False):
    """Enclose the exact joint GLR and stop only when gap_lower > beta_upper.

    Counts have shape (d,2,2), 1<=d<=4. Groups are a partition or a contiguous
    membership vector. R is log(1/delta), without exp(-R). Float parameters mean
    their exact stored binary values. A supplied candidate fixes only the sign
    vector being tested; ALL group types and ALL wrong signs are still searched.
    If omitted, the largest profile lower bound selects a candidate, ties using
    lexicographic order. Rejected/undetermined both require continue or abstain.
    Invalid inputs raise ValueError. Arithmetic failure returns undetermined.

    Endpoint values are strings, never floats. A certificate is conditional on
    the documented likelihood model, analytic maximization, Python Fraction
    exactness and correctly rounded Decimal implementation, not a formal proof.
    """
    started = perf_counter()
    (data, membership, high, low, reports, accuracies, risk, margin, candidate,
     precision_list, task_counts, total) = _validate(
        counts, groups, calibration, type_answers, type_accuracy, R, eta,
        candidate_theta, precisions)
    states = _states(data, membership, high, low, reports, accuracies, margin)
    validated_at = perf_counter()
    beta_terms = [(2, Fraction(len(high) + 1))]
    beta_terms.extend((1, Fraction(n + 1)) for row in task_counts for n in row)
    beta_terms.extend((1, Fraction(len(a) + 1)) for a in reports)
    attempts = []
    operation_counts = {}
    final = None
    status = "undetermined"
    reason = "precision_limit_overlap"
    for precision in precision_list:
        interval = _Intervals(precision)
        try:
            profiles = []
            for theta, rows in states:
                bounds = [interval.weighted_logs(row["terms"]) for row in rows]
                witness = max(range(len(rows)), key=lambda i: bounds[i][0])
                profiles.append({"theta": theta,
                                 "bounds": (bounds[witness][0], max(b[1] for b in bounds)),
                                 "witness": rows[witness]})
            if candidate is None:
                chosen = max(range(len(profiles)), key=lambda i: profiles[i]["bounds"][0])
            else:
                chosen = next(i for i, value in enumerate(profiles) if value["theta"] == candidate)
            selected = profiles[chosen]
            others = [value["bounds"] for i, value in enumerate(profiles) if i != chosen]
            wrong = max(v[0] for v in others), max(v[1] for v in others)
            gap = interval.subtract(selected["bounds"], wrong)
            beta = interval.add(interval.rational(risk), interval.weighted_logs(beta_terms))
            if any(not value.is_finite() for pair in (selected["bounds"], wrong, gap, beta) for value in pair):
                raise ArithmeticError("nonfinite endpoint")
            if any(pair[0] > pair[1] for pair in (selected["bounds"], wrong, gap, beta)):
                raise ArithmeticError("reversed endpoint")
            final = (selected, wrong, gap, beta, profiles, precision)
            if gap[0] > beta[1]:
                status, reason = "certified", "gap_lower_strictly_above_beta_upper"
            elif gap[1] <= beta[0]:
                status, reason = "rejected", "gap_upper_at_or_below_beta_lower"
            attempts.append({"precision": precision, "status": status,
                             "gap_lower": str(gap[0]), "gap_upper": str(gap[1]),
                             "beta_lower": str(beta[0]), "beta_upper": str(beta[1])})
        except (DecimalException, ArithmeticError, ValueError):
            # Never reinterpret a numerical failure as a threshold crossing.
            status, reason = "undetermined", "arithmetic_failure"
            final = None
            attempts.append({"precision": precision, "status": status, "reason": reason})
        for key, value in interval.counts.items():
            operation_counts[key] = operation_counts.get(key, 0) + value
        if status != "undetermined" or reason == "arithmetic_failure":
            break
    result = {
        "status": status, "reason": reason,
        "certified": status == "certified", "interval_certified": status == "certified",
        "decision": "stop" if status == "certified" else "continue_or_abstain",
        "theta": None, "candidate_theta": None,
        "candidate_loglik_lower": None, "candidate_loglik_upper": None,
        "wrong_loglik_lower": None, "wrong_loglik_upper": None,
        "gap_lower": None, "gap_upper": None, "beta_lower": None, "beta_upper": None,
        "precision": attempts[-1]["precision"], "precision_attempts": attempts,
        "dimension": len(data), "groups": len(reports),
        "sign_candidates": len(states), "type_candidates": 2**len(reports),
        "joint_candidates": len(states) * 2**len(reports),
        "total_observations": total, "task_counts": [list(v) for v in task_counts],
        "reference_count_per_stream": len(high), "type_counts": list(map(len, reports)),
        "operation_counts": {"exact_joint_mle_fits": len(states) * 2**len(reports), **operation_counts},
        "exact_input_parameters": {"R": str(risk), "eta": str(margin),
                                   "upper_rate": str(ONE - margin),
                                   "type_accuracy": [str(v) for v in accuracies]},
        "numerical_scope": {
            "arithmetic": "exact_Fraction_MLE_and_outward_Decimal_log_intervals",
            "candidate_domain": "1/2 <= q <= p <= 1-exact_input_eta (closure)",
            "discrete_search": "all_theta_and_all_z",
            "max_dimension": MAX_DIMENSION,
            "max_total_observations": MAX_TOTAL_OBSERVATIONS,
            "trust": "analytic_model_reduction_and_Python_Fraction_Decimal_contracts",
            "formal_proof_assistant_verified": False,
        },
    }
    if final is not None:
        selected, wrong, gap, beta, profiles, _ = final
        result["theta"] = result["candidate_theta"] = list(selected["theta"])
        for prefix, pair in (("candidate_loglik", selected["bounds"]),
                             ("wrong_loglik", wrong), ("gap", gap), ("beta", beta)):
            result[prefix + "_lower"], result[prefix + "_upper"] = map(str, pair)
        witness = selected["witness"]
        result["lower_witness"] = {"z": list(witness["z"]),
                                   "p": str(witness["p"]), "q": str(witness["q"])}
        if include_profiles:
            result["profiles"] = [
                {"theta": list(value["theta"]),
                 "loglik_lower": str(value["bounds"][0]),
                 "loglik_upper": str(value["bounds"][1]),
                 "lower_witness": {"z": list(value["witness"]["z"]),
                                   "p": str(value["witness"]["p"]),
                                   "q": str(value["witness"]["q"])}}
                for value in profiles
            ]
    ended = perf_counter()
    result["timings_seconds"] = {"validation_and_exact_fits": validated_at - started,
                                 "interval_enclosure": ended - validated_at,
                                 "total": ended - started}
    return result
