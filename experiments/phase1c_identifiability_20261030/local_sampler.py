"""Local sampler copied unchanged from phase01 collect.py; independent fresh caches."""
import os
import platform
from pathlib import Path
from design import sha


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

