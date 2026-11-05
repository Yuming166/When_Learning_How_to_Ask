"""Reporting supplement; never collects/retries model responses or changes scores.

Added during collection after a read-only audit found the inherited report did
not explicitly disclose the transport continuation or complete-bank counts.
The original frozen collector/analyzer stays untouched.
"""
from collections import Counter
from pathlib import Path
import experiment as ex


def main():
    ex.verify()
    summary=ex.read(ex.RESULTS/'ANALYSIS.json')
    context=ex.load_context()
    records=ex.record_map(ex.RUN/'records')
    original=ex.record_map(ex.REFERENCE/'luna_records')
    new_bank=ex.make_bank(records,context)
    old_bank=ex.make_bank(original,context)
    valid_profiles={p for p in context['profiles'] if all(new_bank[(p,a)].get('valid') for a in ex.CFG['query_actions'])}
    old_valid_profiles={p for p in context['profiles'] if all(old_bank[(p,a)].get('valid') for a in ex.CFG['query_actions'])}
    common=valid_profiles & old_valid_profiles
    selected=[c for c in context['cases'] if c['profile_id'] in common]
    lookup=ex.trace_lookup(ex.rows(ex.RESULTS/'PAIRED_POLICY_TRACES.jsonl'))
    old_lookup=ex.trace_lookup(ex.rows(ex.REFERENCE/'LUNA_PAIRED_POLICY_TRACES.jsonl'))
    subset={}
    for b in ex.CFG['budgets']:
        subset[str(b)]={}
        for m in ex.CFG['methods']:
            new=[lookup[(c['case_id'],m,b)] for c in selected]
            old=[old_lookup[(c['case_id'],m,b)] for c in selected]
            subset[str(b)][m]={'n':len(selected),'deepseek_correct':sum(r['exact_decision_correct'] for r in new),
                'luna_correct':sum(r['exact_decision_correct'] for r in old),
                'same_selected_action':sum(n['selected_action']==o['selected_action'] for n,o in zip(new,old)),
                'same_query_sequence':sum(n['query_sequence']==o['query_sequence'] for n,o in zip(new,old))}
    jointly_valid=[k for k in new_bank if new_bank[k].get('valid') and old_bank[k].get('valid')]
    agreement=sum(ex.canonical(new_bank[k]['parsed']['value'])==ex.canonical(old_bank[k]['parsed']['value']) for k in jointly_valid)
    receipt=ex.read(ex.BASE/'RUN_RECEIPT.json')
    failures=[r for r in records.values() if r.get('attempted') and not r.get('transport_ok')]
    supplement={'analysis_status':'DESCRIPTIVE_POST_FAILURE_TRANSPORT_DISCLOSURE',
        'added_by':'finalize_report.py; reporting supplement, not frozen collector change',
        'initial_unique_attempts':receipt['initial_attempts_carried_forward'],
        'continuation_new_attempts':receipt['new_attempts'],'combined_unique_attempts':receipt['attempted'],
        'combined_retries':receipt['retries'],'transport_failures':len(failures),
        'transport_failure_classes':dict(Counter(r.get('error_class') for r in failures)),
        'transport_failure_profile_ids':sorted({r['profile_id'] for r in failures}),
        'complete_valid_deepseek_profiles':len(valid_profiles),'complete_valid_luna_profiles':len(old_valid_profiles),
        'common_complete_valid_profiles':len(common),'common_complete_valid_cases':len(selected),
        'jointly_valid_fields':len(jointly_valid),'jointly_valid_fields_equal':agreement,
        'common_complete_valid_profile_ids':sorted(common),'common_complete_valid_subset_metrics':subset,
        'subset_limit':'Post-failure descriptive common-valid subset; selection excludes failures and is not the 280-case primary endpoint.'}
    summary['transport_and_common_valid_supplement']=supplement
    ex.write(ex.RESULTS/'ANALYSIS.json',summary)
    ex.write(ex.RESULTS/'TRANSPORT_AND_COMMON_VALID.json',supplement)
    path=ex.RESULTS/'REPORT_ZH.md'
    report=path.read_text()
    report=report.replace('实际调用 ', '唯一请求尝试 ')
    report=report.replace('这不减少 DeepSeek 的 288 次实际调用。',
        '确定性缓存不减少原定的字段请求；实际尝试数与服务响应数见本补充。')
    marker='\n## 连接中断与续跑披露（补充）\n'
    if marker in report:
        report=report.split(marker)[0]
    extra=[marker,'',
        f"首轮 24 次唯一尝试得到 14 条有效回答和 10 次 TLS 连接失败，其余 264 个字段没有尝试。原首轮原始记录与冻结清单完整保留。",
        f"随后只对从未尝试的 {receipt['new_attempts']} 个字段续跑：改用 requests.Session 连接复用、并发 1、请求间隔 0.5 秒；没有重复失败项或成功项。合计 {receipt['attempted']}/288 次唯一尝试、重试 {receipt['retries']}，其中有效 {summary['valid_answers']}。",
        f"合并结果保留全部 {len(failures)} 次连接失败，涉及画像 {', '.join(supplement['transport_failure_profile_ids'])}。它们没有取得服务回答，不能计为模型内容错误；对下游推荐的影响仍按原规则保留。上面的 280 案例主表包含这部分影响。",
        '连接处理是在失败后调整的，不能声称整次运行按一个完全预注册的成功传输方案完成。恢复后的数据没有补做原失败响应。',
        f"DeepSeek 有 {len(valid_profiles)}/48 个画像拥有完整有效的六字段回答库；Luna 对应为 {len(old_valid_profiles)}/48。两模型共同完整有效的交集为 {len(common)} 个画像、{len(selected)} 个案例。",
        f"逐字段比较：两模型都有效的 {len(jointly_valid)} 条字段回答中，{agreement} 条解析值完全相同。完整有效交集的结果是补充描述，不能取代包含失败的 280 案例主结果。",
        '', '| 预算 | 策略 | 共同完整有效案例数 | Luna 正确 | DeepSeek 正确 |',
        '|---:|---|---:|---:|---:|']
    for b in (3,4,5):
        for m in ex.CFG['methods']:
            q=subset[str(b)][m]
            extra.append(f"| {b} | {m} | {q['n']} | {q['luna_correct']} | {q['deepseek_correct']} |")
    extra+=['', '这次结果应作为第二个模型/API 部署在固定画像字段问答上的描述性复核。连接失败、回答高度重合及开发数据复用共同限制了跨模型稳健性主张；不能据此认为自然顾客行为已得到验证。',
        '原首轮 14 条有效回答的原始 HTTP 响应位于 `artifacts/reference/initial_run/responses/`；续跑的原始响应位于 `artifacts/run/responses/`。TLS 失败只有连接异常记录，不能据请求尝试数推断服务端生成次数或账单。',
        '完整离线复现顺序：先运行 `python experiment.py analyze`，再运行 `python finalize_report.py` 生成本披露与补充描述；两步均为零模型调用。仅重算第一步会生成继承的基础报告，尚未包含续跑披露。',
        '本补充由只读审查发现报告披露缺口后添加；采集器、问题、评分、原始轨迹与主表计数未改变。补充脚本和输出哈希见 `REPORT_FINALIZATION_RECEIPT.json`。']
    path.write_text(report+'\n'.join(extra)+'\n')
    ex.write(ex.RESULTS/'REPORT_FINALIZATION_RECEIPT.json',{'finished_utc':ex.now(),
        'script_sha256':ex.digest(Path(__file__)),'frozen_collection_contract_sha256':ex.digest(ex.BASE/'FROZEN.json'),
        'reporting_supplement_plan_sha256':ex.digest(ex.BASE/'REPORTING_SUPPLEMENT_PLAN.json'),
        'script_matches_plan':ex.digest(Path(__file__))==ex.read(ex.BASE/'REPORTING_SUPPLEMENT_PLAN.json')['script_sha256'],
        'model_calls':0,'changes':'reporting disclosure and common-valid descriptives only; no primary score change'})
    artifacts={str(p.relative_to(ex.BASE)):ex.digest(p) for root in (ex.RUN,ex.RESULTS) for p in sorted(root.rglob('*'))
               if p.is_file() and p.name!='OUTPUT_MANIFEST.json'}
    ex.write(ex.RESULTS/'OUTPUT_MANIFEST.json',{'finished_utc':ex.now(),
        'frozen_contract_sha256':ex.digest(ex.BASE/'FROZEN.json'),'files':artifacts})
    print(ex.canonical({k:v for k,v in supplement.items() if k not in ('common_complete_valid_subset_metrics','common_complete_valid_profile_ids')}))


if __name__=='__main__':
    main()
