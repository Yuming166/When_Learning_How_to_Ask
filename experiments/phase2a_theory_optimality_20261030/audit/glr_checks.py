"""Reproduce bounded independent GLR checks; print all evidence as JSON.

Run from the phase2a directory: python audit/glr_checks.py
No model/API/GPU operations, output-file mutations, or confirmation trials.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import scipy

from phase2a.glr import endpoint_mle, profile_glr

spec = importlib.util.spec_from_file_location("independent_glr_tests", ROOT / "tests/test_glr.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def main():
    began = perf_counter()
    evidence = {
        "scope": "bounded_development_checks_not_delta_correctness_validation",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (ROOT / "phase2a/glr.py", ROOT / "tests/test_glr.py")},
        "independent_checks": [],
        "timing_samples": [],
        "preserved_initial_test_failure": {
            "test": "test_membership_vector_and_sign_flip_equivariance",
            "reason": "overstrict winner-equivariance assertion when multiple signs tie",
            "original_d4_tied_indices": [11, 15],
            "original_tied_log_likelihood": -17.72468971503388,
            "resolution": "compare all permuted profile likelihoods, preserving deterministic lexicographic tie choice",
        },
    }
    for d in (4, 6, 8):
        args = checks.tiny_case(d)
        got = profile_glr(*args)
        scalar = checks.scalar_profiles(*args)
        scipy_profile, residuals, failures = checks.scipy_profiles(*args)
        scalar_error = float(np.max(np.abs(scalar - got["profile_log_likelihoods"])))
        scipy_error = float(np.max(np.abs(scipy_profile - got["profile_log_likelihoods"])))
        evidence["independent_checks"].append({
            "d": d, "G": 2, "joint_states_checked": 2 ** (d + 2),
            "scalar_max_abs_profile_error": scalar_error,
            "scipy_max_abs_profile_error": scipy_error,
            "scipy_max_constraint_violation": max(residuals),
            "scipy_non_success_status_count": len(failures),
            "scipy_non_success_statuses": failures,
        })
        assert scalar_error < 4e-12
        assert scipy_error < 3e-7
        assert max(residuals) < 1e-7
    for d, group_count in ((4, 2), (6, 2), (8, 2), (8, 8)):
        rng = np.random.default_rng(20261030 + d + group_count)
        counts = rng.integers(0, 4, size=(d, 2, 2))
        groups = [list(x) for x in np.array_split(np.arange(d), group_count)]
        timings = [profile_glr(counts, groups)["timings_seconds"]["total"] for _ in range(5)]
        evidence["timing_samples"].append({"purpose": "repeated_small_d_glr", "d": d, "G": group_count,
                                            "joint_states": 2 ** (d + group_count),
                                            "seconds": timings, "median_seconds": float(np.median(timings))})
    counts = np.random.default_rng(1616).integers(0, 4, size=(16, 2, 2))
    result = endpoint_mle(counts, [list(range(8)), list(range(8, 16))])
    warm_results = [endpoint_mle(counts, [list(range(8)), list(range(8, 16))]) for _ in range(5)]
    retained_fields = ("theta", "z", "p_hat", "q_hat", "log_likelihood")
    assert all(all(r[k] == result[k] for k in retained_fields) for r in warm_results)
    linux_status = {line.split(":")[0]: line.split(":")[1].strip()
                    for line in Path("/proc/self/status").read_text().splitlines()
                    if line.startswith(("VmRSS:", "VmHWM:"))}
    evidence["d16_endpoint_only"] = {
        "joint_states": result["joint_candidates"],
        "seconds": result["timings_seconds"]["total"],
        "warm_seconds": [r["timings_seconds"]["total"] for r in warm_results],
        "warm_median_seconds": float(np.median([r["timings_seconds"]["total"] for r in warm_results])),
        "warm_outputs_identical": True,
        "process_peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "linux_process_memory_status": linux_status,
        "no_stopping_fields": all(k not in result for k in ("gap", "beta", "certified")),
        "claim": "one_fixed_budget_endpoint_profile_not_d16_sequential_glr",
        "runtime_limit": "state/operation count bounded; measured host timing is not a guaranteed wall-clock bound",
    }
    # One fixed deterministic fresh-channel seed, small d, round-robin policy.
    # This only exercises actual repeated stopping checks, not a rate claim.
    rng = np.random.default_rng(49304)
    truth = np.array([0, 1, 0, 1])
    true_z = np.array([0, 1])
    counts = np.zeros((4, 2, 2), dtype=np.int64)
    first_crossing = None
    last = None
    for t in range(1, 1025):
        j, fmt = ((t - 1) % 8) // 2, (t - 1) % 2
        rate = .85 if fmt == true_z[j // 2] else .60
        answer = int(truth[j] if rng.random() < rate else 1 - truth[j])
        counts[j, fmt, answer] += 1
        if t % 16 == 0:
            last = profile_glr(counts, [[0, 1], [2, 3]], delta=.05)
            if last["certified"]:
                first_crossing = t
                break
    evidence["single_stopping_smoke_check"] = {
        "seed": 49304, "d": 4, "G": 2, "p": .85, "q": .60, "delta": .05,
        "policy": "round_robin", "check_every": 16, "cap": 1024,
        "first_float64_boundary_crossing": first_crossing,
        "last_gap": last["gap"], "last_beta": last["beta"],
        "last_theta": last["theta"], "truth": truth.tolist(),
        "correct_at_crossing": first_crossing is not None and last["theta"] == truth.tolist(),
        "claim": "one_path_functional_smoke_check_no_error_probability_estimate",
    }
    evidence["elapsed_seconds"] = perf_counter() - began
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
