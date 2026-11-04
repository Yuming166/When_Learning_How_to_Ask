"""Independent enumerated-reply checks and posterior stability checks."""
import unittest
import numpy as np
import run
from decision_value import QuadratureDecisionValue, BridgePolicy
from decision_ig import QuadratureDecisionIG
from policies import forced_action
import json

class DecisionValueChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((run.HERE/'config.json').read_text())
        cls.worlds=run.make_worlds(cls.config)

    def test_design(self):
        self.assertEqual(len(self.worlds)*4,264)
        self.assertEqual(sum(w['track']=='anchor' for w in self.worlds)*4,192)
        self.assertEqual(len({w['profile_cluster'] for w in self.worlds}),12)
        self.assertTrue(all(len(w['private']['types'])==max(w['public']['groups'])+1 for w in self.worlds))
        for cluster in {w['profile_cluster'] for w in self.worlds}:
            self.assertEqual(len({w['private']['response_seed'] for w in self.worlds if w['profile_cluster']==cluster}),1)

    def brute(self,p):
        weights=p._weights / p._weights.sum()
        winner=np.repeat(p._winners,p.type_count*p.order**2)
        prior=np.bincount(winner,weights=weights,minlength=p.item_count)
        scores=[]
        for action in range(2*p.d):
            expected=0.
            for answer in (0,1):
                likelihood=p._positive[action] if answer else 1-p._positive[action]
                unnormalized=weights*likelihood
                probability=unnormalized.sum()
                posterior=unnormalized/probability
                expected+=probability*np.bincount(winner,weights=posterior,minlength=p.item_count).max()
            scores.append(expected-prior.max())
        return np.array(scores)

    def test_beliefs_vs_explicit_posterior_branches(self):
        rng=np.random.default_rng(1803)
        for world in self.worlds[::12]:
            p=QuadratureDecisionValue(world['public'])
            for t in range(80):
                if t%7==0:
                    np.testing.assert_allclose(p.scores(),self.brute(p),atol=3e-14,rtol=1e-10)
                p.observe(int(rng.integers(2*p.d)),int(rng.integers(2)))
            # Arbitrary joint beliefs, not just histories selected by this policy.
            for concentration in (.05,1.,10.):
                p._weights=rng.dirichlet(np.full(p._weights.size,concentration))
                np.testing.assert_allclose(p.scores(),self.brute(p),atol=3e-14,rtol=1e-10)

    def test_same_joint_posterior_and_long_count_reconstruction(self):
        world=self.worlds[-1];p=QuadratureDecisionValue(world['public']);q=QuadratureDecisionIG(world['public'])
        rng=np.random.default_rng(803)
        for t in range(2500):
            action=int(rng.integers(2*p.d));answer=int(rng.random()<.8)
            p.observe(action,answer);q.observe(action,answer)
        np.testing.assert_array_equal(p._log_weights,q._log_weights)
        self.assertTrue(np.isfinite(p._log_weights).all())
        self.assertAlmostEqual(p._weights.sum(),1.,places=12)
        self.assertTrue(np.isfinite(p.scores()).all())
        prior=QuadratureDecisionValue(world['public'])
        logw=prior._log_weights+p._counts[:,1]@p._log_positive+p._counts[:,0]@p._log_negative
        logw-=logw.max();weights=np.exp(logw);weights/=weights.sum()
        np.testing.assert_allclose(weights,p._weights,atol=2e-12,rtol=1e-9)

    def test_zero_gain_and_forcing(self):
        public={'d':1,'groups':[0],'eta':'1/100','catalogue':{'offsets':[0,0],'slopes':[[0],[1]]}}
        p=QuadratureDecisionValue(public)
        for _ in range(100):p.observe(0,1)
        np.testing.assert_array_equal(p.scores(),np.zeros(2))
        policy=BridgePolicy('decision_value',public)
        rng=np.random.default_rng(4)
        for t in range(100):
            action=policy.next();forced=forced_action(t,1)
            if forced is not None:self.assertEqual(action,forced)
            policy.observe(action,int(rng.integers(2)))

if __name__=='__main__': unittest.main()
