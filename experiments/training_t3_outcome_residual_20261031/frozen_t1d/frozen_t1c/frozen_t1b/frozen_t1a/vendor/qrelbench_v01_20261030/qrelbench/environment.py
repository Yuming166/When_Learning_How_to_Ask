"""Trusted server environment. Never hand this object to a learner."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from .data import public_view,evaluate
from .randomness import uniform


class QueryEnvironment:
    def __init__(self,episode,p,q,calibration_size=64,type_accuracy=.8,online_cap=256,
                 control='iid',oracle=False,eta=.05):
        if not 0<eta<.5 or not .5<=q<=p<=1-eta:raise ValueError('Invalid symmetric channel rates')
        if not .5<type_accuracy<=1:raise ValueError('Invalid type accuracy')
        if control not in {'iid','persistent','label_asymmetric'}:raise ValueError('Unknown channel')
        if calibration_size<0 or online_cap<0:raise ValueError('Invalid acquisition limits')
        self._episode=episode;self._p=p;self._q=q;self._M=calibration_size;self._s=type_accuracy
        self._cap=online_cap;self._control=control;self._oracle=oracle
        self._eta=eta
        self._started=False;self._submitted=False;self._counter=Counter();self._cal=None
        self.cost={'task':0,'type':0,'offline':0};self.log_digest=hashlib.sha256();self.trace=[]

    def _record(self,action,args,result):
        event={'action':action,'args':args,'result':result}
        self.log_digest.update(json.dumps(event,sort_keys=True,separators=(',',':')).encode()+b'\n')
        if len(self.trace)<128:self.trace.append(event)

    def _active(self):
        if not self._started or self._submitted:raise RuntimeError('Episode is not active')

    def _charge(self,kind):
        self._active()
        if self.cost['task']+self.cost['type']>=self._cap:raise RuntimeError('Online budget exhausted')
        self.cost[kind]+=1

    def reset(self):
        if self._started:raise RuntimeError('No reset/seed selection within an episode')
        self._started=True;view=public_view(self._episode)
        view['type_accuracy']=[self._s]*len(view['groups'])
        view['calibration_size_per_stream']=self._M
        view['rate_domain']={'eta':self._eta,'q_min':.5,'p_max':1-self._eta,'levels_unknown':True}
        if self._oracle:view['oracle_format_types']=['AB'[z] for z in self._episode.types]
        self._record('reset',{},view);return view

    def query(self,j,format):
        self._active()
        if type(j) is not int or not 0<=j<self._episode.public['d'] or format not in ['A','B']:raise ValueError('Invalid query')
        self._charge('task');m='AB'.index(format);g=self._episode.public['targets'][j]['group']
        r=self._p if m==self._episode.types[g] else self._q
        theta=evaluate(self._episode.records[j],self._episode.public['targets'][j]['proposition'])
        if self._control=='label_asymmetric' and theta==0:r=1-r
        counter=self._counter[j,m];self._counter[j,m]+=1
        draw_index=0 if self._control=='persistent' else counter
        correct=uniform(self._episode.key,'task_error',j,m,draw_index)<r
        answer=theta if correct else 1-theta
        result={'answer':answer};self._record('query',{'j':j,'format':format},result);return result

    def ask_type(self,group):
        self._active()
        if type(group) is not int or not 0<=group<len(self._episode.types):raise ValueError('Invalid group')
        self._charge('type');i=self._counter['type',group];self._counter['type',group]+=1
        correct=uniform(self._episode.key,'type_error',group,i)<self._s
        value=self._episode.types[group] if correct else 1-self._episode.types[group]
        result={'format':'AB'[value]};self._record('ask_type',{'group':group},result);return result

    def get_calibration(self):
        self._active()
        if self._cal is None:
            self._cal={name:[int(uniform(self._episode.key,'offline_reference',name,i)<r) for i in range(self._M)]
                       for name,r in [('high',self._p),('low',self._q)]}
            self.cost['offline']=2*self._M
        result=deepcopy(self._cal);self._record('get_calibration',{},result);return result

    def submit(self,predictions):
        self._active();d=self._episode.public['d']
        if len(predictions)!=d or any(type(x) is not int or x not in [0,1] for x in predictions):raise ValueError('Invalid predictions')
        self._submitted=True;self.predictions=list(predictions)
        # Scoring/reward is never returned to the learner, including at submission.
        result={'submitted':True};self._record('submit',{'predictions':predictions},result);return result

    def score(self):
        if not self._submitted:raise RuntimeError('No early scoring')
        return {'exact':self.predictions==self._episode.truth,
                'correct_facts':sum(a==b for a,b in zip(self.predictions,self._episode.truth)),
                'costs':dict(self.cost),'online':self.cost['task']+self.cost['type'],
                'total_acquisition':sum(self.cost.values()),'transcript_sha256':self.log_digest.hexdigest()}
