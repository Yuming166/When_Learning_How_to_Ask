"""Independent deterministic CertifiedStopping checks, without worlds or RNGs.

The reference logarithm uses exact Fraction series with a proven remainder;
it does not use Decimal.ln, binary logarithms, or precision agreement. A
supporting-gradient certificate verifies the analytic MLE on the full triangle.
"""

from decimal import Decimal, ROUND_UP, localcontext
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json
import sys
import time


PHASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PHASE))
from phase2d import certified as gate  # noqa: E402


HALF, ONE = Fraction(1, 2), Fraction(1)


@lru_cache(maxsize=None)
def reduced_log_bounds(value, terms=140):
    """For 1<=value<=2 use log x=2 atanh((x-1)/(x+1))."""
    assert ONE <= value <= 2
    t = (value - ONE) / (value + ONE)
    if not t:
        return Fraction(0), Fraction(0)
    square, power, partial = t * t, t, Fraction(0)
    for k in range(terms):
        partial += power / (2 * k + 1)
        power *= square
    # All omitted terms are positive; their denominators are >=2N+1.
    remainder = 2 * power / ((2 * terms + 1) * (ONE - square))
    return 2 * partial, 2 * partial + remainder


@lru_cache(maxsize=None)
def rational_log_bounds(value):
    """Exact range reduction, then an exact rational enclosing interval."""
    value = Fraction(value)
    assert value > 0
    shift = 0
    while value < 1:
        value *= 2
        shift -= 1
    while value >= 2:
        value /= 2
        shift += 1
    lo, hi = reduced_log_bounds(value)
    a, b = reduced_log_bounds(Fraction(2))
    if shift >= 0:
        return lo + shift * a, hi + shift * b
    return lo + shift * b, hi + shift * a


def rational_weighted_log_bounds(terms):
    lower, upper = Fraction(0), Fraction(0)
    for weight, value in terms:
        if weight:
            lo, hi = rational_log_bounds(value)
            lower += weight * lo
            upper += weight * hi
    return lower, upper


def assert_contains(decimal_lower, decimal_upper, exact_bounds):
    lower = Fraction(Decimal(decimal_lower))
    upper = Fraction(Decimal(decimal_upper))
    assert lower <= exact_bounds[0] <= exact_bounds[1] <= upper


def assert_supporting_gradient(a, n, b, m, eta, p, q):
    upper = ONE - eta
    assert HALF <= q <= p <= upper
    gradient_p = (a - n * p) / (p * (ONE - p))
    gradient_q = (b - m * q) / (q * (ONE - q))
    for x, y in ((HALF, HALF), (upper, HALF), (upper, upper)):
        assert gradient_p * (x - p) + gradient_q * (y - q) <= 0


def mle_kkt_checks():
    checked = 0
    for eta in (Fraction(1, 8), Fraction.from_float(.05), Fraction(49, 100)):
        for n, m in product(range(7), repeat=2):
            for a, b in product(range(n + 1), range(m + 1)):
                p, q = gate._ordered_mle(a, n, b, m, eta)
                assert_supporting_gradient(a, n, b, m, eta, p, q)
                checked += 1
    return checked


def log_enclosure_checks():
    values = (Fraction(1), HALF, Fraction(7, 8), Fraction(1, 8),
              ONE - Fraction.from_float(.05), Fraction.from_float(.05),
              Fraction(2), Fraction(1_000_000_000_153), Fraction(7, 13))
    checked = 0
    for precision in (16, 50, 80):
        interval = gate._Intervals(precision)
        for value in values:
            lo, hi = interval.log(value)
            assert_contains(lo, hi, rational_log_bounds(value))
            checked += 1
    return checked


def independently_aggregate_profiles(counts, membership, calibration, reports, accuracy, eta):
    """Reconstruct likelihoods directly from each observed stream's probabilities."""
    result = {}
    dimension = len(counts)
    for theta in product((0, 1), repeat=dimension):
        lower, upper = None, None
        for z in product((0, 1), repeat=len(reports)):
            n = [len(calibration['high']), len(calibration['low'])]
            a = [sum(calibration['high']), sum(calibration['low'])]
            for j, row in enumerate(counts):
                for fmt, stream in enumerate(row):
                    channel = int(fmt != z[membership[j]])
                    n[channel] += sum(stream)
                    a[channel] += stream[theta[j]]
            p, q = gate._ordered_mle(a[0], n[0], a[1], n[1], eta)
            assert_supporting_gradient(a[0], n[0], a[1], n[1], eta, p, q)
            terms = []
            for channel, key in enumerate(('high', 'low')):
                rate = (p, q)[channel]
                terms.extend((1, rate if bit else ONE - rate) for bit in calibration[key])
            for j, row in enumerate(counts):
                for fmt, stream in enumerate(row):
                    rate = p if fmt == z[membership[j]] else q
                    for bit, count in enumerate(stream):
                        terms.append((count, rate if bit == theta[j] else ONE - rate))
            for group, answers in enumerate(reports):
                terms.extend((1, accuracy[group] if bit == z[group] else ONE - accuracy[group])
                             for bit in answers)
            lo, hi = rational_weighted_log_bounds(terms)
            lower = lo if lower is None else max(lower, lo)
            upper = hi if upper is None else max(upper, hi)
        result[theta] = lower, upper
    return result


def profile_and_boundary_checks():
    fixtures = [
        ([[[0, 0], [0, 0]]], [0], [], [], [[]], [Fraction(3, 4)], 1),
        ([[[0, 200], [0, 0]]], [0], [], [], [[]], [Fraction(3, 4)], 3),
        ([[[7, 3], [2, 6]], [[0, 9], [8, 1]]], [0, 0],
         [1, 1, 0], [0, 1, 0], [[1, 0, 1]], [Fraction.from_float(.8)], 4),
        ([[[4, 0], [1, 5]], [[1, 6], [7, 0]]], [0, 1],
         [1, 0], [0, 1], [[0, 0, 1], [1]], [Fraction(3, 4), Fraction(7, 8)], 2),
        ([[[j, j + 1], [4 - j, j % 2]] for j in range(4)], [0, 1, 2, 3],
         [1], [0], [[0], [], [1, 0], [1]], [Fraction(3, 4)] * 4, 1),
    ]
    checked_profiles = 0
    for counts, membership, high, low, reports, accuracy, risk in fixtures:
        calibration = {'high': high, 'low': low}
        eta = Fraction.from_float(.05)
        expected = independently_aggregate_profiles(counts, membership, calibration,
                                                    reports, accuracy, eta)
        result = gate.certify_stop(counts, membership, calibration, reports, accuracy,
                                   R=risk, eta=eta, precisions=(50,), include_profiles=True)
        assert result['joint_candidates'] == 2 ** (len(counts) + len(reports))
        for profile in result['profiles']:
            assert_contains(profile['loglik_lower'], profile['loglik_upper'],
                            expected[tuple(profile['theta'])])
            checked_profiles += 1
        candidate = tuple(result['candidate_theta'])
        wrong_bounds = [value for theta, value in expected.items() if theta != candidate]
        wrong = max(a for a, _ in wrong_bounds), max(b for _, b in wrong_bounds)
        assert_contains(result['wrong_loglik_lower'], result['wrong_loglik_upper'], wrong)
        gap = expected[candidate][0] - wrong[1], expected[candidate][1] - wrong[0]
        assert_contains(result['gap_lower'], result['gap_upper'], gap)
        boundary_terms = [(2, Fraction(len(high) + 1))]
        boundary_terms += [(1, Fraction(sum(stream) + 1)) for row in counts for stream in row]
        boundary_terms += [(1, Fraction(len(answers) + 1)) for answers in reports]
        beta = rational_weighted_log_bounds(boundary_terms)
        beta = beta[0] + risk, beta[1] + risk
        assert_contains(result['beta_lower'], result['beta_upper'], beta)
        if result['certified']:
            assert gap[0] > beta[1]
    return {'fixtures': len(fixtures), 'sign_profiles': checked_profiles}


def old_false_crossing_check():
    n = 1_000_000_000_152
    risk = 559615787992.8533
    result = gate.certify_stop([[[0, n], [0, 0]]], [[0]], R=risk,
                               eta=Fraction(1, 8), precisions=(50,))
    gap = rational_log_bounds(Fraction(7, 4))
    beta = rational_log_bounds(Fraction(n + 1))
    exact_risk = Fraction.from_float(risk)
    residual = n * gap[0] - exact_risk - beta[1], n * gap[1] - exact_risk - beta[0]
    assert residual[1] < 0
    assert not result['certified'] and result['status'] == 'rejected'
    return {'n': n, 'R_exact_binary': str(exact_risk), 'status': result['status'],
            'rational_remainder_proves_negative_residual': True}


def selection_context_and_input_checks():
    kwargs = dict(counts=[[[0, 200], [0, 0]]], groups=[[0]], R=3,
                  eta=Fraction(1, 8), precisions=(50,))
    right = gate.certify_stop(**kwargs, candidate_theta=[1])
    wrong = gate.certify_stop(**kwargs, candidate_theta=[0])
    assert right['certified'] and not wrong['certified']
    with localcontext() as ambient:
        ambient.prec = 2
        ambient.rounding = ROUND_UP
        ambient.Emax = 9
        ambient.Emin = -9
        perturbed = gate.certify_stop(**kwargs, candidate_theta=[1])
    for key in ('gap_lower', 'gap_upper', 'beta_lower', 'beta_upper', 'status'):
        assert right[key] == perturbed[key]
    invalid = [
        dict(counts=[[[0, 1.0], [0, 0]]]),
        dict(counts=[[[0, True], [0, 0]]]),
        dict(counts=[[[0, -1], [0, 0]]]),
        dict(counts=[[[0, 2**50 + 1], [0, 0]]]),
        dict(counts=[[[0, 0], [0, 0]]] * 5, groups=[list(range(5))]),
        dict(groups=[[0], [0]]), dict(groups=[]),
        dict(calibration={'high': [1], 'low': []}),
        dict(type_answers=[[0]], type_accuracy=None),
        dict(type_accuracy=[1]), dict(type_accuracy=[Fraction(1, 2)]),
        dict(R=0), dict(R=float('nan')), dict(R=float('inf')),
        dict(eta=0), dict(eta=Fraction(1, 2)), dict(eta=Fraction(1, 2**4097)),
        dict(candidate_theta=[2]), dict(candidate_theta=[]),
        dict(precisions=(10,)), dict(precisions=(80, 50)),
    ]
    for changes in invalid:
        case = dict(kwargs)
        case.update(changes)
        try:
            gate.certify_stop(**case)
        except ValueError:
            pass
        else:
            raise AssertionError(f'malformed case did not reject: {changes}')
    return {'candidate_checks': 2, 'ambient_context_invariance': True,
            'malformed_inputs_rejected': len(invalid)}


def overlap_and_failure_checks():
    # This is a deterministic numerical boundary construction, not a sampled
    # experiment or evidence for a risk guarantee with data-chosen R.
    n = 200
    gap = rational_log_bounds(Fraction(7, 4))
    correction = rational_log_bounds(Fraction(n + 1))
    threshold_lower = n * gap[0] - correction[1]
    scale = 10**40
    risk = Fraction((threshold_lower * scale).numerator
                    // (threshold_lower * scale).denominator, scale)
    assert risk < threshold_lower
    kwargs = dict(counts=[[[0, n], [0, 0]]], groups=[[0]], R=risk,
                  eta=Fraction(1, 8))
    overlap = gate.certify_stop(**kwargs, precisions=(16,))
    assert not overlap['certified'] and overlap['status'] == 'undetermined'
    refined = gate.certify_stop(**kwargs, precisions=(16, 80))
    assert refined['certified'] and len(refined['precision_attempts']) == 2
    original_log = gate._Intervals.log

    def fail_second_precision(self, value):
        if self.down.prec == 80:
            raise ArithmeticError('deterministic injected arithmetic failure')
        return original_log(self, value)

    try:
        gate._Intervals.log = fail_second_precision
        failure = gate.certify_stop(**kwargs, precisions=(16, 80))
    finally:
        gate._Intervals.log = original_log
    assert failure['reason'] == 'arithmetic_failure'
    assert failure['status'] == 'undetermined' and not failure['certified']
    assert failure['theta'] is None and failure['gap_lower'] is None
    return {'precision_limit_returns_undetermined': True,
            'refinement_accepts_rationally_proven_positive_residual': True,
            'arithmetic_failure_discards_prior_endpoints': True}


def main():
    start = time.perf_counter()
    result = {
        'exact_rational_mle_supporting_gradient_checks': mle_kkt_checks(),
        'rational_series_log_enclosure_checks': log_enclosure_checks(),
        'profile_and_boundary_checks': profile_and_boundary_checks(),
        'old_false_crossing': old_false_crossing_check(),
        'selection_context_and_input_checks': selection_context_and_input_checks(),
        'overlap_and_failure_checks': overlap_and_failure_checks(),
        'certificate_source_sha256': hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest(),
        'episodes': 0, 'random_seeds': 0, 'online_actions': 0,
        'offline_observations_acquired': 0, 'model_calls': 0,
    }
    result['wall_seconds'] = time.perf_counter() - start
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
