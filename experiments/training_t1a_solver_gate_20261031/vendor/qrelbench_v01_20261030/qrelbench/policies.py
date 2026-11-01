"""Learner-only policies. No generator/environment or evaluator imports."""
import math
from collections import deque
import numpy as np
from .decoder import decode

NAMES=['Fixed A','Fixed B','Round-Robin','Explore-Then-Commit','Repeat-and-Compare','Direct Type Query','Oracle Format']


def certificate(votes,n,d,delta):
    if n==0:return None
    boundary=math.sqrt(2*n*math.log(2*d*n*(n+1)/delta))
    return int(votes>0) if abs(votes)>boundary else None


class Strategy:
    def __init__(self,name,public):
        if name not in NAMES:raise ValueError('Unknown strategy')
        self.name=name;self.public=public;self.d=public['d'];self.G=len(public['groups'])
        self.counts=np.zeros((self.d,2,2),dtype=int);self.types=[[] for _ in range(self.G)]
        self.agree=np.zeros((self.G,2),dtype=int);self.pairs=np.zeros((self.G,2),dtype=int)
        self.pending_pair={};self.queue=deque();self.cursor=0
        self.type_queue=deque(range(self.G)) if name=='Direct Type Query' else deque()
        self.explore_queue=deque()
        if name=='Explore-Then-Commit':
            for group in public['groups']:
                for j in group['targets'][:2]:
                    self.explore_queue.extend((j,m) for m in ['A','A','B','B'])
        self.commit=None

    def estimate_format(self,g):
        # Public deterministic alternating tie rule; no private seed or types.
        a,b=(self.agree[g]+.5)/(self.pairs[g]+1)
        return 'A' if a>b else 'B' if b>a else 'AB'[g%2]

    def next(self,active):
        if self.type_queue:return ('type',self.type_queue.popleft())
        if self.explore_queue:return ('query',*self.explore_queue.popleft())
        if self.name=='Explore-Then-Commit' and self.commit is None:self.commit=[self.estimate_format(g) for g in range(self.G)]
        if self.queue:return ('query',*self.queue.popleft())
        for _ in range(self.d):
            j=self.cursor%self.d;self.cursor+=1
            if j in active:break
        else:return None
        g=self.public['targets'][j]['group'];name=self.name
        if name=='Fixed A':m='A'
        elif name=='Fixed B':m='B'
        elif name=='Round-Robin':m='AB'[int(self.counts[j].sum())%2]
        elif name=='Explore-Then-Commit':m=self.commit[g]
        elif name=='Direct Type Query':m='AB'[self.types[g][0]]
        elif name=='Oracle Format':m=self.public['oracle_format_types'][g]
        else:
            # Alternate full balanced exploration and selected-format repeat rounds.
            cycle=(self.cursor-1)//self.d
            forms=['A','A','B','B'] if cycle%2==0 else [self.estimate_format(g)]*2
            self.queue.extend((j,m) for m in forms[1:]);m=forms[0]
        return ('query',j,m)

    def observe(self,action,result):
        if action[0]=='type':self.types[action[1]].append('AB'.index(result['format']));return
        _,j,m=action;mi='AB'.index(m);y=result['answer'];self.counts[j,mi,y]+=1
        key=(j,mi)
        if key in self.pending_pair:
            first=self.pending_pair.pop(key);g=self.public['targets'][j]['group']
            self.agree[g,mi]+=first==y;self.pairs[g,mi]+=1
        else:self.pending_pair[key]=y


def run_policy(client,name,job):
    public=client.reset();cal=client.get_calibration();strategy=Strategy(name,public)
    d=public['d'];certified={};online=0
    while online<job['online_cap'] and (job['protocol']=='fixed_budget' or len(certified)<d):
        active=set(range(d))-set(certified) if job['protocol']=='fixed_confidence' else set(range(d))
        action=strategy.next(active)
        if action is None:break
        if action[0]=='type':result=client.ask_type(action[1])
        else:result=client.query(action[1],action[2])
        online+=1;strategy.observe(action,result)
        if job['protocol']=='fixed_confidence' and action[0]=='query':
            j=action[1]
            if j not in certified:
                n=int(strategy.counts[j].sum());votes=int(strategy.counts[j,:,1].sum()-strategy.counts[j,:,0].sum())
                value=certificate(votes,n,d,job['delta'])
                if value is not None:certified[j]=value
    if job['protocol']=='fixed_budget':
        predictions=decode(public,strategy.counts,cal,strategy.types,public.get('oracle_format_types'))
    else:
        # Uncertified guesses remain explicitly censored, never delta-correct completions.
        predictions=[certified.get(j,int(strategy.counts[j,:,1].sum()>strategy.counts[j,:,0].sum())) for j in range(d)]
    client.submit(predictions)
    return {'online_actions':online,'certified':len(certified),
            'completed':job['protocol']=='fixed_budget' or len(certified)==d,
            'certified_predictions':certified,'counts':strategy.counts.tolist(),'selected_types':strategy.types}
