"""Fixed CPU student: raw legal features, train-only normalization, no search.

Importing this module neither imports Torch nor trains a model. Execution of
train_mlp is an explicit, separately authorized step after protocol freeze.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from time import perf_counter, process_time


FEATURES = 69
WIDTH = 64
ACTIONS = 10
EPOCHS = 200
LEARNING_RATE = .001
TRAINING_SEED = 731031


def _torch_model(torch):
    return torch.nn.Sequential(
        torch.nn.Linear(FEATURES, WIDTH), torch.nn.ReLU(),
        torch.nn.Linear(WIDTH, WIDTH), torch.nn.ReLU(),
        torch.nn.Linear(WIDTH, ACTIONS),
    ).to(device="cpu", dtype=torch.float32)


def _training_arrays(rows):
    from .core import state_features
    features, masks, targets = [], [], []
    for row in rows:
        state = row["state"]
        feature = list(state_features(state))
        mask = [bool(value) for value in state["action_mask"]]
        target = [float(value) for value in row["teacher_weights"]]
        if len(feature) != FEATURES or len(mask) != ACTIONS or len(target) != ACTIONS:
            raise ValueError("Unexpected frozen feature/action dimensions")
        if not all(math.isfinite(v) for v in feature + target):
            raise ValueError("Nonfinite training data")
        if not any(mask) or any(v < 0 or (v > 1e-12 and not legal) for v, legal in zip(target, mask)):
            raise ValueError("Teacher target violates legal action mask")
        total = math.fsum(target)
        if abs(total - 1) > 1e-6:
            raise ValueError("Teacher target must sum to one")
        features.append(feature)
        masks.append(mask)
        targets.append([v / total for v in target])
    return features, masks, targets


def _train_mlp_once(train_rows, output_dir, *, epochs=EPOCHS, max_seconds=120,
                    seed=TRAINING_SEED, progress=None):
    """One fixed full-batch KL fit on exactly 1,024 training states.

    Validation never selects epochs, hyperparameters or checkpoint. The final
    reached epoch is saved even if the explicit wall-time cap interrupts the
    schedule; status and completed epochs make that partial run visible.
    The caller must supervise the process for a hard operating-system timeout.
    """
    if epochs != EPOCHS or seed != TRAINING_SEED:
        raise ValueError("T1 permits only the frozen 200-epoch architecture/seed")
    if not 0 < max_seconds <= 120:
        raise ValueError("MLP wall cap must be in (0,120] seconds")
    rows = list(train_rows)
    if len(rows) != 1024:
        raise ValueError("The frozen MLP fit requires exactly 1024 train states")
    destination = Path(output_dir)
    checkpoint = destination / "mlp_student.pt"
    if checkpoint.exists() or (destination / "mlp_training.json").exists():
        raise FileExistsError("Refuse to overwrite or repeat the frozen MLP run")
    started, cpu_started = perf_counter(), process_time()
    features, masks, targets = _training_arrays(rows)
    import torch
    torch.set_num_threads(1)
    # fork_rng(devices=[]) keeps the caller's CPU RNG unchanged and performs no
    # CUDA work. The student and all its tensors are explicitly on the CPU.
    with torch.random.fork_rng(devices=[]):
        torch.random.default_generator.manual_seed(seed)
        x = torch.tensor(features, dtype=torch.float32, device="cpu")
        mask = torch.tensor(masks, dtype=torch.bool, device="cpu")
        target = torch.tensor(targets, dtype=torch.float32, device="cpu")
        mean = x.mean(dim=0)
        std = x.std(dim=0, unbiased=False)
        std = torch.where(std > 1e-6, std, torch.ones_like(std))
        x = (x - mean) / std
        model = _torch_model(torch)
        optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
        losses = []
        status = "completed"
        for epoch in range(epochs):
            if perf_counter() - started >= max_seconds:
                status = "time_cap"
                break
            optimizer.zero_grad(set_to_none=True)
            logits = model(x).masked_fill(~mask, -1e9)
            log_prob = torch.log_softmax(logits, dim=-1)
            # Finite masked logits avoid 0*(-inf); target zeros contribute zero.
            loss = (target * (target.clamp_min(1e-30).log() - log_prob)).sum(dim=1).mean()
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("Nonfinite MLP training loss")
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach()))
            if progress is not None:
                progress({"completed_epochs": len(losses), "optimizer_updates": len(losses),
                          "last_train_loss": losses[-1], "wall_seconds": perf_counter() - started})
        model.eval()
        with torch.inference_mode():
            final_log_prob = torch.log_softmax(model(x).masked_fill(~mask, -1e9), dim=-1)
            final_loss = float((target * (target.clamp_min(1e-30).log() - final_log_prob)).sum(dim=1).mean())
        receipt = {
            "status": status, "train_states": len(rows), "architecture": [FEATURES, WIDTH, WIDTH, ACTIONS],
            "activation": "ReLU", "output": "legal_action_masked_softmax", "device": "cpu",
            "loss": "forward_KL_teacher_weights_to_student", "optimizer": "Adam",
            "learning_rate": LEARNING_RATE, "batch_size": 1024, "seed": seed,
            "planned_epochs": epochs, "completed_epochs": len(losses),
            "optimizer_updates": len(losses), "loss_history": losses,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "final_train_loss": final_loss, "normalization_fit": "train_only",
            "checkpoint_selection": "last_completed_epoch_no_validation_selection",
            "max_seconds": max_seconds, "training_wall_seconds": perf_counter() - started,
            "training_cpu_seconds": process_time() - cpu_started,
            "torch_version": str(torch.__version__),
        }
        destination.mkdir(parents=True, exist_ok=True)
        torch.save({"model_state": model.state_dict(), "mean": mean, "std": std,
                    "receipt": receipt}, checkpoint)
        (destination / "mlp_training.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return {**receipt, "checkpoint": str(checkpoint)}


def train_mlp(train_rows, output_dir, *, epochs=EPOCHS, max_seconds=120,
              seed=TRAINING_SEED):
    """Durable single-attempt wrapper; failures do not silently permit retries."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    started_path = destination / "mlp_started.json"
    initial = {"status": "started", "architecture": [FEATURES, WIDTH, WIDTH, ACTIONS],
               "epochs": epochs, "seed": seed, "max_seconds": max_seconds,
               "automatic_retry": False, "device": "cpu", "parameter_count": 9290}
    with started_path.open("x") as handle:
        handle.write(json.dumps(initial, indent=2) + "\n")
        handle.flush()
    current = {"completed_epochs": 0, "optimizer_updates": 0}

    def progress(value):
        current.update(value)
        temporary = destination / "mlp_progress.tmp"
        temporary.write_text(json.dumps(current, indent=2) + "\n")
        temporary.replace(destination / "mlp_progress.json")

    try:
        return _train_mlp_once(train_rows, destination, epochs=epochs, max_seconds=max_seconds,
                               seed=seed, progress=progress)
    except BaseException as exc:
        failure = {"status": "failed", "error_type": type(exc).__name__, "error": str(exc),
                   **current, "automatic_retry": False}
        (destination / "mlp_failed.json").write_text(json.dumps(failure, indent=2) + "\n")
        raise


class MLPStudent:
    """predict(state) has the same public-state boundary as QwenPolicy."""

    def __init__(self, model, mean, std, torch_module):
        self.model, self.mean, self.std, self.torch = model, mean, std, torch_module
        self.model.eval()

    @classmethod
    def load(cls, path):
        import torch
        torch.set_num_threads(1)
        checkpoint = torch.load(Path(path), map_location="cpu", weights_only=True)
        if checkpoint["receipt"]["architecture"] != [FEATURES, WIDTH, WIDTH, ACTIONS]:
            raise ValueError("Checkpoint architecture does not match frozen T1")
        model = _torch_model(torch)
        model.load_state_dict(checkpoint["model_state"])
        return cls(model, checkpoint["mean"], checkpoint["std"], torch)

    def predict(self, state):
        from .core import state_features
        started, cpu_started = perf_counter(), process_time()
        values = list(state_features(state))
        mask = state["action_mask"]
        if len(values) != FEATURES or len(mask) != ACTIONS or not any(mask):
            raise ValueError("Invalid MLP observable state dimensions")
        torch = self.torch
        x = torch.tensor(values, dtype=torch.float32, device="cpu")
        legal = torch.tensor(mask, dtype=torch.bool, device="cpu")
        with torch.inference_mode():
            logits = self.model((x - self.mean) / self.std).masked_fill(~legal, -1e9)
            weights = torch.softmax(logits, dim=-1).tolist()
        if any(not math.isfinite(v) for v in weights):
            raise FloatingPointError("Nonfinite MLP prediction")
        return {"weights10": weights, "raw": json.dumps({"weights": weights}, separators=(",", ":")),
                "valid": True, "latency": perf_counter() - started,
                "cpu_seconds": process_time() - cpu_started,
                "prompt_tokens": 0, "output_tokens": 0, "model": "MLP_69_64_64_10"}
