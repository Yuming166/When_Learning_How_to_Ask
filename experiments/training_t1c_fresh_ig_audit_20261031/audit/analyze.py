"""Post-run analysis only. Never imports a policy, generates worlds, or retries a run."""
import functools
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['KL-Block', 'KL-Fresh', 'IG-Block', 'IG-Fresh', 'KL-32', 'IG-32',
        'IG-Fresh-Direct', 'Fresh-IG-Lite', 'Budget-Switch', 'Belief-Gated',
        'IG-Group-Block', 'IG-Group-Fresh']
BOOT = 20000
BOOT_SEED = 42017


def read_json(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def terminal(r):
    return r['estimation_history'][-1]


def cell(r):
    return (tuple(r['partition']), r['p'], r['alpha'])


def key(r):
    return r['index'], r['budget'], r['policy']


def scalar_summary(values):
    x = np.asarray(values, dtype=float)
    if not len(x):
        return {'n': 0, 'sum': 0., 'mean': None, 'median': None, 'p95': None}
    return {'n': len(x), 'sum': float(x.sum()), 'mean': float(x.mean()),
            'median': float(np.median(x)), 'p95': float(np.quantile(x, .95))}


class Analysis:
    def __init__(self):
        self.cfg = read_json(ROOT / 'config.json')
        self.execution = read_json(ROOT / 'artifacts/execution.json')
        self.data = list(rows(ROOT / 'artifacts/trajectories.jsonl'))
        self.by = {key(r): r for r in self.data}
        self.planned = {}
        for pi, part in enumerate(self.cfg['partitions']):
            for ri, p in enumerate(self.cfg['p_values']):
                for ai, alpha in enumerate(self.cfg['alphas']):
                    c = (pi * len(self.cfg['p_values']) + ri) * len(self.cfg['alphas']) + ai
                    for rep in range(self.cfg['worlds_per_cell']):
                        index = self.cfg['development_index_start'] + 100 * c + rep
                        self.planned[index] = (tuple(part), p, alpha)
        self.ids = sorted(self.planned)
        self.truth = {}
        self.group_scores = {}

    @functools.lru_cache(maxsize=100)
    def resamples(self, ids):
        if not ids:
            return np.empty((BOOT, 0), dtype=np.int16)
        groups = defaultdict(list)
        for j, i in enumerate(ids):
            groups[self.planned[i]].append(j)
        rng = np.random.default_rng(BOOT_SEED)
        return np.concatenate([rng.choice(v, (BOOT, len(v)), replace=True)
                               for _, v in sorted(groups.items())], axis=1)

    def interval(self, values, ids):
        ids = tuple(ids)
        x = np.asarray(values, dtype=float)
        if not len(ids):
            return {'n': 0, 'mean': None, 'ci95': None}
        assert x.shape == (len(ids),)
        bs = self.resamples(ids)
        return {'n': len(x), 'mean': float(x.mean()),
                'ci95': np.quantile(x[bs].mean(axis=1), [.025, .975]).tolist()}

    def available(self, B, arms, ids=None):
        return [i for i in (self.ids if ids is None else ids)
                if all((i, B, a) in self.by for a in arms)]

    def values(self, B, a, ids, f=lambda r: float(r['exact'])):
        return np.array([f(self.by[i, B, a]) for i in ids], dtype=float)

    def paired(self, B, a, b, ids=None):
        planned_n = len(self.ids if ids is None else ids)
        ids = self.available(B, [a, b], ids)
        av, bv = self.values(B, a, ids), self.values(B, b, ids)
        diff = av - bv
        result = {'candidate': a, 'reference': b, 'budget': B, 'planned_worlds': planned_n,
                  **self.interval(diff, ids),
                  'candidate_only': int(sum(diff > 0)), 'reference_only': int(sum(diff < 0)),
                  'both_success': int(sum((av == 1) & (bv == 1))),
                  'both_failed': int(sum((av == 0) & (bv == 0)))}
        result['identical_primitive_action_history_worlds'] = sum(
            [h['action'] for h in terminal(self.by[i, B, a])['action_history']] ==
            [h['action'] for h in terminal(self.by[i, B, b])['action_history']] for i in ids)
        result['identical_full_transcript_worlds'] = sum(
            self.by[i, B, a]['transcript_sha256'] == self.by[i, B, b]['transcript_sha256'] for i in ids)
        result['world_outcomes'] = [{'world_index': i, 'candidate_exact': bool(x),
                                     'reference_exact': bool(y)} for i, x, y in zip(ids, av, bv)]
        for metric, getter in {
            'type_queries': lambda r: r['costs']['type'],
            'joint_nll': lambda r: r['posterior_quality_posthoc']['joint_nll'],
            'joint_brier': lambda r: r['posterior_quality_posthoc']['joint_brier'],
            'trajectory_cpu': lambda r: r['trajectory_cpu_seconds'],
            'trajectory_wall': lambda r: r['trajectory_wall_seconds'],
        }.items():
            x, y = self.values(B, a, ids, getter), self.values(B, b, ids, getter)
            result[metric + '_difference'] = self.interval(x - y, ids)
        if ids:
            x = self.values(B, a, ids, lambda r: r['trajectory_cpu_seconds'])
            y = self.values(B, b, ids, lambda r: r['trajectory_cpu_seconds'])
            boot = self.resamples(tuple(ids))
            result['cpu_reference_over_candidate'] = {
                'ratio_of_sums': float(y.sum() / x.sum()),
                'ci95': np.quantile(y[boot].sum(1) / x[boot].sum(1), [.025, .975]).tolist()}
        return result

    def arm_summary(self, B, a, ids=None):
        planned_n = len(self.ids if ids is None else ids)
        ids = self.available(B, [a], ids)
        rr = [self.by[i, B, a] for i in ids]
        result = {'policy': a, 'budget': B, 'planned_worlds': planned_n,
                  'observed_worlds': len(rr), 'exact': sum(r['exact'] for r in rr),
                  'recovery': self.interval([float(r['exact']) for r in rr], ids),
                  'fixed_budget_complete': sum(r['fit']['fixed_budget_completed'] for r in rr),
                  'strict_certificates': sum(r['complete'] for r in rr),
                  'wrong_certificates': sum(r['complete'] and not r['exact'] for r in rr),
                  'strict_confidence_censored': sum(r['censored'] for r in rr)}
        getters = {
            'task_queries': lambda r: r['costs']['task'],
            'type_queries': lambda r: r['costs']['type'],
            'offline_cost': lambda r: r['costs']['offline'],
            'online_cost': lambda r: r['online'],
            'total_acquisition': lambda r: r['total_acquisition'],
            'fact_accuracy': lambda r: r['correct_facts'] / 4,
            'joint_nll': lambda r: r['posterior_quality_posthoc']['joint_nll'],
            'joint_brier': lambda r: r['posterior_quality_posthoc']['joint_brier'],
            'p_mae': lambda r: abs(terminal(r)['p_error']),
            'q_mae': lambda r: abs(terminal(r)['q_error']),
            'p_mse': lambda r: terminal(r)['p_error'] ** 2,
            'q_mse': lambda r: terminal(r)['q_error'] ** 2,
            'type_error_rate': lambda r: terminal(r)['type_errors'] / len(r['partition']),
            'trajectory_cpu': lambda r: r['trajectory_cpu_seconds'],
            'trajectory_wall': lambda r: r['trajectory_wall_seconds'],
            'posterior_cpu': lambda r: terminal(r)['component_cpu'].get('posterior', 0.),
            'target_cpu': lambda r: terminal(r)['component_cpu'].get('target', 0.),
            'controller_cpu_exclusive': lambda r: terminal(r)['component_cpu'].get('controller', 0.),
            'terminal_belief_cpu': lambda r: terminal(r)['terminal_belief_cpu'],
            'audit_probe_cpu': lambda r: terminal(r)['audit_probe_cpu'],
            'certification_cpu': lambda r: r['gate_cpu_seconds'],
            'certification_wall': lambda r: r['gate_seconds'],
            'updates': lambda r: len(terminal(r)['update_history']),
            'forced_tasks': lambda r: r['forced_tasks'],
        }
        for metric, getter in getters.items():
            result[metric] = scalar_summary([getter(r) for r in rr])
        unallocated = []
        for r in rr:
            e = terminal(r)
            allocated = sum(e['component_cpu'].values()) + e['terminal_belief_cpu'] + e['audit_probe_cpu'] + r['gate_cpu_seconds']
            unallocated.append(r['trajectory_cpu_seconds'] - allocated)
        result['remaining_trajectory_cpu'] = scalar_summary(unallocated)
        return result

    def factor(self, B, group_uniform=False):
        ib, inf = ('IG-Group-Block', 'IG-Group-Fresh') if group_uniform else ('IG-Block', 'IG-Fresh')
        arms = ['KL-Block', 'KL-Fresh', ib, inf]
        ids = self.available(B, arms)
        kb, kf, ig_b, ig_f = [self.values(B, a, ids) for a in arms]
        effects = {
            'refresh_KL': kf - kb, 'refresh_IG': ig_f - ig_b,
            'IG_minus_KL_block': ig_b - kb, 'IG_minus_KL_fresh': ig_f - kf,
            'refresh_main_effect': .5 * (kf - kb + ig_f - ig_b),
            'objective_main_effect': .5 * (ig_b - kb + ig_f - kf),
            'interaction': (ig_f - ig_b) - (kf - kb),
        }
        return {'arms': arms, 'n': len(ids),
                'scope': ('common group-uniform target simplex; greedy group-average IG vs KL, not a matched horizon/objective geometry'
                          if group_uniform else 'operational allocation rules; onehot IG vs group-uniform KL target classes differ'),
                'effects': {k: self.interval(v, ids) for k, v in effects.items()}}

    def validate(self):
        counts = Counter()
        errors = []

        def check(condition, name):
            counts[name] += 1
            if not condition and len(errors) < 100:
                errors.append(name)

        check(len(self.by) == len(self.data), 'unique_trajectory_keys')
        planned_keys = {(i, B, a) for i in self.ids for B in self.cfg['budgets'] for a in ARMS}
        check(set(self.by) <= planned_keys, 'all_observed_keys_are_planned')
        check(len(self.data) == self.execution['finished_trajectories'], 'execution_row_count')
        errors_by_budget = Counter()
        certificate_status = Counter()
        age = defaultdict(list)
        mismatch = defaultdict(Counter)
        event_times = defaultdict(set)
        rules = defaultdict(Counter)
        controller_overrides = defaultdict(Counter)
        controls = {'Budget-Switch', 'Belief-Gated'}
        for r in self.data:
            B, a = r['budget'], r['policy']
            e = terminal(r)
            hist = e['action_history']
            updates = e['update_history']
            c = np.asarray(r['counts'], dtype=int)
            type_n = sum(map(len, r['type_answers']))
            check(c.shape == (4, 2, 2) and np.all(c >= 0), 'valid_task_counts')
            check(c.sum() == r['costs']['task'] and type_n == r['costs']['type'], 'observation_cost_ledger')
            check(r['online'] == B == r['costs']['task'] + r['costs']['type'], 'exact_online_budget')
            check(r['costs']['offline'] == 2 * r['M'] == 2 * math.ceil(r['alpha'] * r['R']), 'offline_cost_ledger')
            check(r['total_acquisition'] == B + 2 * r['M'], 'total_acquisition_ledger')
            check(len(r['calibration']['high']) == r['M'] == len(r['calibration']['low']), 'calibration_coverage')
            check(len(hist) == B and [h['online_before'] for h in hist] == list(range(B)), 'one_logged_action_per_observation')
            check(all(0 <= h['action'] < 8 + len(r['partition']) for h in hist), 'legal_action_indices')
            forced = [t for t in range(B) if t - 8 * math.isqrt(t // 8) ** 2 < 8]
            check([h['online_before'] for h in hist if h['forced']] == forced, 'common_forced_schedule')
            check(r['forced_tasks'] == len(forced), 'forced_count_ledger')
            check(all(hist[t]['action'] == (t - 8 * math.isqrt(t // 8) ** 2) for t in forced), 'forced_action_identity')
            free = [h for h in hist if not h['forced']]
            if a == 'Fresh-IG-Lite':
                expected_updates = [h['online_before'] for h in free]
            elif a in ['KL-Fresh', 'IG-Fresh', 'IG-Fresh-Direct', 'IG-Group-Fresh']:
                expected_updates = list(range(8, B))
            elif a in ['KL-32', 'IG-32']:
                expected_updates = list(range(8, B, 32))
            else:
                expected_updates = []
                t = 8
                while t < B:
                    expected_updates.append(t)
                    t += math.ceil(math.sqrt(t + 1))
            check([u['online'] for u in updates] == expected_updates, 'audited_target_cadence')
            event_times[(B, a)].add(tuple(u['online'] for u in updates))
            for u in updates:
                w = np.asarray(u['weights'])
                check(len(w) == 8 + len(r['partition']) and np.min(w) >= -1e-12 and abs(w.sum() - 1) < 1e-10, 'normalized_target')
                check(u['posterior_online'] == u['online'], 'target_uses_current_update_posterior')
                if a in ['KL-Block', 'KL-Fresh', 'KL-32', 'IG-Group-Block', 'IG-Group-Fresh']:
                    j = 0
                    for k in r['partition']:
                        for fmt in range(2):
                            check(np.max(np.abs(w[2*j+fmt:2*(j+k)+fmt:2] - w[2*j+fmt])) < 1e-12, 'common_group_uniform_target_class')
                        j += k
            for h in free:
                if a not in controls and h['posterior_online'] is not None:
                    age[(B, a)].append(h['online_before'] - h['posterior_online'])
                if a in ['IG-Block', 'IG-Fresh', 'IG-32', 'IG-Fresh-Direct', 'Fresh-IG-Lite']:
                    mismatch[(B, a)]['free'] += 1
                    mismatch[(B, a)]['action_differs_current_target_argmax'] += h['action'] != h['target_argmax']
                if a in controls:
                    rules[(B, a)][h['selection_rule']] += 1
                    controller_overrides[(B, a)]['free'] += 1
                    controller_overrides[(B, a)]['differs_from_current_KL_proposal'] += h['action'] != h['tracked_candidate']
            if a == 'Budget-Switch':
                check(e['rule_counts'].get('KL', 0) == math.ceil(len(free) / 2) and e['rule_counts'].get('IG', 0) == len(free) // 2, 'predeclared_free_round_switch')
            if a in ['IG-Fresh-Direct', 'Fresh-IG-Lite']:
                check(all(h['action'] == h['target_argmax'] for h in free), 'direct_execution_uses_current_IG_target')
            probs = np.asarray(e['joint_theta_distribution'])
            check(probs.shape == (16,) and np.all(probs >= 0) and abs(probs.sum() - 1) < 1e-10, 'normalized_terminal_posterior')
            check(e['joint_theta_MAP'] == r['fit']['theta'] and e['quadrature_order'] == 32, 'common_terminal_decoder')
            gate = r['strict_certificate']
            check(gate.get('total_observations') == r['total_acquisition'], 'certificate_includes_all_task_type_calibration')
            check(gate.get('task_counts') == c.sum(2).tolist() and gate.get('type_counts') == [len(v) for v in r['type_answers']], 'certificate_observation_shape')
            check(gate['candidate_theta'] == r['fit']['theta'], 'certificate_covers_submitted_candidate')
            check(r['complete'] == gate['certified'] and r['censored'] == (not r['complete']) and r['abstained'] == (not r['complete']), 'certified_vs_guess_status')
            check((r['strictly_certified_output'] == r['fit']['theta']) if r['complete'] else r['strictly_certified_output'] is None, 'no_uncertified_reliable_output')
            check(r['fit']['fixed_budget_completed'], 'fixed_budget_completion_flag')
            check(r['isolation']['no_new_privileges'] and r['isolation']['landlock_abi'] > 0, 'worker_isolation_record')
            certificate_status[(B, gate['status'], gate.get('reason', ''))] += 1
            if r['complete'] and not r['exact']:
                errors_by_budget[B] += 1

        # Only NEW development private scoring records; no old seeds or confirmation files.
        # Truth is used here after actions have been recorded, never returned to workers.
        potentials = {}
        forced_prefixes = {}
        physical_paths = {}
        seen_private = set()
        for priv in rows(ROOT / 'artifacts/private/reproduction.jsonl'):
            job = priv['job']
            k = job['index'], job['budget'], priv['policy']
            seen_private.add(k)
            check(k in self.by, 'new_private_record_has_public_terminal_row')
            if k not in self.by:
                continue
            r = self.by[k]
            truth, types = priv['truth'], priv['types']
            check(len(truth) == 4 and len(types) == len(r['partition']), 'new_scoring_labels_shape')
            if r['index'] in self.truth:
                check(self.truth[r['index']] == (truth, types), 'same_hidden_new_world_across_arms_budgets')
            self.truth[r['index']] = (truth, types)
            guess = r['fit']['theta']
            check(r['exact'] == (guess == truth) and r['correct_facts'] == sum(x == y for x, y in zip(guess, truth)), 'parent_recovery_score')
            e = terminal(r)
            ti = sum(int(bit) << (3-j) for j, bit in enumerate(truth))
            target = np.eye(16)[ti]
            prob = np.asarray(e['joint_theta_distribution'])
            check(abs(-math.log(max(prob[ti], 1e-300)) - r['posterior_quality_posthoc']['joint_nll']) < 1e-10, 'parent_posthoc_NLL')
            check(abs(np.sum((prob-target)**2) - r['posterior_quality_posthoc']['joint_brier']) < 1e-10, 'parent_posthoc_Brier')
            group_score = []
            start = 0
            for g, size in enumerate(r['partition']):
                good = [guess[j] == truth[j] for j in range(start, start+size)]
                group_score.append({'size': size, 'exact': all(good), 'correct_facts': sum(good),
                                    'task_queries': int(np.asarray(r['counts'])[start:start+size].sum()),
                                    'type_queries': len(r['type_answers'][g]),
                                    'type_correct': e['z'][g] == types[g]})
                start += size
            self.group_scores[k] = group_score
            offsets = Counter()
            physical = []
            action_log = e['action_history']
            for event in priv['trace_prefix']:
                method, args, result = event['action'], event['args'], event['result']
                if method == 'query':
                    a = 2 * args['j'] + 'AB'.index(args['format'])
                    answer = result['answer']
                elif method == 'ask_type':
                    a = 8 + args['group']
                    answer = 'AB'.index(result['format'])
                else:
                    continue
                pk = r['index'], a, offsets[a]
                if pk in potentials:
                    check(potentials[pk] == answer, 'same_potential_response_streams')
                else:
                    potentials[pk] = answer
                offsets[a] += 1
                physical.append((a, answer))
            check(len(physical) == r['budget'] and [a for a, y in physical] == [h['action'] for h in action_log], 'logged_actions_match_physical_queries')
            reconstructed = np.zeros((4, 2, 2), dtype=int)
            reconstructed_types = [[] for _ in r['partition']]
            for a, y in physical:
                if a < 8:
                    reconstructed[a // 2, a % 2, y] += 1
                else:
                    reconstructed_types[a - 8].append(y)
            check(np.array_equal(reconstructed, r['counts']) and reconstructed_types == r['type_answers'], 'independent_trace_observation_reconstruction')
            trace_hash = hashlib.sha256()
            for event in priv['trace_prefix']:
                trace_hash.update(json.dumps(event, sort_keys=True, separators=(',', ':')).encode() + b'\n')
            check(trace_hash.hexdigest() == r['transcript_sha256'], 'independent_full_trace_hash')
            physical_paths[k] = physical
            prefix = tuple(physical[:16])
            if r['index'] in forced_prefixes:
                check(forced_prefixes[r['index']] == prefix, 'same_initial_16_observations')
            forced_prefixes[r['index']] = prefix
            check(priv['full_trace_sha256'] == r['transcript_sha256'], 'private_public_transcript_digest')
        check(seen_private == set(self.by), 'new_private_public_coverage')
        for i in self.ids:
            rr = [r for (j, B, a), r in self.by.items() if j == i]
            if not rr:
                continue
            check(len({json.dumps(r['calibration'], sort_keys=True) for r in rr}) == 1, 'same_calibration_across_arms_budgets')
            probes = [terminal(r)['common_t16_features'] for r in rr if r['budget'] > 16]
            if probes:
                check(all(p is not None for p in probes) and len({json.dumps(p, sort_keys=True) for p in probes}) == 1, 'same_predecision_t16_belief_probe')
            at16 = [r for r in rr if r['budget'] == 16]
            if at16:
                check(len({json.dumps(r['fit']['theta']) for r in at16}) == 1 and len({r['exact'] for r in at16}) == 1, 'B16_all_forced_negative_control')
                check(len({json.dumps(terminal(r)['joint_theta_distribution']) for r in at16}) == 1, 'B16_identical_terminal_posterior')
            for a in ARMS:
                if a in controls:
                    continue
                if (i, 32, a) in physical_paths and (i, 64, a) in physical_paths:
                    check(physical_paths[i, 32, a] == physical_paths[i, 64, a][:32], 'non_budget_aware_arm_same_cross_budget_prefix')

        freeze = read_json(ROOT / 'freeze.json')
        bound_ok = all(digest(ROOT / rel) == h for rel, h in freeze['files'].items())
        check(bound_ok, 'original_bound_77_files_preserved')
        inputs = read_json(ROOT / 'INPUT_SNAPSHOT.json')
        check(all(digest(p) == h for p, h in inputs['files'].items()), 'all_historical_input_snapshot_files_preserved')
        old_receipts = {}
        for path in inputs['files']:
            if path.endswith('/FINAL_RECEIPT.json') and ('training_t1a_solver' in path or 'training_t1b_planning' in path):
                receipt = read_json(path)
                base = Path(path).parent
                results = {rel: digest(base / rel) == h for rel, h in receipt['public_files'].items()}
                check(all(results.values()), 'full_old_public_receipt_preserved')
                old_receipts[str(base)] = {'files': len(results), 'all_preserved': all(results.values())}
        deviation = read_json(ROOT / 'PROVENANCE_DEVIATION.json')
        local_ok = all(digest(ROOT / rel) == v['sha256'] for rel, v in deviation['observed_t1c_sources'].items())
        check(local_ok, 'local_code_unchanged_since_poststart_snapshot')
        totals = {c: sum(r['costs'][c] for r in self.data) for c in ['task', 'type', 'offline']}
        failures = list(rows(ROOT / 'artifacts/failures.jsonl'))
        if not failures:
            check(totals == self.execution['costs_including_partial'], 'overall_acquisition_ledger')
        return {
            'passed_observed_checks': not errors, 'error_examples': errors, 'check_counts': dict(counts),
            'planned_paths': len(planned_keys), 'observed_paths': len(self.data),
            'uncompleted_planned_paths': len(planned_keys - set(self.by)),
            'recorded_infrastructure_failures': len(failures), 'failures': failures,
            'certificate_status': [{'budget': k[0], 'status': k[1], 'reason': k[2], 'count': n} for k, n in sorted(certificate_status.items())],
            'wrong_certificates': dict(errors_by_budget), 'acquisition_completed_paths': totals,
            'original_hash_bound_files': len(freeze['files']), 'original_hash_bound_files_preserved': bound_ok,
            'preexecution_full_source_hash_binding': False, 'provenance_deviation': 'PROVENANCE_DEVIATION.json',
            'poststart_local_source_preserved': local_ok, 'old_public_receipts': old_receipts,
            'posterior_age_on_free_actions': {f'{B}/{a}': scalar_summary(v) for (B, a), v in age.items()},
            'onehot_IG_action_vs_current_target': {f'{B}/{a}': dict(v) for (B, a), v in mismatch.items()},
            'target_update_times': {f'{B}/{a}': [list(x) for x in sorted(v)] for (B, a), v in event_times.items()},
            'controller_rule_counts': {f'{B}/{a}': dict(v) for (B, a), v in rules.items()},
            'controller_physical_overrides': {f'{B}/{a}': dict(v) for (B, a), v in controller_overrides.items()},
            'potential_stream_entries_checked': len(potentials),
            'security_scope': 'controlled trusted policy workers under existing Landlock/RPC boundary; not a proof against arbitrary malicious modules',
        }

    def strata(self):
        selections = {}
        for part in self.cfg['partitions']:
            selections['partition=' + ','.join(map(str, part))] = [i for i in self.ids if self.planned[i][0] == tuple(part)]
        for p in self.cfg['p_values']:
            selections['p=' + str(p)] = [i for i in self.ids if self.planned[i][1] == p]
        for alpha in self.cfg['alphas']:
            selections['alpha=' + str(alpha)] = [i for i in self.ids if self.planned[i][2] == alpha]
        for c in sorted(set(self.planned.values())):
            selections['cell=' + repr(c)] = [i for i in self.ids if self.planned[i] == c]
        out = {}
        for B in self.cfg['budgets']:
            out[B] = {}
            for name, ids in selections.items():
                out[B][name] = {
                    'planned_worlds': len(ids),
                    'arms': {a: {'n': len(self.available(B, [a], ids)),
                                 'exact': int(sum(self.values(B, a, self.available(B, [a], ids))))} for a in ARMS},
                    'Lite_minus_KL_Block': self.paired(B, 'Fresh-IG-Lite', 'KL-Block', ids),
                    'IG_Fresh_minus_KL_Fresh': self.paired(B, 'IG-Fresh', 'KL-Fresh', ids),
                    'IG_Group_Fresh_minus_KL_Fresh': self.paired(B, 'IG-Group-Fresh', 'KL-Fresh', ids),
                }
        return out

    def features(self):
        probes = {i: terminal(self.by[i, 32, 'KL-Block'])['common_t16_features']
                  for i in self.ids if (i, 32, 'KL-Block') in self.by}
        specs = {'theta_entropy_half': ('theta_entropy_fraction', .5),
                 'type_entropy_half': ('type_entropy_fraction', .5),
                 'gap_015': ('estimated_gap', .15), 'alpha': ('alpha_observed', 1.5)}
        out = {'feature_scope': 'same forced t16 legal belief; bins fixed before new seed; posthoc outcome association only',
               'probes_available': len(probes), 'bins': {}}
        for name, (field, threshold) in specs.items():
            out['bins'][name] = {}
            for side in ['low', 'high']:
                ids = [i for i, p in probes.items() if (p[field] >= threshold) == (side == 'high')]
                out['bins'][name][side] = {'worlds': len(ids), 'field': field, 'threshold': threshold,
                                          'feature': scalar_summary([probes[i][field] for i in ids]), 'budgets': {}}
                for B in [32, 64]:
                    out['bins'][name][side]['budgets'][B] = {
                        'Lite_minus_KL_Block': self.paired(B, 'Fresh-IG-Lite', 'KL-Block', ids),
                        'IG_Fresh_minus_KL_Fresh': self.paired(B, 'IG-Fresh', 'KL-Fresh', ids),
                        'IG_Group_Fresh_minus_KL_Fresh': self.paired(B, 'IG-Group-Fresh', 'KL-Fresh', ids),
                    }
        out['public_world_features'] = [{'world_index': i, **p} for i, p in sorted(probes.items())]
        return out

    def group_results(self):
        result = {}
        for B in self.cfg['budgets']:
            result[B] = {}
            for a in ARMS:
                groups = defaultdict(list)
                for i in self.available(B, [a]):
                    for g in self.group_scores.get((i, B, a), []):
                        groups[g['size']].append(g)
                result[B][a] = {size: {'groups': len(v),
                                       'exact_groups': sum(g['exact'] for g in v),
                                       'fact_accuracy': sum(g['correct_facts'] for g in v) / (len(v) * size),
                                       'mean_task_queries': np.mean([g['task_queries'] for g in v]).item(),
                                       'mean_type_queries': np.mean([g['type_queries'] for g in v]).item(),
                                       'type_accuracy': np.mean([g['type_correct'] for g in v]).item()}
                                    for size, v in sorted(groups.items())}
        return {'scope': 'descriptive group observations nested within worlds; no independent-group confidence claim', 'budgets': result}

    def type_timing(self):
        out = {}
        for B in self.cfg['budgets']:
            out[B] = {}
            for a in ARMS:
                ids = self.available(B, [a])
                first = []
                hist = Counter()
                per_group = Counter()
                for i in ids:
                    buys = [h for h in terminal(self.by[i, B, a])['action_history'] if h['action'] >= 8]
                    if buys:
                        first.append(buys[0]['online_before'])
                    for h in buys:
                        t = h['online_before']
                        hist[f'{8*(t//8)}-{8*(t//8)+7}'] += 1
                        per_group[h['action'] - 8] += 1
                out[B][a] = {'worlds': len(ids), 'worlds_purchasing_type': len(first),
                              'worlds_without_type_purchase': len(ids) - len(first),
                              'first_type_time_conditional_on_purchase': scalar_summary(first),
                              'type_counts_by_online_before_window': dict(hist),
                              'type_counts_by_group_index': dict(per_group)}
        return {'scope': 'descriptive purchase timing only; completed observations before query, not extra queries or threshold selection', 'budgets': out}

    def run(self):
        validation = self.validate()
        write_json('VALIDATION.json', validation)
        summaries = {B: {a: self.arm_summary(B, a) for a in ARMS} for B in self.cfg['budgets']}
        pairs = [('KL-Fresh', 'KL-Block'), ('IG-Fresh', 'IG-Block'),
                 ('IG-Block', 'KL-Block'), ('IG-Fresh', 'KL-Fresh'),
                 ('IG-Group-Block', 'KL-Block'), ('IG-Group-Fresh', 'KL-Fresh'),
                 ('IG-Group-Fresh', 'IG-Group-Block'),
                 ('IG-Fresh', 'IG-Group-Fresh'), ('IG-Block', 'IG-Group-Block'),
                 ('IG-Fresh-Direct', 'IG-Fresh'), ('IG-Fresh-Direct', 'KL-Fresh'),
                 ('KL-Block', 'KL-32'), ('KL-Fresh', 'KL-32'),
                 ('IG-Block', 'IG-32'), ('IG-Fresh', 'IG-32')]
        pairs += [('Fresh-IG-Lite', a) for a in ARMS if a != 'Fresh-IG-Lite']
        pairs += [(a, b) for a in ['Budget-Switch', 'Belief-Gated'] for b in ['KL-Block', 'KL-Fresh']]
        paired = {B: {a + ' minus ' + b: self.paired(B, a, b) for a, b in pairs}
                  for B in self.cfg['budgets']}
        write_json('PAIRED_OUTCOMES.json', paired)
        features = self.features()
        write_json('BELIEF_FEATURES.json', features)
        write_json('STRATIFIED_RESULTS.json', self.strata())
        write_json('GROUP_RESULTS.json', self.group_results())
        write_json('TYPE_PURCHASE_TIMING.json', self.type_timing())
        factors = {B: {'operational': self.factor(B), 'group_uniform': self.factor(B, True)}
                   for B in self.cfg['budgets']}
        execution = self.execution
        startups = {}
        for r in self.data:
            startups.setdefault(r['policy'], r['isolation']['worker_startup_cpu'])
        total_worker = sum(r['trajectory_cpu_seconds'] for r in self.data)
        runtime = {'execution_wall_seconds': execution['seconds'],
                   'completed_trajectory_worker_cpu': total_worker,
                   'per_worker_kernel_warmup_cpu': startups,
                   'kernel_warmup_total_cpu': sum(startups.values()),
                   'evaluator_cpu_seconds': execution['evaluator_cpu_seconds'],
                   'measured_cpu_lower_bound': total_worker + sum(startups.values()) + execution['evaluator_cpu_seconds'],
                   'not_in_measured_cpu': 'Python interpreter/import bootstrap before worker timer; orchestration outside evaluator main; posthoc analysis/report generation; partial worker CPU if failed',
                   'attribution': 'trajectory CPU includes exclusive posterior/target/controller, terminal estimator, common probe, certificate, and RPC/bookkeeping. planner_cpu overlaps component timers. Parent CPU is aggregate and not attributed per arm.',
                   'all_budgets_by_arm': {}, 'primary_budget_by_arm': summaries[32]}
        for a in ARMS:
            rr = [r for r in self.data if r['policy'] == a]
            runtime['all_budgets_by_arm'][a] = {
                'paths': len(rr), 'cpu': sum(r['trajectory_cpu_seconds'] for r in rr),
                'wall': sum(r['trajectory_wall_seconds'] for r in rr),
                'posterior_cpu': sum(terminal(r)['component_cpu'].get('posterior', 0) for r in rr),
                'target_cpu': sum(terminal(r)['component_cpu'].get('target', 0) for r in rr),
                'controller_cpu': sum(terminal(r)['component_cpu'].get('controller', 0) for r in rr),
                'gate_cpu': sum(r['gate_cpu_seconds'] for r in rr),
                'probe_cpu': sum(terminal(r)['audit_probe_cpu'] for r in rr),
                'terminal_belief_cpu': sum(terminal(r)['terminal_belief_cpu'] for r in rr),
            }
        write_json('RUNTIME.json', runtime)
        pb = paired[32]
        lkb, lkf = [pb['Fresh-IG-Lite minus ' + a] for a in ['KL-Block', 'KL-Fresh']]
        full = (execution['status'] == 'completed' and validation['passed_observed_checks']
                and validation['uncompleted_planned_paths'] == 0 and not validation['recorded_infrastructure_failures'])
        if not full:
            fresh = 'REVISE'
        elif lkb['mean'] >= .03 and lkb['ci95'][0] > 0 and lkf['mean'] >= 0 and lkf['ci95'][0] >= 0:
            fresh = 'GO'
        elif lkb['mean'] <= 0 and lkf['mean'] <= 0:
            fresh = 'NO-GO'
        else:
            fresh = 'REVISE'
        typebins = features['bins']['type_entropy_half']
        enough = min(typebins[s]['worlds'] for s in ['low', 'high']) >= 24
        usable = {}
        for comparison in ['Lite_minus_KL_Block', 'IG_Fresh_minus_KL_Fresh']:
            budget_ok = {}
            for B in [32, 64]:
                lo, hi = [typebins[s]['budgets'][B][comparison] for s in ['low', 'high']]
                def strong(z):
                    return z['n'] >= 24 and abs(z['mean']) >= .03 and (z['ci95'][0] > 0 or z['ci95'][1] < 0)
                budget_ok[B] = enough and strong(lo) and strong(hi) and lo['mean'] * hi['mean'] < 0
            usable[comparison] = {'per_budget': budget_ok, 'both_budgets': all(budget_ok.values())}
        opposite = any(v['both_budgets'] for v in usable.values())
        # Resource gate: positive evidence beyond BOTH fixed controls would also be needed.
        # The current protocol specifies no trained candidate; success is only permission to design.
        controls_not_covering = all(pb['Fresh-IG-Lite minus ' + a]['ci95'][0] > 0
                                    for a in ['Budget-Switch', 'Belief-Gated']) if full else False
        rl_design = bool(full and enough and opposite and controls_not_covering)
        result = {'status': execution['status'], 'scope': 'bounded independent development, no confirmation or training',
                  'primary_budget': 32, 'planned_independent_worlds': len(self.ids),
                  'complete_all_arms_budgets_worlds': len(
                      [i for i in self.ids if all((i, B, a) in self.by for B in self.cfg['budgets'] for a in ARMS)]),
                  'summaries': summaries, 'factorials': factors,
                  'fresh_candidate_preregistered_gate': fresh,
                  'fresh_gate_values': {'Lite_minus_KL_Block': lkb, 'Lite_minus_KL_Fresh': lkf, 'all_paths_complete_valid': full},
                  'rl_added_value': 'GO_DESIGN_ONLY' if rl_design else 'NO-GO_TRAINING_ADDED_VALUE_UNESTABLISHED',
                  'rl_gate': {'type_bin_minimum_24_each': enough, 'opposite_sign_evidence': usable,
                              'beyond_both_simple_controls_strictly_positive_CI': controls_not_covering,
                              'design_only_gate_passed': rl_design},
                  'full_source_preexecution_hash_binding': False,
                  'numerical_scope': 'order32 posterior/float allocation are approximations; terminal certificates use frozen audited Fraction/Decimal iid known-s model only',
                  'training_updates': 0, 'model_calls': 0, 'confirmation_worlds': 0, 'retries': 0}
        write_json('RESULTS.json', result)
        print(json.dumps({'status': execution['status'], 'worlds': len(self.ids),
                          'paths': len(self.data), 'validation': validation['passed_observed_checks'],
                          'fresh_gate': fresh, 'rl_design_gate': rl_design,
                          'B32_exact': {a: summaries[32][a]['exact'] for a in ARMS}}))


if __name__ == '__main__':
    Analysis().run()
