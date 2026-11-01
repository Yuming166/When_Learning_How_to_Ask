"""Bounded, trusted T2 closed-loop evaluation; allocators see observables only.

One strict trajectory supplies both budget readouts and the capped confidence
outcome. Readout-only decoding never changes a target or the stopping decision.
No model loading, fitting, worlds, or evaluation runs occur on module import.
"""
from __future__ import annotations

from copy import deepcopy
import math
import time

import numpy as np

from . import bootstrap  # noqa: F401
from .core import Scheduler, observed_state, teacher_target
from .data import make_world
from .information import WarmSolver
from phase2b.log_glr import log_glr
from phase2d.certified import certify_stop
from phase2d.strategies import AlignedFull, DRRCNoType, DRRCType
from phase2e.strategies import FusedOriginal, FusedInformation


ONLINE_CAP = 6144
CHECK_EVERY = 32
MATCHED_BLOCK = 32
BASELINES = {
    "Native-Fused-Original": FusedOriginal,
    "Fused-Original": FusedOriginal,
    "Fused-Info": FusedInformation,
    "Aligned": AlignedFull,
    "D-RRC-NoType": DRRCNoType,
    "D-RRC-Type": DRRCType,
}
STUDENTS = ("T1-MLP", "T2-MLP", "DeepSets-KL", "DeepSets-Info")
METHODS = tuple(BASELINES) + STUDENTS + ("Warm-KL",)


def _deadline(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("Closed-loop evaluation deadline reached")


def _weights(values, sampler):
    values = np.asarray(values, dtype=float)
    if values.shape != (sampler.E,) or np.any(~np.isfinite(values)) or np.any(values < 0):
        raise ValueError("Allocator returned malformed physical action weights")
    if not math.isclose(float(values.sum()), 1., rel_tol=0., abs_tol=1e-6):
        raise ValueError("Allocator weights do not sum to one")
    if sampler.type_accuracy is None and np.any(values[sampler.L:] != 0):
        raise ValueError("Allocator assigned mass to unavailable type actions")
    return values / values.sum()


def _compact_fit(fit):
    return {k: deepcopy(v) for k, v in fit.items()
            if k not in ("profile_log_likelihoods", "task_counts", "type_counts")}


def _prefix(sampler):
    return {"counts": sampler.counts.tolist(), "forced_counts": sampler.forced.tolist(),
            "type_answers": deepcopy(sampler.types)}


def _instrument(sampler, method, timings, updates):
    """Wrap this instance only; frozen class methods and source remain intact."""
    original_estimate, original_update = sampler._estimate, sampler._update

    def estimate():
        start = time.perf_counter()
        try:
            return original_estimate()
        finally:
            timings["estimation"] += time.perf_counter() - start

    def update():
        start, estimate_before = time.perf_counter(), timings["estimation"]
        try:
            original_update()
        finally:
            total = time.perf_counter() - start
            timings["planning"] += max(0., total - (timings["estimation"] - estimate_before))
        if method != "Native-Fused-Original":
            sampler.next_update = sampler.t + MATCHED_BLOCK
        values = _weights(sampler.weights, sampler)
        updates.append({"online": int(sampler.t), "weights": values.tolist(),
                        "estimate": deepcopy(sampler.last_estimate),
                        "next_update": int(sampler.next_update),
                        "input_boundary": "frozen_observable_estimator_and_counts_only"})

    sampler._estimate, sampler._update = estimate, update


def evaluate_path(spec, seed, R, method, models, readouts, deadline=None, *,
                  budget_only=False, on_progress=None):
    """Evaluate one paired path, retaining all failure and noncoverage outcomes.

    ``spec``, ``seed``, the environment, and episode truth stay inside this trusted
    evaluator. Predictors receive only a copied canonical observable state.
    ``models`` contains already-loaded CPU predictors; loading is driver cost.
    The exact Phase2e floating precheck conditions invocation of the strict gate.
    ``budget_only`` is an explicitly separate development readout mode: the
    public cap remains fixed, but acquisition ends at its last requested budget
    and certification is not evaluated. ``on_progress`` can persist compact
    paid prefixes before expensive calls; it never receives evaluator truth.
    """
    started, cpu_started = time.perf_counter(), time.process_time()
    timings = {key: 0. for key in ("estimation", "planning", "inference", "glr",
                                  "score_glr", "gate", "environment", "wall", "cpu")}
    row = {
        "world_id": spec.get("world_id"), "split": spec.get("kind"), "R": R,
        "method": method, "status": "running", "error": None, "online": 0,
        "mode": "budget_development" if budget_only else "fixed_confidence_with_budget_readouts",
        "costs": {"task": 0, "type": 0, "offline": 0}, "total_acquisition": 0,
        "certified": False, "certified_exact": None, "abstained": True,
        "final_guess": None, "final_guess_exact": None,
        "readouts": [], "gate_history": [], "updates": [], "action_trace": [],
        "counts": None, "forced_counts": None, "type_answers": None,
        "calibration": None, "timings": timings, "glr_checks": 0,
        "inference_calls": 0, "provider_model_calls": 0, "gpu_calls": 0,
        "automatic_retry": False, "strictly_certified_output": None,
        "online_cap": ONLINE_CAP, "check_every": CHECK_EVERY,
        "cadence": "native_frozen_sqrt" if method == "Native-Fused-Original" else "initial_2d_then_every_32",
        "prediction_boundary": "observable_state_only_no_world_seed_or_truth",
        "gate_scope": "not_evaluated_budget_development" if budget_only else "literal_phase2e_float_precheck_then_strict_certificate_at_crossing_or_cap",
        "readout_scope": "scoring_only_decode_with_absorbing_certified_answer",
    }
    env = sampler = episode = None
    calibration = None
    fit = None
    fit_online = None
    certified = False
    progress_index = 0

    def progress(event):
        nonlocal progress_index
        if on_progress is None:
            return
        costs = dict(env.cost) if env is not None else dict(row["costs"])
        payload = {
            "event": event, "world_id": row["world_id"], "split": row["split"],
            "R": R, "method": method, "mode": row["mode"],
            "online": int(sampler.t) if sampler is not None else 0,
            "costs": costs, "total_acquisition": sum(costs.values()),
            "action_trace_start": progress_index,
            "action_trace_block": deepcopy(row["action_trace"][progress_index:]),
            "status": row["status"],
        }
        on_progress(payload)
        progress_index = len(row["action_trace"])

    try:
        if method not in METHODS:
            raise ValueError("Unknown frozen T2 evaluation method")
        d = sum(spec["partition"])
        if method == "T1-MLP" and d != 4:
            row.update(status="not_applicable", abstained=None,
                       not_applicable_reason="frozen_T1_requires_exactly_d4_no_padding_retraining_or_dimension_extrapolation")
            return row
        _deadline(deadline)
        if R not in (16, 64, 256):
            raise ValueError("Evaluation risk must be one of frozen R16/R64/R256")
        if not 1 <= d <= 4 or not 1 <= len(spec["partition"]) <= 2:
            raise ValueError("Evaluation supports d<=4 and G<=2")
        if spec["online_cap"] != ONLINE_CAP:
            raise ValueError("Evaluation must use its frozen public online cap")
        readouts = tuple(readouts)
        valid_count = 1 <= len(readouts) <= 6 if budget_only else len(readouts) == 2
        if not valid_count or len(set(readouts)) != len(readouts) or any(type(b) is not int or not 1 <= b <= min(128, ONLINE_CAP) for b in readouts):
            raise ValueError("Distinct frozen readouts in [1,128] required: two for evaluation, up to six for budget development")
        readouts = tuple(sorted(readouts))
        stop_at = max(readouts) if budget_only else ONLINE_CAP
        row["requested_readouts"] = list(readouts)
        progress("before_environment")
        start = time.perf_counter()
        try:
            # R is passed before references are generated; M=round(alpha*R).
            env, episode = make_world(spec, seed, R)
            public, calibration = env.reset(), env.get_calibration()
        finally:
            timings["environment"] += time.perf_counter() - start
        if public["d"] != d:
            raise ValueError("Public dimension differs from the declared evaluation stratum")
        row["alpha_effective"] = len(calibration["high"]) / R
        row["calibration"] = deepcopy(calibration)
        progress("calibration_acquired")
        if method in BASELINES:
            sampler = BASELINES[method](public, calibration, R)
            _instrument(sampler, method, timings, row["updates"])
        else:
            sampler = Scheduler(public, calibration, R, block=MATCHED_BLOCK)
        warm = WarmSolver() if method == "Warm-KL" else None
        if method in STUDENTS and method not in models:
            raise ValueError("Required preloaded CPU predictor is absent")
        if method == "T1-MLP":
            row["t1_feature_scope"] = "unchanged_frozen_69_features_with_2048_normalization; actual_observable_cap_and_remaining_use_6144"

        def run_fit(score_only=False):
            start = time.perf_counter()
            try:
                return log_glr(sampler.counts, sampler.groups, calibration, sampler.types,
                               public["type_accuracy"], R, eta=sampler.eta)
            finally:
                timings["score_glr" if score_only else "glr"] += time.perf_counter() - start

        def readout(budget, readout_fit, absorbed):
            guess = [int(v) for v in readout_fit["theta"]]
            costs = dict(env.cost)
            return {
                "budget": budget, "effective_online": int(sampler.t),
                "guess": guess, "guess_exact": guess == list(episode.truth),
                "costs": costs, "total_acquisition": sum(costs.values()),
                "absorbed": bool(absorbed), "certified": bool(certified),
                "calibration": deepcopy(calibration), **_prefix(sampler),
            }

        while sampler.t < stop_at:
            _deadline(deadline)
            if method not in BASELINES and sampler.needs_update():
                progress("before_estimation_and_allocation")
                if method == "T1-MLP":
                    # This frozen student consumes raw count features and needs
                    # no posterior estimate. Its internal feature scaling stays
                    # unchanged even though this evaluator has a larger cap.
                    from t1.core import build_state
                    start = time.perf_counter()
                    try:
                        reports = [[len(bits) - sum(bits), sum(bits)] for bits in sampler.types]
                        state = build_state(public, calibration, sampler.counts, sampler.forced,
                                            reports, R, ONLINE_CAP)
                    finally:
                        timings["estimation"] += time.perf_counter() - start
                else:
                    start = time.perf_counter()
                    try:
                        state, _, _ = observed_state(sampler, calibration, R, ONLINE_CAP)
                    finally:
                        timings["estimation"] += time.perf_counter() - start
                update_record = {"online": int(sampler.t), "state": deepcopy(state),
                                 "input_boundary": "canonical_observable_state_only"}
                _deadline(deadline)
                start = time.perf_counter()
                if method == "Warm-KL":
                    try:
                        target = teacher_target(state, solver=warm)
                        predicted = target["teacher_weights"]
                        update_record["teacher_K"] = target["teacher_K"]
                        update_record["solver"] = target["solver"]
                    finally:
                        timings["planning"] += time.perf_counter() - start
                else:
                    row["inference_calls"] += 1
                    try:
                        prediction = models[method].predict(deepcopy(state))
                    finally:
                        timings["inference"] += time.perf_counter() - start
                    if method == "T1-MLP":
                        if not isinstance(prediction, dict) or prediction.get("valid") is not True:
                            raise ValueError("Frozen T1 predictor returned an invalid result")
                        padded = np.asarray(prediction["weights10"], dtype=float)
                        if padded.shape != (10,) or np.any(padded[sampler.E:] != 0):
                            raise ValueError("Frozen T1 padded action vector is invalid")
                        predicted = padded[:sampler.E]
                    else:
                        predicted = prediction
                values = _weights(predicted, sampler)
                sampler.set_target(values)
                update_record.update(weights=values.tolist(), next_update=int(sampler.next_update))
                row["updates"].append(update_record)

            if method in BASELINES and sampler.t >= sampler.next_update:
                progress("before_estimation_and_allocation")
            action = sampler.next(set(range(d)))
            if action is None:
                raise RuntimeError("Sampler returned no action before certification or cap")
            if method == "D-RRC-NoType" and action[0] == "type":
                raise RuntimeError("D-RRC-NoType attempted a type action")
            _deadline(deadline)
            start = time.perf_counter()
            try:
                answer = env.ask_type(action[1]) if action[0] == "type" else env.query(action[1], action[2])
            finally:
                timings["environment"] += time.perf_counter() - start
            sampler.observe(action, answer)
            if action[0] == "type":
                index, bit = sampler.L + action[1], "AB".index(answer["format"])
            else:
                index, bit = 2 * action[1] + "AB".index(action[2]), int(answer["answer"])
            row["action_trace"].append([int(index), int(bit), int(sampler.last_forced)])
            checked = sampler.t % CHECK_EVERY == 0 or sampler.t == stop_at
            if checked:
                _deadline(deadline)
                progress("before_scheduled_glr")
                fit, fit_online = run_fit(), sampler.t
                row["glr_checks"] += 1
                margin = 1e-8 * (1 + math.log1p(sampler.t + 2 * len(calibration["high"])))
                crossing = fit["gap"] - fit["beta"] > margin
                if not budget_only and (crossing or sampler.t == ONLINE_CAP):
                    _deadline(deadline)
                    progress("before_strict_gate")
                    start = time.perf_counter()
                    try:
                        certificate = certify_stop(sampler.counts, sampler.groups, calibration,
                                                   sampler.types, public["type_accuracy"], R,
                                                   sampler.eta, candidate_theta=fit["theta"])
                    finally:
                        timings["gate"] += time.perf_counter() - start
                    if type(certificate.get("certified")) is not bool:
                        raise ValueError("Strict gate returned a malformed certification flag")
                    row["gate_history"].append({"online": int(sampler.t), "floating_crossing": bool(crossing),
                                                "numeric_margin": margin, **deepcopy(certificate)})
                    certified = certificate["certified"]
            if sampler.t in readouts:
                if not checked:
                    progress("before_scoring_only_glr")
                scoring_fit = fit if checked else run_fit(score_only=True)
                row["readouts"].append(readout(sampler.t, scoring_fit, False))
            if certified:
                for budget in readouts:
                    if budget > sampler.t:
                        row["readouts"].append(readout(budget, fit, True))
                break
        if fit is None or fit_online != sampler.t:
            raise RuntimeError("No current scheduled likelihood fit at trajectory termination")
        row["status"] = "completed"
        progress("completed")
    except Exception as exc:
        row["status"] = "failed"
        row["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if env is not None:
            row["costs"] = dict(env.cost)
            row["total_acquisition"] = sum(env.cost.values())
        if sampler is not None:
            row["online"] = int(sampler.t)
            row.update(_prefix(sampler))
        row["certified"] = bool(certified)
        if row["status"] != "not_applicable":
            row["abstained"] = None if budget_only else not certified
        if fit is not None and sampler is not None and fit_online == sampler.t:
            guess = [int(v) for v in fit["theta"]]
            exact = guess == list(episode.truth)
            row.update(final_guess=guess, final_guess_exact=exact, final_fit=_compact_fit(fit))
            if certified:
                row.update(certified_exact=exact, strictly_certified_output=guess)
        row["readouts"].sort(key=lambda item: item["budget"])
        timings["wall"], timings["cpu"] = time.perf_counter() - started, time.process_time() - cpu_started
    return row
