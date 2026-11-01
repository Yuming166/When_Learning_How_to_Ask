import unittest
from copy import deepcopy
import numpy as np
from t2.core import validate_state,teacher_target,observed_state,Scheduler
from t2.data import plans
from t2.bootstrap import ROOT
from phase2e.strategies import FusedOriginal
import json

class CoreTests(unittest.TestCase):
    def fixture(self):
        public={'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8,.8]}
        cal={'high':[1,1,0,1],'low':[0,1,0,1]};s=Scheduler(public,cal,16)
        for _ in range(8):
            a=s.next(range(4));s.observe(a,{'answer':int(a[1]%2==0)})
        return public,cal,s
    def test_literal_teacher_equivalence(self):
        public,cal,s=self.fixture();state,_,_=observed_state(s,cal,16,6144);label=teacher_target(state)
        frozen=FusedOriginal(public,cal,16);frozen.t=s.t;frozen.counts[:]=s.counts;frozen.forced[:]=s.forced;frozen._update()
        np.testing.assert_allclose(label['teacher_weights'],frozen.weights,rtol=1e-12,atol=1e-12)
        self.assertAlmostEqual(label['teacher_K'],frozen.last_estimate['estimated_K'],10)
    def test_whitelist_and_consistency(self):
        _,cal,s=self.fixture();state,_,_=observed_state(s,cal,16,6144)
        for key in ['truth','p','world_id','seed','reward']:
            bad=deepcopy(state);bad[key]=0
            with self.assertRaises(ValueError):validate_state(bad)
        bad=deepcopy(state);bad['estimate']['truth']=[0]*4
        with self.assertRaises(ValueError):validate_state(bad)
    def test_scheduler_requires_injection_and_keeps_square_forcing(self):
        _,_,s=self.fixture();self.assertTrue(s.needs_update())
        with self.assertRaises(RuntimeError):s.next(range(4))
        s.set_target(np.r_[np.ones(8)/8,[0,0]])
        self.assertEqual(s.next_update,40)
        for _ in range(24):
            a=s.next(range(4));s.observe(a,{'answer':1} if a[0]=='query' else {'format':'A'})
        self.assertEqual(s._forced_index(),0)
    def test_world_plans_disjoint_and_behavior_crosses_risk(self):
        p=plans(json.loads((ROOT/'config.json').read_text()));ids=[r['world_id'] for v in p.values() for r in v]
        self.assertEqual(len(ids),400);self.assertEqual(len(ids),len(set(ids)))
        combos={(x['behavior'],x['R']) for x in p['train']};self.assertEqual(len(combos),9)
        self.assertEqual(len({(x['behavior'],x['alpha']) for x in p['train']}),9)
        self.assertEqual(len({(x['behavior'],tuple(x['partition'])) for x in p['train']}),18)
        self.assertEqual(len({(x['behavior'],x['p'],x['q']) for x in p['train']}),9)
        self.assertEqual(len(p['train']),256)
        self.assertTrue(all(x['partition']==[2,2] for x in p['ood_partition']))

if __name__=='__main__':unittest.main()
