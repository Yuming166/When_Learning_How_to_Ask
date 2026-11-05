"""Three-deployment paired comparisons and a bounded Chinese result report."""
from collections import Counter
import experiment as ex


def enrich_and_write(summary):
    context=ex.load_context()
    cases=context['cases']
    new_records=ex.record_map(ex.RUN/'records')
    reference_records={'luna':ex.record_map(ex.REFERENCE/'luna_records'),
                       'deepseek':ex.record_map(ex.REFERENCE/'deepseek_records')}
    banks={'glm':ex.make_bank(new_records,context),
           **{name:ex.make_bank(records,context) for name,records in reference_records.items()}}
    complete={name:{p for p in context['profiles'] if all(bank[(p,a)].get('valid') for a in ex.CFG['query_actions'])}
              for name,bank in banks.items()}
    common=set.intersection(*complete.values())
    common_cases=[c for c in cases if c['profile_id'] in common]
    all_traces={'glm':ex.rows(ex.RESULTS/'PAIRED_POLICY_TRACES.jsonl'),
                'luna':ex.rows(ex.REFERENCE/'LUNA_PAIRED_POLICY_TRACES.jsonl'),
                'deepseek':ex.rows(ex.REFERENCE/'DEEPSEEK_PAIRED_POLICY_TRACES.jsonl')}
    lookups={name:ex.trace_lookup(traces) for name,traces in all_traces.items()}
    refs={'luna':ex.read(ex.REFERENCE/'LUNA_ANALYSIS.json'),
          'deepseek':ex.read(ex.REFERENCE/'DEEPSEEK_ANALYSIS.json')}
    plan=ex.bootstrap_plan(cases)
    against_deepseek={}
    for b in ex.CFG['budgets']:
        against_deepseek[str(b)]={}
        for m in ex.CFG['methods']:
            left={c['case_id']:lookups['glm'][(c['case_id'],m,b)]['exact_decision_correct'] for c in cases}
            right={c['case_id']:lookups['deepseek'][(c['case_id'],m,b)]['exact_decision_correct'] for c in cases}
            comp=ex.paired_difference(cases,left,right,plan)
            comp['selected_action_agreement']=sum(lookups['glm'][(c['case_id'],m,b)]['selected_action']==
                lookups['deepseek'][(c['case_id'],m,b)]['selected_action'] for c in cases)
            against_deepseek[str(b)][m]=comp
    field_agreement={}
    for name in refs:
        keys=[k for k in banks['glm'] if banks['glm'][k].get('valid') and banks[name][k].get('valid')]
        field_agreement[name]={'jointly_valid':len(keys),
            'equal':sum(ex.canonical(banks['glm'][k]['parsed']['value'])==
                        ex.canonical(banks[name][k]['parsed']['value']) for k in keys)}
    common_metrics={}
    for b in ex.CFG['budgets']:
        common_metrics[str(b)]={}
        for m in ex.CFG['methods']:
            common_metrics[str(b)][m]={'n':len(common_cases),
                'correct':{name:sum(lookup[(c['case_id'],m,b)]['exact_decision_correct'] for c in common_cases)
                           for name,lookup in lookups.items()},
                'glm_luna_same_action':sum(lookups['glm'][(c['case_id'],m,b)]['selected_action']==
                     lookups['luna'][(c['case_id'],m,b)]['selected_action'] for c in common_cases),
                'glm_deepseek_same_action':sum(lookups['glm'][(c['case_id'],m,b)]['selected_action']==
                     lookups['deepseek'][(c['case_id'],m,b)]['selected_action'] for c in common_cases)}
    quality={}
    for name,bank in banks.items():
        quality[name]={'planned':288,'valid':sum(bool(v.get('valid')) for v in bank.values()),
                      'exact':sum(bool(v.get('exact_profile_match')) for v in bank.values()),
                      'complete_valid_profiles':len(complete[name])}
    failed=[r for r in new_records.values() if not r.get('valid')]
    summary.update(model_minus_deepseek_pairwise=against_deepseek,
        cross_model_quality=quality,parsed_field_agreement=field_agreement,
        common_complete_profiles=sorted(common),common_complete_cases=len(common_cases),
        common_complete_subset_metrics=common_metrics,
        transport_failure_classes=dict(Counter(r.get('error_class') for r in failed if not r.get('transport_ok'))),
        stream_complete_responses=sum(bool(r.get('sse_complete')) for r in new_records.values()),
        source_comparison_note='Luna CLI decoding/identity unavailable; DeepSeek retained 10 original TLS failures and a post-failure serial continuation; GLM uses complete SSE and matching explicit high inference setting.',
        common_subset_limit='Secondary failure-excluding descriptive intersection; not the 280-case primary estimate.')
    ex.write(ex.RESULTS/'ANALYSIS.json',summary)
    ex.write(ex.RESULTS/'THREE_MODEL_COMPARISON.json',{k:summary[k] for k in (
        'cross_model_quality','parsed_field_agreement','common_complete_profiles','common_complete_cases',
        'common_complete_subset_metrics','model_minus_luna_pairwise','model_minus_deepseek_pairwise',
        'source_comparison_note','common_subset_limit')})
    write_report(summary,refs)


def write_report(s,refs):
    receipt=ex.read(ex.BASE/'RUN_RECEIPT.json')
    lines=['# GLM-5.3 顾客家族复核与三模型同数据比较','','## Material Passport','',
        f"- 状态：`{s['status']}`；48 个合成开发画像、35 个菜单、280 个案例。",
        f"- 请求 `{ex.CFG['requested_model']}`，流中返回标识：`{', '.join(s['reported_models'])}`；千问/阿里云百炼北京接口。",
        '- 模型标识是服务端报告，不是独立权重核验。逐字复用原顾客提示；推荐方是冻结 Python 策略。',
        f"- 计划 288 个唯一字段请求，实际尝试 {s['attempted_calls']}，有效回答 {s['valid_answers']}，精确符合画像 {s['exact_profile_field_matches']}；重试 {receipt['retries']}。",
        f"- 传输/协议失败 {receipt['transport_failures']}；完整 SSE 响应 {s['stream_complete_responses']}。全部 280 案例均进入每个方法与预算分母。",'',
        '## GLM 下的全部预算','',
        '| 预算 | 固定顺序 | Profile IG | Decision-Set IG | Decision Value | DV − DSIG，百分点（95% 区间） |',
        '|---:|---:|---:|---:|---:|---:|']
    for b in ex.CFG['budgets']:
        values=[s['budget_metrics'][m][str(b)] for m in ex.CFG['methods']]
        comp=s['decision_value_pairwise'][str(b)]['decision_set_ig']
        lo,hi=comp['cluster_bootstrap_95_ci']
        lines.append('| '+str(b)+' | '+' | '.join(f"{r['correct']}/280 ({100*r['accuracy']:.1f}%)" for r in values)+
                     f" | {100*comp['difference']:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}] |")
    lines+=['','## 三个顾客部署的全分母比较','',
        '| 预算 | 方法 | Luna | DeepSeek V4.1 Flash | GLM-5.3 |','|---:|---|---:|---:|---:|']
    for b in (3,4,5):
        for m in ex.CFG['methods']:
            values=[refs['luna']['budget_metrics'][m][str(b)],refs['deepseek']['budget_metrics'][m][str(b)],s['budget_metrics'][m][str(b)]]
            lines.append(f'| {b} | {m} | '+' | '.join(f"{r['correct']}/280 ({100*r['accuracy']:.1f}%)" for r in values)+' |')
    lines+=['','## 回答完整性与画像忠实度','',
        '| 顾客部署 | 字段计划 | 有效字段 | 精确符合画像 | 完整有效画像数 |','|---|---:|---:|---:|---:|']
    for name,q in s['cross_model_quality'].items():
        lines.append(f"| {name} | {q['planned']} | {q['valid']} | {q['exact']} | {q['complete_valid_profiles']}/48 |")
    lines+=['', 'DeepSeek 的 10 次 TLS 失败保留在全分母比较中，涉及 22 个案例；原实验在失败后改用串行连接复用，仅继续未尝试字段。这里不重跑或补齐该历史模型。Luna 原回答库含一个无效 pattern 回答。',
        '', '| 与 GLM 比较 | 两边均有效的字段 | 解析值相同 |','|---|---:|---:|']
    for name,q in s['parsed_field_agreement'].items():
        lines.append(f"| {name} | {q['jointly_valid']} | {q['equal']} |")
    lines+=['','## 三模型共同完整有效的补充子集','',
        f"交集为 {len(s['common_complete_profiles'])} 个画像、{s['common_complete_cases']} 个案例。该子集排除了任何模型回答不完整/无效的画像，属于预先规定的次要描述；不能替代 280 案例主结果，也不应借此隐藏连接失败。",'',
        '| 预算 | 方法 | 案例数 | Luna 正确 | DeepSeek 正确 | GLM 正确 |','|---:|---|---:|---:|---:|---:|']
    for b in (3,4,5):
        for m in ex.CFG['methods']:
            r=s['common_complete_subset_metrics'][str(b)][m]
            lines.append(f"| {b} | {m} | {r['n']} | {r['correct']['luna']} | {r['correct']['deepseek']} | {r['correct']['glm']} |")
    lines+=['','## GLM 字段质量与失败','',
        '| 字段 | 计划 | 尝试 | 有效 | 精确符合画像 |','|---|---:|---:|---:|---:|']
    for name,q in s['field_answer_quality'].items():
        lines.append(f"| {name} | {q['planned']} | {q['attempted']} | {q['valid']} | {q['exact']} |")
    lines+=['', '无效/失败项：`'+ex.canonical(s['invalid_answers'])+'`。',
        '', '## 约束、查询成本与 regret','',
        '| 预算 | 方法 | 中断路径 | 硬约束违规 | 平均问题数 | 平均归一化 regret |','|---:|---|---:|---:|---:|---:|']
    for b in (3,4,5):
        for m in ex.CFG['methods']:
            r=s['budget_metrics'][m][str(b)]
            lines.append(f"| {b} | {m} | {r['failed_paths']}/280 | {r['hard_violations']} | {r['mean_query_units']:.2f} | {r['mean_normalized_score_regret']:.4f} |")
    lines+=['', '接口返回 token 用量汇总：`'+ex.canonical(s['token_usage'])+'`；未推测账单。',
        '', '## 科研解释边界','',
        '三个家族名称代表三个指定的顾客模型部署，并非模型总体的随机样本。这里能够检验同一结构化画像问答接口下的方法迁移，不能据此宣称对广泛模型家族、自然多轮顾客、真人偏好或模型驱动推荐 Agent 都稳健。',
        '画像给出了完整原始偏好分数，模型按被问字段返回。若回答高度重合，策略结果接近主要是相同输入下的确定性推论，并不证明顾客行为多样性。自然语言自由表达、跨轮偏好保持和最终购买行为没有在本轮评估。',
        '这 48 个画像和 35 个菜单曾参与方法开发，因此仍是开发面板的第三部署复核，不是独立 held-out 确认。原 Luna BUY_TIED 行为筛查失败结论保持；本轮没有验证 GLM 的购买行为。',
        'GLM 通过 SSE、DeepSeek 通过非流式 API、Luna 通过 Codex CLI。GLM 与 DeepSeek 显式对齐 temperature=1、top_p=1、high 推理及 8192 输出上限；GLM 默认 top_p=0.95 与 max 推理不等于本轮配置。Luna 的后台身份、外层系统与采样参数未能全部对齐，不能把差异因果归因于模型权重。',
        '区间按 48 画像、12 pool/cohort 分层聚类 bootstrap 10,000 次，seed=202611041955；菜单随画像携带。它们是开发面板的描述性区间，不是人群显著性结论；三个预算和多个模型也不能作为独立样本相加。',
        '确定性缓存统计：`'+ex.canonical(s['cache_receipt'])+'`。缓存仅复用相同有效输入下的 Python 策略计算，所有 GLM 字段仍按计划实际请求；失败项不会由 Luna 回答填补。',
        '', '## 复现材料','',
        '`FROZEN.json` 绑定所有提示、输入、原始参考结果及源码。原始 SSE 见 `artifacts/run/responses/`，逐案轨迹和全部指标见 `results/PAIRED_POLICY_TRACES.jsonl` 与 `results/ANALYSIS.json`，三模型对照见 `results/THREE_MODEL_COMPARISON.json`。',
        '执行 `python experiment.py verify` 校验冻结哈希；`python experiment.py analyze` 只离线重算，无 API 调用。不要重复执行 `run`。']
    (ex.RESULTS/'REPORT_ZH.md').write_text('\n'.join(lines)+'\n')
