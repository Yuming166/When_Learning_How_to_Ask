# 缓存和插值审计

## Material Passport

开发实现与成本审计；仅可观测输入。不存在从评测真值/私有种子到在线策略的输入通路。公开参数网格不是训练数据，也没有以闭环效果拟合网格或扩大密度。

## Key 与生命周期

精确 key 为 (实现版本, partition, p_hat.hex, q_hat.hex, alpha.hex, 已知 type_accuracy, eta.hex, tolerance.hex, max_iterations)。它缓存的是规范高/低格式系数 a,b,c，z_hat 在原展开器中映射到 A/B；无需将 z 或历史身份放进 key。版本与代码冻结同属一次进程生命周期，不声称跨版本持久缓存。类型查询不存在时有显式 None。缓存参数改变一个浮点单位会 miss，单元测试覆盖。

量化 key 仅将两条估计率替换为 round(p_hat/.025)、round(q_hat/.025)，保留其他契约。禁止 hidden theta、生成 p/q/z、答案、奖励、world/episode ID、private seed、未来观察或 teacher 标签作为 key。闭环每个世界新建空缓存；离线每轮在固定状态序列上重建缓存，首遍命中率单列，不能把人为重复状态命中当部署效果。

## 插值

56次原 Teacher 网格求解；预计算 CPU 3.819146s，初次构建三角剖分 0.000741s。网格见 DEVELOPMENT_PROTOCOL.md。对同一公共 partition/alpha/s/eta 的 (p_hat,q_hat) 用二维 Delaunay 单纯形内的重心权重插值**整个系数向量**。凸包外、结构不匹配或验收失败都调用原 Teacher。采用 [SciPy Delaunay transform](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html) 的重心映射，几何插值不构成信息约束保证。

## 验收与成本

所有近似候选先检查非负/有限并做保守径向修复，再在当前估计模型中求出每一个 (mask,h) 的连续最小值，同时用初始有效 cuts 加当前候选投影 cuts 求一个新的松弛 LP 下界 L。只有 min information>=1−1e−7 且 −5e−8<=(c^T x−L)/max(1,c^T x)<=max(5 epsilon,5e−8) 才返回。每条 cut 的系数和校准右端都在当前参数上重算。否则回退**冻结原始求解器**；guard、miss、查 key、重算和回退均计时。下界可能太松，因而拒绝本来接近最优的候选；这里偏保守，不能把拒绝率解释成插值方法族不可能有效。

离线第一遍：精确缓存0/23命中；量化缓存6/23命中但0验收；插值23/23覆盖但0验收。没有依据这些结果重调 bin 或网格后再挑最好结果。

闭环统计：

| 方案 | solver 调用 | 命中/覆盖 | 验收 | 回退 | guard CPU 秒 | fallback CPU 秒 |
| --- | --- | --- | --- | --- | --- | --- |
| ExactCache | 1703 | 0 | 0 | 0 | 0.000 | 0.000 |
| QuantizedCache | 1703 | 1425 | 339 | 1364 | 10.366 | 118.630 |
| Interpolation | 1703 | 1703 | 2 | 1701 | 11.588 | 125.341 |


精确缓存1703次调用全部miss并重新调用原solver；表中的0回退仅表示没有近似guard回退，不代表免除了原求解成本。量化缓存278次miss，加1086次guard拒绝，共1364次原solver回退。插值1703次覆盖中仅2次验收。

“命中”与“验收”不同，计数分母是实际 solver 调用（包含调用方必要的第二次精度尝试），不是查询数。fallback CPU 是总 solver 时间的子集，不能重复加。精确缓存命中返回同一问题的已验收结果，不将其误列为近似 guard 验收。

粗网格与严格缺口要求的组合可能不划算；更密网格、跨轨迹共享缓存、原生 LP 基复用均未测量，不能称为已被否定。未修改本轮门槛以换取更多缓存命中。
