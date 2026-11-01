"""Exact rational posterior reference on small observation sets.

Uniform independent sign/type priors and uniform density on the ordered
rate triangle .5<=q<=p<=1-eta. No noisy report is treated as ground truth.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
from functools import lru_cache

@lru_cache(maxsize=4096)
def integral(a,b,c,d,eta):
    """Integral p^a(1-p)^b q^c(1-q)^d over the ordered triangle."""
    lo,hi=F(1,2),1-F(eta)
    power=lambda n:(hi**(n+1)-lo**(n+1))/F(n+1)
    value=F(0)
    for i in range(b+1):
        for j in range(d+1):
            n=c+j+1
            value+=(-1)**(i+j)*comb(b,i)*comb(d,j)/F(n)*(power(a+i+n)-lo**n*power(a+i))
    assert value>0
    return value

def exact_posterior(counts,groups,cal,reports,accuracy,eta=F(1,20)):
    d,G=len(counts),len(groups)
    if d>4 or sum(sum(sum(v) for v in row) for row in counts)+sum(map(len,cal.values()))>24:
        raise ValueError('Reference supports d<=4 and <=24 task/reference observations')
    membership={j:g for g,members in enumerate(groups) for j in members}
    out=[]
    for theta in product(range(2),repeat=d):
        for z in product(range(2),repeat=G):
            hs,hn=sum(cal['high']),len(cal['high']);ls,ln=sum(cal['low']),len(cal['low'])
            for j,row in enumerate(counts):
                for m,cnt in enumerate(row):
                    s,n=int(cnt[theta[j]]),sum(map(int,cnt))
                    if m==z[membership[j]]:hs+=s;hn+=n
                    else:ls+=s;ln+=n
            typ=F(1)
            for g,rr in enumerate(reports):
                acc=F(accuracy[g])
                typ*=acc**sum(v==z[g] for v in rr)*(1-acc)**sum(v!=z[g] for v in rr)
            args=(hs,hn-hs,ls,ln-ls,F(eta))
            base=typ*integral(*args)
            out.append((theta,z,base,typ*integral(hs+1,hn-hs,ls,ln-ls,F(eta)),typ*integral(hs,hn-hs,ls+1,ln-ls,F(eta))))
    norm=sum(r[2] for r in out)
    return {'theta_prob':[sum(r[2] for r in out if r[0][j])/norm for j in range(d)],
            'z_prob':[sum(r[2] for r in out if r[1][g])/norm for g in range(G)],
            'p':sum(r[3] for r in out)/norm,'q':sum(r[4] for r in out)/norm,
            'joint':{(r[0],r[1]):r[2]/norm for r in out},'arithmetic':'exact_Fraction'}
