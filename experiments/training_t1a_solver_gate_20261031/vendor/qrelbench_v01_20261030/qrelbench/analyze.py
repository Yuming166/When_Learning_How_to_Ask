"""Frozen descriptive analysis for the bounded CPU development pilot."""
import csv
import json
import math
from pathlib import Path
import numpy as np
from .evaluate import ROOT
from .policies import NAMES


def wilson(success,total):
    if total==0:return [None,None]
    z=1.959963984540054;p=success/total;den=1+z*z/total
    c=(p+z*z/(2*total))/den;h=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return [max(0,c-h),min(1,c+h)]


def grouped(rows,fields):
    out={}
    for row in rows:out.setdefault(tuple(json.dumps(row[f],sort_keys=True) for f in fields),[]).append(row)
    return out.values()


def summarize(rows):
    table=[]
    for group in grouped(rows,['protocol','scenario','partition','online_cap','delta','policy']):
        first=group[0];n=len(group);complete=[r for r in group if r['completed']]
        entry={k:first[k] for k in ['protocol','scenario','partition','online_cap','delta','policy']}
        entry.update(n=n,exact=sum(r['exact'] for r in group)/n,
            exact_95=wilson(sum(r['exact'] for r in group),n),
            completion=len(complete)/n,completed_exact=sum(r['exact'] for r in complete),
            certificate_errors=sum(r['any_certificate_error'] for r in group),
            mean_online_all=float(np.mean([r['online'] for r in group])),
            mean_offline=float(np.mean([r['costs']['offline'] for r in group])),
            mean_total=float(np.mean([r['total_acquisition'] for r in group])),
            censored=n-len(complete),mean_type_cost=float(np.mean([r['costs']['type'] for r in group])))
        table.append(entry)
    return table


def main():
    run=ROOT/'artifacts/run';execution=json.loads((run/'execution.json').read_text())
    if execution['status']!='completed':raise SystemExit('Incomplete pilot: report execution status before interpreting results')
    rows=[json.loads(line) for line in (run/'episodes.jsonl').read_text().splitlines()]
    assert len(rows)==execution['planned_episodes']==execution['attempted_episodes']
    assert all(r['online']<=r['online_cap'] for r in rows)
    assert all(r['costs']['offline']==2*r['calibration_size'] for r in rows)
    summary=summarize(rows)
    out=ROOT/'artifacts/analysis';out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    fields=list(summary[0])
    with (out/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(summary)
    paired=[]
    rng=np.random.default_rng(2026103017)
    for cells in grouped([r for r in rows if r['scenario']=='base' and r['protocol']=='fixed_budget'],['partition','online_cap']):
        by={(r['policy'],r['index']):r for r in cells};indices=sorted({r['index'] for r in cells})
        bootstrap=rng.integers(0,len(indices),size=(5000,len(indices)))
        for policy in NAMES:
            values=np.array([float(by[policy,i]['exact'])-float(by['Round-Robin',i]['exact']) for i in indices])
            paired.append({'partition':cells[0]['partition'],'budget':cells[0]['online_cap'],'policy':policy,
                'mean_exact_gain_over_rr':float(values.mean()),'paired_episode_bootstrap_95':list(map(float,np.quantile(values[bootstrap].mean(axis=1),[.025,.975])))})
    (out/'paired.json').write_text(json.dumps(paired,indent=2)+'\n')
    valid_fc=[r for r in rows if r['protocol']=='fixed_confidence' and r['certificate_contract_valid']]
    invalid_fc=[r for r in rows if r['protocol']=='fixed_confidence' and not r['certificate_contract_valid']]
    facts={'actual_episodes':len(rows),'online_actions':sum(r['online'] for r in rows),'llm_calls':0,
           'valid_contract_confidence_episodes':len(valid_fc),
           'valid_contract_certificate_errors':sum(r['any_certificate_error'] for r in valid_fc),
           'valid_contract_censored':sum(r['censored'] for r in valid_fc),
           'out_of_model_confidence_episodes':len(invalid_fc),
           'out_of_model_certificate_errors':sum(r['any_certificate_error'] for r in invalid_fc),
           'decision':'GO_TECHNICAL_CONTROLLED_BENCHMARK_ONLY',
           'confirmation_ready':False,'natural_shared_reliability_established':False}
    (out/'facts.json').write_text(json.dumps(facts,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(13,4.8))
    parts=[[1,15],[2,14],[4,12],[8,8],[16]]
    for policy in NAMES:
        values=[next(s['exact'] for s in summary if s['scenario']=='base' and s['protocol']=='fixed_budget' and s['online_cap']==256 and s['partition']==p and s['policy']==policy) for p in parts]
        axes[0].plot(range(5),values,'o-',label=policy,alpha=.85)
        values=[np.mean([s['mean_online_all'] for s in summary if s['scenario']=='base' and s['protocol']=='fixed_confidence' and s['delta']==delta and s['policy']==policy]) for delta in [.1,.05,.01]]
        axes[1].plot([.1,.05,.01],values,'o-',label=policy,alpha=.85)
    axes[0].set_xticks(range(5),[str(p) for p in parts]);axes[0].set_ylabel('Exact recovery fraction');axes[0].set_title('Fixed online budget 256; n=24 per cell')
    axes[1].set_xscale('log');axes[1].invert_xaxis();axes[1].set_xlabel('delta');axes[1].set_ylabel('Mean min(T, 4096), including censored');axes[1].set_title('Confidence certificate; n=2 per partition/cell')
    axes[0].set_xlabel('Known partition (d=16)');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=4,fontsize=8)
    fig.suptitle('QRelBench v0.1 — controlled CPU development only');fig.tight_layout(rect=(0,.15,1,.94))
    fig.savefig(out/'pilot.png',dpi=180);fig.savefig(out/'pilot.pdf');plt.close(fig)
    lines=['# QRelBench v0.1 — CPU Development Pilot','',
      '## Material Passport','Mode: bounded simulation run; source: frozen local code/config; phase: development; no external model calls.','',
      '**GO：作为理论受控 benchmark 原型。尚不具备大规模确认或真实 LLM 可靠性结论。**','',
      f"实际完成 {len(rows)} 个策略-回合评估，{facts['online_actions']:,} 次在线动作；模型调用 0。固定预算任务/类型询问共同计费，校准成本另计。",'',
      '## 固定预算：16 个事实全部恢复','',
      '以下是 B=256 的 exact recovery，不是逐题准确率。每格 24 回合，比例步长 4.17%；完整 Wilson 区间与其他预算见 summary.json/csv；与 RR 的配对开发区间见 paired.json。','',
      '|策略|[1,15]|[2,14]|[4,12]|[8,8]|[16]|','|---|---:|---:|---:|---:|---:|']
    for policy in NAMES:
        vals=[next(s['exact'] for s in summary if s['scenario']=='base' and s['protocol']=='fixed_budget' and s['online_cap']==256 and s['partition']==p and s['policy']==policy) for p in parts]
        lines.append('|'+policy+'|'+'|'.join(f'{v:.1%}' for v in vals)+'|')
    lines+=['','所有固定预算策略均使用相同有限校准样本及共同的组内 joint MAP 解码器；p/q 仅由参考流估计。解码器对估计参数下的类型求和，不接收真实 p/q。它不是连续未知率的完整 Bayes 解，也不证明任何信息分配最优性。Oracle 只额外知道格式类型。',
      '', '## 固定置信与删失','',
      f"满足多数证书条件的固定置信回合 {len(valid_fc)}，其中 {sum(r['censored'] for r in valid_fc)} 个达到预算上限但未完成，观察到 {facts['valid_contract_certificate_errors']} 个已发证符号错误。每个基础单元仅 2 回合，不能据此检验 delta 水平的错误控制。",'',
      '采用独立审阅的保守 time-uniform 多数证书，不是 Theory_Note 中的联合 GLR。已发证符号冻结；未完成预测只作为显式删失的诊断，绝不视作 delta-correct 完成。报告 min(T,cap) 的全分母均值，不将它冒充无删失 E[T]。原模型允许 q=.5；固定或错误永久承诺策略不一定终止。','',
      '|策略|delta=.10 完成/总数|delta=.05 完成/总数|delta=.01 完成/总数|']
    lines.append('|---|---:|---:|---:|')
    for policy in NAMES:
        values=[]
        for delta in [.1,.05,.01]:
            rr=[r for r in rows if r['scenario']=='base' and r['protocol']=='fixed_confidence' and r['delta']==delta and r['policy']==policy]
            values.append(f"{sum(r['completed'] for r in rr)}/{len(rr)}")
        lines.append('|'+policy+'|'+'|'.join(values)+'|')
    lines+=['','## 负控制','',
      '|控制|固定预算平均 exact（跨七策略，每策略8回合）|固定置信已发证错误回合/总数|删失/总数|','|---|---:|---:|---:|']
    for scenario in ['equal_informative','equal_chance','no_sharing','perfect_type','label_asymmetric','persistent']:
        fb=[r for r in rows if r['scenario']==scenario and r['protocol']=='fixed_budget'];fc=[r for r in rows if r['scenario']==scenario and r['protocol']=='fixed_confidence']
        lines.append(f"|{scenario}|{np.mean([r['exact'] for r in fb]):.1%}|{sum(r['any_certificate_error'] for r in fc)}/{len(fc)}|{sum(r['censored'] for r in fc)}/{len(fc)}|")
    lines+=['','该控制表是技术诊断，跨策略平均不作算法比较。p=q 违反严格间隔；真实单元素组属于有效无共享模型；s=1 是单独的完美类型情形。label_asymmetric 对 theta=0 使用 1-r、对 theta=1 使用 r，使部分渠道低于随机，固定置信证书不适用；persistent 固定每题每形式的第一错误，也不适用。它们的错误必须保留，不能解释为证书在原模型中失效。','',
      '## 可作与不可作的结论','',
      '- 构造满足：独立真值、一事实一记录、组共享类型、未知全局 p/q、有限标记校准、逐调用新鲜伪随机错误、完整成本分账。',
      '- 执行支持：冻结 CPU pilot 的 exact/cost/删失统计；确定性语义与小规模独立数值核验；记录在案的负控制行为。',
      '- 未验证：任何自然 LLM 的格式可靠性、跨措辞稳定性、人类用户行为、真实电商数据覆盖、复杂方法优越或 WWW 接收可能性。',
      '- 未实现：信息最优分配、原理论联合 GLR 和最优 leading coefficient 验证。本轮没有进入 Phase 2。',
      '- 测试仅开发命名空间；确认评估未授权，未执行。相同事实/误差子流在策略间用于配对，各回合 learner 状态重建，不得跨回合积累信息。',
      '', '先前 Phase01/UserBench/Phase1c 负结果保持原样。此次合成环境成功并不推翻那些结果，也不证明自然可靠性共享存在。']
    (ROOT/'PILOT_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(facts,indent=2))


if __name__=='__main__':main()
