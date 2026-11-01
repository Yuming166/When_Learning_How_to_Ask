import unittest
import numpy as np
from phase2b.analyze import confidence_at,expected_information
from phase2a.coefficients import inner,kl


class StatisticalContractTests(unittest.TestCase):
    def test_censored_denominator_and_wrong_certification(self):
        rows=[{'online':32,'complete':True,'exact':True,'online_cap':128},
              {'online':64,'complete':True,'exact':False,'online_cap':128},
              {'online':128,'complete':False,'exact':True,'online_cap':128}]
        out=confidence_at(rows,128)
        self.assertEqual((out['n'],out['completed'],out['wrong_certificates']),(3,2,1))
        self.assertEqual(out['mean_min_T_B'],224/3)
        self.assertAlmostEqual(out['wrong_fraction_all'],1/3)
        self.assertEqual(confidence_at(rows,48)['wrong_certificates'],0)

    def test_unsymmetrized_population_information(self):
        part=[1,3];types=[1,0];counts=np.zeros((4,2,2),int);a=[5,7];b=[2,3]
        for j,g in enumerate([0,1,1,1]):counts[j,types[g],0]=a[g];counts[j,1-types[g],0]=b[g]
        reports=[[0]*2,[1]*4];x=np.array(a+b+[2,4],float);kappa=[kl(.8,.2)]*2
        expected=min(inner(part,.85,.6,3,x,mask,h,kappa)['value'] for mask in range(4) for h in range(2))
        observed=expected_information(counts,reports,types,part,.85,.6,3)
        self.assertAlmostEqual(expected,observed,places=11)
        # A completely unobserved sign is not identifiable even when many
        # queries were spent on another coordinate of its sharing group.
        counts[1]=0
        self.assertAlmostEqual(expected_information(counts,reports,types,part,.85,.6,3),0.,places=11)
