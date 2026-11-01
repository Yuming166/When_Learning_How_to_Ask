"""Fresh-context sampled generations; append-only raw records; no label access."""
import argparse
import json
import os
import platform
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from design import ROOT, parse_answer, read_jsonl, sha, write_json


def hashes():
    paths = [ROOT / n for n in ["config.json", "design.py", "collect.py", "analyze.py", "reports/PROTOCOL.md"]]
    paths += sorted((ROOT / "data").glob("*/*.jsonl"))
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in paths}


class LocalSampler:
    def __init__(self, config):
        import torch
        import transformers
        from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration
        self.torch, self.config = torch, config
        assert os.environ.get("CUDA_VISIBLE_DEVICES") == config["physical_gpu"], "Explicit reserved physical GPU required"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        torch.set_num_threads(4)
        torch.set_float32_matmul_precision("highest")
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_path"], local_files_only=True)
        self.model = Qwen3_5ForConditionalGeneration.from_pretrained(
            config["model_path"], local_files_only=True, dtype=getattr(torch, config["dtype"]),
            attn_implementation="sdpa").to(config["device"]).eval()
        self.model.generation_config.pad_token_id = self.tokenizer.eos_token_id
        self.identity = {"backend": "transformers", "model_id": config["model"],
                         "model_class": type(self.model).__name__, "model_path": config["model_path"],
                         "parameter_count": self.model.num_parameters(),
                         "torch": torch.__version__, "transformers": transformers.__version__,
                         "python": platform.python_version(), "dtype": config["dtype"], "tf32": False,
                         "attention": "sdpa", "gpu": torch.cuda.get_device_name(0),
                         "physical_gpu": os.environ["CUDA_VISIBLE_DEVICES"],
                         "model_files": {p.name: sha(p.read_bytes()) for p in Path(config["model_path"]).iterdir()
                                         if p.is_file() and p.suffix in [".json", ".safetensors"]}}
        self.tokenizer_lengths = []

    def generate(self, row):
        torch, cfg = self.torch, self.config
        prompt = self.tokenizer.apply_chat_template(
            [{"role": "system", "content": row["system"]}, {"role": "user", "content": row["prompt"]}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(cfg["device"])
        torch.manual_seed(row["seed"])
        torch.cuda.manual_seed_all(row["seed"])
        with torch.inference_mode():
            output = self.model.generate(**inputs, do_sample=True, temperature=cfg["temperature"],
                                         top_p=cfg["top_p"], top_k=0, max_new_tokens=cfg["max_new_tokens"],
                                         use_cache=True, pad_token_id=self.tokenizer.eos_token_id)
        generated = output[0, inputs["input_ids"].shape[1]:].tolist()
        raw = self.tokenizer.decode(generated, skip_special_tokens=True)
        eos = self.model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        finished = bool(generated and generated[-1] in eos)
        return {"raw_output": raw, "generated_token_ids": generated, "finish_reason": "stop" if finished else "length",
                "input_tokens": inputs["input_ids"].shape[1], "output_tokens": len(generated),
                "model_returned": cfg["model"], "serialized_prompt_sha256": sha(prompt.encode())}


class APISampler:
    def __init__(self, config):
        self.config = config
        host = urllib.parse.urlsplit(config["base_url"]).hostname
        if host not in ["127.0.0.1", "localhost", "10.63.0.88", "10.63.0.82"]:
            raise RuntimeError("Only inspected local hosts are authorized")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        models = self.list_models()
        if config["model"] not in [m["id"] for m in models["data"]]:
            raise RuntimeError("Requested 4B model is not served; refuse substitution")
        self.identity = {"backend": "OpenAI-compatible API", "base_url": config["base_url"], "models": models}

    def call(self, endpoint, payload=None):
        headers = {"Content-Type": "application/json"}
        key = os.environ.get("QWEN_API_KEY")
        if key:
            headers["Authorization"] = "Bearer " + key
        req = urllib.request.Request(self.config["base_url"].rstrip("/") + endpoint,
                                     data=json.dumps(payload).encode() if payload else None, headers=headers)
        with self.opener.open(req, timeout=self.config["request_timeout_seconds"]) as response:
            return json.load(response)

    def list_models(self):
        return self.call("/models")

    def generate(self, row):
        cfg = self.config
        payload = {"model": cfg["model"], "messages": [{"role": "system", "content": row["system"]},
                   {"role": "user", "content": row["prompt"]}], "temperature": cfg["temperature"],
                   "top_p": cfg["top_p"], "top_k": -1, "seed": row["seed"],
                   "max_tokens": cfg["max_new_tokens"], "chat_template_kwargs": {"enable_thinking": False}}
        data = self.call("/chat/completions", payload)
        if data.get("model") != cfg["model"]:
            raise RuntimeError("Returned model identity differs from frozen model")
        choice = data["choices"][0]
        return {"raw_output": choice["message"].get("content") or "", "finish_reason": choice["finish_reason"],
                "model_returned": data["model"], "response": data, "payload_sha256": sha(payload),
                "input_tokens": data.get("usage", {}).get("prompt_tokens"),
                "output_tokens": data.get("usage", {}).get("completion_tokens")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["smoke", "pilot"])
    args = ap.parse_args()
    cfg = json.loads((ROOT / "config.json").read_text())
    freeze = json.loads((ROOT / "freeze.json").read_text())
    if hashes() != freeze["files"]:
        raise SystemExit("Frozen source/data mismatch; no generation authorized under this manifest")
    if args.stage == "pilot":
        gate = json.loads((ROOT / "runs/smoke/smoke_gate.json").read_text())
        if not gate["pass"] or gate["freeze_sha256"] != sha((ROOT / "freeze.json").read_bytes()):
            raise SystemExit("Smoke gate failed or manifest changed")
    out = ROOT / "runs" / args.stage
    if out.exists():
        raise SystemExit("No overwrites or automatic retries; use original records")
    requests = read_jsonl(ROOT / "data" / args.stage / "requests.jsonl")
    attempted = sum(len(read_jsonl(p)) for p in (ROOT / "runs").glob("*/raw.jsonl"))
    if len(requests) + attempted > cfg["total_generation_cap"]:
        raise SystemExit("Generation cap exceeded")
    out.mkdir(parents=True)
    start = time.monotonic()
    write_json(out / "started.json", {"pid": os.getpid(), "stage": args.stage, "unix_time": time.time(),
                                     "planned": len(requests), "freeze_sha256": sha((ROOT / "freeze.json").read_bytes())})
    sampler = LocalSampler(cfg) if cfg["backend"] == "transformers" else APISampler(cfg)
    write_json(out / "model_identity.json", sampler.identity)
    failures = invalid = done = 0
    status = "completed"
    with (out / "raw.jsonl").open("x") as log:
        # Sequential independent requests are intentional: each gets a fresh generation cache and seed.
        for row in requests:
            if time.monotonic() - start > cfg["timeout_seconds"]:
                status = "timeout"; break
            t = time.monotonic()
            record = {**row, "config_sha256": sha((ROOT / "config.json").read_bytes()),
                      "freeze_sha256": sha((ROOT / "freeze.json").read_bytes())}
            try:
                record.update(sampler.generate(row))
                parsed = parse_answer(record["raw_output"]) if record["finish_reason"] == "stop" else None
                record["parsed_answer"] = parsed
                record["status"] = "valid" if parsed is not None else "invalid"
                invalid += int(parsed is None)
            except Exception as exc:
                # Never log credential-bearing HTTP bodies or headers.
                record.update({"status": "error", "error_type": type(exc).__name__, "parsed_answer": None})
                failures += 1
            record["seconds"] = time.monotonic() - t
            record["completed_unix_time"] = time.time()
            log.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            log.flush()
            done += 1
            if done % 16 == 0 or done == len(requests):
                print(json.dumps({"stage": args.stage, "done": done, "planned": len(requests),
                                  "invalid": invalid, "failures": failures, "seconds": round(time.monotonic() - start, 2)}), flush=True)
            if failures >= cfg["max_infrastructure_failures"]:
                status = "infrastructure_stop"; break
    receipt = {"stage": args.stage, "status": status, "planned": len(requests), "attempted": done,
               "unattempted": len(requests) - done, "invalid": invalid, "errors": failures,
               "seconds": time.monotonic() - start, "freeze_sha256": sha((ROOT / "freeze.json").read_bytes())}
    write_json(out / "execution.json", receipt)
    if args.stage == "smoke":
        # Accuracy is not a gate. At least 95% of every request kind must parse correctly.
        rows = read_jsonl(out / "raw.jsonl")
        by_kind = {k: {"total": sum(r["kind"] == k for r in rows),
                       "valid": sum(r["kind"] == k and r["status"] == "valid" for r in rows)}
                   for k in ["task", "direct", "metadata"]}
        passed = done == len(requests) and failures == 0 and all(v["valid"] / v["total"] >= .95 for v in by_kind.values())
        write_json(out / "smoke_gate.json", {**receipt, "pass": passed, "by_kind": by_kind,
                                            "accuracy_used_for_gate": False})
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
