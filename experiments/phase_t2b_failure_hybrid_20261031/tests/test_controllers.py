from copy import deepcopy
import unittest
from unittest.mock import patch
import numpy as np
from test_reuse import state_fixture
from t2b.controllers import Controller,risk_flags
from t2b.worlds import public_plan,specs
from t2b.bootstrap import ROOT
import json

class FakeModel:
 def __init__(self):self.inputs=[]
 def predict(self,s):
  self.inputs.append(deepcopy(s));return np.ones(len(s['action_mask']))/len(s['action_mask'])

class Contracts(unittest.TestCase):
 def setUp(self):
  self.s=state_fixture();self.s['estimate']['theta_prob']=[1.]*4;self.s['estimate']['z_prob']=[1.]*2
 def test_confident_uniform_has_no_risk(self):self.assertFalse(any(risk_flags(self.s,np.ones(10)/10).values()))
 def test_uncertain_starved_fact_is_detected(self):
  self.s['estimate']['theta_prob'][0]=.5;w=np.ones(10);w[:2]=0;w/=w.sum()
  self.assertTrue(risk_flags(self.s,w)['uncertain_fact_starved'])
 def test_private_fields_rejected_before_predictor(self):
  model=FakeModel();c=Controller('DeepSets-KL',{'DeepSets-KL':model});self.s['truth']=[1]*4
  with self.assertRaises(ValueError):c.predict(self.s)
  self.assertEqual(model.inputs,[])
 def test_safe_hybrid_does_not_call_fallback(self):
  model=FakeModel();c=Controller('Hybrid-Risk-Info',{'DeepSets-KL':model})
  with patch.object(c,'info',side_effect=AssertionError('Unnecessary fallback')):
   w=c.predict(self.s,{'opaque':'legal_fit'})
  self.assertAlmostEqual(w.sum(),1.);self.assertFalse(c.decisions[0]['fallback']);self.assertEqual(c.wall['fallback'],0.)
 def test_periodic_uses_shared_fit_without_new_posterior(self):
  model=FakeModel();c=Controller('Periodic-Info',{'DeepSets-KL':model});fit=object()
  with patch('t2b.controllers.information_scores',return_value=np.arange(10)) as scores:
   for _ in range(8):c.predict(self.s,fit)
  self.assertEqual(scores.call_count,2);self.assertIs(scores.call_args[0][0],fit)
  self.assertEqual([i for i,x in enumerate(c.decisions) if x['fallback']],[0,4]);self.assertEqual(len(model.inputs),8)
  self.assertTrue(all(set(s)==set(self.s) for s in model.inputs));self.assertGreater(c.wall['fallback'],0.)
 def test_risk_fallback_does_not_replace_student_boundary(self):
  model=FakeModel();c=Controller('Hybrid-Risk-Info',{'DeepSets-KL':model});self.s['estimate']['z_prob']=[.5,.5]
  with patch('t2b.controllers.information_scores',return_value=np.arange(10)):
   w=c.predict(self.s,object())
  self.assertEqual(w.argmax(),9);self.assertTrue(c.decisions[0]['fallback']);self.assertGreater(c.wall['risk'],0.);self.assertEqual(len(model.inputs),1)
 def test_full_new_roster_and_no_seeds_in_public_manifest(self):
  cfg=json.loads((ROOT/'config.json').read_text());p=public_plan(cfg)
  self.assertEqual(len(p['expected_paths']),624);self.assertEqual(len({s['world_id'] for s in specs(cfg)}),32)
  self.assertEqual(len({(x['world_id'],x['split'],x['R'],x['method']) for x in p['expected_paths']}),624)
  self.assertNotIn('development_seed',str(p));self.assertTrue(all('p' not in s and 'q' not in s for s in p['worlds']))

if __name__=='__main__':unittest.main()
