"""Read-only T1a AnalyticReuse adapter for the frozen T2 observable boundary.

Only the solver implementation is loaded from T1a. Its package bootstrap would
prepend a second vendor tree, so a private package namespace supplies a no-op
bootstrap after T2 has installed its already frozen, identical dependencies.
No historical source, global solver binding, posterior, or stopping gate changes.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import types


T2_ROOT = (Path(__file__).resolve().parents[3] / 'experiments/phase_t2_structure_allocator_v02_20261031')
T1A_ROOT = (Path(__file__).resolve().parents[3] / 'experiments/training_t1a_solver_gate_20261031')
SOURCE_PATH = T1A_ROOT / 't1a' / 'solvers.py'
SOURCE_SHA256 = '89bcdc606e105c2c49c585ab960b94378ae05aa802a3addd4a531011e99a3160'
COEFFICIENT_SHA256 = 'a31bf8eb268d99ab4cc28da09955d14082c229c87fc216400b5d3f9600e5253f'

# This is the same frozen T2 path used by the local integration. T2 bootstrap
# loads numerical code only; this adapter does not load a model/checkpoint.
if str(T2_ROOT) not in sys.path:
    sys.path.insert(0, str(T2_ROOT))
from t2.core import teacher_target  # noqa: E402
from phase2a import coefficients as _coefficients  # noqa: E402


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_frozen_solver():
    if _sha(SOURCE_PATH) != SOURCE_SHA256:
        raise RuntimeError('Frozen T1a solver source hash changed')
    if _sha(_coefficients.__file__) != COEFFICIENT_SHA256:
        raise RuntimeError('Loaded allocation objective is not the audited dependency')
    name = '_t2b_frozen_analytic_reuse'
    qualified = name + '.solvers'
    if qualified in sys.modules:
        return sys.modules[qualified]
    package = types.ModuleType(name)
    package.__path__ = []
    package.__package__ = name
    stub = types.ModuleType(name + '.bootstrap')
    package.bootstrap = stub
    sys.modules[name] = package
    sys.modules[name + '.bootstrap'] = stub
    spec = importlib.util.spec_from_file_location(qualified, SOURCE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(qualified, None)
        raise
    return module


class AnalyticReuseSolver:
    """Original T1a arithmetic exposed through T2's ``solver.solve`` API.

    Each instance owns its original counters. AnalyticReuse does not reuse
    cached answers or support cuts: its optimized algebra/vectorization retains
    the old information LP and full floating continuous-separation checks.
    Failures propagate; there is no hidden fallback or stopping decision.
    """

    def __init__(self):
        self._solver = _load_frozen_solver().Solver('AnalyticReuse')
        self.last_fit = None

    @property
    def stats(self):
        return self._solver.stats

    @property
    def cpu(self):
        return self._solver.cpu

    def solve(self, partition, p, q, alpha, type_accuracy=None, eta=.05,
              tolerance=2e-7, max_iterations=120):
        fit = self._solver(partition, p, q, alpha, type_accuracy, eta,
                           tolerance, max_iterations)
        self.last_fit = fit
        return fit

    __call__ = solve

    def target(self, observable_state):
        """Validate the strict T2 whitelist and use unchanged target expansion."""
        return teacher_target(observable_state, solver=self)

    def diagnostics(self):
        return {'mode': 'AnalyticReuse', 'source_sha256': SOURCE_SHA256,
                'calls': dict(self.stats), 'solver_cpu_seconds': dict(self.cpu),
                'scope': 'floating allocation diagnostics; no stopping certificate'}
