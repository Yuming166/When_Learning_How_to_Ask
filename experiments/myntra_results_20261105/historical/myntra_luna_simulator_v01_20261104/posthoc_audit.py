"""Posthoc correction of the repeated-base aggregation and CLI resource audit."""
import collections
import copy
import hashlib
import json
import pathlib

import luna_simulator as l


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def record_map(folder):
    return {p.stem: l.read(p) for p in pathlib.Path(folder).glob("*.json")}


def stable_summary(records, selected, variants):
    result = {}
    for case in selected:
        rows = [records.get(case + "__" + v, {}) for v in variants]
        canonical = []
        for row in rows:
            if not row.get("valid"):
                continue
            canonical.append(l.canonical(row["parsed"], l.transport.shown_options(
                next(m for m in l.rows(l.PUBLIC / "menus.jsonl") if m["menu_id"] == row["menu_id"]),
                row.get("view", "base"))))
        result[case] = {"planned_repeats": len(variants), "valid_repeats": len(canonical),
                        "all_valid_repeats_identical": len(canonical) == len(variants) and
                        len({json.dumps(x, sort_keys=True) for x in canonical}) == 1,
                        "actions": canonical}
    return result


def main():
    analysis_path = l.RESULTS / "ANALYSIS.json"
    report_path = l.RESULTS / "REPORT_ZH.md"
    original = l.read(analysis_path)
    prior_copy = l.RESULTS / "ANALYSIS_PRE_POSTHOC.json"
    if not prior_copy.exists():
        prior_copy.write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n")
    old_hash = digest(prior_copy) if prior_copy.exists() else digest(analysis_path)
    luna_records = record_map(l.RUN / "records")
    qwen_records = record_map(l.QWEN)
    selected = [c["case_id"] for c in l.rows(l.PRIVATE / "selected_cases.jsonl")]
    menus = {m["menu_id"]: m for m in l.rows(l.PUBLIC / "menus.jsonl")}

    # Correct base repeat aggregation: exactly three unmodified base calls;
    # reverse and alias conditions do not belong in this stability statistic.
    corrected_luna = {}
    for case in selected:
        rows = [luna_records.get(f"{case}__base_{i}", {}) for i in range(1, 4)]
        actions = []
        for row in rows:
            if row.get("valid"):
                actions.append(l.canonical(row["parsed"], l.transport.shown_options(menus[row["menu_id"]])))
        corrected_luna[case] = {"planned_repeats": 3, "valid_repeats": len(actions),
            "all_valid_repeats_identical": len(actions) == 3 and
                len({json.dumps(x, sort_keys=True) for x in actions}) == 1,
            "actions": actions}
    corrected_qwen = {}
    source_jobs = {j["job_id"]: j for j in l.rows(l.PRIVATE / "source_jobs.jsonl")}
    for case in selected:
        variants = ["base", "repeat_same", "repeat_new"]
        rows = [qwen_records.get(f"{case}__{v}", {}) for v in variants]
        actions = []
        for row in rows:
            if row.get("valid"):
                job = source_jobs[row["job_id"]]
                menu = menus[job["menu_id"]]
                actions.append(l.canonical(row["parsed"], l.transport.shown_options(menu, job.get("view", "base"))))
        corrected_qwen[case] = {"planned_repeats": 3, "valid_repeats": len(actions),
            "all_valid_repeats_identical": len(actions) == 3 and
                len({json.dumps(x, sort_keys=True) for x in actions}) == 1,
            "actions": actions}

    usage = {"invocations_with_usage": 0, "input_tokens": 0,
             "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
    for row in luna_records.values():
        for u in row.get("usage_events", []):
            usage["invocations_with_usage"] += 1
            for key in ["input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"]:
                usage[key] += int(u.get(key, 0))
    stderr_files = list((l.RUN / "events").glob("*.stderr.txt"))
    stderr_counts = collections.Counter()
    for path in stderr_files:
        body = path.read_text(errors="replace")
        stderr_counts["calls_with_nonempty_stderr"] += bool(body.strip())
        stderr_counts["model_list_refresh_timeout_lines"] += body.count("failed to refresh available models")
        stderr_counts["system_skill_install_race_lines"] += body.count("failed to install system skills")
        if body.strip() and "failed to refresh available models" not in body and "failed to install system skills" not in body:
            stderr_counts["other_nonempty_stderr_calls"] += 1

    corrected = copy.deepcopy(original)
    corrected["luna"]["base_repeat_stability"] = corrected_luna
    corrected["qwen_reference"]["base_repeat_stability"] = corrected_qwen
    corrected["posthoc_resource_audit"] = {
        "cli_usage": usage,
        "stderr": dict(stderr_counts),
        "model_identity": {"requested_alias": "gpt-6-luna", "reported_backend_model_strings": [],
                           "backend_identity_independently_attested": False},
        "scope": "resource and reporting aggregation only; no score, case, prompt, call, or gate changed"
    }
    corrected["posthoc_correction"] = {
        "change": "recompute repeat stability from base_1/base_2/base_3 only; reverse and alias conditions excluded",
        "original_analysis_sha256": old_hash,
        "scoring_or_model_outputs_changed": False
    }
    l.dump(analysis_path, corrected)
    luna_stable = sum(x["all_valid_repeats_identical"] for x in corrected_luna.values())
    qwen_stable = sum(x["all_valid_repeats_identical"] for x in corrected_qwen.values())
    report = report_path.read_text()
    old_sentence = "三次同文本独立调用中，0/8个画像的三次结果全部有效，其中0/8个画像的决策与商品都完全一致。"
    new_sentence = (f"三次同文本独立调用中，Luna有 {sum(x['valid_repeats']==3 for x in corrected_luna.values())}/8 个画像三次均有效，"
                    f"其中 {luna_stable}/8 个画像的决策与商品完全一致。Qwen历史参照对应为 {qwen_stable}/8。"
                    "该统计只使用原始顺序的三次重复；反序和代号变换不计入。")
    if old_sentence in report:
        report = report.replace(old_sentence, new_sentence)
    if "失败收据保存在 `artifacts/luna_run_failed_preflight_zero_calls/`" not in report:
        report = report.replace("## 完成情况", "## 完成情况\n\n首次预运行因提示日志目录未创建而提前失败，模型调用数为 0；失败收据保存在 `artifacts/luna_run_failed_preflight_zero_calls/`。修复仅涉及日志目录初始化，随后按修订冻结版完成下列72次调用。")
    preflight_note = "首次预运行因提示日志目录未创建而提前失败，模型调用数为 0；失败收据保存在 `artifacts/luna_run_failed_preflight_zero_calls/`。修复仅涉及日志目录初始化，随后按修订冻结版完成下列72次调用。"
    report = report.replace(preflight_note + "\n\n" + preflight_note, preflight_note)
    resource_sentence = (f"Codex CLI 使用量记录为输入 {usage['input_tokens']:,} tokens（其中缓存输入 {usage['cached_input_tokens']:,}），"
                         f"输出 {usage['output_tokens']:,} tokens；72 次中 {stderr_counts['calls_with_nonempty_stderr']} 次有非空标准错误日志，"
                         f"其中包含模型列表刷新超时 {stderr_counts['model_list_refresh_timeout_lines']} 行、系统技能初始化竞争 {stderr_counts['system_skill_install_race_lines']} 行。"
                         "这些日志没有造成请求失败或无效输出；服务端模型标识未通过事件流单独披露。")
    if resource_sentence not in report:
        report = report.replace("## 预设屏幕", "## 调用用量与日志\n\n" + resource_sentence + "\n\n## 预设屏幕")
    if "## 后处理更正" not in report:
        report = report.replace("## 解释边界", "## 后处理更正\n\n初次汇总脚本误把反序和代号变换两种呈现也计入三次基础重复，导致稳定性数字不正确。此处已按原始顺序的 `base_1/base_2/base_3` 重新汇总；原始分析保存在 `ANALYSIS_PRE_POSTHOC.json`，修正记录见 `POSTHOC_AUDIT.json`。动作评分、预设门槛、模型输出及请求数均未改变。\n\n## 解释边界")
    wrapper_note = "Luna 的固定画像和任务被序列化为单条用户消息交给 Codex CLI；Qwen 历史实验则通过独立的 system/user 消息发送。这个角色封装差异会影响行为，因此两者分数只作描述性参照。"
    if wrapper_note not in report:
        report = report.replace("Qwen与Luna的差异同时混有模型、服务协议、采样控制和Codex代理系统差异，不作因果归因。", wrapper_note + " Qwen与Luna的差异同时混有模型、服务协议、采样控制和Codex代理系统差异，不作因果归因。")
    report_path.write_text(report)
    receipt = {"status": "POSTHOC_REPORTING_CORRECTION", "original_analysis_sha256": old_hash,
               "corrected_analysis_sha256": digest(analysis_path),
               "posthoc_script_sha256": digest(l.BASE / "posthoc_audit.py"),
               "pre_correction_analysis_preserved": prior_copy.exists(),
               "luna_stable_profiles_out_of_8": luna_stable,
               "qwen_stable_profiles_out_of_8": qwen_stable,
               "usage": usage, "stderr": dict(stderr_counts),
               "prompt_envelope_difference": "Luna persona is serialized into one Codex CLI user message; Qwen reference used separate system/user roles",
               "scoring_or_outputs_changed": False}
    l.dump(l.RESULTS / "POSTHOC_AUDIT.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
