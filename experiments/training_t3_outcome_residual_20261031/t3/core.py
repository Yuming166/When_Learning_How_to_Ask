"""Observable action features and outcome-aligned residual control.

The MLP shares weights across physical actions. No world identifier, parameter
label, environment object, true state or reward enters this module's inputs.
The frozen quadrature posterior is an approximation to continuous inference.
"""
import math, time
import numpy as np
from . import bootstrap
from t1b.belief import action, index, stable_argmax
from t1b.controller import forced_index
from t1c.strategies import Factor
from t1d.strategies import marginal_information

def binary_entropy(p):
    p=np.clip(np.asarray(p),0,1)
    return -(p*np.log(np.maximum(p,1e-300))+(1-p)*np.log(np.maximum(1-p,1e-300)))

def worst_action(b, task_only=False):
    ent=binary_entropy(b.theta_mass@b.k['theta']); j=stable_argmax(ent)
    scores=marginal_information(b,j)
    return stable_argmax(scores[:2*b.k['d']] if task_only else scores)

def candidates(b, kl):
    """Four requested macro proposals plus a task fallback for the type gate."""
    d=b.k['d'];base=worst_action(b);ig=stable_argmax(b.ig())
    typ=2*d+stable_argmax(b.ig()[2*d:]);task=worst_action(b,True)
    return {'worst':base,'ig':ig,'kl':int(kl),'type':typ,'task':task}

def allowed_actions(proposals, d, mode):
    base=proposals['worst']; pool=sorted(set(proposals.values()))
    if mode=='task':
        pool=[base] if base>=2*d else [a for a in pool if a<2*d]
    elif mode=='type':
        # Task identity is frozen to the worst-fact task proposal. The learner
        # may buy/skip a type report, including when the base proposes type.
        pool=[a for a in pool if a>=2*d or a==proposals['task'] or a==base]
        if base<2*d: pool=[a for a in pool if a>=2*d or a==base]
    elif mode!='joint':raise ValueError('Unknown mask')
    return sorted(set(pool+[base]))

FEATURE_NAMES=[
 'd_over_8','groups_over_d','remaining_over_64','fraction_remaining','free_remaining_over_32',
 'mean_fact_entropy','max_fact_entropy','min_fact_entropy','mean_group_entropy',
 'max_group_entropy','joint_entropy_per_fact','joint_map_probability','p_mean','q_mean','gap_mean',
 'p_sd','q_sd','calibration_per_stream_over_96','type_count_over_32',
 'task_count_over_64','group_size_fraction','group_mean_fact_entropy','group_max_fact_entropy',
 'group_type_entropy','group_type_count_over_16','is_type','fact_entropy','fact_confidence',
 'format_count_over_32','other_format_count_over_32','answer_imbalance_over_32',
 'group_format_count_over_64','joint_information','worst_fact_information','one_step_recovery_gain',
 'predictive_answer_entropy','is_worst_proposal','is_ig_proposal','is_kl_proposal','is_type_proposal']

def features(b, groups, counts, reports, cal_size, t, B, proposals):
    d=b.k['d'];G=len(groups);mass=b.theta_mass;tp=mass@b.k['theta'];ent=binary_entropy(tp)
    # Derive z masses from the same joint quadrature weights, never a report
    # interpreted as a revealed group type.
    zm=b.w.reshape(len(mass),b.k['nz'],b.k['nr']).sum(axis=(0,2));zp=zm@b.k['z']
    hz=binary_entropy(zp);rm=b.w.sum(0);pm=float(rm@b.k['p']);qm=float(rm@b.k['q'])
    sd_p=math.sqrt(max(0,float(rm@(b.k['p']-pm)**2)));sd_q=math.sqrt(max(0,float(rm@(b.k['q']-qm)**2)))
    free_left=sum(forced_index(x,2*d) is None for x in range(t,B))
    glob=[d/8,G/d,(B-t)/64,(B-t)/B,free_left/32,*[float(f(ent))/math.log(2) for f in [np.mean,np.max,np.min]],
      float(np.mean(hz))/math.log(2),float(max(hz))/math.log(2),b.entropy()/(d*math.log(2)),float(max(mass)),pm,qm,pm-qm,
      sd_p,sd_q,cal_size/96,sum(map(len,reports))/32,float(counts.sum())/64]
    ig=b.ig();j=stable_argmax(ent);mi=marginal_information(b,j);rec=b.recovery()-max(mass)
    py=b.first().sum(0);rows=[]
    for a in range(2*d+G):
        typ=a>=2*d;fact=None if typ else a//2;fmt=None if typ else a%2
        g=a-2*d if typ else next(g for g,mm in enumerate(groups) if fact in mm);mm=list(groups[g])
        local=[len(mm)/d,float(np.mean(ent[mm]))/math.log(2),float(max(ent[mm]))/math.log(2),hz[g]/math.log(2),len(reports[g])/16,
          float(typ),0 if typ else ent[fact]/math.log(2),0 if typ else max(tp[fact],1-tp[fact]),
          len(reports[g])/32 if typ else counts[fact,fmt].sum()/32,0 if typ else counts[fact,1-fmt].sum()/32,
          0 if typ else (counts[fact,fmt,1]-counts[fact,fmt,0])/32,
          0 if typ else counts[mm,fmt].sum()/64,ig[a],mi[a],rec[a],float(binary_entropy(py[a]))/math.log(2),
          float(a==proposals['worst']),float(a==proposals['ig']),float(a==proposals['kl']),float(a==proposals['type'])]
        rows.append(glob+local)
    out=np.asarray(rows,dtype=float)
    if out.shape!=(2*d+G,len(FEATURE_NAMES)) or not np.all(np.isfinite(out)):raise ValueError('Invalid legal feature matrix')
    return out

class ValueNet:
    """Shared 40-32-16-1 tanh MLP, trained on pairwise residual value."""
    def __init__(self,seed=0,arrays=None):
        if arrays is not None:self.p={k:np.array(v) for k,v in arrays.items()};return
        rng=np.random.default_rng(seed);sizes=[len(FEATURE_NAMES),32,16,1];self.p={}
        for i,(a,b) in enumerate(zip(sizes[:-1],sizes[1:])):
            self.p[f'W{i}']=rng.normal(0,math.sqrt(1/a),(a,b));self.p[f'b{i}']=np.zeros(b)
    def forward(self,X,cache=False):
        h0=np.tanh(X@self.p['W0']+self.p['b0']);h1=np.tanh(h0@self.p['W1']+self.p['b1']);y=(h1@self.p['W2']+self.p['b2']).ravel()
        return (y,(X,h0,h1)) if cache else y
    def gradients(self,cache,dy):
        X,h0,h1=cache;z=dy[:,None];g={'W2':h1.T@z,'b2':z.sum(0)}
        z=(z@self.p['W2'].T)*(1-h1*h1);g.update(W1=h0.T@z,b1=z.sum(0))
        z=(z@self.p['W1'].T)*(1-h0*h0);g.update(W0=X.T@z,b0=z.sum(0));return g
    def save(self,path):np.savez(path,**self.p)
    @classmethod
    def load(cls,path):
        with np.load(path,allow_pickle=False) as a:return cls(arrays={k:a[k] for k in a.files})

class ResidualPolicy(Factor):
    def __init__(self,public,cal,R,B,mode='joint',net=None,threshold=.02,rule=False):
        super().__init__(public,cal,R,'KL','sqrt','BARPO',B)
        self.mode=mode;self.net=net;self.threshold=threshold;self.rule=rule;self.decisions=[]
    def next(self,active):
        # All residual arms pay for the same frozen AnalyticReuse KL proposal.
        kl_action=super().next(active)
        if self.last_forced:return kl_action
        start=time.process_time();post_before=self.component_cpu['posterior'];b=self.current_belief()
        proposal=candidates(b,index(kl_action,self.d));pool=allowed_actions(proposal,self.d,self.mode);base=proposal['worst']
        X=features(b,self.groups,self.counts,self.types,len(self.calibration['high']),self.t,self.budget,proposal)
        after_features=time.process_time();pred=None;chosen=base
        if self.rule:
            # Frozen simple alternative: buy one report per group at the start
            # of free allocation, then alternate Worst and IG task proposals.
            if self.t<4*self.d+self.G:chosen=2*self.d+self.t-4*self.d
            else:chosen=proposal['worst'] if self.t%2==0 else proposal['ig']
        elif self.net is not None:
            raw=self.net.forward(X)
            if not np.all(np.isfinite(raw)):raise FloatingPointError('Nonfinite learned values')
            pred=raw-raw[base];best=pool[stable_argmax(pred[pool])]
            if pred[best]>self.threshold:chosen=best
        infer_end=time.process_time();self.component_cpu['feature_and_candidates']+=after_features-start-(self.component_cpu['posterior']-post_before)
        self.component_cpu['network_inference']+=infer_end-after_features
        self.component_cpu['controller']+=infer_end-start-(self.component_cpu['posterior']-post_before)
        out=action(int(chosen),self.d);self._pending=out
        self.action_history[-1].update(action=int(chosen),selection_rule='rule' if self.rule else 'learned_residual',base_action=base)
        self.decisions.append({'online':self.t,'proposals':proposal,'allowed':pool,'base':base,'chosen':int(chosen),
          'predicted_advantages':None if pred is None else pred.tolist(),'override':chosen!=base})
        return out
