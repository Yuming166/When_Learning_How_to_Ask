"""Same posterior, schedule, exploration and tracker; injected solver only."""
import time
from . import bootstrap
from .solvers import Solver
from phase2b import aligned
from phase2e.strategies import FusedOriginal,FusedDRRCType

SOLVER_ARMS=['Teacher','ExactCache','QuantizedCache','Interpolation','RadialReuse','AnalyticReuse','WarmStart']
POLICIES=SOLVER_ARMS+['Fused-D-RRC-Type']

class WithSolver(FusedOriginal):
    def __init__(self,public,cal,R,mode,grid):
        super().__init__(public,cal,R);self.solver=Solver(mode,grid)
    def _update(self):
        # One process per policy: no concurrent global patches; always restore.
        original=aligned.solve_allocation;aligned.solve_allocation=self.solver
        try:super()._update()
        finally:aligned.solve_allocation=original
        self.last_estimate['solver_mode']=self.solver.mode
        self.last_estimate['solver_stats']=dict(self.solver.stats)
        self.last_estimate['solver_component_cpu']=dict(self.solver.cpu)

def construct(name,public,cal,R,grid):
    if name=='Fused-D-RRC-Type':return FusedDRRCType(public,cal,R)
    return WithSolver(public,cal,R,name,grid)
