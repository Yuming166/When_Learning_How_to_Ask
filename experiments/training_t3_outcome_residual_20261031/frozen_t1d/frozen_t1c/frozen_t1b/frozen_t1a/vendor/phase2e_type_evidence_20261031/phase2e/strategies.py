"""Additive samplers; frozen strategies are imported without modification."""
import math
import time
import numpy as np
from . import bootstrap
from phase2d.strategies import SAMPLERS as FROZEN
from phase2d.strategies import AlignedFull,AlignedNoType,DRRCType
from .estimator import posterior,public_estimate,information_scores

class Fusion:
    def __init__(self,public,calibration,planning_R):
        super().__init__(public,calibration,planning_R)
        self.calibration={k:list(v) for k,v in calibration.items()}
        self._posterior=None
    def _estimate(self):
        self._posterior=posterior(self.counts,self.groups,self.calibration,self.types,self.type_accuracy,self.eta)
        return {**public_estimate(self._posterior),'forced_tasks':int(self.forced.sum()),
                'forced_task_counts':self.forced.sum(axis=2).tolist()}

class FusedOriginal(Fusion,AlignedFull):pass
class FusedOriginalNoType(Fusion,AlignedNoType):pass
class FusedDRRCType(Fusion,DRRCType):pass

class FusedInformation(Fusion,AlignedFull):
    allow_type=True
    def _update(self):
        wall,cpu=time.perf_counter(),time.process_time()
        estimate=self._estimate()
        scores=information_scores(self._posterior,self.groups,self.type_accuracy,self.allow_type)
        if not np.any(np.isfinite(scores)):raise FloatingPointError('No finite decision-information score')
        chosen=int(np.argmax(scores));self.weights=np.zeros(self.E);self.weights[chosen]=1
        self.last_update=self.t;self.next_update=self.t+max(1,math.ceil(math.sqrt(self.t+1)))
        elapsed,elapsed_cpu=time.perf_counter()-wall,time.process_time()-cpu
        self.planner_seconds+=elapsed;self.planner_cpu_seconds+=elapsed_cpu
        self.last_estimate={**estimate,'online':self.t,'alpha_effective':self.alpha,'weights':self.weights.tolist(),
            'allocation_rule':'greedy_expected_information_about_joint_theta_per_unit_cost',
            'action_log_information':[float(v) if np.isfinite(v) else None for v in scores],
            'paid_type_target_mass':float(self.weights[self.L:].sum()),'next_update':self.next_update,
            'update_seconds':elapsed,'update_cpu_seconds':elapsed_cpu,
            'arithmetic_scope':'numerical_posterior_and_information_not_a_stopping_certificate'}
        self.estimates.append(self.last_estimate)

class FusedInformationNoType(FusedInformation):allow_type=False

SAMPLERS={**FROZEN,'Fused-Original':FusedOriginal,'Fused-Info':FusedInformation,
          'Fused-D-RRC-Type':FusedDRRCType,'Fused-Original-NoType':FusedOriginalNoType,
          'Fused-Info-NoType':FusedInformationNoType}
POLICIES=list(SAMPLERS)
def construct_sampler(name,public,calibration,R):return SAMPLERS[name](public,calibration,R)
