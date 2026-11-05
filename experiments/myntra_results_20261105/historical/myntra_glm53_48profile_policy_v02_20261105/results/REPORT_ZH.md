# GLM-5.3 顾客家族复核与三模型同数据比较

## Material Passport

- 状态：`ANALYZED_COMPLETE`；48 个合成开发画像、35 个菜单、280 个案例。
- 请求 `glm-5.3`，流中返回标识：`glm-5.3`；千问/阿里云百炼北京接口。
- 模型标识是服务端报告，不是独立权重核验。逐字复用原顾客提示；推荐方是冻结 Python 策略。
- 计划 288 个唯一字段请求，实际尝试 288，有效回答 272，精确符合画像 271；重试 0。
- 传输/协议失败 5；完整 SSE 响应 283。全部 280 案例均进入每个方法与预算分母。
- 首轮 6 次尝试（1 有效、5 传输失败）全部保留；仅对未尝试字段续跑 282 次。续跑直连同一千问端点、并发 4、每线程连接复用，重试 0。
- 这是失败后调整的传输路径，不声称原先冻结的代理传输已经干净完成。原 5 次失败不补做，主结果保留其影响。

## GLM 下的全部预算

| 预算 | 固定顺序 | Profile IG | Decision-Set IG | Decision Value | DV − DSIG，百分点（95% 区间） |
|---:|---:|---:|---:|---:|---:|
| 0 | 152/280 (54.3%) | 152/280 (54.3%) | 152/280 (54.3%) | 152/280 (54.3%) | +0.0 [+0.0, +0.0] |
| 1 | 152/280 (54.3%) | 154/280 (55.0%) | 154/280 (55.0%) | 154/280 (55.0%) | +0.0 [+0.0, +0.0] |
| 2 | 150/280 (53.6%) | 171/280 (61.1%) | 155/280 (55.4%) | 162/280 (57.9%) | +2.5 [-0.4, +5.7] |
| 3 | 150/280 (53.6%) | 158/280 (56.4%) | 172/280 (61.4%) | 204/280 (72.9%) | +11.4 [+7.5, +15.4] |
| 4 | 177/280 (63.2%) | 176/280 (62.9%) | 200/280 (71.4%) | 238/280 (85.0%) | +13.6 [+7.5, +19.6] |
| 5 | 191/280 (68.2%) | 182/280 (65.0%) | 233/280 (83.2%) | 255/280 (91.1%) | +7.9 [+3.9, +11.8] |
| 6 | 258/280 (92.1%) | 258/280 (92.1%) | 264/280 (94.3%) | 267/280 (95.4%) | +1.1 [+0.0, +3.2] |

## 三个顾客部署的全分母比较

| 预算 | 方法 | Luna | DeepSeek V4.1 Flash | GLM-5.3 |
|---:|---|---:|---:|---:|
| 3 | fixed_order | 150/280 (53.6%) | 150/280 (53.6%) | 150/280 (53.6%) |
| 3 | profile_ig | 158/280 (56.4%) | 150/280 (53.6%) | 158/280 (56.4%) |
| 3 | decision_set_ig | 167/280 (59.6%) | 166/280 (59.3%) | 172/280 (61.4%) |
| 3 | decision_value | 202/280 (72.1%) | 202/280 (72.1%) | 204/280 (72.9%) |
| 4 | fixed_order | 181/280 (64.6%) | 180/280 (64.3%) | 177/280 (63.2%) |
| 4 | profile_ig | 180/280 (64.3%) | 172/280 (61.4%) | 176/280 (62.9%) |
| 4 | decision_set_ig | 205/280 (73.2%) | 202/280 (72.1%) | 200/280 (71.4%) |
| 4 | decision_value | 244/280 (87.1%) | 239/280 (85.4%) | 238/280 (85.0%) |
| 5 | fixed_order | 212/280 (75.7%) | 198/280 (70.7%) | 191/280 (68.2%) |
| 5 | profile_ig | 208/280 (74.3%) | 197/280 (70.4%) | 182/280 (65.0%) |
| 5 | decision_set_ig | 246/280 (87.9%) | 243/280 (86.8%) | 233/280 (83.2%) |
| 5 | decision_value | 265/280 (94.6%) | 259/280 (92.5%) | 255/280 (91.1%) |

## 回答完整性与画像忠实度

| 顾客部署 | 字段计划 | 有效字段 | 精确符合画像 | 完整有效画像数 |
|---|---:|---:|---:|---:|
| glm | 288 | 272 | 271 | 40/48 |
| luna | 288 | 287 | 287 | 47/48 |
| deepseek | 288 | 278 | 278 | 46/48 |

DeepSeek 的 10 次 TLS 失败保留在全分母比较中，涉及 22 个案例；原实验在失败后改用串行连接复用，仅继续未尝试字段。这里不重跑或补齐该历史模型。Luna 原回答库含一个无效 pattern 回答。

| 与 GLM 比较 | 两边均有效的字段 | 解析值相同 |
|---|---:|---:|
| luna | 271 | 271 |
| deepseek | 262 | 261 |

## 三模型共同完整有效的补充子集

交集为 37 个画像、196 个案例。该子集排除了任何模型回答不完整/无效的画像，属于预先规定的次要描述；不能替代 280 案例主结果，也不应借此隐藏连接失败。

| 预算 | 方法 | 案例数 | Luna 正确 | DeepSeek 正确 | GLM 正确 |
|---:|---|---:|---:|---:|---:|
| 3 | fixed_order | 196 | 95 | 95 | 95 |
| 3 | profile_ig | 196 | 107 | 107 | 107 |
| 3 | decision_set_ig | 196 | 121 | 121 | 121 |
| 3 | decision_value | 196 | 145 | 145 | 145 |
| 4 | fixed_order | 196 | 126 | 126 | 126 |
| 4 | profile_ig | 196 | 124 | 124 | 124 |
| 4 | decision_set_ig | 196 | 144 | 144 | 144 |
| 4 | decision_value | 196 | 170 | 170 | 170 |
| 5 | fixed_order | 196 | 141 | 141 | 141 |
| 5 | profile_ig | 196 | 138 | 138 | 138 |
| 5 | decision_set_ig | 196 | 173 | 173 | 173 |
| 5 | decision_value | 196 | 185 | 185 | 185 |

## GLM 字段质量与失败

| 字段 | 计划 | 尝试 | 有效 | 精确符合画像 |
|---|---:|---:|---:|---:|
| neckline | 48 | 48 | 45 | 45 |
| sleeve_length | 48 | 48 | 45 | 45 |
| fabric | 48 | 48 | 43 | 43 |
| wash_care | 48 | 48 | 45 | 45 |
| pattern | 48 | 48 | 47 | 46 |
| purchase_threshold | 48 | 48 | 47 | 47 |

无效/失败项：`[{"error_class":"ReadTimeout","job_id":"A-P00__r1__neckline","parse_error":null},{"error_class":"SSLError","job_id":"A-P00__r1__pattern","parse_error":null},{"error_class":"SSLError","job_id":"A-P00__r1__purchase_threshold","parse_error":null},{"error_class":"ReadTimeout","job_id":"A-P00__r1__sleeve_length","parse_error":null},{"error_class":"ProxyError","job_id":"A-P00__r1__wash_care","parse_error":null},{"error_class":"invalid_answer","job_id":"A-P16__r1__fabric","parse_error":"JSONDecodeError: Extra data: line 1 column 160 (char 159)"},{"error_class":"invalid_answer","job_id":"A-P16__r1__neckline","parse_error":"ValueError: score_domain"},{"error_class":"invalid_answer","job_id":"A-P16__r1__wash_care","parse_error":"JSONDecodeError: Extra data: line 1 column 141 (char 140)"},{"error_class":"invalid_answer","job_id":"B-P09__r1__fabric","parse_error":"JSONDecodeError: Expecting ',' delimiter: line 1 column 220 (char 219)"},{"error_class":"invalid_answer","job_id":"B-P09__r1__sleeve_length","parse_error":"ValueError: score_keys"},{"error_class":"invalid_answer","job_id":"B-P11__r1__neckline","parse_error":"ValueError: score_domain"},{"error_class":"invalid_answer","job_id":"B-P13__r1__fabric","parse_error":"JSONDecodeError: Extra data: line 1 column 119 (char 118)"},{"error_class":"invalid_answer","job_id":"B-P20__r1__fabric","parse_error":"JSONDecodeError: Extra data: line 1 column 96 (char 95)"},{"error_class":"invalid_answer","job_id":"B-P21__r1__fabric","parse_error":"JSONDecodeError: Extra data: line 1 column 96 (char 95)"},{"error_class":"invalid_answer","job_id":"B-P23__r1__sleeve_length","parse_error":"ValueError: score_domain"},{"error_class":"invalid_answer","job_id":"B-P23__r1__wash_care","parse_error":"JSONDecodeError: Extra data: line 1 column 141 (char 140)"}]`。

## 约束、查询成本与 regret

| 预算 | 方法 | 中断路径 | 硬约束违规 | 平均问题数 | 平均归一化 regret |
|---:|---|---:|---:|---:|---:|
| 3 | fixed_order | 47/280 | 24 | 2.74 | 0.4071 |
| 3 | profile_ig | 32/280 | 1 | 2.83 | 0.3214 |
| 3 | decision_set_ig | 34/280 | 1 | 2.81 | 0.2821 |
| 3 | decision_value | 32/280 | 0 | 2.83 | 0.2357 |
| 4 | fixed_order | 47/280 | 0 | 3.58 | 0.2071 |
| 4 | profile_ig | 47/280 | 0 | 3.71 | 0.2607 |
| 4 | decision_set_ig | 40/280 | 0 | 3.69 | 0.1821 |
| 4 | decision_value | 36/280 | 0 | 3.71 | 0.1214 |
| 5 | fixed_order | 47/280 | 0 | 4.41 | 0.1607 |
| 5 | profile_ig | 47/280 | 0 | 4.55 | 0.1964 |
| 5 | decision_set_ig | 44/280 | 0 | 4.55 | 0.1107 |
| 5 | decision_value | 44/280 | 0 | 4.59 | 0.0750 |

接口返回 token 用量汇总：`{"completion_tokens":16870,"prompt_tokens":207127,"total_tokens":223997}`；未推测账单。

## 科研解释边界

三个家族名称代表三个指定的顾客模型部署，并非模型总体的随机样本。这里能够检验同一结构化画像问答接口下的方法迁移，不能据此宣称对广泛模型家族、自然多轮顾客、真人偏好或模型驱动推荐 Agent 都稳健。
画像给出了完整原始偏好分数，模型按被问字段返回。若回答高度重合，策略结果接近主要是相同输入下的确定性推论，并不证明顾客行为多样性。自然语言自由表达、跨轮偏好保持和最终购买行为没有在本轮评估。
这 48 个画像和 35 个菜单曾参与方法开发，因此仍是开发面板的第三部署复核，不是独立 held-out 确认。原 Luna BUY_TIED 行为筛查失败结论保持；本轮没有验证 GLM 的购买行为。
GLM 通过 SSE、DeepSeek 通过非流式 API、Luna 通过 Codex CLI。GLM 与 DeepSeek 显式对齐 temperature=1、top_p=1、high 推理及 8192 输出上限；GLM 默认 top_p=0.95 与 max 推理不等于本轮配置。Luna 的后台身份、外层系统与采样参数未能全部对齐，不能把差异因果归因于模型权重。
区间按 48 画像、12 pool/cohort 分层聚类 bootstrap 10,000 次，seed=202611041955；菜单随画像携带。它们是开发面板的描述性区间，不是人群显著性结论；三个预算和多个模型也不能作为独立样本相加。
确定性缓存统计：`{"eligible_profiles":39,"recomputed_cases":62,"reused_cases":218,"reused_trace_rows":6104,"rule":"complete effective answer bank equality; frozen identical inputs and policy"}`。缓存仅复用相同有效输入下的 Python 策略计算，所有 GLM 字段仍按计划实际请求；失败项不会由 Luna 回答填补。

## 复现材料

`FROZEN.json` 绑定所有提示、输入、原始参考结果及源码。原始续跑 SSE 见 `artifacts/run/responses/`，首轮原始流见 `artifacts/reference/initial_glm_run/responses/`；逐案轨迹和全部指标见 `results/PAIRED_POLICY_TRACES.jsonl` 与 `results/ANALYSIS.json`，三模型对照见 `results/THREE_MODEL_COMPARISON.json`。
执行 `python experiment.py verify` 校验冻结哈希；`python experiment.py analyze` 只离线重算，无 API 调用。不要重复执行 `run`。
