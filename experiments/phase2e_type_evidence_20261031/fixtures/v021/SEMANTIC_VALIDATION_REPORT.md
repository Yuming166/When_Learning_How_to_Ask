# v0.2.1 离线语义验证结论

Material Passport：2026-10-31，Asia/Shanghai。完成设计、实现、离线fixture和分离审阅；新Qwen/API请求0、4B请求0、GPU模型加载0、训练0、完整Agent运行0、独立确认0。旧v0.2的5次35B调用属于历史证据，不计成本轮调用。

**总判断：REVISE，作为独立、自然、多样的benchmark仍不足；受控语义核心通过。**

|要求的独立判断|结论|证据范围与限制|
|---|---|---|
|1 Canonical truth validity|GO|96个离线目标Python/SQLite一致，类型与规则边界通过；仅限明示整数域与规则家族|
|2 Query-format semantic equivalence|GO|受控语法96组合／72文本获分离会话审阅；384默认查询完整绑定、互补选项与映射通过。自由NL不在结论内|
|3 Dataset diversity|REVISE|两个fictional域、六谓词、两个结构、有限人工词表、单政策家族；未测新模板或真实Web分布|
|4 Leakage and dependency integrity|GO|移除固定3/3，公开字段审计、全bit翻转元数据不变、显式8条AND边和共享政策因子；不证明任意统计捷径不存在|
|5 Readiness for a bounded Qwen generation pilot|GO，仅限16次受控选择技术pilot的离线准备|代码/语法/完整来源gate及冻结提案齐备；当前未授权执行、未启动。不是自由改写或回答pilot的GO|

## 实际验证

- 39项主测试通过，覆盖全部20个历史框架、不可变类型、实例scope、端点、缺失、单位/ID/negation/mapping扰动、完整来源拒绝、bit翻转不改公共数据、协议桥接与零调用计划。初次30项与后续修正记录均保留。
- 分离审阅：6谓词×16组合=96记录，72唯一文本；默认384查询对象。不是96份独立自然语言数据或384次模型回答。
- 分离探针：129个真值边界案例、96个B布尔赋值、12个缺字段拒绝、4个review gate案例，当前policy整数域两后端一致拒绝。
- 8个构建产物从私有fixture keys精确重放；公开数据不含keys。单次fixture标签分布保留：独立19/48真、机制21/48真。
- 独立世界每目标B两个variant正确选项位置恰好各一次；truth从不为平衡选项而更改。A保留真实标签偏斜。
- 当前自然生成验收来源仍为0；没有将程序生成的controlled query计为已成功Qwen生成。

## 分离审阅与修正证据

审阅来自 `/root/semantic_review`，同模型家族的另一个Codex会话，能看到共同任务背景及修复说明，但没有读取新fixture的私有记录、标签或keys。不是独立人类、跨家族、组织外评审或理论认证。

审阅指出并在freeze前修复：policy整数无上界导致Python/SQLite溢出域不同；空review集合的真空通过；履约短语 `can be dispatched` 的能力模态风险。另将source gate限定为同source的6个不同target。保留初始发现、内存重建旧validator的探针、修复与最终hash，不能反写成从未存在问题。

一个临时比较脚本曾直接比较JSON list与内存tuple而误报不同；正式replay使用canonical JSON。另一次replay正确指出提案schema尚未刷新。两者均记入 `audit/PREFREEZE_CORRECTIONS.json`；没有据此重抽truth或覆盖旧v0.2失败。

compiler与parser共享词表，parse-back有共同错误风险。分离自然语言审阅增加了有限的外部于实现者的判断，但不证明不受限自然语言等价。review hash gate只检查完整性，不认证“谁审过”。

## 构造、测量、未知与论文边界

由构造定义：canonical对象、ground scope、经典NOT、必需记录、共享证据、映射、分离随机域与显式依赖。

实际检查：上述代码测试、有限边界案例、框架分类、hash、依赖和数据公开边界。没有测量Qwen可回答性、格式差异、错误相关性、稳定组共享、无标签预测或停止可靠性。

WWW中可准确描述的是有语义grounding的有限语言编译器、可执行真值规范、旧失败回归与透明审计。当前不能宣称自然Qwen benchmark已验收、自由改写已解决、群组共享可靠性成立、方法优越、δ-correct、真实人类/真实Web代表性、held-out/OOD或跨模型家族泛化。

详细证据：`audit/independent_compiler_review.json`、`.md`、`audit/REVIEWER_CHECK_REPLAY.json`、`audit/TEST_EXECUTION_FINAL.log`、`audit/DATA_AUDIT.json`、`FINAL_RECEIPT.json`。
