"""Exact certificate for an explicit five-dimensional depth-mixing region.

No optimizers, model calls, or parameter-grid extrapolation. The 950 cells cover
the entire nuisance interval using a Taylor remainder. All later checks use
rational inequalities and proven analytic perturbation bounds.
"""
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
HELPER = ROOT.parent / 'web_oracle_structure_20261031/certify_depth_mixing.py'
spec = importlib.util.spec_from_file_location('sealed_depth', HELPER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
law, kl, bern, dec = old.law, old.kl, old.bern, old.dec
log_bounds = old.previous.log_bounds


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def display_bound(x):
    """Decimal is only a display; decisions above it use exact fractions."""
    return dec(x)


def run():
    r, p, q, eta = F(3, 5), F(19, 20), F(3, 5), F(1, 40)
    amin, amax, cmin, cmax = F(19, 20), F(6, 5), F(1, 2), F(3, 2)
    eps = F(1, 40000)
    margin_anchor, cal_anchor = F(1, 35), F(103, 200)
    actions = [(a, L-a) for L in range(1, 7) for a in range(L+1)]
    truth = {ab: law(r, p, q, *ab) for ab in actions}

    # Recompute the sealed point certificate without executing its write path.
    radius, curvature = F(1, 4000), F(44800)
    point_margins = []
    for i in range(950):
        u = F(1, 2) + F(2*i+1, 4000)
        low = bern(p, u)[0] + bern(q, min(q, u))[0]
        derivative = (u-p)/(u*(1-u))
        if u < q:
            derivative += (u-q)/(u*(1-u))
        for L, count in [(1, F(14)), (2, F(2))]:
            P, Q = truth[L, 0], law(r, u, u, L, 0, True)
            low += count*kl(P, Q)[0]
            Qprime = old.pure_law_derivative(r, u, L)
            assert sum(Qprime) == 0
            derivative -= count*sum(x*y/z for x, y, z in zip(P, Qprime, Q))
        margin = low-abs(derivative)*radius-curvature*radius**2/2-1
        assert margin > margin_anchor, (i, dec(margin))
        point_margins.append(margin)

    # Convex profiled calibration achieves its maximum at an endpoint.
    C0low = bern(p, F(1, 2))[0] + bern(q, F(1, 2))[0]
    C0high = bern(p, F(1, 2))[1] + bern(q, F(1, 2))[1]
    Cright = bern(p, 1-eta)[1]
    assert Cright < C0low < C0high < cal_anchor
    rectangle_margin = margin_anchor-(1-amin)*cal_anchor
    assert rectangle_margin == F(79, 28000)

    # All logs used in the analytic derivative bounds, verified exactly.
    log_checks = {
        'depth_one_ratio': (F(1209, 791), F(1, 2)),
        'depth_two_ratio': (F(625, 96), F(2)),
        'same_rate_ratio': (F(61, 39), F(1, 2)),
        'p_logit': (F(24), F(16, 5)),
        'max_alternative_logit': (F(39), F(4)),
    }
    for name, (arg, upper) in log_checks.items():
        assert log_bounds(arg)[1] < upper, name
    # D2 endpoints have these lower bounds; the middle controls the log bound.
    P_end_min = F(39, 100)*F(94, 100)**2
    Q_end_min = F(59, 100)*F(39, 100)
    assert 1/P_end_min < F(625, 96) and 1/Q_end_min < F(625, 96)
    assert F(1128, 10000)/F(4875, 100000) < F(625, 96)
    # Feasibility derivatives: r<=70, p<25, q<2 throughout the auxiliary box.
    r_lip = F(14)*4+F(2)*7
    p_lip = F(14)/4+F(2)*8+amax*4
    q_lip = amax
    assert r_lip == 70 and p_lip < 25 and q_lip < 2
    assert r_lip+p_lip+q_lip < 100
    region_margin = rectangle_margin-100*eps
    assert region_margin == F(9, 28000) > 0
    assert F(16, 5)+F(1, 2) < 4  # C0 perturbation <=4*eps.

    # Fixed-depth lower bounds, with every composition retained.
    base_checks, robust_checks = [], []
    for L in range(1, 7):
        u, v = (F(1, 2), F(1, 2)) if L == 1 else (p, q)
        base_y = F(100) if L == 1 else F(413, 10)
        robust_y = F(100) if L == 1 else F(206, 5)
        div_lip = F(2) if L == 1 else F(83, 39)*(L+1)
        for a in range(L+1):
            Dhi = kl(truth[a, L-a], law(r, u, v, a, L-a, True))[1]
            base_slack = 1+L-base_y*Dhi
            robust_slack = 1+L-robust_y*(Dhi+div_lip*eps)
            assert base_slack > 0 and robust_slack > 0, (L, a)
            base_checks.append(dict(action=[a, L-a], slack_lower_display=dec(base_slack)))
            robust_checks.append(dict(action=[a, L-a],
                divergence_perturbation_bound=str(div_lip*eps),
                slack_lower_display=dec(robust_slack)))

    # Costs and gaps are affine in c. Check all interval endpoints, and all L.
    def cost(c):
        return 16*c+18

    def lower(alpha, c, L, y, cal):
        if L == 1:
            return 50*(c+1)*(1-alpha*cal)
        return y*(c+L)/(L+1)

    families = []
    for label, y, cal, gap, saving in [
        ('fixed_rates_rectangle', F(413, 10), cal_anchor, F(9, 4), F(3, 59)),
        ('five_dimensional_box', F(206, 5), cal_anchor+4*eps, F(15, 7), F(5, 103)),
    ]:
        gaps = [lower(amax, c, L, y, cal)-cost(c)
                for c in [cmin, cmax] for L in range(1, 7)]
        assert min(gaps) == gap
        assert gap/(cost(cmax)+gap) == saving
        families.append(dict(name=label, long_depth_multiplier=str(y),
            calibration_upper=str(cal), uniform_additive_gap=str(gap),
            relative_saving_lower=str(saving),
            depth_one_gap_at_worst_endpoint=str(lower(amax, cmin, 1, y, cal)-cost(cmin))))

    result = dict(
        status='PASS_EXACT_CERTIFICATE_WITH_ANALYTIC_PERTURBATION_BOUNDS',
        date='2026-11-01',
        model=dict(d=1, L_max=6, eta=str(eta), ell='1',
                   oracle_knows='format, not extraction rates or truth',
                   objective='pointwise asymptotic expected online cost / log(1/delta)'),
        fixed_rates=dict(r=str(r), p=str(p), q=str(q)),
        intervals=dict(alpha=[str(amin), str(amax)], c_over_ell=[str(cmin), str(cmax)],
                       r=[str(r-eps), str(r+eps)], p=[str(p-eps), str(p+eps)],
                       q=[str(q-eps), str(q+eps)], rate_radius=str(eps)),
        witness=dict(blocks={'1,0':'14', '2,0':'2'}, cost='16*c+18*ell',
                     exact_point_margin_lower=str(margin_anchor),
                     recomputed_point_margin_display=dec(min(point_margins)),
                     profiled_calibration_max_upper=str(cal_anchor),
                     calibration_actual_endpoint_upper_display=dec(C0high),
                     fixed_rates_information_margin_lower=str(rectangle_margin),
                     perturbed_information_margin_lower=str(region_margin)),
        analytic_bounds=dict(auxiliary_box=dict(r=['.59','.61'], p=['.94','.96'], q=['.59','.61']),
            witness_linf_lipschitz='100', same_rate_KL_linf_lipschitz='83*(L+1)/39',
            depth_one_fair_KL_linf_lipschitz='2', calibration_fair_linf_lipschitz='4',
            log_inequalities={k:dict(argument=str(v[0]), upper=str(v[1])) for k,v in log_checks.items()}),
        conclusions=families, fixed_point_dual_checks=base_checks, robust_dual_checks=robust_checks,
        arithmetic=dict(probabilities='exact rational', logarithms='dyadic atanh intervals, 20 terms',
                        nuisance_cells=950, cell_radius=str(radius), curvature_bound=str(curvature),
                        region_check='analytic Lipschitz bounds plus exact affine endpoint inequalities'),
        limitations=['Sufficient region, not maximal phase boundary.',
            'Not a proof of pure-good optimality or of an exactly two-depth optimum.',
            'No uniform finite-delta remainder or empirical Web/LLM claim.'],
        source_sha256=sha(Path(__file__)),
        dependencies={str(HELPER.relative_to(REPO)):sha(HELPER),
                      str(old.DEPENDENCY.relative_to(REPO)):sha(old.DEPENDENCY)})
    (ROOT/'REGION_CERTIFICATE.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cells=950, actions_checked=27,
                         alpha=result['intervals']['alpha'], c_over_ell=result['intervals']['c_over_ell'],
                         information_margin=str(region_margin), conclusions=families), indent=2))


if __name__ == '__main__':
    run()
