"""Independent, bounded, CPU-only audit checks. No benchmark pilot is launched.

Run from the benchmark root: python -B audit/reviewer_checks.py
The shared-filesystem probe is an intentional demonstration of the declared
honest-policy boundary, not an attempt to access unrelated files.
"""
import hashlib
import itertools
import json
import math
import multiprocessing as mp
import socket
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from qrelbench.data import make_episode, public_view, render
from qrelbench.environment import QueryEnvironment
from qrelbench.policies import Strategy, NAMES, certificate
from qrelbench.decoder import decode, rate_estimates
from qrelbench.evaluate import build_jobs, evaluate_job
from qrelbench.rpc import worker, send, receive
from qrelbench.randomness import uniform
from qrelbench.security import confine_worker


def expect_error(fn, exc=(ValueError, RuntimeError, TypeError)):
    try:
        fn()
    except exc:
        return
    raise AssertionError('Expected a rejected operation')


def canonical_truth(record, proposition):
    """Independent predicate implementation, not data.evaluate()."""
    offer = record['offers']
    kind = proposition['predicate']
    if kind == 'stock':
        return int(offer['availability'].rsplit('/', 1)[-1] == 'InStock')
    if kind == 'price':
        return int(float(offer['price']) <= proposition['threshold'])
    if kind == 'shipping':
        return int(float(offer['shippingDetails']['shippingRate']['value']) == 0.0)
    if kind == 'returns':
        return int(offer['hasMerchantReturnPolicy']['merchantReturnDays'] >= proposition['threshold'])
    raise AssertionError('Unexpected kind')


def generation_checks():
    kinds = set()
    all_labels = []
    all_types = []
    unbalanced = 0
    for i in range(200):
        e = make_episode(762104, 'development', i, [4, 12])
        assert len({id(r) for r in e.records}) == 16
        assert len({r['productID'] for r in e.records}) == 16
        assert len({t['id'] for t in e.public['targets']}) == 16
        for r, t, theta in zip(e.records, e.public['targets'], e.truth):
            assert canonical_truth(r, t['proposition']) == theta
            a = t['queries']['A']
            b = t['queries']['B']
            ca = a.removeprefix('Is it true that ').removesuffix('? Answer 1 for true and 0 for false.')
            cb = b.removeprefix('Choose the truth status of this statement: ').removesuffix('. Answer 1 if it holds and 0 if it does not.')
            assert ca == cb
            kinds.add(t['proposition']['predicate'])
        unbalanced += sum(e.truth[:4]) != 2
        all_labels.extend(e.truth)
        all_types.extend(e.types)
    assert kinds == {'stock', 'price', 'shipping', 'returns'}
    assert unbalanced > 60
    assert abs(np.mean(all_labels) - .5) < .04
    assert abs(np.mean(all_types) - .5) < .08
    a = make_episode(762104, 'development', 0, [4, 12])
    assert a == make_episode(762104, 'development', 0, [4, 12])
    b = make_episode(762104, 'development', 0, [8, 8])
    assert a.truth == b.truth and a.records == b.records
    assert a.public['episode_id'] == b.public['episode_id']
    split_ids = {make_episode(762104, split, 0, [16]).public['episode_id'] for split in ['train', 'development', 'test']}
    assert len(split_ids) == 3
    expect_error(lambda: make_episode(0, 'unknown', 0, [16]))
    expect_error(lambda: make_episode(0, 'train', 0, [0, 16]))
    expect_error(lambda: make_episode(0, 'train', 0, [True]))
    return {'episodes': 200, 'independent_predicate_checks': 3200, 'unbalanced_first_groups': unbalanced,
            'truth_mean': float(np.mean(all_labels)), 'type_mean': float(np.mean(all_types))}


def interface_and_integrity_checks():
    e = make_episode(762104, 'development', 5, [1, 15])
    env = QueryEnvironment(e, .85, .6, calibration_size=16, online_cap=2)
    expect_error(lambda: env.query(0, 'A'))
    expect_error(env.score)
    public = env.reset()
    # First execution rejected this newly added, known model-domain field because
    # the reviewer allow-list was stale. It contains bounds, not realized p/q.
    expected = set(e.public) | {'type_accuracy', 'calibration_size_per_stream', 'rate_domain'}
    assert set(public) == expected
    assert public['rate_domain'] == {'eta': .05, 'q_min': .5, 'p_max': .95, 'levels_unknown': True}
    assert 'oracle_format_types' not in public
    assert not set(public) & {'truth', 'types', 'p', 'q', 'key', 'master_seed', 'reward', 'records', 'provenance'}
    public['targets'][0]['proposition']['predicate'] = 'tampered'
    assert e.public['targets'][0]['proposition']['predicate'] != 'tampered'
    expect_error(env.reset)
    expect_error(lambda: env.query(True, 'A'))
    expect_error(lambda: env.query(-1, 'A'))
    expect_error(lambda: env.query(0, 'unknown'))
    expect_error(lambda: env.ask_type(True))
    assert env.cost == {'task': 0, 'type': 0, 'offline': 0}
    cal = env.get_calibration()
    saved = {k: list(v) for k, v in cal.items()}
    cal['high'][0] ^= 1
    assert env.get_calibration() == saved
    assert env.cost['offline'] == 32
    assert set(env.query(0, 'A')) == {'answer'}
    assert set(env.ask_type(0)) == {'format'}
    expect_error(lambda: env.query(0, 'A'))
    assert env.cost == {'task': 1, 'type': 1, 'offline': 32}
    expect_error(lambda: env.submit([0] * 15))
    expect_error(lambda: env.submit([False] * 16))
    assert env.submit([0] * 16) == {'submitted': True}
    score = env.score()
    assert score['online'] == 2 and score['total_acquisition'] == 34
    expect_error(lambda: env.query(0, 'B'))
    expect_error(lambda: env.ask_type(0))
    expect_error(env.get_calibration)
    expect_error(lambda: env.submit([0] * 16))
    oracle = QueryEnvironment(e, .85, .6, calibration_size=16, online_cap=2, oracle=True)
    ov = oracle.reset()
    assert set(ov) == expected | {'oracle_format_types'}
    assert oracle.get_calibration() == saved
    return {'online_cap_counts_task_and_type': True, 'offline_charged_once': True,
            'submit_returns_no_reward': True, 'oracle_public_addition': 'format types only'}


def channel_checks():
    e = make_episode(762104, 'development', 6, [16])
    n = 3000
    env = QueryEnvironment(e, .85, .6, calibration_size=8000, online_cap=25000)
    env.reset()
    cal = env.get_calibration()
    assert abs(np.mean(cal['high']) - .85) < .025
    assert abs(np.mean(cal['low']) - .6) < .025
    js = [e.truth.index(0), e.truth.index(1)]
    series = []
    rates = []
    for j in js:
        for m in ['A', 'B']:
            r = .85 if 'AB'.index(m) == e.types[0] else .6
            x = np.array([env.query(j, m)['answer'] == e.truth[j] for _ in range(n)], dtype=float)
            empirical = float(np.mean(x))
            lagcov = float(np.mean((x[:-1] - r) * (x[1:] - r)))
            assert abs(empirical - r) < .04
            assert abs(lagcov) < .025
            series.append((x, r))
            rates.append({'label': e.truth[j], 'format': m, 'specified': r, 'empirical': empirical, 'lag_covariance': lagcov})
    for (x, rx), (y, ry) in itertools.combinations(series, 2):
        assert abs(float(np.mean((x-rx)*(y-ry)))) < .025
    tx = np.array([env.ask_type(0)['format'] == 'AB'[e.types[0]] for _ in range(n)])
    assert abs(np.mean(tx) - .8) < .04
    replay = QueryEnvironment(e, .85, .6, calibration_size=8000, online_cap=3)
    replay.reset()
    assert replay.get_calibration() == cal
    j = js[0]
    assert replay.query(j, 'A')['answer'] == int(e.truth[j] if series[0][0][0] else 1-e.truth[j])
    persistent = QueryEnvironment(e, .85, .6, online_cap=100, control='persistent')
    persistent.reset()
    for j in js:
        for m in ['A', 'B']:
            assert len({persistent.query(j, m)['answer'] for _ in range(20)}) == 1
    asymmetric = QueryEnvironment(e, .85, .6, online_cap=4*n, control='label_asymmetric')
    asymmetric.reset()
    arates = []
    for j in js:
        for m in ['A', 'B']:
            r = .85 if 'AB'.index(m) == e.types[0] else .6
            if e.truth[j] == 0:
                r = 1-r
            rate = float(np.mean([asymmetric.query(j, m)['answer'] == e.truth[j] for _ in range(n)]))
            assert abs(rate-r) < .04
            arates.append({'label': e.truth[j], 'format': m, 'specified_correctness': r, 'empirical': rate})
    perfect = QueryEnvironment(e, .85, .6, online_cap=20, type_accuracy=1.)
    perfect.reset()
    assert all(perfect.ask_type(0)['format'] == 'AB'[e.types[0]] for _ in range(20))
    chance = QueryEnvironment(e, .5, .5, online_cap=n)
    chance.reset()
    cr = float(np.mean([chance.query(0, 'A')['answer'] == e.truth[0] for _ in range(n)]))
    assert abs(cr-.5) < .04
    return {'iid_task_draws': 4*n, 'type_draws': n, 'offline_draws': 16000,
            'stream_checks': rates, 'asymmetric_stream_checks': arates,
            'chance_correctness': cr, 'persistent_repetitions_constant': True,
            'scope': 'finite-sample sanity checks; not proof of statistical independence'}


def policies_checks():
    e = make_episode(762104, 'development', 7, [16])
    public = QueryEnvironment(e, .85, .6).reset()
    s = Strategy('Repeat-and-Compare', public)
    # A has 8 agreements/10 pairs; B has 2/2. Raw totals prefer A; rates prefer B.
    s.agree[0] = [8, 2]
    if not hasattr(s, 'pairs'):
        raise AssertionError('Raw agreement defect: missing pair denominator')
    s.pairs[0] = [10, 2]
    assert s.estimate_format(0) == 'B'
    assert certificate(0, 0, 16, .1) is None
    assert certificate(300, 300, 16, .1) == 1
    assert certificate(-300, 300, 16, .1) == 0
    counts = np.array([[[5,1],[1,2]], [[2,0],[0,4]], [[1,2],[5,2]]])
    cal = {'high': [1]*84+[0]*14, 'low': [1]*59+[0]*39}
    pub = {'d': 3, 'groups': [{'targets': [0,1,2]}], 'type_accuracy': [.8]}
    prediction = decode(pub, counts, cal, [[]])
    p, q = rate_estimates(cal)
    vals = []
    for theta in itertools.product([0, 1], repeat=3):
        zll = []
        for z in [0,1]:
            ll = 0.
            for j, t in enumerate(theta):
                for m in [0,1]:
                    r = p if m == z else q
                    ll += int(counts[j,m,t])*math.log(r)+int(counts[j,m,1-t])*math.log1p(-r)
            zll.append(ll)
        vals.append((float(np.logaddexp(*zll)), theta))
    best = max(vals)
    chosen = next(v for v in vals if list(v[1]) == prediction)
    assert list(best[1]) == [1, 1, 0]
    assert best[0] - chosen[0] < 1e-10
    return {'normalized_agreement_regression': 'pass', 'decoder_prediction': prediction,
            'joint_MAP_prediction': list(best[1]), 'joint_MAP_log_advantage': best[0]-chosen[0],
            'decoder_marginal_not_joint_MAP': best[0] > chosen[0]+1e-9}


def spawn_runner_checks():
    ctx = mp.get_context('spawn')
    outcomes = []
    for policy in NAMES:
        parent, child = ctx.Pipe()
        process = ctx.Process(target=worker, args=(child, policy))
        process.start()
        child.close()
        try:
            for protocol in ['fixed_budget', 'fixed_confidence']:
                job = {'protocol': protocol, 'scenario': 'reviewer_smoke', 'partition': [1,15],
                       'index': 170005, 'online_cap': 24, 'calibration_size': 8,
                       'delta': .1 if protocol == 'fixed_confidence' else None,
                       'p': .85, 'q': .6, 's': .8, 'channel': 'iid'}
                result, private = evaluate_job(parent, policy, job, 762104, time.monotonic()+12)
                assert result['online'] == 24
                assert result['costs']['offline'] == 16
                assert result['completed'] == (protocol == 'fixed_budget')
                assert result['censored'] == (protocol == 'fixed_confidence')
                assert len(private['truth']) == 16
                outcomes.append({'policy': policy, 'protocol': protocol, 'online': result['online'],
                                 'censored': result['censored']})
            send(parent, None)
            process.join(5)
            assert process.exitcode == 0
        finally:
            if process.is_alive():
                process.terminate()
                process.join(5)
            parent.close()
    return {'spawned_workers': len(NAMES), 'episodes': outcomes}


def configuration_checks():
    cfg = json.loads((ROOT/'configs/development.json').read_text())
    jobs = build_jobs(cfg)
    planned = len(NAMES)*sum(j['online_cap'] for j in jobs)
    assert planned <= cfg['limits']['maximum_online_actions']
    assert all(j['index'] >= cfg['split_ranges']['development'][0] for j in jobs)
    assert all(j['index'] <= cfg['split_ranges']['development'][1] for j in jobs)
    assert {tuple(p) for p in cfg['partitions']} == {(1,15),(2,14),(4,12),(8,8),(16,)}
    scenarios = {j['scenario'] for j in jobs}
    assert scenarios >= {'base','equal_informative','equal_chance','no_sharing','perfect_type','persistent','label_asymmetric'}
    assert cfg['confirmation_authorized'] is False and cfg['llm_calls_authorized'] is False
    assert cfg['master_seed'] is None
    assert 'sealed' in cfg['seed_source']
    return {'planned_pilot_episodes': len(jobs)*len(NAMES), 'planned_pilot_maximum_online_actions': planned,
            'executed_main_pilot': False, 'negative_controls': sorted(scenarios)}


def randomness_boundary_check():
    # The initial int64/2**64 implementation returned exactly 1.0 here due to
    # float rounding. That makes a purported perfect s=1 type report wrong.
    with patch('qrelbench.randomness.derive', return_value=b'\xff'*32):
        upper = uniform(b'boundary_probe', 'boundary_probe')
    assert 0 <= upper < 1, 'Uniform endpoint rounding violates perfect-type control'
    with patch('qrelbench.randomness.derive', return_value=b'\x00'*32):
        lower = uniform(b'boundary_probe', 'boundary_probe')
    assert lower == 0
    return {'maximum_uniform': upper, 'minimum_uniform': lower, 'half_open_interval': True}


def shared_filesystem_probe(conn):
    """Receives only a public episode, then demonstrates same-UID file access."""
    view = receive(conn)
    cfg = json.loads((ROOT/'configs/development.json').read_text())
    if cfg['master_seed'] is None:
        send(conn, {'config_seed_readable': True, 'public_config_has_no_usable_seed': True,
                    'reconstructed_truth': None})
        conn.close()
        return
    lo, _ = cfg['split_ranges']['development']
    partition = [len(g['targets']) for g in view['groups']]
    for index in range(lo, lo+8):
        e = make_episode(cfg['master_seed'], 'development', index, partition)
        if e.public['episode_id'] == view['episode_id']:
            send(conn, {'reconstructed_truth': e.truth, 'candidates_examined': index-lo+1,
                        'config_seed_readable': True})
            conn.close()
            return
    send(conn, {'config_seed_readable': True, 'reconstructed_truth': None})
    conn.close()


def isolation_limit_check():
    cfg = json.loads((ROOT/'configs/development.json').read_text())
    lo, _ = cfg['split_ranges']['development']
    e = make_episode('reviewer-private-test-fixture', 'development', lo+3, [1,15])
    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe()
    process = ctx.Process(target=shared_filesystem_probe, args=(child,))
    process.start()
    child.close()
    try:
        send(parent, public_view(e))
        assert parent.poll(12)
        result = receive(parent)
        process.join(5)
        assert process.exitcode == 0
        assert result['reconstructed_truth'] is None
        assert result['public_config_has_no_usable_seed']
        return {'config_seed_readable_in_spawned_child': True,
                'public_config_has_no_usable_seed': True,
                'private_truth_reconstructed_from_public_episode_and_shared_config': False,
                'disposition': 'sealed seed corrects the original public-config-seed attack'}
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
        parent.close()


def confined_attack_probe(conn):
    isolation = confine_worker()
    view = receive(conn)
    denied = {}
    for name, path in [('config', ROOT/'configs/development.json'), ('implementation', ROOT/'qrelbench/data.py')]:
        try:
            path.read_bytes()
        except PermissionError:
            denied[name] = True
        else:
            denied[name] = False
    network_denied = {}
    for name in ['bind', 'connect']:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if name == 'bind':
                sock.bind(('127.0.0.1', 0))
            else:
                sock.connect(('127.0.0.1', 9))
        except PermissionError:
            network_denied[name] = True
        except OSError:
            network_denied[name] = False
        else:
            network_denied[name] = False
        finally:
            sock.close()
    # The development seed was already published in the config. This constant
    # models prior policy-author knowledge, without any post-confinement read.
    known_seed = 2026103007
    partition = [len(g['targets']) for g in view['groups']]
    reconstructed = None
    for index in range(100000, 100008):
        e = make_episode(known_seed, 'development', index, partition)
        if e.public['episode_id'] == view['episode_id']:
            reconstructed = e.truth
            break
    # Landlock's handled rights do not include stat metadata.
    stat_visible = (ROOT/'configs/development.json').exists()
    send(conn, {'isolation': isolation, 'file_reads_denied': denied,
                'tcp_denied': network_denied, 'metadata_stat_visible': stat_visible,
                'truth_reconstructed_with_preknown_public_seed': reconstructed})
    conn.close()


def confinement_check():
    cfg = json.loads((ROOT/'configs/development.json').read_text())
    e = make_episode('reviewer-private-test-fixture', 'development', 100003, [1,15])
    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe()
    process = ctx.Process(target=confined_attack_probe, args=(child,))
    process.start()
    child.close()
    try:
        send(parent, public_view(e))
        assert parent.poll(12)
        result = receive(parent)
        process.join(5)
        assert process.exitcode == 0
        assert all(result['file_reads_denied'].values())
        assert all(result['tcp_denied'].values())
        assert result['truth_reconstructed_with_preknown_public_seed'] is None
        del result['truth_reconstructed_with_preknown_public_seed']
        result['truth_reconstruction_with_old_public_seed_succeeded'] = False
        result['disposition'] = 'file-read attack denied; old published seed does not reconstruct private-seed fixture'
        return result
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
        parent.close()


def confinement_fails_closed_check():
    with patch('qrelbench.security.platform.system', return_value='UnsupportedOS'):
        expect_error(confine_worker, RuntimeError)
    class OldKernel:
        def syscall(self, *args):
            return 3
    with patch('qrelbench.security.platform.system', return_value='Linux'), \
         patch('qrelbench.security.platform.machine', return_value='x86_64'), \
         patch('qrelbench.security.os.listdir', return_value=['one_thread']), \
         patch('qrelbench.security.ctypes.CDLL', return_value=OldKernel()):
        expect_error(confine_worker, RuntimeError)
    with patch('qrelbench.security.platform.system', return_value='Linux'), \
         patch('qrelbench.security.platform.machine', return_value='x86_64'), \
         patch('qrelbench.security.os.listdir', return_value=['thread1', 'thread2']):
        expect_error(confine_worker, RuntimeError)
    return {'unsupported_OS_rejected': True, 'Landlock_ABI3_rejected': True, 'multithreaded_bootstrap_rejected': True}


def source_hashes():
    paths = sorted((ROOT/'qrelbench').glob('*.py')) + sorted((ROOT/'tests').glob('*.py'))
    paths += [ROOT/'configs/development.json']
    if (ROOT/'PROTOCOL.md').exists():
        paths.append(ROOT/'PROTOCOL.md')
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    before = source_hashes()
    started = time.monotonic()
    results = {}
    failed = []
    checks = [generation_checks, interface_and_integrity_checks, channel_checks,
              policies_checks, configuration_checks, randomness_boundary_check,
              spawn_runner_checks, isolation_limit_check, confinement_check,
              confinement_fails_closed_check]
    for check in checks:
        try:
            results[check.__name__] = {'status': 'PASS', 'details': check()}
        except Exception:
            failed.append(check.__name__)
            results[check.__name__] = {'status': 'FAIL', 'traceback': traceback.format_exc()}
    after = source_hashes()
    if before != after:
        failed.append('source_changed_during_review')
    print(json.dumps({'independent_reviewer': True, 'seconds': time.monotonic()-started,
                      'source_stable_during_checks': before == after, 'source_sha256': after,
                      'failed_checks': failed, 'checks': results}, indent=2))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
