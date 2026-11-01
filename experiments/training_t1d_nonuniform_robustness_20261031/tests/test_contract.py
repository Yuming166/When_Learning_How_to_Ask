import unittest
import numpy as np
from t1d import bootstrap
from t1d.strategies import construct, category_target, marginal_information, POLICIES
from t1c.strategies import construct as frozen
from phase2e.strategies import FusedOriginal, FusedInformation
from t1b.belief import Belief
from phase2a.coefficients import warmup_lp


def public(part):
    k = 0; groups = []
    for size in part:
        groups.append({'targets': list(range(k, k+size))}); k += size
    return {'d': k, 'groups': groups, 'type_accuracy': [.8]*len(part),
            'rate_domain': {'eta': .05, 'levels_unknown': True}}


def cal(positive=False):
    return {'high': [1, 1, 1, 0]*4 if positive else [], 'low': [1, 0]*8 if positive else []}


def walk(obj, B):
    result = []
    for t in range(B):
        a = obj.next(set(range(obj.d))); result.append(a)
        y = int((t*13 + a[1]*7 + t//3) % 5 < 3)
        obj.observe(a, {'answer': y} if a[0] == 'query' else {'format': 'AB'[y]})
    return result


class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls): warmup_lp()

    def test_all_legal_and_matched_costs(self):
        for part in [[1, 3], [2, 2], [4], [1, 2], [3]]:
            for name in POLICIES:
                o = construct(name, public(part), cal(), 16, 32); walk(o, 32)
                self.assertEqual(o.counts.sum()+sum(map(len, o.types)), 32)
                self.assertEqual(len(o.action_history), 32)

    def test_frozen_physical_equivalence(self):
        for part in [[1, 3], [4], [1, 2], [3]]:
            for positive in [False, True]:
                for new, old in [('KL-AnalyticReuse', 'KL-Block'), ('Fused-Info', 'IG-Block'),
                                 ('Fresh-IG-Lite', 'Fresh-IG-Lite'), ('Belief-Gated', 'Belief-Gated')]:
                    a = construct(new, public(part), cal(positive), 16, 48)
                    b = frozen(old, public(part), cal(positive), 16, 48)
                    self.assertEqual(walk(a, 48), walk(b, 48))

    def test_original_solver_anchor(self):
        a = construct('KL-OriginalSolver', public([1, 2]), cal(True), 16, 32)
        b = FusedOriginal(public([1, 2]), cal(True), 16)
        self.assertEqual(walk(a, 32), walk(b, 32))

    def test_singleton_granularity_equivalence(self):
        # All groups singleton: group and fact classes coincide exactly.
        scores = np.array([.1, .3, .1, .2, .01, .02])
        u, _ = category_target(scores, [(0,), (1,)], 2, True)
        f, _ = category_target(scores, [(0,), (1,)], 2, False)
        np.testing.assert_array_equal(u, f)

    def test_uniform_targets_and_actual_balance(self):
        for name in ['IG-Uniform-Block', 'IG-Uniform-Fresh', 'IG-Uniform-Direct']:
            o = construct(name, public([1, 3]), cal(), 16, 64); walk(o, 64)
            for u in o.update_history:
                w = np.array(u['weights'])
                for group in o.groups:
                    for m in range(2):
                        np.testing.assert_allclose(w[[2*j+m for j in group]], w[2*group[0]+m], atol=0, rtol=0)
            for group in o.groups:
                for m in range(2):
                    n = o.counts[list(group), m].sum(1)
                    self.assertLessEqual(max(n)-min(n), 1)

    def test_dense_factorial_cadences(self):
        for granularity in ['Uniform', 'Fact']:
            for cadence, expected in [('Block', [8, 11, 15, 19, 24, 29]), ('Fresh', list(range(8, 32)))]:
                o = construct('IG-'+granularity+'-'+cadence, public([1, 3]), cal(), 16, 32); walk(o, 32)
                self.assertEqual([u['online'] for u in o.update_history], expected)

    def test_marginal_information_matches_conditioning(self):
        o = construct('Fresh-IG-Lite', public([1, 2]), cal(True), 16, 32); walk(o, 16)
        b = o.current_belief()
        for j in range(3):
            p = b.summary()['theta_prob'][j]
            entropy = lambda x: -(x*np.log(max(x, 1e-300))+(1-x)*np.log(max(1-x, 1e-300)))
            scores = marginal_information(b, j)
            for a in range(o.E):
                expected = entropy(p)
                for y in [0, 1]:
                    prob, child = b.condition(a, y)
                    expected -= prob*entropy(child.summary()['theta_prob'][j])
                self.assertAlmostEqual(scores[a], expected, places=12)

    def test_hidden_arguments_rejected(self):
        with self.assertRaises(TypeError): construct('Fresh-IG-Lite', public([3]), cal(), 16, 32, true_p=.8)

    def test_fixed_type_schedule_and_cost_match(self):
        for part in [[1,3],[4],[1,2],[3]]:
            for B in [16,32,48,64]:
                actions = []
                for name in ['IG-Uniform-FixedType','IG-Fact-FixedType']:
                    obj=construct(name,public(part),cal(),16,B); walk(obj,B)
                    paid=[(h['online_before'],h['action']) for h in obj.action_history if h['action']>=obj.L]
                    expected=[(2*obj.L+g,obj.L+g) for g in range(obj.G) if 2*obj.L+g<B]
                    self.assertEqual(paid,expected);actions.append(paid)
                self.assertEqual(actions[0],actions[1])


if __name__ == '__main__': unittest.main()
