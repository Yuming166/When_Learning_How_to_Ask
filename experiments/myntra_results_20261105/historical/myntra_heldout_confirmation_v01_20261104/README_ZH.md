# 保留集确认实验 v0.1

本实验在 Myntra 原始 `validation_reserved` 与 `test_reserved` 商品上，比较已经冻结的四种 training-free 问询策略。它使用确定性程序模拟画像，不调用 Qwen/Luna，也不代表真人购物行为。

预算 0–6 全部报告，并同时对固定顺序、Profile IG、Decision-Set IG 比较。预算 5 保留为历史主比较点；是否“所有预算都不差”，只由每个 split 内覆盖 3 个基线 × 7 个预算的同时 95% 区间判断。不能用平均效果或挑选单个预算替代这个标准。

开发集未见的属性值在画像效用中按 0 处理。验证集包含品类内未见的 `scoop neck`、`keyhole neck`、`art silk`、`crepe`、`pure silk`；测试集包含 `modal` 和 `yoke design`。画像与先验仍只使用开发集属性词表，避免利用保留集结果或扩展偏好支持集。

先完成结构/双评估器一致性检查并冻结，然后验证集和测试集并发各跑一次（每个 split 4 个 worker）。任何保留集结果都不用于改方法。详见 [PROTOCOL.md](PROTOCOL.md)。
