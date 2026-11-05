# DeepSeek V4.1 Flash 与 Luna：同数据顾客字段问答复核

## Material Passport

- 状态：`ANALYZED_COMPLETE`；48 合成开发画像、35 菜单、280 案例；四种冻结 Python 策略。
- 请求模型 `deepseek-v4.1-flash`；服务返回模型标识：`deepseek-v4.1-flash`。
- 服务商为千问/阿里云百炼；不是 DeepSeek 官方直连。模型标识是接口报告，未独立核验权重。
- 逐字复用 Luna 的顾客提示；一条 user 消息、每字段独立新会话；不调用最终购买选择。
- 计划 288，唯一请求尝试 288，解析有效 278，字段精确符合画像 278；重试 0。
- 原始无效回答与中断路径保留，不剔除案例；每个策略与预算均为 280 个案例。

## DeepSeek 下的全部预算

| 预算 | 固定顺序 | Profile IG | Decision-Set IG | Decision Value | DV − DSIG（画像簇 95% 区间） |
|---:|---:|---:|---:|---:|---:|
| 0 | 152/280 (54.3%) | 152/280 (54.3%) | 152/280 (54.3%) | 152/280 (54.3%) | +0.0 pp [+0.0, +0.0] |
| 1 | 152/280 (54.3%) | 154/280 (55.0%) | 154/280 (55.0%) | 154/280 (55.0%) | +0.0 pp [+0.0, +0.0] |
| 2 | 150/280 (53.6%) | 169/280 (60.4%) | 153/280 (54.6%) | 161/280 (57.5%) | +2.9 pp [-0.4, +6.1] |
| 3 | 150/280 (53.6%) | 150/280 (53.6%) | 166/280 (59.3%) | 202/280 (72.1%) | +12.9 pp [+8.9, +16.8] |
| 4 | 180/280 (64.3%) | 172/280 (61.4%) | 202/280 (72.1%) | 239/280 (85.4%) | +13.2 pp [+7.5, +19.3] |
| 5 | 198/280 (70.7%) | 197/280 (70.4%) | 243/280 (86.8%) | 259/280 (92.5%) | +5.7 pp [+2.5, +8.6] |
| 6 | 273/280 (97.5%) | 274/280 (97.9%) | 274/280 (97.9%) | 274/280 (97.9%) | +0.0 pp [+0.0, +0.0] |

## 与 Luna 的配对比较

| 预算 | 策略 | Luna 正确数 | DeepSeek 正确数 | DeepSeek − Luna | 案例胜/平/负 |
|---:|---|---:|---:|---:|---:|
| 3 | fixed_order | 150/280 | 150/280 | +0.0 pp | 4/272/4 |
| 3 | profile_ig | 158/280 | 150/280 | -2.9 pp | 3/266/11 |
| 3 | decision_set_ig | 167/280 | 166/280 | -0.4 pp | 3/273/4 |
| 3 | decision_value | 202/280 | 202/280 | +0.0 pp | 1/278/1 |
| 4 | fixed_order | 181/280 | 180/280 | -0.4 pp | 4/271/5 |
| 4 | profile_ig | 180/280 | 172/280 | -2.9 pp | 3/266/11 |
| 4 | decision_set_ig | 205/280 | 202/280 | -1.1 pp | 4/269/7 |
| 4 | decision_value | 244/280 | 239/280 | -1.8 pp | 0/275/5 |
| 5 | fixed_order | 212/280 | 198/280 | -5.0 pp | 0/266/14 |
| 5 | profile_ig | 208/280 | 197/280 | -3.9 pp | 2/265/13 |
| 5 | decision_set_ig | 246/280 | 243/280 | -1.1 pp | 2/273/5 |
| 5 | decision_value | 265/280 | 259/280 | -2.1 pp | 0/274/6 |

## 字段回答质量

| 字段 | 计划 | 有效 | 精确符合画像 |
|---|---:|---:|---:|
| neckline | 48 | 47 | 47 |
| sleeve_length | 48 | 47 | 47 |
| fabric | 48 | 46 | 46 |
| wash_care | 48 | 46 | 46 |
| pattern | 48 | 46 | 46 |
| purchase_threshold | 48 | 46 | 46 |

## 失败、约束与成本

| 预算 | 策略 | 中断路径 | 硬约束违规 | 平均提问数 | 平均归一化 regret |
|---:|---|---:|---:|---:|---:|
| 3 | fixed_order | 22/280 | 18 | 2.92 | 0.4214 |
| 3 | profile_ig | 22/280 | 1 | 2.84 | 0.3286 |
| 3 | decision_set_ig | 22/280 | 1 | 2.84 | 0.2786 |
| 3 | decision_value | 22/280 | 0 | 2.84 | 0.2250 |
| 4 | fixed_order | 22/280 | 1 | 3.84 | 0.2071 |
| 4 | profile_ig | 22/280 | 0 | 3.76 | 0.2607 |
| 4 | decision_set_ig | 22/280 | 0 | 3.76 | 0.1679 |
| 4 | decision_value | 22/280 | 0 | 3.76 | 0.1143 |
| 5 | fixed_order | 22/280 | 1 | 4.76 | 0.1286 |
| 5 | profile_ig | 22/280 | 0 | 4.69 | 0.1429 |
| 5 | decision_set_ig | 22/280 | 0 | 4.69 | 0.0750 |
| 5 | decision_value | 22/280 | 0 | 4.69 | 0.0571 |

无效项：`[{"error_class":"URLError","job_id":"A-P02__r1__fabric","parse_error":null},{"error_class":"URLError","job_id":"A-P02__r1__pattern","parse_error":null},{"error_class":"URLError","job_id":"A-P02__r1__purchase_threshold","parse_error":null},{"error_class":"URLError","job_id":"A-P02__r1__wash_care","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__fabric","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__neckline","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__pattern","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__purchase_threshold","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__sleeve_length","parse_error":null},{"error_class":"URLError","job_id":"A-P03__r1__wash_care","parse_error":null}]`。
接口汇总 token usage：`{"completion_tokens":27530,"prompt_tokens":208322,"total_tokens":235852}`；未根据 token 推测账单。

## 预算 5 的目录池结果

| 池 | 商品类 | 案例 | DSIG 正确 | DV 正确 |
|---:|---|---:|---:|---:|
| 0 | Kurtas | 88 | 81 | 81 |
| 1 | Dresses | 40 | 31 | 36 |
| 2 | Kurtas | 120 | 101 | 113 |
| 3 | Kurtis | 8 | 8 | 7 |
| 4 | Tops | 16 | 14 | 14 |
| 5 | Tunics | 8 | 8 | 8 |

## 复现与解释边界

按原 12 个人群池/画像批次分层，对 48 个画像聚类 bootstrap 10,000 次，seed=202611041955；所有菜单随画像整体重采样。区间仅描述该开发面板，不是人群显著性检验。
原 Luna 的全部 28 个单元计数和 21 个配对差值/区间已在推理前精确复算通过。
确定性重放缓存统计：`{"eligible_profiles":45,"recomputed_cases":37,"reused_cases":243,"reused_trace_rows":6804,"rule":"complete effective answer bank equality; frozen identical inputs and policy"}`。只在整个六字段回答库等价且输入/代码完全相同时复用既有轨迹；有任意差异的画像全部案例重新计算。确定性缓存不减少原定的字段请求；实际尝试数与服务响应数见本补充。
DeepSeek 显式启用思考 high、temperature=1、top_p=1，max_tokens=8192；Luna 的 Codex 外层系统、解码参数和服务身份无法完全对齐。因此这里只改变已指定的顾客部署，不把差异因果归因于模型权重。
数据是已参与方法开发的合成画像与真实商品标签，没有真人偏好、点击或购买标签。结果属于第二个模型/API 部署下的结构化问答复核，不能称为独立确认、自然购物对话、真人推荐效果或广泛跨模型稳健性。
画像提供完整原始分数并要求逐字段返回；高一致性主要说明规则遵循。如果两模型回答近乎相同，策略分数接近是确定性推论，行为多样性证据仍有限。
原 Luna BUY_TIED 行为筛查未达门槛的负面结果保留。本轮没有替 DeepSeek 验证最终购买行为。

复现：`python experiment.py verify`（零调用）；`python experiment.py analyze`（仅离线重放与统计）。
输入与源码绑定见 `FROZEN.json`；原始响应见 `artifacts/run/responses/`；调用账本见 `artifacts/run/ATTEMPTS.jsonl`；逐案轨迹与汇总见 `results/`。不要重复运行 `run`。

## 连接中断与续跑披露（补充）


首轮 24 次唯一尝试得到 14 条有效回答和 10 次 TLS 连接失败，其余 264 个字段没有尝试。原首轮原始记录与冻结清单完整保留。
随后只对从未尝试的 264 个字段续跑：改用 requests.Session 连接复用、并发 1、请求间隔 0.5 秒；没有重复失败项或成功项。合计 288/288 次唯一尝试、重试 0，其中有效 278。
合并结果保留全部 10 次连接失败，涉及画像 A-P02, A-P03。它们没有取得服务回答，不能计为模型内容错误；对下游推荐的影响仍按原规则保留。上面的 280 案例主表包含这部分影响。
连接处理是在失败后调整的，不能声称整次运行按一个完全预注册的成功传输方案完成。恢复后的数据没有补做原失败响应。
DeepSeek 有 46/48 个画像拥有完整有效的六字段回答库；Luna 对应为 47/48。两模型共同完整有效的交集为 45 个画像、243 个案例。
逐字段比较：两模型都有效的 277 条字段回答中，277 条解析值完全相同。完整有效交集的结果是补充描述，不能取代包含失败的 280 案例主结果。

| 预算 | 策略 | 共同完整有效案例数 | Luna 正确 | DeepSeek 正确 |
|---:|---|---:|---:|---:|
| 3 | fixed_order | 243 | 121 | 121 |
| 3 | profile_ig | 243 | 128 | 128 |
| 3 | decision_set_ig | 243 | 143 | 143 |
| 3 | decision_value | 243 | 173 | 173 |
| 4 | fixed_order | 243 | 156 | 156 |
| 4 | profile_ig | 243 | 149 | 149 |
| 4 | decision_set_ig | 243 | 179 | 179 |
| 4 | decision_value | 243 | 210 | 210 |
| 5 | fixed_order | 243 | 181 | 181 |
| 5 | profile_ig | 243 | 179 | 179 |
| 5 | decision_set_ig | 243 | 218 | 218 |
| 5 | decision_value | 243 | 230 | 230 |

这次结果应作为第二个模型/API 部署在固定画像字段问答上的描述性复核。连接失败、回答高度重合及开发数据复用共同限制了跨模型稳健性主张；不能据此认为自然顾客行为已得到验证。
原首轮 14 条有效回答的原始 HTTP 响应位于 `artifacts/reference/initial_run/responses/`；续跑的原始响应位于 `artifacts/run/responses/`。TLS 失败只有连接异常记录，不能据请求尝试数推断服务端生成次数或账单。
完整离线复现顺序：先运行 `python experiment.py analyze`，再运行 `python finalize_report.py` 生成本披露与补充描述；两步均为零模型调用。仅重算第一步会生成继承的基础报告，尚未包含续跑披露。
本补充由只读审查发现报告披露缺口后添加；采集器、问题、评分、原始轨迹与主表计数未改变。补充脚本和输出哈希见 `REPORT_FINALIZATION_RECEIPT.json`。
