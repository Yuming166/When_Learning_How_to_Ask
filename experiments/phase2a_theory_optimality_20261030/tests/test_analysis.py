import unittest
from phase2a.analyze import confidence_at


class AnalysisTests(unittest.TestCase):
    def test_censored_wrong_and_completed_denominators(self):
        rows=[{'online':32,'complete':True,'exact':True,'online_cap':128},
              {'online':64,'complete':True,'exact':False,'online_cap':128},
              {'online':128,'complete':False,'exact':True,'online_cap':128}]
        early=confidence_at(rows,48);late=confidence_at(rows,128)
        self.assertEqual((early['n'],early['completed'],early['wrong_certificates']),(3,1,0))
        self.assertEqual((late['n'],late['completed'],late['wrong_certificates']),(3,2,1))
        self.assertEqual(late['mean_min_T_B'],224/3)
        self.assertAlmostEqual(late['wrong_certificate_fraction_all'],1/3)
        with self.assertRaises(ValueError):confidence_at(rows,129)
