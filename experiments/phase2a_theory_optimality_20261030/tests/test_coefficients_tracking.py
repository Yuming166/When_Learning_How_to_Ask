import copy
import math
import unittest
import numpy as np
from phase2a.coefficients import solve_allocation,oracle_coefficient,gamma,critical_alpha,inner
from phase2a.tracking import InformationTracking


class CoefficientTests(unittest.TestCase):
    def test_quoted_boundary_recomputed(self):
        self.assertAlmostEqual(critical_alpha(16,8,.85,.6),2.0431602469,places=8)
        self.assertLess(gamma(16,8,.85,.6,2),1)
        self.assertGreater(gamma(16,8,.85,.6,3),1)
        self.assertLess(gamma(16,4,.85,.6,10),1)
    def test_numerical_primal_dual_brackets_without_gamma_shortcut(self):
        for part,alpha in [([1,3],0),([2,2],3),([4],0),([8,8],3)]:
            result=solve_allocation(part,.85,.6,alpha,.8)
            self.assertLessEqual(result['lower_bound'],result['upper_bound']+1e-9)
            self.assertLess(result['relative_gap'],1e-5)
            self.assertGreaterEqual(result['minimum_information'],1-1e-9)
            oracle=oracle_coefficient(sum(part),.85,.6,alpha)['K']
            self.assertGreaterEqual(result['K'],oracle-1e-6)
    def test_weak_and_intermediate_rate_problems(self):
        for p,q in [(.75,.6),(.6,.55),(.5005,.5)]:
            result=solve_allocation([2,2],p,q,3,.8,tolerance=2e-6)
            self.assertGreaterEqual(result['minimum_information'],1-1e-8)
            self.assertLess(result['relative_gap'],2e-5)
    def test_type_actions_cannot_increase_optimum(self):
        a=solve_allocation([1,3],.85,.6,3)
        b=solve_allocation([1,3],.85,.6,3,.8)
        self.assertLessEqual(b['upper_bound'],a['upper_bound']+1e-6)
    def test_invalid_perfect_type_is_separate(self):
        with self.assertRaises(ValueError):solve_allocation([4],.85,.6,3,1.)


def public_fixture():
    return {'d':4,'groups':[{'targets':[0,1]},{'targets':[2,3]}],
            'targets':[{'group':i//2} for i in range(4)],'type_accuracy':[.8,.8],
            'rate_domain':{'eta':.05}}


class TrackingTests(unittest.TestCase):
    def test_observable_only_reproducible_actions(self):
        public=public_fixture();cal={'high':[1,1,1,0],'low':[1,0,1,0]}
        a,b=InformationTracking(public,cal),InformationTracking(copy.deepcopy(public),copy.deepcopy(cal))
        for t in range(128):
            aa,bb=a.next(set(range(4))),b.next(set(range(4)));self.assertEqual(aa,bb)
            result={'format':'A'} if aa[0]=='type' else {'answer':int((t//3)%2)}
            a.observe(aa,result);b.observe(bb,result)
        self.assertEqual(a.counts.tolist(),b.counts.tolist());self.assertTrue(a.estimates)
        self.assertGreater(a.forced.sum(),0)
        self.assertAlmostEqual(a.weights.sum(),1.,places=7)
    def test_one_response_each_is_not_assumed_perfect_type_information(self):
        a=InformationTracking(public_fixture(),{'high':[],'low':[]})
        for t in range(8):
            action=a.next(set(range(4)));self.assertEqual(action[0],'query');a.observe(action,{'answer':t%2})
        self.assertTrue(np.all(a.forced.sum(axis=2)==1))
        # Types/rates are estimated, never supplied as constructor state.
        self.assertNotIn('truth',vars(a));self.assertNotIn('true_p',vars(a));self.assertNotIn('true_z',vars(a))
