"""Common fixed-budget groupwise joint MAP, with finite-calibration plug-in rates.

Enumerates at most 2^16 sign assignments per group and marginalizes its type.
This is optimal for that plug-in posterior, not for uncertain continuous rates.
It is not an information-optimal allocation or a stopping certificate.
"""
from functools import lru_cache
import math
import numpy as np


def rate_estimates(cal):
    def estimate(values):return min(.999,max(.5,(sum(values)+1)/(len(values)+2)))
    p,q=estimate(cal['high']),estimate(cal['low'])
    if p<q:p=q=(p+q)/2
    return p,q


@lru_cache(maxsize=16)
def assignments(k):
    if not 1<=k<=16:raise ValueError('v0.1 exact decoder supports groups up to 16')
    ids=np.arange(2**k,dtype=np.uint32)[:,None]
    return ((ids>>np.arange(k-1,-1,-1,dtype=np.uint32))&1).astype(float)


def decode(public,counts,cal,type_answers,oracle=None):
    p,q=rate_estimates(cal);pred=[0]*public['d']
    for g,group in enumerate(public['groups']):
        js=group['targets'];terms=np.empty((2,len(js),2));prior=np.zeros(2)
        s=public['type_accuracy'][g]
        for z in range(2):
            for i,j in enumerate(js):
                for theta in [0,1]:
                    value=0.
                    for m in [0,1]:
                        r=p if m==z else q
                        value+=counts[j,m,theta]*math.log(r)+counts[j,m,1-theta]*math.log1p(-r)
                    terms[z,i,theta]=value
            for answer in type_answers[g]:
                probability=s if answer==z else 1-s
                prior[z]+=math.log(probability) if probability else -math.inf
        if oracle is not None:prior[1-'AB'.index(oracle[g])]=-math.inf
        bits=assignments(len(js))
        likelihood=[prior[z]+terms[z,:,0].sum()+bits@(terms[z,:,1]-terms[z,:,0]) for z in range(2)]
        score=np.logaddexp(likelihood[0],likelihood[1])
        selected=bits[int(np.argmax(score))]
        for j,value in zip(js,selected):pred[j]=int(value)
    return pred
