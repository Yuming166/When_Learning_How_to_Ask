"""Posterior-predictive rollout labels; no environment or true-world input.

Sequential predictive sampling is equivalent to sampling one latent world from
the current joint belief and then fresh answers given that world. We integrate
the terminal 0/1 MAP reward over its conditional posterior (Rao-Blackwellization).
The first answer is also summed exactly. Both operations preserve the same
Bayesian expected complete-recovery objective in the order-32 numerical model.
"""
import time
import numpy as np
from .core import worst_action
from t1b.controller import forced_index

def action_values(b,choices,t,B,K,rng):
    start=time.process_time();choices=sorted(set(map(int,choices)));remaining=B-t
    if remaining<1:raise ValueError('Rollout requires a legal query')
    uniforms=rng.random((K,max(0,remaining-1)))
    terminal_draws=rng.random(K);values={};rewards={};sampled={};steps=0
    for a in choices:
        rb=np.zeros(K);binary=np.zeros(K)
        for y in (0,1):
            branch_prob,child=b.condition(a,y)
            for k in range(K):
                state=child
                for offset,clock in enumerate(range(t+1,B)):
                    forced=forced_index(clock,2*b.k['d'])
                    follow=worst_action(state) if forced is None else forced
                    py=float(state.first()[:,follow].sum())
                    _,state=state.condition(follow,int(uniforms[k,offset]<py));steps+=1
                mass=state.theta_mass;best=int(np.argmax(mass))
                rb[k]+=branch_prob*float(mass[best])
                # A sampled terminal 0/1 reward is kept as a diagnostic. The
                # integrated target above has lower conditional variance.
                latent=int(np.searchsorted(np.cumsum(mass),terminal_draws[k],side='right'))
                binary[k]+=branch_prob*float(latent==best)
        rewards[a]=rb;sampled[a]=binary;values[a]=float(rb.mean())
    return {'q':values,'rb_rewards':{a:v.tolist() for a,v in rewards.items()},
      'sampled_terminal_rewards':{a:v.tolist() for a,v in sampled.items()},
      'continuation_steps':steps,'cpu_seconds':time.process_time()-start,'K':K,
      'model':'same frozen joint quadrature order32; first-answer enumeration and terminal Rao-Blackwellization',
      'continuation':'frozen WorstFact-MI rule with identical forced clock'}
