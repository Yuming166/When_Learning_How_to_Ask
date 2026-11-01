"""Accounting invariants independent of any learned policy output."""
import unittest

from t2b.attribution import counts_for, max_gap, prefix_signatures, quantiles, state_metrics


class AttributionTests(unittest.TestCase):
    def test_answer_and_format_axes_are_not_interchanged(self):
        c, f, y = counts_for([[0,1,1],[1,0,0],[0,1,0],[2,0,0]],1,[[0]])
        self.assertEqual(c,[[[0,2],[1,0]]])
        self.assertEqual(f,[[[0,1],[0,0]]])
        self.assertEqual(y,[[1,0]])

    def test_illegal_action_rejected(self):
        for actions in ([[3,0,0]],[[2,0,1]],[[0,2,0]]):
            with self.assertRaises(ValueError):counts_for(actions,1,[[0]])

    def test_query_gap_includes_censored_endpoints(self):
        self.assertEqual(max_gap([2,7],10),5)
        self.assertEqual(max_gap([],10),10)
        self.assertEqual(max_gap([1,2,3],3),1)

    def test_same_time_is_not_same_observed_state(self):
        a=dict(action_trace=[[0,1,0],[1,0,0]],calibration={'high':[],'low':[]})
        b=dict(action_trace=[[1,1,0],[0,0,0]],calibration={'high':[],'low':[]})
        sa=prefix_signatures(a,[1,2],1,[[0]])
        sb=prefix_signatures(b,[1,2],1,[[0]])
        self.assertNotEqual(sa[1],sb[1]);self.assertNotEqual(sa[2],sb[2])

    def test_equal_counts_ignore_irrelevant_action_order(self):
        a=dict(action_trace=[[0,1,0],[1,0,0]],calibration={'high':[],'low':[]})
        b=dict(action_trace=[[1,0,0],[0,1,0]],calibration={'high':[],'low':[]})
        self.assertEqual(prefix_signatures(a,[2],1,[[0]])[2],prefix_signatures(b,[2],1,[[0]])[2])

    def test_statistic_nonfinite_fails_closed(self):
        with self.assertRaises(ValueError):quantiles([1,float('inf')])
        self.assertEqual(quantiles([1,3])['median'],2)

    def test_support_features_do_not_use_correctness(self):
        state=dict(d=1,online=4,counts=[[[1,0],[1,0]]],type_report_counts=[[1,1]],
                   estimate=dict(p=.8,q=.6,theta_prob=[.9],z_prob=[.5]))
        result=state_metrics(state)
        self.assertAlmostEqual(result['observed_type_share'],.5)
        self.assertAlmostEqual(result['min_fact_task_share'],.5)
        self.assertAlmostEqual(result['max_fact_uncertainty'],.1)


if __name__=='__main__':unittest.main()
