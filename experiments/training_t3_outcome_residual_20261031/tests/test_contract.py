import copy,json,math,tempfile,unittest
from pathlib import Path
import numpy as np
from t3 import bootstrap
from t3.core import ValueNet,features,candidates,allowed_actions,ResidualPolicy,FEATURE_NAMES
from t3.rollout import action_values
from t3.roster import worlds,jobs
from t3.evaluator import evaluate
from t3.runner import run_arm
from t1b.belief import Belief
from t1d.strategies import construct
from qrelbench.data import make_episode
from qrelbench.environment import QueryEnvironment

def fixture(d=4):
    groups=[[0],[1,2,3]] if d==4 else [[0],[1,2]]
    counts=np.arange(d*4).reshape(d,2,2)%3
    cal={'high':[1,1,1,0,1,1],'low':[1,0,1,0,1,1]};reports=[[1],[0,1]]
    b=Belief.from_observation(counts,groups,cal,reports,[.8,.8],.05)
    return b,groups,counts,cal,reports

class Contracts(unittest.TestCase):
    def test_last_step_matches_closed_recovery(self):
        b,*_=fixture();q=action_values(b,[0,3,8],31,32,2,np.random.default_rng(3))
        for a in [0,3,8]:self.assertAlmostEqual(q['q'][a],b.recovery()[a],places=12)
    def test_rollout_cannot_mutate_current_belief(self):
        b,*_=fixture();before=b.w.copy();q=action_values(b,[0,8],30,32,2,np.random.default_rng(2))
        np.testing.assert_array_equal(before,b.w)
        self.assertTrue(all(0<=x<=1 for x in q['q'].values()));self.assertEqual(q['continuation_steps'],8)
    def test_feature_allowlist_and_dimensions(self):
        for d in [3,4]:
            b,g,c,cal,r=fixture(d);p=candidates(b,0);X=features(b,g,c,r,len(cal['high']),16,32,p)
            self.assertEqual(X.shape,(2*d+2,len(FEATURE_NAMES)))
            with self.assertRaises(TypeError):features(b,g,c,r,len(cal['high']),16,32,p,true_p=.9)
    def test_shared_scorer_action_permutation(self):
        rng=np.random.default_rng(13);X=rng.normal(size=(10,len(FEATURE_NAMES)));net=ValueNet(8);perm=rng.permutation(10)
        np.testing.assert_allclose(net.forward(X[perm]),net.forward(X)[perm],rtol=1e-13,atol=1e-13)
    def test_finite_difference_gradient(self):
        net=ValueNet(7);X=np.random.default_rng(7).normal(size=(3,len(FEATURE_NAMES)));y,cache=net.forward(X,True)
        grad=net.gradients(cache,np.ones(3)/3);eps=1e-6;old=net.p['W0'][2,3]
        net.p['W0'][2,3]=old+eps;up=net.forward(X).mean();net.p['W0'][2,3]=old-eps;dn=net.forward(X).mean()
        self.assertAlmostEqual(grad['W0'][2,3],(up-dn)/(2*eps),places=8)
    def test_type_and_task_masks(self):
        p={'worst':0,'ig':2,'kl':8,'type':9,'task':0}
        self.assertEqual(allowed_actions(p,4,'task'),[0,2]);self.assertEqual(allowed_actions(p,4,'type'),[0,8,9])
        p.update(worst=8,task=2);self.assertEqual(allowed_actions(p,4,'task'),[8])
    def test_zero_residual_physical_equivalence(self):
        for part in [[1,3],[1,2]]:
            ep=make_episode('T3_LITERAL_ENGINEERING_ONLY','development',3,part)
            e1=QueryEnvironment(ep,.85,.60,0,.8,32);e2=QueryEnvironment(ep,.85,.60,0,.8,32)
            p1=e1.reset();p2=e2.reset();c1=e1.get_calibration();c2=e2.get_calibration()
            old=construct('WorstFact-MI',p1,c1,16,32);new=ResidualPolicy(p2,c2,16,32)
            for t in range(32):
                a=old.next(set(range(sum(part))));b=new.next(set(range(sum(part))));self.assertEqual(a,b)
                r1=e1.ask_type(a[1]) if a[0]=='type' else e1.query(a[1],a[2]);r2=e2.ask_type(b[1]) if b[0]=='type' else e2.query(b[1],b[2])
                self.assertEqual(r1,r2);old.observe(a,r1);new.observe(b,r2)
    def test_split_disjointness_and_heldout_grid(self):
        cfg=json.loads((bootstrap.ROOT/'config.json').read_text())
        tr=worlds('train',cfg);dev=worlds('development',cfg);test=worlds('test',cfg)
        self.assertEqual((len(tr),len(dev),len(test)),(48,24,192));self.assertEqual(len(jobs('test',cfg)),336)
        keys=[(r['split'],r['index']) for r in tr+dev+test];self.assertEqual(len(keys),len(set(keys)))
        self.assertTrue(all(sum(r['partition'])==4 for r in tr));self.assertTrue(any(sum(r['partition'])==3 for r in test))
    def test_noisy_report_not_perfect_revelation(self):
        b,g,c,cal,r=fixture();p=Belief.from_observation(np.zeros_like(c),g,{'high':[],'low':[]},[[1],[]],[.8,.8],.05)
        self.assertAlmostEqual(p.summary()['z_prob'][0],.8,places=10)
    def test_rpc_baseline_and_residual_receipts(self):
        cfg=json.loads((bootstrap.ROOT/'config.json').read_text());plan=jobs('development',cfg)[:1]
        with tempfile.TemporaryDirectory(prefix='t3-literal-') as temp:
            path=Path(temp);ValueNet(1).save(path/'net.npz');target=path/'artifacts/literal_evaluation';target.mkdir(parents=True)
            for name in ['WorstFact-MI','Fresh-IG-Lite','Belief-Gated','KL-AnalyticReuse','Fused-Info','IG-Fact-FixedType','Rule-Switch','Collect-Worst','Learned-Task-1','Learned-Type-1','Learned-Joint-1']:
                model=str(path/'net.npz') if name.startswith('Learned-') else None
                r=run_arm(name,plan,'T3_LITERAL_RPC_ONLY',target/name,model,__import__('time').monotonic()+120)
                self.assertEqual(r['status'],'completed',r);self.assertEqual(r['costs']['task']+r['costs']['type'],32)
            from unittest.mock import patch
            from t3 import report
            with patch.object(report,'ROOT',path):
                records,audit=report.read_evaluation('literal_evaluation')
                self.assertEqual(audit['paths'],11);self.assertTrue(audit['passed'])
                a=report.aggregate(records);self.assertEqual(a['n'],11)
                p=report.paired([records[0]],[records[0]])
                self.assertEqual(p['delta_pp'],0);self.assertEqual(p['ci95_pp'],[0,0])

if __name__=='__main__':unittest.main()
