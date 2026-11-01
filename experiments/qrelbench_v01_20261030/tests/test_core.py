import copy
import itertools
import json
import math
import unittest
from collections import Counter
import numpy as np
from qrelbench.data import make_episode,evaluate,public_view,render
from qrelbench.environment import QueryEnvironment
from qrelbench.policies import Strategy,certificate
from qrelbench.decoder import decode,rate_estimates


class DataProperties(unittest.TestCase):
    def test_generated_semantic_properties(self):
        balance=set();seen=set()
        for seed in range(250):
            ep=make_episode(seed,'development',100000,[1,15]);balance.add(sum(ep.truth))
            self.assertEqual(len({r['productID'] for r in ep.records}),16)
            for j,t in enumerate(ep.public['targets']):
                self.assertEqual(evaluate(ep.records[j],t['proposition']),ep.truth[j])
                for m in ['A','B']:self.assertEqual(t['queries'][m],render(t['proposition'],m))
                seen.add(t['proposition']['predicate'])
        self.assertGreater(len(balance),5);self.assertEqual(seen,{'stock','price','shipping','returns'})
    def test_split_and_reproducibility(self):
        a=make_episode(7,'development',100000,[8,8]);b=make_episode(7,'development',100000,[8,8])
        self.assertEqual(a,b)
        for split in ['train','test']:
            self.assertNotEqual(a.key,make_episode(7,split,100000,[8,8]).key)
        self.assertEqual(a.truth,make_episode(7,'development',100000,[16]).truth)
    def test_public_view_does_not_encode_private_mutations(self):
        ep=make_episode(8,'development',100003,[8,8]);view=public_view(ep)
        ep.truth=[1-x for x in ep.truth];ep.types=[1-x for x in ep.types]
        for record in ep.records:record['offers']={'private_canary':True}
        self.assertEqual(public_view(ep),view)
        serialized=json.dumps(view)
        for forbidden in ['master_seed','private_canary','records','group_type','theta','"p"','"q"']:
            self.assertNotIn(forbidden,serialized)
    def test_truth_independence_and_metadata_smoke(self):
        episodes=[make_episode(91,'development',100000+i,[8,8]) for i in range(800)]
        truth=np.array([e.truth for e in episodes]);corr=np.corrcoef(truth.T)-np.eye(16)
        self.assertLess(abs(corr).max(),.18)
        # Independent stream construction is the basis; this finite test can only find bugs.
        for j in range(16):self.assertLess(abs(truth[:,j].mean()-.5),.08)
        types=np.array([e.types for e in episodes]);self.assertLess(abs(types.mean()-.5),.08)


class EnvironmentTests(unittest.TestCase):
    def new(self,**kwargs):return QueryEnvironment(make_episode(3,'development',100000,[2,2]),.85,.6,**kwargs)
    def test_lifecycle_cost_and_terminal_reward(self):
        env=self.new(calibration_size=13,online_cap=2);view=env.reset()
        self.assertNotIn('oracle_format_types',view)
        with self.assertRaises(RuntimeError):env.reset()
        x=env.get_calibration();self.assertEqual(x,env.get_calibration());self.assertEqual(env.cost['offline'],26)
        with self.assertRaises(RuntimeError):env.score()
        env.query(0,'A');env.ask_type(0)
        self.assertEqual(env.cost,{'task':1,'type':1,'offline':26})
        with self.assertRaises(RuntimeError):env.query(0,'B')
        self.assertEqual(env.submit([0]*4),{'submitted':True})
        with self.assertRaises(RuntimeError):env.get_calibration()
        with self.assertRaises(RuntimeError):env.query(1,'A')
    def test_no_counterfactual_rate_or_seed_public_leak(self):
        e1=self.new();ep=copy.deepcopy(e1._episode);ep.types=[1-z for z in ep.types]
        e2=QueryEnvironment(ep,.75,.55)
        self.assertEqual(e1.reset(),e2.reset())
        self.assertEqual(set(e1.query(0,'A')),{'answer'})
        self.assertEqual(set(e1.ask_type(0)),{'format'})
        self.assertEqual(set(e1.get_calibration()),{'high','low'})
    def test_negative_controls_are_explicit(self):
        ep=make_episode(4,'development',100000,[4])
        persistent=QueryEnvironment(ep,.85,.6,control='persistent',online_cap=100)
        persistent.reset();answers=[persistent.query(0,'A')['answer'] for _ in range(80)]
        self.assertEqual(len(set(answers)),1)
        perfect=QueryEnvironment(ep,.85,.6,type_accuracy=1,online_cap=20);perfect.reset()
        self.assertTrue(all(perfect.ask_type(0)['format']=='AB'[ep.types[0]] for _ in range(10)))
    def test_fresh_errors_reference_statistics(self):
        ep=make_episode(51,'development',100000,[2]);env=QueryEnvironment(ep,.85,.6,calibration_size=10000,online_cap=40000);env.reset()
        series={}
        for j,m in itertools.product(range(2),['A','B']):
            values=np.array([env.query(j,m)['answer']==ep.truth[j] for _ in range(10000)],dtype=float)
            expected=.85 if m=='AB'[ep.types[0]] else .6
            self.assertLess(abs(values.mean()-expected),.03)
            self.assertLess(abs(np.corrcoef(values[:-1],values[1:])[0,1]),.06)
            series[j,m]=values
        self.assertLess(abs(np.corrcoef(series[0,'A'],series[1,'A'])[0,1]),.06)
        cal=env.get_calibration()
        self.assertLess(abs(np.mean(cal['high'])-.85),.03);self.assertLess(abs(np.mean(cal['low'])-.6),.03)
    def test_types_and_errors_repeat_with_private_seed(self):
        a,b=self.new(online_cap=50),self.new(online_cap=50);self.assertEqual(a.reset(),b.reset())
        for j in range(4):
            for m in ['A','B']:
                for _ in range(3):self.assertEqual(a.query(j,m),b.query(j,m))
        self.assertEqual(a.get_calibration(),b.get_calibration())


class PolicyChecks(unittest.TestCase):
    def test_rr_balances_within_each_target(self):
        view=public_view(make_episode(7,'train',0,[4]));view['type_accuracy']=[.8]
        p=Strategy('Round-Robin',view)
        for _ in range(8):
            a=p.next(set(range(4)));p.observe(a,{'answer':0})
        self.assertTrue(np.all(p.counts.sum(axis=2)==1))
    def test_repeat_comparison_uses_denominators(self):
        view=public_view(make_episode(7,'train',0,[4]));view['type_accuracy']=[.8]
        p=Strategy('Repeat-and-Compare',view);p.agree[0]=[80,9];p.pairs[0]=[100,10]
        self.assertEqual(p.estimate_format(0),'B')
    def test_joint_decoder_against_independent_enumeration(self):
        ep=make_episode(14,'train',0,[1,3]);view=public_view(ep);view['type_accuracy']=[.8,.8]
        cal={'high':[1]*16+[0]*2,'low':[1]*11+[0]*7};p,q=rate_estimates(cal)
        rng=np.random.default_rng(771)
        for trial in range(24):
            counts=rng.integers(0,6,size=(4,2,2));types=[[],[trial%2]]
            got=decode(view,counts,cal,types)
            candidates=[]
            for theta in itertools.product([0,1],repeat=4):
                weight=0.
                for zs in itertools.product([0,1],repeat=2):
                    likelihood=1.
                    for j in range(4):
                        g=view['targets'][j]['group']
                        for m in [0,1]:
                            rate=p if m==zs[g] else q
                            likelihood*=rate**int(counts[j,m,theta[j]])*(1-rate)**int(counts[j,m,1-theta[j]])
                    for g,answers in enumerate(types):
                        for a in answers:likelihood*=.8 if a==zs[g] else .2
                    weight+=likelihood
                candidates.append((weight,theta))
            best=max(candidates,key=lambda pair:pair[0])[1]
            self.assertEqual(got,list(best))
    def test_confidence_boundary_edge_cases(self):
        self.assertIsNone(certificate(0,0,16,.1))
        self.assertIsNone(certificate(0,100,16,.1))
        self.assertEqual(certificate(200,200,16,.01),1)
        self.assertEqual(certificate(-200,200,16,.01),0)
    def test_independent_finite_horizon_absorbing_recursion(self):
        # Enumerate binomial path mass by (n,number of ones), absorbing at first boundary.
        for r in [.5,.6,.85]:
            state={0:1.};error=success=0.;delta=.1
            for n in range(1,301):
                nxt={}
                for ones,mass in state.items():
                    nxt[ones]=nxt.get(ones,0)+mass*(1-r);nxt[ones+1]=nxt.get(ones+1,0)+mass*r
                state={}
                for ones,mass in nxt.items():
                    # Independent code path, compare empirical mean to Hoeffding radius.
                    radius=math.sqrt(math.log(2*n*(n+1)/delta)/(2*n))
                    if ones/n>.5+radius:success+=mass
                    elif ones/n<.5-radius:error+=mass
                    else:state[ones]=mass
                self.assertAlmostEqual(sum(state.values())+success+error,1.,places=10)
            self.assertLessEqual(error,delta)


class RandomEndpointTests(unittest.TestCase):
    def test_maximum_random_word_is_strictly_less_than_one(self):
        from unittest.mock import patch
        from qrelbench.randomness import uniform
        with patch('qrelbench.randomness.derive',return_value=b'\xff'*32):
            self.assertLess(uniform(b'k','test'),1.)
        with patch('qrelbench.randomness.derive',return_value=b'\0'*32):
            self.assertEqual(uniform(b'k','test'),0.)
