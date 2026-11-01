"""Render the bounded audit from sealed outputs; no scientific execution."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(n):
    return json.loads((ROOT / n).read_text())


def table(headers, rows):
    return '\n\n' + '\n'.join(['|' + '|'.join(headers) + '|',
                                '|' + '|'.join(['---'] * len(headers)) + '|'] +
                               ['|' + '|'.join(map(str, r)) + '|' for r in rows]) + '\n\n'


def num(x, digits=3):
    return 'NA' if x is None else f'{x:.{digits}f}'


def pp(x):
    return 'NA' if x is None else f'{100*x:+.2f}pp'


def effect(d):
    if d['ci95'] is None:
        return 'NA'
    return f"{pp(d['mean'])} [{pp(d['ci95'][0])}, {pp(d['ci95'][1])}]"


def signal(d):
    if d['ci95'] is None:
        return '无完整配对'
    lo, hi = d['ci95']
    if lo > 0:
        return '开发区间全为正'
    if hi < 0:
        return '开发区间全为负'
    return '开发区间包含零'


def write(n, text):
    (ROOT / n).write_text(text.strip() + '\n')


def main():
    r = load('RESULTS.json')
    paired = load('PAIRED_OUTCOMES.json')
    v = load('VALIDATION.json')
    runtime = load('RUNTIME.json')
    features = load('BELIEF_FEATURES.json')
    strata = load('STRATIFIED_RESULTS.json')
    groups = load('GROUP_RESULTS.json')
    type_timing = load('TYPE_PURCHASE_TIMING.json')
    old = load('HISTORICAL_PAIRED_AUDIT.json')
    ex = load('artifacts/execution.json')
    arms = list(r['summaries']['32'])
    s = r['summaries']
    p32 = paired['32']
    passport = '''
## Evidence scope

本报告来自一个有界、独立的新development批次。没有确认世界、Qwen调用、神经训练、RL更新、PPO或Actor–Critic；没有改写T1a/T1b/T2历史结果、基准生成器或Natural。预先规定B32为主预算，B16/B64为结构/辅助预算。96个世界各重复所有预算和策略，不能把288个预算读数或3456条路径当作独立世界。

协议、配置、依赖、测试和输入快照在新开发entropy生成前已有哈希绑定；runner误用旧目录名，漏列六个本地t1c模块。原freeze未被补写，模块没有在运行后改动；事后hash和早于启动的mtime只能提供支持证据，不能补成预先的完整源码承诺。见[PROVENANCE_DEVIATION.json](PROVENANCE_DEVIATION.json)。本批仍是开发证据。
'''
    uncertainty = '''
区间为预定12个单元内、以世界为单位的20000次配对bootstrap百分位区间，seed42017。每单元仅8世界，是固定网格开发不确定性；未作多重比较校正，不宣称总体显著性、确认性发现或普遍优越性。各预算沿用同一批世界；指标和比较不能当独立证据相加。
'''
    scope = '''
所有策略始终购买至B，使用同一个order32数值积分联合后验和完整theta向量joint-MAP最终猜测。目标后验不是精确连续后验。末尾另行调用冻结Fraction/Decimal严格gate，覆盖全部task/type/calibration；其范围限于原iid、已知s及已审计算术/模型假设。固定预算恢复率不是认证正确率，不证明delta-correctness、固定置信成本或渐近最优。
'''

    # Factorial and mechanism report.
    text = '# T1c — Refresh versus objective ablation\n' + passport
    text += '''
## What is actually matched

T1a/T1b KL和冻结Fused-Info真实held-target cadence为t_next=t+ceil(sqrt(t+1))，B32更新点为8,11,15,19,24,29；不是32步。新Fresh因子从t8后每轮重算，包含forced轮。字面32步桥接臂仅在t8、40等更新，不能冒充旧T1a。

四臂共用观测、校准、类型准确率、后验实现、动作收费、forced时钟、累计欠额跟踪和最终decoder。KL使用AnalyticReuse，后验均值p/q及边际z-MAP用于KL规划；IG对当前联合theta预测积分，最大化I(theta;Y)/cost。故这是两种定义明确的规划准则比较，不能称对所有KL/IG目标的普遍判断。

原始IG的one-hot事实目标和KL的组内均匀目标具有不同约束。为此同时报告IG-Group两臂：选择平均IG最高的组格式并在组内均匀分配，或选择单独type；其target simplex与KL一致。它仍是一步信息准则对KL备择规划的比较。原2×2中目标差包括组内事实自适应，不能误归因为单纯信息目标。
'''
    names = {
        'refresh_KL': 'KL刷新：Fresh−Block', 'refresh_IG': 'IG刷新：Fresh−Block',
        'IG_minus_KL_block': 'Block下IG−KL', 'IG_minus_KL_fresh': 'Fresh下IG−KL',
        'refresh_main_effect': '刷新主效应', 'objective_main_effect': '准则主效应',
        'interaction': '交互：IG刷新差−KL刷新差'}
    for kind, title in [('operational', '原始可执行规则2×2'), ('group_uniform', '同组内均匀target空间2×2')]:
        text += '\n## ' + title + '\n'
        text += table(['效应', 'B16', '主B32', '辅助B64'],
                      [[title, *[effect(r['factorials'][str(B)][kind]['effects'][k]) for B in [16, 32, 64]]]
                       for k, title in names.items()])
    bridge_pairs = [
        ('IG-Fresh-Direct minus IG-Fresh', '同backend、同clock：直接执行−累计跟踪'),
        ('Fresh-IG-Lite minus IG-Fresh-Direct', '实用dense/tie/跳过forced计算版本−log直接执行'),
        ('IG-Fresh minus IG-Group-Fresh', 'Fresh下单事实IG−组均匀IG'),
        ('KL-Block minus KL-32', 'KL原sqrt−字面32步'),
        ('IG-Block minus IG-32', 'IG原sqrt−字面32步')]
    text += '\n## Bridges and execution\n'
    text += table(['比较', '主B32', '辅助B64'],
                  [[label, effect(paired['32'][k]), effect(paired['64'][k])] for k, label in bridge_pairs])
    text += '“Lite−log直接执行”同时改变浮点实现和tie、跳过forced轮更新，不能称纯执行效应。仅“log直接执行−log跟踪”保持目标实现和clock相同。\n'
    diagnostic = []
    for a in ['IG-Block', 'IG-Fresh', 'IG-32', 'IG-Fresh-Direct', 'Fresh-IG-Lite']:
        d = v['onehot_IG_action_vs_current_target'].get('32/' + a, {})
        age = v['posterior_age_on_free_actions'].get('32/' + a, {})
        diagnostic.append([a, d.get('action_differs_current_target_argmax', 0), d.get('free', 0), num(age.get('mean'))])
    text += table(['B32策略', '自由动作不同于当前one-hot目标', '自由动作总数', '使用后验平均年龄/观察数'], diagnostic)
    text += '''
累计跟踪器可能追赶旧目标，故每步更新目标不等于每步执行当前最大IG。该不一致诊断只用于one-hot臂；组均匀目标内多个事实都合法，不能用其单一argmax作同样判断。两个switching臂的日志posterior_online是基础KL候选阶段的时间，之后IG会重算后验；不据此字段判断控制器使用旧信念。

forced轮同样累积目标质量，因此后续欠额可能受forced阶段旧target影响。direct/residual臂继承记录的tracking上/下界字段只作记账，原tracker的理论欠额保证不会自动随新执行规则保留，未用它们认证停止。
'''
    text += '\n## Supported interpretation\n'
    for kind, title in [('operational', '原始规则'), ('group_uniform', '同target空间')]:
        eff = r['factorials']['32'][kind]['effects']
        text += f"\n{title}：Fresh下IG−KL为{effect(eff['IG_minus_KL_fresh'])}，{signal(eff['IG_minus_KL_fresh'])}；刷新主效应为{effect(eff['refresh_main_effect'])}；准则主效应为{effect(eff['objective_main_effect'])}。"
    text += '\n\n因子差、直接执行差和组内自适应差来自会随策略分歧的轨迹，不能相加成一个唯一的历史收益分解。完整逐世界配对见PAIRED_OUTCOMES.json，事件日志见原始terminal记录。\n' + uncertainty + scope
    text += '''
本轮主B32中，单独提高KL刷新仅68→69；共同tracker的fresh单事实IG为78，fresh组均匀IG为71，fresh KL为69。优势没有随KL每步刷新而消失，但同target空间下还没有支持纯IG准则优势的正区间。组内事实自适应是重要候选解释，单独对照的区间下界恰为零，不能称已确证的唯一机制。直接执行在B32为77而tracker为78，B64则91对87；“删跟踪器总会更好”也不成立。
'''
    write('REFRESH_VS_OBJECTIVE_ABLATION.md', text)

    # Paired outcome report.
    text = '# T1c — Paired finite-budget results\n' + passport
    text += '\n## Denominators and reliability\n'
    all_cert = sum(s[B][a]['strict_certificates'] for B in s for a in arms)
    all_wrong = sum(s[B][a]['wrong_certificates'] for B in s for a in arms)
    all_censored = sum(s[B][a]['strict_confidence_censored'] for B in s for a in arms)
    text += (f"\n计划{v['planned_paths']}条，完成终局记录{v['observed_paths']}条；未完成计划路径{v['uncompleted_planned_paths']}，"
             f"基础设施失败{v['recorded_infrastructure_failures']}，逐项检查通过={v['passed_observed_checks']}。"
             f"严格证书{all_cert}，错误证书{all_wrong}，预算末仍未认证{all_censored}。"
             "原字段censored表示严格停止未到达；它不表示固定预算路径没有执行完。认证拒绝属于正常未过阈值，数值/模型不支持另看status明细。\n")
    text += table(['预算', 'gate状态', '原因', '条数'],
                  [[z['budget'], z['status'], z['reason'], z['count']] for z in v['certificate_status']])
    text += scope
    text += '\n## Primary budget B32\n'
    text += table(['策略', '完整恢复/96', '恢复率', '平均task', '平均type', '平均总获取成本', 'joint NLL↓', 'joint Brier↓', 'p MAE↓', 'q MAE↓'],
                  [[a, f"{s['32'][a]['exact']}/{s['32'][a]['observed_worlds']}",
                    num(100 * s['32'][a]['recovery']['mean'], 2) + '%',
                    num(s['32'][a]['task_queries']['mean'], 2), num(s['32'][a]['type_queries']['mean'], 2),
                    num(s['32'][a]['total_acquisition']['mean'], 2), num(s['32'][a]['joint_nll']['mean']),
                    num(s['32'][a]['joint_brier']['mean']), num(s['32'][a]['p_mae']['mean']), num(s['32'][a]['q_mae']['mean'])]
                   for a in arms])
    text += '每条B32在线成本均为32；alpha0或3使离线成本分别为0或96（两条各M=48的已标注流），平衡网格平均总获取成本80。后验质量、p/q误差来自共同终局新估计；不把 held-target 时刻的旧估计与Fresh终局比较。\n'
    quality_rows = []
    for a in ['KL-Block', 'KL-Fresh', 'IG-Fresh', 'Budget-Switch', 'Belief-Gated']:
        z = p32['Fresh-IG-Lite minus ' + a]
        values = []
        for metric in ['joint_nll_difference', 'joint_brier_difference']:
            q = z[metric]
            values.append(num(q['mean']) + ' [' + ', '.join(num(x) for x in q['ci95']) + ']')
        quality_rows.append(['Lite−' + a, *values])
    text += table(['主B32后验质量配对差（负为Lite较好）', 'NLL差及区间', 'Brier差及区间'], quality_rows)
    text += '\n## Historical paired audit and independent new batch\n'
    old_rows = []
    for B in ['16', '32', '64']:
        d = old['budgets'][B]
        old_rows.append([B, d['fresh_only'], d['kl_only'], d['both_success'], d['both_failed'],
                         pp(d['difference']) + ' [' + ', '.join(pp(x) for x in d['paired_stratified_ci95']) + ']'])
    text += '\n历史T1b原96世界（事后审计，不能与新批混成确认）：\n'
    text += table(['B', 'Fresh独赢', 'KL独赢', '都成功', '都失败', 'Fresh−KL及开发区间'], old_rows)
    text += '旧B32的McNemar参考p=0.07835；它与分层bootstrap有不同条件，不能选择更有利的统计量宣布确认。T2的43/72与35/72使用24主世界×三个相关R、不同分布/clock/GLR中间读数，不能直接合并，见POLICY_SEMANTICS_AUDIT。\n'
    comparisons = []
    for B in ['16', '32', '64']:
        d = paired[B]['Fresh-IG-Lite minus KL-Block']
        comparisons.append([B, d['n'], d['candidate_only'], d['reference_only'], d['both_success'], d['both_failed'], effect(d)])
    text += '\n新96世界，实用Lite相对原KL-Block：\n'
    text += table(['B', '配对n', 'Lite独赢', 'KL独赢', '都成功', '都失败', 'Lite−KL及开发区间'], comparisons)
    keys = ['Fresh-IG-Lite minus KL-Fresh', 'IG-Fresh minus KL-Fresh',
            'IG-Group-Fresh minus KL-Fresh', 'IG-Fresh-Direct minus IG-Fresh',
            'Fresh-IG-Lite minus Budget-Switch', 'Fresh-IG-Lite minus Belief-Gated']
    text += table(['主B32配对', 'n', '候选独赢', '参考独赢', '都成功', '都失败', '差及开发区间'],
                  [[k, p32[k]['n'], p32[k]['candidate_only'], p32[k]['reference_only'],
                    p32[k]['both_success'], p32[k]['both_failed'], effect(p32[k])] for k in keys])
    text += '\n## Prespecified other budgets\n'
    text += table(['策略', 'B16完整恢复', 'B64完整恢复', 'B64平均type', 'B64 NLL↓', 'B64 Brier↓'],
                  [[a, f"{s['16'][a]['exact']}/{s['16'][a]['observed_worlds']}",
                    f"{s['64'][a]['exact']}/{s['64'][a]['observed_worlds']}", num(s['64'][a]['type_queries']['mean'], 2),
                    num(s['64'][a]['joint_nll']['mean']), num(s['64'][a]['joint_brier']['mean'])] for a in arms])
    text += 'B16全部是共同forced动作，不能检验自适应策略优劣。B32自由动作16次；B64自由动作40次。总成本均由固定B和该世界预购校准决定，恢复率更高不直接证明达到相同恢复率所需查询更少。\n'
    text += '\n## All B32 parameter cells\n'
    cells = [(name, z) for name, z in strata['32'].items() if name.startswith('cell=')]
    text += table(['单元 (partition,p,alpha)', 'n', *arms],
                  [[name[5:], z['planned_worlds'], *[str(z['arms'][a]['exact']) + '/' + str(z['arms'][a]['n']) for a in arms]] for name, z in cells])
    text += '\n全部预算的partition、p、alpha及12个单元均见STRATIFIED_RESULTS.json；按组大小统计的组内恢复/事实准确率、task/type次数见GROUP_RESULTS.json。组嵌套在世界内，未把组当独立重复。全部逐世界四格表和后验质量/CPU配对区间见PAIRED_OUTCOMES.json；没有按胜负筛选实例。\n'
    text += '\n## Group-size behavior at B32\n'
    group_rows = []
    for a in ['KL-Block', 'KL-Fresh', 'IG-Fresh', 'IG-Group-Fresh', 'Fresh-IG-Lite']:
        for size, z in groups['budgets']['32'][a].items():
            group_rows.append([a, size, f"{z['exact_groups']}/{z['groups']}", num(100*z['fact_accuracy'], 2) + '%',
                               num(z['mean_task_queries'], 2), num(z['mean_type_queries'], 2)])
    text += table(['策略', '组大小', '组内完整恢复/组数', '事实准确率', '每组平均task', '每组平均type'], group_rows)
    text += '\n## Type purchase timing at B32\n'
    text += table(['策略', '购买过type的世界/全部', '首次type前已完成观察数中位数（只在购买者中）', 't16–23的type总数', 't24–31的type总数'],
                  [[a, str(type_timing['budgets']['32'][a]['worlds_purchasing_type']) + '/' + str(type_timing['budgets']['32'][a]['worlds']),
                    num(type_timing['budgets']['32'][a]['first_type_time_conditional_on_purchase']['median'], 1),
                    type_timing['budgets']['32'][a]['type_counts_by_online_before_window'].get('16-23', 0),
                    type_timing['budgets']['32'][a]['type_counts_by_online_before_window'].get('24-31', 0)] for a in arms])
    text += '购买时序为描述性审计，没有据此新增调度规则或调阈值。全部预算及组索引计数见TYPE_PURCHASE_TIMING.json。\n'
    text += uncertainty
    write('PAIRED_FINITE_BUDGET_RESULTS.md', text)

    # Computational accounting.
    text = '# T1c — Computational cost\n' + passport
    text += '\n## Acquisition accounting\n'
    costs = ex['costs_including_partial']
    text += (f"\n本次共计task={costs['task']}、type={costs['type']}、offline={costs['offline']}，"
             f"在线{costs['task'] + costs['type']}，总获取成本{sum(costs.values())}。"
             "task/type每次均收费1；已标注校准每个观察收费1。在线硬上限135000，wall硬上限1800秒，没有自动重试或增加实例。\n")
    text += '\n## Primary B32: full trajectory and exclusive components\n'
    text += table(['策略', 'CPU合计/s', 'wall合计/s', '单路径CPU中位/ms', 'CPU p95/ms', '后验/s', 'target/s', 'controller/s', '终局后验/s', '公共probe/s', '严格gate/s', '其余/s'],
                  [[a, num(s['32'][a]['trajectory_cpu']['sum']), num(s['32'][a]['trajectory_wall']['sum']),
                    num(1000*s['32'][a]['trajectory_cpu']['median'], 2), num(1000*s['32'][a]['trajectory_cpu']['p95'], 2),
                    *[num(s['32'][a][m]['sum']) for m in ['posterior_cpu', 'target_cpu', 'controller_cpu_exclusive',
                                                         'terminal_belief_cpu', 'audit_probe_cpu', 'certification_cpu', 'remaining_trajectory_cpu']]] for a in arms])
    text += '''
posterior、target、controller三个新timer按排他方式记录；terminal estimator、公共t16 probe和gate单列。其余含动作/记账/RPC等；原planner_cpu_seconds与上述部件重叠，不能再相加。每步重算log-information实现的额外成本，不等于所有IG实现都昂贵；Lite采用dense概率矩实现并删除旧控制器中未使用的KL规划和macro计算。
'''
    cpu_rows = []
    for a in ['KL-Block', 'KL-Fresh', 'IG-Fresh-Direct', 'Budget-Switch', 'Belief-Gated']:
        d = p32['Fresh-IG-Lite minus ' + a]
        z = d.get('cpu_reference_over_candidate', {})
        cpu_rows.append([a + ' / Lite', num(z.get('ratio_of_sums')),
                         'NA' if 'ci95' not in z else '[' + ', '.join(num(x) for x in z['ci95']) + ']',
                         effect(d)])
    text += table(['主B32 CPU比（大于1表示Lite更快）', '配对总CPU比', '开发区间', 'Lite恢复率差'], cpu_rows)
    text += '\n## Whole bounded run\n'
    text += table(['策略', '全部预算路径', 'worker CPU/s', '路径wall合计/s', 'posterior/s', 'target/s', 'controller/s'],
                  [[a, z['paths'], num(z['cpu']), num(z['wall']), num(z['posterior_cpu']), num(z['target_cpu']), num(z['controller_cpu'])]
                   for a, z in runtime['all_budgets_by_arm'].items()])
    text += (f"\n实际运行wall={num(ex['seconds'])}秒；完成路径worker CPU={num(runtime['completed_trajectory_worker_cpu'])}秒；"
             f"公共kernel warmup CPU={num(runtime['kernel_warmup_total_cpu'])}秒；父评测器CPU={num(runtime['evaluator_cpu_seconds'])}秒。"
             f"这些已测CPU之和为{num(runtime['measured_cpu_lower_bound'])}秒。"
             "这不是完整机器CPU：子进程导入和部分解释器启动发生在worker timer前，分析/报告也不在科学run计时内。父进程CPU没有可信的逐臂归属，不能用worker比值声称完整机器的同等加速。策略次序在世界预算对之间循环，减少固定排序影响；单机负载和该次小实例仍限制时间结论。\n")
    text += 'RUNTIME.json保留所有部件和原始范围；计时是本轮实际测量，不外推GPU、语言任务、大d或未测试R。旧T1b与新Lite来自不同开发批次，不计算跨批“无损加速”比值。Lite与旧实现的六组literal工程流动作相同只是有限等价回归证据。\n'
    text += uncertainty
    write('COMPUTATIONAL_COST.md', text)

    # RL added-value assessment.
    text = '# T1c — Is reinforcement learning needed?\n' + passport
    text += '\n## Non-trained controls\n'
    text += '''
Budget-Switch按自由轮数前半KL、后半IG，B32为8+8；避免旧B/2墙钟规则在forced16后直接退化成全IG。Belief-Gated使用当前合法后验：剩余自由轮<=8或KL候选IG/maxIG<.75时选IG（maxIG>1e-14），其余KL。两者固定于新seed之前，没有用隐藏真值、终局评分或事后最优规则选动作。
'''
    text += table(['策略', 'B32恢复/96', 'B32 CPU/s', '相对KL-Block差', 'Lite减该策略', 'B64恢复/96'],
                  [[a, f"{s['32'][a]['exact']}/{s['32'][a]['observed_worlds']}", num(s['32'][a]['trajectory_cpu']['sum']),
                    effect(p32[a + ' minus KL-Block']), effect(p32['Fresh-IG-Lite minus ' + a]),
                    f"{s['64'][a]['exact']}/{s['64'][a]['observed_worlds']}"] for a in ['Budget-Switch', 'Belief-Gated']])
    text += table(['B32控制器', '自由KL执行次数', '自由IG执行次数'],
                  [[a, v['controller_rule_counts'].get('32/' + a, {}).get('KL', 0),
                    v['controller_rule_counts'].get('32/' + a, {}).get('IG', 0)] for a in ['Budget-Switch', 'Belief-Gated']])
    text += table(['B32控制器', '实际动作不同于当时KL提案的次数', '自由动作总数'],
                  [[a, v['controller_physical_overrides'].get('32/' + a, {}).get('differs_from_current_KL_proposal', 0),
                    v['controller_physical_overrides'].get('32/' + a, {}).get('free', 0)] for a in ['Budget-Switch', 'Belief-Gated']])
    text += '控制器标记选IG时仍可能与KL提案选同一个动作；实际override统计只对当时同一状态下的KL提案，不能当完整KL反事实轨迹。\n'
    text += '\n## Observable predecision features\n'
    text += '''
所有策略在t16首次自由动作前，使用同一批原始观察计算共同probe；逐世界逐臂/预算一致性已经验证。预定bins为theta熵占比>=.5、组类型熵占比>=.5、估计p−q>=.15、alpha0/3。不按最终轨迹胜负重划bin，不训练回归器或搜索阈值。

表中每行报告同一bin内配对恢复差；这是事后检验关联，不能当作一个已部署的“先看真值再切换”策略。不同特征bins重叠，不能相加。所有空bin也保留。熵bin可能与alpha和分组结构关联，未控制所有此类混杂，不宣称特征的因果异质性或一个已验证的泛化预测器。
'''
    feat_rows = []
    for name, bins in features['bins'].items():
        for side, z in bins.items():
            feat_rows.append([name + '/' + side, z['worlds'],
                              effect(z['budgets']['32']['Lite_minus_KL_Block']),
                              effect(z['budgets']['64']['Lite_minus_KL_Block']),
                              effect(z['budgets']['32']['IG_Fresh_minus_KL_Fresh']),
                              effect(z['budgets']['64']['IG_Fresh_minus_KL_Fresh'])])
    text += table(['共同t16 bin', 'n', 'B32 Lite−KL', 'B64 Lite−KL', 'B32 tracked IG−fresh KL', 'B64 tracked IG−fresh KL'], feat_rows)
    text += '同target空间的IG-Group配对区间、特征取值摘要及每个新世界的合法probe见BELIEF_FEATURES.json；按分组/p/alpha的全部表现见STRATIFIED_RESULTS.json。未声称已经构建可泛化的预测器。\n'
    gate = r['rl_gate']
    text += '\n## Resource gate and decision\n'
    text += (f"\n预定type-high/low每bin至少24世界：{gate['type_bin_minimum_24_each']}。"
             "进一步要求B32和B64均出现相反方向、幅度至少3pp、区间排除零的KL/IG优势，且简单控制器尚未覆盖收益。\n")
    text += table(['比较', 'B32相反且区间排零', 'B64相反且区间排零', '两预算均满足'],
                  [[k, z['per_budget']['32'], z['per_budget']['64'], z['both_budgets']]
                   for k, z in gate['opposite_sign_evidence'].items()])
    text += (f"\nRL结论：**{r['rl_added_value']}**。"
             "“超过两个简单控制”的区间检查只是保守的附加描述性条件，并非预先声明的必要统计检验；不以它替代预定type-bin条件。"
             "在未建立稳定、可观测且未被廉价规则覆盖的剩余收益时，不设计带执行授权的新RL pilot，不启动训练。\n")
    bg_pair = p32['Fresh-IG-Lite minus Belief-Gated']
    text += (f"\n本批type熵预定low bin为{features['bins']['type_entropy_half']['low']['worlds']}世界，"
             f"high bin为{features['bins']['type_entropy_half']['high']['worlds']}世界，无法检验预定的双区间异质性条件；"
             "不能在看到结果后另调type阈值补足样本。B32中Belief-Gated与Lite逐世界恢复成败完全一致，"
             f"但动作序列完全相同仅{bg_pair['identical_primitive_action_history_worlds']}/{bg_pair['n']}；"
             "它们不是被误接成同一个策略。Belief-Gated CPU更多，未显示额外恢复收益。"
             "其余预定bins也没有建立在B32/B64都稳定出现、区间排零的相反KL/IG优势，故当前缺乏训练切换器的可用证据。\n")
    text += '''
本批比较的是无训练策略。RL可能在更长预算、更大d或其他分布有价值仍是未检验假设；不能将“RL额外价值未建立”写成对所有RL的否定。保留既有残差动作接口即可，没必要为了论文加入模型训练。若未来另行批准研究，仍须保持认证停止独立于学习策略；当前结果不满足自动启动任何后续阶段的授权。
'''
    text += uncertainty + scope
    write('RL_ADDED_VALUE_ASSESSMENT.md', text)

    # Final standalone decision.
    lite, klb, klf = [s['32'][a] for a in ['Fresh-IG-Lite', 'KL-Block', 'KL-Fresh']]
    d = p32['Fresh-IG-Lite minus KL-Block']
    df = p32['Fresh-IG-Lite minus KL-Fresh']
    text = '# T1c — Final research decision\n'
    text += (f"\n**Fresh-IG实用候选：{r['fresh_candidate_preregistered_gate']}（预注册开发门槛）；RL训练："
             f"{r['rl_added_value']}。本轮已经停止，不自动追加确认、RL设计实验或训练。**\n")
    text += passport
    text += '\n## Primary result\n'
    text += (f"\nB32新96世界：Lite完整恢复{lite['exact']}/{lite['observed_worlds']}，"
             f"原KL-Block {klb['exact']}/{klb['observed_worlds']}，KL-Fresh {klf['exact']}/{klf['observed_worlds']}。"
             f"Lite−KL-Block={effect(d)}；Lite−KL-Fresh={effect(df)}。"
             f"旧T1b的+9.375pp仅为历史开发信号，本批独立结果完整保留，不能择优合并。\n")
    text += table(['预定Fresh候选门槛', '实际'],
                  [['相对KL-Block点差>=3pp且区间下界>0', effect(d)],
                   ['相对KL-Fresh点差>=0且区间下界>=0', effect(df)],
                   ['全部预算完成、无非法路径', r['fresh_gate_values']['all_paths_complete_valid']]])
    text += '\n## What has and has not been established\n'
    op = r['factorials']['32']['operational']['effects']
    gr = r['factorials']['32']['group_uniform']['effects']
    text += table(['问题', '本轮证据与边界'],
                  [['统计估计', '共同终局NLL/Brier/pq误差已报告；不同查询历史的后验质量不等于一个新估计器更好。'],
                   ['有限预算信息获取', f"Lite−原KL {effect(d)}；Lite−fresh KL {effect(df)}。仅此网格开发结果。"],
                   ['纯刷新解释', f"KL刷新 {effect(op['refresh_KL'])}；原IG刷新 {effect(op['refresh_IG'])}。不由策略名字推断。"],
                   ['信息准则解释', f"共同tracker的fresh IG−KL {effect(op['IG_minus_KL_fresh'])}；同target空间 {effect(gr['IG_minus_KL_fresh'])}。"],
                   ['在线/总获取成本', '每条固定B路径的总在线与预购校准成本相同；不能从恢复率直接声称节省到达同一可靠度的查询。'],
                   ['计算时间', f"B32 Lite CPU {num(lite['trajectory_cpu']['sum'])}s；KL-Block {num(klb['trajectory_cpu']['sum'])}s；KL-Fresh {num(klf['trajectory_cpu']['sum'])}s。这是worker轨迹计时，父CPU单列。"],
                   ['认证停止', f"全部{v['observed_paths']}条终局证书{all_cert}、错误证书{all_wrong}；{all_censored}条未认证。正常拒绝不能称数值失败或可靠停止成功。"],
                   ['学习必要性', '未训练任何策略；门槛逐项见RL_ADDED_VALUE_ASSESSMENT，不把事后oracle或特征关联当部署收益。']])
    text += '''
具体归因结论：原KL不是每32步更新；把KL改成每步后仍只有69/96，Fresh-IG优势并非仅由该clock假设解释。相同tracker下fresh单事实IG为78/96；把IG也约束到组内均匀target后降为71/96，对fresh KL的差区间跨零。因此支持有限预算下这一完整实用分配规则的开发价值，尚不支持“IG数学目标本身普遍更优”。

终局theta信念NLL/Brier改善，但p的平均绝对误差没有改善；并非全面的可靠性估计突破。Lite相对原sqrt KL的完整worker CPU比约1.44×，相对每步KL约4.01×；原KL对照上未达到2×完整路径加速。类型熵二分的低熵bin为0/96；廉价Belief-Gated在B32也为79/96、逐世界成败相同，且计算更贵。没有建立需由RL利用的稳定额外收益。
'''
    text += '''
## Research disposition

保留AnalyticReuse作为冻结理论驱动KL基线，保留Fresh-IG-Lite作为本轮被明确审计的有限预算候选；是否推进由上方门槛结论决定，不能自动解释为确认授权。原Fused-Info、tracked IG、直接IG及组均匀IG分别报告，不能互相替名。

对WWW材料，本轮可提供带完整分母和限制的有限预算开发附录/机制分析。它不支持加入“训练带来收益”的贡献，也不证明KL渐近理论错误。没有真实语言环境迁移证据；不把Exact上的数值结果写成Natural Agent有效性。

源码hash漏列是保留的审计缺陷，不能把这批称为完整源码预承诺确认。协议中的设计、阈值和预算没有随结果修改；不因该记录缺陷重抽有利世界。旧T1a/T1b全public receipts及只读T2输入已再次核验。

全部六项交付及机器可读配对/成本/验证凭据均在本目录。没有开启下一阶段。
'''
    text += uncertainty + scope
    write('FINAL_DECISION.md', text)

    write('README.md', f'''# T1c — Fresh-IG mechanism and fairness audit

分支training/t1c_fresh_ig_audit，base3186587。状态：{ex['status']}；Fresh候选门槛={r['fresh_candidate_preregistered_gate']}；RL={r['rl_added_value']}。独立新开发、无训练、无确认。

## Read first

- [FINAL_DECISION.md](FINAL_DECISION.md)
- [POLICY_SEMANTICS_AUDIT.md](POLICY_SEMANTICS_AUDIT.md)
- [REFRESH_VS_OBJECTIVE_ABLATION.md](REFRESH_VS_OBJECTIVE_ABLATION.md)
- [PAIRED_FINITE_BUDGET_RESULTS.md](PAIRED_FINITE_BUDGET_RESULTS.md)
- [COMPUTATIONAL_COST.md](COMPUTATIONAL_COST.md)
- [RL_ADDED_VALUE_ASSESSMENT.md](RL_ADDED_VALUE_ASSESSMENT.md)

## Reproducibility

T1C_PROTOCOL.md/config.json/freeze.json保存预定设计和真实原始清单；PROVENANCE_DEVIATION.json明确六个新模块未被预先hash绑定，勿把事后快照当预承诺。

INPUT_SNAPSHOT.json绑定只读历史源码/报告，frozen_t1b保留完整相同依赖，不改生成器或旧基线。tests/test_factorial.py及audit/工程日志覆盖cadence、动作、组均匀空间及Lite回归。无需GPU或模型。

RESULTS.json、PAIRED_OUTCOMES.json、STRATIFIED_RESULTS.json、GROUP_RESULTS.json、TYPE_PURCHASE_TIMING.json、BELIEF_FEATURES.json、RUNTIME.json、VALIDATION.json保留全部开发统计及分母。FINAL_RECEIPT.json hash绑定最终public文件与本地artifacts；原始结果和新私有reproduction在被git忽略的artifacts。没有读取旧seed或保留确认seed；新truth仅在动作完成后父端评分。

唯一科学运行已结束。runner拒绝覆盖已有artifacts；不要删除目录后自动重试。原始模块保持运行时字节不变。重算报告仅运行`python audit/analyze.py`、`python audit/render.py`，不导入训练/策略或生成新世界；之后receipt需要重新生成以反映字节变动。

本分支仅暂存本实验allow-list，不自动提交、推送或合并；无下一阶段授权。
''')
    print(json.dumps({'rendered_required_reports': 5, 'preserved_preexecution_semantics_report': True,
                      'fresh': r['fresh_candidate_preregistered_gate'], 'rl': r['rl_added_value']}))


if __name__ == '__main__':
    main()
