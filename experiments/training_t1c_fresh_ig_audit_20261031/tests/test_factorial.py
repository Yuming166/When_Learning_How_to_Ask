import unittest
import numpy as np
from t1c import bootstrap
from t1c.strategies import construct,free_count
from t1a.strategies import WithSolver
from t1b.controller import Residual
from phase2e.strategies import FusedInformation
from phase2a.coefficients import warmup_lp

def public(part):
 groups=[];j=0
 for k in part:groups.append({'targets':list(range(j,j+k))});j+=k
 return {'d':j,'groups':groups,'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8]*len(part)}
def calibration(positive=False):return {'high':([1,1,1,0]*12 if positive else []),'low':([1,0]*24 if positive else [])}
def response(a,t):
 idx=2*a[1]+'AB'.index(a[2]) if a[0]=='query' else 8+a[1]
 y=int((t*13+idx*7+t//3)%5<3)
 return {'answer':y} if a[0]=='query' else {'format':'AB'[y]}
def walk(o,B):
 actions=[]
 for t in range(B):
  a=o.next(set(range(4)));actions.append(a);o.observe(a,response(a,t))
 return actions
class Contract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):warmup_lp()
 def test_update_cadences(self):
  for prefix,expected in [('Block',[8,11,15,19,24,29]),('Fresh',list(range(8,32))),('32',[8])]:
   for objective in ['KL','IG']:
    o=construct(objective+'-'+prefix,public([1,3]),calibration(),16,32);walk(o,32)
    self.assertEqual([e['online'] for e in o.update_history],expected)
 def test_kl_original_equivalence(self):
  a=construct('KL-Block',public([1,3]),calibration(),16,64)
  b=WithSolver(public([1,3]),calibration(),16,'AnalyticReuse',{})
  self.assertEqual(walk(a,64),walk(b,64));np.testing.assert_array_equal(a.counts,b.counts)
 def test_ig_original_equivalence(self):
  a=construct('IG-Block',public([1,3]),calibration(),16,64);b=FusedInformation(public([1,3]),calibration(),16)
  self.assertEqual(walk(a,64),walk(b,64))
 def test_lite_matches_t1b_and_avoids_kl(self):
  for part in [[1,3],[2,2],[4]]:
   for positive in [False,True]:
    a=construct('Fresh-IG-Lite',public(part),calibration(positive),16,64)
    b=Residual(public(part),calibration(positive),16,'Fresh-IG',64)
    self.assertEqual(walk(a,64),walk(b,64))
    self.assertEqual(a.solver.stats['calls'],0);self.assertGreater(b.solver.stats['calls'],0)
    self.assertEqual(len(a.update_history),40)
 def test_executor_only_target_equality_at_common_prefix(self):
  a=construct('IG-Fresh',public([1,3]),calibration(),16,32)
  b=construct('IG-Fresh-Direct',public([1,3]),calibration(),16,32)
  self.assertEqual(walk(a,16),walk(b,16))
  a.next(set(range(4)));b.next(set(range(4)))
  np.testing.assert_array_equal(a.weights,b.weights);self.assertEqual(a.last_update,b.last_update)
 def test_fixed_switch_counts_free_queries(self):
  self.assertEqual([free_count(8,B) for B in [16,32,64]],[0,16,40])
  o=construct('Budget-Switch',public([1,3]),calibration(),16,32);walk(o,32)
  self.assertEqual(o.rule_counts,{'KL':8,'IG':8})
 def test_common_evidence_and_cost_ledger(self):
  for name in ['KL-Fresh','IG-Fresh-Direct','Fresh-IG-Lite','Belief-Gated']:
   o=construct(name,public([2,2]),calibration(True),16,32);walk(o,32)
   self.assertEqual(o.forced.sum(),16);self.assertEqual(o.counts.sum()+sum(map(len,o.types)),32)
   self.assertEqual(o.alpha,3)
 def test_group_uniform_target_space(self):
  o=construct('IG-Group-Fresh',public([1,3]),calibration(True),16,32);walk(o,32)
  self.assertEqual(len(o.update_history),24);self.assertEqual(o.last_estimate['paid_type_target_mass'],float(o.weights[o.L:].sum()))
  for e in o.update_history:
   w=np.array(e['weights']);self.assertAlmostEqual(sum(w),1.)
   for group in o.groups:
    for fmt in range(2):np.testing.assert_allclose(w[[2*j+fmt for j in group]],w[2*group[0]+fmt],atol=0,rtol=0)
 def test_forbidden_constructor_input(self):
  with self.assertRaises(TypeError):construct('Fresh-IG-Lite',public([4]),calibration(),16,32,true_p=.85)
if __name__=='__main__':unittest.main()
