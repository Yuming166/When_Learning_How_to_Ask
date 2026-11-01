import math
import unittest
import numpy as np
from phase2b.log_glr import log_glr
from phase2a.glr import profile_glr


class LogRiskTests(unittest.TestCase):
    def test_large_R_underflow_and_exact_threshold_transcription(self):
        counts=np.array([[[1,5],[2,3]],[[4,2],[3,1]]]);groups=[[0],[1]]
        cal={'high':[1,1,0],'low':[0,1,0]};types=[[0,0],[]]
        result=log_glr(counts,groups,cal,types,[.8,.8],1024)
        expected=1024+2*math.log(4)+sum(math.log1p(int(n)) for n in counts.sum(axis=2).flat)+math.log(3)
        self.assertAlmostEqual(result['beta'],expected)
        self.assertEqual(math.exp(-1024),0.);self.assertTrue(math.isfinite(result['beta']))
        small=profile_glr(counts,groups,cal,types,[.8,.8],delta=math.exp(-16))
        wrapped=log_glr(counts,groups,cal,types,[.8,.8],16)
        self.assertAlmostEqual(small['beta'],wrapped['beta'])
        for key in ['theta','z','gap','log_likelihood']:self.assertEqual(small[key],wrapped[key])
    def test_reject_invalid_R(self):
        for R in [0,-1,float('inf'),float('nan')]:
            with self.assertRaises(ValueError):log_glr(np.zeros((1,2,2),int),[[0]],{'high':[],'low':[]},[[]],[.8],R)
