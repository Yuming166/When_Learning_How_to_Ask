"""All-world restricted-cost analysis; no completed-only expected-cost claims."""
import json
import math
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from .bootstrap import ROOT
from .runner import jobs
from .policy import POLICIES
from phase2a.coefficients import solve_allocation,oracle_coefficient,fit_ordered,kl


def load(path):return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def identity(row):return (row['policy'],row['index'])


def cell(row):return (tuple(row['partition']),row['alpha'],row['R'])


def confidence_at(rows,B):
    if not rows or any(B>r['online_cap'] for r in rows):raise ValueError('Budget beyond observed support')
    completed=[r['complete'] and r['online']<=B for r in rows]
    wrong=[done and not r['exact'] for done,r in zip(completed,rows)]
    return {'B':B,'n':len(rows),'completed':sum(completed),'wrong_certificates':sum(wrong),
        'completion_fraction':float(np.mean(completed)),'wrong_fraction_all':float(np.mean(wrong)),
        'mean_min_T_B':float(np.mean([min(r['online'],B) for r in rows]))}


def resample_mean(values,rng,n=4000):
    values=np.asarray(values,float)
    return np.quantile(rng.choice(values,(n,len(values)),replace=True).mean(axis=1),[.025,.975]).tolist()


def expected_information(counts,type_answers,types,partition,p,q,M,eta=.05,s=.8):
    """Evaluator-only population KL at actual counts, min all wrong sign states.

    Counts are not symmetrized: each reversed coordinate has its actual counts.
    The raw truth signs cancel after mathematical orientation. True group types
    are used ONLY after the run; this function is never imported by a learner.
    """
    membership=[g for g,k in enumerate(partition) for _ in range(k)]
    n=np.asarray(counts).sum(axis=2);kappa=kl(s,1-s);minimum=math.inf
    for mask in range(2**len(partition)):
        for j in range(len(membership)):
            su,nu,sv,nv=M*p,M,M*q,M
            for i,g in enumerate(membership):
                a,b=n[i,types[g]],n[i,1-types[g]]
                sp=(p if i!=j else 1-p)*a;sq=(q if i!=j else 1-q)*b
                if mask>>g&1:sv+=sp;nv+=a;su+=sq;nu+=b
                else:su+=sp;nu+=a;sv+=sq;nv+=b
            u,v=fit_ordered(su,nu,sv,nv,eta)
            value=M*(kl(p,u)+kl(q,v))
            for i,g in enumerate(membership):
                x,y=(v,u) if mask>>g&1 else (u,v)
                if i==j:x,y=1-x,1-y
                value+=n[i,types[g]]*kl(p,x)+n[i,1-types[g]]*kl(q,y)
            value+=sum(len(type_answers[g])*kappa for g in range(len(partition)) if mask>>g&1)
            minimum=min(minimum,value)
    return float(minimum)


def main():
    cfg=json.loads((ROOT/'config.json').read_text());run=ROOT/'artifacts/run'
    receipt=json.loads((run/'execution.json').read_text())
    if receipt['status']!='completed':raise RuntimeError('Partial run: retain failure/missingness; no complete comparison')
    rows=load(run/'trajectories.jsonl');plan=jobs(cfg)
    expected={(policy,j['index']) for j in plan for policy in POLICIES}
    if Counter(identity(r) for r in rows)!=Counter(expected) or len(rows)!=receipt['finished_trajectories'] or len(rows)!=receipt['planned_trajectories']:
        raise RuntimeError('Missing or duplicate planned trajectory')
    if any(sum(r['costs'][k] for r in rows)!=receipt['costs_including_partial'][k] for k in ['task','type','offline']):raise RuntimeError('Complete-run cost totals disagree')
    private=load(run/'private/reproduction.jsonl');priv={(r['policy'],r['job']['index']):r for r in private}
    if len(priv)!=len(rows):raise RuntimeError('Private reproduction coverage differs')
    out=ROOT/'artifacts/analysis';out.mkdir(exist_ok=False)
    groups=defaultdict(list)
    for r in rows:groups[(cell(r),r['policy'])].append(r)
    rng=np.random.default_rng(cfg['bootstrap_analysis_seed']);refs=[];summary=[];paired=[];curves=[];diagnostics=[]
    for part in cfg['partitions']:
        for alpha in cfg['alphas']:
            task=solve_allocation(part,cfg['p'],cfg['q'],alpha)
            typed=solve_allocation(part,cfg['p'],cfg['q'],alpha,cfg['type_accuracy'])
            oracle=oracle_coefficient(sum(part),cfg['p'],cfg['q'],alpha)
            refs.append({'partition':part,'alpha':alpha,'K_task_only':task['K'],'K_task_type':typed['K'],
                'K_oracle':oracle['K'],'task_lower':task['lower_bound'],'type_lower':typed['lower_bound'],
                'scope':'post-run population reference only; no true parameter sent to learner'})
    for (key,policy),rr in sorted(groups.items()):
        part,alpha,R=key;cap=rr[0]['online_cap'];n=len(rr);costs=[r['online']/R for r in rr]
        reference=next(ref for ref in refs if ref['partition']==list(part) and ref['alpha']==alpha)
        coefficient=reference['K_oracle'] if policy=='Oracle Format' else reference['K_task_type'] if policy in ['Aligned Tracking','Direct Type Query'] else reference['K_task_only']
        summary.append({'partition':list(part),'alpha':alpha,'R':R,'policy':policy,'n':n,'cap':cap,
            'completed':sum(r['complete'] for r in rr),'censored':sum(r['censored'] for r in rr),
            'wrong_certificates':sum(r['complete'] and not r['exact'] for r in rr),
            'mean_min_T_B_over_R':float(np.mean(costs)),'bootstrap_mean_95':resample_mean(costs,rng,cfg['bootstrap_resamples']),
            'coefficient_reference':coefficient,'restricted_ratio_over_K':float(np.mean(costs))/coefficient,
            'offline':rr[0]['costs']['offline'],'mean_total_acquisition_over_R':float(np.mean([r['total_acquisition']/R for r in rr])),
            'mean_task':float(np.mean([r['costs']['task'] for r in rr])),
            'mean_type':float(np.mean([r['costs']['type'] for r in rr])),
            'mean_glr_seconds':float(np.mean([r['glr_seconds'] for r in rr])),
            'mean_planner_seconds':float(np.mean([r['planner_seconds'] for r in rr])),
            'completed_costs':[r['online'] for r in rr if r['complete']],
            'interpretation':'restricted mean; any censoring leaves E[T]/R unidentified; n=4 exploratory intervals'})
        Bs=sorted(set(min(cap,b) for b in [R,2*R,4*R,8*R,12*R,16*R,24*R,cap]))
        curves.append({'partition':list(part),'alpha':alpha,'R':R,'policy':policy,'curve':[confidence_at(rr,B) for B in Bs]})
    for key in sorted({cell(r) for r in rows}):
        part,alpha,R=key;left={r['index']:r for r in groups[(key,'Aligned Tracking')]}
        for baseline in POLICIES[:-1]:
            right={r['index']:r for r in groups[(key,baseline)]}
            if left.keys()!=right.keys():raise RuntimeError('Unpaired cell')
            diff=[(left[i]['online']-right[i]['online'])/R for i in sorted(left)]
            paired.append({'partition':list(part),'alpha':alpha,'R':R,'baseline':baseline,'n_pairs':len(diff),
                'aligned_minus_baseline_restricted_over_R':float(np.mean(diff)),
                'paired_bootstrap_95':resample_mean(diff,rng,cfg['bootstrap_resamples']),
                'aligned_censored':sum(r['censored'] for r in left.values()),'baseline_censored':sum(r['censored'] for r in right.values()),
                'exploratory':True,'multiplicity_adjusted':False})
    for r in rows:
        if r['policy']!='Aligned Tracking':continue
        history=r['estimation_history'];last=history[-1]
        truth=priv[identity(r)]
        info=expected_information(r['counts'],r['type_answers'],truth['types'],r['partition'],r['p'],r['q'],r['M'],r['eta'],r['s'])
        diagnostics.append({'partition':r['partition'],'alpha':r['alpha'],'R':r['R'],'index':r['index'],
            'online':r['online'],'complete':r['complete'],'forced_fraction':r['forced_tasks']/r['online'],
            'last_theta_errors':last['theta_errors'],'last_type_errors':last['type_errors'],
            'last_p_error':last['p_error'],'last_q_error':last['q_error'],'last_grid_mesh':last['grid_mesh'],
            'solver_updates':len(history),'maximum_solver_relative_gap':max(e['solver_relative_gap'] for e in history),
            'numerical_floor_active':any(e['numerical_floor_active'] for e in history),
            'last_update_ratio':last['online']/r['online'],
            'final_beta_over_R':r['fit']['beta']/r['R'],'realized_population_min_KL_over_R':info/r['R'],
            'scope':'population information uses private true types only in offline analysis; never learner input'})
    totals={k:sum(r['costs'][k] for r in rows) for k in ['task','type','offline']}
    facts={'trajectories':len(rows),'independent_worlds':len({r['index'] for r in rows}),'cells':len({cell(r) for r in rows}),
        'policies':POLICIES,'per_cell_n':cfg['episodes_per_cell'],'costs':totals,'online_actions':totals['task']+totals['type'],
        'total_acquisition':sum(totals.values()),'completed':sum(r['complete'] for r in rows),
        'censored':sum(r['censored'] for r in rows),'wrong_certificates':sum(r['complete'] and not r['exact'] for r in rows),
        'planner_seconds':sum(r['planner_seconds'] for r in rows),'glr_seconds':sum(r['glr_seconds'] for r in rows),
        'wall_seconds':receipt['seconds'],'new_model_calls':0,'new_confirmation_episodes':0,
        'formal_exact_machine_optimality':False,'scope':'independent-cell development cost diagnostic, no inferential confirmation'}
    for name,value in [('facts',facts),('summary',summary),('paired',paired),('coefficients',refs),('confidence_curves',curves),('diagnostics',diagnostics)]:
        (out/f'{name}.json').write_text(json.dumps(value,indent=2)+'\n')
    plots(summary,refs,diagnostics,curves,out,cfg)
    report(facts,summary,refs,diagnostics,ROOT)
    print(json.dumps(facts,indent=2))


def plots(summary,refs,diagnostics,curves,out,cfg):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors=dict(zip(POLICIES,['#777777','#e58115','#19a7a0','#228b22','#bd3030']))
    def save(fig,name):
        fig.tight_layout();fig.savefig(out/f'{name}.png',dpi=170);fig.savefig(out/f'{name}.pdf');plt.close(fig)
    for total in [False,True]:
        fig,axes=plt.subplots(2,2,figsize=(12,8))
        for pi,part in enumerate(cfg['partitions']):
            for ai,alpha in enumerate(cfg['alphas']):
                ax=axes[pi,ai];ref=next(r for r in refs if r['partition']==part and r['alpha']==alpha)
                for policy in POLICIES:
                    rr=sorted([r for r in summary if r['partition']==part and r['alpha']==alpha and r['policy']==policy],key=lambda r:r['R'])
                    shift=2*alpha if total else 0
                    ys=[r['mean_min_T_B_over_R']+shift for r in rr]
                    lo=[max(0,y-(r['bootstrap_mean_95'][0]+shift)) for r,y in zip(rr,ys)]
                    hi=[max(0,(r['bootstrap_mean_95'][1]+shift)-y) for r,y in zip(rr,ys)]
                    ax.errorbar([r['R'] for r in rr],ys,yerr=[lo,hi],fmt='o-',capsize=2,label=policy,color=colors[policy],markersize=4)
                    for r,y in zip(rr,ys):
                        if r['censored']:ax.plot(r['R'],y,'x',color='black',markersize=9)
                shift=2*alpha if total else 0
                for key,label,color,style in [('K_task_type','K tasks+type','#111111',':'),('K_task_only','K tasks only','#777777','--'),('K_oracle','K Oracle','#228b22','--')]:ax.axhline(ref[key]+shift,label=label,color=color,ls=style,lw=1)
                ax.set_xscale('log',base=4);ax.set_xticks(cfg['Rs'],cfg['Rs']);ax.set_ylim(bottom=0)
                ax.set_title(f'{part}; alpha={alpha}; 4 independent worlds/point');ax.set_xlabel('R = log(1/delta)')
                ax.set_ylabel('(Restricted online + offline)/R' if total else 'Restricted mean online/R');ax.grid(alpha=.15)
        axes[0,0].legend(fontsize=6);fig.suptitle('x marks censoring; intervals exploratory bootstrap; no E[T] identification when censored',fontsize=9)
        save(fig,'total_cost_convergence' if total else 'online_cost_convergence')
    fig,axes=plt.subplots(2,3,figsize=(14,7))
    specs=[('forced_fraction','Forced task fraction'),('last_theta_errors','Last sign-estimation errors'),('last_type_errors','Last type-estimation errors'),('final_beta_over_R','Stopping boundary / R'),('realized_population_min_KL_over_R','Population min KL at actual counts / R'),('last_grid_mesh','Last estimator grid mesh')]
    for ax,(key,label) in zip(axes.flat,specs):
        for part in cfg['partitions']:
            for alpha in cfg['alphas']:
                values=[float(np.mean([r[key] for r in diagnostics if r['partition']==part and r['alpha']==alpha and r['R']==R])) for R in cfg['Rs']]
                ax.plot(cfg['Rs'],values,'o-',label=f'{part}, alpha={alpha}')
        ax.set_xscale('log',base=4);ax.set_xticks(cfg['Rs'],cfg['Rs']);ax.set_title(label);ax.set_xlabel('R')
    axes[0,0].legend(fontsize=6);save(fig,'aligned_diagnostics')
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for policy in POLICIES:
        rr=[r for r in summary if r['policy']==policy]
        axes[0,0].plot(cfg['Rs'],[sum(r['completed'] for r in rr if r['R']==R)/sum(r['n'] for r in rr if r['R']==R) for R in cfg['Rs']],'o-',label=policy,color=colors[policy])
        axes[0,1].plot(cfg['Rs'],[sum(r['wrong_certificates'] for r in rr if r['R']==R)/sum(r['n'] for r in rr if r['R']==R) for R in cfg['Rs']],'o-',color=colors[policy])
        axes[1,0].plot(cfg['Rs'],[float(np.mean([r['mean_planner_seconds']+r['mean_glr_seconds'] for r in rr if r['R']==R])) for R in cfg['Rs']],'o-',color=colors[policy])
    axes[0,0].set_title('Completion / all paths');axes[0,0].set_ylim(0,1.05);axes[0,0].legend(fontsize=6)
    axes[0,1].set_title('Wrong certifications / all paths');axes[1,0].set_title('Planner + GLR wall seconds / path')
    for i,policy in enumerate(POLICIES):
        values=[n for r in summary if r['policy']==policy and r['R']==1024 for n in r['completed_costs']]
        axes[1,1].plot([i]*len(values),values,'o',color=colors[policy],alpha=.5,markersize=4)
    axes[1,1].set_xticks(range(5),['RR','RRC','Direct','Oracle','Aligned'],rotation=20);axes[1,1].set_title('Completed cost distribution, R=1024 (conditional)')
    for ax in [axes[0,0],axes[0,1],axes[1,0]]:ax.set_xscale('log',base=4);ax.set_xticks(cfg['Rs'],cfg['Rs']);ax.set_xlabel('R')
    save(fig,'completion_and_compute')
    # The requested completion/wrong/restricted-cost curves against query B.
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for policy in POLICIES:
        subset=[r for r in curves if r['policy']==policy and r['R']==1024]
        Bs=[r['B'] for r in subset[0]['curve']]
        for ai,key in enumerate(['completion_fraction','wrong_fraction_all','mean_min_T_B']):
            axes[ai].plot(Bs,[float(np.mean([next(x[key] for x in r['curve'] if x['B']==B) for r in subset])) for B in Bs],'o-',label=policy,color=colors[policy])
    for ax,title in zip(axes,['Completed / all','Wrong certificates / all','Mean min(T,B), censoring retained']):ax.set_xscale('log',base=2);ax.set_xlabel('Online budget B');ax.set_title(title)
    axes[0].legend(fontsize=6);fig.suptitle('R=1024; four prespecified cells, 16 independent worlds per policy',fontsize=9);save(fig,'budget_completion_curves')


def report(facts,summary,refs,diagnostics,root):
    lines=['# Phase 2b：证明与代码对齐、查询成本收敛诊断','',
        '## Material Passport','',
        '范围：受控 Bernoulli benchmark、理论证明审计和一次小规模 CPU 开发批次。独立单元为预先生成的档案/响应世界；不同单元使用不同索引，五个策略只在同一单元内配对。数学审查为分离的同模型家族代理；没有外部专家或跨模型认证。','',
        '**结论边界：可以核验理想策略的证明条件，并诊断有限 R 的成本变化；本轮不能证明有限精度程序渐近最优，也不是独立确认实验。**','',
        f"完成 {facts['trajectories']} 条轨迹、{facts['independent_worlds']} 个独立世界、{facts['online_actions']:,} 次在线动作、{facts['costs']['offline']:,} 个离线观测；主批次用时 {facts['wall_seconds']:.2f} 秒。新模型调用和独立确认样本均为零。",'',
        '## P0：证明与实现','',
        '原 Theory_Note.md 未改写。证明补充见 PROOF_ADDENDUM.md 及独立 audit/THEOREM1_REVIEW.md；逐项对应见 ALIGNMENT_MATRIX.md。有限校准必须与在线观测一起集中，不能把固定离线坏事件的概率当作 t 的衰减函数。确定性累计分配跟踪通过显式 O(sqrt(t)) 偏差界替代随机分配；强制样本估计、渐细网格和延迟更新均具有明确条件。','',
        '实际 GLR 是连续参数解析 profile 加离散穷举，R 直接以对数表示，可处理 R=1024，未截断或下溢为零。Python 使用 float64、固定底层求解容差/信息 pad/舍入，未提供区间算术证书；理想实数算法的论证不等于对当前可执行程序的精确最优性认证。','',
        '## P1：N/R 与 K','',
        '下表为所有四个独立世界的截断平均在线成本/R；完成列为 Aligned Tracking 的完成数。任何删失均保留，不能将该统计量解释为无截断 E[T]/R。不同 R 使用独立单元，因此曲线不会通过重复使用两个档案制造样本量。','',
        '|分组|alpha|R|K 任务+类型|K Oracle|Aligned N/R|Aligned 完成|RRC N/R|RR N/R|Direct N/R|Oracle N/R|',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for ref in refs:
        for R in [16,64,256,1024]:
            def row(policy):return next(r for r in summary if r['partition']==ref['partition'] and r['alpha']==ref['alpha'] and r['R']==R and r['policy']==policy)
            a=row('Aligned Tracking')
            vals=[row(p)['mean_min_T_B_over_R'] for p in ['Repeat-and-Compare','Round-Robin','Direct Type Query','Oracle Format']]
            lines.append(f"|{ref['partition']}|{ref['alpha']}|{R}|{ref['K_task_type']:.4f}|{ref['K_oracle']:.4f}|{a['mean_min_T_B_over_R']:.4f}|{a['completed']}/4|"+'|'.join(f'{v:.4f}' for v in vals)+'|')
    lines+=['',
        '完整逐单元 bootstrap 区间、配对差异、删失与计算时间见 artifacts/analysis/summary.json 和 paired.json。区间只有 n=4，属于探索性描述，未做多重比较校正；不据此宣称普遍胜出或统计确认。在线成本和总 acquisition/R 分开绘图；总成本另加2M/R=2alpha，跨alpha的在线节省不能当作总获取成本下降。','',
        '## P2：停止、删失与计算成本','',
        f"全部轨迹中 {facts['completed']} 完成，{facts['censored']} 删失，{facts['wrong_certificates']} 次已完成错误认证。零观测错误不能验证极小 delta；计入预算上限的统计量是 E[min(T,B)] 的开发估计，不是 E[T]。",'',
        '|策略|完成 / 全部|删失|错误认证 / 全部|规划秒|GLR秒|',
        '|---|---:|---:|---:|---:|---:|']
    for policy in POLICIES:
        rr=[r for r in summary if r['policy']==policy];n=sum(r['n'] for r in rr)
        lines.append(f"|{policy}|{sum(r['completed'] for r in rr)}/{n}|{sum(r['censored'] for r in rr)}|{sum(r['wrong_certificates'] for r in rr)}/{n}|{sum(r['mean_planner_seconds']*r['n'] for r in rr):.2f}|{sum(r['mean_glr_seconds']*r['n'] for r in rr):.2f}|")
    lines+=['',
        '所有策略共用 GLR、离线校准、实例与停止检查时刻，每次任务/类型询问各计一次在线成本。Oracle 只获知格式类型，符号和可靠性仍未知。Direct 的永久格式承诺可能在此上限内不完成；没有删除这些路径。此阶段仅检验模型内收敛；历史失配负控制完整保留，没有包装为新的确认结果。','',
        '## 偏离理论系数时的诊断','',
        'Aligned 的强制探索比例、末次参数估计错误、网格步长、求解上下界、停止阈值/R、实际分配的总体最小 KL/R 已保留。总体 KL 只在运行后使用真实组类型计算，未回传采样器。它是分配信息量诊断，不能替代实际 GLR 或用来选择有利轨迹。','',
        '|分组|alpha|R|强制比例|符号错误|类型错误|阈值/R|总体最小KL/R|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for ref in refs:
        for R in [16,64,256,1024]:
            rr=[r for r in diagnostics if r['partition']==ref['partition'] and r['alpha']==ref['alpha'] and r['R']==R]
            values=[np.mean([r[k] for r in rr]) for k in ['forced_fraction','last_theta_errors','last_type_errors','final_beta_over_R','realized_population_min_KL_over_R']]
            lines.append(f"|{ref['partition']}|{ref['alpha']}|{R}|"+'|'.join(f'{v:.4f}' for v in values)+'|')
    lines+=['',
        '## 11项统计解释检查','',
        '1 Simpson：保留所有分组/alpha/R单元，不用汇总方向替代分层结果。2 Ecological：主张限于受控生成世界，不外推人类或自然 LLM。3 Berkson：未按结果筛选单元。4 Collider：未以完成状态筛选主成本。5 Base rate：报告所有轨迹、完成与错误全分母。6 Regression to mean：未按先前极端表现选本轮种子。7 Survivorship：删失保留，完成成本条件分布另标。8 Look elsewhere：完整预设曲线保留，不做挑点显著性主张。9 Forking paths：预先冻结配置、分析和种子承诺；本轮属于开发。10 Causal：机制结论只在明示随机通道模型内，不作真实用户因果外推。11 Reverse causality：动作先于反馈，公共/隐藏状态边界和成本由独立 evaluator 记录。11/11 已检查；小 n、删失和有限精度仍限制解释。','',
        '图与原始分析位于 artifacts/analysis/。完整性核对和既有轨迹重放另见 VALIDATION.json。所有早期实验保持原样，未开展 Phase3、模型调用或第二轮调参。']
    (root/'PILOT_REPORT.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
