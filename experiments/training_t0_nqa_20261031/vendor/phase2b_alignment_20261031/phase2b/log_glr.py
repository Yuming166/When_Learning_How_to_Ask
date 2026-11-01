"""Log-risk interface: keeps R=1024 finite without exp(-R) underflow."""
import math
import numpy as np
from . import bootstrap
from phase2a.glr import profile_glr


def log_glr(counts,groups,calibration,type_answers,type_accuracy,R,eta=.05,oracle_types=None):
    if not isinstance(R,(float,int)) or not math.isfinite(R) or R<=0:raise ValueError('R must be positive and finite')
    # In the read-only likelihood routine delta affects beta only, never the
    # likelihood profiles. Rebuild beta directly to avoid exp/log underflow.
    fit=profile_glr(counts,groups,calibration,type_answers,type_accuracy,delta=.5,eta=eta,oracle_types=oracle_types)
    terms=[2*math.log1p(len(calibration['high']))]
    terms.extend(math.log1p(int(n)) for n in np.asarray(counts).sum(axis=2).reshape(-1))
    terms.extend(math.log1p(len(a)) for a in type_answers)
    fit['beta']=float(R+math.fsum(terms));fit['certified']=fit['gap']>=fit['beta']
    fit['log_inverse_delta']=R;fit['risk_representation']='R=log(1/delta), no exp(-R) conversion'
    fit['interval_certified']=False
    return fit
