import unittest
import numpy as np
from t0.nqa_reference import UntrainedNQA,expand

def state(sizes):return {'p_hat':.85,'q_hat':.60,'alpha':3.,'eta':.05,'group_sizes':sizes,'type_accuracy':[.8]*len(sizes),'epsilon':1e-4}
class ContractTests(unittest.TestCase):
    def test_group_permutation_equivariance(self):
        m=UntrainedNQA();s=state([1,3]);s['type_accuracy']=[.7,.9]
        a=m.forward(s);b=m.forward({**s,'group_sizes':[3,1],'type_accuracy':[.9,.7]})
        np.testing.assert_allclose(a['group_mass'][::-1],b['group_mass'],rtol=0,atol=1e-14)
        self.assertAlmostEqual(a['K_hat'],b['K_hat'])
    def test_variable_sizes_and_group_counts_interface_only(self):
        m=UntrainedNQA()
        for sizes in [[1],[3],[4],[1,1],[1,2],[2,2],[1,2,3]]:
            out=m.forward(state(sizes));self.assertEqual(out['group_mass'].shape,(len(sizes),3))
            self.assertAlmostEqual(out['group_mass'].sum(),1);self.assertGreater(out['K_hat'],0)
    def test_type_mask(self):
        s=state([1,3]);s['type_accuracy']=None
        out=UntrainedNQA().forward(s);np.testing.assert_equal(out['group_mass'][:,2],0)
    def test_fact_permutation_expansion(self):
        mass=UntrainedNQA().forward(state([1,3]))['group_mass'];a=expand(mass,[[0],[1,2,3]],[1,0],4)
        perm=[2,0,3,1];b=expand(mass,[[perm[0]],[perm[j] for j in [1,2,3]]],[1,0],4)
        for j in range(4):np.testing.assert_allclose(a[2*j:2*j+2],b[2*perm[j]:2*perm[j]+2])
    def test_format_mapping(self):
        mass=UntrainedNQA().forward(state([1,3]))['group_mass']
        a=expand(mass,[[0],[1,2,3]],[1,0],4);b=expand(mass,[[0],[1,2,3]],[0,1],4)
        np.testing.assert_allclose(a[:8].reshape(4,2)[:,::-1],b[:8].reshape(4,2));np.testing.assert_allclose(a[8:],b[8:])
    def test_private_input_rejected(self):
        for key in ['truth','true_p','true_q','seed','world_id','teacher_weights','reward','score']:
            with self.assertRaises(ValueError):UntrainedNQA().forward({**state([4]),key:0})
    def test_group_mass_KL_equals_action_KL(self):
        a=np.array([[.1,.2,.05],[.4,.2,.05]]);b=np.array([[.2,.15,.1],[.3,.2,.05]])
        wa=expand(a,[[0],[1,2,3]],[1,0],4);wb=expand(b,[[0],[1,2,3]],[1,0],4)
        self.assertAlmostEqual(float(np.sum(a*np.log(a/b))),float(np.sum(wa*np.log(wa/wb))))
    def test_parameter_count_and_untrained_status(self):
        m=UntrainedNQA();self.assertEqual(m.parameter_count,10660);self.assertTrue(m.forward(state([4]))['status'].startswith('UNTRAINED'))
if __name__=='__main__':unittest.main()
