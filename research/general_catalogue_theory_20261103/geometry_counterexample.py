#!/usr/bin/env python3
"""Bounded arithmetic checks for ADVERSARIAL_GEOMETRY.md; no external calls."""
from __future__ import annotations

import math
import random
from decimal import Decimal, localcontext


def entropy(x: float) -> float:
    if x == 0.0 or x == 1.0:
        return 0.0
    return -x * math.log(x) - (1.0 - x) * math.log1p(-x)


def psi(p: float, s: float) -> float:
    return entropy(max(0.5, p - (2 * p - 1) * s)) - entropy(p)


def split_information(p: float, ws: list[float], ts: list[float], a: set[int]) -> float:
    total = 0.0
    for block in (a, set(range(len(ws))) - a):
        mass = math.fsum(ws[g] for g in block)
        flips = math.fsum(ts[g] for g in block)
        if mass:
            total += mass * psi(p, flips / mass)
    return total


def information(p: float, ws: list[float], ts: list[float]) -> tuple[float, float]:
    groups = range(len(ws))
    exhaustive = min(
        split_information(p, ws, ts, {g for g in groups if bits & (1 << g)})
        for bits in range(1 << len(ws))
    )
    ordered = sorted(groups, key=lambda g: ts[g] / ws[g])
    prefix = min(
        split_information(p, ws, ts, set(ordered[:cut]))
        for cut in range(len(ws) + 1)
    )
    return exhaustive, prefix


def crossing(k: int) -> float:
    with localcontext() as context:
        context.prec = 80
        two = Decimal(2)

        def j_of_e(e: Decimal) -> Decimal:
            x = (1 + e) / 2
            return two.ln() + x * x.ln() + (1 - x) * (1 - x).ln()

        a = 1 - two / k
        lo, hi = Decimal("0.0001"), Decimal("0.9999999999999999")
        for _ in range(250):
            mid = (lo + hi) / 2
            if j_of_e(mid) - 2 * j_of_e(a * mid) < 0:
                lo = mid
            else:
                hi = mid
        return float((1 + (lo + hi) / 2) / 2)


def main() -> None:
    # Exhaust all two-cluster assignments on 300 deterministic grouped fixtures.
    rng = random.Random(20261103)
    worst = 0.0
    for count in range(1, 7):
        for _ in range(50):
            raw = [rng.random() + 0.01 for _ in range(count)]
            norm = math.fsum(raw)
            ws = [x / norm for x in raw]
            ts = [w * rng.random() for w in ws]
            full, ordered = information(0.5 + 0.49 * rng.random(), ws, ts)
            worst = max(worst, abs(full - ordered))
    assert worst < 2e-14
    print(f"prefix-versus-exhaustive: 300 fixtures, max absolute error {worst:.3g}")

    p = 0.75
    b = math.log(2) - entropy(p)
    assert 2**40 * 3**6 < 11**11 * 5**5
    assert 2**20 > 7**7
    assert psi(p, 1 / 8) < b / 2
    assert psi(p, 1 / 8) > psi(p, 1 / 4) / 2
    print(f"p=.75: B/2={b/2:.16f}, psi(1/8)={psi(p,1/8):.16f}")
    print(f"short-row information={psi(p,1/4)/2:.16f}")

    # The three-column example has balanced tight pairs and losing slack rows.
    pairs = [(1 / 2, 1 / 6), (1 / 2, 1 / 6)]
    pair_info, _ = information(p, [x[0] for x in pairs], [x[1] for x in pairs])
    row_info, _ = information(p, [1 / 2, 1 / 2], [1 / 2, 0])
    assert math.isclose(pair_info, psi(p, 1 / 3), abs_tol=1e-14)
    assert math.isclose(row_info, b / 2, abs_tol=1e-14)
    assert row_info < pair_info
    print(f"k=3: tight-pair information={pair_info:.16f}, slack-row={row_info:.16f}")

    for k in range(3, 11):
        low = 4 / k * (1 - 1 / k)
        high = entropy(1 / k) / math.log(2)
        if low < 0.5 < high:
            p_star = crossing(k)
            print(f"k={k}: unique p_star={p_star:.15f}; limits {low:.15f}, {high:.15f}")
        else:
            behavior = "equality throughout" if high <= 0.5 else "strict inequality throughout"
            print(f"k={k}: {behavior}; limits {low:.15f}, {high:.15f}")


if __name__ == "__main__":
    main()
