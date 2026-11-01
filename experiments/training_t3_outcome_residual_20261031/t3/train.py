"""Nine fixed small fits; checkpoint selection uses DEV labels only."""
import time
import numpy as np
from .core import ValueNet,allowed_actions

def examples(states,mode):
    xs=[];xb=[];ys=[];world=[]
    for s in states:
        X=np.asarray(s['features']);base=s['proposals']['worst'];q=s['values']['q']
        for a in allowed_actions(s['proposals'],s['d'],mode):
            if a==base:continue
            xs.append(X[a]);xb.append(X[base]);ys.append(float(q[str(a)])-float(q[str(base)]));world.append(s['world_index'])
    if not xs:raise ValueError('No residual examples')
    return np.array(xs),np.array(xb),np.array(ys),world

def fit(train_states,dev_states,mode,seed,folder,cfg):
    start=time.process_time();wall=time.monotonic();X,Xb,y,world=examples(train_states,mode)
    D,Db,dy,_=examples(dev_states,mode);net=ValueNet(seed);rng=np.random.default_rng(seed)
    m={k:np.zeros_like(v) for k,v in net.p.items()};v={k:np.zeros_like(v) for k,v in net.p.items()}
    step=0;history=[];best=None;best_loss=float('inf');selected=None
    for epoch in range(1,cfg['epochs']+1):
        order=rng.permutation(len(y))
        for offset in range(0,len(y),cfg['batch_size']):
            ix=order[offset:offset+cfg['batch_size']];data=np.concatenate([X[ix],Xb[ix]])
            output,cache=net.forward(data,True);n=len(ix);diff=output[:n]-output[n:]-y[ix]
            derivative=np.r_[2*diff/n,-2*diff/n];grad=net.gradients(cache,derivative);step+=1
            for k in net.p:
                g=grad[k]+cfg['l2']*net.p[k];m[k]=.9*m[k]+.1*g;v[k]=.999*v[k]+.001*g*g
                net.p[k]-=cfg['learning_rate']*(m[k]/(1-.9**step))/(np.sqrt(v[k]/(1-.999**step))+1e-8)
        if epoch in cfg['checkpoints']:
            pred=net.forward(D)-net.forward(Db);loss=float(np.mean((pred-dy)**2))
            path=folder/f'{mode}_seed{seed}_epoch{epoch}.npz';net.save(path)
            history.append({'epoch':epoch,'train_mse':float(np.mean((net.forward(X)-net.forward(Xb)-y)**2)),
              'dev_mse':loss,'dev_zero_residual_mse':float(np.mean(dy*dy)),'checkpoint':str(path.name)})
            if loss<best_loss:best_loss=loss;best=path;selected=epoch
    return {'mode':mode,'seed':seed,'train_pairs':len(y),'dev_pairs':len(dy),'training_worlds':len(set(world)),
      'parameters':sum(a.size for a in net.p.values()),'optimizer_steps':step,'epochs':cfg['epochs'],
      'selected_epoch_by_dev_mse':selected,'selected_checkpoint':best.name,'history':history,
      'cpu_seconds':time.process_time()-start,'wall_seconds':time.monotonic()-wall,
      'selection':'DEV-label MSE checkpoint, then DEV episode success for seed; no TEST access'}
