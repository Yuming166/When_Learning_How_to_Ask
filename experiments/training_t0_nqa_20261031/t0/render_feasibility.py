"""Render saved T0 profiling evidence, no execution of algorithms or training."""
import json
from .bootstrap import ROOT

def main():
    d=json.loads((ROOT/'artifacts/profile_summary.json').read_text());r=json.loads((ROOT/'artifacts/repair_profile_summary.json').read_text());m=d['mean_cpu'];total=m['teacher_total_cpu']
    lines=['|部件|平均 CPU / 更新|占完整规划|','|---|---:|---:|']
    for title,key in [('完整 Teacher 规划','teacher_total_cpu'),('联合后验','posterior_cpu'),('KL 求解流程','solver_cpu'),('其中 LP','linprog_cpu'),('其中解析 inner','analytic_inner_cpu'),('solver 其他','solver_residual_cpu'),('展开/记录/封装','expand_logging_and_wrapping_cpu')]:
        lines.append(f'|{title}|{m[key]*1000:.3f} ms|{m[key]/total*100:.2f}%|')
    text=f'''# T0 Training Feasibility Study

## Material Passport

2026-10-31，Asia/Shanghai。**完成的只有 T0 CPU 剖析、设计和未训练接口检查。** 新世界0、新任务/类型/校准观测0、训练更新0、Qwen/GPU/模型API调用0。协议设计不能被读成已达到训练目标。

输入快照绑定既有 Phase2e 代码与公开轨迹记录。每个原8个固定单元取最小世界索引，保留64/256/终点前缀，共 {d['states']} 状态、{d['existing_worlds']} 个历史世界；每状态三次封装计时，共 {d['timed_updates']} 更新。首轮每状态另跑未封装 Teacher 和既有 Fused-Info，后者只作同状态计算参考。所有输入都是公共可观测数据，没有读私有种子/答案文件。状态不是未来训练数据或独立新样本。

主剖析墙钟 {d['seconds']:.3f}s。封装只计时并在调用后恢复函数，不改磁盘源码或算法。第一轮 {d['first_repeat_states_compared_to_unwrapped']}/{d['first_repeat_states_compared_to_unwrapped']} 个不同状态的分配权重与未封装实现一致到1e-13；其余两次重复只计时，未重复声称做了该对照检查。

## 开销定位

'''+ '\n'.join(lines)+f'''

LP 和解析 inner 是 KL 流程内部的互斥计时子集，不能再与总 KL 行相加。统计按所选状态等权、每状态相同重复次数；不同世界若保留前缀数不同，不能把这些状态当成独立有效性样本。

未封装 Teacher 平均 {m['unwrapped_update_cpu']*1000:.3f}ms/更新，封装后 {total*1000:.3f}ms，存在计时开销和 warm-cache/调用顺序差异。同状态 Fused-Info 平均 {m['fused_info_update_cpu']*1000:.3f}ms；这是部件更新耗时，不是闭环查询成本或新的方法有效性实验。

结论：在这些状态上，优先摊销 **KL 分配** 有计算空间。仅把后验推断变成无限快，按此占比也最多约 {1/(1-m['posterior_cpu']/total):.3f}倍加速，不能满足2倍完整规划目标。反之，完全消除 solver 的理想上界不等于网络可实现的加速，更不保证查询效率。原 Phase2e 的各臂总 CPU 含不同轨迹/更新次数，不能直接用两臂总数相减推断 LP 或后验开销。

## 重复解析检查与廉价对照

主计时的 analytic inner 占比约 {m['analytic_inner_cpu']/total*100:.1f}%，明显高于 LP 的 {m['linprog_cpu']/total*100:.1f}%。另在同一8世界各取最后前缀做8次 cProfile；径向修复嵌套函数 minimum 每次被调用37次。其累积时间与全部 inner 累积时间之比落在 {min(r['radial_cumulative_over_inner_cumulative'])*100:.1f}%–{max(r['radial_cumulative_over_inner_cumulative'])*100:.1f}%；该比值含重叠计时与 profiler 开销，只用于定位重复调用，不与主计时相乘制造精确预算。

补充 cProfile 按名称筛选未取得 solver/LP 总计时项，首次控制台汇总曾因空分母失败；八次调用的数据已保存。只从保存数据修复可用字段汇总，没有重跑。空字段不解释为耗时为0；主计时不受此影响。详见 repair_profile_summary.json。这一局限保留在最终收据里。

因此，warm-start 若只减少 LP 调用，可能绕不开主要重复开销。缓存、备择 cuts 复用、已验收的向量化/分配不变实现优化，必须与 Student 公平竞争。本线不修改 Phase2e 算法；这些是 T1 前需要单列验收的基线，而非已经测得的优化结果。

## 缓存与模型选择

23个状态的首遍精确 tuple 有 {d['unique_tuple_first_pass_cache_hits']}/{d['first_pass_tuples']} 个重复 key。相同 key 的字典查找微测约 {d['identical_tuple_lookup_cpu']*1e9:.1f}ns，但没有包含构造 key、后验、miss、验证或全局缓存生命周期，不能称为部署加速或证明缓存无用。量化缓存和 warm-start 尚未实现或测量。

未训练 NQA 仅10660参数，8项契约测试通过，支持组/事实置换及不同事实数的接口。参数小不等于训练有效。当前没有 trained Student 的查询成本、信息缺口、推理延迟或2×/5%结果。

历史旧 T1 的四份报告已与其最终回执核对。旧教师为 forced-only Aligned，旧 MLP/LoRA 输入、更新时钟和目标编码与本提案不同；其已加载 MLP 约0.53ms、LoRA约5.60s的历史延迟只能作为该后端的记录，不能与此处 Teacher 时间拼成严格配对速度比。旧 pilot 的停止诊断未支持轻量或 LoRA 代替 Teacher，固定预算又出现天花板，正是本协议要求闭环和强廉价基线的原因。未重跑旧训练/评测。

## T0 判决

**方向建议：优先轻量的 KL 分配摊销；保留联合后验和独立认证。** 训练必要性尚未建立，先完成廉价对照验收；T1属于设计完成、未执行的下一阶段。Qwen T2当前延后，不是本轮必需组件。2倍速度/5%查询非劣性仅为探索性门槛。机制、自然语言、跨可靠率/事实数的科学效果均未由这次计时证明。

可复现产物：profile_rows.jsonl、profile_summary.json、repair_profile.json、repair_profile_summary.json、INPUT_SNAPSHOT.json、T0_PROFILE_PLAN.json、SECONDARY_PROFILE_PLAN.json，以及 tests/test_contract.py。未封装 Teacher 的23次调用、主69次封装调用、Fused-Info23次和补充 Teacher8次全部是存储状态上的 CPU 计算，不是新查询或训练更新。
'''
    (ROOT/'T0_FEASIBILITY_REPORT.md').write_text(text)
    print('Rendered T0 feasibility report from saved records')
if __name__=='__main__':main()
