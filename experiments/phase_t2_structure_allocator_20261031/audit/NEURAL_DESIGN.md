# T2 neural allocation implementation

Implementation: `t2/neural.py`. This file describes a single fixed architecture
and training configuration. No architecture sweep, validation selection,
language model, text representation, or reinforcement learning is involved.

## Observable features

Every external state is validated by `t2.core.validate_state` before encoding.
The whitelist applies recursively to posterior estimates and calibration
summaries. Extra truth, rate, seed, or identity fields are rejected. The model
does not receive experiment labels or teacher K as inference features.

- Each fact has 14 features: four log1p observation counts, four log1p forced
  counts, two smoothed positive-response frequencies, posterior sign probability,
  its normalized binary entropy, and two task-action availability flags.
- Each group has 9 features: two log1p type-report counts, posterior type
  probability and entropy, the two-entry estimated-type one-hot vector, known
  type-report accuracy (zero when unavailable), log1p group size, and the type
  action availability flag.
- The 17 global features are eta, posterior p and q, log1p successes and total
  for both calibration streams, the two smoothed calibration frequencies,
  log1p R, online count, online cap and remaining count, remaining/cap and
  online/cap, and log1p d and G. A zero cap uses denominator one.
- Membership is represented explicitly. Fact and group indices are not scalar
  features. These transforms contain no fitted quantities beyond the supplied
  Fused posterior estimates.

The action order is two task formats per fact, interleaved by fact, followed by
one type action per group. Illegal actions receive exactly zero weight.

## Hierarchical DeepSets

All hidden layers have width 32 and use SiLU. There are 12,899 parameters:

1. A shared two-layer fact encoder maps the 14 fact features to 32 coordinates.
2. Fact embeddings are summed within each supplied group. A shared two-layer
   group encoder maps the concatenated group sum and 9 group features to 32
   coordinates.
3. A shared two-layer global encoder receives the sum of fact embeddings, the
   sum of group embeddings, and the 17 global features, and outputs 32 coordinates.
4. The shared task head receives fact, containing-group and global embeddings,
   and returns two task logits. The shared group head receives group and global
   embeddings and returns one type logit. Both heads have one 32-wide hidden
   layer.
5. A single masked softmax normalizes all legal action logits jointly.

Permuting facts and relabeling their memberships permutes the task outputs.
Permuting groups permutes the type outputs. Group member order has no effect.
No maximum d or G is built into these layers. The synthetic d=6,G=3 unit case
checks architectural support, not scientific generalization. Scientific teacher
coverage remains restricted by the separate protocol.

## T2 padded MLP control

The T2 MLP has d<=4,G<=2, hidden widths 32 and 32, and 4,778 parameters. Its 105
inputs comprise the same padded fact, group and global features, the flattened
membership matrix, and explicit fact/group padding flags. It returns 10 padded
action logits with the same legal masked softmax. Feature means and population
standard deviations are fitted only to the supplied training rows. Columns with
standard deviation below 1e-6 use scale one. Inference never updates moments.

This model receives the Fused posterior features and is separate from the frozen
T1 MLP. It is not an architectural or feature-identical replay of T1. Its fixed
padding makes the effect of structural equivariance testable; it cannot predict
outside d<=4,G<=2.

## Objectives and radial approximation

The KL fit minimizes KL(teacher allocation || student allocation). The information
fit uses the same model initialization and adds coefficient-one positive regret:

    K_cut(w) = max_i relu(1 - b_i) / max(C_i @ w, 1e-10)
    loss = KL(teacher || student) + relu(K_cut(w)/K_teacher - 1)

Here C_i is a nonnegative action-information vector from the supplied finite cuts,
and b_i is the offline calibration information offset. Cuts and K_teacher are
training targets, not model inputs. The maximum uses the exact PyTorch max
subgradient. No hidden parameter enters the loss. A satisfied cut with zero
denominator contributes zero; a positive-demand zero-information cut contributes
a large finite value. The denominator floor is optimistic and does not establish
feasibility.

K_cut is a lower approximation based on a finite subset of constraints. Its
positive-part regret is consequently an optimistic surrogate. It must not be
reported as exact radial K or as certified information feasibility. Full exact
radial evaluation belongs to the separate information evaluator.

## Fixed fitting and receipts

The planned fit is 400 Adam updates, learning rate 0.001, batch size 64, uniform
sampling with replacement, CPU only and one Torch thread. The caller supplies
the same seed for both DeepSets fits. No model fits occur on import. Each call
uses one objective and writes only the final model checkpoint; a nonempty output
directory is rejected. There is no validation use or checkpoint selection.

Outputs are `model.pt`, `training_receipt.json`, and `progress.jsonl`. Receipts
record the initial state hash, training-payload hash, implementation hash, seed,
parameter count, complete training configuration, objective, numerical floor,
and sampled training-loss progress. `Predictor.load(path).predict(state)` returns
the legal normalized continuous allocation as a NumPy vector. Canonical public
states always retain task actions; the lower-level mask helper also handles an
empty legal set as an all-zero vector without NaNs.

## Verification boundary

`tests/test_neural.py` contains nine synthetic unit tests: independent fact and
group permutations including noncontiguous memberships, variable dimensions and
batch padding, masking, nested whitelist attacks, finite-cut arithmetic and zero
denominators, finite gradients and parameter limits, cut/action padding, training
normalization isolation, and checkpoint serialization. They perform no
scientific fitting, teacher generation or policy rollout. Passing these tests
establishes implementation contracts, not allocation quality or generalization.
