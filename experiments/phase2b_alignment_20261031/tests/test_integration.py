import json
import multiprocessing as mp
import time
import unittest
from phase2b.runner import ROOT,jobs,public_job,evaluate_job
from phase2b.policy import POLICIES,worker
from qrelbench.rpc import send


class IntegrationTests(unittest.TestCase):
    def test_globally_independent_worlds_and_caps(self):
        cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
        self.assertEqual(len(plan),64);self.assertEqual(len({j['index'] for j in plan}),64)
        self.assertEqual(sum(j['online_cap'] for j in plan)*5,2785280)
        self.assertEqual(sum(2*j['M'] for j in plan)*5,326400)
        for j in plan:
            self.assertEqual(set(public_job(j)),{'R','online_cap','check_every','milestones'})
            self.assertLessEqual(j['check_every'],32)

    def test_actual_confined_workers_empty_and_small_calibration(self):
        for name in POLICIES:
            parent,child=mp.get_context('spawn').Pipe();process=mp.get_context('spawn').Process(target=worker,args=(child,name));process.start();child.close()
            try:
                for R,M in [(16,0),(1024,3)]:
                    job={'partition':[1,3],'alpha':M/R,'R':R,'index':219000,'replicate':0,
                        'p':.85,'q':.6,'s':.8,'eta':.05,'M':M,'online_cap':64,'check_every':16,
                        'milestones':[32,64],'channel':'iid','protocol':'fixed_confidence','scenario':'unit'}
                    counters={'task':0,'type':0,'offline':0}
                    final,_,snapshots=evaluate_job(parent,name,job,'separate-technical-fixture',time.monotonic()+60,counters)
                    self.assertEqual(final['online'],64);self.assertEqual(counters['task']+counters['type'],64)
                    self.assertEqual(counters['offline'],2*M);self.assertEqual(len(snapshots),2)
                    self.assertTrue(final['censored']);self.assertFalse(final['complete'])
                    self.assertTrue(final['isolation']['single_thread_bootstrap'])
                    self.assertEqual(final['fit']['log_inverse_delta'],R)
                send(parent,None);process.join(timeout=5);self.assertEqual(process.exitcode,0)
            finally:
                if process.is_alive():process.terminate();process.join(timeout=5)
                parent.close()
