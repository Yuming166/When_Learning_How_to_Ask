"""Additive routing around the byte-frozen T1d evaluation policy."""
import time
from .bootstrap import ROOT
from .core import ResidualPolicy,ValueNet
from t1d.strategies import construct as frozen_construct
from t1d import policy as frozen_policy
from t1b.belief import kernel
from phase2a.coefficients import warmup_lp
from qrelbench.rpc import Client,send,receive
from qrelbench.security import confine_worker

class Collector(ResidualPolicy):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.training_states=[]
    def next(self,active):
        out=super().next(active)
        if self.t in (16,20,24,28) and not self.last_forced:
            self.training_states.append({'t':self.t,'B':self.budget,'d':self.d,'groups':self.groups,
              'counts':self.counts.tolist(),'reports':[list(v) for v in self.types],
              'calibration':self.calibration,'accuracy':self.type_accuracy,'eta':self.eta,
              'proposals':dict(self.decisions[-1]['proposals'])})
        return out

def warm():
    warmup_lp()
    for groups in [((0,),(1,2,3)),((0,1),(2,3)),((0,1,2,3),),((0,),(1,2)),((0,1,2),)]:
        kernel(sum(map(len,groups)),groups,(.8,)*len(groups),.05,32)

def worker(conn,name,model_path=None):
    startup=time.process_time();warm();net=ValueNet.load(model_path) if model_path else None
    holder={}
    def construct(n,public,cal,R,B):
        if n=='Collect-Worst':obj=Collector(public,cal,R,B)
        elif n=='Rule-Switch':obj=ResidualPolicy(public,cal,R,B,rule=True)
        elif n.startswith('Learned-'):
            mode=n.split('-')[1].lower();obj=ResidualPolicy(public,cal,R,B,mode=mode,net=net)
        else:obj=frozen_construct(n,public,cal,R,B)
        holder['sampler']=obj;return obj
    # Routing only; baseline implementations and fixed-budget decoder/gate are
    # the unchanged frozen functions. Each worker hosts one policy sequentially.
    frozen_policy.construct=construct
    startup=time.process_time()-startup;isolation=confine_worker();isolation['worker_startup_cpu']=startup
    while True:
        job=receive(conn)
        if job is None:break
        try:
            detail=frozen_policy.run_policy(Client(conn),name,job)
            obj=holder['sampler'];detail['estimation_history'][-1]['training_states']=getattr(obj,'training_states',[])
            detail['sampling_scope']='T3 fixed budget; frozen common posterior, MAP decoder and certified terminal gate'
            send(conn,{'done':{**detail,'isolation':isolation}})
        except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
    conn.close()
