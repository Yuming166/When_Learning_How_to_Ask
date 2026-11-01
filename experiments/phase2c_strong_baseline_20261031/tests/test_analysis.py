import json
import unittest
from pathlib import Path
import numpy as np
from phase2c import bootstrap
from phase2c.analyze import population_information, information_at_weights, expand_weights, confirmation_plan
from phase2b.analyze import expected_information, confidence_at
from phase2a.coefficients import solve_allocation


class AnalysisTests(unittest.TestCase):
    def test_population_fractional_counts_match_prior_integer_reference(self):
        n=np.array([[5,2],[3,7],[3,7],[3,7]])
        bits=np.zeros((4,2,2),int);bits[:,:,0]=n
        old=expected_information(bits,[[0]*2,[0]*4],[0,1],[1,3],.85,.6,3)
        new=population_information(n,[2,4],[0,1],[1,3],.85,.6,3)
        self.assertAlmostEqual(old,new,places=11)
        scaled=population_information(n*.25,[.5,1],[0,1],[1,3],.85,.6,.75)
        self.assertAlmostEqual(new*.25,scaled,places=11)

    def test_oriented_optimum_feasible_and_missing_sign_not_identified(self):
        for part,alpha,types in [([1,3],0,[1,0]),([4],3,[1])]:
            fit=solve_allocation(part,.85,.6,alpha,.8)
            w=expand_weights(fit,part,types)
            self.assertAlmostEqual(w.sum(),1.,places=12)
            info=information_at_weights(w,fit['K'],alpha,types,part,.85,.6)
            self.assertGreaterEqual(info,1-1e-7)
        n=np.ones((4,2))*10;n[1]=0
        self.assertAlmostEqual(population_information(n,[20,20],[0,1],[1,3],.85,.6,5),0.,places=11)

    def test_censoring_uses_full_world_denominator(self):
        rows=[dict(online=32,complete=True,exact=True,online_cap=128),
              dict(online=64,complete=True,exact=False,online_cap=128),
              dict(online=128,complete=False,exact=True,online_cap=128)]
        r=confidence_at(rows,128)
        self.assertEqual((r['n'],r['completed'],r['wrong_certificates']),(3,2,1))
        self.assertAlmostEqual(r['mean_min_T_B'],224/3)

    def test_confirmation_planning_consumes_no_seed_or_world(self):
        cfg=json.loads((bootstrap.ROOT/'config.json').read_text());rows=[]
        for part in [[1,3],[4]]:
            for i in range(8):
                for policy,n in [('Aligned Tracking',6000+i*32),('D-RRC',9000+i*16 if len(part)==2 else 6000+i*32)]:
                    rows.append(dict(partition=part,alpha=0,R=1024,index=i,policy=policy,online=n,censored=False))
        p=confirmation_plan(rows,cfg)
        self.assertEqual(p['status'],'FROZEN_NOT_EXECUTED');self.assertIsNone(p['seed'])
        self.assertEqual(p['confirmatory_worlds_consumed'],0)
        self.assertEqual([r['exact_n_worlds'] for r in p['configurations']],[24,24])


if __name__=='__main__':unittest.main()
