import unittest
from interfaces.rl_adapter import MacroBeliefInterface
class Observations:
 def __init__(self):self.paid=0
 def reset(self):return {'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8,.8],'episode_id':'must_not_enter_state'}
 def get_calibration(self):return {'high':[],'low':[]}
 def query(self,j,m):self.paid+=1;return {'answer':1}
 def ask_type(self,g):self.paid+=1;return {'format':'A'}
class InterfaceTest(unittest.TestCase):
 def test_prepare_idempotence_and_no_id_reward(self):
  c=Observations();e=MacroBeliefInterface(c,16,17);a=e.prepare();b=e.prepare();self.assertEqual(a,b)
  self.assertEqual(c.paid,0);self.assertNotIn('episode_id',a);self.assertNotIn('reward',a)
 def test_one_action_one_cost_terminal_lock(self):
  c=Observations();e=MacroBeliefInterface(c,16,17)
  for t in range(17):
   s=e.prepare();macro=0 if s['forced'] else 2
   if not s['legal_macro_mask'][macro]:macro=next(i for i,v in enumerate(s['legal_macro_mask']) if v)
   r=e.act(macro);self.assertIsNone(r['reward']);self.assertEqual(c.paid,t+1)
  self.assertTrue(r['done']);terminal=e.finalize();self.assertEqual(len(terminal['guess']),4);self.assertIsNone(terminal['reward'])
  with self.assertRaises(RuntimeError):e.prepare()
 def test_invalid_action_makes_no_query(self):
  c=Observations();e=MacroBeliefInterface(c,16,17);e.prepare()
  with self.assertRaises(ValueError):e.act(7)
  self.assertEqual(c.paid,0)
if __name__=='__main__':unittest.main()
