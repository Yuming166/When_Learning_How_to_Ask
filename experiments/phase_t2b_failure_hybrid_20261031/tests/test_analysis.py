"""Synthetic arithmetic/coverage tests; no scientific world or model execution."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from t2b.analyze import (CoverageError, aggregate, analyze, break_even,
                         comparison_report, controller_accounting, cost_report,
                         deployment_analysis, paired_analysis,
                         render_figure, training_cost_scenarios)
from t2.analyze import REFERENCE as HISTORICAL_REFERENCE


METHODS = ['AnalyticReuse', 'Fused-Info', 'DeepSets-KL', 'DeepSets-Info']


def fixture():
    cfg = {'data': {'splits': [], 'snapshot_times': [], 'test_worlds_per_split': 0},
           'evaluation': {'splits': ['id', 'ood_calibration'], 'worlds_per_split': 1,
                          'extra_variable_worlds': 1, 'extra_variable_R': 64,
                          'risks': [16, 64], 'methods': METHODS,
                          'readout_budgets': [32, 64]},
           'analysis': {'bootstrap_resamples': 100, 'bootstrap_seed': 731202},
           'go_targets': {'query_ratio_upper': 1.05, 'planning_speedup_lower': 2.}}
    plan = {'expected_paths': [], 'expected_offline': []}; paths = []
    for split in ('eval_id', 'eval_ood_calibration', 'eval_variable'):
        world = split+'_literal_fixture'
        risks = [64] if split == 'eval_variable' else cfg['evaluation']['risks']
        for risk in risks:
            for method in METHODS:
                online = 100+risk+(4 if method.startswith('DeepSets') else 0)
                neural = method.startswith('DeepSets')
                timings = {key: (1. if neural else 4.) for key in
                           ('estimation', 'planning', 'inference', 'glr', 'score_glr', 'gate', 'environment', 'wall', 'cpu')}
                row = {'world_id': world, 'split': split, 'R': risk, 'method': method,
                       'status': 'completed', 'online': online,
                       'costs': {'task': online-4, 'type': 4, 'offline': 8},
                       'total_acquisition': online+8, 'certified': True,
                       'certified_exact': True, 'abstained': False,
                       'final_guess_exact': True, 'timings': timings, 'readouts': []}
                for budget in (32, 64):
                    row['readouts'].append({'budget': budget, 'effective_online': budget,
                                            'costs': {'task': budget-2, 'type': 2, 'offline': 8},
                                            'total_acquisition': budget+8,
                                            'guess_exact': True, 'absorbed': False})
                paths.append(row)
                plan['expected_paths'].append({key: row[key] for key in ('world_id', 'split', 'R', 'method', 'status')})
    return paths, plan, cfg


def historical():
    return training_cost_scenarios({'outer_cpu_seconds': 472., 'prior_failed_world_original_cost_unknown': True},
                                  {'models': {'deepsets_kl': {'outer_cpu_seconds': 5.},
                                              'deepsets_info': {'outer_cpu_seconds': 11.}}})


class AnalysisContract(unittest.TestCase):
    def test_complete_manifest_and_both_references(self):
        paths, plan, cfg = fixture(); result = aggregate(paths, plan, cfg)
        self.assertEqual(result['coverage']['path_records_observed'], 20)
        self.assertEqual(result['coverage']['readout_cells_observed'], 40)
        self.assertEqual({row['reference'] for row in result['paired']}, {'AnalyticReuse', 'Fused-Info'})
        self.assertEqual(HISTORICAL_REFERENCE, 'Fused-Original')
        row = next(row for row in result['paired'] if row['split'] == 'main_pooled' and
                   row['R'] == 'pooled_R' and row['method'] == 'DeepSets-KL' and row['reference'] == 'AnalyticReuse')
        self.assertEqual(row['expected_pairs'], 4)
        self.assertEqual(row['world_clusters'], 2)
        self.assertEqual(row['online_restricted_cost_ratio']['world_clusters'], 2)
        self.assertAlmostEqual(row['online_restricted_cost_ratio']['point'], 576/560)
        self.assertEqual(row['full_path_cpu_speedup']['point'], 4.)
        self.assertTrue(row['latency_flags']['full_path_cpu_descriptive_range_lower_ge_2'])

    def test_missing_duplicate_and_unexpected_records_fail_closed(self):
        paths, plan, cfg = fixture()
        with self.assertRaises(CoverageError): aggregate(paths[:-1], plan, cfg)
        with self.assertRaises(CoverageError): aggregate(paths+[deepcopy(paths[0])], plan, cfg)
        altered = deepcopy(paths); altered[0]['world_id'] = 'unplanned'
        with self.assertRaises(CoverageError): aggregate(altered, plan, cfg)

    def test_failed_pair_keeps_denominator_without_completed_only_mean(self):
        paths, plan, cfg = fixture()
        row = next(row for row in paths if row['method'] == 'DeepSets-KL' and row['split'] == 'eval_id')
        row.update(status='failed', readouts=[])
        result = aggregate(paths, plan, cfg)
        pooled = next(row for row in result['pooled_summaries'] if row['split'] == 'main_pooled' and row['method'] == 'DeepSets-KL')
        self.assertEqual(pooled['applicable'], 4); self.assertEqual(pooled['completed'], 3)
        self.assertIsNone(pooled['online_restricted_cost_mean'])
        paired = next(row for row in result['paired'] if row['split'] == 'main_pooled' and row['R'] == 'pooled_R' and row['method'] == 'DeepSets-KL' and row['reference'] == 'AnalyticReuse')
        self.assertEqual(paired['expected_pairs'], 4); self.assertEqual(paired['complete_pairs'], 3)
        self.assertFalse(paired['paired_metrics_available'])
        self.assertNotIn('online_restricted_cost_ratio', paired)

    def test_new_abstention_not_hidden_by_recovered_reference_abstention(self):
        paths, _, cfg = fixture()
        candidate = next(row for row in paths if row['method'] == 'DeepSets-KL' and row['split'] == 'eval_id' and row['R'] == 16)
        reference = next(row for row in paths if row['method'] == 'AnalyticReuse' and row['split'] == 'eval_ood_calibration' and row['R'] == 16)
        for row in (candidate, reference):
            row.update(certified=False, certified_exact=None, abstained=True)
        results, _ = paired_analysis(paths, cfg)
        row = next(row for row in results if row['split'] == 'main_pooled' and row['R'] == 'pooled_R' and row['method'] == 'DeepSets-KL' and row['reference'] == 'AnalyticReuse')
        self.assertEqual(row['certification_counts']['candidate_abstained'], 1)
        self.assertEqual(row['certification_counts']['reference_abstained'], 1)
        self.assertEqual(row['certification_counts']['additional_abstention_pairs'], 1)
        self.assertEqual(row['certification_counts']['recovered_reference_abstention_pairs'], 1)
        self.assertTrue(row['additional_cap_flags']['no_more_abstentions_in_total'])
        self.assertFalse(row['additional_cap_flags']['no_additional_abstention_pairs'])
        self.assertFalse(row['all_original_engineering_flags_pass'])

    def test_caps_remain_in_cost_and_wrong_certificate_fails_strict_gate(self):
        paths, plan, cfg = fixture()
        row = next(row for row in paths if row['method'] == 'DeepSets-KL' and row['split'] == 'eval_id' and row['R'] == 16)
        row.update(online=6144, total_acquisition=6152, costs={'task': 6140, 'type': 4, 'offline': 8},
                   certified=False, certified_exact=None, abstained=True)
        result = aggregate(paths, plan, cfg)
        summary = next(item for item in result['path_summaries'] if item['method'] == row['method'] and item['split'] == row['split'] and item['R'] == row['R'])
        self.assertEqual(summary['online_restricted_cost_mean'], 6144)
        row.update(certified=True, certified_exact=False, abstained=False, final_guess_exact=False)
        result = aggregate(paths, plan, cfg)
        paired = next(item for item in result['paired'] if item['method'] == row['method'] and item['split'] == row['split'] and item['R'] == row['R'] and item['reference'] == 'AnalyticReuse')
        self.assertFalse(paired['additional_cap_flags']['no_wrong_candidate_certificates'])
        self.assertFalse(paired['all_original_engineering_flags_pass'])

    def test_training_scenarios_preserve_unknown_cost_and_shared_charge(self):
        costs = historical(); charges = costs['method_charges_cpu_seconds']
        self.assertEqual(charges['DeepSets-KL']['known_construction_plus_fit'], 477.)
        self.assertEqual(charges['DeepSets-Info']['fit_only'], 11.)
        self.assertEqual(charges['Hybrid-Risk-Info']['fit_only'], 5.)
        self.assertEqual(charges['Fused-Info']['known_construction_plus_fit'], 0.)
        self.assertTrue(costs['original_failed_prefix_cost_unknown'])

    def test_break_even_regions_and_amortization_arithmetic(self):
        row = break_even(4., -3., 5., 100)
        self.assertAlmostEqual(row['lambda_threshold_cpu_seconds_per_query'], 2.95/4)
        self.assertEqual(row['advantage_region'], '0 <= lambda < threshold')
        self.assertEqual(break_even(4., -3., 5., 1)['advantage_region'], 'none for nonnegative lambda')
        row = break_even(-4., 3., 0., 100)
        self.assertEqual(row['lambda_threshold_cpu_seconds_per_query'], .75)
        self.assertEqual(row['advantage_region'], 'lambda > threshold')
        self.assertEqual(break_even(0., -3., 0., 1)['advantage_region'], 'all nonnegative lambda')
        self.assertEqual(break_even(0., 0., 0., 1)['advantage_region'], 'tie for all lambda')
        with self.assertRaises(CoverageError): break_even(1., -1., 0., 0)

    def test_deployment_all_scenarios_and_failed_scope_unavailable(self):
        paths, _, cfg = fixture(); _, vectors = paired_analysis(paths, cfg)
        rows = deployment_analysis(vectors, historical())
        row = next(row for row in rows if row['method'] == 'DeepSets-KL' and row['reference'] == 'AnalyticReuse')
        self.assertEqual(row['delta_acquisition_per_deployment'], 4.)
        self.assertEqual(row['delta_full_path_cpu_seconds'], -3.)
        self.assertEqual(len(row['scenarios']), 12)
        selected = next(vector for vector in vectors if vector['method'] == 'DeepSets-KL' and vector['reference'] == 'AnalyticReuse' and vector['split'] != 'eval_variable')
        selected['complete_pair'] = False
        row = next(row for row in deployment_analysis(vectors, historical()) if row['method'] == 'DeepSets-KL' and row['reference'] == 'AnalyticReuse')
        self.assertFalse(row['available']); self.assertEqual(row['scenarios'], [])

    def test_reports_and_standalone_scientific_figure(self):
        paths, plan, cfg = fixture(); result = aggregate(paths, plan, cfg)
        text = comparison_report(result)
        self.assertIn('中途预算', text)
        result['controller_accounting'] = controller_accounting(paths)
        costs = historical()
        report = cost_report(result, costs, deployment_analysis(result['paired_vectors'], costs), {'evaluation_execution': {}})
        self.assertIn('known_construction_plus_fit', report)
        self.assertIn('原始前缀成本未知', report)
        with tempfile.TemporaryDirectory() as directory:
            files = render_figure(result, Path(directory))
            self.assertEqual(len(files), 2)
            self.assertTrue((Path(directory)/'paired_query_cpu.png').read_bytes().startswith(b'\x89PNG'))
            self.assertTrue((Path(directory)/'paired_query_cpu.pdf').read_bytes().startswith(b'%PDF'))

    def test_nested_controller_accounting_does_not_fill_unknowns(self):
        paths, _, _ = fixture(); rows = controller_accounting(paths)
        self.assertTrue(all(not row['component_accounting_complete'] for row in rows))
        self.assertTrue(all('wall_seconds_total' not in row for row in rows))
        for row in paths:
            row['controller_decisions'] = [{'fallback': True}, {'fallback': False}]
            row['controller_accounting'] = {'wall': {'neural': .1, 'risk': .2, 'fallback': .3},
                                            'cpu': {'neural': .01, 'risk': .02, 'fallback': .03},
                                            'controller_enclosing_wall': .7, 'overhead_wall': .1,
                                            'fallback_calls': 1, 'allocation_calls': 2}
        row = next(row for row in controller_accounting(paths) if row['method'] == 'DeepSets-KL')
        self.assertEqual(row['allocation_calls_total'], 10)
        self.assertEqual(row['fallback_calls_total'], 5)
        self.assertAlmostEqual(row['wall_seconds_total']['fallback'], 1.5)
        self.assertAlmostEqual(row['cpu_seconds_total']['fallback'], .15)

    def test_save_once_reports_block_before_any_inputs_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'MATCHED_COMPARISON_RESULTS.md').write_text('retained')
            with self.assertRaises(FileExistsError): analyze(root)
            self.assertEqual((root/'MATCHED_COMPARISON_RESULTS.md').read_text(), 'retained')
            self.assertFalse((root/'artifacts/analysis').exists())


if __name__ == '__main__':
    unittest.main()
