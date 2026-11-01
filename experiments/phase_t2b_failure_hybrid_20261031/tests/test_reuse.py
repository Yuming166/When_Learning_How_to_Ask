"""Fixed observable fixtures only; no sampled world, seed, truth, or model."""
from copy import deepcopy
import unittest

import numpy as np

from t2b.reuse import AnalyticReuseSolver, _load_frozen_solver
from t2.core import Scheduler, observed_state, teacher_target
from phase2a.coefficients import solve_allocation
from phase2b.log_glr import log_glr
from phase2d.certified import certify_stop
from phase2e.strategies import FusedOriginal


def public_fixture(groups):
    return {'d': sum(map(len, groups)),
            'groups': [{'targets': list(g)} for g in groups],
            'rate_domain': {'eta': .05}, 'type_accuracy': [.8] * len(groups)}


def state_fixture(groups=((0,), (1, 2, 3)), alpha=.5):
    d = sum(map(len, groups)); G = len(groups); M = int(64 * alpha)
    counts = np.full((d, 2, 2), 2, dtype=int)
    online = int(counts.sum())
    return {'schema': 't2_observable_v1', 'd': d, 'groups': [list(g) for g in groups],
            'eta': .05, 'known_s': [.8] * G, 'counts': counts.tolist(),
            'forced_counts': np.ones_like(counts).tolist(),
            'type_report_counts': [[0, 0] for _ in groups],
            'calibration': {'high': {'successes': int(.75 * M), 'total': M},
                            'low': {'successes': int(.5 * M), 'total': M}},
            'R': 64., 'online': online, 'online_cap': 6144, 'remaining': 6144-online,
            'estimate': {'p': .85, 'q': .6, 'theta_prob': [.7] * d,
                         'z_prob': [.6] * G, 'z': [g % 2 for g in range(G)]},
            'action_mask': [1] * (2*d + G)}


class ReuseContract(unittest.TestCase):
    def test_original_solver_module_loaded_without_vendor_bootstrap(self):
        module = _load_frozen_solver()
        self.assertTrue(module.__name__.startswith('_t2b_frozen_analytic_reuse.'))
        self.assertEqual(module.bootstrap.__dict__.get('ROOT'), None)
        self.assertIs(module.old.solve_allocation, solve_allocation)

    def test_same_input_allocations_and_objectives(self):
        # A small literal fixture grid, not a sampled or outcome-selected set.
        cases = [([4], 0., [.8]), ([1, 3], .5, [.8, .8]),
                 ([2, 2], 3., [.8, .8]), ([1, 3], 0., None)]
        for partition, alpha, accuracy in cases:
            with self.subTest(partition=partition, alpha=alpha, accuracy=accuracy):
                args = (partition, .85, .6, alpha, accuracy, .05, 1e-4, 200)
                reference = solve_allocation(*args)
                adapter = AnalyticReuseSolver(); actual = adapter.solve(*args)
                x = lambda fit: np.asarray(fit['a'] + fit['b'] + fit['c']) / fit['K']
                np.testing.assert_allclose(x(actual), x(reference), atol=2e-11, rtol=0)
                self.assertAlmostEqual(actual['K']/reference['K'], 1., places=10)
                self.assertGreaterEqual(actual['minimum_information'], 1.-1e-7)
                self.assertGreaterEqual(actual['relative_gap'], -5e-8)
                self.assertLessEqual(actual['relative_gap'], 5e-4)
                self.assertEqual(adapter.stats['calls'], 1)
                self.assertNotIn('fallback', adapter.stats)
                self.assertNotIn('hits', adapter.stats)

    def test_target_matches_frozen_expansion_and_does_not_mutate_state(self):
        state = state_fixture(); before = deepcopy(state)
        reference = teacher_target(state)
        adapter = AnalyticReuseSolver(); actual = adapter.target(state)
        np.testing.assert_allclose(actual['teacher_weights'], reference['teacher_weights'], atol=2e-11, rtol=0)
        self.assertAlmostEqual(actual['teacher_K']/reference['teacher_K'], 1., places=10)
        self.assertEqual(state, before)
        self.assertEqual(adapter.stats['calls'], len(actual['solver']['attempts']))

    def test_private_field_rejected_before_solver_call(self):
        state = state_fixture(); state['private_theta'] = [0, 0, 0, 0]
        adapter = AnalyticReuseSolver()
        with self.assertRaises(ValueError): adapter.target(state)
        self.assertEqual(adapter.stats['calls'], 0)

    def test_solver_rejects_additional_private_parameter(self):
        adapter = AnalyticReuseSolver()
        with self.assertRaises(TypeError):
            adapter.solve([4], .85, .6, 0., [.8], private_theta=[0, 0, 0, 0])

    def test_deterministic_observable_trajectory_and_gate_identity(self):
        # Literal action-specific bit strings are a technical replay fixture.
        # They have no sampled generating parameters or correctness labels.
        patterns = ('11010110111', '00110110', '11101011', '0100101',
                    '101111001', '01011001', '111010011', '001101011',
                    '01110101', '1011101')
        groups = ((0,), (1, 2, 3)); public = public_fixture(groups)
        calibration = {'high': [1, 1, 0, 1] * 8, 'low': [0, 1] * 16}
        reference = FusedOriginal(public, calibration, 64)
        original_update = reference._update
        def matched_update():
            original_update(); reference.next_update = reference.t + 32
        reference._update = matched_update
        candidate = Scheduler(public, calibration, 64, block=32)
        solver = AnalyticReuseSolver(); offsets = [{}, {}]; traces = [[], []]
        final_costs = []
        for t in range(128):
            if candidate.needs_update():
                state, _, _ = observed_state(candidate, calibration, 64, 6144)
                target = solver.target(state); candidate.set_target(target['teacher_weights'])
            for k, sampler in enumerate((reference, candidate)):
                action = sampler.next(set(range(4)))
                index = 8 + action[1] if action[0] == 'type' else 2*action[1] + 'AB'.index(action[2])
                nth = offsets[k].get(index, 0); offsets[k][index] = nth + 1
                bit = int(patterns[index][nth % len(patterns[index])])
                result = {'format': 'AB'[bit]} if action[0] == 'type' else {'answer': bit}
                traces[k].append((action, bit, sampler.last_forced))
                sampler.observe(action, result)
            self.assertEqual(traces[0][-1], traces[1][-1])
            np.testing.assert_allclose(reference.weights, candidate.weights, atol=2e-10, rtol=0)
        for sampler in (reference, candidate):
            final_costs.append({'task': int(sampler.counts.sum()),
                                'type': sum(map(len, sampler.types)),
                                'offline': sum(map(len, calibration.values()))})
        self.assertEqual(final_costs[0], final_costs[1])
        self.assertEqual(traces[0], traces[1])
        np.testing.assert_array_equal(reference.counts, candidate.counts)
        self.assertEqual(reference.types, candidate.types)
        fits = [log_glr(s.counts, s.groups, calibration, s.types, [.8, .8], 64, .05)
                for s in (reference, candidate)]
        for key in ('theta', 'gap', 'beta'): self.assertEqual(fits[0][key], fits[1][key])
        gates = [certify_stop(s.counts, s.groups, calibration, s.types, [.8, .8], 64,
                              .05, candidate_theta=fits[k]['theta'])
                 for k, s in enumerate((reference, candidate))]
        # The strict arithmetic output must match; separate wall timers need not.
        self.assertEqual({k:v for k,v in gates[0].items() if k != 'timings_seconds'},
                         {k:v for k,v in gates[1].items() if k != 'timings_seconds'})
        self.assertEqual(candidate.t, 128)
        self.assertEqual(solver.stats['calls'], 4)


if __name__ == '__main__':
    unittest.main()
