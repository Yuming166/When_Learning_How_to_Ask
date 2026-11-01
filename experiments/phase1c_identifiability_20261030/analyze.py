"""Frozen clustered development analysis. Selection is evaluated on later targets."""
import itertools
import json
from collections import Counter
import numpy as np
from design import ROOT,read_jsonl,write_json,sha
from policies import choose,explore_then_commit,repeat_and_compare


def interval(values,indices):
    a=np.asarray(values,dtype=float)
    means=a[indices].mean(axis=1)
    return {'mean':float(a.mean()),'cluster_bootstrap_95':list(map(float,np.quantile(means,[.025,.975]))),'groups':len(a)}


def main():
    raw=read_jsonl(ROOT/'run/raw.jsonl');truth=read_jsonl(ROOT/'data/private_truth.jsonl')
    assert len(raw)==192 and len({r['request_id'] for r in raw})==192, 'Incomplete coverage: no efficacy analysis'
    private={t['preference_id']:t for t in truth};scored=[]
    for r in raw:
        t=private[r['preference_id']]
        scored.append({**r,'theta':t['theta'],'verified_depth':t['verified_depth'],
                       'correct':r['canonical_answer']==t['theta'] if r['canonical_answer'] is not None else False})
    (ROOT/'run/scored.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in scored))
    groups=list(dict.fromkeys(r['group_id'] for r in scored));G=len(groups);assert G==8
    rng=np.random.default_rng(2026103013);indices=rng.integers(0,G,size=(10000,G))
    group_rows=[];all_prefix=[];all_pairs=[];all_quality=[]
    for g in groups:
        rows=[r for r in scored if r['group_id']==g];pairs=[];quality=[]
        for j in range(6):
            pairs.append({m:[r['canonical_answer'] for r in rows if r['target_index']==j and r['format']==m] for m in ['A','B']})
            quality.append({m:np.mean([r['correct'] for r in rows if r['target_index']==j and r['format']==m]).item() for m in ['A','B']})
        prefix=pairs[:2];all_prefix.append(prefix);all_pairs.append(pairs);all_quality.append(quality)
        etc=explore_then_commit(g,prefix)
        # True labels are used only by this explicitly labelled audit reference.
        label_scores={m:sum(q[m] for q in quality[:2]) for m in ['A','B']}
        labelled=max(label_scores,key=label_scores.get) if label_scores['A']!=label_scores['B'] else choose(g,[])
        urc_choices=[repeat_and_compare(g,pairs[:j]) for j in range(2,6)]
        score=lambda choices:float(np.mean([quality[j][m] for j,m in zip(range(2,6),choices)]))
        metrics={'Fixed A':score(['A']*4),'Fixed B':score(['B']*4),'Round-Robin':score(['A','B','A','B']),
                 'Explore-Then-Commit':score([etc]*4),'Unsupervised Repeat-and-Compare':score(urc_choices),
                 'Labelled-prefix reference':score([labelled]*4)}
        for digit in [0,1]:
            metrics[f'Constant digit {digit}']=float(np.mean([private[r['preference_id']]['correct_digit']==digit for r in rows if r['target_index']>=2]))
        metrics['Hindsight oracle (test labels)']=max(metrics['Fixed A'],metrics['Fixed B'])
        gap_pre=float(np.mean([q['A']-q['B'] for q in quality[:2]]))
        gap_test=metrics['Fixed A']-metrics['Fixed B']
        agreements={m:sum(int(None not in p[m] and p[m][0]==p[m][1]) for p in pairs) for m in ['A','B']}
        wrong_agreement={m:sum(int(all(r['status']=='valid' and not r['correct'] for r in rows if r['target_index']==j and r['format']==m)) for j in range(6)) for m in ['A','B']}
        group_rows.append({'group_id':g,'metrics':metrics,'etc_choice':etc,'urc_choices':urc_choices,
            'prefix_signed_accuracy_gap':gap_pre,'heldout_signed_accuracy_gap':gap_test,
            'signed_gap_product':gap_pre*gap_test,'repeat_agreement_pairs':agreements,
            'both_wrong_pairs':wrong_agreement,'full_accuracy':float(np.mean([r['correct'] for r in rows]))})
    metrics={name:interval([g['metrics'][name] for g in group_rows],indices) for name in group_rows[0]['metrics']}
    gains={}
    for method in ['Explore-Then-Commit','Unsupervised Repeat-and-Compare']:
        gains[method]={base:interval([g['metrics'][method]-g['metrics'][base] for g in group_rows],indices)
                       for base in ['Fixed A','Fixed B','Round-Robin','Constant digit 0','Constant digit 1']}
    full=interval([g['full_accuracy'] for g in group_rows],indices)
    sharing=interval([g['signed_gap_product'] for g in group_rows],indices)
    heldout_gap=interval([g['heldout_signed_accuracy_gap'] for g in group_rows],indices)
    # Exact all-permutation shuffled-prefix control; no labels reach the selector.
    choice_matrix=[[choose(groups[i],all_prefix[k]) for k in range(G)] for i in range(G)]
    quality_by_group=np.array([[np.mean([q[m] for q in quality[2:]]) for m in ['A','B']] for quality in all_quality])
    perm_scores=[]
    for perm in itertools.permutations(range(G)):
        perm_scores.append(float(np.mean([quality_by_group[i,'AB'.index(choice_matrix[i][perm[i]])] for i in range(G)])))
    actual=metrics['Explore-Then-Commit']['mean']
    shuffled={'permutations':len(perm_scores),'mean':float(np.mean(perm_scores)),
              'range_95':list(map(float,np.quantile(perm_scores,[.025,.975]))),
              'fraction_at_least_actual':float(np.mean(np.array(perm_scores)>=actual)),
              'scope':'Exact permutation diagnostic, includes ties/identity; exchangeability is not established as a causal randomization design.'}
    gap_product_supported=sharing['cluster_bootstrap_95'][0]>0
    basic_supported=full['cluster_bootstrap_95'][0]>.5
    transfer_supported=all(v['cluster_bootstrap_95'][0]>0 for v in gains['Explore-Then-Commit'].values())
    decision={'basic_correctness_supported':basic_supported,'cross_target_signed_gap_supported':gap_product_supported,
        'unlabelled_etc_gain_over_all_fixed_and_rr_supported':transfer_supported,
        'empirical_foundation_supported':basic_supported and gap_product_supported and transfer_supported,
        'phase2_started':False,'phase2_ready':False,
        'status':'REVIEW_ONLY_PENDING_TRIVIAL_BASELINES' if basic_supported and gap_product_supported and transfer_supported else 'REVISE_OR_NO_GO',
        'additional_limit':'Direct type and public-metadata selectors were not newly generated under the 192 task-response cap; a positive foundation alone would not rule them out.'}
    strata={}
    for key in ['format','option_flip','template_id','verified_depth','theta']:
        strata[key]={str(v):{'n':sum(r[key]==v for r in scored),'correct':sum(r[key]==v and r['correct'] for r in scored),
                             'invalid':sum(r[key]==v and r['status']!='valid' for r in scored)} for v in sorted({r[key] for r in scored})}
    result={'development_only':True,'model_calls':len(raw),'valid':sum(r['status']=='valid' for r in raw),
        'invalid_or_error':sum(r['status']!='valid' for r in raw),'full_correct':sum(r['correct'] for r in scored),
        'full_accuracy':full,'heldout_per_strategy_denominator':64,'heldout_unique_targets':32,
        'metrics':metrics,'paired_gains':gains,'group_sharing_gap_product':sharing,'heldout_A_minus_B':heldout_gap,
        'groups':group_rows,'shuffled_prefix_control':shuffled,'strata':strata,'decision':decision,
        'replay_query_cost_per_group':{'Fixed A / Fixed B / Round-Robin':8,'Explore-Then-Commit':16,
                                      'Unsupervised Repeat-and-Compare':22,'actual_full_grid':24},
        'score_scope':'Mean correctness of both chosen-format responses on four heldout targets per group, not joint recovery accuracy or equal-cost policy superiority.'}
    write_json(ROOT/'run/analysis.json',result)
    failures=[{k:r[k] for k in ['request_id','group_id','preference_id','format','repeat','option_flip','prompt','raw_output','canonical_answer','theta','verified_depth','status']} for r in scored if not r['correct']]
    (ROOT/'run/failure_examples.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in failures))
    lines=['# Phase 1c 开发测试结果','',f"判断：**{decision['status']}**。未进入 Phase 2。",'',
       f"实际 {len(raw)} 次回答，{result['valid']} 有效；{result['full_correct']}/{len(raw)} 正确。所有结果是开发观察，不是确认实验。",'',
       '|策略|后四题所选形式的平均正确率|世界聚类 bootstrap 95% 区间|','|---|---:|---:|']
    for name,s in metrics.items():
        lo,hi=s['cluster_bootstrap_95'];lines.append(f"|{name}|{s['mean']:.2%}|[{lo:.2%}, {hi:.2%}]|")
    lines+=['',f"基础正确率获得支持：{basic_supported}；跨目标有符号 gap 乘积获得支持：{gap_product_supported}；ETC 对两个固定形式和 RR 的配对提升均获得支持：{transfer_supported}。",'',
        '每项策略在相同的 32 个后续目标上计分，共 64 个回答；前两题作为探索，绝不使用前两题的真实标签选择形式。Repeat-and-Compare 在每题前利用此前目标两种形式的重复一致性更新。无效回答计错，未删档案。',
        '', '成本不同：固定形式/RR 在后续目标用 8 次回答；ETC 连探索共 16 次；持续均衡采样后比较的 Repeat-and-Compare 共 22 次。此表测迁移可靠性，不能用于声称同预算方法胜出。Oracle 是显式引用，test-label oracle 有事后乐观偏差。',
        '',f"打乱探索组与测试组匹配的全部 {len(perm_scores)} 个排列：平均 {shuffled['mean']:.2%}，不少于真实匹配表现的比例 {shuffled['fraction_at_least_actual']:.3f}。这是小样本诊断，非已证明可交换性的随机试验 p 值。",'',
        '完整每组 gap、一致但双错、选项位置/模板/推理深度分层及所有错误见 analysis.json 和 failure_examples.jsonl。8 个世界不足以验证共同 p/q、每个渠道高于随机或条件独立。两次重复无法区分持续语义错误与某个极低可靠率。模板 0 用于探索、模板 1 用于后续目标，模板变化与目标变化同时发生，不能单独归因。',
        '', '本轮没有额外 direct-type/metadata 模型调用，也没有测试 35B。即便基础条件通过，仍需排除便宜的类型识别策略后再讨论 Phase 2。']
    (ROOT/'run/REPORT_ZH.md').write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.8));names=list(metrics)
    for i,n in enumerate(names):
        s=metrics[n];lo,hi=s['cluster_bootstrap_95'];ax.errorbar(s['mean']*100,i,xerr=[[100*(s['mean']-lo)],[100*(hi-s['mean'])]],fmt='o',capsize=3)
    ax.set_yticks(range(len(names)),names);ax.invert_yaxis();ax.set_xlabel('Held-out response correctness (%)');ax.axvline(50,color='gray',linestyle=':');ax.set_title('Development only: 8 ProofWriter worlds, 32 held-out targets')
    fig.tight_layout();fig.savefig(ROOT/'run/discovery.png',dpi=180);fig.savefig(ROOT/'run/discovery.pdf');plt.close(fig)
    print(json.dumps({'decision':decision,'full_accuracy':full,'metrics':metrics},indent=2))


if __name__=='__main__':main()
