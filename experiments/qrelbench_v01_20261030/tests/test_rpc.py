import multiprocessing as mp
import time
import unittest
from qrelbench.evaluate import evaluate_job,build_jobs,ROOT
from qrelbench.policies import NAMES
from qrelbench.rpc import worker,send
import json


class RPCChecks(unittest.TestCase):
    def test_real_spawn_public_interface_and_oracle_cost(self):
        results={}
        for name in NAMES:
            parent,child=mp.get_context('spawn').Pipe()
            process=mp.get_context('spawn').Process(target=worker,args=(child,name));process.start();child.close()
            job={'protocol':'fixed_budget','scenario':'perfect_type','partition':[2,2],'index':100100,
                 'online_cap':26 if name=='Direct Type Query' else 24,'calibration_size':32,
                 'delta':None,'p':.85,'q':.6,'s':1.,'channel':'iid'}
            try:
                r,details=evaluate_job(parent,name,job,77,time.monotonic()+20);results[name]=(r,details)
                self.assertEqual(r['online'],job['online_cap']);self.assertTrue(r['completed'])
                self.assertEqual(r['total_acquisition'],job['online_cap']+64)
                send(parent,None);process.join(timeout=5);self.assertEqual(process.exitcode,0)
            finally:
                if process.is_alive():process.terminate();process.join()
                parent.close()
        a,da=results['Direct Type Query'];b,db=results['Oracle Format']
        self.assertEqual(da['counts'],db['counts']);self.assertEqual(a['exact'],b['exact'])
        self.assertEqual(a['costs']['type'],2);self.assertEqual(b['costs']['type'],0)
    def test_planned_bound_and_split_scope(self):
        cfg=json.loads((ROOT/'configs/development.json').read_text());jobs=build_jobs(cfg)
        maximum=sum(j['online_cap'] for j in jobs)*len(NAMES)
        self.assertLessEqual(maximum,cfg['limits']['maximum_online_actions'])
        self.assertTrue(all(100000<=j['index']<200000 for j in jobs))
        cfg['split']='test'
        with self.assertRaises(ValueError):build_jobs(cfg)
