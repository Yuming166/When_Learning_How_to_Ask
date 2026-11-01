"""Render required reports from the frozen comparison."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def tab(headers,rows):
 return '| '+' | '.join(map(str,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
def write(name,s):(ROOT/name).write_text(s.strip()+'\n')
def pc(x):return f'{100*x:.2f}%'
def pp(x):return f'{100*x:+.2f} pp'
def main():
 s=json.loads((ROOT/'RESULTS.json').read_text());v=json.loads((ROOT/'VALIDATION.json').read_text());ex=s['execution'];allb=s['summaries'];ss=allb['32'];la=ss['Lookahead-2'];kl=s['gate_checks']['gain_vs_KL'];one=s['gate_checks']['gain_vs_same_objective_one_step']
 short={'GO':'有条件GO：规划价值门槛通过，可以另行审议轻量RL pilot；本轮仍不训练。',
        'REVISE':'REVISE：尚未充分证明值得训练RL，保留接口与设计，不启动T2。',
        'NO-GO':'NO-GO：本轮不支持启动RL训练；保留T1a与更简单的策略。'}[s['decision']]
 res_table=tab(['策略','B16成功/96','B32成功/96','B64成功/96','B32类型均值','B32 CPU秒','B32 joint NLL','B32 joint Brier'],
  [[n,allb['16'][n]['successes'],x['successes'],allb['64'][n]['successes'],f"{x['type_mean']:.2f}",f"{x['trajectory_cpu']:.3f}",f"{x['joint_nll_mean']:.4f}",f"{x['joint_brier_mean']:.4f}"] for n,x in ss.items()])
 diff_table=tab(['预算','LA2对照','恢复率差','95%开发配对区间','赢/输/同'],
  [[c['budget'],c['reference'],pp(c['difference']),f"[{100*c['ci95'][0]:+.2f},{100*c['ci95'][1]:+.2f}] pp",f"{c['wins']}/{c['losses']}/{c['ties']}"] for c in s['paired_accuracy_differences']])
 cell_table=tab(['分组','p','alpha','n','KL成功','FreshIG成功','TaskOnly成功','Recovery1成功','LA2成功','KL天花板标记'],
 [[c['partition'],c['p'],c['alpha'],c['n'],c['success_counts']['AnalyticReuse'],c['success_counts']['Fresh-IG'],c['success_counts']['Task-Only'],c['success_counts']['Recovery-1'],c['success_counts']['Lookahead-2'],c['reference_ceiling']] for c in s['cells'] if c['budget']==32])
 cpu_table=tab(['策略','全预算CPU秒','B32 KL/target CPU','B32 controller CPU','其中预测KL CPU','B32终局belief CPU','B32 gate CPU','B32 CPU中位数/p90'],
 [[n,f"{sum(allb[b][n]['trajectory_cpu'] for b in ['16','32','64']):.3f}",f"{x['planner_cpu']:.3f}",f"{x['controller_cpu']:.3f}",f"{x['forecast_solver_cpu']:.3f}",f"{x['terminal_belief_cpu']:.3f}",f"{x['gate_cpu']:.3f}",f"{x['cpu_median']:.3f}/{x['cpu_p90']:.3f}"] for n,x in ss.items()])
 macro_table=tab(['策略','B32受控动作','KL标签','IG标签','TYPE标签','TASK标签','B32真实type总数'],
 [[n,x['controlled_actions'],x['macros'].get('KL',0),x['macros'].get('IG',0),x['macros'].get('TYPE',0),x['macros'].get('TASK',0),x['costs']['type']] for n,x in ss.items()])
 cert_table=tab(['预算','策略','固定预算完成','末端认证','未认证猜测','错证','数值未定'],
 [[B,n,x['fixed_budget_completed'],x['certified'],x['terminal_uncertified'],x['wrong_certified'],x['gate_undetermined']] for B,d in allb.items() for n,x in d.items()])
 panel=json.loads((ROOT/'QUADRATURE_SENSITIVITY.json').read_text());fullcost=sum(ex['costs_including_partial'].values())
 write('FINITE_BUDGET_RESULTS.md',f'''# T1b finite-budget development results

## Material Passport

完成一次预先冻结的无训练开发比较。96个新独立Exact世界、12单元各8；同世界三个预算×九臂，共2592条路径。主要预算B32，B16结构对照，B64辅助；不从结果选择预算或世界。无RL训练rollouts、PPO、Qwen、LoRA、模型调用、确认或基准源修改。**{short}**

## 完整恢复和后验质量

{res_table}

所有臂最终共同使用order32联合后验对完整theta向量的joint MAP decoder。NLL/Brier是父评测器终局对真实theta的事后评分，未返回在线控制器。不是用各策略自己的decoder混比。R16在离线前固定，alpha=M/R，alpha0/3对应每条参考流M0/48，和B不是同一归一化比例。

主要差异：LA2相对AnalyticReuse为 {pp(kl['difference'])}，开发区间[{100*kl['ci95'][0]:+.2f},{100*kl['ci95'][1]:+.2f}] pp；相对同目标Recovery1为 {pp(one['difference'])}，区间[{100*one['ci95'][0]:+.2f},{100*one['ci95'][1]:+.2f}] pp。一步对照将“换成完整向量恢复目标”与“多预测一步”分开，不能只凭胜过KL或熵IG推断长期价值。Fresh-IG在B32为{ss['Fresh-IG']['successes']}/96、高于本轮LA2的{la['successes']}/96；这是廉价策略的描述性信号，不是经过确认的策略优越性。Fresh-IG同时改变后验刷新和直接动作选择（冻结Info则跟踪延迟target），不能把两者差异全部归因于clock。

{diff_table}

区间来自12单元内配对世界bootstrap20,000次，seed22017。不同预算使用同一组世界，不能把2592路径或288个world-budget组合当独立样本。全部预算保留，但只有B32作主门槛；没有多候选事后择优。区间是开发性不确定性摘要，非确认结果或均匀非劣性证明。

## 所有主预算单元

{cell_table}

天花板按预定KL恢复率>=.95标记，不删除。B16无自由动作，9臂的计数与decoder在96/96世界完全相同，已由审计核对；这不是“RL与所有策略一样好”的可学习结果。B32的Fixed-KL-IG在t16首次自由行动时已越过B/2，因此退化为Fresh-IG；不把两份相同策略当两条独立科学证据。全部预算单元见RESULTS.json和PAIRED_OUTCOMES.json。

## 获取与计算成本

在线总计 {ex['costs_including_partial']['task']+ex['costs_including_partial']['type']:,}，任务 {ex['costs_including_partial']['task']:,}，type {ex['costs_including_partial']['type']:,}；按每臂每预算收取的offline {ex['costs_including_partial']['offline']:,}，总获取 {fullcost:,}。每一组同世界同预算各臂在线恰为B、offline恰为2M；因此本实验不可能证明在线/总查询数减少，改进若有只能表现为同成本恢复率更高。物理配对共用的独特校准总量为 {sum(c['offline_mean']*c['worlds'] for n,c in allb['32'].items() if n=='AnalyticReuse'):,.0f}，账单按使用策略重复计费另列。

{cpu_table}

controller包含当前belief重算、候选动作、二步矩、分支条件化及未来clock上的KL重算；forecast KL是controller的子集，不能重复相加。KL/target是原sqrt-clock上的主规划；terminal belief和gate独立列出。轨迹CPU还包含动作跟踪、RPC编解码、日志与其他开销。全运行墙钟 {ex['seconds']:.3f}s（上限1500s），父评测服务CPU {ex['evaluator_cpu_seconds']:.3f}s，未逐臂分摊。原始完整CPU/墙钟、各预算与p90在RESULTS.json。

Fresh-IG、Task-Only和固定残差日程的当前包装都保留KL虚拟骨架；不声称它们已删去所有无用计算或具有最快可实现延迟。冻结Fused-Info和D-RRC未被强加KL计算。后续若训练RL，必须面对移除无用规划的廉价heuristic，不能靠当前包装开销制造算力优势。

## 控制决策和非短视模型值

{macro_table}

Type-Then-Task使用预定组号顺序购买，不总对应最不确定组TYPE候选；主比较Recovery1和LA2始终具有相同四个候选规则。macro可指向同一个物理动作，重合时日志采用第一个canonical标签；因此TYPE标签不等于实际type购买总数，不能据宏标签单独做因果归因。

LA2在B32共 {la['two_step_decisions']} 个真正二步决策；其中 {la['model_gain_over_1e6']} 个对Recovery1首动作后的同一二步续策值有>1e−6的增益（{pc(la['model_gain_positive_fraction'])}），平均 {la['model_gain_mean']:.6g}、最大 {la['model_gain_max']:.6g}；有 {la['different_from_myopic']} 次改变首个物理动作。它们是同一策略访问状态上的描述性模型诊断，不是独立世界，不是实际终局恢复率增益，也不证明收益来自type购买。未做type禁用的匹配干预，组别差异只作描述。

## 固定预算猜测与可靠证书

{cert_table}

预算末未认证是本实验正常输出状态，不是被删掉的失败样本；全部固定预算episode均计分。没有在证书第一次通过时停止，所以不报告固定置信停止成本，也不将“终局猜对”冒充认证可靠输出。原终局certificate覆盖全部任务、type与两条calibration，候选来自共同decoder；通过才允许strict output。模型/算术条件仍是原审计的iid、已知s、Fraction/Decimal范围，未获得新的保证等级。

## 数值与记录审计

9项契约测试通过：一步/二步分支、Gram矩与独立嵌套Bayes枚举、冻结IG对照、精确Fraction小参考、forced账本、末步截断和白名单。初始两项fixture误以t8为自由轮，修正至t16后通过，初始日志保留；没有科学世界重跑。

全部{v['paths']}条终局cost/count/certificate记录和 {v['two_step_decisions_checked']} 次二步值非负诊断检查通过。预定24个终点的32/64积分敏感性：joint theta最大概率误差 {v['maximum_joint_mass_error_32_64']:.3g}，joint MAP一致 {v['sensitivity_joint_MAP_agrees']}/24。它是有限panel的数值证据，不是连续后验或所有二步策略的数值认证。原源文件和T1a冻结依赖哈希全部保留。
''')
 reason=[]
 if not (kl['difference']>=.03 and kl['ci95'][0]>0):reason.append('LA2相对KL的>=3pp且区间下界>0门槛未满足')
 if not (one['difference']>=.01 and one['ci95'][0]>0):reason.append('LA2相对同目标一步策略的>=1pp且区间下界>0门槛未满足')
 if not s['gate_checks']['not_below_other_cheap_baselines_by_point']:reason.append('LA2未在点估计上达到全部廉价对照')
 if la['model_gain_positive_fraction']<.05:reason.append('同树二步增益>1e-6的决策比例未达5%')
 reasontext='；'.join(reason) if reason else '预先指定的开发资源门槛全部通过，但没有执行RL训练或确认'
 write('FINAL_DECISION.md',f'''# T1b final research decision

## Material Passport

**{short}** 结论限定于本次预先固定的Exact d4、B16/32/64、两档率/三分组/两校准设置。研究完成后停止，无自动增样、三步搜索、PPO或确认。

可以引入RL的接口已经构建：小型策略在KL/IG/TYPE/TASK之间选择，优化有限预算终局完整恢复；它不需要重新训练Qwen模仿KL求解器。**接口可行与训练值得是不同判断。** 当前数值结果如下。

|问题|主预算B32的证据|判断|
|---|---|---|
|是否优于T1a|LA2 {la['successes']}/96 vs KL {ss['AnalyticReuse']['successes']}/96；差 {pp(kl['difference'])}，区间[{100*kl['ci95'][0]:+.2f},{100*kl['ci95'][1]:+.2f}] pp|开发门槛{'通过' if kl['difference']>=.03 and kl['ci95'][0]>0 else '未通过'}|
|是否证明第二步价值|LA2 {la['successes']}/96 vs Recovery1 {ss['Recovery-1']['successes']}/96；差 {pp(one['difference'])}，区间[{100*one['ci95'][0]:+.2f},{100*one['ci95'][1]:+.2f}] pp|同目标比较{'通过门槛' if one['difference']>=.01 and one['ci95'][0]>0 else '不足以通过门槛'}|
|是否减少查询/总获取|每臂固定B与2M|未减少；不是本实验的可变目标|
|是否降低计算|LA2完整CPU {la['trajectory_cpu']:.3f}s，KL {ss['AnalyticReuse']['trajectory_cpu']:.3f}s|如需摊销，必须先有恢复收益，不能只凭规划开销大就训练|
|是否提升认证可靠性|LA2预算末认证 {la['certified']}/96，错证 {la['wrong_certified']}|沿用原gate，有限预算猜测不具有其风险保证|

门槛审计：{reasontext}。

## 如何解释

T1a提供加速的参考KL分配；本轮使用统一joint-MAP decoder测试新决策目标。若简单Recovery1或Fresh-IG胜过渐近KL，只能说明有限预算目标/更新频率重要，不能将其全部归为长时域规划价值。二步树内更高的Bayesian成功概率，也未必提高固定生成率下的实际完整恢复率；prior/model失配、horizon2截断与候选集限制都可能影响结果。

{'当前建议保留T1a作为统计骨架，并允许另行冻结一个轻量残差RL pilot协议，重点验证能否保留规划收益同时降低树开销；本轮不自动执行。' if s['decision']=='GO' else '当前不启动残差Actor-Critic训练。保留无训练基线、RL-ready接口与条件设计，不能把本轮有限证据包装成已实现的Training贡献。Fresh-IG在B32和B64的较高恢复数是更值得先做廉价、预先冻结验证的描述性信号；本轮不追加验证，也不直接替换不可变T1a。若以后要研究更远期价值，应先提出新的预先固定问题与预算，不能继续在这96世界上筛选规则再称独立评价。'}

本结果不否定所有RL、所有更长horizon或其他任务；也没有完成新颖性审计。Generic RL实验设计和学习加在线lookahead已有文献，详见LOOKAHEAD_BASELINES.md。组共享/付费type的因果价值尚需匹配消融；当前决策记录只能描述购买行为。

## 可靠性和外推

原严格认证使用完整观察，不依赖RL预测正确；符合可预测选样与原模型时可延续原错误认证控制。残差覆盖tracker后，原O(sqrt(t))实际欠额界不能直接继承；所有固定浮点floor、联合后验近似与无限期证明缺口仍存在。不能宣称固定预算效果验证原Theorem1的渐近最优性，不能迁移认证到未验收的Mechanism/Natural。

T1a原始结果、源文件、旧LoRA/MLP负结果、保留确认协议均未覆盖。当前训练更新0、RL训练rollout0、Qwen/模型调用0、确认世界0。六项交付物完成；源哈希、原始公开轨迹与私有开发来源由FINAL_RECEIPT绑定。
''')
 write('README.md',f'''# T1b — Planning Value Audit before RL

**{short}** 96新开发世界、2592条固定预算路径，未训练RL。

- [预先冻结的协议](T1B_PLANNING_PROTOCOL.md)
- [信念POMDP接口](BELIEF_POMDP_INTERFACE.md)
- [前瞻与强基线](LOOKAHEAD_BASELINES.md)
- [有限预算结果](FINITE_BUDGET_RESULTS.md)
- [条件RL设计，未执行](RL_FEASIBILITY_DESIGN.md)
- [最终判断](FINAL_DECISION.md)

代码在t1b/，冻结T1a依赖在frozen_t1a/，只新增本隔离目录。额外的[宏动作接口](interfaces/README.md)提供prepare/act/finalize与重复动作mask，三项literal-stub测试通过；它未用于已冻结的科学比较，单独绑定INTERFACE_RECEIPT。RESULTS.json保留全部单元/预算；PAIRED_OUTCOMES.json保留逐世界结果；VALIDATION与FINAL_RECEIPT记录范围和hash。

已执行命令（不是再次执行许可）：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v`、`python -m t1b.preflight`、`python -m t1b.runner`。runner拒绝覆盖，预算固定，不自动重试。私有开发熵只保留本地忽略目录；精确复现同一世界需要该本地记录，新的entropy不等于复现。

分析与验证只读取已有结果：`python audit/analyze.py`、`python audit/validate.py`、`python audit/render.py`、`python audit/seal.py`。不得自动启动下一阶段。
''')
 print('rendered final reports')
if __name__=='__main__':main()
