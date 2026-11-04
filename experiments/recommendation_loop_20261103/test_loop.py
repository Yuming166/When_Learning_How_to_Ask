"""Observable contracts, allocation-goal difference and shared response pairing."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from certification import CertifiedDecisionGate
from policies import ARMS, ObservablePolicy, forced_action, minimum_flips
from run_loop import make_worlds, stable_seed
from run_loop import run_arm

ROOT=Path(__file__).resolve().parent
PUBLIC={'d':4,'groups':[0,0,1,1],'eta':'1/100',
        'catalogue':{'offsets':[0,-7],'slopes':[[0,0,0,0],[5,4,2,1]]}}


class LoopChecks(unittest.TestCase):
    def test_private_fields_rejected_for_every_arm(self):
        for name in ARMS:
            for field,value in [('theta',[1]*4),('p',.8),('seed',123),('winner',1)]:
                public=copy.deepcopy(PUBLIC);public[field]=value
                with self.assertRaises(ValueError):ObservablePolicy(name,public)

    def test_full_and_decision_allocators_share_estimate_but_not_alternatives(self):
        a=ObservablePolicy('decision_kl',PUBLIC);b=ObservablePolicy('profile_kl',PUBLIC)
        counts=np.array([[[20,80],[40,60]]]*4,dtype=np.int64)
        for p in (a,b):p.counts[:]=counts;p.t=int(counts.sum());p._update()
        self.assertEqual(a.updates[-1]['estimate'],b.updates[-1]['estimate'])
        self.assertEqual(set(a.updates[-1]['minimal_flips']),{1,2,12})
        self.assertEqual(set(b.updates[-1]['minimal_flips']),{1,2,4,8})
        self.assertFalse(np.allclose(a.weights,b.weights))

    def test_unidentified_rate_fallback_is_shared_and_logged(self):
        counts=np.zeros((4,2,2),dtype=np.int64);counts[:,:,0]=10;counts[:,:,1]=10
        for name in ('joint_dr_rc','profile_kl','decision_kl'):
            p=ObservablePolicy(name,PUBLIC);p.counts[:]=counts;p.t=int(counts.sum());p._update()
            self.assertEqual(p.updates[-1]['status'],'UNIDENTIFIED_RATES_UNIFORM_TARGET')
            np.testing.assert_array_equal(p.weights,np.full(8,.125))

    def test_forced_counts_are_sublinear_pathwise(self):
        d=6;forced=np.zeros(2*d,dtype=int)
        for t in range(2000):
            action=forced_action(t,d)
            if action is not None:forced[action]+=1
            n=int(np.sqrt((t+1)/(2*d)))
            self.assertGreaterEqual(forced.min(),n)
            self.assertLessEqual(forced.max(),n+1)
            self.assertLessEqual(forced.sum(),np.sqrt(2*d*(t+1))+2*d)

    def test_world_generation_is_stable_and_policy_inputs_are_public(self):
        c=json.loads((ROOT/'config.json').read_text())
        worlds=make_worlds(c);self.assertEqual(worlds,make_worlds(c))
        self.assertEqual(len(worlds),8)
        self.assertEqual(len({w['profile_cluster'] for w in worlds}),4)
        for w in worlds:self.assertEqual(set(w['public']),{'d','groups','eta','catalogue'})

    def test_raw_response_streams_are_action_indexed_and_replayable(self):
        c=json.loads((ROOT/'config.json').read_text());w=make_worlds(c)[0]
        seed=w['private']['response_seed']
        def sample_order(actions):
            rngs=[np.random.default_rng(stable_seed(seed,str(a))) for a in range(8)]
            return [(a,float(rngs[a].random())) for a in actions]
        a=sample_order([0,1,0,1]);b=sample_order([1,0,1,0])
        self.assertEqual([x for i,x in a if i==0],[x for i,x in b if i==0])
        self.assertEqual([x for i,x in a if i==1],[x for i,x in b if i==1])
        self.assertNotEqual(a[0][1],a[2][1])

    def test_common_item_gate_can_certify_with_unobserved_preference(self):
        public={'d':2,'groups':[0,0],'eta':'1/100',
                'catalogue':{'offsets':[0,1],'slopes':[[0,0],[1,1]]}}
        counts=np.zeros((2,2,2),dtype=np.int64);counts[0,0,1]=20
        gate=CertifiedDecisionGate(public,R=3)
        result=gate.check(counts)
        self.assertEqual(result['status'],'CERTIFIED');self.assertEqual(result['item'],1)
        self.assertEqual(counts[1].sum(),0)

    def test_pending_and_invalid_observations_fail_closed(self):
        p=ObservablePolicy('round_robin',PUBLIC);a=p.next()
        with self.assertRaises(RuntimeError):p.next()
        with self.assertRaises(ValueError):p.observe(a,True)
        with self.assertRaises(ValueError):p.observe(a+1,1)
        p.observe(a,1);self.assertEqual(p.t,1)

    def test_postprocessing_error_preserves_preexisting_certificate(self):
        c=json.loads((ROOT/'config.json').read_text());c['max_queries']=1
        world=make_worlds(c)[0]
        real_factory=ObservablePolicy
        def policy_factory(*args,**kwargs):
            policy=real_factory(*args,**kwargs)
            policy.model.estimate=lambda counts:(_ for _ in ()).throw(RuntimeError('diagnostic failure fixture'))
            return policy
        # This tests harness state handling, not certificate mathematics; gate
        # correctness has separate exact tests. At the cap the stub is called.
        class StubGate:
            def __init__(self,public,R):self.model=real_factory('round_robin',public).model
            def check(self,counts):return {'status':'CERTIFIED','certified':True,'item':0}
        with patch('run_loop.ObservablePolicy',side_effect=policy_factory),patch('run_loop.CertifiedDecisionGate',StubGate):
            result=run_arm(world,'round_robin',c)
        self.assertEqual(result['status'],'CERTIFIED')
        self.assertIsNone(result['failure']);self.assertIsNotNone(result['certificate'])
        self.assertEqual(result['postprocessing_failure']['type'],'RuntimeError')


if __name__=='__main__':unittest.main()
