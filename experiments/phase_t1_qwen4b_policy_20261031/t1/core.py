"""Legal observable inputs and common scheduling for the isolated T1 pilot."""
from copy import deepcopy
import json
import math
from pathlib import Path
import sys

# Historical imports must never create bytecode in the frozen research tree.
sys.dont_write_bytecode = True
ORIGINAL_ROOT = (Path(__file__).resolve().parents[3])
for historical in ("phase2a_theory_optimality_20261030", "phase2b_alignment_20261031"):
    location = str(ORIGINAL_ROOT / "experiments" / historical)
    if location not in sys.path:
        sys.path.insert(0, location)

import numpy as np
from phase2b.aligned import TheoryAlignedTracking

ACTION_DIM = 10
FEATURE_DIM = 69
BLOCK_SIZE = 128
PUBLIC_CAP = 2048
SCHEMA = "t1_observable_v1"
STATE_KEYS = frozenset(("schema", "d", "groups", "eta", "known_s", "counts", "forced_counts",
                        "type_report_counts", "calibration", "R", "online", "online_cap", "remaining", "action_mask"))
SYSTEM_PROMPT = (
    "You allocate queries using only the supplied observable state. Return exactly one JSON array "
    "of 10 integer percentages, each from 0 to 100, summing to 100. Entries 0..7 are "
    "task queries (0,A),(0,B),(1,A),(1,B),(2,A),(2,B),(3,A),(3,B). Entries 8..9 are "
    "type queries for groups 0..1. Every action whose action_mask is 0 must receive 0. "
    "Provide no explanation or additional text."
)


def _integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _count_array(value, shape, name):
    array = np.asarray(value)
    if array.shape != shape or array.dtype.kind not in "iu" or np.any(array < 0) or np.any(array > 2**50):
        raise ValueError(f"Invalid nonnegative integer {name}")
    return array.astype(np.int64, copy=True)


def calibration_summary(calibration):
    if set(calibration) != {"high", "low"}:
        raise ValueError("Expected both labelled calibration streams")
    result = {}
    for key in ("high", "low"):
        values = list(calibration[key])
        if any(type(value) not in (int, bool) or value not in (0, 1) for value in values):
            raise ValueError("Calibration observations must be bits")
        result[key] = {"successes": sum(values), "total": len(values)}
    if result["high"]["total"] != result["low"]["total"]:
        raise ValueError("Labelled reference stream lengths must agree")
    return result


def build_state(public, calibration, counts, forced_counts, type_report_counts, R, online_cap):
    """Extract an allowlist; unrelated public metadata is never retained."""
    groups = [list(group["targets"]) for group in public["groups"]]
    known = public.get("type_accuracy")
    state = {"schema": SCHEMA, "d": public["d"], "groups": groups,
             "eta": public["rate_domain"]["eta"], "known_s": None if known is None else list(known),
             "counts": np.asarray(counts).tolist(), "forced_counts": np.asarray(forced_counts).tolist(),
             "type_report_counts": np.asarray(type_report_counts).tolist(),
             "calibration": calibration_summary(calibration), "R": float(R), "online_cap": online_cap}
    state["online"] = int(np.asarray(counts).sum() + np.asarray(type_report_counts).sum())
    state["remaining"] = online_cap - state["online"]
    state["action_mask"] = [1] * 8 + [int(known is not None and g < len(groups)) for g in range(2)]
    return validate_state(state)


def validate_state(state):
    """Return a normalized safe copy; extra fields, including nested ones, fail."""
    if not isinstance(state, dict) or set(state) != STATE_KEYS or state["schema"] != SCHEMA:
        raise ValueError("State violates the observable field allowlist")
    d = _integer(state["d"], "d", 1)
    if d != 4:
        raise ValueError("T1 has exactly four task coordinates")
    groups = state["groups"]
    if not isinstance(groups, list) or not 1 <= len(groups) <= 2 or any(not isinstance(g, list) or not g for g in groups):
        raise ValueError("Expected one or two nonempty groups")
    groups = [[_integer(j, "coordinate") for j in group] for group in groups]
    if sorted(j for group in groups for j in group) != list(range(d)):
        raise ValueError("Groups must partition the four coordinates")
    eta = float(state["eta"])
    if not math.isfinite(eta) or not 0 < eta < .5:
        raise ValueError("Invalid public rate domain")
    known = state["known_s"]
    if known is not None:
        known = [float(value) for value in known]
        if len(known) != len(groups) or any(not math.isfinite(s) or not .5 < s < 1 for s in known):
            raise ValueError("Invalid known type accuracies")
    counts = _count_array(state["counts"], (d, 2, 2), "response counts")
    forced = _count_array(state["forced_counts"], (d, 2, 2), "forced response counts")
    reports = _count_array(state["type_report_counts"], (len(groups), 2), "type report counts")
    if np.any(forced > counts) or (known is None and np.any(reports)):
        raise ValueError("Inconsistent forced counts or unavailable type reports")
    calibration = state["calibration"]
    if not isinstance(calibration, dict) or set(calibration) != {"high", "low"}:
        raise ValueError("Invalid calibration summary")
    normalized_calibration = {}
    for key in ("high", "low"):
        stream = calibration[key]
        if not isinstance(stream, dict) or set(stream) != {"successes", "total"}:
            raise ValueError("Calibration summary violates allowlist")
        successes, total = (_integer(stream[name], name) for name in ("successes", "total"))
        if successes > total:
            raise ValueError("Calibration successes exceed total")
        normalized_calibration[key] = {"successes": successes, "total": total}
    if normalized_calibration["high"]["total"] != normalized_calibration["low"]["total"]:
        raise ValueError("Reference lengths differ")
    risk = float(state["R"])
    if not math.isfinite(risk) or risk <= 0:
        raise ValueError("Invalid public confidence target")
    online = _integer(state["online"], "online")
    cap = _integer(state["online_cap"], "online cap", 1)
    remaining = _integer(state["remaining"], "remaining")
    if online != int(counts.sum() + reports.sum()) or online > cap or remaining != cap - online:
        raise ValueError("Observable action counts disagree with public budget")
    mask = [1] * 8 + [int(known is not None and g < len(groups)) for g in range(2)]
    if state["action_mask"] != mask or any(type(x) is not int for x in state["action_mask"]):
        raise ValueError("Incorrect legal action mask")
    return {"schema": SCHEMA, "d": d, "groups": groups, "eta": eta, "known_s": known,
            "counts": counts.tolist(), "forced_counts": forced.tolist(), "type_report_counts": reports.tolist(),
            "calibration": normalized_calibration, "R": risk, "online": online,
            "online_cap": cap, "remaining": remaining, "action_mask": mask}


def serialize_state(state):
    return json.dumps(validate_state(state), sort_keys=True, separators=(",", ":"), allow_nan=False)


def state_features(state):
    """69 allowlisted features, with fixed log1p scaling of observed counts."""
    state = validate_state(state)
    membership = np.zeros((4, 2))
    for g, members in enumerate(state["groups"]):
        membership[members, g] = 1.
    group_count = len(state["groups"])
    known = [0., 0.] if state["known_s"] is None else state["known_s"] + [0.] * (2 - group_count)
    reports = np.zeros((2, 2))
    reports[:group_count] = state["type_report_counts"]
    numbers = (np.asarray(state["counts"]).ravel().tolist() + np.asarray(state["forced_counts"]).ravel().tolist()
               + reports.ravel().tolist() + [state["calibration"][key][field] for key in ("high", "low") for field in ("successes", "total")]
               + [state[key] for key in ("R", "online", "online_cap", "remaining")])
    prefix = [state["d"] / 4, group_count / 2, state["eta"]] + membership.ravel().tolist() + [int(g < group_count) for g in range(2)] + known + state["action_mask"]
    features = np.r_[prefix, np.log1p(numbers) / math.log1p(PUBLIC_CAP)].astype(np.float32)
    if features.shape != (FEATURE_DIM,) or not np.all(np.isfinite(features)):
        raise ValueError("Invalid observable feature vector")
    return features


def uniform_legal(state):
    mask = np.asarray(validate_state(state)["action_mask"], dtype=float)
    return mask / mask.sum()


def validate_weights(weights, state):
    state = validate_state(state)
    weights = np.asarray(weights, dtype=float)
    if weights.shape != (ACTION_DIM,) or not np.all(np.isfinite(weights)) or np.any(weights < 0):
        raise ValueError("Expected ten finite nonnegative action weights")
    if abs(float(weights.sum()) - 1.) > 1e-7 or np.any(weights[np.asarray(state["action_mask"]) == 0] != 0):
        raise ValueError("Weights violate normalization or action availability")
    return weights / weights.sum()


def quantize_percent(weights, state):
    weights = validate_weights(weights, state)
    scaled = weights * 100
    result = np.floor(scaled).astype(int)
    remaining = 100 - int(result.sum())
    legal = [i for i, allowed in enumerate(state["action_mask"]) if allowed]
    order = sorted(legal, key=lambda i: (-(scaled[i] - result[i]), i))
    if not 0 <= remaining <= len(order):
        raise FloatingPointError("Invalid largest-remainder residual")
    for index in order[:remaining]:
        result[index] += 1
    return result.tolist()


def parse_percent(text, state):
    """Invalid outputs get exact uniform legal weights, never teacher fallback."""
    state = validate_state(state)
    try:
        percentages = json.loads(text)
        if not isinstance(percentages, list) or len(percentages) != ACTION_DIM:
            raise ValueError("Expected a JSON array of length ten")
        if any(type(x) is not int or not 0 <= x <= 100 for x in percentages) or sum(percentages) != 100:
            raise ValueError("Expected integer percentages summing to 100")
        if any(value and not legal for value, legal in zip(percentages, state["action_mask"])):
            raise ValueError("Positive percentage for unavailable/padded action")
        return {"weights": [x / 100 for x in percentages], "percent": percentages, "valid": True, "error": None}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"weights": uniform_legal(state).tolist(), "percent": None, "valid": False,
                "error": type(exc).__name__ + ": " + str(exc)}


class _ReferenceLength:
    def __init__(self, count):
        self.count = count

    def __len__(self):
        return self.count

    def __iter__(self):
        raise AssertionError("Frozen allocation teacher must not inspect calibration bits")


def teacher_target(state):
    """Run the literal frozen allocation update from legal observable counts."""
    state = validate_state(state)
    public = {"d": state["d"], "groups": [{"targets": group} for group in state["groups"]],
              "rate_domain": {"eta": state["eta"]}, "type_accuracy": state["known_s"]}
    calibration = {key: _ReferenceLength(state["calibration"][key]["total"]) for key in ("high", "low")}
    teacher = TheoryAlignedTracking(public, calibration, state["R"])
    teacher.t = state["online"]
    teacher.counts[:] = state["counts"]
    teacher.forced[:] = state["forced_counts"]
    teacher.types = [[0] * pair[0] + [1] * pair[1] for pair in state["type_report_counts"]]
    teacher._update()
    weights = np.zeros(ACTION_DIM)
    weights[:teacher.E] = teacher.weights
    return {"weights": validate_weights(weights, state).tolist(), "percent": quantize_percent(weights, state),
            "estimate": deepcopy(teacher.last_estimate), "teacher_K": teacher.last_estimate["estimated_K"]}


def messages_for(state, percentages=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": serialize_state(state)}]
    if percentages is not None:
        parsed = parse_percent(json.dumps(percentages), state)
        if not parsed["valid"]:
            raise ValueError("Invalid supervised percentage label")
        messages.append({"role": "assistant", "content": json.dumps(percentages, separators=(",", ":"))})
    return messages


class CommonScheduler(TheoryAlignedTracking):
    """Frozen square exploration/tracking, externally supplied block targets."""
    def __init__(self, public, calibration, R, online_cap=PUBLIC_CAP, block_size=BLOCK_SIZE):
        super().__init__(public, calibration, R)
        if self.d != 4 or block_size != BLOCK_SIZE:
            raise ValueError("Frozen T1 scheduler requires d=4 and block size128")
        self.online_cap = _integer(online_cap, "online cap", 1)
        self.block_size = block_size
        self._state_public = {"d": self.d, "groups": [{"targets": list(group)} for group in self.groups],
                              "rate_domain": {"eta": self.eta}, "type_accuracy": self.type_accuracy}
        self._state_calibration = {key: list(calibration[key]) for key in ("high", "low")}
        self.next_update = math.inf
        self._target_updated_at = None
        self.target_history = []

    def _update(self):
        raise RuntimeError("CommonScheduler targets must be supplied externally")

    def needs_update(self):
        return self.t >= self.L and (self.t - self.L) % self.block_size == 0 and self._target_updated_at != self.t

    def state(self):
        reports = [[len(group) - sum(group), sum(group)] for group in self.types]
        return build_state(self._state_public, self._state_calibration, self.counts, self.forced,
                           reports, self.planning_R, self.online_cap)

    def next(self, active):
        if self.t >= self.online_cap:
            raise RuntimeError("Public acquisition limit reached")
        if self.needs_update():
            raise RuntimeError("A new target is required at this block boundary")
        return super().next(active)

    def set_target(self, weights):
        if self._pending is not None or not self.needs_update():
            raise RuntimeError("Install one target only at the declared predecision block boundary")
        values = validate_weights(weights, self.state())
        self.weights = values[:self.E].copy()
        self._target_updated_at = self.t
        self.target_history.append({"online": self.t, "weights": values.tolist()})


FrozenAligned = TheoryAlignedTracking
