"""Observable-only, untrained controllers. No outcome/identity inputs."""
import time
from copy import deepcopy
import numpy as np
from . import bootstrap
from t2.core import validate_state, normalize, teacher_target
from phase2e.estimator import information_scores
from .reuse import AnalyticReuseSolver

METHODS=('Fused-Original-Cold','AnalyticReuse','Fused-Info','DeepSets-KL','DeepSets-Info','Hybrid-Risk-Info','Hybrid-Risk-Reuse','Periodic-Info')

def risk_flags(state,weights):
    s=validate_state(state);d=s['d'];G=len(s['groups']);w=normalize(weights,s)
    theta=np.asarray(s['estimate']['theta_prob']);z=np.asarray(s['estimate']['z_prob'])
    u=4*theta*(1-theta);v=4*z*(1-z);task=w[:2*d].reshape(d,2).sum(1)
    # Fixed algebraic thresholds, no fitted labels or posthoc success inputs.
    return {'uncertain_fact':bool(np.any(u>.5)), 'uncertain_type':bool(np.any(v>.5)),
            'uncertain_fact_starved':bool(np.any((u>.05)&(task<.25/d))),
            'confident_type_overweight':bool(np.all(v<.05) and w[2*d:].sum()>G/(2*d+G)+1e-12),
            'concentrated':bool(np.max(w)>.8)}

class Controller:
    def __init__(self,method,models):
        if method not in METHODS:raise ValueError('Unknown controller')
        self.method=method;self.models=models;self.reuse=AnalyticReuseSolver() if method in ['AnalyticReuse','Hybrid-Risk-Reuse'] else None;self.decisions=[]
        self.wall={'neural':0.,'risk':0.,'fallback':0.};self.cpu=dict(self.wall)
    def timed(self,key,fn):
        start,cpu=time.perf_counter(),time.process_time()
        try:return fn()
        finally:self.wall[key]+=time.perf_counter()-start;self.cpu[key]+=time.process_time()-cpu
    def info(self,state,fit):
        if fit is None:raise ValueError('Shared observable joint posterior required')
        scores=information_scores(fit,state['groups'],state['known_s'],True)
        if not np.isfinite(scores).any():raise FloatingPointError('No finite information action')
        w=np.zeros(len(state['action_mask']));w[int(np.argmax(scores))]=1.
        return w
    def predict(self,state,observable_fit=None):
        s=validate_state(state);m=self.method;flags={};fallback=False;source=m
        if m=='Fused-Original-Cold':
            w=self.timed('fallback',lambda:teacher_target(s)['teacher_weights'])
        elif m=='AnalyticReuse':
            w=self.timed('fallback',lambda:self.reuse.target(s)['teacher_weights'])
        elif m=='Fused-Info':w=self.timed('fallback',lambda:self.info(s,observable_fit))
        else:
            student='DeepSets-Info' if m=='DeepSets-Info' else 'DeepSets-KL'
            w=self.timed('neural',lambda:self.models[student].predict(deepcopy(s)))
            if m.startswith('Hybrid-'):
                flags=self.timed('risk',lambda:risk_flags(s,w));fallback=any(flags.values())
            elif m=='Periodic-Info':fallback=(len(self.decisions)%4==0)
            if fallback:
                source='AnalyticReuse' if m=='Hybrid-Risk-Reuse' else 'Fused-Info'
                w=self.timed('fallback',lambda:self.reuse.target(s)['teacher_weights'] if source=='AnalyticReuse' else self.info(s,observable_fit))
        w=normalize(w,s)
        self.decisions.append({'online':s['online'],'fallback':fallback,'source':source,'risk_flags':flags})
        return w
