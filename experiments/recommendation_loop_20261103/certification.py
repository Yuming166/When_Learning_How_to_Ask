"""Separately tested d<=6, G<=2 recommendation-level likelihood certificate.

Only arithmetic primitives are reused from the historical d<=4 sign gate. Its
validation, state construction and stopping function are NEVER used here.
"""

from __future__ import annotations

from decimal import DecimalException
from fractions import Fraction
import importlib.util
from pathlib import Path
from time import perf_counter

try:
    from .likelihood import (JointLikelihood, MAX_DIMENSION, MAX_GROUPS,
                             MAX_TOTAL_OBSERVATIONS, MAX_CONSTANT_BITS, _integer, _sequence)
except ImportError:
    from likelihood import (JointLikelihood, MAX_DIMENSION, MAX_GROUPS,
                            MAX_TOTAL_OBSERVATIONS, MAX_CONSTANT_BITS, _integer, _sequence)


_SOURCE = Path(__file__).resolve().parents[1] / "phase2d_method_improvement_20261031" / "phase2d" / "certified.py"
_SPEC = importlib.util.spec_from_file_location("_recommendation_decimal_primitives", _SOURCE)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("cannot load historical arithmetic primitives")
_ARITHMETIC = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_ARITHMETIC)
_Intervals = _ARITHMETIC._Intervals
_ordered_mle = _ARITHMETIC._ordered_mle


class CertifiedDecisionGate:
    """Exact continuous profile fits, outward log bounds, strict separation.

    L_i = max_{theta: winner(theta)=i,z,.5<=q<=p<=1-eta} log L.
    Certification requires lower(L_i - max_{k != i} L_k) > upper(beta),
    where beta = R + sum_{j,fmt} log(N[j,fmt]+1). R is a positive integer.
    Class profiles are MAXIMA (the GLR), not posterior sums over states.
    """

    def __init__(self, public, R=3, precisions=(50, 80, 120)):
        self.model = JointLikelihood(public)
        self.R = _integer(R, "R")
        if self.R <= 0:
            raise ValueError("R must be a positive exact integer")
        if self.R.bit_length() > MAX_CONSTANT_BITS:
            raise ValueError("R exceeds bounded constant scope")
        self.precisions = tuple(_integer(p, "precisions") for p in _sequence(precisions, "precisions"))
        if (not 1 <= len(self.precisions) <= 6
                or any(not 16 <= p <= 512 for p in self.precisions)
                or any(a >= b for a, b in zip(self.precisions, self.precisions[1:]))):
            raise ValueError("precisions must be 1..6 increasing integers in [16,512]")

    def check(self, counts, candidate_item=None):
        started = perf_counter()
        model = self.model
        data = model.validate_counts(counts)
        candidate = model.validate_candidate(candidate_item)
        statistics = model._sufficient_statistics(data)
        states = []
        for theta in range(2**model.d):
            for z in range(2**model.G):
                hs, hn, ls, ln = (int(array[theta, z]) for array in statistics)
                p, q = _ordered_mle(hs, hn, ls, ln, model.eta)
                states.append({"theta_mask": theta, "z_mask": z,
                               "item": int(model.winner_by_theta[theta]),
                               "p": p, "q": q,
                               "terms": ((hs, p), (hn - hs, 1-p),
                                         (ls, q), (ln - ls, 1-q))})
        action_counts = data.sum(axis=2)
        threshold_terms = [(1, Fraction(int(n) + 1)) for n in action_counts.flat]
        attempts, operations = [], {}
        status, reason, final = "UNDETERMINED", "precision_limit_overlap", None
        for precision in self.precisions:
            interval = _Intervals(precision)
            try:
                bounds = [interval.weighted_logs(state["terms"]) for state in states]
                if any(not endpoint.is_finite() for pair in bounds for endpoint in pair):
                    raise ArithmeticError("nonfinite state endpoint")
                if any(pair[0] > pair[1] for pair in bounds):
                    raise ArithmeticError("reversed state endpoint")
                classes = {}
                for item in model.items:
                    indexes = [i for i, state in enumerate(states) if state["item"] == item]
                    witness = max(indexes, key=lambda i: bounds[i][0])
                    classes[item] = {"bounds": (bounds[witness][0], max(bounds[i][1] for i in indexes)),
                                     "witness": states[witness]}
                chosen = candidate if candidate is not None else max(classes, key=lambda item: classes[item]["bounds"][0])
                selected = classes[chosen]
                others = [value["bounds"] for item, value in classes.items() if item != chosen]
                beta = interval.add(interval.rational(Fraction(self.R)), interval.weighted_logs(threshold_terms))
                if others:
                    wrong = max(pair[0] for pair in others), max(pair[1] for pair in others)
                    gap = interval.subtract(selected["bounds"], wrong)
                    pairs = [entry["bounds"] for entry in classes.values()] + [wrong, gap, beta]
                    if any(not endpoint.is_finite() for pair in pairs for endpoint in pair):
                        raise ArithmeticError("nonfinite likelihood endpoint")
                    if any(pair[0] > pair[1] for pair in pairs):
                        raise ArithmeticError("reversed likelihood endpoint")
                    if gap[0] > beta[1]:
                        status, reason = "CERTIFIED", "gap_lower_strictly_above_threshold_upper"
                    elif gap[1] <= beta[0]:
                        status, reason = "NOT_CERTIFIED", "gap_upper_at_or_below_threshold_lower"
                else:
                    # The public catalogue has a constant recommendation on the cube.
                    wrong, gap = None, None
                    status, reason = "CERTIFIED", "public_recommendation_constant_on_full_cube"
                final = chosen, selected, wrong, gap, beta, classes
                attempts.append({"precision": precision, "status": status,
                                 "gap_lower": str(gap[0]) if gap else "+Infinity",
                                 "gap_upper": str(gap[1]) if gap else "+Infinity",
                                 "threshold_lower": str(beta[0]), "threshold_upper": str(beta[1])})
            except (DecimalException, ArithmeticError, ValueError, OverflowError):
                status, reason, final = "UNDETERMINED", "arithmetic_failure", None
                attempts.append({"precision": precision, "status": status, "reason": reason})
            for key, value in interval.counts.items():
                operations[key] = operations.get(key, 0) + value
            if status != "UNDETERMINED" or reason == "arithmetic_failure":
                break
        result = {"status": status, "certified": status == "CERTIFIED",
                  "item": None, "candidate_item": None,
                  "decision": "stop" if status == "CERTIFIED" else "continue_or_abstain",
                  "reason": reason, "gap_lower": None, "gap_upper": None,
                  "threshold_lower": None, "threshold_upper": None,
                  "beta_lower": None, "beta_upper": None,
                  "candidate_loglik_lower": None, "candidate_loglik_upper": None,
                  "alternative_loglik_lower": None, "alternative_loglik_upper": None,
                  "precision": attempts[-1]["precision"], "precision_attempts": attempts,
                  "class_loglik_bounds": {}, "total_observations": int(data.sum()),
                  "action_counts": action_counts.tolist(),
                  "scope": {"max_dimension": MAX_DIMENSION, "max_groups": MAX_GROUPS,
                            "max_total_observations": MAX_TOTAL_OBSERVATIONS,
                            "dimension": model.d, "groups": model.G,
                            "theta_states": 2**model.d, "type_states": 2**model.G,
                            "joint_states": len(states), "recommendation_classes": len(model.items),
                            "channel": "1/2 <= q <= p <= 1-eta; continuous closure",
                            "eta": str(model.eta), "R": self.R,
                            "calibration_M": 0, "type_reports": 0,
                            "arithmetic": "exact_Fraction_MLE_outward_Decimal_log_intervals",
                            "aggregation": "max_within_same_recommendation_item",
                            "old_d4_gate_called": False,
                            "formal_proof_assistant_verified": False,
                            "trust": "analytic_model_reduction_and_Python_Fraction_Decimal_contracts"},
                  "operation_counts": {"exact_joint_mle_fits": len(states), **operations}}
        if final is not None:
            chosen, selected, wrong, gap, beta, classes = final
            result["candidate_item"] = int(chosen)
            if status == "CERTIFIED":
                result["item"] = int(chosen)
            result["class_loglik_bounds"] = {str(item): {"lower": str(value["bounds"][0]),
                                                        "upper": str(value["bounds"][1])}
                                            for item, value in classes.items()}
            for prefix, pair in (("candidate_loglik", selected["bounds"]),
                                 ("alternative_loglik", wrong), ("gap", gap),
                                 ("threshold", beta), ("beta", beta)):
                if pair is not None:
                    result[prefix + "_lower"], result[prefix + "_upper"] = map(str, pair)
            if gap is None:
                result["gap_lower"] = result["gap_upper"] = "+Infinity"
                result["alternative_loglik_lower"] = result["alternative_loglik_upper"] = "-Infinity"
            witness = selected["witness"]
            result["lower_witness"] = {"theta_mask": witness["theta_mask"],
                                       "z_mask": witness["z_mask"],
                                       "p": str(witness["p"]), "q": str(witness["q"])}
        result["elapsed_seconds"] = perf_counter() - started
        return result
