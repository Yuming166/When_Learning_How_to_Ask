"""Frozen descriptive matched analysis; no model loading, fitting or worlds.

Key coverage, path summaries and whole-world ratio resampling are reused from
frozen T2. References are explicit arguments; historical module globals never
change. Restricted capped costs are not untruncated stopping-time estimates.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from . import bootstrap
from t2.analyze import (CoverageError, RANGE_NOTE, TIMINGS, _finite, _require,
                        clustered_ratio, summarize_paths, validate_coverage)


ROOT = bootstrap.ROOT
REFERENCES = ('AnalyticReuse', 'Fused-Info')
DEPLOYMENT_COUNTS = (1, 100, 1000, 10000)
REPORTS = ('MATCHED_COMPARISON_RESULTS.md', 'DEPLOYMENT_COST_ANALYSIS.md')


def _scopes(row):
    scopes = [(row['split'], row['R']), (row['split'], 'pooled_R')]
    if row['split'] != 'eval_variable':
        scopes += [('main_pooled', row['R']), ('main_pooled', 'pooled_R')]
    return scopes


def _bound(statistic, side):
    value = statistic.get('descriptive_bootstrap_range', [{}, {}])[side]
    return None if value.get('infinite') else value.get('value')


def paired_analysis(paths, config, references=REFERENCES):
    """All planned pairs; any failed pair makes that scope unavailable."""
    indexed = {}
    for row in paths:
        key = (row['world_id'], row['R'], row['method'])
        _require(key not in indexed, 'Duplicate path identity in paired analysis')
        indexed[key] = row
    _require(len(set(references)) == len(references), 'Duplicate reference')
    vectors = []
    for reference in references:
        for row in paths:
            if row['method'] == reference or row['status'] == 'not_applicable':
                continue
            key = (row['world_id'], row['R'], reference)
            _require(key in indexed, 'Missing planned reference: ' + str(key))
            baseline = indexed[key]
            complete = row['status'] == baseline['status'] == 'completed'
            item = {'world_id': row['world_id'], 'split': row['split'], 'R': row['R'],
                    'method': row['method'], 'reference': reference,
                    'complete_pair': complete, 'candidate_status': row['status'],
                    'reference_status': baseline['status']}
            if complete:
                for prefix, source in (('candidate', row), ('reference', baseline)):
                    item.update({prefix+'_online': source['online'],
                                 prefix+'_total_acquisition': source['total_acquisition'],
                                 prefix+'_inclusive_compute': sum(source['timings'][k] for k in ('estimation', 'planning', 'inference')),
                                 prefix+'_cpu': source['timings']['cpu'],
                                 prefix+'_wall': source['timings']['wall'],
                                 prefix+'_certified': source['certified'],
                                 prefix+'_certified_exact': source['certified_exact'],
                                 prefix+'_abstained': source['abstained']})
            vectors.append(item)
    groups = defaultdict(list)
    for row in vectors:
        for split, risk in _scopes(row):
            groups[(split, risk, row['method'], row['reference'])].append(row)
    bs = {'resamples': config['analysis']['bootstrap_resamples'],
          'seed': config['analysis']['bootstrap_seed']}
    results = []
    for (split, risk, method, reference), rows in sorted(groups.items(), key=lambda item: str(item[0])):
        complete = all(row['complete_pair'] for row in rows)
        result = {'split': split, 'R': risk, 'method': method, 'reference': reference,
                  'expected_pairs': len(rows), 'complete_pairs': sum(row['complete_pair'] for row in rows),
                  'world_clusters': len({row['world_id'] for row in rows}),
                  'paired_metrics_available': complete}
        if complete:
            worlds = [row['world_id'] for row in rows]
            for metric, numerator, denominator in (
                ('online_restricted_cost_ratio', 'candidate_online', 'reference_online'),
                ('total_acquisition_restricted_cost_ratio', 'candidate_total_acquisition', 'reference_total_acquisition'),
                ('inclusive_compute_speedup', 'reference_inclusive_compute', 'candidate_inclusive_compute'),
                ('full_path_cpu_speedup', 'reference_cpu', 'candidate_cpu'),
                ('full_path_wall_speedup', 'reference_wall', 'candidate_wall'),
            ):
                result[metric] = clustered_ratio(worlds, [row[numerator] for row in rows], [row[denominator] for row in rows], **bs)
            counts = {}
            for prefix in ('candidate', 'reference'):
                counts[prefix+'_certified'] = sum(row[prefix+'_certified'] for row in rows)
                counts[prefix+'_wrong_certificates'] = sum(row[prefix+'_certified'] and row[prefix+'_certified_exact'] is not True for row in rows)
                counts[prefix+'_abstained'] = sum(row[prefix+'_abstained'] for row in rows)
            counts['additional_abstention_pairs'] = sum(row['candidate_abstained'] and not row['reference_abstained'] for row in rows)
            counts['recovered_reference_abstention_pairs'] = sum(not row['candidate_abstained'] and row['reference_abstained'] for row in rows)
            result['certification_counts'] = counts
            strict = all(row['candidate_certified'] and row['reference_certified'] and
                         row['candidate_certified_exact'] is True and row['reference_certified_exact'] is True and
                         not row['candidate_abstained'] and not row['reference_abstained'] for row in rows)
            query_upper = _bound(result['online_restricted_cost_ratio'], 1)
            speed_lower = _bound(result['inclusive_compute_speedup'], 0)
            result['engineering_flags'] = {
                'all_candidate_and_reference_paths_certified_correctly_without_abstention': strict,
                'query_descriptive_range_upper_le_1_05': query_upper is not None and query_upper <= config['go_targets']['query_ratio_upper'],
                'inclusive_speedup_descriptive_range_lower_ge_2': speed_lower is not None and speed_lower >= config['go_targets']['planning_speedup_lower'],
            }
            result['latency_flags'] = {'full_path_cpu_descriptive_range_lower_ge_2': (_bound(result['full_path_cpu_speedup'], 0) is not None and _bound(result['full_path_cpu_speedup'], 0) >= config['go_targets']['planning_speedup_lower'])}
            result['additional_cap_flags'] = {
                'no_additional_abstention_pairs': counts['additional_abstention_pairs'] == 0,
                'no_more_abstentions_in_total': counts['candidate_abstained'] <= counts['reference_abstained'],
                'no_wrong_candidate_certificates': counts['candidate_wrong_certificates'] == 0,
            }
            result['all_original_engineering_flags_pass'] = all(result['engineering_flags'].values())
        else:
            result.update(unavailable_reason='At least one planned pair failed; completed-pair-only estimates forbidden',
                          all_original_engineering_flags_pass=False)
        result['decision'] = 'manual_review_required; descriptive ranges do not establish population noninferiority'
        results.append(result)
    return results, sorted(vectors, key=lambda row: (row['reference'], row['split'], row['world_id'], row['R'], row['method']))


def aggregate(paths, plan, config):
    budgets = config['evaluation']['readout_budgets']
    coverage = validate_coverage(paths, [], plan, config, budgets)
    summaries, readouts = summarize_paths(paths, budgets)
    paired, vectors = paired_analysis(paths, config)
    pooled = []
    for scope in ('main_pooled', 'eval_variable'):
        for method in config['evaluation']['methods']:
            rows = [row for row in paths if row['method'] == method and
                    (row['split'] == 'eval_variable' if scope == 'eval_variable' else row['split'] != 'eval_variable')]
            applicable = [row for row in rows if row['status'] != 'not_applicable']
            completed = [row for row in applicable if row['status'] == 'completed']
            complete = bool(applicable) and len(completed) == len(applicable)
            pooled.append({'split': scope, 'method': method, 'expected_paths': len(rows),
                           'applicable': len(applicable), 'completed': len(completed),
                           'failed': len(applicable)-len(completed),
                           'certified': sum(row['certified'] for row in completed),
                           'wrong_certificates': sum(row['certified'] and row['certified_exact'] is not True for row in completed),
                           'abstained': sum(row['abstained'] for row in completed),
                           'online_restricted_cost_mean': float(np.mean([row['online'] for row in completed])) if complete else None,
                           'total_acquisition_restricted_cost_mean': float(np.mean([row['total_acquisition'] for row in completed])) if complete else None,
                           'full_path_cpu_mean': float(np.mean([row['timings']['cpu'] for row in completed])) if complete else None,
                           'full_path_wall_mean': float(np.mean([row['timings']['wall'] for row in completed])) if complete else None,
                           'timing_seconds_total': {key: sum(row['timings'][key] for row in completed) if complete else None for key in TIMINGS}})
    return {'coverage': coverage, 'path_summaries': summaries, 'readouts': readouts,
            'pooled_summaries': pooled, 'paired': paired, 'paired_vectors': vectors,
            'references': list(REFERENCES), 'range_note': RANGE_NOTE,
            'decision': 'manual_review_required', 'config': config}


def training_cost_scenarios(preparation, training):
    """Explicit known partial historical CPU charges, never a full-project total."""
    prep = _finite(preparation['outer_cpu_seconds'], 'historical preparation CPU')
    costs = {'DeepSets-KL': _finite(training['models']['deepsets_kl']['outer_cpu_seconds'], 'KL fit CPU'),
             'DeepSets-Info': _finite(training['models']['deepsets_info']['outer_cpu_seconds'], 'Info fit CPU')}
    result = {}
    for method in ('Fused-Original-Cold', 'AnalyticReuse', 'Fused-Info',
                   'DeepSets-KL', 'DeepSets-Info', 'Hybrid-Risk-Info', 'Hybrid-Risk-Reuse', 'Periodic-Info'):
        neural = method not in ('Fused-Original-Cold', 'AnalyticReuse', 'Fused-Info')
        fit = costs['DeepSets-Info' if method == 'DeepSets-Info' else 'DeepSets-KL'] if neural else 0.
        result[method] = {'sunk_training': 0., 'fit_only': fit,
                          'known_construction_plus_fit': prep+fit if neural else 0.}
    return {'method_charges_cpu_seconds': result,
            'preparation_cpu_seconds': prep, 'fit_cpu_seconds': costs,
            'original_failed_prefix_cost_unknown': bool(preparation.get('prior_failed_world_original_cost_unknown', True)),
            'scope': 'known stage CPU after imports; construction charged in full to one deployed neural policy; excludes unknown initial failure, human time, tuning, old evaluation and future cold initialization'}


def break_even(delta_queries, delta_cpu, training_charge, deployments):
    """DeltaC/c_CPU = lambda*DeltaN + DeltaCPU + training_charge/M.

    lambda is nonnegative CPU-seconds-equivalent per acquired observation.
    A threshold is a point-estimate cost scenario, not an inferential guarantee.
    """
    for value, label in ((delta_cpu, 'delta_cpu'), (delta_queries, 'delta_queries')):
        _finite(value, label, nonnegative=False)
    _finite(training_charge, 'training charge')
    _require(type(deployments) is int and deployments > 0, 'Positive integer deployment count required')
    intercept = delta_cpu + training_charge/deployments
    result = {'delta_queries': float(delta_queries), 'delta_path_cpu_seconds': float(delta_cpu),
              'training_charge_cpu_seconds': float(training_charge), 'deployments': deployments,
              'training_charge_per_deployment_cpu_seconds': float(training_charge/deployments),
              'intercept_cpu_seconds': float(intercept), 'lambda_threshold_cpu_seconds_per_query': None,
              'cold_initialization_assumption': 'already loaded service; any differential cold initialization adds DeltaInitCPU/M to intercept'}
    if delta_queries > 0:
        if intercept < 0:
            result.update(advantage_region='0 <= lambda < threshold', lambda_threshold_cpu_seconds_per_query=-intercept/delta_queries)
        else:
            result['advantage_region'] = 'none for nonnegative lambda'
    elif delta_queries < 0:
        if intercept < 0:
            result['advantage_region'] = 'all nonnegative lambda'
        elif intercept == 0:
            result['advantage_region'] = 'lambda > 0; tie at zero'
        else:
            result.update(advantage_region='lambda > threshold', lambda_threshold_cpu_seconds_per_query=-intercept/delta_queries)
    else:
        result['advantage_region'] = 'all nonnegative lambda' if intercept < 0 else 'tie for all lambda' if intercept == 0 else 'none for nonnegative lambda'
    return result


def deployment_analysis(paired_vectors, historical_costs):
    groups = defaultdict(list)
    for row in paired_vectors:
        if row['split'] == 'eval_variable':
            continue
        groups[(row['method'], row['reference'])].append(row)
    results = []
    for (method, reference), rows in sorted(groups.items()):
        record = {'split': 'main_pooled', 'R': 'pooled_R', 'method': method, 'reference': reference,
                  'expected_pairs': len(rows), 'world_clusters': len({row['world_id'] for row in rows}),
                  'available': all(row['complete_pair'] for row in rows), 'scenarios': []}
        if record['available']:
            # Paired calibration costs are equal; use all acquired observations
            # explicitly, so this cancellation is checked by the data arithmetic.
            delta_N = float(np.mean([row['candidate_total_acquisition']-row['reference_total_acquisition'] for row in rows]))
            delta_cpu = float(np.mean([row['candidate_cpu']-row['reference_cpu'] for row in rows]))
            record.update(delta_acquisition_per_deployment=delta_N, delta_full_path_cpu_seconds=delta_cpu)
            for scenario, charge in historical_costs['method_charges_cpu_seconds'][method].items():
                for deployments in DEPLOYMENT_COUNTS:
                    record['scenarios'].append({'training_scenario': scenario,
                                                **break_even(delta_N, delta_cpu, charge, deployments)})
        else:
            record['unavailable_reason'] = 'At least one planned pair failed; no completed-pair-only deployment estimate'
        results.append(record)
    return results


def controller_accounting(paths):
    """Nested controller counters are diagnostics, not extra full-path charges."""
    groups = defaultdict(list)
    for row in paths:
        groups[row['method']].append(row)
    result = []
    for method, rows in sorted(groups.items()):
        available = all(row['status'] == 'completed' for row in rows)
        decisions = [decision for row in rows for decision in row.get('controller_decisions', [])]
        accounting = [row.get('controller_accounting') for row in rows]
        component_complete = available and all(isinstance(item, dict) for item in accounting)
        item = {'method': method, 'applicable_paths': len(rows), 'all_completed': available,
                'decisions_observed': len(decisions),
                'fallback_decisions_observed': sum(bool(decision['fallback']) for decision in decisions),
                'fallback_fraction_observed': sum(bool(decision['fallback']) for decision in decisions)/len(decisions) if decisions else None,
                'component_accounting_complete': component_complete,
                'scope': 'all main plus variable paths; controller components nested in full planner/path timings; no double counting'}
        if component_complete:
            for clock in ('wall', 'cpu'):
                item[clock+'_seconds_total'] = {key: sum(_finite(a[clock][key], 'controller '+clock+' '+key) for a in accounting)
                                               for key in ('neural', 'risk', 'fallback')}
            for key in ('controller_enclosing_wall', 'overhead_wall', 'fallback_calls', 'allocation_calls'):
                item[key+'_total'] = sum(_finite(a[key], 'controller '+key) for a in accounting)
        else:
            item['unavailable_reason'] = 'Incomplete path or missing controller accounting; unknown components not filled with zero'
        result.append(item)
    return result


def _fmt(value, digits=3):
    return 'NA' if value is None else str(value) if isinstance(value, (str, bool)) else f'{value:.{digits}f}'


def _stat(statistic):
    if not statistic or not statistic.get('available'):
        return 'NA'
    lower, upper = (_bound(statistic, side) for side in (0, 1))
    return f"{_fmt(statistic['point'])} [{_fmt(lower)}, {_fmt(upper)}]"


def _table(headers, rows):
    return '\n'.join(['|'+'|'.join(headers)+'|', '|'+'|'.join(['---']*len(headers))+'|'] +
                     ['|'+'|'.join(str(value) for value in row)+'|' for row in rows])


def comparison_report(result):
    coverage = result['coverage']
    lines = ['# T2b matched development comparison', '',
             '## Material Passport', '', '完整结论由 FINAL_DECISION.md 给出；此报告不自动宣布 GO。所有数字限于冻结开发 roster，未使用保留确认集。', '',
             f"路径覆盖 {coverage['path_records_observed']}/{coverage['path_records_expected']}；状态 {coverage['path_status_counts']}；预算读数 {coverage['readout_cells_observed']}/{coverage['readout_cells_expected']}。", '',
             '每个主世界的三个 R 一起重采样；主池中的 72 条配对记录来自 24 个世界，不能当成 72 个独立样本。所有区间均为固定异质网格的描述性世界聚类重采样范围，不是校准总体置信区间或正式非劣检验。', '',
             '在线均值包含 cap 弃权，是 restricted capped acquisition cost；不是未截断期望停止时间。总获取还包括两条校准流。', '']
    main = [row for row in result['pooled_summaries'] if row['split'] == 'main_pooled']
    lines += [_table(['方法', '路径', '在线均值', '总获取均值', '正确认证', '弃权', '全路径 CPU 均值 s', '全路径 wall 均值 s'],
                     [[row['method'], f"{row['completed']}/{row['applicable']}", _fmt(row['online_restricted_cost_mean']),
                       _fmt(row['total_acquisition_restricted_cost_mean']), f"{row['certified']-row['wrong_certificates']}/{row['applicable']}",
                       row['abstained'], _fmt(row['full_path_cpu_mean']), _fmt(row['full_path_wall_mean'])] for row in main]), '']
    for reference in REFERENCES:
        selected = [row for row in result['paired'] if row['split'] == 'main_pooled' and row['R'] == 'pooled_R' and row['reference'] == reference]
        lines += [f'## 配对参考：{reference}', '',
                  _table(['方法', '在线成本比', '总获取比', '估计+规划+推理加速', '全路径 CPU 加速', '全路径 wall 加速', '新增弃权对', '原三门全过'],
                         [[row['method'], _stat(row.get('online_restricted_cost_ratio')), _stat(row.get('total_acquisition_restricted_cost_ratio')),
                           _stat(row.get('inclusive_compute_speedup')), _stat(row.get('full_path_cpu_speedup')), _stat(row.get('full_path_wall_speedup')),
                           row.get('certification_counts', {}).get('additional_abstention_pairs', 'NA'), row['all_original_engineering_flags_pass']] for row in selected]), '']
    lines += ['## 条件结果与完整分母', '',
              '下表保留每个 split/R 的全部适用路径；main/variable 分开。完整配对范围、失败状态、各字段向量见 artifacts/analysis/aggregate.json 与 paired_vectors.json。', '',
              _table(['split', 'R', '方法', '完成/适用', '在线均值', '认证', '弃权', '失败'],
                     [[row['split'], row['R'], row['method'], f"{row['completed']}/{row['applicable']}", _fmt(row['online_restricted_cost_mean']),
                       row['certified'], row['abstained'], row['failed']] for row in result['path_summaries']]), '',
              '## 中途预算评分（独立于固定置信认证）', '',
              'B=32/64 是同一固定置信轨迹的中途读数，公共 cap 仍为 6144；不是 T1b 已知剩余 horizon 的固定预算实验。提前认证后的读数使用吸收答案和实际已付成本。', '',
              _table(['split', 'R', '方法', 'B', '正确/适用', '缺失', '吸收', '有效在线均值'],
                     [[row['split'], row['R'], row['method'], row['budget'], f"{row['exact_count']}/{row['expected_applicable']}", row['missing'],
                       row['absorbed'], _fmt(row['mean_effective_online'])] for row in result['readouts']]), '',
              '## 验收与限制', '',
              '原 T2 三门全部保留：在线成本比的描述性范围上界 ≤1.05；估计+规划+推理加速的描述性范围下界 ≥2；候选和参考的全部路径正确认证且无弃权。另列相对参考的新增弃权对、弃权总数及错证，不用净恢复数抵销新增失败。描述性门标记不等于总体非劣证明。', '',
              '所有 controller 经过相同后验、cadence32、平方强制探索、累计目标跟踪和原严格 gate。风险启发式只改变 planner 选择，不给查询非劣或停止时间保证。所有 fallback 计算包含在 planner/controller 和完整 path 计时中。', '',
              '置信停止、有限精度 planning 与 quadrature 近似均保留原限制；本轮没有模型训练、RL、Qwen 调用、Natural benchmark 或独立确认。', '']
    return '\n'.join(lines)


def cost_report(result, historical_costs, deployment, receipts):
    lines = ['# T2b deployment cost analysis', '',
             '成本判断依赖每次反馈与 CPU 的相对价格；这里不编造货币单价，也不把组件 wall 加速当成全流程 CPU 加速。', '',
             'C_total = c_query N + c_CPU T_CPU + C_train/M。配对差值除以 c_CPU 后为 lambda DeltaN + DeltaCPU + T_known/M，其中 lambda=c_query/c_CPU（CPU 秒等价/观测），M 为未来部署次数。', '',
             'N 使用总获取，DeltaCPU 使用完整 path CPU；同一世界/R 的校准成本相同而在差值中抵销。下面是固定开发网格的点估计情景，不是价格预测、置信边界或外推收益保证。', '',
             f"历史已知 preparation CPU={historical_costs['preparation_cpu_seconds']:.9f}s；单次拟合 {historical_costs['fit_cpu_seconds']}。", '',
             '三种训练摊销情景：sunk_training=0（已发生且复用）；fit_only=对应单模型 CPU 拟合；known_construction_plus_fit=将整次已知共享 preparation 全额分配给该模型，再加其拟合。hybrid/periodic 使用 DeepSets-KL 成本，纯基线为零；不把无训练阶段说成整个部署无需训练。', '',
             '历史初次失败 world 的原始前缀成本未知；上述是已知部分阶段 CPU，不是完整项目成本。没有把未知项填为零。它们也不包括人工、原开发评估/调参、能耗或 GPU 价格。', '',
             '## 每次部署的观测与完整 CPU 差值', '',
             _table(['方法', '参考', '完整配对', 'Delta获取', 'Delta CPU s'],
                    [[row['method'], row['reference'], row['available'], _fmt(row.get('delta_acquisition_per_deployment')),
                      _fmt(row.get('delta_full_path_cpu_seconds'))] for row in deployment]), '',
             '## M=1000 的 break-even 情景', '',
             'lambda 小于/大于阈值的方向见区域列；阈值单位为 CPU 秒等价/观测。等号是持平，不属于严格节省。全部 M=1/100/1000/10000 情景保留在 deployment_scenarios.json。', '',
             _table(['方法', '参考', '训练情景', '每部署训练 CPU s', 'lambda 阈值', '节省区域'],
                    [[row['method'], row['reference'], scenario['training_scenario'], _fmt(scenario['training_charge_per_deployment_cpu_seconds']),
                      _fmt(scenario['lambda_threshold_cpu_seconds_per_query'], 6), scenario['advantage_region']]
                     for row in deployment for scenario in row['scenarios'] if scenario['deployments'] == 1000]), '',
             '## Controller 嵌套计算分项（主池与变维度全部路径）', '',
             _table(['方法', '分项完整', '条件回退次数/决策数', 'neural wall/CPU s', 'risk wall/CPU s', 'baseline/fallback wall/CPU s', 'controller 外壳 wall s'],
                    [[row['method'], row['component_accounting_complete'],
                      f"{row['fallback_decisions_observed']}/{row['decisions_observed']}",
                      '/'.join(_fmt(row.get(clock+'_seconds_total', {}).get('neural')) for clock in ('wall', 'cpu')),
                      '/'.join(_fmt(row.get(clock+'_seconds_total', {}).get('risk')) for clock in ('wall', 'cpu')),
                      '/'.join(_fmt(row.get(clock+'_seconds_total', {}).get('fallback')) for clock in ('wall', 'cpu')),
                      _fmt(row.get('controller_enclosing_wall_total'))] for row in result['controller_accounting']]), '',
             '纯基线的计算也记在 baseline/fallback 分项；条件回退次数只表示 hybrid/periodic 的实际切换。缺失分项显示 NA，不填零。', '',
             '## 测量范围与完整执行账本', '',
             '完整 path CPU/wall 包含估计、planner/controller、神经推理、风险指标、fallback、GLR、gate 与环境；模型冷加载/worker 启动在 driver 账本另列。本轮 inference 仅含神经计算；风险、fallback 和 controller 包装余量计入 planning。controller 自身分项是嵌套诊断，不能额外加到 path 总数。', '',
             'break-even 默认已加载长期服务。未来若每批部署重新初始化，应在截距额外加入差分冷初始化 CPU/M；共享加载两个模型的 worker 成本未武断归给某一方法。保存的 driver/worker 加载收据供独立配置计算，不能将其默认当成未来为零。wall 并行总时与子进程 CPU 总和不是同一计量。', '',
             '执行收据见 artifacts/analysis/execution_receipts.json；本报告不把嵌套阶段耗时相加为完整项目总耗时。', '',
             '本轮 execution 收据（原样保留在 JSON，不含模型/真实答案数据）：', '',
             '```json', json.dumps(receipts.get('evaluation_execution', {}), indent=2, sort_keys=True), '```', '']
    return '\n'.join(lines)


def render_figure(result, directory):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), constrained_layout=True)
    colors = {'DeepSets-KL': '#3366aa', 'DeepSets-Info': '#66a5cc',
              'Hybrid-Risk-Info': '#cc6633', 'Hybrid-Risk-Reuse': '#996633',
              'Periodic-Info': '#8866aa', 'Fused-Info': '#339966',
              'AnalyticReuse': '#666666', 'Fused-Original-Cold': '#999999'}
    for ax, reference in zip(axes, REFERENCES):
        selected = [row for row in result['paired'] if row['split'] == 'main_pooled' and row['R'] == 'pooled_R' and row['reference'] == reference]
        points = []
        for row in selected:
            query, speed = row.get('online_restricted_cost_ratio'), row.get('full_path_cpu_speedup')
            if not query or not speed or not query.get('available') or not speed.get('available'):
                continue
            x, y = query['point'], speed['point']; xlo, xhi = (_bound(query, k) for k in (0, 1)); ylo, yhi = (_bound(speed, k) for k in (0, 1))
            if None in (xlo, xhi, ylo, yhi):
                continue
            # The point can fall just outside a percentile interval; draw range
            # segments directly rather than requiring nonnegative error sizes.
            color = colors[row['method']]
            ax.plot([xlo, xhi], [y, y], color=color, alpha=.65)
            ax.plot([x, x], [ylo, yhi], color=color, alpha=.65)
            ax.scatter([x], [y], color=color, s=28)
            points.append((x, y, row['method'], color))
        for i, (x, y, method, color) in enumerate(points):
            ax.annotate(method, (x, y), xytext=(5, 6 if i % 2 else -12),
                        textcoords='offset points', fontsize=8, color=color)
        ax.axvline(1., color='gray', linestyle=':', linewidth=1)
        ax.axvline(1.05, color='#aa3333', linestyle='--', linewidth=1)
        ax.axhline(2., color='#aa3333', linestyle='--', linewidth=1)
        ax.set_title('Reference: '+reference)
        ax.set_xlabel('Restricted online query cost ratio (lower is better)')
        ax.set_ylabel('Full-path CPU speedup (higher is better)')
        ax.grid(alpha=.2)
        ax.margins(x=.2, y=.2)
    fig.suptitle('T2b matched development: query/CPU tradeoff\nWhole-world descriptive ranges; no population noninferiority claim', fontsize=12)
    outputs = []
    for suffix in ('png', 'pdf'):
        path = directory/('paired_query_cpu.'+suffix)
        fig.savefig(path, dpi=160, metadata={'Title': 'T2b matched query CPU comparison'})
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def _read_json(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def analyze(root=ROOT, outdir=None):
    root = Path(root); outdir = Path(outdir) if outdir is not None else root/'artifacts/analysis'
    if outdir.exists() and (not outdir.is_dir() or any(outdir.iterdir())):
        raise FileExistsError('Analysis directory is not empty; prior attempts are never overwritten')
    for report in REPORTS:
        if (root/report).exists():
            raise FileExistsError('Analysis report already exists: '+report)
    outdir.mkdir(parents=True, exist_ok=True)
    started, cpu_started = time.perf_counter(), time.process_time()
    execution = {'status': 'started', 'analysis_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 'python_version': platform.python_version(), 'numpy_version': str(np.__version__),
                 'model_calls': 0, 'simulation_worlds': 0, 'training_updates': 0,
                 'automatic_retry': False, 'decision': 'manual_review_required'}
    _write(outdir/'execution.json', execution)
    try:
        from .integrity import verify
        freeze = verify('generation_freeze.json')
        import matplotlib
        execution['matplotlib_version'] = str(matplotlib.__version__)
        inputs = {'config': root/'config.json', 'plan': root/'artifacts/plan_public.json',
                  'paths': root/'artifacts/evaluation/paths.jsonl',
                  'evaluation_execution': root/'artifacts/evaluation/execution.json',
                  'historical_preparation': bootstrap.T2/'artifacts/prepare_execution.json',
                  'historical_training': bootstrap.T2/'artifacts/training/execution.json'}
        for name, path in inputs.items():
            _require(path.is_file(), 'Missing required input '+name)
        config, plan = (_read_json(inputs[key]) for key in ('config', 'plan'))
        paths = [json.loads(line) for line in inputs['paths'].read_text().splitlines() if line.strip()]
        result = aggregate(paths, plan, config)
        result['generation_freeze_check'] = freeze
        historical = training_cost_scenarios(_read_json(inputs['historical_preparation']), _read_json(inputs['historical_training']))
        deployment = deployment_analysis(result['paired_vectors'], historical)
        result['controller_accounting'] = controller_accounting(paths)
        result['historical_cost_scenarios'] = historical
        result['deployment_scenarios'] = deployment
        receipts = {'evaluation_execution': _read_json(inputs['evaluation_execution']), 'worker_model_loads': []}
        for path in sorted((root/'artifacts/evaluation/worker_loads').glob('*.json')):
            receipts['worker_model_loads'].append({'path': str(path), 'receipt': _read_json(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['provenance'] = {name: {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in inputs.items()}
        result['analysis_source_sha256'] = execution['analysis_source_sha256']
        for name, value in (('aggregate.json', result), ('paired_vectors.json', result['paired_vectors']),
                            ('deployment_scenarios.json', deployment), ('execution_receipts.json', receipts)):
            _write(outdir/name, value)
        (root/REPORTS[0]).write_text(comparison_report(result))
        (root/REPORTS[1]).write_text(cost_report(result, historical, deployment, receipts))
        execution['figures'] = render_figure(result, outdir/'figures')
        execution.update(status='completed', coverage=result['coverage'])
        return result
    except Exception as exc:
        execution.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        execution.update(outer_wall_seconds=time.perf_counter()-started, outer_cpu_seconds=time.process_time()-cpu_started)
        _write(outdir/'execution.json', execution)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = analyze(args.root)
    print(json.dumps({'status': 'completed', 'coverage': result['coverage'], 'decision': result['decision']}))


if __name__ == '__main__':
    main()
