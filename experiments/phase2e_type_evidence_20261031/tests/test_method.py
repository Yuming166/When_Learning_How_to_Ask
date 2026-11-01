import unittest
from fractions import Fraction as F
import json
import sys
from pathlib import Path
import numpy as np
from phase2e.exact import exact_posterior
from phase2e.estimator import posterior,information_scores,design
from phase2e.strategies import construct_sampler
from phase2e.interface import validate_exact
ROOT=Path(__file__).resolve().parents[1]

def public(groups):return {'d':sum(map(len,groups)),'groups':[{'targets':g} for g in groups],
                          'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8]*len(groups)}

class EstimationTests(unittest.TestCase):
    def test_exact_prior_and_noisy_report(self):
        empty=[[[0,0],[0,0]]];cal={'high':[],'low':[]}
        x=exact_posterior(empty,[[0]],cal,[[1]],[F(4,5)])
        self.assertEqual(x['z_prob'],[F(4,5)])
        self.assertEqual(x['theta_prob'],[F(1,2)])
        self.assertEqual(x['p'],F(4,5));self.assertEqual(x['q'],F(13,20))
    def test_exact_vs_quadrature_different_groups_and_inputs(self):
        rng=np.random.default_rng(48)
        max_error=0
        for groups in [[[0]],[[0,1]],[[0],[1]],[[0],[1,2]]]:
            d=sum(map(len,groups));G=len(groups)
            for rep in range(5):
                counts=np.zeros((d,2,2),dtype=int)
                for _ in range(8):counts[rng.integers(d),rng.integers(2),rng.integers(2)]+=1
                cal={'high':[1,rep%2],'low':[0,1]};reports=[[rep%2] for g in range(G)]
                x=exact_posterior(counts.tolist(),groups,cal,reports,[F(4,5)]*G)
                y=posterior(counts,groups,cal,reports,[.8]*G)
                a=[float(x['p']),float(x['q'])]+list(map(float,x['theta_prob']+x['z_prob']))
                b=[y['p'],y['q']]+y['theta_prob']+y['z_prob']
                max_error=max(max_error,float(np.max(np.abs(np.array(a)-b))))
        self.assertLess(max_error,1e-12)
    def test_sign_complement_equivariance(self):
        counts=np.array([[[2,5],[4,1]],[[0,4],[1,2]]]);g=[[0,1]];cal={'high':[1,1],'low':[0,1]}
        a=posterior(counts,g,cal,[[1,0]],[.8]);b=posterior(counts[:,:,::-1],g,cal,[[1,0]],[.8])
        np.testing.assert_allclose(a['theta_prob'],1-np.array(b['theta_prob']),atol=1e-13)
        np.testing.assert_allclose(a['z_prob'],b['z_prob'],atol=1e-13)
        self.assertAlmostEqual(a['p'],b['p'])
    def test_type_evidence_accumulates_without_certainty(self):
        c=np.zeros((1,2,2),int);cal={'high':[],'low':[]}
        a=posterior(c,[[0]],cal,[[1]*4],[.8])
        self.assertAlmostEqual(a['z_prob'][0],256/257);self.assertLess(a['z_prob'][0],1)
    def test_plugin_label_is_explicit(self):
        x=posterior(np.ones((1,2,2),int),[[0]],{'high':[1],'low':[0]},[[1]],[.8],plugin=True)
        self.assertEqual(x['quadrature_order'],0);self.assertIn('not_joint',x['inference'])
    def test_information_type_is_zero_without_sign_type_dependency(self):
        f=posterior(np.zeros((2,2,2),int),[[0],[1]],{'high':[],'low':[]},[[],[]],[.8,.8])
        s=information_scores(f,[[0],[1]],[.8,.8]);self.assertTrue(np.all(np.isfinite(s[:4])))
        self.assertTrue(np.all((~np.isfinite(s[4:]))|(s[4:]<-55)))
    def test_information_no_roundoff_floor_for_rare_sign(self):
        c=np.array([[[0,400],[0,100]]]);cal={'high':[1]*40,'low':[1]*25+[0]*15}
        f=posterior(c,[[0]],cal,[[0]*20],[.8])
        s=information_scores(f,[[0]],[.8]);self.assertTrue(np.all(s<-80),s)
    def test_natural_interface_rejected(self):
        p=public([[0]]);p['type_accuracy']='unknown'
        with self.assertRaises(ValueError):validate_exact(p,{'high':[],'low':[]})
    def test_fused_sampling_protocol(self):
        for name in ['Fused-Original','Fused-Info','Fused-D-RRC-Type','Fused-Original-NoType','Fused-Info-NoType']:
            p=public([[0]]);s=construct_sampler(name,p,{'high':[1,1],'low':[0,1]},16)
            for i in range(24):
                a=s.next({0});s.observe(a,{'format':'B'} if a[0]=='type' else {'answer':i%2})
                if name.endswith('NoType'):self.assertEqual(a[0],'query')
            self.assertEqual(int(s.counts.sum())+sum(map(len,s.types)),24)
            self.assertEqual(s.last_estimate['estimator_inputs'],'all_tasks_all_type_reports_labelled_calibration_known_groups')

class FixtureTests(unittest.TestCase):
    def test_validated_public_fixture_normalization(self):
        sys.path.insert(0,str(ROOT/'fixtures/v021'))
        from qrelbench_v021.canonical import from_dict
        from qrelbench_v021.compiler import compile_query
        from qrelbench_v021.bridge import normalize_response
        cases=0
        for mode in ['independent_fixture','dependent_mechanism_fixture']:
            obj=json.loads((ROOT/f'fixtures/v021/public/{mode}.json').read_text())
            for row in obj['targets']:
                p=from_dict(row['proposition'])
                for fmt in ['A','B']:
                    for variant in [0,1]:
                        for bit in [False,True]:
                            q=compile_query(p,fmt,variant)
                            self.assertEqual(normalize_response(p,fmt,variant,q.encode(bit)),{'answer':int(bit),'valid':True});cases+=1
                self.assertEqual(normalize_response(p,'A',0,'maybe'),{'answer':None,'valid':False})
            with self.assertRaises(ValueError):validate_exact({**obj,'type_accuracy':'unknown','rate_domain':{'status':'not_assumed'}},{'high':[],'low':[]})
        self.assertEqual(cases,768)
if __name__=='__main__':unittest.main()
