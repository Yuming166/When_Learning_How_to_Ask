import json
import multiprocessing as mp
import time
import unittest
from phase2a.runner import jobs,ROOT,evaluate_job,public_job
from phase2a.policy import POLICIES,worker
from qrelbench.rpc import send


class IntegrationTests(unittest.TestCase):
    def test_plan_bounded_and_no_private_job_fields(self):
        cfg=json.loads((ROOT/'config.json').read_text());plan=jobs(cfg)
        self.assertLessEqual(sum(j['online_cap'] for j in plan)*6,cfg['limits']['online_actions'])
        self.assertLessEqual(sum(len(j['snapshot_budgets']) for j in plan)*6,cfg['limits']['endpoint_decodes'])
        for j in plan:
            public=public_job(j)
            self.assertTrue(set(public).isdisjoint({'p','q','seed','index','scenario','partition','alpha'}))
    def test_all_policies_actual_confined_rpc_and_snapshot_costs(self):
        for name in POLICIES:
            p,c=mp.get_context('spawn').Pipe();process=mp.get_context('spawn').Process(target=worker,args=(c,name));process.start();c.close()
            job={'protocol':'fixed_budget','scenario':'unit','partition':[2,2],'alpha':0,'R':4,'index':118000,
                 'p':.85,'q':.6,'s':.8,'channel':'iid','M':0,'delta':math_exp_minus4(),
                 'online_cap':48,'check_every':16,'snapshot_budgets':[32,48],'update_every':32}
            counters={'task':0,'type':0,'offline':0}
            try:
                result,private,snaps=evaluate_job(p,name,job,'unit-private-seed',time.monotonic()+30,counters)
                self.assertEqual(result['online'],48);self.assertEqual(counters['task']+counters['type'],48)
                self.assertEqual(counters['offline'],0);self.assertEqual(len(snaps),2)
                self.assertTrue(result['complete']);self.assertTrue(result['isolation']['single_thread_bootstrap'])
                send(p,None);process.join(timeout=5);self.assertEqual(process.exitcode,0)
            finally:
                if process.is_alive():process.terminate();process.join()
                p.close()


def math_exp_minus4():
    import math
    return math.exp(-4)
