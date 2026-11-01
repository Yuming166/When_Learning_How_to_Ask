# W2a：可自动核验的受控页面构造

本语料包含 **24 个虚构档案、192 个二元事实、768 个构造来源 root、1,152 份 HTML**。这里的 1,152 是生成页面数，**模型调用为 0，新增真实网页请求为 0**。没有将 W1 的真实事实、未签核立场或 FactCheck 标签当成真值。

## 构造及输入边界

每档案包含 8 个虚构对象的 `permit_active` 属性。保存的 evaluator-only seed 与固定 SHA256 排名规则确定其中 4 个为真、4 个为假。另一独立命名的 hash 排名使每档案恰有 4 个 YES-first、4 个 NO-first 选项顺序。首次初始化随机生成 seed，随后保留该 seed 即可逐字节重建；seed、真值规则实现和生成器均是评估侧材料，不进入策略输入。

每事实分配 4 个构造 root。第一个 root 生成 3 个不同 URL/页面 ID 的拷贝；其余 3 个 root 各生成 1 页。拷贝的完整 typed statements 相同，页面 ID、URL 不同。root 的原始报告按 `r=3/4` 的受控保留/翻转规则生成，实际保留/翻转动作全部写入私有 edit ledger。本次 768 个 root 中 574 个保留真值、194 个翻转，未为了凑正负比例重新采样。

独立 root 的错误独立性是生成机制的假设；不同 hash 输入与不同 ID 只验证构造及追踪，不是统计独立性的实证。档案内 4/4 平衡引入事实间依赖，因此本语料不支持 `theta_j` 独立同分布的结论。父实验中的单事实概率枚举另行定义其理论先验，不从这组平衡 fixtures 估计参数或先验。

| 目录 | 消费者与内容 | 不包含或限制 |
|---|---|---|
| `corpus/selector_visible/` | 策略清单、虚构事实问题、选项顺序、声明的 root ID 和页面路径 | 不含 theta、源正确性、报告 V、语句、seed、语义答案或 edit ledger |
| `corpus/reader_visible/` | HTML 与等价 typed records，供读取器处理 | 包含网页自身报告，不能作为策略的免费预读取信息；不含真实 theta 或正确性字段 |
| `corpus/evaluator_only/` | seed、构造规则配置、真值、源报告、错误动作、标签、内容 hash | 仅评估侧读取；策略不得 import 生成器/评估器，也不得读取此目录 |

这是输入接口隔离，不声称它能抵御拥有整个工作区文件权限的对抗程序。父实验本轮的策略只读符号计数与观测；没有把页面或 gold 导入策略。公共的构造 root ID 可以供来源感知策略使用，但不暴露它的实际正确性。

## 五种页面语义

页面全部显示同一 `SIMULATED CONTROLLED FIXTURE` 标识，地址使用不可解析的 `.invalid` 模拟域名，没有联网获取步骤。每个语句记录 speaker、target、value、publisher adoption、relation、root 和 role，并使用封闭可解析语法输出同样的可见文本。

| 页面语义 | 数量 | 规则 |
|---|---:|---|
| ASSERT_SUPPORT | 228 | 出版方采纳目标值 1 |
| ASSERT_REFUTE | 234 | 出版方采纳目标值 0 |
| ATTRIBUTED_ONLY | 230 | 仅转述源报告，出版方未采纳 |
| MIXED | 229 | 采纳的源报告与相反的引述干扰语句共存 |
| NOT_ADDRESSED | 231 | 只陈述另一个 auxiliary 属性 |

ASSERT 标签是对目标命题的陈述方向，**不是网页正确性**。例如 ASSERT_SUPPORT 仍可能与隐藏真值相反。两种断言数量无需相等；真值和选项顺序已严格平衡，源错误按预设机制保留。

MIXED 中的反向干扰是同 root 的受控派生语句，关系明确为 `CONTROLLED_COUNTERSTATEMENT_OF_ROOT`，不是新增独立证据。NOT_ADDRESSED 不暴露该目标报告。ATTRIBUTED_ONLY、MIXED、NOT_ADDRESSED 的全页唯一 publisher binary stance 均为 null，不能强行转成错误答案。

因此，完整 1,152 页语料是**构造、语义和来源追踪检查**。父实验的纯二元 `theta → V → Y` 定律针对 root-report experiment，或语料中的单一断言子域；不声称五类页面全都服从同一个二元读取通道。

## 自动核验与限制

独立 evaluator 从 HTML DOM 与可见封闭语法重建语句，并核对二者一致性，再自行计算五类标签；它不直接回显 gold 标签。真值通过另一实现重新计算 hash 排名，源翻转也独立重算，并逐页核对 edit ledger。程序检查 192 个三拷贝组的语句 hash 相同、每事实其余 3 个 root ID 不同、每档案真值/选项顺序平衡，以及 selector 输入不含禁止字段。故意令可见文本与 DOM value 不一致时，解析器必须拒绝。

固定 seed 重建后，全部语料文件内容 hash 保持一致。`CORPUS_CHECKS.json` 保存检查结果及程序/协议/语料清单 hash。对 W1 与 W1.1 的只读守卫比较运行前后递归文件名、大小及 mtime 的摘要；没有将这两个目录的正文作为构造输入。该守卫的范围是元数据一致性，不夸大为独立安全审计。

这些检查说明机器生成内容满足指定接口和封闭语法；**不证明自然网页语义正确、不证明 Qwen 能读取、不估计真实回答可靠性，也不将 W1 历史候选升级为真实网页金标准**。本受控构造的真值由程序规则确定，不以人工签核为前提。

## 复现与样例

首次初始化已经完成，后续使用保留的 evaluator seed 重建：

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python3 generate_corpus.py
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python3 generate_corpus.py --check-only
```

只有新建独立语料时才使用 `--initialize`；删除 seed 会失去原构造的复现条件。不要向策略提供 evaluator-only 文件或生成器源码。

一页可读样例：[虚构 registry 页面](corpus/reader_visible/pages/page_00_2_2_0.html)。它展示的是模拟来源的陈述，不展示该陈述是否符合隐藏真值。对应完整 structured records 保存在 `corpus/reader_visible/records.jsonl`。
