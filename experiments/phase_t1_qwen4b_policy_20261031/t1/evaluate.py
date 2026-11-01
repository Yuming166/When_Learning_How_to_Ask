"""Paired T1 evaluation with injected predictors and explicit full denominators.

No experiment executes on import. Callers freeze inputs and supervise the
process deadline before invoking evaluation. Predictor callbacks receive only
the canonical observable state, never a world specification or evaluator.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json
import math
import sys
from time import perf_counter, process_time


QWEN_METHODS = frozenset(("BaseQwen", "LoRA"))
METHODS = ("NativeAligned", "AlignedBlock128", "DNoTypeBlock128",
           "DTypeBlock128", "MLP", "BaseQwen", "LoRA")
BLOCK_SIZE = 128
PUBLIC_CAP = 2048


def _historical_imports():
    from .core import ORIGINAL_ROOT
    location = str(ORIGINAL_ROOT / "experiments/phase2d_method_improvement_20261031")
    if location not in sys.path:
        sys.path.insert(0, location)
    from phase2d import bootstrap  # noqa: F401


class InferenceLimit(RuntimeError):
    pass


class EvaluationDeadline(TimeoutError):
    pass


@dataclass
class InferenceBudget:
    limit: int = 600
    calls: int = 0
    by_method: dict = field(default_factory=dict)

    def charge(self, method):
        if not 0 <= self.limit <= 600 or self.calls >= self.limit:
            raise InferenceLimit("Frozen total Qwen inference-call budget exhausted")
        self.calls += 1
        self.by_method[method] = self.by_method.get(method, 0) + 1

    def record(self):
        return {"limit": self.limit, "calls": self.calls, "by_method": dict(self.by_method)}


def _deadline(deadline):
    if deadline is not None and perf_counter() >= deadline:
        raise EvaluationDeadline("Frozen evaluation wall deadline reached")


def _predict(predictor, state):
    return predictor.predict(state) if hasattr(predictor, "predict") else predictor(state)


def _normalized(weights, mask):
    values = [float(v) for v in weights]
    if len(values) != 10 or len(mask) != 10 or not any(mask):
        raise ValueError("Invalid allocation dimensions or empty legal mask")
    if any(not math.isfinite(v) or v < 0 or (not legal and v > 1e-10)
           for v, legal in zip(values, mask)):
        raise ValueError("Allocation violates finite nonnegative legal-action contract")
    values = [v if legal else 0. for v, legal in zip(values, mask)]
    total = math.fsum(values)
    if total <= 0 or abs(total - 1) > 1e-5:
        raise ValueError("Allocation must sum to one")
    return [v / total for v in values]


def _uniform(mask):
    total = sum(bool(v) for v in mask)
    if not total:
        raise ValueError("No legal fallback action")
    return [float(bool(v)) / total for v in mask]


def percent_round(weights, mask):
    """Largest remainder, exact total 100, lexicographic fractional ties."""
    values = _normalized(weights, mask)
    scaled = [v * 100 for v in values]
    result = [math.floor(v) if legal else 0 for v, legal in zip(scaled, mask)]
    remainder = 100 - sum(result)
    order = sorted((i for i, legal in enumerate(mask) if legal),
                   key=lambda i: (-(scaled[i] - result[i]), i))
    for i in order[:remainder]:
        result[i] += 1
    if sum(result) != 100:
        raise ArithmeticError("Percent rounding failed exact mass check")
    return result


def call_predictor(predictor, state, *, method, budget=None, is_qwen=False, deadline=None):
    """Charge Qwen before the call; retain failed raw output and legal fallback.

    Only Qwen output/transport failures receive the prespecified uniform legal
    fallback. Invalid numerical or statistical baselines fail visibly.
    Deadline/budget exhaustion is never converted into fallback permission.
    """
    from .core import state_features
    state_features(state)  # invokes the shared observable schema validation
    _deadline(deadline)
    if is_qwen:
        if budget is None:
            raise ValueError("Every Qwen call requires the shared explicit budget")
        budget.charge(method)
    started, cpu_started = perf_counter(), process_time()
    error = None
    prediction = None
    try:
        prediction = _predict(predictor, deepcopy(state))
        if not isinstance(prediction, dict):
            raise ValueError("Predictor must return a record")
        if not prediction.get("valid", False):
            raise ValueError(prediction.get("error") or "Predictor marked output invalid")
        weights = _normalized(prediction.get("weights10", prediction.get("weights")), state["action_mask"])
        valid = True
    except (InferenceLimit, EvaluationDeadline):
        raise
    except Exception as exc:
        if not is_qwen:
            raise
        valid = False
        error = type(exc).__name__ + ": " + str(exc)
        weights = _uniform(state["action_mask"])
        if prediction is None:
            prediction = {"raw": None, "valid": False, "error": error,
                          "prompt_tokens": 0, "output_tokens": 0}
    wall, cpu = perf_counter() - started, process_time() - cpu_started
    return {"weights10": weights, "percent10": percent_round(weights, state["action_mask"]),
            "valid": valid, "fallback": not valid, "error": error,
            "prediction": prediction, "inference_wall_seconds": wall,
            "inference_cpu_seconds": cpu,
            "deadline_exceeded_after_call": deadline is not None and perf_counter() >= deadline,
            "prompt_tokens": int(prediction.get("prompt_tokens", 0)),
            "output_tokens": int(prediction.get("output_tokens", 0))}


def allocation_metrics(teacher_weights, student_weights, mask, teacher_percent=None):
    target, student = _normalized(teacher_weights, mask), _normalized(student_weights, mask)
    epsilon = 1e-8
    smooth = [v + epsilon if legal else 0. for v, legal in zip(student, mask)]
    norm = math.fsum(smooth)
    smooth = [v / norm for v in smooth]
    kl = math.fsum(t * math.log(t / s) for t, s in zip(target, smooth) if t > 0)
    target_percent = percent_round(target, mask) if teacher_percent is None else list(teacher_percent)
    student_percent = percent_round(student, mask)
    if (len(target_percent) != 10 or sum(target_percent) != 100
            or any(type(v) is not int or v < 0 or (v and not legal)
                   for v, legal in zip(target_percent, mask))):
        raise ValueError("Invalid teacher percent target")
    return {
        "allocation_l1": math.fsum(abs(t - s) for t, s in zip(target, student)),
        "forward_kl_epsilon_1e8": max(0., kl),
        "forward_kl_definition": "teacher || normalized(student + 1e-8 on legal actions)",
        "percent_l1": sum(abs(t - s) for t, s in zip(target_percent, student_percent)) / 100,
        "percent_exact": target_percent == student_percent,
        "student_rounding_l1": math.fsum(abs(v - p / 100) for v, p in zip(student, student_percent)),
        "teacher_rounding_l1": math.fsum(abs(v - p / 100) for v, p in zip(target, target_percent)),
    }


def _kl(r, q):
    return (r * math.log(r / q) if r else 0.) + ((1 - r) * math.log((1 - r) / (1 - q)) if r < 1 else 0.)


def _fit_weighted(high_s, high_n, low_s, low_n, eta):
    clip = lambda v: min(1 - eta, max(.5, v))
    p = clip(high_s / high_n) if high_n else .5
    q = clip(low_s / low_n) if low_n else .5
    if high_n and low_n and p < q:
        p = q = clip((high_s + low_s) / (high_n + low_n))
    if not high_n:
        p = q
    return p, q


def plugin_information(state, weights, estimate, teacher_K):
    """Float diagnostic infimum for arbitrary, possibly asymmetric weights.

    The offline intensity is rho=(M/R)/K_teacher, not alpha and not M/t.
    All wrong sign masks, all type assignments and the continuous ordered
    rates are covered. This is an observable plug-in metric, not a certificate.
    """
    weights = _normalized(weights, state["action_mask"])
    d, groups = state["d"], state["groups"]
    if d != 4 or not 1 <= len(groups) <= 2:
        raise ValueError("T1 information metric supports frozen d4, G<=2")
    p, q = float(estimate["p"]), float(estimate["q"])
    z = list(estimate["z"])
    eta = float(state["eta"])
    if not .5 <= q <= p <= 1 - eta or not math.isfinite(teacher_K) or teacher_K <= 0:
        raise ValueError("Invalid observable plug-in estimate or teacher coefficient")
    membership = [None] * d
    for g, members in enumerate(groups):
        for j in members:
            membership[j] = g
    rho = (state["calibration"]["high"]["total"] / state["R"]) / teacher_K
    rates = [[p if fmt == z[membership[j]] else q for fmt in range(2)] for j in range(d)]
    best = math.inf
    for flips in range(1, 2**d):
        for alternative_type in range(2**len(groups)):
            alt_z = [(alternative_type >> g) & 1 for g in range(len(groups))]
            hs, hn, ls, ln = rho * p, rho, rho * q, rho
            for j in range(d):
                for fmt in range(2):
                    weight, rate = weights[2 * j + fmt], rates[j][fmt]
                    oriented = 1 - rate if flips >> j & 1 else rate
                    if fmt == alt_z[membership[j]]:
                        hs, hn = hs + weight * oriented, hn + weight
                    else:
                        ls, ln = ls + weight * oriented, ln + weight
            u, v = _fit_weighted(hs, hn, ls, ln, eta)
            values = [rho * (_kl(p, u) + _kl(q, v))]
            for j in range(d):
                for fmt in range(2):
                    alternate = u if fmt == alt_z[membership[j]] else v
                    if flips >> j & 1:
                        alternate = 1 - alternate
                    values.append(weights[2 * j + fmt] * _kl(rates[j][fmt], alternate))
            if state["known_s"] is not None:
                for g, accuracy in enumerate(state["known_s"]):
                    if alt_z[g] != z[g]:
                        values.append(weights[8 + g] * _kl(accuracy, 1 - accuracy))
            best = min(best, math.fsum(values))
    return max(0., best)


def _average(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    return {"mean": math.fsum(values) / len(values) if values else None,
            "numerator_sum": math.fsum(values), "denominator": len(values),
            "total_rows": len(rows)}


def evaluate_offline(rows, predictor, *, method, budget=None, is_qwen=False, deadline=None,
                     on_record=None):
    rows = list(rows)
    records = []
    interrupted = None
    for position, row in enumerate(rows):
        state = row["state"]
        try:
            result = call_predictor(predictor, state, method=method, budget=budget,
                                    is_qwen=is_qwen, deadline=deadline)
        except Exception as exc:
            interrupted = {"type": type(exc).__name__, "message": str(exc), "next_position": position}
            break
        metrics = allocation_metrics(row["teacher_weights"], result["weights10"],
                                     state["action_mask"], row.get("teacher_percent"))
        info = {"plugin_teacher_information": None, "plugin_student_information": None,
                "plugin_relative_information_deficit": None,
                "information_scope": "observable_plugin_float_diagnostic_not_true_world_or_certificate"}
        if "teacher_estimate" in row and "teacher_K" in row:
            target_info = plugin_information(state, row["teacher_weights"],
                                             row["teacher_estimate"], row["teacher_K"])
            student_info = plugin_information(state, result["weights10"],
                                              row["teacher_estimate"], row["teacher_K"])
            info.update(plugin_teacher_information=target_info, plugin_student_information=student_info,
                        plugin_relative_information_deficit=(1 - student_info / target_info) if target_info > 0 else None,
                        reference_intensity=(state["calibration"]["high"]["total"] / state["R"]) / row["teacher_K"])
        records.append({"position": position, "row_id": row.get("row_id"),
                        "world_id": row.get("world_id"), "split": row.get("split"),
                        "method": method, "state": deepcopy(state),
                        "teacher_weights": row["teacher_weights"],
                        **result, **metrics, **info})
        if on_record is not None:
            on_record(records[-1])
        if result["deadline_exceeded_after_call"]:
            interrupted = {"type": "EvaluationDeadline", "message": "Deadline exceeded during completed call",
                           "next_position": position + 1}
            break
    summary = {"method": method, "states": len(rows), "recorded_states": len(records),
               "not_run_states": len(rows) - len(records),
               "valid": sum(row["valid"] for row in records),
               "invalid_fallbacks": sum(row["fallback"] for row in records),
               "denominator_scope": "all_requested_states_including_invalid_fallbacks"}
    for key in ("allocation_l1", "forward_kl_epsilon_1e8", "percent_l1", "percent_exact",
                "student_rounding_l1", "teacher_rounding_l1", "plugin_relative_information_deficit",
                "inference_wall_seconds", "inference_cpu_seconds", "prompt_tokens", "output_tokens"):
        summary[key] = _average(records, key)
        summary[key]["requested_states"] = len(rows)
    summary["by_split"] = {split: {"states": sum(str(r.get("split")) == split for r in rows),
                                  "recorded_states": len(part),
                                  "not_run_states": sum(str(r.get("split")) == split for r in rows) - len(part),
                                  "allocation_l1": _average(part, "allocation_l1"),
                                  "forward_kl_epsilon_1e8": _average(part, "forward_kl_epsilon_1e8"),
                                  "invalid_fallbacks": sum(r["fallback"] for r in part)}
                           for split in sorted({str(r.get("split")) for r in rows})
                           for part in [[r for r in records if str(r["split"]) == split]]}
    return {"status": "interrupted" if interrupted else "completed", "error": interrupted,
            "records": records, "summary": summary}


def _public_and_calibration(state):
    public = {"d": state["d"], "groups": [{"targets": list(g)} for g in state["groups"]],
              "rate_domain": {"eta": state["eta"]}, "type_accuracy": state["known_s"]}
    calibration = {key: [1] * value["successes"] + [0] * (value["total"] - value["successes"])
                   for key, value in state["calibration"].items()}
    return public, calibration


def _baseline_target(state, cls):
    import numpy as np
    public, calibration = _public_and_calibration(state)
    sampler = cls(public, calibration, state["R"])
    sampler.counts = np.asarray(state["counts"], dtype=np.int64).copy()
    sampler.forced = np.asarray(state["forced_counts"], dtype=np.int64).copy()
    sampler.types = [[0] * pair[0] + [1] * pair[1] for pair in state["type_report_counts"]]
    sampler.t = state["online"]
    sampler._update()
    weights = list(map(float, sampler.weights))
    weights += [0.] * (10 - len(weights))
    return {"weights10": weights, "raw": {"estimate": sampler.last_estimate}, "valid": True,
            "prompt_tokens": 0, "output_tokens": 0}


def baseline_predictors():
    _historical_imports()
    from .core import teacher_target
    from phase2c.decaying import DecayingRepeatAndCompare
    from phase2d.strategies import DRRCType

    def aligned(state):
        result = teacher_target(state)
        return {"weights10": result["weights"], "raw": result, "valid": True,
                "prompt_tokens": 0, "output_tokens": 0}

    return {"AlignedBlock128": aligned,
            "DNoTypeBlock128": lambda state: _baseline_target(state, DecayingRepeatAndCompare),
            "DTypeBlock128": lambda state: _baseline_target(state, DRRCType)}


def _common_fit(sampler, public, calibration, R):
    _historical_imports()
    from phase2b.log_glr import log_glr
    return log_glr(sampler.counts, [g["targets"] for g in public["groups"]], calibration,
                   sampler.types, public["type_accuracy"], R, eta=public["rate_domain"]["eta"])


def _strict_gate(sampler, public, calibration, R, fit):
    _historical_imports()
    from phase2d.certified import certify_stop
    return certify_stop(sampler.counts, [g["targets"] for g in public["groups"]], calibration,
                        sampler.types, public["type_accuracy"], R,
                        eta=public["rate_domain"]["eta"], candidate_theta=fit["theta"])


def _run_method(spec, seed, name, predictor, *, R, readouts, public_cap,
                budget, deadline, diagnostic, on_event=None):
    _historical_imports()
    from .core import CommonScheduler, build_state
    from .data import make_world
    from phase2b.aligned import TheoryAlignedTracking
    started, cpu_started = perf_counter(), process_time()
    _deadline(deadline)
    env, episode = make_world(spec, seed)
    public, calibration = env.reset(), env.get_calibration()
    native = name == "NativeAligned"
    if native:
        sampler = TheoryAlignedTracking(public, calibration, R)
    else:
        if predictor is None:
            raise ValueError("Matched method requires its predictor")
        sampler = CommonScheduler(public, calibration, R, online_cap=public_cap, block_size=BLOCK_SIZE)
    stop_at = public_cap if diagnostic else max(readouts)
    predictions, actions, snapshots, gates = [], [], [], []
    complete, fit, error = False, None, None
    glr_wall = glr_cpu = gate_wall = gate_cpu = 0.
    inference_wall = inference_cpu = 0.
    prompt_tokens = output_tokens = invalid = 0

    def emit(kind, payload):
        if on_event is not None:
            on_event({"kind": kind, "world_id": spec["world_id"], "method": name, "payload": payload})

    def native_state():
        report_counts = [[len(a) - sum(a), sum(a)] for a in sampler.types]
        return build_state(public, calibration, sampler.counts, sampler.forced, report_counts, R, public_cap)

    try:
        while sampler.t < stop_at:
            _deadline(deadline)
            before_update = sampler.last_update
            if not native and sampler.needs_update():
                state = sampler.state()
                prediction = call_predictor(predictor, state, method=name, budget=budget,
                                            is_qwen=name in QWEN_METHODS, deadline=deadline)
                sampler.set_target(prediction["weights10"])
                predictions.append({"online": sampler.t, "state": deepcopy(state), **prediction})
                emit("prediction", predictions[-1])
                inference_wall += prediction["inference_wall_seconds"]
                inference_cpu += prediction["inference_cpu_seconds"]
                prompt_tokens += prediction["prompt_tokens"]
                output_tokens += prediction["output_tokens"]
                invalid += int(prediction["fallback"])
            before_planner_wall, before_planner_cpu = sampler.planner_seconds, sampler.planner_cpu_seconds
            action = sampler.next(set(range(public["d"])))
            if native and sampler.last_update != before_update:
                state = native_state()
                weights = list(map(float, sampler.weights)) + [0.] * (10 - len(sampler.weights))
                wall = sampler.planner_seconds - before_planner_wall
                cpu = sampler.planner_cpu_seconds - before_planner_cpu
                predictions.append({"online": sampler.t, "state": state, "weights10": weights,
                                    "valid": True, "fallback": False,
                                    "prediction": {"raw": deepcopy(sampler.last_estimate)},
                                    "inference_wall_seconds": wall, "inference_cpu_seconds": cpu,
                                    "prompt_tokens": 0, "output_tokens": 0})
                emit("prediction", predictions[-1])
                inference_wall += wall
                inference_cpu += cpu
            if action is None:
                raise RuntimeError("Sampler returned no action before evaluator deadline")
            _deadline(deadline)
            answer = env.ask_type(action[1]) if action[0] == "type" else env.query(action[1], action[2])
            sampler.observe(action, answer)
            actions.append({"online": sampler.t, "action": list(action), "answer": deepcopy(answer)})
            emit("action", actions[-1])
            checkpoint = (sampler.t % BLOCK_SIZE == 0 or sampler.t == stop_at) if diagnostic else sampler.t in readouts
            if not checkpoint:
                continue
            wall_start, cpu_start = perf_counter(), process_time()
            fit = _common_fit(sampler, public, calibration, R)
            glr_wall += perf_counter() - wall_start
            glr_cpu += process_time() - cpu_start
            certificate = None
            if diagnostic:
                wall_start, cpu_start = perf_counter(), process_time()
                certificate = _strict_gate(sampler, public, calibration, R, fit)
                gate_wall += perf_counter() - wall_start
                gate_cpu += process_time() - cpu_start
                gates.append({"online": sampler.t, **certificate})
                complete = bool(certificate["certified"])
            exact = list(fit["theta"]) == list(episode.truth)
            snapshots.append({"online": sampler.t, "guess": fit["theta"], "guess_exact": exact,
                              "correct_facts": sum(a == b for a, b in zip(fit["theta"], episode.truth)),
                              "costs": dict(env.cost), "total_acquisition": sum(env.cost.values()),
                              "counts": sampler.counts.tolist(), "type_answers": deepcopy(sampler.types),
                              "fit": fit, "strict_certificate": certificate,
                              "strictly_certified_output": fit["theta"] if complete else None,
                              "fixed_budget_guess_is_certified": False,
                              "inference_wall_seconds": inference_wall,
                              "inference_cpu_seconds": inference_cpu,
                              "glr_wall_seconds": glr_wall, "gate_wall_seconds": gate_wall,
                              "prompt_tokens": prompt_tokens, "output_tokens": output_tokens,
                              "invalid_fallbacks": invalid,
                              "elapsed_wall_seconds": perf_counter() - started,
                              "elapsed_cpu_seconds": process_time() - cpu_started})
            emit("snapshot", snapshots[-1])
            if complete:
                break
        if fit is None:
            raise RuntimeError("No planned evaluation readout reached")
        env.submit([int(v) for v in fit["theta"]])
        score = env.score()
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        score = None
    return {
        "world_id": spec["world_id"], "world_index": spec["index"], "split": spec["split"],
        "method": name, "mode": "fixed_confidence_diagnostic" if diagnostic else "fixed_budget",
        "status": "failed" if error else "completed", "error": error,
        "R": R, "public_online_cap": public_cap, "evaluation_readouts": list(readouts),
        "alpha_effective": len(calibration["high"]) / R,
        "diagnostic_calibration_scope": "same_world_same_M; R16 yields alpha0_or4" if diagnostic else None,
        "cadence": "native_frozen_sqrt_updates" if native else "initial8_then_block128",
        "online": sampler.t, "costs": dict(env.cost), "total_acquisition": sum(env.cost.values()),
        "complete": complete, "abstained": bool(diagnostic and not complete),
        "strictly_certified_output": fit["theta"] if complete else None,
        "certified_exact": (list(fit["theta"]) == list(episode.truth)) if complete else None,
        "final_guess": None if fit is None else fit["theta"],
        "final_guess_exact": None if fit is None else list(fit["theta"]) == list(episode.truth),
        "snapshots": snapshots, "gate_history": gates, "predictions": predictions,
        "action_trace": actions, "counts": sampler.counts.tolist(), "forced_counts": sampler.forced.tolist(),
        "type_answers": deepcopy(sampler.types), "calibration": deepcopy(calibration),
        "inference_calls": len(predictions), "inference_wall_seconds": inference_wall,
        "inference_cpu_seconds": inference_cpu, "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens, "invalid_fallbacks": invalid,
        "glr_wall_seconds": glr_wall, "glr_cpu_seconds": glr_cpu,
        "gate_wall_seconds": gate_wall, "gate_cpu_seconds": gate_cpu,
        "wall_seconds": perf_counter() - started, "cpu_seconds": process_time() - cpu_started,
        "score": score,
        "prediction_boundary": "canonical_observable_state_only_no_evaluator_metadata",
    }


def evaluate_world(spec, seed, methods, *, R=64, readouts=(256, 512),
                   public_cap=PUBLIC_CAP, budget=None, deadline=None, diagnostic=False,
                   on_event=None):
    """Run methods paired on the same world and shared potential stream draws.

    methods maps name to predictor; NativeAligned may map to None. The world
    spec/seed are evaluator-only inputs. R16 diagnostics reuse the exact world
    and M from spec but start a separate policy path with the changed public R.
    No confirmation-world source or index is consulted.
    """
    if public_cap != PUBLIC_CAP or int(spec["online_cap"]) != PUBLIC_CAP:
        raise ValueError("T1 public budget must remain 2048 in every policy input")
    if R != (16 if diagnostic else 64):
        raise ValueError("Frozen T1 risk target is R64 primary and R16 diagnostic")
    if tuple(readouts) != (256, 512):
        raise ValueError("Frozen fixed-budget readouts are 256 and 512")
    if not methods or any(name not in METHODS for name in methods):
        raise ValueError("Unknown or empty T1 method set")
    records = []
    for name, predictor in methods.items():
        result = _run_method(spec, seed, name, predictor, R=R, readouts=readouts,
                             public_cap=public_cap, budget=budget, deadline=deadline, diagnostic=diagnostic,
                             on_event=on_event)
        records.append(result)
        if on_event is not None:
            on_event({"kind": "path_result", "world_id": spec["world_id"], "method": name, "payload": result})
        if result["status"] != "completed":
            return {"world_id": spec["world_id"], "status": "interrupted", "records": records,
                    "not_run_methods": [n for n in methods if n not in [r["method"] for r in records]],
                    "call_budget": None if budget is None else budget.record()}
    return {"world_id": spec["world_id"], "status": "completed", "records": records,
            "not_run_methods": [], "call_budget": None if budget is None else budget.record()}


def summarize_paths(records, *, expected_world_ids=None):
    """World-level/full-denominator summaries; incomplete paths stay visible."""
    records = list(records)
    expected = None if expected_world_ids is None else set(expected_world_ids)
    summary = {}
    for name in sorted(METHODS if expected is not None else {r["method"] for r in records}):
        rows = [r for r in records if r["method"] == name]
        identifiers = [r["world_id"] for r in rows]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Do not mix duplicate worlds/modes in one summary")
        denominator = len(expected) if expected is not None else len(rows)
        if expected is not None and not set(identifiers) <= expected:
            raise ValueError("Unexpected world in frozen evaluation summary")
        readouts = {}
        for budget in (256, 512):
            snapshots = [s for row in rows for s in row["snapshots"] if s["online"] == budget]
            correct = sum(s["guess_exact"] for s in snapshots)
            readouts[str(budget)] = {"exact_recovered": correct, "denominator": denominator,
                                     "observed_readouts": len(snapshots),
                                     "missing_readouts": denominator - len(snapshots),
                                     "exact_recovery_lower_fraction": correct / denominator if denominator else None}
        summary[name] = {
            "denominator": denominator, "recorded_paths": len(rows),
            "failed_paths": sum(r["status"] != "completed" for r in rows),
            "missing_paths": denominator - len(rows), "readouts": readouts,
            "certified_outputs": sum(r["complete"] for r in rows),
            "wrong_certified_outputs": sum(r["complete"] and not r["certified_exact"] for r in rows),
            "abstentions": sum(r["abstained"] for r in rows),
            "invalid_fallbacks": sum(r["invalid_fallbacks"] for r in rows),
            "total_costs": {kind: sum(r["costs"][kind] for r in rows) for kind in ("task", "type", "offline")},
            "inference_wall_seconds": sum(r["inference_wall_seconds"] for r in rows),
            "inference_cpu_seconds": sum(r["inference_cpu_seconds"] for r in rows),
            "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
            "output_tokens": sum(r["output_tokens"] for r in rows),
        }
    return summary


def paired_recovery(records, left, right, *, budget=512, expected_world_ids=None):
    """Pair by complete world, retaining missing outcomes in the denominator."""
    def index_rows(name):
        result = {}
        for row in records:
            if row["method"] != name:
                continue
            if row["world_id"] in result:
                raise ValueError("Duplicate paired world")
            snapshots = [s for s in row["snapshots"] if s["online"] == budget]
            result[row["world_id"]] = snapshots[0]["guess_exact"] if snapshots else None
        return result

    a, b = index_rows(left), index_rows(right)
    worlds = set(expected_world_ids) if expected_world_ids is not None else set(a) | set(b)
    outcomes = [{"world_id": world, "left": a.get(world), "right": b.get(world)} for world in sorted(worlds)]
    return {"left": left, "right": right, "budget": budget, "denominator": len(worlds),
            "left_only_correct": sum(r["left"] is True and r["right"] is False for r in outcomes),
            "right_only_correct": sum(r["right"] is True and r["left"] is False for r in outcomes),
            "both_correct": sum(r["left"] is True and r["right"] is True for r in outcomes),
            "both_wrong": sum(r["left"] is False and r["right"] is False for r in outcomes),
            "missing_pairs": sum(r["left"] is None or r["right"] is None for r in outcomes),
            "world_outcomes": outcomes}
