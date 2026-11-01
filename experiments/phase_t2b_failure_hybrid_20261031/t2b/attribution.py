"""Post-hoc accounting of saved T2 records; no inference, replay, or private inputs.

Run: python -m t2b.attribution.  This module uses only the standard library.
An action-trace accounting pass is not a simulator or a posterior replay.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (Path(__file__).resolve().parents[3] / 'experiments/phase_t2_structure_allocator_v02_20261031')
CORE = ('Fused-Original', 'Fused-Info', 'DeepSets-KL', 'DeepSets-Info')
STUDENTS = ('DeepSets-KL', 'DeepSets-Info')
MAIN_SPLITS = ('eval_id', 'eval_ood_parameters', 'eval_ood_partition', 'eval_ood_calibration')
# Descriptive display levels, not a learned controller or an efficacy gate.
DIVERGENCE_LEVELS = (.1, .25, .5)


def fail(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def mean(values):
    values = list(values)
    return statistics.mean(values) if values else None


def quantiles(values):
    a = sorted(float(v) for v in values)
    fail(all(math.isfinite(v) for v in a), 'nonfinite descriptive statistic')
    if not a:
        return None
    def at(p):
        x = p * (len(a) - 1)
        lo = int(x)
        return a[lo] + (a[min(lo + 1, len(a) - 1)] - a[lo]) * (x - lo)
    return dict(n=len(a), min=a[0], q25=at(.25), median=at(.5), q75=at(.75), max=a[-1], mean=mean(a))


def counts_for(actions, d, groups):
    counts = [[[0, 0] for _ in range(2)] for _ in range(d)]
    forced = [[[0, 0] for _ in range(2)] for _ in range(d)]
    types = [[0, 0] for _ in groups]
    for action, answer, is_forced in actions:
        fail(type(action) is int and 0 <= action < 2*d + len(groups), 'action outside legal domain')
        fail(answer in (0, 1) and is_forced in (0, 1), 'invalid answer/forced bit')
        if action < 2*d:
            j, form = divmod(action, 2)
            counts[j][form][answer] += 1
            forced[j][form][answer] += is_forced
        else:
            fail(not is_forced, 'type action cannot be forced task exploration')
            types[action-2*d][answer] += 1
    return counts, forced, types


def max_gap(events, end):
    """Largest interval between queries, including start/end censoring."""
    return max(b-a for a, b in zip([0]+list(events), list(events)+[end]))


def state_metrics(state):
    d, est = state['d'], state['estimate']
    online = state['online']
    theta = [min(1., max(0., float(v))) for v in est['theta_prob']]
    z = [min(1., max(0., float(v))) for v in est['z_prob']]
    tasks = [sum(sum(c) for c in fact) for fact in state['counts']]
    types = [sum(c) for c in state['type_report_counts']]
    return {
        'online': float(online), 'p': est['p'], 'q': est['q'],
        'rate_gap': est['p'] - est['q'],
        'max_fact_uncertainty': max(min(v, 1-v) for v in theta),
        'max_type_uncertainty': max(min(v, 1-v) for v in z),
        'observed_type_share': sum(types)/max(1, online),
        'max_group_type_share': max(types)/max(1, online),
        'min_fact_task_share': min(tasks)/max(1, online),
        'task_count_imbalance': max(tasks)/max(1, min(tasks)),
    }


def canonical_estimate(update):
    est = update['state']['estimate'] if 'state' in update else update['estimate']
    return {k: est[k] for k in ('p', 'q', 'theta_prob', 'z_prob', 'z')}


def path_accounting(row, spec):
    """Validate recorded actions against final public count sufficient statistics."""
    groups, d = [], sum(spec['partition'])
    offset = 0
    for size in spec['partition']:
        groups.append(list(range(offset, offset+size)))
        offset += size
    actions = row['action_trace']
    fail(len(actions) == row['online'], 'trace length != charged online cost')
    counts, forced, types = counts_for(actions, d, groups)
    fail(counts == row['counts'], 'final task counts disagree with action trace')
    fail(forced == row['forced_counts'], 'final forced counts disagree with action trace')
    fail(types == [[x.count(0), x.count(1)] for x in row['type_answers']], 'type counts disagree with trace')
    task_n = sum(sum(sum(c) for c in fact) for fact in counts)
    type_n = sum(sum(c) for c in types)
    fail(task_n == row['costs']['task'] and type_n == row['costs']['type'], 'action cost accounting mismatch')
    fail(task_n+type_n == row['online'], 'online action denominator mismatch')
    calibration_n = sum(len(row['calibration'][k]) for k in ('high', 'low'))
    fail(calibration_n == row['costs']['offline'], 'calibration cost mismatch')
    fail(row['total_acquisition'] == row['online']+calibration_n, 'total acquisition mismatch')
    fail(bool(row['certified']) != bool(row['abstained']), 'completed path must certify or abstain')
    fail(row['online'] <= row['online_cap'], 'path beyond cap')
    fail(not row['abstained'] or row['online'] == row['online_cap'], 'abstention before cap')
    updates = row['updates']
    fail(all(updates[i]['online'] < updates[i+1]['online'] for i in range(len(updates)-1)), 'unordered updates')
    fact_n = [sum(sum(c) for c in fact) for fact in counts]
    forced_n = [sum(sum(c) for c in fact) for fact in forced]
    form_n = [[sum(c) for c in fact] for fact in counts]
    fact_events = [[] for _ in range(d)]
    group_type_events = [[] for _ in groups]
    for i, (action, _, _) in enumerate(actions, 1):
        (fact_events[action//2] if action < 2*d else group_type_events[action-2*d]).append(i)
    allocation_min_fact, concentration, typemass = [], [], []
    for update in updates:
        w = update['weights']
        fail(len(w) == 2*d+len(groups), 'allocation dimension mismatch')
        fail(all(math.isfinite(v) and v >= -1e-12 for v in w) and abs(sum(w)-1)<1e-6, 'invalid saved allocation')
        allocation_min_fact.append(min(w[2*j]+w[2*j+1] for j in range(d)))
        concentration.append(max(w))
        typemass.append(sum(w[2*d:]))
    fit = row['final_fit']
    fail(all(k in fit for k in ('gap','beta','theta','z','alternative_theta','alternative_z')), 'missing final profile alternative')
    bottleneck = {
        'candidate_theta': fit['theta'], 'candidate_z': fit['z'],
        'alternative_theta': fit['alternative_theta'], 'alternative_z': fit['alternative_z'],
        'flipped_fact_indices': [j for j,(a,b) in enumerate(zip(fit['theta'],fit['alternative_theta'])) if a!=b],
        'flipped_group_indices': [g for g,(a,b) in enumerate(zip(fit['z'],fit['alternative_z'])) if a!=b],
        'gap': fit['gap'], 'beta': fit['beta'], 'gap_minus_beta': fit['gap']-fit['beta'],
        'scope': 'saved final float64 empirical profile fit, not latent truth or full bottleneck history',
    }
    gates = [dict(online=g['online'], certified=g['certified'], status=g['status'],
                  strict_margin_lower=float(g['gap_lower'])-float(g['beta_upper']),
                  strict_margin_upper=float(g['gap_upper'])-float(g['beta_lower']))
             for g in row['gate_history']]
    return {
        'world_id': row['world_id'], 'split': row['split'], 'R': row['R'], 'method': row['method'],
        'd': d, 'groups': groups, 'partition': spec['partition'], 'alpha': spec['alpha'],
        'online': row['online'], 'task': task_n, 'type': type_n, 'offline': calibration_n,
        'certified': row['certified'], 'abstained': row['abstained'],
        'task_type_share': {'task': task_n/row['online'], 'type': type_n/row['online']},
        'fact_task_counts': fact_n, 'fact_form_counts': form_n, 'fact_forced_counts': forced_n,
        'group_type_counts': [sum(c) for c in types],
        'max_fact_query_gap': [max_gap(x,row['online']) for x in fact_events],
        'max_group_type_gap': [max_gap(x,row['online']) for x in group_type_events],
        'min_fact_allocation_mass': quantiles(allocation_min_fact),
        'max_action_allocation_mass': quantiles(concentration),
        'target_type_allocation_mass': quantiles(typemass),
        'final_profile_bottleneck': bottleneck, 'strict_gate_records': gates,
        'recorded_updates': len(updates), 'scheduled_glr_checks': row['glr_checks'],
        'scheduled_glr_values_available': False,
    }


def prefix_signatures(row, times, d, groups):
    """Count sufficient statistics only; no posterior or environment recomputation."""
    wanted=set(times)
    c=[[[0,0],[0,0]] for _ in range(d)]
    y=[[0,0] for _ in groups]
    result={}
    for t,(a,b,_) in enumerate(row['action_trace'],1):
        if a<2*d:c[a//2][a%2][b]+=1
        else:y[a-2*d][b]+=1
        if t in wanted:
            result[t]=json.dumps([c,y,row['calibration']],sort_keys=True,separators=(',',':'))
    return result


def compare_updates(student, teacher, d, groups):
    su={u['online']:u for u in student['updates']}
    tu={u['online']:u for u in teacher['updates']}
    times=sorted(su.keys() & tu.keys())
    ss=prefix_signatures(student,times,d,groups)
    ts=prefix_signatures(teacher,times,d,groups)
    rows=[]
    for t in times:
        a,b=su[t],tu[t]
        ea,eb=canonical_estimate(a),canonical_estimate(b)
        l1=sum(abs(x-y) for x,y in zip(a['weights'],b['weights']))
        rows.append(dict(online=t, allocation_l1=l1, same_observed_counts=ss[t]==ts[t],
                         theta_probability_l1=sum(abs(x-y) for x,y in zip(ea['theta_prob'],eb['theta_prob'])),
                         type_probability_l1=sum(abs(x-y) for x,y in zip(ea['z_prob'],eb['z_prob'])),
                         p_abs_difference=abs(ea['p']-eb['p']), q_abs_difference=abs(ea['q']-eb['q']),
                         student_type_target=sum(a['weights'][2*d:]),teacher_type_target=sum(b['weights'][2*d:])))
    first_action=next((t for t,(a,b) in enumerate(zip(student['action_trace'],teacher['action_trace']),1) if a[0]!=b[0]),None)
    return dict(world_id=student['world_id'],split=student['split'],R=student['R'],method=student['method'],
                paired_online_difference=student['online']-teacher['online'],
                paired_type_difference=student['costs']['type']-teacher['costs']['type'],
                paired_task_difference=student['costs']['task']-teacher['costs']['task'],
                first_different_action_clock=first_action,
                earliest_recorded_l1_crossing={str(level):next((x['online'] for x in rows if x['allocation_l1']>=level),None) for level in DIVERGENCE_LEVELS},
                same_count_update_count=sum(x['same_observed_counts'] for x in rows),
                matched_clock_update_count=len(rows),
                all_clock_records=rows,
                interpretation='same clock does not imply same belief/history; causal attribution unavailable')


def drift_summary(row, train_envelopes):
    d=len(row['counts']);env=train_envelopes[d]
    metrics=[];outside=collections.Counter();within_snapshot_support=0
    for update in row['updates']:
        if 'state' not in update:
            continue
        state=update['state']
        fail(state['d']==d and state['online']==update['online'], 'saved state/update mismatch')
        vals=state_metrics(state);metrics.append(vals)
        if vals['online']<=1024:
            within_snapshot_support+=1
            for name,value in vals.items():
                if name=='online':continue
                lo,hi=env[name]
                if value<lo-1e-10 or value>hi+1e-10:outside[name]+=1
    return dict(world_id=row['world_id'],split=row['split'],R=row['R'],method=row['method'],d=d,
                observable_saved_state_count=len(metrics),
                updates_beyond_training_last_snapshot=sum(m['online']>1024 for m in metrics),
                updates_within_training_time_range=within_snapshot_support,
                outside_matching_dimension_training_envelope_within_time=dict(outside),
                feature_summaries={k:quantiles(m[k] for m in metrics) for k in metrics[0]} if metrics else {},
                interpretation='training support diagnostic only; OOD design and policy history differ; not identified policy-induced shift')


def validate_saved_update_states(row, d, groups):
    # Compare saved public neural count states to one cumulative trace accounting pass.
    by_t={u['online']:u['state'] for u in row['updates'] if 'state' in u}
    if not by_t:return 0
    c=[[[0,0],[0,0]] for _ in range(d)];f=[[[0,0],[0,0]] for _ in range(d)];y=[[0,0] for _ in groups]
    checked=0
    for t,(a,b,forced) in enumerate(row['action_trace'],1):
        if a<2*d:
            c[a//2][a%2][b]+=1;f[a//2][a%2][b]+=forced
        else:y[a-2*d][b]+=1
        if t in by_t:
            state=by_t[t]
            fail(state['counts']==c and state['forced_counts']==f and state['type_report_counts']==y,'saved update state contradicts prefix counts')
            checked+=1
    fail(checked==len(by_t),'missing update prefix')
    return checked


def aggregate(paths):
    buckets=collections.defaultdict(list)
    for x in paths:
        for key in ((x['method'],'all_main','all_R'),(x['method'],'all_main',str(x['R'])),(x['method'],x['split'],str(x['R']))):
            buckets[key].append(x)
    result=[]
    for (method,split,risk),a in sorted(buckets.items()):
        result.append(dict(method=method,split=split,R=risk,n=len(a),
                           online_mean=mean(x['online'] for x in a), task_mean=mean(x['task'] for x in a),
                           type_mean=mean(x['type'] for x in a), offline_mean=mean(x['offline'] for x in a),
                           certified=sum(x['certified'] for x in a),abstained=sum(x['abstained'] for x in a),
                           aggregate_type_share=sum(x['type'] for x in a)/sum(x['online'] for x in a),
                           final_min_fact_counts=quantiles(min(x['fact_task_counts']) for x in a),
                           final_glr_margin=quantiles(x['final_profile_bottleneck']['gap_minus_beta'] for x in a)))
    return result


def write_report(out, summary):
    def f(x):return f'{x:.2f}'
    lines=['# T2b：既有 T2 闭环失败归因', '',
           '本报告只分析冻结的 T2 v02 记录，没有生成新世界、运行模型、重新求解分配或重放后验。它是事后描述性审计，不能把相关性解释为失败的因果机制。', '',
           '## 覆盖与可识别范围', '',
           f"原始记录 {summary['coverage']['source_path_records']} 条；主评测 {summary['coverage']['main_completed_paths']} 条（24 个世界、三个 R、11 种方法）。逐条检查动作成本与最终计数，并核对 {summary['coverage']['validated_saved_neural_states']} 个已保存学生状态的计数前缀。没有使用隐藏真值、种子、正确率标签或未来结果作为风险信号。", '',
           '已有记录保存每次分配、学生输入状态、完整动作记录、最终 profile GLR 及其替代假设、严格停止门结果。中途 GLR 检查仅有执行标记，没有逐次统计量；因此不能恢复完整 GLR/边界曲线、逐时瓶颈替代或认证进展。这里不补跑求解器来填补缺失。', '',
           '## 各方法的查询组成', '',
           '| 方法 | 在线均值 | task 均值 | type 均值 | type 总占比 | 认证/72 |',
           '|---|---:|---:|---:|---:|---:|']
    for a in summary['aggregates']:
        if a['method'] in CORE and a['split']=='all_main' and a['R']=='all_R':
            lines.append(f"| {a['method']} | {f(a['online_mean'])} | {f(a['task_mean'])} | {f(a['type_mean'])} | {a['aggregate_type_share']:.2%} | {a['certified']}/72 |")
    lines += ['', '完整 11 方法、各 R 与 OOD 条件的分母和组成见 `artifacts/attribution/summary.json`。三个 R 共享同一世界，不能当作 72 个独立世界。', '',
              '## 额外 calibration-OOD、R=256 弃权', '',
              '| 方法 | 在线 | task | type | 最终 GLR − 阈值 | 最终翻转事实 | 最终翻转组 |',
              '|---|---:|---:|---:|---:|---|---|']
    for a in summary['selected_cases']['additional_cap']['policies']:
        b=a['final_profile_bottleneck']
        lines.append(f"| {a['method']} | {a['online']} | {a['task']} | {a['type']} | {f(b['gap_minus_beta'])} | {b['flipped_fact_indices']} | {b['flipped_group_indices']} |")
    lines += ['', '该例的初始更新 t=8 具有完全相同的观测计数和后验，允许直接比较这一状态的分配：', '',
              '| 学生 | 初始分配 L1 | 初始 type 质量 | 教师 type 质量 | 首次不同动作时钟 | 最早记录 L1≥0.25 |',
              '|---|---:|---:|---:|---:|---:|']
    for pair in summary['selected_cases']['additional_cap']['paired']:
        initial=pair['all_clock_records'][0]
        lines.append(f"| {pair['method']} | {initial['allocation_l1']:.4f} | {initial['student_type_target']:.4f} | {initial['teacher_type_target']:.4f} | {pair['first_different_action_clock']} | {pair['earliest_recorded_l1_crossing']['0.25']} |")
    lines += ['', '这两条学生路径与教师共有 182 个匹配时钟更新，但只有初始更新仍具有相同观测充分统计量。', '',
              '| 方法 | 每事实 task 数 | 各组 type 数 | 每事实最长任务间隔 |',
              '|---|---|---|---|']
    for a in summary['selected_cases']['additional_cap']['policies']:
        lines.append(f"| {a['method']} | {a['fact_task_counts']} | {a['group_type_counts']} | {a['max_fact_query_gap']} |")
    lines += ['', '该例中，学生在上限之前消耗更多类型询问，因而即使总在线数较多，任务观测更少。最终 GLR 的困难替代涉及事实翻转，严格门仍拒绝认证。这是可观察的 task/type 稀释现象；单条配对路径不能证明“只减少 type 就会获救”，因为行动会改变之后的观测与后验。', '',
              '学生已保存的最终更新后验对事实几乎完全确信，仍不足以越过严格 GLR。后验确信与模型全替代认证并非同一个目标；教师在本例也很确信，因此这不是学生专属的因果解释。', '',
              '## 低 R 的 DeepSets-Info', '',
              '| R | 教师在线均值 | KL 在线均值 | Info 在线均值 | KL type 均值 | Info type 均值 |',
              '|---|---:|---:|---:|---:|---:|']
    for r in (16,64,256):
        a={x['method']:x for x in summary['aggregates'] if x['split']=='all_main' and x['R']==str(r)}
        lines.append(f"| {r} | {f(a['Fused-Original']['online_mean'])} | {f(a['DeepSets-KL']['online_mean'])} | {f(a['DeepSets-Info']['online_mean'])} | {f(a['DeepSets-KL']['type_mean'])} | {f(a['DeepSets-Info']['type_mean'])} |")
    lines += ['', '按预先固定的审计规则，另列 R=16 中 Info 相对教师额外在线数最大的三条路径，仅作事后案例，不把它们作为混合控制器的阈值调参集。每条路径及对应四方法计数、最终瓶颈、分配/后验差异见 `selected_cases.json`。', '',
              '| 世界 | Info − 教师在线 | Info − 教师 type | Info − 教师 task |',
              '|---|---:|---:|---:|']
    for case in summary['selected_cases']['largest_low_r_info_excess']:
        p=case['paired']
        lines.append(f"| `{p['world_id']}` | {p['paired_online_difference']} | {p['paired_type_difference']} | {p['paired_task_difference']} |")
    lines += ['', '## 分配偏离、低覆盖与后验支持范围', '',
              '分配 L1 的 0.10/0.25/0.50 三个展示水平固定用于描述最早已记录偏离，不是混合策略阈值。先报告首次不同动作，再比较相同在线时钟下的已记录分配；只有计数、类型报告和校准证据均相同时才标为同观测状态。分歧之后，同 t 的后验通常来自不同历史，不能把分配差解释成同一状态下的学生误差。', '',
              '本次没有发现完全不采样的事实：强制探索保证任务形式持续覆盖。仍保留每事实/形式计数、含终点截尾的最长查询间隔、最小目标事实质量和类型目标质量。低权重或最长间隔本身不证明某事实在统计意义上被“饿死”；零 type 也不自动构成组信息不足，因为 task 与校准同样提供类型信息。', '',
              f"两个 DeepSets 共保存 {summary['drift']['student_saved_update_count']} 次主评测更新，其中 {summary['drift']['updates_beyond_training_last_snapshot']} 次超过训练最后快照 t=1024。这是明确的时间/计数支持范围变化，但教师部署也可运行到更晚；不能单凭这一点确认策略诱导的分布偏移。", '',
              '脚本另按事实数匹配训练状态，计算在线时间≤1024时的可观察指标是否越出训练 min/max 范围；不使用测试成败选择指标。结果见 `drift.json`。这些范围不等于密度支持，也没有分离预设 OOD 条件与策略历史影响，因而当前证据不足以启动 DAgger 并声称修复已识别分布偏移。', '',
              '## 可供冻结混合设计使用的廉价信号', '',
              '可合法计算：当前分配的类型质量与最大行动质量；每事实任务计数/目标质量；事实或类型后验不确定性；在线时间是否超过既有训练快照；已真实计算并缓存的认证间距。任何信号均无非劣保证。不能为了得到认证间距而隐去一次完整 GLR 的成本；没有缓存时不可伪造。', '',
              '本审计没有根据正确答案、认证成功标签或上述极端路径选择控制器阈值。混合候选及固定周期对照应在新开发世界生成前另行冻结。', '',
              '结论：已观察到额外弃权路径的 type 预算扩张和任务观测稀释；完整瓶颈演化、因果解释与政策诱导分布偏移仍未确认。保留信息目标与停止目标错位、闭环支持偏移两种假说，下一步只比较预注册的无训练混合策略。', '']
    (out.parent.parent/'FAILURE_STATE_ATTRIBUTION.md').write_text('\n'.join(lines))


def run(source: Path, root: Path):
    started=time.perf_counter();cpu=time.process_time()
    out=root/'artifacts/attribution'
    fail(not out.exists(), 'attribution output already exists; refusing overwrite')
    relative_inputs=['artifacts/evaluation/paths.jsonl','artifacts/evaluation/execution.json','artifacts/plan_public.json','artifacts/data/train.jsonl','FINAL_RECEIPT.json']
    hashes={p:digest(source/p) for p in relative_inputs}
    receipt=json.loads((source/'FINAL_RECEIPT.json').read_text())
    for p in relative_inputs[:-1]:
        fail(receipt['artifact_sha256'].get(p)==hashes[p],f'frozen T2 receipt mismatch: {p}')
    execution=json.loads((source/'artifacts/evaluation/execution.json').read_text())
    fail(execution['status']=='completed' and execution['failed_paths']==0,'source evaluation incomplete')
    plan=json.loads((source/'artifacts/plan_public.json').read_text())
    specs={x['world_id']:x for x in plan['worlds']}
    rows=load_jsonl(source/'artifacts/evaluation/paths.jsonl')
    fail(len(rows)==858,'unexpected source denominator')
    keys=[(x['world_id'],x['R'],x['method']) for x in rows]
    fail(len(set(keys))==len(keys),'duplicate source path')
    expected={(x['world_id'],x['R'],x['method']) for x in plan['expected_paths']}
    fail(set(keys)==expected,'source path roster differs from plan')
    main=[x for x in rows if x['split'] in MAIN_SPLITS]
    fail(len(main)==792 and all(x['status']=='completed' for x in main),'incomplete main source paths')
    training=load_jsonl(source/'artifacts/data/train.jsonl')
    fail(len(training)==1536,'unexpected training state denominator')
    env=collections.defaultdict(lambda:collections.defaultdict(list))
    for row in training:
        fail(row['split']=='train','nontraining state used for support envelope')
        for k,v in state_metrics(row['state']).items():env[row['state']['d']][k].append(v)
    env={d:{k:[min(v),max(v)] for k,v in features.items()} for d,features in env.items()}
    accounting=[];checked_states=0
    for row in main:
        a=path_accounting(row,specs[row['world_id']]);accounting.append(a)
        checked_states+=validate_saved_update_states(row,a['d'],a['groups'])
    indexed={(x['world_id'],x['R'],x['method']):x for x in main}
    accindexed={(x['world_id'],x['R'],x['method']):x for x in accounting}
    paired=[];drift=[]
    for row in main:
        if row['method'] not in STUDENTS:continue
        a=accindexed[row['world_id'],row['R'],row['method']]
        paired.append(compare_updates(row,indexed[row['world_id'],row['R'],'Fused-Original'],a['d'],a['groups']))
        drift.append(drift_summary(row,env))
    extras=[x for x in paired if indexed[x['world_id'],x['R'],x['method']]['abstained'] and not indexed[x['world_id'],x['R'],'Fused-Original']['abstained']]
    fail(len(extras)==2 and len({(x['world_id'],x['R']) for x in extras})==1,'unexpected additional-cap roster')
    wid,risk=extras[0]['world_id'],extras[0]['R']
    def case(pair):
        w,r=pair['world_id'],pair['R']
        return dict(world_id=w,R=r,paired=pair,policies=[accindexed[w,r,m] for m in CORE])
    additional=dict(world_id=wid,R=risk,policies=[accindexed[wid,risk,m] for m in CORE],paired=extras)
    ranked=sorted((x for x in paired if x['method']=='DeepSets-Info' and x['R']==16),key=lambda x:(-x['paired_online_difference'],x['world_id']))[:3]
    summary=dict(scope='posthoc deterministic accounting of existing frozen T2; no causal or efficacy claim',
                 coverage=dict(source_path_records=len(rows),main_completed_paths=len(main),main_worlds=24,risks=[16,64,256],methods=11,validated_saved_neural_states=checked_states),
                 aggregates=aggregate(accounting),
                 selected_cases=dict(additional_cap=additional,largest_low_r_info_excess=[case(x) for x in ranked]),
                 drift=dict(student_saved_update_count=sum(x['observable_saved_state_count'] for x in drift),updates_beyond_training_last_snapshot=sum(x['updates_beyond_training_last_snapshot'] for x in drift)),
                 unavailable=['scheduled intermediate GLR values','time-resolved bottleneck alternatives','causal allocation-error effects','identified policy-induced density shift'],
                 source_inputs=hashes,source_final_receipt_status=receipt['status'],
                 action_trace_accounting_is_environment_replay=False,
                 private_sources_read=False,correctness_labels_used=False,new_worlds=0,inference_calls=0,training_calls=0,solver_calls=0)
    fail(all(digest(source/p)==h for p,h in hashes.items()),'source changed during audit')
    out.mkdir(parents=True)
    def save(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    save('path_accounting.json',accounting)
    save('paired_divergence.json',paired)
    save('drift.json',dict(training_envelopes=env,paths=drift))
    save('selected_cases.json',summary['selected_cases'])
    save('summary.json',summary)
    write_report(out,summary)
    save('execution.json',dict(status='completed',wall_seconds=time.perf_counter()-started,cpu_seconds=time.process_time()-cpu,source_hashes=hashes,main_paths=len(main),validated_saved_neural_states=checked_states,private_inputs_read=False,inference_calls=0,training_calls=0,solver_calls=0))
    print(json.dumps(dict(status='completed',main_paths=len(main),validated_saved_neural_states=checked_states,output=str(out))))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    run(args.source,args.root)
