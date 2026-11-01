import unittest
from unittest.mock import patch
from phase2e import bootstrap
from phase2e.policy import run_policy
from phase2e.strategies import POLICIES
class FixtureClient:
    def reset(self):return {'d':1,'groups':[{'targets':[0]}],'rate_domain':{'eta':.05,'levels_unknown':True},'type_accuracy':[.8]}
    def get_calibration(self):return {'high':[],'low':[]}
    def query(self,j,format):return {'answer':1}
    def ask_type(self,group):return {'format':'A'}
    def submit(self,p):self.submitted=p
    def _call(self,*a,**kw):return {'recorded':True}
class StrictFlow(unittest.TestCase):
    def test_all_arms_bounded_strict_gate(self):
        for name in POLICIES:
            x=run_policy(FixtureClient(),name,{'R':2,'online_cap':64,'check_every':16,'milestones':[16,64],'stop_mode':'certified'})
            if x['complete']:self.assertTrue(x['strict_certificate']['certified'])
            else:self.assertIsNone(x['strictly_certified_output'])
    def test_undetermined_never_falls_back_to_float(self):
        with patch('phase2e.policy.certify_stop',return_value={'certified':False,'status':'undetermined'}):
            x=run_policy(FixtureClient(),'Fused-Info',{'R':1,'online_cap':64,'check_every':16,'milestones':[16,64],'stop_mode':'certified'})
        self.assertEqual(x['online'],64);self.assertFalse(x['complete']);self.assertTrue(x['abstained']);self.assertIsNone(x['strictly_certified_output'])
if __name__=='__main__':unittest.main()
