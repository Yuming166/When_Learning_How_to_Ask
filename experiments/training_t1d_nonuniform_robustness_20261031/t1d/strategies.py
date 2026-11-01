"""Additive T1d policies. Frozen historical modules are never patched on disk."""
import math
import time
import numpy as np
from scipy.special import rel_entr
from . import bootstrap
from t1c.strategies import Factor, FreshLite, Switching
from t1a.solvers import Solver
from t1b.belief import action, index, stable_argmax

POLICIES = ['KL-OriginalSolver', 'KL-AnalyticReuse', 'KL-Fresh', 'Fused-Info',
            'IG-Uniform-Block', 'IG-Fact-Block', 'IG-Uniform-Fresh', 'IG-Fact-Fresh',
            'IG-Uniform-Direct', 'Fresh-IG-Lite', 'Belief-Gated', 'WorstFact-MI',
            'IG-Uniform-FixedType', 'IG-Fact-FixedType']


def category_target(scores, groups, d, uniform):
    """Same dense scores, unit cost and 1e-12 score tie rule in both classes."""
    if not uniform:
        selected = stable_argmax(scores)
        weights = np.zeros(len(scores)); weights[selected] = 1
        return weights, [selected]
    support = [[2*j+m for j in members] for members in groups for m in range(2)]
    support += [[2*d+g] for g in range(len(groups))]
    category_scores = np.array([np.mean(scores[s]) for s in support])
    selected_support = support[stable_argmax(category_scores)]
    weights = np.zeros(len(scores)); weights[selected_support] = 1/len(selected_support)
    return weights, selected_support


def marginal_information(b, j):
    """I(theta_j;Y_a) for every available task and type action."""
    first = b.first(); mass_theta = b.theta_mass
    py = first.sum(axis=0)
    out = np.zeros(len(py))
    # Sum both binary states separately; 1-p would erase rare-state evidence.
    for value in [0, 1]:
        mask = b.k['theta'][:, j] == value
        mass = float(mass_theta[mask].sum()); joint = first[mask].sum(axis=0)
        out += rel_entr(np.maximum(joint, 0), mass*py)
        out += rel_entr(np.maximum(mass-joint, 0), mass*(1-py))
    if not np.all(np.isfinite(out)): raise FloatingPointError('Nonfinite marginal information')
    return np.maximum(out, 0)


class DenseTracking(Factor):
    def __init__(self, public, cal, R, B, uniform, fresh):
        super().__init__(public, cal, R, 'IG-Dense', 'fresh' if fresh else 'sqrt', 'track', B)
        self.uniform = uniform

    def _update(self):
        start = time.process_time(); wall = time.perf_counter(); before = self.component_cpu['posterior']
        b = self.current_belief()
        self.weights, _ = category_target(b.ig(), self.groups, self.d, self.uniform)
        self.last_update = self.t
        self.next_update = self.t + (1 if self.cadence == 'fresh' else math.ceil(math.sqrt(self.t+1)))
        elapsed = time.process_time()-start
        self.component_cpu['target'] += max(0, elapsed-(self.component_cpu['posterior']-before))
        self.planner_cpu_seconds += elapsed; self.planner_seconds += time.perf_counter()-wall
        self.last_estimate = {**b.summary(), 'online': self.t, 'weights': self.weights.tolist(),
                              'next_update': self.next_update, 'allocation_rule': 'dense_IG_uniform' if self.uniform else 'dense_IG_fact'}
        self.estimates.append(self.last_estimate)
        self.update_history.append({'online': self.t, 'next_update': self.next_update,
            'weights': self.weights.tolist(), 'posterior_online': self.fit_online, 'cadence': self.cadence})


class UniformDirect(FreshLite):
    """Free-round fresh category choice; balance counts within chosen group/format."""
    def __init__(self, public, cal, R, B, worst=False, fixed_type=None):
        super().__init__(public, cal, R, B); self.worst = worst
        self.fixed_type = fixed_type; self.fixed_purchases = 0

    def next(self, active):
        if self._pending is not None: raise RuntimeError('Pending observation')
        if set(active) != set(range(self.d)): raise ValueError('All targets active')
        forced = self._forced_index(); self.last_forced = forced is not None
        diagnostic = {}
        if forced is None:
            start = time.process_time(); wall = time.perf_counter(); before = self.component_cpu['posterior']
            b = self.current_belief()
            if self.fixed_type is not None and self.fixed_purchases < self.G:
                self.weights = np.zeros(self.E); selected_type = self.L+self.fixed_purchases
                self.weights[selected_type] = 1; support = [selected_type]; self.fixed_purchases += 1
                diagnostic = {'fixed_type_purchase': True}
            elif self.fixed_type is not None:
                scores = b.ig().copy(); scores[self.L:] = -np.inf
                self.weights, support = category_target(scores, self.groups, self.d, self.fixed_type == 'uniform')
                diagnostic = {'fixed_type_purchase': False}
            elif self.worst:
                p = np.clip(np.asarray(b.summary()['theta_prob']),0,1)
                entropy = -p*np.log(np.maximum(p, 1e-300))-(1-p)*np.log(np.maximum(1-p, 1e-300))
                j = stable_argmax(entropy)
                scores = marginal_information(b, j)
                self.weights, support = category_target(scores, self.groups, self.d, False)
                diagnostic = {'priority_fact': j}
            else:
                self.weights, support = category_target(b.ig(), self.groups, self.d, True)
            # Integer least-count ties use smallest primitive action index.
            counts = self._actual_counts()
            selected = min(support, key=lambda a: (counts[a], a))
            self.last_update = self.t; self.next_update = self.t+1
            elapsed = time.process_time()-start
            self.component_cpu['target'] += max(0, elapsed-(self.component_cpu['posterior']-before))
            self.planner_cpu_seconds += elapsed; self.planner_seconds += time.perf_counter()-wall
            self.last_estimate = {**b.summary(), 'online': self.t, 'weights': self.weights.tolist(),
                                  'next_update': self.next_update, 'allocation_rule': 'worst_fact_marginal_MI' if self.worst else 'direct_group_average_IG'}
            self.estimates.append(self.last_estimate)
            self.update_history.append({'online': self.t, 'next_update': self.next_update,
                'weights': self.weights.tolist(), 'posterior_online': self.fit_online, 'cadence': 'fresh_free'})
        else: selected = forced
        self.cumulative += self.weights
        a = action(selected, self.d); self._pending = a; self._record(a, selected)
        self.action_history[-1].update(diagnostic)
        return a


def construct(name, public, cal, R, B):
    if name == 'KL-OriginalSolver':
        obj = Factor(public, cal, R, 'KL', 'sqrt', 'track', B)
        obj.solver = Solver('Teacher', {})
        return obj
    if name in ['KL-AnalyticReuse', 'KL-Fresh']:
        return Factor(public, cal, R, 'KL', 'sqrt' if name == 'KL-AnalyticReuse' else 'fresh', 'track', B)
    if name == 'Fused-Info': return Factor(public, cal, R, 'IG', 'sqrt', 'track', B)
    if name in ['IG-Uniform-Block', 'IG-Fact-Block', 'IG-Uniform-Fresh', 'IG-Fact-Fresh']:
        return DenseTracking(public, cal, R, B, 'Uniform' in name, name.endswith('Fresh'))
    if name == 'IG-Uniform-Direct': return UniformDirect(public, cal, R, B)
    if name == 'Fresh-IG-Lite': return FreshLite(public, cal, R, B)
    if name == 'Belief-Gated': return Switching(public, cal, R, B, 'Belief-Gated')
    if name == 'WorstFact-MI': return UniformDirect(public, cal, R, B, worst=True)
    if name in ['IG-Uniform-FixedType','IG-Fact-FixedType']:
        return UniformDirect(public, cal, R, B, fixed_type='uniform' if 'Uniform' in name else 'fact')
    raise ValueError('Unregistered policy')
