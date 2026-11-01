import json
import time
import unittest
from phase2d.runner import evaluate_job


class ScriptedConnection:
    def __init__(self):
        self.messages=iter([
            {'method':'reset','args':{}},
            {'method':'get_calibration','args':{}},
            {'method':'query','args':{'j':0,'format':'A'}},
            {'worker_error':'injected_failure_before_first_snapshot'},
        ])
        self.responses=[]
    def poll(self,timeout):return True
    def recv_bytes(self):return json.dumps(next(self.messages)).encode()
    def send_bytes(self,data):self.responses.append(json.loads(data))


class FailureReceiptTests(unittest.TestCase):
    def test_exact_partial_observations_survive_failure_before_snapshot(self):
        conn=ScriptedConnection();records=[];counters={'task':0,'type':0,'offline':0}
        job={'partition':[1,3],'alpha':3/16,'R':16,'index':419010,'replicate':0,
             'p':.85,'q':.6,'s':.8,'eta':.05,'M':3,'online_cap':64,'check_every':16,
             'milestones':[32,64],'stop_mode':'floating','channel':'iid',
             'protocol':'fixed_confidence','scenario':'failure_technical_fixture'}
        with self.assertRaisesRegex(RuntimeError,'injected_failure'):
            evaluate_job(conn,'D-RRC-NoType',job,'fixed-failure-technical-fixture',
                time.monotonic()+5,counters,on_failure=lambda a,b:records.append((a,b)))
        self.assertEqual(counters,{'task':1,'type':0,'offline':6})
        self.assertEqual(len(records),1);row,private=records[0]
        self.assertEqual(row['status'],'failed');self.assertEqual(row['snapshot_count'],0)
        self.assertEqual(row['online_observed'],1);self.assertEqual(row['costs_observed'],counters)
        self.assertEqual(sum(sum(pair) for target in row['counts_observed'] for pair in target),1)
        self.assertFalse(row['terminal_stopping_cost_observed'])
        self.assertFalse(row['submitted_before_failure'])
        self.assertEqual(row['partial_trace_sha256'],private['partial_trace_sha256'])
        self.assertEqual(len(private['trace_prefix']),3)
        self.assertEqual(len(row['calibration_observed']['high']),3)


if __name__=='__main__':unittest.main()
