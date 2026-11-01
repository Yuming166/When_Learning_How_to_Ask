"""Untrained NumPy interface reference, not a trained allocation policy.

Group equivariance and action expansion can be checked without fitting any
weights. No optimizer/training routine or model/provider call is provided.
"""
import math
import numpy as np
FIELDS={'p_hat','q_hat','alpha','eta','group_sizes','type_accuracy','epsilon'}

def features(state):
    if set(state)!=FIELDS:raise ValueError('Planning-state allow-list violation')
    p,q,alpha,eta,eps=[float(state[k]) for k in ['p_hat','q_hat','alpha','eta','epsilon']]
    if not all(math.isfinite(v) for v in [p,q,alpha,eta,eps]) or not 0<eta<.5 or not .5<=q<p<=1-eta+1e-15 or alpha<0 or eps<=0:
        raise ValueError('Invalid observable planning parameters')
    sizes=state['group_sizes'];G=len(sizes)
    if not G or any(type(k) is not int or k<=0 for k in sizes):raise ValueError('Nonempty positive group sizes required')
    supplied=state['type_accuracy'];available=supplied is not None
    if available and (len(supplied)!=G or any(not .5<float(s)<1 for s in supplied)):raise ValueError('Known finite type accuracies required')
    s=[float(x) for x in supplied] if available else [.5]*G
    local=np.array([[math.log1p(k),ss,float(available)] for k,ss in zip(sizes,s)])
    glob=np.array([p,q,p-q,math.log1p(alpha),eta,math.log1p(sum(sizes)),math.log1p(G),math.log(eps)])
    mask=np.ones((G,3),dtype=bool);mask[:,2]=available
    return glob,local,mask

class UntrainedNQA:
    def __init__(self,fixture_seed=123):
        rng=np.random.default_rng(fixture_seed)
        def layer(n,m):return [rng.normal(0,.02,size=(n,m)),np.zeros(m)]
        self.phi1=layer(3,32);self.phi2=layer(32,32)
        self.head1=layer(107,64);self.head2=layer(64,3)
        self.k1=layer(72,32);self.k2=layer(32,1)
    @property
    def parameter_count(self):return sum(x.size for layer in [self.phi1,self.phi2,self.head1,self.head2,self.k1,self.k2] for x in layer)
    def forward(self,state):
        glob,local,mask=features(state)
        linear=lambda x,layer:x@layer[0]+layer[1]
        h=np.tanh(linear(np.tanh(linear(local,self.phi1)),self.phi2))
        context=np.r_[glob,h.mean(axis=0),h.sum(axis=0)]
        joined=np.c_[h,np.broadcast_to(context,(len(h),len(context))),local]
        logits=linear(np.tanh(linear(joined,self.head1)),self.head2)
        logits=np.where(mask,logits,-np.inf);mass=np.exp(logits-np.max(logits));mass/=mass.sum()
        logK=float(linear(np.tanh(linear(context,self.k1)),self.k2)[0])
        return {'group_mass':mass,'K_hat':math.exp(float(np.clip(logK,-20,20))),
                'status':'UNTRAINED_INTERFACE_FIXTURE_NOT_A_SCIENTIFIC_POLICY'}

def expand(group_mass,groups,preferred,d):
    mass=np.asarray(group_mass,dtype=float)
    if mass.shape!=(len(groups),3) or np.any(~np.isfinite(mass)) or np.any(mass<0) or abs(mass.sum()-1)>1e-12:raise ValueError('Invalid probability mass')
    if sorted(j for gg in groups for j in gg)!=list(range(d)) or any(not gg for gg in groups):raise ValueError('Known partition required')
    if len(preferred)!=len(groups) or any(type(v) is not int or v not in (0,1) for v in preferred):raise ValueError('Observable format estimates must be bits')
    weights=np.zeros(2*d+len(groups))
    for g,members in enumerate(groups):
        for j in members:
            weights[2*j+preferred[g]]=mass[g,0]/len(members)
            weights[2*j+1-preferred[g]]=mass[g,1]/len(members)
        weights[2*d+g]=mass[g,2]
    return weights
