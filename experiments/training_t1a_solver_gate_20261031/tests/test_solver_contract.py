import unittest
import numpy as np
from t1a.solvers import Model,Solver,old,optimized,x_of,canonical

class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):old.warmup_lp()
    def test_analytic_all_alternatives(self):
        rng=np.random.default_rng(110)
        for part in ([4],[1,3],[2,2]):
            for alpha in (0.,3.):
                m=Model(part,.85,.6,alpha,[.8]*len(part),.05)
                for _ in range(12):
                    x=rng.uniform(0,10,len(m.cost));f=m.fits(x)
                    ref=[old.inner(part,.85,.6,alpha,x,a,b,m.kappa,.05)['value'] for a,b in m.alts]
                    np.testing.assert_allclose(f[0],ref,rtol=5e-14,atol=1e-13)
    def test_zero_alpha_homogeneity(self):
        m=Model([1,3],.85,.6,0,[.8,.8],.05);x=np.arange(1,7,dtype=float)
        np.testing.assert_allclose(m.fits(3*x)[0],3*m.fits(x)[0],rtol=2e-14)
    def test_full_allocation_equivalence(self):
        args=([1,3],.85,.6,3,[.8,.8],.05,1e-4,200);a=old.solve_allocation(*args);b=optimized(*args)
        np.testing.assert_allclose(x_of(a)/a['K'],x_of(b)/b['K'],atol=1e-10,rtol=0)
    def test_exact_cache(self):
        args=([4],.85,.6,0,[.8],.05,1e-4,200);s=Solver('ExactCache');a=s(*args);b=s(*args)
        self.assertEqual(a,b);self.assertEqual(s.stats['hits'],1)
        altered=list(args);altered[1]=np.nextafter(.85,1);s(*altered);self.assertEqual(s.stats['hits'],1)
    def test_whitelist_signature(self):
        with self.assertRaises(TypeError):canonical([4],.85,.6,0,[.8],.05,1e-4,200,private_seed='forbidden')
    def test_bad_approximation_falls_back(self):
        args=([1,3],.85,.6,0,[.8,.8],.05,1e-4,200);s=Solver('QuantizedCache');s(*args)
        key=canonical(*args,quantized=True);s.cache[key]['a']=[0,0];s.cache[key]['b']=[0,0];s.cache[key]['c']=[0,0]
        f=s(*args);self.assertEqual(s.stats['fallback'],2);self.assertEqual(s.stats['guard_error'],1)
        self.assertGreaterEqual(f['minimum_information'],1-1e-7)
    def test_no_type_mask(self):
        f=optimized([1,3],.85,.6,0,None,.05,1e-4,200);self.assertEqual(f['c'],[0.,0.])
    def test_warm_recomputes_current_problem(self):
        s=Solver('WarmStart');s([1,3],.85,.6,0,[.8,.8],.05,1e-4,200)
        f=s([1,3],.8,.62,0,[.8,.8],.05,1e-4,200);m=Model([1,3],.8,.62,0,[.8,.8],.05)
        self.assertEqual(s.stats['warm_calls'],1);self.assertGreaterEqual(min(m.fits(x_of(f))[0]),1-1e-7)
if __name__=='__main__':unittest.main()
