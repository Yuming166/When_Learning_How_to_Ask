"""Synthetic architecture/gradient checks only: no scientific fit or rollout."""
from copy import deepcopy
import tempfile
from pathlib import Path
import unittest

import numpy as np
import torch

from t2.neural import (
    HierarchicalDeepSets, PaddedMLP, Predictor, allocation_loss, collate,
    encode_state, finite_cut_radial, masked_distribution, _training_batch,
)


def synthetic_state(groups=((0, 2), (1,)), available=True):
    groups = [list(g) for g in groups]
    d, G = sum(map(len, groups)), len(groups)
    counts = (np.arange(d*4).reshape(d, 2, 2) % 5).astype(int)
    reports = (np.arange(G*2).reshape(G, 2) % 3).astype(int) if available else np.zeros((G, 2), dtype=int)
    online = int(counts.sum() + reports.sum())
    return {
        "schema": "t2_observable_v1", "d": d, "groups": groups,
        "eta": .05, "known_s": np.linspace(.7, .85, G).tolist() if available else None,
        "counts": counts.tolist(), "forced_counts": (counts // 2).tolist(),
        "type_report_counts": reports.tolist(),
        "calibration": {"high": {"successes": 8, "total": 10}, "low": {"successes": 6, "total": 10}},
        "R": 8.0, "online": online, "online_cap": online + 80, "remaining": 80,
        "estimate": {"p": .8, "q": .6, "theta_prob": np.linspace(.1, .9, d).tolist(),
                     "z_prob": np.linspace(.2, .8, G).tolist(), "z": (np.arange(G) % 2).tolist()},
        "action_mask": [1]*(2*d) + [int(available)]*G,
    }


def relabel(state, fact_order, group_order):
    """New index i names old fact fact_order[i]; similarly for groups."""
    s = deepcopy(state)
    inverse = {old: new for new, old in enumerate(fact_order)}
    s["groups"] = [[inverse[j] for j in reversed(state["groups"][g])] for g in group_order]
    for key in ("counts", "forced_counts"):
        s[key] = [state[key][j] for j in fact_order]
    s["estimate"]["theta_prob"] = [state["estimate"]["theta_prob"][j] for j in fact_order]
    for key in ("z_prob", "z"):
        s["estimate"][key] = [state["estimate"][key][g] for g in group_order]
    s["type_report_counts"] = [state["type_report_counts"][g] for g in group_order]
    if state["known_s"] is not None:
        s["known_s"] = [state["known_s"][g] for g in group_order]
    order = [2*j+m for j in fact_order for m in (0, 1)] + [2*state["d"]+g for g in group_order]
    s["action_mask"] = [state["action_mask"][j] for j in order]
    return s, order


class NeuralContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        torch.manual_seed(17)

    def test_fact_and_group_permutation_equivariance_noncontiguous(self):
        state = synthetic_state(((0, 3), (1, 5), (2, 4)))
        predictor = Predictor(HierarchicalDeepSets(), "deepsets_kl")
        original = predictor.predict(state)
        for fact_order, group_order in [
            ([4, 1, 5, 0, 3, 2], [2, 0, 1]),
            ([0, 1, 2, 3, 4, 5], [1, 2, 0]),
            ([5, 4, 3, 2, 1, 0], [0, 1, 2]),
        ]:
            permuted, action_order = relabel(state, fact_order, group_order)
            np.testing.assert_allclose(predictor.predict(permuted), original[action_order], rtol=2e-6, atol=2e-7)

    def test_variable_dimensions_and_batch_padding(self):
        states = [synthetic_state(((0,),)), synthetic_state(), synthetic_state(((0, 3), (1, 5), (2, 4)))]
        model = HierarchicalDeepSets().eval()
        features = [encode_state(s) for s in states]
        batch = collate(features)
        with torch.no_grad():
            weights, _ = model(batch)
        D = batch["fact"].shape[1]
        for i, feature in enumerate(features):
            packed = torch.cat((weights[i, :2*feature.d], weights[i, 2*D:2*D+feature.G])).numpy()
            np.testing.assert_allclose(packed, Predictor(model, "deepsets_kl").predict(states[i]), rtol=2e-6, atol=2e-7)
            self.assertAlmostEqual(float(weights[i].sum()), 1, places=6)
            self.assertTrue(torch.equal(weights[i][~batch["action_mask"][i]], torch.zeros_like(weights[i][~batch["action_mask"][i]])))

    def test_legal_masks_and_zero_mask_safeguard(self):
        state = synthetic_state(available=False)
        for kind, model in (("mlp", PaddedMLP()), ("deepsets_kl", HierarchicalDeepSets())):
            predicted = Predictor(model, kind).predict(state)
            self.assertAlmostEqual(float(predicted.sum()), 1, places=12)
            np.testing.assert_array_equal(predicted[2*state["d"]:], 0)
        logits = torch.tensor([[1000., -1000.], [2., 3.]], requires_grad=True)
        weights, logs = masked_distribution(logits, torch.tensor([[False, False], [True, False]]))
        self.assertTrue(torch.isfinite(weights).all() and torch.isfinite(logs).all())
        self.assertEqual(weights.tolist(), [[0., 0.], [1., 0.]])
        weights.sum().backward()
        self.assertTrue(torch.isfinite(logits.grad).all())

    def test_strict_observable_whitelist(self):
        for mutate in (
            lambda s: s.update({"hidden_theta": [1]*s["d"]}),
            lambda s: s["estimate"].update({"true_p": .81}),
            lambda s: s["calibration"]["high"].update({"seed": 14}),
        ):
            state = synthetic_state()
            mutate(state)
            with self.assertRaises(ValueError):
                Predictor(HierarchicalDeepSets(), "deepsets_kl").predict(state)

    def test_radial_formula_offsets_and_zero_denominators(self):
        weights = torch.tensor([[.25, .75]], requires_grad=True)
        C = torch.tensor([[[1., 0.], [0., 2.], [0., 0.]]])
        b = torch.tensor([[.5, .25, 1.]])
        result = finite_cut_radial(weights, C, b)
        self.assertAlmostEqual(float(result), 2.)
        result.backward()
        self.assertTrue(torch.isfinite(weights.grad).all())
        zeros = finite_cut_radial(weights.detach(), torch.zeros(1, 1, 2), torch.zeros(1, 1))
        self.assertTrue(torch.isfinite(zeros).all())
        self.assertGreater(float(zeros), 1e9)
        satisfied = finite_cut_radial(weights.detach(), torch.zeros(1, 1, 2), torch.ones(1, 1)*1.2)
        self.assertEqual(float(satisfied), 0.)

    def test_information_gradient_and_parameter_budget(self):
        torch.manual_seed(91)
        first = HierarchicalDeepSets()
        torch.manual_seed(91)
        second = HierarchicalDeepSets()
        for a, b in zip(first.parameters(), second.parameters()):
            torch.testing.assert_close(a, b, rtol=0, atol=0)
        batch = collate([encode_state(synthetic_state())])
        weights, log_weights = first(batch)
        targets = torch.zeros_like(weights)
        targets[0, 0] = 1
        C = torch.linspace(.01, .08, weights.shape[1])[None, None]
        loss, metrics = allocation_loss(weights, log_weights, targets, coefficients=C,
                                        offsets=torch.zeros(1, 1), teacher_K=torch.ones(1))
        self.assertGreater(metrics["finite_cut_positive_regret"], 0)
        loss.backward()
        for parameter in first.parameters():
            self.assertIsNotNone(parameter.grad)
            self.assertTrue(torch.isfinite(parameter.grad).all())
        self.assertGreater(sum(float(p.grad.abs().sum()) for p in first.parameters()), 0)
        for model in (first, PaddedMLP()):
            self.assertLess(sum(p.numel() for p in model.parameters()), 50000)

    def test_training_batch_keeps_type_positions_and_cut_padding(self):
        states = [synthetic_state(((0,),)), synthetic_state()]
        rows, features, targets = [], [], []
        for index, state in enumerate(states):
            x = encode_state(state)
            target = np.arange(1, 2*x.d+x.G+1, dtype=np.float32)
            target /= target.sum()
            C = np.tile(np.arange(2*x.d+x.G, dtype=np.float32), (index+1, 1))
            rows.append({"state": state, "teacher_K": 2., "cuts": {"cut_coefficients": C.tolist(), "cut_offsets": [.2]*(index+1)}})
            features.append(x)
            targets.append(target)
        batch, y, extras = _training_batch(rows, features, targets, np.array([0, 1]), "deepsets_info")
        D = batch["fact"].shape[1]
        self.assertEqual(float(y[0, 2*D]), float(targets[0][-1]))
        self.assertEqual(float(extras["coefficients"][0, 0, 2*D]), 2.)
        self.assertEqual(float(extras["offsets"][0, 1]), 1.)
        self.assertEqual(float(extras["coefficients"][0, 1].sum()), 0.)

    def test_mlp_normalization_training_only_and_dimension_limit(self):
        state = synthetic_state()
        model = PaddedMLP()
        model.fit_normalization([encode_state(state)])
        before = (model.feature_mean.clone(), model.feature_scale.clone())
        changed = deepcopy(state)
        changed["calibration"]["high"]["successes"] = 9
        predicted = Predictor(model, "mlp").predict(changed)
        self.assertTrue(np.isfinite(predicted).all())
        torch.testing.assert_close(model.feature_mean, before[0])
        torch.testing.assert_close(model.feature_scale, before[1])
        with self.assertRaises(ValueError):
            Predictor(model, "mlp").predict(synthetic_state(((0, 3), (1, 5), (2, 4))))

    def test_serialization_round_trip_without_training(self):
        state = synthetic_state()
        for kind, model in (("mlp", PaddedMLP()), ("deepsets_info", HierarchicalDeepSets())):
            original = Predictor(model, kind)
            with tempfile.TemporaryDirectory(prefix="t2-neural-unit-") as directory:
                path = Path(directory) / "model.pt"
                original.save(path)
                restored = Predictor.load(path)
                np.testing.assert_array_equal(original.predict(state), restored.predict(state))


if __name__ == "__main__":
    unittest.main()
