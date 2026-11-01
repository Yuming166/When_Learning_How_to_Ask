"""Observable-only T2 allocators; importing this module never trains a model.

The two DeepSets objectives share the same 32-wide architecture. The information
objective uses a finite-cut lower approximation to radial K, not exact radial K.
All model inputs pass the canonical observable-state whitelist before encoding.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np
import torch
from torch import nn


WIDTH = 32
FACT_DIM = 14
GROUP_DIM = 9
GLOBAL_DIM = 17
MLP_MAX_D = 4
MLP_MAX_G = 2
KINDS = ("mlp", "deepsets_kl", "deepsets_info")
FEATURE_VERSION = "t2_observable_features_v1"
RADIAL_DENOMINATOR_FLOOR = 1e-10


def _validate(state: dict) -> dict:
    # Late import keeps the feature boundary shared with the evaluator and avoids
    # importing the scientific teacher merely by importing the model module.
    from .core import validate_state
    return validate_state(state)


def _entropy(probability: np.ndarray) -> np.ndarray:
    p = np.clip(probability, 1e-12, 1 - 1e-12)
    return -(p * np.log(p) + (1 - p) * np.log1p(-p)) / math.log(2)


@dataclass
class Features:
    fact: np.ndarray
    group: np.ndarray
    global_: np.ndarray
    membership: np.ndarray
    action_mask: np.ndarray

    @property
    def d(self) -> int:
        return len(self.fact)

    @property
    def G(self) -> int:
        return len(self.group)


def encode_state(state: dict) -> Features:
    """Fixed, index-free transforms of the strict public state.

    Count entries are ordered exactly as in the public schema. No fitted feature
    transforms are used here; only the padded MLP fits training-set moments.
    """
    s = _validate(state)
    d, groups, e = s["d"], s["groups"], s["estimate"]
    G = len(groups)
    counts = np.asarray(s["counts"], dtype=np.float64)
    forced = np.asarray(s["forced_counts"], dtype=np.float64)
    reports = np.asarray(s["type_report_counts"], dtype=np.float64)
    mask = np.asarray(s["action_mask"], dtype=bool)
    theta = np.asarray(e["theta_prob"], dtype=np.float64)
    z = np.asarray(e["z_prob"], dtype=np.float64)
    membership = np.zeros((G, d), dtype=np.float32)
    for g, members in enumerate(groups):
        membership[g, members] = 1
    fact = np.concatenate((
        np.log1p(counts).reshape(d, 4),
        np.log1p(forced).reshape(d, 4),
        (counts[:, :, 1] + .5) / (counts.sum(axis=2) + 1),
        theta[:, None], _entropy(theta)[:, None], mask[:2*d].reshape(d, 2),
    ), axis=1)
    known_s = np.zeros(G) if s["known_s"] is None else np.asarray(s["known_s"])
    group = np.concatenate((
        np.log1p(reports), z[:, None], _entropy(z)[:, None],
        np.eye(2)[np.asarray(e["z"], dtype=int)], known_s[:, None],
        np.log1p(membership.sum(axis=1))[:, None], mask[2*d:, None],
    ), axis=1)
    high, low = s["calibration"]["high"], s["calibration"]["low"]
    cap = max(s["online_cap"], 1)
    global_ = np.asarray([
        s["eta"], e["p"], e["q"],
        np.log1p(high["successes"]), np.log1p(high["total"]),
        np.log1p(low["successes"]), np.log1p(low["total"]),
        (high["successes"] + .5) / (high["total"] + 1),
        (low["successes"] + .5) / (low["total"] + 1),
        np.log1p(s["R"]), np.log1p(s["online"]),
        np.log1p(s["online_cap"]), np.log1p(s["remaining"]),
        s["remaining"] / cap, s["online"] / cap, np.log1p(d), np.log1p(G),
    ], dtype=np.float32)
    if fact.shape != (d, FACT_DIM) or group.shape != (G, GROUP_DIM) or global_.shape != (GLOBAL_DIM,):
        raise AssertionError("Feature contract drift")
    return Features(fact.astype(np.float32), group.astype(np.float32), global_, membership, mask)


def collate(features: list[Features], *, padded_mlp: bool = False) -> dict[str, torch.Tensor]:
    """Batch arbitrary partitions without making fact/group indices features."""
    if not features:
        raise ValueError("Empty batch")
    D = MLP_MAX_D if padded_mlp else max(x.d for x in features)
    G = MLP_MAX_G if padded_mlp else max(x.G for x in features)
    if any(x.d > D or x.G > G for x in features):
        raise ValueError("Padded MLP supports d <= 4 and G <= 2 only")
    B = len(features)
    result = {
        "fact": torch.zeros(B, D, FACT_DIM), "group": torch.zeros(B, G, GROUP_DIM),
        "global": torch.zeros(B, GLOBAL_DIM), "membership": torch.zeros(B, G, D),
        "fact_valid": torch.zeros(B, D, dtype=torch.bool),
        "group_valid": torch.zeros(B, G, dtype=torch.bool),
        "action_mask": torch.zeros(B, 2*D+G, dtype=torch.bool),
    }
    for i, x in enumerate(features):
        result["fact"][i, :x.d] = torch.from_numpy(x.fact)
        result["group"][i, :x.G] = torch.from_numpy(x.group)
        result["global"][i] = torch.from_numpy(x.global_)
        result["membership"][i, :x.G, :x.d] = torch.from_numpy(x.membership)
        result["fact_valid"][i, :x.d] = True
        result["group_valid"][i, :x.G] = True
        result["action_mask"][i, :2*x.d] = torch.from_numpy(x.action_mask[:2*x.d])
        result["action_mask"][i, 2*D:2*D+x.G] = torch.from_numpy(x.action_mask[2*x.d:])
    return result


def masked_distribution(logits: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Legal simplex weights and finite log probabilities, including empty masks."""
    if logits.shape != mask.shape or not torch.isfinite(logits).all():
        raise ValueError("Invalid logits or mask shape")
    # A finite sentinel also handles entirely masked rows without a NaN softmax.
    masked_logits = logits.masked_fill(~mask, torch.finfo(logits.dtype).min)
    logs = torch.log_softmax(masked_logits, dim=-1)
    weights = logs.exp().masked_fill(~mask, 0)
    logs = logs.masked_fill(~mask, 0)
    return weights, logs


def _two_layer(in_dim: int, out_dim: int = WIDTH) -> nn.Sequential:
    return nn.Sequential(nn.Linear(in_dim, WIDTH), nn.SiLU(), nn.Linear(WIDTH, out_dim), nn.SiLU())


class HierarchicalDeepSets(nn.Module):
    """Equivariant fact -> group sum -> global sum -> action heads."""
    def __init__(self) -> None:
        super().__init__()
        self.fact_encoder = _two_layer(FACT_DIM)
        self.group_encoder = _two_layer(WIDTH + GROUP_DIM)
        self.global_encoder = _two_layer(2*WIDTH + GLOBAL_DIM)
        self.task_head = nn.Sequential(nn.Linear(3*WIDTH, WIDTH), nn.SiLU(), nn.Linear(WIDTH, 2))
        self.type_head = nn.Sequential(nn.Linear(2*WIDTH, WIDTH), nn.SiLU(), nn.Linear(WIDTH, 1))

    def forward(self, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        fact = self.fact_encoder(batch["fact"]) * batch["fact_valid"].unsqueeze(-1)
        group_sum = torch.bmm(batch["membership"], fact)
        group = self.group_encoder(torch.cat((group_sum, batch["group"]), dim=-1))
        group = group * batch["group_valid"].unsqueeze(-1)
        global_ = self.global_encoder(torch.cat((fact.sum(1), group.sum(1), batch["global"]), dim=-1))
        parents = torch.bmm(batch["membership"].transpose(1, 2), group)
        task_logits = self.task_head(torch.cat((fact, parents, global_[:, None].expand_as(fact)), dim=-1))
        type_logits = self.type_head(torch.cat((group, global_[:, None].expand_as(group)), dim=-1))
        logits = torch.cat((task_logits.flatten(1), type_logits.squeeze(-1)), dim=-1)
        return masked_distribution(logits, batch["action_mask"])


class PaddedMLP(nn.Module):
    """T2 control, distinct from the frozen T1 MLP and its feature definition."""
    INPUT_DIM = MLP_MAX_D*FACT_DIM + MLP_MAX_G*GROUP_DIM + GLOBAL_DIM + MLP_MAX_D*MLP_MAX_G + MLP_MAX_D + MLP_MAX_G

    def __init__(self) -> None:
        super().__init__()
        self.register_buffer("feature_mean", torch.zeros(self.INPUT_DIM))
        self.register_buffer("feature_scale", torch.ones(self.INPUT_DIM))
        self.network = nn.Sequential(
            nn.Linear(self.INPUT_DIM, WIDTH), nn.SiLU(), nn.Linear(WIDTH, WIDTH),
            nn.SiLU(), nn.Linear(WIDTH, 2*MLP_MAX_D+MLP_MAX_G),
        )

    @staticmethod
    def flatten(batch: dict[str, torch.Tensor]) -> torch.Tensor:
        if batch["fact"].shape[1] != MLP_MAX_D or batch["group"].shape[1] != MLP_MAX_G:
            raise ValueError("Use padded_mlp=True when collating MLP inputs")
        return torch.cat((batch["fact"].flatten(1), batch["group"].flatten(1),
                          batch["global"], batch["membership"].flatten(1),
                          batch["fact_valid"].float(), batch["group_valid"].float()), dim=1)

    def fit_normalization(self, training_features: list[Features]) -> None:
        values = self.flatten(collate(training_features, padded_mlp=True))
        with torch.no_grad():
            self.feature_mean.copy_(values.mean(0))
            scales = values.std(0, unbiased=False)
            # Constant training columns retain their original units at inference.
            self.feature_scale.copy_(torch.where(scales < 1e-6, torch.ones_like(scales), scales))

    def forward(self, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        values = (self.flatten(batch) - self.feature_mean) / self.feature_scale
        return masked_distribution(self.network(values), batch["action_mask"])


def finite_cut_radial(weights: torch.Tensor, coefficients: torch.Tensor, offsets: torch.Tensor) -> torch.Tensor:
    """K_cut(w)=max_i (1-b_i)_+/(C_i w), with a documented floor.

    Shapes: [B,A], [B,N,A], [B,N]. Exact max supplies the usual differentiable
    subgradient. The denominator floor makes zero-information cases finite and
    optimistic; this function must never be reported as exact radial evaluation.
    """
    if coefficients.ndim != 3 or offsets.shape != coefficients.shape[:2] or coefficients.shape[0] != weights.shape[0] or coefficients.shape[2] != weights.shape[1] or coefficients.shape[1] == 0:
        raise ValueError("Invalid finite-cut shapes")
    if not torch.isfinite(coefficients).all() or not torch.isfinite(offsets).all() or (coefficients < 0).any() or (offsets < 0).any():
        raise ValueError("Finite cuts must contain finite nonnegative information")
    information = torch.einsum("bna,ba->bn", coefficients, weights)
    required = torch.relu(1 - offsets)
    return (required / information.clamp_min(RADIAL_DENOMINATOR_FLOOR)).amax(dim=1)


def allocation_loss(weights: torch.Tensor, log_weights: torch.Tensor, targets: torch.Tensor,
                    *, coefficients: torch.Tensor | None = None, offsets: torch.Tensor | None = None,
                    teacher_K: torch.Tensor | None = None) -> tuple[torch.Tensor, dict[str, float]]:
    target_logs = targets.clamp_min(torch.finfo(targets.dtype).tiny).log()
    kl = (targets * (target_logs - log_weights)).sum(1).mean()
    regret = weights.sum() * 0
    if coefficients is not None:
        if offsets is None or teacher_K is None or not torch.isfinite(teacher_K).all() or (teacher_K <= 0).any():
            raise ValueError("Information loss requires finite positive teacher K")
        radial = finite_cut_radial(weights, coefficients, offsets)
        regret = torch.relu(radial / teacher_K - 1).mean()
    loss = kl + regret
    if not torch.isfinite(loss):
        raise FloatingPointError("Non-finite training objective")
    return loss, {"loss": float(loss.detach()), "kl": float(kl.detach()), "finite_cut_positive_regret": float(regret.detach())}


def _new_model(kind: str) -> nn.Module:
    if kind not in KINDS:
        raise ValueError(f"Unknown model kind: {kind}")
    return PaddedMLP() if kind == "mlp" else HierarchicalDeepSets()


class Predictor:
    def __init__(self, model: nn.Module, kind: str, *, receipt: dict | None = None, model_path: Path | None = None) -> None:
        self.model = model.cpu().eval()
        self.kind = kind
        self.receipt = receipt or {}
        self.model_path = model_path

    def predict(self, state: dict) -> np.ndarray:
        features = encode_state(state)
        batch = collate([features], padded_mlp=self.kind == "mlp")
        with torch.inference_mode():
            weights, _ = self.model(batch)
        D = batch["fact"].shape[1]
        result = torch.cat((weights[0, :2*features.d], weights[0, 2*D:2*D+features.G])).double().numpy()
        if not np.isfinite(result).all() or (result < 0).any() or np.any(result[~features.action_mask] != 0):
            raise FloatingPointError("Invalid model allocation")
        total = result.sum()
        return result / total if total > 0 else result

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"format": "t2_neural_v1", "feature_version": FEATURE_VERSION,
                    "kind": self.kind, "width": WIDTH, "state_dict": self.model.state_dict(),
                    "receipt": self.receipt}, path)
        self.model_path = path

    @classmethod
    def load(cls, path: str | Path) -> "Predictor":
        path = Path(path)
        if path.is_dir():
            path = path / "model.pt"
        torch.set_num_threads(1)
        payload = torch.load(path, map_location="cpu", weights_only=True)
        if payload.get("format") != "t2_neural_v1" or payload.get("feature_version") != FEATURE_VERSION or payload.get("width") != WIDTH:
            raise ValueError("Unsupported model checkpoint")
        model = _new_model(payload["kind"])
        model.load_state_dict(payload["state_dict"], strict=True)
        return cls(model, payload["kind"], receipt=payload.get("receipt"), model_path=path)


def _json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Unsupported provenance value: {type(value).__name__}")


def _prepare_rows(rows: list[dict], kind: str) -> tuple[list[Features], list[np.ndarray]]:
    if not rows:
        raise ValueError("Training rows are empty")
    features, targets = [], []
    for row in rows:
        x = encode_state(row["state"])
        target = np.asarray(row["teacher_weights"], dtype=np.float64)
        if target.shape != x.action_mask.shape or not np.isfinite(target).all() or (target < 0).any() or np.any(target[~x.action_mask] != 0) or abs(target.sum() - 1) > 1e-6:
            raise ValueError("Teacher weights violate the legal simplex")
        if not math.isfinite(float(row["teacher_K"])) or row["teacher_K"] <= 0:
            raise ValueError("Teacher K must be finite and positive")
        if kind == "mlp" and (x.d > MLP_MAX_D or x.G > MLP_MAX_G):
            raise ValueError("Padded MLP training dimensions exceed d=4,G=2")
        if kind == "deepsets_info":
            cuts = row["cuts"]
            C = np.asarray(cuts["cut_coefficients"], dtype=np.float64)
            b = np.asarray(cuts["cut_offsets"], dtype=np.float64)
            if C.ndim != 2 or C.shape[0] == 0 or C.shape[1] != len(target) or b.shape != (len(C),) or not np.isfinite(C).all() or not np.isfinite(b).all() or (C < 0).any() or (b < 0).any():
                raise ValueError("Invalid training information cuts")
        features.append(x)
        targets.append(target.astype(np.float32))
    return features, targets


def _training_batch(rows: list[dict], features: list[Features], targets: list[np.ndarray], indices: np.ndarray,
                    kind: str) -> tuple[dict[str, torch.Tensor], torch.Tensor, dict[str, torch.Tensor]]:
    chosen = [features[int(i)] for i in indices]
    batch = collate(chosen, padded_mlp=kind == "mlp")
    D, A = batch["fact"].shape[1], batch["action_mask"].shape[1]
    y = torch.zeros(len(chosen), A)
    extras = {}
    if kind == "deepsets_info":
        N = max(len(rows[int(i)]["cuts"]["cut_offsets"]) for i in indices)
        extras = {"coefficients": torch.zeros(len(chosen), N, A),
                  "offsets": torch.ones(len(chosen), N), "teacher_K": torch.zeros(len(chosen))}
    for b, (idx, x) in enumerate(zip(indices, chosen)):
        target = torch.from_numpy(targets[int(idx)])
        y[b, :2*x.d] = target[:2*x.d]
        y[b, 2*D:2*D+x.G] = target[2*x.d:]
        if extras:
            row = rows[int(idx)]
            C = torch.as_tensor(row["cuts"]["cut_coefficients"], dtype=torch.float32)
            n = len(C)
            extras["coefficients"][b, :n, :2*x.d] = C[:, :2*x.d]
            extras["coefficients"][b, :n, 2*D:2*D+x.G] = C[:, 2*x.d:]
            extras["offsets"][b, :n] = torch.as_tensor(row["cuts"]["cut_offsets"], dtype=torch.float32)
            extras["teacher_K"][b] = row["teacher_K"]
    return batch, y, extras


def fit(rows: list[dict], kind: str = "deepsets_kl", outdir: str | Path | None = None,
        steps: int = 400, seed: int = 20261031, batch_size: int = 64, lr: float = .001) -> Predictor:
    """One fixed CPU fit, with one final checkpoint and no validation selection."""
    if kind not in KINDS or steps < 1 or batch_size < 1 or not math.isfinite(lr) or lr <= 0 or outdir is None:
        raise ValueError("Invalid fit configuration")
    outdir = Path(outdir)
    if outdir.exists() and any(outdir.iterdir()):
        raise FileExistsError("Fit output must be empty; refusing to replace a previous fit")
    features, targets = _prepare_rows(rows, kind)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model = _new_model(kind).cpu()
    if kind == "mlp":
        model.fit_normalization(features)
    initial_hash = hashlib.sha256(b"".join(v.detach().numpy().tobytes() for v in model.state_dict().values())).hexdigest()
    count = sum(p.numel() for p in model.parameters())
    if count >= 50000:
        raise AssertionError("Frozen parameter budget exceeded")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    outdir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    progress = []
    with (outdir / "progress.jsonl").open("w") as log:
        for step in range(1, steps + 1):
            indices = rng.integers(0, len(rows), size=batch_size)
            batch, y, extras = _training_batch(rows, features, targets, indices, kind)
            optimizer.zero_grad(set_to_none=True)
            weights, log_weights = model(batch)
            loss, metrics = allocation_loss(weights, log_weights, y, **extras)
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                raise FloatingPointError("Non-finite training gradient")
            optimizer.step()
            if step == 1 or step % 25 == 0 or step == steps:
                record = {"step": step, **metrics}
                progress.append(record)
                log.write(json.dumps(record, sort_keys=True) + "\n")
                log.flush()
    training_payload = [{k: row[k] for k in ("state", "teacher_weights", "teacher_K")} |
                        ({"cuts": row["cuts"]} if kind == "deepsets_info" else {}) for row in rows]
    training_hash = hashlib.sha256(json.dumps(training_payload, sort_keys=True, separators=(",", ":"), allow_nan=False, default=_json_default).encode()).hexdigest()
    receipt = {
        "kind": kind, "feature_version": FEATURE_VERSION, "width": WIDTH,
        "parameter_count": count, "training_rows": len(rows), "steps": steps,
        "seed": seed, "batch_size": batch_size, "learning_rate": lr,
        "optimizer": "Adam", "device": "cpu", "torch_threads": 1,
        "torch_version": str(torch.__version__), "deterministic_algorithms": True,
        "initial_state_sha256": initial_hash, "training_payload_sha256": training_hash,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "normalization": "training_rows_only" if kind == "mlp" else "fixed_observable_transforms",
        "selection": "none; final checkpoint only", "checkpoint_count": 1,
        "objective": "KL(teacher||student)" + (" + relu(K_cut(student)/K_teacher-1)" if kind == "deepsets_info" else ""),
        "information_regret_weight": 1.0 if kind == "deepsets_info" else 0.0,
        "information_surrogate": "finite-cut radial lower approximation with exact max subgradient",
        "radial_denominator_floor": RADIAL_DENOMINATOR_FLOOR,
        "uses_hidden_parameters": False, "validation_used": False,
        "elapsed_seconds": time.perf_counter() - started, "progress": progress,
        "final_batch": metrics,
    }
    predictor = Predictor(model, kind, receipt=receipt)
    predictor.save(outdir / "model.pt")
    (outdir / "training_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return predictor
