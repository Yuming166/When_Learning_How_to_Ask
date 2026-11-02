#!/usr/bin/env python3
"""CPU-only evaluations of the paper's equations; no model or network calls."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize, minimize_scalar

ROOT = Path(__file__).resolve().parent
P, Q, D, ETA = 0.85, 0.60, 16, 0.05
GROUP_SIZES = (1, 2, 4, 8, 16)


def kl(r: float, x: float) -> float:
    return r * math.log(r / x) + (1 - r) * math.log((1 - r) / (1 - x))


def f(k: int, p: float, u: float) -> float:
    return kl(p, 1 - u) + (k - 1) * kl(p, u)


def oracle_pair(a: float, alpha: float) -> tuple[float, float]:
    u = max(0.5, (alpha * P + a * (1 + (D - 2) * P)) / (alpha + D * a))
    if u >= Q:
        return u, Q
    u = max(0.5, (alpha * (P + Q) + a * (1 + (D - 2) * P)) / (2 * alpha + D * a))
    return u, u


def oracle_value(a: float, alpha: float) -> float:
    u, v = oracle_pair(a, alpha)
    return alpha * (kl(P, u) + kl(Q, v)) + a * f(D, P, u)


def a_star(alpha: float) -> float:
    lo, hi = 0.0, 1.0
    while oracle_value(hi, alpha) < 1:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if oracle_value(mid, alpha) < 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def gamma(k: int, alpha: float, a: float) -> float:
    v = max(0.5, (alpha * Q + a * (1 + (k - 2) * P)) / (alpha + k * a))
    return alpha * kl(Q, v) + a * f(k, P, v)


def check_equations() -> dict:
    """Independent convex minimizations check the closed-form substitutions."""
    oracle_errors, gamma_errors, root_errors = [], [], []
    for alpha in (0.0, 0.3, 2.0, 8.0, 20.0):
        a = a_star(alpha)
        root_errors.append(abs(oracle_value(a, alpha) - 1))
        # Different computation: a numerical constrained 2-variable optimizer.
        objective = lambda uv: alpha * (kl(P, uv[0]) + kl(Q, uv[1])) + a * f(D, P, uv[0])
        fit = minimize(
            objective, x0=[0.8, 0.6], method="SLSQP",
            bounds=[(0.5, 1 - ETA), (0.5, 1 - ETA)],
            constraints={"type": "ineq", "fun": lambda uv: uv[0] - uv[1]},
            options={"ftol": 1e-12, "maxiter": 200},
        )
        if not fit.success:
            raise RuntimeError(f"Independent oracle minimization failed: {fit.message}")
        oracle_errors.append(abs(float(fit.fun) - oracle_value(a, alpha)))
        gs = [gamma(k, alpha, a) for k in GROUP_SIZES]
        if any(y < x - 1e-10 for x, y in zip(gs, gs[1:])):
            raise AssertionError("Gamma must be nondecreasing in group size")
        for k in GROUP_SIZES:
            obj = lambda v: alpha * kl(Q, v) + a * f(k, P, v)
            fit1 = minimize_scalar(obj, bounds=(0.5, 1 - ETA), method="bounded",
                                   options={"xatol": 1e-13})
            numerical = min(float(fit1.fun), obj(0.5), obj(1 - ETA))
            gamma_errors.append(abs(numerical - gamma(k, alpha, a)))
    assert max(oracle_errors) < 1e-8
    assert max(gamma_errors) < 1e-8
    assert max(root_errors) < 1e-11
    a0 = a_star(0)
    assert abs(gamma(D, 0, a0) - 1) < 1e-10
    assert all(gamma(k, 0, a0) < 1 for k in GROUP_SIZES if k < D)
    return {
        "kind": "numerical_consistency_checks_not_proofs",
        "independent_oracle_minimizations": len(oracle_errors),
        "independent_gamma_minimizations": len(gamma_errors),
        "max_oracle_minimum_error": max(oracle_errors),
        "max_gamma_minimum_error": max(gamma_errors),
        "max_oracle_equation_residual": max(root_errors),
        "zero_calibration_criterion": "PASS",
        "group_size_monotonicity_on_checked_grid": "PASS",
    }


def main() -> None:
    evidence, figures = ROOT / "evidence", ROOT / "figures"
    evidence.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    checks = check_equations()
    alphas = np.linspace(0, 20, 401)
    rows = []
    for alpha in alphas:
        a = a_star(float(alpha))
        rows.append({"alpha": float(alpha), "a_oracle": a, "K_oracle": D * a,
                     **{f"gamma_k{k}": gamma(k, float(alpha), a) for k in GROUP_SIZES}})
    with (evidence / "boundary_values.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, ax = plt.subplots(figsize=(3.25, 1.85), layout="constrained")
    colors = ("#969696", "#d0822b", "#279189", "#3b70ad", "#574477")
    for k, color in zip(GROUP_SIZES, colors):
        ax.plot(alphas, [row[f"gamma_k{k}"] for row in rows], color=color,
                linewidth=1.5, label=f"$k_{{\\min}}={k}$")
    ax.axhline(1, color="#333333", linestyle="--", linewidth=0.8, zorder=0)
    ax.set(xlabel=r"Calibration per stream $\alpha=M_\delta/\log(1/\delta)$",
           ylabel=r"Boundary statistic $\Gamma_{k_{\min}}$", xlim=(0, 20), ylim=(0.20, 1.85))
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([0.25, 0.75, 1.0, 1.5])
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.02), ncols=3, frameon=False, fontsize=6.8,
              handlelength=1.4, columnspacing=0.8)
    ax.text(9.5, 1.24, "$\\Gamma\\geq1$: oracle equality", fontsize=6.8)
    fig.savefig(figures / "sharing_boundary.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(figures / "sharing_boundary.png", dpi=220)
    plt.close(fig)
    thresholds = {}
    for k in GROUP_SIZES:
        hits = [r["alpha"] for r in rows if r[f"gamma_k{k}"] >= 1 - 1e-10]
        thresholds[str(k)] = {"first_grid_alpha_with_gamma_ge_one": min(hits) if hits else None,
                              "interpretation": "grid diagnostic; not a proved monotonic threshold"}
    result = {"parameters": {"d": D, "p": P, "q": Q, "eta": ETA,
                             "equal_size_partitions": list(GROUP_SIZES),
                             "alpha_range": [0, 20], "alpha_grid_points": len(rows)},
              "checks": checks, "grid_crossings": thresholds,
              "alpha_zero": rows[0], "alpha_twenty": rows[-1],
              "equal_average_group_comparison": {
                  "alpha": 4.0, "partition_1": [8, 8], "partition_2": [1, 15],
                  "gamma_8": gamma(8, 4.0, a_star(4.0)),
                  "gamma_1": gamma(1, 4.0, a_star(4.0)),
                  "interpretation": "same average group size; zero versus positive leading premium"},
              "source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "new_model_calls": 0,
              "claim_limit": "equation evaluations, not observations or empirical method comparison"}
    (evidence / "numerical_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
